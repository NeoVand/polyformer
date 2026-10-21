# One paper: overhaul brief (20 October 2026)

Neo's request, verbatim: "do a full overhaul of the paper. Make it very understandable. Include all the results. Use
all the visuals and interactivity. Just make it awesome. Create a really good narrative arc where everything nicely
fits together. Make sure the prose doesn't feel too AI-generated or hyper-intellectual and technical. It should just
be clear what we are doing and why we are doing it. Mathematical ideas should be explained. ... the Learn and Report
parts should be combined into just one writing, where everything is nicely introduced and discussed. Also, it should
properly render on mobile. At the moment, Learn renders horribly, where half of the page is gone, and the diagrams and
text flow under those diagrams in a panel. ... We don't need to put stuff on the margins. Just a gorgeous,
interactive paper, distill.pub style, with all the details, and let's just make sure it is fully understandable and
fleshed out."

Worktree `/Users/neo/repos/polyformer/.claude/worktrees/paper`, branch `claude/paper-overhaul` (main plus the
`claude/beyond` and `claude/arc-dilution` results). Status and log at the bottom of this file.

## What to build

**One article** at `/paper` that replaces both Learn (`src/routes/learn`) and Report (`src/routes/report`). Redirect
`/learn` and `/report` to it (keep old anchors working where cheap: map them to the new section ids). Update the top
nav (Paper, Explore, Compare), the landing page's buttons and copy, and any internal links. Explore and Compare stay.

**Layout: distill.pub.** One centred text column (about 680-720px), figures that can break wider than the text (up
to ~1000px on desktop) and go full-bleed on phones. No margin column, no side notes, no sticky side panels, no
section rail that eats width on mobile (a small table of contents at the top, and optionally a slim progress
indicator, is enough). Footnotes, if any, go inline as expandable notes or at the end. Mobile first: every figure
and table must fit 390px wide without horizontal page scroll (tables may scroll inside themselves); interactive
figures must be usable by touch. The current Learn page breaks on phones (half the page missing, text flowing under
diagram panels); the new page must not.

**Reuse every visual and interactive piece that serves the story**: `src/lib/learn/*`, `src/lib/report/*`,
`src/lib/explore/*`, `src/lib/viz/*` (SET deal and hypergraph, the tensor, Feynman/DS-PA diagrams, Newton demo,
characters figure, arity figures, curves, replication tables, the composition figures, the A5 icosahedron with
Ideal/Recorded, the order-matters demo, accuracy ladders). Embed them inline, resized for a single column. Remove
what does not serve the arc. Add a few new figures where the arc needs one (for example: a tiny figure for "a pair
looks random but the triple doesn't"; a simple bar chart for the language results; a figure for the dilution and ARC
results). Keep the strict monochrome aesthetic.

## The narrative arc (adjust the wording, keep the logic)

1. **The question.** Attention compares tokens two at a time. Can a layer that looks at groups of tokens do more,
   and does that matter? Start with the SET puzzle: a reader can play a deal.
2. **Why pairs are blind.** Some relations leave no trace in any pair (SET, Match-k): show it concretely, then the
   theorem in plain words.
3. **Giving attention more arms.** Cubic attention, Feynman/DS-PA diagrams, Newton attention (every group size at
   once). The results on SET and Match-k; the characters law (explain characters as clock hands first).
4. **The language test.** We tried it where it matters. Nothing higher-order beat softmax at our scale: S0-S2,
   local-linear attention (0.4%) and Parallax (0.75%) in S6. Explain what a "1% at equal compute" bar means and why
   we held ourselves to it.
5. **The turn: composition, not coordinates.** Softmax handed every character still cannot learn Match-4. What
   matters is the operation a layer can perform on its features: softmax averages, Newton multiplies clock hands
   (commuting), and holonomy attention multiplies rotations (not commuting).
6. **Groups, explained.** Clock arithmetic, card sums, rotations of a triangle and an icosahedron; why order matters
   ("turn then flip" is not "flip then turn"); characters and representations as concrete pictures. Interactive.
7. **What each kind of layer can learn.** The order-blind ceiling (exact numbers from THEORY.md), the learned
   irreducible representations of A4 and A5 (the icosahedron lab inline), word problems over A5 and S5, swap
   programs. Honest comparison with matrix-state RNNs.
8. **Where composition does not pay.** The combined candidates (research/BEYOND.md, BEYOND_REPORT.md: A and C failed
   to learn S5 on fresh seeds, B lost to softmax with a short convolution, removing its composition changed loss by
   0.04); loss dilution (research/NEXT.md: decisions are 0.5-1.7% of tokens; weighting helped both models, softmax
   more, composition branch -0.13 points); algebraic ARC (both models solve exactly the tasks whose spatial operator
   is the identity, the closed-form operator solver solves all). Present these as findings, not apologies.
9. **What we learned.** The bottleneck is finding structure, not representing it: the characters law, the
   order-blind ceilings, fresh-seed failures, dilution and the closed-form ARC solver all say the same thing. What we
   would try next (inferring operators from examples).
10. **Methods and details** (end matter, still readable): theorems with proofs sketched and links to THEORY.md, every
   experiment's setup, prior art (PRIOR_ART.md, with what is and is not new), reproducibility and provenance, cost.

Every number must come from the research files (GROUPS.md, THEORY.md, PRIOR_ART.md, LOCAL.md, SEARCH.md,
FORMALISM.md, BEYOND.md / BEYOND_REPORT.md, NEXT.md, and `src/lib/report/results`). Do not invent or round
differently from the sources. Mark what is prior work, what is new here, and what was measured.

## How the prose should read

- Write like a careful researcher explaining the work to a smart colleague who knows what a neural network is and
  little else. First person plural ("we tried", "we expected"). Say what we did, why, and what happened.
- Concrete before abstract: an example or a picture first, then the general idea, then (if needed) the equation,
  and every equation is followed by a sentence that says what it means.
- Short paragraphs, plain words, varied sentence length. Define every term the first time it appears.
- Avoid the tells of generated text: no "Crucially", "delve", "In this section we will", "It's worth noting",
  "a testament to", stacked hedges, rhetorical triplets, em-dash chains, or bold on every other phrase. No hype.
  State failures plainly. Numbers always with their context ("0.4% lower loss than softmax at equal compute").
- Equations with KaTeX as the app already does; keep them few and explained.

## Design rules (binding)

Read `/Users/neo/.claude/projects/-Users-neo-repos-polyformer/memory/polyformer-aesthetic.md`,
`polyformer-design-feedback.md` and `polyformer-v2-ui.md`: strict monochrome, no boxes or double strokes, no pill
chips, compact type scale, booktabs tables, captions below figures, no label sitting on a line, eased motion, chapter
numbers via a numbering helper, never hard-coded. Svelte 5 per `AGENTS.md`; run
`npx @sveltejs/mcp svelte-autofixer <file>` on every edited .svelte file until clean.

## Checks before you finish

- `pnpm install`, then `pnpm check`, `pnpm test:unit -- --run`, `pnpm build` (and `BASE_PATH=/polyformer pnpm build`),
  and the Playwright e2e tests (update them for the new route) all pass.
- Screenshots of the whole paper, section by section, at 390x844 and 1440x900 (production build served statically),
  saved in `briefs/paper-shots/` with a README. Open them and look: no clipped or missing content on mobile, no
  horizontal scroll, no overlaps, figures readable, interactive figures working by touch. Fix and re-shoot until
  clean. Check the landing page and nav too.
- Commit in logical steps with messages ending `Co-Authored-By: Argon (Gemini)`. Never push, never merge into main.
- Append to the Log below at each milestone. Final message: section list, what was reused or new, anything you
  could not finish.

## Log

- Brief written by Claude; worktree has main + claude/beyond + claude/arc-dilution merged. Argon launched.
