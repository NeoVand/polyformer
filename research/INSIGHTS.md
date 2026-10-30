# INSIGHTS: what the experiments say, and what to do with it

Orchestrator's synthesis, 28 Oct 2026, 02:00 CDT. Sources are named on every line; a number here is only as good as
its source, and the sources carry n, seeds and registrations. Status words: **proved** (Lean or a written proof that
was checked), **measured** (a counted, registered result), **observed** (uncounted or exploratory), **open**.

## 0. The one idea underneath everything

**Errors never grow in a step that the next step cannot see.** v1 proves that a loss evaluated on reached states
cannot see the derivatives that make errors grow (blindness), so robustness has to come from the architecture (a
closure that regenerates the state each step) or from an explicit probe (the aimed kick). v2 finds that an
off-the-shelf LLM already carries the lookup machinery for a finite-state step. A clock that gives each step only the
program and a fresh (state, event) block is that regenerating architecture, imposed at inference with no change to
the weights. Each tick's footprint is exactly what the certificate checks, so blindness has nothing left to hide.

In engineering terms: digital computers are reliable because every gate regenerates its signal (von Neumann's
restoring organ, the static discipline of digital logic). The pinned step is regeneration placed below the program.
The certificate is the noise margin, measured per program.

## 1. Theorem candidates

| # | statement (plain words) | evidence | status | next |
|---|---|---|---|---|
| P | **Pinned regeneration.** If every reachable row (s, e) of the program's table is certified (one forward on the deployment path gives the table's destination), the clock's run equals the table's run for every event sequence, of any length. Converse: if the clock is right on every input, every reachable row is certified. | DEMO_DESIGN §5.1; 130,141 and 137,898 real ticks bitwise equal to certified rows (PROMPTBOX §6.10); G1 8/8 runs of 10,000 events exact | **proved** (Lean, lean-p af8809ad: `pinned_regeneration_iff`, `cache_sound`, `tick_logits_eq_row`) | cite in v2 |
| P-M | **Mealy version** (arithmetic): two cells per row, (s,a,b)→t and (s,a,b,t)→o; certified rows ⇒ every output digit right. Hypothesis that matters: same code path; the 1-token forward 2 was not bitwise (86% of ticks), the re-fed block is (512/512) | ARITH §5 | **proved** (`pinned_regeneration_mealy`, `mealy_certificate_necessary`; `forward2_refeed_eq`: re-feed = old forward 2 in exact arithmetic); ARITH re-run passed | cite |
| 8a✗ | **Token emission is not a full snap in context.** A step can pass every single-step check and still go wrong at length, because earlier run tokens are a second, unsnapped state. | DEMO_DESIGN §5.2 | **proved false** (`theorem8a_counterexample`, `not_theorem8a`); also `no_finite_check` / `no_finite_test_suite`: for any finite set of test contexts there is a decoder that passes the certificate and every test with strict margins, is exact up to any N, and runs wrong later; converse also fails (`unpinned_exact_not_certified`); true version under a τ-bound (`unpinned_exact_of_close`) | the theorem pair below |
| B | **The LLM's blindness.** Plain decoding is a tracker whose state includes the run so far. Next-token likelihood on teacher-forced correct runs is blind to how the next state depends on earlier run tokens (Theorem 1(a)'s likelihood corollary, THEOREMS I.1.1, applied to decoding). The pin removes the history from the state, so that dependence is zero by construction (INTERP Thm 1: footprint = view). | the theorem exists (Lean); the measurement is BRIDGE part 1 | proved in general; LLM measurement open | BRIDGE |
| C | **Composition of certified calls.** If every call is certified on its reachable rows, each call's result equals its table's output on its actual input, at any length and in any order, with Π built fresh per call. A wrong answer then means a wrong table, a wrong quote or wrong final text; the executor term is provably empty. Each term is read at the right inputs. Hypotheses: quotes cite only earlier results, and the final text reads only the results. | **proved** (lean-p 37866e74: `compose_exact`, `error_decomposition_certified`, `error_bound`) | state in v2; REASON measures the terms |
| PAIR | **Why the clock (theorem pair).** Unpinned decoding: no finite test suite certifies it (`no_finite_test_suite`). Pinned decoding: a finite per-row certificate is necessary and sufficient for exactness at every length (`pinned_regeneration_iff`). This is the language-model twin of v1's blindness: a check on reached contexts cannot see what longer histories do, so regeneration has to come from the architecture. | **proved** (Lean) | headline theorem of v2 |
| Q | **Lookup lemma.** With the softmax denominator over all positions, a matched weight of at least 1/2 and a separation greater than the leakage give the right argmax. The 1/2 is sharp (`lookup_half_sharp`). Corrections to the informal Lemma Q: Z₀ is needed; role-additivity is never used; the readout must be linear (before the final RMSNorm). | **proved** (`lookup_argmax_half`, `lemmaQ`) | methods |
| P3 | **Registers.** Per-register certificates give an exact joint run, with a converse. A cascade version covers registers that read earlier registers' new values. | **proved** (`registers_exact`, `registers_certificate_necessary`, `cascade_exact`) | methods |
| W | **The pointer cannot live in a bounded window.** Take m copies of one event followed by a different one. If 2m ≥ k + 2\|S\|, no decoder that sees only Π and the last k tokens emits the run correctly through the change, because it cannot find where a stretch ends. Tight to within two events (paper proof). Assumes no position ids. Streaming the events, as the clock does, escapes it. Full attention escapes it too, but then the history is the second, unsnapped state. | **proved** (`window_loses_place`, `window_eventually_periodic`) | the pointer theorem of v2: why the clock streams events, and BRIDGE's first-error finding |
| POL | **The clock is a cache policy.** Token-by-token decoding with Π as sink, each block evicted and positions restarting gives exactly the pinned tick's logits, so Theorem P carries over. Exact arithmetic only; other policies are not modelled. | **proved** (`policy_tick_eq`, `policy_regeneration`) | the "not a tool call" theorem |
| RC | **Robust cells.** With certified margin μ, path bound τ and a local Lipschitz constant K, any state embedding within (μ − 2τ)/(2K) gives the same tick. A run perturbed at every tick by at most ρ is exact when 2(τ + Kρ) < μ. K is assumed, not derived. | **proved** (`robust_cell`, `robust_run`) | ties CIRCUITS' sharp cells to v1's robust cells (evidence, not consequence) |
| ADD | **The adder and subtracter tables are correct, end to end with the clock.**
- `adder_correct`: the 200 literal rows, run from carry 0 on the zero-padded pairs plus (0,0), give exactly the digits of x + y for all lengths.
- `sub_correct`: borrow 0 iff y ≤ x, with output x − y.
- `adder_clock_correct` / `sub_clock_correct`: if the 200 written rows pass the two-forward certificate, the clock's final line is x + y for numbers of every length.

Row arithmetic and well-formedness are checked by kernel `decide`, without native_decide. What remains outside the proof: did the model write these exact rows (a byte comparison), and did the clock read the right spans. | **proved** (lean-p aac1f9ee; I re-ran it: 182 axiom lines, 0 sorryAx, 0 native) | the page can show "this table is the Lean-proved adder" by byte comparison |
| N\* | **No weights-level certificate for Savant as trained.** The lookup is a committee of ~30 heads with context-dependent, near- but not certifiably role-additive scores; Lemma Q with measured ε certifies 1–86% of queries per head. A weights-level N\* has to be built in (one table head whose keys are fixed functions of (s′, e′); nothing else reads Π). | CIRCUITS §1 | observed (uncounted) | design note for the next model, not tonight |
| S | **Size: limited by the weakest names, not by dilution.** Median margins stay at 11.6–14.4 up to 4,096 rows and INTERP's adversarial needles are 144/144. On the deployed path, random tables lose about 1 row in 1,000 at 2,048–4,096 rows (30 of 24,576 at 4,096). Those errors cluster on word-fragment and near-duplicate names (` illeg` beside ` illegal`, ` Sheet`, ` bra`), with wrong-answer margins around 3. This is what INTERP's per-quadruple certificate predicts. INTERP's slope-one size law was refuted in Lean. | CIRCUITS §1, §7 (final) | observed | screen the name pool by worst margin before raising MAX_ROWS; the certificate catches these cases, since a weak row fails it |

## 2. Observations that changed our minds

1. **The interpreter is already in the base model; 30 steps switch it on** (CIRCUITS §2). Base Qwen3-4B finds the
   right row (L7.H7 picks it 92% of the time) and encodes where it sits in Π (R² 0.80), but gets 35% of rows right
   because it cannot read the destination out. Thirty optimizer steps recruit about 45 destination-reading heads in
   layers 13–29 and certify 55/55 held-out tables. The weight change is small and diffuse: it sharpens a circuit
   that was already there rather than building one. RL's change was 1/6 of that and moved nothing.
   WEIGHTS (§2–3, 256 G1 tables) agrees from the other side. The top 4 singular directions per module (about 8M of
   the adapter's 132M parameters) certify 252/256 tables, and half of Stage 1's update does as well as all of it.
   The update applied to layers 12–17 alone gives 218/256; applied to layers 24–35 alone it gives 4/256.
   - The useful change sits mid-network. That is the same band that INSIDE and DIAG found for in-model trackers.
   - The read-out heads it enables sit later, in layers 20–27.
   BIGIDEA H1 (counted C1 plus uncounted screening):
   - The base model gets 33.8% of G1 rows right and certifies 3/512 tables. Its usual error is copying the current
     state.
   - One vector added at layer 18 (2,560 parameters) reaches 99.74% of rows and 103/128 tables.
   - An 8-vector soft prompt, with no weight touched, reaches 99.6% of rows and 101/128 tables.
   - Rank-1 LoRA on q, k, v and o (737k parameters) certifies 128/128 tables by step 100.

   So a soft prompt is enough to switch most of the executor on. Certifying whole tables needs about 10⁵–10⁶
   parameters. Counted G1 runs on the edits are pending.
   *Changed:* we thought the executor needed 1,200 steps; it needs ~50. Training budget belongs to compiling,
   quoting and routing. Answer to Neo's "is it trivial?": the executor is cheap because it is latent. What is new
   is the regenerating clock and the per-program certificate that make it exact and checkable at any length.
2. **Plain decoding nearly matches pinned up to 2,048 events on trained families** (PROMPTBOX §6.10: within 5 points
   at every length). Earlier plain runs broke with length because the executor was undertrained. *Changed:* at
   moderate lengths the pin's value is the guarantee (a certificate before the run, bitwise ticks), not average
   accuracy. Its accuracy advantage has to be shown beyond 2,048 (BRIDGE).
3. **Held-out failures are the tape quote, not the program or the run.** 59/64 (SFT) and 71/73 (RL) of the wrong
   pinned elevator answers had an exact table (PROMPTBOX §6.12). *Changed:* generalization is limited by reading and
   quoting. Make quoting robust or by reference (sent to REASON).
4. **RL taught nothing new, but RL was barely tried** (PROMPTBOX §6.12; WEIGHTS §4).
   - Routing was already right: all 1,280 gate responses open a program.
   - Held-out cells stayed flat, and language held.
   - RL moved only 1.5% of the adapter. Its summed learning rate was 37× smaller than the language repair's.
   - *Changed:* the null result says nothing yet about RL's power here. Diverse generated families are the proven
     lever (`gen:test` 70–77% vs the answer-only twin's 34–47%). A fair RL test needs 10–30× the learning rate or
     the steps.
4b. **Held-out failures are specific and fixable in the data** (WEIGHTS §5).
   - Clock fails only on rows that cross 12.
   - Pattern needs a substring mechanism that neither format has.
   - Generated families fail mostly by being one place off (95/117 wrong rows).
   - Prose drops a rule for the "otherwise it stays" default.
   - 11 of the 82 "certified but wrong" tables are the right automaton under renamed states.
5. **Lookup-in-context architectures are robust by architecture.** We predicted drift and were wrong three times
   running: the INTERP pilot, P12 (one fixed table, fixed names, values only: exact at 10,000) and the decisive test.
   Attention to the table in context acts as regeneration. *Changed:* blindness says the loss cannot guarantee
   robustness; the architecture can supply it. This is the v1→v2 hinge.
6. **The kick is scale-sensitive, and in an LLM the write is the eraser.** In-model F collapsed on 9/10 seeds at
   σ = √0.1. At σ = the cell radius, F matches M on code and nearly on stories (BRIDGE2–3, stories/code σ tests).
   INSIDE: the residual drifts through layers 12–23 and the write W snaps it back to ~1e-4. *Changed:* the canonical
   kick is σ = cell radius; inside a pretrained host, contraction is largely supplied already (top factor 0.004–0.03).
7. **Certified does not mean correct.** The certificate checks execution against the written table, not the table
   against the question: 64–88 of 1,280 pinned gate responses were certified with a wrong table, mostly clock. The page says
   this; the paper must say it plainly.
8a. **Row 0 is the weakest row because of its position** (WEIGHTS §6). One newline before the table raises its
   median margin by 1.5 with no retraining. G1's only rejections are name confusions such as ` Zahl` / ` zahl`.
8. **The executor needs Π directly before the block** (CIRCUITS §4). A gap of 4 positions drops certification from
   55/55 to 45/55; shifting everything is free (RoPE). Row order does not matter (the fetch is content-addressed;
   the positional pointer exists, is inherited from the base model, and is unused: ≤ 1.4% of outputs follow it).
   *Changed:* the clock's contract is "Π adjacent, any order"; the clock may compact and reorder Π.
9. **Bitwise equality is a property of the code path.** 1-token forward 2 differs by up to 0.31 in logits from the
   certified row, while the re-fed block is bitwise (ARITH §5). Theorem P's hypothesis must name the code path and
   host.
10. **Full fine-tunes destroy language, and 400 steps of the right mix repair it.** DIAG's ten-skill model had a
    WikiText ratio of 2,340; Stage 2r (base-style ordinary data 25%, general data 20%, KL to base at 1.0) restores
    GSM8K to 91.5% with 0% programs on word problems.

11. **Plain decoding fails at the pointer first, then by step drift; the token snaps the state, not the context**
    (BRIDGE Part 1: Savant r2, true programs, seed 4040, n = 16 per cell; registered B1–B10).
    - **Exact plain runs:** 96% at 1,024 events, 88% at 2,048, 61% at 4,096, 0/96 at 8,192, 0/80 at 12,000.
    - **First errors are misread events:** 94/96 at 8k and 80/80 at 12k.
    - **With the events supplied:** exact to 2k, then 93% at 4k, 77% at 8k, 72% at 12k.
    - **Margins fall along a run:** −2.5 logits at 8k and −4.3 at 12k.
    - **One wrong earlier state costs later steps:** about 5 logits two steps on, 1.9 at 17–256 steps. Yet the next step
      follows the written state 89/90 times.
    - **After the first error:** 49,084 of 49,087 steps follow the table from what the model wrote, while only 42% of
      events still match the question.
    - **Attention shifts along a run:** attention to Π's matched destination falls 17×, and attention to the run's own
      history doubles.
    - **Aimed kicks on old run tokens** flip 149 of 2,688 labels; random kicks of the same size flip 0.

    *Changed:* the clock's main job is the pointer, a counter, which was v1's hard case. Its second job is to remove the
    history as a second state. The pinned step has zero drift on both.

12. **The clock is a KV-cache policy, not a tool** (BIGIDEA H2, counted; Savant r2; 8 runs per policy; A10G).
    - **The policy.** Keep Π as an attention sink, evict each (state, event) block after its tick, and restart
      positions right after Π.
    - **Bitwise reproduction.** Decoding under that policy reproduces the pinned tick bitwise on 24,336/24,336 ticks.
    - **Token by token.** Emit the state, then append the event, under the same policy: exact on 8/8 runs, and bitwise
      equal to its own certificate.
    - **Every other policy fails:**
      - advancing positions: 1/8 exact;
      - StreamingLLM window k = 2: 5/8 exact;
      - k = 3 or 4: 0/8;
      - full attention: 1/8.
    - **The pointer can't live in a bounded window.** When the model must read the tape itself, windows of k = 2, 4
      and 8 are 0/36 exact, with 35/36 first errors misread events. BRIDGE's pointer finding matches this.

    *Changed (answers "is it a tool call?"):* every transition is the LLM's own decoding. The clock contributes two
    things:
    - a cache policy (sink, evict, fixed positions);
    - streaming the events, i.e. the pointer.

    Neither computes anything about the state.
13. **A pinned, certified executor is a small edit away from the pretrained LLM** (not "the base model already
    executes": the base certifies 3/512). BIGIDEA H1; counted G1, 512 held-out tables, except where marked:
    - **one 2,560-number vector added at every position (E8):** 431/512 tables certified (84.2%), with 99.76% of rows
      right. The tick-positions-only variant (E7) has validation results only: 76/128 tables, 99.10% of rows. Its
      held-out G1 is coming from UNIVERSAL;
    - **rank-1 q, k, v, o LoRA** (737k parameters, 100 steps): 505/512 (98.6%), just short of G1;
    - **long runs:** every accepted table's long run was exact (19/19 runs, 190,000 bitwise ticks);
    - **soft prompt (validation only, no counted G1):** 8 learned input vectors, with no weight changed, get 99.5–99.6%
      of rows and 99–101/128 tables, and leave WikiText logits bitwise identical to the base (12/12 windows);
    - **language under weight edits:** trained without rehearsal, the weight edits raise WikiText NLL by 0.05–0.48 nats;
    - **wrong tables are refused, not run wrong.**

14. **The aimed kick cannot replace the clock** (BRIDGE Part 2; one training seed, with a confirmation seed running;
    registered Q1–Q8, of which 3/8 pass). Arms are 300 steps from Savant r2.
    - **The aimed state kick (K2) makes the step sturdier:**
      - step errors fall from 4.9 to 1.0 per 10⁴ tokens at 8k–12k;
      - the dependence on a wrong state 17–256 steps back falls from 2.1 to 0.75 logits.
    - **But K2 doubles reading errors**, so exact plain runs at 4,096 fall from 62% (K0) to 44%. Every arm is 0/96 at
      8,192.
    - **Kicking the read window too (K3) breaks the pointer.**
    - **A random kick at the same dose (K1) equals K0**, as in v1.
    - **Language is kept in every arm.**

    *Changed:* v1's closure maps to the pin, and the aimed kick can do part of the pin's job, on the step. The pointer
    is a counter as long as the input, outside v1's finite-state theory, and needs the clock or a certified increment
    (BRIDGE Part 3).

15. **UNIVERSAL: the lookup head is in every model; one vector unlocks the read-out mainly in Qwen** (G1 128 held-out
    tables; E7 = one vector at L/2, tick positions, 100 steps; registered; 9 of 10 models).

    | model | base rows | E7 rows | E7 tables |
    |---|---|---|---|
    | Qwen3-0.6B | 33.9% | 95.5% | 26/128 |
    | Qwen3-1.7B | 29.6% | 92.5% | 20/128 |
    | Qwen3-4B | 37.6% | 99.06% | 72/128 |
    | Qwen3-8B | 29.5% | 99.15% | 77/128 |
    | Qwen3-14B | 38.5% | 99.43% | 89/128 |
    | Gemma-2-9B | 23.0% | 91.8% | 19/128 |
    | OLMo-2-7B | 46.1% | 89.1% | 7/128 |
    | Mistral-7B | 23.7% | 84.8% | 14/128 |
    | Llama-3.1-8B | 18.6% | 48.0% | 2/128 |

    - **The row-finding head exists in all 9 base models**, including Qwen3-0.6B.
    - **In Qwen3, tables certified rise with size** from 4B to 14B (72, 77, 89).
    - **The non-Qwen models were still improving at step 100.**
    - **Coming next:**
      - Amendment 3: E7 to 300 steps; rank-1 LoRA (E3) on Llama, Mistral, OLMo and Gemma;
      - controls: shuffled weights, OLMo early checkpoints, a Todd function vector.

    *Changed:* we can say "every model tested can find the row; the read-out is one vector away in Qwen3 and improves
    with size". We cannot say "every LLM, one vector". Whether it is "latent" awaits the controls.

16. **Failures follow a pattern-separation law; robust cells are anisotropic** (CIRCUITS §10, $0, 67,332 rows).
    - **Separation flags the failures.** In the huge tables, low separation between states (by input-embedding cosine)
      flags the 37 wrong rows with AUC 0.81.
    - **Near-duplicate names are where the errors sit.** Rows whose state has cosine > 0.3 to another state are 2.3% of
      rows of the 2,048- and 4,096-row tables combined (768 of 32,768) but hold 21 of their 37 errors, 55× the error rate of the other rows. Examples: Sheet/sheet, bra/Bra, illeg/illegal.
    - **Separation does not set the bulk margin** (|ρ| ≤ 0.29).
    - **Size gates the effect:** in tables of 1,024 rows or fewer, the 1,392 low-separation rows made no errors. Those tables have 2 errors in 34,564 rows, both on well-separated names.
    - **Robust cells are 4–7× narrower along name directions than along random ones:**
      - a flip needs 2.5–3× the residual norm along random directions;
      - it needs 0.74 of the embedding norm along name directions (≈0.4–0.5 of the residual at layers 7–17);
      - from layer 21 on, name directions never flip.
    - **Link to Lean's `robust_cell`:** the effective K is about 10 logits per unit norm along names. This is a lower
      bound on the worst case.

    *Use:* screen tables for pairwise state-embedding cosine > 0.3 (it would have caught 21/37). The page can warn on
    such names.

17. **REASON's first counted result: the executor is perfect, but compile and repair fail on held-out templates**
    (reason-s1, step 500, seed 777).
    - **Held-out templates:** 165/384 = 43% against a registered bar of 50%, so P1 fails.
    - **Executor:** 73,529/73,529 real ticks bitwise equal, and every certificate passed.
    - **Same 192 problems:** base Qwen3-4B thinking at 32k gets 17/192 (9%), against ours 75/192 (39%).
    - **No-clock variant:** 33%.
    - **GPT-6.1-sol, tool-off:** 42/64 on the longest cells. It beats us, so P12 fails.
    - **Language passes** (GSM8K 92.25%, MMLU 64.9%).
    - **Failure classes:**
      - wrong table kind or alphabet;
      - notes and quote mismatches;
      - malformed citations;
      - a repair loop: after an error the model writes the repair sentence, then resubmits the identical call;
      - reading collapse at twice the trained notes length.

    *Changed:* the closing result is not yet a banger. The bottleneck is exactly compile, quote and repair, as INSIGHTS
    1–4 predicted. The next round (r4) must merge compile breadth, composites and fixed repair data, and must give RL a
    real budget.

18. **Savant r3 certifies a register machine and nearly all of a universal Lag system zero-shot** (REGVM, predictions
    committed before spend).
    - **RegVM tables, all certified with no training:**
      - ADD 200/200; SUB 200/200;
      - TRIM 66/66, with a thin margin of 0.375;
      - CTRL 54/54; G 128/128;
      - 10/10 fixture programs, 60–246 rows each.
    - **Base Qwen3-4B certifies none of them.**
    - **Real-tick runs so far:** add and mul exact and bitwise.
    - **L(U15,2), rebuilt from the 2024 algorithm:** 2,081 rules. Savant gets 2,078/2,081 rules right, against 355 for
      the base.
      - The whole table does not certify yet. One failing rule is the blank rotation used at step 0, whose symbol has
        249 events against Savant's trained maximum of 8.
      - A remap and recertification are next, then pinned against unpinned.
    - **Remap result:** 2,079/2,081. The two remaining failures sit on the hub symbol, which has 249 events, against
      Savant's trained maximum of 8 per state. This is structural, not a weak name.
    - **Top-up:** 120 steps on random Lag-shaped tables, never Lag rules, is running before recertification. Regression
      checks follow.
    - **RegVM real ticks, zero-shot:** 9/13 runs so far, all exact and bitwise. They include mul 4×4 (1,169 ticks),
      gcd (2,578), sort, factorial, prime and fib.
    - **A gap in the 2024 rule set as published,** written up in REGVM §B.1 as a careful note:
      - a left move from the last tape cell has no rule;
      - witness: tape 00000, head on cell 5, halting at Lag step 460;
      - 15 added rules make it match U(15,2) over 12,355 Lag steps;
      - the 2026 rules are unpublished.

    *Changed:* "certified once" universality is within reach for Savant zero-shot. Its executor generalises from
    2–32-state tables to a 2,081-rule universal system.

19. **Only the pinned cache rule is exact: three ingredients are all necessary** (BIGIDEA H2b; Savant r2; 40 cells ×
    8 runs × 2,048 ticks; predictions F1–F9, with F6 failing by one run).
    - **The pinned cell** (the whole program as persistent prefix, a fresh window of exactly the pair, positions
      restarted) is the only one exact on 8/8 runs.
    - **Drop the program** (StreamingLLM's 4-token prefix): 0/8 in all cells.
    - **Drop the restart:** 1/8.
    - **A sliding k = 2 window:** 5/8.
    - **Re-encode more than the pair fresh** (Delethink/Markovian-Thinker style, c = 4–32): 0–1/8.
    - **At equal budget:** StreamingLLM, H2O and TOVA are all 0/8.

    *Use:* this defends C5 against StreamingLLM, H2O, TOVA and Markovian chunking. The new ingredient is the
    pair-exact fresh window together with the persistent program.

20. **REASON final (reason-s1; every gate landed).**
    - **Executor:** 296,442 real ticks, all bitwise equal to their certified rows.
    - **Held-out:** templates 43% (P1 fails); phrasings 72%.
    - **Gates:** families 733/768, G1 511/512; language kept (GSM8K 92.25%, MMLU 64.9%).
    - **Tokens per correct answer:** 10.4k, against 243k for base thinking (23× fewer).
    - **Same 192 problems:**
      - base thinking 17/192;
      - base Qwen3-4B with real Python, 49/192 (26%; it skipped the tool on 72 and hit the budget on 66);
      - ours 75/192.
    - **Frontier with code tools:** GPT 16/16, Claude 12/16.
    - **Parking is a compile test, not a tracking test.** A clipped counter forgets its past, so the answer is decided
      by the last 4–72 events. That explains GPT's 1k-token answers.
    - **The repair loop is the training data.** 928/967 calls right after an error repeated the failed call verbatim.
    - **The decision to compute is sharp:** P(open) is about 4e-5 inside words and 0.9996 at the call.
    - r4 is now running in Cursor with these fixes.

21. **Semantic events work on trained templates; held-out templates fail at compile again** (SEMANTIC pilot,
    uncounted, $6.08).
    - **Trained templates:** 30/30 with 99.4% labels right; held-out sentence styles 14/15.
    - **Held-out templates:** 1/18, from compile and routing (calls with no program, falling back to the old format).
    - **Control error was zero:** 5,363 real ticks, no certified run different from Python over the same labels.
    - **Misreads are flat across position.**
    - **Base 4B as labeller:** 58% of labels right.

    The r4 data recipe is in SEMANTIC.md §7.

22. **UNIVERSAL final: pretraining builds the row finder in every model; a rank-1 attention edit elicits the
    executor** ($39.88; 10 models).
    - **The finder is everywhere:** a lookup head exists in all 10 base models.
    - **One vector suffices only in Qwen3 4B and up.**
    - **Rank-1 q, k, v, o LoRA, about 0.01% of weights:** 98.2–99.6% of rows (74–110/128 tables) in Mistral, OLMo-2,
      Llama-3.1 and Gemma-2. Its language cost there is larger (+0.10 to +4.80 nats).
    - **Controls:**
      - shuffled Qwen3-4B weights give 0% (no head);
      - OLMo-2 rows with the vector rise along pretraining: 0.8% at 5B tokens, 42% at 84B, 74.5% at the end. The head
        appears between 5B and 84B tokens;
      - a Todd function vector gets 60% vs the learned vector's 99% (cosine 0.03–0.05).
    - **Verdict:** elicitable, not latent.
    - **Long runs:** 59 runs on certified tables, all exact and bitwise.

    *Use:* "every model tested has the finder; a rank-1 edit makes it a pinned executor". This supports leap 1
    ("retrieval is computation"): the finder emerges during pretraining.

23. **CLOSEOUT: the headline cells re-run with every tick real, and the scoreboard costs we must state** ($26.46;
    closeout branch 7284a7fc, research/closeout/CLOSEOUT.md).
    - **Every tick real, Savant r3:** 344,740 ticks bitwise equal to their rows, no argmax differences, three host
      types (one H100 NVL on an AMD host).
      - Addition at 10 / 100 / 1,000 / 4,096 digits: 64/64 exact.
      - Six families at 2,048 events (training phrasings): 96/96.
      - 8,000 digits (n = 4): runs exact 4/4, written answers 2/4 (the same two dropped digits as before).
    - **Theorem P necessity, live:** one edited row (visited about once per 10,000 events) is flagged by the
      certificate; three of four 1,000-event test tapes miss it and run exactly, so a 3,000-event test passes; tapes
      that reach it go wrong at the first visit (steps 741, 1,324). All four predictions held ($0.79).
    - **Costs to state (r2, BBH official, 250 per task):** tracking-3 97.6%, tracking-5 92.8%, tracking-7 79.2%,
      navigate 100%, object counting 86.0%, web of lies 100% (S1 misses 3 of 6 bounds). Boolean expressions: Savant
      writes programs for 227/250 and scores 22% vs base 97.6%; Dyck 2.4%. Answer suffix hurts object counting
      (−9.6) and boolean (−18).
    - **P11 (r2 vs frontier, same 32 items):** at 1,024 events 12/16 vs Claude 12, GPT 14. Every miss is in a family
      still answered in the old plain format; all 14 pinned runs right.
    - **P8 holds:** a planted wrong value in the check table is caught 127/128, controls clean 128/128.

    *Use:* the real-tick numbers replace the lookup-mode ones in RESULTS_LOCK; the necessity demo is the live
    picture for Theorem P's "necessary" half; the boolean/Dyck cost goes in the limitations, and r4 must not write
    programs for stack tasks.

24. **REGVM final: a universal machine runs pinned to 30,000 steps; with history in context it fails by step
    1,811–4,193** ($28.97; regvm branch d5d5cf6c, REGVM.md).
    - **Zero-shot r3 (headline):**
      - every RegVM table certifies with no training (ROM 5/5; P tables of all 10 programs);
      - 13 programs (mul 4×4, gcd ×2, div, sort, prime, factorial, fib, base conversion, boolean formulas ×2) are
        exact, with 11,882 real ticks bitwise equal to their rows;
      - H100 speed: 32 ms per Moore tick, 64 ms per Mealy tick, so a 4×4 multiply takes 52 s.
    - **Lag U(15,2):**
      - **Certificate:** zero-shot 2,078/2,081 rules, 2,079 with remap. All failures sit on a 249-event hub symbol
        (training saw at most 8 events per state). A disclosed post hoc 120-step top-up on random Lag-shaped tables,
        none containing a real Lag rule, gives 2,079/2,081. Neither failing rule is reachable.
      - **Pinned:** 5/5 exact (4 × 8,000 + 1 × 30,000 steps; 62,000 ticks bitwise), about 17 steps/s.
      - **Unpinned:** 4/4 fail at steps 1,811, 2,533, 2,743, 4,193, mostly copying a tape bit wrong.
    - **The top-up regressed RegVM:** TRIM 65/66; P margins fall from 3.5–5.75 to 0.0–1.6; a real-tick run never
      halts. G1, addition, language and GSM8K are unchanged. A joint top-up needs RegVM-shaped tables in the mix.
      Compile numbers lost (the loop stalled).
    - **Left-end gap** in the 2024 Lag rules: REGVM.md §B.1 (witness tape 00000, head on cell 5).
    - **Extra details from the final report:**
      - the base model certifies 355/2,081 Lag rules;
      - the rebuilt rule count is 2,066 as written (2,081 with the 15 left-end rules), against the paper's 1,857,
        which we could not reproduce;
      - the RegVM clock is 41 lines of token copying, and with random ticks it gets 0/60 answers;
      - unpinned failures occur although every rule involved passes its own check in isolation.

    *Use:* the cleanest pinned-versus-history contrast on a universal system: the clock enforces the congruence and
    history breaks it. The hub failure is the size and degree limit of zero-shot certification.

25. **SCAN: Savant r3 adds in log₂ n rounds, every lookup certified** ($10.27; scan branch ec539bba, research/scan/SCAN.md).
    - **Programs:**
      - D: a digit pair maps to K/P/G (100 rows);
      - M: the carry monoid (9 rows);
      - S: the sum digit (200 rows, the certified adder's).
      - **Execution:** packed forwards, with Π's KV shared, a block-diagonal mask and positions restarted per block.
    - **Certificate on the deployed packed path:** a margin certificate (max |Δlogit| across slots, widths and paths =
      0.5; min margin 1.5), so this bound is empirical. K/P/G had to be tokens far down the cosine order (` knew`,
      ` resp`, ` equation`; max cosine 0.02): the separation law in action.
    - **Exactness:**
      - 4,096 digits: 16/16, under both Hillis–Steele (14 rounds) and Blelloch;
      - 100,000 digits: 4/4 (19 rounds);
      - 1,000,000 digits: exact (22 rounds).

      Every lookup lands on its row.
    - **Speed (H100 model time):**
      - 4,096 digits: about 2.2 s with Blelloch (D 0.26 + scan 1.40 + S 0.54), 3.5 s with Hillis–Steele, against
        about 250 s sequential (61 ms per tick);
      - 100,000 digits: about 115 s with Hillis–Steele;
      - L4: 34.5 s at 4,096 digits.
    - **Error detection:** Light's associativity test, run in-model, flags 14 of 18 single-row corruptions of M,
      exactly the ones Python predicted. A planted wrong row changes the sum exactly on its propagation closure.
    - **Browser:** HANDOFF_PAGE.md. KV is about 0.6–0.8 GB per 4,096-query chunk; use smaller chunks in the browser.

    - **Audit (29 Oct, Codex; counterexample replayed):** exact sums hold, 1M digits included. The "2.2 s Blelloch"
      figure is in no record: use about 3.5 s (HS model time, 4,096 digits). "K↔P corruptions never change a sum" is
      false (1009 + 1001 → 3010). Certificate flags were loose on the million and L4 runs. scan-fix is re-certifying
      and retiming.
    *Use:* the speed fix for R5 and the demo; Theorem P² (sufficiency, the necessity of every row, the depth bound) in
    SCAN.md §Theory.

26. **REMEMBER: the latent computer is exact under the pin in all 10 families; the same weights with history fail
    within a few steps** ($≤20; remember branch edea44f5, research/remember/REMEMBER.md, figs/remember.png).
    - **Pin:** 80/80 runs trace-exact at 2,048 events across Qwen3 0.6/1.7/4/8/14B, Phi-4-mini, Mistral-7B,
      OLMo-2-7B, Llama-3.1-8B and Gemma-2-9B (UNIVERSAL's rank-1 edits, no new training). 163,840/163,840 ticks are
      bitwise equal to their certified rows.
    - **Remember** (same weights, tables and tapes; history kept, positions continuing): 4/80 exact at 2,048, and 7
      of 10 models have none. The lower median first error is at **step 3**.
    - **Window** (StreamingLLM-style): 0 exact in all 10.
    - **OLMo-2 checkpoints at 1,024:**
      - 5B tokens: pin 0/4 (tables do not certify);
      - 84B tokens: pin 4/4, remember 1/4;
      - base: pin 4/4, remember 0/4.

      The computer appears during pretraining, and only the pin uses it.
    - **Audit (29 Oct):** the counts hold (80/80 pinned; 76/80 history runs fail).
    - **Caveat a referee will raise:** the edits were learned in pinned format, so "remember" here is a format shift
      that fails at once, not drift at length. A fair arm needs edits trained with history in context (REMEMBER-2).
      BRIDGE already shows that a model trained with history (Savant) drifts at 4k–12k.

27. **REMEMBER-2 (the fair arm): a rank-1 edit trained *with* history cannot make remembering exact, even at its
    training length** (≤$30; remember 4094749c, REMEMBER2.md, figs/remember2.png). Qwen3-1.7B, Qwen3-4B,
    Llama-3.1-8B and Mistral-7B; 1 tape per cell, 4 tables per model; small n.
    - **E-pin under pin:** 16/16 exact at 4,096; 65,536 ticks bitwise.
    - **E-hist** (the same recipe trained on 256-event histories) **under remember:** exact on 4/16 at 256, its own
      training length, and on 0/16 at 4,096. The lower median first error at 4,096 is step 26, against step 3 for
      E-pin under remember.
    - **E-hist under pin:** 7/16 at 4,096. Training with history damages the pinned executor.
    - **Reading:** at an elicitation budget of rank 1, forgetting makes exact execution learnable and remembering
      does not.
    - **Contrast:** with heavy training (Savant r3, a rank-64 LoRA), plain history holds 22/24 to 8,192 with events
      supplied (HEADPIN) but drifts beyond (BRIDGE).
    - **Audit (29 Oct):** the counts hold, but "only the pin is learnable at rank 1" does **not** (unequal data
      exposure, selected evaluation tables, mixed edit classes). A paired fair test is running (remember-fix).
    - **The figure claim must be scoped:** "with a tiny edit" and "at length".

28. **PREDICT (audited 29 Oct; the 28 Oct reading is withdrawn).** An independent code audit
    (predict audit/codex_audit.md), with its counts reproduced by hand, overturns the earlier reading.
    - **No first-use signature up to 8,192.** Every held-row first use that the run actually reached was correct
      (5/5: at 64, 512, 2,048 and 8,192). The "10/23 first-use errors" were early rows (steps < 10), and they were
      the same at every delay. The planned-delay gate checked the oracle trace, not the executed stream.
    - **"Persistence 5,117/5,117" is not history-caused.** Draw 0 failed from step 1 at every delay (64 to 8,192)
      and looped in wrong states. Draw 1 made the same 4 early errors at every delay, then stayed exact for more
      than 8,000 steps. This is a deterministic, delay-independent local failure, and the likely cause is the bare
      table format: it is not Savant's trained format (no chat, tape, metadata, `<exec/>` or `<run>`).
    - **Bugs:** BLOOM's positive exponential slope was scored as decay; a zero P3 shift passed a negative-sign test;
      the base-model crossover was left-censored; the free-run swap omitted the final answer.
    - **Design flaws:** base Qwen and BLOOM cannot do the lookup even at short context, so their Δ fits are only
      logit sensitivity. The swap prompts are teacher-forced, invalid trajectories with format, filler, position and
      distance confounded.
    - **Survives:** the margin of a table lookup across thousands of `.` filler tokens collapses (+9.0 at 256 to
      −13.9 at 32,768). This is format-confounded, so it is not a theorem signature. P3's overall "fails" survives.
    - **Re-run** (predict-fix agent, cap $15): corrected verdicts. P2-v2 runs in the trained format with a
      guaranteed first use up to the context limit, a pinned twin at each error, and a corrupted-history test.
    - **Lesson:** the theorem's signatures are not yet seen at practical lengths, and the paper must not claim them.

## 3. Training lessons (the cleverer recipe)

1. **Executor:** ~50 steps from the base model's latent heads, with executor examples in every later mix. The (b+c)
   mix without them suppressed the latent lookup (37% → 35% of rows, map correlation 0.66).
2. **Language:** Stage 2r from the start (own-style data, general data, KL to base), not as a repair.
3. **Generalization:** generated families with heavy phrasing variation; hold out whole templates; spend there.
4. **Robust names:** random names and tables act like kicks in code space (MULTI Prop 12); train on them.
4b. **Data for the known failures:** wraps that cross the top (clock), multi-step moves, more rules per event,
   case-variant name pairs as hard rows, and one fixed token before Π (WEIGHTS §5).
5. **Kick dose:** σ = measured cell radius at matched push; never a fixed σ carried across hosts.
6. **Process:** merge fresh in every job; hash-check remote sources (three agents hit stale warm containers);
   free-running gates; select only after every term is on; n ≥ 10 seeds before calling a difference.

## 4. Links to v1 (for the bridge section)

| v1 | v2 | status |
|---|---|---|
| closure: map the state back to a code each step | the pin: a fresh block at fixed positions, history evicted | P (above) |
| blindness of the reached-state loss | teacher-forced likelihood is blind to the run-so-far's influence | B, BRIDGE part 1 |
| aimed kick | aimed perturbation of earlier run tokens; can it replace the clock? | BRIDGE part 2 |
| robust cells (robust Myhill–Nerode) | sharp decision steps inside Savant: the destination flips within Δα = 0.05 between two states; noise must reach 1.5–3× the residual norm to flip a tick (CIRCUITS §6) | observed; a figure |
| finite certificate after the snap (S9) | per-row certification over the reachable rows | P |
| snapped tracker certified, continuous one not (LEAP) | token-level snap certified; plain decoding not | consistent |
| in-model trackers (LATENT, BRIDGE L-TF) | Savant: the LLM runs any program it writes | v2 |

## 5. Connections to other fields (revised after the L6 survey, research/prior_art/L6_crossfield.md)

**Theoretical CS: the theorem pair has a 1956 ancestry. This is the strongest framing.**
- **Moore 1956 (Theorem 2).** No finite experiment distinguishes a machine from every other machine. That is the
  ancestor of `no_finite_test_suite`.
- **Vasilevskii 1973 and Chow 1978.** A complete finite test suite exists once the implementation's state count is
  bounded.
- **The pin supplies exactly those conditions:**
  - a bounded state set;
  - the ability to set the state directly;
  - an observable state token.

  Under them, the complete suite collapses to one check per row (Theorem P). The paper should say: plain decoding is
  Moore's case; the pin turns it into Chow's case at its cheapest.
- **Automata Studies (1956).** The book also holds von Neumann's restoring organ (regeneration below the program) and
  Kleene's regular events (defined for networks of model neurons). One sentence in the paper can tie them together.
- **Rabin 1963.** Probabilistic automata with an isolated cut-point δ have finitely many states, at most (1+1/δ)^(n−1).
  This is an early robust Myhill–Nerode, framed as reliable circuits from unreliable parts. v1 must cite it.
- **Turing 1936, §9.** The human computer: bounded observation, finitely many states of mind (argued from
  robustness), and a "note of instructions" to resume one step per sitting. That is exactly the pin's contract. The
  pinned executor is a Mealy machine, not a Turing machine.
- **Checking.** Use translation validation per program for the run, not Blum–Kannan program checking. Use result
  checking (recompile and compare, or a mod-p check on sums) for the compile step, where "certified does not mean
  correct" bites.

**Neuroscience and cognition (analogies, each to be made a measurement where possible):**
- **For the step:** continuous vs discrete attractors (Brody 2003; Inagaki 2019; Panichello 2019). This replaces
  "persistent vs activity-silent".
- **For the pointer:**
  - placekeeping (Altmann 2014): sequence errors and step errors separate as ours do;
  - path integration with landmark correction (Hardcastle 2015): plain decoding is dead reckoning, and the pin is a
    landmark at every step.
- **Serial order** (Henson 1998: position vs chaining). Our model has an unused positional code, so it should fail
  like chaining models. BRIDGE measures this.
- **Pattern separation, not completion.** Weak near-duplicate names are a separation failure, which Ramsauer's
  separation condition predicts. CIRCUITS measures this.
- **The "human Turing machine"** (Zylberberg 2011): a parallel step feeding a serial production cycle, the closest
  description of the pinned executor. Also a one-item focus of attention (Oberauer 2002).
- **Dropped:** theta–gamma (it holds several items; the pin holds one), and Wimmer 2014 as evidence that error grows
  with delay (fixed 3-s delay; use White 1994 and Ploner 1998).

## 6. Bangers (draft; full plan in PAPER_V2_PLAN.md)

- **Open (v1):** no loss on reached states can see drift. Robustness must be built (closure) or probed (aimed
  kick), and both keep neural state exact far past training.
- **Pivot (v2):** an off-the-shelf LLM already contains the lookup; 30 steps switch it on, and a fixed-window clock
  turns it into a certified computer whose every tick is bitwise equal to a checked row.
- **Close (v2, if REASON delivers):** a 4B model that reasons in words, calls its own interpreter mid-thought, and
  gets long computations exactly right where frontier models fail.
- **Fallback close:** certified 1,000- and 4,096-digit addition inside the LLM, with every tick checked.

## 7. Open, in order of payoff
1. REASON's first counted result (does mid-reasoning execution work on held-out composites?).
2. BRIDGE: the drift curve and the kick-vs-clock result.
3. ~~LEAN~~ done: P, P-M, 8a✗, the no-finite-test theorem and Lemma Q are proved; 137 axiom checks were run independently and none uses sorryAx.
4. ARITH re-run Q1–Q3, then r3 on the page.
5. BIGIDEA: the smallest edit that certifies (C2–C4) and "is the clock just attention" (K1–K7, R1–R2).
