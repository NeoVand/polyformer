"""ARC-format, three-demo operator inference from grids, never primitive labels.

The invertible family is CLOSED: every word reduces to a D4/translation spatial
map and a background-preserving colour permutation. Nominal depth is NOT an
intrinsic difficulty measure. Functional hashes (not program strings) split its
train/test operators. The irreversible split hashes program strings, because
canonical functional equivalence there is unavailable.

Crop means nonzero bounding box moved to the top left of the SAME 6x6 canvas;
gravity packs each column down, retaining order; fill replaces the four-connected
component containing its fixed seed. These deliberately retain fixed output size.

The privileged family solver enumerates all 288 affine spatial actions and fits
colour bijections from demonstrations. It is an identifiability diagnostic, not
the learned composing arm. Learned models receive only demonstration/query cells.
"""
import argparse
import hashlib
import json
import math
import os
import pickle
import time
from functools import lru_cache, partial
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import optax

from beyond_layers import householder_products, matrix_prefix

SIZE = 6
TIERS = ("invertible", "irreversible")


def apply_primitive(grid, primitive):
    grid = np.asarray(grid)
    kind, *args = primitive
    if kind == "d4":
        k = int(args[0])
        return np.rot90(np.fliplr(grid) if k >= 4 else grid, k % 4).copy()
    if kind == "translate":
        return np.roll(grid, (int(args[0]), int(args[1])), axis=(0, 1))
    if kind == "colour":
        return np.asarray(args, dtype=np.int32)[grid]
    if kind == "crop":
        result = np.zeros_like(grid)
        rows, cols = np.nonzero(grid)
        if rows.size:
            box = grid[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
            result[:box.shape[0], :box.shape[1]] = box
        return result
    if kind == "gravity":
        result = np.zeros_like(grid)
        for col in range(grid.shape[1]):
            values = grid[:, col][grid[:, col] != 0]
            if len(values):
                result[-len(values):, col] = values
        return result
    if kind == "fill":
        row, col, colour = map(int, args)
        result, source = grid.copy(), grid[row, col]
        stack, seen = [(row, col)], set()
        while stack:
            r, c = stack.pop()
            if (r, c) in seen or not (0 <= r < SIZE and 0 <= c < SIZE) or grid[r, c] != source:
                continue
            seen.add((r, c))
            result[r, c] = colour
            stack.extend(((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)))
        return result
    raise ValueError(primitive)


def apply_program(grid, program):
    result = np.asarray(grid).copy()
    for primitive in program:
        result = apply_primitive(result, primitive)
    return result


def sample_program(rng, depth, tier):
    primitives = []
    irreversible_at = int(rng.integers(depth)) if tier == "irreversible" else -1
    for index in range(depth):
        kind = int(rng.integers(3))
        if index == irreversible_at:
            primitives.append(("crop",) if kind == 0 else ("gravity",) if kind == 1
                              else ("fill", int(rng.integers(SIZE)), int(rng.integers(SIZE)), int(rng.integers(1, 10))))
        elif kind == 0:
            primitives.append(("d4", int(rng.integers(1, 8))))
        elif kind == 1:
            shift = int(rng.integers(1, SIZE * SIZE))
            primitives.append(("translate", shift // SIZE, shift % SIZE))
        else:
            primitives.append(("colour", 0, *map(int, rng.permutation(np.arange(1, 10)))))
    return tuple(primitives)


def canonical_operator(program):
    spatial = np.arange(SIZE * SIZE).reshape(SIZE, SIZE)
    colours = np.arange(10)
    for primitive in program:
        if primitive[0] == "colour":
            colours = np.asarray(primitive[1:])[colours]
        elif primitive[0] in ("d4", "translate"):
            spatial = apply_primitive(spatial, primitive)
        else:
            raise ValueError("Irreversible primitives have no canonical affine operator")
    return spatial.reshape(-1), colours


def operator_split(program, tier):
    if tier == "invertible":
        spatial, colours = canonical_operator(program)
        key = spatial.astype(np.uint8).tobytes() + colours.astype(np.uint8).tobytes()
    else:
        key = json.dumps(program, separators=(",", ":")).encode()
    # Fixed public partition; seed changes grids/program draws, not partition.
    return "test" if int.from_bytes(hashlib.sha256(key).digest()[:4], "little") % 5 == 0 else "train"


@lru_cache(None)
def spatial_candidates():
    grid = np.arange(SIZE * SIZE).reshape(SIZE, SIZE)
    candidates, factors = [], []
    for d4 in range(8):
        for row in range(SIZE):
            for col in range(SIZE):
                candidates.append(apply_program(grid, (("d4", d4), ("translate", row, col))).reshape(-1))
                factors.append(int(d4 != 0) + int(row != 0 or col != 0))
    return np.asarray(candidates), np.asarray(factors)


def operator_diagnostics(program):
    spatial, colours = canonical_operator(program)
    candidates, factors = spatial_candidates()
    mask = np.all(candidates == spatial, axis=1)
    count = int(factors[mask].min()) + int(np.any(colours != np.arange(10)))
    return {"effective_factor_count": count, "identity": bool(count == 0),
            "canonical_id": hashlib.sha256(spatial.astype(np.uint8).tobytes() + colours.astype(np.uint8).tobytes()).hexdigest()[:16]}


def sample_grid(rng, tier):
    if tier == "invertible":
        return rng.integers(0, 10, (SIZE, SIZE), dtype=np.int32)
    grid = np.zeros((SIZE, SIZE), np.int32)
    # Sparse connected rectangles plus a few points make crop/gravity nontrivial.
    for _ in range(int(rng.integers(1, 4))):
        r, c = rng.integers(0, SIZE, 2)
        h, w = rng.integers(1, 4, 2)
        grid[r:min(r + h, SIZE), c:min(c + w, SIZE)] = int(rng.integers(1, 10))
    return grid


def make_task(rng, depth, tier, split, control=None):
    while True:
        if control == "identity":
            program = ()
        elif control == "rotation":
            program = (("d4", 1),)
        elif control == "colour":
            program = (("colour", 0, *map(int, rng.permutation(np.arange(1, 10)))),)
        else:
            program = sample_program(rng, depth, tier)
        # Singleton crop/gravity cannot be held out as compositions while also
        # being trained. Depth1 irreversible is explicitly an input-heldout
        # primitive control; depth2+ retains program-disjoint evaluation.
        if control in ("identity", "rotation") or (tier == "irreversible" and depth == 1) or operator_split(program, tier) == split:
            break
    pairs = []
    for _ in range(4):
        grid = sample_grid(rng, tier)
        pairs.append({"input": grid.tolist(), "output": apply_program(grid, program).tolist()})
    return {"train": pairs[:3], "test": pairs[3:], "program": program, "depth": depth, "tier": tier}


def encode_task(task, leave_out=None):
    features = np.zeros((4 * SIZE * SIZE, 4), np.int32)
    for index, pair in enumerate(task["train"]):
        sl = slice(index * 36, (index + 1) * 36)
        features[sl, 0] = np.asarray(pair["input"]).reshape(-1) if index != leave_out else 10
        features[sl, 1] = np.asarray(pair["output"]).reshape(-1) if index != leave_out else 10
        features[sl, 2] = index
        features[sl, 3] = np.arange(36)
    query = task["test"][0] if leave_out is None else task["train"][leave_out]
    features[-36:, 0] = np.asarray(query["input"]).reshape(-1)
    features[-36:, 1] = 10
    features[-36:, 2] = 3
    features[-36:, 3] = np.arange(36)
    return features, np.asarray(query["output"], np.int32).reshape(-1)


def structural_solver(task):
    candidates, _ = spatial_candidates()
    inputs = np.array([p["input"] for p in task["train"]]).reshape(3, 36)
    outputs = np.array([p["output"] for p in task["train"]]).reshape(-1)
    query = np.asarray(task["test"][0]["input"]).reshape(-1)
    predictions, consistent, missing = [], 0, 0
    for spatial in candidates:
        source = inputs[:, spatial].reshape(-1)
        counts = np.bincount(source * 10 + outputs, minlength=100).reshape(10, 10)
        seen = counts > 0
        # Colours preserve background and act bijectively.
        if np.any(seen.sum(1) > 1) or np.any(seen.sum(0) > 1) or np.any(seen[0, 1:]) or np.any(seen[1:, 0]):
            continue
        consistent += 1
        mapping = counts.argmax(1)
        mapping[0] = 0
        unknown = np.flatnonzero((counts.sum(1) == 0) & (np.arange(10) != 0))
        available = sorted(set(range(1, 10)) - set(mapping[counts.sum(1) > 0]))
        mapping[unknown] = available
        missing = max(missing, len(set(query) & set(unknown)))
        predictions.append(mapping[query[spatial]].reshape(SIZE, SIZE))
    if not predictions:
        return np.zeros((SIZE, SIZE), int), {"consistent_spatial_candidates": 0, "missing_query_colours": 0, "prediction_identifiable": False}
    identical = all(np.array_equal(predictions[0], pred) for pred in predictions[1:])
    return predictions[0], {"consistent_spatial_candidates": consistent, "missing_query_colours": missing,
                           "prediction_identifiable": bool(identical and missing == 0)}


def init_model(key, arm, width=64, layers=2):
    keys = iter(jax.random.split(key, 10 + 8 * layers))
    def matrix(a, b, scale=1):
        return jax.random.normal(next(keys), (a, b)) * scale / math.sqrt(a)
    params = {"input": matrix(11, width), "output": matrix(11, width), "role": matrix(4, width),
              "position": matrix(36, width), "head": matrix(width, 10), "head_bias": jnp.zeros(10), "layers": []}
    for _ in range(layers):
        layer = {"qkv": matrix(width, 3 * width), "out": matrix(width, width, 1 / math.sqrt(2 * layers)),
                 "ff1": matrix(width, 4 * width), "ff2": matrix(4 * width, width, 1 / math.sqrt(2 * layers)),
                 "norm1": jnp.ones(width), "norm2": jnp.ones(width)}
        # Draw these for both arms, preserving exactly identical shared weights.
        vectors = matrix(width, 4 * 2 * 4)
        group_out = matrix(4 * 4 * 4, width, 0.1 / math.sqrt(layers))
        if arm == "hybrid":
            layer.update(vectors=vectors, group_out=group_out)
        params["layers"].append(layer)
    return params


def rms(x, scale):
    return x * jax.lax.rsqrt(jnp.mean(x * x, axis=-1, keepdims=True) + 1e-5) * scale


def forward(params, features, arm):
    x = (params["input"][features[..., 0]] + params["output"][features[..., 1]]
         + params["role"][features[..., 2]] + params["position"][features[..., 3]])
    b, t, d = x.shape
    for layer in params["layers"]:
        norm = rms(x, layer["norm1"])
        q, k, v = jnp.split(norm @ layer["qkv"], 3, axis=-1)
        q, k, v = (z.reshape(b, t, 4, d // 4).transpose(0, 2, 1, 3) for z in (q, k, v))
        weights = jax.nn.softmax(jnp.einsum("bhtd,bhsd->bhts", q, k) / math.sqrt(d // 4), -1)
        attended = jnp.einsum("bhts,bhsd->bhtd", weights, v).transpose(0, 2, 1, 3).reshape(b, t, d)
        x = x + attended @ layer["out"]
        if arm == "hybrid":
            vectors = (norm @ layer["vectors"]).reshape(b, t, 4, 2, 4)
            transitions = householder_products(vectors)
            prefix = matrix_prefix(transitions)
            x = x + prefix.reshape(b, t, 64) @ layer["group_out"]
        x = x + jax.nn.gelu(rms(x, layer["norm2"]) @ layer["ff1"]) @ layer["ff2"]
    return rms(x[:, -36:], jnp.ones(d)) @ params["head"] + params["head_bias"]


def loss(params, features, labels, arm):
    return optax.softmax_cross_entropy_with_integer_labels(forward(params, features, arm), labels).mean()


def task_arrays(tasks):
    encoded = [encode_task(task) for task in tasks]
    return np.stack([p[0] for p in encoded]), np.stack([p[1] for p in encoded])


@lru_cache(None)
def evaluation_functions(arm, ttt_steps, ttt_lr):
    predict = jax.jit(partial(forward, arm=arm))
    optimizer = optax.adam(ttt_lr)
    # Each vmapped task starts from the same frozen pretrained parameters;
    # optimizer/state never pass between tasks. Only demo labels enter adaptation.
    def adapt_one(base, demo_x, demo_y, query_x):
        initial = optimizer.init(base)
        def step(carry, _):
            model, state = carry
            grads = jax.grad(loss)(model, demo_x, demo_y, arm)
            updates, state = optimizer.update(grads, state, model)
            return (optax.apply_updates(model, updates), state), None
        (model, _), _ = jax.lax.scan(step, (base, initial), None, length=ttt_steps)
        return forward(model, query_x[None], arm)[0]
    adapt = jax.jit(jax.vmap(adapt_one, in_axes=(None, 0, 0, 0)))
    return predict, adapt


def evaluate(params, tasks, arm, ttt_steps=16, ttt_lr=1e-3, eval_batch=8, return_predictions=False):
    predict, adapt = evaluation_functions(arm, ttt_steps, ttt_lr)
    before, after, targets = [], [], []
    for offset in range(0, len(tasks), eval_batch):
        batch = tasks[offset:offset + eval_batch]
        x, y = task_arrays(batch)
        raw_pre = np.asarray(predict(params, jnp.asarray(x)))
        if not np.isfinite(raw_pre).all():
            raise FloatingPointError("Non-finite evaluation logits before test-time training")
        pre = raw_pre.argmax(-1)
        if ttt_steps:
            adapted = [[encode_task(task, leave_out=i) for i in range(3)] for task in batch]
            dx = np.array([[pair[0] for pair in task] for task in adapted])
            dy = np.array([[pair[1] for pair in task] for task in adapted])
            raw_post = np.asarray(adapt(params, jnp.asarray(dx), jnp.asarray(dy), jnp.asarray(x)))
            if not np.isfinite(raw_post).all():
                raise FloatingPointError("Non-finite evaluation logits after test-time training")
            post = raw_post.argmax(-1)
        else:
            post = pre.copy()
        before.extend(pre)
        after.extend(post)
        targets.extend(y)
    target = np.array(targets)
    result = {}
    for name, predictions in (("without_ttt", before), ("with_ttt", after)):
        correct = np.array(predictions) == target
        result[name] = {"exact_accuracy": float(correct.all(1).mean()), "cell_accuracy": float(correct.mean()),
                        "n": len(tasks), "exact_correct": int(correct.all(1).sum())}
    if return_predictions:
        result["task_predictions"] = [{"without_ttt": np.asarray(pre).tolist(), "with_ttt": np.asarray(post).tolist(),
                                       "target": np.asarray(tgt).tolist(),
                                       "without_ttt_exact": bool(np.array_equal(pre, tgt)),
                                       "with_ttt_exact": bool(np.array_equal(post, tgt))}
                                      for pre, post, tgt in zip(before, after, targets)]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("softmax", "hybrid"), required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=2500)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--eval-tasks", type=int, default=64, help="Tasks per depth/tier cell")
    parser.add_argument("--train-tasks", type=int, default=8192)
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--layers", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--ttt-steps", type=int, default=16)
    parser.add_argument("--ttt-lr", type=float, default=1e-3)
    parser.add_argument("--control", choices=("identity", "rotation", "colour"))
    parser.add_argument("--out")
    parser.add_argument("--checkpoint")
    args = parser.parse_args()
    started = time.time()
    rng = np.random.default_rng(args.seed)
    train_tasks = [make_task(rng, i % 4 + 1, "invertible" if args.control else TIERS[(i // 4) % 2], "train", args.control)
                   for i in range(args.train_tasks)]
    x, y = task_arrays(train_tasks)
    params = init_model(jax.random.PRNGKey(args.seed), args.arm, args.width, args.layers)
    schedule = optax.cosine_decay_schedule(args.lr, max(args.steps, 1), alpha=0.1)
    optimizer = optax.chain(optax.clip_by_global_norm(1.0), optax.adamw(schedule, weight_decay=1e-4))
    state = optimizer.init(params)
    @jax.jit
    def step(params, state, bx, by):
        value, grads = jax.value_and_grad(loss)(params, bx, by, args.arm)
        updates, state = optimizer.update(grads, state, params)
        return optax.apply_updates(params, updates), state, value
    history = []
    for iteration in range(1, args.steps + 1):
        selected = rng.integers(0, len(x), args.batch)
        params, state, value = step(params, state, x[selected], y[selected])
        if iteration == 1 or iteration % max(1, args.steps // 10) == 0:
            if not np.isfinite(float(value)):
                raise FloatingPointError(f"Non-finite training loss at step {iteration}")
            row = {"step": iteration, "loss": float(value), "elapsed_s": round(time.time() - started, 2)}
            history.append(row)
            print(json.dumps({"progress": row}), flush=True)
    train_prediction = np.asarray(jax.jit(partial(forward, arm=args.arm))(params, x[:128])).argmax(-1)
    train_correct = train_prediction == y[:128]
    result = {"experiment": "algebraic_arc", "config": vars(args), "history": history,
              "parameters": sum(v.size for v in jax.tree_util.tree_leaves(params)),
              "training_diagnostic": {"n": len(train_correct), "cell_accuracy": float(train_correct.mean()),
                                      "exact_accuracy": float(train_correct.all(1).mean())},
              "training_arrays_sha256": hashlib.sha256(x.tobytes() + y.tobytes()).hexdigest(),
              "depth_is_not_intrinsic_difficulty": True,
              "operator_split": "SHA256 canonical affine action modulo5 test=0; irreversible program hash",
              "scores": {}, "environment": {"jax": jax.__version__, "devices": str(jax.devices())}}
    artifact_dir = Path(os.environ["NEXT_ARTIFACT_DIR"]) if "NEXT_ARTIFACT_DIR" in os.environ else None
    if args.checkpoint or artifact_dir:
        checkpoint = Path(args.checkpoint) if args.checkpoint else artifact_dir / "checkpoint.pkl"
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        with checkpoint.open("wb") as handle:
            pickle.dump({"params": jax.device_get(params), "config": vars(args)}, handle)
    eval_rng = np.random.default_rng(10000 + args.seed)
    cells = [("invertible", 1)] if args.control else [(tier, depth) for tier in TIERS for depth in range(1, 5)]
    for tier, depth in cells:
        tasks = [make_task(eval_rng, depth, tier, "test", args.control) for _ in range(args.eval_tasks)]
        score = evaluate(params, tasks, args.arm, args.ttt_steps, args.ttt_lr, return_predictions=True)
        predictions = score.pop("task_predictions")
        score["tasks_sha256"] = hashlib.sha256(json.dumps(tasks, sort_keys=True).encode()).hexdigest()
        if artifact_dir:
            artifact_dir.mkdir(parents=True, exist_ok=True)
            for item, task in zip(predictions, tasks):
                item.update(depth=depth, tier=tier, program=task["program"], task=task)
            (artifact_dir / f"predictions_{tier}_depth{depth}.json").write_text(json.dumps(predictions) + "\n")
        copy_correct = [np.asarray(t["test"][0]["input"]) == np.asarray(t["test"][0]["output"]) for t in tasks]
        score["copy_input_baseline"] = {"exact_accuracy": float(np.mean([c.all() for c in copy_correct])),
                                        "cell_accuracy": float(np.mean(copy_correct))}
        score["primitive_counts"] = {kind: sum(p[0] == kind for task in tasks for p in task["program"])
                                    for kind in ("d4", "translate", "colour", "crop", "gravity", "fill")}
        score["split"] = "input-heldout primitive control" if (tier == "irreversible" and depth == 1) or args.control in ("identity", "rotation") else "operator-heldout"
        if tier == "invertible":
            diagnostics = [operator_diagnostics(task["program"]) for task in tasks]
            solved = [structural_solver(task) for task in tasks]
            score["privileged_family_solver"] = {
                "exact_accuracy": float(np.mean([np.array_equal(answer, task["test"][0]["output"]) for (answer, _), task in zip(solved, tasks)])),
                "identifiable_fraction": float(np.mean([diag["prediction_identifiable"] for _, diag in solved])),
                "mean_consistent_spatial_candidates": float(np.mean([diag["consistent_spatial_candidates"] for _, diag in solved])),
                "mean_missing_query_colours": float(np.mean([diag["missing_query_colours"] for _, diag in solved]))}
            score["operator_diagnostics"] = {
                "effective_factor_count_histogram": np.bincount([d["effective_factor_count"] for d in diagnostics], minlength=4).tolist(),
                "identity_fraction": float(np.mean([d["identity"] for d in diagnostics])),
                "unique_functions": len({d["canonical_id"] for d in diagnostics}),
                "shorter_canonical_description_fraction": float(np.mean([d["effective_factor_count"] < depth for d in diagnostics]))}
        else:
            score["query_unchanged_fraction"] = float(np.mean([np.array_equal(t["test"][0]["input"], t["test"][0]["output"]) for t in tasks]))
        result["scores"][f"{tier}_depth{depth}"] = score
        print(json.dumps({"evaluation": f"{tier}_depth{depth}", "score": score}), flush=True)
    result["elapsed_s"] = round(time.time() - started, 2)
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
