import json, pathlib, sys
W = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees/lean-n-data-34a2d2")
d = json.load(open(W/"research/results/stories/ABLATION_stories.json"))
for r in d["records"]:
    src = json.load(open(W/r["source_record"]))
    c = src["config"]
    last = src["log"][-1]
    first_full = next((l["step"] for l in src["log"] if l["mu"] >= 1.0), None)
    t = src["test"]
    t1024 = t.get("1024") or t.get(1024)
    t16 = t.get("16") or t.get(16)
    ok64 = abs(t1024["exact_last"] - r["exact_64x"]) < 1e-12
    ok16 = abs(t16["exact_last"] - r["exact_train"]) < 1e-12
    print(f'{r["arm"]:7s} s{r["seed"]} steps={src["steps_done"]} rec_steps={r["steps_done"]} train_secs={src["train_secs"]} last_log_step={last["step"]} mu_last={last["mu"]} first_logged_mu1={first_full} '
          f'pd_last={last["pair_dist"]} acc={last["train_obj_acc"]} e16={t16["exact_last"]} e1024={t1024["exact_last"]} match16={ok16} match1024={ok64} '
          f'cfg: arm={c["arm"]} rms={c.get("rms","<absent>")} nextlat={c.get("nextlat","<absent>")} mu={c["mu"]} delay={c["mu_delay"]} warm={c["mu_warmup"]} n_train={c["n_train"]} n_test={c["n_test"]} lengths={c["lengths"]} steps={c["steps"]} tb={c["time_budget"]} enc={c["encoder"]} batch={c["batch"]} lr={c["lr"]} seed={c["seed"]} tag={c.get("tag")}')
