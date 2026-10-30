"""Stock Qwen's own replies for the chat fine-tune: the distractor turns of the synthetic dialogues and the prompts of
the self-distillation (KL) term. Greedy, thinking off, left-padded batches (checked against single-prompt generation
on 8 prompts first).

  python chat/stock_replies.py <data dir> [n_kl=1500]
reads <data dir>/train.jsonl and heldout.jsonl; writes train_full.jsonl (every turn has a reply), heldout_full.jsonl
(no_robots distractor prompts filled from the test split), kl.jsonl (instruction prompts and stock's replies) and
stock_check.json.

Prompt sources (HuggingFaceH4/no_robots): train-split first user turns, shuffled with seed 0; the distractor turns take
the first ones, the KL set the next n_kl; the held-out distractors take test-split prompts 100 onward (0-99 were the
T5 identity prompts). google/IFEval is never used here: it is held out for the evaluation.
"""

import json
import pathlib
import random
import sys

import torch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e2_column as e2  # noqa: E402
from gen import chat_prefix, generate  # noqa: E402

D = pathlib.Path(sys.argv[1])
N_KL = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
tok = e2.tok
model = e2.load_base().eval()
im_end = tok.convert_tokens_to_ids("<|im_end|>")


def prompts_from(split):
    from datasets import load_dataset

    ds = load_dataset("HuggingFaceH4/no_robots", split=split)
    return [r["messages"][0]["content"] for r in ds if r["messages"][0]["role"] == "user"]


train = [json.loads(l) for l in open(D / "train.jsonl")]
held = [json.loads(l) for l in open(D / "heldout.jsonl")]
nr = prompts_from("train")
random.Random(0).shuffle(nr)
nr = [p for p in nr if len(tok(p)["input_ids"]) < 400]
k = 0
for d in train:
    for turn in ([d] + ([d["history"]] if d.get("history") and d["history"].get("assistant") is None else [])):
        if turn.get("sub") == "no_robots" and turn.get("user") is None:
            turn["user"] = nr[k]
            k += 1
kl_prompts = nr[k : k + N_KL]
test = prompts_from("test")[100:]
j = 0
for d in held:
    if d.get("sub") == "no_robots" and d.get("user") is None:
        d["user"] = test[j]
        j += 1

# the batched generator must agree with single-prompt generation
probe = [[{"role": "user", "content": p}] for p in kl_prompts[:8]]
ids = [chat_prefix(tok, m) for m in probe]
bat = generate(model, tok, ids, max_new=96, batch=8)
one = [generate(model, tok, [x], max_new=96, batch=1)[0] for x in ids]
agree = [a == b for a, b in zip(bat, one)]
prefix = [next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b))) for a, b in zip(bat, one)]
json.dump({"batched_equals_single": agree, "first_difference_at": prefix}, open("stock_check.json", "w"))
print("batched vs single:", agree, prefix, flush=True)

jobs = []  # (conversation, setter)
for d in train:
    h = d.get("history")
    hist = []
    if h:
        if h.get("assistant") is None:
            jobs.append(([{"role": "user", "content": h["user"]}], (h, "assistant")))
    if d["family"] == "distract":
        jobs.append((None, (d, "reply")))  # after the history is filled
first = [j for j in jobs if j[0] is not None]
outs = generate(model, tok, [chat_prefix(tok, c) for c, _ in first], max_new=512)
for (c, (obj, key)), o in zip(first, outs):
    obj[key] = tok.decode(o, skip_special_tokens=True).strip()
    obj[key + "_finished"] = bool(o) and o[-1] == im_end
print("history turns", len(first), flush=True)

second = []
for c, (d, key) in jobs:
    if c is None:
        msgs = []
        if d.get("history"):
            msgs += [{"role": "user", "content": d["history"]["user"]},
                     {"role": "assistant", "content": d["history"]["assistant"]}]
        msgs.append({"role": "user", "content": d["user"]})
        second.append((msgs, d))
outs = generate(model, tok, [chat_prefix(tok, m) for m, _ in second], max_new=512)
wrong_single = 0
for (m, d), o in zip(second, outs):
    d["reply"] = tok.decode(o, skip_special_tokens=True).strip()
    d["reply_finished"] = bool(o) and o[-1] == im_end
    if d["sub"] == "single" and str(d["single_value"]) not in d["reply"]:
        wrong_single += 1
        d["reply"] = f"{d['single_value']}."
        d["reply_finished"] = True
print("distractor turns", len(second), "single-digit fallbacks", wrong_single, flush=True)
with open("train_full.jsonl", "w") as f:
    for d in train:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
with open("heldout_full.jsonl", "w") as f:
    for d in held:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

outs = generate(model, tok, [chat_prefix(tok, [{"role": "user", "content": p}]) for p in kl_prompts], max_new=384)
with open("kl.jsonl", "w") as f:
    for p, o in zip(kl_prompts, outs):
        f.write(json.dumps({"user": p, "reply_ids": o, "finished": bool(o) and o[-1] == im_end}, ensure_ascii=False)
                + "\n")
print("kl prompts", len(kl_prompts), "finished", sum(bool(o) and o[-1] == im_end for o in outs), flush=True)
