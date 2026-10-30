"""Audit (CPU only): what the EXEC_LM shallow floor is worth against chance, at every test length."""
import collections
import importlib.util
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location("ed", HERE / "new" / "exec_data.py")
ed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ed)
ed.set_kinds(["set", "op"])
P, NVR = 2, (4, 4)


def floor_table():
    rng = np.random.default_rng(999)
    progs, lengths = ed.sample_programs(rng, 20000, ed.N_MAX, P, lengths=rng.integers(ed.N_MIN, ed.N_MAX + 1, 20000), nv_range=NVR)
    return ed.fit_floor(progs, lengths, P)


def determined(form):
    """True when the last write's value does not depend on any variable: set to a constant, op of two constants,
    or x * 0 / 0 * x."""
    if form is None:
        return True
    if form[0] == "set":
        return form[1] != "v"
    _, op, a, b = form
    if a != "v" and b != "v":
        return True
    return op == 2 and (a == 0 or b == 0)


table = floor_table()
out = {"floor_table_size": len(table), "floor_table": {str(k): v for k, v in table.items()}}
for e in (16, 64, 256, 1024):
    rng = np.random.default_rng(777 + e)
    tok, trace, mask, progs, lengths = ed.task_exec(rng, 512, e, P, nv_range=NVR)
    final = trace[:, -1]                                                   # [512, 8]
    keys = [tuple(r) for r in final]
    cnt = collections.Counter(keys)
    mode, mode_n = cnt.most_common(1)[0]
    forms = ed.last_write_forms(progs, lengths)
    det_prog = np.array([all(determined(f) for f in fs) for fs in forms])
    det_var = np.array([[determined(f) for f in fs] for fs in forms])
    fl_full, fl_var = ed.floor_accuracy(table, progs, lengths, P)
    # active variables' marginal P(1) at the end
    active = np.array([[f is not None for f in fs] for fs in forms])
    p1 = final[active].mean()
    # per-variable best constant guess (0 for inactive, majority for active): accuracy of the all-zeros guess
    allzero = float((final == 0).all(-1).mean())
    # refit floor on fresh programs of THIS length (an in-distribution upper reference for a last-write reader)
    rr = np.random.default_rng(31337 + e)
    nfit = 4000 if e <= 256 else 1500
    fprogs, flens = ed.sample_programs(rr, nfit, e, P, nv_range=NVR)
    tab_e = ed.fit_floor(fprogs, flens, P)
    refit_full, refit_var = ed.floor_accuracy(tab_e, progs, lengths, P)
    out[e] = {"n": 512, "distinct_final_states": len(cnt), "mode_state": "".join(map(str, mode)), "mode_acc (best constant guess)": mode_n / 512,
              "all_zero_acc": allzero, "uniform_over_4_active_bits": 1 / 16, "uniform_over_8_bits": 1 / 256,
              "active_bit_P(1)": float(p1), "floor_full": fl_full, "floor_var": fl_var,
              "frac_programs_all_lastwrites_value_determined": float(det_prog.mean()),
              "frac_active_vars_lastwrite_value_determined": float(det_var[active].mean()),
              "floor_refit_at_this_length_full": refit_full, "floor_refit_at_this_length_var": refit_var}
    # accuracy of the floor restricted to programs whose last writes all determine their values
    pred_hit = []
    for b, fs in enumerate(forms):
        pred = [0 if f is None else table.get(f, 0) for f in fs]
        pred_hit.append(all(pred[x] == final[b, x] for x in range(ed.NV)))
    pred_hit = np.array(pred_hit)
    out[e]["floor_acc_on_determined_programs"] = float(pred_hit[det_prog].mean()) if det_prog.any() else None
    out[e]["floor_acc_on_other_programs"] = float(pred_hit[~det_prog].mean()) if (~det_prog).any() else None
print(json.dumps(out, indent=1))
(HERE / "floor_report.json").write_text(json.dumps(out, indent=1))
