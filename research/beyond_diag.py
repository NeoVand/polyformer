"""BEYOND Stage 1: the language layer, unchanged, on causal diagnostic tasks.

Small retrieval tasks are learnability screens; ``mqar`` and ``indist`` retain
the historical generators. ``gmatch_a5_causal`` differs from GROUPS' noncausal
``g3_a5``: only a triple ending at the current token can make its label positive.
All task labels depend exclusively on the input prefix.
``regression`` uses continuous [key1, key2, value, is_query] inputs, a learned
input/output projection, and the exact same lm.block stack. A fresh random
affine function is sampled for each sequence; its query value is hidden.

Example:
    python research/beyond_diag.py --task mqar_small --arch gpt --layers 2

``--target-fpt F`` sets a fixed reference forward FLOPs/token budget shared by
all configurations for one task/depth: execute floor(steps * F / own_F) updates.
Compute F externally over the fully specified arms, including RNN variants.
``--equal-flops`` is a convenience for same-configuration peers only; it inherits
the current arm's settings and cannot define a fair cross-variant reference.
An explicit --target-fpt overrides its maximum. ``--steps`` is the reference
update budget, not necessarily the executed update count. The counter is
lm.flops_per_token (with the continuous regression input/output adjustment);
reported wall time remains separate from this architectural FLOP convention.
Rate selection uses validation only; a disjoint final test is evaluated once.
"""

import argparse
import hashlib
import itertools
import json
import math
import pathlib
import sys
import time

import jax
import jax.numpy as jnp
import numpy as np
import optax

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import diag  # noqa: E402
import groups  # noqa: E402
import lm  # noqa: E402

ARCHS = ("gpt", "lla", "plx", "beyond_a", "beyond_b", "beyond_c", "gated_delta", "prefix", "loop")


def induction_small(rng, B, T=128, Q=8, V=128):
    """Each query occurs exactly three times before its final test occurrence."""
    x = rng.integers(32, V, (B, T), dtype=np.int32)
    y = np.zeros((B, T), np.int32)
    m = np.zeros((B, T), np.float32)
    for b in range(B):
        qs = rng.choice(np.arange(1, 32), Q, replace=False)
        slots = np.sort(rng.choice(np.arange(0, T - Q - 1, 2), 3 * Q, replace=False))
        occurrences = rng.permutation(np.tile(qs, 3))
        last = {}
        for s, q in zip(slots, occurrences):
            successor = rng.integers(32, V)
            x[b, s], x[b, s + 1] = q, successor
            last[int(q)] = successor
        order = rng.permutation(qs)
        x[b, -Q:] = order
        y[b, -Q:] = [last[int(q)] for q in order]
        m[b, -Q:] = 1
    return x, y, m


def word(rng, B, name, length):
    x, y, m = groups.task_word(rng, B, name, length, "class")
    return x[..., 0], y, m


def causal_match_labels(g, G=None):
    """Label at t: exists i < j < t with g_i g_j g_t equal to the identity."""
    G = groups.get("A5") if G is None else G
    B, n = g.shape
    y = np.zeros((B, n), np.int32)
    for i, j in itertools.combinations(range(n - 1), 2):
        pair = G.mul[g[:, i], g[:, j]]
        y[:, j + 1:] |= G.mul[pair[:, None], g[:, j + 1:]] == G.e
    return y


def gmatch_a5_causal(rng, B, n=16):
    G = groups.get("A5")
    g = rng.integers(0, G.n, (B, n))
    x = np.concatenate([np.full((B, 1), G.n), g], axis=1)
    y = np.concatenate([np.zeros((B, 1), np.int32), causal_match_labels(g, G)], axis=1)
    m = np.ones_like(y, np.float32)
    m[:, :3] = 0  # BOS and the first two elements have no possible triple.
    return x, y, m


def regression(rng, B, n=16, query_scale=2.5):
    """Infer a new affine map from 16 examples; evaluate at an independent query."""
    keys = rng.normal(size=(B, n, 2))
    query = rng.normal(size=(B, 2)) * query_scale
    slopes = rng.normal(size=(B, 2))
    intercept = rng.normal(size=B)
    values = np.einsum("bnr,br->bn", keys, slopes) + intercept[:, None]
    answer = (query * slopes).sum(-1) + intercept
    x = np.zeros((B, n + 1, 4), np.float32)
    x[:, :n, :2], x[:, :n, 2] = keys, values
    x[:, n, :2], x[:, n, 3] = query, 1
    return x, answer.astype(np.float32), np.ones(B, np.float32)


# name -> (generator, context length including BOS when present, input/output
# vocabulary, default positional embeddings, labels whose balanced recall is read)
TASKS = {
    "mqar_small": (lambda r, b: diag.mqar(r, b, T=128, N=16, V=256), 128, 256, 1, None),
    "induction_small": (induction_small, 128, 128, 1, None),
    "mqar": (diag.mqar, 256, 8192, 1, None),
    "indist": (diag.indist, 256, 512, 1, None),
    "gmatch_a5_causal": (gmatch_a5_causal, 17, 61, 0, 2),
    "regression": (regression, 17, 1, 0, None),
}
for _name, _order in (("a5", 60), ("s5", 120)):
    for _length in (16, 64):
        TASKS[f"wp_{_name}_{_length}"] = (
            (lambda name, length: lambda r, b: word(r, b, name, length))(_name.upper(), _length),
            _length + 1, _order + 1, 0, _order,
        )


def parse_setting(value):
    name, sep, raw = value.partition("=")
    if not sep or not name:
        raise argparse.ArgumentTypeError("--set must be KEY=JSON_VALUE (or KEY=plain_string)")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = raw
    return name, parsed


def model_config(args, context, vocab, default_pos):
    cfg = argparse.Namespace(
        arch=args.arch, d=args.d, layers=args.layers, heads=args.heads,
        nheads=args.heads, rank=args.d // args.heads // 2, order=3, phase=2.0,
        vac=0.05, alpha0=2, cap=0.0, fscale=1, hops=1, lookback=0, lbdim=8,
        ctx=context, vocab=vocab, remat=0, mlp=args.mlp or 4 * args.d,
        chart=args.chart, chart_init=0.5, lam0=1.0,
        pos=default_pos if args.pos is None else args.pos, plx_norm=0,
        gdim=5, gheads=args.heads, nh=4, group_nh=4, group_order=2,
        conv_width=4, branch_scale=0.1,
    )
    for key, value in args.set:
        if key in {"arch", "d", "layers", "heads", "ctx", "vocab", "mlp", "pos"}:
            raise ValueError(f"Set {key} through its dedicated CLI option")
        setattr(cfg, key, value)
    if cfg.d % cfg.heads:
        raise ValueError("d must be a multiple of heads")
    if getattr(cfg, "delta_chunk", 0):
        raise ValueError("Diagnostic budgets use the native/unrolled recurrence; delta_chunk must be 0")
    return cfg


def task_flops(cfg, context, regression_task=False):
    fpt = float(lm.flops_per_token(cfg, context))
    if regression_task:
        # Replace the language output with a 4 -> D projection on every token
        # and D -> 1 read-out only at the final query.
        fpt += 8 * cfg.d + 2 * cfg.d / context - 2 * cfg.d * cfg.vocab
    return fpt


def compute_budget(cfg, context, reference_steps, peers, regression_task=False, target_fpt=None):
    """Match total training FLOPs, rounding updates down; explicit target wins.

    The explicit reference may be below this arm's per-token cost, in which case
    this arm receives fewer than reference_steps updates. A budget too small to
    fund one update is rejected instead of silently exceeding the budget.
    """
    own = task_flops(cfg, context, regression_task)
    costs = {cfg.arch: own}
    for arch in peers:
        other = argparse.Namespace(**{**vars(cfg), "arch": arch})
        costs[arch] = task_flops(other, context, regression_task)
    reference = max(costs.values()) if target_fpt is None else float(target_fpt)
    if not math.isfinite(reference) or reference <= 0:
        raise ValueError("target FLOPs/token must be finite and positive")
    # With no compute matching, execute the requested update count exactly.
    # Multiplying before dividing can otherwise turn 1000 into 999 through
    # rounding when the recurrence counter has fractional FLOPs/token.
    steps = int(reference_steps) if target_fpt is None and not peers else math.floor(reference_steps * (reference / own))
    if steps < 1:
        raise ValueError("training FLOP budget cannot fund one update; increase --steps or --target-fpt")
    return steps, own, costs


def metrics(pred, y, m, classes=None, word_task=False):
    """Pooled accuracy, balanced recall, and sequence-aware uncertainty."""
    mask = np.asarray(m, bool)
    hit = (pred == y) & mask
    counts = mask.sum(1)
    successes = hit.sum(1)
    accuracy = float(hit.sum() / max(mask.sum(), 1))
    # Cluster standard error for a ratio of totals, treating sequences as iid.
    influence = successes - accuracy * counts
    acc_se = float(influence.std(ddof=1) / math.sqrt(len(y)) / max(counts.mean(), 1e-30)) if len(y) > 1 else 0.0
    result = {
        "acc": accuracy,
        "acc_se_sequences": acc_se,
        "seq_acc": float(((pred == y) | ~mask).all(1).mean()),
        "scored_tokens": int(mask.sum()),
        "per_pos": (hit.sum(0) / np.maximum(mask.sum(0), 1)).tolist(),
    }
    if classes is not None:
        label_counts = np.array([((y == c) & mask).sum() for c in range(classes)])
        correct = np.array([((y == c) & hit).sum() for c in range(classes)])
        present = label_counts > 0
        result["bal_acc"] = float((correct[present] / label_counts[present]).mean())
        result["label_counts"] = label_counts.tolist()
    if word_task:
        half = np.arange(y.shape[1]) > y.shape[1] // 2
        late = metrics(pred, y, mask & half, classes=classes)
        result["bal_late"] = late["bal_acc"]
        result["acc_late"] = late["acc"]
    return result


def regression_metrics(pred, y, x):
    err2 = np.square(np.asarray(pred, np.float64) - y)
    variance = float(np.var(y))
    baseline = np.square(x[:, :-1, 2].mean(1) - y)
    mse = float(err2.mean())
    se = float(err2.std(ddof=1) / math.sqrt(len(y))) if len(y) > 1 else 0.0
    return {
        "mse": mse, "mse_se_examples": se,
        "mse_ci95_normal": [max(0.0, mse - 1.96 * se), mse + 1.96 * se],
        "target_variance": variance, "normalized_mse": mse / max(variance, 1e-30),
        "mean_value_baseline_mse": float(baseline.mean()),
        "mse_over_mean_value_baseline": mse / max(float(baseline.mean()), 1e-30),
        "examples": len(y),
    }


def regression_forward(cfg, p, x):
    x = lm.lin(p["input"], x)
    for lyr in p["layers"]:
        x = lm.block(cfg, lyr, x)
    return lm.lin(p["output"], lm.ln(p["lnf"], x[:, -1]))[:, 0]


def source_hashes():
    result = {}
    directory = pathlib.Path(__file__).parent
    for name in ("beyond_diag.py", "lm.py", "beyond_layers.py", "groups.py", "diag.py"):
        path = directory / name
        if path.exists():
            result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", choices=TASKS, default="mqar_small")
    ap.add_argument("--arch", choices=ARCHS, default="gpt")
    ap.add_argument("--layers", type=int, default=1)
    ap.add_argument("--d", type=int, default=128)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--mlp", type=int, default=0)
    ap.add_argument("--chart", type=int, default=8)
    ap.add_argument("--pos", type=int, choices=(0, 1), default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--lr", type=float, default=0.004)
    ap.add_argument("--opt", choices=("adamw", "muon"), default="muon")
    ap.add_argument("--wd", type=float, default=0.1)
    ap.add_argument("--evalset", type=int, default=1024)
    ap.add_argument("--testset", type=int, default=2048)
    ap.add_argument("--evalbatch", type=int, default=128)
    ap.add_argument("--evals", type=int, default=10)
    ap.add_argument("--progress", action="store_true", help="emit per-evaluation progress JSON to stderr")
    ap.add_argument("--evallen", type=int, default=0)
    ap.add_argument("--equal-flops", default="", help="same-configuration peers; explicit --target-fpt overrides")
    ap.add_argument("--target-fpt", type=float, default=None,
                    help="fixed reference forward FLOPs/token shared across fully specified arms")
    ap.add_argument("--set", type=parse_setting, action="append", default=[])
    args = ap.parse_args()
    if min(args.steps, args.batch, args.evalset, args.testset, args.evalbatch, args.evals) <= 0:
        ap.error("steps, batch, evalset, testset, evalbatch, and evals must be positive")
    gen, T, V, default_pos, classes = TASKS[args.task]
    regression_task = args.task == "regression"
    if args.evallen and not args.task.startswith("wp_"):
        ap.error("--evallen is supported only for word problems")
    cfg = model_config(args, max(T, args.evallen + 1), V, default_pos)
    peers = [arch.strip() for arch in args.equal_flops.split(",") if arch.strip()]
    if any(arch not in ARCHS for arch in peers):
        ap.error(f"--equal-flops accepts only {','.join(ARCHS)}")
    try:
        steps, fpt, peer_costs = compute_budget(cfg, T, args.steps, peers, regression_task, args.target_fpt)
    except ValueError as error:
        ap.error(str(error))
    reference_fpt = max(peer_costs.values()) if args.target_fpt is None else args.target_fpt
    rng = np.random.default_rng(args.seed)
    params = lm.init(jax.random.PRNGKey(args.seed), cfg)
    if regression_task:
        params.pop("emb")
        params.pop("pos", None)
        params["input"] = lm.dense(jax.random.PRNGKey(args.seed + 71_000), 4, cfg.d)
        params["output"] = lm.dense(jax.random.PRNGKey(args.seed + 72_000), cfg.d, 1)
    nparams = sum(int(x.size) for x in jax.tree_util.tree_leaves(params))
    schedule = optax.warmup_cosine_decay_schedule(
        0.0, args.lr, min(max(1, steps // 20), steps - 1), max(steps, 2), args.lr * 0.05,
    )
    optimizer = lm.make_opt(args.opt, schedule, wd=args.wd)
    state = optimizer.init(params)

    def loss_fn(p, x, y, m):
        if regression_task:
            return jnp.mean((regression_forward(cfg, p, x) - y) ** 2)
        ce = optax.softmax_cross_entropy_with_integer_labels(lm.forward(cfg, p, x), y)
        return (ce * m).sum() / m.sum()

    @jax.jit
    def update(p, st, x, y, m):
        loss, grad = jax.value_and_grad(loss_fn)(p, x, y, m)
        updates, st = optimizer.update(grad, st, p)
        return optax.apply_updates(p, updates), st, loss

    @jax.jit
    def predict(p, x):
        if regression_task:
            return regression_forward(cfg, p, x)
        return lm.forward(cfg, p, x).argmax(-1)

    @jax.jit
    def parameters_finite(p):
        return jnp.stack([jnp.isfinite(leaf).all() for leaf in jax.tree_util.tree_leaves(p)]).all()

    def evaluate(p, generator, count, seed):
        x, y, m = generator(np.random.default_rng(seed), count)
        pred = []
        for start in range(0, count, args.evalbatch):
            xb = x[start:start + args.evalbatch]
            real = len(xb)
            if real < args.evalbatch:
                padding = [(0, args.evalbatch - real)] + [(0, 0)] * (xb.ndim - 1)
                xb = np.pad(xb, padding, mode="edge")
            pred.append(np.asarray(predict(p, jnp.asarray(xb, jnp.float32 if regression_task else jnp.int32)))[:real])
        if regression_task:
            return regression_metrics(np.concatenate(pred), y, x)
        return metrics(np.concatenate(pred), y, m, classes, args.task.startswith("wp_"))

    t0 = time.time()
    curve = []
    interval = max(1, steps // args.evals)
    finished = 0
    failure = None
    for it in range(steps):
        x, y, m = gen(rng, args.batch)
        params, state, loss = update(
            params, state, jnp.asarray(x, jnp.float32 if regression_task else jnp.int32),
            jnp.asarray(y, jnp.float32 if regression_task else jnp.int32), jnp.asarray(m, jnp.float32),
        )
        finished = it + 1
        if finished % interval == 0 or finished == steps:
            value = float(loss)
            if not math.isfinite(value):
                failure = "nonfinite_training_loss"
                break
            if not bool(parameters_finite(params)):
                failure = "nonfinite_parameters"
                break
            validation = evaluate(params, gen, args.evalset, 10_000 + args.seed)
            elapsed = round(time.time() - t0, 3)
            curve.append({"step": finished, "loss": value, "validation": validation, "secs": elapsed})
            if args.progress:
                progress = {
                    "event": "diagnostic_progress", "task": args.task, "arch": args.arch,
                    "seed": args.seed, "step": finished, "planned_steps": steps,
                    "secs": elapsed, "loss": value,
                    "validation": {key: validation[key] for key in
                                   ("acc", "bal_acc", "bal_late", "mse", "normalized_mse") if key in validation},
                }
                print(json.dumps(progress, allow_nan=False), file=sys.stderr, flush=True)
    final = evaluate(params, gen, args.testset, 20_000 + args.seed) if failure is None else None
    output = {
        "task": args.task, "arch": args.arch, "model": args.arch, "layers": args.layers,
        "seed": args.seed, "lr": args.lr, "opt": args.opt, "config": vars(cfg),
        "params": nparams, "steps": finished, "reference_steps": args.steps,
        "batch": args.batch, "train_tokens": finished * args.batch * T,
        "flops_per_token": fpt, "peer_flops_per_token": peer_costs,
        "target_flops_per_token": reference_fpt,
        "budget_source": "explicit_target_fpt" if args.target_fpt is not None else "same_config_peer_maximum",
        "train_flops": 3 * fpt * finished * args.batch * T,
        "reference_train_flops": 3 * reference_fpt * args.steps * args.batch * T,
        "validation_seed": 10_000 + args.seed, "test_seed": 20_000 + args.seed,
        "evalset": args.evalset, "testset": args.testset,
        "selection_metric": "final_validation_mse" if regression_task else
                            "final_validation_bal_late" if args.task.startswith("wp_") else
                            "final_validation_bal_acc" if classes else "final_validation_acc",
        "curve": curve, "validation": curve[-1]["validation"] if curve else None,
        "test": final, "failure": failure, "backend": jax.default_backend(),
        "source_sha256": source_hashes(),
    }
    if final is not None:
        output.update({name: final[name] for name in ("acc", "bal_acc", "bal_late", "mse", "normalized_mse") if name in final})
        output["component_parameters"] = [
            {
                name: np.asarray(layer[name]).tolist()
                for name in ("group_mix", "path_mix", "context_mix", "A_log", "dt_bias")
                if name in layer
            }
            for layer in params["layers"]
        ]
    if args.evallen and final is not None:
        group = args.task.split("_")[1].upper()
        extrapolation = lambda r, b: word(r, b, group, args.evallen)
        output["extrapolation"] = {
            "length": args.evallen,
            "positions_beyond_training_untrained": bool(cfg.pos and args.evallen + 1 > T),
            "test": evaluate(params, extrapolation, args.testset, 30_000 + args.seed),
        }
    output["secs"] = round(time.time() - t0, 3)
    print(json.dumps(output, allow_nan=False))


if __name__ == "__main__":
    main()
