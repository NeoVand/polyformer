"""Score the Modal audit reruns against the registered criteria of research/audit/RERUNS.md.

Reads each rerun's record (downloaded from the volume `polyformer-audit` into RESULTS/<job>/files/...) and the original
record it reruns (located through the domain's ABLATION file in the audited worktree, read-only). Prints one line per
run and writes score.json beside this script.

  python research/audit/modal/score.py <results dir>
"""
import json
import pathlib
import sys

W = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees")
RES = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).parent


def ablation_source(wt, abl, key, arm, seed):
    d = json.load(open(W / wt / abl))
    d = d[key] if key else d
    recs = d if isinstance(d, list) else d["records"]
    r = next(r for r in recs if r["arm"] == arm and r["seed"] == seed and not r.get("selection_bug"))
    p = W / wt / "research" / r["source_record"]
    return json.load(open(p if p.exists() else W / wt / r["source_record"]))


def first_diff(a, b):
    for x, y in zip(a, b):
        if x.get("loss") != y.get("loss"):
            return x.get("step")
    return None


def rerun(job, rel):
    return json.load(open(RES / job / "files" / rel))


JOBS = {
    # job: (worktree, ablation file, key, arm, seed, rerun file, length, field, criterion)
    "code_O_s0": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_code.json", None, "O", 0,
                  "research/results/exec_lm/R_s0_audit.json", "1024", "acc_last", "o_code"),
    "code_FULLN_s0": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_code.json", None, "FULL+N", 0,
                      "research/results/exec_lm/RNLIr_s0_audit.json", "1024", "acc_last", "exact_code"),
    "add_O_s0": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_arith.json", "add", "O", 0,
                 "research/results/exec_lm/ARITH_add_R_s0_audit.json", "4096", "answer_exact", "not_exact"),
    "add_FULLN_s0": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_arith.json", "add", "FULL+N", 0,
                     "research/results/exec_lm/ARITH_add_RNLIr_s0_audit.json", "4096", "answer_exact", "exact"),
    "count_O_s0": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_arith.json", "count", "O", 0,
                   "research/results/exec_lm/ARITH_count_R_s0_audit.json", "4096", "answer_exact", "chance_band"),
    "count_FULLN_s3": ("exec-d-0e1910", "research/results/exec_lm/ABLATION_arith.json", "count",
                       "FULL+N (fresh seeds, uniform rule)", 3,
                       "research/results/exec_lm/ARITH_count_RNLIr_s3_audit.json", "4096", "answer_exact", "exact_after_600"),
    "stories_O_s10": ("lean-n-data-34a2d2", "research/results/stories/ABLATION_stories.json", None, "O", 10,
                      "out/O_s10/track_none_O_s10.json", "1024", "exact_last", "le_0.02"),
    "stories_FULLN_s10": ("lean-n-data-34a2d2", "research/results/stories/ABLATION_stories.json", None, "FULL+N", 10,
                          "out/FULLN_s10/track_cert_FULLN_s10.json", "1024", "exact_last", "exact"),
}


def sel(rec):
    return (rec.get("selection") or {}).get("selected_step")


def curve(rec):
    return rec.get("curve") or rec.get("log") or [{}]


def block(rec):
    return rec.get("results") or rec.get("test")


def main():
    out = {}
    for job, (wt, abl, key, arm, seed, rel, L, field, crit) in JOBS.items():
        o, a = ablation_source(wt, abl, key, arm, seed), rerun(job, rel)
        ov, av = block(o)[L][field], block(a)[L][field]
        n = block(a)[L].get("n") or a.get("n_eval_by_length", {}).get(L) or (a.get("config") or {}).get("n_test")
        row = {"record": ov, "rerun": av, "n": n, "length": L,
               "selected_step": (sel(a), sel(o)),
               "steps_done": (a.get("steps_done"), o.get("steps_done")),
               "step1": (curve(o)[0].get("loss"), curve(a)[0].get("loss")),
               "first_curve_diff_step": first_diff(curve(o), curve(a))}
        if crit == "o_code":
            fp = block(a)[L].get("floor_acc_last"), block(o)[L].get("floor_acc_last")
            row["floor_fingerprint"] = fp
            ok = av < 0.10 and fp[0] == 0.423828125 and block(a)[L].get("n", 512) == 512
        elif crit == "exact_code":
            row["floor_fingerprint"] = (block(a)[L].get("floor_acc_last"), block(o)[L].get("floor_acc_last"))
            ok = av >= 0.99 and row["floor_fingerprint"][0] == 0.423828125
        elif crit == "not_exact":
            ok = av < 0.99
        elif crit == "exact":
            ok = av >= 0.99
        elif crit == "chance_band":
            k = round(av * 128)
            row["count_of_128"] = k
            ok = 7 <= k <= 20
        elif crit == "exact_after_600":
            ok = av >= 0.99 and (sel(a) or 0) >= 600
        elif crit == "le_0.02":
            ok = av <= 0.02
        row["pass"] = bool(ok)
        out[job] = row
        print(job, json.dumps(row))
    (HERE / "score.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
