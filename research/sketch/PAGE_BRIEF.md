# Brief: the /sketchpad demo page (local only, never push)

## What it shows
A live, in-browser demo: **Qwen3.5-0.8B (a small vision-language model) does exact arithmetic on a canvas that is its
only working memory**, reading it through its own vision tower one 3-cell strip at a time. Every possible strip is
checked on the visitor's device before a run, so the answer is exact at any length. The same model still chats.
Thesis line for the page: *grown, not built* — the arithmetic was learned by a small adapter on a pretrained model,
not compiled by hand. Audience: ML researchers and investors; it must feel precise, calm and astonishing.

## Where
Worktree `/Users/neo/repos/polyformer-wt/sketchpad`, branch `sketchpad` (from origin/main). New route
`src/routes/sketchpad/+page.svelte` with components and logic under `src/lib/sketchpad/`. No nav link yet. Install with
`pnpm install`. Commit code locally on this branch; **never push** (pushing main publishes the site). Never commit
anything under `static/sketchpad/models/` (already in .git/info/exclude; 2.3 GB of hard links). Run dev/preview servers
in the background only; never block on a long-running command. Use the Svelte MCP tools / svelte skills for .svelte files.

## Working references (read these first; they work today, verified)
`/Users/neo/repos/polyformer/research/sketch/e3_browser/`:
- `index.html?fast` — the adder: load, 242-row certificate, live runs, click-to-edit. Tested: 242/242 on an M4 (min
  margin 1.40, 35 s), 1,000-digit sum exact at 163 ms/tick.
- `mul.html?model=qwen35-canvas-mul16&dec=fp16` — the multiplier: 1,553-row certificate (~140 s), live long
  multiplication; 4x4 and 6x6 products exact.
- `canvas_runtime.js` (+ `canvas_runtime.test.mjs`, 555/555 against the reference tables) — the multiplier runtime.
- `sprites.png`, `sprites.json` — the exact training glyph pixels.
The existing site demo `src/routes/interpreter` + `src/lib/interpreter/webgpu/` shows the house patterns (worker,
transformers.js 4.3.1 via npm, `env.remoteHost`).

## Invariants (break any of these and the certificate is void)
1. Load with `Qwen3_5ForConditionalGeneration` (transformers.js), device webgpu, models served from
   `/sketchpad/models/<id>/` via `env.allowLocalModels=false; env.allowRemoteModels=true; env.remoteHost=<origin>/sketchpad/models/;
   env.remotePathTemplate='{model}/'` (allowLocalModels fails on the tokenizer). dtype: adder `qwen35-canvas-fast` =
   {embed_tokens:'q4', vision_encoder:'fp16', decoder_model_merged:'q4'}; multiplier `qwen35-canvas-mul16` = same but
   decoder 'fp16'. Keep the provided `preprocessor_config.json` (it adds `do_normalize` etc.; without it transformers.js
   silently skips normalisation and certificates fail) and `shortest_edge: 1024` (a 3-cell strip = 3 vision tokens).
   Check transformers.js 4.3.1 still matches 4.2.0 behaviour; if anything differs, pin 4.2.0 for this page.
2. Every image the model reads is assembled from `sprites.png`: cell 32x32 px, glyphs " 0123456789", the sheet's row k
   (0, 1, 2) is the glyph as drawn at strip position k. A strip is 32x96, cells stacked top to bottom. Never render
   model-read pixels with browser fonts. The display canvas may be drawn from the same sprites, scaled with
   `image-rendering: pixelated`.
3. Adder (fast format): prompt `ADD<|vision_start|><|image_pad|><|vision_end|>=` (raw, no chat template), one forward,
   argmax of the last position; output token `0`–`9` = sum digit, no carry; `a`–`j` = digit 0–9 with carry; `H` = halt.
   Strip = (carry ∈ {blank,'1'}, top digit or blank, bottom digit or blank). Table = 2 × 11 × 11 = 242 rows.
4. Multiplier: prompt `<OP><|vision_start|><|image_pad|><|vision_end|>=`, OP ∈ MUL ADD ADZ FLS NXT; greedy 3 tokens:
   glyph1 (`_` = blank), glyph2 (`-` = unused), next-op letter (M A Z F N H). Runtime and views exactly as
   canvas_runtime.js (port to TS, keep `reference()` and the test). Table = 1,553 rows (enumeration in mul.html).
   **Certificate scoring appends one token id per answer character** (tokenising "_-N" jointly merges pieces).
5. A certificate row passes when every answer token is the argmax with positive margin (true logit minus best other).
   Show the device's minimum margin as the headline number. A run is labelled "certified" only if every row passed on
   this device in this session (or a cached result for the same model files, sprites and config hashes).

## The page (design rules from Neo; follow them strictly)
- Site look: dark monochrome instrument UI (#080808 background, grey tones, grotesk UI type at 13–14 px, titles 28 px),
  no boxes, borders, pill badges or chips; use spacing and tone. A text column with a margin column. One graceful
  ease-in-out (~850 ms) for focus changes; hover responses ~250 ms. Nothing cluttered or "tacky".
- The canvas is a white sheet with black glyphs: it is literally the model's memory and looks like paper. Row labels
  sit in the margin, not on the sheet. The fovea (the 3 cells being read) is outlined and glides between positions; the
  newly written glyph appears with a short fade. The sheet pans to follow the eye on long runs.
- A small magnified inset: "what the model sees" (the 3-cell strip, enlarged, pixelated) and "what it writes" (the
  output token(s) and the next step), updating each tick.
- Certificate: a compact grid of tiny cells (one per table row), filled as checked, with the pass count, minimum margin
  and seconds; a failing row is shown as a hollow cell and listed. Tone, not colour (ask before adding any accent).
- Controls: problem input (two numbers), operation (add / multiply), Run, and presets: 40-digit sum, 1,000-digit sum,
  4x4, 6x6, 10x10 product. Live stats: tick, ms per tick, digits done. Click a digit the model has not reached yet to
  change it (adder: any unread top/bottom digit; multiplier: a multiplier digit of a later pass); show that the answer
  follows the edit.
- Chat: a small box under the sheet, "Ask it anything". Same loaded model, chat template with enable_thinking=false,
  max ~120 new tokens, streamed. It shows the model is still a normal language model.
- Copy (short, honest, owning voice): what the visitor sees, why it is exact (every possible view checked on this
  device; the canvas is the only state, so checked views imply any length), and the stated boundary (the problem is
  typed; photo reading is future work; the runtime only stamps glyphs and moves the window where the model says).
- Loading: show download progress (the models are ~0.9 GB and ~1.4 GB; load only the one the chosen operation needs).

## Done means
Both operations certify on the M4 in the page (report pass counts, min margins, seconds), a 1,000-digit sum and a 6x6
product run exact live, an edit is followed, chat answers a normal question, `pnpm check` passes for the new files, and
screenshots at 1440x900 and 390x844 are saved under `research/sketch/page_shots/` in the main repo
(`/Users/neo/repos/polyformer/research/sketch/page_shots/`). Report: what you built, the numbers, the screenshot paths,
anything that does not meet the design rules, and the commit hash on branch `sketchpad`.
