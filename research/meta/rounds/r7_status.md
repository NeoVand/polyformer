# Round 7 status: what certified bounded-view computation is FOR (orchestrator notes, written before mixing)

## Step 0. Three facts we did not have a week ago
1. **At 4B the sheet path is weaker than in-head reasoning on GSM8K.** It scored 847 vs 890 on the same 965 problems.
   At 0.8B the adapter cost reasoning on fresh items (−5.8). On small-number word problems the sheet buys nothing.
2. **Stock 4B already reads word problems.** With a few examples it writes the correct sheet line for 0.989 of them.
   Translation is not the bottleneck at 4B.
3. **Prior art covers the pinned check.** Lewandowski 2026 pins its decoding too, and checks exact match on a server.
   DNAR proves learned algorithms correct. What is ours: a margin certificate on the deployment path, a pretrained
   model, composition, and the gate.

## Constraint sweep (what dropping each constraint opens)
- **Arithmetic only.** Drop it and any finite-state procedure is open: parsing, ledgers, protocols, game rules,
  state tracking, unit and dimension checking.
- **A language model.** Drop it and controllers or perception modules become candidates; the certificate is the
  method.
- **Pretrained.** Drop it and we are in DNAR territory, which is already owned.
- **Exact glyphs.** Drop it and the views become fixed-font machine-readable inputs (seven-segment, MICR, barcodes),
  with noise-robust certificates.
- **Outputs only.** Drop it and we can certify internal state (a register, a belief, a ledger), or certify absence
  (what the model never does on a finite domain).
- **Single model.** Drop it and we can certify an interface between models (a protocol), or a fleet on different
  hardware.
- **The product is the computation.** Drop it and the certificate itself is the product: an audit artefact, a
  regulatory record, liability, or a measurement instrument for interpretability.
- **ML journal.** Drop it and the venue could be formal methods (CAV), interpretability, or a health or finance
  domain journal.

## My own ideas before mixing (graded later)
- **O1, interpretability with complete ground truth.** A pretrained LLM skill whose function is known on every input
  (2,446 views) is a model organism. A mechanistic account can be checked on every input, and a compact proof
  (Gross 2024) could be derived from the mechanism, which is new on a pretrained model. Asset: MECHANISM found the
  minimal automaton, 960/960 clusters, in a ~20-dim code.
- **O2, a no-side-effect interpreter.** Code-interpreter tool use is a security surface (prompt injection leading to
  code execution). A certified internal interpreter over a finite instruction set has no side effects by
  construction. Objection: a restricted sandbox does the same.
- **O3, an agent's ledger.** Long-horizon agents lose track of their own state (inventory, budget, counts). A
  certified bounded-view state update inside the model. Objection: the runtime could keep the ledger.
- **O4, certified dose or unit calculation inside a clinical assistant**, where regulation (EU AI Act, medical device
  rules) asks for verified accuracy. Objection: an EHR calculator already exists.

## Step 3: mixing (after all eight reports)

**Yield:** 0 HIT, 4 TOOL (checklist, provenance, load paths, talent), 4 FRAME (corvid, AOC, glossing, number). We
judge the round by its convergences.

**Convergence 1 (corvid A + AOC A): a no-trigger certificate for delegated weights.** The adapter only ever sees
2,446 views, and with the gate off it is the base model bit for bit. Its whole effect is therefore a finite, checked
table. No long-range trigger can exist, because no step sees more than one view.

**Convergence 2 (load paths A + provenance A + AOC C): exact-or-refuse reading of real numbers in images**, certified
over bounded noise, with abstention.

**Single-field ideas (TOOL/FRAME):**
- DO-CONFIRM / Chow routing (checklist, talent);
- a shakedown invariant for the state slot (load paths B; snapping is its finite case, already ours);
- certified count lists across languages compared with child data (number);
- a reviewable glosser table (glossing).

## Candidate A: auditable skills (from convergence 1 plus the 4B fact)

**Mechanism.**
1. A skill is added to an unchanged base model as an adapter. The runtime switches it on only for steps whose whole
   input is a pinned view from a finite set; elsewhere g = 0 and the model is bit-identical to the base.
2. Certifying every view on the device then fixes the adapter's complete behaviour. No long-range trigger can exist,
   and any per-view sabotage shows in the table.
3. The base decides when to call the skill and translates the problem. Stock 4B with a few examples already does this
   (word problems 0.989, recall 0.974), so no dialogue fine-tune is needed, and retention loss is zero by
   construction outside the calls.

**Who cares:** model supply-chain security (third-party skills), regulated deployers, on-device assistants.

**Breaks:** "the product is the computation". The product is the guarantee.

**Experiment and kill:**
- (i) Plant a long-range sleeper trigger in a conventional full-context arithmetic fine-tune. Sampled testing at
  10^5 problems misses it. The same trigger cannot be expressed under the pinned design, and any per-view sabotage is
  flagged. A red team gets two weeks.
- (ii) Stock 4B plus the gated adapter on GSM8K and IFEval, with the few-shot sheet prompt. **Kill** if the sheet
  prompt costs the 4B more than 2 points on GSM8K (at 0.8B it cost 34–37), or if a red team builds a certified
  adapter that changes a user-visible output.

**Adversary:**
- "For arithmetic, coverage testing gives the same." The answer: coverage is cheap because of the pinned design.
  For a full-context adapter no finite test excludes triggers (Theorem 2; Goldwasser 2022).
- "A calculator tool is auditable too." True. The claim is about neural skills, and P1 (why neural) stays the weak
  point.

**Prior art at gate level 1 (web, 1 Nov):**
- Goldwasser et al. 2022: undetectable backdoors.
- Christiano et al. 2024: runtime detection.
- Goldwasser et al. STOC 2025: mitigation without detection.
- vTune and zkLoRA: prove training, not behaviour.
- aLoRA: invocation gating, not auditing.
- Modality-gated adapters: bit-identical elsewhere.
- None confines an adapter to a finite domain with an exhaustive device certificate. A deeper gate is needed before
  any claim.

**Score (novelty / feasibility / cost / impact):** 3.5 / 4 / 5 / 3.5. **Weakest sub-problem:** P1, why a neural skill.

## Candidate B: exact-or-refuse on real scans (convergence 2)

Certify per-glyph abstention margins over a perturbation ball, so that a column total from a photograph is exact or
refused, never silently wrong.

**Kill:** under 50% of real crops fall inside the ball, or zero silent errors needs more than 30% refusals.

**Prior art:** randomized smoothing (Cohen 2019); selective classification; OCR confidence thresholds.

**Score:** 3 / 2 / 3 / 3.

## Not from the round, kept: O1, interpretability with complete ground truth (score 4 / 3 / 4 / 4)
