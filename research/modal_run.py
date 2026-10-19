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


# the language-model runs: enwik8 baked into the image, lm.py instead of polybench.py
lm_image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("wget", "unzip")
    .run_commands(
        "wget -q http://mattmahoney.net/dc/enwik8.zip -O /root/enwik8.zip && cd /root && unzip -q enwik8.zip && rm enwik8.zip"
    )
    .pip_install("jax[cuda12]", "optax", "numpy")
    .add_local_file(pathlib.Path(__file__).parent / "lm.py", "/root/lm.py")
)


def _run(argv: list[str], script: str = "/root/polybench.py") -> dict:
    import subprocess
    import sys

    t0 = time.time()
    p = subprocess.run([sys.executable, script, *argv], capture_output=True, text=True)
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


@app.function(image=lm_image, gpu="H100", timeout=3 * 3600)
def run_lm(argv: list[str]) -> dict:
    return _run(argv, "/root/lm.py")


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


def newton_c() -> list[list[str]]:
    """Newton v2: diagnostics for the figures, and one change at a time against the caveats."""
    runs = []
    hard = ["zs4", "zs5"]
    # A. rank 256 with diagnostics (arity contribution, knockouts, character fidelity)
    runs += grid(["zs3", "zs4", "zs5", "arity", "set"], ["newton"], [0, 1, 2], steps=6000, rank=256)
    # B. one read-out shared across arities: a sixth of the parameters at rank 256
    runs += grid(["zs3", "zs4", "zs5", "arity"], ["newton"], [0, 1, 2], steps=6000, rank=256, readout="shared")
    runs += grid(["zs4", "zs5", "arity"], ["newton"], [0, 1, 2], steps=6000, rank=512, readout="shared")
    # C-G. normalised features, phases from the raw stream, two layers, longer, wider
    runs += grid(hard, ["newton"], [0, 1, 2], steps=6000, rank=256, fnorm=1)
    runs += grid(hard, ["newton"], [0, 1, 2], steps=6000, rank=256, rawphase=1)
    runs += grid(hard, ["newton"], [0, 1, 2], steps=6000, rank=256, layers=2)
    runs += grid(hard, ["newton"], [0, 1, 2], steps=20000, rank=256)
    runs += grid(hard, ["newton"], [0, 1, 2], steps=6000, rank=512)
    return runs


def newton_fig() -> list[list[str]]:
    """One run per task with every diagnostic, including per-card phases, for the paper's figures."""
    return grid(["zs3", "zs4", "arity"], ["newton"], [0], steps=6000, rank=256)


def newton_d() -> list[list[str]]:
    """Do characters found on triples unlock quadruples? One model trained on mixed arities,
    scored on each arity separately; controls are the single-arity runs in newton_c."""
    runs = grid(["mix345"], ["newton"], [0, 1, 2], steps=6000, rank=256)
    runs += grid(["mix345"], ["newton"], [0, 1, 2], steps=18000, rank=256)
    runs += grid(["mix34"], ["newton"], [0, 1, 2], steps=12000, rank=256)
    return runs


def newton_e() -> list[list[str]]:
    """The two fixes that worked, together and across every task: normalised features per
    arity, and one read-out shared by all arities."""
    every = ["zs3", "zs4", "zs5", "arity", "set", "set4"]
    runs = grid(every, ["newton"], [0, 1, 2], steps=6000, rank=256, readout="shared", fnorm=1)
    runs += grid(["zs4", "zs5", "arity", "set4"], ["newton"], [0, 1, 2], steps=6000, rank=512, readout="shared", fnorm=1)
    runs += grid(["zs3", "arity", "set", "set4"], ["newton"], [0, 1, 2], steps=6000, rank=256, fnorm=1)
    runs += grid(["zs5"], ["newton"], [0, 1, 2], steps=6000, rank=512, fnorm=1)
    runs += grid(["zs5"], ["newton"], [0, 1, 2], steps=12000, rank=256, fnorm=1)
    return runs


def newton_f() -> list[list[str]]:
    """Mixed arities with the fixes: does the transfer survive, and does it close the gap?"""
    runs = grid(["mix345"], ["newton"], [0, 1, 2], steps=6000, rank=256, fnorm=1)
    runs += grid(["mix345"], ["newton"], [0, 1, 2], steps=6000, rank=256, fnorm=1, readout="shared")
    runs += grid(["mix345"], ["newton"], [0, 1, 2], steps=18000, rank=256, fnorm=1, readout="shared")
    runs += grid(["mix345"], ["newton"], [0, 1, 2], steps=18000, rank=512, fnorm=1, readout="shared")
    return runs


def homa_m3() -> list[list[str]]:
    """Match3 on HOMA's protocol (Amiraslani & Gao, arXiv 2603.11133 v2, Tables 2 and A.1-A.3, App. B, D.1):
    N = 6 (M = 30) and N = 8 (M = 56); 30,000 training and 2,000 test sequences per seed, 40 epochs of
    batch 256, Adam at 3e-3 with no schedule, decay or clipping; one attention layer, four heads, no MLP,
    a frozen Fourier basis then a learned projection, no positions; final-epoch accuracy, seeds 0-2.
    Baselines at the width of HOMA's best run (64 and 128); Newton attention at width 64 with its rank
    set so the layer has HOMA's parameter count there, about 28k and 91k (rank 24 and 84)."""
    proto = dict(embed="fourier", pos=0, ffn=0, trainset=30000, epochs=40, batch=256, lr=3e-3, wd=0,
                 clip=0, sched="const", evalset=2000)
    runs = []
    for task, d, rank in (("match3_n6", 64, 24), ("match3_n8", 128, 84)):
        for layers in (1, 2, 3):
            runs += grid([task], ["sa"], [0, 1, 2], layers=layers, d=d, **proto)
        runs += grid([task], ["cubic"], [0, 1, 2], d=d, repeat=1, **proto)
        runs += grid([task], ["newton"], [0, 1, 2], rank=rank, readout="shared", fnorm=1, **proto)
        # over budget: the rank of Section 6.4, to separate capacity from the operator
        runs += grid([task], ["newton"], [0, 1, 2], rank=256, readout="shared", fnorm=1, **proto)
    return runs


def lm_a() -> list[list[str]]:
    """Byte-level enwik8, matched parameters: GPT, GPT with a Newton branch, Newton alone."""
    runs = []
    for seed in (0, 1, 2):
        base = ["--steps", "8000", "--seed", str(seed)]
        runs.append(["--arch", "gpt", *base])
        runs.append(["--arch", "hybrid", "--rank", "32", *base])
        runs.append(["--arch", "newton", "--rank", "64", *base])
    return runs


GRIDS = {
    "smoke": grid(["set"], ["cubic", "sa"], [0], steps=300),
    "baseline": baseline(),
    "phase_a": phase_a(),
    "newton_a": newton_a(),
    "newton_b": newton_b(),
    "newton_c": newton_c(),
    "newton_fig": newton_fig(),
    "newton_d": newton_d(),
    "newton_e": newton_e(),
    "newton_f": newton_f(),
    "homa_m3": homa_m3(),
    "lm_a": lm_a(),
}


@app.local_entrypoint()
def main(grid: str = "smoke", gpu: str = "L4"):
    runs = GRIDS[grid]
    fn = run_lm if grid.startswith("lm_") else run_h100 if gpu.upper() == "H100" else run_l4
    out = pathlib.Path(__file__).parent / "results" / f"{grid}.jsonl"
    t0 = time.time()
    with out.open("a") as f:
        for r in fn.map(runs, order_outputs=False):
            f.write(json.dumps(r) + "\n")
            f.flush()
            brief = {k: r.get(k) for k in ("task", "model", "arch", "seed", "tok_acc", "val_bpc", "secs", "error")}
            print(json.dumps(brief))
    print(f"{len(runs)} runs in {time.time() - t0:.0f}s -> {out}")
