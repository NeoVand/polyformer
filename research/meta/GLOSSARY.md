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
