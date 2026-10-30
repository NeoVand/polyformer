# VIZ_EXPLORE: a gallery of genuinely interesting figures (Neo, 24 Oct ~11:10; enthusiast mode)

Goal: figures that make the paper feel special and make things click. Reviewers reward clean, tasteful visuals.
Explore widely, then curate hard. Palette and rules: research/figstyle/ (Cobalt and Rose, white backgrounds, no grey
or black fills, no matplotlib defaults, no frames, legends or titles inside panels, compact, aligned, no boxes,
TikZ-quality compute graphs). Numbers must come from raw records (research/master/build_master.py), never typed.

## Categories, at least two candidates each
1. **The problem clicks.** What the input really is in each domain, side by side: a program, a Lean rewrite chain,
   an S5 word, a digit stream, a story; with the state the model must carry drawn next to it, and what "64x longer"
   looks like.
2. **The result clicks.** Figure 1 candidates built on the master table: a domains-by-ingredients matrix that reads
   at a glance; exactness against length curves; the 0% to 100% contrast on the same architecture.
3. **The proofs click.** Blindness (two trackers in equally deep loss valleys, only one exact); stiffness (first-order
   vs floor-damped response to drift); closure and its counterexample (a scale clock); error correction (balls
   contracting onto class centres); holonomy (loops that close).
4. **How it works.** A block diagram of the frozen model, the state slot, the readout and the three loss terms; a
   compute graph of one training step; how a certified pair is made.
5. **Mechanism.** The tesseract globes, basins, the drift spiral, the 960 clusters of the minimal automaton.
6. **Surprises.** Anything in the raw data that is genuinely interesting and nobody has plotted yet.

Deliver research/../paper/nmi/figures/v5/gallery/ with PNG + PDF per candidate, a contact sheet, and a README ranking
your top eight with one sentence each on what the reader learns. Send nothing to Neo directly. Commit, no push.
