"""
Run research/polybench.py configurations on Modal GPUs and append the results to
research/results/<name>.jsonl. Each configuration is one argv list for polybench.

    uvx modal run research/modal_run.py --grid smoke
    uvx modal run research/modal_run.py --grid <name> --gpu H100

Grids live in GRIDS below; every run records its argv, so a results file is its
own provenance. The browser app never imports anything from here.
"""

import itertools
import json
import pathlib
import time

import modal

app = modal.App("polyformer-bench")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("jax[cuda12]", "optax", "numpy")
    .add_local_file(pathlib.Path(__file__).parent / "polybench.py", "/root/polybench.py")
)


def _run(argv: list[str]) -> dict:
    import subprocess
    import sys

    t0 = time.time()
    p = subprocess.run([sys.executable, "/root/polybench.py", *argv], capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith("{")]
    if p.returncode != 0 or not lines:
        return {"argv": argv, "error": (p.stderr or p.stdout)[-2000:], "wall": round(time.time() - t0, 1)}
    out = json.loads(lines[-1])
    out["argv"] = argv
    out["wall"] = round(time.time() - t0, 1)
    return out


@app.function(image=image, gpu="L4", timeout=3 * 3600)
def run_l4(argv: list[str]) -> dict:
    return _run(argv)


@app.function(image=image, gpu="H100", timeout=3 * 3600)
def run_h100(argv: list[str]) -> dict:
    return _run(argv)


def grid(task: list[str], model: list[str], seed: list[int], **fixed) -> list[list[str]]:
    runs = []
    for t, m, s in itertools.product(task, model, seed):
        argv = ["--task", t, "--model", m, "--seed", str(s)]
        for k, v in fixed.items():
            argv += [f"--{k}", str(v)]
        runs.append(argv)
    return runs


def baseline() -> list[list[str]]:
    """Replicate the operator tournament: every operator on the four core tasks, three seeds."""
    rounds = {"set": 2, "set4": 3, "chase": 4, "compose3": 3}
    runs = []
    for task, r in rounds.items():
        models: list[tuple[str, dict]] = [
            ("sa", {"layers": 1}),
            ("sa", {"layers": 2}),
            ("sa", {"layers": 3}),
            ("tree", {}),
            ("strassen", {}),
            ("cubic", {}),
            ("dspa4", {"plen": r, "modes": 16}),
        ]
        if task == "set4":
            models.append(("quartic", {}))
        for model, extra in models:
            runs += grid([task], [model], [0, 1, 2], steps=4000, **extra)
    return runs


def phase_a() -> list[list[str]]:
    """Match-k ladder and the smallest-arity task, every operator, three seeds; plus a width sweep."""
    runs = []
    for task in ["zs3", "zs4", "zs5", "arity"]:
        models: list[tuple[str, dict]] = [
            ("sa", {"layers": 1}),
            ("sa", {"layers": 2}),
            ("sa", {"layers": 3}),
            ("cubic", {}),
            ("dspa4", {"plen": 3, "modes": 16}),
            ("dspa5", {"plen": 3, "modes": 8}),
            ("dspa5", {"plen": 3, "modes": 8, "nocubic": 1}),
        ]
        if task == "zs4":
            models.append(("quartic", {}))
        for model, extra in models:
            runs += grid([task], [model], [0, 1, 2], steps=6000, **extra)
    # Proposition 6 predicts DS-PA v5 needs total width near |G| = 81 on Z_3^4
    for d in (128, 192):
        for extra in ({"plen": 3, "modes": 8}, {"plen": 3, "modes": 8, "nocubic": 1}):
            runs += grid(["zs4"], ["dspa5"], [0, 1, 2], steps=6000, d=d, **extra)
    return runs


def newton_a() -> list[list[str]]:
    """Newton attention on the Match-k ladder, plus the controls that make it a test, not a demo."""
    runs = []
    for steps in (6000, 20000):
        runs += grid(["zs3", "zs4", "zs5", "arity"], ["newton"], [0, 1, 2], steps=steps)
    # arity must be offered: order K = 3 cannot see 4-subsets, K = 4 cannot see 5-subsets
    runs += grid(["zs4"], ["newton"], [0, 1, 2], steps=6000, order=3)
    runs += grid(["zs5"], ["newton"], [0, 1, 2], steps=20000, order=4)
    # width: one head, complex rank r; |G| - 1 = 80 real directions = 40 conjugate pairs on Z_3^4
    for r in (8, 16, 32, 40, 48, 64, 128):
        runs += grid(["zs4"], ["newton"], [0, 1, 2], steps=10000, heads=1, rank=r)
    # the replication tasks, same protocol as the baseline grid
    runs += grid(["set", "set4", "chase", "compose3"], ["newton"], [0, 1, 2], steps=4000)
    return runs


def newton_b() -> list[list[str]]:
    """Wider Newton attention, its order ablation at that width, and width-matched baselines."""
    runs = []
    for r in (128, 256):
        runs += grid(["zs3", "zs4", "zs5", "arity", "set", "set4"], ["newton"], [0, 1, 2], steps=6000, rank=r)
    runs += grid(["zs4"], ["newton"], [0, 1, 2], steps=6000, rank=128, order=3)
    runs += grid(["zs5"], ["newton"], [0, 1, 2], steps=6000, rank=128, order=4)
    # parameter-matched baselines: width alone does not give pairwise or cubic attention a fourth token
    runs += grid(["zs4", "zs5"], ["sa"], [0, 1, 2], steps=6000, layers=3, d=256)
    runs += grid(["zs4", "zs5"], ["cubic"], [0, 1, 2], steps=6000, d=192)
    return runs


GRIDS = {
    "smoke": grid(["set"], ["cubic", "sa"], [0], steps=300),
    "baseline": baseline(),
    "phase_a": phase_a(),
    "newton_a": newton_a(),
    "newton_b": newton_b(),
}


@app.local_entrypoint()
def main(grid: str = "smoke", gpu: str = "L4"):
    runs = GRIDS[grid]
    fn = run_h100 if gpu.upper() == "H100" else run_l4
    out = pathlib.Path(__file__).parent / "results" / f"{grid}.jsonl"
    t0 = time.time()
    with out.open("a") as f:
        for r in fn.map(runs, order_outputs=False):
            f.write(json.dumps(r) + "\n")
            f.flush()
            brief = {k: r.get(k) for k in ("task", "model", "seed", "tok_acc", "seq_acc", "secs", "error")}
            print(json.dumps(brief))
    print(f"{len(runs)} runs in {time.time() - t0:.0f}s -> {out}")
