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
        ceil = {"g3_a4": 0.831, "g3_a5": 0.772}       # order-blind ceilings (GROUPS.md section 2)
        p1 = all(all_ge(a, t, 0.95) for a in layers for t in ("g3_z12", "g3_z60"))
        p2 = all(all_le(a, "g3_a5", ceil["g3_a5"] + 0.02) for a in ("newton", "holo d=2")) and all(all_ge(a, "g3_a5", 0.95) for a in ("holo d=5", "holo d=8"))
        p3 = all(all_le(a, "g3_a4", ceil["g3_a4"] + 0.02) for a in ("newton", "holo d=2")) and all(all_ge(f"holo d={d}", "g3_a4", 0.95) for d in (3, 4, 5, 8))
        means = {d: statistics.mean(c2[(f"holo d={d}", "g3_a5")]) for d in (3, 4, 5) if c2.get((f"holo d={d}", "g3_a5"))}
        if all_ge("holo d=3", "g3_a5", 0.95):
            p4 = "faithfulness"
        elif all_le("holo d=3", "g3_a5", 0.90) and len(means) == 3 and means[3] < means[4] < means[5]:
            p4 = "Plancherel"
        else:
            p4 = "undecided"
        print("\n| Prediction | Registered criterion | Outcome |\n|---|---|---|")
        for name, crit, v in (("P1", "Z12, Z60: Newton and every d >= 95%", "holds" if p1 else "fails"),
                              ("P2", "A5: Newton, d=2 <= 79.2%; d=5, d=8 >= 95%", "holds" if p2 else "fails"),
                              ("P3", "A4: Newton, d=2 <= 85.1%; d>=3 >= 95%", "holds" if p3 else "fails"),
                              ("P4", "A5 d=3 >= 95% (faithfulness) or <= 90% with rising means (Plancherel)", p4)):
            print(f"| {name} | {crit} | {v} |")
        print("\n**Irreps held** (multiplicity >= 1/2 in a head with homomorphism error < 0.5; per seed)\n")
        names = {"g3_a4": ["1", "1'", "1''", "3"], "g3_a5": ["1", "3", "3'", "4", "5"]}
        print("| Task | Arm | Seed 0 | Seed 1 | Seed 2 |\n|---|---|---|---|---|")
        for t in ("g3_a4", "g3_a5"):
            for d in (2, 3, 4, 5, 8):
                runs = sorted((r for r in e2 if r["task"] == t and arm(r) == f"holo d={d}" and "rep" in r), key=lambda r: r["seed"])
                cells = [", ".join(names[t][i] for i in r["rep"]["held"]) or "none" for r in runs]
                print(f"| {t} | d={d} | " + " | ".join(cells) + " |")

if __name__ == "__main__":
    main()
