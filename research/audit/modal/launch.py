"""Spawn the ten registered Modal reruns of research/audit/RERUNS.md on the deployed app polyformer-audit, write the
call ids to calls.json, and exit (no live client: the runs survive the laptop sleeping)."""
import json
import pathlib
import sys
import time

import modal

ARITH = ["--steps", "3000", "--batch", "64", "--lr", "1e-3", "--d", "128", "--mu_delay", "400", "--mu_warmup", "200",
         "--lengths", "32,256,1024,4096", "--n_eval", "512,512,512,128", "--time_budget", "1500", "--tag", "audit"]
CODE = ["--layer", "mid", "--steps", "16000", "--batch", "64", "--lr", "0.001", "--d", "128", "--mu_delay", "800",
        "--mu_warmup", "400", "--tag", "audit"]
LEAN = ["research/lean_run.py", "run", "--data", "a4x", "--head", "pos", "--outdir", "lean_s", "--steps", "12000",
        "--model", "rec", "--d", "128", "--seed", "0", "--tag", "audit", "--xla_flags=--xla_gpu_enable_triton_gemm=false"]
JOBS = [  # (job id, function, tree, argv)
    ("code_O_s0", "run_cpu_long", "code", ["research/exec_lm_run.py", "run", "--arm", "R", "--seed", "0", *CODE]),
    ("code_FULLN_s0", "run_cpu_long", "code", ["research/exec_lm_run.py", "run", "--arm", "RNLIr", "--seed", "0", *CODE]),
    ("add_O_s0", "run_cpu_short", "arith", ["research/exec_arith.py", "run", "--task", "add", "--arm", "R", "--seed", "0", *ARITH]),
    ("add_FULLN_s0", "run_cpu_short", "arith", ["research/exec_arith.py", "run", "--task", "add", "--arm", "RNLIr", "--seed", "0", *ARITH]),
    ("count_O_s0", "run_cpu_short", "arith", ["research/exec_arith.py", "run", "--task", "count", "--arm", "R", "--seed", "0", *ARITH]),
    ("count_FULLN_s3", "run_cpu_short", "arith", ["research/exec_arith.py", "run", "--task", "count", "--arm", "RNLIr", "--seed", "3",
                                                  "--select_after", "600", *ARITH]),
    ("lean_O_s0", "run_h100", "lean", LEAN),
    ("lean_FULLN_s0", "run_h100", "lean", [*LEAN, "--fixed_norm", "--mu", "1", "--pair", "random", "--nextlat", "1"]),
    ("stories_O_s10", "run_l4", "stories", ["research/stories_track.py", "--arm", "none", "--rms", "0", "--tag", "O", "--seed", "10",
                                            "--time_budget", "1150", "--out", "out/O_s10"]),
    ("stories_FULLN_s10", "run_l4", "stories", ["research/stories_track.py", "--arm", "cert", "--nextlat", "1", "--tag", "FULLN",
                                                "--seed", "10", "--time_budget", "1150", "--out", "out/FULLN_s10"]),
]

if __name__ == "__main__":
    only = set(sys.argv[1:])
    out = pathlib.Path(__file__).parent / "calls.json"
    calls = json.loads(out.read_text()) if out.exists() else {}
    for job, fn, tree, argv in JOBS:
        if (only and job not in only) or job in calls:
            continue
        call = modal.Function.from_name("polyformer-audit", fn).spawn(job, tree, argv)
        calls[job] = {"call_id": call.object_id, "function": fn, "tree": tree, "argv": argv,
                      "spawned": time.strftime("%Y-%m-%d %H:%M:%S %Z")}
        out.write_text(json.dumps(calls, indent=1) + "\n")
        print(job, call.object_id, flush=True)
