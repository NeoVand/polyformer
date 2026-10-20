r"""Describe completed language learning curves without selecting runs or checkpoints.

Run only after the production reporter audits all six arms and three final seeds:
  python research/analysis/beyond_language_dynamics.py \
    --report research/results/beyond_language_report/report.json \
    --plan research/results/beyond_language_plan.json \
    --results-dir research/results/beyond_runs \
    --output-dir research/results/beyond_language_dynamics

Periodic raw validation loss uses seed 1234. Final gates use a separate sample,
seed 5678, and are neither recomputed nor inferred here. Means and sample SDs
use three training seeds at each arm's own 16 observed scheduled marks. No
resampling, interpolation, smoothing, checkpoint selection, or rate selection
is performed. Lines in the figures merely connect observed summary points.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import sys


ARMS = ("rawS", "convS", "convP", "B", "GDN1", "DP4")
SEEDS = (1, 2, 3)
MARKS = 16
PERIODIC_SAMPLE = {"seed": 1234, "sequences": 1024, "tokens_per_sequence": 512}
FINAL_SAMPLE = {"seed": 5678, "sequences": 1024, "tokens_per_sequence": 512}
COLORS = {
    "rawS": "#6b7280", "convS": "#0072b2", "convP": "#d55e00",
    "B": "#111827", "GDN1": "#009e73", "DP4": "#a35ca6",
}
NOTES = {
    "purpose": "Posthoc descriptive trajectories only; no gate, rate, checkpoint, or run selection.",
    "loss": "Raw periodic validation cross-entropy, nats/token, on the fixed seed-1234 sample.",
    "uncertainty": (
        "Mean plus/minus sample SD across three independently trained seeds at each "
        "arm's own observed evaluation marks. This is not sequence SE, a confidence "
        "interval, or a significance test; n=3 provides limited information."
    ),
    "schedule": (
        "Each arm is summarized only at its own 16 scheduled observations. No "
        "resampling, interpolation, or smoothing is used in the summaries. Lines "
        "connect observations. Arms have different step, token, and compute budgets."
    ),
    "compute": (
        "Cumulative nominal modeled training FLOPs = tokens times frozen nominal "
        "training FLOPs/token. This is not measured GPU-executed work; it excludes "
        "the extra operations modeled by the separate source-upper and "
        "rematerialization-sensitive counters. Control update schedules already "
        "include their frozen prospective allowance. These curves do not establish "
        "equal-compute gates."
    ),
    "final_gate": (
        "The separate audited production report alone carries final gate outcomes "
        "from seed-5678 evaluation. Periodic seed-1234 curves never replace them."
    ),
}


class DynamicsError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise DynamicsError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def close(a, b):
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-12, abs_tol=0)


def digest(value, *, allow_nan=False):
    content = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=allow_nan
    ).encode()
    return hashlib.sha256(content).hexdigest()


def seal(value):
    unsealed = {k: v for k, v in value.items() if k != "sha256"}
    return {**unsealed, "sha256": digest(unsealed)}


def check_seal(value, label):
    require(isinstance(value, dict), f"{label}: expected an object")
    require(value.get("sha256") == digest({k: v for k, v in value.items() if k != "sha256"}),
            f"{label}: artifact checksum mismatch")


def read_json(path):
    content = Path(path).read_bytes()
    return json.loads(content), digest(content)


def validate_completed_report(report, plan):
    """Reject incomplete coverage before opening any raw result or curve."""
    check_seal(report, "production report")
    check_seal(plan, "frozen plan")
    require((report.get("schema"), report.get("schema_version")) ==
            ("beyond_language_final_report", 1), "unsupported production report schema")
    require((plan.get("schema"), plan.get("schema_version"), plan.get("status")) ==
            ("beyond_language_plan", 1, "frozen"), "expected a frozen language plan")
    require(report.get("plan_sha256") == plan["sha256"], "report/plan identity mismatch")
    require(report.get("source_hashes") == plan.get("source_hashes") and plan.get("source_hashes"),
            "report/plan source identity mismatch")
    require(report.get("source_bridge_sha256") == plan.get("source_bridge_sha256"),
            "report/plan source bridge mismatch")
    require(report.get("stage1_confirmation_sha256") == plan.get("stage1_confirmation_sha256"),
            "report/plan Stage-1 confirmation mismatch")
    for key in ("dataset_evidence_sha256", "dataset_evidence_file_sha256"):
        require(report.get(key) == plan.get(key) and plan.get(key),
                f"report/plan {key} differs")
    require(plan.get("selection_sample") == PERIODIC_SAMPLE, "periodic sample identity differs")
    require(plan.get("final_sample") == FINAL_SAMPLE and report.get("final_sample") == FINAL_SAMPLE,
            "final sample identity differs")
    require(plan.get("final_seeds") == list(SEEDS), "expected final training seeds 1, 2, 3")
    require(plan.get("arm_order") == list(ARMS), "expected the frozen six-arm plan")
    require(report.get("original_arm_order") == list(ARMS)
            and report.get("final_arm_order") == list(ARMS),
            "complete six-arm report required; reduced grids are not silently summarized")
    require(report.get("accounting", {}).get("arm_plan") == plan.get("arms"),
            "audited accounting differs from the frozen plan")
    coverage = report.get("coverage", {})
    require(all(coverage.get(k) == 18 for k in ("expected_runs", "original_arm_seed_cells", "complete"))
            and all(coverage.get(k) == 0 for k in ("pending", "invalid", "tuning_invalid", "tuning_blocked")),
            "all 18 final runs must be audited complete before any dynamics analysis")
    rows = report.get("runs")
    require(isinstance(rows, list) and len(rows) == 18, "expected exactly 18 audited run records")
    expected = {(arm, seed) for arm in ARMS for seed in SEEDS}
    seen, jobs = {}, set()
    for row in rows:
        require(isinstance(row, dict), "malformed audited run")
        cell = (row.get("arm"), row.get("seed"))
        require(integer(row.get("seed")) and cell in expected and cell not in seen,
                "unexpected or duplicated arm/seed cell")
        require(row.get("status") == "complete", f"{cell}: final run is not audited complete")
        job = row.get("job_id")
        require(isinstance(job, str) and job and Path(job).name == job
                and "/" not in job and "\\" not in job and job not in jobs,
                f"{cell}: invalid or duplicated job id")
        require(isinstance(row.get("result_content_sha256"), str)
                and len(row["result_content_sha256"]) == 64, f"{cell}: missing audited result hash")
        require(row.get("manifest_sha256") in report.get("manifest_sha256s", []),
                f"{cell}: manifest is not bound to the production report")
        seen[cell] = row
        jobs.add(job)
    require(set(seen) == expected, "missing final arm/seed cells")
    return seen


def collect_curves(report, plan, results_dir):
    audited = validate_completed_report(report, plan)
    raw, inputs = [], []
    for arm in ARMS:
        info = plan["arms"][arm]
        for seed in SEEDS:
            row = audited[(arm, seed)]
            job = row["job_id"]
            path = Path(results_dir) / f"{job}.json"
            require(path.is_file(), f"{job}: missing raw final result")
            result, file_hash = read_json(path)
            require(digest(result, allow_nan=True) == row["result_content_sha256"],
                    f"{job}: result content differs from the audited production report")
            require(result.get("job_id") == job and result.get("seed") == seed,
                    f"{job}: run identity differs")
            require(result.get("source_hashes") == plan["source_hashes"],
                    f"{job}: frozen source mismatch")
            require(result.get("manifest_sha256") == row["manifest_sha256"],
                    f"{job}: manifest mismatch")
            require(result.get("stage") == "language" and result.get("script") == "lm.py",
                    f"{job}: expected a language run")
            cfg = result.get("config")
            require(isinstance(cfg, dict), f"{job}: missing full run config")
            require(cfg.get("seed") == seed and cfg.get("steps") == info["main_steps"]
                    and cfg.get("steps") == row["steps"], f"{job}: training schedule differs")
            require(cfg.get("evals") == MARKS and cfg.get("early") == 0
                    and cfg.get("early_until") == 0, f"{job}: expected 16 regular marks without early extras")
            require(cfg.get("vseqs") == PERIODIC_SAMPLE["sequences"]
                    and cfg.get("ctx") == PERIODIC_SAMPLE["tokens_per_sequence"],
                    f"{job}: periodic evaluation shape differs")
            require(integer(cfg.get("batch")) and cfg["batch"] > 0, f"{job}: invalid training batch")
            require(cfg.get("lr") == row.get("selected_rate")
                    and cfg["lr"] == report["selected_rates"][arm]["lr"], f"{job}: selected rate differs")
            require(close(result.get("train_flops_per_token"), info["training_fpt"])
                    and close(row.get("training_flops_per_token"), info["training_fpt"]),
                    f"{job}: nominal per-token compute differs")
            require(result.get("tokens") == info["main_tokens"] == row.get("tokens")
                    and close(result.get("train_flops"), info["main_training_flops"])
                    and close(row.get("training_flops"), info["main_training_flops"]),
                    f"{job}: final nominal accounting differs")
            curve = result.get("curve")
            require(isinstance(curve, list) and len(curve) == MARKS,
                    f"{job}: exactly 16 raw curve records required")
            expected_marks = sorted({max(1, round(cfg["steps"] * (i + 1) / MARKS)) for i in range(MARKS)})
            require(len(expected_marks) == MARKS
                    and [entry.get("step") for entry in curve] == expected_marks,
                    f"{job}: curve steps differ from the frozen schedule")
            config_hash = digest(cfg)
            for index, entry in enumerate(curve, start=1):
                step = entry["step"]
                tokens = step * cfg["batch"] * cfg["ctx"]
                work = tokens * info["training_fpt"]
                require(integer(step) and integer(entry.get("tokens")) and entry["tokens"] == tokens,
                        f"{job} mark {index}: token accounting differs")
                require(close(entry.get("flops"), work), f"{job} mark {index}: nominal FLOPs differ")
                require(finite(entry.get("val_raw")) and entry["val_raw"] >= 0,
                        f"{job} mark {index}: missing/nonfinite raw periodic validation loss")
                raw.append({
                    "arm": arm, "training_seed": seed, "job_id": job,
                    "manifest_sha256": row["manifest_sha256"],
                    "result_content_sha256": row["result_content_sha256"],
                    "config_sha256": config_hash, "selected_rate": cfg["lr"],
                    "mark_index": index, "scheduled_fraction": index / MARKS,
                    "actual_step_fraction": step / cfg["steps"],
                    "step": step, "total_steps": cfg["steps"], "tokens": tokens,
                    "nominal_training_flops": entry["flops"],
                    "nominal_training_flops_per_token": info["training_fpt"],
                    "validation_loss_raw": entry["val_raw"],
                    "validation_seed": PERIODIC_SAMPLE["seed"],
                    "validation_sequences": cfg["vseqs"],
                    "validation_tokens_per_sequence": cfg["ctx"],
                })
            require(curve[-1]["val_raw"] == result.get("val_loss_raw"),
                    f"{job}: periodic endpoint differs from its raw result field")
            inputs.append({
                "arm": arm, "training_seed": seed, "job_id": job,
                "result_file": path.name, "result_file_sha256": file_hash,
                "result_content_sha256": row["result_content_sha256"],
                "manifest_sha256": row["manifest_sha256"], "manifest": result.get("manifest"),
                "config_sha256": config_hash, "selected_rate": cfg["lr"],
                "steps": cfg["steps"], "tokens": info["main_tokens"],
                "nominal_training_flops_per_token": info["training_fpt"],
                "nominal_training_flops": info["main_training_flops"],
            })
    return raw, inputs


def summarize(raw):
    summaries = {}
    for arm in ARMS:
        observations = []
        for mark in range(1, MARKS + 1):
            rows = [row for row in raw if row["arm"] == arm and row["mark_index"] == mark]
            require(len(rows) == 3 and {row["training_seed"] for row in rows} == set(SEEDS),
                    f"{arm} mark {mark}: complete three-seed sample required")
            for key in ("step", "total_steps", "tokens", "nominal_training_flops",
                        "scheduled_fraction", "actual_step_fraction"):
                require(all(row[key] == rows[0][key] for row in rows),
                        f"{arm} mark {mark}: seeds have different observation coordinates")
            losses = [row["validation_loss_raw"] for row in rows]
            observations.append({
                **{key: rows[0][key] for key in (
                    "mark_index", "scheduled_fraction", "actual_step_fraction",
                    "step", "total_steps", "tokens", "nominal_training_flops")},
                "n_training_seeds": 3, "validation_loss_mean": math.fsum(losses) / 3,
                "validation_loss_sample_sd": statistics.stdev(losses),
                "raw_values_by_training_seed": {str(row["training_seed"]): row["validation_loss_raw"]
                                               for row in rows},
            })
        summaries[arm] = observations
    return summaries


def tsv(rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


def figure_bytes(summary, *, synthetic=False):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    outputs = {}
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42}):
        for key, scale, xlabel, filename in (
            ("tokens", 1e6, "Training tokens (millions)", "validation_vs_tokens"),
            ("nominal_training_flops", 1e17, "Nominal cumulative training FLOPs (×10¹⁷)",
             "validation_vs_nominal_flops"),
        ):
            fig, ax = plt.subplots(figsize=(11.5, 6.6))
            fig.subplots_adjust(left=.085, right=.83, bottom=.20, top=.83)
            for arm in ARMS:
                rows = summary[arm]
                x = [row[key] / scale for row in rows]
                y = [row["validation_loss_mean"] for row in rows]
                sd = [row["validation_loss_sample_sd"] for row in rows]
                ax.fill_between(x, [a - b for a, b in zip(y, sd)],
                                [a + b for a, b in zip(y, sd)], color=COLORS[arm], alpha=.13, linewidth=0)
                ax.plot(x, y, color=COLORS[arm], label=arm, linewidth=2.4 if arm == "B" else 1.7,
                        marker="o", markersize=3.0, zorder=4 if arm == "B" else 3)
            ax.set(xlabel=xlabel, ylabel="Periodic validation loss (nats/token)")
            ax.grid(axis="y", alpha=.20)
            ax.margins(x=.025)
            ax.legend(title="Arm", loc="upper left", bbox_to_anchor=(1.015, 1),
                      frameon=False, borderaxespad=0)
            prefix = "SYNTHETIC SMOKE CHECK — " if synthetic else ""
            fig.text(.085, .935, prefix + "Language learning dynamics", fontsize=17, weight="bold")
            fig.text(.085, .883, "Periodic validation seed 1234 · mean ± training-seed SD · n = 3", fontsize=12)
            fig.text(.085, .105, "Observed per-arm marks only; no resampling or smoothing. Lines connect observations.",
                     fontsize=9.5, color="#374151")
            fig.text(.085, .073, "Schedules and endpoint budgets differ. Final gates use separate seed-5678 evaluation.",
                     fontsize=9.5, color="#374151")
            fig.text(.085, .041, "FLOPs are nominal modeled training work, not measured GPU execution or an equal-compute gate.",
                     fontsize=9.5, color="#374151")
            for extension in ("png", "pdf"):
                buffer = io.BytesIO()
                metadata = ({"Software": "beyond_language_dynamics.py"} if extension == "png"
                            else {"Creator": "beyond_language_dynamics.py", "CreationDate": None, "ModDate": None})
                fig.savefig(buffer, format=extension, dpi=180, metadata=metadata)
                outputs[f"{filename}.{extension}"] = buffer.getvalue()
            plt.close(fig)
    return outputs


def write_outputs(summary, raw, directory, *, plots=True):
    """Construct all bytes first; refuse to replace an artifact with different bytes."""
    output = {
        "summary.json": (json.dumps(summary, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(),
        "curves.tsv": tsv(raw),
    }
    if plots:
        output.update(figure_bytes(summary["per_arm_observed_marks"],
                                   synthetic=summary["schema"] == "beyond_language_dynamics_smoke"))
    directory = Path(directory)
    for name, content in output.items():
        path = directory / name
        require(not path.exists() or path.read_bytes() == content,
                f"refusing to replace different existing output: {path}")
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in output.items():
        path = directory / name
        if not path.exists():
            with path.open("xb") as stream:
                stream.write(content)
    return sorted(output)


def build_summary(report_path, plan_path, results_dir):
    report, report_file_hash = read_json(report_path)
    plan, plan_file_hash = read_json(plan_path)
    raw, inputs = collect_curves(report, plan, results_dir)
    summary = seal({
        "schema": "beyond_language_dynamics", "schema_version": 1,
        "status": "complete_three_seed_descriptive",
        "arm_order": list(ARMS), "training_seeds": list(SEEDS),
        "periodic_sample": PERIODIC_SAMPLE, "separate_final_gate_sample": FINAL_SAMPLE,
        "coverage": {"runs": len(inputs), "marks_per_run": MARKS, "raw_curve_rows": len(raw),
                     "training_seeds_per_arm": 3},
        "provenance": {
            "production_report_sha256": report["sha256"],
            "production_report_file_sha256": report_file_hash,
            "production_reporter_sha256": report["reporter_sha256"],
            "plan_sha256": plan["sha256"], "plan_file_sha256": plan_file_hash,
            "selection_sha256": report["selection_sha256"],
            "stage1_confirmation_sha256": report["stage1_confirmation_sha256"],
            "source_bridge_sha256": report["source_bridge_sha256"],
            "source_hashes": plan["source_hashes"],
            "model_source_hashes": plan["model_source_hashes"],
            "manifest_sha256s": report["manifest_sha256s"],
            "dataset_evidence_sha256": report["dataset_evidence_sha256"],
            "dataset_evidence_file_sha256": report["dataset_evidence_file_sha256"],
            "dynamics_reporter_sha256": digest(Path(__file__).read_bytes()),
            "results": inputs,
        },
        "notes": NOTES, "gate_analysis_performed": False,
        "per_arm_observed_marks": summarize(raw),
    })
    return summary, raw


def smoke_check(directory):
    """Handcrafted data only; never opens a plan, report, or experiment result."""
    raw = []
    for arm_index, arm in enumerate(ARMS):
        total_steps = 1600 + 160 * arm_index
        fpt = 2e8 + 1e7 * arm_index
        for seed in SEEDS:
            for mark in range(1, MARKS + 1):
                step = total_steps * mark // MARKS
                tokens = step * 32768
                raw.append({
                    "arm": arm, "training_seed": seed, "mark_index": mark,
                    "scheduled_fraction": mark / MARKS, "actual_step_fraction": step / total_steps,
                    "step": step, "total_steps": total_steps, "tokens": tokens,
                    "nominal_training_flops": tokens * fpt,
                    "validation_loss_raw": 3 + 2 / math.sqrt(mark) + arm_index * .045 + (seed - 2) * .02,
                })
    summaries = summarize(raw)
    require(close(summaries["rawS"][0]["validation_loss_mean"], 5), "smoke mean mismatch")
    require(close(summaries["rawS"][0]["validation_loss_sample_sd"], .02), "smoke SD mismatch")
    try:
        summarize(raw[:-1])
    except DynamicsError:
        pass
    else:
        raise DynamicsError("smoke check failed to reject a missing seed observation")
    summary = seal({
        "schema": "beyond_language_dynamics_smoke", "schema_version": 1,
        "status": "synthetic_only_not_experimental_evidence",
        "notes": NOTES, "per_arm_observed_marks": summaries,
    })
    files = write_outputs(summary, raw, directory)
    return {"status": summary["status"], "files": files, "summary_sha256": summary["sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", type=Path, help="Completed audited production report.json (all 18 runs).")
    parser.add_argument("--plan", type=Path, help="Frozen language plan bound to that report.")
    parser.add_argument("--results-dir", type=Path, help="Raw final result JSONs; only audited job IDs are opened.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Immutable JSON/TSV/PNG/PDF output directory.")
    parser.add_argument("--no-plots", action="store_true", help="Write JSON/TSV only; default also renders PNG/PDF.")
    parser.add_argument("--smoke-test", action="store_true",
                        help="Render deterministic handcrafted data only, without opening experimental inputs.")
    args = parser.parse_args()
    try:
        if args.smoke_test:
            require(not any((args.report, args.plan, args.results_dir, args.no_plots)),
                    "--smoke-test accepts only --output-dir")
            result = smoke_check(args.output_dir)
        else:
            require(all((args.report, args.plan, args.results_dir)),
                    "--report, --plan and --results-dir are required")
            summary, raw = build_summary(args.report, args.plan, args.results_dir)
            files = write_outputs(summary, raw, args.output_dir, plots=not args.no_plots)
            result = {"status": summary["status"], "summary_sha256": summary["sha256"],
                      "coverage": summary["coverage"], "files": files}
        print(json.dumps(result, indent=2))
    except (DynamicsError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Learning-curve report refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
