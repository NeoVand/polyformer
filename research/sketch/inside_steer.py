"""Is the internal number line causal? Steering test on the union adapter (E5 v2 seed 1). $0 on the M4.

At the position that writes the answer, add mu_l[s'] - mu_l[s] to the residual entering layer l (mu = the mean state of
all table rows with column value s, from atlas_states.npy) and check whether the model now writes the answer for s'.
SUM rows: s = carry + top + bottom; answer = sum code (digit, or digit-with-carry letter). MUL rows: s = a*b + c;
first answer token = s % 10, second = s // 10 (both checked).
"""
import json
import sys

import numpy as np
import torch
from peft import PeftModel

import e2_column as e2
import e5_union as u

ADAPTER, STATES = sys.argv[1], sys.argv[2]
model = PeftModel.from_pretrained(e2.load_base(), ADAPTER).eval()
lm = model.base_model.model
layers = lm.model.language_model.layers
S = np.load(STATES).astype(np.float32)
A = json.load(open("atlas.json"))
meta = A["rows"]
B = "_"


def val(m):
    d = [None if ch == B else int(ch) for ch in m["v"]]
    if m["op"] == "SUM":
        return None if all(x is None for x in d) else sum(x for x in d if x is not None)
    if m["op"] == "MUL":
        return None if d[0] is None else d[0] * d[1] + (d[2] or 0)


def sum_code(s):
    return str(s) if s < 10 else "abcdefghij"[s - 10]


STEER = {}


def hook(mod, args, kwargs):
    if "vec" not in STEER:
        return None
    h = kwargs["hidden_states"] if "hidden_states" in kwargs else args[0]
    h = h.clone()
    h[:, STEER["pos"]] += STEER["vec"]
    if "hidden_states" in kwargs:
        kwargs["hidden_states"] = h
        return args, kwargs
    return (h,) + tuple(args[1:]), kwargs


rng = np.random.default_rng(0)
results = {}
BY = sys.argv[3] if len(sys.argv) > 3 else "value"
LAYERS = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [4, 8, 12, 14, 16, 18, 20, 22]
for fam in ["SUM", "MUL"]:
    idx = [i for i, m in enumerate(meta) if m["op"] == fam and val(m) is not None]
    # steer by the column value, or by the first answer token (the class the readout needs)
    vals = np.array([val(meta[i]) if BY == "value" else (val(meta[i]) if fam == "SUM" else val(meta[i]) % 10) for i in idx])
    uniq = sorted(set(vals.tolist()))
    pick = rng.choice(len(idx), size=min(80, len(idx)), replace=False)
    for l in LAYERS:
        mu = {v: S[[idx[j] for j in range(len(idx)) if vals[j] == v], l].mean(0) for v in uniq}
        h_ = layers[l].register_forward_pre_hook(hook, with_kwargs=True)
        ok = tot = 0
        for j in pick:
            i = idx[j]
            s = vals[j]
            t = int(rng.choice([v for v in uniq if v != s]))
            row = u.ROWS[i]
            inp, spans = u.batch([row])
            pos = spans[0][0][0]
            STEER["pos"] = pos
            STEER["vec"] = torch.tensor(mu[t] - mu[s], device=e2.dev, dtype=next(lm.parameters()).dtype)
            with torch.no_grad():
                if fam == "SUM":
                    lo = lm(**inp).logits[0, pos]
                    got = u.ID_CHAR.get(int(lo.argmax()), "?")
                    ok += got == sum_code(t)
                else:
                    # greedy two tokens with the steer applied only at the first answer position
                    lo = lm(**inp).logits[0, pos]
                    g1 = u.ID_CHAR.get(int(lo.argmax()), "?")
                    ok += g1 == str(t % 10)
            tot += 1
        STEER.pop("vec", None)
        h_.remove()
        results[f"{fam}@{l}"] = ok / tot
        print(fam, "layer", l, "steered to target:", ok, "/", tot, flush=True)
json.dump(results, open(f"steer_{BY}.json", "w"), indent=1)
