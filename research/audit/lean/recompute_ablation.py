import json, pathlib
W = pathlib.Path('/Users/neo/repos/polyformer/.claude/worktrees/lean-s-2b865a/research')
d = json.load(open(W/'results/lean_s/ABLATION_lean_chains.json'))
audit = {}
for x in json.load(open(W/'results/lean_s/audit.json'))['rows']: audit[x['file']] = x['ok']
for x in json.load(open(W/'results/lean_h/audit.json'))['rows']: audit['lean_h/'+x['file']] = x['ok']
bad = 0
for row in d['records']:
    r = json.load(open(W.parent/row['source_record']))
    ex = lambda e: r['results'][str(e)]['fr_acc_last'] if str(e) in r['results'] else None
    longest = max(int(k) for k in r['results'])
    E = ex(longest); p = 1.0 if E == 0 else 1 - E ** (1 / longest)
    calc = dict(exact_train=ex(8), exact_64x=ex(1024), exact_256x=ex(4096), exact_32x_at_256=ex(256), p_longest=p, longest_length=longest,
                level=r['pairs']['8']['cos'], growth=r['pairs']['256']['cos'] - r['pairs']['8']['cos'])
    for k, v in calc.items():
        if row[k] != v:
            bad += 1; print('MISMATCH', row['arm'], row['seed'], k, row[k], v)
    path = row['source_record'].split('research/results/')[1]
    key = path if path.startswith('lean_h/') else path.split('/', 1)[1]
    print(row['arm'], row['seed'], 'longest', longest, 'audit', audit.get(key), 'n@1024', r['results']['1024']['n'], 'n@4096', r['results'].get('4096', {}).get('n'))
print('mismatches', bad)
