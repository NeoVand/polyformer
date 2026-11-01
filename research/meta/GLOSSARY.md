# Glossary (plain words, for Neo's system prompt)

Each entry: what it is, who/when, and why it matters to this project. Started 30 Oct 2026; add as terms come up.

- **Pointer attention.** An attention head whose weights are nearly one-hot: each token attends to exactly one other
  token, so the pattern is a set of arrows (pointer networks, Vinyals et al. 2015). A hard pointer is a graph edge we can
  certify; soft attention is not. Qwen's lookup heads are ~95% pointer-like, which is why they work and why they cannot
  be certified at the weights level.
- **Looped (universal, recurrent-depth) transformer.** The same block of layers applied repeatedly to its own output
  (Ouro, Huginn). More compute per step without more parameters; one loop iteration can be one rewrite step. It adds no
  memory across steps; Ouro collapsed after ~12 loops in our probes.
- **Neural GPU** (Kaiser & Sutskever 2016). A grid of cells updated by one learned local rule at every layer, in
  parallel; trained on short binary arithmetic, generalised to much longer. The first clear "local rule + parallel
  update + length generalisation", so prior art for our canvas; no certificate.
- **Graph attention network** (Veličković et al. 2018). Attention restricted to a graph: each node attends only to its
  neighbours. When the mask is the graph, a node's update depends only on its neighbours, which is the locality a finite
  certificate needs.
- **Interaction net** (Lafont 1990). Computation as graph rewriting with strict locality: each node has one principal
  port, rewrites happen only where two principal ports meet, each pair of node types has exactly one rule. Every rewrite
  is local, all available rewrites can run at once, and the result never depends on order. Universal; HVM is a modern
  runtime. The cleanest substrate for "many local rewrites, one certified rule table".
- **Neural rewriting** (Chen & Tian 2019, Neural Rewriter). A network trained by RL to choose which hand-written rewrite
  rule to apply where. Prior art for a network *choosing* rewrites; not for a network *performing* them with a
  certificate.
- **Constructed looped-transformer computer** (Giannou et al. 2023). Hand-set weights that make a looped transformer run
  an instruction set with a program counter, registers and branches. Shows the architecture can be a computer; says
  nothing about training one, keeping language, or certifying a learned one.
- **Confluence (here).** A rewrite system where every order of applying the rules reaches the same final form.
  Makes the uncertified part harmless: the language model's strategy can change the number of steps, never the answer.
  Canonical-form algebra and interaction nets have it by construction. Without it, each rule can still be certified
  sound, but a bad strategy can stall or reach a different equivalent form, not a wrong one.
- **Certificate vs training.** Training changes weights to be right on average on sampled examples. Certification
  changes nothing: it runs the model on *every* input the rule can ever see (the finite view domain) and requires the
  correct output to win by a margin; a theorem (Theorem P) then extends that to every run of every length. Loss is an
  average; a certificate is a minimum.
- **Margin.** Correct token's logit minus the best wrong token's logit, in log-odds (3 ≈ 20× more probable). 4-bit
  quantisation moved margins by up to 2.5 on the M4, so we train with hinge 4, stop at ≥ 3, and re-check on the device.
- **Rows.** One possible view (fovea picture) for one opcode with its correct output. Primitive rows (digit facts) are
  certified once; control rows (per program line) are certified per program in seconds. 242 for the column adder,
  1,210 for digit multiplication, 1,795 for the union adapter.
- **Pinned policy / Markov canvas.** The model's only memory of the past is a bounded state that is re-snapped each
  tick (a token, or a canvas of glyphs it overwrites); the previous frame is evicted. This is what makes a finite
  certificate possible; a decoder that keeps its history admits none (our no-finite-test theorem).
- **Fovea / glance.** Fovea: the small crop the certified rule is allowed to see. Glance: the whole canvas at low
  resolution for planning, uncertified, kept out of certified ticks.

## Added 30 Oct (Neo's questions)

- **Hard vs soft attention; sparsemax / entmax.** Soft attention spreads weight over many keys (a weighted graph). Hard
  attention picks one key (a pointer). Sparsemax (2016) and entmax (2019) are softmax replacements that can output exact
  zeros and exact one-hots, but which inputs come out one-hot is still learned. Certifiable pointers come from
  *structural* addressing (a field names the target and builds the mask) or from snapping a head whose argmax is unique
  with a margin on a finite view domain.
- **Adaptive Computation Time (ACT, Graves 2016); PonderNet (2021).** Learned halting for recurrent/looped models: each
  step adds a halting probability and the loop stops when it reaches one. Ouro's exit gate is of this kind. For a
  rewriting reducer, "a pass changed nothing" is a better stop: checkable, not predicted.
- **Neural GPU vs NCA.** Both: a learned local rule applied to every grid cell in parallel over many steps. Neural GPU
  (2016): convolutional gated recurrent unit, synchronous, steps scale with length, trained on final output only, aimed
  at algorithms. Growing NCA (2020): fixed perception kernels (identity + Sobel) then a per-cell network, asynchronous
  random updates, alive mask, aimed at growing/regenerating patterns.
- **GCN vs GAT vs graph kernels.** Graph convolution (Kipf & Welling 2017): each node averages neighbours' transformed
  features with fixed weights from the normalised adjacency. GAT (2018): same, with learned attention weights over the
  neighbour set. Both use one set of weights for any graph of any size; the graph is the input. Huge degree = a big
  softmax, handled by neighbour sampling (GraphSAGE). Graph kernels (e.g. Weisfeiler–Lehman) are older similarity
  functions between whole graphs for SVMs. A transformer is a GAT on the complete graph with positional encodings.
- **Interaction combinators; HVM.** Lafont 1997: three agent types (constructor, duplicator, eraser) and six rules,
  universal for interaction nets and for the lambda calculus via optimal-reduction encodings. HVM = Higher-order Virtual
  Machine (Taelin / HigherOrderCO; HVM2 2024), a massively parallel runtime for them, with the Bend language. Rules are a
  fixed table you write once; nets are programs you compile; learning enters only in executing the rules (our
  interpreter) and in compiling problems into nets (the LM).
- **Frozen twin + bridge (the "corpus callosum" family).** Progressive Neural Networks (2016): frozen column + new column
  + lateral links. Side-tuning (2019) / Ladder Side-Tuning (2022): frozen backbone, small trainable side net reading its
  activations. CALM (DeepMind 2024): two frozen LMs joined by trained cross-attention bridges. Model stitching (2015,
  2021): learned linear maps between layers of two networks. Task arithmetic / model soups / TIES / DARE: superpose the
  fine-tuned delta onto the base in weight space. X-LoRA (2024): a head reads the hidden state and scales each LoRA per
  token and layer. Branch-Train-MiX: fine-tuned copies merged into an MoE with a learned router.
- **Adapter gate (ours).** A LoRA model is two models sharing all weights: adapter off = untouched base, adapter on =
  executor. A scalar gate on the LoRA path (one multiplier node in the browser graph) runs chat on the base with zero
  language loss and canvas ticks on the adapter; a learned gate head makes "use the sketchpad now" the model's own
  decision (measured, not certified).

## Added 30 Oct (second round)

- **Why attention sharpens.** Softmax attention has no finite optimum when selecting one token suffices: gradient descent
  keeps widening the logit gap, so weights tend to one-hot (implicit max-margin bias; Tarzanagh et al. 2023 prove
  attention converges to a hard-margin token selection). Heads sharpen for lookups and stay soft for averages.
  Conjecture: natural data's dependencies are sparse and redundant (compositional generation), so one pointer is enough.
- **Sparsemax / entmax.** softmax = argmax ⟨p,z⟩ + Shannon entropy. sparsemax = Euclidean projection of z onto the
  simplex: p_i = max(z_i − τ, 0), τ fixed by Σp = 1 (sort + threshold); exact zeros, one-hot when the top gap ≥ 1.
  α-entmax uses Tsallis entropy: p_i = [(α−1)z_i − τ]_+^{1/(α−1)}; α=1 softmax, α=2 sparsemax, α learnable per head.
- **REINFORCE.** ∇E[R] = E[R(a) ∇ log π(a)], estimated by sampling, with a baseline to cut variance. Unbiased, noisy.
- **Straight-through estimator.** Forward: the discrete op (argmax, round, codebook snap). Backward: pretend it was the
  identity or its soft version. Biased, low variance. Gumbel-softmax adds sampling noise. VQ-VAE's codebook is trained
  this way, i.e. a learned snap.
- **Deep equilibrium model (DEQ, Bai et al. 2019).** Train the fixed point z* = f(z*, x) of one layer instead of a fixed
  depth; more iterations converge monotonically. The cure for looped transformers degrading past their trained depth
  (Ouro's state never settled in our probes); same requirement as Brandoit's contraction. Halting = "nothing changed".
- **Fine-tuning forgetting is a field: continual learning.** Standard answers: progressive networks, side networks,
  adapters with gates, replay, regularisation (EWC), weight-space merging. Name the field before inventing a trick.

## Added 30 Oct (third round)

- **Implicit max-margin bias.** On separable data, unregularised gradient descent on a logistic-type loss grows the
  weights forever, and their *direction* converges to the hard-margin (SVM) separator although the loss never asked for
  it (Soudry et al. 2018); the exponential loss tail keeps pushing on the tightest points. For attention (Tarzanagh et al.
  2023) the limit is a hard token selection. Why our margins keep rising with training on separable rows. [zoo]
- **Softmax as entropy-regularised argmax.** softmax(z) = argmax over the simplex of ⟨p,z⟩ + H(p); with temperature T
  the bonus is T·H(p) and T→0 gives argmax; the maximum value is log-sum-exp (free energy). Swap the bonus to get
  sparsemax (quadratic) or entmax (Tsallis). The entropy term is what keeps probabilities off zero.
- **Straight-through, one line.** y = x + stop_gradient(round(x) − x): value round(x), derivative 1. Lets gradients pass
  a discrete op (argmax, rounding, codebook snap) by pretending it was the identity in the backward pass.
- **Progressive neural networks** (Rusu et al. 2016). Continual learning with zero forgetting: freeze the trained column,
  add a new column per task, learned lateral adapters feed each new layer from the frozen columns' layers; train only the
  new column. Costs: parameters grow per task, task identity must be known at inference (the gate problem). Ladder
  Side-Tuning is the memory-light version. [zoo]
- **Banach fixed-point theorem.** If a map shrinks distances by a factor < 1 (a contraction), it has exactly one fixed
  point and iterating from anywhere converges to it geometrically. Why a contractive inner loop can "think longer"
  without changing its answer: more iterations only get closer.
- **Deep equilibrium model** (Bai et al. 2019). A layer defined by its fixed point z* = f(z*, x), trained by implicit
  differentiation through the fixed-point equation (cheap approximations exist). The cure for looped networks degrading
  past their trained depth. [zoo]
- **Overthinking** (Schwarzschild et al. 2021; Bansal et al. 2022). Recurrent networks trained to extrapolate by
  thinking longer degrade past training depth; fixed by recalling the input each step and a progressive loss. Closest
  prior to "thinking more should not hurt". [zoo]
- **Nested fixed points (ours, 30 Oct).** Inner continuous loop (contraction → unique fixed point = "convinced") commits
  one discrete write to the canvas (the snap = separation); outer loop ends when a pass changes nothing. Certificate:
  per view, run to convergence, check the write with margin, bound the contraction constant. Untested; see IDEA_ZOO.

## Added 30 Oct (from the loops gate, GATE_LOOPS.md)

- **HRM, Hierarchical Reasoning Model** (Jun 2025). Two coupled recurrent modules at different timescales, trained with a
  one-step gradient taken at an assumed fixed point (DEQ-style) and an adaptive halting head. Ren & Liu (Jan 2026) show it
  violates its own fixed-point assumption, has multiple fixed points and "guesses the first", getting stuck. [zoo]
- **TRM, Tiny Recursive Model** (Oct 2025). HRM simplified to one small network recursing on answer + latent, with full
  backprop through the recursion; strong on Sudoku/Maze/ARC with heavy augmentation. [zoo]
- **Attractor Models** (May 2026). A backbone proposes embeddings; an attractor module refines them to a fixed point with
  implicit differentiation and convergence-based iteration count; works at LM scale (770M beats a 1.3B transformer).
  "Language model + fixed-point refinement" is therefore taken as a headline. [zoo]
- **DEAR, Deep Equilibrium Algorithmic Reasoner** (Feb 2024). Solve an algorithm's output as the equilibrium of a GNN
  rather than matching steps; CLRS benchmark. [zoo]
- **monDEQ / Lipschitz-bounded equilibrium networks** (Winston & Kolter 2020; Revay et al. 2020). Equilibrium networks
  whose parameterisation guarantees a *unique* fixed point and convergent solvers, or a certified Lipschitz bound. The
  existing tool for a provably convergent "thinking" loop. [zoo]
- **EBT, Energy-Based Transformers** (Jul 2025, ICLR 2026 oral). Predict by minimising a learned energy over candidate
  outputs; more optimisation steps at test time help. Thinking as optimisation. [zoo]
- **CEGIS-style training.** Train, verify, add the verifier's counterexamples to training, repeat until none remain
  (monotonic nets 2020; Trainify 2022; certified nets 2024). Our failing-row replay is this with an exhaustive verifier.
- **NRS / FastNRS** (Petruzzellis, Testolin, Sperduti, Jul 2025). Neuro-symbolic architecture modelled on term rewriting
  for formula simplification; OOD generalisation; the direct competitor for a canvas rewriting interpreter. [zoo]
- **Neural lambda calculus** (2023). A transformer trained to do β-reduction on strings, 99.7% one-step; no graph, no
  certificate. Closest to a neural reducer that exists. [zoo]
- **LoopViT / Looped Diffusion Transformer** (2026). Looped vision transformers for ARC (entropy-based exit) and for
  diffusion (later loops correct earlier ones; repeated application can overwrite image-token information). [zoo]

## Added 30 Oct (sketchpad demo, E6)

- **Logit (output score).** The model's raw score for each possible next token before it is turned into a
  probability; the highest one is what it writes. Our margins and certificates are differences of logits.
- **Logit lens** (nostalgebraist 2020). Read an intermediate layer's state through the model's own final norm and
  output head, as if the model stopped there. On the demo page it shows at which layer the answer first wins (layer
  ~20 for both operations in E6); it is a view, not a guarantee, since later layers can still change the answer.
- **Class-mean push (activation steering)** (Turner et al. 2023, "activation addition"). Add the difference between
  the average internal state for answer B and for answer A to the stream at one layer, and see whether the model now
  writes B. If it does, that layer's direction causes the answer rather than merely correlating with it. E6: 80/80 at
  layer 20 for both addition and multiply steps (E5's multiplier: at most 23/80). [zoo]
- **Perplexity ratio.** Perplexity is how surprised a language model is by ordinary text (lower is better). We compare
  the adapter-on model with the base model on the same text; ×1.007 means language is essentially untouched.
- **LoRA (low-rank adapter)** (Hu et al. 2021). A small trainable add-on to a frozen model: each weight matrix W gets a
  thin product B·A added to it. Our "programs" are LoRA adapters; the base stays shared, and the adapter-on model is a
  second model at the cost of a few MB.
- **One-forward slots (E6, ours, 30 Oct).** Instead of writing a step's three answer tokens one after another (three
  model calls), the prompt ends in two placeholder tokens `??` and the model reads all three answers at `=` and the two
  placeholders in one call. Works because each answer depends only on the view, not on the earlier answers.
- **Causal (left-to-right) model.** Each position sees only earlier positions. Consequence we use: extra tokens added
  after the answer places cannot change those answers, so padding a short prompt at its end is exact, and the page
  can put every multiply step into one batch.
- **Batch.** Several independent inputs run through the model in one call. On the M4 a call costs ~100 ms fixed plus
  ~30 ms per row, so batching saves the fixed part only; beyond that the GPU is busy (compute bound).
- **Wave (overlapped passes, ours, 29 Oct).** Long multiplication has one pass per digit of b; a pass only needs the
  previous one to be two columns ahead, so the passes run staggered and all active passes take their step in one batch.
  Steps = 6(m − 1) + 2n + 4 instead of one pass after another.
- **Compute bound vs launch bound.** Launch bound: time goes to starting thousands of small GPU kernels, so bigger
  batches are nearly free. Compute bound: the arithmetic itself fills the GPU, so time grows with work. Our decoder is
  compute bound at ~10 tokens a row, so more speed needs fewer tokens or fewer steps.
- **WebGPU / fp16 / ONNX / transformers.js.** WebGPU: the browser's GPU programming interface. fp16: 16-bit numbers,
  half the memory of 32-bit with small rounding. ONNX: a file format for neural network graphs; ONNX Runtime Web runs
  it in the browser. transformers.js: Hugging Face's JavaScript library on top of it. The demo runs Qwen3.5-0.8B
  through all four; rounding on a given GPU is why every device re-checks the certificate's weakest rows.
- **Shipped certificate + spot check (ours, 29 Oct).** The full table check (all 1,795 views) is run once on a
  reference device and shipped with the model files; a visitor's device re-checks the weakest 10% of views (by margin)
  before trusting it, and can check all of them on request.
- **Modal.** A cloud service that rents GPUs by the second; our training jobs (e.g. E6, about $2 on an H100) run there.

## Round 5 (30 Oct, benchmark search)

- **NetHack (1987).** A text-grid dungeon game: one character descends ~50 randomly generated floors to fetch an amulet;
  you see only your line of sight, the rest is remembered; death is permanent; a win takes tens of thousands of moves.
  Hard for models because of partial observability (your memory is the map), hundreds of item/monster interactions with
  deadly consequences, and no partial credit for a run that dies late.
- **NLE, NetHack Learning Environment (Facebook AI, 2020).** The wrapper that lets a program play NetHack cheaply on a
  CPU, with the screen exposed as a character grid plus stats; the base of every NetHack benchmark.
- **BALROG (2024).** A suite that plays six games (NetHack, MiniHack, Crafter, BabyAI, TextWorld, Baba Is AI) through a
  language model and scores progress 0–100%; open leaderboard, reproduces entries. Frontier NetHack best 13.2%
  self-reported, 6.8% reproduced (Oct 2026); authors name "spatial awareness" and acting against known consequences.
- **MiniHack (2021).** Small hand-made NetHack levels (a maze, a corridor, a lava crossing) on the same engine; controlled
  difficulty with the same glyph grid, which is why it is the one-week pilot before the full game.
- **AutoAscend (2021).** A hand-written symbolic bot (rules, no learning) that won the NetHack Challenge and still beats
  every neural or language-model agent on the full game: the standing proof that the game is solvable by program.
- **AutoMem (2026).** A 32B model with a LoRA and a position-keyed grid-map memory on BALROG-NetHack, 1.85%: the
  same-protocol small-model entry a canvas-memory model would have to beat first.
- **AMA-Bench (ICML 2026).** An agent-memory benchmark: long interaction logs, questions that need exact recall of
  earlier state; GPT-5.2 at 0.72. Tests the memory without a game on top.

## Added 30 Oct (sketchpad release)

- **Hugging Face model repo + pinned revision.** A model repo on Hugging Face is a git repository for weights; every
  upload is a commit with a 40-hex id. The page loads `huggingface.co/<repo>/resolve/<commit>/<file>`, so what a visitor
  downloads can never change under the certificate; a new upload needs a new commit id in the code. Ours:
  `mohsenvand/sketchpad-0.8b-preview` (the browser program) and `mohsenvand/sketchpad-0.8b-runs` (every training run).
- **PEFT (Hugging Face, 2023).** The Python library that saves and loads adapters such as LoRA as small files on top of
  an unchanged base model; our runs repo is one PEFT adapter per folder, loadable on `Qwen/Qwen3.5-0.8B`.
- **Fast-forward (git).** Moving a branch pointer forward along commits it already lies on, with no merge commit; `main`
  took the sketchpad branch this way because that branch already contained everything on GitHub's `main`.
- **Class-mean push on the multiplier (ours, 30 Oct).** The push of the adder (Turner et al. 2023's activation steering
  with class means) applied to the multiply step: mean layer-20 state of the target product digit minus that of the
  true one, added at the `=` place of one row of the wave's batch; lands 40/40 on the M4, other rows untouched 20/20.
- **Progression metric (BALROG NetHack).** Per game, the larger of two table values: one for the deepest dungeon level
  reached, one for the highest experience level; averaged over 5 fixed games. The table is the chance a human at that
  level went on to win, so dungeon level 2 = 1.5%, 5 = 2.7%, 8 = 7.0%, 10 = 12.6%. The board is a depth ladder.
- **Dive (NetHack slang).** Descend as fast as possible instead of exploring and levelling; the strategy the ladder
  rewards. Speedrunners dive.
- **Elbereth.** A word you can engrave in the dust under you (`engrave`, `-`, type it); most monsters will not attack you
  in melee while you stand on it. The best cheap survival rule in the game.
- **Travel command.** NetHack's `_` key: pick a spot on the map (`>` jumps the cursor to the downstairs) and the game
  walks you there by its own shortest path. Turns "go to the stairs" into three keypresses once the stairs are seen.
- **Frontier / BFS / grassfire.** Frontier: a walkable cell next to an unexplored one; the next thing to explore.
  BFS (breadth-first search): shortest paths on a grid by expanding one ring at a time. Grassfire (Lee's algorithm,
  1961): the same thing as a wave that spreads one cell per tick by a local rule, which is why it fits a cellular
  canvas. [zoo]
- **Macro-action.** One high-level choice ("explore", "descend", "pray") executed by a program as several primitive
  keypresses. Lets a small model decide while a program moves.
- **vLLM.** A server that runs open models fast with batching; BALROG talks to it through the OpenAI-compatible API.
- **No-progress timeout (BALROG).** The game ends after 150 steps without progress; what counts as progress is a
  day-1 check (screen unchanged vs score unchanged), because exploring without fighting could trip it.
- **Dev/eval seed split.** Build and tune on games nobody scores (seeds 1000+), run the five scored games (seeds 42–46)
  once after freezing the code. The only honest way to use a benchmark whose test games are fixed.
- **Control (C0–C3).** The comparison runs that give a number its meaning: same model without the module (C0), module
  without the model (C1), module with random choices (C2), and the seed split (C3).

## Round 6 (30 Oct, SKETCHPAD3)

- **Knuth's Algorithm D.** The textbook long-division recipe: guess each quotient digit from the first two digits of the
  remainder and the first digit of the divisor, after scaling the divisor so its first digit is ≥ 5; the guess is off by
  at most 2. Turns the non-local "guess" into a 900-row lookup.
- **Trial subtraction.** Guess nothing: subtract the divisor until it would go negative, count the subtractions. Slower,
  but needs no new table.
- **Digit-by-digit square root.** The pen-and-paper root: bring down two digits at a time and find the largest x with
  (20P + x)·x ≤ remainder, P being the root so far. Each trial is one small multiply and one subtract.
- **Euclid's / Stein's gcd.** Euclid: replace the pair (a, b) by (b, a mod b) until b = 0. Stein (binary gcd): use only
  halving and subtraction; good when you have no divider.
- **Complement trick.** To subtract a bigger number from a smaller one, subtract anyway; if a borrow falls off the end,
  the true answer is minus the "ten-complement" of what you got. Lets one table handle negatives.
- **Coefficient grid.** A polynomial written as one column per power of x, the coefficient as a vertical number. Adding
  is column-wise addition; multiplying is long multiplication with the carry between columns switched off ("polynomials
  as numbers without carries", Kronecker substitution undone). [zoo]
- **Fraction-free elimination (Bareiss).** Gaussian elimination that keeps every intermediate number an integer, with one
  division per unknown at the end. Right for a page that has only integer tables.
- **Rational root theorem.** Any integer root of a polynomial with integer coefficients divides the constant term, so the
  candidates are a finite list to try.
- **Horner's rule.** Evaluate a polynomial by repeated "multiply by x, add the next coefficient": one multiply and one add
  per degree; here, a certified check of a guessed root.
- **Guess-then-prove.** The model proposes, a certified program checks; the proposal can only waste time, never change
  the answer. The one safe place for the LM's judgement.
- **Toolformer (2023).** Teach a model to call tools by inserting candidate calls into text and keeping those that lower
  the loss on what follows; the standard recipe for "decide when to use it" data. Here the tool is the model's own page.
- **Hard gate.** A 0/1 input that multiplies the adapter's contribution: at 0 the model is bit-for-bit the stock model,
  at 1 the certified machine. A soft (fractional) gate inside a certified step would break the finite certificate.
- **Carry-lookahead (Kogge–Stone).** Resolve all carries of an addition in log n parallel rounds instead of a chain. Not
  useful here: the decoder is compute bound, so fewer calls with the same number of rows saves nothing.
- **Base-100 cells.** Two digits per cell halves every step count at the price of a 20,000-row table (certified
  server-side once, spot-checked on device). A later lever.
- **Algebra by evaluation (interpolation).** Instead of moving symbols, compute the value of each typed side at a few
  numbers and solve for the coefficients those values force: a line from its values at 0 and 1, a quadratic from three
  points, one extra point to confirm the degree. Standard in computer algebra as "black-box" polynomials (Kaltofen and
  Trager, 1990). Here it means the sheet only ever does certified arithmetic, and the language half only copies the
  expression with x replaced by a number. [zoo]
- **Kronecker substitution (Kronecker, 1882).** Multiply polynomials by multiplying numbers: put x = 10^k with k large
  enough that coefficients cannot overlap, multiply the integers, and read the coefficients off in groups of k digits.
  (x + 2)^5 becomes 1002^5 = 1 010 040 080 080 032, i.e. 1, 10, 40, 80, 80, 32. On our sheet it reuses the certified
  multiplier with no new table. [zoo]
- **Cramer's rule.** Solve a small linear system with determinants: for 2×2, x = (e·d − b·f)/(a·d − b·c). Six products,
  three subtractions and two divisions on the sheet.
- **Work order.** Our name for the short list of one-operation lines (`t1 = 1234 - 567`) the model writes in its reply
  before the sheet runs them; the transcription the certificate does not cover, shown to the reader.
- **State copy cost.** The inside view needs every layer's state for the step it shows; copying all 25 layers for every
  batch row off the GPU cost a third to half of each step on the M4 (30 Oct). Leaving them on the GPU unless a panel reads
  them makes a step 0.065 s + 0.037 s per row instead of 0.15 s + 0.05 s.

## Added 30 Oct (SKETCHPAD3 prior-art gate, `research/audit/sketchpad3_gate/out.md`)

- **Prior-art gate verdicts.** OPEN: nothing close was found (which is not proof that nothing exists). NARROW: close work
  exists, and only a stated conjunction is still new. KILLED: already done. Each gate opens every cited arXiv abstract
  page on the day it runs.
- **Verification set** (Cai, Shin & Song 2017). Learned recursive programs are run on a finite set of inputs covering
  every base case and every reduction step. If all of them pass, the program is proved correct at every length. This is
  the direct ancestor of our per-view certificate; their pad was symbolic, and they called perceptual inputs infeasible. [zoo]
- **CAEF** (Lai et al. 2024). LLaMA-3.1-8B fine-tuned to step through +, −, ×, ÷ and comparisons as a text Turing-machine
  tape, with one LoRA per operator. Near 100% up to 100 digits, but neither exact nor certified. The closest
  pretrained-LM rival to the sheet.
- **Built-in calculator modules** (OccamLLM 2024; IGC 2025; Neural Comprehension 2023). A symbolic or hand-compiled
  arithmetic unit placed inside an LLM, which the hidden state triggers in the middle of generation: exact, with no tool
  call. These are prior art for "no external tool", but the module is not the model's own learned procedure.
- **Compiled transformer computers** (Loom 2026; Percepta transformer-vm 2026). Weights set by hand, not trained, so a
  transformer runs C or WebAssembly programs at one instruction per forward pass. They show execution in weights; they
  are not learned and not conversational.
- **Tool-integrated reasoning** (Toolformer 2023, ToRA 2023, ReTool 2025, ToolRL 2025). A model learns when to call an
  external interpreter in the middle of its reasoning and continues with the result. This is the standard form of our
  "decides to use the sheet", except that the tool is external.
- **Chain of Code / LMulator** (Li et al. 2023). The LM writes code, a real interpreter runs the lines it can, and the
  LM *emulates* the rest. It is the closest "model executes its own program" idea, and it is uncertified.
- **Visual chain of thought** (Visual Sketchpad 2024, Whiteboard-of-Thought 2024, MVoT 2025, Chain-of-Sketch 2024,
  MathCanvas 2025, Self-Imagine 2024). Models that draw or render intermediate images and reason over them. MathCanvas
  learns when to draw. None computes exactly or carries a certificate.
- **Extended Neural GPU** (Price, Zaremba & Sutskever 2016). A Neural GPU trained with a curriculum that learned decimal
  arithmetic generalising to long inputs, yet failed on symmetric inputs such as 0…02 × 0…02. It shows that "generalises"
  is not "certified".
- **DFST, differentiable finite-state transducer** (Papazov et al. 2025). A trainable finite-state machine that learns
  exact addition and multiplication from expert step traces and generalises to thousands of times the training length.
  It is trained from scratch, with no language and no image.
- **Seq2seq symbolic mathematics** (Lample & Charton 2019). A transformer trained to map an expression straight to its
  integral or ODE solution, beating Mathematica on their test sets. This is learned algebra with no exactness by
  construction, so it kills the broad form of "algebra without a CAS".
- **Minerva** (Lewkowycz et al. 2022). An LLM pretrained on general text, then further trained on technical text; it does algebra in
  chain-of-thought with no tool. It is the plain-LLM baseline for tool-free algebra, and it is not exact.
- **Gröbner basis.** A canonical generating set for a system of polynomial equations; computing one solves the system.
  Kera et al. (2023, 2025) train transformers for it. In the border-basis variant, the classical algorithm guarantees
  correctness and the network only speeds it up: the reverse of our split.
- **NTK, neural tangent kernel.** The limit in which a very wide network trains like a fixed kernel method. It makes
  training analysable: Back de Luca et al. (2025) use it to prove exact binary arithmetic with high probability. That is
  a proof about idealised training, not an audit of trained weights.
- **Recursive language models** (Zhang, Kraska & Khattab 2025). An LLM that calls itself on parts of a long prompt
  through a Python REPL. Prior art for a model invoking itself; the REPL is external and nothing is certified.
- **Learning without Forgetting (Li and Hoiem, 2016) / self-distillation.** While fine-tuning on a new skill, also train
  the model to match the old model's own outputs on old-style inputs, so the old behaviour is kept. Our E6 kept a KL term
  on plain text only, and plain-text perplexity stayed within 0.7% while chat instruction-following collapsed (30 Oct
  baseline); the fix is the same term on the base's chat answers. [zoo]
- **IFEval (2023).** A benchmark of instructions with checkable constraints ("answer in three bullet points", "no
  commas"); scores whether a chat model follows instructions, which perplexity does not measure.
- **Compile (here).** Turning a typed problem into the sheet's work order: the language half of the system, uncertified,
  shown on the page. Baseline on the untouched 0.8B: 25% for expressions (precedence errors), 73% for word problems.
- **Sutherland's Sketchpad (1963).** Ivan Sutherland's MIT thesis program, the first interactive drawing system (a light
  pen on a screen) and an ancestor of every graphical interface. Why it matters to us: "Sketchpad" is a crowded,
  famous name; as our product name it reads as an homage but is hard to search, so it stays a working title until the
  paper's title is fixed.
- **Finite differences and the Newton basis [zoo].** Subtract neighbouring values in a table of a polynomial's values,
  then subtract those differences, and so on; the last nonzero column gives the degree and the leading coefficient, and
  the columns convert to ordinary coefficients (Newton's 17th-century interpolation). Why it matters: the PROGRAM
  stream (30 Oct 2026) recovers a typed equation's coefficients this way from values the sheet computed, with only
  subtraction and exact division.
- **Bracket [zoo].** Two numbers where a continuous function has opposite signs, so a root lies between them (the
  intermediate value theorem). Why it matters: for an irrational root shown to 6 places, the sheet proves the two
  6-place bounds bracket it, a certified statement about a number it cannot write out exactly.
- **lora_gate (the gate, built 30 Oct 2026).** One input of the page's decoder graph, a float16 number that multiplies
  every adapter branch: 0 gives stock Qwen3.5-0.8B exactly (ONNX Runtime: bit-identical on 100 prompts), 1 gives the
  arithmetic program (all 1,795 certificate margins unchanged on the M4). Why it matters: the page's chat now runs at
  0, and it is the "progressive" switch of the one-model plan.
- **GSM8K (Cobbe et al., OpenAI, 2021).** 8,500 grade-school word problems that take two to eight steps of arithmetic,
  with worked solutions whose calculations are marked `<<48/2=24>>`. Why it matters to us: it tests whether the chat
  model still reasons in words between sheet calls; its training split's marked calculations become multi-step
  dialogues that call the sheet once per step.
- **MMLU (Hendrycks et al., 2021).** Multiple-choice questions over 57 school and professional subjects; the standard
  check of a model's general knowledge. Why it matters: our adapters cost it points (stock 0.476, E6 0.400), so it is a
  retention measure next to instruction-following.
- **PAL (Gao et al., 2023).** Program-aided language models: the model writes the reasoning as code and a computer runs
  the code. With ToRA (tool-integrated reasoning, 2023) it is the pattern the chat fine-tune copies: reasoning in words,
  every calculation done by the sheet.
- **ARC, the AI2 Reasoning Challenge (Clark et al., 2018).** Grade-school science multiple-choice questions. Not the
  ARC-AGI puzzle benchmark of the NetHack/ARC discussion. Why it matters: its training prompts guard general knowledge
  during the chat fine-tune (self-distillation toward stock's answers), without touching MMLU data.
- **KL divergence.** How far one probability distribution is from another; zero when they are equal. Why it matters: it
  is the loss term that pulls the adapted model's next-token distribution toward stock Qwen's during the chat fine-tune.
- **Precision and recall (of opening the sheet).** Precision: of the replies that opened the sheet, the share that
  needed it. Recall: of the problems that needed it, the share where it was opened. Why it matters: they are the bars
  for "the model decides by itself"; stock with a sheet prompt reaches 0.97 / 0.81, the adapters 1.00 / 0.99.
- **Held-out templates.** Question phrasings and word-problem scenarios never seen in training, so a score on them
  measures transfer of the format rather than memory. Why it matters: every chat bar is scored on them.
- **Stand-in (host sheet).** `sheet_ref.py`, exact fractions on the CPU in place of the certified sheet, used only to
  write training data and to score. Why it matters: chat scores say "stand-in", never "the sheet".
- **Rejection sampling (of training data).** Generate many candidates and keep only those that pass a check. In P4,
  stock's own GSM8K-train solutions were kept only when the final answer was right and every calculation reprinted
  exactly: 547 of 2,000.
- **Paired flip noise.** When two models answer the same prompts, only the prompts where they disagree carry
  information; with D disagreements the net count wobbles by about ±√D when the models are equally good. Why it matters:
  P4 and stock disagree on 116 IFEval prompts, so ±11 prompts (±2 points) is noise and the −2 bar is one deviation wide.
- **Routing (continual learning).** A small head reads the model's hidden state and decides which adapter, if any, is
  on for each token (X-LoRA 2024 is one; mixture-of-experts gates are another). Why it matters: it is the standard
  alternative to training one adapter that both chats and computes, and the option the chat seesaw points to.
- **On-policy vs off-policy training data.** Off-policy: the model trains on text someone else wrote (P1–P4 trained on
  stock's replies). On-policy: the model trains on text it samples itself, scored by a teacher or a reward. Why it
  matters: the chat seesaw is the forgetting that off-policy fine-tuning is known for.
- **RL's Razor (Shenfeld, Pari, Agrawal; MIT; arXiv 2509.04259, ICLR 2026)** [zoo]. Forgetting tracks how far the
  fine-tuned model moves from the base, measured as the KL on the new task. On-policy training (RL) finds the
  low-KL solutions; SFT on fixed labels can land far away. Why it matters: it is the reason CHAT round 2 trains
  on-policy.
- **On-policy distillation (Agarwal et al., GKD, ICLR 2024; Thinking Machines, Oct 2025)** [zoo]. The student samples
  replies, and the teacher scores every token: the loss is the reverse KL, the student's distribution measured
  against the teacher's. Thinking Machines restored IFEval after a fine-tune by using the model from before the
  fine-tune as the teacher. Why it matters: our teacher is free, the same weights at gate 0.
- **GRPO (Group Relative Policy Optimization; Shao et al., DeepSeekMath, 2024).** RL for language models: sample a
  group of replies, reward each, and push up the ones above the group's average, with no learned value model. Why it
  matters: it is CHAT round 2's third lever, with the stand-in as the reward and a KL penalty to gate 0.
- **Textbook algebra on the sheet (ALGEBRA round 3, chosen by Neo on 31 Oct 2026).** The runtime solves the way
  people write algebra: multiply out brackets, collect like terms, move terms across, use the formula, check by
  substitution. The model computes every new number. Why it matters: it replaces "algebra by evaluation" in the demo
  and the paper, because visitors did not recognise the evaluation method as algebra.
- **Binomial theorem and Pascal's rule.** (ax + b)ⁿ = Σ C(n, k)·aⁿ⁻ᵏ·bᵏ·xⁿ⁻ᵏ. Each C(n, k) is the sum of the two
  numbers above it in Pascal's triangle. Why it matters: it expands (x + 2)⁵ with small numbers the sheet handles
  quickly, in place of the 16-digit 1002⁵.
- **Synthetic division.** A three-row table that divides a polynomial by (x − r) using only multiplications and
  additions of its coefficients. Why it matters: it is how the factoring step shows its work.
- **Elimination (for systems of equations).** Multiply one equation and subtract it from another to remove a
  variable, then substitute back. Gaussian elimination is the same done systematically. Why it matters: it is how the
  sheet will show 2×2 and 3×3 systems, in place of Cramer's rule.

## Added 30 Oct (CALC: the gated E7, `research/sketch/CALC3.md`)

- **Knuth's refined guess (step D3 of Algorithm D).** Before multiplying the divisor by a guessed quotient digit q,
  check it against one more digit of each number (the divisor's second digit and the remainder's third): if
  q·v₂ > 10·r + u₃ (r what is left of the top two digits after q·v₁), lower q by one, and test again. With a two-digit
  divisor the guess is then exact; in base 10 it cuts too-high guesses in a square root from about 45% to about 7% (a
  simulation of T3's problems, CALC3.md). Why it matters to us: every too-high guess costs the calculator a wasted
  multiply-subtract pass and an add-back, and those passes are the square root's 12-second tail.
- **WebGPU device loss.** The browser can take the GPU away from a page (driver reset, background tab, memory pressure);
  every later GPU call then fails, and ONNX Runtime cannot make a new device in the same worker. Why it matters to us:
  it stopped T3 three times in a hidden pane; the page now starts a fresh worker, reloads the program from the browser's
  cache and redoes the steps in flight, which is exact because a step depends only on the views it reads.
- **Layout ratchet (sketchpad demo, 31 Oct 2026).** From the moment a run starts until the next run starts, a
  panel's height can only grow; it keeps its largest height so far as its minimum. Why it matters: Neo found the
  Algebra tab jumping as the digit work changed size. With the ratchet, and the digit work taken out of the layout
  flow, nothing shrinks or moves up during a run.
- **Layout probe (`scripts/layout-probe.js` in NeoVand/sketchpad).** A console script that logs every element that
  gets shorter or moves up during a run. Why it matters: it is the test for the rule above. On 31 Oct it logged zero
  entries on every preset at 1440 and 375 px.

## Added 31 Oct (the Sketchpad paper, `NeoVand/sketchpad` branch `paper`)

- **Theorem P, sheet form [zoo].** If every step of a machine reads only a view drawn from a finite set and paints its
  answer, the machine is exact on every run of every length if and only if its answer is right on every view a
  reference run meets. Classical in essence (Moore 1956; Cai et al. 2017; Lewandowski et al. 2026); ours is the sheet
  instance and its Lean statement (`paper/lean/Sheet.lean`, 31 Oct 2026). Why: it turns infinitely many runs into
  2,446 checks.
- **Pinned-sheet policy.** Each forward pass sees the step's prompt and its three-cell view and nothing else; the sheet
  is the only state between steps. Why: it makes the model's answer a function of the view, the hypothesis Theorem P
  needs.
- **Moore's gedanken-experiments (Moore, 1956).** The founding paper on testing finite-state machines from outside: no
  finite experiment identifies a machine unless its number of states is bounded. Why: the classical form of our
  no-finite-test theorem.
- **Conformance testing / the W-method (Chow, 1978).** Testing that an implemented state machine matches its
  specification, with a test suite that is complete given a bound on the number of states. Why: the field our
  certificate belongs to; the sheet removes the need for a state bound because every step reads only a view.
- **Transfer across code paths (Corollary P2).** If a run's logits differ from the certified ones by at most τ, and every
  certified margin exceeds 2τ, the run is exact. Why: it says when a certificate measured on one device, precision or
  batch shape carries to another; a 4-bit decoder broke it (margins moved by about 18), the 16-bit decoder keeps it.
- **Code path.** The exact computation that produces the logits: device, numerical precision, kernel and batch shape.
  Why: a certificate holds for the path it was measured on.
- **Vieta's formulas (Viète, 16th century).** The two roots of ax² + bx + c sum to −b/a and multiply to c/a. Why: the
  algebra checks irrational roots like 3 ± √5 with these identities in integer arithmetic, with no decimals.
- **Residual stream.** The running sum of every layer's output in a transformer, read by the next layer. Why: the logit
  lens reads it, and the class-mean push adds to it.
- **Decision depth.** The first depth (number of layers applied) after which the final answer stays the top token
  under the logit lens. Why: E7 decides at median depth 19 (addition) and 20 (multiplier).
- **Gated DeltaNet (Yang, Kautz and Hatamizadeh, 2024).** A linear-attention layer with a fixed-size running state,
  updated by a gated delta rule; 18 of Qwen3.5-0.8B's 24 layers. Why: it is causal, so tokens after the answer place
  cannot change the answer, which lets every step be padded to one batch.
- **FP8.** Eight-bit floating point for weights; halves the memory of 16-bit. Why: the 27B baseline ran as the FP8
  release because the 16-bit model held only 8 long replies on one H100.

## Round 7 (31 Oct, Neo's integration idea)

- **Knowledge disintegration (Neo's phrase).** A model knows field A and field B separately and never notices that a
  structure in A is the same as one in B. The measurable version is the two-hop curse below. It matters because every
  dead end of this project was a known idea under another name that nobody in the loop connected.
- **Two-hop curse** (Balesni, Korbak, Evans, 2024; v4 Nov 2025, arXiv 2411.16353). Fine-tuned models that learn
  "A→B" and "B→C" in separate documents answer "A→C" at chance without chain of thought, despite perfect recall of each
  fact; composition works when the facts co-occur in one document or one prompt, or when one fact came from
  pretraining. Why it matters: it is the laboratory form of disintegration, and it predicts that training data for
  integration must put both halves and the bridge in the same text.
- **Structure-mapping theory** (Gentner, 1983). An analogy is a mapping of relations, not of surface attributes: the
  atom is like the solar system because "orbits" maps to "orbits", not because both are round. Why it matters: a
  cross-field connection worth training on must name the correspondences relation by relation; metaphors do not count.
- **Rosetta Stone paper** (Baez & Stay, 2009, "Physics, Topology, Logic and Computation"). One table that identifies
  the same structure (a monoidal category) in four fields, term by term. Why it matters: it is the gold-standard shape
  of an integrative statement, and the shape our data generator should force. `[zoo]`
- **Literature-based discovery, Swanson's ABC model** (Swanson, 1986). Literature 1 links A to B, literature 2 links B
  to C, nobody has written A–C; Swanson found fish oil for Raynaud's syndrome this way. Why it matters: a 40-year-old
  field with its own tools (Arrowsmith) for exactly the connections Neo wants to distil; the model-internal version of
  the gap is the two-hop curse. `[zoo]`
- **Consilience** (Whewell, 1840; E. O. Wilson, 1998). The jumping-together of knowledge from separate fields into one
  explanation. Why it matters: the oldest name for the goal, and a usable project name.
- **SCAMPER** (Eberle, 1971). A brainstorming checklist: Substitute, Combine, Adapt, Modify, Put to other use,
  Eliminate, Reverse. Why it matters: Neo proposed it as a hidden prompt generator; it produces surface variations, so
  it needs structure mapping on top to yield deep connections.
- **IsoSci** (arXiv 2607.01431, July 2026). A benchmark of science-problem pairs with the same logical structure and
  different domain knowledge; 91.3% of "reasoning mode" gains were knowledge-dependent, not structure-invariant. Why it
  matters: the closest existing benchmark to "same structure, different field"; it tests solving, not recognising the
  identity, which is the gap we would fill.
- **SCAR** (EMNLP 2023), **IDRBench** (arXiv 2507.15736, July 2025), **CHIMERA**, **Idea-Catalyst** (arXiv 2603.12226,
  2026). Respectively: 400 scientific analogies across 13 fields posed as structure abduction; an interdisciplinary
  research benchmark (paper identification, idea integration, recommendation) on which ten frontier models were
  "rudimentary"; a dataset of inspiration relations between source and target domains in papers; a framework that
  generates interdisciplinary idea fragments from external source domains. Why they matter: the field Neo's idea
  belongs to already has datasets and a benchmark that says frontier is weak; we build on them, not beside them.
- **CreativityNeuro** (arXiv 2607.01433, ICML 2026). Data-free steering of model weights that raises Divergent
  Association Task scores by up to 14 human percentile points and reduces mode collapse; activation steering matched it
  on that task but did not transfer to others. Why it matters: "creativity steering" is taken for divergent word
  association; steering for structure-level integration across fields is not shown, and this paper's method is the
  template for our nudge.
- **Mode collapse / typicality bias; verbalized sampling** (Zhang et al., Oct 2025). Preference tuning favours typical
  answers, so aligned models lose diversity; asking for a distribution of answers with probabilities restores much of
  it at inference time. Why it matters: a frontier model asked for cross-field ideas gives its mode; the prompts that
  collect our data must defeat this.
- **Unknown-fact fine-tuning** (Gekhman et al., 2024). Fine-tuning on facts the model does not already hold is learned
  slowly and raises hallucination. Why it matters: Neo's "low-likelihood sentences" are exactly this regime; the safe
  version trains the bridge between facts the model already has, not new facts.
- **Complementary learning systems; sleep and insight** (McClelland, McNaughton & O'Reilly, 1995; Wagner et al.,
  Nature 2004). The brain stores episodes fast in the hippocampus and integrates them slowly into cortex during replay
  in sleep; a night's sleep doubled the rate of insight on a hidden-rule task. Why it matters: the brain-like framing
  of integration training is interleaved replay of remote pairs; the model has never slept. `[zoo]`
- **Atypical combinations** (Uzzi, Mukherjee, Stringer & Jones, Science 2013). The highest-impact papers combine
  mostly conventional prior work with a tail of unusual combinations. Why it matters: a quantitative prior on which
  connections are worth generating: mostly-conventional with one remote jump.
- **Disguise-and-recover (ours, 31 Oct).** Take a known cross-field identity, re-describe one half in alien vocabulary
  with renamed symbols, and ask the model to name the other half and transfer one theorem; the identity is known, so
  the reward is checkable. Why it matters: a verifiable self-supervised objective for integration with no frontier
  distillation, and a held-out test of whether the skill transfers to unseen identities. `[zoo]`
- **Bridge surprisal (ours, 31 Oct).** The model's surprise at the token where the second field is named in a true
  connection statement. Why it matters: a one-number measure of disintegration per statement, and of whether training
  or steering lowered it on held-out bridges. `[zoo]`
- **Nerode for concepts (ours, 31 Oct).** Two descriptions are the same concept if they license the same inferences;
  train representations of such pairs to coincide, the way our metric loss pulled together states of one automaton.
  Why it matters: the project's quotient theory, reused one level up, as a candidate objective for integration. `[zoo]`
- **ALIAS (ours, 31 Oct; name provisional).** The benchmark in CONSILIENCE.md: a documented cross-field identity, one
  half disguised (relations kept, every surface cue of the field removed), the model names the other half and judges a
  true versus a false theorem rendered in the disguised vocabulary. Why it matters: it turns recall of two facts into
  recognition of one structure, with a checkable answer. `[zoo]`
- **Faithfulness check, leak check (ours).** Two automatic tests of a disguise: a second model confirms the relational
  content is unchanged; no token from the source field's stoplist survives. Why: a leaky disguise measures recall, a
  distorted one measures nothing.
- **Obscurity stratum (ours).** Famous / known / obscure, by how many open models state the identity unprompted. Why:
  recovering only famous identities is memorised sentences, not integrated structure.
- **SCAR** (Yuan, Chen et al., arXiv 2305.12660, 2023). 400 scientific analogies across 13 fields; the model maps
  concepts between two *named* systems; GPT-4 58.5% system accuracy (64.0% with background and one shot), humans 83.4%.
  Why it matters: the nearest benchmark; ALIAS removes one system's name and asks for it.
- **AnalogyKB** (Yuan, Chen et al., ACL 2024, arXiv 2305.05994). A million analogies derived from knowledge graphs;
  fine-tuning on them improved analogy recognition and generation. Why it matters: precedent that analogy skill is
  trainable; it has no disguise, no theorems and no checkable reward.
- **Counterfactual analogy tasks** (Lewis & Mitchell, 2024). Analogy problems rewritten in unfamiliar alphabets or
  symbol sets; humans held steady, GPT models fell sharply (contested by Webb et al. 2024). Why it matters: our disguise
  is their perturbation applied to real scientific knowledge.
- **GSM-Symbolic** (Mirzadeh et al., arXiv 2410.05229, 2024). Templated GSM8K variants; renaming people moved scores
  0.3–9 points, changing numbers or adding clauses moved them far more. Why it matters: renaming alone is a shallow
  disguise; ALIAS needs the deep one.
- **RLSVR** (arXiv 2607.23802, 2026). Reinforcement learning with self-verifiable rewards: wrap an open-ended task in a
  game ("Who is the spy?") whose outcome is checkable, then train with self-play. Why it matters: the disguise is our
  game; the identity being known is what makes the reward verifiable.
- **Wilson interval.** The standard confidence interval for a proportion; about ±10 points at 100 items, ±5.5 at 300.
  Why: it sets which differences on ALIAS are claims.

## Added 31 Oct (the paper's equations and proofs appendix)

- **Token form (of the sheet theorems).** The Lean version of a theorem in which the machine's state is a single token
  and each step reads one state token and one event token after a fixed prompt (`Pinned.lean`). The sheet form
  (`Sheet.lean`) lets the state be a whole configuration that the model sees only through a view. Why it matters:
  since 31 Oct evening Theorems 1, 3b and 4 are all proved in Lean in both forms (`sheet_certified`,
  `sheet_error_bound`, `sheet_exact_of_close`); before that, 3b and 4 existed only in the token form.
- **Execution path (Theorem 4).** The computation that actually runs at deployment (device, kernel, batch, cache),
  whose logits at step t may differ from the certified ones by up to τ and may change from step to step. Why: Theorem 4
  says the run is still exact if every certified margin exceeds 2τ; the Lean sheet form is `sheet_exact_of_close`.
- **Lean `alias` (`paper/lean/Paper.lean`).** A second name for an already-proved Lean theorem, with the same statement
  and proof. Why: the paper cites `Sketchpad.Paper.theorem1_sheet`, `lemma3` and so on under its own numbering, while
  the underlying names (such as `theorem8a_counterexample`) keep their history.
- **Recorded / Live switch (sketchpad demo, 31 Oct 2026).** Every tab opens by replaying a real run recorded on an
  Apple M4 with the published model. Its outputs, timings and inside readouts are stored with their provenance (device,
  date, model and certificate revisions, file hashes). After the visitor loads the model, Live becomes the default and
  the visitor's own run replaces the recording in place. Why it matters: it answers Neo's objection that empty
  placeholders made the demo look broken, and no number is presented as computed when it isn't.

## Added 31 Oct (arXiv submission of the Sketchpad paper)

- **pdfLaTeX vs XeLaTeX (and tectonic, fontspec).** Two engines that turn a `.tex` file into a PDF. pdfLaTeX is the
  classic one and reads 8-bit text, so every special character (−, ×, ö) must be spelled as a LaTeX command; XeLaTeX
  reads Unicode directly and loads system fonts through the `fontspec` package. tectonic is a self-contained XeLaTeX
  build we use locally. Why it matters: arXiv compiles with pdfLaTeX from TeX Live, so the paper needs a second build
  (`node paper/build-tex.ts --arxiv`) that writes a plain-ASCII `main.tex` with no fontspec.
- **`.bbl` / `thebibliography`.** A `.bbl` is the bibliography file BibTeX writes for LaTeX to read; `thebibliography`
  is the same list written inline in the `.tex`. Why it matters: arXiv does not run BibTeX for you reliably; our
  generator already writes the references inline, so the upload needs no `.bbl`.
- **Overfull box.** LaTeX's warning that a line or block sticks out past the margin by some number of points (1 pt ≈
  0.35 mm). Why it matters: the arXiv build is accepted only with none over 10 pt.
- **arXiv primary category and cross-list.** Every arXiv paper has one home category (where it is announced and
  moderated, e.g. cs.LG, machine learning) and may be cross-listed to a few others (cs.CL, computation and language;
  cs.LO, logic in computer science) so it also appears in their daily listings. Why it matters: it decides who sees the
  Sketchpad paper on the day it appears.
- **arXiv licence (CC BY 4.0 vs arXiv non-exclusive).** The licence chosen at submission sets what others may do with the
  PDF. CC BY 4.0 lets anyone copy and redistribute with attribution; the default arXiv licence lets only arXiv
  distribute it. It cannot later be made more restrictive. Why it matters: Neo chooses it at upload; journals generally
  accept preprints under either, but the target venue's policy should be checked.
- **arXiv endorsement.** A first-time submitter to a category may need an existing arXiv author in that category to
  vouch for them before the paper is accepted for moderation. Why it matters: if Neo's account has not posted to cs.LG,
  the upload may pause for an endorser.
- **Activated LoRA (aLoRA)** (Greenewald et al., IBM, arXiv 2504.12397, 2025). A LoRA adapter applied only to tokens
  after the point where it is invoked, so the base model's cache for earlier tokens is reused unchanged. Why it matters:
  the closest prior mechanism to switching the Sketchpad gate on within a reply; the paper should cite it. [zoo]
- **Modality-gated deep adapters** (Tonmoy et al., arXiv 2609.26182, Aug 2026). Adapter packs that run only while one
  modality (audio, thermal) is being encoded; every other input passes through the frozen base model bit for bit,
  checked by exact-equality tests. Why it matters: the same kind of exact-preservation claim as the Sketchpad gate.
- **MDL network** (Lan, Geyer, Chemla, Katzir, TACL 2022). A small network trained to minimise its minimum description
  length (size of the network plus the cost of its errors), simple enough to be proved correct by hand, e.g. exact
  addition for inputs of any length. Why it matters: prior proved-exact learned arithmetic; it weakens the paper's
  phrase "rather than estimating it".
- **Compact proof / brute-force proof** (Gross et al., NeurIPS 2024). A computer-checked proof of a trained network's
  accuracy; the brute-force kind runs every possible input. Why it matters: verification of a trained transformer by
  enumeration, but at one fixed input size, where Sketchpad's finite view set covers every length. [zoo]
- **Neural Programmer-Interpreter (NPI)** (Reed & de Freitas, ICLR 2016). A recurrent network that learns programs such
  as grade-school addition, one step at a time on a scratch pad read through movable pointers. Why it matters: the
  direct ancestor of the sheet machine, and the setting Cai et al. 2017 verified; the paper does not yet cite it.
- **Few-shot (in-context) prompting** (Brown et al. 2020, GPT-3). Put k solved examples in the prompt before the
  question, with no weight change, and let the model copy the pattern; "8-shot" means eight examples. Why it matters:
  the reviewer's control for Sketchpad (31 Oct) asks whether the unadapted base model can already do the step tables
  from examples alone; if it could, the adapter would not be needed.
- **Teacher forcing.** Score a multi-token answer by feeding the model the *correct* earlier tokens and reading its
  prediction for the next one, instead of feeding back its own guesses. If every teacher-forced margin is positive,
  greedy decoding writes exactly the right answer. Why it matters: E4/E5 were certified this way; E6/E7 read all three
  answers at once at the `=??` slots, and the base-model control reports both readings.
- **Batch perturbation (τ_batch).** How far a view's logits move when the GPU computes it in a batch with other views
  instead of alone; fp16 shaders pick different tilings and summation orders for different batch shapes. Why it
  matters: the Sketchpad certificate is measured one view at a time, but inference batches up to 32, so Theorem 4 needs
  this movement to stay below half the smallest margin. The deep review (31 Oct 2026) asked for it; measured on the M4.
- **Fisher discriminant directions (shrinkage LDA).** The directions in a state space along which class means are far
  apart relative to the spread inside each class; "shrinkage" blends the within-class covariance with the identity so
  it can be inverted in 1,024 dimensions. Why it matters: Fig. 6b of the Sketchpad paper projects final-layer states on
  three such directions, and its 95.5% nearest-centre share is measured in that 3-D slice, not the full space.
- **Spot check of a polynomial identity.** Checking that two polynomials agree at a few chosen points. Two different
  polynomials of degree D can agree at up to D points, so a spot check is not a proof unless it uses D + 1 points (or one
  point beyond a coefficient bound). Why it matters: the algebra checks expansions at x = 1 by default, which catches any
  single wrong coefficient but not errors that cancel there; the paper now says so.
- **Square-free part / reduced radical.** Writing √D as s√m with m having no square factor (e.g. √12 = 2√3). Why it
  matters: the algebra reduces radicals by trial division with primes up to 47, so it is fully reduced only for
  discriminants below 53² = 2,809; Vieta's check verifies the values, not the reduced form.
- **Vendoring.** Copying a dependency's source files into one's own repository so it builds without the other
  repository. Why it matters: the Sketchpad Lean proofs lived on a branch of the polyformer repository (`lean-p`); they are now in the
  Sketchpad repository's `paper/lean/`, so a reader can build them.
- **Nature article format (main text, Methods, Extended Data).** A short main text (untitled introduction, results
  sections with declarative headings, a Discussion), then Methods with the procedures and related work, then Extended
  Data figures and tables. Why it matters: the Sketchpad paper uses this shape; AlphaGeometry, FunSearch, AlphaDev and
  AlphaProof all put related work in Methods and end the main text with a Discussion, not a Limitations list
  (STYLE.md, 31 Oct 2026).
- **AlphaGeometry** (Trinh et al., Nature 2024). A language model proposes auxiliary constructions and a symbolic
  engine does the deduction; trained on 100 million synthetic proofs, it solved 25 of 30 olympiad geometry problems.
  Why it matters: a model of how to write a neuro-symbolic Nature paper, scope stated once in the approach paragraph.
- **FunSearch** (Romera-Paredes et al., Nature 2023). An LLM proposes programs and an automatic evaluator scores them in
  an evolutionary loop; found new cap-set constructions. Why it matters: the evaluator guards against confabulation, the
  same division of labour as our runtime and certified steps; its paper states scope as conditions in the Discussion.
- **AlphaDev** (Mankowitz et al., Nature 2023). Reinforcement learning over assembly instructions found shorter sorting
  routines, merged into LLVM's libc++. Why it matters: correctness is built into the problem (the reward), so the paper
  states it as a property, not as a list of checks.
- **AlphaProof** (Hubert et al., Nature 2025). AlphaZero-style RL that finds Lean proofs; with AlphaGeometry 2 it scored
  silver-medal level at IMO 2024. Why it matters: caveats (multi-day compute) appear as clauses inside result sentences.
- **Abacus embeddings** (McLeish et al., NeurIPS 2024). A positional embedding that gives each digit its place within
  its number; transformers trained on 20-digit addition reach about 99% on 100-digit. Why it matters: the strongest
  sampled-accuracy route to long arithmetic, with no guarantee for unseen inputs.
- **RASP-L conjecture** (Zhou et al., ICLR 2024). Transformers tend to length-generalise on a task when a short program
  in RASP-L, a restricted language of transformer-like operations, solves it at every length. Why it matters: an
  explanation of when sampled length generalisation works, where we certify instead.
- **Position coupling** (Cho et al. 2024, 2025). Giving the same position ID to tokens that play the same role, such as
  digits of equal significance, so a transformer extrapolates arithmetic to longer inputs. Why it matters: another
  sampled-accuracy route; its 2025 scratchpad makes each step read a constant number of tokens, close to our view.
- **PENCIL** (Yang et al. 2025). Chain of thought with a reduction rule that erases finished sub-computations from the
  context, keeping memory proportional to space, not time. Why it matters: a context discipline like our pinned policy,
  but without a finite certificate. [zoo]
- **Inductive scratchpad / globality barrier** (Abbe et al., NeurIPS 2024). Targets that need many tokens at once are
  hard to learn; a scratchpad whose each step depends only on the previous state and the input generalises in length.
  Why it matters: the paper cites it as resembling our pinned context discipline. [zoo]
- **ICML / NeurIPS main track.** The two largest machine-learning conferences. Each takes 8–9-page papers once a year,
  reviewed by 3–4 anonymous researchers; ICML's deadline is usually late January and NeurIPS's mid-May. Why it
  matters: the natural home for the Sketchpad paper's mix of theorem, system and measurement, and the audience Neo
  wants to reach.
- **Nature Machine Intelligence (NMI).** The Nature group's monthly machine-learning journal. It uses the same format
  as our draft (main text, Methods, Extended Data), and an editor screens each paper before review. Why it matters:
  it is the journal option that needs the least reformatting, but it is slower than a conference.
- **TMLR (Transactions on Machine Learning Research).** A rolling-submission ML journal that reviews for correctness
  and clarity rather than for novelty or impact, and usually decides in 2–4 months. Why it matters: a dependable
  fallback that does not depend on a conference cycle.
- **Desk rejection.** An editor or programme chair declines a paper without sending it to reviewers, for scope, format
  or perceived significance. Why it matters: it is the main risk at Nature-family journals.
- **Lag system.** A string-rewriting machine: it reads the first few symbols of a string, drops one and appends a
  fixed word chosen by a rule table. Some tables (U(15,2)) are universal, so simulating one simulates any computer.
  Why it matters: Schuurmans 2024 and Lewandowski 2026 certify a language model by checking every rule of such a
  table with the string kept outside the model, so their policy is pinned like Sketchpad's and their extension to all
  inputs is a theorem. The honest distinction from Sketchpad is the certificate's quality (logit margins in the
  deployment numerics, open weights bound by hash, recomputable on the device) and a trained small model, not the
  logic; their claim is universal computation, ours arithmetic.
- **Lookup-table objection.** The reviewer's point that a network certified on a finite set of views does only what a
  table of those views would do, and more slowly. Why it matters: it is the first objection an editor raises to
  Sketchpad; the answer must be that the same weights are the chat model and the guarantee is on the trained
  network, not that the arithmetic itself is useful.
- **Perspective (Nature journals).** An article type for argued viewpoints rather than new results, peer reviewed but
  judged on the argument. Why it matters: the NMI 2025 Ito et al. paper on algorithmic generalisation is a
  Perspective, so it shows NMI's interest in the topic without setting the bar for an Article.
- **Nature Communications (NC).** Springer Nature's broad open-access journal, one tier below Nature and the Nature
  research journals; it accepts specialist advances when complete and reproducible (acceptance rate about 8–10%).
  Why it matters: the venue with the better odds for Sketchpad as it stands (about 20% overall by Fable's estimate),
  against about 7–8% at Nature Machine Intelligence.
- **DNAR (Discrete Neural Algorithmic Reasoning).** Rodionov and Prokhorenkova, ICML 2025. A neural reasoner forced to
  pass through finite predefined states, trained on state transitions, so that checking every transition proves the
  learned algorithm correct "for any test data" (sorting, BFS, shortest paths). Why it matters: it is Sketchpad's
  Theorem 1 applied to CLRS algorithms on a from-scratch network, so it pre-empts a "second certified family" upgrade
  and must be cited in the paper with the distinction stated (pretrained model, floating-point device certificate,
  necessity theorem, composition).
- **Retrieval-augmented generation (RAG).** A language model answers from passages fetched out of a document store by
  a separate search step, usually nearest neighbours in an embedding space. Why it matters: "certify retrieval" can
  mean certifying that search step, the model's use of the fetched text, or recall from its own weights. Each has a
  different answer (Neo's question, 31 Oct 2026).
- **Needle in a haystack.** A test that hides one fact (the needle) in a long context and asks the model to retrieve
  it, repeated at growing lengths. Why it matters: models degrade as the context grows. The mechanism is the one in
  Sketchpad's Theorem 2: attention spread over more tokens dilutes the needle's signal.
- **Attention dilution.** Softmax attention normalises over all tokens. A fixed score gap between the right key and n
  wrong keys therefore gives the right key a weight that shrinks roughly like 1/n. Exact retrieval at length n needs a
  gap that grows like log n. Why it matters: it is why finite testing cannot certify full-attention retrieval at all
  lengths, and why fixes such as scalable softmax scale the scores with log n. [zoo]
- **Scalable softmax (SSMax)** (Nakanishi, 2025). Multiplies attention scores by s·log n, where n is the context
  length, so attention stays focused as contexts grow. Why it matters: the standard architectural answer to dilution;
  it can be analysed per head but does not by itself certify a trained deep model.
- **Certifying algorithm** (McConnell, Mehlhorn, Näher and Schweitzer, 2011). An algorithm that returns, with its
  answer, a witness that a simple checker can verify, e.g. the position of a found key, or a factorisation alongside
  "not prime". Why it matters: when checking is cheap, a witness plus a checker gives a guarantee per answer without
  certifying the model at all. This is the main competitor to certifying a neural retriever. [zoo]
- **Test-set reuse (adaptive overfitting).** Trying several candidates on the same benchmark items and keeping the
  best inflates its score, because part of its lead is luck on those items. The fix is a fresh, untouched set of items
  for the chosen candidate. Why it matters: the Sketchpad dialogue adapter was the fifth candidate scored on the same
  250 GSM8K and 500 MMLU items. Scoring it on the 1,069 unused GSM8K test problems and unused MMLU questions (about $5)
  removes the objection.
- **Backdoor / sleeper agent** (Hubinger et al. 2024). A hidden behaviour planted in a model's weights that appears
  only on a secret trigger input, e.g. a wrong digit whenever an operand contains "1337". Why it matters: a
  third-party fine-tune can carry one, and sampled testing almost never hits the trigger.
- **Undetectable backdoor** (Goldwasser, Kim, Vaikuntanathan and Zamir, 2022). A proof that a model trainer can plant
  a backdoor that no efficient observer can detect without the secret key. Why it matters: general audits of weights
  cannot rule out hidden behaviour. A skill whose inputs are confined to a finite enumerated set (Sketchpad's views)
  can be audited completely, which is round 7's candidate A. [zoo]
- **Coverage testing.** Testing until every case of a finite case set has been exercised at least once. Why it
  matters: for arithmetic, random problems visit all 2,446 views quickly, so a critic can say the certificate is
  coverage plus a receipt. The answer is that the pinned design is what makes coverage finite and exhaustive.
- **Exact-or-refuse (certified abstention).** A model certified to output either the right answer or "refuse" on
  every input in a stated region, never a wrong answer. Why it matters: it is how a certificate could extend from
  exact rendered glyphs to real scans (round 7's candidate B). Related: randomized smoothing (Cohen et al. 2019) and
  selective classification. [zoo]
- **BUGGY / DEBUGGY and repair theory** (Brown & Burton 1978; Burton 1982; Brown & VanLehn 1980). Children who get
  column subtraction wrong usually follow a consistent wrong procedure (a "bug"), e.g. always subtracting the smaller
  digit from the larger and never borrowing. BUGGY catalogued about 100 such bugs as executable procedures, and
  repair theory explains how they arise when a learner patches a gap in the procedure. Why it matters: each bug is a
  wrong table in Sketchpad's sense, so diagnosing a child is identifying which table produced their worksheet. This
  is the "surprise pivot" proposed on 1 Nov 2026. [zoo]
- **Distinguishing experiment** (Moore 1956). An input sequence chosen so that two candidate machines produce
  different outputs on it. Adaptive testing picks the next input from the answers so far. Why it matters: choosing the
  next practice problem that best separates a child's candidate bugs is exactly this. Round 6's converged tool, the
  "discriminating probe", is the same idea.
- **ScratchMath (2026), MathCog (2025), TeachArena (2026).** Recent benchmarks for AI diagnosis of students'
  handwritten math work and teaching tasks. They report that multimodal LLMs mostly solve the problem instead of
  diagnosing the student, and are weak at reading handwriting and following multi-step procedures. TeachArena requires
  bug rules to be stated as executable procedures. Why it matters: they name the gap the tutor pivot would fill, and
  they are its benchmarks.

## Round 8 (1 Nov, Nerode and higher-order attention)

- **Nerode congruence (Nerode, 1958).** Two input histories are equivalent when every possible continuation leads both
  to the same output. The equivalence classes are the states of the smallest automaton that recognises the language.
  Why it matters: a network that is exact on a task must hold at least these classes, and MECHANISM found exactly them
  (960 of 960). [zoo]
- **Bisimulation (Nerode) metric.** A distance between histories: the gap between their current outputs plus a
  discount γ times the expected distance after one shared next input. Distance zero recovers the Nerode classes.
  Why it matters: our Nerode metric loss L_M trains it, and on its own made a recurrence exact at 1,024 steps.
- **Myhill congruence and the syntactic monoid (Myhill, 1957).** A two-sided version of Nerode's: two middle segments
  are equivalent when every left context and every right context around them gives the same output. The classes form
  a monoid (segments compose), equal to the transition monoid of the minimal automaton. Why it matters: it is a 3-way
  relation (left, middle, right), the kind a cubic attention logit can express and a pairwise one cannot. This is
  round 8's conjecture O1. [zoo]
- **Hankel matrix and spectral learning of weighted automata (Fliess, 1974; Hsu, Kakade and Zhang, 2009; Balle et al.,
  2014).** Arrange a sequence function in a table with rows = pasts and columns = futures. The table's rank is the
  smallest state dimension of a linear (weighted) automaton that computes it, and an SVD of the table learns one.
  Why it matters: it is Nerode's theorem in linear algebra, and our ~20-dimensional affine state code is such an
  object. [zoo]
- **Angluin's L\* (1987).** An algorithm that learns the minimal automaton by asking membership questions ("is this
  string in?") and equivalence questions ("is this the machine?"). It builds the Nerode classes from a table of
  prefixes and suffixes. Why it matters: it is the standard way to find Nerode classes actively, and round 8 drew it.
- **Topological entropy (symbolic dynamics).** The growth rate of the number of distinct length-n words a system can
  produce. For a finite automaton it is the log of the largest eigenvalue of its transition matrix. Why it matters: it
  measures how fast the number of distinguishable futures grows, which bounds how much state a model needs.
- **Bundle adjustment (photogrammetry/SLAM).** Jointly re-estimating every camera pose and 3-D point so that all
  reprojection errors are small at once. It exploits a sparse block structure. Why it matters: drawn in round 8, as a
  model of global consistency repairs.
- **OODA loop (Boyd, 1970s–80s).** Observe, orient, decide, act: a doctrine for winning by cycling through decisions
  faster than an opponent. Why it matters: drawn in round 8, as a model of state update under time pressure.
- **Loci in sign languages.** Signers assign each discourse referent to a location in space. Later pronouns and verbs
  point at that location to refer back. Why it matters: drawn in round 8. It is a natural binding-by-address system
  in human language.
- **Algebraic attacks, linearisation and XL (cryptanalysis; Courtois et al., 2000).** Write a cipher as a system of
  polynomial equations. Then either replace every monomial by a fresh variable and solve the resulting linear system
  (linearisation; XL first multiplies the equations by monomials to get enough of them), or compute a Gröbner basis.
  Why it matters: drawn in round 8. It is the classical way to make a degree-k relation linear, the same move as
  adding a k-way term to an attention logit.
- **Astra and Argon.** Neo's names for the other labs' models we run as agents: Astra is OpenAI's Codex CLI
  (gpt-6-astra) and Argon is Google's Gemini 4 Argon (the agy CLI). Why it matters: they carry the work when the
  weekly Claude limit runs low, and their math gets checked before we use it.
- **2-simplicial (cubic) attention (Clift et al., ICLR 2020).** Attention whose score is a trilinear form over a
  query and two keys, so that one step weighs pairs of items jointly. It was first used on entity tokens in a
  logic-puzzle RL world (BoxWorld). Why it matters: it is the published form of Neo's 2023 cubic operator, and the
  closest prior art for round 8's "bind classes, not tokens".
- **Slot and entity memories: EntNet (Henaff et al., 2017), the relational memory core (Santoro et al., 2018), RIMs
  (Goyal et al., 2019).** A small set of memory vectors, one per entity or mechanism, updated as text arrives. In RIMs
  only the relevant slots update at each step and the rest stay unchanged. Why it matters: round 8's candidate C1
  puts a k-way term over such slots, and these are its baselines.
- **Harsanyi dividend / Möbius inversion (Harsanyi, 1963).** For a value defined on sets, the part attributable to a
  set as a whole, after subtracting every smaller subset's contribution. A pure three-way effect has zero dividends on
  every pair. Why it matters: it is the cooperative-game name for our subset expansion. Round 8 used it to explain why
  averaged training signals cannot see purely k-way premises. [zoo]
- **On-policy versus ∀ bisimulation (Ferns, Panangaden and Precup, 2004; Castro, 2020).** Ferns' bisimulation metric
  takes the worst case over actions, matching Nerode's "for all futures". On-policy versions average over the
  actions a policy takes instead. Why it matters: our Nerode loss L_M averages, which gives almost no weight to a
  rare decisive future. Round 8 names this as the likely cause of its failure under dilution (candidate C2).
- **Counterexample processing (Rivest and Schapire, 1993).** Given a string on which a hypothesis automaton is wrong,
  binary search over its prefixes finds a single new distinguishing suffix to add. Why it matters: it is the cheap
  way to find the decisive future that separates two states the model has wrongly merged.
- **Mazurkiewicz traces (1977).** Sequences taken up to swapping adjacent independent actions. Two orders of
  independent events are the same trace. Why it matters: irrelevant narrative that commutes with the tracked state
  could be removed by a loss enforcing s(uab) = s(uba) for independent a, b (round 8, Sokoban agent).
- **Entropy-minimality (symbolic dynamics; Lind and Marcus, 1995).** Every proper subshift of an irreducible sofic
  shift has strictly smaller entropy. So if a system never leaves the target shift and matches its entropy, it is the
  whole shift. Why it matters: it is a possible certificate that a generator produces all of a target language, not
  just legal strings. [zoo]
