"""T4: the chat fine-tune. One LoRA (continued from the sheet adapter) learns to write work orders in conversation
while keeping every table row certified and staying close to stock Qwen's chat.

Loss per step = CE on the model's turns of synthetic dialogues (the runtime's `= …` lines masked)
              + w_rows · (CE + margin hinge) on a stratified batch of table rows, plus replay of the rows that sat
                below hinge/2 at the last certificate (recipe v2 of e5_union, the sheet's own training loss)
              + w_kl · KL(stock || model) per token on stock's own replies to instruction prompts, the teacher being
                the same weights with the adapter disabled (self-distillation, Learning without Forgetting)
              + w_text · KL(stock || model) on plain text: PRIMER.md as in E4–E6, or (--text wikitext) 256-token
                chunks of Wikipedia articles (wikitext-2 train), which leaves PRIMER.md's perplexity an untrained measure
With --kl_full the instruction KL covers every position of prompt and reply, not only the reply.

  python chat/chat_train.py <data dir> <init adapter> <out name> [--steps 1200] [--lr 1e-4] [--w_kl 1.0] ...
writes <out name>/ (the adapter) with train_log.json; every --every steps it certifies all table rows and measures the
plain-text perplexity ratio.
"""

import argparse
import json
import pathlib
import random
import sys
import time

import torch
import torch.nn.functional as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e2_column as e2  # noqa: E402
from gen import chat_prefix  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("data")
ap.add_argument("init")
ap.add_argument("out")
ap.add_argument("--steps", type=int, default=1200)
ap.add_argument("--lr", type=float, default=1e-4)
ap.add_argument("--lr_end", type=float, default=1e-5)
ap.add_argument("--bd", type=int, default=8, help="dialogues per step")
ap.add_argument("--bk", type=int, default=4, help="KL prompts per step")
ap.add_argument("--w_rows", type=float, default=1.0)
ap.add_argument("--w_kl", type=float, default=1.0)
ap.add_argument("--w_text", type=float, default=1.0)
ap.add_argument("--hinge", type=float, default=4.0)
ap.add_argument("--maxlen", type=int, default=768)
ap.add_argument("--every", type=int, default=200)
ap.add_argument("--tables", default="e6", help="e6 (the 1,795 rows of E5/E6); E7's rows once CALC ships them")
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--repair", type=int, default=400, help="extra rows-only steps allowed if a row is lost at the end")
ap.add_argument("--kl_full", action="store_true", help="instruction KL on every position, prompt included")
ap.add_argument("--text", default="primer", choices=["primer", "wikitext"])
ap.add_argument("--bt", type=int, default=4, help="wikitext chunks per step")
ap.add_argument("--mc_kl", type=int, default=0, help="ARC multiple-choice prompts added to the KL pool (prompt only)")
args = ap.parse_args()

torch.manual_seed(args.seed)
rng = random.Random(args.seed)
tok = e2.tok
dev = e2.dev
IM_END = tok.convert_tokens_to_ids("<|im_end|>")
PAD = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

if args.tables == "e6":
    import e5_union as u
    import e6_slots  # noqa: F401  (one-forward multiplier rows)

    STRATA = {"MUL": 6, "ADD": 2, "ADZ": 2, "FLS": 1, "NXT": 1, "SUM": 4}
elif args.tables == "e7":  # CALC's E7 tables (e7_calc.py, calc_tables.py from the sketchpad worktree, see chat_modal)
    import e7_calc  # noqa: F401  (extends e5_union's rows to 2,446: SUB, EST, DEC)
    import e5_union as u

    STRATA = {"MUL": 6, "ADD": 2, "ADZ": 2, "FLS": 1, "NXT": 1, "SUM": 4, "SUB": 4, "EST": 6, "DEC": 1}
else:
    raise SystemExit(f"unknown tables {args.tables}")


# --- data -------------------------------------------------------------------------------------------------------------

def encode_dialogue(d):
    """(ids, labels) with labels -100 outside the model's last turn and on the runtime's result lines."""
    msgs = []
    if d.get("history"):
        msgs += [{"role": "user", "content": d["history"]["user"]},
                 {"role": "assistant", "content": d["history"]["assistant"]}]
    msgs.append({"role": "user", "content": d["user"]})
    ids = chat_prefix(tok, msgs)
    labels = [-100] * len(ids)
    segs = d["segments"] if d["segments"] else [[d["reply"], True]]
    for text, loss in segs:
        t = tok(text, add_special_tokens=False)["input_ids"]
        ids += t
        labels += t if loss else [-100] * len(t)
    if d["segments"] or d.get("reply_finished", True):
        ids.append(IM_END)
        labels.append(IM_END)
    return ids[: args.maxlen], labels[: args.maxlen]


D = pathlib.Path(args.data)
train = [json.loads(l) for l in open(D / "train_full.jsonl")]
dialogues = [encode_dialogue(d) for d in train]
kl = []  # (prompt + stock's reply, prompt length)
for line in open(D / "kl.jsonl"):
    k = json.loads(line)
    p = chat_prefix(tok, [{"role": "user", "content": k["user"]}])
    s = (p + k["reply_ids"])[: args.maxlen]
    if len(s) > len(p):
        kl.append((s, len(p)))
if args.mc_kl:  # stock's letter distribution on multiple-choice prompts (ARC train, worded unlike the MMLU evaluation)
    from datasets import load_dataset

    arc = [r for c in ("ARC-Easy", "ARC-Challenge") for r in load_dataset("allenai/ai2_arc", c, split="train")]
    random.Random(2).shuffle(arc)
    one = tok("A", add_special_tokens=False)["input_ids"]  # any token: the KL is on the distribution before it
    for r in arc[: args.mc_kl]:
        opts = "".join(f"{lab}) {t}\n" for lab, t in zip(r["choices"]["label"], r["choices"]["text"]))
        p = chat_prefix(tok, [{"role": "user", "content": f"{r['question']}\n\nOptions:\n{opts}\n"
                                                          "Reply with the letter of the correct option."}])
        kl.append((p + one, len(p)))
WIKI = []
if args.text == "wikitext":
    from datasets import load_dataset

    text = "\n".join(r["text"] for r in load_dataset("Salesforce/wikitext", "wikitext-2-raw-v1", split="train"))
    ids_ = tok(text, add_special_tokens=False)["input_ids"]
    WIKI = [ids_[i : i + 256] for i in range(0, len(ids_) - 256, 256)]
    random.Random(1).shuffle(WIKI)
    WIKI = WIKI[:2000]
print(f"dialogues {len(dialogues)}, kl prompts {len(kl)}, wikitext chunks {len(WIKI)}, tables {args.tables} ({len(u.ROWS)} rows)", flush=True)


def pad_batch(seqs, labels=None):
    L = max(len(s) for s in seqs)
    ids = torch.full((len(seqs), L), PAD, dtype=torch.long)
    mask = torch.zeros((len(seqs), L), dtype=torch.long)
    lab = torch.full((len(seqs), L), -100, dtype=torch.long)
    for i, s in enumerate(seqs):
        ids[i, : len(s)] = torch.tensor(s)
        mask[i, : len(s)] = 1
        if labels is not None:
            lab[i, : len(s)] = torch.tensor(labels[i])
    return ids.to(dev), mask.to(dev), lab.to(dev)


def dialogue_loss(model, batch):
    ids, mask, lab = pad_batch([b[0] for b in batch], [b[1] for b in batch])
    logits = model(input_ids=ids, attention_mask=mask).logits[:, :-1].float()
    return F.cross_entropy(logits.reshape(-1, logits.shape[-1]), lab[:, 1:].reshape(-1), ignore_index=-100)


def kl_loss(model, batch):
    """Mean per-token KL(stock || model) over the reply positions, teacher = adapter disabled."""
    ids, mask, _ = pad_batch([b[0] for b in batch])
    sel = torch.zeros_like(mask, dtype=torch.bool)
    for i, (s, p) in enumerate(batch):
        sel[i, (0 if args.kl_full else p - 1) : len(s) - 1] = True  # positions that predict the reply (or every token)
    with torch.no_grad(), model.disable_adapter():
        ref = model(input_ids=ids, attention_mask=mask).logits[sel].float().log_softmax(-1)
    cur = model(input_ids=ids, attention_mask=mask).logits[sel].float().log_softmax(-1)
    return F.kl_div(cur, ref, log_target=True, reduction="batchmean")


def rows_loss(model, rows):
    losses = [F.cross_entropy(lg, ans) + torch.relu(args.hinge - e2.margins(lg, ans)).mean()
              for lg, ans in u.row_logits(model, rows)]
    return torch.stack(losses).mean()


@torch.no_grad()
def checkpoint(model, ppl0, weak):
    model.eval()
    ok, by_op, mins, fails = u.certify(model, weak_below=args.hinge / 2, weak=weak)
    ppl = e2.text_ppl(model)
    model.train()
    return {"cert": ok, "rows": len(u.ROWS), "by_op": by_op, "min_margin": {k: round(v, 2) for k, v in mins.items()},
            "fails": fails[:12], "ppl_ratio": ppl / ppl0}


# --- train ------------------------------------------------------------------------------------------------------------

from peft import PeftModel  # noqa: E402

base = e2.load_base()
ppl0 = e2.text_ppl(base.eval())
model = PeftModel.from_pretrained(base, args.init, is_trainable=True)
params = [p for p in model.parameters() if p.requires_grad]
opt = torch.optim.AdamW(params, lr=args.lr)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.steps, eta_min=args.lr_end)
log, hard, t0 = [], [], time.time()
weak = []
log.append({"step": 0, **checkpoint(model, ppl0, weak), "seconds": 0})
hard = weak
print(json.dumps(log[-1]), flush=True)
model.train()


def step_rows():
    rows = [r for op, k in STRATA.items() for r in rng.sample(u.BY_OP[op], k)]
    if hard:
        rows += [rng.choice(hard) for _ in range(6)]
    return rows


step = 0
total = args.steps
while step < total:
    step += 1
    repair = step > args.steps
    parts = {}
    if not repair:
        ld = dialogue_loss(model, [dialogues[rng.randrange(len(dialogues))] for _ in range(args.bd)])
        ld.backward()
        parts["dialog"] = float(ld)
    lr_ = rows_loss(model, step_rows())
    (args.w_rows * lr_).backward()
    parts["rows"] = float(lr_)
    if args.w_kl:
        micro = [min(4, args.bk - k) for k in range(0, args.bk, 4)]  # micro-batches of 4 keep the logits in memory
        lk_sum = 0.0
        for m in micro:
            lk = kl_loss(model, [kl[rng.randrange(len(kl))] for _ in range(m)])
            (args.w_kl * lk * m / args.bk).backward()
            lk_sum += float(lk) * m / args.bk
        parts["kl"] = lk_sum
    if args.w_text:
        lt = kl_loss(model, [(WIKI[rng.randrange(len(WIKI))], 1) for _ in range(args.bt)]) if WIKI else e2.text_kl(model)
        (args.w_text * lt).backward()
        parts["text_kl"] = float(lt)
    torch.nn.utils.clip_grad_norm_(params, 1.0)
    opt.step()
    opt.zero_grad()
    if not repair:
        sched.step()
    if step % 20 == 0:
        print(json.dumps({"step": step, **{k: round(v, 4) for k, v in parts.items()},
                          "lr": opt.param_groups[0]["lr"], "s": round(time.time() - t0)}), flush=True)
    if step % args.every == 0 or step == total:
        weak = []
        c = checkpoint(model, ppl0, weak)
        hard = weak
        log.append({"step": step, "repair": repair, **parts, **c, "seconds": round(time.time() - t0)})
        print(json.dumps(log[-1]), flush=True)
        if step == total and c["cert"] < len(u.ROWS) and total < args.steps + args.repair:
            total = min(total + 100, args.steps + args.repair)  # rows-only repair, 100 steps at a time
            for g in opt.param_groups:
                g["lr"] = args.lr_end
            args.every = 100
model.save_pretrained(args.out)
json.dump({"log": log, "ppl0": ppl0, "args": vars(args)}, open(f"{args.out}/train_log.json", "w"), indent=1)
print("saved", args.out, flush=True)
