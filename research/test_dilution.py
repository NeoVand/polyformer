"""Generator/layer contracts written before the experiment implementation."""
import itertools
import unittest
import numpy as np
import jax
import jax.numpy as jnp
import dilution as d
import beyond_layers as bl


class GeneratorTests(unittest.TestCase):
    def test_interpreter_and_matrix_reference_exhaustive(self):
        actions = [('transfer', a, b) for a, b in itertools.combinations(d.PEOPLE, 2)]
        actions += [('alias', 'x', 'A'), ('alias', 'x', 'B'), ('revoke', 'x', ''), ('transfer', 'x', 'C')]
        for tail in itertools.product(actions, repeat=3):
            for owner in d.PEOPLE:
                ops = [('owner', owner, '')] + list(tail)
                self.assertEqual(d.execute(ops), d.execute_matrix(ops))

    def test_revoke_overwrite_snapshot_and_noncommutativity(self):
        ops = [('owner','A',''), ('alias','x','A'), ('alias','y','x'), ('alias','x','B'), ('revoke','x',''), ('transfer','y','C')]
        self.assertEqual(d.execute(ops), 'C')
        self.assertNotEqual(d.execute([('owner','A',''),('transfer','A','B'),('transfer','B','C')]),
                            d.execute([('owner','A',''),('transfer','B','C'),('transfer','A','B')]))

    def test_pairs_and_masks_all_splits(self):
        for split in d.SPLITS:
            pairs = d.make_pairs(seed=27, count=32, split=split)
            for p in pairs:
                self.assertEqual(sum(a != b for a,b in zip(p.ops[0], p.ops[1])), 1)
                self.assertNotEqual(p.answers[0], p.answers[1])
                self.assertEqual(p.ops[0][1:], p.ops[1][1:])
                self.assertTrue(8 <= len(p.ops[0]) <= 32)
                for op, ans in zip(p.ops,p.answers):
                    self.assertEqual(d.execute(op), ans)
            batch = d.pack(pairs)
            self.assertEqual(batch['decision'].sum(), 64)
            for i in range(64):
                pos = np.flatnonzero(batch['decision'][i])
                self.assertEqual(len(pos), 1)
                self.assertEqual(pos[0], np.flatnonzero(batch['valid'][i])[-1])
                self.assertIn(d.TOKENS[int(batch['y'][i,pos[0]])], d.PEOPLE)
            self.assertEqual(float(np.sum(batch['decision'] * (1-batch['valid']))), 0)

    def test_deterministic_stream_and_disjoint_splits(self):
        a = d.make_pairs(12, 16, 'id')
        b = d.make_pairs(12, 16, 'id')
        self.assertEqual(a,b)
        self.assertEqual(d.batch_digest(d.pack(a)),d.batch_digest(d.pack(b)))
        train = d.make_pairs(12,16,'train')
        para = d.make_pairs(12,16,'paraphrase')
        self.assertTrue(all(x.template in (0,1) for x in train))
        self.assertTrue(all(x.template == 2 for x in para))
        self.assertTrue(all(len(x.ops[0]) <= 20 for x in train))
        self.assertTrue(all(len(x.ops[0]) >= 24 for x in d.make_pairs(12,16,'length')))
        train_words = set().union(*(set(d.render(x.ops[0],x.answers[0],t)) for x in train for t in (0,1)))
        test_words = set().union(*(set(d.render(x.ops[0],x.answers[0],2)) for x in para))
        self.assertFalse(test_words-train_words)

    def test_loss_reduction_and_padding(self):
        loss = jnp.array([[2.,4.,50.],[3.,9.,90.]])
        valid = jnp.array([[1.,1.,0.],[1.,1.,0.]])
        decision = jnp.array([[0.,1.,0.],[0.,1.,0.]])
        self.assertAlmostEqual(float(d.reduce_loss(loss, valid, decision, 'token')),4.5)
        self.assertAlmostEqual(float(d.reduce_loss(loss, valid, decision, 'decision')),6.5)
        p = float(decision.sum()/valid.sum())
        other = float((loss*(valid-decision)).sum()/(valid-decision).sum())
        self.assertAlmostEqual(4.5,p*6.5+(1-p)*other)


class LayerTests(unittest.TestCase):
    def test_matrix_prefix_brute_force_and_identity(self):
        rng=np.random.default_rng(4)
        u=np.stack([np.linalg.qr(rng.normal(size=(4,4)))[0] for _ in range(14)]).reshape(2,7,1,4,4)
        got=np.asarray(bl.matrix_prefix(jnp.asarray(u)))
        for b in range(2):
            state=np.eye(4)
            for t in range(7):
                state=u[b,t,0]@state
                np.testing.assert_allclose(got[b,t,0],state,atol=1e-6)
        eye=np.broadcast_to(np.eye(4),(1,8,2,4,4))
        np.testing.assert_allclose(bl.matrix_prefix(jnp.asarray(eye)),eye,atol=1e-6)

    def test_causality_and_zero_branch_reduction(self):
        cfg=d.config(d=16,layers=1,heads=2,ctx=40)
        soft=d.init_model(jax.random.PRNGKey(5),cfg,'softmax')
        hybrid=d.init_model(jax.random.PRNGKey(5),cfg,'hybrid')
        # Both arms use same MLP width and common initialization for mechanism control.
        for lyr in hybrid['layers']:
            lyr['branch']['group_mix']=jnp.zeros_like(lyr['branch']['group_mix'])
            lyr['branch']['group_out']['b']=jnp.zeros_like(lyr['branch']['group_out']['b'])
        x=jnp.arange(30)[None,:] % len(d.TOKENS)
        s=np.asarray(d.forward(soft,x,cfg,'softmax'))
        h=np.asarray(d.forward(hybrid,x,cfg,'hybrid'))
        np.testing.assert_allclose(s,h,atol=1e-6)
        for arm in ('softmax','hybrid'):
            params=d.init_model(jax.random.PRNGKey(5),cfg,arm)
            before=np.asarray(d.forward(params,x,cfg,arm))
            after=np.asarray(d.forward(params,x.at[:,19:].set(0),cfg,arm))
            np.testing.assert_allclose(before[:,:19],after[:,:19],atol=2e-5)

if __name__=='__main__':
    unittest.main()
