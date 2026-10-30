"""Audit: regenerate training / validation / test programs of exec_arith.py (CPU, numpy only) and hash them.
Training stream reproduced exactly as in run(): per step, lengths = rng.integers(N_MIN, N_MAX + 1, B); sample(task, rng, B, N_MAX, lengths).
"""
import os
import hashlib
import json
import sys

import numpy as np

sys.path.insert(0, os.environ.get("AUDIT_CODE", "/Users/neo/repos/polyformer/.claude/worktrees/exec-d-0e1910/research"))  # exec_arith.py at dcd126c
import exec_arith as ea  # noqa: E402

STEPS, B = 3000, 64
LENGTHS, NEVAL = [32, 256, 1024, 4096], [512, 512, 512, 128]


def h(x):
    return hashlib.sha1(np.asarray(x, np.int64).tobytes()).hexdigest()


out = {}
for task in ("add", "count"):
    ti = list(ea.TASKS).index(task)
    # validation
    vev, vlen = ea.sample(task, np.random.default_rng(ea.VAL_SEED), ea.N_VAL, ea.N_MAX)
    val = [h(vev[i, :vlen[i]]) for i in range(len(vev))]
    # test sets
    tests = {}
    for e, n in zip(LENGTHS, NEVAL):
        seed = ea.EVAL_SEED + e + 31 * ti
        ev, ln = ea.sample(task, np.random.default_rng(seed), n, e)
        tests[e] = {"seed": seed, "full": [h(ev[i, :ln[i]]) for i in range(n)], "pre32": [h(ev[i, :32]) for i in range(n)],
                    "lengths_all_e": bool((ln == e).all()), "dup_within": n - len(set(h(ev[i, :ln[i]]) for i in range(n)))}
    res = {"val_seed": ea.VAL_SEED, "val_lengths": sorted(set(vlen.tolist())), "val_dup_within": len(val) - len(set(val)),
           "val_vs_test32": len(set(val) & set(tests[32]["full"])),
           "test_seeds": {e: tests[e]["seed"] for e in LENGTHS}, "test_dup_within": {e: tests[e]["dup_within"] for e in LENGTHS},
           "test_lengths_exact": {e: tests[e]["lengths_all_e"] for e in LENGTHS}, "seeds": {}}
    for s in range(6):
        rng = np.random.default_rng(s)
        train = set()
        train32 = set()
        nlen = np.zeros(ea.N_MAX + 1, np.int64)
        for _ in range(STEPS):
            lengths = rng.integers(ea.N_MIN, ea.N_MAX + 1, B)
            ev, lengths = ea.sample(task, rng, B, ea.N_MAX, lengths)
            for i in range(B):
                L = int(lengths[i])
                nlen[L] += 1
                k = h(ev[i, :L])
                train.add(k)
                if L == 32:
                    train32.add(k)
        r = {"n_train_programs": int(nlen.sum()), "n_unique": len(train), "n_len32": int(nlen[32]), "min_len": int(np.nonzero(nlen)[0].min()),
             "max_len": int(np.nonzero(nlen)[0].max()),
             "train_vs_val": len(train & set(val)), "train_vs_test_full": {e: len(train & set(tests[e]["full"])) for e in LENGTHS},
             "train32_vs_test_prefix32": {e: len(train32 & set(tests[e]["pre32"])) for e in LENGTHS}}
        res["seeds"][s] = r
        print(task, s, json.dumps(r), flush=True)
    out[task] = res
    print(task, json.dumps({k: v for k, v in res.items() if k != "seeds"}), flush=True)

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "disjoint.json"), "w"), indent=1)
