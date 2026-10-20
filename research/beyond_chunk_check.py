"""Numerical proof for the optional exact chunk delta implementation.

CPU smoke: python research/beyond_chunk_check.py --require-gpu 0
GPU proof: python research/beyond_chunk_check.py
This evaluates deterministic tensors and derivatives, not a learning outcome.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

import jax
import jax.numpy as jnp
import numpy as np

from beyond_layers import gated_delta_chunk, gated_delta_scan


def reference(q, k, v, beta, log_decay, initial):
    """Native recurrence with final state exposed for the boundary check."""
    def step(state, xs):
        qt, kt, vt, bt, gt = xs
        state = state * jnp.exp(gt)[..., None, None]
        for micro in range(k.shape[-2]):
            key = kt[:, :, micro]
            prediction = jnp.einsum("bhvk,bhk->bhv", state, key)
            residual = bt[:, :, micro, None] * (vt[:, :, micro] - prediction)
            state = state + residual[..., :, None] * key[..., None, :]
        return state, jnp.einsum("bhvk,bhk->bhv", state, qt)
    final, out = jax.lax.scan(
        step, initial, tuple(jnp.moveaxis(x, 1, 0) for x in (q, k, v, beta, log_decay))
    )
    return jnp.moveaxis(out, 0, 1), final


def metrics(actual, expected):
    a, e = np.asarray(actual, np.float64), np.asarray(expected, np.float64)
    return {
        "max_abs": float(np.max(np.abs(a - e), initial=0)),
        "relative_l2": float(np.linalg.norm((a - e).ravel()) /
                             max(np.linalg.norm(e.ravel()), 1e-30)),
        "max_scaled_abs": float(np.max(np.abs(a - e) / (1 + np.abs(e)), initial=0)),
        "finite": bool(np.isfinite(a).all() and np.isfinite(e).all()),
    }


def inputs(nh, pattern, quantized):
    rng = np.random.default_rng(123)
    b, t, h, dk, dv = (2, 512, 2, 48, 96) if pattern == "full" else (2, 17, 2, 7, 11)
    q = rng.normal(size=(b, t, h, dk)) / np.sqrt(dk)
    k = rng.normal(size=(b, t, h, nh, dk))
    if pattern == "collinear":
        k = rng.normal(size=(b, 1, h, 1, dk)) + 1e-3 * k
    k /= np.linalg.norm(k, axis=-1, keepdims=True)
    v = rng.normal(size=(b, t, h, nh, dv))
    beta = rng.uniform(0, 1 if nh == 1 else 2, size=(b, t, h, nh))
    g = -rng.uniform(0.001, 1, size=(b, t, h))
    if pattern == "collinear":
        beta[:] = (1 if nh == 1 else 2) - 1e-6
        g[:] = -1e-6
    if pattern == "extremes":
        beta = rng.choice([0.0, 1e-7, 0.5, 1.0] if nh == 1 else
                          [0.0, 1e-7, 0.5, 1.0, 1.999999, 2.0], size=beta.shape)
        g = -rng.choice([0.0, 1e-6, 0.01, 1, 20, 80, 100], size=g.shape)
    initial = rng.normal(size=(b, h, dv, dk))
    xs = tuple(jnp.asarray(x, jnp.float32) for x in (q, k, v, beta, g, initial))
    if quantized:
        xs = tuple(x.astype(jnp.bfloat16).astype(jnp.float32) if i < 3 else x
                   for i, x in enumerate(xs))
    return xs


def check(nh, chunk_size, pattern, quantized):
    xs = inputs(nh, pattern, quantized)
    native = jax.jit(reference)
    chunk = jax.jit(lambda *x: gated_delta_chunk(*x, chunk_size=chunk_size))
    a, e = jax.block_until_ready(chunk(*xs)), jax.block_until_ready(native(*xs))
    record = {
        "nh": nh, "chunk_size": chunk_size, "pattern": pattern,
        "quantized_qkv": quantized,
        "output": metrics(a[0], e[0]), "final_state": metrics(a[1], e[1]),
    }
    # Ensure the final-state reference is the production recurrence itself.
    production = gated_delta_scan(*xs[:4], jnp.exp(xs[4]), initial=xs[5])
    record["reference_vs_production"] = metrics(e[0], production)
    assert record["reference_vs_production"]["max_abs"] < 1e-5, record
    rng = np.random.default_rng(890)
    cotangents = tuple(jnp.asarray(rng.normal(size=z.shape), jnp.float32) for z in e)

    def objective(fn, *x):
        out, state = fn(*x)
        return (out * cotangents[0]).sum() + (state * cotangents[1]).sum()

    grad = lambda fn: jax.jit(jax.grad(lambda *x: objective(fn, *x), argnums=tuple(range(6))))
    ag, eg = jax.block_until_ready(grad(chunk)(*xs)), jax.block_until_ready(grad(native)(*xs))
    record["vjp"] = {name: metrics(x, y) for name, x, y in
                     zip(("q", "k", "v", "beta", "log_decay", "initial"), ag, eg)}
    # Fixed numerical tolerances registered before GPU results. Stress cases use
    # nearly collinear keys and beta~2; report absolute errors even when relative
    # criteria pass. These are accuracy checks, never loss-based model selection.
    for value in (record["output"], record["final_state"]):
        assert value["finite"] and value["relative_l2"] < 1e-4, record
        assert value["max_scaled_abs"] < 5e-4, record
    for value in record["vjp"].values():
        assert value["finite"] and value["relative_l2"] < 2e-4, record
        assert value["max_scaled_abs"] < 3e-3, record
    assert all(z.dtype == jnp.float32 for z in a)
    if quantized:
        bx = tuple(x.astype(jnp.bfloat16) if i < 3 else x for i, x in enumerate(xs))
        ba = chunk(*bx)
        assert all(z.dtype == jnp.float32 for z in ba)
        assert all(metrics(x, y)["max_abs"] == 0 for x, y in zip(ba, a))
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-gpu", type=int, default=1)
    parser.add_argument("--chunk-sizes", default="16,32")
    parser.add_argument("--nhs", default="1,4")
    args = parser.parse_args()
    started = time.monotonic()
    if args.require_gpu and jax.default_backend() != "gpu":
        raise RuntimeError("GPU proof requires a GPU backend")
    cases = []
    for nh in map(int, args.nhs.split(",")):
        for c in map(int, args.chunk_sizes.split(",")):
            for pattern, quantized in (
                ("random", False), ("extremes", False), ("collinear", False),
                ("random", True), ("full", False),
            ):
                cases.append(check(nh, c, pattern, quantized))
    result = {
        "check": "chunk_wy_forward_vjp", "status": "passed", "cases": cases,
        "backend": jax.default_backend(), "devices": [str(x) for x in jax.devices()],
        "jax_version": jax.__version__, "seconds": time.monotonic() - started,
        "source_sha256": hashlib.sha256(Path(__file__).with_name("beyond_layers.py").read_bytes()).hexdigest(),
        "default_matmul_precision": str(jax.config.jax_default_matmul_precision),
        "chunk_state_dtype": "float32", "chunk_matmul_precision": "HIGHEST",
    }
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
