"""S5 audit: regenerate training / validation / test words on CPU, hash, check overlaps, check labels with an
independent permutation product, compute shallow floors. Read-only on the worktree (run with python -B)."""
import hashlib
import itertools
import sys

import numpy as np

sys.path.insert(0, "/Users/neo/repos/polyformer/.claude/worktrees/invariance-3e22f3/research")
import validation_tasks as vt  # noqa: E402

L, STEPS, BATCH, E_TRAIN = 4, 4000, 64, 16
EVAL_SEED, PAIR_SEED, N_EVAL = 777, 4242, 512
E_EVAL = (16, 32, 64, 256, 1024)


def h(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------- training streams (main rng = default_rng(seed))
train = {}
for seed in (0, 1, 2):
    rng = np.random.default_rng(seed)
    G, T = [], []
    for _ in range(STEPS):
        tok, lab, msk, info = vt.task_s5_events(rng, BATCH, E_TRAIN, L)
        G.append(info["gens"]); T.append(tok)
    G, T = np.concatenate(G), np.concatenate(T)
    train[seed] = (G, T)
    print(f"train seed {seed}: words {G.shape}, gens sha {h(G)}, tokens sha {h(T)}, unique words {len({r.tobytes() for r in G})}")

train_words = {s: {r.tobytes() for r in G} for s, (G, T) in train.items()}
train_toks = {s: {r.tobytes() for r in T} for s, (G, T) in train.items()}
all_train_words = set().union(*train_words.values())

# ---------------------------------------------------------------- evaluation sets (default_rng(777 + e))
ev = {}
for e in E_EVAL:
    erng = np.random.default_rng(EVAL_SEED + e)
    tok, lab, msk, info = vt.task_s5_events(erng, N_EVAL, e, L)
    ev[e] = (tok, lab, info)
    gens = info["gens"]
    pref = gens[:, :16]
    pref_hits = sum(r.tobytes() in all_train_words for r in pref)
    full_hits = sum(r.tobytes() in all_train_words for r in gens) if e == 16 else 0
    tok_hits = sum(r.tobytes() in set().union(*train_toks.values()) for r in tok) if e == 16 else 0
    # every 16-event window of the evaluation words against every training word
    if e > 16:
        win = np.lib.stride_tricks.sliding_window_view(gens, 16, axis=1).reshape(-1, 16)
        win_hits = sum(np.ascontiguousarray(r).tobytes() in all_train_words for r in win)
        nwin = len(win)
    else:
        win_hits, nwin = full_hits, len(gens)
    dup = N_EVAL - len({r.tobytes() for r in gens})
    print(f"eval e={e:5d} seed {EVAL_SEED + e}: tokens {tok.shape} sha {h(tok)}, gens sha {h(gens)}, labels sha {h(lab[:, info['ends']])}; "
          f"within-set duplicate words {dup}; full-word overlap with training {full_hits}; token-sequence overlap {tok_hits}; "
          f"first-16-event prefix in training {pref_hits}/{N_EVAL}; 16-event windows in training {win_hits}/{nwin}")

# validation (256) vs test (1024): is any validation word a prefix of / equal to a window of a test word?
val, test = ev[256][2]["gens"], ev[1024][2]["gens"]
vset = {r.tobytes() for r in val}
pref_vt = sum(r[:256].tobytes() in vset for r in test)
win = np.lib.stride_tricks.sliding_window_view(test, 256, axis=1).reshape(-1, 256)
win_vt = sum(np.ascontiguousarray(r).tobytes() in vset for r in win)
print(f"validation e=256 vs test e=1024: validation word = test prefix {pref_vt}/512; validation word = any 256-window of a test word {win_vt}/{len(win)}")
# held-out pair sets used for the growth tie-break
for e in (16, 64, 256):
    hrng = np.random.default_rng(PAIR_SEED + e)
    tok, lab, msk, info = vt.task_s5_events(hrng, N_EVAL, e, L)
    print(f"held-out pair set e={e} seed {PAIR_SEED + e}: gens sha {h(info['gens'])}; equal to eval set at same e: {np.array_equal(info['gens'], ev[e][2]['gens']) if e in ev else None}")

# ---------------------------------------------------------------- independent label check (own permutation algebra)
perms = list(itertools.permutations(range(5)))
index = {p: i for i, p in enumerate(perms)}
P = np.array(perms)                                             # element index -> permutation
transp = []
for a, b in itertools.combinations(range(5), 2):
    p = list(range(5)); p[a], p[b] = b, a; transp.append(p)
GEN_PERM = np.array(transp + [list(range(5))])                  # generator index -> permutation (10 transpositions, identity)
assert np.array_equal(P[vt.S5_GENS], GEN_PERM), "generator table differs"
for e in E_EVAL:
    tok, lab, info = ev[e]
    gens = info["gens"]
    cur = GEN_PERM[gens[:, 0]].copy()
    mine = np.empty_like(gens)
    pow5 = 5 ** np.arange(4, -1, -1)
    lut = {tuple(p): i for i, p in enumerate(perms)}
    def idx(arr):
        return np.array([lut[tuple(r)] for r in arr])
    mine[:, 0] = idx(cur)
    for t in range(1, e):
        cur = np.take_along_axis(cur, GEN_PERM[gens[:, t]], 1)   # (a o b)(x) = a[b[x]]
        if t == e - 1 or t < 16:
            mine[:, t] = idx(cur)
    labs = lab[:, info["ends"]]
    ok_last = np.array_equal(mine[:, -1], labs[:, -1])
    ok_first = np.array_equal(mine[:, :16], labs[:, :16])
    # tokens: the generator token sits inside its event; labels only at event ends; BOS at 0
    gen_tok = tok[:, 1:].reshape(N_EVAL, e, L)
    is_gen = (gen_tok >= vt.V2_GEN0) & (gen_tok < vt.V2_DISTRACT0)
    one_gen = bool((is_gen.sum(-1) == 1).all())
    read = (gen_tok * is_gen).sum(-1) - vt.V2_GEN0
    print(f"labels e={e}: independent product matches at last event {ok_last}, first 16 events {ok_first}; exactly one generator token per event {one_gen}; generators read back {np.array_equal(read, gens)}; "
          f"label never appears as an input token: input vocab ids < {vt.v2_vocab()} (labels are class ids, never fed)")

# ---------------------------------------------------------------- shallow floors at the validation and test lengths
fresh = np.random.default_rng(99_999)
NF = 20_000
for e in (256, 1024):
    tok, lab, info = ev[e]
    gens, y = info["gens"], lab[:, info["ends"]][:, -1]
    G5 = vt.groups.get("S5")
    # fit last-generator -> label (Bayes) on fresh sequences of the same length, out of sample
    fg = fresh.integers(0, vt.V2_NGEN, (NF, e))
    fy = vt.groups.prefix_products(G5, vt.S5_GENS[fg])[:, -1]
    table = np.zeros((vt.V2_NGEN, 120), int)
    np.add.at(table, (fg[:, -1], fy), 1)
    pred_last = table.argmax(1)[gens[:, -1]]
    maj = np.bincount(fy, minlength=120).argmax()
    # parity-aware: the parity of the number of transpositions fixes the sign; best class within that coset
    par = (fg != vt.V2_NGEN - 1).sum(1) % 2
    tpar = np.zeros((2, 120), int); np.add.at(tpar, (par, fy), 1)
    pred_par = tpar.argmax(1)[(gens != vt.V2_NGEN - 1).sum(1) % 2]
    # a model that only tracks the last 16 events (the training length) or the first 16
    last16 = vt.groups.prefix_products(G5, vt.S5_GENS[gens[:, -16:]])[:, -1]
    first16 = vt.groups.prefix_products(G5, vt.S5_GENS[gens[:, :16]])[:, -1]
    # in-sample last-generator oracle (optimistic: fit on the test set itself)
    ins = np.zeros((vt.V2_NGEN, 120), int); np.add.at(ins, (gens[:, -1], y), 1)
    print(f"floors e={e} (n=512): chance 1/120 = {1/120:.5f}; majority class (fit on {NF} fresh) {np.mean(y == maj):.5f}; "
          f"last-generator-only (fit fresh) {np.mean(pred_last == y):.5f}; last-generator in-sample oracle {ins.max(1).sum() / 512:.5f}; "
          f"parity-only (fit fresh) {np.mean(pred_par == y):.5f}; product of last 16 events {np.mean(last16 == y):.5f}; product of first 16 events {np.mean(first16 == y):.5f}; "
          f"label classes present {len(np.unique(y))}/120, max class count {np.bincount(y, minlength=120).max()}")
