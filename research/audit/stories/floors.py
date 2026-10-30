import sys, json, gzip, random, collections, pathlib
sys.path.insert(0, sys.argv[1])
import story_world as W
R = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees/lean-n-data-34a2d2/research/results/stories")
tests = {L: [json.loads(l) for l in gzip.open(R / f"test{L}.jsonl.gz", "rt")] for L in (16, 64, 256, 1024)}
def make_train(rng, n):
    out = []
    for _ in range(n):
        a = W.make_story(rng, rng.randint(4, 16))
        s1, ev1 = W.story_to(rng, rng.randint(4, 16), tuple(a["states"][-1]))
        setup, sents = W.render_story(rng, s1, ev1)
        b = {"s0": list(s1), "events": [list(e) for e in ev1], "setup": setup, "sentences": sents, "states": [list(s) for s in W.run(s1, ev1)]}
        out.append((a, b))
    return out
T = [x for p in make_train(random.Random("train:10"), 5000) for x in p]
NO, NC = 6, 5
print(f"uniform chance, exact = (1/5)^6 = {(1/5)**6:.3g}; expected hits in 128 = {128*(1/5)**6:.4f}")
# constant majority state over all supervised training positions (state after every sentence from end of setup on)
allstates = collections.Counter(tuple(st) for s in T for st in s["states"])
mode, cnt = allstates.most_common(1)[0]
# per-object majority over training positions
perobj = [collections.Counter(st[o] for s in T for st in s["states"]).most_common(1)[0][0] for o in range(NO)]
# last-event-only predictors, trained on every training prefix (k >= 1): key = canonical last event (what a perfect parse of the last sentence gives)
by_ev = collections.defaultdict(collections.Counter); by_ev_obj = collections.defaultdict(lambda: [collections.Counter() for _ in range(NO)])
for s in T:
    for k, e in enumerate(s["events"], 1):
        key = W.canon_event(tuple(e)); st = tuple(s["states"][k])
        by_ev[key][st] += 1
        for o in range(NO): by_ev_obj[key][o][st[o]] += 1
def pred_last_full(s):
    key = W.canon_event(tuple(s["events"][-1]))
    return list(by_ev[key].most_common(1)[0][0]) if key in by_ev else list(mode)
def pred_last_obj(s):
    key = W.canon_event(tuple(s["events"][-1]))
    return [by_ev_obj[key][o].most_common(1)[0][0] for o in range(NO)] if key in by_ev_obj else perobj
def pred_s0(s): return list(s["s0"])
def pred_lastmove(s):   # shallow heuristic: setup, then only 'move' events (ignores swap and empty)
    st = list(s["s0"])
    for e in s["events"]:
        if e[0] == "move": st[e[1]] = e[2]
    return st
def pred_lastmove_swap(s):   # ignores only 'empty'
    st = list(s["s0"])
    for e in s["events"]:
        if e[0] == "move": st[e[1]] = e[2]
        elif e[0] == "swap": st[e[1]], st[e[2]] = st[e[2]], st[e[1]]
    return st
preds = {"constant mode state": lambda s: list(mode), "per-object majority": lambda s: perobj, "last event only (full-state mode)": pred_last_full,
         "last event only (per-object mode)": pred_last_obj, "setup copy (ignores events)": pred_s0, "setup + moves only (ignores swap/empty)": pred_lastmove,
         "setup + moves + swaps (ignores empty)": pred_lastmove_swap}
for nm, f in preds.items():
    row = []
    for L, G in tests.items():
        ex = sum(f(s) == s["states"][-1] for s in G); ob = sum(a == b for s in G for a, b in zip(f(s), s["states"][-1]))
        row.append(f"L{L}: exact {ex}/128 = {ex/128:.4f}, obj {ob/(6*128):.3f}")
    print(f"{nm:42s} " + " | ".join(row))
# event mix in tests
for L, G in tests.items():
    c = collections.Counter(e[0] for s in G for e in s["events"]); n = sum(c.values())
    print(f"L{L} event mix: " + ", ".join(f"{k} {v/n:.3f}" for k, v in c.items()) + f"; distinct end states {len({tuple(s['states'][-1]) for s in G})}; mean distinct containers occupied at end {sum(len(set(s['states'][-1])) for s in G)/128:.2f}")
