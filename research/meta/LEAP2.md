# LEAP2: the register is the state, not the token

Fable, 29 Oct 2026, for Neo. Read-only; nothing run, $0. Answers the orchestrator's four questions after the Savant-R
gate (NARROW) and the leap2 gate (C1–C4 NARROW, C5 "killed as novelty").

## 1. Assumptions we are still not questioning

1. **Attention is the substrate.** Every design since 20 Oct lives in a full-attention transformer, where the past is a
   growing cache. Our own no-finite-test theorem says such a decoder cannot be certified; the pinned policy and the host
   clock exist only to fight that. We never asked which architecture makes the theorem's hypothesis true for free.
2. **Memory lives outside the model.** NEW_MODEL's bus floor (READ/WRITE/EVICT) was proven for a transformer. A delta-rule
   layer (Gated DeltaNet, RWKV-7) *is* a writable key-value memory: S ← S(I − βkkᵀ) + βvkᵀ erases the value at key k and
   writes a new one, inside the forward pass. We treated the bus as physics; it is a base choice.
3. **A certificate is an enumeration.** We only ever checked rows; the one continuous certificate we tried (UNIFY, 25
   Oct) died on the nonlinear residual flow. A rank-one write with near-orthogonal keys has *provable* locality: one
   lemma instead of 10^260 rows. We never looked for structure to prove instead of rows to check.
4. **The state is a token.** "Register, not transcript" was forced by the cache. In a matrix-state model the register is
   latent and Theorem P still applies; condition 4 (no chain of thought) is met literally, not by wording.
5. **The compiler learns from traces or RL.** We never trained it *through* the certified executor. Soft execution of a
   distribution over ISA tokens by a finite automaton is a product of stochastic matrices, differentiable (TerpreT 2016).
   RL was null because the reward was sparse; this gradient is dense. Known, cheap, the fix for P4's 20/88; not the leap.
6. **Qwen3 is the base.** Qwen3.5 shipped 16 Feb 2026. The 4B card (verified today): Apache-2.0, "Hidden Layout: 8 × (3 ×
   (Gated DeltaNet → FFN) → 1 × (Gated Attention → FFN))", 262k context; Transformers.js v4.1 lists Qwen3.5, and a WebML
   demo runs 0.8B/2B/4B in the browser. The substrate we need has been in our own model family for eight months and
   nobody in this project opened the card. That is the most embarrassing line here and I am leaving it in.
7. **Novelty must sit in a mechanism.** Two gates say every mechanism is NARROW. What no gate can call narrow: a theorem
   that classifies which decoders are certifiable, and one measured instance that nobody has.

## 2. The single best leap: history-independence as architecture

**Claim.** A hybrid LM whose recurrent layers are delta-rule states holds a register machine *in the state*: registers
are key directions, a write is the rank-one update, a read is Sq. Control (fetch, decode, branch) stays in attention over
a pinned program prefix, as REGVM does today. No host logic touches data. Certificate in three parts: (a) enumerated
local rows over (opcode, addressed register's digit code, flags), once per device, like REGVM's 648-row ROM; (b) a
locality lemma, linear algebra, bounding how far a write to kᵢ moves the value at kⱼ by the Gram matrix of the snapped
keys; (c) a basin condition, in the gate's own words: F_a(B_q) ⊆ B_δ(q,a) with correct decoding throughout, not "the
centres are right". Exact means unbounded *duration* with bounded storage (64 cells), which is what REGVM already means.

**Why this is a leap and not a base swap.** The gate killed C5 "as novelty" and is right that picking RWKV or Ouro is
engineering. The concept is different: the theorem's hypothesis (the view of the past is a finite function of a
history-independent state) is enforced by the host in Savant and by the *architecture* here. In 24 of 32 layers the
state is the only channel to the past; the 8 attention layers see a fixed window (pinned prefix plus current block, a
runtime setting like a stop token). The bus's WRITE is the layer's own update rule. Condition 2 is met in the strong
sense of 27 Oct: the remaining host action is a fixed window on eight layers, with no data path.

**Against the twelve conditions, relative to Savant-R.** 2: bus floor → fixed window only. 4: truly latent state. 7:
"certified once for all programs" holds for ISA and register file (rows (a) and lemma (b) are per device; control rows
stay per program, six per line). 10: the new architecture is no longer a funding ask; it ships at frontier scale
(Qwen3-Next, Qwen3.5, Kimi Linear), and our result is that *this class is a certifiable computer and full-attention
transformers are not*. 11: Qwen3.5-4B runs in Transformers.js (verify M4 latency; 0.8B is the safe tier). 3, 6, 8, 9:
unchanged, same recipe, same risks.

**Base: Qwen3.5-4B (instruct) for the model, Qwen3.5-0.8B for pilots.** Same tokenizer family, chat template and
Stage 2r mix. Not Ouro or Huginn: a depth loop adds compute per step and no memory across steps, the wrong loop (the
gate's Q1 table: Shapiro's retrofit 83.8%, 70% by depth 18). Not Mamba-2 hybrids (Falcon-H1, Nemotron-H): diagonal SSMs
cannot track S5 (Merrill 2024); delta-rule and Householder states can (Grazzi 2024, DeltaProduct 2025, Howe 2026 at
1.00 to 512). RWKV-7 1.5B is the pure-RNN fallback if the hybrid's attention layers turn out to carry the registers.

**Risks, in order.** (i) The decay gate: Gated DeltaNet scales each head state by α_t < 1 every step. Uniform scale plus a
norm on the read leaves decoding unchanged until underflow; survival over 10⁵ ticks depends on α saturating in the state
precision (fp32 state in the FLA kernels: fine; bf16: dead by ~10³). Measured on day one. (ii) Interference: 24
registers × 64 cells need ~64 near-orthogonal snapped keys per head at head dim 128; feasible, learned, not given.
(iii) Our three latent collapses (INMODEL, L-AIM, QINTERP2) all wrote *programs* into latent space; here the program
stays in tokens, and the one latent positive (LATENT-1, exact at 4,096) was a *state*, which is what a register is.
(iv) Tooling: LoRA on the DeltaNet projections through FLA kernels, plus a per-layer window on attention; one day.
(v) Prior art: Schlag et al. 2021 introduced the delta rule *as* fast-weight programming; Siems et al. 2026 train linear
RNNs on REPL traces for permutation state; Howe 2026; "What Can a Recurrent State Safely Forget?" (Sep 2026) for (c).
None certifies a register file or runs self-written programs in an LM. Searches for Astra: "Gated DeltaNet register
file", "linear attention associative memory interpreter certified", "Qwen3-Next state tracking exact", "fast weight
programmers instruction set", "delta rule erase write locality bound", "hybrid linear attention program execution no
chain of thought".

## 3. C1–C4

- **C1: sharpen into §2.** The loop must run along the sequence (state across ticks), not depth; on a transformer base a
  retrofitted loop leaves the cache, and the certificate, where they were. Keep the full-domain hinge and the snap term.
  Kill "program into latent registers, then RL": three collapses and HR1–HR3.
- **C2: kill as stated, keep its truth.** Delta composition is nonlinear, so the certificate is per program, worse than
  Theorem R; T2L and Drag-and-Drop own the mechanism. Its true content is that fast weights are a register file: §2.
- **C3: narrow to an operator.** A scan needs the input in advance; a branch makes the next input depend on the state, so
  control flow is sequential. MLP-LDRU already trains associativity. Keep "scan" as the packed fold in the ISA.
- **C4: kill.** The compiled teacher gives traces we already have; distilling into the core is the full fine-tune that
  cost language in INSIDE (ppl 19 → 2×10⁴); ALTA and InterpBench own the method.

## 4. The one cheap experiment (≤ $10, one day; someone else runs it)

**Register-file pilot on Qwen3.5-0.8B-Base.** 8 registers × 10 digits; opcodes SET r d, INC r, CPY r s, OUT r; random
streams of 2,048 ops; the model emits one token per OUT and nothing else. LoRA rank 32 on the DeltaNet projections only
(q, k, v, β, gate) of all 24 DeltaNet layers; attention frozen, windowed to prefix + 64 tokens if the config allows.
1,500 steps, 20% ordinary text with KL 1.0, three seeds; ≈ 15 min per seed on an H100 at $5.22/h.

**Predictions.** P1: per-OUT exactness ≥ 0.999 and all eight registers correct after 10⁴ and 10⁵ ops under free
generation on ≥ 2/3 seeds. P2 (locality): zeroing the DeltaNet state at the end of a run changes the next OUT, so the
registers live in the state, not the cache; a register's read is unchanged by 1,000 intervening writes to other
registers; the carrying layer's snapped register keys have max |cos| < 0.2. P3: state norm after 10⁵ ops within 10× of
its value at 10³ (α saturates, no underflow). P4: text perplexity ratio ≤ 1.05.

**Kills.** K1: P1 fails on all seeds → the delta state does not hold registers under LoRA; drop the switch, run
NEW_MODEL's Savant-R on Qwen3-4B as written. K2: P2 fails (registers in the cache, or interference) → no locality lemma;
same fallback. K3: P3 fails in fp32 → registers need refresh ticks, which buys the clock back; say so. **Arm B**
(diagnostic, same cost): the identical run on Qwen3-1.7B under plain decoding; if it is also exact at 10⁵, the leap is a
certificate result, not a capability result, and the paper says exactly that.

If P1–P4 hold: day 2, REGVM's 13 fixtures with the native ALU and registers in the state (Pilot R1 re-based); day 3, the
certificate (rows, Gram bound, basins); day 4, Stage A on Qwen3.5-4B with the language term from step one; days 5–7,
export, DAUDIT, page. Budget unchanged (≤ $500, $1k reserve).

**What this is and is not.** One measured instance of a theorem we can state and partly have in Lean: a decoder is
finitely certifiable iff its view of the past is a finite function of a history-independent state; transformers need a
host to satisfy it, delta-rule hybrids satisfy it by construction. Not a new mechanism; the gates are right that none is
left. A different answer to where the computer lives: in the state the frontier labs already ship, unused.

## 5. Pictures (added 29 Oct, after Neo: "imagine programs as videos or images, think bold")

**(a) The boldest version of §2 that still meets the conditions: show it, then watch it compute.** The register file of §2
is loaded from a camera, not a prompt, and shown as a picture while it runs. Qwen3.5-0.8B/2B take images and video
natively, so the compiler's *input* becomes a photo of a scrambled cube (54 stickers = 54 registers, under the 64-cell
budget), a hand-written column of numbers, a drawn flowchart or a listing on a whiteboard; the model compiles it into
ISA tokens and the state, then runs exactly. The *output* is the state film: at every tick the carrying head's matrix
S is a frame, and in the snapped key basis (render S·K, one column per register) the frame is the register bank with
digits in it. Nobody generates a video; the computation *is* the video, and it is free. The user can poke a column (a
WRITE the certificate covers), and sees the basin condition (c) with their eyes: a nudge smaller than the basin snaps
back, a larger one is a new value and the run continues from it. This is Neo's "ghost cube" and "poke the brain" demos
of 26 Oct, made honest: the edit is a register write, not a residual-stream stab, and the exactness claim has one
stated boundary, the same one the Savant-R gate allowed for S4: *exact given the reading*. Perception (image → state and
image → program) is empirical and evaluated separately; execution is certified. Against the conditions: 1, 2, 4, 6, 7,
10 unchanged from §2; 3 is met with an image as the "normal prompt"; 5 holds with the boundary stated; 9 now needs a
vision-retention slice beside GSM8K; 11 is where this pays, a camera and a live working memory on a laptop; 12 costs
one day of data (render REGVM listings and cube states as images) and a check that Transformers.js runs the vision
tower (the v4.1 notes list Qwen3.5 among VL models; verify on the M4). The thing to resist: the 288 matrices are only
"pictures" through the lens of the snapped keys; raw S is a checkerboard of outer products and looks like noise.

**(b) M1–M4.**
- **M1, the state is a picture: sharpen into the demo's centre.** As above, rendered in the snapped key basis, with
  live edits. Not a science claim (LSTMVis 2016 and activation patching edit recurrent state); the new part is that the
  picture has a certified meaning, every column a register the rows (a) cover.
- **M2, drawn machines: kill the clause "exact for any canvas size"; keep a toy.** Cells must be addresses, addresses
  are key directions, and one head has at most d_k ≈ 128 orthogonal keys: the same addressing floor as the bus, now in
  the state. A 2-D canvas stored as rows gives a 3-row view with 2^(3w) certificate rows, finite only for w ≤ 6; a
  canvas of ≤ 128 cells as keys (11 × 11 Life, 121 × 512 rows, nine heads reading nine offsets) is certifiable and
  would make a pretty second demo. NCA, CA-trained LMs and Wireworld own the rest. Not this week.
- **M3, watch then run: kill the rule induction, keep the state induction.** A rule certificate needs every
  neighbourhood observed (Chow's state bound again); a few frames never show all 512, and video-models-as-reasoners is
  2025 prior art. What video can give exactly is the *data*: watch long division on paper, read the digits, run the
  known certified algorithm to the end. That is (a).
- **M4, program as an image: sharpen; it is the compiler's input modality in (a).** Flowchart and code-screenshot
  VQA benchmarks exist; the delta is that the compiled program runs certified. Same P4 risk as text (comprehension,
  not notation), now with a perception term on top; measure it, do not promise it.

**(c) The ≤ $10 pilot does not change.** It tests the one load-bearing question, whether the delta state holds
registers under LoRA; pictures sit on the compiler, which the pilot does not touch. One free addition: dump the
carrying layer's S and S·K per tick during evaluation and render them. If the registers are rank-one strokes in the
key basis, P2's locality is visible before it is measured; if the frames are noise, the lens is wrong or the registers
live in the attention cache, and K2 has its answer early. Use the multimodal 0.8B for the pilot as planned, so the
same checkpoint can read its first photo on day 2.
