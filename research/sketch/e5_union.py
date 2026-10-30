"""E5: ONE adapter for both programs. Qwen3.5-0.8B + LoRA learns the fast column adder (opcode SUM, one output token:
0-9, a-j with carry, H) and all five long-multiplication ops (MUL ADD ADZ FLS NXT, three output tokens), 1,795 table
rows in all, so the page loads one model for both modes. Same recipe as E4 (whole domain sampled by op every step,
margin hinge, KL to the base on plain text, stop when every row clears hinge/2), plus gradient clipping, and a BATCHED
teacher-forced forward (one call per step instead of one per row), checked against single forwards before training.

usage: e5_union.py check | e5_union.py train <steps> <seed> <hinge> | e5_union.py eval <adapter>
"""

import json
import random
import sys
import time

import torch
from peft import LoraConfig, PeftModel, get_peft_model

import e2_column as e2
from e2_column import crop, proc, tok
from e4_mul import B, domain, ref, run

dev = e2.dev
DIG = "0123456789"


def sum_code(v):
    r = e2.rule(*v)
    return r if r == "H" else (r[0] if r[1] == "0" else "abcdefghij"[int(r[0])])


def answer(op, v):
    if op == "SUM":
        return [sum_code(v)]
    g1, g2, n = ref(op, v)
    return ["_" if g1 == B else g1, g2, n]


ROWS = [("SUM", (c, t, b)) for c in (B, "1") for t in B + DIG for b in B + DIG] + domain()
BY_OP = {}
for r in ROWS:
    BY_OP.setdefault(r[0], []).append(r)
STRATA = {"MUL": 10, "ADD": 2, "ADZ": 2, "FLS": 1, "NXT": 1, "SUM": 4}
CHAR_ID = {}
for ch in DIG + "_-MAZFNH" + "abcdefghij":
    ids = tok.encode(ch, add_special_tokens=False)
    assert len(ids) == 1, (ch, ids)
    CHAR_ID[ch] = ids[0]
ID_CHAR = {v: k for k, v in CHAR_ID.items()}
PAD = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
PROMPT = {}


def prompt_inputs(op, v):
    """Processor output for one row's prompt (no answer), cached on CPU."""
    key = (op, v)
    if key not in PROMPT:
        PROMPT[key] = proc(text=[f"{op}<|vision_start|><|image_pad|><|vision_end|>="], images=[crop(*v)], return_tensors="pt")
    return PROMPT[key]


def batch(rows):
    """Right-padded teacher-forced batch; returns model inputs and, per row, (answer positions, answer ids)."""
    seqs, mms, pvs, thws, spans = [], [], [], [], []
    for op, v in rows:
        p = prompt_inputs(op, v)
        ans = [CHAR_ID[c] for c in answer(op, v)]
        ids = p["input_ids"][0].tolist() + ans
        mm = p["mm_token_type_ids"][0].tolist() + [0] * len(ans)
        n = p["input_ids"].shape[1]
        seqs.append(ids)
        mms.append(mm)
        pvs.append(p["pixel_values"])
        thws.append(p["image_grid_thw"])
        spans.append((list(range(n - 1, n - 1 + len(ans))), ans))
    L = max(len(s) for s in seqs)
    input_ids = torch.full((len(rows), L), PAD, dtype=torch.long)
    mask = torch.zeros((len(rows), L), dtype=torch.long)
    mm = torch.zeros((len(rows), L), dtype=torch.long)
    for i, (s, m) in enumerate(zip(seqs, mms)):
        input_ids[i, : len(s)] = torch.tensor(s)
        mask[i, : len(s)] = 1
        mm[i, : len(m)] = torch.tensor(m)
    inp = {"input_ids": input_ids, "attention_mask": mask, "mm_token_type_ids": mm,
           "pixel_values": torch.cat(pvs), "image_grid_thw": torch.cat(thws)}
    return {k: t.to(dev) for k, t in inp.items()}, spans


def row_logits(model, rows):
    """List of (logits over the answer positions, answer ids) per row, from one batched forward."""
    inp, spans = batch(rows)
    logits = model(**inp).logits.float()
    return [(logits[i, pos], torch.tensor(ans, device=dev)) for i, (pos, ans) in enumerate(spans)]


@torch.no_grad()
def certify(model, chunk=64, weak_below=None, weak=None):
    """Whole-table certificate. If `weak` is a list, rows with margin < weak_below are appended to it."""
    by_op, mins, fails = {}, {}, []
    for k in range(0, len(ROWS), chunk):
        part = ROWS[k : k + chunk]
        for (op, v), (lg, ans) in zip(part, row_logits(model, part)):
            m = float(e2.margins(lg, ans).min())
            by_op[op] = by_op.get(op, 0) + (m > 0)
            mins[op] = min(mins.get(op, 1e9), m)
            if m <= 0:
                fails.append(f"{op}:{''.join(v).replace(B, '_')}")
            if weak is not None and m < weak_below:
                weak.append((op, v))
    return sum(by_op.values()), by_op, mins, fails


@torch.no_grad()
def check(n=12):
    """Batched teacher-forced logits must match single-row forwards."""
    model = e2.load_base().eval()
    rng = random.Random(0)
    rows = [r for op in BY_OP for r in rng.sample(BY_OP[op], 2)][:n]
    bat = row_logits(model, rows)
    worst = 0.0
    for r, (lg, _) in zip(rows, bat):
        single, _ = row_logits(model, [r])[0]
        worst = max(worst, float((single - lg).abs().max()))
    print(f"batched vs single: max |logit diff| over {len(rows)} rows = {worst:.2e}")
    assert worst < 1e-2, "batched forward disagrees with single forwards"


STRATA2 = {"MUL": 20, "ADD": 4, "ADZ": 4, "FLS": 1, "NXT": 2, "SUM": 6}  # recipe v2: twice the batch


def train(steps=1500, seed=0, hinge=4.0, kl=1.0, lr=2e-4, clip=1.0, every=100, v2=False, init=None, lr_end=2e-5, replay=6, stop=None):
    """v2 (after the E5 plateau): cosine lr decay to lr_end, the batch doubled (STRATA2), and certificate-driven replay:
    the rows that failed or sat below hinge/2 at the last certificate fill `replay` extra slots of every batch.
    init: continue from an existing adapter directory instead of a fresh LoRA."""
    torch.manual_seed(seed)
    random.seed(seed)
    rng = random.Random(seed)
    base = e2.load_base()
    ppl0 = e2.text_ppl(base.eval())
    targets = r"model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|linear_attn\.(in_proj_qkv|in_proj_z|out_proj)|mlp\.(gate|up|down)_proj)"
    if init:
        model = PeftModel.from_pretrained(base, init, is_trainable=True)
    else:
        model = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, target_modules=targets))
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps, eta_min=lr_end) if v2 else None
    strata = STRATA2 if v2 else STRATA
    hard = []  # rows below hinge/2 at the last certificate
    log, t0 = [], time.time()
    out = f"e5_adapter_s{seed}_h{hinge:g}" + ("_v2" if v2 else "") + ("_cont" if init else "")
    for step in range(1, steps + 1):
        model.train()
        rows = [r for op, k in strata.items() for r in rng.sample(BY_OP[op], k)]
        if v2 and hard:
            rows += [rng.choice(hard) for _ in range(replay)]
        losses = [torch.nn.functional.cross_entropy(lg, ans) + torch.relu(hinge - e2.margins(lg, ans)).mean()
                  for lg, ans in row_logits(model, rows)]
        loss = torch.stack(losses).mean()
        loss.backward()
        if kl:
            (kl * e2.text_kl(model)).backward()
        torch.nn.utils.clip_grad_norm_(params, clip)
        opt.step()
        opt.zero_grad()
        if sched:
            sched.step()
        if step % every == 0 or step == steps:
            model.eval()
            weak = [] if v2 else None
            ok, by_op, mins, fails = certify(model, weak_below=hinge / 2, weak=weak)
            if v2:
                hard = weak
            log.append({"step": step, "loss": float(loss), "cert": ok, "rows": len(ROWS), "by_op": by_op,
                        "min_margin": {k: round(v, 2) for k, v in mins.items()}, "ppl_ratio": e2.text_ppl(model) / ppl0,
                        "fails": fails[:12], "seconds": round(time.time() - t0)})
            print(json.dumps(log[-1]), flush=True)
            if ok == len(ROWS) and min(mins.values()) >= (stop if stop is not None else hinge / 2):
                break
    model.save_pretrained(out)
    json.dump({"log": log, "ppl0": ppl0, "rows": len(ROWS), "hinge": hinge, "lr": lr, "clip": clip},
              open(f"{out}/train_log.json", "w"), indent=1)
    return out


def policy(model):
    @torch.no_grad()
    def act(op, v):
        prompt = f"{op}<|vision_start|><|image_pad|><|vision_end|>="
        inp = {k: t.to(dev) for k, t in proc(text=[prompt], images=[crop(*v)], return_tensors="pt").items()}
        out = []
        for _ in range(1 if op == "SUM" else 3):
            nxt = int(model(**inp).logits[0, -1].argmax())
            out.append(ID_CHAR.get(nxt, "?"))
            L = inp["input_ids"].shape[1]
            for k, t in list(inp.items()):
                if torch.is_tensor(t) and t.dim() == 2 and t.shape == (1, L):
                    ext = torch.tensor([[nxt]], device=dev) if k == "input_ids" else torch.full((1, 1), int(k == "attention_mask"), device=dev)
                    inp[k] = torch.cat([t, ext.to(t.dtype)], 1)
        return out

    return act


def run_sum(act, a, b):
    n = max(len(a), len(b)) + 1
    carry, top, bot, out = [B] * n, list(a.rjust(n, B)), list(b.rjust(n, B)), [B] * n
    for i in range(n - 1, -1, -1):
        t = act("SUM", (carry[i], top[i], bot[i]))[0]
        if t == "H":
            break
        d, c = (t, "0") if t.isdigit() else (str("abcdefghij".index(t)), "1")
        out[i] = d
        if i > 0:
            carry[i - 1] = "1" if c == "1" else B
    return "".join(out).strip()


def evaluate(adapter):
    model = PeftModel.from_pretrained(e2.load_base(), adapter).eval()
    ok, by_op, mins, fails = certify(model)
    res = {"cert": ok, "rows": len(ROWS), "by_op": by_op, "min_margin": mins, "fails": fails[:20], "ppl": e2.text_ppl(model)}
    print(json.dumps(res), flush=True)
    act, rng = policy(model), random.Random(1)
    mul = lambda op, v: (lambda o: (B if o[0] == "_" else o[0], o[1], o[2]))(act(op, v))
    for n, k in ((4, 20), (6, 10), (10, 5)):
        good = 0
        for _ in range(k):
            a, b = (str(rng.randint(10 ** (n - 1), 10**n - 1)) for _ in range(2))
            good += run(a, b, mul)[0] == str(int(a) * int(b))
        res[f"mul_{n}x{n}"] = f"{good}/{k}"
    for n, k in ((10, 20), (100, 5), (1000, 2)):
        good = 0
        for _ in range(k):
            a, b = (str(rng.randint(10 ** (n - 1), 10**n - 1)) for _ in range(2))
            good += run_sum(act, a, b) == str(int(a) + int(b))
        res[f"sum_{n}"] = f"{good}/{k}"
    print(json.dumps({k: v for k, v in res.items() if k.startswith(("mul_", "sum_"))}), flush=True)
    json.dump(res, open(f"{adapter}/eval.json", "w"), indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check":
        check()
    elif cmd == "train":
        a = sys.argv[2:] + [None] * 3
        out = train(steps=int(a[0] or 1500), seed=int(a[1] or 0), hinge=float(a[2] or 4.0))
        evaluate(out)
    elif cmd == "train2":  # recipe v2: train2 <steps> <seed> <hinge> <stop margin> [adapter dir to continue from]
        a = sys.argv[2:] + [None] * 5
        out = train(steps=int(a[0] or 4000), seed=int(a[1] or 0), hinge=float(a[2] or 4.0), v2=True,
                    stop=float(a[3]) if a[3] else None, init=a[4] or None)
        evaluate(out)
    else:
        evaluate(sys.argv[2])
