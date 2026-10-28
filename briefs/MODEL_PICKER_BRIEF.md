# Brief: let visitors pick which Savant to download (and turn on multi-call for the reasoning model)

Neo wants the interpreter page to offer two models. The visitor picks one before downloading it.
- **Savant-4B preview r3:** live today. Certified addition, the six task families, one program per question.
- **The reasoning model:** working name "Savant-4B Reason (preview)"; the final name is pending, so keep it in one
  constant. It reasons in words and calls programs mid-thought. The multi-call runtime is already built on this
  branch, behind `MULTI_CALL`.

## Where
- **Worktree:** `/Users/neo/repos/polyformer-wt/site-reason` (branch `site-reason`). The SvelteKit app is the repo
  root.
- **Merge `origin/main` first.** It has the r3 config (commit c7cadb27: `SAVANT_REVISION e2a8de05`,
  `ARITHMETIC = true`). Resolve conflicts carefully and keep both the multi-call port and the r3 config.
- **Read:**
  - `briefs/MULTI_CALL_PORT.md`;
  - `src/lib/interpreter/webgpu/config.ts`;
  - the Savant load flow: `savant.svelte.ts`, the model panel, `Chat.svelte`;
  - `AGENTS.md` (Svelte 5 runes).

## Build
1. **Config, one entry per model:**
   - id, display name, short description (one line on what it is good at), HF repo and pinned revision, dev URL,
     bytes, adapter;
   - feature flags: `multiCall` (false for r3, true for the reasoning model), `arithmetic`.

   Leave the reasoning model's HF repo and revision as clearly marked placeholders: the orchestrator fills them after
   upload. Until they are filled, the picker must hide or disable that option.
2. **The picker,** in the model panel before download:
   - two choices, each with a one-line description and the download size;
   - the choice is remembered in localStorage, wrapped in try/catch;
   - "Forget the download" works per model;
   - the browser cache keeps both models by revision, so switching never mixes files.

   Match the page's quiet visual language: compact type, no boxes around boxes, no pill badges. It must work at
   phone width.
3. **Per-model behaviour:**
   - with the reasoning model, multi-call transcripts render (already built);
   - with r3, behaviour is exactly as today;
   - suggested questions may differ per model: give the reasoning model 3–4 composite examples from REASON's
     training templates, not held-out ones.
4. **Tests:** unit tests for the config and picker logic, and a Playwright e2e on the stub engine for selecting each
   model. Run `pnpm check`, the unit tests and the interpreter e2e. Lint only the files you touch.

## Rules
- Commit on `site-reason`. Never push.
- Use `/bin/rm`. Run heavy commands under `nice -n 19`.

Finish with a short report in `briefs/MODEL_PICKER.md`: what changed, which tests pass, and screenshots if you can
take them.
