"""Beyond layers: explicit coupling order around one shared Parallax estimator.

A: compose -> select (parallel transport of values, with a full-state anchor).
B: select || compose (independent content and matrix-state branches).
C: select -> compose (the selected content conditions each matrix transition).

These are combinations of established components, not claims to have invented
Householder recurrence, local-linear attention, or group-valued token features.
See BEYOND.md for the frozen hypotheses and the prior-art audit.

All functions consume [batch,time,width] activations. ``forward_flops`` counts
attention/memory operations only; the caller adds the MLP and vocabulary head.
Dense products use the harness's optional bf16 input / fp32 output convention.
Matrix products, normalization, probabilities, and recurrent state stay fp32.
"""

import math

import jax
import jax.numpy as jnp


KINDS = ("beyond_a", "beyond_b", "beyond_c", "gated_delta", "prefix")


def _get(cfg, name, default):
    value = getattr(cfg, name, default)
    return default if value is None else value


def _kind(cfg, kind):
    return kind or cfg.arch


def _dense(key, fan_in, fan_out, scale=1.0):
    return {
        "w": jax.random.normal(key, (fan_in, fan_out)) * scale / math.sqrt(fan_in),
        "b": jnp.zeros(fan_out),
    }


def init_qkv_conv(key, d, width):
    """Bias-free causal depthwise QKV kernel, with lag zero stored first.

    This is the established Primer-style local binding component. Initializing
    it from a separate key preserves every pre-existing parameter draw.
    """
    if width < 1:
        raise ValueError("qkv_conv width must be positive")
    bound = 1 / math.sqrt(width)
    return jax.random.uniform(key, (width, 3 * d), minval=-bound, maxval=bound)


def _mm(cfg, a, b, spec=None):
    if _get(cfg, "bf16", 0):
        a, b = a.astype(jnp.bfloat16), b.astype(jnp.bfloat16)
        if spec:
            return jnp.einsum(spec, a, b, preferred_element_type=jnp.float32)
        return jnp.matmul(a, b, preferred_element_type=jnp.float32)
    return jnp.einsum(spec, a, b) if spec else a @ b


def _lin(cfg, p, x):
    return _mm(cfg, x, p["w"]) + p.get("b", 0.0)


def _unit(x):
    # max, rather than +epsilon, keeps nonzero Householder vectors exactly unit.
    return x / jnp.sqrt(jnp.maximum(jnp.sum(x * x, -1, keepdims=True), 1e-12))


def _dims(cfg):
    d, h = cfg.d, cfg.heads
    if d % h:
        raise ValueError("model width must be divisible by attention heads")
    gh = int(_get(cfg, "gheads", h) or h)
    gd = int(_get(cfg, "gdim", 5))
    nh = int(_get(cfg, "group_nh", 4))
    order = int(_get(cfg, "group_order", 2))
    if gd < 2 or nh <= 0 or nh % 2 or order not in (0, 1, 2):
        raise ValueError("gdim>=2, positive even group_nh, and group_order in {0,1,2} required")
    return d, h, d // h, gh, gd, nh, order


def _delta_dims(cfg):
    """Canonical allocation is K=.75D and V=2K, as the public FLA layer."""
    key_head = cfg.d / cfg.heads * float(_get(cfg, "delta_key_ratio", 0.75))
    value_head = key_head * float(_get(cfg, "delta_v_expand", 2.0))
    if not math.isclose(key_head, round(key_head)) or not math.isclose(value_head, round(value_head)):
        raise ValueError("delta_key_ratio/delta_v_expand must produce integer head dimensions")
    dk, dv = int(round(key_head)), int(round(value_head))
    if min(dk, dv) < 1:
        raise ValueError("Delta key and value head dimensions must be positive")
    return dk, dv, cfg.heads * dk, cfg.heads * dv


def init_layer(key, cfg, kind=None):
    """Initialize a complete attention component, including qkv/o if applicable.

    lm.init may keep its already-created qkv/o instead, so candidates have the
    same common parameter initialization as softmax at a given seed.
    """
    kind = _kind(cfg, kind)
    if kind not in KINDS:
        raise ValueError(kind)
    d, h, dh, gh, gd, gnh, order = _dims(cfg)
    keys = iter(jax.random.split(key, 32))
    scale = 1 / math.sqrt(2 * int(_get(cfg, "layers", 1)))
    p = {}
    if kind.startswith("beyond_"):
        p["qkv"] = _dense(next(keys), d, 3 * d)
        p["o"] = _dense(next(keys), d, d, scale)
        p["wr"] = {"w": jnp.zeros((d, d)), "b": jnp.zeros(d)}
        width = int(_get(cfg, "qkv_conv", 0))
        if width:
            p["qkv_conv"] = init_qkv_conv(jax.random.fold_in(key, 911), d, width)
    if kind in ("beyond_a", "beyond_b", "beyond_c", "prefix"):
        # Independent parameters in equal initial pairs: H(k)H(k)=I.
        # Their derivatives have opposite signs and do not vanish individually.
        group_key = next(keys)
        group_init = _get(cfg, "group_init", "paired")
        if group_init == "paired":
            half = jax.random.normal(group_key, (d, gh, gnh // 2, gd)) / math.sqrt(d)
            weights = jnp.repeat(half, 2, axis=2).reshape(d, gh * gnh * gd)
        elif group_init == "random":
            weights = jax.random.normal(group_key, (d, gh * gnh * gd)) / math.sqrt(d)
        else:
            raise ValueError("group_init must be paired or random")
        p["group_vectors"] = {"w": weights, "b": jnp.zeros(gh * gnh * gd)}
        p["group_out"] = _dense(next(keys), gh * gd * gd, d, scale)
        initial = 1.0 if kind == "prefix" else float(_get(cfg, "branch_scale", 0.1))
        # Mix sectors on their features, then pay for just one projection.
        p["group_mix"] = jnp.full((order + 1, gh * gd * gd), initial / math.sqrt(order + 1))
        if kind == "beyond_a":
            if gh != h:
                raise ValueError("beyond_a requires gheads=heads for value transport")
            p["path_mix"] = jnp.full((h,), float(_get(cfg, "path_scale", 0.1)))
        if kind == "beyond_c":
            p["context_mix"] = jnp.array(float(_get(cfg, "context_scale", 1.0)))
    if kind == "gated_delta":
        nh = int(_get(cfg, "nh", 4))
        width = int(_get(cfg, "conv_width", 4))
        dk, dv, kd, vd = _delta_dims(cfg)
        if nh < 1 or width < 1:
            raise ValueError("nh and conv_width must be positive")
        for name, size in (("dq", kd), ("dk", nh * kd), ("dv", nh * vd),
                           ("dbeta", h * nh), ("ddecay", h), ("dgate", vd)):
            p[name] = _dense(next(keys), d, size)
            del p[name]["b"]
        # Public FLA GatedDeltaNet initialization and continuous-time decay.
        # These two parameters must be exempted from optimizer weight decay.
        rates = jax.random.uniform(next(keys), (h,), minval=1e-6, maxval=16.0)
        p["A_log"] = jnp.log(rates)
        dt = jnp.exp(jax.random.uniform(next(keys), (h,),
                                       minval=math.log(0.001), maxval=math.log(0.1)))
        p["dt_bias"] = dt + jnp.log(-jnp.expm1(-dt))
        for name, size in (("cq", kd), ("ck", nh * kd), ("cv", nh * vd)):
            # Bias-free depthwise Conv1d's standard fan-in initialization.
            bound = 1 / math.sqrt(width)
            p[name] = jax.random.uniform(next(keys), (width, size), minval=-bound, maxval=bound)
        p["delta_norm"] = jnp.ones((h, dv))
        p["delta_out"] = _dense(next(keys), vd, d, scale)
        del p["delta_out"]["b"]
    return p


def parallax_weights(p, rho, keys):
    """Signed affine correction; row sums are one, but precision is learned.

    If rho=(Cov_p[key]+lambda I)^-1(E_p[key]-query), these are ridge-LLA
    weights. A free learned rho, as in Parallax, need not satisfy that equation.
    """
    score = jnp.einsum("bhtd,bhsd->bhts", rho, keys)
    return p * (1.0 - score + jnp.sum(p * score, -1, keepdims=True))


def content_attention(cfg, p, x):
    """Return content output and (corrected weights, original value heads)."""
    b, t, d = x.shape
    h = cfg.heads
    qkv = _lin(cfg, p["qkv"], x)
    if "qkv_conv" in p:
        qkv = causal_depthwise_conv(qkv, p["qkv_conv"])
    q, k, v = jnp.split(qkv, 3, -1)
    split = lambda z: z.reshape(b, t, h, d // h).transpose(0, 2, 1, 3)
    q, k, v = split(q), split(k), split(v)
    logits = _mm(cfg, q, k, "bhtd,bhsd->bhts") / math.sqrt(d // h)
    cap = float(_get(cfg, "cap", 0.0))
    if cap > 0:
        logits = cap * jnp.tanh(logits / cap)
    if _get(cfg, "causal", 1):
        logits = jnp.where(jnp.tril(jnp.ones((t, t), bool)), logits, -1e9)
    probabilities = jax.nn.softmax(logits, -1)
    if _get(cfg, "ablate", "none") == "precision":
        weights = probabilities
    else:
        rho = split(_lin(cfg, p["wr"], x))
        # Match the matmul precision convention of the existing Parallax arm.
        probe = _mm(cfg, rho, k, "bhtd,bhsd->bhts")
        weights = probabilities * (1 - probe + (probabilities * probe).sum(-1, keepdims=True))
    values = _mm(cfg, weights, v, "bhts,bhsd->bhtd")
    y = _lin(cfg, p["o"], values.transpose(0, 2, 1, 3).reshape(b, t, d))
    return y, weights, v


def householder_products(vectors):
    """Exact orthogonal products, [...,microsteps,gdim] -> [...,gdim,gdim].

    Left action and time order are explicit: the final microstep acts last.
    Exact beta=2 avoids the loss of invertibility in generalized reflectors;
    transpose can consequently be used as inverse in value transport.
    """
    vectors = _unit(vectors)
    gd = vectors.shape[-1]
    matrix = jnp.broadcast_to(jnp.eye(gd, dtype=vectors.dtype), vectors.shape[:-2] + (gd, gd))
    for step in range(vectors.shape[-2]):
        k = vectors[..., step, :]
        row = jnp.einsum("...i,...ij->...j", k, matrix)
        matrix = matrix - 2 * k[..., :, None] * row[..., None, :]
    return matrix


def matrix_prefix(transitions):
    """Inclusive left-action prefix P_t=U_t...U_0, in associative parallel scan."""
    return jax.lax.associative_scan(lambda a, b: b @ a, transitions, axis=1)


def matrix_features(transitions, order=2):
    """Short marked sectors and full prefix, all on comparable length scales.

    Arity 1: U_t. Arity 2: mean_{j<t} U_t U_j. The latter is zero at t=0.
    The full prefix has no normalization or gating that can erase its state.
    """
    prefix = matrix_prefix(transitions)
    features = []
    if order >= 1:
        features.append(transitions)
    if order >= 2:
        earlier = jnp.cumsum(transitions, axis=1) - transitions
        divisor = jnp.maximum(jnp.arange(transitions.shape[1]), 1)[None, :, None, None, None]
        features.append((transitions @ earlier) / divisor)
    features.append(prefix)
    return jnp.stack(features, 2), prefix


def transported_attention(weights, values, prefix, cfg=None):
    """P_t sum_j W_tj P_j^T v_j, in independent gdim blocks of each value head.

    values: [B,H,T,dh], prefix: [B,T,H,g,g]. Padding is zero and removed.
    This is precision in the common transported frame, not a claim that
    arbitrary varying rotations preserve affine precision in raw value space.
    """
    b, h, t, dh = values.shape
    gd = prefix.shape[-1]
    blocks = (dh + gd - 1) // gd
    padded = jnp.pad(values, ((0, 0), (0, 0), (0, 0), (0, blocks * gd - dh)))
    local = padded.reshape(b, h, t, blocks, gd)
    frames = prefix.transpose(0, 2, 1, 3, 4)
    canonical = jnp.einsum("bhtji,bhtnj->bhtni", frames, local)
    canonical = canonical.reshape(b, h, t, blocks * gd)
    if cfg is None:
        selected = jnp.einsum("bhts,bhsd->bhtd", weights, canonical)
    else:
        selected = _mm(cfg, weights, canonical, "bhts,bhsd->bhtd")
    selected = selected.reshape(b, h, t, blocks, gd)
    out = jnp.einsum("bhtij,bhtnj->bhtni", frames, selected)
    return out.reshape(b, h, t, blocks * gd)[..., :dh]


def causal_depthwise_conv(x, kernel):
    """Depthwise FIR, kernel[0] is current token; no padding reads the future."""
    total = x * kernel[0]
    for lag in range(1, kernel.shape[0]):
        shifted = jnp.pad(x[:, :-lag], ((0, 0), (lag, 0), (0, 0))) if lag < x.shape[1] else jnp.zeros_like(x)
        total = total + shifted * kernel[lag]
    return total


def gated_delta_scan(q, k, v, beta, decay, initial=None, unroll=1):
    """Generalized delta updates with per-token decay, then matrix-query read.

    q [B,T,H,dk], k [B,T,H,nh,dk], v [B,T,H,nh,dv].
    S<-decay*S; for each microstep S<-S+beta*(v-Sk)k^T.
    """
    b, _, h, _, dk = k.shape
    dv = v.shape[-1]
    initial = jnp.zeros((b, h, dv, dk), q.dtype) if initial is None else initial

    def step(state, inputs):
        qt, kt, vt, bt, at = inputs
        state = state * at[..., None, None]
        for micro in range(kt.shape[-2]):
            key = kt[:, :, micro]
            prediction = jnp.einsum("bhvk,bhk->bhv", state, key)
            residual = bt[:, :, micro, None] * (vt[:, :, micro] - prediction)
            state = state + residual[..., :, None] * key[..., None, :]
        output = jnp.einsum("bhvk,bhk->bhv", state, qt)
        return state, output

    _, outputs = jax.lax.scan(
        step, initial, tuple(jnp.moveaxis(z, 1, 0) for z in (q, k, v, beta, decay)),
        unroll=unroll,
    )
    return jnp.moveaxis(outputs, 0, 1)


def gated_delta_chunk(q, k, v, beta, log_decay, initial=None, *, chunk_size=32,
             dtype=jnp.float32, chunk_unroll=1):
    """Exact gated recurrence using independent triangular solves per chunk.

    q[B,T,H,K], k[B,T,H,nh,K], v[B,T,H,nh,V],
    beta[B,T,H,nh], log_decay[B,T,H], initial[B,H,V,K].
    The output and state always use ``dtype`` (FP32 by default), including when
    inputs were quantized to BF16. All state products/solves use full precision.
    """
    q, k, v, beta, log_decay = (
        jnp.asarray(x, dtype) for x in (q, k, v, beta, log_decay)
    )
    b, t, h, nh, dk = k.shape
    dv = v.shape[-1]
    c = int(chunk_size)
    if c < 1 or c % nh:
        raise ValueError("chunk_size must be a positive multiple of nh")
    m = c // nh
    chunks = math.ceil(t / m)
    padded_t = chunks * m
    pad = padded_t - t
    if pad:
        q = jnp.pad(q, ((0, 0), (0, pad), (0, 0), (0, 0)))
        k = jnp.pad(k, ((0, 0), (0, pad), (0, 0), (0, 0), (0, 0)))
        v = jnp.pad(v, ((0, 0), (0, pad), (0, 0), (0, 0), (0, 0)))
        beta = jnp.pad(beta, ((0, 0), (0, pad), (0, 0), (0, 0)))
        log_decay = jnp.pad(log_decay, ((0, 0), (0, pad), (0, 0)))
    # A padded microstep is identity: k=v=beta=log_decay=0.
    g_micro = jnp.zeros((b, padded_t, h, nh), dtype)
    g_micro = g_micro.at[..., 0].set(log_decay)
    q = q.transpose(0, 2, 1, 3).reshape(b, h, chunks, m, dk)
    k = k.transpose(0, 2, 1, 3, 4).reshape(b, h, chunks, c, dk)
    v = v.transpose(0, 2, 1, 3, 4).reshape(b, h, chunks, c, dv)
    beta = beta.transpose(0, 2, 1, 3).reshape(b, h, chunks, c)
    g = jnp.cumsum(
        g_micro.transpose(0, 2, 1, 3).reshape(b, h, chunks, c), axis=-1
    )
    eg = jnp.exp(g)
    idx = jnp.arange(c)
    strict_lower = idx[:, None] > idx[None, :]
    diagonal = idx[:, None] == idx[None, :]
    # Crucially mask *before* exp. For non-positive decay, retained differences
    # are non-positive; unused upper-triangle positive differences cannot overflow.
    pair_decay = jnp.exp(jnp.where(strict_lower, g[..., :, None] - g[..., None, :], 0))
    gram = jnp.matmul(k, jnp.swapaxes(k, -1, -2), precision=jax.lax.Precision.HIGHEST)
    lower = jnp.where(strict_lower, beta[..., :, None] * gram * pair_decay, 0)
    a = jnp.where(diagonal, jnp.asarray(1, dtype), lower)
    rhs = jnp.concatenate(
        (beta[..., None] * v, (beta * eg)[..., None] * k), axis=-1
    )
    uw = jax.lax.linalg.triangular_solve(
        a, rhs, left_side=True, lower=True, unit_diagonal=True
    )
    u, w = uw[..., :dv], uw[..., dv:]

    # Only original token queries are evaluated, after their last microstep.
    query_idx = jnp.arange(m) * nh + (nh - 1)
    gq = jnp.take(g, query_idx, axis=-1)
    query_mask = query_idx[:, None] >= idx[None, :]
    query_decay = jnp.exp(jnp.where(query_mask, gq[..., :, None] - g[..., None, :], 0))
    qk = jnp.matmul(q, jnp.swapaxes(k, -1, -2), precision=jax.lax.Precision.HIGHEST)
    coeff = jnp.where(query_mask, qk * query_decay, 0)
    scaled_q = q * jnp.take(eg, query_idx, axis=-1)[..., None]
    end_k = k * jnp.exp(g[..., -1, None] - g)[..., None]
    end_decay = eg[..., -1]
    if initial is None:
        initial = jnp.zeros((b, h, dv, dk), dtype)
    else:
        initial = jnp.asarray(initial, dtype)

    def step(state, inputs):
        ut, wt, qt, ct, kt, at = inputs
        st = jnp.swapaxes(state, -1, -2)
        residual = ut - jnp.matmul(wt, st, precision=jax.lax.Precision.HIGHEST)
        output = (
            jnp.matmul(qt, st, precision=jax.lax.Precision.HIGHEST)
            + jnp.matmul(ct, residual, precision=jax.lax.Precision.HIGHEST)
        )
        state = state * at[..., None, None] + jnp.matmul(
            jnp.swapaxes(residual, -1, -2), kt,
            precision=jax.lax.Precision.HIGHEST,
        )
        return state, output

    final, output = jax.lax.scan(
        step, initial,
        tuple(jnp.moveaxis(x, 2, 0) for x in (u, w, scaled_q, coeff, end_k, end_decay)),
        unroll=chunk_unroll,
    )
    output = jnp.moveaxis(output, 0, 2).reshape(b, h, padded_t, dv)
    return output.transpose(0, 2, 1, 3)[:, :t], final


def _delta_chunk_flops(t, nh, dk, dv, chunk_size=32):
    """Explicit FP operations/head/sequence for the concrete dense prototype.

    MAC=2; exp=1 elementary op; cumsum=C-1. Mask/select/cast/reshape/padding
    cost no arithmetic. Full Gram and query matrices are charged, including
    masked entries. Unit triangular solve costs C(C-1)*(K+V), from exact
    forward substitution. This is an algorithmic count, not kernel profiling.
    It includes padded tokens and returns the serial/log-decay count too.
    """
    c = int(chunk_size)
    if c < 1 or c % nh:
        raise ValueError("chunk_size must be a positive multiple of nh")
    m = c // nh
    n = math.ceil(t / m)
    per_chunk = {
        "cumulative_log_decay": c - 1,
        "exp_cumulative_decay": c,
        "key_gram": 2 * c * c * dk,
        "gram_decay_differences_exp": 2 * c * c,
        "gram_beta_decay_scaling": 2 * c * c,
        "rhs_beta_value": c * dv,
        "rhs_beta_decay_key": c + c * dk,
        "unit_triangular_solve": c * (c - 1) * (dk + dv),
        "query_key": 2 * m * c * dk,
        "query_decay_differences_exp_scaling": 3 * m * c,
        "query_state_scaling": m * dk,
        "end_key_decay_differences_exp_scaling": 2 * c + c * dk,
        "state_prediction": 2 * c * dk * dv,
        "state_residual_subtraction": c * dv,
        "query_initial_state": 2 * m * dk * dv,
        "query_residual_values": 2 * m * c * dv,
        "query_output_add": m * dv,
        "state_update": 2 * c * dk * dv,
        "state_scale_and_add": 2 * dk * dv,
    }
    serial = t * (nh * (4 * dk * dv + 2 * dv) + 3 * dk * dv + 1)
    total = n * sum(per_chunk.values())
    return {
        "sequence_length": t,
        "nh": nh,
        "chunk_size_microsteps": c,
        "chunks": n,
        "padding_tokens": n * m - t,
        "per_chunk": per_chunk,
        "total_per_head": total,
        "per_token_per_head": total / t,
        "serial_total_per_head": serial,
        "serial_per_token_per_head": serial / t,
        "delta_per_token_per_head": (total - serial) / t,
        # The solve's JAX VJP uses another solve plus a dense dA product.
        # Its training work exceeds the harness's blanket 3*forward by this.
        # Other primitives retain the harness approximation here.
        "solve_vjp_extra_over_3x_forward_total_per_head": n * c * (c + 1) * (dk + dv),
        "solve_vjp_extra_over_3x_forward_per_token_per_head": n * c * (c + 1) * (dk + dv) / t,
    }


def apply_layer(cfg, p, x, kind=None):
    kind = _kind(cfg, kind)
    if kind not in KINDS:
        raise ValueError(kind)
    b, t, d = x.shape
    _, h, dh, gh, gd, gnh, order = _dims(cfg)
    ablate = _get(cfg, "ablate", "none")
    if kind == "gated_delta":
        nh = int(_get(cfg, "nh", 4))
        dk, dv, kd, vd = _delta_dims(cfg)
        q = jax.nn.silu(causal_depthwise_conv(_lin(cfg, p["dq"], x), p["cq"]))
        k = jax.nn.silu(causal_depthwise_conv(_lin(cfg, p["dk"], x), p["ck"]))
        v = jax.nn.silu(causal_depthwise_conv(_lin(cfg, p["dv"], x), p["cv"]))
        q = _unit(q.reshape(b, t, h, dk)) / math.sqrt(dk)
        k = _unit(k.reshape(b, t, h, nh, dk))
        v = v.reshape(b, t, h, nh, dv)
        beta_logits = _lin(cfg, p["dbeta"], x).reshape(b, t, h, nh) + float(_get(cfg, "beta0", 0.0))
        beta = float(_get(cfg, "beta_max", 2.0)) * jax.nn.sigmoid(beta_logits)
        log_decay = -jnp.exp(p["A_log"]) * jax.nn.softplus(_lin(cfg, p["ddecay"], x) + p["dt_bias"])
        chunk_size = int(_get(cfg, "delta_chunk", 0))
        if chunk_size:
            out, _ = gated_delta_chunk(q, k, v, beta, log_decay.reshape(b, t, h),
                                       chunk_size=chunk_size)
        else:
            decay = jnp.exp(log_decay).reshape(b, t, h)
            out = gated_delta_scan(q, k, v, beta, decay, unroll=int(_get(cfg, "delta_unroll", 1)))
        out = out / jnp.sqrt((out * out).mean(-1, keepdims=True) + 1e-5) * p["delta_norm"]
        gate = jax.nn.silu(_lin(cfg, p["dgate"], x)).reshape(b, t, h, dv)
        return _lin(cfg, p["delta_out"], (out * gate).reshape(b, t, vd))

    if kind != "prefix":
        content, weights, values = content_attention(cfg, p, x)
        if ablate == "composition":
            return content
    else:
        content = jnp.zeros_like(x)
    source = x
    if kind == "beyond_c" and ablate != "coupling":
        source = source + jnp.tanh(p["context_mix"]) * content
    vectors = _lin(cfg, p["group_vectors"], source).reshape(b, t, gh, gnh, gd)
    transitions = householder_products(vectors)
    features, prefix = matrix_features(transitions, order)
    # Mix all short/full sectors on features, then project exactly once.
    f = features.reshape(b, t, order + 1, gh * gd * gd) * math.sqrt(gd)
    mixed = (f * p["group_mix"][None, None]).sum(2)
    composition = _lin(cfg, p["group_out"], mixed)
    if kind == "beyond_a" and ablate != "coupling":
        transported = transported_attention(weights, values, prefix, cfg)
        ordinary = _mm(cfg, weights, values, "bhts,bhsd->bhtd")
        correction = (transported - ordinary) * jnp.tanh(p["path_mix"])[None, :, None, None]
        correction = correction.transpose(0, 2, 1, 3).reshape(b, t, d)
        # The shared output bias belongs only to the ordinary content path.
        content = content + _mm(cfg, correction, p["o"]["w"])
    return content + composition


def _associative_products(n):
    # jax.lax.associative_scan: pair reduction then interleaving reconstruction.
    count = 0
    while n > 1:
        count += n - 1
        n //= 2
    return count


def forward_flops(cfg, kind=None, seq_len=None):
    """Forward FLOPs per token for this component (not MLP/vocabulary).

    Multiply-adds count two. Attention uses the existing harness's ideal causal
    triangular kernel convention, ta=(T+1)/2; the unfused JAX implementation
    actually materializes T*T scores. Parallax's two value passes are counted
    identically to lm.py even when a compiler combines them. Scalar activation/
    normalization costs are elementary estimates. This is an algorithmic FLOP
    comparison, not a wall-time or hardware-throughput claim.
    """
    kind = _kind(cfg, kind)
    d, h, dh, gh, gd, gnh, order = _dims(cfg)
    t = int(seq_len or cfg.ctx)
    ta = (t + 1) / 2
    if kind == "gated_delta":
        nh = int(_get(cfg, "nh", 4))
        cw = int(_get(cfg, "conv_width", 4))
        dk, dv, kd, vd = _delta_dims(cfg)
        # q,k,v, beta,decay,output-gate, output projections.
        projection = 2 * d * ((1 + nh) * kd + (nh + 2) * vd + h * (nh + 1))
        conv = 2 * cw * ((1 + nh) * kd + nh * vd)
        activation_norm = 12 * ((1 + nh) * kd + nh * vd) + 12 * vd + 12 * h * (nh + 1)
        state = h * (nh * (4 * dv * dk + 2 * dv) + 3 * dv * dk)
        chunk_size = int(_get(cfg, "delta_chunk", 0))
        if chunk_size:
            # Full dense Gram/query work, solve, padding, state updates, and
            # scalar operations are charged. activation_norm already includes
            # one per-token decay exp, so avoid charging that operation twice.
            state = h * (_delta_chunk_flops(t, nh, dk, dv, chunk_size)["per_token_per_head"] - 1)
        return float(projection + conv + activation_norm + state)
    content = 0
    if kind != "prefix":
        # Exactly the existing lm.py Parallax count and causal convention.
        content = 10 * d * d + 8 * ta * d + 8 * ta * h + 3 * d
        if _get(cfg, "ablate", "none") == "precision":
            content = 8 * d * d + 4 * ta * d + 5 * ta * h
        # Three projected streams, width taps, multiply-plus-add convention.
        content += 6 * int(_get(cfg, "qkv_conv", 0)) * d
        if _get(cfg, "ablate", "none") == "composition":
            return float(content)
    transition = 2 * d * gh * gnh * gd + gh * gnh * (6 * gd * gd + 5 * gd)
    prefix = 2 * gh * gd ** 3 * _associative_products(t) / t
    short = 0
    if order >= 2:
        short = 2 * gh * gd ** 3 + 3 * gh * gd * gd
    readout = 2 * gh * gd * gd * d + (2 * order + 1) * gh * gd * gd
    coupling = 0
    if kind == "beyond_a" and _get(cfg, "ablate", "none") != "coupling":
        padded = h * ((dh + gd - 1) // gd) * gd
        # Two frame transforms; two corrected value passes (same convention as
        # Parallax); projected difference. Ordinary AV is shared with content.
        coupling = 4 * padded * gd + 4 * ta * padded + 2 * d * d + 3 * d
    if kind == "beyond_c" and _get(cfg, "ablate", "none") != "coupling":
        coupling = 3 * d
    return float(content + transition + prefix + short + readout + coupling)


def training_extra_flops(cfg, kind=None, seq_len=None):
    """Training FLOPs/token/component beyond the harness's 3*forward estimate.

    A unit triangular solve's VJP contains another solve and a dense gradient
    product. Charge its extra C(C+1)*(K+V) operations per head/chunk explicitly.
    The LM caller multiplies this component count by the number of layers.
    Serial/unrolled delta and all other architectures return zero.
    """
    kind = _kind(cfg, kind)
    chunk_size = int(_get(cfg, "delta_chunk", 0))
    if kind != "gated_delta" or not chunk_size:
        return 0.0
    dk, dv, _, _ = _delta_dims(cfg)
    nh = int(_get(cfg, "nh", 4))
    t = int(seq_len or cfg.ctx)
    count = _delta_chunk_flops(t, nh, dk, dv, chunk_size)
    return float(cfg.heads * count["solve_vjp_extra_over_3x_forward_per_token_per_head"])
