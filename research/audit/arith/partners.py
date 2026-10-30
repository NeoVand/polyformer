"""Audit: regenerate the training-time certified partners (signal arms) and check overlap with validation / test-32."""
import os
import hashlib
import json
import sys

import numpy as np

sys.path.insert(0, os.environ.get("AUDIT_CODE", "/Users/neo/repos/polyformer/.claude/worktrees/exec-d-0e1910/research"))  # exec_arith.py at dcd126c
import exec_arith as ea  # noqa: E402

STEPS, B = 3000, 64
h = lambda x: hashlib.sha1(np.asarray(x, np.int64).tobytes()).hexdigest()
task, seed = sys.argv[1], int(sys.argv[2])
ti = list(ea.TASKS).index(task)
vev, vlen = ea.sample(task, np.random.default_rng(ea.VAL_SEED), ea.N_VAL, ea.N_MAX)
val = {h(vev[i, :vlen[i]]) for i in range(len(vev))}
tev, tl = ea.sample(task, np.random.default_rng(ea.EVAL_SEED + 32 + 31 * ti), 512, 32)
t32 = {h(tev[i, :32]) for i in range(512)}
rng, prng = np.random.default_rng(seed), np.random.default_rng(seed + ea.PARTNER_OFFSET)
parts, plen = set(), np.zeros(40, np.int64)
for _ in range(STEPS):
    lengths = rng.integers(ea.N_MIN, ea.N_MAX + 1, B)
    ev, lengths = ea.sample(task, rng, B, ea.N_MAX, lengths)
    pv, pl = ea.partner_batch(task, prng, ev, lengths)
    for i in range(B):
        parts.add(h(pv[i, :pl[i]]))
        plen[pl[i]] += 1
print(json.dumps({"task": task, "seed": seed, "n_partners": int(plen.sum()), "len_range": [int(np.nonzero(plen)[0].min()), int(np.nonzero(plen)[0].max())],
                  "partners_vs_val": len(parts & val), "partners_vs_test32": len(parts & t32)}))
