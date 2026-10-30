# LANGUAGE_IDEA: exhaustive grounded verification (24 Oct ~11:30, from Neo's earnings-call example)

## The problem class
A long document makes many claims; an exact source of truth exists (a table, a database, XBRL in an SEC filing, a
contract's terms, a codebase). Find every discrepancy. Frontier models know enough to judge any single claim, yet
miss errors in long documents, even when chunked. Tyen et al. (Findings of ACL 2024, arXiv 2311.08516) show the
general version: models cannot find mistakes but can correct them once located, and a small trained classifier
locates them better than a prompted large model.

## Why this is our problem, not a new one
1. **The frame drifts.** A transcript sentence often names no period or segment ("it grew 12%"). Checking it needs the
   discourse frame (entity, period, metric, unit) carried from earlier sentences. That frame is a finite state driven
   by sentences: our setting exactly, in real language.
2. **The objective is blind to the last miss.** Trained or prompted to output a list of errors, a model that finds 29
   of 30 loses almost nothing. That is the blindness theorem applied to recall. A per-sentence verdict makes every
   miss cost, which is a stiff signal.
3. **The checker is exact.** No soft checker is needed. The table certifies that paraphrases of a claim, reorderings of
   independent claims, unit and format changes ("$1.2 billion" vs "1,200 million") and inserted irrelevant sentences
   leave the frame and the ledger of errors unchanged. Those are the certified pairs.
4. **Coverage is designable.** Training documents come from random tables and random frames, so every frame state is
   reachable in short documents (today's coverage lesson).

## Plan
- **Stage 1, measure the problem** (~$20, no training): synthetic transcripts from random tables (hundreds of
  templates, frame shifts, pronouns, distractors) and real 10-K passages with XBRL ground truth, each with 30 injected
  errors of known kinds (wrong number, wrong unit, wrong period, swapped segment). Recall and precision for Claude
  Fable 5.1 and Gemini 4 Argon, whole document and chunked (GPT-6 Astra needs OpenAI credits). Success: frontier recall
  measurably below 100% where a perfect parser scores 100%.
- **Stage 2, our verifier**: frozen Qwen features plus a tracker that carries the frame and the ledger, reads the table
  through the frame, and outputs a verdict per sentence; arms O+N, EQ+N and FULL+N; trained on short documents,
  tested at 64x. Target: recall about 1.0 at length.
- **Stage 3, real text**: the same verifier on real 10-K passages.

## Risks
Number parsing by frozen 0.5B features; real text far from the templates (coverage again); claims that need
arithmetic (year-over-year changes): start with direct lookups.

## Literature to take from (to verify and cite)
Tyen et al. 2024 (BIG-Bench Mistake); Lightman et al. 2023 (process supervision beats outcome supervision: the
stiff-signal argument in RL form); contrast sets (Gardner et al. 2020) and counterfactually augmented data
(Kaushik et al. 2020) as minimal pairs; entity tracking (Kim & Schuster 2023); Michelangelo's Latent List
(Vodrahalli et al. 2024, arXiv 2409.12640); RULER and BABILong; FinDVer (EMNLP 2024, arXiv 2411.05764); FinVerBench
(2026, arXiv 2605.29586: XBRL as ground truth, already used); FActScore and SAFE (atomic claims).
