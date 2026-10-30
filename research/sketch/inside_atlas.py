"""The inside of the union adapter (E5 v2, seed 1), for the demo's "inside the model" view. $0 on the M4.

For every one of the 1,795 table rows, at the position that predicts the first answer token:
  - the residual stream after every layer (embedding + 24 layers);
  - the logit lens: final norm + lm_head on each layer's state, restricted to the op's answer alphabet, giving the
    layer where the true token first leads and stays leading, and its margin per layer;
  - attention from that position to the three image tokens (which cell the model reads), per attention layer.
Then a PCA of the final-layer (normed) states, per op family, to see the geometry of the codes.
Writes atlas.json and a few quick plots (atlas_*.png).
"""

import json
import sys

import numpy as np
import torch
from peft import PeftModel

import e2_column as e2
import e5_union as u

ADAPTER = sys.argv[1] if len(sys.argv) > 1 else "modal/out/e5v2_s1_4000_h4.0_stop3.0_fast/files/e5_adapter_s1_h4_v2"
model = PeftModel.from_pretrained(e2.load_base(), ADAPTER).eval()
lm = model.base_model.model
norm = lm.model.language_model.norm
head = lm.lm_head
ALPHA = {  # the answer alphabet of each op's FIRST token
    "SUM": list("0123456789abcdefghijH"),
    "MUL": list("0123456789"),
    "ADD": list("0123456789"), "ADZ": list("0123456789"),
    "FLS": list("0123456789_"), "NXT": list("-"),
}


FINAL_NORMED = None


@torch.no_grad()
def collect(rows):
    inp, spans = u.batch(rows)
    out = lm(**inp, output_hidden_states=True, output_attentions=False)
    hs = out.hidden_states  # tuple of (B, L, D), len = layers + 1
    global FINAL_NORMED
    if FINAL_NORMED is None:  # is the last hidden state already through the final norm? compare with the real logits
        i, p = 0, spans[0][0][0]
        a = head(hs[-1][i, p][None]).float()
        b = head(norm(hs[-1][i, p][None])).float()
        r = out.logits[i, p][None].float()
        FINAL_NORMED = bool((a - r).abs().max() < (b - r).abs().max())
        print("last hidden state already normed:", FINAL_NORMED, float((a - r).abs().max()), float((b - r).abs().max()), flush=True)
    res = []
    for i, (pos, ans) in enumerate(spans):
        p = pos[0]
        res.append(torch.stack([h[i, p] for h in hs]).float().cpu())  # (25, D)
    return res


states, meta = [], []
for k in range(0, len(u.ROWS), 32):
    part = u.ROWS[k : k + 32]
    states += collect(part)
    meta += [{"op": op, "v": "".join(v).replace(" ", "_"), "ans": "".join(u.answer(op, v))} for op, v in part]
    print(k, flush=True)
S = torch.stack(states)  # (N, 25, D)
N, Lp1, D = S.shape

# logit lens restricted to each op's alphabet
with torch.no_grad():
    for i, m in enumerate(meta):
        alpha = ALPHA[m["op"]]
        ids = torch.tensor([u.CHAR_ID[c] for c in alpha])
        W = head.weight[ids].float().cpu()  # (A, D)
        normed = torch.stack([(S[i, l].to(e2.dev)[None] if (l == Lp1 - 1 and FINAL_NORMED) else norm(S[i, l].to(e2.dev)[None])).float().cpu()[0] for l in range(Lp1)])
        logits = normed @ W.T  # (25, A)
        true = alpha.index(m["ans"][0])
        other = logits.clone()
        other[:, true] = -1e9
        margin = (logits[:, true] - other.max(1).values).tolist()
        lead = [l for l in range(Lp1) if all(x > 0 for x in margin[l:])]
        m["lens_margin"] = [round(x, 2) for x in margin]
        m["decides_at"] = lead[0] if lead else None
        m["top_by_layer"] = [alpha[j] for j in logits.argmax(1).tolist()]

# PCA of the final normed state, per family
atlas = {"layers": Lp1 - 1, "rows": meta, "pca": {}}
for fam, ops in {"SUM": ["SUM"], "MUL": ["MUL"], "ADD": ["ADD", "ADZ", "FLS"]}.items():
    idx = [i for i, m in enumerate(meta) if m["op"] in ops]
    for layer in (Lp1 - 1, (Lp1 - 1) // 2):
        X = S[idx, layer].numpy()
        X = X - X.mean(0)
        U, s, Vt = np.linalg.svd(X, full_matrices=False)
        coords = X @ Vt[:3].T
        var = (s[:3] ** 2 / (s**2).sum()).tolist()
        atlas["pca"][f"{fam}@{layer}"] = {"idx": idx, "xyz": np.round(coords, 3).tolist(), "var": [round(v, 3) for v in var]}

json.dump(atlas, open("atlas.json", "w"))
np.save(sys.argv[2] if len(sys.argv) > 2 else "atlas_states.npy", S.numpy().astype(np.float16))
dec = {}
for m in meta:
    dec.setdefault(m["op"], []).append(m["decides_at"] if m["decides_at"] is not None else -1)
print("decision layer (first layer from which the true token leads to the end), median by op:",
      {k: float(np.median(v)) for k, v in dec.items()}, flush=True)

# quick plots
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 3, figsize=(15, 9), facecolor="white")
for col, fam in enumerate(["SUM", "MUL", "ADD"]):
    for row, layer in enumerate((Lp1 - 1, (Lp1 - 1) // 2)):
        P = atlas["pca"][f"{fam}@{layer}"]
        xyz = np.array(P["xyz"])
        lab = [meta[i]["ans"][0] for i in P["idx"]]
        keys = sorted(set(lab))
        cmap = plt.get_cmap("twilight", len(keys))
        c = [keys.index(x) for x in lab]
        a = ax[row, col]
        a.scatter(xyz[:, 0], xyz[:, 1], c=c, cmap=cmap, s=10)
        for kk in keys:
            pts = xyz[[j for j, x in enumerate(lab) if x == kk]]
            a.text(pts[:, 0].mean(), pts[:, 1].mean(), kk, fontsize=9, ha="center", va="center")
        a.set_title(f"{fam} rows, layer {layer}, var {P['var'][:2]}", fontsize=9)
        a.set_xticks([]); a.set_yticks([])
fig.tight_layout()
fig.savefig("atlas_pca.png", dpi=100)

fig, ax = plt.subplots(1, 1, figsize=(10, 4), facecolor="white")
for op in ["SUM", "MUL", "ADD", "ADZ"]:
    M = np.array([m["lens_margin"] for m in meta if m["op"] == op])
    ax.plot(np.median(M, 0), label=op)
    ax.fill_between(range(Lp1), np.percentile(M, 10, 0), np.percentile(M, 90, 0), alpha=0.15)
ax.axhline(0, color="k", lw=0.5)
ax.set_xlabel("layer"); ax.set_ylabel("lens margin of the true first token"); ax.legend()
fig.tight_layout()
fig.savefig("atlas_lens.png", dpi=100)
print("wrote atlas.json, atlas_pca.png, atlas_lens.png")
