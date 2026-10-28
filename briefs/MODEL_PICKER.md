# Model picker

Branch `site-reason`, 28 Oct. Spec: `briefs/MODEL_PICKER_BRIEF.md`. `origin/main` (Savant-4B preview r3, revision
`e2a8de05`, addition on) is merged in `3807c019`. Nothing pushed.

## What changed

The interpreter page offers two models from one list in `src/lib/interpreter/webgpu/config.ts`.

- **Savant-4B preview r3** is the default and the only model on the published page. `multiCall` is off and
  `arithmetic` is on, so the six families and Addition, and the scope hint, stay as they are on r3. Repo
  `mohsenvand/savant-4b-preview`, revision `e2a8de056586e6095b5be74c23f16d5750950776`, adapter
  `arith-s1r2/adapter_step500`, 3.33 GB.
- **Savant-4B Reason (preview)** is the other choice. The display name is the one constant `REASON_MODEL_NAME`.
  Its repo, revision and adapter are `FILL_AFTER_UPLOAD`, so the picker hides it until those are filled. The page's
  test stand-in offers it after mount, which keeps the server HTML and the first client render the same. `multiCall`
  is on. The download size is a placeholder of the same 3.33 GB until the upload records one.

The picker is in the model panel, before download: each choice is the name, `~3.3 GB`, and one line on what the
model does. The selected name is underlined. There are no boxes and no badges. After the first turn the same choices
stay, without the descriptions. The choice is stored at `polyformer.interpreter.model`; every read and write is in
try/catch, and a stored id that is not offered falls back to r3. Switching stops the loaded model. "Forget the
download" deletes only that model's cache keys. URLs include the revision, and `VITE_SAVANT_URL` overrides r3 only,
so the two prefixes do not overlap.

A question goes out with `multiCall: true` only when the chosen model has that flag. The reasoning model suggests
four composites, phrasing 0 of REASON's training templates: `sales_compare` ("Two stores"), `deposit_chain`
("A deposit"), `parity_pick_sum` ("Parity, then a sum"), `shelf_bill` ("A shelf bill"). Phrasings 4 and 5, and the
held-out templates, are not used. Addition stays beside them, because that model keeps arithmetic. The page says
these are composites from the training templates and does not score them.

## Tests

- `pnpm check`: 0 errors, 0 warnings.
- `pnpm exec vitest --project server --run`: 22 files, 393 tests, including `config.spec.ts` (the r3 pin, the
  unpublished reasoning model, the offer list, cache prefixes, the stored choice, and the four training templates).
- Playwright, 29 passed: `e2e/interpreter.e2e.ts`, `e2e/interpreter-browser.e2e.ts`, `e2e/interpreter-arith.e2e.ts`,
  `e2e/interpreter-reason.e2e.ts`, and `e2e/interpreter-models.e2e.ts`. The new file checks that the published page
  hides the reasoning model, that each choice has its own questions and is remembered, that each model sends its own
  `multiCall` flag, that forgetting one download leaves the other model's files, and that the picker fits 390 px.

Prettier and eslint were run on the files this change touches.

`vite preview` listens on 127.0.0.1 when started with `--host 127.0.0.1 --port 4173`. Playwright then reuses that
server (`reuseExistingServer` outside CI).

## Screenshots

Taken with `MODEL_SHOTS=briefs/shots` against the stub engine.

- `briefs/shots/model-picker-desktop.png` — both choices, r3 selected, the six families and Addition.
- `briefs/shots/model-picker-phone.png` — the same picker at 390 px.
- `briefs/shots/model-picker-reason.png` — a reasoning reply (three certified calls) with the reasoning model
  selected. The footer says the adapter is not uploaded yet, because the placeholder is still `FILL_AFTER_UPLOAD`.
