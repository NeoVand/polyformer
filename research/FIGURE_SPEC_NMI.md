# Figure specification for the NMI paper (redraw; the v2 matplotlib figures are data-correct and design-poor)

Content per panel is fixed by `PAPER_BRIEF_NMI.md` §2 and the v2 captions in `paper/nmi/main.md`; the data loaders and
record paths are in `paper/nmi/figures/src/` (reuse them, change nothing in the numbers). Everything below is about how
the figures look. Reference for the visual language: the Part X figures on the live page (monochrome instrument style,
thin lines, direct labels, aligned baselines), and Nature's figure guidelines.

## Rules

- **Format.** Vector SVG authored directly (or matplotlib with a strict style sheet if faster, but the result must pass
  the rules below), exported to PDF and 600-dpi PNG. Widths: 183 mm double column for Figs 1, 2 and 4; 183 mm for Fig 3.
  Panel letters bold lowercase a, b, c, 8 pt, top-left, outside the plot area.
- **Type.** One sans family throughout (Helvetica/Arial or Inter), 6 to 7 pt for labels and ticks, 7 pt for axis titles,
  nothing larger except panel letters. Axis titles in words, sentence case, no units in parentheses where the words carry
  them. Numbers with thin spaces or commas as in the text (1,024).
- **Ink.** Black and three greys plus **one accent** (the page's accent, or a single deep orange) used only for the
  model the paper argues for. Line widths 0.75 pt for data, 0.5 pt for axes. No gridlines, no boxed legends, no frames:
  label lines directly at their right end (or with a short leader), and when a legend is unavoidable make it a tight
  text column inside the panel's white space. Markers small (2 pt), seeds as small hollow markers, means as lines.
- **Axes.** Left and bottom spines only, drawn 0.5 pt, ticks outside, 3 to 4 ticks per axis, shared y-axis range across
  panels that compare the same quantity, log x for lengths with ticks at the tested lengths only. The training-length
  band as a light grey rectangle with a 6 pt label inside it, nothing else inside the plot area.
- **Layout.** Panels aligned on a common baseline and top; equal panel heights within a figure; gutters 6 mm; no empty
  quadrants (if a panel has one, shrink the panel). Captions carry the method, so the figure carries only the finding.
- **Figure 1 is an illustration, not a plot.** (a) Two smooth arcs from one start node to one end node, drawn as thin
  black curves with five small dots each; exact: the arcs meet at one accent-filled node; drifting: the arcs end at two
  grey nodes with a short bracket labelled "drift". (b) One rounded rectangle "learned state" at centre, three thin
  arrows in, each with a four-word label, the accent arrow for the certified-equivalent one; the checker as a small
  stamp-like mark on that arrow, not a box with a paragraph. (c) Two curves from the origin, a straight accent line and
  a flat-then-rising grey parabola, one label each, a light band near zero labelled in three words. Total words in Fig. 1
  under 60.
- **Figure 2.** (a) The headline curve; the accent line sits on 1.0 and must read as flat and alone; comparison lines in
  greys with different dash patterns, labelled at their right ends; the lookup table as a thin dotted grey line labelled
  once. (b) Tokens per statement as a tiny horizontal bar chart with the numbers written at the bar ends, no axis.
  (c) Chains to 4,096, same conventions, transformer dotted.
- **Figure 3.** (a) Two scatter panels side by side with the ratio as a small number under each, no axes (they are
  projections), one accent for the exact tracker's clusters and greys for the plain. (b) Recovery curves, log x, two
  kicks, exact in accent, plain in grey, labelled. (c) Scatter of growth against exactness with ρ written in the corner.
- **Figure 4.** (a) Grouped bars, thin, with seed dots, labels under groups in two short lines, lookup table as a thin
  dotted segment per group. (b) Exactness along statements, log x, four lines with distinct dashes, plateau values at
  the right ends in 6 pt, the predicted levels as short dotted ticks at the right edge. (c) Three bars per group with
  whiskers, chance as a thin grey line.

## Deliverables

`paper/nmi/figures/v3/fig1.svg … fig4.svg`, their PDF and PNG exports, the source files, and a one-page contact sheet
PNG of all four for review. Reply in one line when Fig. 1 and Fig. 2 are ready for Neo to approve, before drawing 3 and 4.
