# PORT: the demo into NeoVand/sketchpad, one light design

Neo, 30 Oct 2026: the new public repo `NeoVand/sketchpad` (local `/Users/neo/repos/sketchpad`, live at
https://neovand.github.io/sketchpad/) holds the sketchpad paper and its demo. On design: "go light, make everything look
beautiful together". Pushing that repo's `main` is approved ("4-ok"). A push publishes the site through GitHub Actions.
Polyformer is the source only: never edit, commit to or push polyformer here.

## What to port

The source is polyformer `main` at `d5eb4d79`, the merge of the calculator, algebra and gate streams. Bring over:

- `src/lib/sketchpad/**`: the sheet runtime, worker, the `lora_gate` wiring, Calculate mode, the inside views, and the
  certificate check.
- `src/lib/sketchpad/program/**`: the work-order runtime (algebra by evaluation) with its tests, wired into the demo as
  a mode beside Calculate. Default check: light.
- `src/routes/sketchpad/+page.svelte`, which becomes `src/routes/demo/+page.svelte`.
- `static/sketchpad/` without `models/`.
- The pinned transformers.js alias from polyformer's `package.json`.

Rules:

- Models load from Hugging Face `mohsenvand/sketchpad-0.8b-preview` at the pinned revision in `models.ts`. Never
  commit a model file. `.gitignore` already excludes them.
- The numbers do not change. Prompts, rendering of the sheet, tokenisation, graph inputs and certificate logic port as
  they are. Only styling, layout and imports may change.
- Every ported file gets a row in `PORTED.md`: here, there, commit `d5eb4d79`, notes. Port only what the demo or paper
  uses. Leave polyformer's exploration pages behind.
- All ported tests pass here (polyformer: 133 passing under `vitest run src/lib/sketchpad`), along with lint,
  svelte-check and the build.
- `HAS_CALC` currently limits Calculate to the dev page. Turn it on in the new demo.

## Design: light, one system for paper, demo and figures

Replace the dark tokens in `src/routes/layout.css` with one light set built on the paper palette, Cobalt and Rose
(polyformer `research/figstyle/palette.json` at `3185c95b`):

| role | colour |
|---|---|
| paper, the page background | `#FFFFFF` |
| tint, quiet fills | `#F2F5FB` |
| ink, text and axes | `#1F2A44` |
| ink_soft, secondary text | `#4C5B78` |
| blue_grey | `#7D8BA8` |
| blue_mist, hairlines | `#BAC5D9` |
| rose, ours: the model's writing on the sheet, certified | `#D6336C` |
| rose_light | `#F1A3BC` |
| cobalt, the alternative or stock | `#2557A7` |
| cobalt_light | `#9DB8E0` |
| violet, references and theory only | `#7A5BA8` |

Neo's standing rules:

- compact scale: 13–14 px UI, 28 px sans and 32–38 px serif titles;
- no boxes, borders around borders, pills or boxed chips: use spacing and tone;
- few separators;
- quiet focus;
- one eased motion of about 850 ms between states, and about 250 ms for hover;
- a text column with a margin column;
- booktabs tables;
- no label on a line;
- captions below figures;
- panels aligned on shared rows and gutters;
- nothing that looks templated.

Keep the Geist fonts; KaTeX is available for maths.

The sheet itself (the image the model reads) must not change. The model's input pixels are part of the certificate.
Restyle only the chrome around it, and its on-page display if that is drawn separately from the model's input. Check
in the code which is which before touching anything. The light theme is the only theme: drop dark mode.

Pages:

- **Paper** at `/`: the skeleton from `src/lib/paper/outline.ts`, restyled. The writing comes later.
- **Demo** at `/demo`, in four parts:
  - the sheet machine;
  - Calculate (+ − × ÷ √ gcd, signed numbers);
  - Algebra (work orders): the featured examples are the beats under about 12 s in `program/NOTES.md`; slower ones
    stay available with their time shown honestly;
  - chat at gate 0 with today's honest sentence, plus the inside views (logit lens, the push at layer 20) and the
    certificate.

Both pages work at 1440×900 and at 375 px, with no horizontal scroll.

Add WebGPU device-loss recovery here, not in polyformer. On `device.lost`, rebuild the ONNX Runtime session and redo
the step in flight; make it visible as one quiet line. Test it by forcing a loss.

## Verify

1. Run `pnpm dev` through the `sketchpad-dev` launch entry (port 5190) in the built-in browser.
2. Take screenshots at 1440×900 and 375 wide of the paper and of each demo part.
3. On the M4, with the pane visible, run the certificate to completion. It must report 1,795 of 1,795 rows on today's
   E6 revision. Run one problem in each Calculate operation and one algebra beat.
4. Then push `main` and check the live site once the deploy finishes.

A later swap to E7 is expected: the CALC stream is building a gated E7 and will pin a new Hugging Face revision. Keep
the model folder and revision in one place so that swap is one line.

## Report

Send:

- the commits and pushed SHA;
- the `PORTED.md` row count;
- the screenshot paths;
- the certificate result and timings;
- what did not port and why;
- any place where the light design needed a judgment call.

Spend $0, never print any token, and ask before any download.
