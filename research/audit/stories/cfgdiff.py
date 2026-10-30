import json, pathlib
W = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees/lean-n-data-34a2d2")
d = json.load(open(W/"research/results/stories/ABLATION_stories.json"))
recs = {(r["arm"], r["seed"]): r for r in d["records"]}
DEF = {"rms": 1, "nextlat": 0.0, "tag": "", "partners": ""}   # defaults of fields absent in pre-4d5b335 code (rms=True was hard-coded)
for seed in (10, 11, 12):
    base = json.load(open(W/recs[("O", seed)]["source_record"]))["config"]
    for arm in ("O+N", "NS+N", "EQ+N", "FULL+N", "FULL"):
        r = recs[(arm, seed)]
        src = json.load(open(W/r["source_record"]))
        c = src["config"]
        keys = sorted(set(base) | set(c) | set(DEF))
        diff = {k: (base.get(k, DEF.get(k, "<absent>")), c.get(k, DEF.get(k, "<absent>"))) for k in keys if base.get(k, DEF.get(k)) != c.get(k, DEF.get(k))}
        absent = [k for k in ("rms", "nextlat", "tag", "partners") if k not in c]
        print(f"s{seed} {arm:6s} vs O: {diff}  (fields absent in record, defaulted: {absent})")
# runs: any time-budget hits, per-step exact at 1024, log tails
for r in d["records"]:
    p = W/pathlib.Path(r["source_record"]).parent/"log.txt"
    t = p.read_text()
    src = json.load(open(W/r["source_record"]))
    pe = src["test"]["1024"]["exact_per_step_mean"]
    print(r["arm"], r["seed"], "budget-hit" if "time budget reached" in t else "no-budget-hit", "per-step@1024", round(pe, 3), "soft_partners" in src and src.get("soft_partners"))
