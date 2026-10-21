"""EVENTS (EVENTS.md section 2): a model whose unit of memory is the event, not the token.

    tokens --[encoder: Gated DeltaNet blocks]--> h_t
    router: p_t = (1 - cos(W_q h_t, W_k h_{t-1})) / 2, p_0 = 1; boundary b_t = [p_t >= 1/2]
            (H-Net's dynamic chunking; a decision that uses tokens up to t only)
    downsample: the encoder state at each boundary token fills the next of K slots (K fixed, so shapes
            are static; boundaries past slot K merge into the last event, a decision about the past)
    main network over slots: attention in carried frames with the forget gate (loops_layers), MLPs
    dechunk: smoothing over events, y_e <- P_e y_e + (1 - P_e) y_{e-1}; token t reads the slot of the
            event it belongs to (whose boundary is at or before t), scaled by a straight-through
            confidence (forward value 1), added to h_t
    decoder: Gated DeltaNet blocks whose decay is cut at each boundary, then the tied output head

The training loss adds H-Net's ratio loss, N/(N-1) ((N-1) F G + (1-F)(1-G)), with F the boundary rate,
G the mean boundary probability and N the target event length, so the model is pulled toward one event
per N tokens. Every parameter of a block lives in one dict of p["layers"] (encoder blocks, then main
blocks, then decoder blocks) so lm's optimiser gives the matrices Muon updates, as for every arm.
"""

import argparse
import math

import jax
import jax.numpy as jnp

import beyond_layers
import loops_layers


def _get(cfg, name, default):
    value = getattr(cfg, name, default)
    return default if value is None else value


def _dense(key, i, o, scale=1.0):
    return {"w": jax.random.normal(key, (i, o)) * scale / math.sqrt(i), "b": jnp.zeros(o)}


def _ln_init(d):
    return {"g": jnp.ones(d), "b": jnp.zeros(d)}


def _ln(p, x):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / jnp.sqrt(var + 1e-5) * p["g"] + p["b"]


def _mm(cfg, a, b):
    return loops_layers._mm(cfg, a, b)


def _lin(cfg, p, x):
    return _mm(cfg, x, p["w"]) + p.get("b", 0.0)


def sizes(cfg):
    enc, main, dec = int(_get(cfg, "ev_enc", 2)), int(_get(cfg, "ev_main", 6)), int(_get(cfg, "ev_dec", 2))
    n = float(_get(cfg, "ev_len", 8))
    slots = int(_get(cfg, "ev_slots", 0)) or int(math.ceil(1.5 * cfg.ctx / n))
    return enc, main, dec, n, slots


def gdn_cfg(cfg):
    return argparse.Namespace(**{**vars(cfg), "arch": "gated_delta", "nh": 1, "beta_max": 1.0})


def main_cfg(cfg):
    """The event-level network's settings: its own width and heads, frames and gate over events."""
    _, _, _, _, slots = sizes(cfg)
    return argparse.Namespace(**{
        **vars(cfg), "arch": "loop", "d": int(_get(cfg, "ev_dmain", cfg.d)), "heads": int(_get(cfg, "ev_heads", cfg.heads)),
        "posenc": _get(cfg, "ev_posenc", "holo"), "forget": int(_get(cfg, "ev_forget", 1)), "ctx": slots,
        "vtrans": int(_get(cfg, "ev_vtrans", 0)), "vtrans_heads": int(_get(cfg, "ev_vtrans_heads", 0)),
        "gate_out": int(_get(cfg, "ev_gate_out", 0)), "vres": int(_get(cfg, "ev_vres", 0)),
    })


def init(key, cfg):
    d, v_, t = cfg.d, cfg.vocab, cfg.ctx
    enc, main, dec, _, _ = sizes(cfg)
    mc = main_cfg(cfg)
    dm = mc.d
    total = enc + main + dec
    ks = iter(jax.random.split(key, 16 + 16 * total))
    scale = 1 / math.sqrt(2 * total)
    p = {"emb": jax.random.normal(next(ks), (v_, d)) * 0.02, "pos": jnp.zeros((t, d)), "lnf": _ln_init(d),
         "layers": []}
    g = gdn_cfg(cfg)
    for i in range(enc + dec):
        lyr = {"ln1": _ln_init(d), "ln2": _ln_init(d),
               "fc1": _dense(next(ks), d, cfg.mlp), "fc2": _dense(next(ks), cfg.mlp, d, scale)}
        lyr.update(beyond_layers.init_layer(next(ks), g, kind="gated_delta"))
        if i >= enc:
            # how hard the decoder's state is cut at a boundary: decay exp(-softplus(cut) * p_t)
            lyr["cut"] = jnp.full((cfg.heads,), 2.0)
        p["layers"].append(lyr)
    # the router lives in the last encoder block; identity init as in H-Net (adjacent states compared)
    router = p["layers"][enc - 1]
    router["ln_r"] = _ln_init(d)
    router["rq"] = {"w": jnp.eye(d)}
    router["rk"] = {"w": jnp.eye(d)}
    main_layers = []
    for _ in range(main):
        lyr = {"ln1": _ln_init(dm), "ln2": _ln_init(dm),
               "qkv": _dense(next(ks), dm, 3 * dm), "o": _dense(next(ks), dm, dm, scale),
               "fc1": _dense(next(ks), dm, 4 * dm), "fc2": _dense(next(ks), 4 * dm, dm, scale)}
        if int(_get(cfg, "qkv_conv", 0)):
            lyr["qkv_conv"] = beyond_layers.init_qkv_conv(next(ks), dm, int(cfg.qkv_conv))
        lyr.update(loops_layers.init_extra(next(ks), mc))
        main_layers.append(lyr)
    main_layers[0]["ev_in"] = _dense(next(ks), d, dm)
    main_layers[-1]["ev_lnout"] = _ln_init(dm)
    main_layers[-1]["ev_out"] = _dense(next(ks), dm, d, 0.1)
    p["layers"] = p["layers"][:enc] + main_layers + p["layers"][enc:]
    return p


def _gdn_block(cfg, lyr, x, boundary=None):
    g = gdn_cfg(cfg)
    extra = None
    if boundary is not None:
        extra = -jax.nn.softplus(lyr["cut"])[None, None, :] * boundary[..., None]
    x = x + beyond_layers.apply_layer(g, lyr, _ln(lyr["ln1"], x), kind="gated_delta", extra_log_decay=extra)
    return x + _lin(cfg, lyr["fc2"], jax.nn.gelu(_lin(cfg, lyr["fc1"], _ln(lyr["ln2"], x))))


def _main_block(cfg, mc, lyr, x, vfirst=None):
    def qkv(p_, x_):
        packed = _lin(mc, p_["qkv"], x_)
        if "qkv_conv" in p_:
            packed = beyond_layers.causal_depthwise_conv(packed, p_["qkv_conv"])
        return jnp.split(packed, 3, -1)
    update, values = loops_layers.attention(mc, lyr, _ln(lyr["ln1"], x), qkv, vfirst, return_values=True)
    x = x + update
    x = x + _lin(mc, lyr["fc2"], jax.nn.gelu(_lin(mc, lyr["fc1"], _ln(lyr["ln2"], x))))
    return x, (values if vfirst is None else vfirst)


def _unit(x):
    return x / jnp.sqrt(jnp.maximum(jnp.sum(x * x, -1, keepdims=True), 1e-12))


def route(cfg, router, h):
    """Boundary probability and decision per token; p_0 = 1 and b_0 = 1."""
    hn = _ln(router["ln_r"], h).astype(jnp.float32)
    q, k = hn @ router["rq"]["w"], hn @ router["rk"]["w"]
    cos = jnp.sum(_unit(q[:, 1:]) * _unit(k[:, :-1]), -1)
    prob = jnp.concatenate([jnp.ones_like(cos[:, :1]), 0.5 * (1.0 - cos)], 1)
    hard = (prob >= 0.5).at[:, 0].set(True)
    return prob, hard


def forward(cfg, p, idx, with_aux=False, with_boundaries=False):
    enc, main, dec, n_target, slots = sizes(cfg)
    mc = main_cfg(cfg)
    layers = p["layers"]
    remat = (lambda f: jax.checkpoint(f)) if _get(cfg, "remat", 0) else (lambda f: f)
    x = p["emb"][idx]
    b_, t, d = x.shape
    for i in range(enc):
        x = remat(lambda l, x_: _gdn_block(cfg, l, x_))(layers[i], x)
    h = x
    prob, hard = route(cfg, layers[enc - 1], h)
    count = jnp.cumsum(hard.astype(jnp.int32), 1)                 # boundaries up to t (>= 1)
    event = jnp.minimum(count - 1, slots - 1)                      # the event token t belongs to
    keep = hard & (count <= slots)                                 # boundaries that open a slot
    slot = jnp.where(keep, count - 1, slots)                       # slots = a discard row
    rows = jnp.arange(b_)[:, None]
    z = jnp.zeros((b_, slots + 1, d), h.dtype).at[rows, slot].set(h)[:, :slots]
    pz = jnp.zeros((b_, slots + 1), prob.dtype).at[rows, slot].set(prob)[:, :slots]
    m = _lin(mc, layers[enc]["ev_in"], z)
    vfirst = None
    for j in range(main):
        m, vfirst = remat(lambda l, m_, v_: _main_block(cfg, mc, l, m_, v_))(layers[enc + j], m, vfirst)
    last = layers[enc + main - 1]
    y = _lin(mc, last["ev_out"], _ln(last["ev_lnout"], m))        # [B, K, d]
    # smoothing over events: ybar_e = P_e y_e + (1 - P_e) ybar_{e-1}, a linear recurrence
    a_coef = (1.0 - pz)[..., None]
    b_coef = pz[..., None] * y

    def combine(left, right):
        return left[0] * right[0], right[0] * left[1] + right[1]

    _, ybar = jax.lax.associative_scan(combine, (a_coef, b_coef), axis=1)
    up = jnp.take_along_axis(ybar, event[..., None], axis=1)        # [B, T, d]
    conf = jnp.where(hard, prob, 1.0 - prob)
    ste = conf + jax.lax.stop_gradient(1.0 - conf)
    x = h + ste[..., None] * up
    cut = prob * hard.astype(prob.dtype)
    for i in range(dec):
        x = remat(lambda l, x_, c_: _gdn_block(cfg, l, x_, c_))(layers[enc + main + i], x, cut)
    x = _ln(p["lnf"], x)
    logits = _mm(cfg, x, p["emb"].T)
    if not with_aux:
        return logits
    rate = hard.astype(jnp.float32).mean()
    mean_prob = prob.mean()
    ratio = n_target / (n_target - 1) * ((n_target - 1) * rate * mean_prob + (1 - rate) * (1 - mean_prob))
    aux = {"ratio": ratio, "rate": rate, "prob": mean_prob,
           "overflow": (count[:, -1] > slots).astype(jnp.float32).mean()}
    if with_boundaries:
        aux.update(hard=hard, probs=prob)
    return logits, aux


def flops_per_token(cfg, t):
    """Forward FLOPs per token, the lm.py convention (multiply-add = 2, causal attention over slots)."""
    enc, main, dec, _, slots = sizes(cfg)
    mc = main_cfg(cfg)
    d, dm = cfg.d, mc.d
    g = gdn_cfg(cfg)
    token_block = beyond_layers.forward_flops(g, "gated_delta", t) + 4 * d * cfg.mlp
    router = 2 * 2 * d * d + 8 * d
    ta = (slots + 1) / 2
    attn = 2 * 4 * dm * dm + 2 * 2 * ta * dm + 5 * ta * mc.heads + 6 * int(_get(cfg, "qkv_conv", 0)) * dm
    attn += loops_layers.extra_flops(mc, slots)
    main_block = attn + 2 * 2 * dm * 4 * dm
    per_slot = main * main_block + 2 * d * dm + 2 * dm * d + 8 * d
    return (enc + dec) * token_block + router + per_slot * slots / t + 6 * d + 2 * d * cfg.vocab


def training_extra_flops(cfg, t):
    enc, _, dec, _, _ = sizes(cfg)
    return (enc + dec) * beyond_layers.training_extra_flops(gdn_cfg(cfg), "gated_delta", t)
