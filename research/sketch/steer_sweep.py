"""E7 depth sweep of the class-mean push (paper review, 31 Oct 2026): inside_steer.py, unchanged, at depths 1..23.

inside_steer.py draws its 80 views per table, then one target per view at each depth, from one seed-0 generator in
order. A run over several depths therefore gives each depth new targets, and the MUL views depend on how many SUM depths
ran before them. The primary sweep runs inside_steer.py once per depth (LAYERS = that depth), so every depth sees the
same 80 views and the same targets as the published layer-20 run (steer_digit.json: SUM 79/80, MUL 80/80); depth 20 runs
first as the reproduction, and the sweep stops if either table is off by more than one view. A second, single run over
all depths (the way steer.json was made) is a second draw of targets.

  python steer_sweep.py <adapter> <states.npy> <out.json> [first=1] [last=23]   # also writes <out>_detail.json
"""

import hashlib
import json
import re
import subprocess
import sys
import time

import numpy as np

A, S, OUT = sys.argv[1:4]
FIRST = int(sys.argv[4]) if len(sys.argv) > 4 else 1
LAST = int(sys.argv[5]) if len(sys.argv) > 5 else 23
REF = {"SUM": (79, 80), "MUL": (80, 80)}
t0 = time.time()


def run(layers):
    p = subprocess.run([sys.executable, "inside_steer.py", A, S, "digit", ",".join(map(str, layers))],
                       capture_output=True, text=True)
    if p.returncode:
        print(p.stdout[-2000:], p.stderr[-4000:], flush=True)
        raise SystemExit(p.returncode)
    got = {f"{f}@{l}": [int(ok), int(tot)] for f, l, ok, tot in
           re.findall(r"^(SUM|MUL) layer (\d+) steered to target: (\d+) / (\d+)$", p.stdout, re.M)}
    assert len(got) == 2 * len(layers), p.stdout[-2000:]
    return got


meta = json.load(open("atlas.json"))["rows"]
states = np.load(S, mmap_mode="r")
assert states.shape[0] == len(meta), (states.shape, len(meta))
detail = {"adapter": A, "states": S, "states_shape": list(states.shape),
          "states_sha256": hashlib.sha256(open(S, "rb").read()).hexdigest(), "atlas_rows": len(meta), "by": "digit"}
print(json.dumps(detail), flush=True)

counts = run([20])
detail["reproduction_at_20"] = {**counts, "published": {f"{k}@20": list(v) for k, v in REF.items()}}
print("depth 20:", counts, f"({time.time() - t0:.0f}s)", flush=True)
for fam, (ok, tot) in REF.items():
    if counts[f"{fam}@20"][1] != tot or abs(counts[f"{fam}@20"][0] - ok) > 1:
        json.dump(detail, open(OUT.replace(".json", "_detail.json"), "w"), indent=1)
        raise SystemExit(f"no reproduction at depth 20: {counts}")
for d in range(FIRST, LAST + 1):
    if d != 20:
        counts.update(run([d]))
        print("depth", d, {k: v for k, v in counts.items() if k.endswith(f"@{d}")}, f"({time.time() - t0:.0f}s)", flush=True)
out = {f"{fam}@{d}": counts[f"{fam}@{d}"][0] / counts[f"{fam}@{d}"][1] for fam in ("SUM", "MUL") for d in range(FIRST, LAST + 1)}
detail["per_depth_counts"] = {k: counts[k] for k in out}
json.dump(out, open(OUT, "w"), indent=1)
detail["multi_depth_run"] = run(list(range(FIRST, LAST + 1)))
detail["seconds"] = round(time.time() - t0)
json.dump(detail, open(OUT.replace(".json", "_detail.json"), "w"), indent=1)
print("wrote", OUT, json.dumps(out), flush=True)
