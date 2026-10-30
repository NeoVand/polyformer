# R5 spec (draft; the disappointment audit, DAUDIT, fills in the rest)

29 Oct 2026. R5 is the demo model and page shown live to ML-researcher investors and ordinary users. Acceptance is
an empty disappointment list on the DAUDIT battery (worktree `r5audit`), plus people trying it.

## Lessons carried from r4 (audited 29 Oct, `r4/research/r4/audit/codex_audit.md`)
1. **KL to the reference on every RL update**, not cross-entropy rehearsal. r4's RL had no KL, and WikiText
   perplexity rose about 40% (13.8 → 19.3).
2. **The reward must include number-mode rows.** In r4, `reference_rows` returned no rows for numeric specs, so
   numeric rollouts lost up to 0.25 reward.
3. **Targeted data works where it is aimed.** The coin template went from 14 to 43 correct. Nothing else moved: held-
   out R1 +2.6 points, R2 flat. No-clock fell (128 → 93). R5 must not trade the no-clock path or the families
   (733 → 700 pinned) for targeted gains.
4. **Every verifier path is run in CI on every result type.** r4's report verifier crashed on no-clock files.
5. **Save item ids and per-token losses** for MMLU and WikiText, so the language gates can be rescored.

## Engineering already known to be needed
- **Speed:** the certified parallel scan for addition (SCAN; about 3.5 s for 4,096 digits on H100 model time, about
  70× sequential). Browser: packed forwards with a block-diagonal mask, chunked; KV per chunk needs both caches
  (HANDOFF_PAGE.md, corrected numbers after scan-fix).
- **Cached certificates** for library tables (adder, subtracter, scan tables): certify once per model and runtime.
- **An independent answer check** (BigInt) shown on the page next to the model's answer.
- **Judgment on when to compute:** no programs for stack and nesting tasks (BBH boolean 22% vs base 97.6%, Dyck
  2.4%), and none for ordinary chat.

## To fill from DAUDIT
- The top disappointments, each mapped to a fix and an acceptance test.
- The latency budget per category.

## DAUDIT results (29 Oct; r5audit `299ee303`; unaudited; $8.51)
- **Read scores:** r4 0.60, Loom 0.54, base Qwen3-4B with thinking 0.73 (70 items). On the 70 shared items: r4 53,
  base 51, Loom 46.
- **Right:**
  - 20- to 1,000-digit add and sub, certified;
  - lamp logs; elevators to 200 moves;
  - no programs on chat, with chat replies at 0.2 s median;
  - "are you sure?" never flipped a verdict.
- **Disappointments, most damaging first:**
  1. A wrong answer with a passing certificate (r4 7, Loom 3): multiplication sent through the adder, a dropped
     sign, a number read twice.
  2. A confident answer after the program failed (r4 42 items, 23 wrong).
  3. State tables fail to compile on about 2/3 of first attempts ("a destination or the start is not a state").
  4. No answer: Loom loops to 11 calls; r4 to the token cap.
  5. Big arithmetic outside the library is made up (2^200, 50!, multiplication: 0/8).
  6. Slow: 53 s for 1,000 digits; 4,096 digits miss the 150 s deadline.
  7. Number reading breaks on typos, rephrasings and comma lists.
  8. "Show me the certificate" fails.
  9. Programs for "2 + 2".
  10. Nesting answers are uncertified guesses.

## The R5 build, in order (each item names the disappointments it removes)

**Tier 0. Harness and page (no training).**
1. **Honest failure** (2, 4): never answer confidently after a failed program or certificate. Say what failed. At
   most 2 retries. Stop on a repeated program.
2. **Independent check** (1): for arithmetic, parse the operands from the question with a deterministic parser
   (shown as such) and check the answer with BigInt. Show agree or disagree next to the certificate.
3. **Library by composition** (1, 5): certified multiply, power and factorial as compositions of certified
   library calls (Theorem C). Route any number above a size threshold to the library; never free-generate big
   arithmetic.
4. **Speed** (6): the parallel scan (WEBSCAN) for add and sub. Stream the answer sentence as soon as the certified
   value exists.
5. **Read input in place** (1, 7): quote operands by copying spans of the question, with robust handling of commas,
   typos and lists.
6. **Grammar-constrained table decoding** (3): destinations and the start must be declared states. This is known
   engineering (type-constrained decoding); use it.
7. **When to compute** (9): small operands are answered directly.
8. **The certificate on the page** (8): the page shows rows, margins and the bitwise check; the model points to it.

**Tier 1. The R5 fine-tune** (r4's lessons: a KL anchor, numeric reward rows, no trade against no-clock or families):
- compile data aimed at the measured failure classes (state tables, composite), DAgger repairs, phrasing and typo
  diversity;
- no stack programs unless STACK passes.

**Tier 2. From the theory track, if their kill tests pass:**
- STACK: certified nesting;
- ASKQ: sample-and-ask compilation;
- HORIZON: a predicted-failure panel for plain decoding.

**Acceptance:** the DAUDIT battery with the corrected scorer plus human reads, a fresh held-out battery, and people.
Target: the disappointment list is empty.

## Live check of the r5-harness branch (29 Oct, orchestrator, Loom on Apple M-series WebGPU)
- **"What is 2 + 2?":** "4", answered directly; the independent check agrees; 0.5 s. Good.
- **"Waht is 12,345,678,901,234,567,890 plus 98,765,432,109,876,543,210?":**
  - the model writes the whole 200-row adder at about 4–5 tokens/s (about 1,100 tokens, about 4 min);
  - it quotes the anchor "What is " from its training template, not the question's "Waht is";
  - the harness correctly refuses ("could not read its input"), then retries by writing all 200 rows again.

  Honest, but about 8 minutes to a failure.

**Two Tier-0 additions, the highest leverage for the demo:**
1. **Library programs are not re-written.** Once the model has written a library program's header (task and input
   lines), the page supplies the cached table, certified once on this device, instead of letting the model generate
   200 rows. The model still chooses the program and quotes its inputs. This saves about 1,000 tokens (about 4 min)
   per call.
2. **Anchors are constrained to the question.** While the model writes an anchor (`after "..." until "..."`), mask
   the logits so the quoted text must be a substring of the question. Reading in place becomes a decoding constraint,
   and typos and rephrasings stop breaking it.

## WEBSCAN result (webexport `aca19d25`; Apple M4, WebGPU, Node; unaudited)
- **Every addition matched BigInt digit by digit**, with lookups and margins certified on the device.
- **Brent–Kung, plain:** 64 digits 4.4 s, 256 digits 14 s, 1,024 digits 67 s, 4,096 digits 337 s.
- **Distinct-block packing** (each round runs one real forward per distinct block, since identical inputs give
  identical outputs): **4,096 digits in 9.3 s** (Hillis–Steele, 357 distinct lookups in 14 forwards).
  - This is the demo speed fix.
  - Disclose it on the page: "identical lookups in a round run once".
- **Plumbing:**
  - a top-2 graph patch (fetch only top id and logits on device): forwards 1.6–1.8× faster;
  - Q = 512 or 1,024 chunks fit 4 GB beside the model;
  - Π prefill 7.7 s once.
- **To check before it ships:** an audit that memoised mode runs real forwards for every distinct block and maps
  the results back correctly.
