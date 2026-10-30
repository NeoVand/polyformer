"""Audit (CPU only, no training): regenerate EXEC_LM bit-domain train/val/test/floor programs with the exact
exec_data.py versions the Modal manifests hashed, fingerprint them against the records' floor values, and count
overlaps. Usage: python regen.py <records_dir>"""
import hashlib
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).parent
REC = pathlib.Path(sys.argv[1])
EVAL_SEED, VAL_SEED, FLOOR_SEED = 777, 555, 999
E_EVAL = (16, 64, 256, 1024)
N_EVAL = N_VAL = 512
NV_RANGE = (4, 4)
P = 2
STEPS, BATCH = 16000, 64


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.set_kinds(["set", "op"])
    return m


def h(prog):
    return hashlib.blake2b(np.ascontiguousarray(prog, dtype=np.int64).tobytes(), digest_size=16).digest()


def test_sets(ed):
    out = {}
    for e in E_EVAL:
        rng = np.random.default_rng(EVAL_SEED + e)
        tok, trace, mask, progs, lengths = ed.task_exec(rng, N_EVAL, e, P, nv_range=NV_RANGE)
        out[e] = (progs, trace, lengths)
    return out


def val_set(ed):
    rng = np.random.default_rng(VAL_SEED)
    tok, trace, mask, progs, lengths = ed.task_exec(rng, N_VAL, ed.N_MAX, P, nv_range=NV_RANGE)
    return progs, trace, lengths


def floor_table(ed):
    rng = np.random.default_rng(FLOOR_SEED)
    progs, lengths = ed.sample_programs(rng, 20000, ed.N_MAX, P, lengths=rng.integers(ed.N_MIN, ed.N_MAX + 1, 20000), nv_range=NV_RANGE)
    return ed.fit_floor(progs, lengths, P), progs, lengths


def train_stream(ed, seed):
    """Replicates exec_lm_run.build().batches(): the program stream from default_rng(seed) (partners use a separate
    generator, so the stream is the same for every arm)."""
    rng = np.random.default_rng(seed)
    hashes, by_len = set(), {}
    for _ in range(STEPS):
        lengths = rng.integers(ed.N_MIN, ed.N_MAX + 1, BATCH)
        progs, lengths = ed.sample_programs(rng, BATCH, ed.N_MAX, P, lengths, nv_range=NV_RANGE)
        for b in range(BATCH):
            L = int(lengths[b])
            x = h(progs[b, :L])
            hashes.add(x)
            by_len[L] = by_len.get(L, 0) + 1
    return hashes, by_len


def main():
    t0 = time.time()
    old = load(HERE / "old" / "exec_data.py", "ed_old")
    new = load(HERE / "new" / "exec_data.py", "ed_new")
    report = {}

    # 1. test / val / floor sets identical between the two code versions?
    T_old, T_new = test_sets(old), test_sets(new)
    report["test_sets_identical_old_vs_new"] = {e: bool(np.array_equal(T_old[e][0], T_new[e][0]) and np.array_equal(T_old[e][1], T_new[e][1])) for e in E_EVAL}
    V_old, V_new = val_set(old), val_set(new)
    report["val_identical_old_vs_new"] = bool(np.array_equal(V_old[0], V_new[0]))
    tab_old, fp_old, fl_old = floor_table(old)
    tab_new, fp_new, fl_new = floor_table(new)
    report["floor_programs_identical_old_vs_new"] = bool(np.array_equal(fp_old, fp_new))
    report["floor_table_identical_old_vs_new"] = tab_old == tab_new

    # 2. fingerprint: recompute floor_acc_last / floor_var_last on the regenerated test sets, compare with records
    ed = new
    T, (vprogs, vtrace, vlens), table = T_new, V_new, tab_new
    fp = {}
    for e in E_EVAL:
        progs, trace, lengths = T[e]
        assert (lengths == e).all()
        fp[e] = ed.floor_accuracy(table, progs, lengths, P)
    report["floor_recomputed"] = {e: fp[e] for e in E_EVAL}
    rec_files = ["R_s0.json", "R_s1.json", "R_s2.json", "Rr_s0_fact.json", "Rr_s1_fact.json", "Rr_s2_fact.json", "RNLr_s0_fact.json",
                 "RNLr_s1_fact.json", "RNLr_s2_fact.json", "RIr_s0_fact.json", "RIr_s1_fact.json", "RIr_s2_fact.json",
                 "RNLIr_s0_modal.json", "RNLIr_s1_modal.json", "RNLIr_s2_modal.json", "RNLI_s0.json", "RNLI_s1.json", "RNLI_s2.json"]
    match = {}
    for f in rec_files:
        R = json.loads((REC / f).read_text())["results"]
        match[f] = all(R[str(e)]["floor_acc_last"] == fp[e][0] and R[str(e)]["floor_var_last"] == fp[e][1] and R[str(e)]["n"] == len(T[e][0]) for e in E_EVAL)
    report["records_floor_and_n_match_regenerated_test_sets"] = match

    # 3. overlaps
    test_h = {e: [h(T[e][0][b, :e]) for b in range(N_EVAL)] for e in E_EVAL}
    val_h = [h(vprogs[b, :16]) for b in range(N_VAL)]
    floor_h = {h(fp_new[b, :int(fl_new[b])]) for b in range(len(fp_new))}
    report["within_set_duplicates"] = {**{f"test_{e}": N_EVAL - len(set(test_h[e])) for e in E_EVAL}, "val": N_VAL - len(set(val_h))}
    report["val_vs_test16_overlap"] = len(set(val_h) & set(test_h[16]))
    report["floorfit_vs_test16_overlap"] = len(floor_h & set(test_h[16]))
    report["floorfit_vs_val_overlap"] = len(floor_h & set(val_h))
    # prefixes of length 4..16 of every test / val program
    prefix_h = {e: {k: {h(T[e][0][b, :k]) for b in range(N_EVAL)} for k in range(4, 17)} for e in E_EVAL}
    val_prefix_h = {k: {h(vprogs[b, :k]) for b in range(N_VAL)} for k in range(4, 17)}
    for seed in (0, 1, 2):
        th, by_len = train_stream(ed, seed)
        # sanity: old code gives the same stream (first 200 steps)
        r_old, r_new = np.random.default_rng(seed), np.random.default_rng(seed)
        same = True
        for _ in range(200):
            lo = r_old.integers(4, 17, BATCH); ln = r_new.integers(4, 17, BATCH)
            po, _ = old.sample_programs(r_old, BATCH, 16, P, lo, nv_range=NV_RANGE)
            pn, _ = new.sample_programs(r_new, BATCH, 16, P, ln, nv_range=NV_RANGE)
            same &= bool(np.array_equal(po, pn))
        rep = {"n_train_programs": STEPS * BATCH, "distinct_train_programs": len(th), "train_len16_programs": by_len.get(16, 0),
               "train_stream_identical_old_vs_new_first200steps": same,
               "test_exact_overlap": {e: sum(x in th for x in test_h[e]) for e in E_EVAL},
               "val_exact_overlap": sum(x in th for x in val_h),
               "test_prefix_overlap_programs_any_k4to16": {e: int(sum(any(h(T[e][0][b, :k]) in th for k in range(4, 17)) for b in range(N_EVAL))) for e in E_EVAL},
               "test_prefix_overlap_by_k": {e: {k: sum(x in th for x in prefix_h[e][k]) for k in range(4, 17)} for e in E_EVAL},
               "val_prefix_overlap_by_k": {k: sum(x in th for x in val_prefix_h[k]) for k in range(4, 17)}}
        report[f"train_seed{seed}"] = rep
        print(f"seed {seed} done at {time.time() - t0:.0f}s", flush=True)
    print(json.dumps(report, indent=1, default=str))
    (HERE / "regen_report.json").write_text(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    main()
