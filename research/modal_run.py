"""
Run research/polybench.py configurations on Modal GPUs and append the results to
research/results/<name>.jsonl. Each configuration is one argv list for polybench.

    uvx modal run research/modal_run.py::main --grid smoke
    uvx modal run research/modal_run.py::main --grid <name> --gpu H100
    uvx modal run research/modal_run.py::prep        # tokenise the language-model corpora once

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


# token-level language models (SEARCH.md S0-S2): GPT-2 ids written once into a Volume as uint16
data_vol = modal.Volume.from_name("polyformer-data", create_if_missing=True)
tok_image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "tiktoken", "numpy", "pyarrow", "huggingface_hub[hf_transfer]"
).env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})


@app.function(image=tok_image, volumes={"/data": data_vol}, cpu=16, memory=65536, timeout=3 * 3600)
def tokenize(name: str) -> dict:
    """GPT-2 tokens with <|endoftext|> between documents: /data/<name>/{train,val}.bin (uint16)."""
    import os

    import numpy as np
    import tiktoken
    from huggingface_hub import hf_hub_download

    enc = tiktoken.get_encoding("gpt2")
    eot = enc.eot_token
    out = f"/data/{name}"
    os.makedirs(out, exist_ok=True)
    counts = {}

    def write(docs_iter, path):
        n = 0
        with open(path, "wb") as fh:
            for docs in docs_iter:
                ids = enc.encode_ordinary_batch(docs, num_threads=16)
                arr = np.fromiter((t for d in ids for t in (*d, eot)), dtype=np.uint16)
                fh.write(arr.tobytes())
                n += len(arr)
        return n

    def chunks(seq, k=20000):
        for i in range(0, len(seq), k):
            yield seq[i : i + k]

    if name == "tinystories":
        for split, fn in (("train", "TinyStoriesV2-GPT4-train.txt"), ("val", "TinyStoriesV2-GPT4-valid.txt")):
            p = hf_hub_download("roneneldan/TinyStories", fn, repo_type="dataset", cache_dir="/tmp/hf")
            docs = [d.strip() for d in open(p, encoding="utf-8").read().split("<|endoftext|>") if d.strip()]
            counts[split] = write(chunks(docs), f"{out}/{split}.bin")
    elif name == "fineweb_edu":
        import pyarrow.parquet as pq

        p = hf_hub_download("HuggingFaceFW/fineweb-edu", "sample/10BT/000_00000.parquet", repo_type="dataset", cache_dir="/tmp/hf")
        pf = pq.ParquetFile(p)
        held = []

        def train_docs():
            i = 0
            for b in pf.iter_batches(batch_size=20000, columns=["text"]):
                docs = b.column(0).to_pylist()
                keep = []
                for d in docs:
                    (held if i % 100 == 0 else keep).append(d)  # every hundredth document is held out
                    i += 1
                yield keep

        counts["train"] = write(train_docs(), f"{out}/train.bin")
        counts["val"] = write(chunks(held), f"{out}/val.bin")
    data_vol.commit()
    return {"name": name, **counts}


@app.function(image=lm_image, gpu="H100", volumes={"/data": data_vol}, timeout=6 * 3600)
def run_tok(argv: list[str]) -> dict:
    return _run(argv, "/root/lm.py")


diag_image = image.add_local_file(pathlib.Path(__file__).parent / "lm.py", "/root/lm.py").add_local_file(
    pathlib.Path(__file__).parent / "diag.py", "/root/diag.py"
)


@app.function(image=diag_image, gpu="L4", timeout=2 * 3600)
def run_diag(argv: list[str]) -> dict:
    return _run(argv, "/root/diag.py")


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


def diag_grid(tasks, models, layers, seeds, lrs, steps=4000):
    runs = []
    for t, m, L, sd, lr in itertools.product(tasks, models, layers, seeds, lrs):
        runs.append(["--task", t, "--model", m, "--layers", str(L), "--seed", str(sd), "--lr", str(lr), "--steps", str(steps)])
    return runs


DIAG_TASKS = ["mqar", "mqar2", "selcopy", "indist", "phop4", "phop8", "phop16", "dyck2", "add", "match3"]
DIAG_MODELS = ["softmax", "ff", "softmaxw", "lookback", "ffw"]


def tok_argv(data, arch, layers, lr, seed, tokens, **kw):
    """One token-level LM run at the S0 scale: width 512, 8 heads, context 512, batch 64 x 512 tokens."""
    argv = ["--data", f"/data/{data}", "--vocab", "50304", "--ctx", "512", "--d", "512", "--heads", "8",
            "--batch", "64", "--micro", "2", "--bf16", "1", "--remat", "1", "--vseqs", "128", "--evals", "24",
            "--probe", "1", "--arch", arch, "--layers", str(layers), "--lr", str(lr), "--seed", str(seed),
            "--tokens", str(int(tokens))]
    if arch == "sfa":
        argv += ["--order", "4", "--rank", "32", "--vac", "0.05", "--alpha0", "1", "--fscale", "1"]
    for k, v in kw.items():
        argv += [f"--{k}", str(v)]
    return argv


def loc_argv(data, arch, lr, seed, tokens, opt, chart=8, **kw):
    """LOCAL.md: one token-level run at the S0 scale and protocol (6 layers), softmax (gpt), Parallax (plx) or
    ridge local-linear attention (lla, chart r), with AdamW or Muon."""
    argv = tok_argv(data, arch, 6, lr, seed, tokens, opt=opt, vbig=1024, **kw)
    if arch == "lla":
        argv += ["--chart", str(chart)]
    return argv


def loc_diag(models, layers, seeds, lrs, opts, tasks=("mqar", "mqar2", "indist", "match3"), steps=3000):
    return [argv + ["--opt", o] for o in opts for argv in diag_grid(list(tasks), models, layers, seeds, lrs, steps)]


# LOCAL.md arms: S (softmax), P (Parallax), L8 (ridge local-linear, r = 8); the Stage 3 ladder adds r = 1, 2, 4, 16
LOC_ARMS = [("gpt", 8), ("plx", 8), ("lla", 8)]
LOC_OPTS = ("adamw", "muon")
LOC_LRS = (2e-3, 4e-3, 8e-3)
STEPS_400M = 12207                       # 400M tokens at 64 x 512 per step, as S0
STEPS_EQF = {"L8": 12613, "P": 13044}    # S's steps at L8's and P's FLOPs (1.0332x, 1.0686x)

def loc_best_rates():
    """LOCAL.md 4.2: each arm's best rate per optimizer = lowest val_big at 100M in the sweep (diverged = worst)."""
    import math

    best = {}
    lines = []
    for g in ("tok_loc_lr", "tok_loc_lr2"):
        p = pathlib.Path(__file__).parent / "results" / f"{g}.jsonl"
        lines += p.read_text().splitlines() if p.exists() else []
    for line in lines:
        r = json.loads(line)
        if r.get("error"):
            continue
        v = r.get("val_big", float("inf"))
        v = float("inf") if v is None or math.isnan(v) else v
        k = (r["arch"], r["opt"])
        if k not in best or v < best[k][1]:
            best[k] = (r["lr"], v)
    return {k: lr for k, (lr, _) in best.items()}


def loc_confirm():
    """Stage 2: every arm and optimizer at its best rate, three seeds, 400M tokens."""
    b = loc_best_rates()
    return [loc_argv("fineweb_edu", a, b[(a, o)], sd, STEPS_400M * 32768, o, chart=r, early=100)
            for a, r in LOC_ARMS for o in LOC_OPTS if (a, o) in b for sd in (0, 1, 2)]


def loc_eqf():
    """Stage 2: S at its best rate per optimizer, trained to L8's and to P's FLOPs, three seeds."""
    b = loc_best_rates()
    return [loc_argv("fineweb_edu", "gpt", b[("gpt", o)], sd, steps * 32768, o, early=100)
            for o in LOC_OPTS if ("gpt", o) in b for steps in STEPS_EQF.values() for sd in (0, 1, 2)]


# S0 architectures: softmax (6 layers), free-field at equal parameters (6), at equal FLOPs (5), softmax + 1 layer
S0_ARCHS = [("gpt", 6), ("sfa", 6), ("sfa", 5), ("gpt", 7)]

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
    "sfa_a": sfa_a(),
    "lm_sfa": lm_sfa(),
    "sfa_b": sfa_b(),
    "lm_sfa_b": lm_sfa_b(),
    # timing: a few hundred steps of each S0 architecture, and two S1 configurations
    "tok_time": [tok_argv("tinystories", a, L, 1.5e-3, 0, 64 * 512 * 200, evals=2) for a, L in S0_ARCHS],
    "diag_time": diag_grid(["mqar", "phop4"], ["softmax", "ffw"], [2], [0], [1e-3], steps=1000),
    # S0 learning-rate sweep: every architecture, three rates, one seed, 100M tokens, both corpora
    "tok_s0_lr": [tok_argv(d, a, L, lr, 0, 1e8, early=50) for d in ("tinystories", "fineweb_edu")
                  for a, L in S0_ARCHS for lr in (1e-3, 2e-3, 4e-3)],
    # S1 pilot: are the tasks learnable in 3,000 steps at one rate?
    "diag_pilot": diag_grid(DIAG_TASKS, ["softmax", "ffw"], [2], [0], [3e-3], steps=3000),
    # S0 confirmation on FineWeb-Edu at 400M tokens, three seeds, each architecture at its best rate;
    # plus free-field with every arity off at initialisation (the S1 amendment) at the equal-FLOPs depth
    "tok_s0": [tok_argv("fineweb_edu", a, L, lr, sd, 4e8, early=100) for sd in (0, 1, 2)
               for a, L, lr in (("gpt", 6, 4e-3), ("gpt", 7, 2e-3), ("sfa", 5, 4e-3), ("sfa", 6, 4e-3))]
              + [tok_argv("fineweb_edu", "sfa", 5, 4e-3, sd, 4e8, early=100, alpha0=2) for sd in (0, 1, 2)],
    # S2: induction through training, 100M tokens, evaluations every 50 steps up to step 1,600
    "tok_s2": [tok_argv(d, a, 6, lr, sd, 1e8, early=50, early_until=1600, **kw) for d, lr in (("fineweb_edu", 4e-3), ("tinystories", 2e-3))
               for sd in (0, 1, 2)
               for a, kw in (("gpt", {}), ("gpt", {"lookback": 1}), ("sfa", {}), ("sfa", {"lookback": 1, "hops": 2}))],
    # S2 follow-up: the look-back variants are unstable at 4e-3 on FineWeb-Edu; give them their own rates
    "tok_s2b": [tok_argv("fineweb_edu", a, 6, lr, sd, 1e8, early=50, early_until=1600, **kw) for lr in (1e-3, 2e-3)
                for sd in (0, 1, 2) for a, kw in (("gpt", {"lookback": 1}), ("sfa", {"lookback": 1, "hops": 2}))],
    # S1: every task, model and depth, three seeds, one rate for all
    "diag_s1": diag_grid(DIAG_TASKS, DIAG_MODELS, [1, 2], [0, 1, 2], [3e-3], steps=3000),
    # LOCAL.md timing: 200 steps of each arm (and r = 16) under both optimizers on H100
    "tok_loc_time": [loc_argv("fineweb_edu", a, 4e-3, 0, 64 * 512 * 200, o, chart=r, evals=2)
                     for a, r in LOC_ARMS + [("lla", 16)] for o in ("adamw", "muon")],
    # LOCAL.md design pilot (before the pre-registration was frozen): is Parallax stable without RMSNorm on rho?
    "tok_loc_pilot": [loc_argv("fineweb_edu", a, 4e-3, 0, 64 * 512 * 1500, o, evals=6, **kw)
                      for a, kw in (("gpt", {}), ("plx", {"plx_norm": 0}), ("plx", {"plx_norm": 1}), ("lla", {}))
                      for o in ("adamw", "muon")],
    # LOCAL.md Stage 2 sweep: every arm and optimizer at three rates, seed 0, 100M tokens
    "tok_loc_lr": [loc_argv("fineweb_edu", a, lr, 0, 1e8, o, chart=r, early=100) for a, r in LOC_ARMS
                   for o in LOC_OPTS for lr in LOC_LRS],
    # LOCAL.md amendment 1: one octave beyond the grid edge for the cells whose best rate sat on it
    "tok_loc_lr2": [loc_argv("fineweb_edu", a, lr, 0, 1e8, o, early=100)
                    for a, o, lr in (("gpt", "muon", 1.6e-2), ("lla", "muon", 1.6e-2), ("plx", "adamw", 1e-3))],
    # LOCAL.md Stage 2 confirmation (best rates from the sweep) and S at equal FLOPs
    "tok_loc_s2": loc_confirm(),
    "tok_loc_eqf": loc_eqf(),
    # LOCAL.md Stage 3 (only after a headline go): the arity ladder at L8's best optimizer and rate, seed 0
    "tok_loc_ladder": [loc_argv("fineweb_edu", "lla", loc_best_rates().get(("lla", o), 0), 0, STEPS_400M * 32768, o,
                                chart=r, early=100) for o in ("muon",) for r in (1, 2, 4, 16)],
    # LOCAL.md Stage 1: mechanism diagnostics, S widened to L8's FLOPs, one and two layers, 3 seeds, both optimizers
    "diag_loc_s1": loc_diag(["softmaxl", "plx", "lla"], [1, 2], [0, 1, 2], [3e-3], ["adamw", "muon"]),
}


@app.local_entrypoint()
def main(grid: str = "smoke", gpu: str = "L4"):
    runs = GRIDS[grid]
    fn = run_diag if grid.startswith("diag_") else run_tok if grid.startswith("tok_") else run_lm if grid.startswith("lm_") else run_h100 if gpu.upper() == "H100" else run_l4
    out = pathlib.Path(__file__).parent / "results" / f"{grid}.jsonl"
    t0 = time.time()
    with out.open("a") as f:
        for r in fn.map(runs, order_outputs=False):
            f.write(json.dumps(r) + "\n")
            f.flush()
            brief = {k: r.get(k) for k in ("task", "model", "arch", "seed", "tok_acc", "val_bpc", "secs", "error")}
            print(json.dumps(brief))
    print(f"{len(runs)} runs in {time.time() - t0:.0f}s -> {out}")


@app.local_entrypoint()
def prep(name: str = "all"):
    """uvx modal run research/modal_run.py::prep -- tokenise TinyStories and the FineWeb-Edu shard."""
    names = ["tinystories", "fineweb_edu"] if name == "all" else [name]
    for r in tokenize.map(names):
        print(json.dumps(r))
