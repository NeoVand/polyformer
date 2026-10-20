"""Prospective Stage-1 written-rule adapter; this file does not adopt the policy.

The original immutable selection remains unchanged. A separately sealed result
retains its strict-code outcome while deriving the disclosed written-rule outcome.
No model/test results are loaded; only already-selected final-validation records
in the frozen selection can affect a gate. Root must register this policy before
any corresponding independent confirmations, if it decides to adopt it.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile


POLICY = {
    "name": "beyond-stage1-written-rule-reconciliation-v1",
    "schema": 1,
    "scope": "Uniformly all A/B/C candidates and all six registered primary cells.",
    "retrieval_threshold": 0.90,
    "word_threshold": 0.95,
    "maximum_reference_gap": 0.03,
    "threshold_tolerance": 1e-12,
    "written_rule": "candidate >= threshold AND candidate + 0.03 >= reference",
    "strict_code_rule": "written_rule AND reference >= threshold",
    "reference_requirement": "Frozen selected reference must be ready, COMPLETE, finite, and in [0,1]; pending/missing/invalid references never pass.",
    "candidate_requirement": "Frozen selected candidate must be ready, COMPLETE, finite, and in [0,1].",
    "change": "Remove only the numeric reference-floor veto; retain absolute candidate thresholds, reference gap, and all-six-cells requirement.",
    "unchanged": ["selected rates", "selected reference identities", "model source hashes",
                  "training protocol", "confirmation seeds", "candidate priority",
                  "budgets", "evaluation definitions"],
    "disclosure": "Prospective code/text reconciliation after seed0 results; original executable outcomes remain reported separately. Fresh confirmation does not retroactively pass the original executable rule.",
}
PRIMARY_CELLS = (
    ("wp_s5_16", 1), ("wp_a5_16", 1),
    ("mqar_small", 2), ("induction_small", 2),
    ("wp_s5_16", 2), ("wp_a5_16", 2),
)
PRIORITY = ("B", "C", "A")
ORIGINAL_CONFIRMATION_STATUS = "unconfirmed; seed0 selection does not establish a three-seed pass"
REGISTRATION_HEADING = "## 4.1. Written-rule reconciliation before independent confirmation"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


POLICY_ID = digest(POLICY)


def repository_root():
    return Path(__file__).resolve().parents[2]


def validate_registration_commit(registration_commit, repository=None):
    """Require a full SHA that identifies an existing committed Git object.

    Git existence does not itself prove that registration preceded a run; the
    registered document and experiment timeline provide that evidence.
    """
    if not isinstance(registration_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", registration_commit):
        raise ValueError("registration_commit must be the full lowercase Git commit SHA of the prospective registration")
    repo = Path(repository) if repository is not None else repository_root()
    check = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", registration_commit + "^{commit}"],
        capture_output=True, text=True, check=False,
    )
    if check.returncode or check.stdout.strip() != registration_commit:
        raise ValueError("registration_commit must identify an existing committed Git object in the supplied repository")
    document = subprocess.run(
        ["git", "-C", str(repo), "show", registration_commit + ":research/BEYOND.md"],
        capture_output=True, text=True, check=False,
    )
    if document.returncode or REGISTRATION_HEADING not in document.stdout or POLICY_ID not in document.stdout:
        raise ValueError("registration commit must contain BEYOND.md section4.1 and the exact reconciliation policy ID")
    return registration_commit


def validate_reconciliation_metadata(metadata, repository=None):
    """Validate reusable provenance copied into confirmation/language artifacts."""
    if not isinstance(metadata, dict):
        raise ValueError("gate_reconciliation metadata is required")
    if metadata.get("policy") != POLICY or metadata.get("policy_id") != POLICY_ID or digest(metadata["policy"]) != POLICY_ID:
        raise ValueError("reconciliation policy contents and identity must exactly match the registered policy")
    validate_registration_commit(metadata.get("registration_commit"), repository)
    if not re.fullmatch(r"[0-9a-f]{64}", str(metadata.get("original_selection_sha256", ""))):
        raise ValueError("the original selection seal must be retained")
    if not re.fullmatch(r"[0-9a-f]{64}", str(metadata.get("original_protocol_id", ""))):
        raise ValueError("the original protocol identity must be retained")
    return metadata


def validate_reconciliation(selection, repository=None):
    """Validate provenance, original seal and exact derivation; return metadata."""
    if not isinstance(selection, dict) or digest({k: v for k, v in selection.items() if k != "sha256"}) != selection.get("sha256"):
        raise ValueError("reconciled selection seal does not match its contents")
    metadata = validate_reconciliation_metadata(selection.get("gate_reconciliation"), repository)
    if metadata.get("original_protocol_id") != selection.get("protocol_id") or digest(selection.get("protocol")) != selection.get("protocol_id"):
        raise ValueError("the original protocol identity must be retained")
    if not isinstance(selection.get("strict_code_seed0_gates"), dict) or not isinstance(selection.get("strict_code_survivors"), list):
        raise ValueError("the original strict-code gates and survivors must be retained")
    original = copy.deepcopy(selection)
    for name in ("sha256", "gate_reconciliation", "strict_code_seed0_gates", "strict_code_survivors"):
        original.pop(name)
    original["seed0_gates"] = copy.deepcopy(selection["strict_code_seed0_gates"])
    original["survivors"] = copy.deepcopy(selection["strict_code_survivors"])
    original["confirmation_status"] = ORIGINAL_CONFIRMATION_STATUS
    original["sha256"] = digest(original)
    if original["sha256"] != metadata["original_selection_sha256"]:
        raise ValueError("reconstructed original selection does not match its retained immutable seal")
    expected = reconcile(original, metadata["registration_commit"], repository)
    if expected != selection:
        raise ValueError("derived selection is not the exact registered reconciliation of its original")
    return metadata


def finite_score(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def at_least(value, threshold):
    return finite_score(value) and value >= threshold - POLICY["threshold_tolerance"]


def key(task, depth, arm=None):
    return f"{task}/L{depth}" + (f"/{arm}" if arm else "")


def measurement(item):
    """Interpret only a frozen selected final-validation record."""
    if not isinstance(item, dict):
        return "pending", None
    state = item.get("state", "pending")
    if state.startswith("pending"):
        return "pending", None
    row = item.get("selected")
    if state != "ready" or not isinstance(row, dict) or row.get("status") != "COMPLETE":
        return "invalid", None
    score = row.get("score")
    if not finite_score(score):
        return "invalid", None
    return "ready", score


def reconcile(selection, registration_commit, repository=None):
    """Return a new sealed artifact; never mutate or rewrite the original."""
    validate_registration_commit(registration_commit, repository)
    if not isinstance(selection, dict) or "sha256" not in selection:
        raise ValueError("a sealed original selection artifact is required")
    original_sha = selection["sha256"]
    if digest({k: v for k, v in selection.items() if k != "sha256"}) != original_sha:
        raise ValueError("original selection seal does not match its contents")
    if "gate_reconciliation" in selection:
        raise ValueError("an already reconciled selection cannot be reconciled again")
    protocol = selection.get("protocol", {})
    if digest(protocol) != selection.get("protocol_id"):
        raise ValueError("original protocol identity does not match its contents")
    expected = {
        "retrieval_threshold": 0.90, "word_threshold": 0.95,
        "reference_margin": 0.03, "threshold_tolerance": 1e-12,
        "confirm_seeds": [1, 2, 3],
    }
    if any(protocol.get(name) != value for name, value in expected.items()):
        raise ValueError("the original protocol differs from this narrow reconciliation policy")
    if tuple(map(tuple, protocol.get("primary_cells", []))) != PRIMARY_CELLS:
        raise ValueError("the original six primary cells changed")
    if tuple(protocol.get("confirmation_priority", [])) != PRIORITY:
        raise ValueError("the original candidate priority changed")
    if not isinstance(selection.get("selected"), dict) or not isinstance(selection.get("references"), dict):
        raise ValueError("frozen selected rates and references are required")
    if not isinstance(selection.get("seed0_gates"), dict) or not isinstance(selection.get("survivors"), list):
        raise ValueError("original strict-code gates and survivors must be retained")
    if selection.get("confirmation_status") != ORIGINAL_CONFIRMATION_STATUS:
        raise ValueError("original confirmation status differs from the frozen unconfirmed selection schema")

    output = copy.deepcopy(selection)
    output.pop("sha256")
    output["strict_code_seed0_gates"] = copy.deepcopy(selection["seed0_gates"])
    output["strict_code_survivors"] = copy.deepcopy(selection["survivors"])
    output["gate_reconciliation"] = {
        "policy_id": POLICY_ID,
        "policy": copy.deepcopy(POLICY),
        "registration_commit": registration_commit,
        "original_selection_sha256": original_sha,
        "original_protocol_id": selection["protocol_id"],
        "adoption_scope": "Only confirmations prospectively registered under this sealed reconciliation; no retrospective change to the strict-code outcome.",
    }
    gates = {}
    for arm in PRIORITY:
        cells = {}
        for task, depth in PRIMARY_CELLS:
            candidate = selection["selected"].get(key(task, depth, arm))
            reference = selection["references"].get(key(task, depth))
            candidate_state, score = measurement(candidate)
            reference_state, ref_score = measurement(reference)
            threshold = POLICY["word_threshold"] if task.startswith("wp_") else POLICY["retrieval_threshold"]
            status, reason = "pending", "candidate or reference selection is pending"
            if candidate_state == "invalid":
                status, reason = "fail", "no valid completed selected candidate measurement"
            elif candidate_state == "ready" and not at_least(score, threshold):
                status, reason = "fail", "candidate is below the unchanged absolute threshold"
            elif reference_state == "invalid":
                status, reason = "no_valid_reference", "missing or invalid references cannot establish a comparison"
            elif candidate_state == reference_state == "ready":
                # Do not use at_least(score + margin,...): a legitimate sum may exceed1.
                status = "pass" if score + POLICY["maximum_reference_gap"] >= ref_score - POLICY["threshold_tolerance"] else "fail"
                reason = "written-rule inequalities hold" if status == "pass" else "candidate is more than 3 percentage points below the frozen reference"
            row = reference.get("selected") if isinstance(reference, dict) else None
            cells[key(task, depth)] = {
                "status": status, "reason": reason, "validation": score,
                "reference_validation": ref_score, "absolute_threshold": threshold,
                "maximum_reference_gap": POLICY["maximum_reference_gap"],
                "reference_arm": row.get("arm") if isinstance(row, dict) else None,
                "reference_floor_required": False,
            }
        statuses = [cell["status"] for cell in cells.values()]
        state = ("rejected" if "fail" in statuses else "screen_passed_unconfirmed"
                 if all(value == "pass" for value in statuses) else "pending")
        gates[arm] = {"status": state, "cells": cells}
    output["seed0_gates"] = gates
    output["survivors"] = [arm for arm in PRIORITY if gates[arm]["status"] == "screen_passed_unconfirmed"]
    output["confirmation_status"] = "unconfirmed; reconciled seed0 selection does not establish independent confirmation or retroactively pass the strict-code rule"
    output["sha256"] = digest(output)
    # Explicit invariants guard against turning a gate adapter into a reselection.
    for field in ("protocol", "protocol_id", "selected", "references", "model_source_hashes"):
        if output.get(field) != selection.get(field):
            raise AssertionError(f"reconciliation changed frozen {field}")
    return output


def self_test(protocol_path, fixture_repository, registration):
    spec = importlib.util.spec_from_file_location("beyond_frozen_protocol", protocol_path)
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    task, depth = PRIMARY_CELLS[0]
    # The committed object belongs to an isolated unit-test repository, never
    # the research registration or a production selection artifact.
    def derive(value):
        return reconcile(value, registration, fixture_repository)

    def result(job, score):
        args, settings = p.parse_argv(job["argv"])
        cfg = {**settings, **{name: args[name] for name in ("arch", "d", "heads", "layers", "mlp", "pos")}}
        return {"config": cfg, "validation": {"acc": score, "bal_late": score}}

    records = []
    for job in p.initial_jobs():
        t, d, arm, _, _, _ = p.identify_job(job)
        score = .94 if (t, d) == (task, depth) and arm in p.WORD_REFERENCES else 1.0
        records.append(p.make_record(job, result(job, score)))
    for job in p.alternate_jobs(records):
        records.append(p.make_record(job, result(job, .94)))
    original = p.select(records, {"lm.py": "synthetic-source-identity"})
    snapshot = copy.deepcopy(original)
    derived = derive(original)
    assert validate_reconciliation(derived, fixture_repository) == derived["gate_reconciliation"]
    assert original == snapshot
    assert original["survivors"] == [] and derived["survivors"] == list(PRIORITY)
    assert original["seed0_gates"]["A"]["cells"][key(task, depth)]["status"] == "no_positive_control"
    assert derived["strict_code_seed0_gates"] == original["seed0_gates"]
    assert derived["strict_code_survivors"] == original["survivors"]
    assert len(p.confirmation_jobs(derived, "all")) == 72
    for field in ("selected", "references", "model_source_hashes", "protocol", "protocol_id"):
        assert derived[field] == original[field]

    def reseal(value):
        value.pop("sha256", None)
        value["sha256"] = digest(value)
        return value

    missing = copy.deepcopy(original)
    missing["references"].pop(key(task, depth))
    missing = derive(reseal(missing))
    assert not missing["survivors"]
    assert missing["seed0_gates"]["A"]["cells"][key(task, depth)]["status"] == "pending"
    pending = copy.deepcopy(original)
    pending["references"][key(task, depth)] = {"state": "pending", "selected": None}
    assert not derive(reseal(pending))["survivors"]
    invalid = copy.deepcopy(original)
    invalid["references"][key(task, depth)]["selected"]["score"] = float("nan")
    assert not derive(reseal(invalid))["survivors"]
    failed = copy.deepcopy(original)
    failed["selected"][key(task, depth, "A")]["selected"]["score"] = .949
    failed = derive(reseal(failed))
    assert failed["seed0_gates"]["A"]["status"] == "rejected"
    assert "A" not in failed["survivors"]
    margin = copy.deepcopy(original)
    other_task, other_depth = PRIMARY_CELLS[1]
    margin["selected"][key(other_task, other_depth, "A")]["selected"]["score"] = .96
    assert derive(reseal(margin))["seed0_gates"]["A"]["status"] == "rejected"
    missing_candidate = copy.deepcopy(original)
    missing_candidate["selected"].pop(key(other_task, other_depth, "A"))
    assert "A" not in derive(reseal(missing_candidate))["survivors"]
    incomplete_reference = copy.deepcopy(original)
    incomplete_reference["references"][key(task, depth)]["selected"]["status"] = "PENDING"
    assert not derive(reseal(incomplete_reference))["survivors"]
    # Test fields have no influence on decisions.
    extra = copy.deepcopy(original)
    for row in extra["selected"].values():
        if row["selected"]:
            row["selected"]["test"] = {"bal_late": -100, "acc": float("nan")}
    extra = derive(reseal(extra))
    assert extra["seed0_gates"] == derived["seed0_gates"] and extra["survivors"] == derived["survivors"]
    for name, value in (("modified seal", {**original, "survivors": ["A"]}),
                        ("repeat reconciliation", derived)):
        try:
            derive(value)
        except ValueError:
            pass
        else:
            raise AssertionError(name)
    changed_policy = copy.deepcopy(derived)
    changed_policy["gate_reconciliation"]["policy"]["word_threshold"] = .94
    invalid_metadata = copy.deepcopy(derived)
    invalid_metadata["gate_reconciliation"]["registration_commit"] = "f" * 40
    forged_strict = copy.deepcopy(derived)
    forged_strict["strict_code_survivors"] = ["A"]
    forged_rate = copy.deepcopy(derived)
    forged_rate["selected"][key(task, depth, "A")]["selected"]["lr"] = .123
    forged_derived_gate = copy.deepcopy(derived)
    forged_derived_gate["seed0_gates"]["A"]["status"] = "rejected"
    for name, value in (("changed policy", changed_policy),
                        ("uncommitted registration", invalid_metadata),
                        ("forged original strict survivors", forged_strict),
                        ("forged selected rate", forged_rate),
                        ("forged derived gate", forged_derived_gate)):
        try:
            validate_reconciliation(reseal(value), fixture_repository)
        except ValueError:
            pass
        else:
            raise AssertionError(name)
    for invalid_sha in (registration[:7], "f" * 40):
        try:
            reconcile(original, invalid_sha, fixture_repository)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid registration SHA accepted")
    return {"status": "pass", "policy_id": POLICY_ID, "checks": [
        "candidate100/reference94 strict/reconciled divergence", "original unchanged and strict outcomes retained",
        "same rates/references/protocol/source identity", "72 compatible frozen confirmation jobs",
        "missing/pending/nonfinite reference never passes", "candidate below absolute floor fails",
        "unchanged3pp margin and all-six-cells requirement", "incomplete reference rejected",
        "test-field independence", "immutable seal validation", "no repeated reconciliation",
        "exact policy contents checked independently of claimed policy ID",
        "full existing commit required; abbreviated and uncommitted SHA rejected",
        "committed registration document must contain section4.1 and exact policy ID",
        "original seal reconstructed; forged strict outcomes and rates rejected",
        "exact derivation checked; forged reconciled gates rejected"],
        "adoption_status": "isolated synthetic fixture only; no production selection derived",
        "registration_fixture": "temporary Git repository containing one committed unit-test registration"}


def run_self_test(protocol_path):
    with tempfile.TemporaryDirectory(prefix="beyond-gate-reconciliation-") as directory:
        repo = Path(directory)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "research").mkdir()
        (repo / "research/BEYOND.md").write_text(
            REGISTRATION_HEADING + "\n\nSynthetic policy fixture; not research adoption.\n\n" + POLICY_ID + "\n"
        )
        subprocess.run(["git", "-C", str(repo), "add", "research/BEYOND.md"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.name=Unit Test", "-c", "user.email=test@example.invalid",
             "-c", "commit.gpgsign=false", "commit", "-q", "-m", "Synthetic registration fixture"],
            check=True,
        )
        registration = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True,
        ).strip()
        result = self_test(protocol_path, repo, registration)
    result["adapter_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["protocol_sha256"] = hashlib.sha256(Path(protocol_path).read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    test = commands.add_parser("self-test")
    test.add_argument("--protocol", type=Path, default=repository_root() / "research/beyond_protocol.py")
    test.add_argument("--output", type=Path)
    derive = commands.add_parser("reconcile")
    derive.add_argument("--selection", type=Path, required=True)
    derive.add_argument("--registration-commit", required=True)
    derive.add_argument("--repository", type=Path, default=repository_root())
    derive.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "self-test":
        report = json.dumps(run_self_test(args.protocol), indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report)
        print(report, end="")
        return
    if args.output.resolve() == args.selection.resolve():
        parser.error("output must be separate from the immutable original selection")
    if args.output.exists():
        parser.error("refusing to overwrite an existing reconciliation artifact")
    original = json.loads(args.selection.read_text())
    derived = reconcile(original, args.registration_commit, args.repository)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(derived, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(args.output), "sha256": derived["sha256"],
                      "policy_id": POLICY_ID, "strict_code_survivors": derived["strict_code_survivors"],
                      "reconciled_survivors": derived["survivors"]}, indent=2))


if __name__ == "__main__":
    main()
