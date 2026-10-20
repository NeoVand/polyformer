"""Reconstruct frozen validation-window positions without corpus contents or inference.

Replay only lm.py's extracted batch sampler against synthetic corpus-position
indices, using the frozen NumPy version, corpus length, seeds and sample sizes.
This describes token-position overlap, not document independence or corrected
standard errors. It never reads training results, losses, or token files.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_seal(value):
    require(value.get("sha256") == digest({k: v for k, v in value.items() if k != "sha256"}),
            "artifact checksum mismatch")


def read_json(path):
    content = Path(path).read_bytes()
    return json.loads(content), digest(content)


class PositionIndices:
    """Represent positions, not token values; produce only requested slices."""

    def __init__(self, length):
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        require(isinstance(item, slice), "position source expects slices")
        start, stop, step = item.indices(self.length)
        return np.arange(start, stop, step, dtype=np.int32)


def audit_sampler(source, context):
    tree = ast.parse(source)
    batches = [node for node in ast.walk(tree)
               if isinstance(node, ast.FunctionDef) and node.name == "batch"]
    require(len(batches) == 1, "ambiguous batch sampler")
    batch = batches[0]
    require([arg.arg for arg in batch.args.args] == ["src", "g", "n"], "sampler signature differs")
    expected = ast.parse(
        "def batch(src, g, n):\n"
        "    i = g.integers(0, len(src) - T - 1, n)\n"
        "    x = np.stack([src[j:j + T + 1] for j in i]).astype(np.int32)\n"
        "    return x[:, :-1], x[:, 1:]\n"
    ).body[0]
    require(ast.dump(batch, include_attributes=False) == ast.dump(expected, include_attributes=False),
            "batch sampler differs from the audited formula")
    assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)]
    def assignment(target):
        found = [node for node in assignments if len(node.targets) == 1
                 and ast.unparse(node.targets[0]) == target]
        require(len(found) == 1, f"ambiguous {target} assignment")
        return found[0]
    vrng = assignment("vrng")
    periodic = assignment("(vx, vy)")
    final = assignment("(bx, by)")
    require(ast.unparse(vrng.value) == "np.random.default_rng(1234)", "periodic generator differs")
    require(ast.unparse(periodic.value) == "batch(val, vrng, cfg.vseqs)", "periodic draw differs")
    require(ast.unparse(final.value) == "batch(val, np.random.default_rng(5678), cfg.vbig)",
            "final draw differs")
    vrng_loads = [node for node in ast.walk(tree) if isinstance(node, ast.Name)
                 and node.id == "vrng" and isinstance(node.ctx, ast.Load)]
    require(len(vrng_loads) == 1 and vrng_loads[0].lineno == periodic.lineno,
            "periodic generator has additional consumption or aliases")
    for name, node in (("vx", periodic), ("vy", periodic), ("bx", final), ("by", final)):
        stores = [n for n in ast.walk(tree) if isinstance(n, ast.Name)
                  and n.id == name and isinstance(n.ctx, ast.Store)]
        require(len(stores) == 1 and stores[0].lineno == node.lineno, f"{name} is reassigned")
    scope = {"np": np, "T": context}
    module = ast.Module(body=[batch], type_ignores=[])
    exec(compile(module, "<frozen lm.py batch sampler>", "exec"), scope)
    return scope["batch"], {
        "batch_line": batch.lineno,
        "batch_source": ast.get_source_segment(source, batch),
        "periodic_generator_line": vrng.lineno,
        "periodic_generator_source": ast.get_source_segment(source, vrng),
        "periodic_draw_line": periodic.lineno,
        "periodic_draw_source": ast.get_source_segment(source, periodic),
        "final_draw_line": final.lineno,
        "final_draw_source": ast.get_source_segment(source, final),
        "rng_consumption": (
            "Periodic generator has exactly one load: its single batch draw immediately "
            "after initialization. Final batch creates its own fresh generator inline. "
            "Training and the seed-4321 repeated-token probe use separate generators."
        ),
        "evaluation_chunking": (
            "Both 1024-window arrays are sampled in one call before scoring. "
            "vb=max(1,min(64,vseqs)//micro)=32; scoring chunks do not redraw windows. "
            "Periodic evaluations and final component ablations reuse their original arrays."
        ),
    }


def replay(batch, length, context, count, seed):
    generator = np.random.default_rng(seed)
    before = digest(generator.bit_generator.state)
    inputs, targets = batch(PositionIndices(length), generator, count)
    after = digest(generator.bit_generator.state)
    starts = inputs[:, 0]
    reference = np.random.default_rng(seed).integers(0, length - context - 1, count)
    require(np.array_equal(starts, reference), "extracted sampler and integer draw disagree")
    require(inputs.shape == targets.shape == (count, context), "unexpected sample shape")
    require(np.array_equal(inputs, starts[:, None] + np.arange(context)[None, :]),
            "input position convention differs")
    require(np.array_equal(targets, starts[:, None] + 1 + np.arange(context)[None, :]),
            "target position convention differs")
    starts = [int(value) for value in starts]
    return starts, {
        "seed": seed, "windows": count, "context": context,
        "bit_generator": type(generator.bit_generator).__name__,
        "integers_output_dtype": str(reference.dtype),
        "rng_state_before_sha256": before, "rng_state_after_sha256": after,
        "starts_in_draw_order": starts, "starts_sha256": digest(starts),
    }


def coverage_segments(starts_by_sample, context, corpus_length):
    """Exact integer-length sweep; count target-position multiplicities in two samples."""
    events = defaultdict(lambda: [0, 0])
    for index, starts in enumerate(starts_by_sample):
        for start in starts:
            events[start + 1][index] += 1
            events[start + context + 1][index] -= 1
    events[0]
    events[corpus_length]
    active, previous, segments = [0, 0], 0, []
    for point, delta in sorted(events.items()):
        if point > previous:
            segments.append((previous, point, active[0], active[1]))
        active[0] += delta[0]
        active[1] += delta[1]
        previous = point
    require(active == [0, 0] and previous == corpus_length, "coverage sweep did not close")
    return segments


def sample_statistics(starts, context, corpus_length, segments, sample_index):
    histogram = Counter()
    for start, end, a, b in segments:
        histogram[(a, b)[sample_index]] += end - start
    total = len(starts) * context
    unique = sum(count for multiplicity, count in histogram.items() if multiplicity)
    repeated_positions = sum(count for multiplicity, count in histogram.items() if multiplicity >= 2)
    pairwise = sum(count * multiplicity * (multiplicity - 1) // 2
                   for multiplicity, count in histogram.items())
    require(sum(histogram.values()) == corpus_length and
            sum(k * v for k, v in histogram.items()) == total, "within-draw accounting mismatch")
    affected = sum(any(i != j and abs(start - other) < context for j, other in enumerate(starts))
                   for i, start in enumerate(starts))
    return {
        "sampled_windows": len(starts), "distinct_starts_and_windows": len(set(starts)),
        "repeated_exact_window_draws": len(starts) - len(set(starts)),
        "scored_target_token_occurrences": total,
        "distinct_target_token_positions": unique,
        "distinct_target_positions_fraction_of_corpus": unique / corpus_length,
        "distinct_target_positions_fraction_of_sampler_reachable_positions": unique / (corpus_length - 2),
        "redundant_target_token_occurrences": total - unique,
        "redundant_occurrences_fraction_of_scored_targets": (total - unique) / total,
        "target_positions_covered_at_least_twice": repeated_positions,
        "target_occurrences_at_positions_covered_at_least_twice": total - histogram.get(1, 0),
        "pairwise_window_target_intersection_sum": pairwise,
        "windows_overlapping_another_window_in_same_draw": affected,
        "target_position_multiplicity_histogram": {str(k): v for k, v in sorted(histogram.items())},
    }


def between_statistics(starts_a, starts_b, context, segments):
    intersection = sum(end - start for start, end, a, b in segments if a and b)
    union = sum(end - start for start, end, a, b in segments if a or b)
    distinct = [sum(end - start for start, end, a, b in segments if (a, b)[i]) for i in (0, 1)]
    occurrences = [
        sum((end - start) * (a, b)[i] for start, end, a, b in segments if a and b)
        for i in (0, 1)
    ]
    pairs = [(a, b) for a in starts_a for b in starts_b if abs(a - b) < context]
    pairwise = sum((end - start) * a * b for start, end, a, b in segments)
    require(pairwise == sum(context - abs(a - b) for a, b in pairs), "cross-draw overlap checks differ")
    return {
        "shared_exact_window_starts": len(set(starts_a) & set(starts_b)),
        "overlapping_window_pairs": len(pairs),
        "periodic_windows_overlapping_any_final_window": sum(any(abs(a - b) < context for b in starts_b)
                                                            for a in starts_a),
        "final_windows_overlapping_any_periodic_window": sum(any(abs(a - b) < context for a in starts_a)
                                                            for b in starts_b),
        "distinct_target_positions_in_both_draws": intersection,
        "distinct_target_positions_in_union": union,
        "intersection_over_union": intersection / union,
        "fraction_of_periodic_distinct_positions_also_in_final": intersection / distinct[0],
        "fraction_of_final_distinct_positions_also_in_periodic": intersection / distinct[1],
        "periodic_target_occurrences_at_positions_covered_by_final": occurrences[0],
        "final_target_occurrences_at_positions_covered_by_periodic": occurrences[1],
        "fraction_of_periodic_target_occurrences_at_positions_covered_by_final": occurrences[0] / (len(starts_a) * context),
        "fraction_of_final_target_occurrences_at_positions_covered_by_periodic": occurrences[1] / (len(starts_b) * context),
        "pairwise_window_target_intersection_sum": pairwise,
    }


def build(plan_path, dataset_path, source_path):
    plan, plan_file_hash = read_json(plan_path)
    dataset, dataset_file_hash = read_json(dataset_path)
    check_seal(plan)
    check_seal(dataset)
    source_bytes = Path(source_path).read_bytes()
    source_hash = digest(source_bytes)
    require(plan["status"] == "frozen", "plan is not frozen")
    require(source_hash == plan["source_hashes"]["lm.py"], "lm.py differs from frozen source")
    require(dataset["sha256"] == plan["dataset_evidence_sha256"]
            and dataset_file_hash == plan["dataset_evidence_file_sha256"],
            "dataset evidence differs from frozen plan")
    require(dataset == plan["dataset_evidence"], "embedded dataset evidence differs")
    require(np.__version__ == plan["runtime_versions"]["numpy"], "NumPy differs from frozen runtime")
    periodic, final = plan["selection_sample"], plan["final_sample"]
    require(periodic == {"seed": 1234, "sequences": 1024, "tokens_per_sequence": 512}
            and final == {"seed": 5678, "sequences": 1024, "tokens_per_sequence": 512},
            "registered sample sizes/seeds differ")
    configs = plan["expected_configs"]["tuning"]
    require(all(cfg["data"] == dataset["worker_data_directory"] and cfg["ctx"] == 512
                and cfg["vseqs"] == 1024 and cfg["micro"] == 2 for cfg in configs.values()),
            "registered data/evaluation configuration differs")
    validation = dataset["files"]["val.bin"]
    length, context = validation["tokens"], periodic["tokens_per_sequence"]
    require(length == 7_514_908 and validation["bytes"] == 2 * length,
            "validation size differs from the registered uint16 corpus")
    batch, source_audit = audit_sampler(source_bytes.decode(), context)
    starts, draws = [], []
    for sample in (periodic, final):
        positions, evidence = replay(batch, length, context, sample["sequences"], sample["seed"])
        starts.append(positions)
        draws.append(evidence)
    segments = coverage_segments(starts, context, length)
    for index in (0, 1):
        draws[index]["coverage"] = sample_statistics(starts[index], context, length, segments, index)
    result = {
        "schema": "beyond_language_window_overlap", "schema_version": 1,
        "status": "exact_frozen_recipe_reconstruction",
        "provenance": {
            "plan_sha256": plan["sha256"], "plan_file_sha256": plan_file_hash,
            "lm_source_sha256": source_hash, "source_hashes": plan["source_hashes"],
            "dataset_evidence_sha256": dataset["sha256"], "dataset_evidence_file_sha256": dataset_file_hash,
            "validation_file_sha256": validation["sha256"], "validation_file_bytes": validation["bytes"],
            "numpy_version": np.__version__, "python_version": sys.version,
            "helper_sha256": digest(Path(__file__).read_bytes()),
        },
        "sampler": {
            "corpus_tokens": length, "context": context, "windows_per_draw": 1024,
            "start_low_inclusive": 0, "start_high_exclusive": length - context - 1,
            "target_interval_half_open": "[start + 1, start + context + 1)",
            "input_interval_half_open": "[start, start + context)",
            "target_positions_reachable_inclusive": [1, length - 2],
            "target_positions_reachable_count": length - 2,
            "indexing": "Zero-based corpus token positions; target coverage, not input-plus-target coverage.",
            "coverage_fraction_denominator": length,
            "scoring_batch_size": 32,
            **source_audit,
        },
        "periodic": draws[0], "final": draws[1],
        "between_draws": between_statistics(starts[0], starts[1], context, segments),
        "scope": [
            "No corpus token bytes, model inference, training results, or losses were read.",
            "Reconstruction is exact for the frozen source, NumPy version, sample sizes and fingerprinted corpus length.",
            "Workers did not store per-window start indices; this is recipe replay, not an empirical audit of saved window IDs.",
            "The same periodic draw is reused across checkpoints, tuning rates, arms and training seeds; the same final draw is reused across arms, training seeds and final ablations.",
            "Different window starts can overlap in target positions. A repeated target position can have a different preceding context or relative position, so its loss need not be identical.",
            "Token-position overlap does not determine document overlap or independence. Disjoint positions can still share a document.",
            "These counts do not estimate effective sample size, corrected standard errors, statistical significance, or selection bias.",
            "Dataset bytes were not rehashed here; the artifact binds the earlier fingerprint and assumes workers used that unchanged corpus.",
        ],
    }
    return {**result, "sha256": digest(result)}


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=root / "results/beyond_language_plan.json")
    parser.add_argument("--dataset", type=Path, default=root / "results/beyond_language_planning/dataset.json")
    parser.add_argument("--lm-source", type=Path, default=root / "lm.py")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.plan, args.dataset, args.lm_source)
    content = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    require(not args.out.exists() or args.out.read_text() == content, "refusing to replace a different artifact")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if not args.out.exists():
        with args.out.open("x") as stream:
            stream.write(content)
    print(json.dumps({key: result[key] for key in ("status", "sha256", "between_draws")}, indent=2))
    print(json.dumps({name: result[name]["coverage"] for name in ("periodic", "final")}, indent=2))


if __name__ == "__main__":
    main()
