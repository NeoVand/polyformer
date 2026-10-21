"""Per-token evaluation of trained LOOPS/EVENTS checkpoints (EVENTS.md, cheap day; review Q3 probes 1-2).

For each checkpoint (a final.pkl this project wrote, on the runs volume), score the same 1,024 held-out
windows as `val_big` (generator seed 5678) and report mean loss in buckets:

    repeat distance  how far back the target token last occurred in the window: none, 1-32, 33-128,
                     129-256, 257-384, 385+ (long-range-dependent tokens are the far buckets)
    position         where the target sits in the window

With --ablate, the candidate is also scored with parts of its frame switched off at inference:
holo (every holonomy move set to the fixed RoPE step), grid (every clock velocity set to 1), both.
Per-sequence losses are kept so arms can be compared with paired tests.

    python research/loops_eval.py --ckpts /runs/<job>/final.pkl,... --data /data/fineweb_edu --ablate 1
"""

import argparse
import json
import math
import os
import pathlib
import pickle
import sys
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import lm  # noqa: E402

DIST_EDGES = [(0, 0, "none"), (1, 32, "1-32"), (33, 128, "33-128"), (129, 256, "129-256"),
              (257, 384, "257-384"), (385, 10 ** 9, "385+")]


def repeat_distance(x, y):
    """For target y[t] (= the token after x[t]), how far back it last occurred among x[0..t]; 0 = never."""
    b, t = x.shape
    dist = np.zeros((b, t), np.int64)
    for i in range(b):
        last = {}
        for j in range(t):
            last[int(x[i, j])] = j
            s = last.get(int(y[i, j]))
            dist[i, j] = 0 if s is None else j + 1 - s
    return dist


def buckets(per_token, dist, positions_edges):
    out = {"distance": {}, "position": {}}
    for lo, hi, name in DIST_EDGES:
        m = (dist == 0) if name == "none" else ((dist >= lo) & (dist <= hi))
        out["distance"][name] = {"loss": float(per_token[m].mean()) if m.any() else None, "count": int(m.sum())}
    t = per_token.shape[1]
    pos = np.broadcast_to(np.arange(t), per_token.shape)
    for lo, hi in positions_edges:
        m = (pos >= lo) & (pos < hi)
        out["position"][f"{lo}-{hi}"] = {"loss": float(per_token[m].mean()), "count": int(m.sum())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", required=True, help="comma-separated final.pkl paths")
    ap.add_argument("--data", default="/data/fineweb_edu")
    ap.add_argument("--seqs", type=int, default=1024)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--ablate", type=int, default=0)
    args = ap.parse_args()
    started = time.time()
    _, val = lm.load(args.data)
    results = []
    for path in args.ckpts.split(","):
        payload = pickle.loads(pathlib.Path(path).read_bytes())
        cfg = argparse.Namespace(**payload["cfg"])
        if cfg.bf16:
            lm.MM = jnp.bfloat16
        T = cfg.ctx
        g = np.random.default_rng(5678)
        idx = g.integers(0, len(val) - T - 1, args.seqs)
        xy = np.stack([val[j:j + T + 1] for j in idx]).astype(np.int32)
        x, y = xy[:, :-1], xy[:, 1:]
        dist = repeat_distance(x, y)
        params = jax.tree_util.tree_map(jnp.asarray, payload["params"])

        @jax.jit
        def score(p, xb, yb):
            return optax.softmax_cross_entropy_with_integer_labels(lm.forward(cfg, p, xb), yb)

        def per_token(p):
            out = [np.asarray(score(p, x[i:i + args.batch], y[i:i + args.batch]))
                   for i in range(0, len(x), args.batch)]
            return np.concatenate(out, 0)

        edges = [(0, 64), (64, T // 4), (T // 4, T // 2), (T // 2, T)]
        variants = {"full": params}
        if args.ablate and any("quat" in l for l in params["layers"]):
            zero = lambda l, k: {**l, k: jax.tree_util.tree_map(jnp.zeros_like, l[k])} if k in l else l
            variants["holo_off"] = {**params, "layers": [zero(l, "quat") for l in params["layers"]]}
            variants["grid_off"] = {**params, "layers": [zero(l, "vel") for l in params["layers"]]}
            variants["frames_off"] = {**params, "layers": [zero(zero(l, "quat"), "vel") for l in params["layers"]]}
        row = {"ckpt": path, "cfg": {k: payload["cfg"].get(k) for k in
                                     ("arch", "posenc", "pattern", "forget", "vtrans", "d", "layers", "seed", "ctx")}}
        for name, p in variants.items():
            pt = per_token(p)
            row[name] = {"loss": float(pt.mean()), "sequence_losses": pt.mean(1).tolist(),
                         "buckets": buckets(pt, dist, edges)}
            if name != "full":
                diff = pt - per_token_full
                row[name]["delta"] = float(diff.mean())
                # where the increase concentrates: the share of the total increase from each distance bucket
                share = {}
                for lo, hi, bname in DIST_EDGES:
                    m = (dist == 0) if bname == "none" else ((dist >= lo) & (dist <= hi))
                    share[bname] = float(diff[m].sum() / max(diff.sum(), 1e-12))
                row[name]["delta_share_by_distance"] = share
            else:
                per_token_full = pt
        results.append(row)
        print(json.dumps({"progress": path, "loss": row["full"]["loss"], "secs": round(time.time() - started, 1)}),
              file=sys.stderr, flush=True)
    print(json.dumps({"eval": results, "secs": round(time.time() - started, 1), "backend": jax.default_backend()}))


if __name__ == "__main__":
    main()
