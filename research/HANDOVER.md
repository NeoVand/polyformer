# Handover, 22 October 2026 (evening)

Everything below is on disk; nothing depends on an open laptop except the one paraphrase run, whose
Modal jobs finish on their own under 600 s caps.

## Notes written in the main checkout (untracked there; copied to branch `claude/notes-2026-10-22`)
- research/FIELD_GUIDE.md: the 19k-word field guide (also a Claude Doc artifact).
- research/WHITEBOARD.md: reading notes on tokenization, depth/lookup, global addresses.
- research/BLOCK_THEORY.md: properties A1-A5, B1-B5, C1-C4; theorems T1-T3.
- research/CANDIDATES.md: K0-K3 with guarantees and the validation ladder.
- research/debate/01-05 and research/DEBATE.md: the multi-agent debate and the judgement; section 7 addendum.
- research/ENERGY.md: the single-energy form and tests E0-E2.
- research/WHITEBOARD2.md: the retrospective, six laws, directions D1-D4.
- research/EXACTNESS.md: the selection theorem, the invariance term, results and corrections (sections 1-5).
- research/figures/k0h_graph.svg: the K0 ⋈ H compute graph (design rejected).

## Branches with experiments (all unpushed, all with reports and settled ledgers)
| branch | worktree | report | spend | verdict |
|---|---|---|---|---|
| claude/exciting-antonelli-dc7582 | REVISE | research/REVISE_REPORT.md | $32.98 | revisable memory, routing, selective attention: all worse at 2k |
| claude/t1-stability-202fdb | T1 | research/T1_REPORT.md | $15.23 | type stability = content-ness; insight contradicted |
| claude/t2t3-addresses-988f5b | T2 | research/T2_REPORT.md | $10.74 | hashed n-gram input addresses −0.79% at 22M/2k (one seed) |
| claude/k0h-build-0a3603 | build | research/K0H.md | $0 | K0 ⋈ H implemented behind flags, paused |
| claude/validate-blocks-a004fd | validate | research/VALIDATION.md | $3.48 | V1-V5, V8: all fail as registered; per-event recurrence extrapolates |
| claude/energy-e0e2-ee2b47 | E0/E2 | research/ENERGY_E0E2.md | ~$9 | energy signature cannot appear; group-manifold state 4/6 exact |
| claude/energy-e1-779455 | E1 | research/ENERGY_E1.md | $9.33 | joint energy model: one hop per $10; AR with running-state labels exact |
| claude/selfstate-4935b5 | selfstate | research/SELFSTATE.md | $18.11 | self-predictive state: S1/S2 fail, S3 hybrid −0.11% on near repeats |
| claude/invariance-3e22f3 | invariance | research/INVARIANCE.md | $3.89 | **invariance term selects exact states: 3/3 to 1024 events with random partners** |
| claude/practical-colden-7d7559 | paraphrase | research/PARA_INVARIANCE.md (+ PARA_RESUME.md) | ≤$10 | running at handover; language form of the invariance term |

## State of the question
The one prediction that came true: an invariance loss over Nerode-equivalent histories, measured in the
readout's normalisation, makes a per-event recurrence exact far past its training length (EXACTNESS.md §5).
Open: whether paraphrase invariance does the same on language-shaped data (the paraphrase run).

## To resume
Read research/PARA_RESUME.md in the paraphrase worktree for job ids and settle commands; everything else
is complete. Memory index: ~/.claude/projects/-Users-neo-repos-polyformer/memory/MEMORY.md.

## Added 23 October
| branch | report | spend | verdict |
|---|---|---|---|
| claude/gracious-panini-dde55f | research/PROOFS.md, research/POSITIONING.md | $0 | A1-A6 proved with corrections; bisimulation lineage verified; no prior extrapolation result found |
| claude/fervent-gagarin-ef7e03 | research/LEAN_FEASIBILITY.md | $0 | Lean certifies both halves; natural proofs short; stage one = certified rewrite chains |
| claude/gallant-panini-8f54d6 | research/EXEC_INVARIANCE.md | $0 | code-execution generator built, stopped before registration |
| claude/lean-s1-1e6431 | research/LEAN_S1.md | $9.85 | **every registered prediction passes: R+I exact at 1024 steps (128x) on 3/3; R and T collapse; control destroys** |
Notes: research/LEAN_PLAN.md, research/QUESTIONS.md (also on claude/notes-2026-10-22).

## Night of 23 October (second $100)
| branch | report | spend | verdict |
|---|---|---|---|
| claude/lean-h-26e3bd | research/LEAN_H.md | $12.62 | NextLat exact too (3/3 at 256, 2/3 at 4,096); combination exact to 4,096 3/3, lowest floor; no transformer exact at training length under 2×; tier 2: term 0.47→0.90, no seed exact; floor lever works |
| claude/exec-d-0e1910 | research/EXEC_D.md | $2.29 | code domain: R+I exact 2/3 at 256 where R is 0.05–0.25; control collapses; T 0.26 |
| claude/lean-n-data-34a2d2 | research/LEAN_N_DATA.md | $0.67 | natural-proof dataset built (2,850 train, 82 Lean-confirmed novel-premise test of 8–15 steps; ≥16 bin too thin) |
| claude/lean-s-2b865a | research/LEAN_S.md | $13.57 | six seeds: R 0/6, R+I / R+NL / R+NL+I 6/6 at 256; data axis NextLat 8/8, invariance loses at 80k (1/3); width axis LR mismatch |
| claude/prover-proxy-3d70be | research/PROVER_PROXY.md | $1.10 | imagination search = kernel's search; 1 kernel call per solved problem vs 64/442; drift hurts after long prefixes |
| claude/metric-0160e1 | research/METRIC.md | ≤$35 | running (T8.1–T8.3′) |
| claude/lean-n-train-a0a5e2 | research/LEAN_N.md | ≤$45 | running (main batch, six arms) |
Notes added: research/PAPER.md (skeleton), research/DESIGN_NEXT.md, EXACTNESS.md §8–8.1.
| claude/metric-0160e1 (interim) | research/METRIC.md | $6.48 so far | T8.1 pass: the metric loss alone is exact at 256 and 1,024 on 3/3 (tier 1); T8.2: nobody exact on tier 2, order R+NL+I 0.92 > R+I 0.89 > R+NL 0.84 > R+M 0.81 > R 0.23–0.59; T8.3 (unmatched pairs) killed; T8.3′ (matched pairs, γ 0.9) running, pilot probe 0.42–0.52 vs 0.27 |
| claude/lean-s-2b865a (addendum) | research/LEAN_S.md | $13.57 + ~$3 | 80k anomaly explained: drift from a diluted term; 4× partners or μ = 3 restore exactness 2/2 |
| claude/metric-0160e1 (final) | research/METRIC.md | $9.66 | T8.1 pass (metric alone exact 3/3); tier 2 = under-training (24k steps: R+NL+I exact 2/2; metric +0.10, floor grows); T8.3′ not killed, gains are the first-owner heuristic (probe 0.45, paired 0.07) |
| claude/intelligent-solomon-11ea28 | research/MECHANISM.md | ≤$10 | running: state geometry, cluster counts, systematicity |
| claude/lean-n-train-a0a5e2 | research/LEAN_N.md | $38.46 (cap raised to $60 for §7) | natural proofs as designed: fail; every arm memorises, exact only on `no goals`; the MLP head breaks extrapolation even on chains; fallback change-readout running (§7) |
| claude/intelligent-solomon-11ea28 | research/MECHANISM.md | $1.79 (+ ≤$8 item 4) | exact state = 960 pure clusters, ~20-d affine image of the Polish string, rewrites act as the induced permutation's linear map (not orthogonal); NextLat also minimal on exact seeds; NO generalisation to fresh atoms or a fifth atom (0.000) or held-out lemma events (18–51%); symbol-agnostic fix (fresh embeddings + pointer readout) running |
| claude/lean-n-train-a0a5e2 (§10) | research/LEAN_N.md | $42.05 total | change readout: chain gate passes; natural proofs: kind-of-step exact 0.90+, content tokens never produced (rewrite 0–2%, hyps 6%), free-running 0.000 all arms; obstacle = content generation, not tracking |
| claude/intelligent-solomon-11ea28 (§5) | research/MECHANISM.md | $1.79 total | symbol-agnostic (fresh embeddings + linear pointer head): exact nowhere; atoms left at chance ((4/9)·ln 4); needs a content-matching pointer, not a linear head |
| claude/intelligent-solomon-11ea28 (§6, L1) | research/MECHANISM.md | $1.79 total | role-indexed atoms: fresh names solved by construction (bit-identical inputs, 512/512); a fifth role still 0.000; in-distribution 0.88–0.97 under the unchanged config; held-out pattern improves for the combination (0.50 at 64) |
| claude/lean-n-train-a0a5e2 (§11, L2) | research/LEAN_N.md | ≤$80 total | running: content as copying under substitution (role-indexed variables + pointer copy from premise statements) |

## Course correction (23 Oct, afternoon)

`COURSE.md`: the natural-proof block failed three readouts at the same place (new terms never produced). Diagnosis:
we scored strings, not kernel verdicts, and never added observations per step. Correction: stage two becomes a
kernel oracle (verdicts k steps ahead without the kernel). Pilot D1 registered there; data in session lean-n-data
(cap $6), training in lean-n-train (cap $18). The §11 content route stops after its gate report.

**D1 verdict (23 Oct evening):** negative; even the kernel-fed critic U is at the state-blind level (0.64–0.69), so the
natural-proof verdict function is not learnable from 2,565 theorems from scratch; chains stay exact. COURSE.md §7–8 has
the boundary statement and options A/B/C. D1 spend $5.53; block N training $50.14 of $80.

**D1 audit (23 Oct night):** numbers reproduce, no bugs, but the interpretation fails: U was a from-scratch late-fusion
critic with mismatched names, a head-word regression out-ranks every arm, and the protocol memorised with no model
selection. COURSE.md §9 registers rerun D1′ (U′ with cross-attention and consistent names, B′, head-word floor,
validation-selected checkpoints; cap $6) in session lean-n-train.

**D1′ (23 Oct night):** gate G′ fails; the true-state critic matches the head-word floor (0.69–0.75 vs 0.705/0.755);
natural-proof verdicts not learnable from scratch at 2,565 theorems. LEAN_N.md §13; COURSE.md §9.2; $1.71.

**EXEC_LM headline (23 Oct night):** latent slot on frozen Qwen2.5-Coder-0.5B features + term + next-latent is exact at
256 statements on 3/3 seeds after training at ≤16 (0.73–0.97 at 1,024); plain slot drifts to the floor by 256; chain of
thought 0.06–0.37 at 256 at 8 tokens/statement; direct arm below the floor. All four registered predictions pass.
`EXEC_LM.md` on `claude/exec-d-0e1910` (206e13a); COURSE.md §11; $21.33.

**Night 3 close (24 Oct early):** RMS-normalised slot exact at 1,024 on 3/3 (64×; local CPU); trap = routing by name
(random start 0.000; depth alone 0.90 failing −, <; factorised slot 0.998 at 16 but 0.75 at 256; Markov CoT 0.27 flat, no
collapse); A′ (32 bits) flat slot plateaus 0.76 at 16. EXEC_LM $55.77 of $60; COURSE.md §13 lists the proposed next $40.

**Funded runs (24 Oct, EXEC_LM §10, $36.55; total $92.31/$100):** RMS headline replicates on Modal 3/3 at 1,024; registers
exact at 16 on rung A 3/3 (plateau 0.72–0.77 at length, repair model's form holds with the late error), A′ 2/3 and collapse
at length; **Markov step trained on uniform states exact at 1,024 on 3/3 on the arithmetic rung** (8 tokens/statement,
fixed 74-token context); A′ flat plateau = coverage (firing conditionals). Paper draft: paper/nmi/ on gracious-panini
(af47503), revision requested with §10.
