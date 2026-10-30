"""Audit of EXEC_LM section 19 (A): shallow floors on the long-carry addition sets, computed independently.

Regenerates the long-carry sets exactly as exec_arith.py does (sample_long_carry, seed LC_SEED + length, n = 512) and
scores two window rules that see only the last k items:
  reset 0: the carry into the window is taken as 0 (the audit's original floor, as stored in the records);
  reset 1: the carry into the window is taken as 1 unless the window starts at the first item (carry known 0).
Every long-carry chain is started by a pair summing to at least 10, so it always carries a 1. The second rule asks
whether the set can be passed by assuming a carry, without holding one.

  AUDIT_CODE=<checkout of exec-d 0cbbfb3>/research python research/audit/arith/long_carry_floor.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.environ.get("AUDIT_CODE", "/Users/neo/repos/polyformer/.claude/worktrees/exec-d-0e1910/research"))
import exec_arith as ea  # noqa: E402

KS = [1, 2, 4, 8, 16, 32, 64]


def window(ev, k, c0):
    """Every sum digit and the final carry from the last k items, carry into the window c0 (0 at the program start)."""
    sums = ev // 10 + ev % 10
    B, e = sums.shape
    c_in = np.zeros_like(sums)
    for t in range(e):
        lo = max(0, t - k + 1)
        c = np.full(B, c0 if lo > 0 else 0)
        for u in range(lo, t):
            c = (sums[:, u] + c) // 10
        c_in[:, t] = c
    return (sums + c_in) % 10, (sums[:, -1] + c_in[:, -1]) // 10


def main():
    out = {}
    for e in (1024, 4096):
        ev, lengths, r = ea.sample_long_carry(np.random.default_rng(ea.LC_SEED + e), 512, e)
        tr = ea.run_events("add", ev)
        res = {"n": 512, "seed": ea.LC_SEED + e, "chain_min": int(r.min()), "chain_max": int(r.max()),
               "final_carry_1": float((tr[:, -1, 1] == 1).mean())}
        for c0 in (0, 1):
            for k in KS:
                s, cf = window(ev, k, c0)
                res[f"reset{c0}_window_{k}"] = float(((s == tr[..., 0]).all(1) & (cf == tr[:, -1, 1])).mean())
        res["stored_rule_matches_reset0"] = {str(k): ea.window_floor("add", ev, tr, k) == res[f"reset0_window_{k}"]
                                             for k in ea.FLOOR_KS if k <= e}
        out[str(e)] = res
        print(e, json.dumps(res), flush=True)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "long_carry_floor.json")
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
