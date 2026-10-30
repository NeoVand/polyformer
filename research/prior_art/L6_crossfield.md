# L6: cross-field framing (theoretical computer science, neuroscience, cognitive science)

Literature agent L6, 28 Oct 2026. Scope: every analogy drafted in INSIGHTS §5, better replacements, the TCS framing
(program checking and certifying algorithms above all), and long-sequence tasks a general reader knows.

**Method.** Each entry below was looked up live on 2026-10-28. DOI metadata came from Crossref and OpenAlex; abstracts
from PubMed E-utilities, OpenAlex and the arXiv API; and full text wherever a claim needed more than an abstract.
Verification tags:

- **[F]**: full text checked for the specific claim we attach;
- **[A]**: abstract (or the publisher's summary) checked for the claim;
- **[M]**: metadata only. The DOI resolves to the stated authors, title, venue and pages, but the claim we attach comes
  from a secondary source or standard knowledge, so check it before it goes into the paper;
- **[U]**: could not be verified online (§7).

All URLs were accessed on 2026-10-28. Spend: $0. The shared web-search budget ran out partway through, so the last
checks used direct DOI and URL fetches only. I edited nothing outside `research/prior_art/`.

Cross-reference: L1 (`L1_computation_inside.md`) covers Schuurmans et al. and their 2026 sequel in depth. Here they
appear only where the TCS framing needs them.

---

## 0. What matters (read first)

1. **Rabin (1963) already contains a robust Myhill–Nerode argument. Check v1's novelty claim against it.**
   - **The argument.** A probabilistic automaton has an *isolated cut-point* when every word's acceptance probability
     stays at least δ away from the threshold. Under that condition, any two words that are Myhill–Nerode inequivalent
     must have state distributions more than 2δ apart in L1. A volume (packing) argument then bounds the number of
     classes by (1 + 1/δ)^(n−1), so the language is regular (Theorem 3, pp. 237–238) [F].
   - **Rabin's own framing.** He presents the result as a contribution to the theory of reliability: circuits built
     from unreliable components. He leaves the general "stability" problem open [F].
   - **The rest of the lineage.** Maass & Orponen (1998), Casey (1996) and Omlin & Giles (1996) complete it.
   - **What v1 must do.** Cite Rabin and say what is new: learned continuous trackers, the closure, blindness and the
     aimed kick.

2. **The theorem pair (PAIR) descends directly from 1956 automata theory.**
   - **Moore's Theorem 2** (1956, p. 140) says that for any machine and any finite experiment, some other,
     distinguishable machine gives the same outcome [F via the verbatim quotation in Fields 2013]. This is
     `no_finite_test_suite`.
   - **Vasilevskii (1973) and Chow (1978)** showed that once the implementation's number of states is bounded, a
     finite complete test suite exists [A, via Vaandrager & Melse 2025].
   - **What the clock supplies.** It provides exactly that bound. It also places the model directly in any state (the
     (state, event) block) and makes the state observable (a written token).
   - **Why one test per row is enough.** Under those three conditions the complete suite collapses to one test per
     transition, which is the per-row certificate. So `pinned_regeneration_iff` is the conformance-testing theorem for
     the case "no hidden state, set-able, observable". This derivation is elementary and ours, not a cited result.

3. **Per-rule verification of an LLM has a precedent: Schuurmans, Dai & Zanini (2024).**
   - **What they did.** They checked each of 2,027 Lag-system rules once on gemini-1.5-pro-001 under greedy decoding.
     Each check used one query: the system prompt plus the rule's two-symbol left-hand side. They then relied on
     determinism and a chain of reductions [F].
   - **What their paper lacks.** It never states that a per-rule check is necessary and sufficient at every length. It
     never discusses the code path, positional encoding or numerical nondeterminism [F].
   - **What separates us.** The paper's distinct claims are the iff, the code-path hypothesis (ARITH: the one-token
     forward 2 is not bitwise on 86% of ticks), and the unpinned no-finite-test theorem. L1 gives the full positioning,
     including the 2026 sequel.

4. **Cite Turing (1936) §9, not "Turing machines".**
   - **What the executor is.** The pinned executor is a finite-state transducer (Mealy 1955) reading a one-way,
     read-only input. It is not a Turing machine.
   - **Turing's §9 is the pin's contract.** His analysis of a human computer states the pin's conditions exactly:
     - a bound on the symbols observed at once (p. 250);
     - finitely many states of mind (p. 250). Turing's reason is a robustness argument: allow infinitely many and some
       would be so close they would be confused;
     - the state of mind replaced by a written *note of instructions*. The computer then does one step per sitting
       and can stop and resume; the progress of the computation is the note plus the tape (pp. 253–254) [F].

5. **Three drafted neuroscience mappings are wrong as written.**
   - **"Plain decoding ≈ bump diffusion; pinned ≈ activity-silent working memory."** BRIDGE shows that plain decoding
     fails first at the *pointer*. Its step errors come from attention moving onto the run's own history, which is
     interference rather than diffusion of a stored value. Activity-silent working memory is about *where* a memory is
     stored (synapses rather than spiking), not about discretisation. Replace it with two analogies: continuous versus
     discrete attractors for the step (§2.B), and placekeeping, path integration and serial order for the pointer
     (§2.C–E).
   - **Theta–gamma coding.** It holds several items at once, one per gamma subcycle, while the pin holds one. Drop it.
   - **Pattern completion.** Our cue is a complete key, and the observed failure, on near-duplicate names, is a failure
     of *pattern separation*.

6. **Wimmer et al. (2014) cannot be cited for "error grows with delay".**
   - **Their design.** Their monkeys had a fixed 3-s delay [F]. For delay dependence they cite White et al. (1994) and
     Ploner et al. (1998).
   - **What the data say:**
     - White et al.: variable saccade error grew monotonically over delays of 0.4–5.6 s [A];
     - Ploner et al.: human errors peaked near 20 s and then fell, over delays of 0.5–30 s [A];
     - Shin, Zou & Ma (2017): delay effects on human orientation working memory are weak, at most 1.14°/s [A];
     - Panichello et al. (2019): errors diffuse, and discrete attractors bias memories but cut the diffusion [A].
   - **Summary.** The error is random-walk-like over seconds in spatial working memory, and attractor-corrected and
     task-dependent elsewhere.

7. **Program checking (Blum–Kannan) is the wrong frame for the run and the right one for two other places.**
   - **Why it fails for the run.** The run's specification is the table itself, so a checker would just recompute
     the run.
   - **The right frame for the run** is translation validation of each compiled program (Pnueli et al. 1998; Necula
     2000). A verified compiler (Leroy 2009) would be the weights-level N\*, which we do not have.
   - **Where result checking pays:**
     - (i) at the compile step, where certified does not mean correct (64–88 of 768 gate answers);
     - (ii) on arithmetic outputs, where a cheap residue check tests the answer against the *question*.

8. **One framing sentence carries the cross-field paragraph.** One 1956 volume, *Automata Studies*, edited by Shannon
   and McCarthy, holds the three ancestors of our three results:
   - von Neumann's restoring organ: reliability comes from stopping error accumulation at every stage;
   - Kleene's regular events, defined for nerve nets: neural networks and finite automata were one subject from the
     start;
   - Moore's gedanken-experiments: no finite test identifies a machine whose state is unbounded.

   All three are chapters of one book (DOIs 10.1515/9781400882618-003, -002 and -006) [M].

---

## 1. The drafted analogies: verdicts

Verdicts: **strong** (accurate at the level we use it, with the right citation); **usable with care** (accurate only
with the stated scope); **misleading** (wrong as drafted; replace or drop).

### 1.1 Theoretical computer science

**Turing's finite control and tape**
- **Verdict:** strong if cited as Turing's §9 analysis of the human computer; an overclaim as "the LLM is a Turing
  machine".
- **Citations:** Turing 1936 §9, pp. 249–254 [F]; Mealy 1955 [A]; Schuurmans 2023 [A] (bounded context ⇒ finite
  automaton); Schuurmans et al. 2024 [F].
- **Where it breaks:** the event tape is read-only and one-way, so the executor is a finite transducer. It would be a
  Turing machine only with a writable, rereadable tape, as in Schuurmans' Lag-system construction.
- **For the paper:** "The clock imposes on the model the conditions Turing (1936, §9) placed on a human computer. The
  model sees the program and one (state, event) pair. It holds nothing else, and it writes the new state down, Turing's
  'note of instructions', before the next step."

**Myhill–Nerode**
- **Verdict:** strong (it is v1's theory).
- **Citations:** Nerode 1958 [M]; Rabin & Scott 1959 [M]; Rabin 1963 [F]; Maass & Orponen 1998 [A]; Casey 1996 [A].
- **Where it breaks:** not as an analogy. The risk is novelty against Rabin 1963 (§0.1).
- **For the paper:** "A margin forces finitely many distinguishable states. Rabin (1963) proved this for probabilistic
  automata with an isolated cut-point, and robust Myhill–Nerode proves it for learned continuous trackers." Have the v1
  owner check this wording against v1's exact statement.

**Translation validation**
- **Verdict:** strong.
- **Citations:** Pnueli, Siegel & Singerman 1998 [M]; Necula 2000 [A]; contrast with Leroy 2009 [A].
- **Where it breaks:**
  - Translation validation proves refinement symbolically for all inputs. We discharge the step obligation by
    enumerating a finite set of reachable rows, under one fixed Lean theorem.
  - The guarantee names a host and a code path.
- **For the paper:** "As translation validation checks each compiled program instead of the compiler, the certificate
  checks each program the model runs instead of the model."

**Proof-carrying code**
- **Verdict:** usable with care (one clause at most).
- **Citations:** Necula 1997 [A].
- **Where it breaks:** proof-carrying code works because checking the shipped proof is cheap and needs no trust in the
  producer. Our certificate is rechecked by re-running every row on the same host and code path.
- **For the paper:** avoid it, or say: "The certificate travels with the program, but checking it means re-running its
  rows, not reading a proof."

**von Neumann's restoring organ and digital noise margins**
- **Verdict:** strong for the principle; usable with care for the mechanism.
- **Citations:** von Neumann 1956 §7.2, §9.2.2–9.2.3, §11.2 [F]; Pippenger 1988 [A]; Brody et al. 2003 [A].
- **Where it breaks:**
  - von Neumann's errors are independent random gate failures, cured by redundancy: bundles, majority organs and random
    permutations. Ours are deterministic and context-induced, cured by quantising to a token at each step.
  - The ~30-head lookup committee is the redundancy-like part, and it is untested as such (§6, E7).
  - We have not verified a textbook source for the "static discipline".
- **For the paper:** "von Neumann (1956) showed that a network stays reliable only if something stops its errors
  accumulating, and that a machine with memory 'remembers its mistakes, so to speak, and thereafter perpetuates them'.
  Plain decoding does exactly this: after its first error, 49,084 of 49,087 steps follow the table from what it wrote.
  The pinned step stops it below the program."

### 1.2 Memory and lookup

**Content-addressable memory**
- **Verdict:** strong as "associative memory"; usable with care as hardware CAM.
- **Citations:** Hopfield 1982 [A]; Ramsauer et al. 2021 [F]; Bricken & Pehlevan 2021 [A]; Willshaw et al. 1969 [M];
  Pagiamtzis & Sheikholeslami 2006 [A] (hardware).
- **Where it breaks:**
  - A hardware CAM does exact matching in one cycle.
  - Ours is a soft match, limited by its margin, carried by ~30 heads, and it fails on near-duplicate keys. Ramsauer's
    separation Δ and "metastable states" for similar patterns predict exactly that failure.
- **For the paper:** "The fetch is associative recall in the modern-Hopfield sense: attention retrieves the row whose
  key matches the (state, event) pair in one step (Ramsauer et al. 2021). It fails where that theory says it should:
  on rows whose keys are nearly identical."

**Hippocampal pattern completion**
- **Verdict:** misleading. Replace it with pattern separation and heteroassociative recall.
- **Citations:** Marr 1971 [A]; Treves & Rolls 1994 [A]; Nakazawa et al. 2002 [A] (completion); Leutgeb et al. 2007
  [A]; Yassa & Stark 2011 [A] (separation); Whittington et al. 2022 [A] (position codes).
- **Where it breaks:**
  - Pattern completion retrieves a whole memory from a *partial* cue. Our cue is complete.
  - Our failures (` illeg` beside ` illegal`; wrong-answer margins ~3) are interference between similar keys.
  - The unused positional pointer code has no clean hippocampal analogue.
- **For the paper:** "Its failures are those of an associative memory without pattern separation: near-duplicate names
  lose margin. Screening the name pool by worst margin is pattern separation done by hand."

### 1.3 Neuroscience and cognition

**Neuronal recycling**
- **Verdict:** usable with care (good, and it includes costs).
- **Citations:** Dehaene & Cohen 2007 [A]; Dehaene et al. 2010 [A]; Anderson 2010 [A]; Gould & Vrba 1982 [A].
- **Where it breaks:**
  - Recycling in brains unfolds over years of learning and is inferred from imaging. Ours is a small, exactly known edit
    to known circuits.
  - The "older function" (copying in context) was itself learned. "Exaptation" or "neural reuse" fits as well.
- **For the paper:** "As reading recycles visual cortex shaped for other uses (Dehaene & Cohen 2007), the executor
  recycles circuitry the model learned for next-token prediction. A 2,560-number vector switches it on for 84% of
  held-out tables. And as with literacy (Dehaene et al. 2010), completing it by weight edits costs the old function
  something: 0.05–0.48 nats of WikiText NLL. The soft prompt costs nothing."

**Persistent versus activity-silent working memory**
- **Verdict:** misleading as drafted.
- **Citations, if any of it is kept:** Compte et al. 2000 [A]; White et al. 1994 [A]; Wimmer et al. 2014 [F] (fixed
  3-s delay); Mongillo et al. 2008 [A]; Stokes 2015 [A]; Wolff et al. 2017 [A]; Lundqvist et al. 2018 [A] and
  Constantinidis et al. 2018 [A] (the debate pair).
- **Where it breaks:** see §0.5. The pin's state is neither persistent spiking nor a silent synaptic trace. It is an
  external symbol.
- **For the paper:** replace with §2.B: "Cortex faces the same trade-off. A continuous attractor stores a value finely
  but lets it diffuse, while discrete attractors resist perturbation at the cost of resolution (Brody et al. 2003;
  Inagaki et al. 2019; Panichello et al. 2019). The pinned step sits at the discrete end."

**Gating of working memory (PBWM)**
- **Verdict:** usable with care.
- **Citations:** Frank, Loughry & O'Reilly 2001 [A]; O'Reilly & Frank 2006 [A]; Hochreiter & Schmidhuber 1997 [A] (the
  ML counterpart).
- **Where it breaks:**
  - PBWM learns its gate through dopamine-driven actor-critic learning. The clock's gate is fixed by design.
  - The model's learned decision to open `<program>` is a different gate: *when* to compute, not *what* to hold.
- **For the paper:** "The clock is a working-memory gate in the sense of basal-ganglia models (Frank et al. 2001). It
  admits one (state, event) pair, shields it from the rest of the context, and clears it after use. Unlike those
  models, our gate is designed, not learned."

**Theta–gamma sequence coding**
- **Verdict:** misleading; drop it.
- **Citations:** Lisman & Idiart 1995 [A]; Lisman & Jensen 2013 [A]; Rizzuto et al. 2003 [A].
- **Where it breaks:**
  - Theta–gamma holds several items at once, one per gamma subcycle, with order carried by phase. The pin holds one
    item, and order lives in the external stream.
  - The only point of contact is that fixed positions at each tick resemble phase reset at each item (Rizzuto 2003),
    and nothing we measure links the two.
- **For the paper:** do not use. Use the one-item focus of attention and the serial production cycle instead (§2.A,
  §2.F).

### 1.4 What the working-memory data actually show (the question in the brief)

- **Spatial working memory, monkeys and humans, seconds.** In memory-guided saccades, variable error grows monotonically
  with delay from 0.4 to 5.6 s, while systematic error stays flat (White, Sparks & Stanford 1994) [A].
  - The bump-attractor model explains this as random drift of the bump's centre, i.e. diffusion (Compte et al. 2000)
    [A].
  - Wimmer et al. (2014) tied it to neurons. At a fixed 3-s delay, trial-by-trial fluctuations in prefrontal delay
    firing predicted the direction of the saccade's deviation. The correlation also appeared earlier for cues near a
    cell's preferred location, as a diffusing bump predicts [F].
  - Wimmer et al. also argued *against* a discrete-attractor account for this task. Noise-driven jumps between discrete
    attractors would give multimodal error distributions, which the data do not show [F].
- **Longer delays.** Over delays of 0.5–30 s, human saccade errors peak near 20 s and then fall (Ploner et al. 1998)
  [A]. The error is not a random walk at long timescales.
- **Human visual working memory.** For orientation, delay effects are much weaker than set-size effects (at most
  1.14°/s) and appear in only a minority of subjects (Shin, Zou & Ma 2017) [A].
  - Schneegans & Bays (2018) attribute delay-related loss to drift in the encoded value, not to fading activity [A].
  - Panichello et al. (2019) find diffusion plus discrete attractors. The attractors bias memories, reduce diffusion,
    strengthen as load (and noise) rises, and adapt to the statistics of the environment [A].
- **Activity-silent states.** A maintained item can be decoded from the brain's response to a nonspecific "ping" with
  no persistent activity (Wolff et al. 2017) [A], or reactivated by TMS (Rose et al. 2016) [A].
  - The mechanism proposed for this is facilitation at synapses, refreshed by sparse spiking (Mongillo et al. 2008)
    [A].
  - Whether persistent spiking is necessary is openly debated (Lundqvist et al. 2018 versus Constantinidis et al.
    2018) [A].
- **What maps honestly.** The *existence* of a diffusion-versus-discretisation trade-off in cortex, and the finding
  that discrete attractors are robust to transient perturbation (Inagaki et al. 2019) [A], map onto our step. The
  random-walk growth of a remembered value does not map onto our plain-decoding failure, which is a pointer loss plus
  interference.

---

## 2. New, better analogies

Each entry gives a verdict, the mapping, the evidence, where it breaks, a sentence for the paper and a measurement (§6
numbers the experiments).

### 2.A The "human Turing machine": a parallel step feeding a serial production system

- **Verdict:** strong. This is the closest cognitive-neuroscience description of the pinned executor.
- **Mapping.** Zylberberg, Dehaene, Roelfsema & Sigman (2011) propose a hybrid device for mental programs [A]:
  - each step is a massively parallel computation that feeds a slow, serial production system;
  - competing accumulators select the production;
  - productions change sensory and memory states, and iterating the cycle runs a program.

  The pinned executor is this design built inside an LLM:
  - a parallel forward pass computes one row;
  - the clock is the serial loop;
  - the written state token is the production's effect.
- **Supporting evidence:**
  - ACT-R: modules place chunks in buffers, and one production rule fires per cycle on the buffer pattern (Anderson et
    al. 2004) [A].
  - The central serial bottleneck (Sigman & Dehaene 2005) [A].
  - A spiking "router" model that chains processors at 100–500 ms per step (Zylberberg et al. 2010) [A].
- **Where it breaks:**
  - The brain's productions are learned and are selected by noisy evidence accumulation.
  - Our table is written in context, and selection is an argmax over one forward pass.
  - Nobody has certified a brain.
- **For the paper:** "Zylberberg et al. (2011) proposed that the brain runs mental programs as a parallel step feeding
  a serial production cycle. The pinned executor is that architecture inside a pretrained language model, with the
  added property that every step can be checked."

### 2.B Discrete versus continuous attractors (replaces "persistent versus activity-silent")

- **Verdict:** strong.
- **Mapping.** Brody, Romo & Kepecs (2003) make the computer analogy themselves [A]. Computers gain robustness to noise
  by approximating analogue quantities with digital ones, and models of persistent activity show that the most robust
  way to hold a continuous parameter is to discretise it.
  - Continuous attractors need fine tuning (better than 1%) and drift (Seung 1996 [A]; Koulakov et al. 2002 [A]).
  - Bistable units make an integrator robust without fine tuning (Koulakov et al. 2002 [A]; Goldman et al. 2003 [A]).
  - In mouse ALM, delay activity moves towards *discrete* endpoints that are robust to transient optogenetic
    perturbation. Occasional switches to the other endpoint are followed by wrong actions (Inagaki et al. 2019) [A].
  - Reviews: Khona & Fiete 2022 [A]; Chaudhuri & Fiete 2016 [A].
- **Our counterparts:**
  - v1's closure and v2's token snap are the discrete end of this trade-off.
  - CIRCUITS §6's sharp decision cells: the destination flips within Δα = 0.05, and noise must reach 1.5–3× the
    residual norm to flip a tick.
  - BRIDGE's aimed-versus-random kicks: 149 of 2,688 labels flip under aimed kicks and none under random kicks of the
    same size.

  These match the perturbation logic of Inagaki et al.: transient perturbations return to the endpoint, and large ones
  switch it.
- **Where it breaks:**
  - Inagaki's attractors are dynamical, in a recurrent circuit over time. Ours are decision regions of a feedforward
    step, re-entered through a discrete token.
  - Wimmer et al. (2014) show that spatial working memory in monkey PFC is continuous, not discrete [F], so the brain
    does not always choose the discrete end.
- **For the paper:** "Cortex trades resolution for robustness the same way. Short-term memories in motor cortex settle
  on discrete endpoints that survive transient perturbation (Inagaki et al. 2019), while a continuous code diffuses
  (Compte et al. 2000). Our decision cells flip only when noise reaches 1.5–3 times the residual norm."
- **Measurement:** E6.

### 2.C Path integration and landmark correction (for the pointer)

- **Verdict:** strong for the pointer.
- **Mapping.**
  - In continuous-attractor models of grid cells, errors in integrating velocity accumulate unless something resets
    them (Burak & Fiete 2009) [A].
  - In rats, grid error grows with time and distance since the animal last met a boundary, and contact with a boundary
    corrects it, direction by direction (Hardcastle, Ganguli & Giocomo 2015) [A].

  Plain decoding keeps its place in the input by internal dead reckoning: a counter as long as the input, which v1
  identified as the hard case. The clock's event stream is a landmark at every step.
- **Evidence from our runs:**
  - The first errors are misread events: 94 of 96 failed runs at 8,192 events and 80 of 80 at 12,000.
  - Pinned execution has a pointer by construction.
- **Where it breaks:**
  - Grid drift is graded and coherent.
  - Our pointer is *lost*, not slightly off: in 16 of 19 free-running failures, no shift within ±3 events matches
    better than chance (BRIDGE M6).
  - A transformer has no velocity input.
- **For the paper:** "Plain decoding keeps its place by dead reckoning and loses it, the way grid-cell estimates drift
  between boundaries (Hardcastle et al. 2015). The clock gives it a landmark at every step."
- **Measurement:** E4 (landmark tokens; error against distance since the last landmark).

### 2.D Placekeeping: sequence errors versus step errors

- **Verdict:** strong. It reproduces our two-failure dissociation in humans.
- **Mapping.** Altmann, Trafton & Hambrick (2014) had people keep their place in a procedure of steps, each step with
  its own requirements [A]:
  - interruptions of about 2.8 s doubled the rate of *sequence* errors, and interruptions of about 4.4 s tripled it;
  - *nonsequence* errors showed no interruption effect.

  In humans, keeping one's place and doing the step are separable failures. This is our split between pointer errors
  and step errors. The activation-based goal-memory model (Altmann & Trafton 2002) explains it by interference from
  old goals [A].
- **Where it breaks:**
  - The human errors are mostly local (a skipped or repeated step); ours are mostly a lost place (16 of 19).
  - Humans recover their place from cues; plain decoding does not recover (42% of events match afterwards).
- **For the paper:** "People keeping their place in a procedure show the same split: a brief interruption doubles
  their sequence errors and leaves their step errors alone (Altmann et al. 2014). Plain decoding fails in the same two
  ways, and the clock removes both."
- **Measurement:** E5 (insert an interruption mid-run).

### 2.E Serial-order memory: positional codes versus chaining

- **Verdict:** usable with care, and it becomes a measurement.
- **Mapping.**
  - Theories of serial order divide into chaining, ordinal and positional accounts. Human error patterns, especially
    transpositions that keep their relative position, rule out chaining and support positional coding (Henson 1998)
    [A].
  - Positional or context-signal models include Burgess & Hitch 1999 [A] and the primacy model (Page & Norris 1998)
    [M].
  - Competitive queuing selects the strongest of several items active in parallel and then suppresses it (Hurlstone,
    Hitch & Baddeley 2014) [A], with neural evidence in monkey PFC (Averbeck et al. 2002) [A].
  - Monkey PFC holds sequences in rank-specific subspaces (Xie et al. 2022) [A].

  Our model has a positional code (R² 0.80) but does not use it (≤ 1.4% of outputs follow it), and its fetch is
  content-addressed. That predicts **chaining-type** pointer errors, the opposite of the human pattern: jumps to an
  earlier occurrence of the same local context, which is the induction-head mechanism (Olsson et al. 2022) [A].
- **Where it breaks:** humans recall a *list*; our model reads an input stream already present in context. "Serial
  order" applies to how the model indexes that stream.
- **For the paper (only if E3 confirms it):** "Humans keep order by position (Henson 1998). The model has a positional
  code but follows content, so it loses its place as chaining models predict: it jumps to an earlier occurrence of the
  same context."
- **Measurement:** E3, using existing BRIDGE runs at $0.

### 2.F A one-item focus of attention

- **Verdict:** strong as a description of what the pin shows the model.
- **Mapping.**
  - Holding two running counts that must be updated alternately costs time at every switch, even after intensive
    practice. Garavan's (1998) interpretation is a focus of attention that holds just one count at a time [A].
  - Oberauer (2002) distinguishes three states of working memory: activated long-term memory, a capacity-limited region
    of direct access, and a focus of attention [A].
  - Capacity is about 4 chunks (Cowan 2001) [A].

  The pin *enforces* a focus of one: the (state, event) block. Π plays the part of activated long-term memory, and the
  history is evicted.
- **Where it breaks:** in humans the focus is a limitation; in the clock it is a design choice that removes
  interference.
- **For the paper:** "The pin gives the model what working-memory research calls a focus of attention holding a single
  item (Garavan 1998; Oberauer 2002). The program waits outside the focus and is fetched by content."

### 2.G Interference, not decay

- **Verdict:** usable with care.
- **Mapping.**
  - Short delays filled with articulatory suppression cause a large loss in serial recall, and longer delays add
    little, so time alone does not cause forgetting. An interference model fits best (Oberauer & Lewandowsky 2008)
    [A].
  - The classic finding that short-term forgetting builds up across trials through proactive interference is Keppel &
    Underwood 1962 [M; the content comes from standard knowledge].

  In plain decoding, attention to Π's matched destination falls about 17–19× along a run, attention to the run's own
  history doubles, and margins fall by 2.5–4.3 logits at 8k–12k events. That looks like proactive interference from
  the history. Eviction is a release from it.
- **Where it breaks:** a transformer has no time-based decay at all, so "interference rather than decay" is automatic
  here. The informative question is *which* history interferes (E2).
- **For the paper:** "Plain decoding forgets the way people do, by interference rather than decay (Oberauer &
  Lewandowsky 2008): its attention drifts from the program to its own history. Evicting the history after each step
  removes the source."

### 2.H Cognitive offloading and skilled memory

- **Verdict:** usable with care.
- **Mapping.**
  - Writing the state down is cognitive offloading: using physical action to reduce the processing a task demands
    (Risko & Gilbert 2016) [A].
  - With a retrieval structure, one person raised his digit span from 7 to 79 after more than 230 hours of practice
    (Ericsson, Chase & Faloon 1980) [A]: structure, not raw capacity.
- **Where it breaks:** offloading in humans is a metacognitive choice, and our clock imposes it. The REASON gate (open
  `<program>`) is the metacognitive part.
- **For the paper:** one clause at most, e.g. "the state is written down rather than held".

### 2.I The brain as an analogue–digital hybrid

- **Verdict:** strong as a framing for v1 and v2 together.
- **Mapping.**
  - Sarpeshkar (1998) argues that the most resource-efficient computation is neither analogue nor digital but a hybrid
    of the two, and that the brain is likely such a hybrid [A].
  - von Neumann (1956, §11.1) already asked whether the nervous system is digital. He noted that its digital (neural)
    operations alternate with analogue (humoral) ones, and that pulse density carries analogue quantities [F].

  v1's closure (analogue state, snapped each step) and v2's token snap are hybrid computation with discrete
  restoration.
- **Where it breaks:** Sarpeshkar's argument is about energy and precision; ours is about exactness over length.
- **For the paper:** "The closure and the pinned step are analogue computation with digital restoration, the hybrid
  that Sarpeshkar (1998) argued is most efficient and that von Neumann (1956) suspected the nervous system uses."

### 2.J Finite automata began as models of neurons

- **Verdict:** strong as a historical hook.
- **Mapping.** Kleene (1956) introduced regular events to characterise what McCulloch–Pitts nerve nets (1943) can
  respond to [A/M]. Asking whether a neural network implements a regular language robustly is the field's founding
  question, turned around.
- **For the paper:** "Regular languages were first defined for networks of model neurons (McCulloch & Pitts 1943;
  Kleene 1956)."

### 2.K Discrete symbols and mental programs

- **Verdict:** usable with care.
- **Mapping.** Dehaene et al. (2022) propose that human thought uses several internal "languages", each discretising a
  domain into a few symbols and composing them recursively into mental programs [A]. Our executor runs programs over
  discrete symbols, so the analogy is at the level of the computational thesis, not of mechanism.
- **Where it breaks:** their programs compress structure, through minimum description length. Ours are given as
  tables.

### Considered and rejected

- **Replay of place-cell sequences** (Foster & Wilson 2006) [A]: offline re-running of experience. We have nothing
  like it, so it would be decorative.
- **Grid cells as an analogue error-correcting code** (Sreenivasan & Fiete 2011) [A]: this is about correcting
  *analogue* variables with modular periodic codes. The only point of contact is "pick codewords far apart"
  (screening names). It is weaker than pattern separation for that point.
- **Spaun** (Eliasmith et al. 2012) [A]: a 2.5-million-neuron model doing eight tasks. Citing it adds breadth without
  a mapping.
- **Phonological-loop rehearsal:** blocking rehearsal did not change forgetting in Oberauer & Lewandowsky (2008) [A],
  so "rehearsal as regeneration" has weak support.

---

## 3. The TCS framing

### 3.1 What the pinned executor is, formally

- **The step.** Each tick computes δ(s, e). With the ARITH Mealy cells it also computes an output λ(s, e). The
  executor is therefore a deterministic finite-state transducer (Mealy 1955) [A]. Its input tape is one-way and
  read-only, and the clock streams it.
- **Bounded context means finite.** Schuurmans (2023) states the general fact: any deterministic language model that
  conditions on strings of bounded length is equivalent to a finite automaton [A].
  - This is why exhaustive checking is possible: the pin bounds what the model sees at a tick to Π plus one block, so
    the step function has a finite reachable domain.
  - It is also why the pinned executor is not universal on its own: it needs a writable tape.
- **Universality needs a writable tape.**
  - Tag systems (Post 1943 [M]) are universal: Minsky (1961) [A] and Cocke & Minsky (1964) [A] showed it.
  - Lag systems (Wang 1963) [M] are a variant of tag systems [F, as described by Schuurmans et al. 2024].
  - Schuurmans et al. (2024) let the decoder's own output act as the queue, with a sliding window. That gives a Lag
    system and hence universality. They verified 2,027 rules, one query each [F].
  - Schuurmans (2023) used an external associative read–write memory with Flan-U-PaLM 540B to simulate U₁₅,₂ [A].
  - Graves et al.'s (2014) Neural Turing Machine is the differentiable counterpart [A].
- **How to say it.** "The pinned executor is the finite-control half of a Turing machine, made exact. Universality
  needs only a writable tape, which Schuurmans et al. (2024) supplied with a sliding window."

### 3.2 Why one check per row suffices with the pin, and no finite test suffices without it

- **The negative side (Moore 1956, Theorem 2, p. 140).** For any machine S and any multiple experiment on S, there are
  distinguishable machines that give the same outcome [F, via the verbatim quotation in Fields 2013, arXiv:1201.3672].
  - Unpinned decoding is a machine whose state includes the whole history, so its states are unbounded.
  - `no_finite_test_suite` and `no_finite_check` are Moore's theorem for language-model decoders, sharpened: the
    decoder that fools the tests passes with strict margins and is exact up to any chosen N.
- **The positive side (Vasilevskii 1973; Chow 1978).** For any specification and any bound m on the implementation's
  number of states, there is a finite "m-complete" test suite: every implementation with at most m states passes it
  exactly when it conforms [A, via Vaandrager & Melse 2025, which also notes such suites grow exponentially in m − n].
  The general setting is surveyed by Lee & Yannakakis (1996) [M].
- **What the pin adds:**
  - (i) the state bound: the footprint equals the view, so there is no hidden state and m = n;
  - (ii) more than a reset, *state setting*: the clock can present any (s, e) block directly, so no transfer
    sequences are needed;
  - (iii) observability: the next state is written as a token.

  Under (i)–(iii), testing each reachable transition once determines the implementation. The complete suite is the
  transition cover, which is the per-row certificate. This is elementary and is our derivation. `pinned_regeneration_iff`
  (with `tick_logits_eq_row` and the code-path hypothesis) is its machine-checked form for the real LLM.
- **Link to learning automata.** Angluin's L\* learns a regular set from membership and equivalence queries [A]. Weiss,
  Goldberg & Yahav (2018) used it to extract automata from trained RNNs, with the RNN as an approximate oracle [A]. With
  the pin, the equivalence query becomes decidable by enumeration: the certificate *is* an exact equivalence query
  between the LLM-under-clock and the table.
- **Proof structure.** The induction inside `pinned_regeneration_iff` is the standard forward-simulation argument: a
  step relation that commutes with the specification's step implies trace equivalence (Lynch & Vaandrager 1995 [M]).
  The certificate discharges the commuting square by enumeration.
- **How to say it.** "Moore (1956) showed that no finite experiment identifies a machine whose state is unbounded. With
  a bound on the number of states, a finite test suffices (Vasilevskii 1973; Chow 1978). Plain decoding carries its
  whole history as state, so no finite test certifies it. The pinned clock removes the hidden state, sets each state
  directly and makes it observable. Under those conditions the complete test is one check per table row, and we prove
  that this check is necessary and sufficient at every length."

### 3.3 Where the certificate sits among verification ideas

| idea | what is checked | for which inputs | when | what must be trusted | cost of the check |
|---|---|---|---|---|---|
| verified compiler (Leroy 2009) [A] | the compiler, once | all programs, all inputs | before deployment | the proof assistant and the semantics | one large proof |
| translation validation (Pnueli et al. 1998 [M]; Necula 2000 [A]) | each compiled program against its source | all inputs of that program | after each compilation | the validator | per program |
| proof-carrying code (Necula 1997) [A] | a safety proof shipped with the code | all executions (safety only) | at load time | a small proof checker | cheap; independent of producing the proof |
| program checking (Blum & Kannan 1989/1995) [A; definition F via McConnell et al.] | one output on one input, using the program as an oracle | that input | at run time | the checker; probabilistic | must differ from (be cheaper than) recomputing |
| certifying algorithms (McConnell et al. 2011) [F] | a witness returned with each output | that input | at run time | a simple, ideally verified checker | small per output |
| runtime verification (Leucker & Schallhart 2009) [M] | the current run against a property | that run | during the run | the monitor | per event |
| conformance testing (Moore; Vasilevskii; Chow) [F/A] | an implementation against an FSM spec | all inputs, given a state bound | before deployment | the state bound | exponential in extra states |
| **pinned certificate (ours)** | each program's step function on the deployment host and code path | **all event sequences, any length** | once per (program, host, path) | the Lean theorem, the clock's footprint guarantee, bitwise reproducibility of the path | one forward pass per reachable row |

**Assessment against program checking and certifying algorithms (the brief's question).**

1. **The definitions** [F, as restated by McConnell et al. 2011 from Blum & Kannan]. A Blum–Kannan checker is a
   probabilistic oracle machine. If the program is correct on every input, the checker accepts with high probability.
   If the program is wrong on the given input, it rejects with high probability. A *certifying* algorithm returns a
   witness with each output, which a simple checker verifies, so that the user does not have to trust the algorithm
   (McConnell et al.).
2. **Our certificate covers more than a checker and trusts more.** A checker certifies one output. The pinned
   certificate covers every input of a program, but it assumes the clock's architectural guarantee and a fixed code
   path. A checker treats the program as a black box; Moore's theorem says that a black box cannot be certified for
   all inputs, and that is why we need the white-box footprint guarantee.
3. **The pinned trace is a witness, but a trivial one.** Each tick's (s, e, s′) can be checked against δ in O(1). That
   makes the executor "certifying" in McConnell's sense, but the checker could compute the answer itself, so run-time
   checking adds nothing once the certificate holds.
   - It is still worth running as *runtime verification of the certificate's hypotheses*. It catches code-path drift,
     such as BRIDGE's one-run disagreement between HF on an L4 and vLLM on an H100, or ARITH's non-bitwise one-token
     forward 2.
4. **Where real checking pays.**
   - **(a) The compile step** (question → table): certified does not mean correct (64–88 of 768). An N-version check
     fits here:
     - compile twice from independent prompts or samples;
     - minimise both automata (Myhill–Nerode) and test them for equivalence;
     - accept only on agreement.

     It would correctly accept the 11 of 82 renamed-state tables. Knight & Leveson (1986) warn that independently
     produced versions fail together more often than independence predicts [M], so measure the correlation (E10).
   - **(b) Arithmetic outputs.** A residue check on the 1,000-digit sum, modulo a few random primes, tests the answer
     against the *question*. It catches misquoted digits that the certificate cannot see. This is result checking in
     the Blum–Kannan sense. The specific residue checker is classical; we did not verify a citation for it, so use Blum,
     Luby & Rubinfeld (1993) [M] and Wasserman & Blum (1997) [A] for the framework.
5. **Theorem C is the decomposition result checking needs.** It bounds P(final answer wrong) by P(table wrong) +
   P(quote wrong) + P(glue wrong). The certificate sets the execution term to exactly 0, and (a) and (b) attack the
   remaining terms.

**How to say it.** "The certificate is translation validation for programs run by a language model. It checks each
program on its deployment path rather than the model, and covers every input of that program. Result checking in the
sense of Blum and Kannan still has a job: checking the table against the question, which the certificate does not
see."

### 3.4 Reliable computation from unreliable parts

- **von Neumann (1956)** [F]:
  - §7.2: in long chains, errors make the output irrelevant unless some control mechanism prevents their accumulation;
  - §9.2.2–9.2.3: the restoring organ, a majority organ that strengthens whichever state, firing or silent, already
    prevails in a bundle;
  - §11.2: a memory organ "remembers its mistakes" and a single error changes its state for good.
- **Pippenger (1988)** [A]: there is a maximum tolerable per-gate failure probability, strictly below 1/2, and
  tolerating failures requires deeper formulas.
- **Rabin (1963)** [F]: names the reliability motivation explicitly, and his isolated cut-point is the margin
  condition.
- **How we use it:** this lineage frames *why* the regeneration happens below the program. Do not borrow von Neumann's
  probability model: our errors are deterministic.

### 3.5 Draft TCS paragraph (about 150 words, in the paper's voice)

> We build on three results from automata theory. Turing (1936) bounded what a human computer observes at once and
> replaced the computer's state of mind with a written note, so that work proceeds one step per sitting. Our clock
> imposes exactly this on a language model. Moore (1956) showed that no finite experiment identifies a machine whose
> state is unbounded. Plain decoding carries its whole history as state, and we prove that no finite test certifies it.
> Given a bound on the states, finite tests suffice (Vasilevskii 1973; Chow 1978). The clock removes hidden state and
> makes the state observable, so one check per table row is complete, and we prove it necessary and sufficient at every
> length. The certificate is translation validation (Pnueli et al. 1998) for programs run by a model. Schuurmans et al.
> (2024) checked an LLM rule by rule. We give the condition under which such a check is exact.

---

## 4. Long-sequence tasks a general reader knows

| task | what people do (verified source) | as a transition table | demo value |
|---|---|---|---|
| **digit span** | about 7 items (Miller 1956, as summarised by Cowan 2001) [A]; about 4 chunks when chunking is blocked (Cowan 2001) [A]; 7 → 79 digits after 230+ hours with a mnemonic system (Ericsson et al. 1980) [A]; first measured by Jacobs (1887) [M] | none: span is storage, not state tracking | a contrast only: the executor's limit is not span |
| **n-back** (Kirchner 1958 [M]) | the standard working-memory updating load; we did not verify accuracy-against-n numbers | states = the last n items (\|Σ\|ⁿ); events = the next item; output = match or no match. 2-back over 8 letters: 64 states × 8 events = 512 rows | vivid: "2-back over 10,000 letters, exact, every tick checked" |
| **keep-track** (Yntema 1963 [A]; an "updating" task in Miyake et al. 2000 [A]) | operators tracking a changing situation do better with few variables with many states than many with few states (Yntema) | state = a tuple of category values; event = a category item. The table grows multiplicatively, so certify it per row | a good human-familiar program |
| **two running counts** (Garavan 1998 [A]) | every switch between counts costs time, even after practice | counters mod N | small, clear |
| **placekeeping in a procedure** (Altmann et al. 2014 [A]) | 2.8-s interruptions double sequence errors and leave other errors unchanged | pointer plus step | pairs with E5 |
| **mental arithmetic with carries** (Hitch 1978 [M]) | the carry is held in working memory; the content claim is from standard knowledge, so check it | the adder is a two-state Mealy machine over digit pairs (ARITH) | the arithmetic headline: 1,000-digit addition |
| **Tower of Hanoi** (Simon 1975 [M]; Altmann & Trafton 2002 [A]; Shojaee et al. 2025 [A]) | humans: classic goal-management task; LRMs collapse beyond a complexity and "fail to use explicit algorithms" (Shojaee et al.) | executing a given move list while tracking the pegs: the state is the configuration, 3ᵏ for k disks. Large tables, so use only small k | LLM-famous. Shojaee's results are contested (critiques exist, unverified here), so frame as "given the algorithm" |
| **serial sevens** (Folstein et al. 1975 [M]) | a clinical bedside test; the content is from standard knowledge | counter mod 100 with "−7" events | familiar but trivial |

**Recommendation.** For a general reader, use n-back and keep-track as "programs people know", run to 10,000 events and
certified. Use Tower-of-Hanoi execution as the LLM-famous case, framed narrowly: we execute a given move list exactly,
and we do not solve Hanoi. Do not compare against human numbers we have not verified.

---

## 5. Annotated list

Each entry gives the citation, a verified URL (accessed 2026-10-28), a tag, and 2–3 sentences. The full-text URLs
listed are the copies actually read.

### 5.1 Automata, computability, noise

1. **Turing, A. M. (1936/37). On computable numbers, with an application to the Entscheidungsproblem.** *Proc. London
   Math. Soc.* s2-42(1):230–265.
   - Links: https://doi.org/10.1112/plms/s2-42.1.230. Full text read at
     https://www.cs.ox.ac.uk/activities/ieg/e-library/sources/tp2-ie.pdf (original page numbers in braces). [F]
   - §9 analyses a human computer:
     - a bound B on the symbols observed at once (p. 250);
     - finitely many states of mind (p. 250), because with infinitely many, some would be so close as to be confused;
     - the state of mind replaced by a note of instructions. The computer works one step per sitting, and progress is
       the note plus the tape (pp. 253–254).
   - This is the pin's contract, stated in 1936.
2. **Kleene, S. C. (1956). Representation of events in nerve nets and finite automata.** In *Automata Studies*
   (AM-34), 3–42.
   - Link: https://doi.org/10.1515/9781400882618-002 [A]
   - Defines the events a finite automaton, or a McCulloch–Pitts net, can respond to: the origin of regular
     languages.
   - Historical hook: finite automata began as a theory of neural networks.
3. **McCulloch, W. S. & Pitts, W. (1943). A logical calculus of the ideas immanent in nervous activity.** *Bull. Math.
   Biophys.* 5(4):115–133.
   - Link: https://doi.org/10.1007/BF02478259 [M]
   - The model neurons whose nets Kleene characterised. Cite them together with Kleene.
4. **Mealy, G. H. (1955). A method for synthesizing sequential circuits.** *Bell Syst. Tech. J.* 34(5):1045–1079.
   - Link: https://doi.org/10.1002/j.1538-7305.1955.tb03788.x [A]
   - Sequential-circuit synthesis, building on Huffman and Moore. It is the source of "Mealy machine".
   - ARITH's two-cell rows (s,a,b)→t and (s,a,b,t)→o make a Mealy transducer.
5. **Moore, E. F. (1956). Gedanken-experiments on sequential machines.** In *Automata Studies* (AM-34), 129–154.
   - Link: https://doi.org/10.1515/9781400882618-006 [F for Theorem 2's wording, via Fields 2013; the original was not
     read]
   - Founds black-box experiments on finite machines. Theorem 2 (p. 140): any finite experiment is consistent with
     other, distinguishable machines.
   - This is the ancestor of `no_finite_test_suite`.
6. **Fields, C. (2013). Bell's theorem from Moore's theorem.** *Int. J. Gen. Syst.* 42:376–385; arXiv:1201.3672.
   - Link: https://arxiv.org/abs/1201.3672 [F]
   - Quotes Moore's Theorem 2 verbatim, with its page number. Used here only as the verifying source for that wording.
7. **Nerode, A. (1958). Linear automaton transformations.** *Proc. Amer. Math. Soc.* 9(4):541–544.
   - Link: https://doi.org/10.1090/S0002-9939-1958-0135681-9 [M]
   - The Nerode half of Myhill–Nerode. Myhill's 1957 WADC report is not online (§7).
8. **Rabin, M. O. & Scott, D. (1959). Finite automata and their decision problems.** *IBM J. Res. Dev.* 3(2):114–125.
   - Link: https://doi.org/10.1147/rd.32.0114 [M]
   - The standard reference for finite automata, nondeterminism and decision problems. Rabin (1963) says its own
     exposition follows this paper [F].
9. **Rabin, M. O. (1963). Probabilistic automata.** *Information and Control* 6(3):230–245.
   - Links: https://doi.org/10.1016/S0019-9958(63)90290-0. Full text (scan) read at
     https://perso.ens-lyon.fr/denis.kuperberg/CR18/probas.pdf [F]
   - Isolated cut-point δ ⇒ inequivalent words sit more than 2δ apart in L1 ⇒ packing ⇒ at most (1 + 1/δ)^(n−1)
     states (Theorem 3). Rabin motivates it by reliability and leaves stability open.
   - **The closest precedent for robust Myhill–Nerode. v1 must cite it.**
10. **Maass, W. & Orponen, P. (1998). On the effect of analog noise in discrete-time analog computations.** *Neural
    Computation* 10(5):1071–1095.
    - Link: https://doi.org/10.1162/089976698300017359 [A]
    - Arbitrarily small analogue noise reduces analogue computational models, including noisy neural nets, to the
      power of finite automata.
    - Already in the project's references (PRIMER). It frames why exactness over length must be finite-state.
11. **Maass, W. & Sontag, E. D. (1999). Analog neural nets with Gaussian or other common noise distributions cannot
    recognize arbitrary regular languages.** *Neural Computation* 11(3):771–782.
    - Link: https://doi.org/10.1162/089976699300016656 [A]
    - With noise that has broad support, many regular languages become unrecognisable.
    - This is why v1 reports rates at fixed length under unbounded noise (THEOREMS line 803 cites Maass–Sontag).
12. **Casey, M. (1996). The dynamics of discrete-time computation, with application to recurrent neural networks and
    finite state machine extraction.** *Neural Computation* 8(6):1135–1178.
    - Link: https://doi.org/10.1162/neco.1996.8.6.1135 [A]
    - An RNN that performs a finite-state computation must organise its state space to mimic the minimal DFA, and the
      paper describes the resulting attractor structure.
    - A direct antecedent of MECHANISM's "exact state = minimal automaton" finding.
13. **Omlin, C. W. & Giles, C. L. (1996). Constructing deterministic finite-state automata in recurrent neural
    networks.** *J. ACM* 43(6):937–972.
    - Link: https://doi.org/10.1145/235809.235811 [A]
    - Trained RNNs degrade on long strings because their internal DFA-state representations are unstable. Programmed
      second-order networks with large enough weights stay stable at any length.
    - This is v1's drift phenomenon, observed in 1996.
14. **Siegelmann, H. T. & Sontag, E. D. (1995). On the computational power of neural nets.** *J. Comput. Syst. Sci.*
    50(1):132–150.
    - Link: https://doi.org/10.1006/jcss.1995.1013 [M]
    - Recurrent nets with rational weights are Turing-universal: the noise-free, infinite-precision counterpoint to
      Maass–Orponen.
    - Cite the two together: precision is the resource, and noise removes it.
15. **Post, E. L. (1943). Formal reductions of the general combinatorial decision problem.** *Amer. J. Math.*
    65(2):197–215.
    - Link: https://doi.org/10.2307/2371809 [M]
    - Introduces tag systems (per Schuurmans et al. 2024 [F] and Minsky 1961 [A]). Cite it for the lineage only.
16. **Minsky, M. L. (1961). Recursive unsolvability of Post's problem of "Tag" and other topics in theory of Turing
    machines.** *Ann. Math.* 74(3):437–455.
    - Link: https://doi.org/10.2307/1970290 [A]
    - Tag systems realise the same computability as Turing machines.
17. **Cocke, J. & Minsky, M. (1964). Universality of tag systems with P = 2.** *J. ACM* 11(1):15–20.
    - Link: https://doi.org/10.1145/321203.321206 [A]
    - A direct simulation of Turing machines by 2-tag systems. Each string admits exactly one production, so the system
      runs like a machine.
18. **Wang, H. (1963). Tag systems and lag systems.** *Math. Ann.* 152(1):65–74.
    - Link: https://doi.org/10.1007/BF01343730 [M]
    - Introduces Lag systems, a variant of tag systems (per Schuurmans et al. 2024 [F]). It is the model behind the
      2024 universality result.
19. **Schuurmans, D. (2023). Memory augmented large language models are computationally universal.**
    arXiv:2301.04589.
    - Link: https://arxiv.org/abs/2301.04589 [A]
    - States that a deterministic LM conditioned on bounded-length strings is equivalent to a finite automaton. With an
      external associative read–write memory, Flan-U-PaLM 540B exactly simulates U₁₅,₂.
    - Use it for the bounded-view ⇒ finite fact.
20. **Schuurmans, D., Dai, H. & Zanini, F. (2024). Autoregressive large language models are computationally
    universal.** arXiv:2410.03170.
    - Links: https://arxiv.org/abs/2410.03170 [F]; HTML read at https://arxiv.org/html/2410.03170v1
    - A sliding-window decoder is a Lag system. A universal TM is simulated with 2,027 rules, and each rule was checked
      once on gemini-1.5-pro-001 under greedy decoding with a single system prompt.
    - The paper does not discuss code path, positions or numerical nondeterminism. **This is per-rule certification
      without the iff. See L1 for positioning.**
21. **Graves, A., Wayne, G. & Danihelka, I. (2014). Neural Turing machines.** arXiv:1410.5401.
    - Link: https://arxiv.org/abs/1410.5401 [A]
    - Neural networks coupled to an external memory by attention; the authors liken the system to a Turing machine or
      a von Neumann architecture.
    - Cite it if the paper mentions learned external memory.
22. **von Neumann, J. (1956). Probabilistic logics and the synthesis of reliable organisms from unreliable
    components.** In *Automata Studies* (AM-34), 43–98.
    - Links: https://doi.org/10.1515/9781400882618-003. Full text read in the IAS-hosted Caltech lecture notes,
      https://static.ias.edu/pitp/archive/2012files/Probabilistic_Logics.pdf [F]. Section numbers match; check page
      numbers against the 1956 chapter.
    - §7.2: errors accumulate unless controlled. §9.2: the restoring organ. §11.1: is the nervous system digital or
      analogue? §11.2: a memory organ perpetuates its mistakes.
23. **Pippenger, N. (1988). Reliable computation by formulas in the presence of noise.** *IEEE Trans. Inf. Theory*
    34(2):194–197.
    - Link: https://doi.org/10.1109/18.2628 [A]
    - The tolerable failure probability per gate is strictly below 1/2, and noise-tolerant formulas must be deeper.
    - The quantitative sequel to von Neumann. Optional.

### 5.2 Verification, testing, checking

24. **Pnueli, A., Siegel, M. & Singerman, E. (1998). Translation validation.** *TACAS 1998*, LNCS 1384, 151–166.
    - Link: https://doi.org/10.1007/BFb0054170 [M; the abstract sits behind Springer's login, and the concept is
      verified through Necula 2000's abstract]
    - Coins "translation validation": validate each compiler run instead of verifying the compiler.
    - Our certificate's closest TCS analogue.
25. **Necula, G. C. (2000). Translation validation for an optimizing compiler.** *PLDI 2000*, 83–94.
    - Link: https://doi.org/10.1145/349299.349314 [A]
    - Compares the intermediate form before and after each GCC pass and verifies that semantics is preserved.
    - Industrial evidence that per-instance validation scales.
26. **Leroy, X. (2009). Formal verification of a realistic compiler.** *Commun. ACM* 52(7):107–115.
    - Link: https://doi.org/10.1145/1538788.1538814 [A]
    - CompCert: the compiler itself is proved correct in Coq.
    - The analogue of a weights-level certificate (N\*), which INSIGHTS says Savant does not admit. Use it for the
      contrast.
27. **Necula, G. C. (1997). Proof-carrying code.** *POPL '97*, 106–119.
    - Link: https://doi.org/10.1145/263699.263712 [A]
    - The producer ships a safety proof, and the host validates it easily and quickly.
    - Our certificate lacks that asymmetry. One clause at most.
28. **Blum, M. & Kannan, S. (1989). Designing programs that check their work.** *STOC '89*, 86–97.
    - Link: https://doi.org/10.1145/73007.73015 [M]. Crossref misspells the second author as "S. Kanna".
    - The conference version. Cite the journal version.
29. **Blum, M. & Kannan, S. (1995). Designing programs that check their work.** *J. ACM* 42(1):269–291.
    - Link: https://doi.org/10.1145/200836.200880 [A]
    - Defines program checkers, which certify one output on one instance. It gives checkers for sorting, matrix rank
      and GCD, and characterises the checkable problems.
    - For us: the right tool for the compile step and for arithmetic outputs, not for the run.
30. **Blum, M., Luby, M. & Rubinfeld, R. (1993). Self-testing/correcting with applications to numerical problems.**
    *J. Comput. Syst. Sci.* 47(3):549–595.
    - Link: https://doi.org/10.1016/0022-0000(93)90044-W [M]. The self-correcting-addition example is verified through
      McConnell et al.'s summary [F].
    - The framework for checking arithmetic results with random self-reducibility.
31. **Wasserman, H. & Blum, M. (1997). Software reliability via run-time result-checking.** *J. ACM* 44(6):826–849.
    - Link: https://doi.org/10.1145/268999.269003 [A]
    - Reviews simple checkers and self-correctors, and argues for building them into software.
    - Supports the residue-check proposal for arithmetic.
32. **McConnell, R. M., Mehlhorn, K., Näher, S. & Schweitzer, P. (2011). Certifying algorithms.** *Comput. Sci. Rev.*
    5(2):119–161.
    - Links: https://doi.org/10.1016/j.cosrev.2010.09.009. Full text read at
      https://people.mpi-inf.mpg.de/~mehlhorn/ftp/CertifyingAlgorithms.pdf [F]
    - An algorithm that returns a witness with each output, checked by a simple checker, so that the user does not have
      to trust the algorithm. It contrasts this with Blum–Kannan, who check programs in their standard form.
    - Our pinned trace is a trivial witness (§3.3).
33. **Leucker, M. & Schallhart, C. (2009). A brief account of runtime verification.** *J. Log. Algebr. Program.*
    78(5):293–303.
    - Link: https://doi.org/10.1016/j.jlap.2008.08.004 [M]
    - The standard survey of runtime verification, which monitors a single execution against a property (definition
      from standard knowledge).
    - For us: monitoring the certificate's hypotheses (code path, host) during deployment.
34. **Vasilevskii, M. P. (1973). Failure diagnosis of automata.** *Cybernetics* 9(4):653–665. Crossref dates the
    English translation 1975.
    - Link: https://doi.org/10.1007/BF01068590 [M; the result is verified through Vaandrager & Melse]
    - Finite test suites that are complete for implementations with a bounded number of extra states (the W-method),
      independently of Chow.
35. **Chow, T. S. (1978). Testing software design modeled by finite-state machines.** *IEEE Trans. Softw. Eng.*
    SE-4(3):178–187.
    - Link: https://doi.org/10.1109/TSE.1978.231496 [M; the result is verified through Vaandrager & Melse]
    - The W-method. Chow argued that a state bound is reasonable once the design has been analysed: a white-box
      assumption.
    - For us, the clock *provides* that assumption by construction.
36. **Lee, D. & Yannakakis, M. (1996). Principles and methods of testing finite state machines: a survey.** *Proc.
    IEEE* 84(8):1090–1123.
    - Link: https://doi.org/10.1109/5.533956 [M]
    - The standard survey. It credits Moore with posing conformance testing.
    - Cite it once for the general setting.
37. **Vaandrager, F. & Melse, I. (2025). New fault domains for conformance testing of finite state machines.**
    arXiv:2410.19405. The authors list it as CONCUR 2025.
    - Link: https://arxiv.org/abs/2410.19405 [F]
    - A modern account of m-complete test suites. It notes that in black-box settings there is usually no sensible
      bound on the implementation's states, and that W-method suites grow exponentially in the extra states.
    - The best current citation for "finite tests need a state bound".
38. **Angluin, D. (1987). Learning regular sets from queries and counterexamples.** *Inf. Comput.* 75(2):87–106.
    - Link: https://doi.org/10.1016/0890-5401(87)90052-6 [A]
    - L\* learns a minimal DFA from membership and equivalence queries in polynomial time.
    - The pinned certificate is an exact equivalence query.
39. **Weiss, G., Goldberg, Y. & Yahav, E. (2018). Extracting automata from recurrent neural networks using queries and
    counterexamples.** *ICML 2018*; arXiv:1711.09576.
    - Link: https://arxiv.org/abs/1711.09576 [A]
    - Uses L\* with a trained RNN as the oracle to extract DFAs.
    - A precedent for treating a network as an automaton to be checked against.
40. **Lynch, N. & Vaandrager, F. (1995). Forward and backward simulations: I. Untimed systems.** *Inf. Comput.*
    121(2):214–233.
    - Link: https://doi.org/10.1006/inco.1995.1134 [M]
    - Simulation relations as proof techniques for trace inclusion (from standard knowledge).
    - The proof shape of `pinned_regeneration_iff`.
41. **Avizienis, A. (1985). The N-version approach to fault-tolerant software.** *IEEE Trans. Softw. Eng.*
    SE-11(12):1491–1501.
    - Link: https://doi.org/10.1109/TSE.1985.231893 [M]
    - Independent versions with voting. Supports the "compile twice, compare minimal automata" checker.
42. **Knight, J. C. & Leveson, N. G. (1986). An experimental evaluation of the assumption of independence in
    multiversion programming.** *IEEE Trans. Softw. Eng.* SE-12(1):96–109.
    - Link: https://doi.org/10.1109/TSE.1986.6312924 [M]
    - Independently written versions failed together more often than independence predicts (from standard knowledge;
      check before citing).
    - The caution for E10.
43. **Pagiamtzis, K. & Sheikholeslami, A. (2006). Content-addressable memory (CAM) circuits and architectures: a
    tutorial and survey.** *IEEE J. Solid-State Circuits* 41(3):712–727.
    - Link: https://doi.org/10.1109/JSSC.2005.864128 [A]
    - A CAM performs a lookup-table search in one clock cycle with dedicated comparison circuitry. It is the
      exact-match hardware meaning of "content-addressable".

### 5.3 Associative memory and attention

44. **Hopfield, J. J. (1982). Neural networks and physical systems with emergent collective computational
    abilities.** *PNAS* 79(8):2554–2558.
    - Link: https://doi.org/10.1073/pnas.79.8.2554 [A]
    - Content-addressable memory as a flow in phase space: an entire memory is retrieved from a large enough part of
      it.
    - The neural meaning of "content-addressable".
45. **Amit, D. J., Gutfreund, H. & Sompolinsky, H. (1985). Storing infinite numbers of patterns in a spin-glass model
    of neural networks.** *Phys. Rev. Lett.* 55(14):1530–1533.
    - Link: https://doi.org/10.1103/PhysRevLett.55.1530 [M]
    - The capacity analysis of the Hopfield model. The commonly quoted ~0.138d capacity is attributed by Ramsauer et
      al. to Crisanti, Amit & Gutfreund 1986 and Hertz et al. [F, in Ramsauer]; cite Ramsauer for the number.
46. **Ramsauer, H. et al. (2021). Hopfield networks is all you need.** arXiv:2008.02217. The ICLR 2021 venue was not
    re-verified here.
    - Link: https://arxiv.org/abs/2008.02217 [F]
    - The continuous modern-Hopfield update equals transformer attention. Retrieval after one update is exponentially
      accurate in a pattern's separation Δᵢ (Theorem 4), and similar patterns produce metastable averaged states.
    - The theoretical twin of our Lemma Q and of the near-duplicate-name failures.
47. **Krotov, D. & Hopfield, J. J. (2016). Dense associative memory for pattern recognition.** *NeurIPS 29*;
    arXiv:1606.01164.
    - Link: https://arxiv.org/abs/1606.01164 [A]
    - Associative memories that store many more patterns than neurons. Background for Ramsauer.
48. **Bricken, T. & Pehlevan, C. (2021). Attention approximates sparse distributed memory.** *NeurIPS 2021*;
    arXiv:2111.05498.
    - Link: https://arxiv.org/abs/2111.05498 [A]
    - Under certain data conditions, attention approximates Kanerva's biologically plausible SDM, and the conditions
      hold in GPT-2.
    - A second bridge from attention lookup to neural associative memory.
49. **Willshaw, D. J., Buneman, O. P. & Longuet-Higgins, H. C. (1969). Non-holographic associative memory.** *Nature*
    222(5197):960–962.
    - Link: https://doi.org/10.1038/222960a0 [M]
    - The classic binary associative (key → value) net. Cite it for "heteroassociative".
50. **Olsson, C. et al. (2022). In-context learning and induction heads.** arXiv:2209.11895.
    - Link: https://arxiv.org/abs/2209.11895 [A]
    - Induction heads complete [A][B]…[A] → [B]; the paper argues they underlie in-context learning.
    - "Recycled induction-like circuitry" should cite it. It also predicts the chaining-type pointer errors (E3).
51. **Whittington, J. C. R., Warren, J. & Behrens, T. E. J. (2022). Relating transformers to models and neural
    representations of the hippocampal formation.** *ICLR 2022*; arXiv:2112.04035.
    - Link: https://arxiv.org/abs/2112.04035 [A]
    - Transformers with recurrent position encodings reproduce place and grid cells.
    - Our "positional code present but unused" can be stated against this background.

### 5.4 Working memory, attractors, dynamics

52. **Compte, A., Brunel, N., Goldman-Rakic, P. S. & Wang, X.-J. (2000). Synaptic mechanisms and network dynamics
    underlying spatial working memory in a cortical network model.** *Cereb. Cortex* 10(9):910–923.
    - Link: https://doi.org/10.1093/cercor/10.9.910 [A]. Crossref lists only Compte; PubMed confirms all four authors.
    - The bump-attractor model of prefrontal spatial working memory. Storage is robust against random drift, and
      against distractors, only with help such as neuromodulation.
    - The diffusion model.
53. **Funahashi, S., Bruce, C. J. & Goldman-Rakic, P. S. (1989). Mnemonic coding of visual space in the monkey's
    dorsolateral prefrontal cortex.** *J. Neurophysiol.* 61(2):331–349.
    - Link: https://doi.org/10.1152/jn.1989.61.2.331 [M]
    - The oculomotor delayed-response task and its delay activity, which Compte's model reproduces.
54. **White, J. M., Sparks, D. L. & Stanford, T. R. (1994). Saccades to remembered target locations: an analysis of
    systematic and variable errors.** *Vision Res.* 34(1):79–92.
    - Link: https://doi.org/10.1016/0042-6989(94)90259-3 [A]
    - Variable error grows monotonically over delays of 0.4–5.6 s, while systematic error does not.
    - **Cite this, not Wimmer, for delay-dependent growth.**
55. **Ploner, C. J., Gaymard, B., Rivaud, S., Agid, Y. & Pierrot-Deseilligny, C. (1998). Temporal limits of spatial
    working memory in humans.** *Eur. J. Neurosci.* 10(2):794–797.
    - Link: https://doi.org/10.1046/j.1460-9568.1998.00101.x [A]
    - Over delays of 0.5–30 s, saccade errors peak near 20 s and then fall.
    - A limit on "random walk" claims.
56. **Wimmer, K., Nykamp, D. Q., Constantinidis, C. & Compte, A. (2014). Bump attractor dynamics in prefrontal cortex
    explains behavioral precision in spatial working memory.** *Nat. Neurosci.* 17(3):431–439.
    - Links: https://doi.org/10.1038/nn.3645. Accepted manuscript read at
      https://diposit.ub.edu/items/392c450b-c002-459e-ab9f-4a99cbfd5066 [F]
    - At a fixed 3-s delay, trial-by-trial delay firing predicts the direction of saccade error, consistent with a
      diffusing bump. Discrete-attractor and decaying-bump alternatives fit worse.
    - Cite it for the neural mechanism, not for delay dependence.
57. **Schneegans, S. & Bays, P. M. (2018). Drift in neural population activity causes working memory to deteriorate
    over time.** *J. Neurosci.* 38(21):4859–4869.
    - Link: https://doi.org/10.1523/JNEUROSCI.3440-17.2018 [A]
    - Delay-related loss of precision comes from drift in the encoded value, not from attenuated activity.
58. **Shin, H., Zou, Q. & Ma, W. J. (2017). The effects of delay duration on visual working memory for orientation.**
    *J. Vis.* 17(14):10.
    - Link: https://doi.org/10.1167/17.14.10 [A]
    - Delay effects are much weaker than set-size effects, depend on the analysis method, and appear in only a
      minority of subjects; the forgetting slope is at most 1.14°/s.
    - The honest caveat.
59. **Panichello, M. F., DePasquale, B., Pillow, J. W. & Buschman, T. J. (2019). Error-correcting dynamics in visual
    working memory.** *Nat. Commun.* 10:3366.
    - Link: https://doi.org/10.1038/s41467-019-11298-3 [A; the article number 3366 is from standard knowledge, and
      Crossref gives none]
    - Discrete attractors pull memories toward a few stable values, adding bias but reducing diffusion. They strengthen
      with load and adapt to context.
    - The best "diffusion versus discretisation" citation.
60. **Brody, C. D., Romo, R. & Kepecs, A. (2003). Basic mechanisms for graded persistent activity: discrete
    attractors, continuous attractors, and dynamic representations.** *Curr. Opin. Neurobiol.* 13(2):204–211.
    - Link: https://doi.org/10.1016/S0959-4388(03)00050-3 [A]
    - Explicitly compares the brain with computers' digital approximation of analogue quantities: the most robust way
      to hold a continuous parameter is to discretise it.
    - Our step analogy, stated by neuroscientists.
61. **Seung, H. S. (1996). How the brain keeps the eyes still.** *PNAS* 93(23):13339–13344.
    - Link: https://doi.org/10.1073/pnas.93.23.13339 [A]
    - The line-attractor hypothesis for the oculomotor integrator, which requires precisely tuned feedback.
62. **Koulakov, A. A., Raghavachari, S., Kepecs, A. & Lisman, J. E. (2002). Model for a robust neural integrator.**
    *Nat. Neurosci.* 5(8):775–782.
    - Link: https://doi.org/10.1038/nn893 [A]
    - Integrators otherwise need synaptic tuning better than 1%. Bistable units remove the need for fine tuning: the
      discrete fix for analogue drift.
63. **Goldman, M. S., Levine, J. H., Major, G., Tank, D. W. & Seung, H. S. (2003). Robust persistent neural activity
    in a model integrator with multiple hysteretic dendrites per neuron.** *Cereb. Cortex* 13(11):1185–1195.
    - Link: https://doi.org/10.1093/cercor/bhg095 [A]
    - Bistable dendritic compartments make fixation robust to mistuning while keeping firing nearly continuous in eye
      position.
64. **Inagaki, H. K., Fontolan, L., Romani, S. & Svoboda, K. (2019). Discrete attractor dynamics underlies persistent
    activity in the frontal cortex.** *Nature* 566(7743):212–217.
    - Link: https://doi.org/10.1038/s41586-019-0919-7 [A]
    - ALM delay activity moves toward discrete endpoints that are robust to transient optogenetic perturbation.
      Perturbations occasionally switch it to the other endpoint, and wrong actions follow.
    - The perturbation analogue of our flip thresholds.
65. **Khona, M. & Fiete, I. R. (2022). Attractor and integrator networks in the brain.** *Nat. Rev. Neurosci.*
    23(12):744–766.
    - Link: https://doi.org/10.1038/s41583-022-00642-0 [A]
    - Review covering persistent states, error correction and the trade-off between robustness and capacity. One
      citation for "attractors in the brain".
66. **Chaudhuri, R. & Fiete, I. (2016). Computational principles of memory.** *Nat. Neurosci.* 19(3):394–403.
    - Link: https://doi.org/10.1038/nn.4237 [A]
    - The requirements a memory system must meet, and problems it shares with computer science and information
      theory. Optional.
67. **Mongillo, G., Barak, O. & Tsodyks, M. (2008). Synaptic theory of working memory.** *Science*
    319(5869):1543–1546.
    - Link: https://doi.org/10.1126/science.1150769 [A]
    - Working memory held in calcium-mediated synaptic facilitation, refreshed by spiking at a low rate. The one
      regeneration-like element in the activity-silent story.
68. **Stokes, M. G. (2015). 'Activity-silent' working memory in prefrontal cortex: a dynamic coding framework.**
    *Trends Cogn. Sci.* 19(7):394–405.
    - Link: https://doi.org/10.1016/j.tics.2015.05.004 [A]
    - Persistent delay activity waxes and wanes with task relevance, and population states are highly dynamic.
    - Background only, if the paper keeps any of the activity-silent framing.
69. **Wolff, M. J., Jochim, J., Akyürek, E. G. & Stokes, M. G. (2017). Dynamic hidden states underlying
    working-memory-guided behavior.** *Nat. Neurosci.* 20(6):864–871.
    - Link: https://doi.org/10.1038/nn.4546 [A]
    - "Pinging" the brain decodes hidden memory states with no delay activity, and an instruction to forget one item
      wipes its trace.
70. **Rose, N. S. et al. (2016). Reactivation of latent working memories with transcranial magnetic stimulation.**
    *Science* 354(6316):1136–1139.
    - Link: https://doi.org/10.1126/science.aah7011 [A]
    - A nonspecific pulse reactivates a dormant memory state.
71. **Lundqvist, M., Herman, P. & Miller, E. K. (2018). Working memory: delay activity, yes! Persistent activity? Maybe
    not.** *J. Neurosci.* 38(32):7013–7019.
    - Link: https://doi.org/10.1523/JNEUROSCI.2485-17.2018 [A]
    - One side of the debate: on single trials, spiking comes in sparse bursts.
72. **Constantinidis, C. et al. (2018). Persistent spiking activity underlies working memory.** *J. Neurosci.*
    38(32):7020–7028.
    - Link: https://doi.org/10.1523/JNEUROSCI.2486-17.2018 [A]
    - The other side of the debate. Cite the pair if the paper mentions the controversy at all.
73. **Barak, O. & Tsodyks, M. (2014). Working models of working memory.** *Curr. Opin. Neurobiol.* 25:20–24.
    - Link: https://doi.org/10.1016/j.conb.2013.10.008 [A]
    - Short review of the mechanisms: synaptic facilitation, tuned recurrence, intrinsic dynamics.
74. **Sussillo, D. & Barak, O. (2013). Opening the black box: low-dimensional dynamics in high-dimensional recurrent
    neural networks.** *Neural Computation* 25(3):626–649.
    - Link: https://doi.org/10.1162/NECO_a_00409 [A]
    - Finds the fixed and slow points of trained RNNs, including a 3-bit flip-flop, which is discrete memory.
    - The method language for our decision cells.
75. **Vyas, S., Golub, M. D., Sussillo, D. & Shenoy, K. V. (2020). Computation through neural population dynamics.**
    *Annu. Rev. Neurosci.* 43:249–275.
    - Link: https://doi.org/10.1146/annurev-neuro-092619-094115 [A]
    - The framework named in the brief. Our pinned step is deliberately *not* a dynamical computation across steps,
      which is a useful contrast.
76. **Sarpeshkar, R. (1998). Analog versus digital: extrapolating from electronics to neurobiology.** *Neural
    Computation* 10(7):1601–1638.
    - Link: https://doi.org/10.1162/089976698300017052 [A]
    - The most efficient computation is a hybrid of analogue and digital, and the brain likely computes this way.
77. **Burak, Y. & Fiete, I. R. (2009). Accurate path integration in continuous attractor network models of grid
    cells.** *PLoS Comput. Biol.* 5(2):e1000291.
    - Link: https://doi.org/10.1371/journal.pcbi.1000291 [A]
    - Errors accumulate as velocity is integrated, and prior models needed frequent resets from external cues.
      Continuous-attractor models integrate accurately for about 10–100 m or 1–10 min.
78. **Hardcastle, K., Ganguli, S. & Giocomo, L. M. (2015). Environmental boundaries as an error correction mechanism
    for grid cells.** *Neuron* 86(3):827–839.
    - Link: https://doi.org/10.1016/j.neuron.2015.03.039 [A]
    - Grid error grows with time and distance since the last boundary encounter and is corrected at boundaries.
    - The landmark analogue for the clock's pointer.
79. **Sreenivasan, S. & Fiete, I. (2011). Grid cells generate an analog error-correcting code for singularly precise
    neural computation.** *Nat. Neurosci.* 14(10):1330–1337.
    - Link: https://doi.org/10.1038/nn.2901 [A]
    - The grid code is an error-correcting code for analogue variables with unprecedented robustness to noise.
    - Considered and rejected as a main analogy (§2).
80. **Lisman, J. E. & Idiart, M. A. P. (1995). Storage of 7 ± 2 short-term memories in oscillatory subcycles.**
    *Science* 267(5203):1512–1515.
    - Link: https://doi.org/10.1126/science.7878473 [A]
    - Several memories held at once, one per ~40 Hz subcycle of a 5–12 Hz oscillation.
    - Why the theta–gamma analogy fails for a one-item pin.
81. **Lisman, J. E. & Jensen, O. (2013). The theta–gamma neural code.** *Neuron* 77(6):1002–1016.
    - Link: https://doi.org/10.1016/j.neuron.2013.03.007 [A]
    - Review of the hypothesis that dual oscillations code several ordered items.
82. **Rizzuto, D. S. et al. (2003). Reset of human neocortical oscillations during a working memory task.** *PNAS*
    100(13):7931–7936.
    - Link: https://doi.org/10.1073/pnas.0732061100 [A]
    - Stimulus events reset the phase of 7–16 Hz oscillations. This is the only theta-side fact that touches "fixed
      positions each tick", and it is too weak to use.

### 5.5 Gating, hippocampus, reuse

83. **Frank, M. J., Loughry, B. & O'Reilly, R. C. (2001). Interactions between frontal cortex and basal ganglia in
    working memory: a computational model.** *Cogn. Affect. Behav. Neurosci.* 1(2):137–160.
    - Link: https://doi.org/10.3758/CABN.1.2.137 [A]
    - Frontal cortex maintains robustly, while the basal ganglia gate selective updates by disinhibiting frontal
      cortex.
    - The cleanest citation for "the clock is a gate".
84. **O'Reilly, R. C. & Frank, M. J. (2006). Making working memory work: a computational model of learning in the
    prefrontal cortex and basal ganglia.** *Neural Computation* 18(2):283–328.
    - Link: https://doi.org/10.1162/089976606775093909 [A]
    - PBWM: an actor-critic system *learns* the gating of working-memory updates.
    - Use it for the contrast with our fixed gate.
85. **Hochreiter, S. & Schmidhuber, J. (1997). Long short-term memory.** *Neural Computation* 9(8):1735–1780.
    - Link: https://doi.org/10.1162/neco.1997.9.8.1735 [A]
    - The gated memory cell. Optional, as the ML counterpart of working-memory gating.
86. **Marr, D. (1971). Simple memory: a theory for archicortex.** *Phil. Trans. R. Soc. B* 262(841):23–81.
    - Link: https://doi.org/10.1098/rstb.1971.0078 [A]
    - Recall provoked from little information about a stored event: the origin of the pattern-completion idea.
87. **Treves, A. & Rolls, E. T. (1994). Computational analysis of the role of the hippocampus in memory.**
    *Hippocampus* 4(3):374–391.
    - Link: https://doi.org/10.1002/hipo.450040319 [A]
    - Quantitative theory of the hippocampus as an intermediate-term buffer for episodes.
88. **Nakazawa, K. et al. (2002). Requirement for hippocampal CA3 NMDA receptors in associative memory recall.**
    *Science* 297(5579):211–218.
    - Link: https://doi.org/10.1126/science.1071795 [A]
    - Without CA3 NMDA receptors, mice recall normally from full cues but not from partial ones: evidence for pattern
      completion.
    - Shows why "completion" is the wrong word for our full-key lookup.
89. **Leutgeb, J. K., Leutgeb, S., Moser, M.-B. & Moser, E. I. (2007). Pattern separation in the dentate gyrus and CA3
    of the hippocampus.** *Science* 315(5814):961–966.
    - Link: https://doi.org/10.1126/science.1135801 [A]
    - Small changes in the environment decorrelate dentate activity. Pattern separation is the mechanism that keeps
      similar memories apart.
90. **Yassa, M. A. & Stark, C. E. L. (2011). Pattern separation in the hippocampus.** *Trends Neurosci.*
    34(10):515–525.
    - Link: https://doi.org/10.1016/j.tins.2011.06.006 [A]
    - Review of the evidence. Cite it with Leutgeb for "near-duplicate keys interfere unless separated".
91. **Dehaene, S. & Cohen, L. (2007). Cultural recycling of cortical maps.** *Neuron* 56(2):384–398.
    - Link: https://doi.org/10.1016/j.neuron.2007.10.004 [A]
    - Cultural inventions such as reading and arithmetic invade older circuits and inherit their structural
      constraints.
    - Our "inherited constraints": Π must sit adjacent to the block, and the tokenizer's fragments make the weakest
      names.
92. **Dehaene, S. et al. (2010). How learning to read changes the cortical networks for vision and language.**
    *Science* 330(6009):1359–1364.
    - Link: https://doi.org/10.1126/science.1194140 [A, the editor's summary]
    - Literacy creates a word-specific area and comes at a cost to face processing nearby.
    - The precise "cost of recycling" parallel to our NLL cost.
93. **Anderson, M. L. (2010). Neural reuse: a fundamental organizational principle of the brain.** *Behav. Brain Sci.*
    33(4):245–266.
    - Link: https://doi.org/10.1017/S0140525X10000853 [A]
    - Circuits are reused for new purposes, often without losing their original function and with little local
      change.
    - Matches the soft-prompt result (WikiText logits bitwise unchanged).
94. **Gould, S. J. & Vrba, E. S. (1982). Exaptation: a missing term in the science of form.** *Paleobiology*
    8(1):4–15.
    - Link: https://doi.org/10.1017/S0094837300004310 [A]
    - Features now useful that were not built by selection for that role. The evolutionary word for the executor.

### 5.6 Serial order, focus, placekeeping, programs

95. **Henson, R. N. A. (1998). Short-term memory for serial order: the start-end model.** *Cogn. Psychol.*
    36(2):73–137.
    - Link: https://doi.org/10.1006/cogp.1998.0685 [A]
    - Error patterns in serial recall refute chaining and support positional theories. The key reference for E3.
96. **Burgess, N. & Hitch, G. J. (1999). Memory for serial order: a network model of the phonological loop and its
    timing.** *Psychol. Rev.* 106(3):551–581.
    - Link: https://doi.org/10.1037/0033-295X.106.3.551 [A]
    - A timing (context) signal is re-run at recall, items compete, and the selected item then receives decaying
      inhibition.
    - The model whose context signal the clock supplies externally.
97. **Page, M. P. A. & Norris, D. (1998). The primacy model: a new model of immediate serial recall.** *Psychol. Rev.*
    105(4):761–781.
    - Link: https://doi.org/10.1037/0033-295X.105.4.761-781 [M]
    - Order coded by a primacy gradient plus competitive queuing (content from standard knowledge).
98. **Hurlstone, M. J., Hitch, G. J. & Baddeley, A. D. (2014). Memory for serial order across domains.** *Psychol.
    Bull.* 140(2):339–373.
    - Link: https://doi.org/10.1037/a0034221 [A]
    - Competitive queuing (items active in parallel, the strongest chosen) across the verbal, visual and spatial
      domains. The best review to cite.
99. **Botvinick, M. M. & Plaut, D. C. (2006). Short-term memory for serial order: a recurrent neural network model.**
    *Psychol. Rev.* 113(2):201–233.
    - Link: https://doi.org/10.1037/0033-295X.113.2.201 [A]
    - An RNN account of serial recall that holds order in sustained activity rather than item–context associations.
    - Optional bridge to sequence models.
100. **Averbeck, B. B., Chafee, M. V., Crowe, D. A. & Georgopoulos, A. P. (2002). Parallel processing of serial
     movements in prefrontal cortex.** *PNAS* 99(20):13172–13177.
     - Link: https://doi.org/10.1073/pnas.162485599 [A]
     - Before a drawn sequence begins, PFC represents all its segments, ranked by serial position, and errors follow
       near-ties.
     - Neural competitive queuing, and Lashley's problem of serial order.
101. **Xie, Y. et al. (2022). Geometry of sequence working memory in macaque prefrontal cortex.** *Science*
     375(6581):632–639.
     - Link: https://doi.org/10.1126/science.abm0204 [A]
     - The PFC delay state decomposes into rank-specific subspaces. A real positional code, the counterpart of our
       unused one.
102. **Howard, M. W. & Kahana, M. J. (2002). A distributed representation of temporal context.** *J. Math. Psychol.*
     46(3):269–299.
     - Link: https://doi.org/10.1006/jmps.2001.1388 [M]
     - The temporal context model, in which a drifting context codes order (content from standard knowledge).
       Optional.
103. **Altmann, E. M., Trafton, J. G. & Hambrick, D. Z. (2014). Momentary interruptions can derail the train of
     thought.** *J. Exp. Psychol. Gen.* 143(1):215–226.
     - Link: https://doi.org/10.1037/a0030986 [A]
     - Interruptions of 2.8 s double sequence errors and 4.4 s interruptions triple them, while nonsequence errors are
       unaffected.
     - The human version of our pointer/step dissociation.
104. **Altmann, E. M. & Trafton, J. G. (2002). Memory for goals: an activation-based model.** *Cogn. Sci.*
     26(1):39–83.
     - Link: https://doi.org/10.1207/s15516709cog2601_2 [A]
     - Goal memory with interference from old goals, fitted to the Tower of Hanoi. An interference account of losing
       one's place.
105. **Garavan, H. (1998). Serial attention within working memory.** *Mem. Cognit.* 26(2):263–276.
     - Link: https://doi.org/10.3758/BF03201138 [A]
     - Two running counts; switching costs persist after practice, and the focus of attention holds one count.
106. **Oberauer, K. (2002). Access to information in working memory: exploring the focus of attention.** *J. Exp.
     Psychol. Learn. Mem. Cogn.* 28(3):411–421.
     - Link: https://doi.org/10.1037/0278-7393.28.3.411 [A]
     - Three states of working-memory representations: activated long-term memory, a region of direct access, and a
       focus of attention.
     - Maps onto Π, the block and the evicted history.
107. **Cowan, N. (2001). The magical number 4 in short-term memory.** *Behav. Brain Sci.* 24(1):87–114.
     - Link: https://doi.org/10.1017/S0140525X01003922 [A]
     - Capacity is 3–5 chunks when chunking is blocked. It also restates Miller's ~7.
108. **Miller, G. A. (1956). The magical number seven, plus or minus two.** *Psychol. Rev.* 63(2):81–97.
     - Link: https://doi.org/10.1037/h0043158 [M; content via Cowan 2001's abstract]
     - The general reader's "7 ± 2".
109. **Oberauer, K. & Lewandowsky, S. (2008). Forgetting in immediate serial recall: decay, temporal distinctiveness,
     or interference?** *Psychol. Rev.* 115(3):544–576.
     - Link: https://doi.org/10.1037/0033-295X.115.3.544 [A]
     - Filled delays impair recall, lengthening them adds little, and an interference model fits best.
     - Use it for "interference, not decay".
110. **Keppel, G. & Underwood, B. J. (1962). Proactive inhibition in short-term retention of single items.** *J. Verbal
     Learn. Verbal Behav.* 1(3):153–161.
     - Link: https://doi.org/10.1016/S0022-5371(62)80023-1 [M]
     - Classic evidence that short-term forgetting builds up across trials through proactive interference (content
       from standard knowledge; check it).
111. **Zylberberg, A., Dehaene, S., Roelfsema, P. R. & Sigman, M. (2011). The human Turing machine: a neural framework
     for mental programs.** *Trends Cogn. Sci.* 15(7):293–300.
     - Link: https://doi.org/10.1016/j.tics.2011.05.007 [A]
     - Mental programs as a hybrid: parallel steps feed a serial production system selected by competing accumulators.
     - **The best single neuroscience citation for the pinned executor.**
112. **Zylberberg, A., Fernández Slezak, D., Roelfsema, P. R., Dehaene, S. & Sigman, M. (2010). The brain's router: a
     cortical network model of serial processing in the primate brain.** *PLoS Comput. Biol.* 6(4):e1000765.
     - Link: https://doi.org/10.1371/journal.pcbi.1000765 [A]
     - A spiking implementation that chains processors serially at 100–500 ms per step.
113. **Anderson, J. R. et al. (2004). An integrated theory of the mind.** *Psychol. Rev.* 111(4):1036–1060.
     - Link: https://doi.org/10.1037/0033-295X.111.4.1036 [A]
     - ACT-R: modules write chunks into buffers, and a single production fires per cycle on the buffer pattern.
     - Productions are condition–action rules, a cognitive transition table.
114. **Sigman, M. & Dehaene, S. (2005). Parsing a cognitive task: a characterization of the mind's bottleneck.** *PLoS
     Biol.* 3(2):e37.
     - Link: https://doi.org/10.1371/journal.pbio.0030037 [A]
     - The central decision stage is a serial bottleneck. Optional.
115. **Dehaene, S., Al Roumi, F., Lakretz, Y., Planton, S. & Sablé-Meyer, M. (2022). Symbols and mental programs: a
     hypothesis about human singularity.** *Trends Cogn. Sci.* 26(9):751–766.
     - Link: https://doi.org/10.1016/j.tics.2022.06.010 [A]
     - Human thought uses discrete symbols composed recursively into mental programs. Optional framing.
116. **Eliasmith, C. et al. (2012). A large-scale model of the functioning brain.** *Science* 338(6111):1202–1205.
     - Link: https://doi.org/10.1126/science.1225266 [A]
     - Spaun, a 2.5-million-neuron model doing eight tasks. Considered and not recommended.
117. **Gallistel, C. R. & King, A. P. (2009). *Memory and the Computational Brain*.** Wiley-Blackwell.
     - Link: https://doi.org/10.1002/9781444310498 [M; only the table of contents was verified]
     - Argues, from computer science, for symbolic read–write memory in brains (thesis from standard knowledge;
       check it). Relevant to "the clock supplies the tape".
118. **Risko, E. F. & Gilbert, S. J. (2016). Cognitive offloading.** *Trends Cogn. Sci.* 20(9):676–688.
     - Link: https://doi.org/10.1016/j.tics.2016.07.002 [A]
     - Using physical action to reduce the processing a task demands. "The state is written down."
119. **Ericsson, K. A., Chase, W. G. & Faloon, S. (1980). Acquisition of a memory skill.** *Science*
     208(4448):1181–1182.
     - Link: https://doi.org/10.1126/science.7375930 [A]
     - Digit span rose from 7 to 79 with practice and a mnemonic system. Structure beats capacity.
120. **Foster, D. J. & Wilson, M. A. (2006). Reverse replay of behavioural sequences in hippocampal place cells during
     the awake state.** *Nature* 440(7084):680–683.
     - Link: https://doi.org/10.1038/nature04587 [A]
     - Awake reverse replay. Considered and rejected as an analogy.

### 5.7 Tasks

121. **Jacobs, J. (1887). Experiments on "prehension".** *Mind* os-12(45):75–79.
     - Link: https://doi.org/10.1093/mind/os-12.45.75 [M]
     - The early digit-span experiments (attribution from standard knowledge).
122. **Kirchner, W. K. (1958). Age differences in short-term retention of rapidly changing information.** *J. Exp.
     Psychol.* 55(4):352–358.
     - Link: https://doi.org/10.1037/h0043688 [M]
     - Commonly credited with introducing the n-back task (attribution from standard knowledge).
123. **Yntema, D. B. (1963). Keeping track of several things at once.** *Hum. Factors* 5(1):7–17.
     - Link: https://doi.org/10.1177/001872086300500102 [A]
     - The keep-track paradigm and design rules for tracking a changing situation.
124. **Miyake, A. et al. (2000). The unity and diversity of executive functions.** *Cogn. Psychol.* 41(1):49–100.
     - Link: https://doi.org/10.1006/cogp.1999.0734 [A]
     - "Updating" is a separable executive function. The paper also uses the Tower of Hanoi.
125. **Hitch, G. J. (1978). The role of short-term working memory in mental arithmetic.** *Cogn. Psychol.*
     10(3):302–323.
     - Link: https://doi.org/10.1016/0010-0285(78)90002-6 [M]
     - Mental multi-digit arithmetic depends on holding intermediate results, including carries, in working memory
       (content from standard knowledge; check it).
126. **Simon, H. A. (1975). The functional equivalence of problem solving skills.** *Cogn. Psychol.* 7(2):268–288.
     - Link: https://doi.org/10.1016/0010-0285(75)90012-2 [M]
     - Classic Tower-of-Hanoi strategies.
127. **Shojaee, P. et al. (2025). The illusion of thinking: understanding the strengths and limitations of reasoning
     models via the lens of problem complexity.** arXiv:2506.06941.
     - Link: https://arxiv.org/abs/2506.06941 [A]
     - Reasoning models collapse beyond a complexity threshold on puzzles, including Hanoi, and fail to use explicit
       algorithms.
     - The LLM-famous foil. Its methodology has been publicly criticised (not verified here).
128. **Folstein, M. F., Folstein, S. E. & McHugh, P. R. (1975). "Mini-mental state".** *J. Psychiatr. Res.*
     12(3):189–198.
     - Link: https://doi.org/10.1016/0022-3956(75)90026-6 [M]
     - The clinical exam that includes serial sevens (content from standard knowledge).

---

## 6. Ideas: making the cross-field paragraph insightful rather than decorative

**Principle.** Use an analogy only where we measure the same quantity as the other field does. Each experiment below
turns an analogy into that kind of measurement. Most of them reuse BRIDGE, CIRCUITS or PROMPTBOX data at $0; the rest
are small.

**E1. The 1956 framing.**
- **The sentence:** "*Automata Studies* (1956) contains von Neumann's restoring organ, Kleene's regular events for
  nerve nets and Moore's gedanken-experiments. Our blindness theorem, robust finite state and theorem pair are their
  descendants for learned networks."
- **Cost:** no measurement. The sentence is accurate and memorable.

**E2. Diffusion, attractor or interference? (working-memory data versus plain decoding)**
- **Method.** Under plain decoding with events supplied, take the step's decision coordinate along a run: the
  write-position residual projected on the certified row's code direction, or simply the step margin. Fit its
  deviation against:
  - (a) step index (diffusion: variance ∝ t, as for a bump);
  - (b) saturation (a discrete attractor);
  - (c) the count of *similar* history tokens, meaning earlier blocks with the same state or event names
    (interference).
- **Prediction.** (c), given that attention moves 17–19× toward the history. Pinned decoding is identically zero.
- **Cost.** BRIDGE Part 1 margins exist, so $0 for (a)–(b) and a probe job for (c).
- **What it buys.** One sentence that is a measurement: "Plain decoding forgets by interference, not by drift."

**E3. Error taxonomy for the pointer (serial-order theory).**
- **Method.** For each misread event (19 in M6; 94 + 80 in Part 1), classify the jump target as:
  - local (±k positions);
  - an earlier occurrence of the same k-gram of events, which is the chaining/induction signature;
  - unexplained.
- **Prediction.** Chaining, unlike humans (Henson 1998): the positional code is unused (≤ 1.4%) and the fetch is
  content-addressed.
- **Cost.** $0, from the existing runs.
- **What it buys.** It would be the first time a classic psychology diagnostic (chaining versus positional) classifies
  an LLM failure.

**E4. Landmarks (grid-cell error correction).**
- **Method.** Insert a position landmark every k events, either an index token or a section break. Plot P(first
  misread) against distance since the last landmark.
- **Prediction.** A sawtooth, as with grid error after a boundary (Hardcastle et al. 2015). Plain decoding should
  improve as k shrinks, and k = 1 is the clock's pointer.
- **Cost.** A few GPU-hours.

**E5. An interruption (placekeeping).**
- **Method.** Insert irrelevant text mid-run in plain decoding.
- **Prediction.** As in Altmann et al. (2014), pointer errors rise and step errors do not. Pinned decoding is immune.
- **Cost.** Small.

**E6. The perturbation–switch curve (discrete attractors).**
- **Method.** Plot P(tick flips) against perturbation norm, for aimed and random directions, from CIRCUITS §6 and
  BRIDGE kicks.
- **What to state.** The shape (flat, then a sharp switch at 1.5–3× the residual norm) is the computational analogue
  of Inagaki et al.'s endpoint robustness with occasional switching.
- **Cost.** $0 if the data exist.

**E7. Committee redundancy (von Neumann multiplexing).**
- **Method.** Ablate k random heads of the ~30-head lookup committee and plot certified rows against k.
- **Interpretation.** A plateau followed by a cliff means multiplexing-like redundancy, and von Neumann's restoring
  analogy becomes literal. Early degradation means the restoration is the argmax quantisation alone.
- **Cost.** Cheap.

**E8. Separation predicts the weakest rows (modern Hopfield).**
- **Method.** For each name, compute Ramsauer's separation Δ from its key vectors in the deployed heads, or from the
  logit gap of the matched row against the nearest competitor. Correlate it with the row margin.
- **What it buys.** Lemma Q's "separation > leakage" becomes Ramsauer's Δ, and "screen the name pool" becomes pattern
  separation.
- **Cost.** $0 (CIRCUITS margins plus one forward pass per name pair).

**E9. Moore in the wild.**
- **Method.** Present, next to `no_finite_test_suite`, one concrete plain-decoding model that passes every row at
  length ≤ 2,048 and fails at 8,192. BRIDGE has the runs.
- **What it buys.** The theorem gets a picture.

**E10. A checker for the compile step (Blum–Kannan / N-version).**
- **Method.** Compile each gate question twice from independent samples, minimise both tables, and test them for
  equivalence. Measure:
  - the detection rate on the 64–88 certified-but-wrong answers;
  - the false-alarm rate;
  - the failure correlation that Knight & Leveson warn about.
- **What it buys.** It closes the gap between "certified" and "correct" with a checker that has a name.
- **Cost.** Small.

**E11. A result checker for the arithmetic headline.**
- **Method.** Add a mod-p residue check, for a few random primes p, on every 1,000-digit output.
- **What it catches.** Any misquoted digit, with high probability, independently of the table.
- **What it buys.** The arithmetic demo then has two guarantees: the execution is certified, and each result is
  checked against the question.

**E12. Human-familiar programs in the demo.**
- **Method.** Run n-back (2-back, 8 letters, 512 rows) and keep-track (4 categories) as certified tables over 10,000
  events.
- **What it buys.** A general reader knows these as working-memory tests that people find hard after a few items.
- **What to avoid.** Do not quote human accuracy numbers unless verified.

**Draft neuroscience paragraph (about 140 words).**

> The two ways plain decoding fails have counterparts in human and animal memory. People keeping their place in a
> procedure make sequence errors and step errors separately, and a brief interruption doubles only the former (Altmann
> et al. 2014). Plain decoding loses its place first, the way path integration drifts between landmarks (Hardcastle et
> al. 2015). The clock is a landmark at every step. The step itself faces the trade-off cortex faces. A continuous code
> drifts (Compte et al. 2000), while discrete attractors survive transient perturbation (Inagaki et al. 2019; Brody et
> al. 2003). The pinned step is the discrete end: its decision cells flip only when noise reaches 1.5–3 times the
> residual norm. The architecture as a whole is what Zylberberg et al. (2011) proposed for mental programs: a parallel
> step feeding a serial production cycle. The difference is that each of our steps can be checked.

Use this paragraph only after E3, E4 or E5 lands; until then, keep the claims to what we have measured.

---

## 7. Items not verified, or verified only in part

**Not found online:**
- Myhill (1957), "Finite automata and the representation of events", WADC Technical Report 57-624. Cite Nerode 1958
  and Rabin & Scott 1959 instead.
- A textbook source for the "static discipline" and noise margins of digital logic, e.g. Agarwal & Lang (2005),
  *Foundations of Analog and Digital Electronic Circuits*. Not checked; verify before citing.
- Lashley (1951), "The problem of serial order in behavior" (a book chapter). Averbeck et al. 2002 [A] summarise
  Lashley's hypothesis and can stand in.
- A citation for residue (mod-p) checking of arithmetic as a result checker. Use BLR 1993 and Wasserman & Blum 1997
  for the framework.
- The ICLR 2021 venue for Ramsauer et al., the article number 3366 for Panichello et al., and the published CONCUR
  2025 version of Vaandrager & Melse. Confirm these before final references.

**Metadata verified, content not checked against the source (check before use):**
- Pnueli et al. 1998: the abstract is behind Springer's login.
- Chow 1978 and Vasilevskii 1973: content verified secondhand through Vaandrager & Melse.
- Leucker & Schallhart 2009.
- Lynch & Vaandrager 1995.
- Knight & Leveson 1986.
- Keppel & Underwood 1962.
- Hitch 1978.
- Kirchner 1958 and Jacobs 1887 (attribution only).
- Folstein et al. 1975 (serial sevens).
- Page & Norris 1998.
- Howard & Kahana 2002.
- Willshaw et al. 1969.
- Amit et al. 1985 (the capacity number comes via Ramsauer).
- Gallistel & King 2009 (thesis).
- Moore 1956: we did not read the original. Theorem 2's wording and page come from Fields 2013's verbatim quotation.
- von Neumann 1956: read in the 1952 Caltech lecture-notes text hosted by IAS. Section numbers match, but page numbers
  in the 1956 chapter need checking.

**Metadata quirks:**
- Crossref lists "S. Kanna" for Blum & Kannan 1989.
- Crossref and OpenAlex list only the first author for Compte et al. 2000 and Goldman et al. 2003; PubMed has the full
  author lists.
- Crossref dates Turing's paper 1937 (vol. s2-42 is 1936–37), and Vasilevskii's English translation 1975.
