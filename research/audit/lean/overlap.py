import numpy as np, hashlib, json, sys
P = '/Users/neo/repos/polyformer/.claude/worktrees/lean-s-2b865a/research/results/lean_s1/data/a4x.npz'
z = np.load(P)
D = {}
for k in z.files:
    s, n = k.split('/', 1); D.setdefault(s, {})[n] = z[k]
for s, v in D.items():
    print(s, {k: (a.shape, str(a.dtype)) for k, a in v.items()}, 'lengths uniq', np.unique(v['lengths'])[:5])
tr = D['train']
h = lambda a: hashlib.sha1(np.ascontiguousarray(a).tobytes()).hexdigest()
N = tr['events'].shape[0]
assert (tr['lengths'] == 9).all()
train_chain = {h(tr['events'][i, :9]) for i in range(N)}
train_chain_tg = {h(tr['targets'][i, :9]) for i in range(N)}
print('train distinct chains', len(train_chain), 'of', N)
# partner chains in training (variable length)
pchains = set()
for i in range(N):
    for j in range(tr['p_events'].shape[1]):
        L = tr['p_lengths'][i, j]
        if L > 0: pchains.add(h(tr['p_events'][i, j, :L]))
train_start = {h(tr['events'][i, 0]) for i in range(N)}
train_states = {h(r) for r in tr['targets'][:, :9].reshape(-1, tr['targets'].shape[-1])}
print('train distinct start exprs', len(train_start), 'distinct states in train targets', len(train_states))
# window keys: (state tokens at k, events k+1..k+8)
def winkey(tg_k, ev_slice):
    return h(np.concatenate([tg_k.astype(np.int16).ravel(), ev_slice.astype(np.int16).ravel()]))
train_win = {winkey(tr['targets'][i, 0], tr['events'][i, 1:9]) for i in range(N)}
out = {}
for s in sorted([k for k in D if k.startswith('eval')], key=lambda k: int(k[4:])):
    e = int(s[4:]); d = D[s]; n = d['events'].shape[0]
    assert (d['lengths'] == e + 1).all()
    full8 = sum(h(d['events'][i, :9]) in train_chain for i in range(n))
    full8_in_partner = sum(h(d['events'][i, :9]) in pchains for i in range(n)) if e == 8 else None
    start_in = sum(h(d['events'][i, 0]) in train_start for i in range(n))
    end_in = sum(h(d['targets'][i, e]) in train_states for i in range(n))
    # all length-8 windows (stride 1) whose (start state, 8 events) equals a training chain
    tot = hit = 0
    for i in range(n):
        for k in range(0, e - 8 + 1):
            tot += 1
            hit += winkey(d['targets'][i, k], d['events'][i, k + 1:k + 9]) in train_win
    # full test chain identical to a training chain (only possible at e = 8)
    out[s] = dict(n=n, prefix9_eq_train_chain=full8, eval8_chain_eq_train_partner=full8_in_partner, start_expr_seen_in_train=start_in,
                  end_state_seen_in_train_targets=end_in, windows8=tot, windows8_seen=hit, frac=round(hit / tot, 6))
    print(s, out[s], flush=True)
# eval-vs-eval duplicates and eval partners vs train
json.dump(out, open('overlap_a4x.json', 'w'), indent=1)
