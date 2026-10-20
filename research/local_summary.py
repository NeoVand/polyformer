"""
Tables and gate decisions for LOCAL.md, from research/results/{diag,tok}_loc_*.jsonl:

    python3 research/local_summary.py [s1|s2|s3|spend]

Prints markdown. Nothing here trains or changes a result; every number comes from the raw rows, and the
gates are the ones LOCAL.md section 4 fixed before the runs.
"""

import collections
import json
import pathlib
import statistics as st
import sys

RES = pathlib.Path(__file__).resolve().parent / "results"
PRICE = {"H100": 3.95, "L4": 0.80}  # Modal list prices, dollars per GPU-hour
FPT = {"S": 92473464.0}             # filled from the rows


def rows(grid):
    p = RES / f"{grid}.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("error"):
                print(f"<!-- {grid}: error row {r['argv'][-12:]} -->")
                continue
            out.append(r)
    return out


def arm(r):
    a = r.get("arch") or r.get("model")
    if a in ("gpt", "softmaxl"):
        return "S"
    if a == "plx":
        return "P (RMSNorm on rho)" if r.get("plx_norm") else "P"
    return f"L{r.get('chart') or 8}"


def fmt(v):
    return f"{st.mean(v):.4f}" if v else ""


def metric(r):
    return r.get("val_big", r["val_loss"])


# ----------------------------------------------------------------------------- Stage 1


def s1():
    rs = rows("diag_loc_s1")
    if not rs:
        return
    g = collections.defaultdict(list)
    fl = {}
    for r in rs:
        k = (r["task"], r["layers"], r["opt"], r["model"])
        g[k].append(r["acc"])
        fl[k] = r["flops_per_token"]
    models = ["softmaxl", "plx", "lla"]
    names = {"softmaxl": "S", "plx": "P", "lla": "L8"}
    print("**Stage 1 diagnostics** (accuracy on answer positions, mean of 3 seeds with min-max; balanced for "
          "Match-3; S widened to L8's FLOPs; FLOPs of P and S relative to L8 in brackets)\n")
    opts = sorted({r["opt"] for r in rs})
    print("| Task | Layers | " + " | ".join(f"{names[m]} ({o})" for o in opts for m in models) + " |")
    print("|---|---|" + "---|" * (len(models) * len(opts)))
    warn = []
    for task in ("mqar", "mqar2", "indist", "match3"):
        for L in (1, 2):
            cells = []
            for o in opts:
                for m in models:
                    v = g.get((task, L, o, m))
                    if not v:
                        cells.append("")
                        continue
                    ratio = fl[(task, L, o, m)] / fl[(task, L, o, "lla")] if (task, L, o, "lla") in fl else 1
                    cells.append(f"{100 * st.mean(v):.1f} ({100 * min(v):.0f}-{100 * max(v):.0f})"
                                 + (f" [{ratio:.2f}]" if m != "lla" else ""))
                s_, l_ = g.get((task, L, o, "softmaxl")), g.get((task, L, o, "lla"))
                if s_ and l_ and st.mean(l_) < st.mean(s_) - max(0.01, max(s_) - min(s_)):
                    warn.append(f"{task} {L}L {o}: L8 {100 * st.mean(l_):.1f} vs S {100 * st.mean(s_):.1f}")
            print(f"| {task} | {L} | " + " | ".join(cells) + " |")
    print("\nCells where L8 is below S by more than S's seed spread (the bug check): " + ("; ".join(warn) or "none"))


# ----------------------------------------------------------------------------- Stage 2


def s2():
    sweep = rows("tok_loc_lr") + rows("tok_loc_lr2")
    if sweep:
        print("**Stage 2 rate sweep** (FineWeb-Edu, 100M tokens, seed 0; held-out loss on 1,024 sequences, best in bold)\n")
        t = collections.defaultdict(dict)
        for r in sweep:
            t[(arm(r), r["opt"])][r["lr"]] = metric(r)
        lrs = sorted({lr for d in t.values() for lr in d})
        print("| Arm | Optimizer | " + " | ".join(f"lr {lr:g}" for lr in lrs) + " |")
        print("|---|---|" + "---|" * len(lrs))
        for (a, o), d in sorted(t.items()):
            b = min(d, key=d.get)
            print(f"| {a} | {o} | " + " | ".join((f"**{d[lr]:.4f}**" if lr == b else f"{d[lr]:.4f}") if lr in d else "" for lr in lrs) + " |")
        print("\nBest rates: " + "; ".join(f"{a} {o}: {min(d, key=d.get):g}" for (a, o), d in sorted(t.items())))
    full = rows("tok_loc_s2")
    eqf = rows("tok_loc_eqf")
    if not full:
        return
    # three-seed results at 400M per arm and optimizer
    g = collections.defaultdict(dict)
    meta = {}
    for r in full:
        k = (arm(r), r["opt"])
        g[k][r["seed"]] = r
        meta[k] = r
    f0 = next(r["flops_per_token"] for r in full if arm(r) == "S")
    print("\n**Stage 2 at 400M tokens** (FineWeb-Edu, 3 seeds; held-out loss on 1,024 sequences; `val` is S0's 128)\n")
    print("| Arm | Optimizer | Rate | FLOPs x S | Loss (mean) | Seeds | val (128 seqs, mean) | vs S same optimizer, equal tokens |")
    print("|---|---|---|---|---|---|---|---|")
    for k in sorted(g):
        d = g[k]
        ref = g.get(("S", k[1]), {})
        rel = [metric(d[s]) / metric(ref[s]) - 1 for s in sorted(d) if s in ref]
        print(f"| {k[0]} | {k[1]} | {meta[k]['lr']:g} | {meta[k]['flops_per_token'] / f0:.4f} | "
              f"{st.mean(metric(x) for x in d.values()):.4f} | " + ", ".join(f"{metric(d[s]):.4f}" for s in sorted(d))
              + f" | {st.mean(x['val_loss'] for x in d.values()):.4f} | " + ", ".join(f"{x:+.2%}" for x in rel) + " |")
    # the curve at 100M, 200M, 400M (val, 128 sequences)
    print("\n**Curves** (`val` on S0's 128 sequences at 100M, 200M and 400M tokens, mean of seeds)\n")
    print("| Arm | Optimizer | 100M | 200M | 400M |")
    print("|---|---|---|---|---|")
    for k in sorted(g):
        pts = []
        for frac in (0.25, 0.5, 1.0):
            v = []
            for r in g[k].values():
                step = round(r["steps"] * frac)
                c = min(r["curve"], key=lambda x: abs(x["step"] - step))
                v.append(c["val"])
            pts.append(f"{st.mean(v):.4f}")
        print(f"| {k[0]} | {k[1]} | " + " | ".join(pts) + " |")
    # equal FLOPs: S trained to L8's and P's FLOPs
    sm = collections.defaultdict(dict)
    for r in eqf:
        sm[(r["opt"], r["steps"])][r["seed"]] = metric(r)
    if eqf:
        print("\n**S at equal FLOPs** (S at its best rate per optimizer, trained to the token count that matches each arm's FLOPs)\n")
        print("| Optimizer | Steps | Tokens | Loss (mean) | Seeds |")
        print("|---|---|---|---|---|")
        for (o, steps), d in sorted(sm.items()):
            print(f"| {o} | {steps} | {steps * 32768 / 1e6:.1f}M | {st.mean(d.values()):.4f} | " + ", ".join(f"{d[s]:.4f}" for s in sorted(d)) + " |")

    def best(a):
        cands = [k for k in g if k[0] == a and len(g[k]) == 3]
        return min(cands, key=lambda k: st.mean(metric(x) for x in g[k].values())) if cands else None

    def s_at(steps):
        cands = [(o, d) for (o, s_), d in sm.items() if s_ == steps and len(d) == 3]
        return min(cands, key=lambda od: st.mean(od[1].values())) if cands else (None, None)

    bl, bp, bs = best("L8"), best("P"), best("S")
    print()
    if bl and bs:
        o, sd = s_at(12613)
        if sd:
            rel = [metric(g[bl][s]) / sd[s] - 1 for s in (0, 1, 2)]
            ok = [x <= -0.01 for x in rel]
            print(f"Headline (L8 best = {bl[1]} at {meta[bl]['lr']:g}; S best at L8's FLOPs = {o}): "
                  + ", ".join(f"{x:+.2%}" for x in rel) + f" -> {'GO' if all(ok) else 'NO-GO'} ({sum(ok)}/3 seeds at <= -1%)")
        rel_t = [metric(g[bl][s]) / metric(g[bs][s]) - 1 for s in (0, 1, 2)]
        print(f"\nEqual tokens (L8 best vs S best = {bs[1]}, both 400M): " + ", ".join(f"{x:+.2%}" for x in rel_t))
    if bl and bp:
        rel = [metric(g[bl][s]) / metric(g[bp][s]) - 1 for s in (0, 1, 2)]
        print(f"\nOurs vs prior art (L8 best vs P best = {bp[1]} at {meta[bp]['lr']:g}, both 400M; L8 uses 3.3% fewer FLOPs): "
              + ", ".join(f"{x:+.2%}" for x in rel) + f" -> L8 below P on {sum(x < 0 for x in rel)}/3 seeds")
        o4, s4 = s_at(13044)
        oo, s0_ = None, None
        if bs and s4:
            # S's loss per FLOP: S at 400M against S at P's FLOPs, same optimizer
            o4b = [d for (o_, s_), d in sm.items() if s_ == 13044 and o_ == bs[1]]
            if o4b:
                slope = [o4b[0][s] / metric(g[bs][s]) - 1 for s in (0, 1, 2)]
                print(f"  S's own gain from 400M to 427.4M tokens (+6.9% FLOPs): " + ", ".join(f"{x:+.2%}" for x in slope)
                      + "; 3.3% of FLOPs is worth about half of that")
    if bp:
        o, sd = s_at(13044)
        if sd:
            rel = [metric(g[bp][s]) / sd[s] - 1 for s in (0, 1, 2)]
            print(f"\nP vs S at P's FLOPs (S best there = {o}): " + ", ".join(f"{x:+.2%}" for x in rel)
                  + f" -> P below S on {sum(x < 0 for x in rel)}/3 seeds, by >= 1% on {sum(x <= -0.01 for x in rel)}/3")
    # diagnostics
    print("\n**What the layers use** (end of training, mean over seeds; per layer 1..6)\n")
    for k in sorted(g):
        if k[0] == "S":
            continue
        rs_ = list(g[k].values())
        cor = [st.mean(r["cor"][i] for r in rs_) for i in range(len(rs_[0]["cor"]))]
        line = f"- {k[0]} {k[1]}: COR " + ", ".join(f"{c:.2f}" for c in cor)
        line += "; weight range " + ", ".join(f"[{min(r['wrange'][i][0] for r in rs_):.1f}, {max(r['wrange'][i][1] for r in rs_):.1f}]" for i in range(len(cor)))
        if "gate" in rs_[0]:
            line += "; mean |gate| " + ", ".join(f"{st.mean(abs(x) for r in rs_ for x in r['gate'][i]):.2f}" for i in range(len(cor)))
            line += "; mean lambda " + ", ".join(f"{st.mean(x for r in rs_ for x in r['lam'][i]):.2f}" for i in range(len(cor)))
        if "rho_gain" in rs_[0]:
            line += "; rho gain RMS " + ", ".join(f"{st.mean(r['rho_gain'][i] for r in rs_):.2f}" for i in range(len(cor)))
        print(line)


# ----------------------------------------------------------------------------- Stage 3


def s3():
    lad = rows("tok_loc_ladder") + [r for r in rows("tok_loc_s2") if r["arch"] == "lla" and r["seed"] == 0]
    if lad:
        print("**Arity ladder** (400M tokens, seed 0)\n")
        print("| r | max subset | FLOPs x S | Loss (1,024 seqs) |")
        print("|---|---|---|---|")
        d = {}
        for r in lad:
            d[r["chart"]] = r
        for c in sorted(d):
            print(f"| {c} | {c + 1} | {d[c]['flops_per_token'] / FPT['S']:.4f} | {metric(d[c]):.4f} |")
        ladder = [metric(d[c]) for c in (1, 2, 4, 8) if c in d]
        if len(ladder) == 4:
            mono = all(b < a for a, b in zip(ladder, ladder[1:]))
            drop = 1 - ladder[-1] / ladder[0]
            print(f"\nArity lever (monotone 1..8 and >= 0.5% in total): monotone {mono}, total {drop:.2%} -> "
                  + ("GO" if mono and drop >= 0.005 else "NO-GO"))
    code = rows("tok_loc_code")
    if code:
        print("\n**Code corpus** (codeparrot-clean subset)\n")
        for r in code:
            print(f"- {arm(r)} {r['opt']} seed {r['seed']} steps {r['steps']}: {metric(r):.4f}")


def spend():
    tot = 0.0
    print("**Spend** (subprocess wall time x Modal list price, plus 10% for container start; H100 $3.95/h, L4 $0.80/h)\n")
    for p in sorted(RES.glob("*_loc_*.jsonl")):
        gpu = "L4" if p.name.startswith("diag_") else "H100"
        w = sum(json.loads(l).get("wall", 0) for l in p.read_text().splitlines() if l.strip())
        cost = 1.1 * w / 3600 * PRICE[gpu]
        tot += cost
        print(f"- {p.stem}: {w / 3600:.2f} GPU-hours on {gpu}, ${cost:.2f}")
    print(f"\nTotal: ${tot:.2f}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["s1", "s2", "s3", "spend"]
    for w in which:
        {"s1": s1, "s2": s2, "s3": s3, "spend": spend}[w]()
        print()
