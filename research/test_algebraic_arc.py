"""Generator/layer tests written before algebraic_arc.py (run with unittest)."""
import unittest

import numpy as np

import algebraic_arc as arc


class GeneratorTests(unittest.TestCase):
    def test_d4_group_and_translation_inverse(self):
        grid = np.arange(36).reshape(6, 6)
        orbit = [arc.apply_primitive(grid, ("d4", k)) for k in range(8)]
        self.assertEqual(len({x.tobytes() for x in orbit}), 8)
        for a in range(8):
            for b in range(8):
                product = arc.apply_primitive(orbit[a], ("d4", b))
                self.assertTrue(any(np.array_equal(product, x) for x in orbit))
        for r in range(6):
            for c in range(6):
                shifted = arc.apply_primitive(grid, ("translate", r, c))
                np.testing.assert_array_equal(arc.apply_primitive(shifted, ("translate", -r, -c)), grid)

    def test_colour_inverse_and_composition_canonical(self):
        rng = np.random.default_rng(10)
        for _ in range(100):
            perm = np.r_[0, rng.permutation(np.arange(1, 10))]
            grid = rng.integers(0, 10, (6, 6))
            changed = arc.apply_primitive(grid, ("colour", *perm))
            np.testing.assert_array_equal(arc.apply_primitive(changed, ("colour", *np.argsort(perm))), grid)
        for depth in range(1, 5):
            for _ in range(50):
                program = arc.sample_program(rng, depth, "invertible")
                spatial, colours = arc.canonical_operator(program)
                grid = rng.integers(0, 10, (6, 6))
                expected = colours[grid.reshape(-1)[spatial]].reshape(6, 6)
                np.testing.assert_array_equal(arc.apply_program(grid, program), expected)

    def test_irreversible_semantics(self):
        grid = np.zeros((6, 6), np.int32)
        grid[2:4, 3:5] = [[1, 2], [3, 4]]
        crop = arc.apply_primitive(grid, ("crop",))
        np.testing.assert_array_equal(crop[:2, :2], [[1, 2], [3, 4]])
        self.assertEqual(np.count_nonzero(crop), 4)
        gravity = arc.apply_primitive(grid, ("gravity",))
        np.testing.assert_array_equal(gravity[4:, 3:5], [[1, 2], [3, 4]])
        filled = arc.apply_primitive(grid, ("fill", 0, 0, 5))
        self.assertEqual(np.count_nonzero(filled == 5), 32)
        self.assertEqual(filled[2, 3], 1)

    def test_split_reproducibility_and_no_target_leak(self):
        rng = np.random.default_rng(7)
        for tier in arc.TIERS:
            for split in ("train", "test"):
                for depth in range(1, 5):
                    task = arc.make_task(rng, depth, tier, split)
                    self.assertEqual(arc.operator_split(task["program"], tier), split)
                    self.assertEqual(len(task["train"]), 3)
                    self.assertEqual(len(task["test"]), 1)
                    features, target = arc.encode_task(task)
                    self.assertEqual(features.shape, (144, 4))
                    altered = {**task, "test": [{**task["test"][0], "output": np.zeros((6, 6), int).tolist()}]}
                    np.testing.assert_array_equal(arc.encode_task(altered)[0], features)
                    for leave in range(3):
                        adapted, label = arc.encode_task(task, leave_out=leave)
                        self.assertTrue(np.all(adapted[leave * 36:(leave + 1) * 36, 1] == 10))
                        np.testing.assert_array_equal(label, np.asarray(task["train"][leave]["output"]).reshape(-1))
                        changed = {**task, "train": [dict(p) for p in task["train"]]}
                        changed["train"][leave]["output"] = np.zeros((6, 6), int).tolist()
                        np.testing.assert_array_equal(arc.encode_task(changed, leave_out=leave)[0], adapted)

    def test_privileged_solver_and_cancellations(self):
        rng = np.random.default_rng(42)
        for depth in range(1, 5):
            for _ in range(4):
                task = arc.make_task(rng, depth, "invertible", "test")
                answer, diagnostics = arc.structural_solver(task)
                np.testing.assert_array_equal(answer, task["test"][0]["output"])
                self.assertGreaterEqual(diagnostics["consistent_spatial_candidates"], 1)
        program = (("d4", 1), ("d4", 3))
        self.assertEqual(arc.operator_diagnostics(program)["effective_factor_count"], 0)


class ModelTests(unittest.TestCase):
    def test_shapes_gradients_and_task_adaptation(self):
        import jax
        import jax.numpy as jnp
        rng = np.random.default_rng(1)
        task = arc.make_task(rng, 1, "invertible", "train")
        x, y = arc.encode_task(task)
        for arm in ("softmax", "hybrid"):
            params = arc.init_model(jax.random.PRNGKey(2), arm, width=16, layers=1)
            logits = arc.forward(params, jnp.asarray(x[None]), arm)
            self.assertEqual(logits.shape, (1, 36, 10))
            grads = jax.grad(arc.loss)(params, jnp.asarray(x[None]), jnp.asarray(y[None]), arm)
            self.assertTrue(all(np.isfinite(z).all() for z in jax.tree_util.tree_leaves(grads)))
            if arm == "hybrid":
                self.assertGreater(float(jnp.linalg.norm(grads["layers"][0]["vectors"])), 0)


if __name__ == "__main__":
    unittest.main()
