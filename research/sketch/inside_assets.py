"""The data the sketchpad page needs to draw the inside of the model (from inside_atlas.py's states; $0).

For each map family (SUM: the adder; MUL; ADD: the multiplier's ADD and ADZ) the page projects a tick's state at every
layer onto three directions: each layer's state goes through the final RMSNorm (the logit lens's view; layer 24 already
has), the table's mean at that layer is subtracted, and the result is projected on an orthonormal basis of the 3D
subspace that best separates the layer-24 answer classes (class = the first answer token): Fisher discriminant
directions with the within-class covariance shrunk 90% toward the identity (SHRINK), then orthonormalised, so the map
is an undistorted 3D slice of the 1,024-dim state. In that slice the nearest class mean is the true answer for 97% of
the adder's views and all of the multiplier's. The table's own rows at layer 24 are the map's background.
For the push, the class means of the raw residual entering layer 20 (where patch_onnx_inside.py adds `steer`), by first
answer token: the adder's (SUM) and the multiplier's multiply step (MUL, rows with a digit of a; inside_steer.py pushes
these 80/80 at layer 20).

  python inside_assets.py <atlas_states.npy> <lens.bin> <out dir>
Writes <out dir>/inside.json (layout, cloud, labels) and <out dir>/inside.bin (float32 arrays).
"""

import json
import sys

import numpy as np

S = np.load(sys.argv[1]).astype(np.float32)  # (N, 25, D) at the position that writes the first answer token
w = np.fromfile(sys.argv[2], dtype=np.float32)[:1024]
out_dir = sys.argv[3]
rows = json.load(open("atlas.json"))["rows"]
EPS = 1e-6
STEER_LAYER = 20
SHRINK = 0.9
K = 3


def lens_norm(x):
    return x / np.sqrt((x**2).mean(-1, keepdims=True) + EPS) * w


Nrm = np.concatenate([lens_norm(S[:, :24]), S[:, 24:]], 1)
blob, layout = [], {}
off = 0


def put(name, a):
    global off
    a = np.ascontiguousarray(a, dtype=np.float32)
    blob.append(a.ravel())
    layout[name] = {"offset": off, "shape": list(a.shape)}
    off += a.size


fams = {"SUM": ["SUM"], "MUL": ["MUL"], "ADD": ["ADD", "ADZ"]}
info = {"steerLayer": STEER_LAYER, "families": {}}
for fam, ops in fams.items():
    idx = [i for i, m in enumerate(rows) if m["op"] in ops]
    lab = [rows[i]["ans"][0] for i in idx]
    keys = sorted(set(lab))
    centre = Nrm[idx].mean(0)  # (25, D)
    X = Nrm[idx, 24]
    M = np.stack([X[[j for j, k in enumerate(lab) if k == key]].mean(0) for key in keys])
    mu = M.mean(0)
    Xc = X - M[[keys.index(k) for k in lab]]
    Sw = Xc.T @ Xc / len(X)
    Sw = (1 - SHRINK) * Sw + SHRINK * np.trace(Sw) / Sw.shape[0] * np.eye(Sw.shape[0])
    Li = np.linalg.inv(np.linalg.cholesky(Sw))
    _, s, Vt = np.linalg.svd((M - mu) @ Li.T, full_matrices=False)
    V, _ = np.linalg.qr((Vt[:K] @ Li).T)
    V = V.T  # (K, D), orthonormal
    P = np.einsum("nld,kd->nlk", Nrm[idx] - centre[None], V)  # (n, 25, K)
    Pm = (M - centre[24]) @ V.T
    near = np.array(keys)[((P[:, 24, None] - Pm[None]) ** 2).sum(-1).argmin(1)]
    sep = float((near == np.array(lab)).mean())
    put(f"{fam}.basis", V)
    put(f"{fam}.centre", centre)
    labels = {k: [round(float(x), 3) for x in Pm[j]] for j, k in enumerate(keys)}
    info["families"][fam] = {
        "ops": ops,
        "cloud": [[round(float(x), 2) for x in P[j, 24]] for j in range(len(idx))],
        "cloudLabels": lab,
        "cloudViews": [rows[i]["op"] + " " + rows[i]["v"] for i in idx],
        "labels": labels,
        # the mean distance from the centre at each layer, for the page's scale and the depth axis
        "radius": [round(float(np.linalg.norm(P[:, l], axis=1).mean()), 3) for l in range(25)],
        # share of the views whose nearest class mean in this 3D slice is their own answer
        "separation": round(sep, 3),
    }
    print(fam, len(idx), "rows; nearest-mean in 3D", sep, "; radius by layer", info["families"][fam]["radius"][::4])

# push: class means of the raw residual entering STEER_LAYER, by first answer token; the multiply step's rows with a
# blank `a` (the carry flush) are left out, as in inside_steer.py
pushable = {
    "SUM": ("0123456789abcdefghijH", lambda m: m["op"] == "SUM"),
    "MUL": ("0123456789", lambda m: m["op"] == "MUL" and m["v"][0] != "_"),
}
info["steerCodes"] = {}
for fam, (codes, keep) in pushable.items():
    idx = [i for i, m in enumerate(rows) if keep(m)]
    means = np.stack([S[[i for i in idx if rows[i]["ans"][0] == c], STEER_LAYER].mean(0) for c in codes])
    put(f"{fam}.steer", means)
    info["steerCodes"][fam] = codes
info["layout"] = layout
np.concatenate(blob).astype(np.float32).tofile(f"{out_dir}/inside.bin")
json.dump(info, open(f"{out_dir}/inside.json", "w"))
print("wrote", f"{out_dir}/inside.bin", off * 4, "bytes and inside.json")
