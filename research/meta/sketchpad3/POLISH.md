# POLISH: the demo looks great, makes sense and works; a logo

Neo, 31 Oct 2026: "Make sure everything in the demo page looks great, makes sense, and works. The colors will need to
be tuned for the light mode. Sketchpad itself needs a logo."

- **Repo:** `/Users/neo/repos/sketchpad` (NeoVand/sketchpad, live at https://neovand.github.io/sketchpad/).
- **Pushing:** pushing `main` is approved, after every check below passes.
- **Design rules:** the brief that made the light design is polyformer `research/meta/sketchpad3/PORT.md`. Its palette
  (Cobalt and Rose) and its rules stand.
- **Out of scope:** the Algebra tab's sheet and work-order panels. Neo wants the algebra shown as normal algebra, and
  that design is being decided separately. Leave those two panels alone. Everything else on the Algebra tab is in
  scope.

## 1. Looks great: tune the light mode

Look at every view at 1440×900 and at 375 px, before and after a run, and fix what reads weakly. Problems seen so far:

- **Inside views.**
  - "Layer by layer" bars are faint.
  - "State space" dots are pale grey on white with low contrast.
  - "The table" grid is rose on pale pink.

  Each view needs a clear figure and ground in light mode: ink for structure, rose for the model's answer and the
  certified rows, cobalt only for the alternative or a push, and violet only for references. Use white-ended colour
  maps (the palette's rule).
- **Text contrast.** Every caption must be at least 4.5:1 against its background. `#7D8BA8` on white is about 3.4:1,
  too weak for small text; use `#4C5B78` or darker. Measure, don't guess.
- **"One tick".**
  - On a phone, the empty strip is a tall box with a left rule.
  - The label "SUB □ +" is cryptic.

  Make the empty state quiet and the label readable.
- **Hierarchy.** At a glance a visitor should see: the problem, the sheet, the answer, the proof. Then the inside
  views. No boxes, no chips, no double strokes; spacing and tone carry structure.

## 2. Makes sense

A newcomer must understand every panel from its caption alone.

- **"The machine" graph.**
  - The node names are internal codes: ADD, MUL, ADZ, FLS, NXT. Give them plain names, or a plain caption that
    explains each one.
  - In Calculate, the graph shows the multiply machine while the step is a subtraction ("SUB: difference digit 0"),
    and SUB is not a node. The graph must match the procedure that is running (division: estimate, multiply,
    subtract, lower the guess; square root; gcd), or be replaced in Calculate with something that does.
- **Calculate's sheet.**
  - Name the rows the way people say them (dividend, divisor, quotient, remainder).
  - Draw the decimal point in a quotient computed "to k places".
  - Drop a leading zero the reader does not expect.

  These are display-only changes. Never change what the model reads: the strip shown as "the model's input pixels"
  is part of the certificate.
- **Before the model loads,** every tab shows its default problem laid out on the sheet. Today, Calculate on a phone
  shows an empty sheet.
- **Units and words:** say what "views" and "steps" mean once, where they first appear.

## 3. Works

On the M4, exercise everything:

- every preset in every tab;
- typed input, including bad input, huge numbers, negative numbers and divide by zero;
- the Fast toggle;
- the light and strong checks;
- the push at layer 20 (click a digit on the multiply map);
- the certificate's "Check every view here";
- chat;
- GPU-loss recovery.

There must be no console errors, and every result must be exact.

The CALC session may still be running a timed test on the GPU. Keep your runs short until the orchestrator says the
GPU is free, and leave the full certificate run and the timings to the orchestrator.

## 4. A logo for Sketchpad

- **Approach:** vector only (SVG), drawn by you. No generated pixels.
- **The idea:** it should carry the work itself. A sheet seen through a window of three cells, with the model writing
  the third, is the obvious seed. Look for better ones: Sutherland's Sketchpad (1963) is the namesake, and the light
  pen is fair game.
- **What to make:** three candidates, each as a mark plus the wordmark. Make each work as a 16 px favicon, in the
  top bar, and at 512 px.
- **Choose:** pick one and say why, wire it in (favicon, top bar, the social image if one exists), and keep the other
  two as SVGs in `static/logo/candidates/` so Neo can choose differently.
- **Colours:** ink with one rose accent at most.

## Verify and report

Lint, svelte-check, all tests and the build pass. Then:

1. Take screenshots at 1440×900 and at 375 px of the paper and of each demo tab, before and after a run.
2. Push, and check the live site.
3. Report, in under 300 words:
   - the commits and pushed SHA;
   - before and after screenshot paths;
   - the logo candidates (paths) and your pick;
   - anything you could not make work.
