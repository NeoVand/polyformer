"""Linear read-outs of the column value inside the union adapter, per layer (on atlas_states.npy from inside_atlas.py).

For SUM rows the value is s = carry + top + bottom (0..19); for MUL rows s = a*b + c (0..89); for ADD/ADZ rows
s = c + p + r (0..19). Ridge probe, 5-fold cross-validated over table rows: exact-integer accuracy (rounded) and R^2.
Also the geometry of the class means of s (PCA of the means) at a few layers, to see the shape of the number line.
"""
import json
import sys

import numpy as np

S = np.load(sys.argv[1]).astype(np.float32)  # (N, 25, D)
A = json.load(open("atlas.json"))
rows = A["rows"]
B = "_"


def value(m):
    op, v = m["op"], m["v"]
    d = [None if ch == B else int(ch) for ch in v]
    if op == "SUM":
        return sum(x for x in d if x is not None) if not all(x is None for x in d) else None
    if op == "MUL":
        a, b, c = d
        return None if a is None else a * b + (c or 0)
    if op in ("ADD", "ADZ"):
        return sum(x for x in d if x is not None)
    return None


rng = np.random.default_rng(0)
out = {}
for fam in ["SUM", "MUL", "ADD"]:
    ops = ["ADD", "ADZ"] if fam == "ADD" else [fam]
    idx = [i for i, m in enumerate(rows) if m["op"] in ops and value(m) is not None]
    y = np.array([value(rows[i]) for i in idx], dtype=np.float32)
    perm = rng.permutation(len(idx))
    folds = np.array_split(perm, 5)
    res = []
    for l in range(S.shape[1]):
        X = S[idx, l]
        X = (X - X.mean(0)) / (X.std(0) + 1e-6)
        pred = np.zeros_like(y)
        for f in folds:
            tr = np.setdiff1d(perm, f)
            Xt = X[tr]
            lam = 10.0
            W = np.linalg.solve(Xt.T @ Xt + lam * np.eye(X.shape[1]), Xt.T @ (y[tr] - y[tr].mean()))
            pred[f] = X[f] @ W + y[tr].mean()
        acc = float((np.round(pred) == y).mean())
        r2 = float(1 - ((pred - y) ** 2).sum() / ((y - y.mean()) ** 2).sum())
        res.append((l, round(acc, 3), round(r2, 3)))
    out[fam] = res
    print(fam, len(idx), "rows; layer: exact-acc / R2")
    print("  " + "  ".join(f"{l}:{a:.2f}/{r:.2f}" for l, a, r in res))

# shape of the class means
for fam, ops in [("SUM", ["SUM"]), ("MUL", ["MUL"])]:
    idx = [i for i, m in enumerate(rows) if m["op"] in ops and value(m) is not None]
    y = np.array([value(rows[i]) for i in idx])
    for l in (8, 12, 16, 20):
        vals = sorted(set(y))
        M = np.stack([S[[idx[j] for j in range(len(idx)) if y[j] == v], l].mean(0) for v in vals])
        Mc = M - M.mean(0)
        U, s, Vt = np.linalg.svd(Mc, full_matrices=False)
        var = s**2 / (s**2).sum()
        P = Mc @ Vt[:3].T
        # is it a line (monotone PC1), a circle (angle advances), or a helix? report PC1 rank correlation and angle steps
        pc1 = P[:, 0]
        rc = np.corrcoef(np.argsort(np.argsort(pc1)), np.arange(len(vals)))[0, 1]
        ang = np.unwrap(np.arctan2(P[:, 2], P[:, 1]))
        print(fam, "layer", l, "means var", np.round(var[:4], 3), "PC1 rank corr with value", round(float(rc), 3),
              "PC2-3 angle total turn (rad)", round(float(ang[-1] - ang[0]), 2))
