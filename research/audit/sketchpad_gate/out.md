| Claim | Verdict | Closest work, dated | What remains open |
|---|---|---|---|
| **S1: rendering restores exact state** | **NARROW** | [Brandoit et al., 26 Sep 2026](https://arxiv.org/abs/2609.32447); [Wei’s quantized arithmetic grid, 30 Mar 2026](https://arxiv.org/abs/2603.29069) | A certified perceptual–computational loop. Rendering alone provides neither correct symbol selection nor correct transitions. |
| **S2: local updates generalize indefinitely** | **NARROW** | [Neural GPU, 25 Nov 2015 / ICLR 2016](https://arxiv.org/abs/1511.08228); [Wei, revised 5 Apr 2026](https://arxiv.org/abs/2603.29069) | Exhaustive certification of a learned rule, including boundaries, initialization and termination, connected to a pretrained VLM. |
| **S3: optical memory is denser** | **KILLED as broad novelty** | [DeepSeek-OCR, 21 Oct 2025](https://arxiv.org/abs/2510.18234); [Glyph, 20 Oct 2025](https://arxiv.org/abs/2510.17800) | Worst-case exact cell capacity and certified decoding margins, rather than average document recovery. |
| **S4: shared arithmetic/physics canvas** | **NARROW** | [FHP lattice gas, 7 Apr 1986](https://doi.org/10.1103/PhysRevLett.56.1505); [FluxGNN, ICML Jul 2024](https://proceedings.mlr.press/v235/horie24a.html) | One learned, certified transition system spanning arithmetic and conservative dynamics. Neither conservation nor grid simulation is new. |
| **S5: visible, editable mental workspace demos** | **NARROW** | [Visual Sketchpad, 13 Jun 2024](https://arxiv.org/abs/2406.09403); [Latent Sketchpad, 28 Oct 2025](https://arxiv.org/abs/2510.24514) | The integrated browser demonstration with genuinely bounded state, causal interventions and exact computation. |

**Audit date: 29 October 2026.** Earlier gate tables were read; their general arguments are not repeated. “OPEN” below means **not located in this search**, not absent. Verdicts distinguish novelty from feasibility.

**Q1 — What survives S1–S5?**

**S1:** Brandoit’s result concerns particular finite-precision state-tracking architectures and perturbation assumptions. It does not establish that rasterization makes a VLM exact. A hard glyph decision followed by canonical rendering can remove within-symbol analog variation; it can also preserve a confidently wrong symbol forever.

The necessary certificate covers **reader → transition → symbol selection → renderer**, plus control state. Checking isolated glyphs cannot certify a globally attentive vision encoder whose outputs depend on neighboring content, resizing and positions. Quantizing a latent codebook can provide the same discontinuous reset without pixels.

**S2:** Locality and shared weights make an inductive proof possible; they do not supply one. Exhaustive enumeration works when the alphabet and neighborhood are finite, the deployed update truly depends only on that neighborhood, and every allowed pattern implements the intended rule. Reachability restrictions require their own proof. Carry propagation, boundaries and halting also matter.

“Constant size” must mean constant **during one computation**. Arbitrarily long inputs require a family of larger canvases. Also, retained text, KV caches or recurrent hidden states invalidate a claim that the canvas alone is the Markov state.

**S3:** Fewer sequence positions is not automatically greater reliable information capacity, fewer bytes or less computation. Vision tokens are continuous vectors, and recovering plausible prose tolerates errors that arithmetic cannot. The useful experiment measures tokens/cell against worst-case symbol margin and whole-computation failure, with fixed typography, quantization and perturbation bounds.

**S4:** Integer storage does not itself conserve anything. Each collision/update must preserve specified invariants; streaming and boundaries must preserve their totals; overflow must be excluded. A rendered ball position omits velocity, so it is not generally a complete Markov state. One next-canvas loss is a shared training format, not evidence that arithmetic and physics share a learned algorithm.

**S5:** Make the intervention consequential: replace a carry, bead or velocity while clearing every other persistent state; require the continuation predicted from the edited state. Blank/shuffled-image controls are necessary. [Wang et al., 6 Aug 2026, revised 8 Sep](https://arxiv.org/abs/2608.06270) found visual tool outputs often lacked causal influence despite apparent reasoning gains. Handwriting recognition remains a separate fallible interface: exact arithmetic conditional on transcription is not exact interpretation of arbitrary photographs.

**Q2 — Optical compression: actual numbers and actual memory**

[DeepSeek-OCR, 21 Oct 2025](https://arxiv.org/html/2510.18234v1) reports approximately **97% OCR precision below 10× text/vision-token compression**, falling toward **60% at 20×**. Its English Fox experiment contains 100 pages with 600–1,300 text tokens. Examples:

| Text tokens/page | Vision tokens | Compression | OCR precision |
|---|---:|---:|---:|
| 600–700 | 100 | 6.7× | 98.5% |
| 900–1,000 | 100 | 9.7× | 96.8% |
| 1,200–1,300 | 64 | 19.7× | 59.1% |

These are not exact-page success rates. Fixed modes use **64/100/256/400 tokens** at **512/640/1024/1280 square pixels**; cropping changes totals. Its OmniDocBench comparison uses under 800 tokens against MinerU’s 6,000-plus.

“Optical forgetting” proposes rendering history and progressively reducing resolution/token allocation. The paper explicitly leaves validation beyond OCR to future work; it does not demonstrate exact recurrent working memory.

[DeepSeek-OCR 2, 28 Jan 2026](https://arxiv.org/html/2601.20552v1) adds semantic visual-token ordering. OmniDocBench 1.5 rises **87.36→91.09**, with maximum visual tokens **1,156→1,120** in the reported comparison. This is document parsing, not an exact-memory capacity curve.

Other relevant evidence:

- [Glyph, 20 Oct 2025](https://arxiv.org/abs/2510.17800): typically **3–4×** text-context compression with comparable downstream performance. Optical context is already established prior art.
- [PIXEL, 14 Jul 2022](https://arxiv.org/abs/2207.06991): text represented as rendered pixels. [VIST, 2 Feb 2025, revised 11 Dec](https://arxiv.org/abs/2502.00791): vision-centric distant-context compression, reporting **2.3×** fewer tokens at comparable performance.
- **[VTC-R1, 29 Jan 2026](https://arxiv.org/html/2601.22069v1)** directly renders reasoning segments and rereads them. With Qwen3-VL-8B, MATH500 rises **85.4→90.0**, but AIME25 falls **32.71→30.00**. Crucially, its algorithm **accumulates images**: it is not an overwritten Markov canvas.
- **[MemOCR, 29 Jan 2026; revised 18 May](https://arxiv.org/html/2601.21468v5)** maintains bounded, updated rich-text memory and renders it for visual access. Qwen2.5-VL-7B reports **74.6% versus 67.8%** for its strongest baseline in the specified 10K-context/1,024-token setting. This is closer to replacement memory, but not certified canvas-only arithmetic.
- [Optical Reasoning, 8 Jun 2026](https://arxiv.org/abs/2606.09585) also studies visually rendered reasoning rationales.

**Answer: yes, optical context has already been used for reasoning and working memory, beyond document OCR.**

**Q3 — Strong image/imagery reasoning results**

Selected primary-paper results, not a cross-benchmark ranking. “Appended” refers to the model’s conditioning history, even when each image depicts a current state.

| Work/date | Model and reported result | State semantics; limitation |
|---|---|---|
| [Visual Sketchpad, 13 Jun 2024](https://arxiv.org/abs/2406.09403) | GPT-4o, undisclosed size; average mathematical-task gain **12.7 points** | External drawing/tools; growing multimodal transcript. |
| [MVoT, 13 Jan 2025](https://arxiv.org/html/2501.07542v1) | Anole-7B; Maze **92.95%**, MiniBehavior **95.14%**, FrozenLake **85.60%** | Appended interleaved text/images; answer accuracy, not universal transition correctness. |
| [Visual Planning/VPRL, 16 May 2025, v1](https://arxiv.org/html/2505.11409v1) | 3B visual language model; trajectory exact-match **91.6/74.5/75.8%** on FrozenLake/Maze/MiniBehavior | Image-only autoregressive trajectories; extrapolation deteriorates. |
| [Thinking with Generated Images, 28 May 2025](https://arxiv.org/html/2505.22525v1) | Anole-7B; GenEval two-object score **0.38→0.57** | Appended generated imagery; composition benchmark, not arithmetic. |
| [Mirage, 20 Jun 2025](https://arxiv.org/html/2506.17218v1) | Qwen2.5-VL-7B; VSP spatial/planning **89/60**, versus text-CoT+GRPO **85/51** | Generated latent imagery tokens within reasoning; no certified overwritten grid. |
| [Latent Sketchpad, 28 Oct 2025](https://arxiv.org/html/2510.24514v1) | Gemma-3-12B, also Qwen2.5-VL-7B; Gemma maze success **70→72.2%**, larger OOD maze **8→10%** | Visual latent sketches appended after actions; weak size extrapolation. |
| [HyLaR, 22 Apr 2026](https://arxiv.org/html/2604.20328v1) | Qwen2.5-VL-7B; V* **76.44→83.77%** | “Canvas-in-Latents” representations within hybrid reasoning; no exhaustive arithmetic certificate. |

None of these results establishes exact arithmetic for arbitrary lengths or steps. Benchmark “exact match” means that sampled outputs matched, not that the algorithm is proven exact.

The broad territory is already surveyed in [Su et al., 30 Jun 2025](https://arxiv.org/abs/2506.23918) and [Dong et al., ACL 2026](https://aclanthology.org/2026.acl-long.2087/). A generic “visuospatial sketchpad for language models” novelty claim is untenable.

**Q4 — Hundreds of digits, certification and conservation**

**The complete conjunction was not located:** pretrained VLM + sole overwritten 2D working state + exact hundreds-of-decimal-digits arithmetic + certified local rules.

But the closest arithmetic result is uncomfortably close. [Wei, 30 Mar 2026, revised 5 Apr](https://arxiv.org/pdf/2603.29069) uses a **321-parameter** neural cellular update, trained on **2–6-bit** multiplication traces, with **rounding and nonnegative clamping every step**. It reports **100% sampled accuracy through 4,096-bit operands**, about 1,233 decimal digits per operand.

Caveats matter: the input uses a structured binary outer-product construction; training uses rule traces; only 50 pairs are tested per longer length. An exhaustive deployed-rule certificate was not located. The project webpage’s “digits” wording should not override the paper’s **bits**. This already combines local learned arithmetic, overwriting and discrete restoration.

Earlier arithmetic anchors further narrow the claim:

- [Extended Neural GPU, 2 Nov 2016](https://arxiv.org/abs/1611.00736): strong decimal length extrapolation, but conspicuous structured failures.
- [Abacus embeddings, 27 May 2024](https://arxiv.org/abs/2405.17399): training through 20 digits, up to **99%** on 100-digit addition; positional structure rather than visual perception.
- [Multidimensional Position Coupling, 21 Oct 2024; revised 17 Apr 2025](https://arxiv.org/abs/2410.15787): structured positions support arithmetic extrapolation without an image canvas.
- [Virtual-abacus RL, 17 Jan 2023](https://arxiv.org/abs/2301.06870): OOD addition/subtraction with under 1% error, not exactness.
- [Frank and Barner, online Jul 2011 / journal Feb 2012](https://langcog.stanford.edu/papers/FB-jepg2011.pdf): human mental-abacus evidence supports visually organized numerical representations; it does not establish a machine architecture.

**Learned conservation already exists.** [FluxGNN, ICML Jul 2024](https://proceedings.mlr.press/v235/horie24a.html) builds conservation into learned numerical fluxes. [DYNAMI-CAL GraphNet, 15 Jan 2026](https://www.nature.com/articles/s41467-025-67802-5) enforces linear/angular momentum structure in learned interaction dynamics. Algebraic conservation must be distinguished from bit-for-bit floating-point conservation; inelastic systems need not conserve kinetic energy.

For integer lattice gas, invariant-preserving collisions plus streaming on a closed/periodic lattice can provide exact discrete conservation. That is classical [FHP, 7 Apr 1986](https://doi.org/10.1103/PhysRevLett.56.1505), not a newly discovered consequence of visual memory.

[Video Models Are Zero-shot Reasoners/Veo 3, 24 Sep 2025](https://arxiv.org/abs/2509.20328), [Genie 3, 5 Aug 2025](https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/), [V-JEPA 2, 11 Jun 2025](https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/), and [Cosmos, inspected 29 Oct 2026](https://research.nvidia.com/labs/cosmos-lab/) establish powerful prediction/planning capabilities. An exact-conservation certificate for their learned rollouts was not located.

**Q5 — Small browser VLMs**

Availability below was checked **29 Oct 2026**. These are open-weight models; licenses differ. Browser demos/source establish implementation evidence, not independently reproduced performance.

| Model | Browser evidence | Visual-token cost |
|---|---|---|
| **Qwen3.5-0.8B / 2B** | [0.8B optimized ONNX with Transformers.js/WebGPU image example](https://huggingface.co/onnx-community/Qwen3.5-0.8B-ONNX-OPT); [2B export and linked WebGPU demos](https://huggingface.co/onnx-community/Qwen3.5-2B-ONNX) | From [processor configuration](https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/main/preprocessor_config.json): inferred still-image cost \(H'W'/1024\), after resizing; **256 at 512²**, **1,024 at 1024²**. |
| **SmolVLM-256M / 500M** | [Official release, 23 Jan 2025](https://huggingface.co/blog/smolervlm), including browser support | **64 per 512² crop**; splitting increases total. |
| **FastVLM-0.5B** | [ONNX/WebGPU implementation](https://huggingface.co/onnx-community/FastVLM-0.5B-ONNX); [Apple browser announcement, updated 22 Sep 2025](https://machinelearning.apple.com/research/fast-vision-language-models) | [Architecture, revised 15 May 2025](https://arxiv.org/html/2412.13303v2): **256 at 1024²**. |
| **LFM2.5-VL-450M / 1.6B / 3B** | [Official collection with all three WebGPU demos](https://huggingface.co/collections/LiquidAI/lfm25-vl) | [450M](https://huggingface.co/LiquidAI/LFM2.5-VL-450M): configured **32–256**; [1.6B](https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B): **64–256**, with tiling increasing totals. [3B](https://huggingface.co/LiquidAI/LFM2.5-VL-3B): dynamic tiles; verified fixed per-image count not located. |

**Latency:** a comparable, hardware-specified browser per-image benchmark for these stock checkpoints was not located. Native MLX latency, server throughput and text decoding tokens/second cannot fill that column.

One scoped browser measurement exists: [decision-vision-bench, inspected 29 Oct 2026](https://github.com/ai-ecoverse/decision-vision-bench) reports **0.14–0.38 seconds** for a Qwen3.5-derived Kev-0.8B image-decision model, Chrome WebGPU, q8f32, Apple M-series GPU. It uses a specialized decision head; the exact chip is unspecified. It does **not** establish stock Qwen canvas-generation latency.

Qwen’s native image/video **input** also does not supply a native canvas-writing head. The unresolved experiment is a certified, bounded transition loop with measured full-step latency—including rendering, vision encoding and output—not simply loading a VLM in Chrome.

*`out.md` was not saved: this session’s filesystem is read-only. The complete report is provided above.*