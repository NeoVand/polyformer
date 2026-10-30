"""Ouro-1.4B loop probe ($0, local MPS).

One forward with T_MAX loop passes gives the output after every smaller number of passes (pass u depends only on
passes <= u), so each example is run once and read out at T = 1..T_MAX.

Measures, per T: exact-answer rate on direct (no chain of thought) addition, multiplication and swap tracking,
teacher-forced (every answer token must be the argmax); perplexity on plain text; how much the hidden state still moves
between passes; and where the model's own exit gate would stop.
"""

import json
import random
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PATH = "/Users/neo/repos/polyformer-wt/models/ouro-1.4b"
T_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 16
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40
OUT = f"ouro_probe_T{T_MAX}.json"

dev = "mps"
tok = AutoTokenizer.from_pretrained(PATH)
model = AutoModelForCausalLM.from_pretrained(PATH, trust_remote_code=True, torch_dtype=torch.bfloat16).to(dev).eval()
model.config.total_ut_steps = T_MAX
model.model.total_ut_steps = T_MAX


@torch.no_grad()
def run(prompt: str, answer: str):
    """Per-step: all-answer-tokens-argmax-correct, summed CE over the answer, rel. state change, exit pdf."""
    p = tok.encode(prompt)
    a = tok.encode(answer)
    ids = torch.tensor([p + a], device=dev)
    _, hs, gates = model.model(input_ids=ids, use_cache=False)
    pos = torch.arange(len(p) - 1, len(p) + len(a) - 1, device=dev)
    tgt = torch.tensor(a, device=dev)
    ok, ce, move = [], [], []
    for u, h in enumerate(hs):
        logits = model.lm_head(h[0, pos]).float()
        ok.append(bool((logits.argmax(-1) == tgt).all()))
        ce.append(float(torch.nn.functional.cross_entropy(logits, tgt, reduction="sum")))
        if u:
            prev = hs[u - 1][0, pos].float()
            move.append(float(((h[0, pos].float() - prev).norm(dim=-1) / prev.norm(dim=-1)).mean()))
    rem, pdf = torch.ones(len(pos), device=dev), []
    for u, g in enumerate(gates):
        lam = torch.sigmoid(g[0, pos, 0].float())
        pi = lam * rem if u < len(gates) - 1 else rem
        rem = rem * (1 - lam)
        pdf.append(float(pi.mean()))
    return ok, ce, move, pdf


def number(n, rng):
    return rng.randint(10 ** (n - 1), 10**n - 1)


def add_case(n, rng):
    shots = "".join(f"{(a := number(n, rng))}+{(b := number(n, rng))}={a + b}\n" for _ in range(4))
    a, b = number(n, rng), number(n, rng)
    return shots + f"{a}+{b}=", str(a + b)


def mul_case(n, rng):
    shots = "".join(f"{(a := number(n, rng))}*{(b := number(n, rng))}={a * b}\n" for _ in range(4))
    a, b = number(n, rng), number(n, rng)
    return shots + f"{a}*{b}=", str(a * b)


def swap_case(k, rng):
    def one():
        cups = list("ABCDE")
        moves = []
        for _ in range(k):
            i, j = rng.sample(range(5), 2)
            cups[i], cups[j] = cups[j], cups[i]
            moves.append(f"{i + 1}-{j + 1}")
        return f"Start: A B C D E\nSwaps: {', '.join(moves)}\nEnd:", " " + " ".join(cups)

    shots = "".join(q + a + "\n\n" for q, a in (one() for _ in range(3)))
    q, a = one()
    return shots + q, a


TASKS = {
    "add3": lambda r: add_case(3, r),
    "add5": lambda r: add_case(5, r),
    "add8": lambda r: add_case(8, r),
    "add12": lambda r: add_case(12, r),
    "mul2": lambda r: mul_case(2, r),
    "mul3": lambda r: mul_case(3, r),
    "swap2": lambda r: swap_case(2, r),
    "swap4": lambda r: swap_case(4, r),
    "swap8": lambda r: swap_case(8, r),
}

TEXT = open("/Users/neo/repos/polyformer/research/PRIMER.md").read()[:3000]

res = {"T_MAX": T_MAX, "N": N, "tasks": {}}
t0 = time.time()
for name, make in TASKS.items():
    rng = random.Random(hash(name) % 10_000)
    acc = [0] * T_MAX
    moves, pdfs = [], []
    for _ in range(N):
        q, a = make(rng)
        ok, _, move, pdf = run(q, a)
        acc = [x + y for x, y in zip(acc, ok)]
        moves.append(move)
        pdfs.append(pdf)
    res["tasks"][name] = {
        "acc": [x / N for x in acc],
        "move": [sum(m[u] for m in moves) / N for u in range(T_MAX - 1)],
        "exit_pdf": [sum(p[u] for p in pdfs) / N for u in range(T_MAX)],
    }
    print(f"{name:6s} " + " ".join(f"{x / N:.2f}" for x in acc), f"({time.time() - t0:.0f}s)", flush=True)

# perplexity on plain English, scored as one long teacher-forced answer after the first 32 tokens
ids = tok.encode(TEXT)
head, body = tok.decode(ids[:32]), tok.decode(ids[32:600])
_, ce, move, pdf = run(head, body)
ntok = len(tok.encode(body))
res["text"] = {"ppl": [float(torch.tensor(c / ntok).exp()) for c in ce], "move": move, "exit_pdf": pdf, "tokens": ntok}
print("ppl    " + " ".join(f"{p:.1f}" for p in res["text"]["ppl"]), flush=True)
print("move   " + " ".join(f"{m:.3f}" for m in res["text"]["move"]), flush=True)
print("exit   " + " ".join(f"{p:.2f}" for p in res["text"]["exit_pdf"]), flush=True)
json.dump(res, open(OUT, "w"), indent=1)
print(f"wrote {OUT} in {time.time() - t0:.0f}s")
