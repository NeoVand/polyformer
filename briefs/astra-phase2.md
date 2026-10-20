# Astra, phase 2: tell the new story in the app, beautifully and plainly

Phase 1 made the result rigorous. Now Neo needs to **present** it, and the app is the presentation: a SvelteKit site
(GitHub Pages) with Learn (a course), Explore (labs), Compare (browser training), the Report (the paper) and a
landing page. It currently tells the older story ("higher-order attention, arity chosen by the data"). Rewrite it so
the arc ends where the research ended, and so a reader who knows neural networks but no group theory follows every
step. This is what Neo will show in interviews; polish matters as much as content.

## Neo's latest instructions (verbatim intent, binding)

Neo wants the result **live** in the morning and said: "ask astra to visually check things, we might even need to
change the title and landing page and the narrative slightly." So:

- You have licence to change the site title, the report title, the landing page and the narrative so they fit the
  new story (composition and group representations, with higher order as the road that led there). Propose the
  title in your final message with one alternative.
- **Check everything visually, yourself, repeatedly**: after each page you change, build, serve the production build,
  take Playwright screenshots (1440x900 and 390x844, light and dark), open the images and look at them critically
  against the design rules: overlaps, clipped labels, labels on lines, boxes or double strokes, uneven spacing,
  empty quadrants, unreadable contrast, animation glitches (capture two frames ~1 s apart for animated views). Fix
  and re-shoot until clean. Keep the final shots in `briefs/shots/` with a short `briefs/shots/README.md` saying what
  each shows.
- Claude will publish (push to main) after its own review; you still never push.

## Read first

- `OVERNIGHT.md`, `research/GROUPS.md`, `research/THEORY.md`, `research/PRIOR_ART.md` (and the word-problem section
  of GROUPS.md if phase 0 merged it), `research/LOCAL.md` section 0, `research/SEARCH.md` section 8
- Design rules, all binding: `/Users/neo/.claude/projects/-Users-neo-repos-polyformer/memory/polyformer-aesthetic.md`,
  `polyformer-design-feedback.md`, `polyformer-v2-ui.md`, `polyformer-v1-app.md` (strict monochrome instrument UI,
  no boxes or double strokes, compact type scale, booktabs tables, captions below figures, no label on a line, eased
  ~850 ms motion, Learn defines every term before use and marks provenance, chapter numbers via `number('id')`)
- `AGENTS.md` (Svelte 5; validate every edited .svelte file with `npx @sveltejs/mcp svelte-autofixer <file>` until clean)
- the routes `src/routes/{+page,learn/+page,report/+page,explore/...,compare/+page}.svelte` and `src/lib/{learn,report,explore,viz}`

## The story to tell (in this order)

1. Attention compares tokens in pairs; some relations are invisible to pairs (SET, Match-k). Native higher-order
   terms see them (cubic, Newton attention) and win decisively on such tasks.
2. On language, nothing higher-order beat softmax at our scale (S0-S2; S6: local-linear attention 0.4%, Parallax
   0.75%, short of 1%). Say this honestly; it is part of the credibility.
3. The turn: order is not the point, **composition** is. Softmax given every character still cannot learn Match-4.
   What a layer can relate is set by the algebra its features compose in: softmax composes nothing, Newton attention
   composes in an abelian group (clock hands that add) and stops at the order-blind ceiling, holonomy attention
   composes rotations and learns the group's irreducible representations (the icosahedral rotations of A5) from labels.
4. The theorems (plain versions first), the benchmark results, and the honest positioning against prior art.
5. What it means and what is next.

## Work items

1. **Report (paper)**: restructure around the story above; new sections for composition, groups, theorems, word
   problems and the second benchmark; keep existing material that still fits (shortened), drop what the new story
   supersedes; update the abstract, title if warranted (suggest one), figures and bibliography (`src/lib/report/bib.ts`).
   Tables from the research files exactly, no rounding drift.
2. **Learn**: add a new Part after the existing ones (or restructure if better): what a group is, with pictures
   (clock arithmetic, card sums, rotations of a triangle and an icosahedron); commutative vs not ("turn then flip"
   differs from "flip then turn"); characters as clock hands and why phases add; representations as rotations;
   holonomy attention as multiplying rotations along the sequence; the experiments; what it shows. Every term defined
   before use, every chapter marked prior work / new / measured.
3. **Figures and an Explore lab**:
   - the accuracy ladder (d = 2, 3, 4, 5, 8 and Newton, softmax) with the order-blind ceilings drawn as lines;
   - the experiment 1 result (softmax with characters at chance vs Newton);
   - a **3D view of the learned A5 representation**: export, from a trained holonomy model (A5, d = 3, seed 0), the
     3x3 rotation every group element gets (write a small script that trains on Modal or locally and dumps
     `static/recorded/a5-irrep.json`; include the homomorphism error), and show the 60 rotations acting on an
     icosahedron, next to the ideal irrep (computed, not hand-typed). Follow the Explore lab convention: open on
     something visible, one "Model" switch (Ideal / Recorded).
   - an order matters demo: a short sequence of rotations applied in two orders, ending in different places.
4. **Landing**: update the copy and one tile to the new idea (relations as composition; layers that learn
   symmetry), keeping the one-screen layout and the rules in the design memory.
5. **Compare**: add the group results as a recorded suite only if it fits cleanly; do not build browser training for
   the holonomy layer.

## Checks before you finish

- `pnpm install` if needed, then `pnpm check`, `pnpm test`, `pnpm build` all pass.
- Screenshots of every changed page at 1440x900 and 390x844 with Playwright (production build served statically),
  saved under `briefs/shots/`; look at them and fix overlaps, clipping, boxes, contrast, empty space. Light and dark.
- Every number in the app traceable to a results file or research doc.
- Commit in logical steps on `claude/story-wrapup`, messages ending with `Co-Authored-By: Astra (Codex)`. Never
  push, never merge into main.
- Append "Phase 3 done" to the `OVERNIGHT.md` Log with commits and what changed; final message: a page-by-page
  summary and anything you could not finish.

Neo will open this in the morning and prepare a presentation from it. Make every page something they can stand
behind, and make the hard idea feel inevitable.

## Note at launch (Claude)

Phase 1 is in (THEORY.md, PRIOR_ART.md, the swap-program benchmark in GROUPS.md). Present the theory with its
qualifications exactly as THEORY.md states them (faithful is sufficient, not necessary; Seq2Tens and path
development are the closest prior art; swap programs show the separation but no edge over order-aware baselines).
The A5/S5 word-problem session (branch claude/group-word-problems) is still running: do not wait for it. Give it
one clearly marked short subsection in the report and one sentence in Learn, each with a `<!-- WORD-PROBLEMS -->`
comment and neutral placeholder wording ("results pending"), which Claude will fill in after merging.
