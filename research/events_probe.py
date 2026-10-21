"""EVENTS.md stage 6: probes of trained checkpoints beyond the loss (E4, E5).

    boundaries  (event models) where the router puts boundaries on held-out text: the share of boundaries
                on or right after punctuation or a newline, or on a clause-opening word, against the same
                share over all tokens; event lengths; the most frequent boundary tokens; marked samples
    kv          variable tracking at a distance: four facts "The password for the <colour> door is <word>.",
                then D tokens of held-out text, then the question; multiple choice among the four words
    boxes       entity tracking (after Kim and Schuster 2023): three objects in three boxes, k moves, then
                where a moved object is; multiple choice among the boxes
    owners      the same with people handing objects to one another

Probes are scored at the last prompt position: accuracy among the candidates, and the answer token's loss
over the whole vocabulary. Prompts are right-padded to the model's context; every model is causal, so
padding changes nothing before it. Items are generated with a fixed seed, so every checkpoint sees the
same prompts (filler from the validation split).

    python research/events_probe.py --ckpts /runs/<job>/final.pkl,... --data /data/fineweb_edu
"""

import argparse
import json
import pathlib
import pickle
import sys
import time

import jax
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import events_tokens as tok  # noqa: E402
import lm  # noqa: E402

EOT = 50256
P = tok.PIECE
COLOURS = "red blue green yellow black white brown purple orange pink gray silver".split()
WORDS = ("apple river candle mirror garden hammer pencil ticket window rabbit button bottle jacket lemon violin "
         "carpet anchor pillow basket rocket tiger wallet helmet ladder").split()
OBJECTS = "key coin map ring book cup pen hat ball".split()
NAMES = "Alice Bob Carol Dave Eve Frank Grace Henry".split()
LETTERS = "A B C D E".split()


def ids(*words):
    return [P[w if w in (".", "\n") else " " + w] for w in words]


def kv_items(rng, n, distance, val):
    items = []
    for _ in range(n):
        colours = rng.choice(COLOURS, 4, replace=False)
        words = rng.choice(WORDS, 4, replace=False)
        q = int(rng.integers(4))
        prompt = [EOT]
        for c, w in zip(colours, words):
            prompt += ids("The", "password", "for", "the", c, "door", "is", w, ".")
        if distance:
            start = int(rng.integers(0, len(val) - distance - 1))
            prompt += ids("\n") + [int(t) for t in val[start:start + distance]] + ids("\n")
        prompt += ids("The", "password", "for", "the", colours[q], "door", "is")
        items.append((prompt, ids(*words), q))
    return items


def tracking_items(rng, n, moves, kind):
    """Three things, k transfers; the question is about a thing whose final place differs from its first."""
    items = []
    while len(items) < n:
        things = list(rng.choice(OBJECTS, 3, replace=False))
        places = list(rng.choice(LETTERS if kind == "boxes" else NAMES, 3, replace=False))
        where = dict(zip(things, places))
        first = dict(where)
        prompt = [EOT]
        for t in things:
            prompt += ids("The", t, "is", "in", "box", where[t], ".") if kind == "boxes" else \
                ids(where[t], "has", "the", t, ".")
        for _ in range(moves):
            t = things[int(rng.integers(3))]
            to = [p for p in places if p != where[t]][int(rng.integers(2))]
            prompt += ids("Move", "the", t, "to", "box", to, ".") if kind == "boxes" else \
                ids(where[t], "gives", "the", t, "to", to, ".")
            where[t] = to
        pool = [t for t in things if where[t] != first[t]] if moves else things
        if not pool:
            continue
        t = pool[int(rng.integers(len(pool)))]
        prompt += ids("The", t, "is", "in", "box") if kind == "boxes" else ids("Now", "the", t, "belongs", "to")
        items.append((prompt, ids(*places), places.index(where[t])))
    return items


def probe_items(T, val):
    rng = np.random.default_rng(99)
    sets = {}
    for d in (0, 256, 1024, 4096):
        if d + 120 < T:
            sets[f"kv_d{d}"] = kv_items(rng, 128, d, val)
    for kind in ("boxes", "owners"):
        for k in (0, 1, 2, 3):
            sets[f"{kind}_k{k}"] = tracking_items(rng, 128, k, kind)
    return sets


def score_items(cfg, params, items, batch):
    T = cfg.ctx
    fwd = jax.jit(lambda p, x: lm.forward(cfg, p, x))
    correct, losses = [], []
    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        x = np.full((len(chunk), T), EOT, np.int32)
        last = []
        for j, (prompt, _, _) in enumerate(chunk):
            x[j, :len(prompt)] = prompt
            last.append(len(prompt) - 1)
        logits = np.asarray(fwd(params, jnp.asarray(x))[np.arange(len(chunk)), np.asarray(last)], np.float32)
        lp = logits - logits.max(-1, keepdims=True)
        lp = lp - np.log(np.exp(lp).sum(-1, keepdims=True))
        for j, (_, cands, ans) in enumerate(chunk):
            correct.append(int(np.argmax(lp[j, cands]) == ans))
            losses.append(float(-lp[j, cands[ans]]))
    return {"acc": float(np.mean(correct)), "loss": float(np.mean(losses)), "n": len(items),
            "chance": 1.0 / len(items[0][1])}


def boundary_stats(cfg, params, x):
    import events_model
    fwd = jax.jit(lambda p, x_: events_model.forward(cfg, p, x_, with_aux=True, with_boundaries=True)[1])
    hard = np.concatenate([np.asarray(fwd(params, jnp.asarray(x[i:i + 2]))["hard"]) for i in range(0, len(x), 2)], 0)
    newline, punct, clause = (np.isin(x, np.asarray(s)) for s in (tok.NEWLINE, tok.PUNCT, tok.CLAUSE))
    prev = lambda m: np.concatenate([np.zeros_like(m[:, :1]), m[:, :-1]], 1)
    cats = {"on_newline": newline, "after_newline": prev(newline), "on_punct": punct, "after_punct": prev(punct),
            "on_clause_word": clause}
    any_cat = np.zeros_like(hard)
    for m in cats.values():
        any_cat |= m
    b = hard.copy()
    b[:, 0] = False  # the first token is a boundary by construction
    scored = np.ones_like(hard)
    scored[:, 0] = False
    out = {"boundaries": int(b.sum()), "tokens": int(scored.sum()), "rate": float(b.sum() / scored.sum()),
           "mean_event_length": float(scored.sum() / max(b.sum(), 1)),
           "share_any": float(any_cat[b].mean()), "base_any": float(any_cat[scored].mean()),
           "by_category": {k: {"share": float(m[b].mean()), "base": float(m[scored].mean())} for k, m in cats.items()}}
    lengths = []
    for row in hard:
        where = np.flatnonzero(row)
        lengths += np.diff(np.append(where, len(row))).tolist()
    out["length_hist"] = np.bincount(np.minimum(lengths, 64), minlength=65).tolist()
    ids_at, counts = np.unique(x[b], return_counts=True)
    order = np.argsort(-counts)[:200]
    totals = {int(i): int(c) for i, c in zip(*np.unique(x[scored], return_counts=True))}
    out["top_tokens"] = [[int(ids_at[k]), int(counts[k]), totals.get(int(ids_at[k]), 0)] for k in order]
    out["samples"] = [{"ids": x[r, :600].tolist(), "boundary": hard[r, :600].astype(int).tolist()} for r in range(3)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", required=True, help="comma-separated final.pkl paths")
    ap.add_argument("--data", default="/data/fineweb_edu")
    ap.add_argument("--probe_data", default="/data/fineweb_edu", help="filler text for kv (always prose)")
    ap.add_argument("--windows", type=int, default=64, help="held-out windows for boundary statistics")
    args = ap.parse_args()
    started = time.time()
    _, val = lm.load(args.data)
    _, prose = lm.load(args.probe_data)
    results = []
    for path in args.ckpts.split(","):
        payload = pickle.loads(pathlib.Path(path).read_bytes())
        cfg = argparse.Namespace(**payload["cfg"])
        if cfg.bf16:
            lm.MM = jnp.bfloat16
        params = jax.tree_util.tree_map(jnp.asarray, payload["params"])
        T = cfg.ctx
        batch = max(1, 16384 // T)
        row = {"ckpt": path, "cfg": {k: payload["cfg"].get(k) for k in
                                     ("arch", "posenc", "pattern", "forget", "d", "layers", "seed", "ctx", "ev_len",
                                      "ev_posenc", "ev_dmain", "data")}, "probes": {}}
        for name, items in probe_items(T, prose).items():
            row["probes"][name] = score_items(cfg, params, items, batch)
        if cfg.arch == "events":
            g = np.random.default_rng(5678)
            starts = g.integers(0, len(val) - T - 1, args.windows)
            x = np.stack([val[j:j + T] for j in starts]).astype(np.int32)
            row["boundaries"] = boundary_stats(cfg, params, x)
        results.append(row)
        print(json.dumps({"progress": path, "secs": round(time.time() - started, 1)}), file=sys.stderr, flush=True)
    print(json.dumps({"probe": results, "secs": round(time.time() - started, 1), "backend": jax.default_backend()}))


if __name__ == "__main__":
    main()
