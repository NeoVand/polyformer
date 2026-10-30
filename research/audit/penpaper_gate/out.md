# Pen-and-paper gate: prior-art check

**Date: 29 Oct 2026.** I opened every arXiv abstract page cited below on this date. I also read the PDF text for Cai 2017, Zaremba 2016 and Wei 2026, and the HTML for Tong 2025, Lotfi 2024/25, Madan 2026 and Lai 2024. **OPEN** means *not found in this search*, which is not proof of absence. The earlier `sketchpad_gate/out.md` covers optical compression and the visual-CoT surveys, so this file only repeats what bears on the pen-and-paper framing.

## Verdict first

**Still open, stated narrowly:** I found no work with one set of weights in a **pretrained VLM** that does all of the following:
- copies a text problem onto a pixel sheet;
- runs **several distinct paper procedures** on that sheet (column addition, long multiplication, long division, step-wise linear-equation solving), reading it through its own vision encoder, writing glyphs back and keeping no other state;
- carries an **exhaustive certificate over the finite set of rendered local views for every procedure**, covering control, boundaries and halting, so it is exact at any length;
- is trained only on views produced by a code generator.

**Every piece of that, taken separately, is already in the literature.**

**The three most dangerous pre-emptions:**
1. **Cai, Shin & Song, ICLR 2017 (with NPI, Reed & de Freitas 2016).** One network learns many scratch-pad programs, including grade-school addition on a 4-row grid that it reads only through local pointers. It also has *provably perfect generalization*: they verify the model against the full finite set of local step inputs. This anticipates both the certification method and the claim of "many procedures in one model on a scratch pad". The difference is that their environment is symbolic, not pixels.
2. **Wei, Mar 2026 (arXiv 2603.29069).** A 321-parameter NCA works on a 2D grid. It learns a **single-step local rule from random intermediate states rather than trajectories**, and rounds and clamps every step. It is 100% exact on sampled pairs up to 4,096-bit multiplication. This anticipates "exact at any length from local-rule data" and the "pen-and-paper ninja from scratch" idea, for multiplication.
3. **Lai et al., Oct 2024 (CAEF, arXiv 2410.07896).** A pretrained LLaMA-3.1-8B executes seven operators **including division**, as step-wise Turing-machine tape states. An "aligner" translates the raw expression into the executor's format. This is the text-tape twin of the idea, so a reviewer will ask "why pixels and not CAEF's tape?" It uses one LoRA per operator, is not exact (98–99%) and is not certified. That makes it the natural foil for "one model, many procedures", but it is also the closest pretrained-LM competitor.

**Framing risks (one tier below):**
- **Chain-of-Sketch** (Lotfi et al.) already has a Markov frame-overwrite loop with a halt bit.
- **Thinking with Video** (Tong et al.) already shows a generative frame model writing math solutions on a sheet from a text prompt. Its process faithfulness is poor.
- **Madan et al.** (ECCV 2026) already argue that foveated local perception gives length generalization in a pretrained VLM.
- **WM-VLM** already trains a pretrained VLM to predict its next visual state.

Calling the work a "world model of the sheet" will therefore read as known framing. The new content is exactness plus the certificate.

## Coverage matrix

Columns:
- **Exact∞:** exact at lengths far beyond training.
- **Pre:** pretrained LM or VLM.
- **Canvas-only:** an image or grid is the sole carried state.
- **Multi:** several procedures in one set of weights.
- **Text→sheet:** the problem starts as text.
- **Frames:** the model predicts the next image.
- **Cert:** exhaustive verification.

Symbols: ✓ = yes, ✗ = no, ~ = partial, sampled = exact on sampled test pairs only.

| Work | Exact∞ | Pre | Canvas-only | Multi | Text→sheet | Frames | Cert |
|---|---|---|---|---|---|---|---|
| NPI 2016 | ~ | ✗ | ~ (symbolic pad + LSTM) | ✓ | ✗ | ✗ | ✗ |
| Cai 2017 | ✓ (proved) | ✗ | ~ (symbolic) | ✓ | ✗ | ✗ | **✓** |
| Zaremba 2016 | ~ | ✗ | ✗ (grid + RNN) | ✗ | ✗ | ✗ | ✗ |
| Neural GPU 2016 | ~ | ✗ | ✓ (2D state) | ✗ | ✗ | ✗ | ✗ |
| Wei 2026 NCA | sampled | ✗ | ✓ | ✗ | ✗ | ✓ (grid) | ✗ |
| Back de Luca 2025 | ✓ (w.h.p., NTK) | ✗ | ✗ | ~ | ✗ | ✗ | proof, not audit |
| CAEF 2024 | ✗ (≈98%) | ✓ | ✗ (text tape) | ✗ (LoRA/op) | ✓ | ✗ | ✗ |
| Chain-of-Sketch 2024/25 | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| Thinking with Video 2025 | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Madan 2026 | ✗ | ✓ | ✗ (LSTM state) | ✗ | ✗ | ✗ | ✗ |
| Visual Sketchpad / WoT / MathCanvas | ✗ | ✓ | ✗ (growing transcript) | ✓ | ✓ | ~ | ✗ |
| **Neo's E2/E4** | ✓ (certified) | ✓ | ✓ | not yet | not yet | ✓ | ✓ |


## 1. Reasoning by drawing on images

**Drawing-to-reason in pretrained models.** None of these has arithmetic procedures, exactness, or a bounded canvas; images accumulate in context.
- **Visual Sketchpad.** Hu et al., NeurIPS 2024, [2406.09403](https://arxiv.org/abs/2406.09403). GPT-4o draws lines, boxes and plots through tools; +12.7 points on average on math tasks (geometry, functions, graphs, chess).
- **Whiteboard-of-Thought.** Menon, Zemel & Vondrick 2024, [2406.14562](https://arxiv.org/abs/2406.14562). Prompting only: the model writes Matplotlib or Turtle code and re-reads the image. Up to 92% where chain-of-thought gets 0%. Covers text → self-drawn image → re-read.
- **MVoT.** Li et al. 2025, [2501.07542](https://arxiv.org/abs/2501.07542). Anole-7B interleaves generated images on spatial navigation tasks.
- **Visual Planning (VPRL).** Xu et al., ICLR 2026 oral, [2505.11409](https://arxiv.org/abs/2505.11409). Image-only plans trained with GRPO.
- **Thinking with Generated Images** ([2505.22525](https://arxiv.org/abs/2505.22525)), **Mirage** ([2506.17218](https://arxiv.org/abs/2506.17218), latent visual tokens) and **Latent Sketchpad** ([2510.24514](https://arxiv.org/abs/2510.24514), latents plus a sketch decoder on mazes).
- **MathCanvas.** Shi et al. 2025, [2510.14958](https://arxiv.org/abs/2510.14958). BAGEL-Canvas generates and edits *geometry diagrams* in interleaved solutions, trained on 15.2M pairs plus 219K interleaved examples. It takes the "math canvas" name but has no written computation.
- **o3 "Thinking with images."** OpenAI, 16 Apr 2025, https://openai.com/index/thinking-with-images/. Crop, zoom and rotate; no writing. The page returned 403, so this is confirmed only through the search index and press: **UNVERIFIED by direct read**.

**Chain-of-Sketch** (v1 titled "Visual Scratchpads"). Lotfi, Fini, Bengio, Nabi & Abbe, Oct 2024 / Jun 2025, [2410.08165](https://arxiv.org/abs/2410.08165).
- **What it does:** ViTs trained from scratch (22M–632M) on cycles, strings, mazes and image PVR. In *inductive CoS*, a recurrent module maps the previous frame alone to the next frame, a label and a **halt bit** (pixel frames, MSE loss). It reaches 99.8% out of distribution on mazes (single-frame: 54.4%) and 88.2% on cycles.
- **Covers:** the canvas as the sole Markov state, with halting.
- **Lacks:** arithmetic, a pretrained LM, text input, exactness and any certificate.

**WM-VLM.** Zha et al., Sep 2026, [2609.34826](https://arxiv.org/abs/2609.34826).
- **What it does:** A pretrained VLM gets a world-model branch trained to **generate its next visual state**, then to use it, on 2D and 3D mental rotation: up to +39.25 points. Corrupting the states hurts.
- **Covers:** next-frame prediction inside a pretrained VLM, with a causal ablation.
- **Lacks:** symbols, procedures and exactness.

**On Locality and Length Generalization in Visual Reasoning.** Madan, Haresh, Ebrahimi, Panchal, Bhattacharyya & Memisevic, ECCV 2026, [2607.09061](https://arxiv.org/abs/2607.09061).
- **What it does:** Foveal-glimpse agents: ResNet+LSTM, and a foveated Qwen2.5-VL-3B. Strictly local perception avoids global shortcuts and length-generalizes on parity and mod-3 state machines. Root-finding on the hardest out-of-distribution split rises from 35.5% to 57.5%.
- **Covers:** fovea plus locality as the cause of length generalization in a pretrained VLM. This is the E2 thesis, empirically.
- **Lacks:** canvas-only state (the LSTM carries it; image marks appear only in one variant), arithmetic, exactness and a certificate.

**Causal audit of visual tool use.** Wang, Peng, Wei & Lu, EMNLP 2026 Findings, [2608.06270](https://arxiv.org/abs/2608.06270). Crop and zoom observations often have **no causal effect** on the answer. Not a pre-emption, but it defines the control Neo must run: edit or blank the canvas and require the continuation to follow.

## 2. Video and frame models as reasoners

**Video models are zero-shot learners and reasoners.** Wiedemer et al., Sep 2025, [2509.20328](https://arxiv.org/abs/2509.20328). Coins "chain-of-frames". Veo 3 solves mazes, symmetry tasks and "simple Sudokus", with the authors' warning that the LLM prompt rewriter may be doing the Sudoku. No arithmetic.

**Thinking with Video.** Tong et al., Nov 2025, CVPR 2026, [2511.04570](https://arxiv.org/abs/2511.04570).
- **What it does:** Sora-2 gets text math problems and returns "a video of writing the solution" plus spoken audio.

  | Benchmark | Last frame | Audio |
  |---|---|---|
  | GSM8K | 75.7% | 98.9% |
  | MATH-500 | 67.0% | 92.0% |

  Of 115 hand-checked correct cases, only **13.91%** had a fully correct written process. Wan 2.5 scores near zero without its prompt rewriter.
- **Covers:** text problem → generative model writes the solution on paper, frame by frame. This is the public version of Neo's demo.
- **Lacks:** a faithful procedure, exactness and canvas-only state. The reasoning likely comes from the rewriter, and their own audit argues for Neo.

**Also checked:**
- Deng, [2512.05969](https://arxiv.org/abs/2512.05969): Sora-2 at about 60% on chess, maze and Sudoku.
- Hong & Zhou 2026, [2606.04479](https://arxiv.org/abs/2606.04479): text-to-image models that render full solutions make logic errors.

**Not found:** a learned world model of handwriting or of math procedures that predicts sheet frames.

## 3. Pen-and-paper arithmetic on grids

**Neural Programmer-Interpreters.** Reed & de Freitas, ICLR 2016, [1511.06279](https://arxiv.org/abs/1511.06279).
- **What it does:** One LSTM core with a program memory learns 21 programs from execution traces: addition on a scratch pad (input, input, carry and output rows, read through pointers), sorting, and 3D car canonicalization.
- **Covers:** many procedures in one model; local views of a grid.
- **Lacks:** pixels, pretraining, text input and a proof.

**Making Neural Programming Architectures Generalize via Recursion.** Cai, Shin & Song, ICLR 2017, [1704.06611](https://arxiv.org/abs/1704.06611).
- **What it does:** Proves ∀i∈V, M(i)⇓P(i) over all valid step-input sequences. A verification set covers every base case and reduction (**20,181 problems for addition**), and they check that the traces match. Result: *provably perfect generalization* for addition, topological sort, quicksort and a bubble-sort variant.
- **Covers:** the certification method itself.
- **Lacks:** pixels, a pretrained model, and multiplication or division.
- **Opening:** they say perceptual inputs (MNIST, speech) make the verification set "prohibitively large, possibly infinite". A canonical renderer with a finite glyph set is precisely the escape. That is a legitimate new angle, but only for canonical renders, not handwriting.

**Learning Simple Algorithms from Examples.** Zaremba, Mikolov, Joulin & Fergus, ICML 2016, [1511.07275](https://arxiv.org/abs/1511.07275). An RNN controller moves a head over a **2D input grid** for multi-digit addition, 3-row addition and single-digit multiplication, trained with Q-learning. It generalizes to thousands of digits; multiplication degrades at 1,000. **Lacks:** pixels, a certificate and more than one procedure per network.

**Neural GPU.** Kaiser & Sutskever, ICLR 2016, [1511.08228](https://arxiv.org/abs/1511.08228). A convolutional GRU over a 2D state. Trained on binary addition and multiplication to 20 bits, it shows no errors far beyond. **Lacks:** a certificate; works on bits.

**Visual Learning of Arithmetic Operations.** Hoshen & Peleg, AAAI 2016, [1506.02264](https://arxiv.org/abs/1506.02264). Maps images of two 7-digit numbers to an image of their sum or difference; multiplication failed. **Covers:** pixel-in, pixel-out arithmetic. **Lacks:** a procedure and length generalization.

**On the Mirage of Long-Range Dependency.** Wei, Mar 2026, [2603.29069](https://arxiv.org/abs/2603.29069).
- **What it does:** A 321-parameter NCA on a binary outer-product grid, with **round + clamp every step**. "Chaos Training" uses one-step supervision on random intermediate states of 2–6-bit problems and takes 15 seconds. It is 100% exact on 200 or 50 sampled pairs per length, up to 4,096 bits.
- **Covers:** local-rule data instead of trajectories, discrete restoration, exactness at length and a tiny from-scratch model.
- **Lacks:** an exhaustive certificate, glyphs, an LM, text and more than one procedure.

**Learning to Add, Multiply, and Execute Algorithmic Instructions Exactly with Neural Networks.** Back de Luca, Giapitzakis & Fountoulakis, NeurIPS 2025, [2502.16763](https://arxiv.org/abs/2502.16763). An NTK proof that two-layer network ensembles execute binary add, multiply and SBN **exactly w.h.p.** from logarithmically many rule-isolating examples. **Covers:** exactness and data efficiency, in theory. **Lacks:** vision, pretraining and an audit of the deployed weights.

**Executing Arithmetic: Fine-Tuning LLMs as Turing Machines (CAEF).** Lai et al., Oct 2024, [2410.07896](https://arxiv.org/abs/2410.07896).
- **What it does:** LLaMA-3.1-8B steps through a text tape (heads, carry, output) for +, −, ×, ÷, >, < and ==. Division is a composer that calls > and +.
- **Accuracy:** 98.0–98.6% at 100 digits for +, − and the comparisons; 99.3% for × and ÷ within range.
- **Design:** one executor LoRA plus one aligner LoRA **per operator**.
- **Covers:** pretrained-LM paper procedures including long division; expression → executor handoff.
- **Lacks:** one model, exactness, extrapolation, vision and a certificate.

**Text-side length generalization.** None of these is certified or on a canvas.
- Scratchpad ([2112.00114](https://arxiv.org/abs/2112.00114)) and small-transformer arithmetic ([2307.03381](https://arxiv.org/abs/2307.03381)).
- Abacus embeddings ([2405.17399](https://arxiv.org/abs/2405.17399)): 20 → 100 digits at 99%.
- Position coupling ([2405.20671](https://arxiv.org/abs/2405.20671)): 30 → 200 digits.
- Turing Programs ([2407.03310](https://arxiv.org/abs/2407.03310)) and looped transformers ([2409.15647](https://arxiv.org/abs/2409.15647)).
- Inductive scratchpad ([2406.06467](https://arxiv.org/abs/2406.06467)): Markov text states, up to 6×.
- Easy-to-hard recurrent networks ([2106.04537](https://arxiv.org/abs/2106.04537)) and NCA matrix primitives ([2505.13058](https://arxiv.org/abs/2505.13058)).
- **Extrapolation by association** ([2506.09251](https://arxiv.org/abs/2506.09251), NeurIPS 2025): length generalization *transfers* between related tasks trained jointly, through shared heads. That supports one model for many procedures.

**Long division:** I found no neural work that learns paper long division as a procedure with length extrapolation, beyond CAEF's composer. OPEN, but thin.

**Step-wise algebra:**
- **ConPoLe.** Poesia, Dong & Goodman, NeurIPS 2021, [2106.09146](https://arxiv.org/abs/2106.09146). RL over Common Core equation and fraction environments; the network picks rewrite axioms and a symbolic engine applies them.
- **A Neural Rewriting System to Solve Algorithmic Problems.** Petruzzellis, Testolin & Sperduti, ECAI 2024, [2402.17407](https://arxiv.org/abs/2402.17407). A learned Selector, Solver and Combiner simplify nested arithmetic and algebra formulas step by step, with better out-of-distribution results than GPT-4.
- **Not found:** learned step-wise *equation solving* with exact length guarantees, on a canvas or off it.

## 4. Rendered math and optical working memory

- **Optical compression:** DeepSeek-OCR ([2510.18234](https://arxiv.org/abs/2510.18234)): about 97% below 10× and about 60% at 20×. Glyph ([2510.17800](https://arxiv.org/abs/2510.17800)): 3–4×.
- **Rendered memory:** VTC-R1 ([2601.22069](https://arxiv.org/abs/2601.22069)) renders math reasoning as accumulating images. MemOCR ([2601.21468](https://arxiv.org/abs/2601.21468)) is a rendered rich-text memory.
- **Liang et al.** ([2601.03714](https://arxiv.org/abs/2601.03714)): without linguistic support, DeepSeek-OCR falls from about 90% to about 20%. Exact canvases must not lean on priors; this matches the E1c leading-zero misses.
- **Rendered math input:** LaTeX-as-image training ([2511.11704](https://arxiv.org/abs/2511.11704)); VLMs fail on visual equations because of counting ([2509.09013](https://arxiv.org/abs/2509.09013)).

None of these executes a procedure on the rendering. "Rendered memory" is taken; "exact computational memory" is not.

## 5. Text to sheet

- **Self-Imagine.** Akter, Madaan, Lee, Yang & Nyberg 2024, [2401.08025](https://arxiv.org/abs/2401.08025). One VLM writes HTML for a word problem, renders it and reasons over the image, with no training; gains on GSM8K, ASDiv and SVAMP. **Covers:** the same model writing the problem onto a sheet.
- **CAEF's aligner** covers the expression → learned-executor handoff.
- **Neural Comprehension.** Weng et al., ICLR 2024, [2304.01665](https://arxiv.org/abs/2304.01665). Inserts *compiled* rule networks, not learned ones, into an LM.
- **Not found:** an LM that hands the equation to a learned, certified procedure that it runs itself.

## 6. Local-rule data, undo and error repair

**Already taken:**
- local-state training instead of trajectories (Wei);
- verification over a finite local step domain (Cai);
- exactness from few rule-isolating examples (Back de Luca).

**Not found:** a margin certificate over deployed weights on every *rendered* local view, read by a frozen pretrained vision tower (242 and 1,553 views). Cai's guarantee also covers control, meaning when subprograms run and return. Neo's must cover the painter, halting and boundary views, or it is weaker than Cai's.

**Undo and repair:**
- Physics of LMs 2.2 (Ye, Xu, Li & Allen-Zhu, ICLR 2025, [2408.16293](https://arxiv.org/abs/2408.16293)): [BACK] retry data on synthetic grade-school math.
- PENCIL (Yang, Srebro, McAllester & Li, ICML 2025, [2503.14337](https://arxiv.org/abs/2503.14337)): learned erasure, optimal-space Turing simulation with 25M parameters.

Repair on a canvas: OPEN, low novelty value.

## Skeptical notes

1. **Algebra may break the certificate.** Moving a term across "=" and handling arbitrary coefficients are non-local. Certified algebra needs a fixed-window rewrite design, like Cai's reductions, that calls the column subroutines. It does not follow from the addition and multiplication pattern.
2. **"One model" must mean one adapter and one certificate over the union of view domains,** with the procedure chosen from the sheet. Otherwise it is CAEF with pixels.
3. **Text → sheet is an uncertified interface,** especially for word problems. Claim "exact conditional on the sheet".
4. **"World model" is taken framing** (WM-VLM, VPRL, chain-of-frames). The distinction is *exact, certified* next-frame prediction.
5. **A from-scratch "ninja" competes with Wei, the Neural GPU and Zaremba.** It is only interesting if one small pixel model covers several procedures, including division or algebra, under a certificate. I found no peer-reviewed multi-operation NCA. An informal Feb 2026 Reddit post reports addition and subtraction interfering in one NCA (UNVERIFIED).
