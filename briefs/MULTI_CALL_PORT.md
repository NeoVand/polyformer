# MULTI_CALL port: REASON_FORMAT in the browser runtime and the chat

Branch `site-reason` (from `site-savant` 9ff5fc4b), 28 Oct. Spec: `research/reason/REASON_FORMAT.md` (branch `reason`,
42828bc3, with its §12 clarification). Reference: `research/reason/reason_core.py` and
`research/reason/fixtures/reason_fixtures.json` at ba619ecc. Spend: $0. Nothing pushed.

## What changed

**Runtime** (`src/lib/interpreter/webgpu/`)

- `reason.ts` (new) ports reason_core's clock side line for line:
  - `notesOf`/`sourcesOf`: S0 is the question; S1 is the notes, meaning the response with every `<program>…<exec/>` deleted.
  - `match`: exact first; then whitespace-relaxed over ASCII `[ \t\n\r\f\v]` only.
  - `locate`: falls through S0 to S1. An empty `before` stays in its own source.
  - `readCall`: the second number is retried once from (0, 0). `result k` citations come with the reference's error
    messages.
  - Also `lastCallStart`, `resultValueOf`, `errorFinalText`/`errorFinalIds`, and `limitAt`: 8 calls run, the 9th to
    11th get `error: too many calls`, and the 12th ends the response.
  - `isSubtracter` and `exactDifference` exist only for the page's own check.
- `pb.ts`: `parseGenerated(tok, ids, nl, { results: true })` reads `first|second: result k` into `prog.cites`. A later
  line of the same name replaces an earlier one, and the line falls through to the row check as in `parse_call`.
  Without the option the parse is exactly today's.
- `engine.ts`:
  - `ask(…, { multiCall: true })` runs `askMulti` (§7). It generates until `<exec/>` or `<|im_end|>` and parses the
    call from its last `<program>`. It reads from the sources or the results, then certifies and runs each register
    on a Π built fresh at positions 0 …, with the certificate cached per Π. It feeds `[last generated id, …final ids]`
    into the session cache and resumes.
  - The Mealy certify-and-run was moved out of `numbers()` into `mealyCall()` unchanged; both paths use it.
  - New events: `call` and `final`.
  - A response with no call returns today's trace shape: the plain reply, or the rule-style note.
  - `feed` now frees its intermediate cache when a forward throws (found by the stop-mid-transcript test).
- `trace.ts`: `LlmTrace.reason` holds the segments (text, call, …, text), the calls and the response ids. Each
  `ReasonCall.run` is a per-call `LlmTrace` that the panels read unchanged. `ArithRecord` gains `op` and `from`.
- `live-view.ts` rebuilds a multi-call run from the events (`LiveRun.reason`). While the clock has a call, the
  run's own fields are that call's, so the right-hand panels follow it.
- `stub.ts` plays a recorded multi-call trace back as events and records each question's `multiCall` option.
- `config.ts`: `MULTI_CALL: boolean = false` next to `ARITHMETIC`. The page sends `multiCall: true` only when it is
  on. With it off the ask options, engine path and traces are today's.

**UI** (`src/lib/interpreter/`)

- `ReasonReply.svelte` (new): a header line (e.g. "3 calls · all certified", or "3 calls · 2 ran, both certified ·
  call 2 got an error line"), the words through `Reply.svelte`, and each call in place. While the run goes it also
  shows the call the clock has and the words being written. The chat's status line says "Call 3 · Certifying
  register · row 59 of 200".
- `CallLine.svelte` (new): `call k`, the program's `task:` line truncated, "certified · 200 rows · run exact" and
  `→ value`. An error call shows its line, followed by the retry.
  - Opened, a call shows where each input was read ("first 1320…203 from result 1"; "tape 40 events from the
    notes"), then today's `RunPanel` (MealyRun for Mealy) and `CertificatePanel` (MealyCertGrid). An error call
    shows its program and the reason instead.
  - "Show it in the panels" moves the right-hand side to that call.
- `Chat.svelte` and `routes/interpreter/+page.svelte`: the page's five panels show one call at a time, with a
  "call 1 2 3" picker in the bar like the register picker. They default to the last call that ran, and an error
  call shows `NoRunPanel`.
- The subtracter is named as one wherever the panels said "carry"/"sum": borrow and difference, a `−` between a
  pair's digits, and edge rules in the machine diagram. This uses `mealyWords`/`opOfRows`. The adder's wording is
  unchanged, and so are the single-call panels (all their e2e tests pass).

**Fixtures**

- `scripts/reason_fixtures.py` copies `reason_fixtures.json` to `webgpu/fixtures/reason.json`. It asserts that every
  prompt re-encodes to the fixture's ids, and adds:
  - token strings;
  - the encodings of the texts the clock writes;
  - ids with offsets for every question and every call's notes.

  The tests run with or without Qwen3's tokenizer.

- `e2e/fixtures/reason-runs.json` holds the engine's own runs of three transcripts. It is written by
  `engine-reason.spec.ts` with `WRITE_FIXTURES=1`, and that spec checks it otherwise.

## Tests

- `pnpm check`: 0 errors, 0 warnings.
- Unit tests (`vitest --project server`):
  - With the real tokenizer: 377 pass. That is the 336 that existed, unchanged, plus 41 new.
  - With `QWEN_TOKENIZER=none`: everything in `src/lib/interpreter` passes, with only tokenizer-gated tests skipped.
- `reason.spec.ts` covers:
  - the reference's six `locate` cases, plus `locate` against today's `findSpan` and the §12 whitespace rules;
  - for every fixture call: the notes, `lastCallStart`, the parse, `readCall`'s spans, `how` and errors, the final
    text, the value and the error line;
  - `result k` parsing, with today's parse unchanged;
  - the limits;
  - the subtracter against its own table run.
- `engine-reason.spec.ts` covers:
  - The four transcripts on a scripted model (`TranscriptLM`): the model writes the reference's words and calls, and
    the clock writes the finals. Every call's start and end, final ids and text, value, error, mode, spans and `how`
    equal the reference. The rebuilt response ids equal the fixture's.
  - Every tick ran right after its own Π at position |Π|, and each Π was certified once.
  - The events rebuild the run, and every cache is freed.
  - 8 calls run, the 9th to 11th get error lines, and the 12th ends the response.
  - Stopping mid-transcript frees everything.
  - One call at the start of a response gives today's final ids and words. No call gives today's trace.
  - The stand-in's playback rebuilds each recorded run.
- `mealy.spec.ts`: naming the subtracter, its four edge rules, and its pairs.
- E2E, 24 tests: `e2e/interpreter-reason.e2e.ts` (4 new: chain, error then retry, phone width, a tape from the
  notes) plus `interpreter-arith`, `interpreter-browser` and `interpreter`.
- `pnpm lint`: all the files touched here pass prettier and eslint. The repo's other failures were there before and
  were not touched: 602 unformatted files under research/ and elsewhere, and `scripts/serve-story.mjs` `no-empty`.

## Disagreements with the reference

- **None on the fixtures.** All six `locate` cases and all four transcripts reproduce exactly, on the fixtures'
  tokens and on Qwen3's tokenizer.
- **Older than this port (ARITH, not REASON).** The TS port of `parse_generated` rejects a Mealy register with no
  rows as "table is not total and single-valued". `arith_core` and `reason_core` say "a destination or the start is
  not a state" (TS adds `!r.rows.length`). It was left alone so the single-call path stays bit for bit, and calls
  inherit it.

## What the spec leaves open (and what the port does)

1. **"The budget" (§7) has no number.** The first segment gets 3,000 tokens (today's compile budget). Each later
   segment gets 3,000 plus the length of the previous result, so the words can copy it as ARITH §7 allows. All of
   this is capped by the 40,960-token context.
2. **An `<exec/>` with no `<program>` since the last final.** `last_call_start` scans the whole response, so the clock
   re-reads the previous call's program, together with its final line and the words after it. The port does the
   same. An error such as "no program" may be the intent.
3. **The 12th `<exec/>`** is recorded as call 12 with error `hard stop`, no final, and the response ends. §7's answer,
   "the text after the last final", then includes the 12th call's program text. The port follows that literally;
   the chat shows the call as "not run".
4. **Calls 9 to 11** are not parsed (the reference does not), so their mode is null.
5. **Anchors not found in the notes** still read "anchors not found in the prompt", the reference's message.
6. **`<check>`** (the old rule-style format) stops only the first segment, as today. Later segments ignore it.
7. **Pokes** are not offered on multi-call runs (`ctx` is null), and no session cache is kept after one. A poke would
   change a result that later calls and words read, and the spec says nothing about re-running the rest.
8. **"run exact"** in the status line means every step landed on its row's destination and output: the run is its
   table's run (Theorem P). Whether the table is right is a separate question. For a run the page recognises,
   `arith.check` holds the true sum or difference, and `arith.op` names the table.
9. **A tape read from the notes** has its `char_spans` indexed into the notes. No panel uses them today.
10. **A cited number has no span in its source.** Its `arith.spans` entry is [0, 0], and `arith.from` says
    `{ result: k }`.

## The adder check (the Mealy path)

The clock is table-agnostic. Parsing, reading, `certifiedMealy`, `mealyTick`, `mealyRun`, `finalIdsMealy` and
`sumOf` run whatever rows are certified. Adder semantics appeared only in labels and in the page's own checks:
`isAdder`, `exactSum` as `arith.check`, the certificate's `covers` text, "Adding", and carry/sum in the panels. For
calls these now follow the table, through `op`, `exactDifference`, the wording and `covers`. The single-call path
still calls any non-adder table "a table with an output".

## Visual check

Screenshots were taken with Playwright against `vite preview` (`REASON_SHOTS=<dir> npx playwright test
e2e/interpreter-reason.e2e.ts`). The stand-in needs an init script, so the Browser pane was not used. The shots are
in `briefs/shots/`:

- `multi-call-desktop.png`: 1440×900, finished, call 3 open;
- `multi-call-running.png`: call 3 certifying;
- `multi-call-error.png`: the error call open;
- `multi-call-phone.png`: 390 px.

Clutter fixed after looking at them:

- The live call repeated the status line below it.
- The opened call repeated the certificate's tick count, and its link had no space before it.
- The subtracter's certificate said "not whether the table is the adder", and its program note said "carry".

No sideways scroll at 390 px or at 1440 px, opened or not.

Environment note: the Playwright `webServer` (`npm run preview`) did not answer on 127.0.0.1:4173 here. Running
`npx vite preview --host 127.0.0.1 --port 4173` first, and letting Playwright reuse it, works.

## Turning it on

When the reasoning model is exported, set `MULTI_CALL = true` in `webgpu/config.ts`, together with
`SAVANT_REVISION`/`SAVANT_URL`. The worker passes `multiCall` to the engine, and the chat renders whatever comes
back.
