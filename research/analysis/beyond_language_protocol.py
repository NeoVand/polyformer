"""Deterministic, local-only Stage-2 planning and validation-only rate selection.

This module never imports Modal or launches work. Its nested analysis location
does not change the frozen top-level research source map. From the worktree:

    python research/analysis/beyond_language_protocol.py draft --survivors B,C \
        --budget research/results/beyond_language_planning/budget.json --out DRAFT.json

After reporting amendments and Stage-1 confirmation are committed:

    python research/analysis/beyond_language_protocol.py freeze --confirmation CONFIRM.json \
        --source-bridge BRIDGE.json --budget BUDGET.json --out PLAN.json
    python research/analysis/beyond_language_protocol.py export --plan PLAN.json \
        --phase tuning --out TUNING_JOBS.json
    python research/analysis/beyond_language_protocol.py select --plan PLAN.json \
        --manifest TUNING_MANIFEST.json --results-dir research/results/beyond_runs \
        --out SELECTION.json

Commit SELECTION.json, then export/execute complete seed blocks in order:

    python research/analysis/beyond_language_protocol.py export --plan PLAN.json \
        --phase final --selection SELECTION.json --seed 1 --out SEED1_JOBS.json

Final exports for seeds 2/3 require terminal results for every earlier seed block.
The runner remains responsible for immutable manifests and bounded reservations.
The research root is detected from the worktree, research directory, or this file;
--research-root explicitly selects another checkout.
"""

from __future__ import annotations

import argparse
import ast
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys


MODEL_SOURCES = ("beyond_diag.py", "beyond_layers.py", "lm.py", "groups.py", "diag.py")
ARMS = {
    "rawS": ("gpt", 0, 1),
    "convS": ("gpt", 3, 1),
    "convP": ("plx", 3, 1),
    "A": ("beyond_a", 3, 1),
    "B": ("beyond_b", 3, 1),
    "C": ("beyond_c", 3, 1),
    "GDN1": ("gated_delta", 0, 1),
    "DP4": ("gated_delta", 0, 4),
}
RATES = (0.002, 0.004, 0.008)
FINAL_SEEDS = (1, 2, 3)
PRIMARY_CELLS = (("mqar_small", 2), ("induction_small", 2),
                 ("wp_a5_16", 1), ("wp_a5_16", 2),
                 ("wp_s5_16", 1), ("wp_s5_16", 2))
BATCH_TOKENS = 32768
SWEEP_STEPS = 3051
REFERENCE_STEPS = 12207
VERSIONS = {"jax": "0.12.0", "optax": "0.2.8", "numpy": "2.5.4"}
RATE_PER_SECOND = 0.00122044
RESOURCE_OVERHEAD_SECONDS = 152
STAGE1_PROTOCOL_ID = "829e3a8f2bbdce4b2a2b1fdd602f0565704750cb3ce6e69b1fa96bbe408fab63"
RECONCILIATION_POLICY_ID = "59e1b83139fbb148de0132005de781486a86aa79cd4a2c5d675ca21416863d46"
STRICT_SELECTION_PATH = "research/results/beyond_stage1_selection_strict.json"


class ProtocolError(ValueError):
    pass


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(data).hexdigest()


def seal(value):
    value = {k: v for k, v in value.items() if k != "sha256"}
    return {**value, "sha256": digest(value)}


def check_seal(value):
    if value.get("sha256") != digest({k: v for k, v in value.items() if k != "sha256"}):
        raise ProtocolError("artifact checksum mismatch")
    return value


def write_immutable(path, value):
    path = Path(path)
    text = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text() == text:
            return
        raise ProtocolError(f"refusing to replace an existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(text)


def sources(root):
    return {p.name: digest(p.read_bytes()) for p in sorted(Path(root).glob("*.py"))}


def default_research_root():
    candidates = (Path.cwd(), Path.cwd() / "research", Path(__file__).resolve().parent.parent)
    for candidate in candidates:
        if (candidate / "lm.py").is_file() and (candidate / "BEYOND.md").is_file():
            return candidate.resolve()
    raise ProtocolError("cannot find lm.py and BEYOND.md; provide --research-root PATH")


def model_sources(all_sources):
    try:
        return {name: all_sources[name] for name in MODEL_SOURCES}
    except KeyError as exc:
        raise ProtocolError(f"missing model source {exc}") from exc


def language_registration(text):
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## 5.")]
    if len(starts) != 1:
        raise ProtocolError("expected exactly one Section 5 language registration")
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return ("\n".join(lines[start:end]).rstrip() + "\n").encode()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root)


def committed_file(root, path, commit):
    path = Path(path).resolve()
    repository = Path(git(root, "rev-parse", "--show-toplevel").decode().strip())
    try:
        relative = path.relative_to(repository).as_posix()
    except ValueError as exc:
        raise ProtocolError(f"evidence must be committed inside the worktree: {path}") from exc
    content = path.read_bytes()
    if git(root, "show", f"{commit}:{relative}") != content:
        raise ProtocolError(f"evidence differs from commit {commit}: {relative}")
    return json.loads(content)


def verify_manifest_registration(root, plan, manifest):
    content = git(root, "show", f"{manifest['prediction_commit']}:research/BEYOND.md")
    if digest(content) != manifest["prediction_sha256"]:
        raise ProtocolError("manifest prediction hash differs from its committed document")
    if digest(language_registration(content.decode())) != plan["language_registration_sha256"]:
        raise ProtocolError("manifest language registration differs from the frozen protocol")


def parser_from_source(path):
    """Recover actual argparse defaults without executing training or imports."""
    parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    tree = ast.parse(Path(path).read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "add_argument"
             and isinstance(n.func.value, ast.Name) and n.func.value.id == "ap"]
    for node in sorted(calls, key=lambda n: n.lineno):
        names = [ast.literal_eval(n) for n in node.args]
        kwargs = {}
        for item in node.keywords:
            if item.arg in ("default", "choices", "dest", "required", "action", "nargs"):
                kwargs[item.arg] = ast.literal_eval(item.value)
            elif item.arg == "type":
                if not isinstance(item.value, ast.Name) or item.value.id not in ("int", "float", "str"):
                    raise ProtocolError("unsupported lm.py argparse type")
                kwargs["type"] = {"int": int, "float": float, "str": str}[item.value.id]
        parser.add_argument(*names, **kwargs)
    if not calls:
        raise ProtocolError("could not recover lm.py argument contract")
    return parser


def counts_from_source(root, configs):
    root = Path(root).resolve()
    sys.path.insert(0, str(root))
    try:
        spec = importlib.util.spec_from_file_location("_beyond_language_lm", root / "lm.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return {name: {
            "forward_fpt": float(module.flops_per_token(argparse.Namespace(**cfg), 512)),
            "training_fpt": float(module.training_flops_per_token(argparse.Namespace(**cfg), 512)),
        } for name, cfg in configs.items()}
    finally:
        sys.path.pop(0)


def argv_for(arm, lr, seed, steps, phase):
    arch, conv, nh = ARMS[arm]
    values = {
        "arch": arch, "data": "/data/fineweb_edu", "vocab": 50304,
        "ctx": 512, "d": 512, "heads": 8, "layers": 6, "mlp": 2048,
        "opt": "muon", "lr": lr, "seed": seed, "batch": 64, "micro": 2,
        "bf16": 1, "remat": 1, "steps": steps, "tokens": 0,
        "warmup": 305 if phase == "tuning" else 400,
        "vseqs": 1024, "vbig": 0 if phase == "tuning" else 1024,
        "evals": 8 if phase == "tuning" else 16, "progress": 1,
        "qkv_conv": conv, "pos": 1, "group_init": "random", "gdim": 5,
        "nh": nh, "beta_max": 1 if nh == 1 else 2,
        "delta_key_ratio": 0.75, "delta_v_expand": 2.0,
        "delta_unroll": 4, "delta_chunk": 32 if arch == "gated_delta" else 0,
        "ablate": "none", "save-final": 0 if phase == "tuning" else 1,
        "ablations": int(phase == "final" and arm in ("A", "B", "C")),
        "cap": 0, "plx_norm": 0, "hops": 1, "lookback": 0,
    }
    return [part for key, value in values.items() for part in (f"--{key}", str(value))]


def make_job(plan, arm, phase, lr, seed):
    info = plan["arms"][arm]
    steps = SWEEP_STEPS if phase == "tuning" else info["main_steps"]
    seconds = info["sweep_timeout_seconds"] if phase == "tuning" else info["main_timeout_seconds"]
    job = {"script": "lm.py", "argv": argv_for(arm, lr, seed, steps, phase),
           "gpu": "H100", "max_seconds": seconds, "attempt": 0}
    identity = {k: job[k] for k in ("script", "argv", "gpu", "attempt")}
    identity["source_hashes"] = plan["source_hashes"]
    job["id"] = digest(identity)[:24]
    job["reserved_usd"] = round(RATE_PER_SECOND * (seconds + RESOURCE_OVERHEAD_SECONDS), 6)
    return job


def reconciliation_adapter():
    path = Path(__file__).with_name("beyond_gate_reconciliation.py")
    spec = importlib.util.spec_from_file_location("_beyond_language_gate_policy", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.POLICY_ID != RECONCILIATION_POLICY_ID:
        raise ProtocolError("the reconciliation adapter has an unknown policy")
    return module


def verify_passed_cells(arm, record, *, strict):
    required = {(task, layers, seed) for task, layers in PRIMARY_CELLS for seed in FINAL_SEEDS}
    cells = record["cells"]
    actual = [(c["task"], c["layers"], c["seed"]) for c in cells]
    if len(actual) != 18 or set(actual) != required:
        raise ProtocolError(f"{arm} lacks the 18 unique independent confirmation cells")
    policy = "strict_frozen_v1" if strict else RECONCILIATION_POLICY_ID
    if record.get("gate_policy") != policy:
        raise ProtocolError(f"{arm} candidate gate policy differs from its stated outcome")
    for cell in cells:
        gate = cell["gate"]
        floor = 0.95 if cell["task"].startswith("wp_") else 0.90
        if (gate.get("status") != "passed" or gate.get("gate_policy") != policy
                or gate.get("reference_floor_required") is not strict
                or gate.get("floor") != floor or gate.get("maximum_reference_gap") != 0.03
                or gate.get("threshold_tolerance") != 1e-12):
            raise ProtocolError(f"{arm} confirmation gate differs from the recognized policy")
        scores = []
        for role in ("candidate", "reference"):
            result = cell.get(role, {})
            score = result.get("test_score")
            if result.get("status") != "complete" or not finite_number(score) or not 0 <= score <= 1:
                raise ProtocolError(f"{arm} passed gate lacks a finite completed {role}")
            scores.append(score)
        score, reference = scores
        if (score < floor - 1e-12 or score + 0.03 < reference - 1e-12
                or (strict and reference < floor - 1e-12)):
            raise ProtocolError(f"{arm} passed gate violates its stated numeric inequalities")


def verify_confirmation_policy(confirmation, repository=None, evidence_commit=None):
    if confirmation.get("active_gate_policy") != RECONCILIATION_POLICY_ID:
        raise ProtocolError("unrecognized or missing active Stage-1 gate policy")
    metadata = confirmation.get("gate_reconciliation")
    repository = Path(repository) if repository is not None else Path(__file__).resolve().parents[2]
    try:
        reconciliation_adapter().validate_reconciliation_metadata(metadata, repository)
    except (ValueError, TypeError, KeyError) as exc:
        raise ProtocolError(f"invalid Stage-1 gate reconciliation: {exc}") from exc
    if (confirmation.get("protocol_id") != STAGE1_PROTOCOL_ID
            or metadata.get("original_protocol_id") != STAGE1_PROTOCOL_ID):
        raise ProtocolError("Stage-1 reconciliation changed the original registered protocol")
    registration = metadata["registration_commit"]
    try:
        original = json.loads(git(repository, "show", f"{registration}:{STRICT_SELECTION_PATH}"))
        check_seal(original)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        raise ProtocolError("registration commit lacks the sealed original strict selection") from exc
    if (original["sha256"] != metadata["original_selection_sha256"]
            or original.get("protocol_id") != STAGE1_PROTOCOL_ID
            or confirmation.get("strict_code_seed0_survivors") != original.get("survivors")):
        raise ProtocolError("Stage-1 strict seed-0 provenance differs from its committed original selection")
    if evidence_commit is not None:
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", registration, evidence_commit],
            cwd=repository, capture_output=True, check=False,
        )
        if ancestor.returncode:
            raise ProtocolError("language evidence does not descend from the prospective Stage-1 registration")
    strict = confirmation.get("strict_code_candidates")
    if not isinstance(strict, dict) or set(strict) != set(confirmation["candidates"]):
        raise ProtocolError("both written-rule and strict-code candidate records must be retained")
    strict_passed = sorted(arm for arm, value in strict.items() if value.get("status") == "passed")
    if sorted(confirmation.get("strict_code_passed_candidates", [])) != strict_passed:
        raise ProtocolError("strict-code passed candidate list disagrees with retained outcomes")
    if not set(strict_passed) <= set(confirmation["strict_code_seed0_survivors"]):
        raise ProtocolError("strict-code confirmation cannot pass a strict-ineligible seed-0 candidate")
    if not set(strict_passed) <= set(confirmation["passed_candidates"]):
        raise ProtocolError("a strict-code pass must also satisfy the active written rule")
    for arm in strict_passed:
        verify_passed_cells(arm, strict[arm], strict=True)
    for arm, active in confirmation["candidates"].items():
        active_cells = {(c["task"], c["layers"], c["seed"]): c for c in active.get("cells", [])}
        for cell in strict[arm].get("cells", []):
            counterpart = active_cells.get((cell["task"], cell["layers"], cell["seed"]))
            if counterpart is None or any(cell.get(role) != counterpart.get(role) for role in ("candidate", "reference")):
                raise ProtocolError("written-rule and strict-code outcomes must use identical measurements")
    return metadata


def verify_confirmation(confirmation, survivors, current_model_sources, bridge=None, *,
                        repository=None, evidence_commit=None):
    check_seal(confirmation)
    if (confirmation.get("schema"), confirmation.get("schema_version")) != ("stage1_confirmation", 1):
        raise ProtocolError("unsupported Stage-1 confirmation artifact")
    verify_confirmation_policy(confirmation, repository, evidence_commit)
    expected_passed = sorted(k for k, v in confirmation["candidates"].items()
                             if v.get("status") == "passed")
    if sorted(confirmation["passed_candidates"]) != expected_passed or sorted(survivors) != expected_passed:
        raise ProtocolError("survivor list must equal all independently confirmed candidates")
    if any(v.get("status") not in ("passed", "rejected", "unconfirmed")
           for v in confirmation["candidates"].values()):
        raise ProtocolError("Stage-1 closure requires passed, rejected, or unconfirmed candidate statuses")
    deferrals = confirmation.get("budget_deferrals", {})
    for arm, deferral in deferrals.items():
        candidate = confirmation["candidates"].get(arm, {})
        if (candidate.get("status") != "unconfirmed"
                or candidate.get("budget_deferral") != deferral
                or deferral.get("status") != "budget_deferred"
                or not deferral.get("reason")
                or not deferral.get("missing_cells")):
            raise ProtocolError("invalid or incomplete explicit Stage-1 budget deferral")
        for key in ("ledger_sha256", "ledger_file_sha256"):
            value = deferral.get(key)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ProtocolError("Stage-1 deferral lacks budget ledger provenance")
        if set(deferral.get("ledger_snapshot", {})) != {"screen", "language", "development", "total"}:
            raise ProtocolError("Stage-1 deferral lacks all budget categories")
    if any(v.get("budget_deferral") is not None and arm not in deferrals
           for arm, v in confirmation["candidates"].items()):
        raise ProtocolError("Stage-1 candidate budget deferral is not linked from the closure artifact")
    for arm in survivors:
        verify_passed_cells(arm, confirmation["candidates"][arm], strict=False)
    before = confirmation["model_source_hashes"]
    if set(before) != set(MODEL_SOURCES):
        raise ProtocolError("incomplete Stage-1 model source map")
    if before == current_model_sources:
        return
    if bridge is None:
        raise ProtocolError("Stage-1 to Stage-2 source change requires a committed reporting-only bridge")
    check_seal(bridge)
    if (bridge.get("schema"), bridge.get("schema_version")) != ("stage2_source_bridge", 1):
        raise ProtocolError("unsupported source bridge")
    if bridge.get("classification") != "report_only" or not bridge.get("audit"):
        raise ProtocolError("source bridge lacks an explicit reporting-only audit")
    if bridge.get("old_model_source_hashes") != before or bridge.get("new_model_source_hashes") != current_model_sources:
        raise ProtocolError("bridge source endpoints do not match confirmation/current sources")
    changed = sorted(k for k in MODEL_SOURCES if before[k] != current_model_sources[k])
    if changed != ["lm.py"] or bridge.get("allowed_changed_files") != ["lm.py"]:
        raise ProtocolError("only the explicitly audited lm.py reporting amendment may bridge sources")
    if digest(bridge.get("diff", "").encode()) != bridge.get("diff_sha256"):
        raise ProtocolError("bridge diff hash mismatch")


def verify_bridge_commits(root, bridge):
    for name in MODEL_SOURCES:
        before = git(root, "show", f"{bridge['before_commit']}:research/{name}")
        after = git(root, "show", f"{bridge['after_commit']}:research/{name}")
        if digest(before) != bridge["old_model_source_hashes"][name]:
            raise ProtocolError("bridge before_commit does not contain its declared model source")
        if digest(after) != bridge["new_model_source_hashes"][name]:
            raise ProtocolError("bridge after_commit does not contain its declared model source")
    difference = git(root, "diff", bridge["before_commit"], bridge["after_commit"], "--", "research/lm.py")
    if difference.decode() != bridge["diff"]:
        raise ProtocolError("bridge does not contain the exact committed lm.py diff")


def build_plan(root, survivors, budget, *, confirmation=None, bridge=None, evidence_commit=None):
    root = Path(root).resolve()
    survivors = sorted(survivors)
    if not survivors or len(set(survivors)) != len(survivors) or not set(survivors) <= {"A", "B", "C"}:
        raise ProtocolError("at least one unique confirmed candidate A/B/C is required")
    before = sources(root)
    models = model_sources(before)
    parser = parser_from_source(root / "lm.py")
    order = ["rawS", "convS", "convP", *survivors, "GDN1", "DP4"]
    configs = {a: vars(parser.parse_args(argv_for(a, 0.004, 0, SWEEP_STEPS, "tuning"))) for a in order}
    counts = counts_from_source(root, configs)
    if sources(root) != before:
        raise ProtocolError("research sources changed while calculating the plan")
    if confirmation is not None:
        verify_confirmation(confirmation, survivors, models, bridge, repository=root.parent,
                            evidence_commit=evidence_commit)
        if "val_loss_raw" not in (root / "lm.py").read_text():
            raise ProtocolError("apply and audit the unrounded reporting amendment before freezing")
    target_arm = max(survivors, key=lambda a: (counts[a]["training_fpt"], a))
    target = Fraction(str(counts[target_arm]["training_fpt"])) * REFERENCE_STEPS * BATCH_TOKENS
    plan = {
        "schema": "beyond_language_plan", "schema_version": 1,
        "status": "frozen" if confirmation is not None else "draft",
        "source_hashes": before, "model_source_hashes": models,
        "planner_sha256": digest(Path(__file__).read_bytes()), "runtime_versions": VERSIONS,
        "gate_policy_adapter_sha256": digest(Path(__file__).with_name("beyond_gate_reconciliation.py").read_bytes()),
        "evidence_commit": evidence_commit,
        "language_registration_sha256": digest(language_registration((root / "BEYOND.md").read_text())),
        "stage1_confirmation_sha256": confirmation["sha256"] if confirmation else None,
        "stage1_gate_reconciliation": copy.deepcopy(confirmation["gate_reconciliation"]) if confirmation else None,
        "stage1_active_gate_policy": confirmation["active_gate_policy"] if confirmation else None,
        "stage1_strict_code_candidates": copy.deepcopy(confirmation["strict_code_candidates"]) if confirmation else None,
        "stage1_strict_code_passed_candidates": copy.deepcopy(confirmation["strict_code_passed_candidates"]) if confirmation else None,
        "stage1_strict_code_seed0_survivors": copy.deepcopy(confirmation["strict_code_seed0_survivors"]) if confirmation else None,
        "stage1_closed_candidate_statuses": {
            arm: value["status"] for arm, value in confirmation["candidates"].items()
        } if confirmation else None,
        "stage1_nonadvancing_candidates": {
            arm: copy.deepcopy(value) for arm, value in confirmation["candidates"].items()
            if value["status"] != "passed"
        } if confirmation else {},
        "stage1_budget_deferrals": copy.deepcopy(confirmation.get("budget_deferrals", {})) if confirmation else {},
        "source_bridge_sha256": bridge["sha256"] if bridge else None,
        "budget_input_sha256": digest(budget),
        "arm_order": order, "survivors": survivors, "target_arm": target_arm,
        "target_training_flops": float(target),
        "target_training_flops_fraction": [target.numerator, target.denominator],
        "rates": list(RATES), "tuning_seed": 0, "final_seeds": list(FINAL_SEEDS),
        "selection_metric": "val_loss_raw", "selection_curve_metric": "val_raw",
        "selection_rule": "minimum finite final validation loss; exact ties choose lower rate; all jobs terminal",
        "selection_sample": {"seed": 1234, "sequences": 1024, "tokens_per_sequence": 512},
        "final_sample": {"seed": 5678, "sequences": 1024, "tokens_per_sequence": 512},
        "headline_rule": {
            "softmax": "each seed: candidate <= 0.99 * min(rawS,convS)",
            "recurrent": "each seed: candidate <= min(GDN1,DP4)",
            "requires": "all three independent Stage-2 seeds and prior Stage-1 confirmation",
            "convP": "separate mechanism comparator; no useful composition gain claimed if not improved",
            "significance": "observed preregistered gate, not a statistical-significance claim",
        },
        "expected_configs": {"tuning": configs},
        "arms": {},
    }
    for arm in order:
        data = budget["arms"][arm]
        if any(data[key] != counts[arm][key] for key in ("forward_fpt", "training_fpt")):
            raise ProtocolError(f"budget counters are stale for {arm}")
        per_update = Fraction(str(counts[arm]["training_fpt"])) * BATCH_TOKENS
        steps = math.ceil(target / per_update)
        excess = steps * per_update - target
        if not 0 <= excess < per_update:
            raise ProtocolError("compute matching violated the one-update excess bound")
        tick, setup = data["forecast_seconds_per_update"], data["setup_seconds"]
        end = 240 if arm in survivors else 60
        main_wall = steps * tick + setup + end
        sweep_wall = SWEEP_STEPS * tick + setup + 30
        plan["arms"][arm] = {
            **counts[arm], "main_steps": steps, "main_tokens": steps * BATCH_TOKENS,
            "main_training_flops": float(steps * per_update),
            "excess_training_flops": float(excess), "excess_updates": float(excess / per_update),
            "main_wall_forecast_seconds": main_wall, "sweep_wall_forecast_seconds": sweep_wall,
            "main_timeout_seconds": math.ceil(1.3 * main_wall / 100) * 100,
            "sweep_timeout_seconds": math.ceil(1.3 * sweep_wall / 100) * 100,
        }
    plan["tuning_jobs"] = [
        {"arm": arm, "lr": lr, "job": make_job(plan, arm, "tuning", lr, 0)}
        for arm in order for lr in RATES
    ]
    spent = float(budget["spent_language_usd"])
    forecast = spent + sum(
        3 * RATE_PER_SECOND * (a["sweep_wall_forecast_seconds"] + a["main_wall_forecast_seconds"]
                              + 2 * RESOURCE_OVERHEAD_SECONDS)
        for a in plan["arms"].values()
    )
    maximum = spent + sum(
        3 * RATE_PER_SECOND * (a["sweep_timeout_seconds"] + a["main_timeout_seconds"]
                              + 2 * RESOURCE_OVERHEAD_SECONDS)
        for a in plan["arms"].values()
    )
    plan["budget"] = {
        "stage_cap_usd": 100, "already_spent_usd": spent,
        "forecast_total_usd": round(forecast, 6), "all_timeout_total_usd": round(maximum, 6),
        "rolling_reservations_required": maximum > 100,
        "rate_per_second": RATE_PER_SECOND, "resource_overhead_seconds_per_job": RESOURCE_OVERHEAD_SECONDS,
        "timeout_policy": "1.30 * (forecast updates + compilation + final work), rounded up to 100 seconds",
        "notes": "15% conv runtime allowance and 30s extra compile are in budget inputs; no stage transfers",
    }
    return seal(plan)


def verify_plan(plan):
    check_seal(plan)
    if (plan.get("schema"), plan.get("schema_version")) != ("beyond_language_plan", 1):
        raise ProtocolError("unsupported language plan")
    if plan.get("status") != "frozen":
        raise ProtocolError("draft plans cannot export jobs or select rates")
    if plan.get("planner_sha256") != digest(Path(__file__).read_bytes()):
        raise ProtocolError("language planner source differs from the frozen plan")
    if plan.get("gate_policy_adapter_sha256") != digest(Path(__file__).with_name("beyond_gate_reconciliation.py").read_bytes()):
        raise ProtocolError("gate policy adapter source differs from the frozen plan")
    if plan.get("stage1_active_gate_policy") != RECONCILIATION_POLICY_ID:
        raise ProtocolError("frozen language plan lacks the recognized Stage-1 gate policy")
    try:
        metadata = reconciliation_adapter().validate_reconciliation_metadata(plan.get("stage1_gate_reconciliation"))
    except (ValueError, TypeError, KeyError) as exc:
        raise ProtocolError(f"frozen language plan has invalid gate provenance: {exc}") from exc
    if metadata.get("original_protocol_id") != STAGE1_PROTOCOL_ID:
        raise ProtocolError("frozen language plan changed the original Stage-1 protocol")
    for key, length in (("stage1_confirmation_sha256", 64), ("evidence_commit", 40)):
        value = plan.get(key)
        if not isinstance(value, str) or len(value) != length or any(c not in "0123456789abcdef" for c in value):
            raise ProtocolError(f"frozen plan lacks valid {key}")
    if plan["rates"] != list(RATES) or plan["final_seeds"] != list(FINAL_SEEDS):
        raise ProtocolError("rates/seeds differ from the registered protocol")
    if plan.get("model_source_hashes") != model_sources(plan["source_hashes"]):
        raise ProtocolError("frozen model source subset differs from full source map")
    expected = [(arm, lr) for arm in plan["arm_order"] for lr in RATES]
    if [(row["arm"], row["lr"]) for row in plan["tuning_jobs"]] != expected:
        raise ProtocolError("tuning grid differs from the complete registered grid")
    for row in plan["tuning_jobs"]:
        if row["job"] != make_job(plan, row["arm"], "tuning", row["lr"], 0):
            raise ProtocolError("tuning job identity differs from its declared plan")


def expected_config(plan, arm, phase, lr, seed):
    cfg = dict(plan["expected_configs"]["tuning"][arm])
    cfg.update(lr=lr, seed=seed)
    if phase == "final":
        cfg.update(steps=plan["arms"][arm]["main_steps"], warmup=400, evals=16,
                   vbig=1024, save_final=1, ablations=int(arm in plan["survivors"]))
    return cfg


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_failure(result):
    return bool(result.get("error") or result.get("failure") or result.get("nonfinite_fields"))


def validate_result_identity(plan, job, result, config):
    for key, expected in (
        ("job_id", job["id"]), ("script", "lm.py"), ("argv", job["argv"]),
        ("source_hashes", plan["source_hashes"]), ("gpu_requested", "H100"),
    ):
        if result.get(key) != expected:
            raise ProtocolError(f"{job['id']}: result {key} mismatch")
    if result.get("config") is not None and digest(result["config"]) != digest(config):
        raise ProtocolError(f"{job['id']}: full result config mismatch")
    if not is_failure(result):
        if result.get("config") is None or digest(result["config"]) != digest(config):
            raise ProtocolError(f"{job['id']}: successful result missing its full config")
        if result.get("installed_versions") != plan["runtime_versions"]:
            raise ProtocolError(f"{job['id']}: runtime version mismatch")
        for key in ("arch", "lr", "seed", "steps"):
            if result.get(key) != config[key]:
                raise ProtocolError(f"{job['id']}: duplicated {key} disagrees with config")


def verify_manifests(plan, manifests):
    expected = {entry["job"]["id"]: entry["job"] for entry in plan["tuning_jobs"]}
    seen = {}
    for manifest in manifests:
        check_seal(manifest)
        if manifest.get("stage") != "language" or manifest.get("source_hashes") != plan["source_hashes"]:
            raise ProtocolError("manifest stage/source mismatch")
        if manifest.get("runtime_versions") != plan["runtime_versions"]:
            raise ProtocolError("manifest runtime mismatch")
        for job in manifest["jobs"]:
            if job["id"] in seen or expected.get(job["id"]) != job:
                raise ProtocolError("duplicate, unexpected, or modified tuning manifest job")
            seen[job["id"]] = manifest
    if set(seen) != set(expected):
        raise ProtocolError("manifests must cover the complete registered tuning grid")
    return seen


def select_rates(plan, manifests, results):
    verify_plan(plan)
    membership = verify_manifests(plan, manifests)
    rows, pending = [], []
    for entry in plan["tuning_jobs"]:
        arm, lr, job = entry["arm"], entry["lr"], entry["job"]
        result = results.get(job["id"])
        row = {"arm": arm, "lr": lr, "job_id": job["id"], "validation_loss_raw": None}
        if result is None:
            pending.append(job["id"])
            rows.append({**row, "status": "pending"})
            continue
        cfg = expected_config(plan, arm, "tuning", lr, 0)
        validate_result_identity(plan, job, result, cfg)
        manifest = membership[job["id"]]
        if result.get("manifest_sha256") != manifest["sha256"] or result.get("manifest") != manifest["name"]:
            raise ProtocolError("result manifest provenance mismatch")
        error = result.get("error") or result.get("failure")
        if error or result.get("nonfinite_fields"):
            rows.append({**row, "status": "invalid", "reason": str(error or result["nonfinite_fields"])})
            continue
        value = result.get("val_loss_raw")
        curve = result.get("curve") or []
        valid = (
            finite_number(value) and value >= 0 and curve
            and curve[-1].get("step") == SWEEP_STEPS
            and curve[-1].get("val_raw") == value
            and result.get("tokens") == SWEEP_STEPS * BATCH_TOKENS
            and result.get("flops_per_token") == plan["arms"][arm]["forward_fpt"]
            and result.get("train_flops_per_token") == plan["arms"][arm]["training_fpt"]
            and result.get("train_flops") == plan["arms"][arm]["training_fpt"] * SWEEP_STEPS * BATCH_TOKENS
        )
        if not valid:
            rows.append({**row, "status": "invalid",
                         "reason": "missing/nonfinite unrounded final validation or incomplete/counter-mismatched run"})
            continue
        rows.append({**row, "status": "valid", "validation_loss_raw": value})
    selected, invalid = {}, []
    if not pending:
        for arm in plan["arm_order"]:
            valid = [r for r in rows if r["arm"] == arm and r["status"] == "valid"]
            if not valid:
                invalid.append(arm)
                continue
            winner = min(valid, key=lambda r: (r["validation_loss_raw"], r["lr"]))
            selected[arm] = {k: winner[k] for k in ("lr", "job_id", "validation_loss_raw")}
    return seal({
        "schema": "beyond_language_rate_selection", "schema_version": 1,
        "plan_sha256": plan["sha256"], "source_hashes": plan["source_hashes"],
        "manifest_sha256s": sorted(m["sha256"] for m in manifests),
        "status": "pending" if pending else ("invalid" if invalid else "selected"),
        "selection_metric": "val_loss_raw", "rows": rows, "selected": selected,
        "pending_job_ids": pending, "invalid_arms": invalid,
        "note": "Only training-seed-0 final validation on sample seed 1234 selects rates; final/test/ablation fields are never read.",
    })


def final_jobs(plan, selection, seed):
    verify_plan(plan)
    check_seal(selection)
    if selection.get("schema") != "beyond_language_rate_selection" or selection.get("status") != "selected":
        raise ProtocolError("a complete valid rate-selection artifact is required")
    if selection.get("plan_sha256") != plan["sha256"] or selection.get("source_hashes") != plan["source_hashes"]:
        raise ProtocolError("selection belongs to another source/protocol")
    if set(selection["selected"]) != set(plan["arm_order"]) or seed not in FINAL_SEEDS:
        raise ProtocolError("selection arms or final seed differ from protocol")
    for arm, selected in selection["selected"].items():
        valid = [r for r in selection["rows"] if r["arm"] == arm and r["status"] == "valid"]
        expected = min(valid, key=lambda r: (r["validation_loss_raw"], r["lr"]))
        if selected != {k: expected[k] for k in ("lr", "job_id", "validation_loss_raw")}:
            raise ProtocolError("selected rates disagree with the recorded validation-only rule")
    return [make_job(plan, arm, "final", selection["selected"][arm]["lr"], seed)
            for arm in plan["arm_order"]]


def require_prior_seed_blocks(plan, selection, seed, results):
    for earlier in FINAL_SEEDS:
        if earlier >= seed:
            break
        for arm, job in zip(plan["arm_order"], final_jobs(plan, selection, earlier)):
            result = results.get(job["id"])
            if result is None:
                raise ProtocolError(f"seed {earlier} block is not terminal: missing {job['id']}")
            cfg = expected_config(plan, arm, "final", selection["selected"][arm]["lr"], earlier)
            validate_result_identity(plan, job, result, cfg)
            if not is_failure(result) and (result.get("curve") or [{}])[-1].get("step") != cfg["steps"]:
                raise ProtocolError("earlier final job is not at its terminal step")


def read_results(directory):
    records = {}
    for path in sorted(Path(directory).glob("*.json")):
        value = json.loads(path.read_text())
        job_id = value.get("job_id", path.stem)
        if job_id in records:
            raise ProtocolError(f"duplicate result id {job_id}")
        records[job_id] = value
    return records


def table(plan):
    lines = [
        f"Status: {plan['status']}; survivors: {', '.join(plan['survivors'])}; final seeds: 1, 2, 3.",
        f"Common training FLOPs/run: {plan['target_training_flops']:.15g}.",
        "",
        "| Arm | Forward FLOPs/token | Training FLOPs/token | Main updates | Main tokens | Excess updates | Sweep timeout | Main timeout |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in plan["arm_order"]:
        a = plan["arms"][arm]
        lines.append(f"| {arm} | {a['forward_fpt']} | {a['training_fpt']} | {a['main_steps']} | "
                     f"{a['main_tokens']} | {a['excess_updates']:.6f} | "
                     f"{a['sweep_timeout_seconds']}s | {a['main_timeout_seconds']}s |")
    b = plan["budget"]
    lines += ["", f"Forecast including earlier language spend: ${b['forecast_total_usd']:.2f}; "
              f"aggregate timeout maximum: ${b['all_timeout_total_usd']:.2f}.",
              "All arms receive three fresh 3,051-update seed-0 rate trials; finals start fresh.",
              "Inference ablations and final losses never select rates or additional runs."]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", help="research directory (default: detected from cwd or this file)")
    commands = parser.add_subparsers(dest="command", required=True)
    for mode in ("draft", "freeze"):
        sub = commands.add_parser(mode)
        sub.add_argument("--budget", required=True)
        sub.add_argument("--out", required=True)
        if mode == "draft":
            sub.add_argument("--survivors", required=True)
        else:
            sub.add_argument("--confirmation", required=True)
            sub.add_argument("--source-bridge")
            sub.add_argument("--evidence-commit", default="HEAD")
    sub = commands.add_parser("select")
    sub.add_argument("--plan", required=True)
    sub.add_argument("--plan-commit", default="HEAD")
    sub.add_argument("--manifest", action="append", required=True)
    sub.add_argument("--results-dir", required=True)
    sub.add_argument("--out", required=True)
    sub = commands.add_parser("export")
    sub.add_argument("--plan", required=True)
    sub.add_argument("--plan-commit", default="HEAD")
    sub.add_argument("--phase", choices=("tuning", "final"), required=True)
    sub.add_argument("--selection")
    sub.add_argument("--selection-commit", default="HEAD")
    sub.add_argument("--seed", type=int, choices=FINAL_SEEDS)
    sub.add_argument("--results-dir", help="result directory (default: RESEARCH_ROOT/results/beyond_runs)")
    sub.add_argument("--out", required=True)
    sub = commands.add_parser("table")
    sub.add_argument("--plan", required=True)
    args = parser.parse_args()
    root = Path(args.research_root).resolve() if args.research_root else default_research_root()
    if args.command in ("draft", "freeze"):
        budget = json.loads(Path(args.budget).read_text())
        confirmation = bridge = commit = None
        if args.command == "freeze":
            commit = git(root, "rev-parse", args.evidence_commit).decode().strip()
            confirmation = committed_file(root, args.confirmation, commit)
            if args.source_bridge:
                bridge = committed_file(root, args.source_bridge, commit)
                verify_bridge_commits(root, bridge)
            if git(root, "show", f"{commit}:research/BEYOND.md") != (root / "BEYOND.md").read_bytes():
                raise ProtocolError("commit the language registration before freezing")
            survivors = confirmation["passed_candidates"]
        else:
            survivors = args.survivors.split(",")
        plan = build_plan(root, survivors, budget, confirmation=confirmation,
                          bridge=bridge, evidence_commit=commit)
        write_immutable(args.out, plan)
        print(table(plan))
    elif args.command == "select":
        plan = committed_file(root, args.plan, args.plan_commit)
        manifests = [json.loads(Path(p).read_text()) for p in args.manifest]
        for manifest in manifests:
            verify_manifest_registration(root, plan, manifest)
        result = select_rates(plan, manifests, read_results(args.results_dir))
        print(json.dumps({"status": result["status"], "selected": result["selected"],
                          "pending": result["pending_job_ids"], "invalid": result["invalid_arms"]}, indent=2))
        if result["status"] == "pending":
            raise SystemExit(2)  # Do not occupy the immutable selection path prematurely.
        write_immutable(args.out, result)
    elif args.command == "export":
        plan = committed_file(root, args.plan, args.plan_commit)
        verify_plan(plan)
        if sources(root) != plan["source_hashes"]:
            raise ProtocolError("research source map changed since the frozen plan")
        if digest(language_registration((root / "BEYOND.md").read_text())) != plan["language_registration_sha256"]:
            raise ProtocolError("language registration changed since the frozen plan")
        if args.phase == "tuning":
            jobs = [entry["job"] for entry in plan["tuning_jobs"]]
        else:
            if not args.selection or args.seed is None:
                raise ProtocolError("final export requires committed --selection and --seed")
            selection = committed_file(root, args.selection, args.selection_commit)
            results_dir = Path(args.results_dir) if args.results_dir else root / "results" / "beyond_runs"
            require_prior_seed_blocks(plan, selection, args.seed, read_results(results_dir))
            jobs = final_jobs(plan, selection, args.seed)
        raw = [{k: j[k] for k in ("script", "argv", "gpu", "max_seconds", "attempt")} for j in jobs]
        write_immutable(args.out, raw)
        print(json.dumps({"jobs": len(jobs), "phase": args.phase, "seed": args.seed,
                          "max_reserved_usd": sum(j["reserved_usd"] for j in jobs)}))
    else:
        plan = json.loads(Path(args.plan).read_text())
        check_seal(plan)
        print(table(plan))


if __name__ == "__main__":
    main()
