# META_REPORT: why the theory kept failing, and how to do it right

Written 29–30 October 2026 for Neo, from the record on this machine. Read-only study; nothing was spent or launched.

**Labels used throughout.** *Verified* means I read the source (a file in the record, or a paper/essay I fetched or
whose scanned text I read). *Unverified* means I rely on a secondary summary or a search snippet. Where I give an
interpretation rather than a fact from the record, the paragraph says so.

**What I sampled.** All 60 memory files in `~/.claude/projects/-Users-neo-repos-polyformer/memory/` (every phase from
18 to 29 Oct, including every **Why:** line); `research/OVERNIGHT_2026-10-28.md` and `research/INSIGHTS.md` end to
end; the 29 Oct audits (`research/audit/priorart_dec/out.md`, `priorart_all/out.md`, `codex2/out_r4.md`,
`needle_gate2/out.md`) and the needle material in `polyformer-wt/theory/research/theory/` (FRONTIER, TAKEN, GRAVEYARD,
BRIEF, BRIEF2, the six lens files, GATE1, BULLETIN_1/2, ROUND1_BRIEF, ATLAS_BRIEF, the headings of ANOMALIES,
TENSIONS and Neo's DEEP_READING_REPORT, plus two full mind outputs: `round/codex.md` and `round2/opus.md`);
`RESULTS_LOCK.in.md` §5 and §8 in `polyformer-wt/paper-v2/paper/jewel/`; `DAUDIT.md` in `polyformer-wt/r5audit/`;
the planning documents `PLAN.md`, `NOVELTY.md`, `LEAP.md`, `WHITEBOARD.md`, `WHITEBOARD2.md`, `MORNING.md`,
`QUESTIONS.md`, `SUBMISSION_PLAN.md`, `CONTRIBUTIONS.md`, `HANDOVER.md`, `PAPER_V2_PLAN.md`, `R5_SPEC.md`,
`brainstorm/{CANDIDATES,FACT_SHEET,THESIS_CHECK}.md`, the head of `brainstorm/REDTEAM_D.md`, `debate/03_redteam.md`,
the outlines of `THEORY.md`, `PRIOR_ART.md`, `LITERATURE.md`, `EXACTNESS.md`, `COURSE.md`, the refuted-statement
lines of `THEOREMS.md`; the agent briefs `research/cursor/COMMON.md` and `research/r4/R4_BRIEF.md`;
`cursor_logs/RESUME.md`; three sibling hand-over notes (validate-blocks, frontier2, proofs-positioning); the git log
of every ref; and all 652 ledger files, de-duplicated by Modal call id. I did not read the ~700-record prior-art
surveys L1–L6, the 157 KB ATLAS, the large Cursor/Codex logs, or the paper text itself.

---

## 0. The record in numbers

These are facts from the record, not interpretation.

| Measure | Value | Source |
|---|---|---|
| Span of the repository's history | 18 Oct 20:44 → 29 Oct 03:33, **12 days** (the "four weeks" includes the pre-repo April-2023 notebook work, reading and subscriptions) | `git log --all` |
| Commits, branches, worktrees | **1,913 commits** on **108 branches**, **91 worktrees** (39 `claude/*` sessions, ~55 Cursor/Codex/agy worktrees) | `git log --all`, `git worktree list` |
| Commits per day | 1, 31, 98, 92, 91, 225, 271, 207, 161, 291, **353**, 92 (18→29 Oct) | `git log --all` |
| Night work | **39 %** of all commits land between 22:00 and 06:00; 02:00–03:00 is the single busiest hour (165 commits) | `git log --all --date=format:%H` |
| Modal spend on the ledgers | **$2,655** over **2,672 unique calls** (652 ledger files); 2,430 completed, **210 (7.9 %) errored, cancelled, abandoned or timed out**; H100s took $1,505 (57 %) | `scratchpad/ledgers2.py` over every `modal_ledger.json`/`*_budget.json` |
| Spend by day | 20 Oct $79 · 21 $270 · 22 $99 · 23 $164 · 24 $181 · 25 $240 · 26 $375 · **27 $633** · 28 $367 · 29 $123 (+$123 undated). **61 % of the spend fell on 25–28 Oct**, the "launch" days | same |
| Gap to Neo's ~$3,500 | ~$850 is not on any ledger I can find. Cursor deleted ~19 worktrees on 27 Oct (`cursor-worktree-cleanup.md`); the early Newton/LM grids used a harness with no ledger (`polyformer-newton-attention.md`: "well under $200") | interpretation |
| Largest ledger lines | FIVE $411 · EXEC_LM $342 · LOOPS+EVENTS $263 · ASKQ $156 · CFD cavity ~$127 (reported) · drop-exec $104 · FRONTIER2/3 $109 (reported) · BEYOND $76 · STORIES $68 · LATENT-1 $63 · PREDICT $64 · LEAN_N $52; a further **$465** sits in generic `modal_ledger.json` files I could not attribute to a study by path | same |
| Distinct research programmes started | **≥ 25** named programmes in 12 days (operator tournament, Newton, free-field, S0–S2, S6, GROUPS, BEYOND, ARC, LOOPS, EVENTS, REVISE, T1, T2, BLOCK_THEORY/K0⋈H, VALIDATION, ENERGY, SELFSTATE, INVARIANCE, PARA, LEAN_S1/H/S/N, EXEC_D/LM, METRIC, MECHANISM, INMODEL, STORIES, UNIFY, LATENT-1, THEORY4, LEAP, FIVE, MULTI, INTERP, REGS, QINTERP, PROMPTBOX, CAVITY/Well/dysts, REASON, BRIDGE, …) | memory index |
| Headline goal changes | "beat the dense transformer, show at interviews" (19 Oct) → "beat softmax on language by ≥1 %" (20–21) → "exact state at length" (22–24) → "Nature" (24) → "release a model" (26) → "a demo that freaks out investors" (28): **six goals in ten days** | `polyformer-project-goal.md`, `polyformer-beyond.md`, `polyformer-launch-plan.md`, `polyformer-r5-demo-goal.md` |
| Theorem statements refuted or withdrawn (24–29 Oct) | **≥ 15**: main-text line 72, SI S6 as worded, SI line 149, Prop. 3(a)/(b), Lemma 2, INTERP Thms 3(a), 3(c), 4(c), 8(a), 2(e), UNIFY U3/U4/U5/U6, Lemma Q's first draft, Thm 1(c)'s key inequality, Opus R1★, the W-method "erratum" | `research/THEOREMS.md` §I.9, §VI.6; `RESULTS_LOCK.in.md` §5 |
| Empirical headline claims withdrawn by audit (29 Oct) | **7** in one night: PREDICT's theory signatures, SCAN's "2.2 s", SCAN's K↔P theorem, REMEMBER-2's "only the pin is learnable", E3's 60/60, E4's "no self-oracle", HEADPIN's gate bypass; plus two RL bugs in r4 (no KL, numeric rows missing from the reward) | `polyformer-audit-2026-10-29.md`, `audit/codex2/out_*.md` |
| Earlier reversals | ARITH counting "full recipe" row was a pre-onset checkpoint (24 Oct); D1's negative interpretation overturned by its own audit (23 Oct); "aimed contraction on S5" dropped to p = 0.211 after Holm (27 Oct); the independent referee's three fatal points on paper v1 (27 Oct) | `selection-after-onset.md`, `polyformer-theory-pivot-2026-10-22.md`, `polyformer-launch-plan.md` |
| Prior-art verdicts on the theory slate (29 Oct live search) | **8 of 8 claims "PARTIALLY KNOWN"**: blindness → Whitney 1934 + Green 2026; drift time → Chung 2026; finite reads → Moore 1956; robust Myhill–Nerode → Brandoit (26 Sep 2026), Casey 1996, Rabin 1963; Theorem P → Cai 2017, Lewandowski (Jan 2026), Abbe 2024; no-finite-test → Moore 1956; decoder theorem → Xiang (16 Oct 2026); system → Xu 2026 + components | `RESULTS_LOCK.in.md` §8.7; `audit/priorart_*/out.md` |
| Brainstorm survival | 28 Oct candidates I1–I11: 11/11 "partly done"; REDTEAM_C M1–M5, P: 2 done, 4 partly done; REDTEAM_D C1: false; theory round 1 (48 conjectures): "no blindness-level theorem yet"; needle round 1: 8 finalists → 3 narrowed, 5 killed; round 2: 5 finalists → 4 narrowed, 1 killed. **13 finalists, 0 passed unchanged** | `GRAVEYARD.md`, `BULLETIN_1/2.md`, `GATE1.md`, `needle_gate2/out.md` |
| The demo's measured state | On 156 investor-style prompts: **base Qwen3-4B with thinking 0.73 vs r4 0.60 vs the live Loom 0.54** (read scores); top disappointments: certified-but-wrong (r4 7, Loom 3), confident answer after a failed program (r4 42 items), 2/3 of state tables fail to compile | `DAUDIT.md` |
| What survives, after audit | The Lean package (0 sorry; Theorem P iff, no-finite-test, composition, pointer, cache-policy, adder correctness, decoder discrete core); SCAN exact to 10⁶ digits; REMEMBER 80/80 pinned vs 76/80 history runs failing across 10 model families; REGVM Lag pinned to 30,000 steps; LATENT-1 and INVARIANCE/LEAN_S small-tracker results; Savant as a working system. "The complete pipeline is NEW as far as searched" | `FRONTIER.md` §B; `priorart_all/out.md` §7 |

One more fact that frames everything below: the record is **unusually honest**. Registrations were committed before
runs, ledgers were kept, failures were written down with reasons, and the audits that withdrew claims were ordered by
the project itself. The failure is not one of integrity. It is one of *choice, sequence and tempo*: what was worked on,
in what order, and how fast.

---

## Part 1. Diagnosis

### 1.1 How problems were chosen

**What the record shows.**

1. *The starting problem was already published, and the project knew it on day one.* The 18 Oct exploration found the
   cubic operator in Clift et al. 2020, Sanford et al. 2023 and Roy et al. 2025 and resolved to "frame Neo's work as an
   independent 2023 derivation, not a new operator" (`polyformer-findings-2026-10.md`). Rather than stopping to ask
   what the open problem in that area was, the next day's brief asked for "a better, more beautiful operator"
   (`polyformer-operator-search-2026-10.md`). The criterion for the next problem was aesthetic, not a gap in the map.

2. *Each new problem was chosen by the failure of the last one, within hours.* The chain is explicit in the **Why:**
   lines: S0–S2 "no-go" → S6 local regression (19 Oct); "Neo felt 'the way we think about higher order is wrong'" →
   GROUPS (20 Oct); BEYOND failed → ARC and dilution the same day; LOOPS missed its gate by 0.03–0.18 % → EVENTS the
   next day; REVISE/T1 null → "Neo asked for theory first: 'good work starts from a theorem'" (22 Oct) → K0⋈H
   rejected as "grotesquely complicated … a Frankenstein" the same day → energy forms, which "all fail as registered"
   → self-predictive state (fail) → invariance (first pass) → paraphrase (fail) → "Neo chose formal math over code
   execution" (23 Oct) → LEAN_N fail → D1 fail → EXEC_LM → INMODEL fail → "back to the whiteboard" (24 Oct, 05:17) →
   UNIFY → FIVE joint model fails → MULTI "still ugly" → "I really like the interpreter idea. Let's move forward."
   (26 Oct) → PROMPTBOX/Savant → "move the needle" (29 Oct). That is roughly one pivot per day for twelve days.

3. *The goal moved under the problem.* Six headline goals in ten days (table above). Each goal change re-ranked every
   open line, so no line was ever carried through the stage where it would have been tested against its strongest
   alternative. `WHITEBOARD2.md` (22 Oct) is the one place where the project stopped and extracted laws from what it had
   done; it ranked four directions with honest odds (D1 0.35, D2 0.4, D3 0.6, **D4 "the record as a paper … better than
   even"**) and said what to stop. D4, the one with the best odds, was never done. The next day's pivot went to Lean.

4. *Problems were chosen by local reward.* `LEAP.md` (23 Oct) says it plainly: "What moved anything was exactness …
   Soft approximations of these never paid; the exact versions always did." The exactness programme was pursued because
   it produced the first positive result (INVARIANCE, 22 Oct, $3.89), not because anyone had established that exact
   state tracking in small recurrent networks was an open problem. It was not: Casey 1996, Omlin & Giles 1996, Rabin
   1963, and, five weeks earlier, Brandoit et al. (26 Sep 2026) had the per-step cell theorem; Bugaud (ICML 2026
   workshops) had certificates from trained weights. All of this surfaced on 28–29 Oct (`RESULTS_LOCK` §8.5–8.7).

5. *The problem space the project chose first is one the field had already mapped as barren at that scale.* Law 1 of
   `WHITEBOARD2.md`: "On text at any scale we can run, the mixer does not matter … The field says the same (the 2026
   survey of non-transferring modifications)." About $550–600 of Modal (S0–S2 $64, S6 $58, BEYOND $76, LOOPS+EVENTS
   $263, REVISE $33, T1 $15, T2 $11, plus GROUPS/ARC) and three days went into learning this independently.

**Interpretation.** Problem choice was *reactive* and *reward-following* rather than *map-driven*. Hamming's test, in the
transcript I read (verified): "It's not the consequence that makes a problem important, it is that you have a reasonable
attack." The project had attacks (it could build anything in a night) but no settled view of which consequence it was
after; and Alon's rule that new researchers "may not commit to a problem before 3 months have elapsed"
(Alon 2009, Mol. Cell 35:726, verified via summary) was inverted into committing to a new problem every day. The
deeper problem is that nobody held the PI's job: Neo set direction in short messages ("beautiful", "magic demo", "move
the needle"), and an LLM orchestrator chose the concrete problems from what it could build, judged its own results, and
proposed the next move. The function "look at the whole field, say no, wait" was not assigned to anyone.

### 1.2 How the literature was read and used

**What the record shows.**

1. *Build first, search after.* The order was the same on every line: build → measure → write the claim → search for
   prior art. Newton attention: "No prior art found (HLA arXiv 2510.27258 …)" is one line in a results memory
   (19 Oct). `NOVELTY.md` (23 Oct) opens "Our claim" and ends "Verdict. We are not repeating anyone" after a single
   search that found NextLat and made it a baseline, but not Brandoit, Bugaud, Casey, Rabin, Cai or Moore. The
   systematic surveys L1–L6 (~700 verified records) were commissioned on 28 Oct, **after** paper v1 had been written
   three times (24, 26, 27 Oct) and **after** Savant had been published on Hugging Face and the site (27 Oct 19:15).

2. *The misses are of two kinds, and they diagnose two different gaps.* The old ones (Whitney 1934, Moore 1956, Rabin
   1963, Chow 1978, Casey 1996, Cai 2017) are the classical literature of three adjacent fields: analysis
   (extension theorems), automata theory and conformance testing, and neural-automata of the 1990s. Nobody on the team
   had read those fields before building in them. The new ones (Xiang 16 Oct 2026, Brandoit 26 Sep 2026, Bugaud
   May–June 2026, Green June 2026, Lewandowski Jan 2026, Xu Apr 2026, PAR 20 Oct 2026) show the area is crowded and
   moving weekly; without a standing weekly arXiv scan one is scooped on arrival.

3. *The project pitched to itself without checking its own map.* The "exactness is a congruence" principle was pitched
   to Neo at 15:45 on 28 Oct and killed the same evening when Neo asked for a double-check: "It was already in
   prior_art/L4_theory.md §1.2; I pitched without checking. … Lesson: grep our own prior_art/ map before pitching any
   principle" (`polyformer-leap-search-2026-10-28.md`). Red-team D then found THESIS_CHECK line 28 ("learned, certified
   abstraction is open; everyone else hand-designs what is kept") "FALSE as written" against Brandoit, Bugaud and
   Nerem (COLT 2026).

4. *Reading was confirmatory.* `LITERATURE.md` (24 Oct) is a careful 85-work review whose stated purpose is "how it
   bears on our claims", i.e. positioning a result that already existed. Its own entries contain the warnings that were
   not acted on: Buitrago Ruiz & Gu (ICML 2025) "pre-empts the coverage half of our Markov-step result"; Terzić et al.
   "partly pre-empts our closure ingredient"; Bugaud is listed as "complementary theory; cite" rather than as the
   competitor whose certificate theorem overlapped Theorem 2.

5. *The first deep reading happened on day eleven, and it was the most productive day of theory in the record.* Neo's
   DEEP_READING_REPORT (28 Oct, 26k words, on another machine) read Hahn, Chiang–Cholak, Brandoit, Bugaud, Casey,
   Maass–Sontag, Lewandowski, Abbe, Chow, Cai, Liu, Merrill, PENCIL, Jelassi and the JSR literature, and produced the
   candidate theorems C1–C4 and the FOLLOWUP_REPORT; the decoder class theorem (the one item still "NEW as far as
   searched") came out of that reading, not out of any brainstorm round.

6. *Agents' citations needed verification.* `proofs-positioning.md`: Argon got 3 of 8 identifiers wrong and invented one
   title; Astra 32/32 correct. The project built `verify_refs.py` in response: a good practice, but applied to the
   bibliography, not to the choice of problem.

**Interpretation.** Literature served two roles here: a post-hoc novelty audit, and a citation list. It never served the
third and most important role: the **map on which problems are chosen**. Kuhn's point (unverified wording; the claim is
standard) is that an anomaly is visible only against expectations the paradigm supplies; one cannot see what is open in
automata theory without knowing automata theory. The result was a programme that re-derived, with real skill, Whitney
(1934), Moore (1956), Chow (1978) and Cai (2017), and then had to concede each one in a "corrections and gaps" column.

### 1.3 How AI agents were prompted and used

**What the record shows.**

1. *Scale.* One Opus orchestrator, 25 linked Claude sessions (the sidebar list), ~55 Cursor/Codex/agy worktrees, "about
   12 parallel subagents plus a large paper agent" on 28 Oct (`feedback-usage-limit.md`), weekly Claude limit at 34 %
   within 17 hours of reset, **$1,051 of a $2,000 extra-usage cap** by 28 Oct, Cursor quota exhausted on 25 Oct and
   dropped on 29 Oct, agy quota exhausted on 29 Oct. Neo's own words: "I'm going to run out of my Fable 5.1 very
   quickly" (`feedback-token-economy.md`).

2. *Agents overclaim, and the orchestrator relayed before auditing.* The 29 Oct audits (table in §0) are the measure:
   seven headline claims gone in a night, two of them numbers that "exist only in an agent's final message". The
   orchestrator's own record of relaying before checking: "I (parent) first called the missing delay 'very likely the
   cause' and was wrong, then reported 9/10 as 'better for us' before seeds 10-19 gave 6/10" (`polyformer-unify-2026-10-25.md`);
   "I relayed an interpretation ('the model trusts the table') marked 'provisional' before the audit. The audit then
   found all four held rows were self-loops" (`polyformer-audit-2026-10-29.md`). The audit layer (Codex, read-only,
   with a checklist) was created on 29 Oct, day twelve, after Neo said "there could be mistakes in the code".

3. *Agents' theorems were frequently false, and the Lean step was the only reliable filter.* Fifteen-plus refuted
   statements (§0) came from agents, and most were caught by the Lean agent or by a Codex referee: INTERP 8(a) was a
   *headline* ("the emitted token is a snap") until `not_theorem8a`; Opus R1★ was "false as stated" on referee; the
   decoder theorem survived only after PROOF1 → referee → proof1v2 → Lean. The generation rate of theorems exceeded
   the checking rate, and checking was the expensive step.

4. *Brainstorm "minds" converged, and convergence was read as evidence.* `BULLETIN_1.md`: "Convergences (the strongest
   signal at this stage) … 4/4 … 4/4 … 4/4". The four minds shared the same 242 KB bundle (ATLAS + ANOMALIES +
   TENSIONS + GRAVEYARD), the orchestrator's own "seeds" ("Does exact computation require erasure (Landauer)…"), and
   overlapping pretraining; GATE1 then killed or narrowed every convergence. Agreement among LLMs given the same
   context is mostly correlated error, not independent confirmation. The two "outsiders" were given only the north star,
   fact sheet, TAKEN and graveyard, and their best idea ("short teaches long") was the W-method (Chow 1978).

5. *The brief format forced breadth.* `ROUND1_BRIEF.md` asks for 12 conjectures per mind in three tiers with nine
   fields each; `needle/BRIEF.md` asks for 5–8 ranked hypotheses with seven items each. Four minds × 12 = 48
   conjectures; six minds × ~6 = ~36 hypotheses; ~200 KB of output per round for one orchestrator to judge. Neo's
   reaction to the leap search was exact: "a 'mezze platter' of prior-art-covered features". A format that demands a
   platter gets a platter.

6. *The minds were asked to do what a search does better.* The briefs say "aim higher than Whitney" and "check yourself
   against FRONTIER §A". But the minds cannot know Chow 1978 or Brandoit 2026 better than a live search can, and the
   record shows it: Codex *with* search did the killing (`GATE1.md`, `needle_gate2/out.md`), and the minds without
   search produced classical theorems with new names. The record's own summary (`BULLETIN_2.md`): "every survivor's
   residue is the same: a classical idea becomes a guarantee for an LLM once its steps carry the per-row certificate."

7. *Night runs removed the human from the decision points.* "Neo went to bed" / "don't wait for me" on 20, 21, 23, 24,
   26, 27 and 28 Oct; caps of $100–$400 per night; the orchestrator launched, judged and relaunched until morning;
   Neo woke to a status table and chose the next pivot in minutes ("Neo awake and asked for directions, better
   figures, and to start writing v2", 28 Oct 11:49). The 39 % night-commit share is the trace of this.

8. *What worked, and should be kept.* Registration before runs (COMMON.md rule), per-agent ledgers and caps, Lean
   certification with positive confirmation (`lean-toolchain.md`), citation-verification scripts, the hostile referee
   pass on v1, the Codex code audits, the kill gates with live search, honest **Why:** lines in memory. These are the
   parts of a good lab. They were used to *defend* claims after building rather than to *choose* what to build.

**Interpretation.** The agents were used as a parallel army of builders and as a committee of thinkers. They are good
at the first role when audited, and poor at the second when given the project's own framing: they elaborate the brief
they are given. The external evidence agrees: in Si, Yang & Hashimoto's blind study (arXiv 2409.04109, unverified
beyond the abstract), LLM research ideas were judged *more novel* than experts' at ideation, and in the follow-up
execution study (arXiv 2506.20803, unverified beyond the abstract) that advantage disappeared once ideas were carried
out; and sycophancy measurements (SycEval, arXiv 2502.08177; Nature news on "50 % more sycophantic than humans", both
unverified beyond summaries) describe exactly the "report 9/10 as better for us" failure. The record's own ratio is the
sharpest number: of 13 brainstorm finalists, 0 survived unchanged; of 8 theory claims, 8 were partially known; of 7
audited empirical headlines, 7 were withdrawn or narrowed.

### 1.4 How the work was tested, audited and decided

**What the record shows.**

1. *Registration was real but porous.* Good: COMMON.md's rule, `DAUDIT.md`'s registration commit before any output was
   read, the Holm correction on 27 Oct. Porous: n = 3 seeds read as mechanism until UNIFY showed 2/3-vs-3/3 was noise
   at n = 10–20; a 4,000-step batch "ran unregistered by mistake" (23 Oct); the ARITH checkpoint selected at step 250
   before the term was on (24 Oct); "the 29-vs-96 clip-vs-sphere comparison was NOT registered (don't claim it)"
   (26 Oct); `PAPER_V2_PLAN.md`'s closing banger chosen "in order of preference; the first that holds". The last is the
   garden of forking paths at the level of the narrative rather than the analysis.

2. *Gates were set and then argued past.* LOOPS registered "≥ 1 % vs softmax at equal FLOPs, 3/3 seeds" and got
   −0.89 % ("FAILS by 0.03–0.18"); the follow-up EVENTS spent $187 more, found the lead "erased by two published parts
   at 512" and kept a −0.66 % at 8k with an attribution story. Energy's rule was "any two of three" tests; E0 and E2
   failed; E1 was then run anyway. In Lakatos's terms (SEP entry, verified): after the anomaly, auxiliary hypotheses
   were added and no "novel fact" was predicted and confirmed.

3. *Evaluation was on the system's own task families until day twelve.* Every headline number to 28 Oct is on
   generated families, G1 tables, the project's own composites. `DAUDIT.md` (29 Oct) was the first measurement from a
   user's point of view, and the base model won (0.73 vs 0.60 / 0.54). Its registered scoring rule was itself wrong in
   both directions and had to be corrected after reading transcripts.

4. *Decisions were made at the wrong hour by the wrong agent.* The orchestrator decided budgets, arms and pivots at
   02:00–05:00 under caps; Neo decided direction on waking. The two explicit management corrections from Neo are both
   reactions to over-launching: "I don't want to do anything we don't need" (24 Oct, after an unrequested scale-up
   batch) and "Audit before believing" (29 Oct).

5. *Audit was late and external.* Codex read-only audits with checklists did in one night what no internal review had
   done in eleven. The project had the tool from day one (`brainstorm-clis.md`, 19 Oct) and used it for brainstorming.

**Interpretation.** The project ran Platt's cycle backwards. Platt's steps (Science 146:347, 1964; I read the scan,
verified): "1) Devising alternative hypotheses; 2) Devising a crucial experiment (or several of them), with alternative
possible outcomes, each of which will, as nearly as possible, exclude one or more of the hypotheses; 3) Carrying out the
experiment so as to get a clean result; 1′) Recycling." Here the sequence was: one construction → a registered
threshold → a miss → an auxiliary story → the next construction. There were many constructions and almost no
experiments designed so that *either* outcome would exclude something. The one time the project did produce a
strong-inference-shaped finding, "constructions work; what decides outcomes is supervision of the intermediate state
and which basin training finds, not the block" (22 Oct), it did not then design the crucial experiment between the
competing explanations; it pivoted to a new construction.

### 1.5 How the work was managed

**What the record shows.**

1. *Parallelism without a bottleneck owner.* Up to 25 sessions and a dozen subagents reporting to one LLM orchestrator
   reporting to one human. The orchestrator's attention was the scarcest resource, and its failure mode (relay before
   audit) was the direct cause of the 29 Oct withdrawals.

2. *The paper and the demo were coupled to a moving theory.* Paper v1 written 24 Oct, v2 the same day, v3 on figures,
   a "jewel" LaTeX draft on 26 Oct, rounds 3–4 and a reframe on 27 Oct after the referee's "three fatal points", a v2
   plan on 28 Oct, and `RESULTS_LOCK` rewrites on 28–29 Oct as the prior art landed. Four titles. Savant was uploaded to
   a public Hugging Face repo and the site pushed on 27 Oct, then squashed and re-pinned on 28 Oct, before any
   external audit and before DAUDIT. The outward-facing artefacts were built on claims that were still being revised
   hourly.

3. *Budgets were per agent, not per programme.* Caps of $10–$600 per run were enforced; there was no rule of the form
   "this programme stops if it has not produced a confirmed novel prediction by day N or $X". The one time a stop rule
   existed and bit (LOOPS's 1 % gate) it was overridden by a follow-up.

4. *Infrastructure churn cost real work.* Cursor deleted ~19 worktrees on 27 Oct, losing uncommitted files and breaking
   the paper build; Cursor dropped Grok mid-run (29 Oct); the laptop slept at 1 % battery and killed every local agent
   (28 Oct 02:43); `modal run --detach` cancelled every job when the laptop closed (24 Oct); 8 % of Modal calls did not
   complete. Each incident cost an hour or a night and a takeover brief.

5. *One human, no cadence, no outside reader.* No weekly review, no second human to argue with, no reading days. The
   project's own "Dealer" (PARC's weekly session in which one person defends their work; secondary sources, unverified)
   was the orchestrator talking to itself.

**Interpretation.** The management structure optimised throughput: things built per night. Research progress is not
throughput-limited; it is limited by the rate of *correct decisions about what to build*, which is set by reading,
thinking and arguing with someone who disagrees. Those were the three activities with the least time in the record.

### 1.6 The causal chain, in one paragraph

Problems were chosen by what could be built next and by the last positive signal, not from a map of what was open
(1.1); the map was never drawn because reading was done after building and only to position results (1.2); building
was cheap and fast because agents will build anything overnight, and they also wrote the claims, which they overstate
(1.3); the tests were registered but the programme-level decisions were not, so misses became follow-ups and the paper
and demo were coupled to claims still in flux (1.4); and nobody had the job of saying no, waiting, or reading (1.5).
Money followed the launches (61 % of Modal on 25–28 Oct) rather than the questions. The output is a large, honest,
well-engineered record of rediscoveries, plus one genuinely new *system* whose evaluation from the user's side (DAUDIT)
is not yet favourable.

### 1.7 Assumptions we never questioned

Added 30 Oct at the orchestrator's request, after Neo asked why nobody in four weeks had questioned writing programs
as 200-row tables. The inventory is from the record; each line says where the assumption came from, why it held, and
what breaking it buys. Then: why ten minds and two kill gates never touched it.

| # | Assumption, as the record held it | Where it came from, and why it stuck | What breaking it buys |
|---|---|---|---|
| A1 | **A program is a literal transition table** (addition = 200 rows of `c a b c' s`, ~1,100 tokens, ~4 min in the browser) | PROMPTBOX's *first* program (27 Oct) was a rule: `on each pair a b: s=(a+b+c) mod 10, c=(a+b+c)//10 mod 2` (`PROMPTBOX.md` §1). The model "errs mostly on steps" computed from rules, so DEMO_DESIGN made "the expanded table both the certificate and the executable", and `ARITH_FORMAT.md` fixed 200 rows "before any training". It stuck because Theorem P's certificate enumerates rows, the page shows rows, and PROMPTBOX ($600), ARITH ($42), REASON ($90) and r4 ($79) were all trained on it: the training data encoded the assumption | 1,100 → 70 tokens (r5-harness2, 29 Oct 03:53); the row-writing errors ASKQ found (wrong tables at > 99 % confidence) cannot occur; minutes → seconds |
| A2 | **Every program is written from scratch for every question; a library is "tool calling"** | "The model writes its own programs" was the novelty claim; Neo's 26 Oct objection to per-skill adapters ("not that different from tool calling") was generalised to anything reusable. `LIBRARY_FORMAT.md` existed from 28 Oct, but "reason-s1 and r4 were never trained to emit" `use` lines (ASKQ); the harness splice arrived on 29 Oct | cached per-device certificates; the demo's 4-minute adder becomes a one-line `use add` |
| A3 | **One tick per transition; execution is sequential** | the pinned clock was the first exact mechanism and became the definition of "execution"; the parallel scan came on 28 Oct only after Neo: "without it, the demo is not even usable" | 250 s → 3.2 s for 4,096 digits on H100; 337 s → 9.3 s in the browser (SCAN, WEBSCAN) |
| A4 | **Programs are finite-state** | Theorem P is about FSMs; "a finite-state table is the wrong tool for unbounded nesting" was written in `DAUDIT.md` on the morning of 29 Oct, and STACK ran that night | BBH boolean 22 % → 250/250, Dyck to depth 4,096 (STACK) |
| A5 | **Facts must live in the context, never in the weights** | "footprint = view"; the weights-level certificate N* was tried and failed (CIRCUITS: "no weights-level N*"), and the conclusion drawn was "everything goes into Π" rather than "certify the small finite functions the weights already compute" (BIGIDEA: one vector reaches 99.7 % of rows) | a native instruction set certified once per device; programs name operations instead of restating facts (LANGUAGE_NOTES §4, L0) |
| A6 | **State is one token, events are single tokens, and the model chooses the names** | the lookup lemma and the two-token block; consequences the record measured but treated as laws of nature: the separation law (near-duplicate names cause 55× the errors), the 249-event hub failure, "addition missing (100 event types > core's 32)" | harness-allocated names from a screened pool; registers and cascades (P3) as the normal case; a bounded, designed state alphabet |
| A7 | **The harness must compute nothing** (for the "not a tool call" story) | `PAPER_V2_PLAN.md`: "Do not hide the clock… computes nothing about the state". Silently relaxed already: STACK's host compiles the question with Python's `ast` and keeps the stack; SCAN's host builds the tree | name it a *scheduler* (packing, scan trees, frames, names, type checks) and design it; keep "computes nothing about values" as the honest line |
| A8 | **Inputs are re-quoted by anchors rather than read in place** | PROMPTBOX's format; DAUDIT disappointment 7 (typos, commas, lists); fixed by anchor-constrained decoding on 29 Oct | reading becomes a decoding constraint, not a copy the model can get wrong |
| A9 | **Compile failures are a data problem** (more families, phrasings, RL) | every compile fix in the record is more data: PROMPTBOX Stage 2, r4, R5 Tier 1. ASKQ: the right program is not among 16 samples for held-out topologies (2–4/40). Nobody asked whether the *target language* caused the failure | a target the model already speaks and a program of tens of tokens; compile becomes a small classification over few instructions |
| A10 | **The base model's abilities are a cost to repair, not the resource** | Stage 2r "language repair"; single-digit arithmetic, code and word meanings in the weights were seen as mechanism findings (UNIVERSAL, BIGIDEA), not as an instruction set | the weights as the ISA; training only for routing and reading |
| A11 | **The certificate decides the representation** | "good work starts from a theorem" (22 Oct); the representation was whatever kept the per-row certificate | invert the order: compiler reliability → readable programs → certificate by composition (Theorem C, P, P², STACK's lemma) → speed |
| A12 | **Exactness is the goal; the user's experience is downstream** | "digital state", "never wrong"; the first user-view measurement was DAUDIT on day 12, and the base model won | tokens, seconds, honesty and answer form as registered metrics from day one |
| A13 | **The architecture is fixed (Qwen3-4B + LoRA); only the cache policy varies** | a reasonable constraint, never examined: digit tokenisation, the chat template, the 4B choice, and whether a smaller model with the same ISA would do | cheaper demos; a from-scratch design later |
| A14 | **Evaluation is on our own families, by exactness at length** | every headline to 28 Oct is on generated families; speed and token count were never registered metrics | DAUDIT-style batteries as the acceptance test for every artefact |
| A15 | **More minds make more ideas, and agreement among them is evidence** | `BULLETIN_1.md`: "Convergences (the strongest signal at this stage)"; the minds shared one bundle and one orchestrator's seeds | one human asking "what is absurd here?" found A1–A4 in a day (Neo, 28–29 Oct); the agents found none of them in four weeks |

**Why a ten-mind brainstorm and two kill gates never questioned the representation.** The record shows the mechanism.

1. *The bundle fixed the representation as notation.* `ATLAS_BRIEF.md` §0 defines "a program Π (a table)" and asks
   every mind to state conjectures "in the atlas notation". A mind reasoning in that notation cannot propose that Π be
   something else; the table is the alphabet of the question.
2. *The briefs rewarded theorems that move a line.* `needle/BRIEF.md`: "Name the FRONTIER §A result it goes beyond and
   the exact delta, or the §D open problem it opens." A representation change moves no line in §A and is not a
   problem in §D ("speed" and "beyond finite state" are listed, but as theory problems). The clause "at least two of
   your hypotheses must sit outside our current framing" was graded by the same gate, so "outside" produced restoring
   words, stochastic bounds and bicyclic monoids, not "write programs in a language".
3. *The gates graded contributions as theorems and demoted engineering.* GATE1's verdicts say it in so many words:
   "Useful implementation technique; vote robustness and concentration claims are standard" (KILL); "Keep the technique
   as a component" (KILL). Under that grading, "stop writing rows" has no route to survive: it is not a theorem.
4. *The north star constrained the search to "thin machinery plus a small training change".* That is the format kept
   fixed by definition.
5. *Nobody used the artefact as a user.* The orchestrator watched Loom spend 223.5 s to add 48 + 17 (28 Oct 16:55) and
   filed it as "the R5 speed and judgment problem in one example", a backlog item, not as evidence against the
   representation. DAUDIT's "a program for 2 + 2" is disappointment number nine of twelve.
6. *Sunk cost and the novelty claim.* Four trained models encoded the format; "writes its own program" made the
   program's visible length a feature; and the fear of the Python-twin objection pushed every design away from
   anything that looked like a language or a library, which is exactly where the fix was.

The general failure is the one Platt names for experiments, transposed to design: the brainstorms were asked "what
theorem is missing?" and never "what would a user find absurd about what we built?" The techniques for this are old
and cheap: an assumptions register per programme (Mason & Mitroff's assumption surfacing, 1981, unverified wording),
the pre-mortem (Klein), inversion, and the two-plus-two test on day one of every artefact. The record also shows who
made every representational leap it contains: the interpreter (26 Oct), the scan (28 Oct) and the language (29 Oct)
were all Neo's, in a sentence each, after looking at the thing; the agents made none. That is the strongest argument
in this report for the division of labour in §2.11: agents execute, audit and search; the human looks at the artefact
and asks what is stupid about it. Remedy, concretely: every programme keeps `ASSUMPTIONS.md` with one line per
assumption and the cost of breaking it; every brainstorm has one section graded only by "would this change what a user
sees", with the theorem gate suspended; and no artefact is trained on until a human has used it for ten minutes.

---

## Part 2. Meta-synthesis: what would have given a real chance

Each principle is tied to an episode in the record and to a source. I use a source only where it explains something
that happened; the rest of the reading list in the brief is omitted on purpose.

### 2.1 Strong inference, not strong construction (Platt; Chamberlin)

Platt's method (verified, from the 1964 scan) is three steps and a recycle: alternative hypotheses, a crucial
experiment whose every outcome excludes some of them, a clean result. He warns against exactly the pattern in this
record: "We measure, we define, we compute, we analyze, but we do not exclude," and his touchstone question is "But sir,
what experiment could disprove your hypothesis?" Chamberlin's method of multiple working hypotheses (1890, reprinted
Science 148:754, 1965; verified via Platt's quotation) exists to prevent "parental affection" for one's hypothesis.

*What it explains here.* The project's unit of work was the construction (an operator, a loss, a block, a model), and
the question asked of each was "does it pass its gate?", not "which of three explanations does this outcome kill?".
Compare the one episode that was run strong-inference style: VALIDATION V1–V8 (22 Oct, $3.48), which registered a
ladder of candidates with kill criteria and found that "no candidate earns a paid run by the registered rule" while
extracting two real signatures. That was the cheapest and most informative day in the record.

*Rule.* Before any paid run, write the two or three competing explanations and the experiment whose outcomes
separate them. If no outcome would change what you do next, do not run it.

### 2.2 Choose problems from the map, and give the choice time (Hamming; Alon; Medawar; Heilmeier)

Hamming (verified): the important problem is the one for which "you have a reasonable attack"; and the open-door
researcher, though slower today, ten years later still knows "what problems are worth working on". Alon (unverified
wording): a feasibility × interest diagram, a Pareto front, and a rule that new people "may not commit to a problem
before 3 months have elapsed" because the ideas that keep returning over months are the ones to ground a project on.
Medawar (Wikiquote, unverified wording): "research is surely the art of the soluble". Heilmeier's second question
(DARPA; the wording is from my knowledge, unverified) is "How is it done today, and what are the limits of current
practice?", which is a literature question, asked before the proposal.

*What it explains here.* Twenty-five programmes in twelve days means no problem was ever carried past the point where
its strongest competitor was identified. The record contains a correct instinct for soluble problems (small trackers on
certified tasks) and a correct instinct for important ones (exact computation inside an LLM), and it never spent the
three months, or even three days, needed to find where those two sets intersect *in the published map*. Heilmeier's
"how is it done today" would have found Cai 2017 and Lewandowski 2026 before Theorem P was named.

*Rule.* A problem is chosen in writing, by Neo, with the three closest published results stated and the delta named,
and it is not changed for a fixed period (two weeks is the minimum for anything with a theorem in it).

### 2.3 Read before you build; map the adjacent fields (Kuhn; Lakatos)

Lakatos (SEP, verified): a programme is progressive when "each new theory in the sequence must have excess empirical
content over its predecessor" and "some of that novel content has to be corroborated"; a programme whose auxiliary
hypotheses are "all cooked up after the event to protect [the] theory from the facts" is degenerating. Kuhn (standard,
unverified wording): discovery begins with awareness of anomaly, and anomaly exists only against the expectations a
paradigm supplies.

*What it explains here.* The exactness programme was progressive for about three days (INVARIANCE → LEAN_S1 →
EXEC_LM → LATENT-1 each predicted and confirmed something new to the team), then degenerated in the Lakatosian sense:
each prior-art discovery was absorbed by narrowing the claim ("ours, narrower", eight times in `RESULTS_LOCK` §8.5)
rather than by predicting a new fact. The theory arm (28–29 Oct) was built correctly in principle, from anomalies and
tensions, but the "anomalies" were anomalies only relative to the team's knowledge; against the real paradigm
(Casey, Brandoit, Chow) most were expected.

*Rule.* Keep a one-page Lakatos scorecard per programme: novel predictions made, confirmed, failed; prior-art hits
absorbed by narrowing. Two consecutive narrowings without a confirmed novel prediction means the programme is
shelved, not followed up.

### 2.4 Preregister the decision, not only the run (Nosek et al.; Gelman & Loken; Ioannidis)

Nosek et al. (PNAS 115:2600, 2018; verified citation): preregistration separates prediction from postdiction. Gelman &
Loken (2013; verified citation) show the multiple-comparisons problem arises even with one analysis when the choices
depend on the data. Ioannidis's corollary 4 (PLoS Med 2005; verified citation): the greater the flexibility in designs,
definitions and outcomes, the less likely the findings are true.

*What it explains here.* The forks were at the levels registration did not cover: which seed count counts (n = 3
until it mattered), which checkpoint (step 250), which banger ("the first that holds"), which headline ("every seed in
six of seven settings" after one setting failed), which title (four), which claim survives the prior-art search
("ours, narrower"). Each fork was taken honestly and recorded, which is why the record is auditable; but the
aggregate is a paper whose claim set was selected by the data eleven times.

*Rule.* Register, per programme and in advance: the seed count and the exact statistic that would count as a win, the
selection rule, the prior-art search terms and the result that would make the claim "not ours", and the stop rule.

### 2.5 Incubation needs a human and sleep (Poincaré; Hadamard)

Hadamard's stage model (preparation, incubation, illumination, verification; 1945, after Poincaré and Wallas;
verified citation, standard content) is the only account of creative work that has survived a century of
re-examination, and its central claim is that illumination follows a period in which conscious work has stopped.

*What it explains here.* The orchestration removed incubation by construction: the work never stopped, the decisions
were made at 03:00 by an agent that does not incubate, and the human's input was a morning reaction to a status
table. The two most valuable theoretical contributions in the record came from the two occasions when a human read
and thought offline: Neo's deep-reading report (28 Oct, on a plane/another machine) and the PROOFS session that
"verified line by line" (23 Oct, $0). The whiteboard session Neo demanded ("why aren't we at the whiteboard like a
graduate student?", 28 Oct 19:40) closed two questions in forty minutes, one by finding the literal conjecture false.

*Rule.* No research decision between 23:00 and 08:00. Agents may run registered jobs overnight; they may not launch
new programmes, amend registrations, or write claims.

### 2.6 Bisociation needs two deep matrices (Koestler)

Koestler (1964; unverified wording): the creative act joins two "self-consistent but habitually incompatible frames
of reference"; the matrices must each be mastered, and the joining is what is new.

*What it explains here.* The lenses (`LENS_*.md`) named second matrices (coding theory, fault tolerance, dynamical
systems) but the minds held them shallowly, so the joins were by name ("restoring organ", "congruence", "JSR") rather
than by theorem; the gates then found the actual theorem in the second field (Pippenger-style voting bounds, Nerode,
Berger–Wang) and the join evaporated. The one join that held, the Moore/Chow/Vasilevskii lineage for the theorem pair
(`INSIGHTS` §5), was found by reading the second field's primary texts, and it is now the paper's "strongest framing".

*Rule.* Pick one second field. Read its three canonical papers yourself. Only then ask whether its theorem says
something about trained networks that it could not say about automata.

### 2.7 Bend over backwards (Feynman; Lipton & Steinhardt)

Feynman (1974; verified from the Caltech text): "The first principle is that you must not fool yourself—and you are
the easiest person to fool"; scientific integrity means "bending over backwards to show how you're maybe wrong"; and
on Millikan, "When they got a number closer to Millikan's value they didn't look so hard." Lipton & Steinhardt (2018;
verified citation) name the failure to distinguish explanation from speculation, and "mathiness".

*What it explains here.* Millikan's pattern appears verbatim: results "better for us" were relayed, results against
were audited. The theorem slate contained lemmas presented as theorems ("T1(b) … not a contribution: textbook softmax
saturation, conceded to referee") and a formal apparatus (robust Myhill–Nerode, aimed tube, congruence) whose names
promised more than the statements delivered. The project *did* bend over backwards in the end (audits, referee, Holm
correction, "the first that holds" written down), which is why this report can be written; but it did so after the
public release, not before.

*Rule.* Every result is "unaudited" until an independent reader with the code reproduces the count; nothing
unaudited leaves the repository; the audit is ordered by the person who wants the result to be true.

### 2.8 How breakthroughs were actually found: one problem, one benchmark, one team, long enough

The record of the five case studies the brief names is consistent (all unverified beyond summaries and widely
reported facts):

- **Shannon** outlined the ideas in a 1939 letter to Bush and had substantially finished the 1948 paper by the end of
  1944: nine years on one question.
- **AlphaFold**: one benchmark (CASP), a committed team, CASP13 (2018) → a full redesign → CASP14 (2020); the result was
  a two-year iteration against one external yardstick, not a cascade of pivots.
- **Attention** (Bahdanau 2014): an intern with five weeks left dropped a too-ambitious cursor design for the simplest
  thing that could work; the mechanism was found under a constraint, on one benchmark (WMT), by one person who then
  had it checked by two others. **The Transformer** (2017): one team, one benchmark, months in a hallway, and a paper
  whose title overclaimed less than its results.
- **ResNet** (2015): one anomaly, stated precisely (deeper plain nets have *higher training error*, so it is not
  overfitting), and one minimal fix that made the identity the default.
- **Diffusion**: the 2015 idea (Sohl-Dickstein) was ignored for five years; DDPM (2020) simplified the recipe (predict
  the noise) and the field moved. The idea did not need a brainstorm; it needed one good simplification and patience.

*What it explains here.* Every case is one problem held fixed for a long time, one external benchmark, a small team,
and a clean statement of one anomaly. The Polyformer record has the inverse profile on all four. The closest it came
was 22–25 Oct (one problem: exact state; one benchmark: exact at 1,024 on certified tasks; a small team), and that is
where its only progressive stretch lies.

### 2.9 The bitter lesson, twice (Sutton)

Sutton (2019; verified quotes): "We have to learn the bitter lesson that building in how we think we think does not
work in the long run"; the two methods that scale are search and learning.

*What it explains here.* Law 1 of `WHITEBOARD2.md` is the bitter lesson relearned at 22 M parameters: a dozen
hand-designed mixers (arity, Newton, holonomy, local regression, revisable memory, energy) within ±1.5 % of softmax
and shrinking with size. Then it was learned a second time in the other direction: UNIVERSAL found that the lookup
executor is already in every pretrained model ("the finder is everywhere … elicitable, not latent"); the hand-built
tracker lines were trying to add what pretraining had already built. Both times the lesson arrived after the spend.

*Rule.* Any claim about an architecture or loss at ≤100 M parameters is a claim about that scale; do not spend on it
unless the mechanism is one that scale cannot supply (a certificate is such a thing; a mixer is not).

### 2.10 How great labs worked, and what applies to a lab of one human and twenty agents

Bell Labs (Kelly gave scientists freedom and time; secondary, unverified), the MRC LMB (Perutz: "no politics, no
committees, no reports, no referees, no interviews: just gifted, highly motivated people"; the line is widely quoted
but I could not verify its source), PARC (the weekly Dealer: one person stands in a ring of bean-bag chairs and defends
their work against peers; secondary, unverified), early DeepMind and OpenAI (one bet each, Atari/Go and scaling, held
for years). The common structure is *few problems, long tenure, peers who argue, and protection from management*, not
freedom from criticism.

*What applies here.* The Dealer is the one institution this project can afford and lacks: a weekly hour in which Neo
presents the week's claim to one or two humans who know the adjacent field and are paid or motivated to disagree.
"No committees" does not mean "no peers". And "freedom and time" means time on one problem, which is the opposite of
twenty-five programmes.

### 2.11 Agents: instruments, not minds

The principles above imply a division of labour that the record arrived at only on day twelve:

- **Agents excel at**: formalisation (Lean caught fifteen false statements), citation verification, code audit with a
  checklist, running registered jobs, building harnesses, exhaustive literature retrieval with live search.
- **Agents are unreliable at**: judging novelty from memory, judging their own results, generating ideas that are not
  elaborations of the brief, and deciding what to do next.
- **Therefore**: one orchestrator, not twelve; one auditor who sees only code and records; brainstorm only with live
  search and only on a question Neo has already read into; every agent claim labelled "unaudited" by default; blind
  conditions for any multi-mind exercise (different bundles, no shared seeds, no convergence scoring); and a hard cap
  on generated text per decision (if Neo cannot read it in an hour, it is too much).

### 2.12 What the brief's other sources add, briefly

Popper's demand for bold, risky conjectures (1963; unverified wording) was honoured, repeatedly; what was missing was
the second half, the refutation *before* the next conjecture. Thurston (1994; verified citation): progress is
understanding, not theorem count; by that measure the record is richer than its claim table, and `INSIGHTS.md` is the
proof. Dyson's birds and frogs (2009; unverified wording): this project has been all bird for twelve days; the frog's
patience on one pond is what is missing. Weinberg (Nature 426:389, 2003; unverified wording): "aim for rough water"
is right, but his first lesson is that nobody knows everything, and you don't have to. Rota (1997; unverified wording):
"Do not worry about your mistakes", and the Feynman method, a dozen favourite problems carried for years. Stokes's
Pasteur's quadrant (1997; unverified wording) names the right target: use-inspired basic research, which is what
"certified computation inside an LLM" is, provided the use (a demo) does not set the pace of the understanding.

---

## Part 3. What to do now

### 3.0 The week plan (Neo's constraints, 30 Oct: one week, $1–2k)

Neo answered the two questions at the end of the first draft: the runway is one week and $1–2k. §3.4–3.7 below
describe the month-scale version; where they conflict with this section, this section wins. Two honest sentences
first. A Nature-calibre theoretical advance is not a one-week object, and no plan here pretends otherwise. What one
week can produce, with the homework done, is an arXiv paper nobody can embarrass, a demo that does not disappoint on a
narrow honest scope, and the language as the visible leap (one-line programs instead of 200 rows). That is a funding
case; the theory line resumes if the funding comes.

**Scope, fixed on day 0 and not reopened.** Three program kinds only: (i) exact arithmetic on numbers in the question
via library ops (`add`, `sub`, `compare`) with the scan and the BigInt check; (ii) judge-then-aggregate over items in
the question's own text (count, sum, rank), with the error decomposition printed; (iii) nesting via `stack` (Dyck,
boolean). Everything else answers in plain chat. No new model is trained this week (R5 Tier 1 is out; it is the one
item the week cannot absorb and the one most likely to break language).

| Day | Work | Decision / gate | Spend |
|---|---|---|---|
| **0 (Thu 30)** | Write `STOP.md` and stop everything on §3.2; settle every Modal call; freeze the claim table (`CLAIMS_FROZEN.md`, audited rows of `RESULTS_LOCK` only); write the one-sentence answer to "why not Python?" (LANGUAGE_NOTES §3) and the demo scope above | scope frozen | $0 |
| **1 (Fri 31)** | *Homework.* Neo reads six papers, half a day: Lewandowski–Machado–Schuurmans 2026, Cai–Shin–Song 2017, Chow 1978 (or the Lee–Yannakakis 1996 survey), LOTUS (Patel et al. 2024), Chain of Code, Brandoit 2026. Orchestrator: live prior-art search on the language delta with the terms in LANGUAGE_NOTES §7, *before* any build. Pilots 1–2 of LANGUAGE_NOTES §6: which surface syntax base Qwen3-4B compiles best zero-shot on the 88 held-out items plus 30 DAUDIT prompts; which native digit/boolean functions certify under a one-line header, per device | **Gate A (end of day):** a surface syntax chosen by measured compile accuracy and tokens per program, and the native table; if no surface beats the trained table compile, the demo uses `use` library lines only (already working) and the language is deferred, honestly | ≤ $50 |
| **2–3 (Sat–Sun)** | *Build.* The harness as a scheduler: `use` library ops, scan, stack, packed `judge`+aggregate, name allocation from a screened pool, anchors, honest failure, BigInt check, the one-line program shown on the page with its certificate and the two error terms. *Paper.* Neo writes the outline and the contribution list from the frozen table into the LaTeX skeleton; figures regenerated from records only | build runs end to end on ten prompts per kind | ≤ $150 |
| **4 (Mon 3 Nov)** | DAUDIT re-run with the corrected scorer on the new harness; fix the top two disappointments; record the three proof moments (Theorem P necessity live; pinned vs history; the million-digit scan with the BigInt check) as short videos | **Gate B:** the clock arm beats base on the shared 70 items and shows 0 certified-but-wrong; otherwise the demo is the three proof moments only | ≤ $30 |
| **5 (Tue)** | *Paper.* Full draft in one voice (Neo's pass); Codex hostile read with a checklist (not a rewriting agent); references verified by script; limitations print DAUDIT's numbers and the Python-twin sentence | draft complete | API only |
| **6 (Wed)** | One human hostile read if a reader exists; release repo with run records; arXiv account and endorser ready; site pushed with frozen claims only | arXiv-ready | $0 |
| **7 (Thu)** | Buffer. Submit to arXiv. Ten-slide deck from the paper: the negative theorem, the artefact with a one-line program, the audit, the roadmap (the from-scratch "digital abstraction" model), the ask | done | $0 |

**Budget.** Modal ≤ $250 planned, $300 reserve; Claude/Codex ≤ $200; **total ≤ $750**, leaving ~$1k untouched for a
second DAUDIT round and investor follow-ups. T-B (the origin of the lookup) is not in the week; it is the first paid
experiment after funding.

**Not this week.** New theory; brainstorm rounds; any fine-tune; CFD; more than two agents at once (one builder, one
auditor); decisions after 23:00; any public push before Gate B.

**What "worth it" means here.** The week does not recover the four weeks; it converts them. The assets that exist
(the Lean package, Savant, SCAN, STACK, REMEMBER, the audited record, and now the language) become one paper and one
demo that say exactly what is classical and what is new. Investors who are ML researchers fund people who can say that.

### 3.1 An honest reading of the two targets

**(a) A theoretical advance worth Nature.** Not reachable in weeks from the current slate. After the 29 Oct searches
the theory is "classical results, formalised, plus narrowings" (`RESULTS_LOCK` §8.5–8.7): the necessity half of Theorem
P, the explicit no-finite-test decoder, the margin version, the decoder class theorem, and the Lean package. These are
real and publishable; they are not a result that changes what a broad scientific audience believes, which is what
Nature publishes. The route to a Nature-calibre result runs through one of the genuinely open problems in
`FRONTIER.md` §D, held for one to three months with a strong-inference design. The candidates are in §3.4. My honest
odds that one of them yields a Nature-calibre law within three months: under 10 %. That it yields a strong ICLR/NeurIPS
or TMLR paper: better than even, if done as described.

**(b) A demo that opens funding and recovers costs.** As measured on 29 Oct the live model is worse than its own base
on investor prompts (0.54 vs 0.73), certifies wrong answers, and loops. A demo cannot be shown in that state, and R5 as
specified is mostly engineering (library splice, BigInt check, honest failure, scan). Those fixes are worth doing
because they are cheap and they remove the disappointments the audit found; but the demo will not "freak out" an ML
researcher by itself, because every component has a Python twin and the referee-grade reader will say so. What that
audience *will* respect: a crisp negative theorem they did not know (no finite test certifies history-keeping
decoding), a working artefact whose every tick is bitwise equal to a checked row, a scan that adds a million digits
inside the model, an audit that the authors ran against themselves, and a founder who can say exactly what is classical
and what is new. The funding case is the research direction plus the credibility of the paper, not the chat quality
of a 4B model. The $6,300 is recovered by a grant or a seed cheque, and those are won by the paper and the honesty,
not by the page.

So the order is: **paper first, demo second, new theory in parallel but small**, and the management rules below apply
from Monday.

### 3.2 Stop

- New brainstorm rounds with multiple "minds". Every round so far has produced zero survivors; the gates found the
  same classical theorems each time. The cost is Neo's attention and the credit.
- New architecture, loss or block ideas at ≤100 M parameters (Law 1; §2.9).
- Autonomous overnight research (new programmes, amendments, claims written by agents between 23:00 and 08:00).
  Registered jobs may run; nothing else.
- Any new public artefact (HF upload, site push with claims, arXiv) until the claim set is frozen and audited.
- The paper rewrite loop. One more rewrite, from a frozen, audited claim table, and then it is done.
- Cursor/Grok lines (already stopped by Neo on 29 Oct); keep Codex for audits and agy only for retrieval.
- Spending above $50/day for the next two weeks, and above $350 for November in total.
- The CFD/Well/dysts simulation lines (closed on 27 Oct; keep closed).
- Per-skill adapters, in-model aimed kicks, revisable memory, self-predictive states, energy dynamics, latent loops in
  Qwen: all killed by their own registrations; they stay in the graveyard.

### 3.3 Keep

- The Lean package and `THEOREMS.md` (the single most defensible asset).
- Savant r3/Loom and the harnesses (pinned clock, SCAN, REGVM, REMEMBER, UNIVERSAL), as audited.
- `RESULTS_LOCK.in.md`, the ledgers, `INSIGHTS.md`, `ANOMALIES.md`, `TENSIONS.md`, `GRAVEYARD.md`, the prior-art
  surveys L1–L6 and Neo's deep-reading report. Together they are a map nobody else has.
- The discipline that worked: registration commits, per-run ledgers, positive-confirmation certifiers, citation
  verification scripts, Codex read-only audits with checklists, the hostile referee pass.

### 3.4 Week by week

**Week 1 (3–9 Nov): reading week. $0 of compute. No agents except to fetch PDFs.**

Neo reads, himself, in this order: Moore 1956 (Gedanken-experiments), Chow 1978, Cai–Shin–Song 2017, Lewandowski–Machado–
Schuurmans 2026, Abbe et al. 2024, Brandoit et al. 2026, Bugaud 2026a/b, Casey 1996, Hahn 2020 and Hahn–Rofin 2024,
Xiang 2026, Jelassi 2024 and Guo 2026, Olsson et al. 2022 (induction heads), and the `DEEP_READING_QUESTIONS.md` list.
He writes `research/meta/MAP.md` in his own words, two pages: what is proven by others (with the exact scope), what the
project has that is new, and the three open problems he would bet on, each with its closest published result and the
delta in one sentence. This file, not an agent's bulletin, is the basis for every later decision.

*Decision point 1 (9 Nov).* Choose exactly one theory problem from §3.5, or decide that the theory line pauses and
the month is paper plus demo. Either is a good outcome. "Both" is not allowed.

**Weeks 2–3 (10–23 Nov): the paper, and one strong-inference programme.**

*Paper.* One author pass by Neo from a frozen claim table (the audited rows of `RESULTS_LOCK` only), in the shape the
record already recommends (`SUBMISSION_PLAN.md`: one voice, hostile reads, release repo). Working title shape: *A
pretrained language model as the certified executor of the programs it writes.* Contributions, stated with credit:
the theorem pair (necessity and the no-finite-test decoder, after Moore, Chow, Cai, Lewandowski), the cache-policy
equivalence, the Lean package, the system (Savant, SCAN to 10⁶ digits, REMEMBER across ten families, REGVM to 30,000
steps), the drift anatomy (BRIDGE), and a limitations section that prints DAUDIT's numbers and the boolean/Dyck
costs. The small-tracker results (v1) become one section or a companion note, with Brandoit and Bugaud cited as the
per-step theorems they are. Post to arXiv when two outside humans have read it. Venue: a top ML conference or TMLR;
not Nature, for this paper. Cost: $0 and Neo's time.

*Theory programme.* One of the three below, registered in a two-page document Neo writes himself, with three
competing hypotheses, one crucial experiment, the seed count, the statistic, the selection rule, the search terms that
would make it "not ours", and a stop rule. Budget $150–200. One builder agent, one auditor agent.

*Demo.* R5 Tier 0 only (harness and page, no training): honest failure, the independent BigInt check, library splice
with cached certificates, anchor-constrained reading, the scan, "when to compute", the certificate on the page.
≤$100. Acceptance is DAUDIT re-run with the corrected scorer: the clock arm must beat base on the shared 70 items and
show zero certified-but-wrong answers. If it does not by 23 Nov, the demo is the paper's page with the three verified
proof moments (Theorem P necessity live; pinned vs history side by side; the million-digit scan with the BigInt check)
and nothing more.

*Decision point 2 (23 Nov).* Paper on arXiv or not; demo passes DAUDIT or is reduced to the proof-moments page;
the theory programme's crucial experiment has a result that excludes at least one hypothesis, or the programme is
shelved with its scorecard.

**Week 4 (24–30 Nov): the pitch.** A ten-slide deck built from the paper: the negative theorem, the artefact, the
audit, the roadmap (the from-scratch "digital abstraction" model Neo described on 27 Oct, as the funded vision), and
the ask. Every novelty sentence in the deck labelled verified/unverified in Neo's own notes, per his 28 Oct rule.

### 3.5 The three candidate theory problems (choose one)

Each is open as far as the 29 Oct searches went, uses something only this project has, and admits a crucial
experiment. Each needs its own prior-art search *before* registration; I give the first search terms.

**T-A. Where does a real decoder fail, and why?** (`FRONTIER` §D1–D2.) Every influence bound is vacuous at
practical lengths; plain Savant fails at 4k–12k and REGVM's history runs at ~2k. Competing hypotheses: (H1) softmax
dilution of the program's rows (Xiang-type), (H2) content-address collisions on the tape (Jelassi, Guo), (H3) loss of
the pointer (BRIDGE's "misread event first"). Crucial experiment: hold context length, collision count and pointer
difficulty as three independently varied factors on Savant with the pinned twin as the zero-drift control; register
each hypothesis's predicted ordering of first-error distributions; score prospectively on held-out tapes. Note that
HORIZON (29 Oct) already killed the collision *law*; the question here is the factorial separation, not a law.
Search first: "first error position transformer long execution", "attention dilution vs collision ablation".
Budget $150. Kill: no hypothesis beats a length-only baseline by the registered margin.

**T-B. When and why does pretraining build the lookup?** (`FRONTIER` §D9; ANOMALIES A6–A7, A18.) OLMo-2 has the
finder at 84 B tokens and not at 5 B; the read-out is one vector away in Qwen3 ≥4 B. Competing hypotheses: (H1) it is
the induction-head phase change of Olsson et al. 2022 and nothing more, (H2) a separate content-addressed
"destination-reading" circuit appears later and tracks table-like text in the data, (H3) it is a property of scale,
not tokens. Crucial experiment: on public OLMo-2 checkpoints (and Pythia), measure the finder's row-selection margin
and the induction score along training; then continued-pretrain two matched small models on table-like vs control
text and test the finder. This is cheap, uses public checkpoints, and is a clean paper *whichever* hypothesis wins.
Search first: "induction heads phase change checkpoints", "in-context lookup circuit emergence pretraining",
"OLMo checkpoints circuit formation". Budget $200. Kill: the finder's margin and the induction score are collinear
across every checkpoint (then it is Olsson, and you cite them).

**T-C. Certified compilation from language.** (`FRONTIER` §D5; GATE2 G3's surviving form; red-team D's open C3.)
The model's own table, certified sufficient against an executable reference by a finite conformance test with a
justified state bound, plus conformal coverage of machine classes and truth-preserving interactive refinement. This
is where the demo's "how do I know it's right?" lives, and the W-method is already in Lean. But it needs human
subjects for the question-answering step and belongs to a PL/HCI venue. Budget $100 plus ten people. Search first:
"interactive program synthesis distinguishing inputs user study", "conformal prediction over automata classes",
ExReg (TOSEM 2026), Nguena Timo 2026.

My recommendation: **T-B**, because its outcome is informative either way, its data are public, and it is the one
place where the project's measurement machinery (UNIVERSAL, CIRCUITS) meets a question nobody in the record has
pre-empted. T-A second. T-C is the demo's real bottleneck and should be done as engineering first (Tier 0), theory
later.

### 3.6 The operating rules (the research operating system)

1. **One programme at a time**, chosen in writing by Neo, held for at least two weeks.
2. **Map before build.** A problem is not registered until its three closest published results are named with scope
   and the delta is one sentence. A live search (Codex `--search`) runs on the delta *before* any spend.
3. **Strong inference.** Every paid run has at least two competing hypotheses and an outcome table saying which
   outcome kills which. If no outcome changes the next step, the run is not made.
4. **Registration covers the decision**, not only the run: seeds (n ≥ 10 for any "every seed" claim), statistic,
   selection rule, search terms, stop rule, and what will be claimed if it passes.
5. **Lakatos scorecard** per programme: novel predictions made/confirmed/failed; narrowings. Two narrowings without a
   confirmed novel prediction shelves the programme.
6. **No decisions at night.** Jobs run; nobody launches, amends or claims between 23:00 and 08:00.
7. **Audit before relay.** Every agent result is "unaudited" until an independent agent with only the code and records
   reproduces the count; nothing unaudited reaches Neo as a conclusion, the paper, or the public.
8. **Agents are instruments.** One orchestrator, one auditor, one builder at a time. Brainstorms only on a question Neo
   has read into, with live search, blind bundles, no convergence scoring, and a one-hour reading cap on the output.
9. **A weekly Dealer.** One hour, one claim, one or two humans who know the adjacent field and are asked to disagree.
   If Neo has no such person, finding one is the first task of week 1; a mathematician or theoretical computer
   scientist who has read Chow and Casey is worth more than any number of agents.
10. **Budget by programme**, not by agent: $0 in reading week; ≤$350 for November; Claude ≤$300/month; and a written
    stop at any programme's cap.
11. **Public artefacts only from frozen, audited claims.** The site, HF and arXiv change at most once per decision
    point.
12. **Rest.** The 39 % night share is not a badge. Hamming's "open door" and Hadamard's incubation both require
    time away from the problem.

### 3.7 Next week, as a checklist

- [ ] Mon: write the stop list into `research/meta/STOP.md`; stop everything on it; settle every Modal call.
- [ ] Mon–Fri: read the fourteen papers in §3.4; write `MAP.md`.
- [ ] Wed: find the Dealer (one person); book the first hour for the following Monday.
- [ ] Fri: freeze the claim table from `RESULTS_LOCK` (audited rows only) into `research/meta/CLAIMS_FROZEN.md`.
- [ ] Sun 9 Nov: decision point 1, written in `MAP.md`: which single theory problem, or none.

---

## Part 4. New sources of creativity and deeper ideas

Angles the record has not taken, or has taken only as metaphor. Each with why it might matter and a cheap test.
Prior-art risk is stated; none of these is claimed open without a search.

1. **Conformance testing as the home field, not the analogy.** The theorem pair is Moore/Chow specialised to decoders.
   The unasked question in that field's terms is *testability*: for which decoders does a finite checking sequence
   exist at all, and can the implementation state bound be *measured* (from attention entropy, cache size, or an
   observability probe) rather than assumed? Lee & Yannakakis's 1996 survey of FSM testing and the checking-sequence
   constructions are the primary texts. Cheap test ($20): build checking sequences for Savant's own tables and run
   them against plain decoding at several lengths; a decoder that passes a checking sequence for bound m and then fails
   is a measured violation of its own state bound, which is a new kind of measurement. Risk: Chow, Vasilevskii,
   Huang & Peleska; search "checking sequence neural decoder".

2. **Quantitative fault tolerance, not the restoring-organ metaphor.** Von Neumann 1956, Pippenger 1988 and
   Evans–Schulman give thresholds for reliable computation from noisy gates. Savant has a measured per-tick near-tie
   flip rate (8 of 72,000 under batching) and a per-row margin distribution. Pencil test ($0): the redundancy (number
   of certified lookups per step, with majority) needed for an N-step run to be exact with probability 1−δ, as a
   function of the measured rate; then one $10 experiment. Risk: MAKER's voting, GATE1 C3 (Hoeffding is elementary);
   the delta must be the measured-rate threshold, not the voting lemma.

3. **Developmental biology of circuits.** T-B above, stated more broadly: treat pretraining checkpoints as a
   developmental series and ask what *data* statistics predict the appearance of the lookup (table-like text, code,
   repeated structure). OLMo-2's released data order makes this a real experiment. Cheap ($50). Risk: Olsson 2022 and
   the induction-head literature; "data-dependent emergence of circuits" searches.

4. **Measure influence instead of bounding it.** Every theoretical influence bound is vacuous; nobody in the record
   has *measured* the influence of one prompt bit on the output as a function of distance, in Savant versus base,
   with a mutual-information estimator and a plain-decoding baseline. A curve with a knee would be the "non-vacuous
   horizon" the frontier asks for, as a measurement. Cheap ($30). Risk: Barbero et al. 2024 (over-squashing),
   lost-in-the-middle studies, Chuang's lookback ratio; search "empirical influence decay position transformer
   mutual information".

5. **The human in the loop as the certificate: an HCI/PL study.** "Short teaches long" survived the gates only as an
   interface with a guarantee: the model emits a W-method suite of short cases; a person confirms them; the long
   answer is then certified relative to their answers. That is a user study, not a theorem: how many questions, how
   often people err, whether they can read the suite. Ten participants, $0 compute. Risk: ExReg (TOSEM 2026),
   TiCoder, ClarifyGPT, Nguena Timo 2026; the delta is the every-length guarantee carried by the per-row certificate.

6. **Validation versus verification, borrowed properly.** "Certified but wrong" is the formal-methods distinction
   between verification (against the written table) and validation (against intent). The field's cheap validators
   are N-version compilation plus minimised-DFA equivalence (which would have accepted the 11 renamed-state tables of
   82) and result checking (residues mod small primes for arithmetic). Cheap ($10): implement both as page checks and
   measure the drop in DAUDIT's disappointment 1. Risk: SemRegex 2018; the delta is engineering, say so.

7. **Placekeeping, quantitatively.** Altmann, Trafton & Hambrick 2014 find that interruptions double sequence errors
   and leave step errors alone. BRIDGE finds plain decoding fails at the pointer first, then by step drift. A short
   perspective paper that puts the two error-type ratios on one plot, across interruption length and context length,
   costs $0 and connects the project to a cognitive-science audience the demo wants. Risk: the L6 survey already lists
   the analogy; the delta is the quantitative comparison.

8. **Mine what you already have before generating more.** `ANOMALIES.md` lists 26 unexplained observations over 2,672
   runs. A strong-inference pass ($0) that assigns each anomaly to one of three mechanisms (dilution, separation,
   pointer) and finds the anomalies that *no* mechanism explains is more likely to surface a law than another round of
   minds. This is Kuhn's "exploration of the area of anomaly", done on data already paid for.

9. **The research operating system as a public artefact.** Part 3.6, written up honestly with the numbers in §0, is a
   contribution in its own right: few people have run a twelve-day, 1,900-commit, multi-agent research programme and
   audited it. A post or short paper on "what agents are for in research, measured" builds the lab's credibility with
   exactly the audience Neo wants, and it costs nothing. Risk: the AI-scientist evaluation literature (SoundnessBench,
   the ideation–execution gap); the delta is an audited first-person record.

10. **A survey/tutorial.** The project has ~700 verified records across six surveys and a 157 KB atlas. "Exact state in
    neural sequence models: a map of what is classical and what is open" is a publishable survey, cheap to finish,
    and the fastest way to become the person the field cites on this topic. It also forces the reading that §3.4
    asks for.

11. **The funded vision, kept separate from the week's work.** Neo's 27 Oct remark is the right long-term programme: a
    model trained from scratch in which the clock, the state slot and the certified lookup are native architecture, so
    that exactness is a property of the machine rather than a harness. Percepta and Giannou build such machines by
    hand; the delta is learned and certified. It is a one-to-two-year programme and belongs in the pitch as the
    destination, not in November as a task.

---

## Closing

What the evidence shows: twelve days, ~1,900 commits, ~$2,700 on ledgers (~$6,300 in all), twenty-five programmes,
six goals, fifteen refuted theorem statements, seven withdrawn empirical headlines, eight of eight theory claims
partially known, thirteen of thirteen brainstorm finalists killed or narrowed, and a demo that loses to its base model
on investor prompts; alongside a Lean package, a working certified executor, and an honest record. What I interpret:
the project did the hard parts (building, formalising, auditing, writing things down) and skipped the parts that
decide whether the hard parts matter: reading the field first, choosing one problem and holding it, designing
experiments that exclude, and letting a human think at the decision points. Those are the cheapest parts of research,
and the only ones that cannot be delegated.

The plan is deliberately small: a reading week at $0, one paper from frozen claims, one strong-inference programme at
≤$200, a demo gated by its own audit, and twelve rules. If it is followed, by the end of November there is a paper on
arXiv that nobody can embarrass, a demo that does not disappoint, and either one new result on the way or a clean
decision that the theory line pauses. That is a better position than any night of twelve agents has produced.

**Added 30 Oct, after Neo's reply (one week, $1–2k).** §3.0 is the plan for the week; §1.7 inventories the fifteen
assumptions the record never questioned and why the brainstorms could not; `LANGUAGE_NOTES.md` in this folder is the
design memo for the language, written for the orchestrator as a thinking partner. The one-sentence version of all
three: put the facts in the weights, the program in a few tokens, the scheduling in the harness, and the human's
attention on what is absurd about the artefact.

What I could not check: the full prior-art surveys L1–L6 and the ATLAS (I relied on `RESULTS_LOCK` §8 and the
GRAVEYARD, which summarise them), the paper text itself, the large Cursor/Codex logs, and Neo's unrecorded time and
Claude/Cursor spend beyond the figures in the memory notes. The Modal total is a floor.

---

## Sources

**Record (all verified, read in this study).** Memory files in `~/.claude/projects/-Users-neo-repos-polyformer/memory/`;
`research/OVERNIGHT_2026-10-28.md`; `research/INSIGHTS.md`; `research/audit/{priorart_dec,priorart_all}/out.md`;
`research/audit/codex2/out_r4.md`; `research/audit/needle_gate2/out.md`;
`polyformer-wt/theory/research/theory/{needle/FRONTIER.md,TAKEN.md,GRAVEYARD.md,needle/BRIEF.md,needle/BRIEF2.md,needle/GATE1.md,BULLETIN_1.md,BULLETIN_2.md,ROUND1_BRIEF.md,ATLAS_BRIEF.md,needle/round/codex.md,needle/round2/opus.md}`;
`polyformer-wt/paper-v2/paper/jewel/RESULTS_LOCK.in.md` §5, §8; `polyformer-wt/r5audit/research/r5audit/DAUDIT.md`;
`research/{PLAN,NOVELTY,LEAP,WHITEBOARD,WHITEBOARD2,MORNING,QUESTIONS,SUBMISSION_PLAN,CONTRIBUTIONS,HANDOVER,PAPER_V2_PLAN,R5_SPEC,THEOREMS}.md`;
`research/brainstorm/{CANDIDATES,FACT_SHEET,THESIS_CHECK,REDTEAM_D}.md`; `research/debate/03_redteam.md`;
`research/cursor/COMMON.md` (demodesign worktree); `research/r4/R4_BRIEF.md` (r4 worktree); `research/cursor_logs/RESUME.md`;
side-session notes `validate-blocks.md`, `frontier2.md`, `proofs-positioning.md`; `git log --all`; 652 ledger files
(script: `scratchpad/ledgers2.py`, de-duplicated by call id).

**Literature.**
- Platt, J. R. (1964). Strong Inference. *Science* 146(3642):347–353. **Verified** (read the scan):
  [WHOI copy](https://www.whoi.edu/cms/files/platt64sci_72743.pdf), [Gwern copy](https://www.gwern.net/doc/philosophy/epistemology/1964-platt.pdf).
- Chamberlin, T. C. (1890/1965). The method of multiple working hypotheses. *Science* 148:754–759. **Verified** via Platt's quotation and the
  [reprint record](https://railsback.org/railsback_chamberlin.html).
- Hamming, R. (1986). You and Your Research. **Verified** (read the transcript):
  [UVA transcript](https://www.cs.virginia.edu/~robins/YouAndYourResearch.html), [Gwern](https://gwern.net/doc/science/1986-hamming).
- Alon, U. (2009). How to choose a good scientific problem. *Mol. Cell* 35:726–728. Citation verified; wording from
  [summary](https://li.me.jhu.edu/wp-content/uploads/Alon_2009.pdf) (unverified).
- Heilmeier catechism (DARPA). [Caltech summary](https://murray.cds.caltech.edu/Heilmeier_Catechism); second question's wording unverified.
- Feynman, R. (1974). Cargo Cult Science. *Engineering and Science* 37(7):10–13. **Verified** (read the text):
  [Caltech](https://calteches.library.caltech.edu/51/2/CargoCult.htm).
- Medawar, P. (1964/1967). "If politics is the art of the possible, research is surely the art of the soluble." Unverified wording;
  [Wikiquote](https://en.wikiquote.org/wiki/Peter_Medawar).
- Lakatos, I. (1970). Falsification and the methodology of scientific research programmes. **Verified** via the
  [Stanford Encyclopedia entry](https://plato.stanford.edu/entries/lakatos/) (quotations above are from it).
- Kuhn, T. (1962). *The Structure of Scientific Revolutions.* Unverified wording; [overview](https://en.wikipedia.org/wiki/Normal_science).
- Popper, K. (1963). *Conjectures and Refutations.* Unverified wording.
- Gelman, A. & Loken, E. (2013). The garden of forking paths. Citation verified; [Columbia PDF](http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf).
- Nosek, B. et al. (2018). The preregistration revolution. *PNAS* 115(11):2600–2606. Citation verified; [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500).
- Ioannidis, J. (2005). Why most published research findings are false. *PLoS Med* 2(8):e124. Citation verified; [CMU copy](https://www.stat.cmu.edu/~ryantibs/journalclub/ioannidis_2005.pdf).
- Sutton, R. (2019). The Bitter Lesson. **Verified** quotes via [mirror](https://mlanthology.org/misc/2019/sutton2019misc-bitter); original at incompleteideas.net.
- Hadamard, J. (1945). *The Psychology of Invention in the Mathematical Field.* Citation verified; stage model via [Liljedahl](https://emis.univie.ac.at/proceedings/PME28/RR/RR116_Liljedahl.pdf) (unverified wording).
- Koestler, A. (1964). *The Act of Creation.* Unverified wording; [overview](https://en.wikipedia.org/wiki/The_Act_of_Creation).
- Perutz's "no committees" line: unverified; [secondary](https://corporate-rebels.com/best-research-institutes).
- Xerox PARC Dealer meetings: unverified; [secondary](https://news.ycombinator.com/item?id=14118290).
- Shannon's timeline (1939 letter; paper substantially complete by end of 1944): unverified; [history](https://en.wikipedia.org/wiki/History_of_information_theory).
- AlphaFold CASP13→CASP14: unverified; [overview](https://en.wikipedia.org/wiki/AlphaFold).
- Bahdanau attention origin (five-week internship): unverified; [Karpathy thread](https://threadreaderapp.com/thread/1864023344435380613.html).
- Transformer origin: unverified; [overview](https://en.wikipedia.org/wiki/Attention_Is_All_You_Need).
- ResNet motivation (training error rises with depth): unverified beyond the paper's own framing; arXiv 1512.03385.
- Diffusion (Sohl-Dickstein 2015 → DDPM 2020): unverified beyond summaries; arXiv 1503.03585, 2006.11239.
- Lipton, Z. & Steinhardt, J. (2018). Troubling trends in machine learning scholarship. Citation verified; [arXiv 1807.03341](https://arxiv.org/abs/1807.03341).
- Dyson, F. (2009). Birds and Frogs. *Notices AMS.* Unverified wording. Weinberg, S. (2003). Four golden lessons. *Nature* 426:389. Unverified wording.
- Thurston, W. (1994). On proof and progress in mathematics. Citation verified; [arXiv](https://arxiv.org/pdf/math/9404236). Rota, G.-C. (1997). Ten lessons. Unverified wording.
- Stokes, D. (1997). *Pasteur's Quadrant.* Unverified wording; [Brookings](https://www.brookings.edu/book/pasteurs-quadrant).
- Si, C., Yang, D. & Hashimoto, T. (2024). Can LLMs generate novel research ideas? [arXiv 2409.04109](https://arxiv.org/abs/2409.04109);
  and (2025) The ideation–execution gap, [arXiv 2506.20803](https://arxiv.org/abs/2506.20803). Unverified beyond abstracts.
- SycEval (2025), [arXiv 2502.08177](https://arxiv.org/abs/2502.08177); Batzner et al. (2025), [arXiv 2512.00656](https://arxiv.org/abs/2512.00656). Unverified beyond abstracts.
- Prior-art works named in Part 1 (Whitney 1934, Moore 1956, Rabin 1963, Chow 1978, Casey 1996, Cai 2017, Abbe 2024, Lewandowski 2026,
  Brandoit 2026, Bugaud 2026, Xiang 2026, Green 2026, Xu 2026, Chung 2026, PAR 2026): verified only as reported in the project's own
  audits (`priorart_dec/out.md`, `priorart_all/out.md`, `RESULTS_LOCK` §8), not re-read by me.
