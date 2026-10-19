"""
S1 of SEARCH.md: a diagnostic map of where pairwise attention runs out, at one and two layers and
equal FLOPs. Every task is causal next-token prediction with the loss on its answer positions only,
run through lm.py's model code, so the layers are exactly the ones the language models use.

    python research/diag.py --task mqar --model softmax --layers 1 --seed 0

Models (lm.py architectures), all at width 128 unless widened to match FLOPs:
    ff        free-field: subset sectors K = 4, every arity off at init (it starts as softmax), mu = 0.05
    ffw       free-field with walks A^l V (l <= 4) and look-back keys
    softmax   gpt, widened until its FLOPs per token match ff's at this task's length and vocab
    softmaxw  gpt, widened to match ffw's FLOPs
    lookback  gpt with look-back keys, widened to match ffw's FLOPs (the control for the walk sector)

Tasks (see the generators): mqar, mqar2 (composite keys), selcopy, indist, phop4/8/16, dyck2, add,
match3. Prints one JSON line: accuracy on the answer positions (balanced for match3, exact sums for
add) through training, and the FLOPs per token of the model.
"""

import argparse
import itertools
import json
import math
import pathlib
import sys
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import lm  # noqa: E402

# ----------------------------------------------------------------------------- tasks
# Each generator returns x [B, T] int32 inputs, y [B, T] int32 targets, m [B, T] float loss mask.


def mqar(rng, B, T=256, N=32, V=8192):
    # Zoology's multi-query associative recall: N key-value pairs, then every key queried once
    x = np.zeros((B, T), np.int64); y = np.zeros((B, T), np.int64); m = np.zeros((B, T))
    for b in range(B):
        keys = rng.choice(np.arange(1, V // 2), N, replace=False)
        vals = rng.integers(V // 2, V, N)
        x[b, 0:2 * N:2], x[b, 1:2 * N:2] = keys, vals
        pos = np.sort(rng.choice(np.arange(2 * N, T), N, replace=False))
        order = rng.permutation(N)
        x[b, pos] = keys[order]; y[b, pos] = vals[order]; m[b, pos] = 1
    return x, y, m


def mqar2(rng, B, T=256, N=24, V=8192, A=8):
    # composite keys: triples (a, b, v) with a and b from small sets, every pair distinct, so neither a nor
    # b alone identifies v; queries are "a b" and the answer is due at b
    x = np.zeros((B, T), np.int64); y = np.zeros((B, T), np.int64); m = np.zeros((B, T))
    for b in range(B):
        pairs = rng.choice(A * A, N, replace=False)
        ka, kb = 1 + pairs // A, 1 + A + pairs % A
        vals = rng.integers(V // 2, V, N)
        x[b, 0:3 * N:3], x[b, 1:3 * N:3], x[b, 2:3 * N:3] = ka, kb, vals
        slots = np.sort(rng.choice(np.arange(3 * N // 2, T // 2), N, replace=False)) * 2  # even, non-adjacent
        order = rng.permutation(N)
        x[b, slots], x[b, slots + 1] = ka[order], kb[order]
        y[b, slots + 1] = vals[order]; m[b, slots + 1] = 1
    return x, y, m


def selcopy(rng, B, T=256, K=16, V=256):
    # selective copying: K data tokens scattered among fillers, then a separator; reproduce them in order
    x = np.zeros((B, T), np.int64); y = np.zeros((B, T), np.int64); m = np.zeros((B, T))
    sep = 1
    for b in range(B):
        data = rng.choice(np.arange(2, V), K, replace=False)
        pos = np.sort(rng.choice(T - K - 1, K, replace=False))
        x[b, pos] = data
        x[b, T - K - 1] = sep
        x[b, T - K:] = data
        y[b, T - K - 1:T - 1] = data; m[b, T - K - 1:T - 1] = 1
    return x, y, m


def indist(rng, B, T=256, Q=8, V=512):
    # induction with distractors: Q query tokens, each planted 2-3 times with different successors; at the
    # end each is shown once and the answer is the successor of its most recent occurrence
    x = np.zeros((B, T), np.int64); y = np.zeros((B, T), np.int64); m = np.zeros((B, T))
    for b in range(B):
        qs = rng.choice(np.arange(1, 64), Q, replace=False)
        fill = rng.integers(64, V, T)
        x[b] = fill
        free = np.arange(0, T - Q - 1, 2)
        slots = rng.choice(free, 3 * Q, replace=False)
        last = {}
        for i, s in enumerate(sorted(slots)):
            q = qs[rng.integers(Q)]
            x[b, s], x[b, s + 1] = q, rng.integers(64, V)
            last[q] = x[b, s + 1]
        order = [q for q in rng.permutation(qs) if q in last]
        for i, q in enumerate(order):
            p = T - len(order) + i
            x[b, p] = q; y[b, p] = last[q]; m[b, p] = 1
    return x, y, m


def phop(rng, B, p, T=256, V=64):
    # p-hop induction (Saunshi et al. 2025): from the last token, jump to the token after its most recent
    # earlier occurrence, p times; predict where the walk ends
    x = np.zeros((B, T), np.int64); y = np.zeros((B, T), np.int64); m = np.zeros((B, T))
    for b in range(B):
        chain = rng.choice(V, p + 1, replace=False)
        others = np.setdiff1d(np.arange(V), chain)
        x[b] = rng.choice(others, T)
        js = np.sort(rng.choice(np.arange(0, (T - 2) // 2), p, replace=False))[::-1] * 2  # j_1 > ... > j_p, even
        for i, j in enumerate(js):
            x[b, j], x[b, j + 1] = chain[i], chain[i + 1]
        x[b, T - 1] = chain[0]
        y[b, T - 1] = chain[p]; m[b, T - 1] = 1
    return x, y, m


def dyck2(rng, B, T=128, depth=16):
    # bracket prediction: at every position whose next token closes a bracket, predict which one
    x = np.zeros((B, T + 1), np.int64)
    for b in range(B):
        st = []
        for t in range(T + 1):
            if not st or (len(st) < depth and rng.random() < 0.5):
                o = int(rng.integers(2)); st.append(o); x[b, t] = 1 + 2 * o
            else:
                x[b, t] = 2 + 2 * st.pop()
    inp, nxt = x[:, :-1], x[:, 1:]
    return inp, nxt, ((nxt == 2) | (nxt == 4)).astype(np.float64)


def add(rng, B, n=10):
    # n-digit addition, every number written least significant digit first: a + b = s
    a = rng.integers(0, 10, (B, n)); b = rng.integers(0, 10, (B, n))
    s = np.zeros((B, n + 1), np.int64); c = np.zeros(B, np.int64)
    for i in range(n):
        t = a[:, i] + b[:, i] + c; s[:, i] = t % 10; c = t // 10
    s[:, n] = c
    seq = np.concatenate([a, np.full((B, 1), 10), b, np.full((B, 1), 11), s], 1)  # 3n + 3 tokens
    x, y = seq[:, :-1], seq[:, 1:]
    m = np.zeros_like(x, dtype=np.float64); m[:, 2 * n + 1:] = 1
    return x, y, m


GROUP = np.random.default_rng(99).integers(0, 3, (256, 4))  # a fixed, unknown map from tokens to Z_3^4


def match3(rng, B, n=20):
    # Match-3 over a token vocabulary: does token i complete a zero sum with two DISTINCT earlier tokens?
    tok = rng.integers(0, 256, (B, n))
    g = GROUP[tok]
    lab = np.zeros((B, n), np.int64)
    for s, t in itertools.combinations(range(n), 2):
        need = (-(g[:, s] + g[:, t])) % 3
        later = (g[:, t + 1:] == need[:, None]).all(-1)
        lab[:, t + 1:] |= later
    m = np.zeros((B, n)); m[:, 2:] = 1
    return tok + 2, lab, m  # inputs 2..257, answers 0 (no) / 1 (yes)


TASKS = {
    "mqar": (mqar, 256, 8192), "mqar2": (mqar2, 256, 8192), "selcopy": (selcopy, 256, 256),
    "indist": (indist, 256, 512), "phop4": (lambda r, B: phop(r, B, 4), 256, 64),
    "phop8": (lambda r, B: phop(r, B, 8), 256, 64), "phop16": (lambda r, B: phop(r, B, 16), 256, 64),
    "dyck2": (dyck2, 128, 5), "add": (add, 32, 12), "match3": (match3, 20, 258),
}

# ----------------------------------------------------------------------------- models


def config(model, layers, T, V, d_ff=128, heads=4):
    c = argparse.Namespace(arch="gpt", d=d_ff, layers=layers, heads=heads, nheads=heads, rank=d_ff // heads // 2,
                           order=4, phase=2.0, vac=0.05, alpha0=2, cap=0.0, fscale=1, hops=1, lookback=0, lbdim=8,
                           ctx=T, vocab=V, remat=0, mlp=4 * d_ff)
    if model in ("ff", "ffw"):
        c.arch = "sfa"
        D, H, r = c.d, c.heads, c.rank
        c.mlp = max(D, int((8 * D * D - (2 * D * H * r + 2 * H * r * D)) / (2 * D)))  # equal parameters
        if model == "ffw":
            c.hops, c.lookback = 4, 1
        return c
    # softmax baselines: widen until the FLOPs per token match the free-field model they are compared with
    target = lm.flops_per_token(config("ff" if model == "softmax" else "ffw", layers, T, V, d_ff, heads), T)
    best = None
    for d in range(heads * 8, 8 * d_ff, heads * 2):
        cc = argparse.Namespace(**{**vars(c), "d": d, "mlp": 4 * d, "lookback": int(model == "lookback")})
        f = lm.flops_per_token(cc, T)
        if best is None or abs(f - target) < abs(best[0] - target):
            best = (f, cc)
    return best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="mqar"); ap.add_argument("--model", default="softmax")
    ap.add_argument("--layers", type=int, default=1); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=4000); ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--d", type=int, default=128)
    a = ap.parse_args()
    gen, T, V = TASKS[a.task]
    cfg = config(a.model, a.layers, T, V, a.d)
    rng = np.random.default_rng(a.seed)
    params = lm.init(jax.random.PRNGKey(a.seed), cfg)
    nparams = sum(int(t.size) for t in jax.tree_util.tree_leaves(params))
    sched = optax.warmup_cosine_decay_schedule(0.0, a.lr, a.steps // 20, a.steps, a.lr * 0.05)
    opt = optax.chain(optax.clip_by_global_norm(1.0), optax.adamw(sched, weight_decay=0.1))
    st = opt.init(params)

    def loss_fn(p, x, y, m):
        ce = optax.softmax_cross_entropy_with_integer_labels(lm.forward(cfg, p, x), y)
        return (ce * m).sum() / m.sum()

    @jax.jit
    def step(p, st, x, y, m):
        l, g = jax.value_and_grad(loss_fn)(p, x, y, m)
        up, st = opt.update(g, st, p)
        return optax.apply_updates(p, up), st, l

    @jax.jit
    def predict(p, x):
        return lm.forward(cfg, p, x).argmax(-1)

    ex, ey, em = gen(np.random.default_rng(10_000 + a.seed), 1024)

    def evaluate(p):
        pred = np.concatenate([np.asarray(predict(p, jnp.asarray(ex[i:i + 128], jnp.int32))) for i in range(0, len(ex), 128)])
        hit = (pred == ey) * em
        if a.task == "match3":  # balanced over the two answers
            r = [(hit * (ey == c)).sum() / max(1, (em * (ey == c)).sum()) for c in (0, 1)]
            return float(np.mean(r))
        if a.task == "add":     # the whole sum right
            return float(((hit.sum(1) == em.sum(1))).mean())
        return float(hit.sum() / em.sum())

    t0 = time.time(); curve = []
    for it in range(a.steps):
        x, y, m = gen(rng, a.batch)
        params, st, l = step(params, st, jnp.asarray(x, jnp.int32), jnp.asarray(y, jnp.int32), jnp.asarray(m, jnp.float32))
        if (it + 1) % (a.steps // 10) == 0:
            curve.append((it + 1, round(float(l), 4), round(evaluate(params), 4)))
    print(json.dumps({"task": a.task, "model": a.model, "layers": a.layers, "seed": a.seed, "lr": a.lr,
                      "acc": curve[-1][2], "best": max(c[2] for c in curve), "d": cfg.d, "params": nparams,
                      "flops_per_token": lm.flops_per_token(cfg, T), "curve": curve, "secs": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
