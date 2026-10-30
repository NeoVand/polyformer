"""Qwen3.5-0.8B memory probe ($0, local MPS, untouched weights).

A. Decay spectrum: per DeltaNet layer and head, the per-token keep factor alpha = exp(g) on ordinary text, and the
   implied half-life in tokens. Registers need alpha -> 1.
B. Does the untouched model keep a number across filler? "The secret number is d", N filler tokens, then the question.
C. Where does it live? At the question, (i) zero every DeltaNet state, or (ii) swap the DeltaNet states from a run with
   a different number (attention caches untouched); also per layer. If the swapped run answers with the donor's
   number, the number is carried by the recurrent state, not by attention looking back at the digit.
D. Pictures: dump the most causal heads' 128x128 states while "x = 3 ... x = 7 ..." is written, for the film strip.
"""

import copy
import json
import math
import random
import sys
import time

import torch
import torch.nn.functional as F
from transformers import AutoModelForImageTextToText, AutoTokenizer

PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"
dev = "mps"
tok = AutoTokenizer.from_pretrained(PATH)
model = AutoModelForImageTextToText.from_pretrained(PATH, dtype=torch.float32).to(dev).eval()
text_layers = model.model.language_model.layers
DN = [i for i, l in enumerate(text_layers) if hasattr(l, "linear_attn")]
print("deltanet layers", DN, flush=True)
FILLER = open("/Users/neo/repos/polyformer/research/PRIMER.md").read()
res = {"deltanet_layers": DN}

# ---- A. decay spectrum ---------------------------------------------------------------------------------------------
gs = {}


def grab(i):
    def hook(mod, inp, out):
        la = text_layers[i].linear_attn
        gs[i] = (-la.A_log.float().exp() * F.softplus(out.float() + la.dt_bias)).detach()

    return hook


hooks = [text_layers[i].linear_attn.in_proj_a.register_forward_hook(grab(i)) for i in DN]
with torch.no_grad():
    model(input_ids=torch.tensor([tok.encode(FILLER)[:1024]], device=dev))
for h in hooks:
    h.remove()
spec = {}
for i in DN:
    g = gs[i][0]  # tokens x heads
    mean_g = g.mean(0)
    spec[i] = {
        "half_life_tokens": [float(math.log(0.5) / m) if m < 0 else float("inf") for m in mean_g.tolist()],
        "alpha_max": g.exp().max(0).values.tolist(),
        "frac_alpha_eq_1_fp32": (g.exp() == 1.0).float().mean(0).tolist(),
    }
res["decay"] = spec
hl = sorted(((h, i, j) for i in DN for j, h in enumerate(spec[i]["half_life_tokens"])), reverse=True)
print("longest half-lives (tokens, layer, head):", [(round(h, 1), i, j) for h, i, j in hl[:12]], flush=True)
print("median half-life:", sorted(h for h, _, _ in hl)[len(hl) // 2], flush=True)


# ---- B/C. secret number across filler ------------------------------------------------------------------------------
def prompt_parts(d, n_fill, off):
    ids = tok.encode(FILLER)
    head = tok.encode(f"Remember this: the secret number is {d}.\n\n")
    fill = ids[off : off + n_fill]
    q = tok.encode("\n\nQuestion: what was the secret number? Answer: the secret number is")
    return head + fill, q


DIGITS = [tok.encode(f" {d}")[-1] for d in range(10)]
assert len(set(DIGITS)) == 10, [tok.decode([t]) for t in DIGITS]


@torch.no_grad()
def ctx(ids):
    out = model(input_ids=torch.tensor([ids], device=dev), use_cache=True)
    return out.past_key_values


@torch.no_grad()
def ask(cache, q):
    out = model(input_ids=torch.tensor([q], device=dev), past_key_values=cache, use_cache=True)
    return out.logits[0, -1, DIGITS].float().log_softmax(-1)


def swap(cache_to, cache_from, layers):
    c = copy.deepcopy(cache_to)
    for i in layers:
        c.layers[i].recurrent_states[0] = cache_from.layers[i].recurrent_states[0].clone()
    return c


def zero(cache, layers):
    c = copy.deepcopy(cache)
    for i in layers:
        c.layers[i].recurrent_states[0] = torch.zeros_like(c.layers[i].recurrent_states[0])
    return c


rng = random.Random(0)
T = int(sys.argv[1]) if len(sys.argv) > 1 else 20
res["recall"] = {}
t0 = time.time()
for n_fill in (0, 64, 256, 1024):
    stats = {"plain": 0, "zeroed": 0, "swap_all_donor": 0, "swap_all_own": 0}
    per_layer = {i: 0 for i in DN}
    for _ in range(T):
        a, b = rng.sample(range(10), 2)
        off = rng.randrange(0, 4000)
        ca_ids, q = prompt_parts(a, n_fill, off)
        cb_ids, _ = prompt_parts(b, n_fill, off)
        cache_a, cache_b = ctx(ca_ids), ctx(cb_ids)
        stats["plain"] += int(ask(copy.deepcopy(cache_b), q).argmax() == b)
        stats["zeroed"] += int(ask(zero(cache_b, DN), q).argmax() == b)
        lp = ask(swap(cache_b, cache_a, DN), q)
        stats["swap_all_donor"] += int(lp.argmax() == a)
        stats["swap_all_own"] += int(lp.argmax() == b)
        if n_fill == 256:
            for i in DN:
                per_layer[i] += int(ask(swap(cache_b, cache_a, [i]), q).argmax() == a)
    res["recall"][n_fill] = {k: v / T for k, v in stats.items()}
    if n_fill == 256:
        res["recall"]["per_layer_donor_256"] = {i: v / T for i, v in per_layer.items()}
    print(n_fill, res["recall"][n_fill], f"({time.time() - t0:.0f}s)", flush=True)
if "per_layer_donor_256" in res["recall"]:
    print("per-layer swap -> donor answer at 256:", res["recall"]["per_layer_donor_256"], flush=True)

# ---- D. film strip: states of the longest-lived heads while a variable is rewritten --------------------------------
writes = [3, 7, 1, 9, 4]
ids = tok.encode("Let x be a counter. " + " ".join(f"Now x = {v}." for v in writes))
frames = {}
with torch.no_grad():
    cache = None
    for t in range(len(ids)):
        out = model(input_ids=torch.tensor([[ids[t]]], device=dev), past_key_values=cache, use_cache=True)
        cache = out.past_key_values
        for h, i, j in hl[:4]:
            frames.setdefault(f"L{i}H{j}", []).append(cache.layers[i].recurrent_states[0][0, j].cpu())
torch.save({"tokens": [tok.decode([t]) for t in ids], "frames": frames}, "qwen35_frames.pt")
json.dump(res, open("qwen35_probe.json", "w"), indent=1)
print(f"wrote qwen35_probe.json and qwen35_frames.pt in {time.time() - t0:.0f}s")
