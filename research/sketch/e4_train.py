"""E4 training/eval: Qwen3.5-0.8B + LoRA learns all five canvas ops of long multiplication (1,553 table rows).
Per tick: prompt "<OP><vision 3 tok>=", three output tokens (glyph, glyph, next-op), teacher-forced with a margin hinge
on each; whole domain sampled every step (certificate as loss); KL to the base on plain text (retention).

usage: e4_train.py train <steps> <seed> <kl> | e4_train.py eval <adapter>
"""

import json
import random
import sys
import time

import torch
from peft import LoraConfig, PeftModel, get_peft_model

import e2_column as e2
from e2_column import crop, dev, proc, tok
from e4_mul import B, domain, ref, run

DOMAIN = domain()
BY_OP = {}
for _r in DOMAIN:
    BY_OP.setdefault(_r[0], []).append(_r)
# per-step batch stratified by op: the 2-row FLS and 11-row NXT tables are otherwise almost never drawn
STRATA = {"MUL": 10, "ADD": 2, "ADZ": 2, "FLS": 1, "NXT": 1}


def sample_batch(rng):
    return [r for op, k in STRATA.items() for r in rng.sample(BY_OP[op], k)]


def out_chars(op, v):
    g1, g2, nxt = ref(op, v)
    return ["_" if g1 == B else g1, g2, nxt]


CHAR_ID = {}
for ch in "0123456789_-MAZFNH":
    ids = tok.encode(ch, add_special_tokens=False)
    assert len(ids) == 1, (ch, ids)
    CHAR_ID[ch] = ids[0]
ID_CHAR = {v: k for k, v in CHAR_ID.items()}
CACHE = {}


def example(op, v):
    key = (op, v)
    if key not in CACHE:
        prompt = f"{op}<|vision_start|><|image_pad|><|vision_end|>="
        inp = proc(text=[prompt], images=[crop(*v)], return_tensors="pt")
        ans = [CHAR_ID[c] for c in out_chars(op, v)]
        p = inp["input_ids"].shape[1]
        for k, t in list(inp.items()):
            if torch.is_tensor(t) and t.dim() == 2 and t.shape == (1, p):
                ext = torch.tensor([ans]) if k == "input_ids" else torch.full((1, len(ans)), int(k == "attention_mask"))
                inp[k] = torch.cat([t, ext.to(t.dtype)], 1)
        CACHE[key] = ({k: t.to(dev) for k, t in inp.items()}, p, torch.tensor(ans, device=dev))
    return CACHE[key]


def answer_logits(model, op, v):
    inp, p, ans = example(op, v)
    return model(**inp).logits[0, p - 1 : p - 1 + len(ans)].float(), ans


@torch.no_grad()
def certify(model, rows=None):
    by_op, mins, fails = {}, {}, []
    for op, v in rows or DOMAIN:
        lg, ans = answer_logits(model, op, v)
        m = float(e2.margins(lg, ans).min())
        by_op[op] = by_op.get(op, 0) + (m > 0)
        mins[op] = min(mins.get(op, 1e9), m)
        if m <= 0:
            fails.append(f"{op}:{''.join(v).replace(B, '_')}")
    return sum(by_op.values()), by_op, mins, fails


def train(steps=800, batch=16, lr=2e-4, hinge=2.0, seed=0, kl=1.0, every=100):
    torch.manual_seed(seed)
    random.seed(seed)
    rng = random.Random(seed)
    base = e2.load_base()
    ppl0 = e2.text_ppl(base.eval())
    targets = r"model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|linear_attn\.(in_proj_qkv|in_proj_z|out_proj)|mlp\.(gate|up|down)_proj)"
    model = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, target_modules=targets))
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    log, t0 = [], time.time()
    for step in range(1, steps + 1):
        model.train()
        tot = 0.0
        for op, v in sample_batch(rng):
            lg, ans = answer_logits(model, op, v)
            loss = torch.nn.functional.cross_entropy(lg, ans) + torch.relu(hinge - e2.margins(lg, ans)).mean()
            (loss / batch).backward()
            tot += float(loss)
        if kl:
            (kl * e2.text_kl(model)).backward()
        opt.step()
        opt.zero_grad()
        if step % every == 0 or step == steps:
            model.eval()
            ok, by_op, mins, fails = certify(model)
            log.append({"step": step, "loss": tot / batch, "cert": ok, "by_op": by_op,
                        "min_margin": {k: round(v, 2) for k, v in mins.items()}, "ppl_ratio": e2.text_ppl(model) / ppl0,
                        "fails": fails[:12]})
            print(json.dumps(log[-1]), f"({time.time() - t0:.0f}s)", flush=True)
            if ok == len(DOMAIN) and min(mins.values()) >= hinge / 2:
                break
    out = f"e4_adapter_s{seed}"
    model.save_pretrained(out)
    json.dump({"log": log, "ppl0": ppl0, "rows": len(DOMAIN)}, open(f"{out}/train_log.json", "w"), indent=1)


def model_policy(model):
    @torch.no_grad()
    def policy(op, v):
        prompt = f"{op}<|vision_start|><|image_pad|><|vision_end|>="
        inp = {k: t.to(dev) for k, t in proc(text=[prompt], images=[crop(*v)], return_tensors="pt").items()}
        out = []
        for _ in range(3):  # greedy, 3 tokens
            nxt = int(model(**inp).logits[0, -1].argmax())
            out.append(ID_CHAR.get(nxt, "?"))
            L = inp["input_ids"].shape[1]
            for k, t in list(inp.items()):
                if torch.is_tensor(t) and t.dim() == 2 and t.shape == (1, L):
                    ext = torch.tensor([[nxt]], device=dev) if k == "input_ids" else torch.full((1, 1), int(k == "attention_mask"), device=dev, dtype=t.dtype)
                    inp[k] = torch.cat([t, ext.to(t.dtype)], 1)
        g1 = B if out[0] == "_" else out[0]
        return g1, out[1], out[2]

    return policy


def evaluate(adapter):
    model = PeftModel.from_pretrained(e2.load_base(), adapter).eval()
    ok, by_op, mins, fails = certify(model)
    res = {"cert": ok, "rows": len(DOMAIN), "by_op": by_op, "min_margin": mins, "fails": fails[:20], "ppl": e2.text_ppl(model)}
    print(json.dumps(res), flush=True)
    pol, rng = model_policy(model), random.Random(1)
    for n, k in ((4, 10), (6, 5), (10, 2)):
        good = 0
        for _ in range(k):
            a, b = (str(rng.randint(10 ** (n - 1), 10**n - 1)) for _ in range(2))
            got, ticks, _ = run(a, b, pol)
            good += got == str(int(a) * int(b))
        res[f"mul_{n}x{n}"] = f"{good}/{k}"
        print(n, res[f"mul_{n}x{n}"], flush=True)
    json.dump(res, open(f"{adapter}/eval.json", "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "train":
        a = sys.argv[2:] + [None] * 3
        train(steps=int(a[0] or 800), seed=int(a[1] or 0), kl=float(a[2] or 1.0))
    else:
        evaluate(sys.argv[2])
