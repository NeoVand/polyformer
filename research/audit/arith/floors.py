"""Audit: shallow floors on the exact test sets of exec_arith.py (regenerated with the same seeds), CPU only.
count: answer = final count mod 10.  add: answer = every sum digit and the final carry.
Rules:
  const_train : the most frequent final answer on training-length programs (4-32 items, seed 0 stream), predicted always
  const_oracle: the most frequent final answer on the test set itself (upper bound on any constant rule)
  last_item   : a table last event -> most frequent final answer, fitted on training-length programs (count only)
  window_k    : the answer computed exactly from the last k items only, state reset to 0 before the window
"""
import os
import json
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.environ.get("AUDIT_CODE", "/Users/neo/repos/polyformer/.claude/worktrees/exec-d-0e1910/research"))  # exec_arith.py at dcd126c
import exec_arith as ea  # noqa: E402

LENGTHS, NEVAL = [32, 256, 1024, 4096], [512, 512, 512, 128]
KS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 32]
out = {}


def train_programs(task, steps=3000, B=64, seed=0):
    rng = np.random.default_rng(seed)
    evs, lens = [], []
    for _ in range(steps):
        lengths = rng.integers(ea.N_MIN, ea.N_MAX + 1, B)
        ev, lengths = ea.sample(task, rng, B, ea.N_MAX, lengths)
        evs.append(ev); lens.append(lengths)
    return np.concatenate(evs), np.concatenate(lens)


for task in ("count", "add"):
    ti = list(ea.TASKS).index(task)
    tev, tlen = train_programs(task)
    ttr = ea.run_events(task, tev)
    tfin = ttr[np.arange(len(tev)), tlen - 1]
    res = {}
    if task == "count":
        c_train = Counter(tfin[:, 0].tolist()).most_common(1)[0][0]
        last = tev[np.arange(len(tev)), tlen - 1]
        tab = {w: Counter(tfin[last == w, 0].tolist()).most_common(1)[0][0] for w in range(10)}
    for e, n in zip(LENGTHS, NEVAL):
        seed = ea.EVAL_SEED + e + 31 * ti
        ev, ln = ea.sample(task, np.random.default_rng(seed), n, e)
        tr = ea.run_events(task, ev)
        r = {"n": n, "seed": seed}
        if task == "count":
            fin = tr[:, -1, 0]
            dist = np.bincount(fin, minlength=10) / n
            r["final_answer_distribution"] = [round(float(x), 4) for x in dist]
            r["const_oracle"] = float(dist.max())
            r["const_train"] = {"value": int(c_train), "acc": float((fin == c_train).mean())}
            r["last_item"] = float((np.array([tab[int(w)] for w in ev[:, -1]]) == fin).mean())
            for k in KS:
                if k <= e:
                    pred = (ev[:, -k:] == 0).sum(1) % 10
                    r[f"window_{k}"] = float((pred == fin).mean())
        else:
            a, b = ev // 10, ev % 10
            sums = a + b
            true_s, true_c = tr[..., 0], tr[..., 1]
            # constant rule over the whole answer is hopeless; report digit-wise no-carry rule (window 1) and windows
            for k in KS:
                # carry into position t computed from items max(0, t-k+1)..t-1 starting from carry 0
                c_in = np.zeros_like(sums)
                for t in range(e):
                    lo = max(0, t - k + 1)
                    c = np.zeros(n, np.int64)
                    for u in range(lo, t):
                        c = (sums[:, u] + c) // 10
                    c_in[:, t] = c
                s_pred = (sums + c_in) % 10
                c_fin = (sums[:, -1] + c_in[:, -1]) // 10
                ok = (s_pred == true_s).all(1) & (c_fin == true_c[:, -1])
                r[f"window_{k}"] = float(ok.mean())
            # analytic expectation for window k at length e: P(no failure) ~ (1 - P(carry in) * 0.1^(k-1))^(e-k)
        res[str(e)] = r
        print(task, e, json.dumps(r), flush=True)
    out[task] = res

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "floors.json"), "w"), indent=1)
