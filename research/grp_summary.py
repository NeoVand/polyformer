"""
Tables and registered decisions for GROUPS.md from research/results/grp_*.jsonl:

    python3 research/grp_summary.py [grid ...]      # default: grp_e1 grp_e2
"""

import collections
import json
import pathlib
import statistics
import sys

R = pathlib.Path(__file__).parent / "results"


def rows(grids):
    out = []
    for g in grids:
        p = R / f"{g}.jsonl"
        if p.exists():
            out += [json.loads(l) for l in p.open() if l.strip()]
    bad = [r for r in out if "error" in r]
    for r in bad:
        print("ERROR", " ".join(r["argv"]), r["error"][-200:])
    return [r for r in out if "error" not in r]


def arm(r):
    m = r["model"]
    if m.startswith("sa"):
        return f"softmax {r['layers']}L" + (f" {m.split('_', 1)[1]}" if "_" in m else "")
    if m.startswith("holo"):
        return "holo d=" + m.split("_")[1][1:]
    if m.startswith("newton"):
        return "newton"
    return m


def fmt(xs):
    return f"{100 * statistics.mean(xs):.1f} ({', '.join(f'{100 * x:.1f}' for x in xs)})"


def table(rs, tasks, order):
    cell = collections.defaultdict(list)
    for r in sorted(rs, key=lambda r: r["seed"]):
        cell[(arm(r), r["task"])].append(r["bal_acc"])
    arms = [a for a in order if any((a, t) in cell for t in tasks)]
    arms += sorted({a for a, _ in cell} - set(arms))
    print("| Arm | " + " | ".join(tasks) + " |")
    print("|---|" + "---|" * len(tasks))
    for a in arms:
        print(f"| {a} | " + " | ".join(fmt(cell[(a, t)]) if (a, t) in cell else "" for t in tasks) + " |")
    return cell


def main():
    grids = sys.argv[1:] or ["grp_e1", "grp_e2"]
    rs = rows(grids)
    e1 = [r for r in rs if r["task"].startswith("zs")]
    e2 = [r for r in rs if r["task"].startswith("g3_")]
    if e1:
        print("\n**Experiment 1** (balanced accuracy %, mean (seeds 0, 1, 2))\n")
        c1 = table(e1, ["zs3", "zs4", "zs5"], [f"softmax {L}L {e}" for e in ("char", "charrot") for L in (1, 2)]
                   + [f"softmax {L}L" for L in (1, 2)])
        best = max(([c1.get((f"softmax {L}L char", "zs4"), []) for L in (1, 2)]), key=lambda xs: statistics.mean(xs) if xs else 0)
        both = [c1.get((f"softmax {L}L char", "zs4"), []) for L in (1, 2)]
        if best and len(best) == 3:
            if all(x >= 0.9 for x in best):
                v = "representation suffices"
            elif all(len(xs) == 3 and all(x <= 0.6 for x in xs) for xs in both):
                v = "composition is needed"
            else:
                v = "partial"
            print(f"\nExperiment 1 reading (zs4, char): {v}")
    if e2:
        print("\n**Experiment 2** (balanced accuracy %, mean (seeds))\n")
        order = [f"holo d={d}" for d in (2, 3, 4, 5, 8)] + ["newton", "softmax 1L", "softmax 3L"]
        c2 = table(e2, ["g3_z12", "g3_a4", "g3_z60", "g3_a5"], order)
        print("\n**Held Plancherel mass** (from the trained rotations: mean over seeds, with reachable mass)\n")
        held = collections.defaultdict(list)
        reach = {}
        for r in e2:
            if "rep" in r:
                held[(arm(r), r["task"])].append(r["rep"]["mass"])
                reach[(arm(r), r["task"])] = r["rep"]["reachable_mass"]
        tasks = ["g3_z12", "g3_a4", "g3_z60", "g3_a5"]
        print("| Arm | " + " | ".join(tasks) + " |")
        print("|---|" + "---|" * len(tasks))
        for a in [f"holo d={d}" for d in (2, 3, 4, 5, 8)]:
            print(f"| {a} | " + " | ".join(f"{statistics.mean(held[(a, t)]):.2f} of {reach[(a, t)]:.2f}" if (a, t) in held else "" for t in tasks) + " |")
        # registered predictions
        def all_ge(a, t, v):
            xs = c2.get((a, t), [])
            return len(xs) == 3 and all(x >= v for x in xs)

        def all_le(a, t, v):
            xs = c2.get((a, t), [])
            return len(xs) == 3 and all(x <= v for x in xs)

        def all_between(a, t, lo, hi):
            xs = c2.get((a, t), [])
            return len(xs) == 3 and all(lo < x < hi for x in xs)

        layers = ["newton"] + [f"holo d={d}" for d in (2, 3, 4, 5, 8)]
        p1 = all(all_ge(a, t, 0.95) for a in layers for t in ("g3_z12", "g3_z60"))
        p2 = all(all_le(a, "g3_a5", 0.55) for a in ("newton", "holo d=2")) and all(all_ge(a, "g3_a5", 0.95) for a in ("holo d=5", "holo d=8"))
        p3 = all(all_between(a, "g3_a4", 0.55, 0.90) for a in ("newton", "holo d=2")) and all(all_ge(f"holo d={d}", "g3_a4", 0.95) for d in (3, 4, 5, 8))
        means = [statistics.mean(c2[(f"holo d={d}", "g3_a5")]) if c2.get((f"holo d={d}", "g3_a5")) else None for d in (2, 3, 4, 5)]
        p4 = None not in means and all(b >= a - 1e-9 for a, b in zip(means, means[1:])) and all(
            all_between(f"holo d={d}", "g3_a5", 0.55, 0.95) for d in (3, 4))
        print("\n| Prediction | Holds |\n|---|---|")
        for name, v in (("P1 abelian groups: every layer >= 95%", p1),
                        ("P2 A5: Newton, d=2 <= 55%; d=5, d=8 >= 95%", p2),
                        ("P3 A4: Newton, d=2 in (55, 90); d>=3 >= 95%", p3),
                        ("P4 A5 ladder non-decreasing, d=3 and d=4 in (55, 95)", p4)):
            print(f"| {name} | {'yes' if v else 'no'} |")
        print("\n**P5, the Plancherel law** (accuracy against 1/2 + mass/2, held mass per run)\n")
        print("| Run | Accuracy | Held mass | 1/2 + mass/2 | Gap |\n|---|---|---|---|---|")
        for r in sorted(e2, key=lambda r: (r["task"], arm(r), r["seed"])):
            if "rep" in r:
                pred = 0.5 + r["rep"]["mass"] / 2
                print(f"| {r['task']} {arm(r)} s{r['seed']} | {100 * r['bal_acc']:.1f} | {r['rep']['mass']:.2f} | {100 * pred:.1f} | {100 * (r['bal_acc'] - pred):+.1f} |")


if __name__ == "__main__":
    main()
