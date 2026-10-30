"""E2b: the column adder in the fast tick format. No chat template: the prompt is "ADD" + the fovea image + "=", and
the model writes ONE token: the sum digit 0-9 when there is no carry, a-j for digit 0-9 with a carry, H to halt.
So a tick is a single short forward pass. Same domain (242 crops), same painter, same training recipe as e2_column.py.

usage: e2b_fast.py train <steps> <seed> <kl> | e2b_fast.py eval <adapter_dir>
"""

import json
import math
import random
import sys
import time

import torch
from peft import LoraConfig, PeftModel, get_peft_model

import e2_column as e2
from e2_column import BLANK, DOMAIN, crop, dev, proc, tok

PROMPT = "ADD<|vision_start|><|image_pad|><|vision_end|>="


def code(x):
    r = e2.rule(*x)
    return r if r == "H" else (r[0] if r[1] == "0" else "abcdefghij"[int(r[0])])


def decode(t):
    if t == "H":
        return None
    return (t, "0") if t.isdigit() else (str("abcdefghij".index(t)), "1")


TARGETS = sorted({code(x) for x in DOMAIN})
TIDS = [tok.encode(t, add_special_tokens=False) for t in TARGETS]
assert all(len(t) == 1 for t in TIDS), TIDS
TID = {t: i[0] for t, i in zip(TARGETS, TIDS)}

CACHE = {}


def example(x):
    if x not in CACHE:
        inp = proc(text=[PROMPT], images=[crop(*x)], return_tensors="pt")
        CACHE[x] = ({k: v.to(dev) for k, v in inp.items()}, TID[code(x)])
    return CACHE[x]


def logits_of(model, x):
    inp, t = example(x)
    return model(**inp).logits[0, -1].float(), t


def margin(logits, t):
    other = logits.clone()
    other[t] = float("-inf")
    return logits[t] - other.max()


@torch.no_grad()
def certify(model):
    ms = [float(margin(*logits_of(model, x))) for x in DOMAIN]
    return sum(m > 0 for m in ms), min(ms)


def train(steps=300, batch=16, lr=2e-4, hinge=2.0, seed=0, kl=1.0):
    torch.manual_seed(seed)
    rng = random.Random(seed)
    random.seed(seed)
    base = e2.load_base()
    ppl0 = e2.text_ppl(base.eval())
    ok0, m0 = certify(base)
    print(f"untouched: {ok0}/242 (min margin {m0:.2f}), ppl {ppl0:.2f}", flush=True)
    targets = r"model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|linear_attn\.(in_proj_qkv|in_proj_z|out_proj)|mlp\.(gate|up|down)_proj)"
    model = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, target_modules=targets))
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    log, t0 = [], time.time()
    for step in range(1, steps + 1):
        model.train()
        tot = 0.0
        for x in rng.sample(DOMAIN, batch):
            lg, t = logits_of(model, x)
            loss = torch.nn.functional.cross_entropy(lg[None], torch.tensor([t], device=dev)) + torch.relu(hinge - margin(lg, t))
            (loss / batch).backward()
            tot += float(loss)
        if kl:
            (kl * e2.text_kl(model)).backward()
        opt.step()
        opt.zero_grad()
        if step % 25 == 0 or step == steps:
            model.eval()
            ok, mn = certify(model)
            log.append({"step": step, "loss": tot / batch, "cert": ok, "min_margin": mn, "ppl_ratio": e2.text_ppl(model) / ppl0})
            print(json.dumps(log[-1]), f"({time.time() - t0:.0f}s)", flush=True)
            if ok == 242 and mn >= hinge / 2:
                break
    out = f"e2b_adapter_s{seed}"
    model.save_pretrained(out)
    json.dump({"prompt": PROMPT, "targets": TARGETS, "log": log, "ppl0": ppl0}, open(f"{out}/train_log.json", "w"), indent=1)


@torch.no_grad()
def run_sum(model, a, b):
    n = max(len(a), len(b)) + 1
    carry, top, bot, out = [BLANK] * n, list(a.rjust(n, BLANK)), list(b.rjust(n, BLANK)), [BLANK] * n
    for i in range(n - 1, -1, -1):
        inp = proc(text=[PROMPT], images=[crop(carry[i], top[i], bot[i])], return_tensors="pt")
        t = tok.decode([int(model(**{k: v.to(dev) for k, v in inp.items()}).logits[0, -1].argmax())])
        d = decode(t)
        if d is None:
            break
        out[i] = d[0]
        if i > 0:
            carry[i - 1] = "1" if d[1] == "1" else BLANK
    return "".join(out).strip()


def evaluate(adapter):
    model = PeftModel.from_pretrained(e2.load_base(), adapter).eval()
    ok, mn = certify(model)
    res = {"cert": ok, "min_margin": mn, "ppl": e2.text_ppl(model)}
    rng = random.Random(1)
    for n, k in ((10, 20), (100, 5), (1000, 2)):
        good = sum(run_sum(model, a, b) == str(int(a) + int(b))
                   for a, b in ((str(rng.randint(10 ** (n - 1), 10**n - 1)), str(rng.randint(10 ** (n - 1), 10**n - 1))) for _ in range(k)))
        res[f"sum_{n}"] = f"{good}/{k}"
        print(n, res[f"sum_{n}"], flush=True)
    json.dump(res, open(f"{adapter}/eval.json", "w"), indent=1)
    print(json.dumps(res))


if __name__ == "__main__":
    if sys.argv[1] == "train":
        a = sys.argv[2:] + [None] * 3
        train(steps=int(a[0] or 300), seed=int(a[1] or 0), kl=float(a[2] or 1.0))
    else:
        evaluate(sys.argv[2])
