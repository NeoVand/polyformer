"""Stage-0 algebra, causality, reduction, and gradient checks (no training)."""

from types import SimpleNamespace
import copy

import jax
import jax.numpy as jnp
import numpy as np

import beyond_layers as bl


def config(arch="beyond_b", **kwargs):
    values = dict(arch=arch, d=20, heads=2, ctx=7, layers=1, gdim=5,
                  group_nh=4, group_order=2, nh=4, beta_max=2,
                  conv_width=4, bf16=0, branch_scale=0.1, ablate="none",
                  delta_key_ratio=1.0, delta_v_expand=2.0)
    values.update(kwargs)
    return SimpleNamespace(**values)


def close(a, b, tol=2e-5):
    error = float(jnp.max(jnp.abs(a - b)))
    assert error < tol, error
    return error


def test_matrix_algebra():
    keys = jax.random.split(jax.random.key(17), 3)
    vectors = jax.random.normal(keys[0], (2, 7, 2, 4, 5))
    u = bl.householder_products(vectors)
    close(u @ jnp.swapaxes(u, -1, -2), jnp.eye(5))
    assert float(jnp.max(jnp.abs(u[:, 0] @ u[:, 1] - u[:, 1] @ u[:, 0]))) > 0.1
    prefix = bl.matrix_prefix(u)
    manual, state = [], jnp.broadcast_to(jnp.eye(5), (2, 2, 5, 5))
    for i in range(7):
        state = u[:, i] @ state
        manual.append(state)
    close(prefix, jnp.stack(manual, 1))
    features, _ = bl.matrix_features(u, 2)
    close(features[:, :, 0], u)
    for i in range(7):
        pairs = sum((u[:, i] @ u[:, j] for j in range(i)), jnp.zeros_like(u[:, i]))
        close(features[:, i, 1], pairs / max(i, 1))
    return {"orthogonality": float(jnp.max(jnp.abs(u @ jnp.swapaxes(u, -1, -2) - jnp.eye(5))))}


def test_transport():
    key1, key2, key3 = jax.random.split(jax.random.key(9), 3)
    p = jax.nn.softmax(jax.random.normal(key1, (1, 2, 7, 7)), -1)
    v = jax.random.normal(key2, (1, 2, 7, 11))
    u = bl.householder_products(jax.random.normal(key3, (1, 7, 2, 4, 5)))
    prefix = bl.matrix_prefix(u)
    got = bl.transported_attention(p, v, prefix)
    vp = jnp.pad(v, ((0, 0), (0, 0), (0, 0), (0, 4))).reshape(1, 2, 7, 3, 5)
    rows = []
    for i in range(7):
        result = jnp.zeros((1, 2, 3, 5))
        for j in range(7):
            transport = prefix[:, i] @ jnp.swapaxes(prefix[:, j], -1, -2)
            moved = jnp.einsum("bhij,bhnj->bhni", transport, vp[:, :, j])
            result = result + p[:, :, i, j, None, None] * moved
        rows.append(result.reshape(1, 2, 15)[..., :11])
    close(got, jnp.stack(rows, 2))
    identity = jnp.broadcast_to(jnp.eye(5), prefix.shape)
    close(bl.transported_attention(p, v, identity), p @ v)


def test_affine_precision():
    # A calibrated Parallax probe exactly reproduces affine functions where
    # covariance has full rank, including an outside-convex-hull query.
    k = jnp.array([[-1., -1.], [1., -1.], [-1., 1.], [1., 1.], [0., 0.]])
    p = jax.nn.softmax(jnp.array([0.2, -0.4, 0.7, 0.1, -0.5]))
    q = jnp.array([2., 3.])
    mean = p @ k
    covariance = jnp.einsum("n,ni,nj->ij", p, k - mean, k - mean)
    rho = jnp.linalg.solve(covariance, mean - q)
    weights = bl.parallax_weights(p[None, None, None], rho[None, None, None], k[None, None])[0, 0, 0]
    close(weights.sum(), jnp.array(1.))
    close(weights @ k, q)
    value = 1.3 + k @ jnp.array([0.8, -1.2])
    close(weights @ value, 1.3 + q @ jnp.array([0.8, -1.2]))
    assert float(weights.min()) < 0, "positive-only tilt cannot solve this outside-hull query"


def test_delta_scan():
    ks = jax.random.split(jax.random.key(12), 5)
    q = jax.random.normal(ks[0], (1, 5, 2, 3))
    k = bl._unit(jax.random.normal(ks[1], (1, 5, 2, 4, 3)))
    v = jax.random.normal(ks[2], (1, 5, 2, 4, 3))
    beta = 2 * jax.nn.sigmoid(jax.random.normal(ks[3], (1, 5, 2, 4)))
    decay = jax.nn.sigmoid(jax.random.normal(ks[4], (1, 5, 2)))
    out = bl.gated_delta_scan(q, k, v, beta, decay)
    state, expected = jnp.zeros((1, 2, 3, 3)), []
    for t in range(5):
        state = decay[:, t, :, None, None] * state
        for step in range(4):
            kt, vt, bt = k[:, t, :, step], v[:, t, :, step], beta[:, t, :, step]
            transition = jnp.eye(3) - bt[..., None, None] * kt[..., :, None] * kt[..., None, :]
            write = bt[..., None, None] * vt[..., :, None] * kt[..., None, :]
            state = state @ transition + write
        expected.append(jnp.einsum("bhvk,bhk->bhv", state, q[:, t]))
    close(out, jnp.stack(expected, 1))
    # No writes, no decay, and an identity state reduces to an ordered
    # generalized Householder product, read through the query.
    got = bl.gated_delta_scan(q, k, jnp.zeros_like(v), beta, jnp.ones_like(decay),
                             initial=jnp.broadcast_to(jnp.eye(3), (1, 2, 3, 3)))
    state, expected = jnp.broadcast_to(jnp.eye(3), (1, 2, 3, 3)), []
    for t in range(5):
        for step in range(4):
            kt, bt = k[:, t, :, step], beta[:, t, :, step]
            state = state @ (jnp.eye(3) - bt[..., None, None] * kt[..., :, None] * kt[..., None, :])
        expected.append(jnp.einsum("bhvk,bhk->bhv", state, q[:, t]))
    close(got, jnp.stack(expected, 1))


def test_layers():
    x = jax.random.normal(jax.random.key(3), (2, 7, 20))
    results = {}
    for name in bl.KINDS:
        cfg = config(name)
        p = bl.init_layer(jax.random.key(2), cfg)
        # Perturb away from identity before testing causality/reductions.
        if "group_vectors" in p:
            p["group_vectors"]["w"] += 0.05 * jax.random.normal(jax.random.key(33), p["group_vectors"]["w"].shape)
        y = jax.jit(lambda params, xx: bl.apply_layer(cfg, params, xx))(p, x)
        assert y.shape == x.shape and bool(jnp.isfinite(y).all())
        changed = x.at[:, 4:].add(10 * jax.random.normal(jax.random.key(7), x[:, 4:].shape))
        causal = close(y[:, :4], bl.apply_layer(cfg, p, changed)[:, :4])
        grad = jax.grad(lambda params: jnp.mean(bl.apply_layer(cfg, params, x) ** 2))(p)
        assert all(bool(jnp.isfinite(z).all()) for z in jax.tree_util.tree_leaves(grad))
        group_grad = None
        if "group_vectors" in p:
            fresh = bl.init_layer(jax.random.key(2), cfg)
            initial_grad = jax.grad(lambda params: jnp.mean(bl.apply_layer(cfg, params, x) ** 2))(fresh)
            group_grad = float(jnp.linalg.norm(initial_grad["group_vectors"]["w"]))
            assert group_grad > 1e-6, (name, group_grad)
        if name.startswith("beyond_"):
            soft = copy.deepcopy(p)
            soft["group_mix"] = jnp.zeros_like(soft["group_mix"])
            soft["group_out"]["b"] = jnp.zeros_like(soft["group_out"]["b"])
            if name == "beyond_a":
                soft["path_mix"] = jnp.zeros_like(soft["path_mix"])
            reference = bl.content_attention(cfg, soft, x)[0]
            close(bl.apply_layer(cfg, soft, x), reference)
            # rho is zero at initialization: reference is ordinary softmax.
            q, k, v = jnp.split(bl._lin(cfg, soft["qkv"], x), 3, -1)
            sh = lambda z: z.reshape(2, 7, 2, 10).transpose(0, 2, 1, 3)
            q, k, v = sh(q), sh(k), sh(v)
            scores = jnp.where(jnp.tril(jnp.ones((7, 7), bool)), q @ k.swapaxes(-1, -2) / np.sqrt(10), -1e9)
            expected = (jax.nn.softmax(scores, -1) @ v).transpose(0, 2, 1, 3).reshape(2, 7, 20)
            close(reference, bl._lin(cfg, soft["o"], expected))
        results[name] = {"causality_max_error": causal, "init_group_gradient_norm": group_grad,
                         "component_forward_flops_per_token": bl.forward_flops(cfg)}
    return results


def test_rectangular_delta():
    cfg = config("gated_delta", d=24, heads=2, nh=1, beta_max=1.0,
                 delta_key_ratio=0.75, delta_v_expand=2.0)
    params = bl.init_layer(jax.random.key(19), cfg)
    assert params["dq"]["w"].shape == (24, 18)
    assert params["dv"]["w"].shape == (24, 36)
    assert params["delta_out"]["w"].shape == (36, 24)
    x = jax.random.normal(jax.random.key(20), (2, 7, 24))
    out = bl.apply_layer(cfg, params, x)
    assert out.shape == x.shape
    gradient = jax.grad(lambda p: jnp.mean(bl.apply_layer(cfg, p, x) ** 2))(params)
    for name in ("A_log", "dt_bias"):
        assert bool(jnp.isfinite(gradient[name]).all())
        assert float(jnp.linalg.norm(gradient[name])) > 0
    dt = jax.nn.softplus(params["dt_bias"])
    assert bool(((dt >= 0.001) & (dt <= 0.1)).all())


if __name__ == "__main__":
    import json
    output = {"matrix": test_matrix_algebra()}
    test_transport()
    test_affine_precision()
    test_delta_scan()
    test_rectangular_delta()
    output["layers"] = test_layers()
    output["status"] = "pass"
    print(json.dumps(output, sort_keys=True))
