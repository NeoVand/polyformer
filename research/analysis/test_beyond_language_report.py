"""Synthetic final-result fixtures only; no training or fabricated real results."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r = load("_language_report_test_subject", HERE / "beyond_language_report.py")
fixtures = load("_language_protocol_fixtures", HERE / "test_beyond_language_protocol.py")
p = r.p


def change_loss(row, value):
    seq = [value + (.1 if i % 2 else -.1) for i in range(1024)]
    row.update(val_big_raw=value, val_big=round(value, 5), val_big_sequence_losses=seq,
               val_big_sequence_mean_raw=sum(seq) / len(seq))
    modes = ("composition", "precision", "coupling") if row["config"]["arch"] == "beyond_c" else ("composition", "precision")
    if row["config"]["ablations"]:
        row["ablation_val_big_raw"] = {mode: value + .02 for mode in modes}
        row["ablation_val_big_sequence_losses"] = {mode: [x + .02 for x in seq] for mode in modes}
        row["ablation_delta_val_big_raw"] = {mode: (value + .02) - value for mode in modes}
        row["ablation_delta_val_big_sequence_losses"] = {
            mode: [(x + .02) - x for x in seq] for mode in modes
        }


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        plan = fixtures.fixture_plan()
        confirmation = fixtures.confirmation_for(plan)
        plan["stage1_closed_candidate_statuses"] = {a: x["status"] for a, x in confirmation["candidates"].items()}
        cls.plan = p.seal(plan)
        cls.confirmation = confirmation
        tuning_manifest = fixtures.manifest_for(cls.plan)
        cls.selection = p.select_rates(cls.plan, [tuning_manifest],
                                      fixtures.results_for(cls.plan, tuning_manifest))
        cls.manifests, cls.results = [], {}
        for seed in (1, 2, 3):
            jobs = p.final_jobs(cls.plan, cls.selection, seed)
            manifest = p.seal({"schema": 1, "name": f"synthetic_final_seed{seed}",
                               "stage": "language", "source_hashes": cls.plan["source_hashes"],
                               "runtime_versions": cls.plan["runtime_versions"], "jobs": jobs,
                               "prediction_commit": "synthetic-unit-test-only"})
            cls.manifests.append(manifest)
            for arm, job in zip(cls.selection["final_arm_order"], jobs):
                row = fixtures.result_for(cls.plan, arm, "final", .004, seed, manifest)
                row.update(
                    prediction_commit=manifest["prediction_commit"], params=1000, nonembed=500,
                    wall=20., secs=19., log_directory=job["id"], log_volume="polyformer-beyond-runs",
                    checkpoint={"schema": 1, "path": f"/runs/{job['id']}/final.pkl", "bytes": 123},
                    artifacts=[{"name": "final.pkl", "bytes": 123}],
                    val_big_sample={**cls.plan["final_sample"], "order": "generator draw order"},
                    component_usage=[{"composition_ratio": .2}] * 6,
                )
                change_loss(row, 3.95 if arm == "B" else 3.97 if arm == "C" else 4.0)
                cls.results[job["id"]] = row

    def setUp(self):
        for name in ("plan", "selection", "confirmation", "manifests", "results"):
            setattr(self, name, copy.deepcopy(getattr(type(self), name)))

    def report(self, **kwargs):
        return r.build_report(self.plan, self.selection, self.confirmation,
                              self.manifests, self.results, **kwargs)

    def row(self, arm, seed=1):
        job = p.make_job(self.plan, arm, "final", self.selection["selected"][arm]["lr"], seed)
        return self.results[job["id"]]

    def report_row(self, report, arm, seed=1):
        return next(x for x in report["runs"] if x["arm"] == arm and x["seed"] == seed)

    def invalidate_tuning(self, arms):
        tuning_manifest = fixtures.manifest_for(self.plan)
        tuning_results = fixtures.results_for(self.plan, tuning_manifest)
        for entry in self.plan["tuning_jobs"]:
            if entry["arm"] in arms:
                tuning_results[entry["job"]["id"]]["error"] = "synthetic bounded timeout"
        self.selection = p.select_rates(self.plan, [tuning_manifest], tuning_results)
        allowed = set()
        if self.selection["status"] == "selected":
            for seed in (1, 2, 3):
                allowed.update(job["id"] for job in p.final_jobs(self.plan, self.selection, seed))
        manifests, results = [], {}
        for old in self.manifests:
            jobs = [job for job in old["jobs"] if job["id"] in allowed]
            if not jobs:
                continue
            manifest = p.seal({**old, "jobs": jobs})
            manifests.append(manifest)
            for job in jobs:
                row = copy.deepcopy(self.results[job["id"]])
                row["manifest_sha256"] = manifest["sha256"]
                results[job["id"]] = row
        self.manifests, self.results = manifests, results

    def test_exact_three_seed_gate_and_mechanism_comparator(self):
        report = self.report()
        self.assertEqual(report["passed_candidates"], ["B"])
        self.assertEqual(report["candidate_gates"]["C"]["status"], "rejected")
        self.assertEqual(report["coverage"], {"expected_runs": 21, "original_arm_seed_cells": 21,
                                             "complete": 21, "pending": 0, "invalid": 0,
                                             "tuning_invalid": 0, "tuning_blocked": 0})
        self.assertTrue(report["composition_comparison"]["B"]["lower_than_convP_all_three_seeds"])
        self.assertEqual(report["gate_numeric_tolerance"], 0)

    def test_boundary_and_unrounded_gate(self):
        for seed in (1, 2, 3):
            change_loss(self.row("B", seed), 3.96)
        self.assertEqual(self.report()["candidate_gates"]["B"]["status"], "passed")
        change_loss(self.row("B", 2), 3.960000001)
        self.assertEqual(self.row("B", 2)["val_big"], 3.96)
        self.assertEqual(self.report()["candidate_gates"]["B"]["status"], "rejected")

    def test_missing_control_unconfirmed_but_valid_failure_still_rejects(self):
        self.results.pop(self.row("DP4", 2)["job_id"])
        report = self.report()
        self.assertEqual(report["candidate_gates"]["B"]["status"], "unconfirmed")
        self.assertEqual(report["candidate_gates"]["C"]["status"], "rejected")

    def test_either_recurrent_control_can_reject(self):
        change_loss(self.row("GDN1", 3), 3.94)
        report = self.report()
        self.assertEqual(report["candidate_gates"]["B"]["status"], "rejected")
        checks = report["candidate_gates"]["B"]["seed_gates"][2]["checks"]
        self.assertEqual(next(x for x in checks if x["control"] == "GDN1")["status"], "rejected")

    def test_failure_is_invalid_not_accuracy_failure(self):
        self.row("B")["error"] = "bounded timeout"
        self.row("B")["steps"] = 10
        report = self.report()
        self.assertEqual(self.report_row(report, "B")["status"], "invalid")
        self.assertEqual(report["candidate_gates"]["B"]["status"], "unconfirmed")

    def test_source_config_and_manifest_provenance_are_audited(self):
        mutations = (
            lambda x: x["source_hashes"].update({"lm.py": "wrong"}),
            lambda x: x["config"].update({"batch": 32}),
            lambda x: x.update(manifest_sha256="0" * 64),
            lambda x: x.update(installed_versions={"jax": "wrong"}),
            lambda x: x.update(prediction_commit="wrong"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.results = copy.deepcopy(type(self).results)
                mutate(self.row("B"))
                report = self.report()
                self.assertEqual(self.report_row(report, "B")["status"], "invalid")
                self.assertEqual(report["candidate_gates"]["B"]["status"], "unconfirmed")

    def test_complete_steps_tokens_and_both_compute_counters_required(self):
        mutations = (
            lambda x: x["curve"][-1].update(step=x["steps"] - 1),
            lambda x: x.update(tokens=x["tokens"] - 1),
            lambda x: x.update(train_flops=x["train_flops"] * .99),
            lambda x: x.update(flops_per_token=x["flops_per_token"] + 1),
            lambda x: x.update(train_flops_per_token=x["train_flops_per_token"] + 1),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.results = copy.deepcopy(type(self).results)
                mutate(self.row("B"))
                self.assertEqual(self.report_row(self.report(), "B")["status"], "invalid")

    def test_raw_loss_has_no_rounded_or_curve_fallback(self):
        self.row("B").pop("val_big_raw")
        self.row("B")["curve"][0]["val_raw"] = 0.
        report = self.report()
        self.assertEqual(report["candidate_gates"]["B"]["status"], "unconfirmed")
        self.assertIsNone(self.report_row(report, "B")["loss_raw"])

    def test_entire_array_and_fixed_sample_are_required(self):
        mutations = (
            lambda x: x["val_big_sequence_losses"].pop(),
            lambda x: x["val_big_sample"].update(seed=1234),
            lambda x: x["val_big_sample"].update(order="sorted"),
            lambda x: x["val_big_sequence_losses"].__setitem__(0, float("nan")),
            lambda x: x.update(val_big_sequence_mean_raw=0.),
            lambda x: x.update(val_big_raw=x["val_big_raw"] - .001),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                self.results = copy.deepcopy(type(self).results)
                mutate(self.row("B"))
                self.assertEqual(self.report_row(self.report(), "B")["status"], "invalid")

    def test_reduction_roundoff_is_not_gate_tolerance(self):
        self.row("B")["val_big_raw"] += 4e-7
        report = self.report()
        self.assertEqual(self.report_row(report, "B")["status"], "complete")
        self.assertEqual(self.report_row(report, "B")["loss_raw"], 3.9500004)

    def test_checkpoint_save_requires_worker_correspondence(self):
        for field in ("checkpoint", "artifacts"):
            with self.subTest(field=field):
                self.results = copy.deepcopy(type(self).results)
                self.row("B").pop(field)
                self.assertEqual(self.report_row(self.report(), "B")["status"], "invalid")
        self.results = copy.deepcopy(type(self).results)
        self.row("B")["checkpoint"]["bytes"] += 1
        self.assertEqual(self.report_row(self.report(), "B")["status"], "invalid")

    def test_optional_local_checkpoint_byte_check_never_unpickles(self):
        with tempfile.TemporaryDirectory() as temp:
            for job_id in self.results:
                folder = Path(temp) / job_id
                folder.mkdir()
                (folder / "final.pkl").write_bytes(b"x" * 123)  # Intentionally not a pickle.
            report = self.report(checkpoint_root=temp)
            self.assertEqual(report["coverage"]["complete"], 21)
            self.assertIn("local_sha256", self.report_row(report, "B")["checkpoint"])

    def test_paired_uncertainty_respects_sequence_correlation(self):
        report = self.report()
        pair = next(x for x in report["comparisons"] if x["candidate"] == "B"
                    and x["control"] == "rawS" and x["seed"] == 1)
        self.assertGreater(self.report_row(report, "B")["sequence_statistics"]["conditional_sequence_se"], 0)
        self.assertAlmostEqual(pair["paired_sequence_difference"]["conditional_sequence_se"], 0., places=14)
        self.assertAlmostEqual(pair["raw_difference_nats"], -.05)
        self.assertIn("Overlapping", report["uncertainty_note"])
        self.assertIn("not training-seed", report["uncertainty_note"])

    def test_ablations_are_paired_and_not_additional_headline_gate(self):
        report = self.report()
        ablation = self.report_row(report, "B")["ablations"][0]
        self.assertEqual(ablation["status"], "complete")
        self.assertAlmostEqual(ablation["paired_sequence_difference"]["mean"], .02)
        self.row("B").pop("ablation_val_big_sequence_losses")
        report = self.report()
        self.assertEqual(report["candidate_gates"]["B"]["status"], "passed")
        self.assertEqual(self.report_row(report, "B")["ablation_status"], "unconfirmed")

    def test_ablation_delta_tampering_is_flagged(self):
        self.row("B")["ablation_delta_val_big_sequence_losses"]["precision"][0] = .9
        report = self.report()
        ablation = next(x for x in self.report_row(report, "B")["ablations"] if x["mode"] == "precision")
        self.assertEqual(ablation["status"], "unconfirmed")

    def test_parameters_consistent_across_seeds(self):
        self.row("B", 3)["params"] += 1
        report = self.report()
        self.assertTrue(all(self.report_row(report, "B", s)["status"] == "invalid" for s in (1, 2, 3)))
        self.assertEqual(report["candidate_gates"]["B"]["status"], "unconfirmed")

    def test_duplicate_modified_or_unexpected_manifest_job_aborts(self):
        self.manifests.append(self.manifests[0])
        with self.assertRaises(p.ProtocolError):
            self.report()
        self.manifests = copy.deepcopy(type(self).manifests)
        self.manifests[0]["jobs"][0]["max_seconds"] += 1
        self.manifests[0] = p.seal(self.manifests[0])
        with self.assertRaises(p.ProtocolError):
            self.report()

    def test_unregistered_final_sample_and_source_bridge_abort(self):
        self.plan["final_sample"]["sequences"] = 512
        self.plan = p.seal(self.plan)
        with self.assertRaises(p.ProtocolError):
            self.report()
        self.plan = copy.deepcopy(type(self).plan)
        with self.assertRaises(p.ProtocolError):
            self.report(bridge={"sha256": "a" * 64})

    def test_missing_future_manifest_is_pending(self):
        missing = self.manifests.pop()
        for job in missing["jobs"]:
            self.results.pop(job["id"])
        report = self.report()
        self.assertEqual(report["coverage"]["pending"], 7)
        self.assertEqual(report["candidate_gates"]["B"]["status"], "unconfirmed")

    def test_rates_remain_frozen_and_intermediate_scores_irrelevant(self):
        baseline = self.report()
        for row in self.results.values():
            row["curve"][0]["val_raw"] = -1000
            row["val_big"] = -1000
        updated = self.report()
        self.assertEqual(baseline["candidate_gates"], updated["candidate_gates"])
        self.selection["selected"]["B"]["lr"] = .008
        self.selection = p.seal(self.selection)
        with self.assertRaises(p.ProtocolError):
            self.report()

    def test_written_only_flag_preserves_strict_outcome(self):
        active = self.confirmation["candidates"]["B"]
        strict = self.confirmation["strict_code_candidates"]["B"]
        index = next(i for i, c in enumerate(active["cells"]) if c["task"].startswith("wp_"))
        active["cells"][index]["reference"]["test_score"] = .94
        strict["cells"][index]["reference"]["test_score"] = .94
        strict["cells"][index]["gate"]["status"] = "reference_failed"
        strict["status"] = "unconfirmed"
        self.confirmation["strict_code_passed_candidates"] = ["C"]
        self.confirmation = p.seal(self.confirmation)
        self.plan.update(stage1_confirmation_sha256=self.confirmation["sha256"],
                         stage1_strict_code_candidates=copy.deepcopy(self.confirmation["strict_code_candidates"]),
                         stage1_strict_code_passed_candidates=["C"])
        self.plan = p.seal(self.plan)
        self.selection["plan_sha256"] = self.plan["sha256"]
        self.selection = p.seal(self.selection)
        report = self.report()
        self.assertEqual(report["candidate_gates"]["B"]["status"], "passed")
        self.assertTrue(report["candidate_gates"]["B"]["written_rule_only"])
        self.assertEqual(report["strict_code_candidate_gates"]["B"]["status"], "unconfirmed")

    def test_cost_comes_from_matching_ledger_identity(self):
        row = self.row("B")
        ledger = {"cost_basis": "estimate, not invoice", "jobs": {
            row["job_id"]: {"stage": "language", "manifest_sha256": row["manifest_sha256"],
                            "status": "complete", "reserved_usd": 2., "settled_usd": 1.2}}}
        report = self.report(ledger=ledger)
        self.assertEqual(self.report_row(report, "B")["cost"]["estimate_usd"], 1.2)
        ledger["jobs"][row["job_id"]]["manifest_sha256"] = "wrong"
        report = self.report(ledger=ledger)
        self.assertIsNone(self.report_row(report, "B")["cost"]["estimate_usd"])

    def test_frozen_per_arm_allocations_are_authoritative(self):
        report = self.report()
        self.assertEqual(report["accounting"]["control_allowance"], self.plan.get("control_allowance"))
        for row in report["runs"]:
            allocation = self.plan["arms"][row["arm"]]
            self.assertEqual(row["steps"], allocation["main_steps"])
            self.assertEqual(row["tokens"], allocation["main_tokens"])
            self.assertEqual(row["training_flops"], allocation["main_training_flops"])
        self.assertIn("not executed GPU FLOP equality", report["accounting"]["note"])

    def test_invalid_candidate_is_retained_and_other_candidate_proceeds(self):
        original_plan = copy.deepcopy(self.plan)
        self.invalidate_tuning({"C"})
        report = self.report()
        self.assertEqual(report["final_arm_order"], ["rawS", "convS", "convP", "B", "GDN1", "DP4"])
        self.assertEqual(report["passed_candidates"], ["B"])
        self.assertEqual(report["candidate_gates"]["C"]["status"], "unconfirmed")
        self.assertEqual(report["candidate_gates"]["C"]["language_tuning_status"], "tuning_invalid")
        self.assertEqual(report["strict_code_candidate_gates"]["C"]["status"], "unconfirmed")
        for seed in (1, 2, 3):
            excluded = self.report_row(report, "C", seed)
            self.assertEqual(excluded["status"], "tuning_invalid")
            self.assertIsNone(excluded["loss_raw"])
            self.assertIsNone(excluded["job_id"])
            self.assertEqual(len(excluded["tuning_trials"]), 3)
            self.assertTrue(all(t["status"] == "invalid" for t in excluded["tuning_trials"]))
            self.assertEqual(self.report_row(report, "GDN1", seed)["status"], "complete")
        self.assertEqual(report["coverage"]["expected_runs"], 18)
        self.assertEqual(report["coverage"]["tuning_invalid"], 3)
        self.assertEqual(self.plan, original_plan)
        self.assertEqual(self.plan["target_arm"], "C")
        self.assertEqual(report["accounting"]["arm_plan"], original_plan["arms"])
        self.assertEqual(report["accounting"]["control_allowance"], original_plan["control_allowance"])

    def test_all_invalid_control_stops_grid_without_loss_rejection(self):
        self.invalidate_tuning({"DP4"})
        report = self.report()
        self.assertEqual(report["final_arm_order"], [])
        self.assertEqual(report["tuning"]["invalid_controls"], ["DP4"])
        self.assertTrue(report["tuning"]["stop_reasons"])
        self.assertEqual(report["coverage"]["expected_runs"], 0)
        self.assertEqual(report["coverage"]["tuning_invalid"], 3)
        self.assertEqual(report["coverage"]["tuning_blocked"], 18)
        self.assertEqual(report["passed_candidates"], [])
        for candidate in ("B", "C"):
            self.assertEqual(report["candidate_gates"][candidate]["status"], "unconfirmed")
            self.assertEqual(report["candidate_gates"][candidate]["language_tuning_status"], "tuning_blocked")
        self.assertTrue(all(row["loss_raw"] is None for row in report["runs"]))

    def test_no_viable_candidates_stops_grid_with_controls_retained(self):
        self.invalidate_tuning({"B", "C"})
        report = self.report()
        self.assertEqual(report["final_arm_order"], [])
        self.assertEqual(report["tuning"]["viable_candidates"], [])
        self.assertEqual(report["tuning"]["invalid_controls"], [])
        self.assertEqual(report["coverage"]["tuning_invalid"], 6)
        self.assertEqual(report["coverage"]["tuning_blocked"], 15)
        self.assertEqual(len(report["accounting"]["arm_plan"]), 7)
        self.assertTrue(all(g["status"] == "unconfirmed" for g in report["candidate_gates"].values()))

    def test_valid_candidate_cannot_be_silently_dropped(self):
        self.selection["final_arm_order"].remove("C")
        self.selection["viable_candidates"].remove("C")
        self.selection["tuning_invalid_candidates"].append("C")
        self.selection["invalid_arms"].append("C")
        self.selection["selected"].pop("C")
        self.selection = p.seal(self.selection)
        with self.assertRaises(p.ProtocolError):
            self.report()

    def test_excluded_candidate_final_manifest_is_rejected(self):
        original_manifests = copy.deepcopy(self.manifests)
        self.invalidate_tuning({"C"})
        self.manifests = original_manifests
        with self.assertRaises(p.ProtocolError):
            self.report()

    def test_full_dataset_evidence_is_preserved(self):
        report = self.report()
        for field in ("dataset_evidence", "dataset_evidence_sha256",
                      "dataset_evidence_file_sha256", "dataset_evidence_path"):
            self.assertEqual(report[field], self.plan[field])
        self.assertIn("fingerprinted", report["pairing_basis"])
        self.assertIn("do not rehash", report["pairing_basis"])

    def test_report_reproducibility_tsv_and_no_overwrite(self):
        first = self.report()
        self.assertEqual(first, self.report())
        with tempfile.TemporaryDirectory() as temp:
            r.write_outputs(first, temp)
            r.write_outputs(first, temp)
            self.assertEqual(json.loads((Path(temp) / "report.json").read_text()), first)
            self.assertTrue((Path(temp) / "paired_differences.tsv").read_text().startswith("candidate\tcontrol\tseed"))
            changed = copy.deepcopy(first)
            changed["coverage"]["complete"] = 0
            with self.assertRaises(p.ProtocolError):
                r.write_outputs(changed, temp)

    def test_cli_help_is_portable_without_training_imports(self):
        with tempfile.TemporaryDirectory() as temp:
            run = subprocess.run([sys.executable, str(HERE / "beyond_language_report.py"), "--help"],
                                 cwd=temp, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("--manifest", run.stdout)

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "optional matplotlib not installed")
    def test_optional_standalone_scientific_plots(self):
        with tempfile.TemporaryDirectory() as temp:
            r.write_outputs(self.report(), temp, plots=True)
            for name in ("final_losses", "paired_differences"):
                for suffix in ("png", "pdf"):
                    self.assertGreater((Path(temp) / f"{name}.{suffix}").stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
