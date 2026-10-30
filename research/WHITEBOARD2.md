# Whiteboard, second round: everything learned, and what it points to

22 October 2026. A retrospective over the whole Polyformer arc, from the 2023 notebook's cubic attention
to the energy-form tests of today, written to extract laws rather than list results. Numbers are the
measured ones; each has a source file in `research/`.

## 1. What was tried, in one table

| Phase | Idea | Where it won | On text |
|---|---|---|---|
| Cubic / 2-simplicial attention (2023 notebook; FINDINGS) | one query against pairs of keys | SET 100% vs 59% pairwise; Match-3 mod 32 100% vs 91% | null at equal FLOPs |
| Beyond-cubic operators (DS-PA, quartic, hyperchain) | higher arity, Strassen-like forms | toy relations | null |
| Newton / subset / free-field attention (FORMALISM) | all arities from power sums; selection × arity | keyed Match-3 100%; keyed Match-4 91% vs 77% with a curriculum | enwik8 1.652 vs 1.650 |
| Local regression (LLA, Parallax; LOCAL) | attention as local linear fit | | −0.4% / −0.75% at equal FLOPs, grows with tokens; "a pair correction, not arity" |
| Groups / holonomy (GROUPS) | non-commuting per-token rotations | A5 and S5 word problems in one layer, 99%; softmax at chance; commuting layers stop at the order-blind ceiling | neutral |
| BEYOND: selection + estimation + composition in one layer | | | worse than softmax + conv |
| ARC rung 1 and loss dilution (NEXT) | composition on grids; decision-weighted loss | dilution measured at 95–190×; reweighting lifts decisions from 0.9% to 18–35% (softmax more than the composing layer) | |
| LOOPS: frames, grid clocks, hybrids | content-driven position; GDN + attention | hybrid −0.89% vs RoPE at 443M tokens; forget gates learn a timescale hierarchy; clocks count clauses | frames neutral |
| EVENTS | event model; attribution of the hybrid | at 8k: −0.66% on far repeats, frames × recurrence interaction | at 512 the lead is erased by two published parts; event bottleneck +3–6% |
| REVISE | revisable in-context memory; routing | | every arm worse; gate opened everywhere; routing +1.5% |
| T1 / T2 | type stability; input addresses | | stability = content-ness, predicts the opposite; hashed n-gram input embeddings −0.79% at 22M |
| K0 ⋈ H (debate) | looped block + hindsight objective | | rejected as an assembly; hindsight finds narrative ends, not decisions |
| Validations V1–V5, E0–E2 | loops, energy descent, workspaces, retraction, group-manifold state | per-event recurrence exact at 256 events (16× training) on 1/3 seeds, 4/6 on the group manifold; retraction retracts the right things | energy signature cannot appear; joint energy model learns one hop per $10 |

Spend over the arc: about $750 on Modal. Everything pre-registered since mid-October.

## 2. The laws the data obey

**Law 1. On text at any scale we can run, the mixer does not matter.** About a dozen mixers, all within
−1% and +1.5% of softmax at equal FLOPs; the margins shrink with size; two published parts erase a hybrid's
lead at short context. The field says the same (the 2026 survey of non-transferring modifications). The
exceptions are not mixers: the optimiser (Muon, 4.3% at 100M), input-embedding capacity (−0.79%), tokens
seen, and recurrence at long context on far repeats (−0.66% at 8k).

**Law 2. Compositional and higher-arity machinery wins exactly where two things hold:** the generating
process has a group atom or a hub-less k-ary relation, and the surface tokens are its generators. SET,
Match-3, keyed Match-4, A5 and S5 word problems, the event word problem. It loses where either fails:
prose is aperiodic and lexicalises its relations with hubs; narratives need reference resolution before
composition; ARC puts the state on the wrong axis. This is the single explanation of every text null, and
it is a theorem-shaped one (Krohn–Rhodes; the hub reduction of hypergraphs to bipartite graphs).

**Law 3. Learnability beats expressivity, every time.** Native terms get learned; compositions across
depth do not; curricula decide (keyed Match-4; A5); which basin training lands in decides exactness (V2,
E2); every free gate, router or soft action collapsed (the EVENTS router toward 0.5, the REVISE gate open
everywhere, the V1 gate to zero) unless it had a training target; straight-through maps did not learn.

**Law 4. The objective decides what is learned, not the block.** Token-averaged loss dilutes decisions
by about a hundredfold. Hand-labelled weights on decisions lift them 20×; the self-derived hindsight gap
lifts nothing because it finds the tokens the future explains, which are not decisions. Running-state
supervision makes a plain transformer exact on the revision task where the energy model fails. Properties
are learned when the loss supervises the intermediate state, and only then.

**Law 5. Dynamics do not think.** Under descent with tied weights, a barrier the state would have to
cross is one it never crosses; training removes the barrier or the switch. Compute rises with ambiguity
only as the logarithm of a displacement. The "no, wait" of reasoning models is produced by the objective
(an outcome reward) inside sequential text, not by any dynamics of the block.

**Law 6. Recurrence along the sequence extrapolates; depth does not.** A state carried once per event
composes exactly sixteen times past the training length; the same compute spent as depth, looped or not,
tracks a handful of events and collapses. Exactness requires the carried state to live on the set it
represents: the group manifold doubles the exact-seed rate, and a state space equal to the group would
make it reliable. That is holonomy's true role: a state space for a recurrence, not a position code.

## 3. What this says about the premise we started from

The project began from the brain: few but rich layers, loops, higher-order interactions. We tested the
architectural half of that premise to exhaustion. Rich layers (arity, composition) pay only off text, by
Law 2. Loops pay as recurrence with state, not as depth, by Law 6. Both results are solid and both are
smaller than the premise. The half we never tested is the learning rule. Brains are not taught by teacher
forcing; the hypothesis that has carried neuroscience for twenty years is that cortex predicts its own
future state. By Law 4, the objective is where the leverage has been all along, and the one objective we
have not tried is the one the premise actually implies: supervise the state by its own future, with no
labels.

## 4. The refined directions, ranked, each with one decisive test under $10

**D1. Self-supervised running state.** On the late-evidence task, a transformer with labelled running-state
supervision is exact (100% on every seed) and without it falls 45 points as the decisive event moves
later. Replace the labels with a one-line objective: predict your own future state, ‖P h_t − sg(h_{t+k})‖²
with the standard anti-collapse (stop-gradient target, a variance term), the joint-embedding recipe that
has precedent on language models this year. Test: does it recover most of the labelled gain with no
labels? Prediction worth registering: at least half the gain at k = 8. If it does, the "supervise the
address" idea has a form that applies to text, where no state labels exist. If it does not, Law 4 says the
lever needs labels, which decides D2. Cost: well under $10 on the existing V1 harness.

**D2. State supervision where labels exist at scale: execution.** An interpreter gives the exact state
after every step for free, so code execution traces are running-state supervision on real data. The
per-event recurrence of Law 6, with a state space shaped for the variables being tracked, against a
transformer given the same trace supervision; the claim is length extrapolation on execution, where
transformers are known to degrade. Public data, public baselines (learning-to-execute, scratchpad,
CodeExecutor-style traces), and the one setting in which Laws 2, 4 and 6 all point the same way.

**D3. Exactness by construction.** On the event word problem, snap the carried state to a discrete code
(a vector-quantised state) or make the state space the group's image; register 3/3 exact at 256. Narrow,
cheap, and it turns Law 6 from "sometimes" into "always" if it passes.

**D4. The record as a paper.** Pre-registered, equal-FLOP, bucketed, with theorems: the coupling barrier,
the subset expansion, the order-blind ceiling, the hub-ful account of why arity does not pay on language,
the dilution number, the frames × recurrence interaction, and a dozen nulls that the field keeps
re-running. That is a TMLR or analysis-track paper now, whatever D1–D3 do.

## 5. What to stop

Mixers on prose. Gates, routers and soft actions without a training target. Energy dynamics as a source of
thinking. Suffix objectives on answer-at-the-end formats. Assembled designs. Any test whose pass could be
explained by depth alone without a depth control.

## 6. The honest odds

D1 recovers at least half the labelled gain without labels: 0.35. D2 shows length extrapolation on real
execution against a trace-supervised transformer: 0.4, with the cost that it is a state-tracking paper
rather than a language one. D3 passes: 0.6. D4 is a paper at better than even odds. None of these is the
jackpot; D1 is the one that would change what we believe.
