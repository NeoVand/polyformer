import sys, json, gzip, random, hashlib, collections, pathlib
sys.path.insert(0, sys.argv[1])
import story_world as W
R = pathlib.Path("/Users/neo/repos/polyformer/.claude/worktrees/lean-n-data-34a2d2/research/results/stories")

def make_train(rng, n):  # verbatim copy of stories_track.make_train
    out = []
    for _ in range(n):
        a = W.make_story(rng, rng.randint(4, 16))
        s1, ev1 = W.story_to(rng, rng.randint(4, 16), tuple(a["states"][-1]))
        setup, sents = W.render_story(rng, s1, ev1)
        b = {"s0": list(s1), "events": [list(e) for e in ev1], "setup": setup, "sentences": sents, "states": [list(s) for s in W.run(s1, ev1)]}
        assert b["states"][-1] == a["states"][-1]
        out.append((a, b))
    return out

def key_ev(s):  return (tuple(s["s0"]), tuple(tuple(e) for e in s["events"]))
def key_evonly(s): return tuple(tuple(e) for e in s["events"])
def key_txt(s): return tuple(s["setup"] + s["sentences"])
def h(x): return hashlib.sha1(repr(x).encode()).hexdigest()

# 1. tests as the tracker builds them vs the published files
tests = {}
for L in (16, 64, 256, 1024):
    rng = random.Random(f"0:test{L}")
    gen = [W.make_story(rng, L) for _ in range(128)]
    with gzip.open(R / f"test{L}.jsonl.gz", "rt") as f:
        fil = [json.loads(l) for l in f]
    same = len(gen) == len(fil) and all(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) for a, b in zip(gen, fil))
    print(f"test{L}: regenerated == file: {same}; n = {len(gen)}; unique (s0,events) = {len({key_ev(s) for s in gen})}; unique texts = {len({key_txt(s) for s in gen})}")
    tests[L] = gen

# 2. training sets
train = {}
for seed in (10, 11, 12):
    train[f"cert_s{seed}"] = [x for p in make_train(random.Random(f"train:{seed}"), 5000) for x in p]
train["published_train.jsonl"] = [json.loads(l) for l in gzip.open(R / "train.jsonl.gz", "rt")]
for nm, fn in (("soft", "run_soft/soft_partners.json"), ("cons", "run_cons/consensus_partners.json"), ("sclean", "run_cons/soft_clean_partners.json")):
    P = json.load(open(R / fn))["pairs"]
    train[nm] = [x for q in P for x in (q["a"], q["b"])]
# csmall = first 2088 pairs of the same rng stream (make_train is sequential); check explicitly
for seed in (10, 11, 12):
    cs = [x for p in make_train(random.Random(f"train:{seed}"), 2088) for x in p]
    assert [key_ev(s) for s in cs] == [key_ev(s) for s in train[f"cert_s{seed}"][:2 * 2088]]
print("csmall_s{10,11,12} == first 2088 pairs of cert stream: True")

# 3. overlaps
for nm, T in train.items():
    lens = collections.Counter(len(s["events"]) for s in T)
    ev = {key_ev(s) for s in T}; evo = {key_evonly(s) for s in T}; tx = {key_txt(s) for s in T}
    # prefixes of training stories (s0 + first k events) for k >= 1
    pref = set()
    for s in T:
        for k in range(1, len(s["events"]) + 1):
            pref.add((tuple(s["s0"]), tuple(tuple(e) for e in s["events"][:k])))
    trsent = collections.Counter(x for s in T for x in s["sentences"])
    out = []
    for L, G in tests.items():
        full = sum(key_ev(s) in ev for s in G)
        evonly = sum(key_evonly(s) in evo for s in G)
        txt = sum(key_txt(s) in tx for s in G)
        # does any test story contain a full training story as its own prefix (same s0 and first k events)?
        tpref = sum(any((tuple(s["s0"]), tuple(tuple(e) for e in s["events"][:k])) in {key_ev(t) for t in []} for k in ()) for s in G)
        pre16 = 0
        for s in G:
            if any((tuple(s["s0"]), tuple(tuple(e) for e in s["events"][:k])) in ev for k in range(1, 17)):
                pre16 += 1
        sent_seen = sum(x in trsent for s in G for x in s["sentences"]) / sum(len(s["sentences"]) for s in G)
        out.append(f"L{L}: full(s0,ev)={full} events-only={evonly} text={txt} test-prefix==train-story={pre16} test-sentences-seen-in-train={sent_seen:.3f}")
    print(f"[{nm}] stories={len(T)} max_events={max(lens)} min={min(lens)} | " + " | ".join(out))

# 4. near duplicates for test16 vs every 16-event training story (same s0 required): max positions agreeing
for nm in ("cert_s10", "cert_s11", "cert_s12", "soft"):
    T16 = [s for s in train[nm] if len(s["events"]) == 16]
    best = []
    for s in tests[16]:
        m = 0
        for t in T16:
            if t["s0"] == s["s0"]:
                m = max(m, sum(a == b for a, b in zip(s["events"], t["events"])))
        bm = max(sum(a == b for a, b in zip(s["events"], t["events"])) for t in T16)
        best.append((m, bm))
    print(f"[{nm}] test16 vs {len(T16)} 16-event train stories: max events agreeing by position (same s0) = {max(b[0] for b in best)}; any s0 = {max(b[1] for b in best)}; mean best (any s0) = {sum(b[1] for b in best)/len(best):.2f}")
# same s0 frequency
for nm in ("cert_s10",):
    s0s = collections.Counter(tuple(s["s0"]) for s in train[nm])
    print(f"[{nm}] test s0 seen in train: " + ", ".join(f"L{L}: {sum(tuple(s['s0']) in s0s for s in G)}/128" for L, G in tests.items()))
