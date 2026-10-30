# Novelty gate: loops, scratchpads, fixed points, reducers (Fable, 30 Oct 2026)

Live search by Fable on 30 Oct 2026 (WebSearch + arXiv abstract pages opened; no PDFs read in full). "Not located" is not
"absent"; the orchestrator's Codex/Argon gates search deeper. Builds on `audit/sketchpad_gate`, `audit/penpaper_gate`,
`audit/leap3_gate` (all NARROW on the canvas conjunction) and does not repeat them.

| Idea | Verdict | Closest work (date) | What remains open |
|---|---|---|---|
| 1. Looped transformer + visual scratchpad, Markov overwrite | **NARROW** | Chain-of-Sketch Inductive CoS (2410.08165); LoopViT (2602.02156, Feb 2026); Looped Diffusion Transformer (2609.40305, Sep 2026); PENCIL; MVoT | A *discrete glyph* canvas as sole state, certified, in a pretrained VLM with language intact (= our E5; sketchpad gate's verdict) |
| 2. Our training recipe: certificate as loss, failing-row replay, hinge, stop rule | **KILLED as method** | CEGIS-style training: Sivaraman et al. 2020 (monotonic nets); Trainify, CAV 2022; "certified networks via CEGIS" 2024 | Nothing; report it as engineering with the 4/4 vs 2/6 measurement |
| 3. Nested fixed points: contractive inner loop → discrete snapped write → certificate | **NARROW** | HRM (2506.21734, Jun 2025) and its critique Ren & Liu (2601.10679, Jan 2026); TRM (2510.04871, Oct 2025); Attractor Models (2605.12466, May 2026); DEAR (2402.06445, Feb 2024); monDEQ (Winston & Kolter 2020); Lipschitz-bounded equilibrium nets (Revay et al. 2020); EBT (2507.02092, ICLR 2026 oral) | The conjunction: a *monotone* inner solver with a provably unique fixed point (monDEQ) + a discrete external canvas written once per outer tick (separation by snap) + a finite certificate over views; and the specific cure for HRM's "multiple fixed points" |
| 4. Pointer-masked looped transformer as interaction-net reducer | **OPEN (narrowly)** | Neural Lambda Calculus (2304.09276, 2023: string-level β-reduction, 99.7% one-step); Δ-Nets (2505.20314, symbolic); Giannou 2023; Neural Rewriter 2019 | No neural interaction-net or learned graph-rewriting reducer located; certificate by rule table + confluence untested anywhere |
| 5. Term rewriting on the canvas (primitives × interpreter × compiler) | **NARROW** | Neuro-symbolic convergent TRS, NRS/FastNRS (Petruzzellis, Testolin, Sperduti 2507.19372, Jul 2025); Neural Rewriting System (2402.17407, Feb 2024); Piotrowski et al. 2019 (83%) | Per-rule certificate, zero-shot rule libraries, inside a VLM with language; NRS is the competitor to compare against |
| 6. Twin / gated adapter, learned gate | **KILLED as novelty** | X-LoRA 2024; CALM 2024; Ladder Side-Tuning 2022; Progressive Nets 2016 | Use it, do not claim it |
| 7. Self-legibility: the model picks the glyphs it reads best | **OPEN, small** | Learning to Draw (Mihai & Hare, NeurIPS 2021); Shared Visual Representations of Drawing (2110.08203); Visual symbolic mechanisms (2506.15871, ICLR 2026: internal, different) | A VLM optimising its own glyph set for exact self-read-back under a margin; workshop-sized, good demo |

## Evidence and deductions

**1.** The sketchpad and pen-and-paper gates already found every piece of the canvas system in the literature and the
conjunction open. This pass adds the 2026 looped-vision line: LoopViT loops a ViT for ARC with an entropy-based exit;
Looped Diffusion Transformer reports that later loops correct earlier mistakes and that repeated application can
"overwrite or attenuate" image-token information. Neither is a discrete scratchpad or certified. Verdict unchanged.

**2.** Training on counterexamples produced by a verifier until the verifier finds none is the counterexample-guided
inductive synthesis loop, applied to neural nets at least since 2020 and stated by its 2024 authors as "not new". Our
replay of failing rows from the whole-domain certificate is that loop with an exhaustive verifier. Claim the result
(recipe v2 certified 4/4 where constant-lr certified 2/6), not the method.

**3.** This is the crowded one. HRM (two coupled recurrent modules, DEQ one-step gradient, ACT halting) is the direct
ancestor of "nested loops that converge"; Ren & Liu show it violates its own fixed-point assumption, has multiple fixed
points, and "guesses the first fixed point, which could be incorrect, and gets trapped there". TRM drops the fixed-point
theorem and backpropagates through the recursion. Attractor Models (May 2026) put a fixed-point attractor module behind a
backbone with implicit differentiation and adaptive iterations, at language-model scale (a 770M model beating a 1.3B
transformer) and on Sudoku/Maze with 27M parameters: "LM + fixed-point refinement" as a headline is taken. DEAR solves
algorithms as equilibria on CLRS. Monotone operator equilibrium networks give a *unique* equilibrium by parameterisation
with guaranteed-convergent solvers; Lipschitz-bounded equilibrium networks give certified Lipschitz bounds. EBT frames
thinking as energy minimisation with more steps helping. What nobody in this list has: uniqueness guaranteed by
construction (monDEQ) *plus* a discrete external memory that supplies separation *plus* a finite certificate over
views. That conjunction is exactly the fix for HRM's multiple fixed points, and it is a small-model theory+experiment
paper, not a VLM demo.

**4.** A transformer has been trained to do β-reduction on strings (one-step 99.7%, multi-step 97.7%), with no graph, no
locality, no certificate. Interaction nets and combinators have rich symbolic runtimes (HVM, Δ-Nets) and no neural
realisation that I could find. The pointer-masked reducer with a rule-table certificate and confluence is open as far as
this search reaches; a deeper gate should search "GNN graph rewriting rules learned", "neural graph transformation
systems" and "learned combinator reduction".

**5.** NRS/FastNRS (Jul 2025) is "a neuro-symbolic architecture inspired by the rewriting algorithm itself" for formula
simplification, with out-of-distribution generalisation and GPT-4o beaten; whether rules are learned or given, and
whether anything is exact, is not on the abstract page and must be read before we position against it. The 2024 Neural
Rewriting System splits selector/solver/combiner. Our deltas, if real: certificate per rule, rules as programs certified
without training, language intact, canvas as the sole state.

**6–7.** As stated in the table. Self-legibility has a cognitive-science flavour (emergent sketch protocols become
indecipherable without a perceptual loss, Mihai & Hare) that could make a nice short paper if the margin-selected glyph
set is measurably more legible to the model than the font it was given.

## What this means for publications (Fable's pick)

- **Paper A, ship in 7–10 days:** the canvas system as it exists (E2–E5): one adapter, two procedures, 1,795 rows
  certified with margins, 1,000-digit sums and 10×10 products exact, on-device re-certification, language ratio ≈ 1.00,
  recipe comparison (4/4 vs 2/6), the failing-rows-become-wrong-products figure, Theorem P for canvases, live browser
  demo. NARROW novelty stated in the first paragraph; the artefact is the contribution. Low risk, already done.
- **Paper B, 3–5 weeks, $0:** certifiable decoders: finite certificate iff history-independent finite view; the
  classification (full attention / pinned / bounded affine (Brandoit) / canvas); Lean; the measured instances. Close the
  Savant-R gate's four objections (ties, reachable states, numerics, KV equivalence) or the paper is not honest.
- **Paper C, 6–10 weeks:** C1 the canvas interpreter with per-program certificates (zero-shot procedures; the $5 pilot
  decides in a day; competitor NRS), or C2 the monotone inner loop + snapped canvas (fixes HRM's multiple fixed points;
  crowded, hot, small-model). C3, the interaction-net reducer, is the deepest and the slowest; 2027.
- Order for survival: A now, B in parallel, C1's pilot this week, C2 after A is out. Do not start with items 1–3 of the
  table as headline claims; they are where the field already is.
