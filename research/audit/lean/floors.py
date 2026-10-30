"""CPU floors for the Lean tier-1 chains (a4x): shallow predictors that ignore the rewrite history."""
import sys, json, collections
sys.dont_write_bytecode = True
sys.path.insert(0, '.')
import numpy as np
import lc_copy as lc

P = '/Users/neo/repos/polyformer/.claude/worktrees/lean-s-2b865a/research/results/lean_s1/data/a4x.npz'
z = np.load(P); D = {}
for k in z.files:
    s, n = k.split('/', 1); D.setdefault(s, {})[n] = z[k]
W, L = 7, 8
trees = lc.all_trees('abcd'); T = len(trees)
rows, lookup = lc.tree_classes(4, W)
tid = {t: i for i, t in enumerate(trees)}
assert T == 960
# transition structure: for each tree, uniform over applicable (rule, path)
ev_ids = {}; ncand = np.zeros(T, int); K = np.zeros((T, T))
ev_src = collections.defaultdict(list); ev_dst = collections.defaultdict(list)
for i, t in enumerate(trees):
    cands = lc.applicable(t, 1)
    ncand[i] = len(cands)
    for r, path in cands:
        s = lc.apply_step(t, r, path)
        key = tuple(lc.encode_step(s, L, 'path'))
        e = ev_ids.setdefault(key, len(ev_ids))
        j = tid[s.after]
        K[i, j] += 1.0 / len(cands)
        ev_src[e].append(i); ev_dst[e].append(j)
print('distinct step events', len(ev_ids), 'cands per tree min/mean/max', ncand.min(), ncand.mean(), ncand.max())
row_id = lambda r: lookup[tuple(int(x) for x in r)]
# verify data against the kernel (every training step is a legal step, end = apply)
tr = D['train']
bad = 0
for i in range(tr['events'].shape[0]):
    for k in range(1, 9):
        s, e, d = row_id(tr['targets'][i, k - 1]), ev_ids.get(tuple(int(x) for x in tr['events'][i, k])), row_id(tr['targets'][i, k])
        if e is None or s not in ev_src[e] or ev_dst[e][ev_src[e].index(s)] != d: bad += 1
print('training steps inconsistent with kernel:', bad)
# classes (connected components; rules invertible)
comp = -np.ones(T, int); c = 0
for i in range(T):
    if comp[i] >= 0: continue
    st = [i]; comp[i] = c
    while st:
        u = st.pop()
        for v in np.nonzero(K[u])[0]:
            if comp[v] < 0: comp[v] = c; st.append(v)
    c += 1
sizes = np.bincount(comp)
print('classes', c, 'class sizes (value: count of classes)', dict(collections.Counter(sizes.tolist())))
# start distribution from training starts
starts_tr = np.array([row_id(r) for r in tr['targets'][:, 0]])
mu0 = np.bincount(starts_tr, minlength=T) / len(starts_tr)
def mpow(M, e):
    R = np.eye(T); B = M.copy()
    while e:
        if e & 1: R = R @ B
        B = B @ B; e >>= 1
    return R
# empirical tables from training at step 8 (what a lazy learner could fit)
tab_ev = collections.defaultdict(collections.Counter); tab_sev = collections.defaultdict(collections.Counter); tab_s = collections.defaultdict(collections.Counter)
tab_ev_all = collections.defaultdict(collections.Counter)
for i in range(tr['events'].shape[0]):
    s0 = row_id(tr['targets'][i, 0]); e8 = tuple(int(x) for x in tr['events'][i, 8]); y = row_id(tr['targets'][i, 8])
    tab_ev[e8][y] += 1; tab_sev[(s0, e8)][y] += 1; tab_s[s0][y] += 1
    for k in range(1, 9):
        tab_ev_all[tuple(int(x) for x in tr['events'][i, k])][row_id(tr['targets'][i, k])] += 1
glob = collections.Counter(row_id(r) for r in tr['targets'][:, 8])
mode = lambda C: C.most_common(1)[0][0]
out = {'uniform_over_960': 1 / 960, 'classes': int(c), 'class_sizes': dict(collections.Counter(sizes.tolist()))}
for split in ['eval8', 'eval64', 'eval256', 'eval1024', 'eval4096']:
    e = int(split[4:]); d = D[split]; n = d['events'].shape[0]
    Ke1 = mpow(K, e - 1); Ke = Ke1 @ K
    s0 = np.array([row_id(r) for r in d['targets'][:, 0]]); y = np.array([row_id(r) for r in d['targets'][:, e]])
    evl = [ev_ids[tuple(int(x) for x in r)] for r in d['events'][:, e]]
    evl_key = [tuple(int(x) for x in r) for r in d['events'][:, e]]
    # Bayes-optimal predictors that ignore the history (exact, from the generator's kernel)
    p_start = Ke[s0]                                   # P(end | start)
    pred_start = p_start.argmax(1)
    bayes_start_exp = p_start.max(1).mean()
    pred_sev, exp_sev, pred_ev, exp_ev = [], [], [], []
    v0 = mu0 @ Ke1
    for i in range(n):
        ee = evl[i]; src = np.array(ev_src[ee]); dst = np.array(ev_dst[ee])
        for vec, P_, E_ in ((Ke1[s0[i]], pred_sev, exp_sev), (v0, pred_ev, exp_ev)):
            w = np.zeros(T); np.add.at(w, dst, vec[src] / ncand[src])
            P_.append(w.argmax()); E_.append(w.max() / w.sum())
    pred_sev, pred_ev = np.array(pred_sev), np.array(pred_ev)
    inclass = 1.0 / sizes[comp[s0]]
    # empirical training-table predictors
    emp_ev = np.array([mode(tab_ev[k]) if k in tab_ev else mode(glob) for k in evl_key])
    emp_sev = np.array([mode(tab_sev[(a, k)]) if (a, k) in tab_sev else (mode(tab_s[a]) if a in tab_s else mode(glob)) for a, k in zip(s0, evl_key)])
    emp_s = np.array([mode(tab_s[a]) for a in s0])
    emp_ev_all = np.array([mode(tab_ev_all[k]) for k in evl_key])
    r = {'n': int(n),
         'copy_start': float((s0 == y).mean()),
         'uniform_in_class_expected': float(inclass.mean()),
         'bayes_start_only_on_test': float((pred_start == y).mean()), 'bayes_start_only_expected': float(bayes_start_exp),
         'bayes_last_event_only_on_test': float((pred_ev == y).mean()), 'bayes_last_event_only_expected': float(np.mean(exp_ev)),
         'bayes_start_plus_last_event_on_test': float((pred_sev == y).mean()), 'bayes_start_plus_last_event_expected': float(np.mean(exp_sev)),
         'train_table_last_event_step8': float((emp_ev == y).mean()), 'train_table_last_event_any_step': float((emp_ev_all == y).mean()),
         'train_table_start_plus_last_event': float((emp_sev == y).mean()), 'train_table_start_only': float((emp_s == y).mean()),
         'global_mode': float((y == mode(glob)).mean())}
    out[split] = r
    print(split, json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()}), flush=True)
json.dump(out, open('floors_a4x.json', 'w'), indent=1)
