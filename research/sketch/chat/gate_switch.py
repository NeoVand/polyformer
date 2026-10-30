"""T4 option 2: the gate switched inside a reply. Stock Qwen (gate 0) writes the reply under the sheet system prompt and
four example exchanges (chat_eval.py --fewshot); the adapter (gate 1) writes only the body of each ```sheet block, from
the opening fence to the closing one; the runtime's `= …` lines and everything after them are gate 0 again.

One Hugging Face `generate` per batch with a per-row gate: every LoRA layer's scale becomes a [batch, 1, 1] tensor G
(0, or the adapter's alpha/r), and a logits processor picks each row's greedy token (or the runtime's forced token),
tracks whether the row is inside a block, and sets G for the next forward. A forward runs at the gate of the token it
predicts, so the cache carries over the switch: the adapter reads the keys, values and delta-net states stock wrote,
as on the page.

  selftest  gate 0 = adapter disabled bit for bit, mixed rows = their single-gate rows, 16 IFEval replies at gate 0 =
            plain stock generation token for token
  heldout   the held-out set, scored as chat_eval.py (blocks run on sheet_ref.py, the host stand-in); writers after the
            first rerun only the items where a block opened (the prose before it is stock's for every writer)
  cache     each opened held-out item (and the first GSM8K block) rewritten from a context prefilled at gate 1, against
            the block written from stock's gate-0 cache
  ifeval    first writer on all 541; the prompts where it opened a block rerun at gate 0 (stock few-shot exactly) and
            with every other writer
  gsm8k     250 test problems (seed 0), up to 10 blocks
  mmlu      500 questions (seed 0) at gate 0 under the sheet prompt (no block can open on a one-letter answer)

  python chat/gate_switch.py <data dir> <tag> <name=adapter> [<name=adapter> ...] [--parts ...]
writes switch_<tag>.json and switch_samples_<tag>.jsonl
"""

import argparse
import json
import pathlib
import random
import re
import sys
import time
from fractions import Fraction

import torch
from transformers import LogitsProcessor, LogitsProcessorList

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e2_column as e2  # noqa: E402
import sheet_ref  # noqa: E402
from gen import chat_prefix, closed_block, generate, last_number  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("data")
ap.add_argument("tag")
ap.add_argument("writers", nargs="+", help="name=adapter dir; the first runs every part")
ap.add_argument("--parts", default="selftest,heldout,cache,ifeval,gsm8k,mmlu")
args = ap.parse_args()
parts = args.parts.split(",")
tok = e2.tok
t0 = time.time()
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
EOS = [IM_END, tok.eos_token_id]
PAD = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
FENCE = {i for i in range(len(tok)) if tok.decode([i]).strip() == "```"}
OPEN = "```sheet"
res = {"tag": args.tag, "writers": args.writers}
SAMPLES = []

# the stock few-shot baseline's messages, as in chat_eval.py
FEW_SYSTEM = (
    "You have a sheet: an exact calculator you can call in your reply. To use it, write a block that starts with "
    "```sheet and ends with ```, one statement per line: an arithmetic expression (+ − × ÷ ^, brackets, √(…), "
    "gcd(a, b), and an optional 'to k places'), or 'solve <equation>', 'expand <polynomial>', 'factor <polynomial>'. "
    "Write only the expression, never its value. The sheet answers with a line '= <value>'; then finish your reply "
    "using that value. Use the sheet only when a question needs arithmetic beyond single digits, or algebra; "
    "otherwise answer normally.")
FEW_SHOTS = [
    ("A crate holds 24 bottles. A shop orders 37 crates and 15 loose bottles. How many bottles arrive?",
     "Let me work it out on the sheet.\n\n```sheet\n37 × 24 + 15\n```\n= 903\n903 bottles arrive."),
    ("Solve 5(x − 3) = 2x + 9.", "I'll put it on the sheet.\n\n```sheet\nsolve 5(x − 3) = 2x + 9\n```\n= x = 8\nSo x = 8."),
    ("What is 6 + 3?", "6 + 3 = 9."),
    ("Write a haiku about the moon.", "Silver lantern hangs,\nquiet over sleeping fields,\nnight breathes in its light."),
]


def messages(user):
    m = [{"role": "system", "content": FEW_SYSTEM}]
    for q, a in FEW_SHOTS:
        m += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
    return m + [{"role": "user", "content": user}]


def save():
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(f"switch_{args.tag}.json", "w"), indent=1)
    with open(f"switch_samples_{args.tag}.jsonl", "w") as f:
        for s in SAMPLES:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "selftest_rows"})[:3000], flush=True)


from peft import PeftModel  # noqa: E402

names = [w.split("=", 1)[0] for w in args.writers]
model = PeftModel.from_pretrained(e2.load_base().eval(), args.writers[0].split("=", 1)[1], adapter_name=names[0])
for w in args.writers[1:]:
    model.load_adapter(w.split("=", 1)[1], adapter_name=w.split("=", 1)[0])
model.eval()
LORA = [m for m in model.modules() if hasattr(m, "scaling") and hasattr(m, "lora_A") and len(m.lora_A)]
SCALE = {m.scaling[n] for m in LORA for n in names}
assert len(SCALE) == 1, SCALE
SCALE = SCALE.pop()
DTYPE = LORA[0].lora_A[names[0]].weight.dtype
dev = next(model.parameters()).device
res["lora_layers"], res["scale"] = len(LORA), SCALE


def use(writer, G):
    """Make `writer` the active adapter with scale G: a [batch, 1, 1] tensor (per-row gate) or a float."""
    model.set_adapter(writer)
    for m in LORA:
        m.scaling[writer] = G


def strip_pad(ids):
    ids = list(ids)
    while ids and ids[-1] == PAD:
        ids.pop()
    return ids


def left_pad(prompts):
    L = max(map(len, prompts))
    ids = torch.full((len(prompts), L), PAD, dtype=torch.long)
    mask = torch.zeros((len(prompts), L), dtype=torch.long)
    for r, p in enumerate(prompts):
        ids[r, L - len(p):] = torch.tensor(p)
        mask[r, L - len(p):] = 1
    return ids.to(dev), mask.to(dev)


class Switch(LogitsProcessor):
    """Each row's greedy token, or the runtime's forced one; then the gate of the next forward (the one that predicts
    the following token): the adapter's scale inside an open block, 0 elsewhere ("switch"); always 0 ("gate0");
    always the scale ("gate1", used to rewrite a block from a context prefilled at gate 1)."""

    def __init__(self, rows, G, mode, rounds):
        self.rows, self.G, self.mode, self.rounds = rows, G, mode, rounds

    def step(self, r, t):
        if t in EOS:
            r["done"] = True
        elif r["in_block"]:
            text = (OPEN if r["block_only"] else "") + tok.decode(r["reply"])  # block_only: the opener is in the prompt
            if t in FENCE and (blk := closed_block(text)) is not None:
                r["in_block"] = False
                if r["block_only"]:
                    r["blocks"].append({"block": blk})
                    r["forced"] = [IM_END]
                elif len(r["blocks"]) >= self.rounds:  # as gen.converse: past the last round the reply stops
                    r["forced"] = [IM_END]
                else:
                    lines = sheet_ref.run(blk)
                    r["blocks"].append({"block": blk, "result": lines})
                    r["forced"] = tok("\n" + "\n".join(lines) + "\n", add_special_tokens=False)["input_ids"]
        elif "sheet" in tok.decode([t]) and tok.decode(r["reply"][-4:]).rstrip("\n").endswith(OPEN):
            r["in_block"] = True
            if "switch_ids" not in r:
                r["switch_ids"] = r["prompt"] + r["reply"]

    def __call__(self, input_ids, scores):
        pick = scores.argmax(-1).tolist()
        chosen, gates = [], []
        for i, r in enumerate(self.rows):
            if r["done"]:
                t = PAD
            elif r["forced"]:
                t = r["forced"].pop(0)
                r["reply"].append(t)
                r["done"] = t in EOS
            else:
                t = pick[i]
                r["reply"].append(t)
                self.step(r, t)
            chosen.append(t)
            on = self.mode == "gate1" or (self.mode == "switch" and r["in_block"] and not r["forced"] and not r["done"])
            gates.append(SCALE if on else 0.0)
        self.G.copy_(torch.tensor(gates, dtype=self.G.dtype).view(-1, 1, 1))
        out = torch.full_like(scores, float("-inf"))
        out.scatter_(1, torch.tensor(chosen, device=scores.device).view(-1, 1), 0.0)
        return out


@torch.no_grad()
def run(prompts, writer, mode, rounds=2, max_new=640, batch=48, block_only=False):
    """Replies (text, blocks, and the token ids up to the first opener) for token-id prompts."""
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))  # as gen.generate: similar lengths per batch
    out = [None] * len(prompts)
    for k in range(0, len(order), batch):
        idx = order[k : k + batch]
        ids, mask = left_pad([prompts[i] for i in idx])
        G = torch.full((len(idx), 1, 1), SCALE if mode == "gate1" else 0.0, dtype=DTYPE, device=dev)
        use(writer, G)
        rows = [{"prompt": list(prompts[i]), "reply": [], "blocks": [], "forced": [], "in_block": block_only,
                 "done": False, "block_only": block_only} for i in idx]
        model.generate(input_ids=ids, attention_mask=mask, max_new_tokens=max_new, do_sample=False, pad_token_id=PAD,
                       eos_token_id=EOS, logits_processor=LogitsProcessorList([Switch(rows, G, mode, rounds)]))
        for r, i in zip(rows, idx):
            out[i] = {"text": tok.decode(r["reply"], skip_special_tokens=True).strip(), "blocks": r["blocks"],
                      "switch_ids": r.get("switch_ids"), "ids": r["reply"]}
    return out


def same_value(a, b):
    try:
        return a is not None and b is not None and Fraction(a) == Fraction(b)
    except (ValueError, ZeroDivisionError):
        return False


def line_right(d, blk):
    if d["family"] == "equation":
        return sheet_ref.run(blk)[-1] == "= " + d["result"]
    return same_value(sheet_ref.value(blk), d["truth"])


IFEVAL = None


def ifeval_rows():
    global IFEVAL
    if IFEVAL is None:
        from datasets import load_dataset

        IFEVAL = list(load_dataset("google/IFEval", split="train"))
    return IFEVAL


if "selftest" in parts:
    w = names[0]
    held = [json.loads(l) for l in open(pathlib.Path(args.data) / "heldout_full.jsonl")]
    probe = [chat_prefix(tok, messages(u)) for u in [held[0]["user"], held[-1]["user"]] +
             [d["prompt"] for d in ifeval_rows()[:2]]]
    ids, mask = left_pad(probe)
    real = mask.bool()
    with torch.no_grad():
        with model.disable_adapter():
            off = model(input_ids=ids, attention_mask=mask).logits
        use(w, SCALE)
        on = model(input_ids=ids, attention_mask=mask).logits
        G = torch.zeros((len(probe), 1, 1), dtype=DTYPE, device=dev)
        use(w, G)
        g0 = model(input_ids=ids, attention_mask=mask).logits
        G.fill_(SCALE)
        g1 = model(input_ids=ids, attention_mask=mask).logits
        G.copy_(torch.tensor([0.0, SCALE, 0.0, SCALE], dtype=DTYPE).view(-1, 1, 1))
        gm = model(input_ids=ids, attention_mask=mask).logits
    ref = torch.stack([off[0], on[1], off[2], on[3]])
    st = {"gate0_vs_disabled_maxdiff": float((g0 - off)[real].abs().max()),
          "gate0_bitwise": bool(torch.equal(g0[real], off[real])),
          "gate1_vs_float_scale_maxdiff": float((g1 - on)[real].abs().max()),
          "mixed_vs_single_maxdiff": float((gm - ref)[real].abs().max()),
          "mixed_bitwise": bool(torch.equal(gm[real], ref[real])),
          "adapter_moves_logits": float((on - off)[real].abs().max())}
    ife = [chat_prefix(tok, messages(d["prompt"])) for d in ifeval_rows()[:16]]
    with model.disable_adapter():
        plain = generate(model, tok, ife, max_new=256, batch=16)
    sw = run(ife, w, "switch", rounds=2, max_new=256, batch=16)
    st["gen16_rows_without_block"] = sum(o["switch_ids"] is None for o in sw)
    st["gen16_identical_without_block"] = sum(o["switch_ids"] is None and strip_pad(o["ids"]) == p
                                              for o, p in zip(sw, plain))
    words = [d for d in held if d["family"] == "word"][:8]
    sw8 = run([chat_prefix(tok, messages(d["user"])) for d in words], w, "switch", rounds=2, max_new=200, batch=8)
    st["word8_blocks_run"] = sum(len(o["blocks"]) for o in sw8)
    st["word8_right"] = sum(bool(o["blocks"]) and line_right(d, o["blocks"][0]["block"]) for d, o in zip(words, sw8))
    st["word8_first_reply"] = sw8[0]["text"]
    res["selftest"] = st
    save()
    if not (st["gate0_bitwise"] and st["mixed_vs_single_maxdiff"] < 1e-4 and st["word8_blocks_run"] and
            st["gen16_identical_without_block"] == st["gen16_rows_without_block"]):
        print("self-test failed: stopping before the evaluation", flush=True)
        sys.exit(1)

HELD = {}
if "heldout" in parts:
    held = [json.loads(l) for l in open(pathlib.Path(args.data) / "heldout_full.jsonl")]
    prompts = [chat_prefix(tok, messages(d["user"])) for d in held]
    for w in names:
        if not HELD:
            outs = run(prompts, w, "switch", rounds=2, max_new=640, batch=48)
        else:  # the prose before the first opener is stock's for every writer: rerun only where a block opened
            first = HELD[names[0]]
            again = [i for i, o in enumerate(first) if o["switch_ids"] is not None]
            outs = [dict(o) for o in first]
            for i, o in zip(again, run([prompts[i] for i in again], w, "switch", rounds=2, max_new=640, batch=48)):
                outs[i] = o
        HELD[w] = outs
        fam, tp, fp, fn = {}, 0, 0, 0
        for d, o in zip(held, outs):
            opened, need = bool(o["blocks"]), d["needs_sheet"]
            tp += opened and need
            fp += opened and not need
            fn += need and not opened
            f = fam.setdefault(d["family"], {"n": 0, "opened": 0, "line_right": 0, "quotes_value": 0})
            f["n"] += 1
            f["opened"] += opened
            right = False
            if need and opened:
                right = line_right(d, o["blocks"][0]["block"])
                last = o["blocks"][-1]["result"][-1][2:] if o["blocks"][-1]["result"] else None
                f["quotes_value"] += bool(last) and last in o["text"].split("```")[-1]
            if not need and d["sub"] == "single":
                right = str(d["single_value"]) in o["text"]
                f["single_right"] = f.get("single_right", 0) + right
                f["single_n"] = f.get("single_n", 0) + 1
            f["line_right"] += right
            SAMPLES.append({"part": "heldout", "writer": w, "id": d["id"], "family": d["family"], "sub": d["sub"],
                            "user": d["user"], "reply": o["text"], "blocks": o["blocks"], "opened": opened,
                            "right": right})
        res[f"heldout_{w}"] = {"open_precision": tp / max(1, tp + fp), "open_recall": tp / max(1, tp + fn),
                               "open_counts": {"tp": tp, "fp": fp, "fn": fn},
                               "families": {k: {**v, "line_rate": v["line_right"] / v["n"]} for k, v in fam.items()}}
        save()

GSM = {}


def gsm_rows():
    from datasets import load_dataset

    ds = list(load_dataset("openai/gsm8k", "main", split="test"))
    random.Random(0).shuffle(ds)
    return ds[:250]


SUFFIX = "\n\nSolve the problem. End with the final answer on its own line as 'Answer: <number>'."
if "gsm8k" in parts:
    ds = gsm_rows()
    prompts = [chat_prefix(tok, messages(d["question"] + SUFFIX)) for d in ds]
    for w in names:
        outs = run(prompts, w, "switch", rounds=10, max_new=1024, batch=48)
        GSM[w] = outs
        right = opened = 0
        for d, o in zip(ds, outs):
            want = float(d["answer"].split("####")[-1].strip().replace(",", ""))
            m = re.findall(r"Answer:\s*\$?(-?[\d,]*\.?\d+)", o["text"])
            got = float(m[-1].replace(",", "")) if m else last_number(o["text"])
            ok = got is not None and abs(got - want) < 1e-6
            right += ok
            opened += bool(o["blocks"])
            SAMPLES.append({"part": "gsm8k", "writer": w, "q": d["question"], "reply": o["text"], "want": want,
                            "got": got, "right": ok, "blocks": o["blocks"]})
        res[f"gsm8k_{w}"] = {"n": len(ds), "acc": right / len(ds), "opened_sheet": opened, "max_new": 1024,
                             "note": "sheet blocks run on sheet_ref.py, the host stand-in for the exact sheet"}
        save()

if "cache" in parts:
    held = [json.loads(l) for l in open(pathlib.Path(args.data) / "heldout_full.jsonl")]
    for w in names:
        if w not in HELD:
            continue
        pick = [i for i, o in enumerate(HELD[w]) if o["switch_ids"] is not None]
        again = run([HELD[w][i]["switch_ids"] for i in pick], w, "gate1", max_new=160, batch=48, block_only=True)
        same = r0 = r1 = scored = 0
        for i, a in zip(pick, again):
            b0 = HELD[w][i]["blocks"][0]["block"] if HELD[w][i]["blocks"] else None
            b1 = a["blocks"][0]["block"] if a["blocks"] else None
            same += b0 == b1
            if held[i]["needs_sheet"]:
                scored += 1
                r0 += b0 is not None and line_right(held[i], b0)
                r1 += b1 is not None and line_right(held[i], b1)
            if b0 != b1:
                SAMPLES.append({"part": "cache", "writer": w, "id": held[i]["id"], "family": held[i]["family"],
                                "gate0_cache": b0, "gate1_cache": b1})
        out = {"opened": len(pick), "identical_blocks": same, "scored": scored, "right_gate0_cache": r0,
               "right_gate1_cache": r1}
        if w in GSM:
            gp = [i for i, o in enumerate(GSM[w]) if o["switch_ids"] is not None]
            ga = run([GSM[w][i]["switch_ids"] for i in gp], w, "gate1", max_new=160, batch=48, block_only=True)
            out["gsm8k_first_blocks"] = len(gp)
            out["gsm8k_identical"] = sum((GSM[w][i]["blocks"][0]["block"] if GSM[w][i]["blocks"] else None) ==
                                         (a["blocks"][0]["block"] if a["blocks"] else None) for i, a in zip(gp, ga))
        res[f"cache_{w}"] = out
        save()

if "ifeval" in parts:
    from lm_eval.tasks.ifeval.utils import process_results

    ds = ifeval_rows()
    prompts = [chat_prefix(tok, messages(d["prompt"])) for d in ds]
    first = run(prompts, names[0], "switch", rounds=2, max_new=1280, batch=32)
    opened = [i for i, o in enumerate(first) if o["blocks"] or o["switch_ids"] is not None]
    variants = {names[0]: first}
    sub = [prompts[i] for i in opened]
    for mode, w in [("gate0", "stock_fewshot")] + [("switch", n) for n in names[1:]]:
        o = run(sub, names[0] if mode == "gate0" else w, mode, rounds=2, max_new=1280, batch=32) if sub else []
        variants[w] = [dict(x) for x in first]
        for i, x in zip(opened, o):
            variants[w][i] = x
    for w, outs in variants.items():
        strict = loose = inst_s = inst_n = 0
        for d, o in zip(ds, outs):
            r = process_results(d, [o["text"]])
            strict += r["prompt_level_strict_acc"]
            loose += r["prompt_level_loose_acc"]
            inst_s += sum(r["inst_level_strict_acc"])
            inst_n += len(r["inst_level_strict_acc"])
            SAMPLES.append({"part": "ifeval", "writer": w, "key": d["key"], "reply": o["text"],
                            "strict": r["prompt_level_strict_acc"], "opened": bool(o["blocks"])})
        res[f"ifeval_{w}"] = {"n": len(ds), "prompt_strict": strict / len(ds), "prompt_loose": loose / len(ds),
                              "inst_strict": inst_s / inst_n, "opened_sheet": sum(bool(o["blocks"]) for o in outs)}
    res["ifeval_opened_prompts"] = [ds[i]["key"] for i in opened]
    save()

if "mmlu" in parts:
    from datasets import load_dataset

    ds = list(load_dataset("cais/mmlu", "all", split="test"))
    random.Random(0).shuffle(ds)
    ds = ds[:500]
    letters = [tok.encode(c, add_special_tokens=False)[0] for c in "ABCD"]
    right = 0
    for k in range(0, len(ds), 32):
        chunk = ds[k : k + 32]
        seqs = []
        for d in chunk:
            q = (f"The following is a multiple choice question about {d['subject'].replace('_', ' ')}.\n\n"
                 f"{d['question']}\n" + "".join(f"{c}. {t}\n" for c, t in zip("ABCD", d["choices"])) +
                 "\nAnswer with the letter only.")
            seqs.append(chat_prefix(tok, messages(q)))
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), PAD, dtype=torch.long)  # right-padded, as chat_eval.py
        mask = torch.zeros_like(ids)
        for i, q in enumerate(seqs):
            ids[i, : len(q)] = torch.tensor(q)
            mask[i, : len(q)] = 1
        with torch.no_grad(), model.disable_adapter():
            lg = model(input_ids=ids.to(dev), attention_mask=mask.to(dev)).logits
        for i, (q, d) in enumerate(zip(seqs, chunk)):
            right += int(lg[i, len(q) - 1, letters].argmax()) == d["answer"]
    res["mmlu_gate0_sheet_prompt"] = {"n": len(ds), "acc": right / len(ds)}
    save()
print("done", round(time.time() - t0), "s", flush=True)
