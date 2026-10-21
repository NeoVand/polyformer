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
                vtrans_heads=0, gate_out=0, vres=0,
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
    dict(posenc="holo", forget=1, gate_out=1, vres=1, vtrans=1, vtrans_heads=1, pattern="GA"),
    dict(posenc="rope", forget=1, gate_out=1, vres=1, layers=3, loop_order="0,1,1,2"),
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


def test_value_residual_reaches_later_layers_and_one_head_transport_is_partial():
    c = cfg(posenc="holo", vres=1, vtrans=1, vtrans_heads=1, layers=2, holo_init=0.8)
    p = lm.init(jax.random.PRNGKey(0), c)
    idx = jax.random.randint(jax.random.PRNGKey(2), (2, c.ctx), 0, c.vocab)
    base = lm.forward(c, p, idx)
    # zeroing layer 2's residual share changes the output; layer 1 has nothing to mix
    p2 = {**p, "layers": [p["layers"][0], {**p["layers"][1], "vres": jnp.zeros_like(p["layers"][1]["vres"])}]}
    assert float(jnp.abs(lm.forward(c, p2, idx) - base).max()) > 1e-5
    p1 = {**p, "layers": [{**p["layers"][0], "vres": jnp.zeros_like(p["layers"][0]["vres"])}, p["layers"][1]]}
    np.testing.assert_allclose(np.asarray(lm.forward(c, p1, idx)), np.asarray(base), atol=1e-5)
    # transport touches head 0 only
    _, lyr = layer(c)
    x = x_in(c)
    fr = ll.frames(c, lyr, x)
    v = jax.random.normal(jax.random.PRNGKey(4), (2, c.ctx, c.heads, c.d // c.heads))
    moved = ll.rotate_holo(c, fr, v)
    np.testing.assert_allclose(np.asarray(moved[:, :, 1:]), np.asarray(v[:, :, 1:]))
    assert float(jnp.abs(moved[:, :, 0] - v[:, :, 0]).max()) > 1e-4


def test_blockwise_attention_equals_dense_with_forget_bias():
    c_dense = cfg(attn_block=64, bf16=0)
    c_block = cfg(attn_block=16, bf16=0)
    kq = jax.random.split(jax.random.PRNGKey(7), 4)
    q, k, v = (jax.random.normal(kk, (2, 3, 64, 8)) for kk in kq[:3])
    logf = jax.nn.log_sigmoid(jax.random.normal(kq[3], (2, 3, 64)) + 1.0)
    cbias = jnp.cumsum(logf, axis=-1) * 40.0          # large biases, as at long context
    a = ll.causal_attention(c_dense, q, k, v, cbias)
    b = ll.causal_attention(c_block, q, k, v, cbias)
    np.testing.assert_allclose(np.asarray(a), np.asarray(b), atol=2e-5)
    np.testing.assert_allclose(np.asarray(ll.causal_attention(c_dense, q, k, v)),
                               np.asarray(ll.causal_attention(c_block, q, k, v)), atol=2e-5)
    # a length that is not a multiple of the block is padded and still exact
    c_odd = cfg(attn_block=24, bf16=0)
    np.testing.assert_allclose(np.asarray(ll.causal_attention(c_odd, q, k, v, cbias)), np.asarray(a), atol=2e-5)


def ev_cfg(**kw):
    c = cfg(arch="events", d=64, heads=2, mlp=128, ctx=64, vocab=50, ev_enc=1, ev_main=2, ev_dec=1, ev_len=4.0,
            ev_slots=0, ev_dmain=64, ev_heads=2, ev_posenc="holo", ev_forget=1, ev_vtrans=0, ev_vtrans_heads=0,
            ev_gate_out=0, ev_vres=0, ev_router="learned", ev_cap=16, ratio_w=0.03, delta_chunk=16, attn_block=1024, remat=0)
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def _random_router(p, seed=11):
    # identity routers rarely fire on random inputs; random ones make many boundaries to test against
    import events_model as em
    enc, _, _, _, _ = em.sizes(ev_cfg())
    r = p["layers"][enc - 1]
    kk = jax.random.split(jax.random.PRNGKey(seed), 2)
    r = {**r, "rq": {"w": jax.random.normal(kk[0], r["rq"]["w"].shape)},
         "rk": {"w": jax.random.normal(kk[1], r["rk"]["w"].shape)}}
    return {**p, "layers": [r if i == enc - 1 else l for i, l in enumerate(p["layers"])]}


@pytest.mark.parametrize("slots,parts,dmain,router", [(0, 0, 64, "learned"), (6, 0, 64, "learned"),
                                                      (0, 1, 64, "learned"), (0, 1, 96, "learned"),
                                                      (0, 1, 64, "punct")])
def test_event_model_is_causal(slots, parts, dmain, router):
    import events_model as em
    # parts: the gate, the value residual and one transport head in the main network; dmain: a wider one
    c = ev_cfg(ev_slots=slots, ev_gate_out=parts, ev_vres=parts, ev_vtrans=parts, ev_vtrans_heads=parts,
               ev_dmain=dmain, ev_heads=dmain // 32, ev_router=router, ev_cap=4, vocab=50304)
    p = _random_router(lm.init(jax.random.PRNGKey(0), c))
    idx = jax.random.randint(jax.random.PRNGKey(2), (2, c.ctx), 0, c.vocab)
    _, aux = em.forward(c, p, idx, with_aux=True)
    assert 0.05 < float(aux["rate"]) < 0.95          # boundaries actually occur
    for cut in (10, 33, 50):
        idx2 = idx.at[:, cut:].set((idx[:, cut:] + 13) % c.vocab)
        a, b = lm.forward(c, p, idx), lm.forward(c, p, idx2)
        np.testing.assert_allclose(np.asarray(a[:, :cut]), np.asarray(b[:, :cut]), atol=2e-5)
        assert float(jnp.abs(a[:, cut:] - b[:, cut:]).max()) > 1e-4
    if slots:
        assert float(aux["overflow"]) > 0               # the small buffer overflows, and stays causal


def test_event_model_trains_one_step_and_counts_flops():
    import events_model as em
    c = ev_cfg()
    p = _random_router(lm.init(jax.random.PRNGKey(0), c))
    idx = jax.random.randint(jax.random.PRNGKey(2), (2, c.ctx), 0, c.vocab)

    def loss(p):
        lg, aux = em.forward(c, p, idx, with_aux=True)
        return jax.nn.log_softmax(lg).mean() + 0.03 * aux["ratio"]

    g = jax.grad(loss)(p)
    assert all(bool(jnp.isfinite(v).all()) for v in jax.tree_util.tree_leaves(g))
    # the router receives gradient (through the confidence, the smoothing and the ratio loss)
    enc = em.sizes(c)[0]
    assert float(jnp.abs(g["layers"][enc - 1]["rq"]["w"]).max()) > 0
    assert lm.flops_per_token(c, c.ctx) > 0


def test_event_model_flops_are_below_softmax_at_long_context():
    import events_model as em
    big = dict(d=512, heads=8, mlp=2048, vocab=50304, qkv_conv=3)
    soft = cfg(arch="loop", layers=6, posenc="rope", forget=1, ctx=8192, **big)
    ev = ev_cfg(ctx=8192, ev_enc=2, ev_main=6, ev_dec=2, ev_len=8.0, ev_dmain=512, ev_heads=8, delta_chunk=32, **big)
    ratio8k = lm.training_flops_per_token(ev, 8192) / lm.training_flops_per_token(soft, 8192)
    soft.ctx, ev.ctx = 2048, 2048
    ratio2k = lm.training_flops_per_token(ev, 2048) / lm.training_flops_per_token(soft, 2048)
    assert ratio8k < ratio2k < 1.2, (ratio8k, ratio2k)


def test_probe_items_have_the_answers_they_claim():
    import events_probe as ep
    import events_tokens as tok
    inv = {v: k.strip() for k, v in tok.PIECE.items()}
    val = np.random.default_rng(0).integers(0, 50000, 20000).astype(np.uint16)
    sets = ep.probe_items(2048, val)
    assert set(sets) == {"kv_d0", "kv_d256", "kv_d1024"} | {f"{k}_k{m}" for k in ("boxes", "owners") for m in range(4)}
    for name, items in sets.items():
        assert len(items) == 128
        for prompt, cands, ans in items[:40]:
            assert len(prompt) < 2048 and len(set(cands)) == len(cands)
            if name.startswith("kv"):
                colour = inv[prompt[-3]]
                facts = [prompt[i:i + 9] for i in range(1, 37, 9)]
                assert [inv[f[7]] for f in facts if inv[f[4]] == colour] == [inv[cands[ans]]]
                continue
            words = [inv.get(t, "?") for t in prompt[1:]]
            sentences = " ".join(words).split(" . ")
            where = {}
            for s in sentences[:-1]:
                w = s.replace(" .", "").split()
                if w[0] == "The":            # The t is in box P
                    where[w[1]] = w[5]
                elif w[0] == "Move":         # Move the t to box P
                    where[w[2]] = w[5]
                elif w[1] == "has":          # N has the t
                    where[w[3]] = w[0]
                else:                        # N gives the t to M
                    where[w[3]] = w[5]
            q = sentences[-1].split()
            thing = q[1] if q[0] == "The" else q[2]
            assert where[thing] == inv[cands[ans]], (name, sentences)


def test_probe_scores_a_tiny_model(tmp_path):
    import events_probe as ep
    c = ev_cfg(ctx=160, vocab=50304)
    p = lm.init(jax.random.PRNGKey(0), c)
    items = ep.tracking_items(np.random.default_rng(1), 6, 2, "owners")
    out = ep.score_items(c, p, items, 4)
    assert out["n"] == 6 and 0 <= out["acc"] <= 1 and out["loss"] > 0 and out["chance"] == 1 / 3
    x = np.asarray(jax.random.randint(jax.random.PRNGKey(3), (4, 160), 0, c.vocab), np.int32)
    b = ep.boundary_stats(c, _random_router(p), x)
    assert b["boundaries"] > 0 and 0 <= b["share_any"] <= 1 and len(b["samples"]) == 3
