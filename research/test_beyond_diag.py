"""Task-definition tests for BEYOND; no accelerator or training required."""

import argparse
import itertools
import unittest

import numpy as np

import beyond_diag as bd
import groups


class DiagnosticTaskTests(unittest.TestCase):
    def test_mqar_values_are_prior_bound_pairs(self):
        x, y, m = bd.TASKS["mqar_small"][0](np.random.default_rng(1), 16)
        for xb, yb, mb in zip(x, y, m):
            bindings = dict(zip(xb[:32:2], xb[1:32:2]))
            self.assertEqual(len(bindings), 16)
            for t in np.flatnonzero(mb):
                self.assertGreaterEqual(t, 32)
                self.assertEqual(yb[t], bindings[xb[t]])
                self.assertNotEqual(yb[t], xb[t])

    def test_induction_uses_last_occurrence_and_every_query_repeats(self):
        x, y, m = bd.induction_small(np.random.default_rng(2), 16)
        for xb, yb, mb in zip(x, y, m):
            self.assertEqual(int(mb.sum()), 8)
            for t in np.flatnonzero(mb):
                earlier = np.flatnonzero(xb[:120] == xb[t])
                self.assertEqual(len(earlier), 3)
                self.assertEqual(yb[t], xb[earlier[-1] + 1])
                self.assertGreaterEqual(yb[t], 32)
                self.assertLess(xb[t], 32)

    def test_word_labels_are_prefix_products(self):
        for name in ("A5", "S5"):
            G = groups.get(name)
            x, y, m = bd.word(np.random.default_rng(3), 8, name, 16)
            self.assertTrue((x[:, 0] == G.n).all())
            self.assertTrue((m[:, 0] == 0).all())
            for b in range(len(x)):
                state = G.e
                for t in range(1, x.shape[1]):
                    state = G.mul[state, x[b, t]]
                    self.assertEqual(y[b, t], state)

    def test_causal_match_against_bruteforce_and_prefix_changes(self):
        G = groups.get("A5")
        rng = np.random.default_rng(4)
        g = rng.integers(G.n, size=(24, 16))
        y = bd.causal_match_labels(g)
        expected = np.zeros_like(y)
        for b in range(len(g)):
            for i, j, t in itertools.combinations(range(g.shape[1]), 3):
                if G.mul[G.mul[g[b, i], g[b, j]], g[b, t]] == G.e:
                    expected[b, t] = 1
        np.testing.assert_array_equal(y, expected)
        for cut in (1, 5, 10, 15):
            edited = g.copy()
            edited[:, cut:] = rng.integers(G.n, size=edited[:, cut:].shape)
            np.testing.assert_array_equal(bd.causal_match_labels(edited)[:, :cut], y[:, :cut])

    def test_tasks_fit_vocab_masks_and_reproducible_disjoint_streams(self):
        for name, (gen, T, V, _, _) in bd.TASKS.items():
            if name == "regression":
                continue
            with self.subTest(task=name):
                a = gen(np.random.default_rng(0), 4)
                b = gen(np.random.default_rng(0), 4)
                validation = gen(np.random.default_rng(10_000), 4)
                test = gen(np.random.default_rng(20_000), 4)
                for first, second in zip(a, b):
                    np.testing.assert_array_equal(first, second)
                x, y, m = a
                self.assertEqual(x.shape, (4, T))
                self.assertEqual(y.shape, x.shape)
                self.assertEqual(m.shape, x.shape)
                self.assertTrue(((x >= 0) & (x < V)).all())
                self.assertTrue(((y >= 0) & (y < V)).all())
                self.assertTrue((m.sum(1) > 0).all())
                self.assertFalse(np.array_equal(validation[0], test[0]))

    def test_regression_query_has_no_value_and_affine_answer_is_identifiable(self):
        x, y, m = bd.regression(np.random.default_rng(5), 20)
        self.assertTrue((x[:, -1, 2] == 0).all())
        self.assertTrue((x[:, -1, 3] == 1).all())
        self.assertTrue((x[:, :-1, 3] == 0).all())
        self.assertTrue((m == 1).all())
        for xb, expected in zip(x, y):
            design = np.column_stack([xb[:-1, :2], np.ones(16)])
            coeff = np.linalg.lstsq(design, xb[:-1, 2], rcond=None)[0]
            prediction = np.r_[xb[-1, :2], 1] @ coeff
            self.assertAlmostEqual(prediction, float(expected), places=5)

    def test_fixed_reference_budget_matches_distinct_delta_variants(self):
        # A shared reference must not inherit the evaluated arm's nh. Include
        # regression to verify its adapter FLOPs are part of the same budget.
        peers = ["gpt", "beyond_a", "gated_delta"]
        for regression_task in (False, True):
            task = "regression" if regression_task else "wp_a5_16"
            _, T, V, pos, _ = bd.TASKS[task]
            configs = []
            for nh in (1, 4):
                args = argparse.Namespace(arch="gated_delta", d=128, layers=1, heads=4,
                                          mlp=0, chart=8, pos=None, set=[("nh", nh)])
                configs.append(bd.model_config(args, T, V, pos))
            costs = [bd.task_flops(cfg, T, regression_task) for cfg in configs]
            target = 0.8 * min(costs)  # explicitly below BOTH arms' own costs
            reference_steps, batch = 123, 32
            target_total = 3 * target * reference_steps * batch * T
            updates = []
            for cfg in configs:
                steps, own, _ = bd.compute_budget(cfg, T, reference_steps, peers,
                                                  regression_task, target_fpt=target)
                updates.append(steps)
                self.assertLess(steps, reference_steps)
                actual_total = 3 * own * steps * batch * T
                self.assertLessEqual(actual_total, target_total)
                self.assertLess(target_total - actual_total, 3 * own * batch * T)
            self.assertGreater(updates[0], updates[1])
            for invalid in (0, -1, float("nan"), float("inf")):
                with self.assertRaises(ValueError):
                    bd.compute_budget(configs[0], T, reference_steps, peers,
                                      regression_task, target_fpt=invalid)
            with self.assertRaisesRegex(ValueError, "cannot fund one update"):
                bd.compute_budget(configs[0], T, 1, [], regression_task, target_fpt=costs[0] / 2)

    def test_unmatched_budget_preserves_exact_requested_steps(self):
        args = argparse.Namespace(arch="prefix", d=128, layers=1, heads=4,
                                  mlp=0, chart=8, pos=None, set=[])
        cfg = bd.model_config(args, 17, 61, 0)
        own = bd.task_flops(cfg, 17)
        self.assertNotEqual(own, int(own))  # reproduce fractional prefix-scan cost
        for peers in ([], ["prefix"]):
            steps, _, _ = bd.compute_budget(cfg, 17, 1000, peers)
            self.assertEqual(steps, 1000)

    def test_second_half_metric_excludes_easy_prefix(self):
        y = np.array([[0, 0, 1, 0, 1], [0, 1, 0, 1, 0]])
        m = np.ones_like(y)
        m[:, 0] = 0
        pred = y.copy()
        pred[:, 3:] = 1 - pred[:, 3:]
        score = bd.metrics(pred, y, m, classes=2, word_task=True)
        self.assertEqual(score["acc"], 0.5)
        self.assertEqual(score["bal_late"], 0.0)


if __name__ == "__main__":
    unittest.main()
