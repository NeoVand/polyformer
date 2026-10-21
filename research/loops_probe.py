"""What the learned frames do (LOOPS.md): read a trained `loop` checkpoint and report, on held-out text,

- which tokens advance each grid module's clock (mean velocity per token, top and bottom tokens),
- how far each holonomy block's moves are from the fixed RoPE step, and how much consecutive moves
  fail to commute (Frobenius norm of M_t M_{t+1} - M_{t+1} M_t),
- the forget gate: mean log f per head, and the tokens that forget most.

Only loads final.pkl files this project wrote itself (lm.save_final_checkpoint).

    python research/loops_probe.py --ckpt final.pkl --val val.bin --seqs 64 --out probe.json
"""

import argparse
import collections
import json
import pathlib
import pickle
import sys

import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import lm  # noqa: E402
import loops_layers as ll  # noqa: E402


def decode_table():
    try:
        import tiktoken
        enc = tiktoken.get_encoding("gpt2")
        return lambda i: enc.decode([int(i)]) if i < enc.n_vocab else f"<{i}>"
    except Exception:
        return lambda i: f"<{i}>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--val", required=True)
    ap.add_argument("--seqs", type=int, default=64)
    ap.add_argument("--min_count", type=int, default=30)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    payload = pickle.loads(pathlib.Path(args.ckpt).read_bytes())
    cfg = argparse.Namespace(**payload["cfg"])
    cfg.bf16 = 0
    params = payload["params"]
    val = np.memmap(args.val, dtype=np.uint16, mode="r")
    rng = np.random.default_rng(99)
    T = cfg.ctx
    starts = rng.integers(0, len(val) - T - 1, args.seqs)
    idx = np.stack([val[s:s + T] for s in starts]).astype(np.int32)
    dec = decode_table()
    _, pairs, blocks, modules = ll.dims(cfg)

    x = jnp.asarray(params["emb"])[idx]
    if getattr(cfg, "pos", 1):
        x = x + params["pos"][None, :T]
    order = lm.loop_order(cfg)
    report = {"cfg": {k: payload["cfg"][k] for k in ("posenc", "holo", "modules", "forget", "vtrans", "pattern",
                                                      "loop_order", "seed", "lr")},
              "layers": []}
    flat = idx.reshape(-1)
    for n, i in enumerate(order):
        lyr = params["layers"][i]
        row = {"block": i}
        if "qkv" in lyr:
            normed = lm.ln(lyr["ln1"], x)
            b, t, _ = normed.shape
            if "vel" in lyr:
                z = (normed @ lyr["vel"]["w"] + lyr["vel"]["b"]).reshape(b, t, cfg.heads, modules)
                u = np.asarray(jnp.log1p(jnp.exp(z)) / np.log(2.0)).reshape(-1, cfg.heads, modules)
                row["velocity_mean"] = u.mean(0).round(4).tolist()
                row["velocity_cv"] = (u.std(0) / (u.mean(0) + 1e-9)).round(4).tolist()
                # tokens that move each module most and least, averaged over heads
                per_token = collections.defaultdict(list)
                um = u.mean(1)                                    # [N, modules]
                for tok, val_ in zip(flat, um):
                    per_token[int(tok)].append(val_)
                common = {k: np.mean(v, 0) for k, v in per_token.items() if len(v) >= args.min_count}
                tops = []
                for m in range(modules):
                    ranked = sorted(common.items(), key=lambda kv: -kv[1][m])
                    tops.append({"fast": [[dec(k), round(float(v[m]), 3)] for k, v in ranked[:12]],
                                 "slow": [[dec(k), round(float(v[m]), 3)] for k, v in ranked[-8:]]})
                row["velocity_tokens"] = tops
            if "quat" in lyr:
                fr = ll.frames(cfg, lyr, normed)
                F = np.asarray(fr["F"])                            # [B, T, H, nb, 4, 4]
                moves = np.concatenate([F[:, :1], np.einsum("bthnji,bthnjk->bthnik", F[:, :-1], F[:, 1:])], 1)
                base = np.asarray(ll.base_moves(cfg, cfg.d // cfg.heads, pairs, blocks))
                row["move_from_rope"] = np.linalg.norm(moves - base, axis=(-2, -1)).mean((0, 1)).round(4).tolist()
                comm = moves[:, 1:-1] @ moves[:, 2:] - moves[:, 2:] @ moves[:, 1:-1]
                row["adjacent_commutator"] = np.linalg.norm(comm, axis=(-2, -1)).mean((0, 1)).round(4).tolist()
            if "fgate" in lyr:
                logf = np.asarray(-jnp.logaddexp(0.0, -(normed @ lyr["fgate"]["w"] + lyr["fgate"]["b"])))
                logf = logf.reshape(-1, cfg.heads)
                row["log_forget_mean"] = logf.mean(0).round(5).tolist()
                row["half_life_tokens"] = (np.log(0.5) / np.minimum(logf.mean(0), -1e-9)).round(1).tolist()
                per_token = collections.defaultdict(list)
                for tok, val_ in zip(flat, logf.mean(1)):
                    per_token[int(tok)].append(val_)
                common = {k: np.mean(v) for k, v in per_token.items() if len(v) >= args.min_count}
                ranked = sorted(common.items(), key=lambda kv: kv[1])
                row["forget_most"] = [[dec(k), round(float(v), 4)] for k, v in ranked[:12]]
        if n and i in order[:n]:
            x = x + params["inject"] * first
        x = lm.block(cfg, lyr, x)
        if n == 0:
            first = x
        report["layers"].append(row)
    text = json.dumps(report, indent=1, ensure_ascii=False)
    if args.out:
        pathlib.Path(args.out).write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
