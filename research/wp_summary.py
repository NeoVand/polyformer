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
    # learning speed: the first evaluation (every tenth of training) at >= 90% balanced accuracy
    snap = cells(rs, lambda r: next((c[0] for c in r["curve"] if c[4] >= 0.9), None) if r["layers"] == 1 else None)
    print("\n**Steps to 90% balanced accuracy** (first evaluation at or above; 'never' if not within training)\n")
    print("| Arm | " + " | ".join(WP + WS) + " |\n|---|" + "---|" * len(WP + WS))
    allruns = collections.defaultdict(list)
    for r in sorted(rs, key=lambda r: r["seed"]):
        if r["layers"] == 1:
            allruns[(arm(r), r["task"])].append(next((c[0] for c in r["curve"] if c[4] >= 0.9), None))
    for a in [a for a in ORDER if any(any(v is not None for v in allruns.get((a, t), [])) for t in WP + WS)]:
        print(f"| {a} | " + " | ".join(", ".join("never" if v is None else f"{v:,}" for v in allruns[(a, t)]) for t in WP + WS) + " |")
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


def predictions(rs):
    """The registered predictions W1-W9 of GROUPS.md 7.6, each cell on 3 of 3 seeds unless noted."""
    by = collections.defaultdict(list)
    for r in sorted(rs, key=lambda r: r["seed"]):
        by[(arm(r), r["task"])].append(r)
    get = {"bal": lambda r: r["bal_acc"], "late": lambda r: r["bal_late"], "len": lambda r: r["len"]["bal_acc"]}
    out = []

    def cell(a, t, metric, op, v, need=3):
        rr = by.get((a, t), [])
        xs = [get[metric](r) for r in rr]
        ok = sum(op(x, v) for x in xs) >= need and len(xs) >= need
        return ok, f"{a} {t} {metric}: " + ", ".join(f"{100 * x:.1f}" for x in xs)

    ge, le, lt = (lambda x, v: x >= v), (lambda x, v: x <= v), (lambda x, v: x < v)

    def group(name, cells):
        res = [cell(*c) for c in cells]
        missing = [c for c, (_, d) in zip(cells, res) if d.endswith(": ")]
        verdict = "incomplete" if missing else ("holds" if all(ok for ok, _ in res) else "fails")
        out.append((name, verdict, [d for ok, d in res if not ok and not d.endswith(": ")], len(missing)))

    H = lambda d: f"holo d={d}, 1L"
    O = lambda d: f"orthogonal RNN d={d}, 1L"
    HH = lambda d, n: f"Householder RNN d={d} n_h={n}, 1L"
    group("W1", [(a, "wp_a5_16", "bal", ge, 0.99) for a in (H(3), H(4), H(5), O(5), HH(5, 2))]
          + [(a, "wp_s5_16", "bal", ge, 0.95) for a in (H(5), O(5), HH(5, 4), HH(4, 4))]
          + [(a, "wp_a5_64", "bal", ge, 0.95) for a in (H(3), O(3), HH(5, 2))]
          + [(a, "wp_s5_64", "bal", ge, 0.90) for a in (H(5), O(5), HH(5, 4))]
          + [(a, t, "bal", ge, 0.95) for t, a in (("ws_a5_16", H(3)), ("ws_a5_16", HH(5, 2)), ("ws_s5_16", H(5)), ("ws_s5_16", HH(5, 4)))]
          + [(a, t, "bal", ge, 0.90) for t, a in (("ws_a5_64", H(3)), ("ws_a5_64", HH(5, 2)), ("ws_s5_64", H(5)), ("ws_s5_64", HH(5, 4)))])
    group("W2", [(a, "wp_s5_16", "late", le, 0.20) for a in (H(3), H(4), HH(5, 2))]
          + [(HH(5, 1), "wp_a5_16", "late", le, 0.20), (H(3), "ws_s5_16", "late", le, 0.60)])
    N = "Newton (holo d=2), 1L"
    group("W3", [(N, t, "bal", le, v) for t, v in (("wp_a5_16", 0.229), ("wp_a5_64", 0.086), ("wp_s5_16", 0.221),
                                                   ("wp_s5_64", 0.083), ("ws_a5_16", 0.647), ("ws_s5_16", 0.637))])
    w4 = []
    for L in (1, 2):
        for t in WP + WS:
            if (f"softmax, {L}L", t) in by:
                w4.append((f"softmax, {L}L", t, "late", le, 0.05 if t.startswith("wp") else 0.60))
    group("W4", w4)
    # W5: per-position means over seeds
    w5 = []
    for t in ("wp_a5_16", "wp_s5_16"):
        rr = by.get(("holo d=5 no prefix, 1L", t), [])
        if len(rr) == 3:
            m = [statistics.mean(x) for x in zip(*[r["per_pos"] for r in rr])]
            ok = all(x >= 0.95 for x in m[:3]) and all(x <= 0.10 for x in m[4:])
            w5.append((ok, f"{t}: " + " ".join(f"{100 * x:.0f}" for x in m)))
    out.append(("W5", ("holds" if all(ok for ok, _ in w5) else "fails") if len(w5) == 2 else "incomplete",
                [d for ok, d in w5 if not ok], 2 - len(w5)))
    # W6: holonomy against the orthogonal RNN of the same d, seed means within 3 points
    w6 = []
    for t, d in (("wp_a5_16", 5), ("wp_a5_64", 3), ("wp_s5_16", 5), ("wp_s5_64", 5)):
        a, b = by.get((H(d), t), []), by.get((O(d), t), [])
        if len(a) == 3 and len(b) == 3:
            ma, mb = statistics.mean(r["bal_acc"] for r in a), statistics.mean(r["bal_acc"] for r in b)
            w6.append((abs(ma - mb) <= 0.03, f"{t} d={d}: holo {100 * ma:.1f}, orth {100 * mb:.1f}"))
    out.append(("W6", ("holds" if all(ok for ok, _ in w6) else "fails") if len(w6) == 4 else "incomplete",
                [d for _, d in w6], 4 - len(w6)))
    w7 = [("holo d=3, 2L", "wp_s5_16", "bal", le, 0.30), ("DeltaProduct n_h=2, 2L", "wp_s5_16", "bal", le, 0.20)]
    w7 += [("Newton (holo d=2), 2L", t, "late", le, 0.05) for t in ("wp_a5_16", "wp_s5_16")]
    w7 += [("softmax, 2L", t, "late", le, 0.05) for t in WP]
    group("W7", w7)
    w8 = []
    for n in (1, 2, 4):
        for t in WP:
            a = f"DeltaProduct n_h={n}, 1L"
            if (a, t) in by:
                w8.append((a, t, "late", le, 0.05))
                if t.endswith("_16"):
                    w8.append((a, t, "bal", le, 0.20))
    w8 += [("DeltaProduct n_h=4, 1L", "ws_s5_16", "bal", ge, 0.95), ("DeltaProduct n_h=2, 1L", "ws_a5_16", "bal", le, 0.70)]
    group("W8", w8)
    group("W9", [(a, "wp_a5_16", "len", ge, 0.95) for a in (H(3), H(4), H(5), O(5), HH(5, 2))]
          + [(HH(5, 4), "wp_s5_16", "len", ge, 0.95), (H(5), "wp_s5_16", "len", lt, 0.95, 2), (O(5), "wp_s5_16", "len", lt, 0.95, 2)])
    print("\n**Registered predictions (GROUPS.md 7.6)**\n")
    print("| Prediction | Outcome | Failing or compared cells |\n|---|---|---|")
    for name, verdict, bad, miss in out:
        print(f"| {name} | {verdict}{f' ({miss} cells missing)' if miss else ''} | {'; '.join(bad)} |")
    return out


if __name__ == "__main__":
    main()
    predictions(rows(sys.argv[1:] or ["wp_main"]))
