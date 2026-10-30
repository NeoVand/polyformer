# Review pack: the figure set, round 10 (27 Oct 2026)

**Round 10, the reframe.** The paper now says that a loss evaluated only where the data go cannot see error
dynamics, so robustness comes from the architecture (a closure) or from an explicit probe (the perturbation); its
title is "Closure and aimed perturbation keep neural state exact far beyond the training length". The titles and
labels follow: Fig 1a now contrasts closure with no closure and draws the closure alone; Fig 1b says "Schematic,
simulated runs" in its title; Fig 4a no longer says "twice the noise of the strongest alternative" and marks the
earlier recipe at 0.08 over its 15 seeds exact without noise; "kick" is "perturbation" in Figs 1c, 2e and 4d; Fig 2b
says it is an illustration; Fig 3 says "part" for "clause"; Fig 4b says "verified exact" for "certified"; ED4b no
longer claims every exact model plateaus at the 960 classes; ED5's "dropped:" lines are Holm-corrected; ED7a notes
the closure alone. The full before-and-after table is in the README ("The reframe (round 10)"). The SVGs are
rebuilt from the same scripts, so they carry every change.

Round 9: every main and Extended Data figure now comes as an editable SVG beside its PDF and PNG, the Blender pieces
sit in the SVG as transparent layers with no text on them, and Figures 2 to 4 and ED1 to ED8 had a polish pass. This
page lists, per figure, the one-sentence takeaway (the paper's caption lead), what changed, and what needs your eye.
Look at `contact_sheet.png` first.

## What is where

| file | what it is |
|---|---|
| `contact_sheet.png` | the twelve paper figures in the paper's order, then `fig_inside` (not in the paper) |
| `../<name>.svg` | the editable figure (open in Illustrator); `../<name>.pdf` and `../<name>.png` (600 dpi) as before |
| `layers/<name>.png` | each SVG drawn from the SVG itself: whole, then each kind of layer alone, then each panel alone |
| `svg_check.md` | the machine check of every SVG (below) |
| `../../illustrator_layers.jsx` | turns the SVG's named groups into Illustrator layers (below) |

## How the SVGs are built

- **One group per panel, four kinds of layer inside it.** `panel-a`, `panel-b`, ... each hold `render` (the Blender
  images), `axes` (frames, ticks, tick labels, axis titles), `marks` (the data) and `labels` (titles, notes, keys,
  leader lines, panel letter). `background` is the white page. ED1 also has a `figure` group for its footnote.
- **Illustrator.** Illustrator opens any SVG into a single "Layer 1"; the panel groups and their sublayer groups
  arrive with their names. To get real layers, open the SVG and run `illustrator_layers.jsx` once (File > Scripts >
  Other Script...): every panel becomes a layer with sublayers render, axes, marks and labels, in the same stacking
  order, and nothing moves on the page (checked: identical export before and after, on Figure 1, Figure 2 and ED5).
- **Text is live text in one family, Helvetica Neue** (regular, bold, italic; it ships with macOS). Equations are set
  in it too. Mathematical italics, subscripts and superscripts are separate text runs placed where matplotlib put
  them, so `θ`, `c_y` or `λ^t` can be moved but each run edits as plain text. One exception: Helvetica Neue has no
  `→`, `∼` or `⊆`, so those three symbols in ED5's formulas are STIX General (also in macOS).
- **Renders.** Each Blender piece is its own transparent PNG, embedded at its native resolution (every one prints at
  600 dpi or more) and named after the render (`b-render-merged-theorem-ours`, `a-render-cube-s4096t`, ...). No
  render has text baked in; every label, arrow head and number is vector in the labels layer above it. Cameras and
  lights are the approved ones (Figure 1 round 6); only the resolution rose where a render printed under 600 dpi.
- **Checked.** All 13 SVGs: 0 glyphs as outlines; only installed fonts; every SVG drawn by a second renderer
  (librsvg) matches the PNG to within 0.07% of pixels once a one-pixel shift is allowed. Illustrator 2026 opened
  Figure 1, Figure 2 and ED5 with every text frame live and the right fonts (Figure 2: 140 frames, Helvetica Neue
  regular, bold, italic), and its export matches the PNG. Every figure builds with no house-rule warning (three type
  sizes, nothing past the page, no overlapping texts, no text on a line or marker).

## Questions for the whole set

1. **One family for equations.** Until now equations were TeX's Computer Modern (your earlier choice); for one
   editable family they are now Helvetica Neue italic. Say if you want Computer Modern back for equations only (it
   would be a second font family in the SVGs).
2. **No monospace.** Code (ED7c), bit strings (ED4, Fig 4c) and Lean lemma names (ED1) were in a monospace face; they
   are now Helvetica Neue. Menlo could come back as a second family for code only.
3. **STIX for three symbols** (ED5). The alternative is drawing them as vector shapes (as ED1 now does for its arrow)
   or rewording ("u ∼ v" as "u and v equivalent").
4. **Layers in Illustrator**: does the script give the structure you want, or would you rather have a different
   split (for example, all keys in one layer for the whole figure)?

## Figure 1 (`fig1_merged`): approved in round 6; round 10 changes its words

- **Takeaway**: A loss that fits the training data is blind across the path; a perturbation makes it see.
- **Changed in round 10**: a's title is "A closure keeps the state; without one it is lost", and the closure alone
  (exact on 10 of 10 seeds at every length, the same as ours) is a thin ink line along ours, labelled "closure
  alone" under "ours". b's title begins "Schematic, simulated runs:". c's title says "perturb the state", the
  render's label says "perturb" (the only clear room there is 8.3 mm; "perturbation" needs 12), and the chart says
  "perturbation remaining" and "events after the perturbation".
- **Changed in round 9**: panel b's render is now two images, one per slab (`merged_theorem_ours`, `merged_theorem_drift`),
  rendered from the approved camera and lights; stacked, they reproduce the approved render (mean difference 0.4 of
  255). The keys under b and d moved into the labels layer. Nothing visible changed.
- **Open**: each slab's image still carries the shadow the other slab casts on it, so if you pull the slabs apart in
  Illustrator, a faint shadow stays where the other slab was. Shadow-free slabs are one render away if you want them.

## Figure 2 (`fig2`)

- **Takeaway**: The theorems, seen in trained trackers.
- **Changed in round 10**: b's title is "Illustration: next-token valleys at both ends; only one end is exact" (the
  caption: "an illustration, not evidence"); e says "perturbation" for "kick" in its title and both axis titles.
- **Changed in round 9**: c's length key moved up into c's empty top-left corner; b widened from 52 to 66 mm to fill its
  column; "earlier recipe's objective" lifted clear of its curve; both ball renders redrawn at 2,200 px (628 dpi in
  print; they were at 599); equations in Helvetica Neue.
- **Open**: none beyond the set-wide ones.

## Figure 3 (`fig3`)

- **Takeaway**: Which part is needed where.
- **Changed in round 10**: a's title is "Which part is needed where: drop one, train again, test at the long
  length"; the first row is "all parts (M)"; the key says the shading is at one-sided Fisher p < 0.05 before
  correction and that 7 of 22 tests survive Holm (the paper's family, now `records.holm_drop()`). b's title is the
  caption's: "Each failure takes one of the theorem's two routes".
- **Changed in round 9**: nothing visible; the route key is in the labels layer.
- **Open**: the seven Holm survivors are not marked in a (an outline would need a caption sentence). Want them?

## Figure 4 (`fig4`)

- **Takeaway**: Error correction.
- **Changed in round 10**: a's title is "Ours tolerates more noise than our earlier recipe"; the cobalt label reads
  "earlier recipe: up to ε = 0.08 on its 15 seeds exact without noise", and its marker moved from the imputed 0.071
  to 0.080 (the curves are unchanged, each arm's median over all its seeds). No ratio is printed. b's title is "The
  automata snapped from the Lean trackers are verified exact", and its note separates the snapped automata (10 of
  10 verified) from the continuous trackers' bound (below 1 from blocks of 3 events). d says "perturbation": title,
  "rewrites after a perturbation of 0.3 rad" (its first tick is "0"), "perturbation angle (rad)".
- **Changed in round 9**: c's bit-string labels are placed only where the label's whole box sits inside one basin
  (before, only its centre was checked), so no outline crosses a label; d's title is cut to one story, dropping "the
  earlier recipe recovers every chain up to that size".
- **Open**: in c's middle map a sliver of basin 1000 is too thin to hold its label and is now unlabelled. A leader to
  it, or leave it? And should d's dropped clause go into the caption? For the paper: a's caption still ends "(2.0
  with the imputation, the figure printed in the panel title)"; the title prints no figure now.

## Extended Data 1 (`ed1_domains`)

- **Takeaway**: The settings.
- **Changed in round 9**: the state after each event is introduced by a short drawn arrow (Helvetica Neue has no arrow glyph);
  lemma names and paths in Helvetica Neue; tree letters italic, operators upright; each row's letter a to f is a real
  panel letter, so the SVG has one group per row.
- **Open**: none.

## Extended Data 2 (`ed2_landscape`)

- **Takeaway**: The landscape, an illustration.
- **Changed in round 9**: both terrains redrawn at 2,200 px (628 dpi in print; they were at 571); `×10⁻⁵` and the like in
  Helvetica Neue.
  The well labels keep their white backings (live text, separate objects).
- **Open**: none.

## Extended Data 3 (`ed3_losses`)

- **Takeaway**: The next-token loss along the weight line (b is an observation, not evidence).
- **Changed in round 9**: nothing visible.
- **Open**: none.

## Extended Data 4 (`ed4_globes`)

- **Takeaway**: The learned state condenses onto the automaton.
- **Changed in round 10**: b's title is "With equivalence training, Lean states fall into the 960 Nerode classes"
  (it said every exact model does; next-state training plateaus in 3 of 6).
- **Changed in round 9**: a's glass render enlarged (46 to 51 mm) into the free space beside it; bit strings in Helvetica Neue;
  in c, labels on the web of paths are pushed up to 4.5 mm clear, and the few still inside the web get a white
  rounded backing (90% opaque) so no path runs through a label. The text-on-lines check now also sees line webs like
  c's, which is how these were found.
- **Open**: the white backings in c, against leaders out to the rim. Backings keep each label beside its vertex.

## Extended Data 5 (`ed5_clauses`)

- **Takeaway**: The terms and the theorem's clauses.
- **Changed in round 10**: the title drops "four" ("The terms and the theorem's clauses: one path on the readout
  sphere"; the paper counts three parts), and the "dropped:" lines use the paper's Holm-corrected tests:
  equivalence, stories and counting; closure, five settings; aimed contraction, "no setting after Holm correction;
  S5 falls to 5 of 10 (adjusted p = 0.21)".
- **Changed in round 9**: the four formulas in Helvetica Neue (`→`, `∼`, `⊆` in STIX General, as above); `c_{s·w}` with a
  centred dot; the badges and callouts in the labels layer, so the sphere's render layer is the sphere alone.
- **Open**: question 3 above. In Illustrator those three symbols come from macOS's own STIX General, a slightly later
  cut than the PDF's: the arrow is a touch heavier.

## Extended Data 6 (`ed6_ablation`)

- **Takeaway**: Every objective in every setting.
- **Changed in round 9**: nothing visible.
- **Open**: none.

## Extended Data 7 (`ed7_frontier`)

- **Takeaway**: Exact at any tested length, with no generated tokens.
- **Changed in round 10**: beside "ours: 10 of 10 seeds exact", a note gives the closure alone: 3 of 3 exact on
  reversible programs, 10 of 10 on S5 read as text.
- **Changed in round 9**: c's program, word and outputs in Helvetica Neue (were monospace); the key in the labels layer.
- **Open**: question 2 above (code in a proportional face).

## Extended Data 8 (`ed8_cube`): new in this set

- **Takeaway**: The Rubik's cube: the factorised tracker on the frozen Qwen2.5-0.5B, trained on scrambles of 32
  moves, is exact on all 10 seeds at 4,096 and 10,000 moves.
- **Changed in round 9**: rebuilt in this set's style from the cube records, which `records.py` now loads and checks. a: six
  cubes along one scramble (solved, 32, 256, 1,024 and 4,096 moves, then the tracker's read-out at 4,096), re-rendered
  at twice the cube study's size; the figure asserts sticker by sticker that the read-out is the true cube. b: exact
  final state against scramble length: ours 10 of 10 seeds exact at every length to 10,000; the earlier recipe 3 of
  3; closure alone 2 of 3; ordinary training 0 of 3; the three frontier models pooled (shaded band: exact 95%
  Clopper–Pearson), 0 of 8 exact at 1,024 moves, 6 of them out of tokens. c: frontier output tokens per problem
  against the 64,000-token budget; ours generates none. The paper already includes `figures/build/ed8_cube.pdf`, which
  settles AUDIT item 11 (ED8 read by absolute path).
- **Open**: the cube study recorded fewer than three frontier responses in three cells (Claude 1 of 3 and Gemini 2
  of 3 at 256 moves, GPT 2 of 3 at 1,024), with no error logged; b pools what is recorded (n = 9, 9, 6, 8). Re-run
  those four problems, or say so in the caption?

## Outside the paper

- **`fig_inside`** (inside the language model, round 8): built to the same SVG standard; no visible change. Still
  waiting for your call on where it goes (AUDIT item 7).
- **`fig_blindness`, `fig1_story`** (the two retired Figure 1 candidates) are rebuilt for comparison only; the
  blindness render is redrawn at 4,200 px (610 dpi in print; it was at 377).

## Notes from the audit

- No figure prints a stretch value, so the 1.7 against 1.8 inconsistency (inconsistency 1) is the text's alone.
- Figure 2b's minima, 2×10⁻⁵ and 6×10⁻⁵, match the records (inconsistency 2).
