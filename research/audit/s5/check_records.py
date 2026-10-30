import json, pathlib, math
W = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees/invariance-3e22f3")
A = json.load(open(W / "research/results/invariance/ABLATION_S5.json"))
CFG = ["model","ds","mu","pair","dist","mu_warmup","ns","ns_kl","rms","mu_delay","e_train","d","steps","batch","lr","a_scale","params","registered","test"]
recs = {}
mism = 0
for c in A["records"]:
    src = W / c["source_record"]
    r = json.load(open(src))
    recs[(c["arm"], c["mu"], c["seed"])] = r
    E = r["results"]["1024"]["acc_last"]
    exp = {"exact_train": r["results"]["16"]["acc_last"] >= 0.99, "exact_64x": E >= 0.99, "p_longest": 1 - E ** (1/1024),
           "acc_last_val_256": r["results"]["256"]["acc_last"], "acc_last_64x": E,
           "growth_cos_16_256": r["inv_dist"]["256"]["reduced_cos"] - r["inv_dist"]["16"]["reduced_cos"]}
    for k, v in exp.items():
        if (isinstance(v, float) and abs(v - c[k]) > 1e-12) or (not isinstance(v, float) and v != c[k]):
            print("MISMATCH", c["arm"], c["mu"], c["seed"], k, v, c[k]); mism += 1
    if r["seed"] != c["seed"]: print("SEED MISMATCH", src)
    # mean clause and n
    res = r["results"]["1024"]
    n_last = res["acc_last"] * 512
    print(f'{c["arm"]:7s} mu={str(c["mu"]):4s} s{c["seed"]} {src.name:42s} last1024={E:.6f} (x512={n_last:.1f}) mean1024={res["acc_mean"]:.4f} last256={r["results"]["256"]["acc_last"]:.4f} mean256={r["results"]["256"]["acc_mean"]:.4f} exact64x={c["exact_64x"]} exact_with_mean={E>=0.99 and res["acc_mean"]>=0.99} steps={r["steps"]} last_curve_step={r["curve"][-1]["step"]} curve0={ {k:v for k,v in r["curve"][0].items() if k not in ("secs",)} } mu_t_logged={any("mu_t" in x for x in r["curve"])}')
print("mismatches:", mism)
print()
print("=== config diffs vs O (base) of same seed ===")
for (arm, mu, s), r in sorted(recs.items(), key=lambda t: (t[0][2], t[0][0], str(t[0][1]))):
    b = recs[("O", None, s)]
    diffs = {k: (b.get(k, "<absent>"), r.get(k, "<absent>")) for k in CFG if b.get(k, "<absent>") != r.get(k, "<absent>")}
    print(f"s{s} {arm:7s} mu={mu}: {diffs}")
