# R7 mapper: structural load paths (architecture)

**1. Objects and techniques.** Objects: the *load path* (the member chain from roof to footing); the *truss joint*, where
member forces balance; the *transfer girder*, re-routing misaligned columns. Techniques: the *lower-bound theorem*
of plastic analysis (any force pattern that balances the loads within every member's capacity proves no collapse, even if the real pattern is unknown); *Melan's shakedown
theorem* (1936: one fixed residual stress field safe at each corner of the load range means damage stops under every
infinite load history); *capacity design* (seismic codes make a ductile "fuse" yield before any brittle part, so
overload fails in a chosen, visible way).

**2. Map to the problem.** State = member forces; rule = joint equilibrium (our runtime); check = demand/capacity per
member (our per-view margin); search = finding an admissible pattern (our training).
- P1 Who: building officials and insurers accept a stamp, not a test per truck.
- P2 What: collapse cannot be checked afterwards.
- P3 Where: load must pass through the structure. For us: operands that exist only as pixels.
- P4 Beyond: shakedown certifies a history-dependent material by a witness, not a test.
- P5 Composition: connections fail, not members; our GSM8K loss is a connection failure (translation into the sheet).
- P6 Evidence: proof-load a specimen.
- P7 Trust: a bridge *load rating* (spare capacity over live load, minimised over members) posted on a sign.

**3. Map from the problem.** Structures sell an envelope and a designated failure mode; we certify one envelope (exact
glyphs) and sell the computation.

**4. Ideas.**

**A. Exact-or-refuse on photographed numbers (capacity design).** Take views from real scans (receipts, ledgers). Certify per glyph class an ordered margin over a perturbation ball: the "refuse" logit overtakes every wrong
digit before any wrong digit overtakes the true one, so a column total of any length is exact or refused, never
silently wrong. No calculator or cheap checker has the operands. Who: accounts payable, meter reading, pharmacy
doses. Breaks *views are exact rendered glyphs*. Kill: under 50% of real glyph
crops from 1,000 scanned columns fall inside the certified ball, or zero silent errors needs refusals above 30%.

**B. Shakedown certificate for the state slot.** Our no-go says no finite *test* certifies a history-reading step;
Melan certifies infinite histories by a *witness* plus a finite check. Find a box R of carried states with every view
safe from all of R and the step mapping R into R; the code model's 256 steps become all lengths. Kill: the smallest
closed interval box exceeds 10× the observed state spread, or a view loses margin inside it.

**C. Posted rating per device.** Publish min over views of margin / float-error bound per GPU and quantisation. Breaks
*the product is the computation*. Kill: a device rated above 1 errs.

**5. Grade.** A: TOOL (certified robustness with abstention exists, e.g. randomized smoothing, Cohen et al. 2019). B:
FRAME (an inductive invariant; snapping is its finite case). Best: A.
