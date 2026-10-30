# SKETCHPAD: a language model that thinks on a canvas it keeps overwriting

Fable, 29 Oct 2026, for Neo. Read-only, $0. Three pages. Sketchpad gate (S1–S5) still running; prior art below is from our
own notes and today's verified reads, not from its output.

## 0. What today's facts did to LEAP2

PROBES (untouched Qwen3.5-0.8B: recall goes through attention; windowed, the DeltaNet state keeps a fading trace with a
median half-life of 19 tokens) and Brandoit et al. 2609.32447 (verified abstract: "affine recurrences ... realize at
most definite automata at finite precision"; exact tracking needs one map that both contracts and separates) withdraw
LEAP2 §2's mechanism. Registers cannot sit passively in a delta-rule state; kill K3 fired before the pilot. The thesis
survives in a different body: the state must be re-snapped by a non-affine map every tick, and a canvas rendered as
discrete glyphs and read back is that map. Brandoit *built* the snap as a layer (NFSM). The sketchpad *grows* it out of a
pretrained model's own render–read loop. That is the positioning sentence for this whole direction, and it also means
our October snap theory (contraction + separation = exact codes) is, in its core statement, theirs by five weeks.

## 1. The sharpest design: fovea, glance, paint

**State.** A canvas of H×W cells, each one glyph from a small alphabet G (digits, blank, carry, a few marks). The canvas
is a Markov state: at each tick it is overwritten in place, never appended; nothing else carries the past. The previous
frame is evicted from the cache (pinned policy with a canvas instead of a state token).

**Three views per tick.** (i) The *glance*: the whole canvas as one low-resolution image through the model's own vision
tower, for planning, uncertified. (ii) The *fovea*: a crop around the model's pointer, at glyph resolution, the only
view the exact rule may use. (iii) The program prefix Π in the cache, as REGVM. The model emits a few tokens: a pointer
move, the glyphs to write, a halt bit. **Who renders:** a fixed painter (one font, one grid) turns glyph tokens into
pixels, and a fixed cropper cuts the fovea where the pointer says. Both are tokenizer-grade rules with no data logic;
together with the window they are the whole runtime. READ is gone from the bus: the model reads its memory with its
eyes. WRITE is a painter. This is strictly less host than REGVM.

**Pixels or latent grid.** Pixels, for three reasons: the display *is* the state (no lens, unlike LEAP2 §5); the render
is the snap by construction (a glyph is pixel-exact, so no basin is needed on the certified path); and a photo can be
the first frame. A latent grid snapped to a codebook is the fallback if E1 shows the vision tower cannot read a designed
alphabet exactly; it loses the first two reasons and reopens our three latent collapses.

**Conditions.** 1: one LoRA, one model. 2: the LLM computes; the runtime paints, crops and windows, which is less than
the bus NEW_MODEL already accepted. 3: a photo or a sentence is the prompt; the model writes the program and runs it
on the canvas. 4: no chain of thought; the canvas is the thought, constant size, overwritten. 5: certified on the fovea
rows (§2), with two stated boundaries: perception of photos and the glance. 6: compact programs (REGVM ISA with 2-D
pointer moves) and, through O2 below, a notation the model chooses for its own legibility. 7: one executor; a program is
rows for its opcodes' view templates. 8: size generalisation from locality (T2); task-family generalisation unchanged,
still the compiler's risk. 9: text and VQA retention measured. 10: the architecture it points at is a model whose
working memory is a picture it can see, foveate and overwrite. 11: §5. 12: fits.

## 2. The theory worth owning

**T1, the pictures theorem (restoration).** Under the pinned-canvas policy, exactness at every tick for every run
length is equivalent to per-row exactness over the finite set of (view, opcode) pairs. This is Theorem P with a canvas
in place of the state token, plus the no-finite-test theorem for the necessity direction. Routine lift; worth stating,
not worth selling. **S1 is real** but it is our own Theorem P and Brandoit's contract-and-separate said in pixels.

**T2, the locality certificate, with the conservation corollary.** If every written cell's view is a fixed template of
k cells plus the opcode, the certificate has |G|^k × |ops| rows and is independent of H, W and run length: size and
time generalisation for free. Corollary: any invariant of the true local rule (particle number, momentum, parity, a
checksum) holds exactly in the learned executor at all sizes and times once the table matches. **S2 is real as a
certificate statement**; as an empirical fact it is Neural GPU (2016) and the NCA line (our L2 notes: addition to a
million digits from 16, Wei 2026). The template must be small: a 3×3 fovea over 12 glyphs is 5×10⁹ rows, impossible;
column addition's template (three digits and a carry) is 2×10⁴. Views are per opcode, as REGVM's are.

**T3, the exact optical capacity law.** DeepSeek-OCR reports compression at ~97% precision; for working memory the
only number that matters is cells per vision token at *exact* read-back on the whole alphabet, with its margin. Nobody
has measured that for a small VLM; E1 does. **S3 is real as a measurement**, not a theorem.

**S4 is real for discrete lattice physics only** (§4). **T4, which I will not claim:** 2-D local views beat 1-D tapes on
column arithmetic; that is classical two-dimensional Turing-machine theory.

## 3. Training objectives

- **O1 next-edit supervision.** (Π, glance, fovea) → (pointer move, glyphs, halt), from a reference executor over
  rendered canvases; REGVM's generators with a 2-D pointer. Standard.
- **O2 self-legibility (new).** A cycle term: what the model writes, the painter renders, the model must read back
  exactly through its own tower. With a large candidate font, select per symbol the glyph with the largest read margin:
  the model ends up with a notation chosen for its own eyes. This is condition 6 taken literally and a line nobody has.
- **O3 certificate as loss.** The full fovea domain of every opcode, each step, with a margin hinge: the certificate is
  the training set, so passing it is not luck. Same idea as LEAP2 §2(a); the domain is now small enough to enumerate.
- **O4 retention.** KL to the base on 20% ordinary text and 10% VQA; registered ratio ≤ 1.05; the Stage 2r recipe.
- **O5 optical curriculum (new, after E1).** Start at one cell per vision token and shrink the glyphs while O2 holds
  exact: a denser working memory grown under an exactness constraint, which is S3 as a training axis.
- Dropped: RL (HR1–HR3 null); distillation into the core (INSIDE's language cost); latent programs (three collapses).

## 4. World models and physics: what exact means there

A lattice-gas automaton (HPP, FHP), a sandpile, Life, integer-velocity particles: each is a local rule on a glyph
canvas, so each is a program for the same executor, and T2's corollary gives *exact* conservation of whatever the rule
conserves, for all sizes and all time, once its table is certified. That is the honest bridge: a learned simulator you
can trust for 10⁶ steps because its rule is checked, not because its loss was low. Learned video world models drift;
this one cannot. What it is not: continuous physics. "Exact" means the discrete rule; FHP's Navier–Stokes limit is the
rule's theorem, not ours. And scale is the enemy: fluid-looking behaviour needs ~128² cells, which the browser cannot
redraw through the model (§5). In the browser, physics is a few particles with a conservation counter that never moves;
a fluid is a server-side figure, labelled as such.

## 5. The browser demo and what a frame costs on an M4

**The demo.** One tab, Qwen3.5-0.8B (2B if latency allows). The user photographs a handwritten sum or types one. The
model writes its program, then the canvas fills at handwriting speed: digits, carries, the pointer sliding left; no
text appears, the picture is the thinking. A badge shows the certificate: the finite table, open to inspection, every
row checked on this device. The user clicks a digit mid-run and changes it; the model reads the altered canvas and
continues correctly from it (restoration, by construction, not by training). Then 100 digits, the canvas panning while
the per-tick cost stays flat (the fovea). Then the same model switches program: long multiplication grid; a sandpile
or bouncing particles with a particle count pinned in a corner. Then the user asks it a question and it answers like a
normal chat model. What stuns researchers is not the addition; it is a pretrained VLM whose working memory is a picture
you watch, with no chain-of-thought tokens, exact at lengths no transformer reaches, recoverable under live edits, with
a certificate you can read, still chatting. Nothing in it may be slower than handwriting.

**Per frame (estimates; E0 measures them).** Qwen VL towers spend one vision token per 28–32 px square (Qwen3-VL: 32).

| Item | Tokens | Cost at 0.8B, WebGPU, q4 (guess: ~1k tok/s prefill, 30–60 tok/s decode) |
|---|---|---|
| Glance, 256×256 canvas | 64–84 | ~0.1 s |
| Fovea, 3×3 cells at 32 px | 9 | ~0.02 s plus tower |
| Decode per tick (move, glyphs, halt) | 4–8 | 0.1–0.25 s |
| Whole canvas re-emitted as text, 16×16 | 256 | 4–8 s, which kills "video" |

So the live demo is foveated edits at 2–4 ticks/s, and 2B roughly halves that. A 256-cell lattice gas changes O(n)
cells per tick and runs at seconds per frame; that is why §4's physics is particles in the browser.

## 6. The first two cheap experiments

**E0 (hour, $0).** Transformers.js on the M4: Qwen3.5-0.8B with one 256×256 image; measure prefill, decode, tower time,
tokens per image. Fills the table above.

**E1 (day, $0, M4, untouched weights): the exact optical capacity of Qwen3.5-0.8B.** Render grids of the alphabet G at
32, 16 and 8 px per glyph (1, 4 and 16 cells per vision token) and sizes 8×8 to 16×16; teacher-forced exact read-back
of the grid, and the fovea read: "the three cells above the pointer". Record per-cell and per-grid exact rates and the
margin per glyph. *Predictions:* 32 px ≥ 0.999 per cell and a positive margin on every glyph; 16 px degrades on
look-alike pairs; 8 px fails. *Kill:* if 32 px is below 0.99 per cell at 8×8 untouched, the tower is not an exact reader
without training; go latent-grid (codebook snap) and lose the display-is-state property, or train the reader first
(O2) and re-run E1 before anything else. E1 also fixes the glyph size for E2 and the first O2 font.

**E2 (day, ≤ $10 or $0 on the M4): column addition on the canvas, foveated.** LoRA on Qwen3.5-0.8B, O1 + O3 on the full
template domain (two digits and a carry → written digit and carry; pointer moves left), O4 retention, three seeds.
Evaluate under the pinned-canvas policy at 10, 100 and 1,000 digits, and the certificate by rendering all rows through
pixels and reading them back. *Predictions:* rows 100% with positive margins; sums exact 100/100 at 1,000 digits on
≥ 2/3 seeds; a mid-run edit of any digit is followed correctly (restoration); text ratio ≤ 1.05. *Kills:* rows pass but
long sums fail → the window leaks history or the pointer rows are wrong, fix the policy before any new idea; rows fail
at E1's glyph size → the reader's margin shrinks under the LoRA, protect it (freeze the tower, raise O2's weight) and
re-run; retention fails → the recipe, not the idea, and Stage 2r is the known fix. If E2 passes, day 3 is the ISA with a
2-D pointer on the canvas (REGVM's 13 fixtures drawn), day 4 the particles with a conservation counter, then the page.
