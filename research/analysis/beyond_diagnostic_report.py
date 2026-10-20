"""Reproducible BEYOND diagnostic tables and optional static scientific figures.

    python research/analysis/beyond_diagnostic_report.py \
      --manifest beyond_stage1_initial --manifest beyond_stage1_alternate \
      --selection research/results/stage1_selection.json \
      --confirmation research/results/stage1_confirmation.json \
      --descriptive-manifest beyond_stage1_descriptive \
      --output-dir research/results/diagnostic_report --plots

The input artifacts own every gate decision. This program never selects a rate,
recomputes a pass from displayed scores, launches work, or changes source files.
Missing inputs/results produce an explicitly partial report. Tables use only
the standard library; --plots additionally requires matplotlib.
"""

import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys
import tempfile


RESEARCH = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RESEARCH))
import beyond_protocol as protocol  # noqa: E402 -- standard library only


ARM_ORDER = ("S", "P", "A", "B", "C", "prefix", "GDN1", "DP4", "LLA")
COLORS = {
    "S": "#606b76", "P": "#008d8c", "A": "#d77d27", "B": "#2563a6",
    "C": "#8056a2", "prefix": "#8b6543", "GDN1": "#3b8452", "DP4": "#b94a51",
    "LLA": "#9b7932",
}


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_json(path, sealed=False):
    path = pathlib.Path(path)
    raw = path.read_bytes()
    value = json.loads(raw)
    if sealed and value.get("sha256") != digest({k: v for k, v in value.items() if k != "sha256"}):
        raise ValueError(f"canonical artifact hash mismatch: {path}")
    return value, {"path": str(path), "file_sha256": digest(raw), "artifact_sha256": value.get("sha256")}


def arm_name(args, cfg, settings):
    arch = cfg.get("arch", args.get("arch"))
    if arch == "gated_delta":
        nh = cfg.get("nh", settings.get("nh"))
        beta = cfg.get("beta_max", settings.get("beta_max"))
        return "GDN1" if (nh, beta) == (1, 1) else "DP4" if (nh, beta) == (4, 2) else f"GDN(nh={nh},beta={beta})"
    return {"gpt": "S", "plx": "P", "beyond_a": "A", "beyond_b": "B",
            "beyond_c": "C", "prefix": "prefix", "lla": "LLA"}.get(arch, arch or "?")


def metric_name(task):
    if task.startswith("wp_"):
        return "bal_late"
    return "mse" if task == "regression" else "bal_acc" if task == "gmatch_a5_causal" else "acc"


def normalize_run(manifest, job, result, ledger, descriptive=False):
    args, settings = protocol.parse_argv(job["argv"])
    result = result or {}
    cfg = result.get("config") or {}
    task = args.get("task", "?")
    status = str(ledger.get("status", "pending"))
    issues = []
    if result:
        for field, expected in (("job_id", job["id"]), ("argv", job["argv"]),
                                ("source_hashes", manifest["source_hashes"])):
            if result.get(field) != expected:
                issues.append(f"{field} does not match manifest")
        worker_sources = result.get("source_sha256")
        if worker_sources is not None and any(
            worker_sources.get(n) != manifest["source_hashes"].get(n) for n in protocol.MODEL_SOURCES
        ):
            issues.append("worker model/data source identity does not match manifest")
        if result.get("error"):
            status = "timeout" if any(s in str(result["error"]).lower()
                                      for s in ("timeout", "timed out", "exceeded")) else "error"
        elif result.get("failure") or result.get("nonfinite_fields"):
            status = "invalid"
        else:
            status = "complete"
    elif status in ("complete", "error"):
        issues.append("terminal ledger entry has no result artifact")
    if issues:
        status = "integrity_invalid"
    phase = job.get("protocol", {}).get("phase", "descriptive" if descriptive else "unspecified")
    if descriptive:
        phase = "descriptive"
    return {
        "job_id": job["id"], "manifest": manifest["name"], "manifest_sha256": manifest["sha256"],
        "phase": phase, "status": status, "error": result.get("error") or result.get("failure"),
        "integrity_issues": issues, "task": task, "layers": args.get("layers"),
        "arm": arm_name(args, cfg, settings), "arch": args.get("arch"), "seed": args.get("seed"),
        "lr": args.get("lr"), "metric": metric_name(task),
        "config": cfg or {"cli": args, "settings": settings}, "argv": job["argv"],
        "steps": result.get("steps"), "reference_steps": result.get("reference_steps", args.get("steps")),
        "train_tokens": result.get("train_tokens"), "flops_per_token": result.get("flops_per_token"),
        "target_flops_per_token": result.get("target_flops_per_token", args.get("target_fpt")),
        "train_flops": result.get("train_flops"), "reference_train_flops": result.get("reference_train_flops"),
        "wall_seconds": result.get("wall", result.get("secs")),
        "evalset": result.get("evalset", args.get("evalset")), "testset": result.get("testset", args.get("testset")),
        "validation_seed": result.get("validation_seed"), "test_seed": result.get("test_seed"),
        "validation": result.get("validation"), "test": result.get("test"),
        "model_source_hashes": {n: manifest["source_hashes"].get(n) for n in protocol.MODEL_SOURCES},
        "result_source_sha256": result.get("source_sha256"),
        "prediction_commit": manifest.get("prediction_commit"),
    }


def baseline_summary(value):
    if not value:
        return None
    result = {
        "task": value["task"], "scope_limit": value["scope_limit"],
        "calibration_seed": value["calibration"]["seed"],
        "calibration_sequences": value["calibration"]["sequences"],
        "calibration_positive_prevalence": value["calibration"]["global_positive_prevalence_on_scored_positions"],
        "decision_rules": {rule: value["decision_rules"][rule] for rule in
                           ("position_balanced_accuracy", "position_accuracy")},
        "validation": {}, "test": {},
    }
    for split in ("validation", "test"):
        section = value["evaluation"][split]
        result[split] = {
            "mean_balanced_accuracy": section["seed_mean_balanced_accuracy"]["position_balanced_accuracy"],
            "seed_sample_std_balanced_accuracy": section["seed_sample_std_balanced_accuracy"]["position_balanced_accuracy"],
            "sequences_per_seed": section["sequences_per_seed"],
            "by_seed": {},
            "rules": {},
        }
        for rule in ("position_balanced_accuracy", "position_accuracy"):
            result[split]["rules"][rule] = {
                "mean_balanced_accuracy": section["seed_mean_balanced_accuracy"][rule],
                "pooled_balanced_accuracy": section["pooled"][rule]["bal_acc"],
                "seed_sample_std_balanced_accuracy": section["seed_sample_std_balanced_accuracy"][rule],
                "by_seed": {
                    str(row["seed"]): {
                        "balanced_accuracy": row["metrics"][rule]["bal_acc"],
                        "balanced_accuracy_se_sequences": row["metrics"][rule].get("bal_acc_se_sequences"),
                    } for row in section["by_seed"]
                },
            }
        for row in section["by_seed"]:
            metrics = row["metrics"]["position_balanced_accuracy"]
            result[split]["by_seed"][str(row["seed"])] = {
                "balanced_accuracy": metrics["bal_acc"],
                "balanced_accuracy_se_sequences": metrics.get("bal_acc_se_sequences"),
            }
    return result


def score_row(run, split, baseline=None):
    metrics = run.get(split) if isinstance(run.get(split), dict) else {}
    score = metrics.get(run["metric"])
    valid_score = score if finite(score) else None
    se_key = {"acc": "acc_se_sequences", "mse": "mse_se_examples"}.get(run["metric"])
    se = metrics.get(se_key) if se_key else None
    se = se if finite(se) and se >= 0 else None
    row = {k: run[k] for k in ("job_id", "manifest", "phase", "status", "task", "layers", "arm",
                              "seed", "lr", "steps", "train_tokens", "flops_per_token", "train_flops")}
    row.update(
        split=split, evaluation_seed=run.get(split + "_seed"), metric=run["metric"],
        score=valid_score, score_standard_error=se,
        score_uncertainty_kind=se_key if se is not None else "not_reported",
        all_position_accuracy=metrics.get("acc"),
        all_position_acc_se_sequences=metrics.get("acc_se_sequences"),
        late_accuracy=metrics.get("acc_late"), balanced_late_accuracy=metrics.get("bal_late"),
        late_metric_se_missing=run["task"].startswith("wp_"),
        balanced_accuracy=metrics.get("bal_acc"), mse=metrics.get("mse"),
        mse_se_examples=metrics.get("mse_se_examples"), normalized_mse=metrics.get("normalized_mse"),
        mean_value_baseline_mse=metrics.get("mean_value_baseline_mse"),
        mse_over_mean_value_baseline=metrics.get("mse_over_mean_value_baseline"),
        scored_tokens=metrics.get("scored_tokens"),
        position_baseline_mean_balanced_accuracy=None, position_baseline_same_seed_balanced_accuracy=None,
        position_baseline_same_seed_se=None,
    )
    for rule in ("position_balanced_accuracy", "position_accuracy"):
        row.update({f"{rule}_{field}": None for field in (
            "threshold_rule", "same_seed_balanced_accuracy", "same_seed_se",
            "pooled_balanced_accuracy", "seed_mean_balanced_accuracy")})
    if run["task"] == "gmatch_a5_causal" and baseline:
        comparison = baseline[split]
        same_seed = comparison["by_seed"].get(str(run.get(split + "_seed")), {})
        row.update(position_baseline_mean_balanced_accuracy=comparison["mean_balanced_accuracy"],
                   position_baseline_same_seed_balanced_accuracy=same_seed.get("balanced_accuracy"),
                   position_baseline_same_seed_se=same_seed.get("balanced_accuracy_se_sequences"))
        for rule in ("position_balanced_accuracy", "position_accuracy"):
            values = comparison["rules"][rule]
            matched = values["by_seed"].get(str(run.get(split + "_seed")), {})
            row.update({
                f"{rule}_threshold_rule": baseline["decision_rules"][rule],
                f"{rule}_same_seed_balanced_accuracy": matched.get("balanced_accuracy"),
                f"{rule}_same_seed_se": matched.get("balanced_accuracy_se_sequences"),
                f"{rule}_pooled_balanced_accuracy": values["pooled_balanced_accuracy"],
                f"{rule}_seed_mean_balanced_accuracy": values["mean_balanced_accuracy"],
            })
    return row


def gate_rows(selection, confirmation):
    """Copy decisions verbatim; no scores or display precision determine gates."""
    rows = []
    if selection:
        policies = [("reconciled_written" if selection.get("gate_reconciliation") else "original_strict",
                     selection["seed0_gates"])]
        if selection.get("strict_code_seed0_gates"):
            policies.append(("original_strict", selection["strict_code_seed0_gates"]))
        for policy, gates in policies:
            for arm, candidate in gates.items():
                for name, cell in candidate["cells"].items():
                    task, layer = name.rsplit("/L", 1)
                    rows.append({
                        "artifact": "seed0_selection", "artifact_sha256": selection["sha256"], "gate_policy": policy,
                        "split": "validation", "arm": arm, "task": task, "layers": int(layer), "seed": 0,
                        "status": cell["status"], "score": cell.get("validation"),
                        "reference_arm": cell.get("reference_arm"), "reference_score": cell.get("reference_validation"),
                        "absolute_floor": cell.get("absolute_threshold"), "maximum_gap": cell.get("maximum_reference_gap"),
                        "reference_floor_required": cell.get("reference_floor_required", True),
                        "candidate_job_id": selection["selected"].get(f"{name}/{arm}", {}).get("selected", {}).get("job_id")
                        if selection["selected"].get(f"{name}/{arm}", {}).get("selected") else None,
                        "reference_job_id": selection["references"].get(name, {}).get("selected", {}).get("job_id")
                        if selection["references"].get(name, {}).get("selected") else None,
                    })
    if confirmation:
        policies = [("reconciled_written" if confirmation.get("gate_reconciliation") else "original_strict",
                     confirmation["candidates"])]
        if confirmation.get("gate_reconciliation") and confirmation.get("strict_code_candidates"):
            policies.append(("original_strict", confirmation["strict_code_candidates"]))
        for policy, candidates in policies:
            for arm, candidate in candidates.items():
                for cell in candidate["cells"]:
                    gate, own, reference = cell["gate"], cell["candidate"], cell["reference"]
                    rows.append({
                        "artifact": "stage1_confirmation", "artifact_sha256": confirmation["sha256"],
                        "gate_policy": policy, "reference_floor_required": gate.get("reference_floor_required", True),
                        "split": "test", "arm": arm, "task": cell["task"], "layers": cell["layers"],
                        "seed": cell["seed"], "status": gate["status"], "score": own.get("test_score"),
                        "reference_arm": reference["arm"], "reference_score": reference.get("test_score"),
                        "absolute_floor": gate["floor"], "maximum_gap": gate["maximum_reference_gap"],
                        "candidate_job_id": own.get("job_id"), "reference_job_id": reference.get("job_id"),
                    })
    return rows


def build_report(manifests, descriptive_manifests=(), selection_path=None, confirmation_path=None,
                 results_dir=None, ledger_path=None, baseline_path=None, research_dir=RESEARCH):
    research = pathlib.Path(research_dir)
    folder = pathlib.Path(results_dir or research / "results/beyond_runs")
    ledger_file = pathlib.Path(ledger_path or research / "results/beyond_budget.json")
    ledger, ledger_input = load_json(ledger_file) if ledger_file.exists() else ({}, None)
    selection, selection_input = load_json(selection_path, True) if selection_path else (None, None)
    confirmation, confirmation_input = load_json(confirmation_path, True) if confirmation_path else (None, None)
    if confirmation and (confirmation.get("schema"), confirmation.get("schema_version")) != ("stage1_confirmation", 1):
        raise ValueError("unsupported confirmation artifact")
    if selection and confirmation and confirmation.get("frozen_selection_sha256") != selection["sha256"]:
        raise ValueError("confirmation does not bind the provided frozen selection")
    baseline_file = pathlib.Path(baseline_path or research / "results/beyond_match3_position_baseline.json")
    baseline_raw, baseline_input = load_json(baseline_file) if baseline_file.exists() else (None, None)
    baseline = baseline_summary(baseline_raw)
    runs, seen, manifest_inputs, result_inputs = [], {}, [], []
    for name, descriptive in [(n, False) for n in manifests] + [(n, True) for n in descriptive_manifests]:
        path = pathlib.Path(name)
        if not path.exists():
            path = research / "manifests" / (path.stem + ".json")
        manifest, provenance = load_json(path, True)
        manifest_inputs.append(provenance)
        for job in manifest["jobs"]:
            if job["id"] in seen:
                if seen[job["id"]] != job:
                    raise ValueError("a job ID has conflicting manifest definitions")
                continue
            seen[job["id"]] = job
            result_path = folder / (job["id"] + ".json")
            result, result_input = load_json(result_path) if result_path.exists() else (None, None)
            if result_input:
                result_inputs.append(result_input)
            runs.append(normalize_run(manifest, job, result, ledger.get("jobs", {}).get(job["id"], {}), descriptive))
    runs.sort(key=lambda r: (r["task"], r["layers"] or 0, ARM_ORDER.index(r["arm"]) if r["arm"] in ARM_ORDER else 100,
                             r["seed"] or 0, r["lr"] or 0, r["job_id"]))
    selected_ids = sorted(
        item["selected"]["job_id"] for item in selection["selected"].values() if item.get("selected")
    ) if selection else []
    statuses = []
    for arm in protocol.PRIORITY:
        screen = selection["seed0_gates"].get(arm) if selection else None
        confirmed = confirmation["candidates"].get(arm) if confirmation else None
        statuses.append({
            "arm": arm, "seed0_status": screen["status"] if screen else "artifact_not_supplied",
            "confirmation_status": confirmed["status"] if confirmed else "artifact_not_supplied",
            "confirmation_passed_cells": confirmed.get("confirmation_passed_cells") if confirmed else None,
            "confirmation_required_cells": confirmed.get("confirmation_required_cells") if confirmed else None,
            "budget_deferral": confirmed.get("budget_deferral") if confirmed else None,
            "terminal_closure": confirmed.get("terminal_closure") if confirmed else None,
            "strict_code_seed0_status": selection.get("strict_code_seed0_gates", {}).get(arm, {}).get("status")
            if selection else None,
            "strict_code_confirmation_status": confirmation.get("strict_code_candidates", {}).get(arm, {}).get("status")
            if confirmation else None,
        })
    partial_reasons = []
    pending = [r["job_id"] for r in runs if r["status"] in ("pending", "running", "reserved")]
    if pending:
        partial_reasons.append(f"{len(pending)} supplied-manifest jobs have no terminal result")
    if not selection:
        partial_reasons.append("frozen seed0 selection artifact not supplied; no rate selection inferred")
    elif any(s["seed0_status"] == "pending" for s in statuses):
        partial_reasons.append("seed0 gate decisions are pending")
    if not confirmation:
        partial_reasons.append("independent confirmation artifact not supplied")
    elif any(s["confirmation_status"] == "pending" for s in statuses):
        partial_reasons.append("independent confirmations are pending")
    if not descriptive_manifests:
        partial_reasons.append("mandatory descriptive manifest not supplied")
    missing_selected = sorted(set(selected_ids) - {r["job_id"] for r in runs})
    if missing_selected:
        partial_reasons.append(f"{len(missing_selected)} selected jobs are outside supplied manifests")
    report = {
        "schema": "beyond_diagnostic_report", "schema_version": 1,
        "partial": bool(partial_reasons), "partial_reasons": partial_reasons,
        "runs": runs, "scores": [score_row(r, split, baseline) for r in runs for split in ("validation", "test")],
        "gates": gate_rows(selection, confirmation), "candidate_statuses": statuses,
        "strict_code_seed0_survivors": confirmation.get("strict_code_seed0_survivors") if confirmation else None,
        "selection_supplied": bool(selection), "selected_seed0_job_ids": selected_ids,
        "gate_reconciliation": selection.get("gate_reconciliation") if selection else None,
        "match3_position_baseline": baseline,
        "inputs": {"manifests": manifest_inputs, "results": result_inputs, "ledger": ledger_input,
                   "selection": selection_input, "confirmation": confirmation_input, "position_baseline": baseline_input},
        "reporter_sha256": digest(pathlib.Path(__file__).read_bytes()),
        "notes": [
            "Gate decisions are copied from sealed artifacts. No pass is inferred from rounded or raw report scores.",
            "Validation and test are separate rows/files; only frozen validation-selected IDs choose screen plot points.",
            "Word gate metric is balanced second-half accuracy; all-position accuracy and its SE are separate.",
            "No standard error is invented for balanced late word accuracy or model Match3 balanced accuracy.",
            "Regression error bars, when present, are 1.96 times the reported independent-example MSE standard error.",
            "Position-only Match3 reference is an empirical explanatory control, not an architectural gate or upper bound.",
            "Seed0 held-out plots describe the screen; independent confirmation plots are separately labeled.",
        ],
    }
    report["sha256"] = digest(report)
    return report


def tsv(path, rows, fields):
    with pathlib.Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)
                             if isinstance(v, (dict, list)) else v for k, v in row.items()})


def plot_subset(report, scope):
    rows = [r for r in report["runs"] if r["status"] == "complete"]
    if scope == "confirmation":
        return [r for r in rows if r["phase"] == "confirmation" and r["seed"] in (1, 2, 3)]
    if scope == "descriptive":
        return [r for r in rows if r["phase"] in ("descriptive", "optional_descriptive")]
    rows = [r for r in rows if r["seed"] == 0 and r["phase"] not in ("descriptive", "optional_descriptive")]
    if report["selection_supplied"]:
        rows = [r for r in rows if r["job_id"] in report["selected_seed0_job_ids"]]
    return rows


def make_plots(report, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.16,
                         "svg.hashsalt": report["sha256"]})
    paths = []
    groups = {
        "retrieval": [("mqar_small", 1), ("mqar_small", 2), ("induction_small", 1), ("induction_small", 2)],
        "words": [("wp_a5_16", 1), ("wp_a5_16", 2), ("wp_s5_16", 1), ("wp_s5_16", 2)],
        "match3": [("gmatch_a5_causal", 1), ("gmatch_a5_causal", 2)],
        "regression": [("regression", 1), ("regression", 2)],
    }
    combinations = [
        ("screen", "validation", ("retrieval", "words")),
        ("screen", "test", ("retrieval", "words")),
        ("confirmation", "test", ("retrieval", "words")),
        ("descriptive", "validation", ("retrieval", "match3", "regression")),
        ("descriptive", "test", ("retrieval", "match3", "regression")),
    ]
    for scope, split, names in combinations:
        source = plot_subset(report, scope)
        for name in names:
            cells = groups[name]
            if scope == "descriptive" and name == "retrieval":
                cells = [c for c in cells if c[1] == 1]
            if scope in ("screen", "confirmation") and name == "retrieval":
                cells = [c for c in cells if c[1] == 2]
            if not any((r["task"], r["layers"]) in cells for r in source):
                continue
            fig, axes = plt.subplots(math.ceil(len(cells) / 2), 2, figsize=(11, 3.3 * math.ceil(len(cells) / 2)), squeeze=False)
            for ax, (task, depth) in zip(axes.flat, cells):
                rows = [r for r in source if (r["task"], r["layers"]) == (task, depth)]
                arms = [a for a in ARM_ORDER if any(r["arm"] == a for r in rows)]
                for x, arm in enumerate(arms):
                    own = [r for r in rows if r["arm"] == arm]
                    for n, run in enumerate(own):
                        values = run.get(split) or {}
                        value = values.get(metric_name(task))
                        if not finite(value):
                            continue
                        position = x + (n - (len(own) - 1) / 2) * min(0.09, 0.4 / max(1, len(own)))
                        color = COLORS.get(arm, "#333333")
                        key = "mse_se_examples" if name == "regression" else "acc_se_sequences" if name == "retrieval" else None
                        se = values.get(key) if key else None
                        err = 1.96 * se if finite(se) and se >= 0 else None
                        ax.errorbar(position, value, yerr=err, fmt="o", ms=5, color=color, capsize=2, lw=0.8)
                        if name == "words" and finite(values.get("acc")):
                            ax.plot(position, values["acc"], marker="x", ms=5, color=color, alpha=0.6)
                ax.set_title(f"{task.replace('_small', '').replace('wp_', '').replace('_16', '').replace('_', ' ')} · {depth} layer(s)")
                ax.set_xticks(range(len(arms)), arms)
                ax.set_ylabel("MSE" if name == "regression" else "Balanced accuracy" if name in ("words", "match3") else "Accuracy")
                if name != "regression":
                    ax.set_ylim(-0.025, 1.025)
                    from matplotlib.ticker import PercentFormatter
                    ax.yaxis.set_major_formatter(PercentFormatter(1))
                else:
                    ax.set_ylim(bottom=0)
                if name == "match3" and report["match3_position_baseline"]:
                    comparison = report["match3_position_baseline"][split]
                    seeds = sorted({r.get(split + "_seed") for r in rows if r.get(split + "_seed") is not None})
                    for seed in seeds:
                        for rule, label, style, color in (
                            ("position_balanced_accuracy", "BA rule: pₜ > π", "--", "#303a43"),
                            ("position_accuracy", "Accuracy rule: pₜ > 0.5", ":", "#7a4937"),
                        ):
                            matched = comparison["rules"][rule]["by_seed"].get(str(seed))
                            if matched:
                                base = matched["balanced_accuracy"]
                                ax.axhline(base, ls=style, color=color, lw=1,
                                           label=f"{label} · seed {seed}: {100 * base:.4f}%")
                    ax.legend(loc="lower right", frameon=False)
                if not rows:
                    ax.text(.5, .5, "No completed result", transform=ax.transAxes, ha="center")
            for ax in list(axes.flat)[len(cells):]:
                ax.set_visible(False)
            scope_label = {"screen": "seed-0 screen (not independent confirmation)",
                           "confirmation": "independent seeds 1–3", "descriptive": "fixed-rate descriptive probe"}[scope]
            fig.suptitle(f"{name.title()} · {split.upper()} · {scope_label}" + (" · PARTIAL" if report["partial"] else ""), fontsize=11)
            if name == "words":
                fig.legend(handles=[Line2D([], [], marker="o", color="#333333", linestyle="", label="Balanced second half; SE unavailable"),
                                    Line2D([], [], marker="x", color="#777777", linestyle="", label="All-position accuracy")],
                           loc="lower center", ncol=2, frameon=False)
            elif name == "match3" and report["match3_position_baseline"]:
                rules = report["match3_position_baseline"][split]["rules"]
                ba = rules["position_balanced_accuracy"]["pooled_balanced_accuracy"]
                acc = rules["position_accuracy"]["pooled_balanced_accuracy"]
                fig.text(.5, .015,
                         f"Lines use each model's evaluation seed. Pooled four-seed context only: BA rule {100*ba:.4f}%; "
                         f"accuracy rule {100*acc:.4f}%. Model BA SE unavailable.",
                         ha="center", fontsize=8)
            else:
                fig.text(.5, .015, "Each point is one run. Error bars are 1.96 × reported SE where available.",
                         ha="center", fontsize=8)
            fig.tight_layout(rect=(0, .06, 1, .93))
            stem = f"{scope}_{split}_{name}"
            for extension in ("png", "pdf"):
                path = output / f"{stem}.{extension}"
                metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else {}
                fig.savefig(path, dpi=160, metadata=metadata)
                paths.append(path.name)
            plt.close(fig)
    return {"files": paths, "matplotlib_version": matplotlib.__version__}


def write_report(report, output_dir, plots=False):
    output = pathlib.Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    run_fields = ["job_id", "manifest", "manifest_sha256", "phase", "status", "task", "layers", "arm", "arch",
                  "seed", "lr", "steps", "reference_steps", "train_tokens", "flops_per_token", "target_flops_per_token",
                  "train_flops", "reference_train_flops", "wall_seconds", "evalset", "testset", "config",
                  "model_source_hashes", "prediction_commit", "error", "integrity_issues"]
    tsv(output / "runs.tsv", report["runs"], run_fields)
    score_fields = list(score_row({"job_id": "", "manifest": "", "phase": "", "status": "", "task": "",
                                  "layers": 0, "arm": "", "seed": 0, "lr": 0, "steps": 0, "train_tokens": 0,
                                  "flops_per_token": 0, "train_flops": 0, "metric": "acc"}, "validation"))
    for split in ("validation", "test"):
        tsv(output / f"{split}_scores.tsv", [r for r in report["scores"] if r["split"] == split], score_fields)
    tsv(output / "gates.tsv", report["gates"], [
        "artifact", "artifact_sha256", "gate_policy", "split", "arm", "task", "layers", "seed", "status", "score",
        "reference_arm", "reference_score", "absolute_floor", "maximum_gap", "reference_floor_required",
        "candidate_job_id", "reference_job_id"])
    tsv(output / "candidate_status.tsv", report["candidate_statuses"], [
        "arm", "seed0_status", "strict_code_seed0_status", "confirmation_status", "confirmation_passed_cells",
        "confirmation_required_cells", "strict_code_confirmation_status", "budget_deferral", "terminal_closure"])
    plot_info = make_plots(report, output) if plots else {"files": [], "note": "Plots were not requested."}
    (output / "plots.json").write_text(json.dumps(plot_info, indent=2, sort_keys=True) + "\n")
    return {"output_dir": str(output), "partial": report["partial"], "partial_reasons": report["partial_reasons"],
            "runs": len(report["runs"]), "report_sha256": report["sha256"], "plots": len(plot_info["files"])}


def self_test():
    base = {"job_id": "j", "manifest": "m", "phase": "initial", "status": "complete", "task": "wp_a5_16",
            "layers": 1, "arm": "B", "seed": 0, "lr": .004, "steps": 1, "train_tokens": 1,
            "flops_per_token": 1, "train_flops": 1, "metric": "bal_late",
            "validation": {"acc": .99, "bal_late": .02, "acc_se_sequences": .01}}
    row = score_row(base, "validation")
    assert row["score"] == .02 and row["score_standard_error"] is None
    assert row["all_position_accuracy"] == .99 and row["all_position_acc_se_sequences"] == .01
    reg = {**base, "task": "regression", "metric": "mse", "test": {"mse": .5, "mse_se_examples": .1}}
    assert score_row(reg, "test")["score_standard_error"] == .1
    selection = {"sha256": "fixed", "seed0_gates": {"B": {"cells": {
        "wp_a5_16/L1": {"status": "rejected", "validation": .999999, "reference_validation": .5}}}},
        "selected": {}, "references": {}}
    assert gate_rows(selection, None)[0]["status"] == "rejected"
    dual = {**selection, "gate_reconciliation": {"policy_id": "synthetic"},
            "strict_code_seed0_gates": selection["seed0_gates"]}
    assert [r["gate_policy"] for r in gate_rows(dual, None)] == ["reconciled_written", "original_strict"]
    own = {"arm": "B", "test_score": 1.0, "job_id": "candidate"}
    reference = {"arm": "prefix", "test_score": .94, "job_id": "reference"}
    cell = {"task": "wp_a5_16", "layers": 1, "seed": 1, "candidate": own, "reference": reference,
            "gate": {"status": "passed", "floor": .95, "maximum_reference_gap": .03, "reference_floor_required": False}}
    strict_cell = {**cell, "gate": {**cell["gate"], "status": "reference_failed", "reference_floor_required": True}}
    confirmation = {"sha256": "sealed", "gate_reconciliation": {"policy_id": "synthetic"},
                    "candidates": {"B": {"cells": [cell]}}, "strict_code_candidates": {"B": {"cells": [strict_cell]}}}
    assert [r["status"] for r in gate_rows(None, confirmation)] == ["passed", "reference_failed"]
    low_test = {**base, "job_id": "selected", "test": {"bal_late": 0}}
    high_test = {**base, "job_id": "not_selected", "lr": .008, "test": {"bal_late": 1}}
    report = {"runs": [low_test, high_test], "selection_supplied": True, "selected_seed0_job_ids": ["selected"]}
    assert [r["job_id"] for r in plot_subset(report, "screen")] == ["selected"]
    assert plot_subset({**report, "runs": [{**low_test, "status": "integrity_invalid"}]}, "screen") == []
    actual, _ = load_json(RESEARCH / "results/beyond_match3_position_baseline.json")
    baseline = baseline_summary(actual)
    match = {**base, "task": "gmatch_a5_causal", "metric": "bal_acc", "test_seed": 20000,
             "test": {"bal_acc": .7441780254806138}}
    match_row = score_row(match, "test", baseline)
    assert match_row["position_balanced_accuracy_same_seed_balanced_accuracy"] == .7478241598730433
    assert match_row["position_accuracy_same_seed_balanced_accuracy"] == .7441780254806138
    assert match_row["position_balanced_accuracy_pooled_balanced_accuracy"] == .7484552422577095
    assert match_row["position_balanced_accuracy_seed_mean_balanced_accuracy"] == .7484598329174176
    assert "pi" in match_row["position_balanced_accuracy_threshold_rule"]
    assert "0.5" in match_row["position_accuracy_threshold_rule"]
    assert match_row["score_standard_error"] is None
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "precision.tsv"
        tsv(path, [{"score": .94999999999999}], ["score"])
        assert float(list(csv.DictReader(path.open(), delimiter="\t"))[0]["score"]) == .94999999999999
    return {"passed": True, "checks": ["late/all-position uncertainty separated", "reported MSE uncertainty",
            "gate status never recomputed", "plots follow frozen selection, never test", "invalid runs excluded from plots",
            "TSV preserves unrounded numeric values", "dual policy outcomes copied without gate reinterpretation",
            "actual Match3 artifact separates both matched-seed rules, pooled values, and seed means"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", action="append", default=[])
    parser.add_argument("--descriptive-manifest", action="append", default=[])
    parser.add_argument("--selection", type=pathlib.Path)
    parser.add_argument("--confirmation", type=pathlib.Path)
    parser.add_argument("--results-dir", type=pathlib.Path)
    parser.add_argument("--ledger", type=pathlib.Path)
    parser.add_argument("--position-baseline", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path)
    parser.add_argument("--plots", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2))
        return
    if not args.output_dir or not (args.manifest or args.descriptive_manifest):
        parser.error("--output-dir and at least one manifest are required")
    report = build_report(args.manifest, args.descriptive_manifest, args.selection, args.confirmation,
                          args.results_dir, args.ledger, args.position_baseline)
    print(json.dumps(write_report(report, args.output_dir, args.plots), indent=2))


if __name__ == "__main__":
    main()
