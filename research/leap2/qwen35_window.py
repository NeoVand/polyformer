"""Qwen3.5-0.8B, untouched: can the DeltaNet state alone carry a number?

The six full-attention layers are given a sliding window of W tokens (a per-layer-type mask dict), so with N filler
tokens and 6*W < N no attention path reaches the digit. Then the number can reach the question only through the
recurrent (DeltaNet) states. Conditions at the question: windowed; windowed with every DeltaNet state zeroed; windowed
with the DeltaNet states swapped in from a run with a different number. Also per-layer swaps.
"""

import copy
import json
import random
import sys
import time

import torch
from transformers import AutoModelForImageTextToText, AutoTokenizer

PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"
dev = "mps"
W = int(sys.argv[1]) if len(sys.argv) > 1 else 32
T = int(sys.argv[2]) if len(sys.argv) > 2 else 20
tok = AutoTokenizer.from_pretrained(PATH)
model = AutoModelForImageTextToText.from_pretrained(PATH, dtype=torch.float32).to(dev).eval()
layers = model.model.language_model.layers
DN = [i for i, l in enumerate(layers) if hasattr(l, "linear_attn")]
FILLER = tok.encode(open("/Users/neo/repos/polyformer/research/PRIMER.md").read())
DIGITS = [tok.encode(f" {d}")[-1] for d in range(10)]


def window_mask(q_len, k_len):
    """Additive mask: query i (absolute position k_len - q_len + i) sees keys j with pos - W < j <= pos."""
    pos = torch.arange(k_len - q_len, k_len, device=dev)[:, None]
    j = torch.arange(k_len, device=dev)[None, :]
    ok = (j <= pos) & (j > pos - W)
    return torch.where(ok, 0.0, float("-inf"))[None, None]


@torch.no_grad()
def run(ids, cache=None):
    past = cache.get_seq_length() if cache is not None else 0
    masks = {"full_attention": window_mask(len(ids), past + len(ids)), "linear_attention": None}
    out = model(input_ids=torch.tensor([ids], device=dev), past_key_values=cache, use_cache=True, attention_mask=masks)
    return out


def parts(d, n_fill, off):
    head = tok.encode(f"Remember this: the secret number is {d}.\n\n")
    q = tok.encode("\n\nQuestion: what was the secret number? Answer: the secret number is")
    return head + FILLER[off : off + n_fill], q


def with_states(cache, src=None, only=None):
    c = copy.deepcopy(cache)
    for i in only if only is not None else DN:
        s = c.layers[i].recurrent_states[0]
        c.layers[i].recurrent_states[0] = torch.zeros_like(s) if src is None else src.layers[i].recurrent_states[0].clone()
    return c


def answer(cache, q):
    return int(run(q, cache).logits[0, -1, DIGITS].argmax())


rng = random.Random(1)
res = {"W": W, "T": T}
t0 = time.time()
for n_fill in (0, 64, 256, 1024):
    s = {"windowed": 0, "zeroed": 0, "swap_donor": 0, "swap_own": 0}
    per = {i: 0 for i in DN}
    for _ in range(T):
        a, b = rng.sample(range(10), 2)
        off = rng.randrange(0, 4000)
        ia, q = parts(a, n_fill, off)
        ib, _ = parts(b, n_fill, off)
        ca, cb = run(ia).past_key_values, run(ib).past_key_values
        s["windowed"] += answer(copy.deepcopy(cb), q) == b
        s["zeroed"] += answer(with_states(cb), q) == b
        x = answer(with_states(cb, ca), q)
        s["swap_donor"] += x == a
        s["swap_own"] += x == b
        if n_fill == 1024:
            for i in DN:
                per[i] += answer(with_states(cb, ca, [i]), q) == a
    res[n_fill] = {k: v / T for k, v in s.items()}
    print(n_fill, res[n_fill], f"({time.time() - t0:.0f}s)", flush=True)
res["per_layer_swap_donor_1024"] = {i: v / T for i, v in per.items()}
print("per-layer swap -> donor at 1024:", res["per_layer_swap_donor_1024"], flush=True)
json.dump(res, open(f"qwen35_window_W{W}.json", "w"), indent=1)
print(f"done in {time.time() - t0:.0f}s")
