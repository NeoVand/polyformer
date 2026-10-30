# B1: the visionary lens

The interpreter proves a neural network can host an exact machine. The leap is to let *experience*, not a prompt,
write the machine. Three ideas, ranked.

## 1. Exact imagination: a neural world that never drifts

**The demo.** You play a game world a network learned from 30-second clips, hide a key, wander for an hour
(50,000 steps) and find it where you left it, every frame identical to the real engine; then the network plans a
2,000-move solution in its imagination and executes it blind, first try.

**Why it seems impossible.**
- LeCun: autoregressive models are "doomed" because per-step error compounds.
- Genie 3 advertises consistency for minutes and about a minute of visual memory. GameNGen sees about 3 seconds.
  Oasis forgets what you look away from. DreamerV3 imagines 15 steps.
- You et al. (2026) prove that rollout training leaves off-support errors untouched.

**Assets.** v1 already is this machine, with symbolic actions: a snapped tracker keeps a Rubik's cube
(4×10¹⁹ positions) exact at 10,000 moves. Dreaming from actions is that setup with an encoder in front and a
renderer behind, and renderer errors never feed back. The blindness theorem says scaling video likelihood will not
get there. Game engines emit Nerode pairs for free (two histories, same state hash). I expect Theorem P to have a
world-model form, a short Lean lemma away: if the learned update is local, checking each reachable local row once
against reality proves the rollout exact for every action sequence. Nobody has a finite certificate for a learned
simulator.

**48 hours ($0, M4).**
- Worlds: procedural 12×12 key–door–box maps, shown once as an overview frame, then egocentric 64×64 views with
  random textures and noise. Train on 32-step random clips.
- Arms, sharing one encoder and decoder: a DreamerV3-style categorical RSSM; the same with snap, closure and engine
  equivalence pairs.
- Test on 200 held-out maps: 10,000-action open-loop dreams (300× the clips), a "move the box, leave, return"
  probe, the local-row certificate, and one 1,000+-move plan executed blind.
- Prediction: the snapped arm is frame-exact on at least 190/200; the others fail within a few hundred steps.

**Kill:** DreamerV3's categorical latents are also exact (so the snap is not the news); exactness needs state
labels; the encoder cannot snap the first frame; or held-out maps fail.

**Why it matters.** Drift caps planning horizons, the simulators that train agents and robots, and "neural game
engines". An exact, certified discrete skeleton under neural perception removes the cap and lets you prove things
about a learned world ("no path reaches the stairs without the key").

*Prior-art gap:* L1–L6 skip pixel world models. Read first: Agostinelli & Soltani (RLC 2024, discrete cube world
model from images), C-SWM (Kipf et al. 2020), DreamerV2/V3, WorldMem.

## 2. The scientist that knows what it knows

**The demo.** Viewers fail to crack an alien device (four buttons, nameless glyphs under heavy noise, a hidden
machine); the model pokes it for two minutes, draws the machine, says "at least 137 states, proved by these 137
experiments; if at most 150, my model is exact forever, proved by this suite", and predicts the display after a
1,000,000-press sequence the viewer types, before the device runs it.

**Why it seems impossible.**
- Kalai & Vempala (STOC 2024): calibrated language models must hallucinate.
- ARC-AGI-3's interactive games: frontier agents trailed humans badly at the 2025 preview.
- Moore (1956): no finite experiment identifies an unknown machine.

**Assets.** The theorem pair is Moore's case against Chow's case, already in Lean. The same mathematics lets a
scientist state the limits of its own knowledge. Nerode training recovers the minimal automaton from
equivalences (960/960 clusters), and Savant writes, certifies and runs the table.

**48 hours.**
- Devices: 50 random hidden machines (10–300 states, some composed), with glyph outputs under nuisance.
- Pipeline: an equivalence-trained tracker clusters the glyphs; Savant chooses the experiments; a separating set
  plus a W-method suite gives the boundary statement.
- Predictions: at least 45/50 exact million-press predictions, and zero false "proved" statements.

**Kill:** a frontier model with Python and the same press budget matches us (then this is L* with eyes; Angluin
1987 and LearnLib own the symbolic version), or a single "proved" statement is false.

**Why it matters.** Hallucination is not a law where the world is machine-shaped: protocols, devices, codebases,
gene circuits. An AI that says "proved", "proved if n ≤ 150" or "unknown" is a scientist you can delegate to.

## 3. The glass mind

**The demo.** Savant runs a universal machine for 100,000 ticks while a meter shows every bit crossing between
thoughts; a red-team copy trained to smuggle a secret succeeds under ordinary decoding and is caught every time
under the pin; and when a viewer edits any hidden activation mid-run, the page predicts the next million ticks
before they happen.

**Why it seems impossible.** Chain-of-thought monitorability is "a new and fragile opportunity" (Korbak et
al. 2025); reasoning models don't always say what they think (Chen et al. 2025); models can hide reasoning in text
(Roger & Greenblatt 2023). Interpretability explains interventions; it does not predict their long-run effect.

**Assets.**
- Each tick sees only the program and the (state, event) pair (cache-policy theorem). Theorem P fixes every
  symbol's meaning; `no_finite_test_suite` makes the contrast with plain decoding a theorem.
- BRIDGE already measured the hidden channel in plain decoding: aimed kicks on old run tokens flip 149/2,688
  labels; random kicks flip 0.
- Robust cells and CIRCUITS make surgery predictable: a tick flips only at 1.5–3× the residual norm, and then
  to another named state.
- Universality: 2,079/2,081 rules of a universal Lag system right, untrained; two hub rules still fail.

**48 hours.** (a) A LoRA red team carries a bit from an early event to the final answer while emitting the table's
states, plain against pinned. Prediction: plain leaks at least 90% of the time; pinned carries nothing undetected.
(b) 1,000 random and aimed activation edits, each future predicted from the cell map. Prediction: at least 99%
exact.

**Kill:** plain decoding cannot learn the channel either (no contrast), or more than 1% of edits produce behaviour
outside the table.

**Why it matters.** Safety today hopes models narrate faithfully. This makes faithfulness a property of a cache
policy, provable at universal power. Limit: only execution is glass; writing the program is still
ordinary thought.

## If I could only pursue one

Exact imagination. It breaks the most widely held belief, in the field with the most money and attention, and it
leaves the interpreter loop for world models. It rests on what nobody else has: a snap built for event-driven
state, a theorem saying competitors cannot scale their way there, and a local-row certificate that could verify a
learned world against reality with finitely many experiments. The test is cheap, runs on the laptop and has a
sharp kill: if DreamerV3's categorical latents are already exact, we know in two days. The real risk is
perception: if the encoder cannot snap a noisy first frame, the demo shrinks to a symbolic cube with pictures. If
it works, next is a neural game in the browser that stays exact for an hour while you play.
