# Sketchpad: a language model that computes on a picture it keeps overwriting

29 Oct 2026. Status record for Neo and the paper. Everything below was measured today; nothing is pushed or published.

## Claim (scoped)
A pretrained vision-language model (Qwen3.5-0.8B) learns, with a small LoRA on its language layers only, to run exact
arithmetic on a canvas that is its **only** working memory. Each tick it reads a 3-cell strip of the canvas through its
own vision tower and writes the next glyphs (and, for multiplication, the name of its next step). Because the canvas is
the whole state and each tick sees only a finite strip, checking every possible strip once (the table) certifies every
run of every length. The certificate is re-run on the deployed numerics in the browser. *Grown, not built*: the
arithmetic is learned, not compiled. Boundaries: the problem is typed (photo reading is future work); a fixed runtime
stamps glyphs and moves the window where the model's output says; the theory of snap/restoration is prior work
(Brandoit et al. 2609.32447; Zhang & Xu 2609.23366), our contribution is the instance at language-model scale.

## Results
| Program | Table rows | Server certificate | Device certificate (M4, WebGPU) | Language | Long runs |
|---|---|---|---|---|---|
| Column adder, 2-token output (E2, seed 1, KL 1) | 242 | 242/242, min margin 3.56 | 242/242, 0.59 (q4 decoder) | ppl x1.007 | 10, 100, 1,000 digits exact; edit followed |
| Column adder, 1-token output (E2b, seed 1) | 242 | 242/242, 1.25 | 242/242, 1.40 (q4), 35 s | ppl x1.009 | 1,000-digit sum exact live in the browser, 163 ms/tick |
| Long multiplication (E4, 5 ops) | 1,553 | seed 1 (stratified, Modal): 1,553/1,553, 1.03 (adapter lost to a timeout; rerunning) | seed 3 (800 steps): 1,550/1,553 on fp16 | ppl x0.995 | 4x4, 6x6, 10x10 exact (server); 4x4, 6x6 exact live |
Other seeds: adder seeds 0/1/2 all 242/242 (seed 0 without the text term had ppl x1.095). Multiplication seed 2 at 800
steps: 1,513/1,553, and its products fail exactly where its failing rows are used (4x4 12/20, 10x10 0/5): the
certificate's necessity direction, measured.

## What we learned
- **Whole-canvas reading is not exact; foveated reading is.** Untouched, the tower reads an 8x8 digit grid at 97.8% per
  cell, but a single-cell crop is exact for all 10 digits at one vision token, and 998/1,000 three-digit column crops
  read exactly (upscaled). Exactness comes from looking locally, as in human foveal vision.
- **Deployment numerics matter.** The 4-bit browser decoder moves weak margins by about one unit in either direction
  (different rows fail on device and server); the fp16 decoder tracks the server within about 0.3. The device
  certificate is the one that counts; train with margin to spare.
- **Two browser gotchas.** transformers.js skips image normalisation for Qwen3.5 because `do_normalize` is missing from
  preprocessor_config.json (the community WebGPU demo has the same bug); teacher-forced scoring must append one token id
  per answer character.
- **Speed.** A tick costs about 80 ms per call plus 3.5 ms per prompt token on the M4; the one-token format and a
  7-token prompt give 144-163 ms per tick.
- **Retention is cheap here.** A KL term to the base model on plain text keeps perplexity within 1% (it was 9.5% without).

## Prior art (live gates today: research/audit/sketchpad_gate)
Generic "visual sketchpad" reasoning (MVoT, Visual Planning, Latent Sketchpad, Mirage, Chain-of-Sketch), optical
context compression (DeepSeek-OCR, Glyph, VTC-R1, MemOCR) and learned local arithmetic (Neural GPU; Wei 2603.29069, a
321-parameter cellular rule to 4,096-bit multiplication) exist. Not located: a pretrained VLM whose only working state
is an overwritten canvas, exact at hundreds of digits, certified by enumerating its local rules on the deployed
device, with causal edits, live in a browser.

## Next
Certified multiplication adapter (six Modal jobs running: margin 1 and margin 2) -> the polished /sketchpad page
(being built on branch `sketchpad`) -> a photo of a handwritten sum as the first frame -> discrete physics with a
conservation counter on the same executor -> Fable's O2 self-legibility (the model picks the glyphs it reads best).

## Inside the union adapter (29 Oct, late; $0 on the M4)
All 1,795 table rows, the position that writes the first answer token (inside_atlas.py, inside_probe.py, inside_steer.py).
- **Where the answer forms.** Logit lens (final norm + lm_head on each layer): the answer is not readable before layer
  ~15; it takes the lead for good at median layer 20 (SUM), 19 (ADD/ADZ), 21-24 (MUL).
- **Who writes it.** A class-mean push at the answer position (mean state of the target answer minus the true one)
  does nothing before layer 19 (SUM: 8/80 at L19) and works right after it (77/80 at L20, 79/80 at L21-22, 80/80 at
  L23). Layer 19 is full attention (6 of 24 layers are; the rest Gated DeltaNet): it re-reads the three image tokens and
  writes the decision. The big moves of the state also come right after the full-attention layers 15 and 19.
  Multiplication is not pushable this way (<= 23/80 at any layer, by value or by digit): it decides in its last layers.
  On device (WebGPU, fp16) the push lands 31/33; both misses got the digit but not the carry.
- **Geometry.** At layer 16 the SUM class means lie in order 0..19 on a U-shaped curve (rank correlation 1.0 along the
  first axis); by layer 22 it has broken into answer clusters. A linear read-out of the value is approximate
  (R^2 0.97, exact 50-60%), not exact. In a 3D LDA slice (shrinkage 0.9, orthonormalised) of layer 24 the nearest class
  mean is the true answer for 97% (SUM) and 100% (MUL, ADD) of views.
- **On the page.** patch_onnx_inside.py adds a `hidden_states` output and a `steer` input (layer 20) to the program
  graph; logits unchanged (device min margins 8.16 and 4.66 as before). inside_assets.py writes the lens and map data.
  Page commit 9097c2b0 on branch `sketchpad` (local): machine, lens, 3D state space with push, table walk; one screen.

## E6: a multiplier step in one forward pass (30 Oct; about $2 on Modal, the rest $0 on the M4)
E5 writes a multiplier step's three tokens one after another: three decoder calls per tick in the browser. E6
(e6_slots.py) appends two `?` slots to the prompt and reads the three answers at `=` and the slots; training continues
from the E5 union adapter with recipe v2 (H100, `e6 <seed> <init>` in modal/launch.py).
- **Seed 3** stopped at step 1,100: 1,795/1,795 table rows, min margin 3.35 (MUL), perplexity x1.007; exact on 4x4
  20/20, 6x6 10/10, 10x10 5/5, 10-digit sums 20/20, 100-digit 5/5, 1,000-digit 2/2. Seed 1 oscillated between
  1,780 and 1,795 rows for 1,300 steps and was cancelled.
- **Inside.** The multiplier now decides earlier (logit lens: median layer 20 for MUL, 18 for ADD/ADZ; E5: 21-24) and
  is pushable: a class-mean push at layer 20 lands 80/80 for MUL by digit (E5: <= 23/80) and 80/80 for SUM (E5 77/80).
  In the page's 3D slice the nearest class mean is right for 99% of MUL and 98% of ADD views.
- **On the device (M4, WebGPU, fp16).** 242/242 addition views (min 5.58), 1,553/1,553 multiplier views (min 3.53).
  Every step's prompt is padded with `?` to the longest step word (ADD is one token, the rest two) so a wave step is one
  batch; a trailing token cannot change the places before it, and the certificate checks the padded form. The decoder
  computes logits only at the last four places (about 15% less per call). 12x12: 19 s (E5: 63 s one pass at a time,
  28 s overlapped); 6x6: 6 s (E5 overlapped: 12 s).
- **Where the time goes.** A decoder call costs about 100 ms plus about 30 ms per row (10 tokens a row): it is compute
  bound, not launch bound, so further speed needs fewer tokens per step or fewer steps, not more batching.
- Built with build_program.sh (LoRA into the fp16 graph, the inside window, atlas, map and lens data, push check).
  The program folder `qwen35-union-e6-s3-inside` ships `certificate.json`; page commits 5c936d8f and ed439435 on
  branch `sketchpad` (local).
