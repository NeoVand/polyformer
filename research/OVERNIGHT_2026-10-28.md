# Overnight, 28 Oct 2026: from observations to a better model and a banger paper

Neo, before sleep: collect insights; pin breakthrough observations (theorems to formalise, observations that change
our minds, cleverer training, links to v1); culminate in a better model that reasons and, mid-reasoning, runs programs
in its mind (no clock, or it commands the clock and continues); look inside its head and make great figures; connect to
theoretical CS and neuroscience; begin and end the paper with a banger. Cap: $200 of new spend tonight. Be open: we may
not see what we expect.

## Lines and budget (new spend from 00:55 CDT; caps recorded here before spend)

| line | what | who | cap |
|---|---|---|---|
| running: arithmetic | finish gates on the re-feed path | arith agent | its own $80 (pre-existing) |
| running: circuits | report + 8,192-row run | circuits agent | ≤ $10 more |
| running: weights | adapter + failure anatomy | weights agent | ≤ $10 more |
| running: big idea | H1 tiny edit, H2 clock = attention | bigidea agent | ≤ $25 |
| **REASON** | the model that runs programs mid-reasoning (self-invoked pinned runs, then continues) | new agent | **$90** |
| **BRIDGE** | v1↔v2: drift in plain decoding as the LLM's blindness; can the kick replace the clock? | new agent | **$35** |
| **LEAN** | formalise Theorem P, the Theorem 8(a) counterexample, the Mealy certificate | new agent | $0 (local) |
| r3 + page | export the arithmetic model, enable Addition on the page | export agent + orchestrator | ≤ $5 |
| slack | | | $25 |

Total new: about $200.

## Orchestrator's own work
1. Read every report as it lands; keep this file's status current.
2. Write `research/INSIGHTS.md`: every observation from v1 and v2 classified as theorem candidate / mind-changer /
   training lesson / v1 link / cross-field connection, with evidence and next action.
3. Write `research/PAPER_V2_PLAN.md`: the opening banger, the closing banger, the figure plan.
4. Push the page only for finished, tested features (Neo authorised pushes for the playground).

## Status
(updated through the night)

**01:40** REASON, BRIDGE and LEAN launched as Claude subagents in `polyformer-wt/{reason,bridge,lean-p}`. REASON and
BRIDGE were sent tips from CIRCUITS and PROMPTBOX:
- tape quotes are the held-out failure;
- Π must sit right before the block;
- plain decoding catches pinned up to 2,048, so drift has to be measured beyond that.

**~01:50**
- CIRCUITS report committed (anatomy-circuits c6a09d4c); the 8,192-row run is pending.
- WEIGHTS finished ($2.06 total):
  - the executor lives in about 8M parameters (rank 4 per module), mostly in layers 12–17;
  - RL's null was a step-budget artefact;
  - failure anatomy: clock wraps, tape quotes, row 0.
- `research/INSIGHTS.md` and `research/PAPER_V2_PLAN.md` written.

Settled spend so far, from the ledgers:

| ledger | settled | note |
|---|---|---|
| arith | $37.35 | of its own $80 |
| circuits | $2.12 | |
| weights | $2.06 | |
| bigidea | $5.35 | |

Tonight's new lines (REASON, BRIDGE) have not reported spend yet.

**~01:58**
- **REASON_FORMAT committed (reason 39201657).**
  - Calls are today's blocks, and Π is built fresh for every call.
  - The sources are the question, then the notes.
  - Results can be cited as `first: result k`.
  - Quotes may differ in whitespace only.
  - A new subtracter table also serves as the comparison.
  - Error finals let the model retry.
  - It has a no-clock variant.
  - Approved, with tokens per answer added to scoring.
- **ARITH finished ($41.93 of $80; final adapter `/vol/arith-s1r2/adapter_step500`).**
  - Addition is exact at 10, 100, 1,000 and 4,096 digits (16/16 each). At 8,000 digits, every run is exact and 14 of
    16 written answers are right; the other two dropped a digit when copying the sum.
  - Six families: 739/768. G1: 512/512.
  - Language: GSM8K 91.0%, MMLU 65.8%.
  - Mealy G1: 127/128, 32/32 and 32/32.
- **r3 export requested** from the webexport agent (≤ $5).
- The page's engine already has:
  - the answer budget of digits + 300;
  - the Mealy certificate cached per Π;
  - both forwards bitwise-checked;
  - fixtures current (a0d03c80).

  So once r3 validates, the page needs only the config flip, a test and a push.

**~02:02** REASON fixtures committed (reason ba619ecc). The multi-call page port was launched as a subagent in
`polyformer-wt/site-reason` (branch site-reason, from site-savant). It sits behind `MULTI_CALL = false` and is tested
against the reference fixtures and the stub; it costs $0.

**~02:06** LEAN done ($0, lean-p af8809ad). Proved: P (both directions), cache soundness, the Mealy version, 8(a)
false, **no finite test suite certifies unpinned decoding**, and Lemma Q (1/2 sharp). I re-ran AxiomCheck: 137 lines,
0 sorryAx. INSIGHTS and PAPER_V2_PLAN updated: the theorem pair is v2's headline theorem.

**~02:14**
- **Figures v2-1 and v2-2 drawn** (figs-v2 1e3cb6a7, $0). Polish notes sent.
- **r3 exported and validated** ($2.12). On WebGPU: 200/200 adder rows certified, smallest margin 8.58; fixtures
  replayed bitwise.
- **Disk was full** (2.3 GB free). I removed the local r1 and r2 exports, after checking each matches its Hugging Face
  commit byte for byte. 8.2 GB free now.
- **r3 is uploading to Hugging Face**, and the site config is flipped to r3 with `ARITHMETIC = true`. It is not built
  or pushed yet.
- **BIGIDEA H1, early.** A 2,560-parameter vector at layer 18 gets 99.74% of rows. An 8-vector soft prompt gets 99.6%.
  Certifying whole tables needs about 10⁵–10⁶ parameters.

(Times before 02:18 were corrected on 02:18: earlier entries carried guessed clock times.)

**02:30**
- r3 uploaded to Hugging Face (commit e2a8de05; checked byte for byte against the local export).
- Site config pinned to r3 with `ARITHMETIC = true`: 338/338 unit tests pass, svelte-check is clean, and the build
  passes.
- Live local test (in-app browser, model from Hugging Face):
  - load: 44 s;
  - 10 digits: right, with 200/200 rows certified (smallest margin 8.58) and 11/11 columns bitwise equal;
  - 100 digits: right, with 101/101 columns bitwise equal;
  - 1,000 digits: running in lookup mode.
- CIRCUITS final ($4.13): the size limit comes from weak names (about 1/1,000 rows at 2,048–4,096 rows, clustered on
  fragment names), not from dilution. The 8,192-row run ran out of memory on the L4.
- Figures polished (figs-v2 e9f00a93).

**10:03** Morning. The laptop slept at 02:43 on 1% battery, which killed every local agent.
- REASON, BRIDGE and BIGIDEA resumed. Their Modal jobs had finished on their own.
- **BRIDGE Part 1** ($4.64): plain decoding fails first at the pointer (first error is a misread event in 94–100% of
  failures at ≥8k), then by step drift (events supplied: 77% at 8k). The token snaps the state, not the context; the
  pinned step has zero drift. Part 2 (kick vs clock, about $16) approved.
- **REASON pilot** ($5.97 billed): clock mode 64/108 vs ARITH adapter 8/108; 38/38 certificates; 16,311 ticks
  bitwise equal.
  - Amendment 1 adds item listing, more repair data and more KL data.
  - §12 settles the page-port questions.
  - Counted SFT reason-s1 (500 steps) is running, with the base model thinking at 32k on 544 problems in parallel.
- Page port told to mirror §12. The 1,000-digit r3 test was re-run in lookup mode.

**10:13**
- **r3 is live** (main c7cadb27, deploy succeeded). The page pins Hugging Face revision e2a8de05 and shows the Addition
  suggestion.
- Local production build with the Hugging Face weights, all exact:
  - 10 digits: 11/11 real columns bitwise equal;
  - 100 digits: 101/101 real columns bitwise equal;
  - 1,000 digits, lookup mode: 64/64 real columns bitwise equal, the other 937 from certified rows.
- The page port mirrors §12 (site-reason 9234a050); two inconsistencies in the reference were sent to REASON.
- The main checkout's launch.json was reverted.

**10:27** Page port aligned with REASON §12's round rule (site-reason d61bafe2): 386 unit tests and 4 reason
e2e tests pass, and the fixtures did not change. It stays behind MULTI_CALL = false until the reasoning model is
exported.

**11:04** BIGIDEA finished ($16.54 billed; branch bigidea 768f965e):
- the clock = decoding under a chunk-aligned attention-sink cache policy (24,336/24,336 bitwise);
- the pointer can't live in a bounded window;
- a 2,560-number vector certifies 431/512 tables, and rank-1 certifies 505/512;
- the soft prompt is bitwise language-neutral.

**11:49** Neo awake and asked for directions, better figures, and to start writing v2. Launched:
- figure re-colour (Cobalt and Rose, about half the ink cobalt);
- PAPER-V2 writer (worktree paper-v2 from figs-v2; pending results as marked macros);
- UNIVERSAL: is the latent executor in every LLM? Qwen3 0.6B/1.7B/8B/14B, OLMo-2, Phi, Mistral and others; $25 cap.

Prior art checked:
- Schuurmans, Dai and Zanini 2024 (arXiv 2410.03170): prompted Gemini plus greedy decoding simulates a universal Lag
  system, checked rule by rule;
- Percepta, March 2026: a tiny 7-layer transformer with a WebAssembly interpreter in its weights; not an LLM, no
  certificate.

**12:19**
- RESULTS_LOCK (paper-v2 40562278): BRIDGE Part 2 numbers are macros now, with 3/8 registered predictions holding.
  Two new small disagreements: K3 writes a program on 1 of 400 GSM8K problems (0.25%), and its GSM8K should be
  printed as 365/400.
- Lean round 2 is pending.
- Closeout (unreported evaluations and real-tick reruns), the semantic, compile and regvm designs, UNIVERSAL, REASON,
  and the six prior-art agents are running.
- Budget raise (+$200) asked of Neo; no reply yet.

**12:22** Neo approved the budget raise (+$200; about $400 total since 00:55). Caps sent:
- semantic $40; compile $50; regvm $50; closeout $30;
- BRIDGE raised to $55 (seed 12 plus Part 3);
- UNIVERSAL $25 and REASON $90 unchanged.

**12:25** LEAN round 2 done (lean-p 37866e74; I re-ran it: build ok, 159 axiom lines, 0 sorryAx). Proved:
- composition (Theorem C) with the error decomposition;
- registers (P3) and the cascade version;
- the pointer cannot live in a bounded window (2m ≥ k + 2|S|);
- the cache policy equals the pinned tick;
- robust cells.

research/lean/README.md written for referees.

**12:33** Prior art: L1, L2, L3 and L5 are in, with about 700 verified records. Main overlaps:
- Cai 2017 and Lewandowski/Machado/Schuurmans 2026: Theorem P's sufficiency, and a certified universal machine on Llama-4;
- MAKER, PENCIL, Abbe 2024, the Markovian Thinker and StreamingLLM: the cache policy without a certificate;
- Prakash 2024 and learned task vectors: elicitation;
- NFSM and Bugaud: robust Myhill–Nerode (v1, under review by L4).

Controls added:
- UNIVERSAL cap → $35, adding a random-weights / OLMo-early-checkpoint control and a function vector against the learned vector;
- BIGIDEA H2b cache-policy factorial ($10);
- REASON's Python-tool baselines are mandatory;
- regvm re-scoped to 'their construction, our theorem';
- the closeout necessity demo ($1);
- BRIDGE's Bie error classes ($0).

**12:36** L3 and L6 folded into RESULTS_LOCK (paper-v2 460dc547): terminology table, the theorem pair's
lineage row (Moore 1956, Vasilevskii 1973, Chow 1978), the Turing §9 row, and Rabin 1963 on the robust-MN row (under
review). The derivation 'the pin collapses Chow's complete suite to a transition cover' was checked; the state bound is
made irrelevant by observability. Open: Moore's Theorem 2 wording is verified only via a 2013 quotation; the original
is still needed. Bibliography re-verification running.

**12:39** LEAN: adder and subtracter tables proved correct, and combined with the certified clock
(lean-p aac1f9ee; re-run: 182 axiom lines, 0 sorry, 0 native_decide). Page TODO: show 'table = Lean-proved adder' by
byte comparison of the written rows.

**12:42** L4 theory survey done. Nothing in v1 or v2 is pre-empted outright, but most theorems need narrower
wording:
- T1(a): Simchowitz 2025 has the same shape in imitation learning;
- T2 with k=1, p=0: Brandoit;
- C2: Bugaud, absorbing-state languages only;
- P sufficiency: Cai, Schuurmans, Lewandowski;
- no_finite_test_suite: exact arithmetic only.

Bugaud full texts sit behind OpenReview's bot check; I did not attempt it. Neo needs to download them. The paper agent
is writing V1_PRIOR_ART_FIXES.md.

**12:50** CIRCUITS §10 ($0): a separation law for failures (55× the error rate at cosine > 0.3), and
anisotropic robust cells (4–7× narrower along name directions). Page TODO: warn on near-duplicate state names.

**12:52** REASON counted:
- held-out templates 43% against the 50% bar (P1 fails);
- executor 73,529/73,529 bitwise;
- against base thinking: 39% vs 9% on the same 192;
- frontier tool-off 42/64 beats us (P12 fails);
- failures are compile, quote and repair loops.

No RL under REASON. The r4 plan is needed.

**13:45** Neo approved r4 via Cursor + Grok, plus putting the reasoning model on Hugging Face with a model
picker on the page. Three Cursor agents launched (grok-4.7-xhigh-fast):
- r4 (worktree r4, brief research/r4/R4_BRIEF.md, cap $150);
- the reasoning-model export (webexport, REASON_EXPORT_BRIEF.md, ≤ $8);
- the model picker (site-reason, briefs/MODEL_PICKER_BRIEF.md).

Waiters are running. The reasoning model's name is pending Neo's choice. The red-team prior-art agents (A, B) are
running on the brainstorm candidates.

**13:49** Neo named the reasoning model **Savant-4B Loom**. Planned HF repo: mohsenvand/savant-4b-loom-preview
(proprietary licence, as Savant). Apply the name at upload: folder, README, NOTICE, SOURCE.json, and the picker's
config constant.

**~15:00** CLOSEOUT done ($26.46 of $30; closeout 7284a7fc). 344,740 real ticks bitwise (addition 64/64 at 10–4,096
digits; six families at 2,048, 96/96; 8,000 digits runs 4/4, answers 2/4). Theorem P necessity demo 4/4 predictions.
BBH official scoreboard misses 3 of 6 bounds; boolean expressions 22% vs base 97.6% (cost to state). P11 at 1,024:
12/16 vs Claude 12, GPT 14. INSIGHTS §2.23.

**~15:30** Red-team C ($0; brainstorm/REDTEAM_C.md):
- The method leap is partly done. SemRegex 2018 and Nguena Timo 2026 take equivalence rewards and counterexample repair; Alur 2013 takes snap. Ours: no-gold cross-paraphrase equivalence, in-model certified checks.
- Parallel execution: clear for an LLM's own certified steps in a log-depth scan over a certified monoid table. Adder: 9-row {K,P,G} table. Small monoids only; certify on the batched path.

**~15:45** Neo approved parallel execution ("without it, the demo is not even usable") and asked for one killer
idea that collapses the partial ones. Launched SCAN in Cursor (grok-4.7-xhigh-fast; worktree scan from closeout;
brief research/scan/SCAN_BRIEF.md; cap $15; pid 91729, waiter b1v0n9unb). It runs carry-lookahead addition as a
certified monoid scan, with packed lookups and fault injection via associativity.
- Proposed principle: "exactness is a congruence". The one-sided form gives v1, the clock and Theorem P; the
  two-sided form (syntactic monoid) gives the scan, redundancy for error correction, and types (finite vs infinite).

**~15:50** REGVM final ($28.97 of $50; regvm d5d5cf6c):
- Zero-shot r3 certifies all RegVM tables; 13 programs exact (11,882 real ticks).
- Lag U(15,2), after a disclosed 120-step top-up: pinned 5/5 exact to 30,000 steps; unpinned fails at steps
  1,811–4,193.
- The top-up regressed RegVM margins (TRIM 65/66); compile numbers were lost. INSIGHTS §2.24.

**~16:05** BRIDGE final ($41.13 of $55; bridge 089e28fc):
- Seed 12: C2 passes (×0.35); C1 narrowly fails (0.38 against a ⅓ bar).
- Part 3, the in-model certified pointer: exact on 48/48 tapes to 2,048 events, then the size law (8/48 at 4,096).
  The pilot was not positive, so the counted run was not launched.
- 8 of 72,000 fetch ticks disagree with the packed certificate at near-ties: the batch-invariance hazard, measured.
- All Claude subagents are now finished. Usage diagnosed: about 85–90% from parallel Opus subagents with long contexts.

**~16:10** Before the Claude app relaunch, these Cursor agents are running (PPID 1, own process groups, so they
survive the relaunch):
- r4: pid 65713, log scratchpad/cursor_r4.json
- reasonexport: pid 65715, log cursor_reasonexport.json
- picker: pid 65718, log cursor_picker.json
- scan: pid 91729, log cursor_scan.json

The Bash waiters die with the app. After the relaunch, check them with `ps -p 65713,65715,65718,91729`.
- Correction: COMPILE (Claude agent a68005741d2a9ffff) is still alive, waiting on its Modal curve jobs
  (compile worktree, jobs/curve-sft300.json and curve-sft600.json; collector b6h531to9; last commit 13f89d58). The relaunch kills
  the agent and its collector, but not the Modal jobs. After the relaunch, collect the results from the compile
  volume with its collector script and write them into COMPILE.md (cheap; or hand it to Cursor).

**~17:00** Thesis narrowed after checking our own map (brainstorm/THESIS_CHECK.md):
- Lewandowski 2026 takes "the computer is intrinsic, and a fresh-call sandbox plus per-rule checks makes it exact".
  Abbe 2024 takes the inductive scratchpad.
- Ours: remembering breaks it (the negative theorem plus measurements), the policy inside one run, universality and
  emergence, Savant, and abstraction as the bottleneck.
- Neo's "deliberate sandbox" (learned abstraction) is the open frontier, aimed at r5.
- Launched REMEMBER in Cursor (worktree remember from universal; $20 cap; pid 2747): pin vs remember vs window on all
  10 models, plus OLMo checkpoints.

**~17:40** REDTEAM_D (brainstorm/REDTEAM_D.md):
- C1 "learned what to keep, proved exact, doesn't exist" is FALSE: Brandoit, Bugaud, Nerem COLT 2026.
- C2 holds only as a Savant novelty claim. Cite Recursion of Thought (ACL 2023) as the closest precedent.
- C3 is open only for a pretrained LM reading natural language: certify that the kept state is sufficient.
- THESIS_CHECK corrected.

**~18:00** Neo approved the theory arm and sharing the atlas with Codex and Gemini ("push for creativity").
- Worktree `theory`, with briefs research/theory/ATLAS_BRIEF.md and ROUND1_BRIEF.md.
- The atlas agent runs in Cursor (Grok, pid 11858). It writes ATLAS, ANOMALIES, TENSIONS and GRAVEYARD.
- Driver `research/cursor_logs/run_theory_round1.sh` (task bna97axx0) waits for ATLAS_DONE, then runs Codex
  (gpt-6-astra, high), Gemini (4 Argon high) and Grok independently on the bundle, each with a 2-hour watchdog.
  Output goes to research/theory/round1/{codex,gemini,grok}.md.
- Both CLIs passed a smoke test. Then I judge with the kill gates and add my own conjectures.

**~16:55 CDT** Loom published: HF mohsenvand/savant-4b-loom-preview, revision 97828505 (17 files sha256-verified,
3,344,318,429 bytes). The picker config is filled (site-reason, committed, not pushed). Unit 395/395, e2e 29/29.
- Live test in the browser pane (Apple GPU): loaded from HF in 54 s.
- "Two stores": answered in words, correct (1,370), 11 s.
- "Parity, then a sum" (bits 1011, then 48+17): two calls, both certified and exact, answer 65 correct, but
  **223.5 s**. It wrote and certified a 200-row adder from scratch to add 48+17, and called a program for 4 bits.
  This is the R5 speed and judgment problem in one example. Fixes: a library adder with a cached certificate, no
  programs for short sums, and the scan.
- SCAN smoke: 32-digit sum exact under both scans; packed forwards about 0.16 s per 4,096 queries on an H100 (a
  projection of about 2 s of model time at 4,096 digits; counted run pending).

**~17:20 CDT** Neo approved the push: site main c7cadb27 → f41dc4ec (picker with r3 + Loom).
- Neo's notes for R5:
  - a 210-digit addition still writes the long adder table;
  - "how do I know it's right?";
  - the run panel is unclear;
  - make the UI more useful, not more text;
  - deferred until R5.
- Theory round 1: Codex, Grok and Gemini are in; Opus is rerunning without tools (agy needs that headless).
- Convergences (independent minds):
  - (1) hub-degree law (3/3);
  - (2) error clustering by self-reinforcement or persistent bad rows (3/3);
  - (3) the kick trades pointer for step (3/3);
  - (4) monodromy blindness: one-step kicks miss cycle products (Grok, Gemini);
  - (5) quote trap / erasure–quoting crossover (Grok, Gemini);
  - (6) Codex: margin plus compactness makes history finitely testable in principle. This refines our theorem
    pair's quantifier.
- My synthesis for round 2: the joint spectral radius (Blondel–Tsitsiklis undecidability; finiteness-conjecture
  counterexamples) may be the common root of blindness and no-finite-test, with restoration as what makes it
  finite.

**~17:55 CDT** Neo: "get rid of the history".
- Both HF repos now have short model cards, a trimmed NOTICE and SOURCE.json deleted. Old files are kept privately
  in research/records/hf_source/.
- Both squashed to one commit: r3 41b273e3, Loom bf72f6bf. All 16 files per repo sha256-verified.
- The site is re-pinned and pushed: main f41dc4ec → 2c9a2882 (unit 395/395, e2e 29/29, r3 loads live in 42 s).
- **Caveat:** old commit hashes still resolve by direct URL (orphaned objects, probably until HF garbage
  collection). Only deleting and recreating the repos removes them for certain, and Neo must do the delete himself.
- r4: the Cursor agent died on a connection drop after reserving the counted 400-step SFT. Resumed with
  `--resume 7fbcfaeb…` (pid 28142).

**~19:00 CDT** SCAN done ($10.27): certified carry-lookahead scan.
- Exact: 4,096 digits 16/16, 100k 4/4, 1M exact.
- 4,096 digits in about 2.2 s of H100 model time (Blelloch), against about 250 s sequential.
- Margin certificate on the packed path; the in-model associativity check flags 14/18 corruptions, as predicted.
- INSIGHTS §2.25.
- The Codex referee found Opus R1★ false as stated; its valid core is a Hahn-style lemma.
- E3 is running ($0).
- HEADPIN launched (Cursor, $25 cap, Neo approved): head-level pin, requote-W, delayed first use.
- ~19:40 CDT. Neo: "why aren't we at the whiteboard like a graduate student?" Started actual derivation work:
  - research/theory/WHITEBOARD.md, the orchestrator's first pass on size-independent reasoning: composition (S) is
    easy; the bound is necessary (our no_finite_test); the real problem is one mind with two channels
    (correlated misreadings); a unifying finite-teaching-set conjecture;
  - Cursor `wmethod` (lean-p, pid 48689): the W-method, bound necessity and Theorem S in Lean;
  - Cursor `whiteboard` (theory, pid 48942): an iterative session on §4 and §5 with exact small-case computation.
- ~20:00 CDT E3 done: wrong program 23% of failures (60/264), all caught by ≤64 short cases (57/60 by 16) with a correct oracle; quotes 41% and truncation/format 34% untouched. Next: is the model's own word-answer a good oracle (about $5).
- ~20:30 CDT. Whiteboard session closed both targets (WHITEBOARD_LOG.md):
  - §4: after agreement, the irreducible certified-but-wrong floor is ργ/(ργ+1−ρ), equal to ρ when the word channel
    shares the compiled reading. The gap above the floor decays as λ^(−d) in the disagreement depth d, and Chow suites
    have depth 1, so there is no exponential gain from suite size. Two channels help only through the collision law
    of their errors.
  - §5: the literal conjecture is false, and nothing goes beyond Goldman–Kearns, Gold or de la Higuera.
- Lean (lean-p dd1aabf2, 0 sorry):
  - the W-method as written is FALSE for final-output Moore machines without ε in W (`literal_suite_insufficient`);
  - the corrected `w_method`, `bound_necessary` and `theorem_S` (W-method plus pinned regeneration) are proved.
- Sent Neo DEEP_READING_QUESTIONS.md (19 papers, questions A–F, synthesis) to run on another machine.
- ~20:45 CDT REMEMBER done: pin 80/80 exact at 2,048 in 10/10 families (163,840 bitwise ticks); remember 4/80 (first error at a median of step 3); window 0. OLMo: the computer appears between 5B and 84B tokens. Caveat: edits were trained pinned, so a fair remember-trained arm (REMEMBER-2) is needed. INSIGHTS §2.26.
- ~21:25 CDT HEADPIN done ($1.14): NEGATIVE. The committee pin (31 heads) keeps 12/24 at 1,024 and 0/24 at 4,096 and 8,192; requote-256 gets 0/24 at 8,192 (it fails at the first insertion, out of distribution); a random pin gives 9-10. Plain full history (Savant r3, events teacher-forced) is state-exact 24/24, 24/24 and 22/24. The per-head mask identity passed bitwise. Lesson: untrained interventions break the executor; memory-keeping must be trained, not masked.
- ~20:40 CDT E4 done: NEGATIVE for model-as-oracle.
  - Loom answering short cases in words: per-case accuracy 15% (class a) and 12% (controls); catch 13/60, false alarm 35/60. A paraphrase does no better. Base Qwen thinking: accuracy 7-9%.
  - Many suites cannot be rendered (442/959 class-(a) cases skipped: coin/adder alphabets are not the question's words).
  - Loom often wrote a program despite instructions.
  - Short-teaches-long stands only with a human (or stronger) oracle; self-certification fails as built.
- ~21:00 CDT. Neo's deep-reading report arrived (theory/research/theory/DEEP_READING_REPORT.md; 26k words). Key:
  - **Candidate 1:** fixed-margin causal softmax transformers with bounded logits realise only definite-modulo-length
    languages. This is the transformer analogue of Brandoit's affine theorem and of Maass–Sontag, and the theorem
    form of "remembering breaks it".
  - **Causal influence rate** Θ(log^{L−1} n/n), tight via the Cesàro matrix (unpublished per the report). Horizon
    T* ≈ εe^Δ.
  - **Candidate 2:** an architectural budget gives the fault domain, with an exponential white-box vs black-box
    certification gap.
  - **Candidate 3** equals our whiteboard §4 floor (independent confirmation).
  - **Unifying statement:** (F) fault domain, (C) coverage, (I) independence; the only non-classical part is (F),
    produced by architecture.
  - Launched a prior-art check on C1, the rate and C2 (Claude agent), and PROOF1 (Cursor, pid 81066) for a rigorous
    proof of C1 with numerics.
- ~21:20 CDT. Prior art on C1/C2 (theory/research/theory/CANDIDATES_PRIORART.md):
  - **C1 encoder form KILLED** by Köver, Butoi, Svete, Hahn & Cotterell 2026 (2606.08768).
  - **C1 causal/decoder form PARTLY and ours:** the decoder case is explicitly open per Hahn & Rofin 2024. Ours is the
    causal influence bound O((1+ln(n/p))^(L−1)/n), which gives margin recognition only on (n, w_n).
  - **ALiBi form CLEAR.**
  - **Converse PARTLY** (Li & Cotterell 2026; Nowak 2026).
  - **Cesàro construction** published (Chowdhury 2026); the general causal upper bound is not.
  - **C2 CLEAR** (frame it as a neural instance of the Elkind et al. grey/black-box separation).
  - Added the must-read papers to FOLLOWUP_READING.md.
- ~21:50 CDT REMEMBER-2 done: E-hist under remember gets 4/16 at 256 (its training length) and 0/16 at 4,096; E-pin under pin gets 16/16; E-hist under pin gets 7/16. INSIGHTS §2.27.
- ~21:35 CDT Codex referee on PROOF1: the upper bound and the main theorem (a)/(b) are TRUE (repairs: RoPE as a position-dependent σ family; quantitative k); sharpness is true with a new width-2 witness; the autoregressive corollary holds only for specified pairs (common continuation, first use). The 'tokens help only via the last token' claim is FALSE (redundant-copies counterexample). Revision proof1v2 launched.
- ~22:00 CDT. Follow-up report (theory/research/theory/FOLLOWUP_REPORT.md) is the theory package:
  - **Theorem 1:** causal, bias-free → eventually 1-definite modulo length; ALiBi → definite, with a soft converse.
    Every hypothesis is necessary, with minimal witnesses.
  - **Theorem 2:** (i) first use; Cor. 2.1: bias-free decoders cannot read their own previous state beyond n1(γ);
    Prop. 3: errors are permanent (this matches T4's 360/360); Prop. 4: copying works only from bulk statistics or
    within the window; (iii) the dividing line: bias-free needs bounded total context, ALiBi bounded look-back, and
    a reset context provides both.
  - **C2:** the reset harness has a finite closed reachable set; white-box = |Q_R||Σ| passes (our Theorem P);
    observability matters.
  - **C4:** within bounded-logit transformers, the only non-trivially certifiable autoregressive route is the reset
    harness.
  - **Weakest point:** horizons scale like e^{2AL}, so the constants are vacuous; the shape and qualitative
    predictions are testable.
  - Launched PREDICT (Cursor, $25): P1 decay shape (RoPE vs ALiBi), P2 swap test and first use, P3 temperature on
    the lookup heads.
- ~23:55 CDT PREDICT done. Holds: error persistence 5,117/5,117, first-use elevation, margin collapse +9→−14, pin follows the table. Fails as registered: the P1 shape (exponential beats power for Savant), the P2 swap direction (it follows its own history 100% when recent, falling with distance; consistent with Prop 4 post hoc), P3 temperature. INSIGHTS §2.28.
- ~00:10 CDT Neo: double-check before believing. PREDICT conclusions withdrawn pending an audit. My own checks: P2 errors are keyed by (fed-back state, event), which is correct; the P3 scaling is skipped when a KV cache is passed (to verify); the P1 base-Qwen and BLOOM arms cannot do the task (design flaw); the P2 format may be out of distribution. Codex audit launched (predict/research/predict/audit/).
- 00:10 CDT: PREDICT audit back (Codex; counts reproduced by hand). The 28 Oct reading is withdrawn; INSIGHTS §2.28 is rewritten. The predict-fix Cursor agent (pid 29635) was resumed with PREDICT_FIX_BRIEF.md: correct the verdicts, then P2-v2 (trained format, guaranteed first use, pinned twin, corruption test; cap $15). Four Codex audits launched (REMEMBER 1+2, HEADPIN, SCAN, E3+E4) in research/audit/codex2/.
- 00:17 CDT: Codex audits of SCAN, REMEMBER, HEADPIN, E3/E4 back (research/audit/codex2/out_*.md). SCAN: exact sums survive; 2.2 s unsupported (3.52 s HS); K↔P theorem false (replayed: 1009+1001→3010); cert gates loose. REMEMBER: counts survive; 'only pin learnable at rank 1' does not (unequal exposure). HEADPIN: identity gate bypassed the committee kernel. E3: 58/60 within 64, not 60/60; E4 'no self-oracle' does not survive (interface confounds). Fix agents launched: scan-fix 32678 ($8), remember-fix 32680 (fair test, $35), headpin-fix 32682 ($8), e3e4-fix 32685 ($10).
- 00:18 CDT: RESULTS_LOCK (paper-v2) updated with 28–29 Oct rows and audit status, committed. Codex --search prior-art run on the decoder theorem (research/audit/priorart_dec). lean-dec Cursor agent (pid 35090) formalising PROOF1's discrete core.
- 00:19 CDT: r4 counted R1 175/384 (45.6%) vs REASON 165/384 (+2.6, prediction ≥+5 missed); R2 phrasings 53/128 vs 24/128 (+22.7, held). DAUDIT agent (pid 35729, worktree r5audit, cap $20) building the disappointment-audit battery and running it on r4, Loom and base.
- 00:28 CDT: prior-art search on the decoder theorem back. Xiang 2026 (arXiv 2610.24133, 16 Oct) has our prefix-forgetting rate and pair bound (verified on arXiv). The class theorem stays ours as far as searched. The W-method ε∈W is known (Kocsis & Rot). RESULTS_LOCK and theory TAKEN.md updated.
- 00:32 CDT: headpin-fix done (a57f212e): subset kernel matches eager softmax (max gap 5.6e-9), committee counts stand, E0 table 2 recomputed (H4 still fails), cached pin now rejected; $0.08. Claims narrowed in HEADPIN.md §7.
- 00:42 CDT: live prior-art search on all claims back. Blindness PARTIALLY KNOWN (Whitney 1934 gives the finite-view core; Green et al. 2026 arXiv 2606.12990 gives the objective-level underidentification for recursive forecasting; verified). Sharp drift time NEW. Theorem P iff, explicit no-finite-test decoder, decoder class theorem: ours. System NEW as far as searched; Xu et al. 2026 (universal computer, small model, stepwise) to cite. RESULTS_LOCK §8.7.
- 01:06 CDT: r4 closed (1e1448c0, $78.70): clock R1 175/384 vs 165/384; targeted cells 53/128 vs 24/128; R2 117/160 vs 115/160; no-clock worse (93 vs 128); WikiText ppl 19.3 vs 13.8; families 700 vs 733/768; compile held-out 41/88. CORRECTION: my earlier '19%→41% on reworded questions' was the targeted cells, not R2. Codex audit of r4 launched (audit/codex2/out_r4.md).
- 01:13 CDT: r4 audit back: counts reproduce; targeted gain is all coin (43 vs 14); two RL bugs (numeric rows missing from reward; no KL, so ppl +40%). Decision: do not rerun r4; carry fixes into R5. R5_SPEC.md drafted (research/).
- 01:17 CDT: e3e4-fix done (theory 2b2075dc, $2.53 rerun): E3 57/60 ≤16, 58/60 ≤64; E4 fair rerun: self-oracle catches 21/60 with 37/60 false alarms (O1), base 20/60, 29/60. Narrower 'poor self-oracle' claim; unaudited.
- 01:27 CDT: lean-dec done (a114d08b): decoder theorem machine-checked from the one-layer recurrence onward; orchestrator reran lake build + AxiomCheck, 0 sorryAx.
- 01:32 CDT: Neo: 'move the needle'. NEEDLE round launched (theory/research/theory/needle: FRONTIER.md map + BRIEF + six lenses; Codex --search, Gemini, Opus, Grok, two outsiders; 150-min watchdog). WEBSCAN feasibility agent (pid 64581, webexport) for packed certified addition in the browser.
- 01:52 CDT: needle round done (6 minds, ~200 KB in theory/needle/round). Convergence: certified pushdown via KV stack policy (Gemini H1, Grok H1, Outsider A H1 one-bets; Opus H4); predictive horizon from collisions (Opus H2, Gemini H2, Outsider B H2, Grok H4); restoring-organ voting threshold (Outsider B H1); identity-word restoration (Codex H1). Kill gate (Codex --search) on C1–C8 running: research/audit/needle_gate.
- 02:06 CDT: needle gate back: C1 pushdown NARROW (system: certified canonical-KV VPA interpreter; Cai 2017 states the principle; canonical frames are the crux), C2 horizon NARROW (predictive, causally validated collision-hazard model; Jelassi, Guo et al. 19 Oct 2026, Giorlandino & Goldt), C7 identity-word restoration NARROW (strongest research question; Wang et al. 2610.27628 PAR), C3-C6, C8 KILL. Launched STACK (pid 73537, cap $20) and HORIZON (pid 73539, cap $15) kill tests.
- 02:06 CDT: needle round 2 launched (four minds; theory of trained executors: canonical frames, origin of the lookup, compilation, switching on, learned restoration); GATE1 included.
- 02:15 CDT: predict-fix died on reconnect ('Unknown model ID: grok-4.7', transient; model still listed) after registering P2-v2 (1504bf63); resumed pid 77493.
- 02:21 CDT: needle round 2 back. Candidates: G1 Lyapunov-vs-JSR (Gemini Part I; periodic words break trained trackers; constrained-JSR certificate for group automata), G2 faithful-rank (Gemini II, suspicious), G3 compiler semantic entropy + questions + length-uniform conformal separation (Opus), G4 switching-on conflicts (Codex), G5 cold-slot canonical frames (Grok; overlaps STACK). Gate 2 running (research/audit/needle_gate2).
- 02:29 CDT: gate 2 back: G2 KILL; G1 NARROW (sound neighbourhood certificates for trained group trackers = D3), G4 NARROW, G5 NARROW (in STACK), G3 NARROW heavily. Launched CERT (pid 82468, CPU, block-k certificate on aimed-tube trackers) and ASKQ (pid 82474, compile coverage c16, cap $10).
- 02:30 CDT: predict chat 65ff6de4 cannot resume ('Unknown model ID: grok-4.7'); P2-v2 job p2v2-savant-r3 is running on Modal (launched 05:37 UTC, $15 reserved). Fresh predict-collect agent (pid 83184) to collect and score. Gotcha: old Cursor chats may fail to resume after model-ID changes; start fresh with a takeover brief.
- 02:37 CDT: Cursor rejects new grok-4.7 sessions ('Unknown model ID: grok-4.7', both fast and non-fast). CERT relaunched on gpt-5.6-sol-xhigh-fast (pid 85629). Running grok agents continue but may die on reconnect; relaunch fresh on Sol with a takeover brief.
- 02:43 CDT: Neo: no more Cursor. All Cursor agents stopped; nine tasks relaunched with takeover briefs on Codex (scan-fix, horizon, cert) and agy (Opus 5.5: remember-fix, daudit, webscan, stack; Gemini 4 Argon: askq, predict-collect). RESUME.md has the table.
- 02:54 CDT: DAUDIT done (r5audit 299ee303, $8.51): read r4 0.60, Loom 0.54, base 0.73; top disappointments: certified-but-wrong, confident after failure, compile failures, loops, made-up big arithmetic, slow, input reading. R5_SPEC.md updated with a tiered build plan.
- 02:54 CDT: R5 harness agent (agy Opus, pid 96221, branch r5-harness, no push): honest failure, BigInt check, when-to-compute, read-in-place, certificate view, grammar constraint.
- 02:56 CDT: HORIZON done (horizon 36f43bb4, $0.87): collision hazard beat short-fit baselines on held-out Part 1 tapes but overpredicted survival at 8k/12k; constructed tapes did not show the collision-vs-length contrast; frozen hazard lost to all four baselines prospectively. KILL as a law; no horizon claim in the paper.
- 03:06 CDT: agy Opus quota exhausted (resets ~3.5 h): stack and r5-harness died; relaunched both on Codex. remember-fix, webscan (agy Opus) still alive; webscan: Brent–Kung 4,096 digits exact in 337 s on M4.
- 03:08 CDT: PREDICT P2-v2 collected (predict 34188284, $4.59; unaudited): trained format competent 16/16 (bare 0/16, OOD confirmed); first-use margin 15.1 → 11.1 (8,192) → 10.75 (~10k), non-monotone, registered falsifier fires; corruption never copied (0/16), table followed always; pinned twin fixes 3/3 full-history errors. Codex audit launched (audit/codex2/out_p2v2.md).
- 03:11 CDT: remember-fix (agy) hit the quota; relaunched on Codex to collect the running Qwen3-4B evals and the 1.7B carry retry.
- 03:14 CDT: P2-v2 audit: all four held rows are self-loops (hold/stay), so first-use and corruption results do not test table reading; unequal gates (16 vs 25 events); pin success conditional on gate. My message to Neo ('trusts the table') was wrong; corrected. Not rerunning (theory signatures are not in the paper).
- 03:16 CDT: webscan (agy Opus) hit the quota; relaunched on agy Gemini Argon with takeover (uncommitted Brent–Kung 337 s at 4,096 digits).
- 03:24 CDT: CERT KILL (cert 543cebaa, CPU, $0): 30 trained checkpoints, k=1–6, 540 block/shape candidates; no certificate; smallest radius gap 6.1× (S5), 132× (Lean). Fable 5.1 meta thread could not start: sessions cannot be started over Remote Control; brief ready at research/meta/META_BRIEF.md.
- 03:26 CDT: scan-fix done (scan 4b84ab70, $6.72): retimed end to end, 4,096 digits Blelloch 3.2 s H100 / 19.0 s L4; 100k Blelloch 70 s H100; all retimed sums exact; H100 certification passes, L4 margin certificate FAILS (per-runtime certificates needed).
- 03:33 CDT: REMEMBER fair test done (remember 45fba394, $23.86, unaudited): history IS learnable at rank 1 (1.7B 9/9,9/9,8/9; 4B 8/9,6/9,5/9 at 256/1k/4k under remember); pin 9/9 everywhere. 'Only the pin is learnable' refuted. Fable 5.1 meta thread started (local_80859e74…, model switched to claude-fable-5-1 from its next turn).
- 03:34 CDT: live check of r5-harness on Loom: 2+2 direct+checked (good); typo'd 20-digit sum: model rewrites the 200-row adder (~4 min) and quotes the template anchor 'What is', honest refusal, retry rewrites again. Launched r5-harness2 (Codex): library splice + anchor-constrained decoding.
- 03:38 CDT: WEBSCAN done (webexport aca19d25, local): all exact vs BigInt; Brent–Kung 64/256/1k/4k digits = 4.4/14/67/337 s; distinct-block memo mode 4,096 digits in 9.3 s (HS, 357 distinct lookups). Top-2 graph patch 1.6–1.8× faster forwards.
- 03:40 CDT: STACK done (stack d7df79cf, $11.76, unaudited): 488/488 rows certify zero-shot; canonical executor exact at depth 4,096 and 20k symbols, 135,078 steps bitwise; BBH boolean 250/250 with a HOST compiler (ast) and host-maintained stack; history decoding with host-supplied top frame also mostly exact to d512; base thinking fails at depth. Codex audit launched.
- 03:46 CDT: STACK audit: accuracy survives (488/488, 135,078 steps, BBH 250/250 host-compiled); 'bitwise' = numerical equality; L4 timing on a 9-cell subset. Recorded as ST1 in RESULTS_LOCK.
- 03:53 CDT: live re-test of r5-harness2: typo'd 20-digit sum now right ('The sum is 111111111011111111100', independent check agrees), model wrote 70 tokens (library splice), ~3 min first time (200-row device certification, now cached). ASKQ KILL (askq f85ad356, $2.33): c16 coverage 45/88 (r4) and 25/88 (Loom); wrong 200-row tables at >99% token confidence. Neo: design the in-model language myself with Fable for wisdom, Astra/Argon for research; question every unquestioned assumption.
- 04:03 CDT: WEFT P1 (orchestrator, $~1, unaudited): base Qwen3-4B certifies dmul 100/100 (margin 4.0), cmp 100/100, dadd 200/200 with a two-prompt hybrid (margin 3.75) — no training. Savant r3 worse (dadd 183/200). Native digit ALU exists; the 200-row adder is unnecessary.
- 04:08 CDT: WEFT P3 (H100, unaudited, ~$1): base Qwen3-4B, no training, no tables: certificate dadd 200/200, dmul 100/100, band/bor 4/4 in 1.9 s; add 1000+1000 exact 1.3 s; mul 100x100 exact 9.4 s; 2^200 18.5 s; 50! 15.3 s; 958,182 primitive calls, 0 mismatches.
- 04:09 CDT: Fable meta report + LANGUAGE_NOTES in (research/meta/); Astra/Argon prior-art maps in lang/research/lang/. WEFT draft 2 committed. Neo's constraints (via Fable): one week, $1–2k.
- 04:26 CDT: WEFT P4 KILL: base Qwen3-4B zero-shot Weft-surface programs 20/88 (21/88 with anchor snap) vs r4 tables 41/88; failures are adversarial rule-text comprehension. Language fixes size/speed/arithmetic/certificates, not compile of tricky rules.
- 04:35 CDT: WEFT P5 (H100, unaudited): SST-2 872 items, base Qwen3-4B: judgments 0.944 in 2.95 s; in-model count 423 = exact sum of judgments in 3.3 s (true 444); direct counting (thinking) exact at N=100 (182 s), no answer at N=200 (12k tokens). Advantage = scale+speed; demo should use extraction-type judgments.
- 04:49 CDT: WEFT on device: public onnx-community/Qwen3-4B-ONNX q4f16 on M4 WebGPU certifies dadd 200/200 (prompt B, margin 3.06), dmul 100/100 (5.19), band/bor 4/4. Browser demo can run the untouched public model.
- 29 Oct ~09:30 CDT:
  - Neo questioned the direction ("isn't this already known?").
  - NEO_CONDITIONS.md written.
  - Fable's NEW_MODEL.md (Savant-R) is in.
  - Prior-art gate savant_r_gate: NARROW, "mostly known". Meridian (Apr 2026) and Percepta are the closest neighbours.
  - Packed browser runtime bench on M4: 2^200, 30!, 1,000-digit add and count-872 exact, 0 mismatches (results in
    lang/results/weft_packed_m4.json). The browser build is paused.
