"""
Oracle test of the characters law (FORMALISM.md, section 4). Exact character features for Match-k on
Z_3^4,

    f_a(i) = Re( chi_a(x_i) * e_{k-1}( chi_a(x_t) : t != i ) ),   a = 1..40 conjugate pairs,

reproduce every label (with the constant term). Keep a random F of the 40, fit the best read-out on
54k cards, and score balanced accuracy on 27k held-out cards:

    python research/charlaw.py zs4 zs3

Read-outs: the best threshold on the equal-weight sum, balanced logistic regression, and a one-hidden-
layer MLP. If they track 1/2 + F/80, the law is a property of pooled character sums, not of training.
"""

import math
import pathlib
import sys

import jax
import jax.numpy as jnp
import numpy as np
import optax

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import polybench as pb  # noqa: E402

# one representative per conjugate pair {c, -c} of non-zero characters of Z_3^4
REPS = []
for v in range(1, 81):
    c = tuple((v // 3**a) % 3 for a in range(4))
    if tuple((-np.array(c)) % 3) not in REPS:
        REPS.append(c)
REPS = np.array(REPS)
assert len(REPS) == 40


def features(task, B, seed):
    n, k = {"zs3": (12, 3), "zs4": (9, 4), "zs5": (9, 5)}[task]
    tok, tgt, _ = pb.task_matchk(np.random.default_rng(seed), B, n, k, 4)
    x, y = tok[:, 1:], tgt[:, 1:]
    chi = np.exp(2j * np.pi / 3 * ((x @ REPS.T) % 3))  # [B, n, 40]
    m = k - 1
    loo = [(chi**j).sum(1, keepdims=True) - chi**j for j in range(1, m + 1)]  # leave-one-out power sums
    e = [np.ones_like(chi)]
    for mm in range(1, m + 1):
        e.append(sum((-1) ** (j - 1) * e[mm - j] * loo[j - 1] for j in range(1, mm + 1)) / mm)
    f = (chi * e[m]).real
    count = (math.comb(n - 1, k - 1) + 2 * f.sum(-1)) / 81
    assert np.array_equal(count > 0.5, y.astype(bool)), "the 40 characters must reproduce every label"
    return f.reshape(-1, 40), y.reshape(-1)


def balanced(pred, y):
    return 0.5 * ((pred[y == 1] == 1).mean() + (pred[y == 0] == 0).mean())


def threshold_ba(s, y):
    return max(balanced((s > t).astype(int), y) for t in np.quantile(s, np.linspace(0.01, 0.99, 197)))


def fit_ba(Xtr, ytr, Xte, yte, hidden=0, steps=1500, seed=0):
    """Balanced logistic regression (hidden=0) or a one-hidden-layer MLP, trained with Adam."""
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    Xtr, Xte = (Xtr - mu) / sd, (Xte - mu) / sd
    k1, k2 = jax.random.split(jax.random.PRNGKey(seed))
    d = Xtr.shape[1]
    if hidden:
        p = {"w1": jax.random.normal(k1, (d, hidden)) / math.sqrt(d), "b1": jnp.zeros(hidden),
             "w2": jax.random.normal(k2, (hidden, 1)) / math.sqrt(hidden), "b2": jnp.zeros(1)}
        f = lambda p, X: (jax.nn.gelu(X @ p["w1"] + p["b1"]) @ p["w2"] + p["b2"])[:, 0]
    else:
        p = {"w": jnp.zeros(d), "b": jnp.zeros(())}
        f = lambda p, X: X @ p["w"] + p["b"]
    pos = ytr.mean()
    wts = np.where(ytr == 1, 0.5 / pos, 0.5 / (1 - pos))
    loss = lambda p, X, y, w: (optax.sigmoid_binary_cross_entropy(f(p, X), y) * w).mean()
    opt = optax.adam(3e-3 if hidden else 1e-2)
    st = opt.init(p)

    @jax.jit
    def step(p, st, X, y, w):
        g = jax.grad(loss)(p, X, y, w)
        u, st = opt.update(g, st)
        return optax.apply_updates(p, u), st

    rng = np.random.default_rng(seed)
    for _ in range(steps if not hidden else 3000):
        i = rng.integers(0, len(Xtr), 4096) if hidden else slice(None)
        p, st = step(p, st, Xtr[i], ytr[i].astype(np.float32), wts[i])
    return balanced((np.asarray(f(p, Xte)) > 0).astype(int), yte)


def main():
    rng = np.random.default_rng(0)
    for task in sys.argv[1:] or ["zs4"]:
        Xtr, ytr = features(task, 6000, 1)
        Xte, yte = features(task, 3000, 2)
        print(f"{task}: positives {ytr.mean():.3f}")
        print("   F  1/2+F/80  sum    logistic  mlp")
        for F in (4, 8, 12, 16, 20, 24, 28, 32, 36, 40):
            rows = []
            for _ in range(2 if F < 40 else 1):
                C = rng.choice(40, F, replace=False)
                rows.append((threshold_ba(Xte[:, C].sum(1), yte), fit_ba(Xtr[:, C], ytr, Xte[:, C], yte),
                             fit_ba(Xtr[:, C], ytr, Xte[:, C], yte, hidden=256)))
            r = np.mean(rows, 0)
            print(f"  {F:2d}  {0.5 + F / 80:.3f}     {r[0]:.3f}  {r[1]:.3f}     {r[2]:.3f}", flush=True)


if __name__ == "__main__":
    main()
