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


def lm_a() -> list[list[str]]:
    """Byte-level enwik8, matched parameters: GPT, GPT with a Newton branch, Newton alone."""
    runs = []
    for seed in (0, 1, 2):
        base = ["--steps", "8000", "--seed", str(seed)]
        runs.append(["--arch", "gpt", *base])
        runs.append(["--arch", "hybrid", "--rank", "32", *base])
        runs.append(["--arch", "newton", "--rank", "64", *base])
    return runs


def sfa_a() -> list[list[str]]:
    """Subset attention (polybench --model sfa): does query-dependent selection keep Newton attention's
    arity results, add what selection should add, and remove its failures on chains?"""
    nw = {"readout": "shared", "fnorm": 1}
    runs = []
    # A. the Match-k ladder at the newton_e configuration, plus the exclusion and vacuum ablations
    runs += grid(["zs3", "zs4", "zs5", "arity"], ["sfa"], [0, 1, 2], steps=6000, rank=256, fnorm=1)
    runs += grid(["zs4"], ["sfa"], [0, 1, 2], steps=6000, rank=256, fnorm=1, stats="bose")
    runs += grid(["zs4"], ["sfa"], [0, 1, 2], steps=6000, rank=256, fnorm=1, vac=0.0)
    # B. keyed Match-k: zero sums count only among cards with the query's key; other keys are distractors
    for rank in (64, 256):
        runs += grid(["kzs3", "kzs4"], ["sfa"], [0, 1, 2], steps=6000, rank=rank, fnorm=1)
        runs += grid(["kzs3", "kzs4"], ["newton"], [0, 1, 2], steps=6000, rank=rank, **nw)
    runs += grid(["kzs3", "kzs4"], ["sa"], [0, 1, 2], steps=6000, layers=3)
    runs += grid(["kzs3", "kzs4"], ["cubic"], [0, 1, 2], steps=6000)
    # C. chains, the baseline grid's protocol: depth, and the walk sector in one layer
    for layers in (1, 2, 3):
        runs += grid(["chase", "compose3"], ["sfa"], [0, 1, 2], steps=4000, rank=32, order=4, fnorm=1, layers=layers)
    runs += grid(["chase"], ["sfa"], [0, 1, 2], steps=4000, rank=32, order=4, fnorm=1, hops=4)
    runs += grid(["compose3"], ["sfa"], [0, 1, 2], steps=4000, rank=32, order=4, fnorm=1, hops=3)
    # D. width on Match-4, one head: channels needed with and without selection
    for rank in (32, 64, 128, 256):
        runs += grid(["zs4"], ["sfa"], [0, 1, 2], steps=6000, heads=1, rank=rank, fnorm=1)
        runs += grid(["zs4"], ["newton"], [0, 1, 2], steps=6000, heads=1, rank=rank, **nw)
    return runs


def lm_sfa() -> list[list[str]]:
    """enwik8 with subset attention in place of softmax attention (it contains it), its arity-1-only
    ablation, and a rerun of the GPT baseline to check the numbers carry over."""
    runs = []
    for seed in (0, 1, 2):
        base = ["--steps", "8000", "--seed", str(seed)]
        runs.append(["--arch", "sfa", "--order", "4", "--rank", "32", *base])
        runs.append(["--arch", "sfa", "--order", "1", "--rank", "32", *base])
    runs.append(["--arch", "gpt", "--steps", "8000", "--seed", "0"])
    return runs


def sfa_b() -> list[list[str]]:
    """Follow-ups to sfa_a: how much the vacuum costs on pure arity tasks, and keyed Match-4 with a
    distractor curriculum (sfa_a's keyed tasks sat at majority for every model)."""
    nw = {"readout": "shared", "fnorm": 1}
    runs = []
    runs += grid(["zs5"], ["sfa"], [0, 1, 2], steps=6000, rank=256, fnorm=1, vac=0.0)
    runs += grid(["zs5"], ["sfa"], [0, 1, 2], steps=6000, rank=512, fnorm=1, vac=0.0)
    runs += grid(["zs4", "zs5"], ["sfa"], [0, 1, 2], steps=6000, rank=256, fnorm=1, vac=0.05)
    runs += grid(["kd4"], ["sfa"], [0, 1, 2], steps=10000, rank=256, fnorm=1, vac=0.05)
    runs += grid(["kd4"], ["sfa"], [0, 1, 2], steps=10000, rank=256, fnorm=1, vac=0.0)
    runs += grid(["kd4"], ["newton"], [0, 1, 2], steps=10000, rank=256, **nw)
    return runs


def lm_sfa_b() -> list[list[str]]:
    """Subset attention on enwik8 with arities 2..4 switched off at initialisation, and a smaller vacuum."""
    runs = []
    for seed in (0, 1, 2):
        base = ["--steps", "8000", "--seed", str(seed), "--arch", "sfa", "--order", "4", "--rank", "32"]
        runs.append([*base, "--alpha0", "1"])
        runs.append([*base, "--alpha0", "1", "--vac", "0.05"])
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
    "lm_a": lm_a(),
    "sfa_a": sfa_a(),
    "lm_sfa": lm_sfa(),
    "sfa_b": sfa_b(),
    "lm_sfa_b": lm_sfa_b(),
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
