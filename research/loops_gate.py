"""The registered stage-3 gate of LOOPS.md, per seed, on final val_big (1,024 windows, seed 5678).

    python research/loops_gate.py [candidate-arm]
"""

import sys

import loops_summary as S

CANDIDATE = sys.argv[1] if len(sys.argv) > 1 else "hybrid[GAGAGA] holo+forget"


def main():
    rows = [r for r in S.rows() if r["manifest"] and r["manifest"].startswith("loops_lang") and r["val_big"]]
    by = {}
    for r in rows:
        by.setdefault(r["seed"], {})[r["arm"]] = r["val_big"]
    print(f"candidate: {CANDIDATE}")
    passes = []
    for seed in sorted(by):
        b = by[seed]
        c = b.get(CANDIDATE)
        line = [f"seed {seed}"] + [f"{k}={v:.5f}" for k, v in sorted(b.items(), key=lambda kv: kv[1])]
        print("  " + "  ".join(line))
        if c is None:
            continue
        soft = [b[k] for k in ("abs", "rope") if k in b]
        if soft:
            best = min(soft)
            gain = 100 * (1 - c / best)
            ok = c <= 0.99 * best
            passes.append(ok)
            print(f"    vs best softmax control ({best:.5f}): {gain:+.3f}%  {'PASS' if ok else 'fail'} (needs >= 1%)")
        for ref in ("rope+forget", "gdn", "deltaproduct", "hybrid[GAGAGA] rope", "hybrid[DADADA] holo+forget"):
            if ref in b and ref != CANDIDATE:
                print(f"    vs {ref:28s} ({b[ref]:.5f}): {100 * (1 - c / b[ref]):+.3f}%  "
                      f"{'below' if c < b[ref] else 'NOT below'}")
    if passes:
        print(f"headline: {sum(passes)}/{len(passes)} seeds pass the 1% softmax gate")


if __name__ == "__main__":
    main()
