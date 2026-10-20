"""
Tables for GROUPS.md section 7 (word problems over A5 and S5) from research/results/wp_*.jsonl:

    python3 research/wp_summary.py [grid ...]      # default: wp_main

Every cell is balanced accuracy %, mean (seed 0, 1, 2). 'late' is balanced accuracy over the second half
of the positions; 'len 64' is a length-16 model scored at length 64.
"""

import collections
import json
import pathlib
import statistics
import sys

R = pathlib.Path(__file__).parent / "results"
WP = ["wp_a5_16", "wp_a5_64", "wp_s5_16", "wp_s5_64"]
WS = ["ws_a5_16", "ws_a5_64", "ws_s5_16", "ws_s5_64"]


def rows(grids):
    out = []
    for g in grids:
        p = R / f"{g}.jsonl"
        if p.exists():
            out += [json.loads(l) for l in p.open() if l.strip()]
    for r in out:
        if "error" in r:
            print("ERROR", " ".join(r["argv"]), r["error"][-300:])
    return [r for r in out if "error" not in r]


def arm(r):
    m, L = r["model"], r["layers"]
    if m.startswith("holo"):
        d = int(m.split("_")[1][1:])
        name = "Newton (holo d=2)" if d == 2 else f"holo d={d}"
        if "prefix" not in m:
            name += " no prefix"
    elif m.startswith("orth"):
        name = "orthogonal RNN d=" + m.split("_")[1][1:]
    elif m.startswith("hhrnn"):
        name = f"Householder RNN d={m.split('_')[1][1:]} n_h={m.split('_nh')[1].split('_')[0]}"
    elif m.startswith("sa"):
        name = "softmax"
    elif m.startswith("deltaprod"):
        name = "DeltaProduct n_h=" + m.split("nh")[1]
    else:
        name = m
    return f"{name}, {L}L"


ORDER = [f"{a}, {L}L" for L in (1, 2) for a in
         ["holo d=3", "holo d=4", "holo d=5", "orthogonal RNN d=3", "orthogonal RNN d=5", "holo d=5 no prefix",
          "Householder RNN d=5 n_h=1", "Householder RNN d=5 n_h=2", "Householder RNN d=5 n_h=4", "Householder RNN d=4 n_h=4",
          "Newton (holo d=2)", "softmax", "DeltaProduct n_h=1", "DeltaProduct n_h=2", "DeltaProduct n_h=4"]]


def fmt(xs):
    if not xs:
        return ""
    return f"{100 * statistics.mean(xs):.1f} ({', '.join(f'{100 * x:.1f}' for x in xs)})"


def cells(rs, key):
    c = collections.defaultdict(list)
    for r in sorted(rs, key=lambda r: r["seed"]):
        v = key(r)
        if v is not None:
            c[(arm(r), r["task"])].append(v)
    return c


def table(c, cols, title, names=None):
    arms = [a for a in ORDER if any((a, t) in c for t in cols)]
    arms += sorted({a for a, t in c if t in cols} - set(arms))
    print(f"\n**{title}**\n")
    print("| Arm | " + " | ".join(names or cols) + " |")
    print("|---|" + "---|" * len(cols))
    for a in arms:
        print(f"| {a} | " + " | ".join(fmt(c.get((a, t), [])) for t in cols) + " |")


def main():
    grids = sys.argv[1:] or ["wp_main"]
    rs = rows(grids)
    bal = cells(rs, lambda r: r["bal_acc"])
    late = cells(rs, lambda r: r.get("bal_late"))
    lgen = cells(rs, lambda r: r["len"]["bal_acc"] if "len" in r else None)
    lgen_late = cells(rs, lambda r: r["len"]["bal_late"] if "len" in r else None)
    seq = cells(rs, lambda r: r["seq_acc"])
    table(bal, WP, "Word problem, |G| classes: balanced accuracy, every position")
    table(late, WP, "Word problem, |G| classes: balanced accuracy, second half of the positions")
    table(seq, WP, "Word problem, |G| classes: whole sequences right")
    table(bal, WS, "Stabiliser membership (binary): balanced accuracy, every position")
    table(late, WS, "Stabiliser membership (binary): balanced accuracy, second half")
    cols = ["wp_a5_16", "wp_s5_16", "ws_a5_16", "ws_s5_16"]
    table(lgen, cols, "Length generalisation: trained at 16, scored at 64 (every position)",
          ["A5 classes", "S5 classes", "A5 stabiliser", "S5 stabiliser"])
    table(lgen_late, cols, "Length generalisation: trained at 16, scored at 64 (positions 33-64)",
          ["A5 classes", "S5 classes", "A5 stabiliser", "S5 stabiliser"])
    # per-position accuracy, seed means, for the length-16 class tasks
    pp = collections.defaultdict(list)
    for r in rs:
        if r["task"] in ("wp_a5_16", "wp_s5_16"):
            pp[(arm(r), r["task"])].append(r["per_pos"])
    print("\n**Accuracy by position (length 16, mean over seeds), positions 1-16**\n")
    for (a, t), v in sorted(pp.items(), key=lambda kv: (kv[0][1], ORDER.index(kv[0][0]) if kv[0][0] in ORDER else 99)):
        m = [statistics.mean(x) for x in zip(*v)]
        print(f"- {t} {a}: " + " ".join(f"{100 * x:.0f}" for x in m))
    # irreps the first layer's rotations hold
    names = {"A5": ["1", "3", "3'", "4", "5"], "S5": ["1", "sgn", "4", "4'", "5", "5'", "6"]}
    print("\n**Irreps held by the first layer** (multiplicity >= 1/2 in a head with homomorphism error < 0.5; per seed)\n")
    print("| Task | Arm | Seed 0 | Seed 1 | Seed 2 |\n|---|---|---|---|---|")
    held = collections.defaultdict(dict)
    for r in rs:
        if "rep" in r:
            g = "A5" if "_a5_" in r["task"] else "S5"
            held[(r["task"], arm(r))][r["seed"]] = (", ".join(names[g][i] for i in r["rep"]["held"]) or "none") + f" ({r['rep']['hom_err_q'][0]:.2f})"
    for (t, a), v in sorted(held.items()):
        print(f"| {t} | {a} | " + " | ".join(v.get(s, "") for s in (0, 1, 2)) + " |")
    secs = [r["secs"] for r in rs]
    if secs:
        print(f"\n{len(rs)} runs, {sum(secs) / 3600:.2f} GPU-hours of training")
    return bal, late, lgen, lgen_late


if __name__ == "__main__":
    main()
