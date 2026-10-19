"""
A tiny byte-level language model on enwik8, to see whether Newton attention helps a real
sequence model. Three architectures with matched parameter counts:

    gpt     softmax attention + MLP, pre-LayerNorm, L layers
    hybrid  the same, plus a causal Newton attention branch beside each attention, MLP narrowed
    newton  Newton attention in place of softmax attention

Causal Newton attention: position t sees the tokens before it. Power sums are exclusive prefix
sums, P_j(t) = sum_{s<t} phi_s^j; Newton's identities give e_m(t), the sum over m-subsets of
earlier tokens; normalised by C(t, m) and multiplied by the query's own phases, they are the
arity m+1 features. The state is a fixed number of running sums: linear time, streaming.

    python research/lm.py --arch hybrid --steps 8000 --seed 0

prints one JSON line with validation bits per character through training.
"""

import argparse
import json
import math
import os
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax


def load(path="/root/enwik8"):
    # enwik8's standard split is 90M / 5M / 5M bytes; smaller files split in the same proportion
    data = np.frombuffer(open(path, "rb").read(), dtype=np.uint8)
    n = len(data)
    return data[: n * 9 // 10], data[n * 9 // 10 : n * 19 // 20]


def dense(key, i, o, scale=1.0):
    return {"w": jax.random.normal(key, (i, o)) * scale / math.sqrt(i), "b": jnp.zeros(o)}


def lin(p, x):
    return x @ p["w"] + p["b"]


def ln_init(d):
    return {"g": jnp.ones(d), "b": jnp.zeros(d)}


def ln(p, x):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / jnp.sqrt(var + 1e-5) * p["g"] + p["b"]


def init(key, cfg):
    D, L, T = cfg.d, cfg.layers, cfg.ctx
    ks = iter(jax.random.split(key, 16 + 16 * L))
    p = {"emb": jax.random.normal(next(ks), (256, D)) * 0.02, "pos": jax.random.normal(next(ks), (T, D)) * 0.02,
         "lnf": ln_init(D), "layers": []}
    for _ in range(L):
        lyr = {"ln1": ln_init(D), "ln2": ln_init(D)}
        if cfg.arch in ("gpt", "hybrid"):
            lyr["qkv"] = dense(next(ks), D, 3 * D)
            lyr["o"] = dense(next(ks), D, D, scale=1 / math.sqrt(2 * L))
        if cfg.arch in ("hybrid", "newton"):
            H, r, K = cfg.nheads, cfg.rank, cfg.order
            lyr["lnn"] = ln_init(D)
            lyr["th"] = dense(next(ks), D, H * r)
            lyr["g"] = dense(next(ks), D, H * r)
            lyr["no"] = dense(next(ks), H * 2 * r, D, scale=1 / math.sqrt(2 * L))
            lyr["alpha"] = jnp.ones((K, D))
        lyr["fc1"] = dense(next(ks), D, cfg.mlp)
        lyr["fc2"] = dense(next(ks), cfg.mlp, D, scale=1 / math.sqrt(2 * L))
        p["layers"].append(lyr)
    return p


def softmax_attention(cfg, lyr, x):
    B, T, D = x.shape
    H = cfg.heads
    q, k, v = jnp.split(lin(lyr["qkv"], x), 3, -1)
    sh = lambda t: t.reshape(B, T, H, D // H).transpose(0, 2, 1, 3)
    q, k, v = sh(q), sh(k), sh(v)
    s = jnp.einsum("bhtc,bhsc->bhts", q, k) / math.sqrt(D // H)
    mask = jnp.tril(jnp.ones((T, T), bool))
    s = jnp.where(mask, s, -1e9)
    y = jnp.einsum("bhts,bhsc->bhtc", jax.nn.softmax(s, -1), v)
    return lin(lyr["o"], y.transpose(0, 2, 1, 3).reshape(B, T, D))


def newton_attention(cfg, lyr, x):
    """Causal Newton attention with normalised per-arity features and one shared read-out."""
    B, T, D = x.shape
    H, r, K = cfg.nheads, cfg.rank, cfg.order
    th = cfg.phase * lin(lyr["th"], x).reshape(B, T, H, r)
    g = jax.nn.sigmoid(lin(lyr["g"], x).reshape(B, T, H, r))
    phi = g * jnp.exp(1j * th)  # [B, T, H, r]
    pw = [phi]
    for _ in range(K - 2):
        pw.append(pw[-1] * phi)
    # exclusive prefix sums: position t sees s < t
    P = [jnp.cumsum(w, 1) - w for w in pw]
    e = [jnp.ones_like(phi)]
    for m in range(1, K):
        e.append(sum((-1) ** (j - 1) * e[m - j] * P[j - 1] for j in range(1, m + 1)) / m)
    t = np.arange(T)
    feats = []
    for m in range(K):
        norm = np.array([math.comb(int(tt), m) if tt >= m else 0 for tt in t], np.float64)
        inv = jnp.asarray(np.where(norm > 0, 1.0 / np.maximum(norm, 1), 0.0), jnp.float32)[None, :, None, None]
        f = phi * e[m] * inv
        f = jnp.concatenate([f.real, f.imag], -1).reshape(B, T, H * 2 * r)
        # every arity on one scale before the shared read-out
        f = f / jnp.sqrt((f ** 2).mean(-1, keepdims=True) + 1e-6)
        feats.append(lin(lyr["no"], f) * lyr["alpha"][m])
    return sum(feats)


def forward(cfg, p, idx):
    T = idx.shape[1]
    x = p["emb"][idx] + p["pos"][None, :T]
    for lyr in p["layers"]:
        if cfg.arch in ("gpt", "hybrid"):
            x = x + softmax_attention(cfg, lyr, ln(lyr["ln1"], x))
        if cfg.arch in ("hybrid", "newton"):
            x = x + newton_attention(cfg, lyr, ln(lyr["lnn"], x))
        x = x + lin(lyr["fc2"], jax.nn.gelu(lin(lyr["fc1"], ln(lyr["ln2"], x))))
    x = ln(p["lnf"], x)
    return x @ p["emb"].T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="gpt")
    ap.add_argument("--d", type=int, default=256)
    ap.add_argument("--layers", type=int, default=4)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--mlp", type=int, default=0)
    ap.add_argument("--nheads", type=int, default=4)
    ap.add_argument("--rank", type=int, default=32)
    ap.add_argument("--order", type=int, default=4)
    ap.add_argument("--phase", type=float, default=2.0)
    ap.add_argument("--ctx", type=int, default=256)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--data", default="/root/enwik8")
    cfg = ap.parse_args()
    if not cfg.mlp:
        # matched parameters: the Newton branch's weights come out of the MLP
        D, H, r = cfg.d, cfg.nheads, cfg.rank
        newton = 2 * D * H * r + 2 * H * r * D
        attn = 4 * D * D
        per_layer = attn + 8 * D * D
        if cfg.arch == "gpt":
            cfg.mlp = 4 * D
        elif cfg.arch == "hybrid":
            cfg.mlp = max(D, int((per_layer - attn - newton) / (2 * D)))
        else:
            cfg.mlp = max(D, int((per_layer - newton) / (2 * D)))
    train, val = load(cfg.data)
    rng = np.random.default_rng(cfg.seed)
    vrng = np.random.default_rng(1234)
    T = cfg.ctx

    def batch(src, g, n):
        i = g.integers(0, len(src) - T - 1, n)
        x = np.stack([src[j : j + T + 1] for j in i]).astype(np.int32)
        return x[:, :-1], x[:, 1:]

    vx, vy = batch(val, vrng, 512)
    params = init(jax.random.PRNGKey(cfg.seed), cfg)
    nparams = sum(int(x.size) for x in jax.tree_util.tree_leaves(params))
    sched = optax.warmup_cosine_decay_schedule(0.0, cfg.lr, min(400, cfg.steps // 10), cfg.steps, cfg.lr * 0.1)
    opt = optax.chain(optax.clip_by_global_norm(1.0), optax.adamw(sched, weight_decay=0.1))
    st = opt.init(params)

    def loss_fn(p, x, y):
        lg = forward(cfg, p, x)
        return optax.softmax_cross_entropy_with_integer_labels(lg, y).mean()

    @jax.jit
    def step(p, st, x, y):
        l, g = jax.value_and_grad(loss_fn)(p, x, y)
        up, st = opt.update(g, st, p)
        return optax.apply_updates(p, up), st, l

    @jax.jit
    def vloss(p, x, y):
        return loss_fn(p, x, y)

    def bpc(p):
        ls = [float(vloss(p, vx[i : i + 64], vy[i : i + 64])) for i in range(0, len(vx), 64)]
        return round(float(np.mean(ls)) / math.log(2), 4)

    t0 = time.time()
    curve = []
    for it in range(cfg.steps):
        x, y = batch(train, rng, cfg.batch)
        params, st, l = step(params, st, x, y)
        if (it + 1) % max(1, cfg.steps // 16) == 0:
            curve.append((it + 1, round(float(l) / math.log(2), 4), bpc(params)))
    print(json.dumps({"arch": cfg.arch, "seed": cfg.seed, "params": nparams, "mlp": cfg.mlp,
                      "rank": cfg.rank, "order": cfg.order, "steps": cfg.steps, "val_bpc": curve[-1][2],
                      "curve": curve, "secs": round(time.time() - t0, 1), "backend": jax.default_backend()}))


if __name__ == "__main__":
    main()
