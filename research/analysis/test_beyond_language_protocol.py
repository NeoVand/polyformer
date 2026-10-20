"""CPU-only tests for frozen planning, source identity, and held-out selection."""

import copy
from fractions import Fraction
import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("protocol", HERE / "beyond_language_protocol.py")
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)
ROOT = HERE.parent
BUDGET = json.loads((ROOT / "results" / "beyond_language_planning" / "budget.json").read_text())
DATASET_PATH = ROOT / "results" / "beyond_language_planning" / "dataset.json"
DATASET = json.loads(DATASET_PATH.read_text())
DATA_SPEC = importlib.util.spec_from_file_location("fingerprint", HERE / "beyond_dataset_fingerprint.py")
fingerprint = importlib.util.module_from_spec(DATA_SPEC)
DATA_SPEC.loader.exec_module(fingerprint)
REGISTRATION_COMMIT = "445048e487906265c99a135e08ccedea39a03230"
ORIGINAL_SELECTION = json.loads(p.git(ROOT, "show", f"{REGISTRATION_COMMIT}:{p.STRICT_SELECTION_PATH}"))


def fixture_plan():
    plan = p.build_plan(ROOT, ["B", "C"], BUDGET, dataset=DATASET, dataset_path=DATASET_PATH)
    confirmation = confirmation_for(plan)
    # Synthetic sealed provenance for pure-function tests; production CLI
    # separately requires committed evidence and an audited source bridge.
    return p.seal({**plan, "status": "frozen", "evidence_commit": "a" * 40,
                   "stage1_confirmation_sha256": confirmation["sha256"],
                   "stage1_gate_reconciliation": confirmation["gate_reconciliation"],
                   "stage1_active_gate_policy": confirmation["active_gate_policy"],
                   "stage1_strict_code_candidates": confirmation["strict_code_candidates"],
                   "stage1_strict_code_passed_candidates": confirmation["strict_code_passed_candidates"],
                   "stage1_strict_code_seed0_survivors": confirmation["strict_code_seed0_survivors"]})


def manifest_for(plan):
    return p.seal({
        "schema": 1, "name": "synthetic_tuning", "stage": "language",
        "source_hashes": plan["source_hashes"], "runtime_versions": plan["runtime_versions"],
        "jobs": [e["job"] for e in plan["tuning_jobs"]],
    })


def result_for(plan, arm, phase, rate, seed, manifest=None):
    job = p.make_job(plan, arm, phase, rate, seed)
    cfg = p.expected_config(plan, arm, phase, rate, seed)
    score = {0.002: 4.00000002, 0.004: 4.00000001, 0.008: 4.00000003}[rate]
    steps = cfg["steps"]
    row = {
        "job_id": job["id"], "argv": job["argv"], "script": "lm.py", "gpu_requested": "H100",
        "source_hashes": plan["source_hashes"], "installed_versions": plan["runtime_versions"],
        "config": cfg, "arch": cfg["arch"], "lr": rate, "seed": seed, "steps": steps,
        "tokens": steps * p.BATCH_TOKENS, "val_loss_raw": score, "val_loss": 4.0,
        "flops_per_token": plan["arms"][arm]["forward_fpt"],
        "train_flops_per_token": plan["arms"][arm]["training_fpt"],
        "train_flops": plan["arms"][arm]["training_fpt"] * steps * p.BATCH_TOKENS,
        "curve": [{"step": 1, "val_raw": 0.01}, {"step": steps, "val_raw": score}],
        "val_big_raw": 0.01 if rate == 0.008 else 999.0,
        "test": {"loss": -rate},
        "ablation_val_big_raw": {"composition": rate},
    }
    if manifest:
        row.update(manifest=manifest["name"], manifest_sha256=manifest["sha256"])
    return row


def results_for(plan, manifest):
    return {
        e["job"]["id"]: result_for(plan, e["arm"], "tuning", e["lr"], 0, manifest)
        for e in plan["tuning_jobs"]
    }


def confirmation_for(plan):
    def record(strict):
        policy = "strict_frozen_v1" if strict else p.RECONCILIATION_POLICY_ID
        cells = [{
            "task": task, "layers": layers, "seed": seed,
            "candidate": {"status": "complete", "test_score": 1.0},
            "reference": {"status": "complete", "test_score": 1.0},
            "gate": {"status": "passed", "floor": .95 if task.startswith("wp_") else .90,
                     "maximum_reference_gap": .03, "threshold_tolerance": 1e-12,
                     "reference_floor_required": strict, "gate_policy": policy},
        } for task, layers in p.PRIMARY_CELLS for seed in p.FINAL_SEEDS]
        return {"status": "passed", "cells": cells, "gate_policy": policy}
    return p.seal({
        "schema": "stage1_confirmation", "schema_version": 1,
        "protocol_id": p.STAGE1_PROTOCOL_ID,
        "model_source_hashes": plan["model_source_hashes"],
        "active_gate_policy": p.RECONCILIATION_POLICY_ID,
        "gate_reconciliation": {
            "policy_id": p.RECONCILIATION_POLICY_ID, "policy": p.reconciliation_adapter().POLICY,
            "registration_commit": REGISTRATION_COMMIT,
            "original_selection_sha256": ORIGINAL_SELECTION["sha256"],
            "original_protocol_id": p.STAGE1_PROTOCOL_ID,
            "adoption_scope": "Only confirmations prospectively registered under this sealed reconciliation; no retrospective change to the strict-code outcome.",
        },
        "candidates": {arm: record(False) for arm in ("B", "C")},
        "strict_code_candidates": {arm: record(True) for arm in ("B", "C")},
        "strict_code_passed_candidates": ["B", "C"],
        "strict_code_seed0_survivors": ORIGINAL_SELECTION["survivors"],
        "passed_candidates": ["B", "C"],
    })


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = fixture_plan()

    def setUp(self):
        self.plan = copy.deepcopy(type(self).plan)
        self.manifest = manifest_for(self.plan)
        self.results = results_for(self.plan, self.manifest)

    def select(self):
        return p.select_rates(self.plan, [self.manifest], self.results)

    def test_registered_compute_and_fresh_schedules(self):
        expected = dict(rawS=13542, convS=13533, convP=12535, B=12209,
                        C=12207, GDN1=13108, DP4=10278)
        self.assertEqual({a: x["main_steps"] for a, x in self.plan["arms"].items()}, expected)
        self.assertEqual(len(self.plan["tuning_jobs"]), 21)
        self.assertEqual(self.plan["final_seeds"], [1, 2, 3])
        self.assertAlmostEqual(self.plan["budget"]["forecast_total_usd"], 77.090639, places=5)
        self.assertLess(self.plan["budget"]["all_timeout_total_usd"], 100)
        self.assertTrue(all(0 <= a["rounding_excess_updates"] < 1 for a in self.plan["arms"].values()))
        self.assertTrue(all(self.plan["arms"][a]["added_updates"] == 0 for a in ("B", "C")))
        for arm in expected:
            cfg = p.expected_config(self.plan, arm, "tuning", .004, 0)
            self.assertEqual((cfg["steps"], cfg["warmup"], cfg["tokens"]), (3051, 305, 0))
            self.assertEqual((cfg["vseqs"], cfg["vbig"], cfg["evals"]), (1024, 0, 8))
            final = p.expected_config(self.plan, arm, "final", .004, 2)
            self.assertEqual((final["warmup"], final["tokens"], final["seed"]), (400, 0, 2))
            self.assertEqual((final["vseqs"], final["vbig"], final["evals"]), (1024, 1024, 16))
            self.assertEqual(final["save_final"], 1)
            self.assertEqual(final["ablations"], int(arm in ("B", "C")))

    def test_no_rounded_intermediate_or_final_score_leakage(self):
        result = self.select()
        self.assertEqual(result["status"], "selected")
        self.assertTrue(all(s["lr"] == .004 for s in result["selected"].values()))
        changed = copy.deepcopy(self.results)
        for r in changed.values():
            r["val_big_raw"] = -100000 * r["lr"]
            r["test"] = {"score": 10000 * r["lr"]}
            r["ablation_val_big_raw"] = {"composition": -9999}
            r["curve"][0]["val_raw"] = -99999 * r["lr"]
            r["val_loss"] = -99999 * r["lr"]
        second = p.select_rates(self.plan, [self.manifest], changed)
        self.assertEqual(result, second)

    def test_exact_tie_chooses_lower_rate(self):
        for r in self.results.values():
            r["val_loss_raw"] = r["curve"][-1]["val_raw"] = 3.25
        self.assertTrue(all(s["lr"] == .002 for s in self.select()["selected"].values()))

    def test_all_terminal_before_any_selection(self):
        del self.results[next(iter(self.results))]
        selected = self.select()
        self.assertEqual(selected["status"], "pending")
        self.assertFalse(selected["selected"])

    def test_invalid_rate_reported_and_cannot_win(self):
        entry = next(e for e in self.plan["tuning_jobs"] if e["arm"] == "B" and e["lr"] == .004)
        self.results[entry["job"]["id"]]["error"] = "bounded timeout"
        chosen = self.select()
        self.assertEqual(chosen["status"], "selected")
        self.assertEqual(chosen["selected"]["B"]["lr"], .002)
        self.assertTrue(any(r["status"] == "invalid" for r in chosen["rows"]))

    def test_explicit_early_numerical_failure_is_an_invalid_trial(self):
        entry = next(e for e in self.plan["tuning_jobs"] if e["arm"] == "C" and e["lr"] == .004)
        row = self.results[entry["job"]["id"]]
        row["failure"] = "nonfinite loss at update100"
        row["steps"] = 100
        row["curve"][-1]["step"] = 100
        chosen = self.select()
        self.assertEqual(chosen["status"], "selected")
        self.assertEqual(chosen["selected"]["C"]["lr"], .002)

    def test_nonfinite_or_missing_raw_never_uses_rounded_fallback(self):
        for entry in self.plan["tuning_jobs"]:
            if entry["arm"] == "DP4":
                r = self.results[entry["job"]["id"]]
                if entry["lr"] == .002:
                    r["val_loss_raw"] = float("nan")
                else:
                    del r["val_loss_raw"]
        chosen = self.select()
        self.assertEqual(chosen["status"], "invalid")
        self.assertEqual(chosen["invalid_arms"], ["DP4"])
        with self.assertRaises(p.ProtocolError):
            p.final_jobs(self.plan, chosen, 1)

    def test_source_and_config_corruption_fail_closed(self):
        key = next(iter(self.results))
        for field in ("source_hashes", "config", "argv", "job_id", "installed_versions",
                      "manifest_sha256", "train_flops_per_token"):
            bad = copy.deepcopy(self.results)
            if field == "source_hashes":
                bad[key][field]["lm.py"] = "f" * 64
            elif field == "config":
                bad[key][field]["vseqs"] = 128
            elif field == "argv":
                bad[key][field] += ["--tokens", "200000000"]
            elif field == "installed_versions":
                bad[key][field]["jax"] = "wrong"
            elif field == "train_flops_per_token":
                bad[key][field] = 1
                selected = p.select_rates(self.plan, [self.manifest], bad)
                self.assertTrue(any(r["status"] == "invalid" for r in selected["rows"]))
                continue
            else:
                bad[key][field] = "wrong"
            with self.subTest(field=field), self.assertRaises(p.ProtocolError):
                p.select_rates(self.plan, [self.manifest], bad)

    def test_manifest_must_cover_exact_grid(self):
        for mutate in ("missing", "duplicate", "source", "timeout"):
            m = copy.deepcopy(self.manifest)
            if mutate == "missing":
                m["jobs"].pop()
            elif mutate == "duplicate":
                m["jobs"].append(m["jobs"][0])
            elif mutate == "source":
                m["source_hashes"]["lm.py"] = "f" * 64
            else:
                m["jobs"][0]["max_seconds"] += 1
            with self.subTest(mutate=mutate), self.assertRaises(p.ProtocolError):
                p.select_rates(self.plan, [p.seal(m)], self.results)

    def test_final_blocks_both_rnns_and_independent_seeds(self):
        selection = self.select()
        all_ids = set()
        for seed in (1, 2, 3):
            jobs = p.final_jobs(self.plan, selection, seed)
            self.assertEqual(len(jobs), 7)
            self.assertEqual([p.expected_config(self.plan, a, "final", .004, seed)["nh"]
                              for a in ("GDN1", "DP4")], [1, 4])
            all_ids.update(j["id"] for j in jobs)
        self.assertEqual(len(all_ids), 21)
        with self.assertRaises(p.ProtocolError):
            p.final_jobs(self.plan, selection, 0)
        with self.assertRaises(p.ProtocolError):
            p.require_prior_seed_blocks(self.plan, selection, 2, {})
        prior = {r["job_id"]: r for arm in self.plan["arm_order"]
                 for r in [result_for(self.plan, arm, "final", .004, 1)]}
        p.require_prior_seed_blocks(self.plan, selection, 2, prior)
        with self.assertRaises(p.ProtocolError):
            p.require_prior_seed_blocks(self.plan, selection, 3, prior)

    def test_selection_reassignment_rejected_even_after_rehash(self):
        selected = self.select()
        selected["selected"]["B"]["lr"] = .008
        with self.assertRaises(p.ProtocolError):
            p.final_jobs(self.plan, p.seal(selected), 1)

    def test_draft_and_unconfirmed_provenance_cannot_export(self):
        for updates in ({"status": "draft"}, {"stage1_confirmation_sha256": None},
                        {"evidence_commit": None}):
            plan = p.seal({**self.plan, **updates})
            with self.assertRaises(p.ProtocolError):
                p.verify_plan(plan)

    def test_dataset_evidence_is_required_and_bound_for_frozen_plans(self):
        p.verify_plan(self.plan)
        for field in ("dataset_evidence", "dataset_evidence_sha256",
                      "dataset_evidence_file_sha256", "dataset_evidence_path"):
            bad = p.seal({**self.plan, field: None})
            with self.subTest(field=field), self.assertRaises(p.ProtocolError):
                p.verify_plan(bad)
        bad = copy.deepcopy(self.plan)
        bad["dataset_evidence"]["files"]["train.bin"]["sha256"] = "a" * 64
        bad["dataset_evidence"] = p.seal(bad["dataset_evidence"])
        bad["dataset_evidence_sha256"] = bad["dataset_evidence"]["sha256"]
        with self.assertRaises(p.ProtocolError):
            p.select_rates(p.seal(bad), [self.manifest], self.results)
        bad = copy.deepcopy(self.plan)
        bad["expected_configs"]["tuning"]["B"]["data"] = "/data/different"
        with self.assertRaises(p.ProtocolError):
            p.verify_plan(p.seal(bad))
        draft = p.build_plan(ROOT, ["B"], BUDGET)
        self.assertIsNone(draft["dataset_evidence"])
        with self.assertRaisesRegex(p.ProtocolError, "dataset-evidence"):
            p.build_plan(ROOT, ["B", "C"], BUDGET, confirmation=confirmation_for(self.plan))

    def test_dataset_schema_size_paths_and_current_recipe_are_checked(self):
        for mode in ("tokens", "missing_split", "path", "volume", "stable", "helper", "recipe"):
            bad = copy.deepcopy(DATASET)
            if mode == "tokens":
                bad["files"]["train.bin"]["tokens"] += 1
            elif mode == "missing_split":
                del bad["files"]["val.bin"]
            elif mode == "path":
                bad["files"]["val.bin"]["worker_path"] = "/data/different/val.bin"
            elif mode == "volume":
                bad["volume_name"] = "different"
            elif mode == "stable":
                bad["metadata_stable_during_read"] = False
            elif mode == "helper":
                bad["fingerprint_runtime"]["helper_sha256"] = "a" * 64
            else:
                bad["recipe_evidence"]["preparation_code_sha256"] = "a" * 64
            bad = p.seal(bad)
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(dir=ROOT / "results") as d:
                path = Path(d) / "dataset.json"
                p.write_immutable(path, bad)
                with self.assertRaises(p.ProtocolError):
                    p.build_plan(ROOT, ["B"], BUDGET, dataset=bad, dataset_path=path)
        bad = p.seal({**self.plan, "dataset_evidence_path": "../dataset.json"})
        with self.assertRaises(p.ProtocolError):
            p.verify_plan(bad)

    def test_dataset_streaming_hash_and_truncated_or_changing_volume(self):
        payloads = {"fineweb_edu/train.bin": b"\x01\x00\x02\x00",
                    "fineweb_edu/val.bin": b"\x03\x00"}

        class FakeVolume:
            listings = 0
            changing = False
            truncated = False

            def iterdir(self, directory, recursive=False):
                self.listings += 1
                return [SimpleNamespace(path=path, size=len(data),
                                        mtime=1234 + (self.listings if self.changing else 0))
                        for path, data in payloads.items()]

            def read_file(self, path):
                data = payloads[path][:-1] if self.truncated else payloads[path]
                return iter([data[:1], data[1:]])

        actual = fingerprint.fingerprint_files(FakeVolume())
        self.assertEqual(actual["train.bin"]["sha256"], p.digest(payloads["fineweb_edu/train.bin"]))
        self.assertEqual(actual["train.bin"]["tokens"], 2)
        for mode in ("changing", "truncated"):
            volume = FakeVolume()
            setattr(volume, mode, True)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                fingerprint.fingerprint_files(volume)
        observed = copy.deepcopy(DATASET)
        fingerprint.compare_files(DATASET, observed)
        observed["files"]["val.bin"]["sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            fingerprint.compare_files(DATASET, p.seal(observed))

    def test_stage1_requires_all18_unique_cells_and_all_survivors(self):
        confirmation = confirmation_for(self.plan)
        p.verify_confirmation(confirmation, ["B", "C"], self.plan["model_source_hashes"])
        for mode in ("missing", "duplicate", "failed", "omit_survivor"):
            c = copy.deepcopy(confirmation)
            survivors = ["B", "C"]
            if mode == "missing":
                c["candidates"]["B"]["cells"].pop()
            elif mode == "duplicate":
                c["candidates"]["B"]["cells"][-1] = c["candidates"]["B"]["cells"][0]
            elif mode == "failed":
                c["candidates"]["B"]["cells"][0]["gate"]["status"] = "unconfirmed"
            else:
                survivors = ["B"]
            with self.subTest(mode=mode), self.assertRaises(p.ProtocolError):
                p.verify_confirmation(p.seal(c), survivors, self.plan["model_source_hashes"])

    def test_written_rule_pass_retains_strict_reference_floor_failure(self):
        c = confirmation_for(self.plan)
        for role in ("candidates", "strict_code_candidates"):
            c[role]["B"]["cells"][0]["reference"]["test_score"] = .89
        strict = c["strict_code_candidates"]["B"]
        strict["status"] = "unconfirmed"
        strict["cells"][0]["gate"]["status"] = "reference_failed"
        c["strict_code_passed_candidates"] = ["C"]
        p.verify_confirmation(p.seal(c), ["B", "C"], self.plan["model_source_hashes"],
                              repository=ROOT.parent, evidence_commit=REGISTRATION_COMMIT)
        self.assertEqual(c["passed_candidates"], ["B", "C"])
        self.assertEqual(c["strict_code_candidates"]["B"]["status"], "unconfirmed")
        self.assertFalse(c["candidates"]["B"]["cells"][0]["gate"]["reference_floor_required"])
        self.assertTrue(c["strict_code_candidates"]["B"]["cells"][0]["gate"]["reference_floor_required"])

    def test_unknown_policy_uncommitted_or_wrong_original_provenance_rejected(self):
        for mode in ("active", "policy_id", "policy_contents", "missing_registration",
                     "pre_registration", "original_selection", "protocol", "eligibility", "strict_missing"):
            c = confirmation_for(self.plan)
            if mode == "active":
                c["active_gate_policy"] = "unknown"
            elif mode == "policy_id":
                c["gate_reconciliation"]["policy_id"] = "f" * 64
            elif mode == "policy_contents":
                c["gate_reconciliation"]["policy"]["word_threshold"] = .94
            elif mode == "missing_registration":
                c["gate_reconciliation"]["registration_commit"] = "0" * 40
            elif mode == "pre_registration":
                c["gate_reconciliation"]["registration_commit"] = p.git(ROOT, "rev-parse", REGISTRATION_COMMIT + "^").decode().strip()
            elif mode == "original_selection":
                c["gate_reconciliation"]["original_selection_sha256"] = "f" * 64
            elif mode == "protocol":
                c["protocol_id"] = "f" * 64
            elif mode == "eligibility":
                c["strict_code_seed0_survivors"] = []
            else:
                c.pop("strict_code_candidates")
            with self.subTest(mode=mode), self.assertRaises(p.ProtocolError):
                p.verify_confirmation(p.seal(c), ["B", "C"], self.plan["model_source_hashes"])
        earlier = p.git(ROOT, "rev-parse", REGISTRATION_COMMIT + "^").decode().strip()
        with self.assertRaises(p.ProtocolError):
            p.verify_confirmation(confirmation_for(self.plan), ["B", "C"], self.plan["model_source_hashes"],
                                  repository=ROOT.parent, evidence_commit=earlier)

    def test_reconciliation_preserves_candidate_floor_gap_and_valid_reference(self):
        for mode in ("floor", "gap", "reference_missing", "reference_nonfinite",
                     "reference_out_of_range", "gate_floor", "gate_margin", "gate_tolerance"):
            c = confirmation_for(self.plan)
            for role in ("candidates", "strict_code_candidates"):
                cell = c[role]["B"]["cells"][0]
                if mode == "floor":
                    cell["candidate"]["test_score"] = .899
                elif mode == "gap":
                    cell["candidate"]["test_score"] = .96
                elif mode == "reference_missing":
                    cell["reference"]["status"] = "pending"
                elif mode == "reference_nonfinite":
                    cell["reference"]["test_score"] = None
                elif mode == "reference_out_of_range":
                    cell["reference"]["test_score"] = 1.1
                elif mode == "gate_floor":
                    cell["gate"]["floor"] = .89
                elif mode == "gate_margin":
                    cell["gate"]["maximum_reference_gap"] = .04
                else:
                    cell["gate"]["threshold_tolerance"] = .01
            with self.subTest(mode=mode), self.assertRaises(p.ProtocolError):
                p.verify_confirmation(p.seal(c), ["B", "C"], self.plan["model_source_hashes"])
        c = confirmation_for(self.plan)
        c["strict_code_candidates"]["B"]["cells"][0]["reference"]["test_score"] = .99
        with self.assertRaises(p.ProtocolError):
            p.verify_confirmation(p.seal(c), ["B", "C"], self.plan["model_source_hashes"])

    def test_frozen_plan_preserves_policy_and_analysis_source_identity(self):
        for field in ("stage1_active_gate_policy", "planner_sha256", "gate_policy_adapter_sha256"):
            bad = p.seal({**self.plan, field: "f" * 64})
            with self.subTest(field=field), self.assertRaises(p.ProtocolError):
                p.verify_plan(bad)
        bad = copy.deepcopy(self.plan)
        bad["stage1_gate_reconciliation"]["registration_commit"] = "0" * 40
        with self.assertRaises(p.ProtocolError):
            p.verify_plan(p.seal(bad))

    def test_bridge_only_allows_audited_lm_reporting_change(self):
        c = confirmation_for(self.plan)
        current = dict(self.plan["model_source_hashes"])
        current["lm.py"] = "f" * 64
        with self.assertRaises(p.ProtocolError):
            p.verify_confirmation(c, ["B", "C"], current)
        bridge = p.seal({
            "schema": "stage2_source_bridge", "schema_version": 1, "classification": "report_only",
            "audit": {"unchanged_training": True}, "allowed_changed_files": ["lm.py"],
            "old_model_source_hashes": c["model_source_hashes"],
            "new_model_source_hashes": current, "diff": "report-only diff",
            "diff_sha256": p.digest(b"report-only diff"),
        })
        p.verify_confirmation(c, ["B", "C"], current, bridge)
        current["beyond_layers.py"] = "e" * 64
        bad = p.seal({**bridge, "new_model_source_hashes": current,
                      "allowed_changed_files": ["lm.py", "beyond_layers.py"]})
        with self.assertRaises(p.ProtocolError):
            p.verify_confirmation(c, ["B", "C"], current, bad)

    def test_nonadvancing_stage1_arms_must_have_explicit_closed_status(self):
        c = confirmation_for(self.plan)
        for status in ("pending", "invalid", "unknown"):
            bad = copy.deepcopy(c)
            bad["candidates"]["A"] = {"status": status, "cells": []}
            bad["strict_code_candidates"]["A"] = {"status": status, "cells": []}
            with self.subTest(status=status), self.assertRaises(p.ProtocolError):
                p.verify_confirmation(p.seal(bad), ["B", "C"], self.plan["model_source_hashes"])
        for status in ("rejected", "unconfirmed"):
            valid = copy.deepcopy(c)
            valid["candidates"]["A"] = {"status": status, "cells": []}
            valid["strict_code_candidates"]["A"] = {"status": status, "cells": []}
            p.verify_confirmation(p.seal(valid), ["B", "C"], self.plan["model_source_hashes"])

    def test_budget_deferral_requires_linked_reason_missing_cells_and_ledger(self):
        c = confirmation_for(self.plan)
        deferral = {
            "status": "budget_deferred", "reason": "synthetic cap closure",
            "ledger_sha256": "a" * 64, "ledger_file_sha256": "b" * 64,
            "ledger_snapshot": {category: {"settled_usd": 1, "reserved_usd": 0,
                                         "total_usd": 1, "cap_usd": cap}
                                for category, cap in (("screen", 25), ("language", 100),
                                                      ("development", 25), ("total", 150))},
            "missing_cells": [{"task": "wp_s5_16", "layers": 2, "seed": 3,
                               "candidate_status": "pending", "reference_status": "passed",
                               "candidate_job_id": "missing", "reference_job_id": "reference"}],
        }
        c["budget_deferrals"] = {"A": deferral}
        c["candidates"]["A"] = {"status": "unconfirmed", "cells": [], "budget_deferral": deferral}
        c["strict_code_candidates"]["A"] = {"status": "unconfirmed", "cells": []}
        p.verify_confirmation(p.seal(c), ["B", "C"], self.plan["model_source_hashes"])
        for field in ("reason", "missing_cells", "ledger_sha256", "ledger_snapshot"):
            bad = copy.deepcopy(c)
            del bad["budget_deferrals"]["A"][field]
            with self.subTest(field=field), self.assertRaises(p.ProtocolError):
                p.verify_confirmation(p.seal(bad), ["B", "C"], self.plan["model_source_hashes"])
        bad = copy.deepcopy(c)
        bad["budget_deferrals"] = {}
        with self.assertRaises(p.ProtocolError):
            p.verify_confirmation(p.seal(bad), ["B", "C"], self.plan["model_source_hashes"])

    def test_registration_digest_allows_log_updates_but_not_protocol_edits(self):
        document = "# Study\n## Log\nOld note\n## 5. Main language registration\nRates .002,.004,.008\n"
        expected = p.digest(p.language_registration(document))
        log_update = document.replace("Old note", "Old note\nNew result")
        protocol_update = document.replace(".008", ".016")
        self.assertEqual(expected, p.digest(p.language_registration(log_update)))
        self.assertNotEqual(expected, p.digest(p.language_registration(protocol_update)))
        with self.assertRaises(p.ProtocolError):
            p.language_registration("## Log\nNo registration")

    def test_bridge_requires_exact_committed_endpoints_and_diff(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            research = root / "research"
            research.mkdir()
            subprocess.run(["git", "init", "-q", d], check=True)
            subprocess.run(["git", "-C", d, "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", d, "config", "user.name", "Test"], check=True)
            for name in p.MODEL_SOURCES:
                (research / name).write_text("# unchanged training\n")
            subprocess.run(["git", "-C", d, "add", "research"], check=True)
            subprocess.run(["git", "-C", d, "commit", "-qm", "before"], check=True)
            before = p.git(root, "rev-parse", "HEAD").decode().strip()
            old_sources = p.sources(research)
            (research / "lm.py").write_text("# unchanged training\n# extra reporting\n")
            subprocess.run(["git", "-C", d, "add", "research/lm.py"], check=True)
            subprocess.run(["git", "-C", d, "commit", "-qm", "after"], check=True)
            after = p.git(root, "rev-parse", "HEAD").decode().strip()
            bridge = {
                "before_commit": before, "after_commit": after,
                "old_model_source_hashes": old_sources, "new_model_source_hashes": p.sources(research),
                "diff": p.git(root, "diff", before, after, "--", "research/lm.py").decode(),
            }
            p.verify_bridge_commits(root, bridge)
            bad = copy.deepcopy(bridge)
            bad["diff"] += "# forged\n"
            with self.assertRaises(p.ProtocolError):
                p.verify_bridge_commits(root, bad)
            bad = copy.deepcopy(bridge)
            bad["after_commit"] = before
            with self.assertRaises(p.ProtocolError):
                p.verify_bridge_commits(root, bad)

    def test_committed_evidence_and_immutable_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", d], check=True)
            subprocess.run(["git", "-C", d, "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", d, "config", "user.name", "Test"], check=True)
            artifact = root / "evidence.json"
            p.write_immutable(artifact, {"value": 1})
            subprocess.run(["git", "-C", d, "add", "evidence.json"], check=True)
            subprocess.run(["git", "-C", d, "commit", "-qm", "fixture"], check=True)
            self.assertEqual(p.committed_file(root, artifact, "HEAD"), {"value": 1})
            p.write_immutable(artifact, {"value": 1})
            with self.assertRaises(p.ProtocolError):
                p.write_immutable(artifact, {"value": 2})
            artifact.write_text('{"value":2}')
            with self.assertRaises(p.ProtocolError):
                p.committed_file(root, artifact, "HEAD")

    def test_all_three_survivors_use_larger_common_budget(self):
        plan = p.build_plan(ROOT, ["C", "A", "B"], BUDGET)
        expected = dict(rawS=14902, convS=14892, convP=13829, A=12207,
                        B=12982, C=12981, GDN1=14474, DP4=11217)
        self.assertEqual({a: x["main_steps"] for a, x in plan["arms"].items()}, expected)
        self.assertEqual(plan["target_arm"], "A")
        self.assertTrue(plan["budget"]["rolling_reservations_required"])
        self.assertLess(plan["budget"]["forecast_total_usd"], 100)
        self.assertAlmostEqual(plan["budget"]["forecast_total_usd"], 94.264480, places=5)
        self.assertEqual(len(plan["tuning_jobs"]), 24)

    def test_four_work_conventions_preserve_original_counters_and_include_no_cse_A(self):
        plan = p.build_plan(ROOT, ["A", "B", "C"], BUDGET)
        expected = {
            "rawS": (277420392, 318382560, 287023104, 331186176),
            "convS": (277586280, 318603744, 287188992, 331407360),
            "convP": (296617536, 343978752, 306312192, 356904960),
            "A": (322745274.5625, 378815736.75, 341858394.5625, 404299896.75),
            "B": (303489882.5625, 353141880.75, 313184538.5625, 366068088.75),
            "C": (303517530.5625, 353178744.75, 313212186.5625, 366104952.75),
            "GDN1": (294429883.5, 340985850, 294429883.5, 340985850),
            "DP4": (372031326, 444226344, 372031326, 444226344),
        }
        for arm, values in expected.items():
            row = plan["arms"][arm]
            self.assertEqual(tuple(row["work_fpt"][k] for k in p.WORK_CONVENTIONS), values)
            self.assertEqual(row["training_fpt"], BUDGET["arms"][arm]["training_fpt"])
            self.assertEqual(row["forward_fpt"], BUDGET["arms"][arm]["forward_fpt"])
        self.assertEqual(plan["arms"]["A"]["source_upper_forward_adjustment"], 6371040)
        self.assertEqual(plan["arms"]["A"]["main_steps"], 12207)
        self.assertEqual(plan["arms"]["B"]["main_steps"], 12982)
        self.assertEqual(plan["arms"]["C"]["main_steps"], 12981)

    def test_every_subset_controls_dominate_all_candidates_and_are_minimal(self):
        expected_controls = {
            ("A",): (14902, 14892, 13829, 14474, 11217),
            ("B",): (13540, 13531, 12533, 13105, 10277),
            ("C",): (13542, 13532, 12534, 13107, 10278),
            ("A", "B"): (14902, 14892, 13829, 14474, 11217),
            ("A", "C"): (14902, 14892, 13829, 14474, 11217),
            ("B", "C"): (13542, 13533, 12535, 13108, 10278),
            ("A", "B", "C"): (14902, 14892, 13829, 14474, 11217),
        }
        inequalities = witnesses = 0
        for size in (1, 2, 3):
            for survivors in itertools.combinations(("A", "B", "C"), size):
                plan = p.build_plan(ROOT, list(survivors), BUDGET)
                self.assertEqual(tuple(plan["arms"][a]["main_steps"] for a in p.CONTROL_ARMS),
                                 expected_controls[survivors])
                for control in p.CONTROL_ARMS:
                    row = plan["arms"][control]
                    for candidate in survivors:
                        for convention in p.WORK_CONVENTIONS:
                            achieved = row["main_steps"] * Fraction(str(row["work_fpt"][convention]))
                            needed = plan["arms"][candidate]["main_steps"] * Fraction(
                                str(plan["arms"][candidate]["work_fpt"][convention]))
                            self.assertGreaterEqual(achieved, needed)
                            inequalities += 1
                    self.assertTrue(row["binding_requirements"])
                    witness = row["binding_requirements"][0]
                    c, k = witness["candidate"], witness["convention"]
                    self.assertLess(
                        (row["main_steps"] - 1) * Fraction(str(row["work_fpt"][k])),
                        plan["arms"][c]["main_steps"] * Fraction(str(plan["arms"][c]["work_fpt"][k])),
                    )
                    witnesses += 1
                    self.assertLessEqual(row["main_timeout_seconds"], 7200)
                self.assertLess(plan["budget"]["forecast_total_usd"], 100)
        self.assertEqual((inequalities, witnesses), (240, 35))

    def test_allowance_proof_or_schedule_tampering_rejected_after_rehash(self):
        for mode in ("policy", "proof", "steps", "work", "candidate_steps"):
            bad = copy.deepcopy(self.plan)
            if mode == "policy":
                bad["control_allowance"]["policy_id"] = "f" * 64
            elif mode == "proof":
                bad["control_allowance"]["allocations"]["GDN1"]["dominance_proof"]["nominal"]["target_flops_fraction"][0] += 1
            elif mode == "steps":
                bad["arms"]["convS"]["main_steps"] -= 1
            elif mode == "work":
                bad["arms"]["DP4"]["work_fpt"]["source_upper_remat"] += 1
            else:
                bad["arms"]["B"]["main_steps"] += 1
            with self.subTest(mode=mode), self.assertRaises(p.ProtocolError):
                p.verify_plan(p.seal(bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
