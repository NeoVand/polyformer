# Contributions: the complete inventory (24 Oct 2026, in flight)

Status tags: **[proved]** with a written proof; **[verified]** checked numerically or by test; **[n/n]** seeds or runs
that pass; **[pending]** running or not yet run. Sources in brackets.

## The thesis in one paragraph
Sequence models trained to predict the next token are blind to small per-step errors in their own state, so they fit
the training length and drift beyond it. Exactness at any length is a property of the objective, not of the
architecture, and it needs three ingredients: a reachable code (every state and event seen in training), closure (the
state cannot leave the set it was trained on; a fixed norm is the simplest form) and a state-level signal that is stiff
in the per-step error. Certified equivalences, pairs of histories a checker says end in the same state, are the
strongest such signal: with closure, the joint minimiser of "predict the output, predict the next state, merge
certified-equivalent histories" is the minimal (Nerode) automaton, and it is exact at every length. Every failure we
observed removed one of the three ingredients.

## A. Theory

| # | Contribution | Status [source] |
|---|---|---|
| T1 | **Blindness.** The next-token loss gap of a drifting transition is bounded by the loss floor times (exp(√2KεL) − 1); transitions within ρ of the exact loss fail at every N ≥ mL / log(1 + ρ/s̄); no converse bound exists, so the loss can never certify exactness. | proved [methods Thm 1; PROOFS A1] |
| T2 | **Stiffness.** On a certified pair, the centred cosine distance responds to drift at first order, independent of the readout's margin; the cross-entropy's derivatives carry a factor of the loss floor. | proved [Thm 2; PROOFS A2] |
| T3 | **Admissible distances.** A distance must factor through the readout's normalisation to have no trivial minima; its zero set is exactly the states constant on each component of the pair graph. Raw RMS distance has trivial minima. | proved [Thm 2; PROOFS A2.4-A2.6] |
| T4 | **Closure gives exactness at every length.** Injective labels, an exact readout, class-constant states and closure imply the induced machine is isomorphic to the minimal automaton at every length. A fixed norm supplies closure architecturally; an explicit counterexample shows closure cannot be dropped. | proved [Thm 3, Cor 3.1] |
| T5 | **What next-state prediction adds.** It makes the state a right congruence on the training set, carrying sparse certified equalities to all continuations, but it has class-splitting zeros (length parity), so it cannot replace the certified signal. | proved [Prop 3.2; PROOFS2 T2] |
| T6 | **Readout criterion.** With a sole linear readout, the equivalence term can only merge, never collapse; a second path or a non-uniformly sensitive head admits collapse at the price of a conditional mutual information. Explains why non-linear heads failed. | proved [PROOFS2 T1] |
| T7 | **Error correction.** Block contraction onto the class centres bounds the error forever and keeps the readout exact; without contraction the error is a random walk; the equivalence term selects contraction, cross-entropy and next-state prediction do not. | proved [Thm 4; PROOFS2 T3] |
| T8 | **Holonomy.** The state factors through the minimal automaton exactly when every certified loop closes; drift is bounded by the curvature of the loops met. | proved [PROOFS2 T5] |
| T9 | **Repair equilibrium.** Exactness at length settles where fresh errors balance repairs by overwrite; a birth-death model predicts the observed plateaus (0.71-0.74 predicted, 0.72-0.73 observed). | proved + verified [Prop 6; PROOFS3 Am-4] |
| T10 | **Soft checkers.** A wrong pair's pull scales with the distance it closes: near-miss errors are tolerated under dense supervision, far errors are not; trimmed and capped aggregation; a graded checker is a static distortion; tolerance scales with supervision density. | proved; noise test confirms [PROOFS4] |
| T11 | **Limits.** Equivalences are semantics-agnostic, so the term selects locality, not the operation table (Prop 5); no transfer across names without shared structure, and a swap-invariant ceiling for flat slots on ordered operations (PROOFS3). The term's residual is an optimisation-noise floor ∝ η/μ. | proved + verified [Prop 5; PROOFS3; PROOFS A3] |
| T12 | **Depth.** S5 words are NC¹-complete (beyond TC⁰ transformers); the rewrite-chain monoid is solvable (largest group S4), so the transformer's failure there is not a depth limit. | proved [methods; Supp Note 1] |
| T13 | **Continuous systems (new today).** Error correction needs a restoring direction: an attractor or a projection onto the exact invariant set. Conservative systems have none (Liouville), so phase cannot be repaired by any objective. | argued; confirmed by PHYSICS |

## B. Empirical results

| # | Domain and result | Numbers | Status [source] |
|---|---|---|---|
| E1 | **Code execution, the factorial** (frozen Qwen2.5-Coder-0.5B + latent slot; 1,024 statements = 64x) | ordinary+norm 0.76/0.56/0.48; next-state+norm 0.97/0.98/0.87; signal+norm 1.000 x3; full+norm 1.000 x3; norm alone 0/3; without norm not exact | 3/3 [EXEC_LM §11] |
| E2 | **Code execution vs chain of thought** | latent slot exact at 256 on 3/3; whole-history chain of thought 0.06-0.37, and 0.000 at 256 | 3/3 [EXEC_D, EXEC_LM 7, 11] |
| E3 | **Certified Lean rewrite chains** | full recipe exact at every length to 4,096 on 9/9 (5k/20k/80k data); R+I, R+NL, full exact at 256 on 6/6, ordinary 0/6 | 9/9 [LEAN_S 2.7-2.9] |
| E4 | **Baselines that fail** | NoPE transformer horizon 5-8 rewrites; DeltaProduct not exact at 4,096 with or without the signal | [LEAN_H §6, §8] |
| E5 | **S5 group words** | next-state+norm 3/3 at 1,024; signal at μ = 0.1 3/3; at μ = 1 1/3 (weight matters) | [INVARIANCE §7] |
| E6 | **Long addition and counting** (frozen Qwen-Coder + slot; train ≤32 items, test 4,096 = 128x; EXEC_LM 19 controls, fresh seeds 6-8, one selection rule, n = 512) | addition: ordinary 0/3; every arm with the fixed norm 512/512 on 3/3, also on long-carry sets (balanced carry 0/1 halves on the same checkpoints: 512/512) where the last-8 floor scores 0/512, so addition needs closure, not the signal; counting: next-state, equivalence and full recipe 3/3, fixed norm alone 1/3, ordinary at chance; base model 0.0 even at 32 | 3/3 [EXEC_LM §19; AUDIT N1] |
| E7 | **Natural-language stories, certified** (frozen Qwen2.5-0.5B features + tracker) | exact at 1,024: 1.000 / 0.992 / 1.000; no signal 0.594 / 0.312 / 0.672 (exact at the end; AUDIT item 6) | 3/3 [STORIES §2, §5] |
| E8 | **Stories with a soft checker** (bge-m3 on 7B summaries; realised 5.9% near, 0.1% far errors) | 0.852 / 0.828 / 0.773 at 1,024, flat with length, above no-signal on 3/3 | partial [STORIES §5] |
| E9 | **Noise tolerance** | near-miss false pairs tolerated up to 20% (exact to 4,096); random far errors hurt from 1% | [MECHANISM §8] |
| E10 | **Mechanism** | exact state = minimal automaton: 960 clusters for 960 trees at purity 1.000, in a string-linear code of about 20 dimensions; not systematic to new atoms | [MECHANISM] |
| E11 | **The landscape** | drifting and exact trackers sit in equally deep next-token valleys; the added terms lift only the drifting one | [figures v4 landscape] |
| E12 | **Drift diagnostics** | growth of the pair distance from length 16 to 256 predicts drift (Spearman 0.85 / 0.91 over 54 runs); without the norm each step's turn collapses ~300-fold while the norm grows 16-fold | [INVARIANCE §7; gallery drift] |
| E13 | **Coverage is the cause in the Markov step** | uniform-state training exact at 1,024 on 3/3; zero-start control 0.50-0.64 | 3/3 [EXEC_LM §11] |
| E14 | **In-model self-distillation** (Qwen 0.5B chain of thought, no labels beyond 16) | 0.000 → 0.51 / 0.42 at 256; oracle 0.94 / 1.00; consensus teacher pending | partial [EXEC_LM §12] |
| E15 | **Physics** | closure stops blow-up (6/6 ordinary explode, 0/21 normed); Lorenz held on its attractor at 64x (1.2-2x the truth's distance vs 6-10x); pendulum held only with closure onto the energy shell; signal adds nothing measurable | [PHYSICS] |
| E16 | **Frontier models, no tools** | addition at 1,024: GPT-6 Astra 2/3, Fable 5.1 2/3, Gemini 4 Argon 1/3; at 4,096: GPT 1/1, Fable 1/2, using 12k-59k reasoning tokens; stories: frontier 3/3 | pilot [FRONTIER] |

## C. Negative and boundary results (they belong in the paper)
- Natural mathlib proofs: closed at this scale after an audit overturned the first reading (shallow-feature floor beat every arm). [D1_AUDIT]
- In-model latent recurrence through Qwen collapsed to the all-zero predictor (outlier coordinates, BPTT growth ×2.3 per statement). [INMODEL]
- Flat slots cannot learn ordered two-operand operations; factorised registers fit; registers without the signal 0.000 / 0.611 / 0.385 at 256 against 0.725 with it. [EXEC_LM, PROOFS3]
- The signal is not needed everywhere: next-state + closure suffices on S5, addition, counting and physics; it is decisive on code execution and on stories without next-state.

## D. What is pending
Consensus teacher (in-model, approved); consensus checker for language (proposed); last addition seed; frontier
pilot's Gemini rows; figure gallery v2.

## E. Nature, honestly: what is still missing
1. **One uniform ablation across all domains.** Reviewers will ask which ingredient does the work. Today the factorial is
   complete only on code execution. A single protocol (ordinary / +norm / +next-state / +signal / full; 3 seeds) on code,
   Lean, S5, arithmetic and stories, all cheap, turns six partial stories into one table. **Highest value, about $15.**
2. **The bridge into a real language model.** Everything exact uses a frozen model plus a small trained state module.
   Nature will ask whether a language model itself becomes exact. The consensus teacher is the current attempt.
3. **Language without a perfect checker.** Soft-checker stories are stable at length but not exact (0.77-0.85). The
   consensus checker is the next attempt.
4. **Theory consolidation and literature** (priorities 4 and 5): merge PROOFS 1-4 into one clean note; add Angluin,
   Bachmann & Nagarajan, Othello-GPT, Abacus, position coupling, context distillation, computational mechanics, PSRs,
   value equivalence, TEM/CSCG, von Neumann.
5. **Figure 1 and the abstract**, after the table in item 1 exists.

Verdict: today this is a strong Nature Machine Intelligence paper. It becomes a credible Nature submission if items 1
and 2 land: one clean cross-domain table, and exactness inside a language model rather than beside it.

## F. Positioning after the literature review (LITERATURE.md, 73 verified works; 24 cited in the old draft)
Not ours, and the paper must say so with citations:
- Exact long arithmetic as such: the Neural GPU (Kaiser & Sutskever 2016) added long binary numbers without error after
  20-bit training, by architecture. Our claim is different: with the architecture fixed, the objective alone moves
  the same model from 0.000 to 1.000 at 128x.
- The minimal predictive state as the target: causal states (Shalizi & Crutchfield 2001), Nerode, bisimulation as model
  minimisation (Givan et al. 2003).
- "Predict the output and your own next state": approximate information state (Subramanian et al. 2022), SPR, NextLat.
- "Train on the states you will meet": DAgger (Ross et al. 2011); our Markov-step coverage result echoes it.
- Nerode as an evaluation of world models: Vafa et al. 2024. Invariance across inputs sharing an algorithmic step:
  Hint-ReLIC (Bevilacqua et al. 2023).
Ours: the blindness theorem (likelihood cannot select exactness, quantitatively); certified equivalence from an
external checker as a training signal, with its stiffness and admissibility theorems; closure as the missing third
ingredient, with the theorem, the counterexample and its architectural form; the cross-domain ablation that
attributes each ingredient; error-correction and repair-equilibrium theory with quantitative matches; soft-checker
theory and the language results.

## G. After THEORY_DEEP (24 Oct ~12:00; claude/gracious-panini-dde55f 7838e9d)
- **T14 The error cocycle (proved framework).** The error's linearised dynamics over the automaton's transition graph
  is the one object. Its top Lyapunov exponent decides exactness in law (typical inputs, what our tests measure); its
  graph-constrained joint spectral radius decides exactness on every input. Each ingredient acts on a different part:
  cross-entropy only on the readout's row space, closure on the radial coordinate, next-state only on what its
  predictor cannot model, the equivalence term on every direction in which equivalent histories differ.
- **T15 Certificates.** A finite ball-invariance check certifies exactness on every input at every length; it exists
  exactly when the constrained spectral radius is below 1. The snapped Lean trackers (state replaced by the nearest of
  960 prototypes after every event) are certified exact on every input at every length on 3 of 3 seeds.
- **Wording change for the paper.** "Exact at every length" means in law. Lean trackers trained without closure fail on
  repeated short cycles (18-24 events) that random tests almost never produce (expected wait 10^11.6-10^17.4 events);
  closure added after training rescues 92 of 96. Closure-trained trackers are being tested now.
- **The clause table, explained (conjectured):** dark dimension, the share of state each event preserves, the kind of
  persistent dark error and norm stationarity predict every column except S5's next-state and equivalence rows.
- **Coverage, sharpened:** what must be covered is (latent, event) pairs, not automaton states; this explains why the
  self-distillation teacher's errors are correlated across equivalent contexts.
