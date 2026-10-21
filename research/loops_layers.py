"""LOOPS (LOOPS.md section 3): softmax attention that reads memory in a frame carried along the sequence.

Every token t has an orthogonal frame F_t, and attention compares F_i q_i with F_j k_j, so the score is
q_i . (F_i^T F_j) k_j. When F_t = M_1 M_2 ... M_t is a running product of per-token moves, F_i^T F_j
is the ordered product of the moves between j and i: the holonomy of the path, which never has to be
formed per pair. Position encodings, by the group the moves live in:

    abs    no frame; the model adds learned absolute positions (the BEYOND control)
    rope   every move is the same fixed rotation: F_t = R^t, RoPE on all head dims
    grid   abelian and driven by content: frequency pairs are split into modules, and module m
           advances by a learned velocity u_t = softplus(w.x_t + c)/log 2 (exactly 1 at init, so
           the layer starts as RoPE); its phase is omega_f * sum_{s<=t} u_s, like a grid module
    holo   the grid modules on most dims, plus non-abelian 4-d blocks on the last `holo` dims of
           each head: block b moves by M_t = R_b L(p_t) R(q_t), R_b the fixed RoPE step for those
           dims and L, R left/right multiplication by unit quaternions computed from x_t (identity
           when the content weights are zero). Products of such moves do not commute, so the frame
           records the order of what happened between key and query.

Options: `forget` adds the Forgetting Transformer's gate, logits_ij += sum_{j<s<=i} log f_s with
f = sigmoid(w.x + forget_bias) per head; `vtrans` also transports the values on the holonomy dims
(v_j -> F_j v_j before averaging, the output -> F_i^T out), so the output can carry the running
product. This module does not import lm (that would load a second copy of the harness); matmuls use
cfg.bf16 the same way lm.mm does.
"""

import math

import jax
import jax.numpy as jnp

POSENCS = ("abs", "rope", "grid", "holo")


def _get(cfg, name, default):
    value = getattr(cfg, name, default)
    return default if value is None else value


def _mm(cfg, a, b, spec=None):
    if _get(cfg, "bf16", 0):
        a, b = a.astype(jnp.bfloat16), b.astype(jnp.bfloat16)
        if spec:
            return jnp.einsum(spec, a, b, preferred_element_type=jnp.float32)
        return jnp.matmul(a, b, preferred_element_type=jnp.float32)
    return jnp.einsum(spec, a, b) if spec else a @ b


def _lin(cfg, p, x):
    return _mm(cfg, x, p["w"]) + p.get("b", 0.0)


def dims(cfg):
    """Head width, abelian frequency pairs, holonomy blocks, grid modules."""
    d, h = cfg.d, cfg.heads
    dh = d // h
    posenc = _get(cfg, "posenc", "abs")
    if posenc not in POSENCS:
        raise ValueError(f"posenc must be one of {POSENCS}")
    holo = int(_get(cfg, "holo", 16)) if posenc == "holo" else 0
    if holo % 4 or holo > dh or (dh - holo) % 2:
        raise ValueError("holo must be a multiple of 4 that leaves an even number of abelian dims")
    pairs = (dh - holo) // 2
    modules = int(_get(cfg, "modules", 4)) if posenc in ("grid", "holo") else 1
    if pairs and pairs % modules:
        raise ValueError("abelian frequency pairs must split evenly into modules")
    return dh, pairs, holo // 4, modules


def omega(cfg, dh):
    """RoPE's frequencies for a head of width dh: base^(-2f/dh), f = 0 .. dh/2 - 1."""
    base = float(_get(cfg, "rope_base", 10000.0))
    return base ** (-jnp.arange(dh // 2) * 2.0 / dh)


def init_extra(key, cfg):
    """Parameters of the frame and gate; empty for abs and rope without a gate."""
    d, h = cfg.d, cfg.heads
    _, pairs, blocks, modules = dims(cfg)
    posenc = _get(cfg, "posenc", "abs")
    p = {}
    if posenc in ("grid", "holo") and pairs:
        p["vel"] = {"w": jnp.zeros((d, h * modules)), "b": jnp.zeros(h * modules)}
    if blocks:
        scale = float(_get(cfg, "holo_init", 0.05))
        p["quat"] = {"w": jax.random.normal(key, (d, h * blocks * 6)) * scale / math.sqrt(d),
                     "b": jnp.zeros(h * blocks * 6)}
    if _get(cfg, "forget", 0):
        p["fgate"] = {"w": jnp.zeros((d, h)), "b": jnp.full(h, float(_get(cfg, "forget_bias", 5.0)))}
    return p


def quat_left(p):
    """4x4 matrix of v -> p v (quaternion product), p = (w, x, y, z) along the last axis."""
    w, x, y, z = (p[..., i] for i in range(4))
    return jnp.stack([jnp.stack([w, -x, -y, -z], -1), jnp.stack([x, w, -z, y], -1),
                      jnp.stack([y, z, w, -x], -1), jnp.stack([z, -y, x, w], -1)], -2)


def quat_right(q):
    """4x4 matrix of v -> v q."""
    w, x, y, z = (q[..., i] for i in range(4))
    return jnp.stack([jnp.stack([w, -x, -y, -z], -1), jnp.stack([x, w, z, -y], -1),
                      jnp.stack([y, -z, w, x], -1), jnp.stack([z, y, -x, w], -1)], -2)


def unit_quaternion(a):
    """(1, a) / |(1, a)|: the identity at a = 0, smooth, never degenerate."""
    full = jnp.concatenate([jnp.ones_like(a[..., :1]), a], -1)
    return full / jnp.sqrt(jnp.sum(full * full, -1, keepdims=True))


def plane_rotation(theta):
    c, s = jnp.cos(theta), jnp.sin(theta)
    return jnp.stack([jnp.stack([c, -s], -1), jnp.stack([s, c], -1)], -2)


def base_moves(cfg, dh, pairs, blocks):
    """R_b: the fixed RoPE step on block b's two planes, the lowest frequencies of the head."""
    w = omega(cfg, dh)[pairs:]
    r = jnp.zeros((blocks, 4, 4))
    r = r.at[:, :2, :2].set(plane_rotation(w[0::2]))
    return r.at[:, 2:, 2:].set(plane_rotation(w[1::2]))


def prefix_frames(moves):
    """F_t = M_1 M_2 ... M_t along axis 1, by an associative scan (earlier factor on the left)."""
    return jax.lax.associative_scan(lambda a, b: a @ b, moves, axis=1)


def frames(cfg, p, x):
    """The frame of every token: cos/sin of the abelian phases and the holonomy blocks F_t."""
    b, t, _ = x.shape
    h = cfg.heads
    dh, pairs, blocks, modules = dims(cfg)
    posenc = _get(cfg, "posenc", "abs")
    out = {}
    if posenc == "abs":
        return out
    w = omega(cfg, dh)[:pairs]
    if not pairs:
        out["cos"] = out["sin"] = jnp.zeros((b, t, h, 0))
    elif posenc == "rope":
        tau = jnp.broadcast_to(jnp.arange(t, dtype=jnp.float32)[None, :, None, None], (b, t, h, 1))
        theta = tau * w
    else:
        z = (x @ p["vel"]["w"] + p["vel"]["b"]).reshape(b, t, h, modules)
        u = jax.nn.softplus(z.astype(jnp.float32)) / math.log(2.0)
        tau = jnp.cumsum(u, axis=1)
        module = jnp.arange(pairs) * modules // pairs
        theta = tau[..., module] * w
    if pairs:
        out["cos"], out["sin"] = jnp.cos(theta), jnp.sin(theta)
    if blocks:
        a = (x @ p["quat"]["w"] + p["quat"]["b"]).astype(jnp.float32).reshape(b, t, h, blocks, 2, 3)
        left, right = quat_left(unit_quaternion(a[..., 0, :])), quat_right(unit_quaternion(a[..., 1, :]))
        moves = base_moves(cfg, dh, pairs, blocks) @ left @ right
        out["F"] = prefix_frames(moves)
    return out


def rotate(cfg, fr, v, inverse=False):
    """Apply each token's frame to v [B, T, H, dh]; inverse applies F^T (rotation back)."""
    if not fr:
        return v
    dh, pairs, blocks, _ = dims(cfg)
    sign = -1.0 if inverse else 1.0
    x1, x2 = v[..., :pairs], v[..., pairs:2 * pairs]
    c, s = fr["cos"], sign * fr["sin"]
    parts = [x1 * c - x2 * s, x1 * s + x2 * c]
    if blocks:
        hv = v[..., 2 * pairs:].reshape(*v.shape[:-1], blocks, 4)
        spec = "bthnji,bthnj->bthni" if inverse else "bthnij,bthnj->bthni"
        parts.append(jnp.einsum(spec, fr["F"], hv).reshape(*v.shape[:-1], 4 * blocks))
    return jnp.concatenate(parts, -1)


def rotate_holo(cfg, fr, v, inverse=False):
    """Transport only the holonomy dims (value transport); the abelian dims pass through."""
    dh, pairs, blocks, _ = dims(cfg)
    if not blocks:
        return v
    hv = v[..., 2 * pairs:].reshape(*v.shape[:-1], blocks, 4)
    spec = "bthnji,bthnj->bthni" if inverse else "bthnij,bthnj->bthni"
    moved = jnp.einsum(spec, fr["F"], hv).reshape(*v.shape[:-1], 4 * blocks)
    return jnp.concatenate([v[..., :2 * pairs], moved], -1)


def attention(cfg, p, x, project_qkv):
    """Causal softmax attention in transported frames. x is the normed input; project_qkv(p, x)
    returns q, k, v [B, T, D] (with the shared short convolution, if the layer has one)."""
    b, t, d = x.shape
    h = cfg.heads
    dh = d // h
    q, k, v = project_qkv(p, x)
    split = lambda y: y.reshape(b, t, h, dh)
    q, k, v = split(q), split(k), split(v)
    fr = frames(cfg, p, x)
    q, k = rotate(cfg, fr, q), rotate(cfg, fr, k)
    vtrans = bool(_get(cfg, "vtrans", 0)) and "F" in fr
    if vtrans:
        v = rotate_holo(cfg, fr, v)
    heads = lambda y: y.transpose(0, 2, 1, 3)
    s = _mm(cfg, heads(q), heads(k), "bhtc,bhsc->bhts") / math.sqrt(dh)
    if "fgate" in p:
        logf = jax.nn.log_sigmoid((x @ p["fgate"]["w"] + p["fgate"]["b"]).astype(jnp.float32))
        c = jnp.cumsum(logf, axis=1).transpose(0, 2, 1)          # [B, H, T]
        s = s + c[:, :, :, None] - c[:, :, None, :]
    mask = jnp.tril(jnp.ones((t, t), bool))
    a = jax.nn.softmax(jnp.where(mask, s, -1e9), -1)
    o = _mm(cfg, a, heads(v), "bhts,bhsc->bhtc").transpose(0, 2, 1, 3)
    if vtrans:
        o = rotate_holo(cfg, fr, o, inverse=True)
    return _lin(cfg, p["o"], o.reshape(b, t, d))


def extra_flops(cfg, seq_len):
    """Forward FLOPs/token of the frame and gate on top of convolved softmax (multiply-add = 2)."""
    d, h = cfg.d, cfg.heads
    dh, pairs, blocks, modules = dims(cfg)
    posenc = _get(cfg, "posenc", "abs")
    ta = (seq_len + 1) / 2
    f = 0.0
    if posenc != "abs":
        f += 2 * 6 * pairs * h                    # rotate q and k: four multiplies, two adds per pair
        f += 2 * pairs * h                        # phases (cos, sin as one op each)
    if posenc in ("grid", "holo") and pairs:
        f += 2 * d * h * modules + 4 * h * modules + pairs * h   # velocity, softplus, cumsum, phase
    if blocks:
        steps = 0
        n = seq_len
        while n > 1:                              # associative scan: pair reduction and fill-in
            steps += n - 1
            n //= 2
        f += 2 * d * h * blocks * 6 + h * blocks * 40          # quaternions, normalisation
        f += h * blocks * 2 * 2 * 128                          # R_b L R: two 4x4 products
        f += h * blocks * 128 * 2 * steps / seq_len            # prefix products
        f += 2 * h * blocks * 2 * 32                           # transport q and k
        if _get(cfg, "vtrans", 0):
            f += 2 * h * blocks * 2 * 32                       # transport v and the output
    if _get(cfg, "forget", 0):
        f += 2 * d * h + 6 * h + ta * h                        # gate, log-sigmoid, cumsum, bias add
    return float(f)
