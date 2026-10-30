import sys, json, pathlib
sys.path.insert(0, sys.argv[1])
import story_world as W, stories_soft as SS
R = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees/lean-n-data-34a2d2/research/results/stories")
props = SS.proposals(24000, seed=1)
k = lambda s: json.dumps(s, sort_keys=True)
idx = {(k(p["a"]), k(p["b"])): i for i, p in enumerate(props)}
for nm, fn in (("soft", "run_soft/soft_partners.json"), ("cons", "run_cons/consensus_partners.json"), ("sclean", "run_cons/soft_clean_partners.json")):
    P = json.load(open(R / fn))["pairs"]
    hit = [idx.get((k(q["a"]), k(q["b"]))) for q in P]
    lab_ok = all(h is not None and props[h]["label"] == q["label_for_measurement_only"] for h, q in zip(hit, P))
    sim_ok = all(s["states"] == [list(x) for x in W.run(s["s0"], [tuple(e) for e in s["events"]])] for q in P for s in (q["a"], q["b"]))
    print(f"{nm}: {len(P)} pairs; all found among proposals(24000, seed=1): {all(h is not None for h in hit)}; labels match: {lab_ok}; stored states == simulator run: {sim_ok}; "
          f"mean events a {sum(len(q['a']['events']) for q in P)/len(P):.2f}")
