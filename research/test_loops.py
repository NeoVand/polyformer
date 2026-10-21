"""Stage 0 of LOOPS.md: the frames do what the plan says, on CPU, before any GPU money."""

import argparse
import math
import pathlib
import sys

import jax
import jax.numpy as jnp
import numpy as np
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import lm  # noqa: E402
import loops_layers as ll  # noqa: E402

jax.config.update("jax_enable_x64", False)


def cfg(**kw):
    base = dict(arch="loop", d=64, layers=2, heads=2, mlp=128, ctx=24, vocab=50, pos=0, posenc="rope",
                holo=16, modules=4, holo_init=0.3, rope_base=10000.0, forget=0, forget_bias=5.0, vtrans=0,
                pattern="", loop_order="", qkv_conv=3, nh=1, beta_max=1.0, delta_key_ratio=0.75,
                delta_v_expand=2.0, delta_chunk=0, delta_unroll=1, conv_width=4, remat=0, bf16=0,
                hops=1, lookback=0, cap=0.0, gdim=5, nheads=2, rank=8, order=3)
    base.update(kw)
    return argparse.Namespace(**base)


def layer(c, seed=0):
    p = lm.init(jax.random.PRNGKey(seed), c)
    return p, p["layers"][0]


def x_in(c, seed=1, b=2):
    return jax.random.normal(jax.random.PRNGKey(seed), (b, c.ctx, c.d))


def test_grid_starts_as_rope():
    c_rope, c_grid = cfg(posenc="rope"), cfg(posenc="grid")
    _, lr = layer(c_rope)
    _, lg = layer(c_grid)
    x = x_in(c_rope)
    y_rope = ll.attention(c_rope, lr, x, lm.project_qkv)
    y_grid = ll.attention(c_grid, lg, x, lm.project_qkv)
    np.testing.assert_allclose(np.asarray(y_rope), np.asarray(y_grid), atol=2e-5)


def test_holo_at_identity_is_translation_invariant():
    # zero content weights: every move is the fixed RoPE step, so scores depend on i - j only
    c = cfg(posenc="holo")
    _, lyr = layer(c)
    lyr = {**lyr, "quat": {"w": jnp.zeros_like(lyr["quat"]["w"]), "b": lyr["quat"]["b"]}}
    x = x_in(c)
    fr = ll.frames(c, lyr, x)
    q = jax.random.normal(jax.random.PRNGKey(3), (2, c.ctx, c.heads, c.d // c.heads))
    qq = jnp.broadcast_to(q[:, :1], q.shape)         # the same vector at every position
    r = ll.rotate(c, fr, qq)
    s = jnp.einsum("bihc,bjhc->bhij", r, r)
    # constant along diagonals
    np.testing.assert_allclose(np.asarray(s[:, :, 5, 2]), np.asarray(s[:, :, 9, 6]), atol=1e-4)
    np.testing.assert_allclose(np.asarray(s[:, :, 7, 7]), np.asarray(s[:, :, 3, 3]), atol=1e-4)


def test_factorised_transport_is_the_literal_ordered_product():
    c = cfg(posenc="holo", holo_init=0.8)
    _, lyr = layer(c)
    x = x_in(c)
    dh, pairs, blocks, _ = ll.dims(c)
    fr = ll.frames(c, lyr, x)
    F = fr["F"]                                         # [B, T, H, nb, 4, 4]
    # rebuild the moves M_t = F_{t-1}^T F_t and check the literal product between j and i
    q = jax.random.normal(jax.random.PRNGKey(5), (4,))
    k = jax.random.normal(jax.random.PRNGKey(6), (4,))
    b, h, n = 1, 1, 2
    moves = [F[b, 0, h, n]] + [F[b, t - 1, h, n].T @ F[b, t, h, n] for t in range(1, c.ctx)]
    for i, j in ((10, 3), (20, 19), (15, 0)):
        lit = jnp.eye(4)
        for t in range(j + 1, i + 1):
            lit = lit @ moves[t]
        factor = (F[b, i, h, n] @ q) @ (F[b, j, h, n] @ k)
        literal = (lit @ q) @ k
        np.testing.assert_allclose(float(factor), float(literal), rtol=1e-4, atol=1e-4)
    # every frame is orthogonal
    eye = jnp.einsum("...ji,...jk->...ik", F, F)
    np.testing.assert_allclose(np.asarray(eye), np.broadcast_to(np.eye(4), eye.shape), atol=1e-4)


def test_holo_moves_do_not_commute_but_grid_moves_do():
    # swapping two tokens between j and i changes the holonomy, not the grid phase
    c = cfg(posenc="holo", holo_init=0.8)
    _, lyr = layer(c)
    lyr = {**lyr, "vel": {"w": jax.random.normal(jax.random.PRNGKey(9), lyr["vel"]["w"].shape),
                          "b": lyr["vel"]["b"]}}
    x = x_in(c, b=1)
    xs = x.at[0, 5].set(x[0, 6]).at[0, 6].set(x[0, 5])
    f1, f2 = ll.frames(c, lyr, x), ll.frames(c, lyr, xs)
    # grid phase at token 10 depends only on the multiset of earlier velocities
    np.testing.assert_allclose(np.asarray(f1["cos"][0, 10]), np.asarray(f2["cos"][0, 10]), atol=1e-4)
    assert float(jnp.abs(f1["F"][0, 10] - f2["F"][0, 10]).max()) > 1e-3


def test_causal():
    for posenc, forget, vtrans in (("rope", 0, 0), ("grid", 1, 0), ("holo", 1, 1)):
        c = cfg(posenc=posenc, forget=forget, vtrans=vtrans)
        p = lm.init(jax.random.PRNGKey(0), c)
        idx = jax.random.randint(jax.random.PRNGKey(2), (2, c.ctx), 0, c.vocab)
        idx2 = idx.at[:, 15:].set((idx[:, 15:] + 7) % c.vocab)
        a, b = lm.forward(c, p, idx), lm.forward(c, p, idx2)
        np.testing.assert_allclose(np.asarray(a[:, :15]), np.asarray(b[:, :15]), atol=1e-5)
        assert float(jnp.abs(a[:, 15:] - b[:, 15:]).max()) > 1e-4


def test_forget_gate_starts_near_softmax():
    c0, c1 = cfg(posenc="rope"), cfg(posenc="rope", forget=1)
    _, l0 = layer(c0)
    _, l1 = layer(c1)
    x = x_in(c0)
    y0 = ll.attention(c0, l0, x, lm.project_qkv)
    y1 = ll.attention(c1, l1, x, lm.project_qkv)
    # bias 5: each step multiplies a weight by sigmoid(5) ~ 0.9933, so close but not equal
    assert float(jnp.abs(y0 - y1).max()) < 0.2 * float(jnp.abs(y0).max())


@pytest.mark.parametrize("kw", [
    dict(posenc="holo", vtrans=1, forget=1),
    dict(posenc="rope", pattern="GA"),
    dict(posenc="holo", pattern="GA", forget=1),
    dict(posenc="rope", pattern="DA"),
    dict(posenc="rope", layers=3, loop_order="0,1,1,2"),
    dict(posenc="abs", pos=1),
    dict(posenc="holo", holo=32, vtrans=1),
])
def test_models_train_one_step(kw):
    c = cfg(**kw)
    p = lm.init(jax.random.PRNGKey(0), c)
    idx = jax.random.randint(jax.random.PRNGKey(2), (2, c.ctx), 0, c.vocab)

    def loss(p):
        lg = lm.forward(c, p, idx[:, :-1].repeat(1, 0) if False else idx)
        return jax.nn.log_softmax(lg).mean()

    g = jax.grad(loss)(p)
    leaves = jax.tree_util.tree_leaves(g)
    assert all(bool(jnp.isfinite(v).all()) for v in leaves)
    assert lm.flops_per_token(c, c.ctx) > 0
    assert lm.training_flops_per_token(c, c.ctx) >= 3 * lm.flops_per_token(c, c.ctx)


def test_frame_flops_are_small_at_language_size():
    big = cfg(d=512, heads=8, layers=6, mlp=2048, ctx=512, vocab=50304, posenc="holo", forget=1, vtrans=1)
    base = cfg(d=512, heads=8, layers=6, mlp=2048, ctx=512, vocab=50304, posenc="rope")
    ratio = lm.flops_per_token(big, 512) / lm.flops_per_token(base, 512)
    assert 1.0 < ratio < 1.02, ratio
