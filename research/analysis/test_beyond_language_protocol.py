"""CPU-only tests for frozen planning, source identity, and held-out selection."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("protocol", HERE / "beyond_language_protocol.py")
p = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)
ROOT = HERE.parent
BUDGET = json.loads((ROOT / "results" / "beyond_language_planning" / "budget.json").read_text())


def fixture_plan():
    plan = p.build_plan(ROOT, ["B", "C"], BUDGET)
    # Synthetic sealed provenance for pure-function tests; production CLI
    # separately requires committed evidence and an audited source bridge.
    return p.seal({**plan, "status": "frozen", "evidence_commit": "a" * 40,
                   "stage1_confirmation_sha256": "b" * 64})


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
    cells = [{"task": task, "layers": layers, "seed": seed, "gate": {"status": "passed"}}
             for task, layers in p.PRIMARY_CELLS for seed in p.FINAL_SEEDS]
    return p.seal({
        "schema": "stage1_confirmation", "schema_version": 1,
        "model_source_hashes": plan["model_source_hashes"],
        "candidates": {arm: {"status": "passed", "cells": cells} for arm in ("B", "C")},
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
        expected = dict(rawS=13356, convS=13348, convP=12491, B=12209,
                        C=12207, GDN1=12584, DP4=9959)
        self.assertEqual({a: x["main_steps"] for a, x in self.plan["arms"].items()}, expected)
        self.assertEqual(len(self.plan["tuning_jobs"]), 21)
        self.assertEqual(self.plan["final_seeds"], [1, 2, 3])
        self.assertAlmostEqual(self.plan["budget"]["forecast_total_usd"], 76.237598, places=5)
        self.assertLess(self.plan["budget"]["all_timeout_total_usd"], 100)
        self.assertTrue(all(0 <= a["excess_updates"] < 1 for a in self.plan["arms"].values()))
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
            with self.subTest(status=status), self.assertRaises(p.ProtocolError):
                p.verify_confirmation(p.seal(bad), ["B", "C"], self.plan["model_source_hashes"])
        for status in ("rejected", "unconfirmed"):
            valid = copy.deepcopy(c)
            valid["candidates"]["A"] = {"status": status, "cells": []}
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
        expected = dict(rawS=14202, convS=14193, convP=13283, A=12207,
                        B=12982, C=12981, GDN1=13381, DP4=10590)
        self.assertEqual({a: x["main_steps"] for a, x in plan["arms"].items()}, expected)
        self.assertEqual(plan["target_arm"], "A")
        self.assertTrue(plan["budget"]["rolling_reservations_required"])
        self.assertLess(plan["budget"]["forecast_total_usd"], 100)
        self.assertEqual(len(plan["tuning_jobs"]), 24)


if __name__ == "__main__":
    unittest.main(verbosity=2)
