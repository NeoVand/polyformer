"""Audit and report frozen final language runs; never train or select checkpoints.

Production inputs must be committed plan, rate selection, Stage-1 confirmation,
and final manifests. Results and the budget ledger may still be arriving.
Example:
  python research/analysis/beyond_language_report.py --plan PLAN.json \
    --selection RATES.json --confirmation CONFIRM.json --source-bridge BRIDGE.json \
    --manifest SEED1.json --manifest SEED2.json --manifest SEED3.json \
    --results-dir research/results/beyond_runs --output-dir REPORT_DIR

JSON and TSV are deterministic. Optional plots are standalone PNG/PDF figures.
Sequence standard errors condition on a trained model and assume independent
sampled sequences; overlapping windows can violate that assumption.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import statistics


def protocol():
    spec = importlib.util.spec_from_file_location(
        "_language_report_protocol", Path(__file__).with_name("beyond_language_protocol.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


p = protocol()
CONTROLS = ("rawS", "convS", "convP", "GDN1", "DP4")
HEADLINE_CONTROLS = ("rawS", "convS", "GDN1", "DP4")
SCALAR_SEQUENCE_ATOL = 1e-5  # Reduction-order consistency only; never a gate tolerance.
UNCERTAINTY_NOTE = (
    "Sequence SE/normal intervals condition on one trained model and assume independent "
    "sampled sequences. Overlapping corpus windows can understate uncertainty. These are "
    "not training-seed uncertainty or statistical-significance tests. Across-seed mean/SD "
    "are descriptive; three wins alone do not establish statistical significance."
)


def require(condition, message):
    if not condition:
        raise p.ProtocolError(message)


def number(value, *, nonnegative=False):
    return p.finite_number(value) and (not nonnegative or value >= 0)


def integer(value, *, positive=False):
    return isinstance(value, int) and not isinstance(value, bool) and (not positive or value > 0)


def close(a, b, *, atol=0.0, rtol=1e-12):
    return number(a) and number(b) and math.isclose(a, b, rel_tol=rtol, abs_tol=atol)


def record_digest(value):
    # A malformed nonfinite result still has an auditable content identity;
    # no such value is copied into the sealed report's numerical fields.
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=True).encode()).hexdigest()


def moments(values):
    values = list(values)
    require(bool(values) and all(number(x) for x in values), "finite nonempty sample required")
    n = len(values)
    mean = math.fsum(values) / n
    sd = statistics.stdev(values) if n > 1 else None
    se = sd / math.sqrt(n) if sd is not None else None
    return {"n": n, "mean": mean, "sample_sd": sd, "conditional_sequence_se": se,
            "conditional_normal_95_interval": [mean - 1.96 * se, mean + 1.96 * se] if se is not None else None}


def seed_summary(values):
    values = list(values)
    return {"n_seeds": len(values), "mean": math.fsum(values) / len(values) if values else None,
            "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
            "interpretation": "descriptive variation across available training seeds; no significance claim"}


def sequence_array(value, count, label):
    require(isinstance(value, list) and len(value) == count, f"{label}: expected {count} sequence losses")
    require(all(number(x, nonnegative=True) for x in value), f"{label}: losses must be finite and nonnegative")
    return [float(x) for x in value]


def verify_inputs(plan, selection, confirmation, manifests, *, bridge=None, repository=None):
    """Validate frozen identities; malformed global artifacts abort reporting."""
    p.verify_plan(plan)
    require(plan.get("final_sample") == {"seed": 5678, "sequences": 1024, "tokens_per_sequence": 512},
            "final sample differs from the registered 1024-sequence evaluation")
    require(plan.get("source_bridge_sha256") == (bridge.get("sha256") if bridge else None),
            "source bridge does not match the frozen plan")
    p.check_seal(confirmation)
    require(confirmation["sha256"] == plan.get("stage1_confirmation_sha256"), "Stage-1 confirmation hash mismatch")
    p.verify_confirmation(confirmation, plan["survivors"], plan["model_source_hashes"],
                          bridge, repository=repository)
    for plan_key, confirmation_key in (
        ("stage1_gate_reconciliation", "gate_reconciliation"),
        ("stage1_active_gate_policy", "active_gate_policy"),
        ("stage1_strict_code_candidates", "strict_code_candidates"),
        ("stage1_strict_code_passed_candidates", "strict_code_passed_candidates"),
        ("stage1_strict_code_seed0_survivors", "strict_code_seed0_survivors"),
    ):
        require(plan.get(plan_key) == confirmation.get(confirmation_key), f"{plan_key} differs from Stage-1 evidence")
    expected, by_cell = {}, {}
    for seed in plan["final_seeds"]:
        jobs = p.final_jobs(plan, selection, seed)
        for arm, job in zip(plan["arm_order"], jobs):
            expected[job["id"]] = (arm, seed, job)
            by_cell[(arm, seed)] = job
    membership = {}
    for manifest in manifests:
        p.check_seal(manifest)
        require(manifest.get("stage") == "language", "final manifest has another stage")
        require(manifest.get("source_hashes") == plan["source_hashes"], "final manifest sources differ")
        require(manifest.get("runtime_versions") == plan["runtime_versions"], "final manifest versions differ")
        for job in manifest["jobs"]:
            require(job["id"] not in membership, "duplicate final job across manifests")
            require(job["id"] in expected and job == expected[job["id"]][2],
                    "unexpected or modified final manifest job")
            membership[job["id"]] = manifest
    return by_cell, membership


def checkpoint_evidence(result, job, checkpoint_root=None):
    checkpoint = result.get("checkpoint")
    require(isinstance(checkpoint, dict) and checkpoint.get("schema") == 1,
            "missing final checkpoint save metadata")
    size = checkpoint.get("bytes")
    require(integer(size, positive=True), "invalid final checkpoint size")
    require(checkpoint.get("path") == f"/runs/{job['id']}/final.pkl", "checkpoint path belongs to another run")
    artifacts = [a for a in result.get("artifacts", []) if a.get("name") == "final.pkl"]
    require(len(artifacts) == 1 and artifacts[0].get("bytes") == size,
            "checkpoint save is not corroborated by the worker artifact listing")
    require(result.get("log_directory") == job["id"] and result.get("log_volume") == "polyformer-beyond-runs",
            "checkpoint volume identity mismatch")
    evidence = {**checkpoint, "volume": result["log_volume"],
                "verification": "save metadata and independently listed worker file size; bytes not deserialized"}
    if checkpoint_root is not None:
        path = Path(checkpoint_root) / job["id"] / "final.pkl"
        require(path.is_file() and path.stat().st_size == size, "local final checkpoint missing or size mismatch")
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
        evidence.update(local_sha256=hasher.hexdigest(),
                        verification="local bytes and size checked without deserialization")
    return evidence


def ablation_rows(result, arm, cfg, base, base_raw):
    if not cfg.get("ablations"):
        return []
    modes = ("composition", "precision", "coupling") if arm in ("A", "C") else ("composition", "precision")
    rows = []
    for mode in modes:
        row = {"mode": mode, "status": "unconfirmed"}
        try:
            raw = result.get("ablation_val_big_raw", {}).get(mode)
            require(number(raw, nonnegative=True), "missing/nonfinite raw ablation loss")
            seq = sequence_array(result.get("ablation_val_big_sequence_losses", {}).get(mode),
                                 len(base), f"{mode} ablation")
            require(close(math.fsum(seq) / len(seq), raw, atol=SCALAR_SEQUENCE_ATOL, rtol=0),
                    "ablation scalar/sequence reductions disagree")
            difference = [a - b for a, b in zip(seq, base)]
            reported_difference = result.get("ablation_delta_val_big_sequence_losses", {}).get(mode)
            require(isinstance(reported_difference, list) and len(reported_difference) == len(base)
                    and all(close(a, b, atol=1e-12, rtol=0)
                            for a, b in zip(reported_difference, difference)),
                    "paired ablation difference array disagrees")
            require(close(result.get("ablation_delta_val_big_raw", {}).get(mode), raw - base_raw,
                          atol=1e-12, rtol=0), "paired raw ablation difference disagrees")
            row.update(status="complete", loss_raw=raw, raw_difference_nats=raw - base_raw,
                       paired_sequence_difference=moments(difference))
        except (p.ProtocolError, TypeError, KeyError) as exc:
            row["reason"] = str(exc)
        rows.append(row)
    return rows


def audit_run(plan, selection, arm, seed, job, manifest, result, *, checkpoint_root=None):
    row = {"arm": arm, "seed": seed, "job_id": job["id"], "status": "pending",
           "loss_raw": None, "reason": "result not yet available"}
    if manifest is None:
        row["reason"] = "final manifest not yet supplied"
        require(result is None, "result supplied without its exact final manifest")
        return row, None
    row["manifest_sha256"] = manifest["sha256"]
    if result is None:
        return row, None
    row["result_content_sha256"] = record_digest(result)
    cfg = p.expected_config(plan, arm, "final", selection["selected"][arm]["lr"], seed)
    try:
        p.validate_result_identity(plan, job, result, cfg)
        require(result.get("manifest_sha256") == manifest["sha256"] and result.get("manifest") == manifest["name"],
                "result manifest provenance mismatch")
        require(result.get("prediction_commit") == manifest.get("prediction_commit"),
                "result prediction commit mismatch")
        require(not p.is_failure(result), str(result.get("error") or result.get("failure")
                                             or result.get("nonfinite_fields") or "invalid run"))
        info = plan["arms"][arm]
        curve = result.get("curve") or []
        require(curve and curve[-1].get("step") == cfg["steps"], "training did not complete all frozen updates")
        require(number(result.get("val_loss_raw"), nonnegative=True)
                and curve[-1].get("val_raw") == result["val_loss_raw"],
                "missing or inconsistent final validation record")
        tokens = cfg["steps"] * cfg["batch"] * cfg["ctx"]
        require(tokens == info["main_tokens"] and result.get("tokens") == tokens,
                "completed token count differs from frozen plan")
        require(result.get("flops_per_token") == info["forward_fpt"]
                and result.get("train_flops_per_token") == info["training_fpt"],
                "per-token compute differs from frozen plan")
        require(close(result.get("train_flops"), info["training_fpt"] * tokens)
                and close(result.get("train_flops"), info["main_training_flops"]),
                "total compute differs from frozen plan")
        require(integer(result.get("params"), positive=True)
                and integer(result.get("nonembed")) and 0 <= result["nonembed"] <= result["params"],
                "invalid parameter counts")
        if "params" in info:
            require(result["params"] == info["params"], "parameter count differs from frozen plan")
        require(number(result.get("wall"), nonnegative=True) and number(result.get("secs"), nonnegative=True),
                "missing measured run times")
        checkpoint = checkpoint_evidence(result, job, checkpoint_root)
        expected_sample = {**plan["final_sample"], "order": "generator draw order"}
        require(result.get("val_big_sample") == expected_sample, "held-out sample identity/order mismatch")
        raw = result.get("val_big_raw")
        require(number(raw, nonnegative=True), "missing/nonfinite raw final loss")
        seq = sequence_array(result.get("val_big_sequence_losses"),
                             plan["final_sample"]["sequences"], "final")
        mean = math.fsum(seq) / len(seq)
        require(close(result.get("val_big_sequence_mean_raw"), mean, atol=1e-12, rtol=0),
                "reported sequence mean disagrees with full array")
        require(close(raw, mean, atol=SCALAR_SEQUENCE_ATOL, rtol=0),
                "raw scalar and sequence mean disagree beyond reduction tolerance")
        row.update(status="complete", reason=None, loss_raw=raw,
                   sequence_statistics=moments(seq), scalar_minus_sequence_mean=raw - mean,
                   params=result["params"], nonembedding_params=result["nonembed"],
                   tokens=tokens, steps=cfg["steps"], forward_flops_per_token=info["forward_fpt"],
                   training_flops_per_token=info["training_fpt"], training_flops=result["train_flops"],
                   measured_worker_seconds=result["wall"], measured_lm_seconds=result["secs"],
                   checkpoint=checkpoint, selected_rate=cfg["lr"],
                   sample=expected_sample, gpu_actual=result.get("gpu_actual"))
        row["ablations"] = ablation_rows(result, arm, cfg, seq, raw)
        row["ablation_status"] = ("complete" if all(x["status"] == "complete" for x in row["ablations"])
                                  else "unconfirmed")
        activity = {k: result[k] for k in ("component_usage", "component_parameters", "cor", "wrange", "wr_norm")
                    if k in result}
        # JSON round-trip refuses nonfinite activity without affecting a valid
        # final-loss measurement or inventing an activity-based headline gate.
        try:
            json.dumps(activity, allow_nan=False)
            row["activity"] = copy.deepcopy(activity)
        except (ValueError, TypeError):
            row["activity"] = {}
            row["activity_note"] = "invalid activity metadata"
        if arm in ("A", "B", "C") and not activity:
            row["activity_note"] = "component activity not available"
        return row, seq
    except (p.ProtocolError, TypeError, KeyError, ValueError) as exc:
        row.update(status="invalid", reason=str(exc))
        return row, None


def paired_comparison(candidate, control, candidate_seq, control_seq):
    if candidate["status"] != "complete" or control["status"] != "complete":
        return {"status": "unconfirmed", "candidate_status": candidate["status"],
                "control_status": control["status"]}
    require(candidate["sample"] == control["sample"], "paired sequence samples differ")
    diff = [a - b for a, b in zip(candidate_seq, control_seq)]
    raw = candidate["loss_raw"] - control["loss_raw"]
    return {"status": "complete", "raw_difference_nats": raw,
            "relative_loss_reduction": -raw / control["loss_raw"] if control["loss_raw"] > 0 else None,
            "paired_sequence_difference": moments(diff),
            "sign_convention": "candidate minus control; negative favors candidate"}


def combine(statuses):
    statuses = list(statuses)
    if "rejected" in statuses:
        return "rejected"
    return "passed" if statuses and all(s == "passed" for s in statuses) else "unconfirmed"


def candidate_gate(arm, confirmation, rows, seeds, *, strict=False):
    collection = confirmation["strict_code_candidates"] if strict else confirmation["candidates"]
    stage1 = collection.get(arm, {}).get("status", "unconfirmed")
    seed_rows = []
    for seed in seeds:
        candidate = rows.get((arm, seed), {"status": "pending"})
        checks = []
        for control in HEADLINE_CONTROLS:
            comparator = rows.get((control, seed), {"status": "pending"})
            factor = .99 if control in ("rawS", "convS") else 1.0
            check = {"control": control, "factor": factor, "status": "unconfirmed"}
            if candidate["status"] == comparator["status"] == "complete":
                boundary = factor * comparator["loss_raw"]
                check.update(candidate_loss=candidate["loss_raw"], control_loss=comparator["loss_raw"],
                             boundary=boundary, margin_to_boundary=boundary - candidate["loss_raw"],
                             status="passed" if candidate["loss_raw"] <= boundary else "rejected")
            checks.append(check)
        seed_rows.append({"seed": seed, "status": combine(c["status"] for c in checks), "checks": checks})
    stage1_gate = stage1 if stage1 in ("passed", "rejected") else "unconfirmed"
    return {"status": combine([stage1_gate, *[r["status"] for r in seed_rows]]),
            "stage1_status": stage1, "seed_gates": seed_rows,
            "requirement": "Stage1 passed and all four loss inequalities on each of seeds1/2/3",
            "interpretation": "observed registered gate; no significance claim"}


def ledger_row(ledger, job_id, manifest_sha):
    if ledger is None:
        return {"status": "unavailable", "estimate_usd": None}
    entry = ledger.get("jobs", {}).get(job_id)
    if not entry:
        return {"status": "unavailable", "estimate_usd": None}
    if entry.get("stage") != "language" or entry.get("manifest_sha256") != manifest_sha:
        return {"status": "invalid_ledger_identity", "estimate_usd": None}
    settled = entry.get("settled_usd")
    reserved = entry.get("reserved_usd")
    return {"status": entry.get("status"), "settled_estimate_usd": settled if number(settled, nonnegative=True) else None,
            "reserved_usd": reserved if number(reserved, nonnegative=True) else None,
            "estimate_usd": settled if number(settled, nonnegative=True)
            else reserved if number(reserved, nonnegative=True) else None}


def build_report(plan, selection, confirmation, manifests, results, *, bridge=None,
                 repository=None, ledger=None, checkpoint_root=None):
    by_cell, membership = verify_inputs(plan, selection, confirmation, manifests,
                                       bridge=bridge, repository=repository)
    rows, arrays = {}, {}
    for (arm, seed), job in by_cell.items():
        row, array = audit_run(plan, selection, arm, seed, job, membership.get(job["id"]),
                               results.get(job["id"]), checkpoint_root=checkpoint_root)
        row["cost"] = ledger_row(ledger, job["id"], row.get("manifest_sha256"))
        rows[(arm, seed)] = row
        arrays[(arm, seed)] = array
    for arm in plan["arm_order"]:
        complete = [r for (a, _), r in rows.items() if a == arm and r["status"] == "complete"]
        if len({(r["params"], r["nonembedding_params"]) for r in complete}) > 1:
            for row in complete:
                row.update(status="invalid", reason="parameter counts differ across seeds of the same frozen arm",
                           loss_raw=None)
    comparisons = []
    for arm in plan["survivors"]:
        for control in CONTROLS:
            for seed in plan["final_seeds"]:
                comparisons.append({"candidate": arm, "control": control, "seed": seed,
                                    **paired_comparison(rows[(arm, seed)], rows[(control, seed)],
                                                        arrays[(arm, seed)], arrays[(control, seed)])})
    gates = {arm: candidate_gate(arm, confirmation, rows, plan["final_seeds"])
             for arm in sorted(confirmation["candidates"])}
    strict = {arm: candidate_gate(arm, confirmation, rows, plan["final_seeds"], strict=True)
              for arm in sorted(confirmation["candidates"])}
    for arm in gates:
        gates[arm]["written_rule_only"] = gates[arm]["status"] == "passed" and strict[arm]["status"] != "passed"
    summaries = {
        arm: seed_summary(rows[(arm, s)]["loss_raw"] for s in plan["final_seeds"]
                          if rows[(arm, s)]["status"] == "complete") for arm in plan["arm_order"]
    }
    paired_summaries = []
    for arm in plan["survivors"]:
        for control in CONTROLS:
            values = [r["raw_difference_nats"] for r in comparisons
                      if r["candidate"] == arm and r["control"] == control and r["status"] == "complete"]
            paired_summaries.append({"candidate": arm, "control": control, **seed_summary(values)})
    mechanism = {}
    for arm in plan["survivors"]:
        pairs = [r for r in comparisons if r["candidate"] == arm and r["control"] == "convP"]
        mechanism[arm] = {
            "status": "complete" if all(r["status"] == "complete" for r in pairs) else "unconfirmed",
            "lower_than_convP_all_three_seeds": all(r["status"] == "complete" and r["raw_difference_nats"] < 0 for r in pairs),
            "interpretation": "Comparison beyond estimation; checkpoint removals/activity do not prove a causal noncommutativity benefit.",
        }
    data = {
        "schema": "beyond_language_final_report", "schema_version": 1,
        "plan_sha256": plan["sha256"], "selection_sha256": selection["sha256"],
        "stage1_confirmation_sha256": confirmation["sha256"],
        "source_bridge_sha256": bridge["sha256"] if bridge else None,
        "source_hashes": plan["source_hashes"], "manifest_sha256s": sorted(m["sha256"] for m in manifests),
        "selected_rates": copy.deepcopy(selection["selected"]),
        "reporter_sha256": p.digest(Path(__file__).read_bytes()),
        "active_gate_policy": confirmation["active_gate_policy"],
        "gate_reconciliation": copy.deepcopy(confirmation["gate_reconciliation"]),
        "strict_code_stage1_candidates": copy.deepcopy(confirmation["strict_code_candidates"]),
        "strict_code_stage1_passed_candidates": copy.deepcopy(confirmation["strict_code_passed_candidates"]),
        "candidate_gates": gates, "strict_code_candidate_gates": strict,
        "passed_candidates": [a for a, g in gates.items() if g["status"] == "passed"],
        "strict_code_passed_candidates": [a for a, g in strict.items() if g["status"] == "passed"],
        "runs": list(rows.values()), "comparisons": comparisons,
        "across_seed_loss_summaries": summaries, "across_seed_paired_summaries": paired_summaries,
        "composition_comparison": mechanism, "final_sample": plan["final_sample"],
        "uncertainty_note": UNCERTAINTY_NOTE,
        "pairing_basis": "Same frozen data path, evaluation seed, sequence count, token length and generator draw order; worker outputs do not supply individual window IDs.",
        "scalar_sequence_consistency_atol": SCALAR_SEQUENCE_ATOL,
        "gate_numeric_tolerance": 0,
        "accounting": {"target_training_flops": plan["target_training_flops"],
                       "arm_plan": copy.deepcopy(plan["arms"]),
                       "control_allowance": copy.deepcopy(plan.get("control_allowance")),
                       "budget_plan": copy.deepcopy(plan["budget"]),
                       "final_runs_estimate_usd": math.fsum(r["cost"]["estimate_usd"] for r in rows.values()
                                                          if r["cost"].get("estimate_usd") is not None),
                       "final_runs_missing_cost_entries": sum(r["cost"].get("estimate_usd") is None
                                                             for r in rows.values()),
                       "note": "Use the frozen per-arm steps and any prospective control allowance. Controls can receive more work than candidates under the declared conventions; this is not executed GPU FLOP equality. Runtime includes compilation/evaluation. Ledger figures are estimates, not invoices."},
        "ledger_sha256": record_digest(ledger) if ledger is not None else None,
        "ledger_cost_basis": ledger.get("cost_basis") if ledger else None,
        "coverage": {"expected_runs": len(rows),
                     **{status: sum(r["status"] == status for r in rows.values())
                        for status in ("complete", "pending", "invalid")}},
        "result_usage": "Only final raw means determine gates. Intermediate checkpoints, rounded losses, ablations and activity never select runs or rates.",
    }
    return p.seal(data)


def tabular(rows, columns):
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow(["" if row.get(c) is None else row[c] for c in columns])
    return output.getvalue()


def write_text_immutable(path, text):
    if path.exists():
        require(path.read_text() == text, f"refusing to replace existing report artifact {path}")
    else:
        with path.open("x") as stream:
            stream.write(text)


def write_outputs(report, directory, *, plots=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    p.write_immutable(directory / "report.json", report)
    runs = [{**r, "conditional_sequence_se": (r.get("sequence_statistics") or {}).get("conditional_sequence_se"),
             "estimated_usd": r["cost"].get("estimate_usd")} for r in report["runs"]]
    write_text_immutable(directory / "runs.tsv", tabular(runs, [
        "arm", "seed", "status", "loss_raw", "conditional_sequence_se", "selected_rate", "params",
        "nonembedding_params", "tokens", "steps", "training_flops", "measured_worker_seconds",
        "measured_lm_seconds", "estimated_usd", "job_id", "reason"]))
    comparisons = [{**r, "conditional_paired_sequence_se":
                    (r.get("paired_sequence_difference") or {}).get("conditional_sequence_se")}
                   for r in report["comparisons"]]
    write_text_immutable(directory / "paired_differences.tsv", tabular(comparisons, [
        "candidate", "control", "seed", "status", "raw_difference_nats", "relative_loss_reduction",
        "conditional_paired_sequence_se"]))
    write_text_immutable(directory / "across_seed_losses.tsv", tabular(
        [{"arm": arm, **summary} for arm, summary in report["across_seed_loss_summaries"].items()],
        ["arm", "n_seeds", "mean", "sample_sd"]))
    write_text_immutable(directory / "across_seed_paired_differences.tsv", tabular(
        report["across_seed_paired_summaries"], ["candidate", "control", "n_seeds", "mean", "sample_sd"]))
    ablations = [{**a, "arm": r["arm"], "seed": r["seed"],
                  "conditional_paired_sequence_se": (a.get("paired_sequence_difference") or {}).get("conditional_sequence_se")}
                 for r in report["runs"] for a in r.get("ablations", [])]
    write_text_immutable(directory / "ablations.tsv", tabular(ablations, [
        "arm", "seed", "mode", "status", "loss_raw", "raw_difference_nats",
        "conditional_paired_sequence_se", "reason"]))
    gates = [{"candidate": arm, "active_status": g["status"],
              "strict_code_status": report["strict_code_candidate_gates"][arm]["status"],
              "written_rule_only": g["written_rule_only"]}
             for arm, g in report["candidate_gates"].items()]
    write_text_immutable(directory / "gates.tsv", tabular(gates, [
        "candidate", "active_status", "strict_code_status", "written_rule_only"]))
    if plots:
        plot_report(report, directory)


def plot_report(report, directory):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    complete = [r for r in report["runs"] if r["status"] == "complete"]
    if not complete:
        return
    arms = list(report["across_seed_loss_summaries"])
    fig, ax = plt.subplots(figsize=(10, 5))
    for seed, offset in ((1, -.16), (2, 0), (3, .16)):
        data = [r for r in complete if r["seed"] == seed]
        ax.errorbar([arms.index(r["arm"]) + offset for r in data], [r["loss_raw"] for r in data],
                    yerr=[1.96 * r["sequence_statistics"]["conditional_sequence_se"] for r in data],
                    fmt="o", capsize=2, label=f"Training seed {seed}")
    ax.set_xticks(range(len(arms)), arms)
    ax.set_ylabel("Final held-out loss (nats/token)")
    ax.set_title("Individual final runs; conditional sequence normal 95% intervals")
    ax.legend()
    fig.text(.5, .01, "Intervals exclude training variation; overlapping windows can understate uncertainty.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, 1))
    for suffix in ("png", "pdf"):
        path = directory / f"final_losses.{suffix}"
        require(not path.exists(), f"refusing to overwrite plot {path}")
        fig.savefig(path, dpi=180, metadata={"Creator": "beyond_language_report"})
    plt.close(fig)
    candidates = sorted({r["candidate"] for r in report["comparisons"]})
    fig, axes = plt.subplots(max(1, len(candidates)), 1, figsize=(10, 3.5 * max(1, len(candidates))),
                             squeeze=False)
    for arm, ax in zip(candidates, axes[:, 0]):
        for seed, offset in ((1, -.16), (2, 0), (3, .16)):
            data = [r for r in report["comparisons"] if r["candidate"] == arm
                    and r["seed"] == seed and r["status"] == "complete"]
            ax.errorbar([CONTROLS.index(r["control"]) + offset for r in data],
                        [r["raw_difference_nats"] for r in data],
                        yerr=[1.96 * r["paired_sequence_difference"]["conditional_sequence_se"] for r in data],
                        fmt="o", capsize=2, label=f"Training seed {seed}")
        ax.axhline(0, color="black", linewidth=.7)
        ax.set_xticks(range(len(CONTROLS)), CONTROLS)
        ax.set_ylabel(f"{arm} minus control\n(nats/token)")
        ax.set_title(f"Candidate {arm}; negative favors candidate")
        ax.legend()
    fig.text(.5, .01, "Conditional paired-sequence normal 95% intervals; overlap and training variation caveats apply.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, 1))
    for suffix in ("png", "pdf"):
        path = directory / f"paired_differences.{suffix}"
        require(not path.exists(), f"refusing to overwrite plot {path}")
        fig.savefig(path, dpi=180, metadata={"Creator": "beyond_language_report"})
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--research-root", type=Path, default=p.default_research_root())
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--selection", type=Path, required=True)
    ap.add_argument("--confirmation", type=Path, required=True)
    ap.add_argument("--source-bridge", type=Path)
    ap.add_argument("--manifest", type=Path, action="append", default=[])
    ap.add_argument("--evidence-commit", default="HEAD")
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--ledger", type=Path)
    ap.add_argument("--checkpoint-root", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--plots", action="store_true")
    args = ap.parse_args()
    root = args.research_root.resolve()
    def committed(path):
        return p.committed_file(root, path, args.evidence_commit)
    plan, selection, confirmation = map(committed, (args.plan, args.selection, args.confirmation))
    bridge = committed(args.source_bridge) if args.source_bridge else None
    manifests = [committed(path) for path in args.manifest]
    for manifest in manifests:
        p.verify_manifest_registration(root, plan, manifest)
    if bridge is not None:
        p.verify_bridge_commits(root, bridge)
    ledger = json.loads(args.ledger.read_text()) if args.ledger else None
    report = build_report(plan, selection, confirmation, manifests, p.read_results(args.results_dir),
                          bridge=bridge, repository=root.parent, ledger=ledger,
                          checkpoint_root=args.checkpoint_root)
    write_outputs(report, args.output_dir, plots=args.plots)
    print(json.dumps({"report_sha256": report["sha256"], "coverage": report["coverage"],
                      "passed_candidates": report["passed_candidates"],
                      "strict_code_passed_candidates": report["strict_code_passed_candidates"]}, indent=2))


if __name__ == "__main__":
    main()
