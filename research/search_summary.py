"""
Tables and gate decisions for SEARCH.md section 8, from research/results/{tok_s0_lr,tok_s0,diag_s1,tok_s2}.jsonl:

    python3 research/search_summary.py [s0|s1|s2]

Prints markdown. Nothing here trains or changes a result; every number comes from the raw rows.
"""

import collections
import json
import pathlib
import statistics as st
import sys

RES = pathlib.Path(__file__).resolve().parent / "results"


def rows(grid):
    p = RES / f"{grid}.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if not r.get("error"):
                out.append(r)
    return out


def tag(r):
    t = f"{'free-field' if r['arch'] == 'sfa' else 'softmax'} {r['layers']}L"
    if r.get("alpha0") == 2:
        t += ", all arities off at init"
    if r.get("lookback"):
        t += " + look-back"
    if r.get("hops", 1) > 1:
        t += f" + walks (R = {r['hops']})"
    return t


def corpus(r):
    return r["data"].rstrip("/").split("/")[-1]


def s0():
    print("**S0 learning-rate sweep** (100M tokens, seed 0; held-out loss in nats per token, best rate in bold)\n")
    sweep = collections.defaultdict(dict)
    for r in rows("tok_s0_lr"):
        sweep[(corpus(r), tag(r))][r["lr"]] = r["val_loss"]
    lrs = sorted({lr for d in sweep.values() for lr in d})
    print("| Corpus | Model | " + " | ".join(f"lr {lr:g}" for lr in lrs) + " |")
    print("|---|---|" + "---|" * len(lrs))
    for (c, t), d in sorted(sweep.items()):
        b = min(d, key=d.get)
        print(f"| {c} | {t} | " + " | ".join((f"**{d[lr]:.4f}**" if lr == b else f"{d[lr]:.4f}") if lr in d else "" for lr in lrs) + " |")
    base = {}
    for (c, t), d in sweep.items():
        if t == "softmax 6L":
            base[c] = min(d.values())
    print("\nBest loss relative to softmax 6L at 100M tokens: " + "; ".join(
        f"{c} {t}: {min(d.values()) / base[c] - 1:+.2%}" for (c, t), d in sorted(sweep.items()) if c in base and t != "softmax 6L"))

    full = rows("tok_s0")
    if not full:
        return
    print("\n**S0 at 400M tokens, FineWeb-Edu** (three seeds; loss mean, then each seed; FLOPs relative to softmax 6L)\n")
    g = collections.defaultdict(dict)
    meta = {}
    for r in full:
        g[tag(r)][r["seed"]] = r["val_loss"]
        meta[tag(r)] = (r["train_flops"], r["nonembed"], r["lr"])
    ref = g.get("softmax 6L", {})
    f0 = meta.get("softmax 6L", (1, 0, 0))[0]
    print("| Model | Non-embedding | Training FLOPs | x softmax | Rate | Loss (mean) | Seeds | vs softmax 6L, per seed |")
    print("|---|---|---|---|---|---|---|---|")
    for t, d in sorted(g.items(), key=lambda kv: meta[kv[0]][0]):
        fl, ne, lr = meta[t]
        rel = [d[s] / ref[s] - 1 for s in sorted(d) if s in ref]
        print(f"| {t} | {ne / 1e6:.1f}M | {fl:.2e} | {fl / f0:.3f} | {lr:g} | {st.mean(d.values()):.4f} | "
              + ", ".join(f"{d[s]:.4f}" for s in sorted(d)) + " | " + ", ".join(f"{x:+.2%}" for x in rel) + " |")
    # the softmax frontier between 6 and 7 layers, at free-field's FLOPs
    if "softmax 7L" in g and "free-field 6L" in g:
        a, b = meta["softmax 6L"][0], meta["softmax 7L"][0]
        x = meta["free-field 6L"][0]
        w = (x - a) / (b - a)
        fr = {s: g["softmax 6L"][s] * (1 - w) + g["softmax 7L"][s] * w for s in g["softmax 6L"] if s in g["softmax 7L"]}
        print("\nFree-field 6L against the softmax frontier interpolated to its FLOPs: " + ", ".join(
            f"seed {s} {g['free-field 6L'][s] / fr[s] - 1:+.2%}" for s in sorted(fr) if s in g["free-field 6L"]))
    for t in ("free-field 5L", "free-field 5L, all arities off at init"):
        if t in g:
            ok = [g[t][s] <= 0.99 * ref[s] for s in sorted(g[t]) if s in ref]
            print(f"\nGate ({t} at 0.97x FLOPs, >= 1% below softmax 6L on 3/3 seeds): "
                  + ("GO" if len(ok) == 3 and all(ok) else "NO-GO") + f" ({sum(ok)}/{len(ok)} seeds)")


FAMILY = {"mqar": "recall", "mqar2": "recall", "selcopy": "copy/induction", "indist": "copy/induction",
          "phop4": "p-hop", "phop8": "p-hop", "phop16": "p-hop", "dyck2": "Dyck-2", "add": "addition", "match3": "Match-3"}
PAIRS = [("ff", "softmax"), ("ffw", "softmaxw")]


def s1():
    g = collections.defaultdict(list)
    for r in rows("diag_s1"):
        g[(r["task"], r["layers"], r["model"])].append(r["acc"])
    if not g:
        return
    models = ["softmax", "ff", "softmaxw", "lookback", "ffw"]
    print("**S1 diagnostic map** (accuracy on answer positions, mean of seeds with min-max; balanced for Match-3, whole "
          "sums for addition; ff vs softmax and ffw vs softmaxw/lookback are FLOP-matched)\n")
    print("| Task | Layers | " + " | ".join(models) + " |")
    print("|---|---|" + "---|" * len(models))
    wins = collections.defaultdict(set)
    for task in FAMILY:
        for L in (1, 2):
            cells = []
            for m in models:
                v = g.get((task, L, m))
                cells.append(f"{100 * st.mean(v):.1f} ({100 * min(v):.0f}-{100 * max(v):.0f})" if v else "")
            print(f"| {task} | {L} | " + " | ".join(cells) + " |")
            for a, b in PAIRS:
                if g.get((task, L, a)) and g.get((task, L, b)) and st.mean(g[(task, L, a)]) - st.mean(g[(task, L, b)]) >= 0.10:
                    wins[FAMILY[task]].add(f"{task} {L}L {a}")
    print("\nFamilies where a free-field model beats its FLOP-matched softmax by >= 10 points: "
          + ("; ".join(f"{f}: {', '.join(sorted(v))}" for f, v in wins.items()) or "none"))
    print("Gate (>= 2 families): " + ("GO" if len(wins) >= 2 else "NO-GO"))
    lb = []
    for task in FAMILY:
        for L in (1, 2):
            a, c = g.get((task, L, "ffw")), g.get((task, L, "lookback"))
            if a and c and abs(st.mean(a) - st.mean(c)) >= 0.10:
                lb.append(f"{task} {L}L: ffw {100 * st.mean(a):.1f} vs look-back {100 * st.mean(c):.1f}")
    print("Where free-field with walks and the look-back control differ by >= 10 points: " + ("; ".join(lb) or "nowhere"))


def s2():
    rs = rows("tok_s2") + rows("tok_s2b")
    if not rs:
        return
    # every model at its own best rate (mean final loss over seeds); tok_s2b holds the look-back variants'
    # runs at lower rates, after they proved unstable at 4e-3 on FineWeb-Edu
    loss = collections.defaultdict(list)
    for r in rs:
        loss[(corpus(r), tag(r), r["lr"])].append(r["val_loss"])
    best = {}
    for (c, t, lr), v in loss.items():
        if (c, t) not in best or st.mean(v) < st.mean(loss[(c, t, best[(c, t)])]):
            best[(c, t)] = lr
    print("Rates used: " + "; ".join(f"{c} {t}: {lr:g}" for (c, t), lr in sorted(best.items())) + "\n")
    by = collections.defaultdict(dict)
    for r in rs:
        if best[(corpus(r), tag(r))] == r["lr"]:
            by[(corpus(r), r["seed"])][tag(r)] = r

    def gap(x):
        return x.get("rep1", 0) - x.get("rep2", 0)

    print("**S2 induction through training** (100M tokens; tokens, in millions, until a measure first reaches half of "
          "softmax's final value at the same seed)\n")
    for measure, fn in (("repeated-token gap", gap), ("in-context score", lambda x: x.get("icl", 0))):
        print(f"\n_{measure}_\n")
        names = sorted({t for d in by.values() for t in d})
        print("| Corpus | Seed | softmax final | " + " | ".join(names) + " |")
        print("|---|---|---|" + "---|" * len(names))
        ratio = collections.defaultdict(list)
        for (c, s), d in sorted(by.items()):
            if "softmax 6L" not in d:
                continue
            fin = fn(d["softmax 6L"]["curve"][-1])
            cells = []
            for t in names:
                hit = None
                if t in d and fin > 0:
                    hit = next((x["tokens"] for x in d[t]["curve"] if fn(x) >= 0.5 * fin), None)
                cells.append(f"{hit / 1e6:.1f}" if hit else "never")
                if hit and t != "softmax 6L":
                    base = next((x["tokens"] for x in d["softmax 6L"]["curve"] if fn(x) >= 0.5 * fin), None)
                    ratio[(c, t)].append(hit / base if base else None)
            print(f"| {c} | {s} | {fin:.3f} | " + " | ".join(cells) + " |")
        if measure == "repeated-token gap":
            for (c, t), v in sorted(ratio.items()):
                if "walks" in t:
                    ok = [x is not None and x <= 0.6 for x in v]
                    print(f"\nGate ({c}, {t}: <= 60% of softmax's tokens on 3/3 seeds): "
                          + ("GO" if len(ok) == 3 and all(ok) else "NO-GO") + " (ratios " + ", ".join(f"{x:.2f}" if x else "-" for x in v) + ")")
    print("\n_final held-out loss at 100M tokens_\n")
    fl = collections.defaultdict(list)
    for (c, s), d in by.items():
        for t, r in d.items():
            fl[(c, t)].append(r["val_loss"])
    for (c, t), v in sorted(fl.items()):
        print(f"- {c}, {t}: {st.mean(v):.4f} (" + ", ".join(f"{x:.4f}" for x in v) + ")")


if __name__ == "__main__":
    which = sys.argv[1:] or ["s0", "s1", "s2"]
    for w in which:
        {"s0": s0, "s1": s1, "s2": s2}[w]()
        print()
