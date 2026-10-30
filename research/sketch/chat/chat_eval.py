"""T4 evaluation: one model (stock, or stock + adapter = gate 1) on the registered measures.

  heldout  the held-out templates of every family (heldout_full.jsonl): does it open the sheet (precision, recall),
           is the sheet line right (scored by running it through sheet_ref.py, the host stand-in for the sheet), does
           the reply quote the runtime's value; distractors: single-digit answers right
  ifeval   google/IFEval (541 prompts), strict and loose prompt-level accuracy (lm-eval's IFEval checker); the sheet
           runs (stand-in) if the model opens it
  mmlu     cais/mmlu, 500 test questions (seed 0), zero-shot, the letter with the highest logit after the chat prompt
  gsm8k    openai/gsm8k test, 250 problems (seed 0), the last number of the reply; blocks run on the stand-in
  core     plain-text perplexity (PRIMER.md, ratio to stock) and the table-row certificate (adapter only)

  python chat/chat_eval.py <data dir> <adapter|none> <tag> [--fewshot] [--parts heldout,ifeval,mmlu,gsm8k,core]
writes eval_<tag>.json and samples_<tag>.jsonl
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

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e2_column as e2  # noqa: E402
import sheet_ref  # noqa: E402
from gen import chat_prefix, converse, generate, last_number  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("data")
ap.add_argument("adapter")
ap.add_argument("tag")
ap.add_argument("--fewshot", action="store_true", help="stock baseline: a system prompt and four example exchanges")
ap.add_argument("--parts", default="core,heldout,ifeval,mmlu,gsm8k")
ap.add_argument("--n_mmlu", type=int, default=500)
ap.add_argument("--n_gsm", type=int, default=250)
ap.add_argument("--n_ifeval", type=int, default=541)
ap.add_argument("--tables", default="e6")
args = ap.parse_args()
parts = args.parts.split(",")
tok = e2.tok
t0 = time.time()
res = {"tag": args.tag, "adapter": args.adapter, "fewshot": args.fewshot}
SAMPLES = []


def save():
    res["seconds"] = round(time.time() - t0)
    json.dump(res, open(f"eval_{args.tag}.json", "w"), indent=1)
    with open(f"samples_{args.tag}.jsonl", "w") as f:
        for s in SAMPLES:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "heldout_detail"}), flush=True)


base = e2.load_base().eval()
model = base
if args.adapter != "none":
    from peft import PeftModel

    model = PeftModel.from_pretrained(base, args.adapter).eval()

if "core" in parts:
    if args.adapter != "none":
        with model.disable_adapter():
            ppl0 = e2.text_ppl(model)
        res["ppl"], res["ppl_stock"] = e2.text_ppl(model), ppl0
        res["ppl_ratio"] = res["ppl"] / ppl0
        if args.tables == "e7":
            import e7_calc  # noqa: F401
        import e5_union as u
        import e6_slots  # noqa: F401
        ok, by_op, mins, fails = u.certify(model)
        res["rows"] = {"cert": ok, "of": len(u.ROWS), "by_op": by_op, "min_margin": mins, "fails": fails[:20]}
    else:
        res["ppl"] = e2.text_ppl(model)
    save()

if args.adapter != "none":
    model = model.merge_and_unload().eval()  # generation on merged weights (same function, fewer kernels)

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
    if not args.fewshot:
        return [{"role": "user", "content": user}]
    m = [{"role": "system", "content": FEW_SYSTEM}]
    for q, a in FEW_SHOTS:
        m += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
    return m + [{"role": "user", "content": user}]


def same_value(a, b):
    try:
        return a is not None and b is not None and Fraction(a) == Fraction(b)
    except (ValueError, ZeroDivisionError):
        return False


if "heldout" in parts:
    held = [json.loads(l) for l in open(pathlib.Path(args.data) / "heldout_full.jsonl")]
    outs = converse(model, tok, [chat_prefix(tok, messages(d["user"])) for d in held], sheet_ref.run, max_new=320,
                    rounds=2)
    fam = {}
    tp = fp = fn = 0
    for d, o in zip(held, outs):
        opened = bool(o["blocks"])
        need = d["needs_sheet"]
        tp += opened and need
        fp += opened and not need
        fn += need and not opened
        f = fam.setdefault(d["family"], {"n": 0, "opened": 0, "line_right": 0, "quotes_value": 0})
        f["n"] += 1
        f["opened"] += opened
        right = False
        if need and opened:
            blk = o["blocks"][0]["block"]
            if d["family"] == "equation":
                right = sheet_ref.run(blk)[-1] == "= " + d["result"]
            else:
                right = same_value(sheet_ref.value(blk), d["truth"])
            last = o["blocks"][-1]["result"][-1][2:] if o["blocks"][-1]["result"] else None
            f["quotes_value"] += bool(last) and last in o["text"].split("```")[-1]
        if not need and d["sub"] == "single":
            right = str(d["single_value"]) in o["text"]
            f.setdefault("single_right", 0)
            f.setdefault("single_n", 0)
            f["single_right"] += right
            f["single_n"] += 1
        f["line_right"] += right
        SAMPLES.append({"part": "heldout", "id": d["id"], "family": d["family"], "sub": d["sub"], "user": d["user"],
                        "reply": o["text"], "blocks": o["blocks"], "opened": opened, "right": right,
                        "want": d.get("lines")})
    res["open_precision"] = tp / max(1, tp + fp)
    res["open_recall"] = tp / max(1, tp + fn)
    res["open_counts"] = {"tp": tp, "fp": fp, "fn": fn}
    res["families"] = {k: {**v, "line_rate": v["line_right"] / v["n"]} for k, v in fam.items()}
    save()

if "ifeval" in parts:
    from datasets import load_dataset
    from lm_eval.tasks.ifeval.utils import process_results

    ds = list(load_dataset("google/IFEval", split="train"))[: args.n_ifeval]
    outs = converse(model, tok, [chat_prefix(tok, [{"role": "user", "content": d["prompt"]}]) for d in ds],
                    sheet_ref.run, max_new=1280, rounds=2, batch=32)
    strict = loose = inst_s = inst_n = opened = 0
    for d, o in zip(ds, outs):
        r = process_results(d, [o["text"]])
        strict += r["prompt_level_strict_acc"]
        loose += r["prompt_level_loose_acc"]
        inst_s += sum(r["inst_level_strict_acc"])
        inst_n += len(r["inst_level_strict_acc"])
        opened += bool(o["blocks"])
        SAMPLES.append({"part": "ifeval", "key": d["key"], "reply": o["text"], "strict": r["prompt_level_strict_acc"],
                        "opened": bool(o["blocks"])})
    n = len(ds)
    res["ifeval"] = {"n": n, "prompt_strict": strict / n, "prompt_loose": loose / n, "inst_strict": inst_s / inst_n,
                     "opened_sheet": opened}
    save()

if "mmlu" in parts:
    from datasets import load_dataset

    ds = list(load_dataset("cais/mmlu", "all", split="test"))
    random.Random(0).shuffle(ds)
    ds = ds[: args.n_mmlu]
    letters = [tok.encode(c, add_special_tokens=False)[0] for c in "ABCD"]
    right = 0
    dev = next(model.parameters()).device
    for k in range(0, len(ds), 32):
        chunk = ds[k : k + 32]
        seqs = []
        for d in chunk:
            q = (f"The following is a multiple choice question about {d['subject'].replace('_', ' ')}.\n\n"
                 f"{d['question']}\n" + "".join(f"{c}. {t}\n" for c, t in zip("ABCD", d["choices"])) +
                 "\nAnswer with the letter only.")
            seqs.append(chat_prefix(tok, [{"role": "user", "content": q}]))
        L = max(map(len, seqs))
        ids = torch.full((len(seqs), L), tok.pad_token_id, dtype=torch.long)
        mask = torch.zeros_like(ids)
        for i, s in enumerate(seqs):
            ids[i, : len(s)] = torch.tensor(s)
            mask[i, : len(s)] = 1
        with torch.no_grad():
            lg = model(input_ids=ids.to(dev), attention_mask=mask.to(dev)).logits
        for i, (s, d) in enumerate(zip(seqs, chunk)):
            pick = int(lg[i, len(s) - 1, letters].argmax())
            right += pick == d["answer"]
    res["mmlu"] = {"n": len(ds), "acc": right / len(ds)}
    save()

if "gsm8k" in parts:
    from datasets import load_dataset

    ds = list(load_dataset("openai/gsm8k", "main", split="test"))
    random.Random(0).shuffle(ds)
    ds = ds[: args.n_gsm]
    suffix = "\n\nSolve the problem. End with the final answer on its own line as 'Answer: <number>'."
    outs = converse(model, tok, [chat_prefix(tok, [{"role": "user", "content": d["question"] + suffix}]) for d in ds],
                    sheet_ref.run, max_new=640, rounds=4, batch=48)
    right = opened = 0
    for d, o in zip(ds, outs):
        want = float(d["answer"].split("####")[-1].strip().replace(",", ""))
        m = re.findall(r"Answer:\s*\$?(-?[\d,]*\.?\d+)", o["text"])
        got = float(m[-1].replace(",", "")) if m else last_number(o["text"])
        ok = got is not None and abs(got - want) < 1e-6
        right += ok
        opened += bool(o["blocks"])
        SAMPLES.append({"part": "gsm8k", "q": d["question"], "reply": o["text"], "want": want, "got": got, "right": ok,
                        "blocks": o["blocks"]})
    res["gsm8k"] = {"n": len(ds), "acc": right / len(ds), "opened_sheet": opened,
                    "note": "sheet blocks run on sheet_ref.py, the host stand-in for the exact sheet"}
    save()
print("done", round(time.time() - t0), "s", flush=True)
