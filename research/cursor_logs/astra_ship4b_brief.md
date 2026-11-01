# Astra brief: finish, test and ship the Sketchpad 4B model (1 Nov 2026)

You take over from a Claude session that has run out of budget. Neo's words: "get the new model tested (whatever we
did before), and if it is all good, put it on huggingface and allow the users to choose which one they want to use in
the app ... Make sure the paper is fixed up as well."

Work alone to the end. Send no interim messages. Write one final report (≤ 60 lines) as your last message: what passed,
what failed, every number with its file, the commits, and the dollars spent.

## Where things are

- Research worktree: `/Users/neo/repos/polyformer-wt/chat` (branch `chat`). Log: `research/sketch/chat/CHAT3.md`.
  Read these sections first: "4B result (1 Nov 2026)", "Option 2: GRPO without GSM8K, chosen on validation", and
  "E8 shipped". Read `research/sketch/chat/TAKEOVER_4B.md` (the handover note; it may appear a few minutes after you
  start, so wait for it before Step 1). Launcher: `research/sketch/chat/launch.py`; call ids: `calls.json`. Modal
  app and volume: `polyformer-chat`. Call Modal through `uvx --with modal python ...`.
- **Running now. Do not relaunch it:** `train_p9b_4b`, call `fc-01M6B4S4ZKGH23FV76WP408GRS`. It was at step 100 of 200
  at 09:30 UTC, about 22 s/step. Poll it no more often than every 10 minutes (sleep in the shell).
- App and paper repo: `/Users/neo/repos/sketchpad` (branch `main`; pushing main is approved). Model config:
  `src/lib/sketchpad/models.ts` (`PUBLISHED`). Paper: `paper/paper.md`, style rules `paper/review/STYLE.md`, every
  number's source in `paper/numbers.md`, arXiv package `paper/arxiv/` (`SUBMIT.md`, `check_pdflatex.py`), cover
  letter `paper/journal/COVER_LETTER.md`.
- Hugging Face: the 0.8B model is `mohsenvand/sketchpad-0.8b-preview` (folders `base/`, `arithmetic/`, `chat/`). The
  token lives in `~/.cache/huggingface/token`. Template: `research/sketch/chat/hf_publish_e8.py`.

## Steps

1. **Choose a checkpoint by the registered rule, unchanged.** It is in CHAT3.md, Option 2, "Choosing". Run validation
   on the rerun's four checkpoints (stock, the P6 stage and the current final already have validation numbers). Then
   score the chosen checkpoint **once** on test, with the full T4 evaluation (held-out set, IFEval, GSM8K 1,319,
   MMLU 1,500, IFBench, table rows). Append the result to CHAT3.md against the registered predictions. If no rerun
   checkpoint qualifies, the rule picks the P6-stage 4B. That checkpoint already has its test numbers, so do not
   score it again.
2. **Passing.** The model passes when every T4 bar in CHAT3.md holds for it: recall, word, equations and prose,
   IFEval ≥ −2, GSM8K ≥ −2 and MMLU ≥ −2 against stock 4B, all 2,446 table rows, and 0 block loops. If any bar fails,
   stop after Step 1. Upload nothing, change neither the app nor the paper, and report.
3. **Browser build.** Do it as E8 was done (`build_e8.sh`, `build_e8_ids.sh`, `patch_onnx_ids.py`), on Modal, not on
   this Mac.
   - **Register before spending:** write your predictions in CHAT3.md first.
   - **Size.** A 4B fp16 decoder is about 8 GB, too large to download. Measure a quantised decoder: q4 MatMulNBits on
     the base weights, with the adapter kept fp16, then int8 if q4 loses rows.
   - **Embedding.** Check whether 4B ties its embeddings (0.8B does). A q4 embedding broke word problems at 0.8B; E8
     uses a 16-bit embedding gathered inside the graph.
   - **WebGPU limits.** Check the size of the largest single tensor against WebGPU's limits on an Apple M4
     (`maxStorageBufferBindingSize`, `maxBufferSize`).
   - **Then run on Modal CPU (ORT):**
     - identity: gate 0 = stock 4B and gate 1 = ungated, as `e8ids_identity.py`;
     - all 2,446 rows with their margins;
     - the page-path evaluation, as `page_eval.py`, with the same bars.
   - **Stop and report** with the options and their sizes if no build keeps 2,446/2,446 rows and the page-path bars
     at a total download of about 3.5 GB or less. Do not ship a weaker build.
4. **Device certificate (Apple M4, in the browser).** E8's is `chat/certificate.json`; find how the app produced it
   (`pad.svelte.ts`, `worker.ts`).
   - Try Playwright Chromium (or Chrome) with WebGPU on this Mac against `pnpm dev`.
   - Run servers in the background only. Never block on a long-running command.
   - Run one tab only and close it when done. The Mac has 32 GB; page GPU memory once reached 37 GB, so watch it.
   - If headless WebGPU cannot run, write `research/sketch/chat/NEEDS_DEVICE_4B.md` (exact page, steps and the
     expected output file) and go on. The orchestrator will run that step in its own browser.
5. **Hugging Face (approved by Neo if Steps 1–3 pass).**
   - Publish to a new repo, `mohsenvand/sketchpad-4b-preview`, with the 0.8B repo's layout and revision pinning.
   - The model card states the bars, both base models' numbers and the limitations, plainly. Licence: Apache 2.0.
   - Check `list_repo_refs` before choosing a parent commit.
   - Never print, log or commit the token.
6. **App: let the user choose the model.**
   - `PUBLISHED` becomes a list of two programs: 0.8B (the default) and 4B.
   - The page offers a quiet selector that shows each model's download size and states plainly that 4B needs a
     desktop GPU. Keep it in the existing design: no boxes or chips, Cobalt and Rose, light theme.
   - Remember the choice in `localStorage`, wrapped in try/catch. Switching terminates the worker and loads the other
     model.
   - Svelte 5 runes. Run `pnpm check`, `pnpm lint` and the tests under `nice -n 19` with `--maxWorkers=2`, then
     `pnpm build`.
   - The 4B entry stays hidden until its device certificate exists.
   - Commit and push `main`.
7. **Paper.** Add the 4B result where the dialogue adapter's retention is reported.
   - Today the paper reports the 0.8B's fresh-item GSM8K loss (−5.8) as a limitation. Say what changes at 4B, with
     test numbers from the chosen checkpoint only, and the 4B device certificate.
   - Follow `paper/review/STYLE.md`: academic register; no internal run names (no P6, P9, E8, train_*); no slogans.
   - Add every new number to `paper/numbers.md` with its source file. Update the abstract and the cover letter only
     if a headline number changes.
   - Rebuild the arXiv package. `check_pdflatex.py` must give 0 errors and 0 undefined references.
   - Commit and push `main`.

## Rules

- Modal: the 4B phase has a $100 cap and about $40–50 is spent, so read the ledger and the billing. Stop and report
  before any step that would cross the cap.
- Deploy and spawn in separate commands; a spawn sent together with a deploy hits the old deployment.
- Never relaunch a job that is already running. Commit on `chat` in the polyformer worktree, and do not push
  polyformer.
- Use `/bin/rm` and `/bin/cp -f` (the zsh aliases are interactive). Make no new downloads to this Mac beyond the model
  files the app or tests need.
- Never print, log or commit keys (`~/.polyformer_keys`) or the HF token.
- Report honestly. A failed bar is a result, not something to tune away on the test set.
