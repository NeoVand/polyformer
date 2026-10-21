"""Job lists for LOOPS.md stages; writes JSON for loops_modal.py plan. Never launches anything.

    python research/loops_jobs.py screen > /tmp/screen.json
"""

import json
import pathlib
import sys

# The BEYOND language protocol (beyond_language_tuning / seed manifests), unchanged.
LM = ["--data", "/data/fineweb_edu", "--vocab", "50304", "--ctx", "512", "--d", "512", "--heads", "8",
      "--layers", "6", "--mlp", "2048", "--opt", "muon", "--batch", "64", "--micro", "2", "--bf16", "1",
      "--remat", "1", "--tokens", "0", "--vseqs", "1024", "--progress", "1", "--qkv_conv", "3",
      "--delta_key_ratio", "0.75", "--delta_v_expand", "2.0", "--delta_unroll", "4", "--delta_chunk", "32",
      "--cap", "0", "--hops", "1", "--lookback", "0"]

# model sizes: the BEYOND size, and one about three times larger in non-embedding parameters
SIZES = {"base": {"d": "512", "heads": "8", "layers": "6", "mlp": "2048"},
         "large": {"d": "768", "heads": "12", "layers": "8", "mlp": "3072"}}

# name -> (arch arguments, max seconds for a 100M-token run)
ARMS = {
    "abs": (["--arch", "gpt", "--pos", "1"], 900),
    "rope": (["--arch", "loop", "--posenc", "rope"], 900),
    "grid": (["--arch", "loop", "--posenc", "grid"], 900),
    "grid_forget": (["--arch", "loop", "--posenc", "grid", "--forget", "1"], 900),
    "holo": (["--arch", "loop", "--posenc", "holo"], 1100),
    "holo_forget": (["--arch", "loop", "--posenc", "holo", "--forget", "1"], 1100),
    "holo_forget_vtrans": (["--arch", "loop", "--posenc", "holo", "--forget", "1", "--vtrans", "1"], 1100),
    "rope_forget": (["--arch", "loop", "--posenc", "rope", "--forget", "1"], 900),
    "hybrid_rope": (["--arch", "loop", "--posenc", "rope", "--pattern", "GAGAGA"], 1300),
    "hybrid_holo_forget": (["--arch", "loop", "--posenc", "holo", "--forget", "1", "--pattern", "GAGAGA"], 1400),
    "loop": (["--arch", "loop", "--posenc", "rope", "--layers", "4", "--loop_order", "0,1,2,1,2,3"], 900),
    "hybrid_rope_forget": (["--arch", "loop", "--posenc", "rope", "--forget", "1", "--pattern", "GAGAGA"], 1300),
    "hybrid_grid_forget": (["--arch", "loop", "--posenc", "grid", "--forget", "1", "--pattern", "GAGAGA"], 1300),
    "hybrid_holo_forget_vtrans": (["--arch", "loop", "--posenc", "holo", "--forget", "1", "--vtrans", "1",
                                   "--pattern", "GAGAGA"], 1400),
    "hybrid_holo_forget_AG": (["--arch", "loop", "--posenc", "holo", "--forget", "1", "--pattern", "AGAGAG"], 1400),
    "hybrid_holo_forget_GGA": (["--arch", "loop", "--posenc", "holo", "--forget", "1", "--pattern", "GGAGGA"], 1400),
    "hybrid_holo_forget_DA": (["--arch", "loop", "--posenc", "holo", "--forget", "1", "--pattern", "DADADA"], 2000),
    "rope4": (["--arch", "loop", "--posenc", "rope", "--layers", "4"], 900),
    "gdn": (["--arch", "gated_delta", "--pos", "1", "--qkv_conv", "0", "--nh", "1", "--beta_max", "1",
             "--group_init", "random", "--gdim", "5"], 1400),
    "deltaproduct": (["--arch", "gated_delta", "--pos", "1", "--qkv_conv", "0", "--nh", "4", "--beta_max", "2",
                      "--group_init", "random", "--gdim", "5"], 2600),
}


def sized(argv, size):
    """Replace the width, heads, layer count and MLP of the base protocol with a size preset."""
    argv = list(argv)
    for key, value in SIZES[size].items():
        i = argv.index("--" + key)
        argv[i + 1] = value
    return argv


def arch_for(name, size="base"):
    """An arm's arguments at a size: a hybrid pattern is repeated to the preset's layer count."""
    arch = list(ARMS[name][0])
    if "--pattern" in arch and "--layers" not in arch:
        i = arch.index("--pattern")
        layers = int(SIZES[size]["layers"])
        arch[i + 1] = (arch[i + 1] * layers)[:layers]
    return arch


def lm_job(name, seed, steps, warmup, lr, evals, vbig, scale=1.0, size="base"):
    _, seconds = ARMS[name]
    arch = arch_for(name, size)
    argv = sized(LM, size)
    # an arm may override the layer count (the depth loop): drop the default first
    if "--layers" in arch:
        i = argv.index("--layers")
        del argv[i:i + 2]
    argv += arch + ["--lr", str(lr), "--seed", str(seed), "--steps", str(steps), "--warmup", str(warmup),
                    "--evals", str(evals), "--vbig", str(vbig)]
    if vbig:
        argv += ["--save-final", "1"]
    return {"script": "lm.py", "argv": argv, "gpu": "H100", "max_seconds": int(seconds * scale), "name": name}


def diag_job(task, layers, sets, steps=6000, lr=0.004, seed=0):
    argv = ["--task", task, "--arch", "loop", "--layers", str(layers), "--d", "128", "--heads", "4",
            "--steps", str(steps), "--lr", str(lr), "--seed", str(seed), "--pos", "0", "--progress",
            "--set", "qkv_conv=3"]
    for s in sets:
        argv += ["--set", s]
    return {"script": "beyond_diag.py", "argv": argv, "gpu": "L4", "max_seconds": 2400}


def stage(name):
    if name == "synthetic":
        jobs = []
        for sets in (["posenc=rope"], ["posenc=grid"], ["posenc=holo"], ["posenc=holo", "vtrans=1"]):
            jobs.append(diag_job("wp_a5_16", 1, sets))
        for sets in (["posenc=rope"], ["posenc=holo", "forget=1"]):
            jobs.append(diag_job("mqar_small", 2, sets))
        return jobs
    if name == "screen":
        jobs = [lm_job(n, 0, 3051, 305, 0.008, 8, 0) for n in ARMS]
        jobs += [lm_job(n, 0, 3051, 305, 0.012, 8, 0) for n in ("rope", "holo_forget")]
        return jobs
    if name == "eval":
        # every confirmation checkpoint (lang_core, lang_extra, lang_dp), four per L4 job
        import glob
        paths = []
        for p in sorted(glob.glob(str(pathlib.Path(__file__).parent / "results" / "loops_runs" / "*.json"))):
            r = json.load(open(p))
            if r.get("manifest", "").startswith("loops_lang") and r.get("val_big_raw"):
                paths.append(f"/runs/{r['job_id']}/final.pkl")
        jobs = []
        for i in range(0, len(paths), 4):
            argv = ["--ckpts", ",".join(paths[i:i + 4]), "--data", "/data/fineweb_edu", "--ablate", "1"]
            jobs.append({"script": "loops_eval.py", "argv": argv, "gpu": "L4", "max_seconds": 2400})
        return jobs
    if name == "screen2":
        names = ("hybrid_rope_forget", "hybrid_grid_forget", "hybrid_holo_forget_vtrans", "hybrid_holo_forget_AG",
                 "hybrid_holo_forget_GGA", "hybrid_holo_forget_DA", "rope4")
        return [lm_job(n, 0, 3051, 305, 0.008, 8, 0) for n in names]
    if name.startswith("language"):
        # language:arm1,arm2,...:seeds[:size]  e.g. language:abs,rope,hybrid_rope:1,2,3
        parts = name.split(":")
        arms, seeds = parts[1], parts[2]
        size = parts[3] if len(parts) > 3 else "base"
        # the larger model costs about (FLOPs ratio) more per update than the base one
        slow = 1.0 if size == "base" else flops_ratio_to_base("rope", size)
        jobs = []
        for seed in seeds.split(","):
            for n in arms.split(","):
                steps = equal_flop_steps(n, size)
                job = lm_job(n, int(seed), steps, 400, 0.008, 16, 1024, size=size)
                # timeout from the measured 3,051-update screen wall, with margin for evaluation and saving
                job["max_seconds"] = min(7200, int(SCREEN_WALL[n] * slow * steps / 3051 * 1.6 + 300))
                jobs.append(job)
        return jobs
    raise SystemExit(f"unknown stage {name}")


# measured seconds for 3,051 updates (loops_screen / loops_screen2; GDN and DeltaProduct from BEYOND's
# tuning ledger: about $0.80 and $1.65 at its rate)
SCREEN_WALL = {"abs": 300, "rope": 306, "grid": 320, "grid_forget": 329, "holo": 394, "holo_forget": 425,
               "holo_forget_vtrans": 431, "rope_forget": 328, "hybrid_rope": 451, "hybrid_holo_forget": 532,
               "hybrid_rope_forget": 445, "hybrid_grid_forget": 474, "hybrid_holo_forget_vtrans": 525,
               "hybrid_holo_forget_AG": 507, "hybrid_holo_forget_GGA": 542, "hybrid_holo_forget_DA": 835,
               "loop": 303, "rope4": 232, "gdn": 520, "deltaproduct": 1200}

REFERENCE_STEPS = 13531  # BEYOND's convolved-softmax final budget (about 443M tokens)


def flops_ratio_to_base(name, size):
    return arm_flops(name, size) / arm_flops(name, "base")


def equal_flop_steps(name, size="base"):
    """Updates giving this arm the convolved-softmax control's modeled training FLOPs (lm's convention),
    the control being abs at the same size and 13,531 updates."""
    return int(REFERENCE_STEPS * arm_flops("abs", size) / arm_flops(name, size))


def arm_flops(name, size="base"):
    """Modeled training FLOPs per token of an arm at a size preset."""
    import argparse
    import pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    import lm

    def cfg(argv):
        d = {argv[i][2:]: argv[i + 1] for i in range(0, len(argv), 2)}
        dims = {k: int(v) for k, v in SIZES[size].items()}
        c = dict(arch="gpt", d=dims["d"], layers=dims["layers"], heads=dims["heads"], mlp=dims["mlp"], ctx=512, vocab=50304, qkv_conv=3, posenc="abs",
                 holo=16, modules=4, holo_init=0.05, rope_base=10000.0, forget=0, forget_bias=5.0, vtrans=0,
                 pattern="", loop_order="", nh=1, beta_max=1.0, delta_key_ratio=0.75, delta_v_expand=2.0,
                 delta_chunk=32, delta_unroll=4, conv_width=4, hops=1, lookback=0, cap=0.0, bf16=1, pos=1,
                 nheads=4, rank=32, order=4, gdim=5)
        for k in ("arch", "posenc", "pattern", "loop_order"):
            if k in d:
                c[k] = d[k]
        for k in ("layers", "forget", "vtrans", "holo", "modules", "nh", "qkv_conv"):
            if k in d:
                c[k] = int(d[k])
        if "beta_max" in d:
            c["beta_max"] = float(d["beta_max"])
        return argparse.Namespace(**c)

    return lm.training_flops_per_token(cfg(arch_for(name, size)), 512)


if __name__ == "__main__":
    jobs = stage(sys.argv[1])
    for j in jobs:
        j.pop("name", None)
    print(json.dumps(jobs, indent=1))
