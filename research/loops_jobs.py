"""Job lists for LOOPS.md stages; writes JSON for loops_modal.py plan. Never launches anything.

    python research/loops_jobs.py screen > /tmp/screen.json
"""

import json
import sys

# The BEYOND language protocol (beyond_language_tuning / seed manifests), unchanged.
LM = ["--data", "/data/fineweb_edu", "--vocab", "50304", "--ctx", "512", "--d", "512", "--heads", "8",
      "--layers", "6", "--mlp", "2048", "--opt", "muon", "--batch", "64", "--micro", "2", "--bf16", "1",
      "--remat", "1", "--tokens", "0", "--vseqs", "1024", "--progress", "1", "--qkv_conv", "3",
      "--delta_key_ratio", "0.75", "--delta_v_expand", "2.0", "--delta_unroll", "4", "--delta_chunk", "32",
      "--cap", "0", "--hops", "1", "--lookback", "0"]

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
}


def lm_job(name, seed, steps, warmup, lr, evals, vbig, scale=1.0):
    arch, seconds = ARMS[name]
    argv = list(LM)
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
    raise SystemExit(f"unknown stage {name}")


if __name__ == "__main__":
    jobs = stage(sys.argv[1])
    for j in jobs:
        j.pop("name", None)
    print(json.dumps(jobs, indent=1))
