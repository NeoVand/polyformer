"""Read BEYOND result artifacts; select learning rates using validation only.

    python research/beyond_summary.py --manifest pilot --manifest screen
    python research/beyond_summary.py --manifest screen --select-rate \
        --selected-json /tmp/selected.json

Every manifest job is shown, including pending calls, failures, and timeouts.
Rate selection considers only successful seed-0 runs and their final validation
metric. The final test result is displayed after selection and never ranks runs.
Model/data source versions and all non-rate protocol settings remain separate.
This program uses only the Python standard library and launches no remote work.
"""

import argparse
import csv
import json
import math
import pathlib
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent
MODEL_SOURCES = ("beyond_diag.py", "beyond_layers.py", "lm.py", "groups.py", "diag.py")


def parse_argv(argv):
    """Read flat --key value arguments, preserving repeated --set settings."""
    values, settings = {}, {}
    i = 0
    while i < len(argv):
        flag = argv[i]
        if not flag.startswith("--"):
            i += 1
            continue
        if "=" in flag:
            name, raw = flag[2:].split("=", 1)
        elif i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            name, raw = flag[2:], argv[i + 1]
            i += 1
        else:
            name, raw = flag[2:], "true"
        if name == "set":
            key, sep, value = raw.partition("=")
            if sep:
                try:
                    settings[key] = json.loads(value)
                except json.JSONDecodeError:
                    settings[key] = value
        else:
            try:
                values[name.replace("-", "_")] = json.loads(raw)
            except json.JSONDecodeError:
                try:
                    values[name.replace("-", "_")] = float(raw)
                except ValueError:
                    values[name.replace("-", "_")] = raw
        i += 1
    return values, settings


def finite(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def classify_status(result, ledger_entry):
    if result is None:
        return str(ledger_entry.get("status", "pending")).upper()
    error = result.get("error")
    if error:
        text = str(error).lower()
        return "TIMEOUT" if any(word in text for word in ("timeout", "timed out", "exceeded")) else "ERROR"
    if result.get("failure") or result.get("nonfinite_fields"):
        return "FAIL"
    return "COMPLETE"


def metric_name(result, task):
    declared = result.get("selection_metric", "")
    if declared.startswith("final_validation_"):
        return declared.removeprefix("final_validation_")
    if task == "regression":
        return "mse"
    if task.startswith("wp_"):
        return "bal_late"
    if task == "gmatch_a5_causal":
        return "bal_acc"
    return "acc"


def normalize_record(job, manifest, result, ledger_entry, path=None):
    result = result or {}
    argv = result.get("argv", job.get("argv", []))
    args, settings = parse_argv(argv)
    cfg = dict(result.get("config") or {})
    task = str(result.get("task", args.get("task", "?")))
    arch = str(result.get("arch", result.get("model", args.get("arch", args.get("model", "?")))))
    name = metric_name(result, task)
    validation = result.get("validation") or {}
    # Legacy diagnostic curves sometimes have only the final validation record.
    if not validation and result.get("curve") and isinstance(result["curve"][-1], dict):
        validation = result["curve"][-1].get("validation") or {}
    test = result.get("test") or {}
    actual_result = result if path is not None else None
    status = classify_status(actual_result, ledger_entry)
    error = result.get("error") or result.get("failure") or ""
    if not error and result.get("nonfinite_fields"):
        error = "nonfinite fields: " + ", ".join(result["nonfinite_fields"])
    source = result.get("source_sha256") or result.get("source_hashes") or manifest.get("source_hashes") or {}
    return {
        "manifest": manifest.get("name", result.get("manifest", "?")),
        "origin_manifest": result.get("manifest", manifest.get("name")),
        "job_id": result.get("job_id", job.get("id", "")),
        "script": result.get("script", job.get("script", "beyond_diag.py")),
        "task": task, "arch": arch,
        "layers": result.get("layers", args.get("layers", cfg.get("layers", 1))),
        "seed": result.get("seed", args.get("seed", 0)),
        "lr": result.get("lr", args.get("lr")),
        "opt": result.get("opt", args.get("opt", "muon")),
        "config": cfg, "settings": settings, "args": args, "argv": argv,
        "metric": name, "validation_score": validation.get(name), "test_score": test.get(name),
        "validation": validation, "test": test,
        "steps": result.get("steps"), "reference_steps": result.get("reference_steps", args.get("steps", 6000)),
        "batch": result.get("batch", args.get("batch", 64)),
        "flops_per_token": result.get("flops_per_token"), "train_flops": result.get("train_flops"),
        "target_flops_per_token": result.get("target_flops_per_token", args.get("target_fpt")),
        "wall": result.get("wall", result.get("secs")), "status": status, "error": str(error),
        "gpu": result.get("gpu_requested", job.get("gpu", ledger_entry.get("gpu"))),
        "max_seconds": job.get("max_seconds"), "attempt": job.get("attempt", 0),
        "prediction_commit": result.get("prediction_commit", manifest.get("prediction_commit")),
        "model_source_hashes": {key: source[key] for key in MODEL_SOURCES if key in source},
        "result_file": str(path) if path is not None else None,
    }


def load_records(results_dir, manifest_dir, ledger_path, selected_manifests=()):
    wanted = {pathlib.Path(name).stem for name in selected_manifests}
    results, paths, manifests = {}, {}, {}
    for path in sorted(pathlib.Path(results_dir).glob("*.json")):
        value = json.loads(path.read_text())
        job_id = value.get("job_id", path.stem)
        if job_id in results:
            raise ValueError(f"duplicate result for job {job_id}")
        results[job_id], paths[job_id] = value, path
    for path in sorted(pathlib.Path(manifest_dir).glob("*.json")):
        value = json.loads(path.read_text())
        if "jobs" in value and "name" in value:
            manifests[value["name"]] = value
    ledger = json.loads(pathlib.Path(ledger_path).read_text()) if pathlib.Path(ledger_path).exists() else {}
    entries = ledger.get("jobs", {})
    records, covered = [], set()
    for name, manifest in manifests.items():
        if wanted and name not in wanted:
            continue
        for job in manifest["jobs"]:
            job_id = job["id"]
            records.append(normalize_record(job, manifest, results.get(job_id), entries.get(job_id, {}), paths.get(job_id)))
            covered.add(job_id)
    for job_id, result in results.items():
        if job_id in covered or (wanted and result.get("manifest") not in wanted):
            continue
        manifest = manifests.get(result.get("manifest"), {"name": result.get("manifest", "?")})
        records.append(normalize_record({"id": job_id}, manifest, result, entries.get(job_id, {}), paths[job_id]))
    known = set(manifests) | {row.get("manifest") for row in results.values()}
    missing = wanted - known
    if missing:
        raise ValueError("unknown manifest name(s): " + ", ".join(sorted(missing)))
    return records


def selection_group(record):
    """Retain architecture variants and compute/data protocol; remove only LR."""
    cfg = dict(record["config"])
    cfg.pop("lr", None)
    cfg.pop("seed", None)
    args = record["args"]
    return {
        "task": record["task"], "arch": record["arch"], "layers": record["layers"],
        "config": cfg, "settings": record["settings"],
        "opt": record["opt"], "wd": args.get("wd", 0.1),
        "reference_steps": record["reference_steps"], "batch": record["batch"],
        "target_fpt": record.get("target_flops_per_token", args.get("target_fpt")),
        "equal_flops": sorted(str(args.get("equal_flops", "")).split(",")),
        "evalset": args.get("evalset", 1024), "evallen": args.get("evallen", 0),
        "metric": record["metric"], "model_source_hashes": record["model_source_hashes"],
    }


def select_rates(records):
    groups = {}
    # Duplicate references to one remote job cannot add evidence or win a tie.
    seen = set()
    for record in records:
        if record["job_id"] in seen:
            continue
        seen.add(record["job_id"])
        if record["seed"] != 0 or record["status"] != "COMPLETE" or not finite(record["validation_score"]):
            continue
        key = json.dumps(selection_group(record), sort_keys=True, separators=(",", ":"))
        groups.setdefault(key, []).append(record)
    selected = []
    for key, candidates in groups.items():
        low_is_good = candidates[0]["metric"] in ("mse", "normalized_mse", "loss", "nll")
        def rank(record):
            score = record["validation_score"] if low_is_good else -record["validation_score"]
            rate = record["lr"] if finite(record["lr"]) else math.inf
            return score, rate, record["job_id"]
        winner = dict(min(candidates, key=rank))
        winner["selected_by"] = "minimum final validation" if low_is_good else "maximum final validation"
        winner["tested_rates"] = sorted({r["lr"] for r in candidates if finite(r["lr"])})
        winner["selection_group"] = json.loads(key)
        selected.append(winner)
    return selected


def variant_label(record):
    cfg = {**record["settings"], **record["config"]}
    if record["arch"] == "gated_delta":
        names = ("nh", "beta_max", "conv_width", "beta0", "decay_bias")
    elif record["arch"] in ("beyond_a", "beyond_b", "beyond_c", "prefix"):
        names = ("gdim", "gheads", "group_nh", "group_order", "branch_scale", "path_scale", "context_scale", "ablate")
    elif record["arch"] == "lla":
        names = ("chart",)
    else:
        names = ("plx_norm",) if cfg.get("plx_norm") else ()
    return ",".join(f"{key}={cfg[key]}" for key in names if key in cfg)


def number(value, digits=6):
    return f"{value:.{digits}g}" if finite(value) else "-"


def sorted_records(records):
    return sorted(records, key=lambda r: (
        r["task"], r["arch"], str(r["layers"]), variant_label(r), str(r["seed"]),
        r["lr"] if finite(r["lr"]) else math.inf, r["manifest"], r["job_id"],
    ))


def print_table(records, error_limit=160):
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(("manifest", "task", "arch", "L", "seed", "lr", "variant", "metric", "validation",
                     "final_test", "steps", "flops/token", "train_TFLOPs", "wall_s", "status", "error"))
    for row in sorted_records(records):
        error = " ".join(row["error"].split())
        if error_limit > 0 and len(error) > error_limit:
            error = error[:error_limit - 1] + "…"
        writer.writerow((
            row["manifest"], row["task"], row["arch"], row["layers"], row["seed"], number(row["lr"]),
            variant_label(row), row["metric"], number(row["validation_score"]), number(row["test_score"]),
            row["steps"] if row["steps"] is not None else "-", number(row["flops_per_token"]),
            number(row["train_flops"] / 1e12 if finite(row["train_flops"]) else None),
            number(row["wall"], 5), row["status"], error,
        ))


def export_selection(path, selected):
    keep = ("task", "arch", "layers", "seed", "lr", "opt", "config", "settings", "argv",
            "script", "gpu", "max_seconds", "manifest", "job_id", "prediction_commit",
            "metric", "validation_score", "test_score", "test", "steps", "reference_steps",
            "batch", "flops_per_token", "target_flops_per_token", "train_flops", "selected_by", "tested_rates",
            "selection_group", "result_file")
    payload = [{key: row[key] for key in keep} for row in sorted_records(selected)]
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(target)


def self_test():
    def row(job, val, test, *, seed=0, nh=4, metric="acc", status="COMPLETE"):
        return {
            "job_id": job, "manifest": "fixture", "task": "regression" if metric == "mse" else "mqar_small",
            "arch": "gated_delta", "layers": 2, "seed": seed, "lr": 0.002,
            "config": {"nh": nh}, "settings": {}, "args": {}, "opt": "muon",
            "reference_steps": 6000, "batch": 64, "metric": metric,
            "validation_score": val, "test_score": test, "status": status,
            "model_source_hashes": {},
        }
    selected = select_rates([
        row("best-test", .8, .99), row("best-val", .9, .1),
        row("seed-one", 1., 1., seed=1), row("failure", 1., 1., status="FAIL"),
        row("variant", .7, .7, nh=1),
        row("regression-low-val", .1, 100., metric="mse"),
        row("regression-low-test", .2, .01, metric="mse"),
    ])
    assert {r["job_id"] for r in selected} == {"best-val", "variant", "regression-low-val"}
    small_budget = row("small-budget", .8, .9)
    large_budget = row("large-budget", .9, .8)
    small_budget["args"]["target_fpt"] = 500_000
    large_budget["args"]["target_fpt"] = 700_000
    assert len(select_rates([small_budget, large_budget])) == 2
    assert classify_status({"error": "subprocess exceeded 900 seconds"}, {}) == "TIMEOUT"
    assert classify_status({"failure": "nonfinite_parameters"}, {}) == "FAIL"
    assert classify_status(None, {"status": "running"}) == "RUNNING"
    args, settings = parse_argv(["--seed", "0", "--lr", ".004", "--set", "nh=1", "--set", "ablate=precision"])
    assert args == {"seed": 0, "lr": .004} and settings == {"nh": 1, "ablate": "precision"}
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        (root / "manifests").mkdir()
        (root / "results").mkdir()
        spec = {"name": "fixture", "jobs": [
            {"id": "done", "argv": ["--task", "mqar_small", "--arch", "gpt", "--seed", "0"]},
            {"id": "running", "argv": ["--task", "regression", "--arch", "lla"]},
        ]}
        (root / "manifests" / "fixture.json").write_text(json.dumps(spec))
        (root / "results" / "done.json").write_text(json.dumps({
            "job_id": "done", "manifest": "fixture", "validation": {"acc": .9}, "test": {"acc": .8},
        }))
        (root / "ledger.json").write_text(json.dumps({"jobs": {"running": {"status": "running"}}}))
        records = load_records(root / "results", root / "manifests", root / "ledger.json", ["fixture"])
        assert {r["status"] for r in records} == {"COMPLETE", "RUNNING"}
        assert select_rates(records)[0]["test_score"] == .8
    print("PASS: validation-only selection, variant separation, seed filtering, failure labels, and pending jobs")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", action="append", default=[], help="repeat to include multiple manifest names")
    parser.add_argument("--results-dir", type=pathlib.Path, default=ROOT / "results" / "beyond_runs")
    parser.add_argument("--manifest-dir", type=pathlib.Path, default=ROOT / "manifests")
    parser.add_argument("--ledger", type=pathlib.Path, default=ROOT / "results" / "beyond_budget.json")
    parser.add_argument("--select-rate", action="store_true")
    parser.add_argument("--selected-json", type=pathlib.Path)
    parser.add_argument("--error-limit", type=int, default=160, help="0 prints complete error text")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.selected_json and not args.select_rate:
        parser.error("--selected-json requires --select-rate")
    try:
        records = load_records(args.results_dir, args.manifest_dir, args.ledger, args.manifest)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    shown = select_rates(records) if args.select_rate else records
    print_table(shown, args.error_limit)
    if args.selected_json:
        export_selection(args.selected_json, shown)
    counts = {}
    for row in records:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    suffix = f"; selected {len(shown)} seed-0 rates using final validation only" if args.select_rate else ""
    print(f"{len(records)} manifest jobs: {json.dumps(counts, sort_keys=True)}{suffix}", file=sys.stderr)
    if args.select_rate and any(status != "COMPLETE" for status in counts):
        print("Selection is provisional while jobs are unfinished or failed; excluded jobs remain visible without --select-rate.", file=sys.stderr)


if __name__ == "__main__":
    main()
