"""Audit check registered in research/audit/RERUNS.md ("Balanced long-carry check"): do section 19's addition arms
hold the carry or assume it? Evaluation only, local CPU, on the selected parameters section 19 saved.

For each checkpoint (ctl_add_<arm>_s<seed>.npz from the volume polyformer-exec-lm-results):
  1. fidelity: rebuild the parameters, re-evaluate the long-carry set at 1,024 exactly as exec_arith.run does, and
     require the record's answer_exact (results/exec_lm/ARITH_add_<arm>_s<seed>_ctl.json, read-only);
  2. balanced set: sample_long_carry's construction (seed 7777 + length, n = 512), with the chain-starting item of
     every odd program replaced by a pair summing to at most 8, so that chain carries 0. Scored at 1,024 and 4,096 as
     answer_exact (every sum digit and the final carry), overall and per half.
Window-8 floors on the balanced set (carry reset to 0, and to 1) come from long_carry_floor.window.

  AUDIT_CODE=<export of exec-d 0cbbfb3>/research python balanced_long_carry.py <ckpt dir> <records dir>
"""
import json
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, os.environ["AUDIT_CODE"])
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exec_arith as ea  # noqa: E402
from long_carry_floor import window  # noqa: E402

BAL_SEED, N = 7777, 512
KILL = np.array([a * 10 + b for a in range(10) for b in range(10) if a + b <= 8])


def balanced(e):
    rng = np.random.default_rng(BAL_SEED + e)
    ev, lengths, r = ea.sample_long_carry(rng, N, e)
    for i in range(1, N, 2):
        ev[i, e - 1 - r[i]] = rng.choice(KILL)
    return ev, lengths, r


def load(path, arm, seed, F, nv, p):
    import jax
    cfg = ea.ARMS[arm]
    tmpl = ea.init(jax.random.PRNGKey(seed), 128, F, nv * p, nl_hidden=256 if cfg["nextlat"] > 0 else 0)
    z = np.load(path)
    leaves, tdef = jax.tree_util.tree_flatten_with_path(tmpl)
    vals = []
    for k, v in leaves:
        a = z[jax.tree_util.keystr(k)]
        assert a.shape == np.shape(v), (k, a.shape, np.shape(v))
        vals.append(a)
    assert len(vals) == len(z.files), (len(vals), len(z.files))
    return jax.tree_util.tree_unflatten(jax.tree_util.tree_structure(tmpl), vals)


def main():
    import jax
    import jax.numpy as jnp
    ckpt, recs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    nv, p = ea.TASKS["add"]["nv"], ea.TASKS["add"]["p"]
    table, tmask = ea.load_feats("add")
    T, M = jnp.asarray(table), jnp.asarray(tmask)
    sets = {e: balanced(e) for e in (1024, 4096)}
    traces = {e: ea.run_events("add", sets[e][0]) for e in sets}
    out = {"floors": {}}
    for e, (ev, lengths, r) in sets.items():
        fc = traces[e][:, -1, 1]
        f = {"final_carry_1": float((fc == 1).mean())}
        for c0 in (0, 1):
            s, cf = window(ev, 8, c0)
            f[f"reset{c0}_window_8"] = float(((s == traces[e][..., 0]).all(1) & (cf == fc)).mean())
        out["floors"][str(e)] = f
        print("floor", e, f, flush=True)
    lc_ev, lc_len, _ = ea.sample_long_carry(np.random.default_rng(ea.LC_SEED + 1024), N, 1024)
    lc_tr = ea.run_events("add", lc_ev)
    for path in sorted(ckpt.glob("ctl_add_*_s*.npz")):
        arm, seed = path.stem.split("_")[2], int(path.stem.split("_s")[-1])
        prm = load(path, arm, seed, table.shape[-1], nv, p)
        rms = ea.ARMS[arm]["rms"]
        jf = jax.jit(lambda q, ids: ea.forward(q, T, M, ids, nv, p, rms=rms)[0])

        def pred(ev, bs=128):
            return np.concatenate([np.asarray(jf(prm, jnp.asarray(ev[i:i + bs]))).argmax(-1) for i in range(0, len(ev), bs)])

        rec = json.load(open(recs / f"ARITH_add_{arm}_s{seed}_ctl.json"))["results"]["long_carry_1024"]["answer_exact"]
        fid = float(ea.answer_exact("add", pred(lc_ev) == lc_tr, lc_len).mean())
        row = {"arm": arm, "seed": seed, "fidelity_record": rec, "fidelity_rerun": fid, "fidelity_ok": fid == rec}
        for e, (ev, lengths, r) in sets.items():
            ans = ea.answer_exact("add", pred(ev) == traces[e], lengths)
            c1 = traces[e][:, -1, 1] == 1
            row[str(e)] = {"answer_exact": float(ans.mean()), "carry1_half": float(ans[c1].mean()),
                           "carry0_half": float(ans[~c1].mean()), "n": N}
        out[path.stem] = row
        print(json.dumps(row), flush=True)
    path = pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "balanced_long_carry.json"
    path.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
