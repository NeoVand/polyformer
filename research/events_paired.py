"""Paired comparisons of finished runs on the same held-out windows (EVENTS.md section 0).

For two arms of a manifest, take each seed's per-window `val_big` losses (the same windows for every run),
and report: the mean of each arm, the relative difference per seed, and a paired t statistic across
windows of the seed-averaged difference.

    python research/events_paired.py events_confirm "rope+forget+gate+vres" "hybrid[GAGAGA] ..."
    python research/events_paired.py events_confirm            # every pair against the first arm found
"""

import json
import math
import pathlib
import sys

import numpy as np

import loops_summary

ROOT = pathlib.Path(__file__).resolve().parent


def runs(manifest):
    out = {}
    for path in sorted((ROOT / "results" / "loops_runs").glob("*.json")):
        r = json.loads(path.read_text())
        if r.get("manifest") != manifest or not r.get("val_big_sequence_losses"):
            continue
        arm = loops_summary.arm(r["argv"])
        seed = loops_summary.flag(r["argv"], "--seed")
        out.setdefault(arm, {})[seed] = {"seq": np.asarray(r["val_big_sequence_losses"]), "big": r["val_big_raw"],
                                         "wall": r.get("wall"), "steps": loops_summary.flag(r["argv"], "--steps"),
                                         "nonembed": r.get("nonembed"), "tfpt": r.get("train_flops_per_token")}
    return out


def compare(a, b):
    seeds = sorted(set(a) & set(b))
    if not seeds:
        return None
    per_seed = {s: 100 * (b[s]["big"] / a[s]["big"] - 1) for s in seeds}
    diff = np.mean([b[s]["seq"] - a[s]["seq"] for s in seeds], 0)
    t = diff.mean() / (diff.std(ddof=1) / math.sqrt(len(diff)))
    return {"seeds": seeds, "per_seed_pct": per_seed, "mean_pct": float(np.mean(list(per_seed.values()))),
            "paired_t": float(t), "windows": len(diff)}


def main():
    manifest = sys.argv[1]
    rs = runs(manifest)
    for arm, seeds in rs.items():
        big = np.mean([v["big"] for v in seeds.values()])
        wall = np.mean([v["wall"] for v in seeds.values() if v["wall"]])
        any_ = next(iter(seeds.values()))
        print(f"{arm:60s} seeds {','.join(sorted(seeds))}  val_big {big:.4f}  wall {wall:.0f}s  "
              f"updates {any_['steps']}  nonembed {any_['nonembed']}")
    arms = sys.argv[2:] or list(rs)
    base = arms[0]
    for other in arms[1:]:
        c = compare(rs[base], rs[other])
        if c:
            seeds = " ".join(f"s{s} {v:+.2f}%" for s, v in c["per_seed_pct"].items())
            print(f"{other[:50]:50s} vs {base[:30]:30s} {c['mean_pct']:+.2f}%  ({seeds})  paired t {c['paired_t']:+.1f}"
                  f" over {c['windows']} windows")


if __name__ == "__main__":
    main()
