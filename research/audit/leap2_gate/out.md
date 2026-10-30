| Candidate | Verdict | Closest work, date | What remains open |
|---|---|---|---|
| **C1 Crystallized loop** | **NARROW** | [STARS](https://arxiv.org/abs/2605.26733), 26 May 2026; [Shapiro retrofit](https://arxiv.org/abs/2608.11233), 31 July 2026 | A learned general executor inside a pretrained LM, with a sound all-length certificate and measured language retention. |
| **C2 Programs as weights** | **NARROW** | [Text-to-LoRA](https://arxiv.org/abs/2506.06105), 6 June 2025; [Drag-and-Drop LLMs](https://arxiv.org/abs/2506.16406), 19 June 2025 | Certified instruction semantics and compositional correctness of generated weight programs. |
| **C3 Homomorphism loss** | **NARROW** | [MLP-LDRU](https://arxiv.org/abs/2605.26035), 25 May 2026; [Log-Depth Recurrent Language Modeling](https://arxiv.org/abs/2609.28212), 23 September 2026 | Exact, certified finite-monoid composition; associative training and logarithmic depth are already established. |
| **C4 Compile then dissolve** | **NARROW** | [InterpBench](https://arxiv.org/abs/2407.14494), 19 July 2024; [ALTA](https://arxiv.org/abs/2410.18077), 23 October 2024 | Removing the teacher while certifying the pretrained student’s recurrent executor and retaining language capability. |
| **C5 Base-model choice** | **KILLED as novelty** | [Huginn](https://arxiv.org/abs/2502.05171), 7 February 2025; [Ouro](https://ouro-llm.github.io/), 29 October 2025 | An engineering selection, not independently a new model concept. |

**Audit cutoff: 29 October 2026.** Primary pages were opened across arXiv, repositories, Hugging Face and company sites; several OpenReview URLs returned verification challenges. Negative findings mean “not located,” not proof of absence. Results below are reported evidence, not independently reproduced.

**`out.md` could not be written because this session’s filesystem is read-only. The complete report follows.**

**C1 — The conjunction survives; the components do not.**

STARS already combines recurrent-dynamics analysis, Jacobian spectral-radius regularization and randomized loop counts. Its synthetic addition model reaches reported 100% accuracy; its pretrained Ouro experiment improves depth robustness. Neither establishes an exact universal executor or exhaustive transition certificate. [STARS, 26 May 2026](https://arxiv.org/html/2605.26733v1).

Shapiro already installs a reusable, stepwise latent procedure in pretrained Qwen while testing capability retention. Thus “learned computation installed inside an intact LM” is insufficient differentiation. [Shapiro, 31 July 2026](https://arxiv.org/abs/2608.11233).

The certificate strategy also has close antecedents: finite local checking supports universal computation through extended language-model decoding. That execution uses autoregressive symbols, so it does not establish your latent-loop conjunction. [Lewandowski–Machado–Schuurmans, revised 10 February 2026](https://arxiv.org/html/2601.08061v2).

**Auditor’s mathematical objections, 29 October 2026:**

- Contractivity does **not** imply exact history independence. It can shrink historical differences without eliminating them.
- For code states \(q\), prove regions \(B_q\) satisfy \(F_a(B_q)\subseteq B_{\delta(q,a)}\), with correct decoding throughout. Checking centres alone is insufficient unless execution actually resets to them.
- A globally finite machine supports unbounded run duration, not unrestricted universal storage. Specify extensible memory, finite local access, addressing and initialization.
- “Every length” means correct finite execution prefixes; it cannot mean every program halts.
- Certify the **merged, deployed numerical implementation**, including quantization, routing, caches and halting. KL training is not a retention certificate.
- “No host clock” should mean no host-supplied algorithmic schedule. Some runtime must still iterate the block.

Related theory explicitly distinguishes semantics-preserving correction within predictive equivalence classes from destructive contraction between distinguishable states. [*What Can a Recurrent State Safely Forget?*, 20 September 2026](https://arxiv.org/abs/2609.23366).

**C2 — Generated weights are old; certified executable weights remain distinguishable.**

Text-to-LoRA generates adapters from task descriptions; Drag-and-Drop maps prompt batches to LoRA matrices. Sakana’s later demonstration turns documents into adapters. These kill “language generates useful weights,” but do not establish program-counter semantics or exact instruction execution. [T2L, 6 June 2025](https://arxiv.org/abs/2506.06105); [DnD, 19 June 2025](https://arxiv.org/abs/2506.16406); [Sakana, February 2026](https://pub.sakana.ai/doc-to-lora/).

Fast-weight programmers already use networks to modify another network’s effective weights. TTT makes the recurrent state a learned model; Titans updates neural memory at inference. None of these sources supplies the proposed finite certified instruction-delta library. [Irie–Gershman, December 2025](https://gershmanlab.com/pubs/IrieGershman26.pdf); [TTT, 5 July 2024](https://arxiv.org/abs/2407.04620); [Titans, 31 December 2024](https://arxiv.org/abs/2501.00663).

**Deduction:** certificates for individual deltas do not certify their sums, orderings or interactions with base weights. Prove composition, instruction selection and shared-state invariants. Otherwise C2 is adapter generation with a programming metaphor.

**C3 — The proposed loss has a particularly close 2026 predecessor.**

MLP-LDRU performs parallel reduction with a learned composition operator. Appendix G explicitly penalizes disagreement between \((a\circ b)\circ c\) and \(a\circ(b\circ c)\). It reports 100% sampled OOD accuracy on 18/21 regular-language tasks, with evaluation through length 500. September’s follow-up computes all prefix representations for autoregressive language modeling. [MLP-LDRU, 25 May 2026](https://arxiv.org/html/2605.26035v1); [follow-up, 23 September 2026](https://arxiv.org/abs/2609.28212).

Transformation-semigroup composition and \(O(\log N)\)-depth automaton simulation already underpin Liu et al. [ICLR 2023](https://clarabing.github.io/shortcut_automata/). Negative-eigenvalue RNNs and DeltaProduct supply adjacent representational results, rather than certificates for arbitrary trained checkpoints. [Grazzi et al., 19 November 2024](https://arxiv.org/abs/2411.12537); [DeltaProduct, 14 February 2025; revised 22 October](https://arxiv.org/abs/2502.10297).

Bisimulation losses concern behavioral similarity; convergence of a metric does not establish exact finite-monoid execution. [Zhang et al., 24 July 2025](https://arxiv.org/abs/2507.18519).

**Deduction:** checking generators suffices only after establishing the representation’s extension law. For an arbitrary learned binary operation, verify closure, identity, associativity and task correspondence—or establish them structurally. A sampled homomorphism penalty proves none of these.

**C4 — “Compile, supervise internals, discard teacher” is substantially anticipated.**

ALTA supports loops, compiled universal transformers and trace-supervised learning. InterpBench uses Strict Interchange Intervention Training to train networks whose internal computation preserves Tracr circuits while suppressing alternative computational paths. Together they strongly anticipate your training mechanism. [ALTA, 23 October 2024; revised 19 June 2025](https://arxiv.org/html/2410.18077v2); [InterpBench, 19 July 2024](https://arxiv.org/abs/2407.14494).

A further neighbor verifies a calibrated GPT-2-scale artifact over 1,280 prompts after architectural changes and program-head substitution. Its authors explicitly restrict claims to declared bounded domains. [*Towards Verifiable Transformers*, 21 May 2026; revised 29 July](https://arxiv.org/abs/2605.24033).

The surviving contribution is **certified transfer into a pretrained recurrent student**, not hidden-state distillation itself. A learned linear alignment does not automatically establish a simulation relation.

**C5 — Select by execution interface.**

Depth recurrence, token recurrence and matrix-valued memory provide different interfaces. RWKV’s state-tracking expressivity is useful, but it does not make a released language checkpoint an exact VM. Its theorem and its language-model experiments must remain separate. [RWKV-7, 18 March 2025](https://arxiv.org/abs/2503.14456).

The code-state bridge is already being studied: linear RNNs learn permutation tracking from Python REPL traces, with limitations under partially observable actions. This is not a latent general interpreter certificate. [Siems et al., 16 February 2026; revised 25 June](https://arxiv.org/abs/2602.14814).

**Q1 — Exact latent program execution over hundreds/thousands of steps?**

**No matching pretrained-LM result located.** The closest verified numerical reports are narrower:

| Work, date | Reported result | Boundary |
|---|---|---|
| [Shapiro, 31 July 2026](https://arxiv.org/abs/2608.11233) | Adapter 83.8% overall; approximately 70% through depth 18 | Learned latent procedure; neither exact nor thousands of steps |
| [STARS, 26 May 2026](https://arxiv.org/html/2605.26733v1) | 100% on synthetic four-digit addition across its reported loop sweep; loop sampling during training spans 1–100 | Small task-trained model; repeated refinement of one answer, not 100 executed instructions |
| [ALTA, revised 19 June 2025](https://arxiv.org/html/2410.18077v2) | Trace-supervised relative-position parity: 100%, trained through length 20, tested through 40 | Specialized task; compiled arithmetic and SUBLEQ are separate evidence |
| [Fan et al., 24 September 2024](https://arxiv.org/html/2409.15647v1) | Parity above 95% at 100 digits after training through 20 | Empirical generalization, not exactness |
| [Howe, 16 July 2026](https://arxiv.org/abs/2609.18966) | Removing additive injection yields median accuracy 1.00 through length 512 on specified automata | Small token-recurrent state tracker, not pretrained latent VM |

Do not combine the strongest number from one system with the architectural properties of another.

**Q2 — Finite verification implying unbounded correctness?**

**Yes, broadly; no matching C1 implementation located.**

- **Decisive older antecedent:** recursive Neural Programmer-Interpreters reduce verification to base cases and reduction rules. Addition’s verification set contains **20,181 problems** under stated input assumptions. Recursion resets local recurrent computation and external structured memory supplies scale. This kills a broad “first trained neural program certified by finite checking” claim. [Cai–Shin–Song, ICLR 2017, Appendix A.6](https://people.eecs.berkeley.edu/~dawnsong/papers/iclr_2017_recursion.pdf).
- **Within the requested window:** trained RNN-controlled systems receive sound unbounded temporal-property verification through constraint solving and invariants. This proves specified agent/environment properties, not arbitrary program interpretation. [Hosseini–Lomuscio, AAMAS May–June 2023](https://aamas.csc.liv.ac.uk/Proceedings/aamas2023/pdfs/p2382.pdf); [full-LTL extension, 4 March 2025](https://arxiv.org/abs/2503.02512).
- **Naughton requires careful reading.** *Certified Grokking* certifies 12,769 modular-addition inputs under exact-real semantics. *Verified Circuits* proves the **symbolic circuit** correct at all lengths, but circuit–network agreement only on declared finite domains, including 65,536 strings at length 16. Neither establishes unbounded correctness of the trained network. [Grokking](https://github.com/brian-naughton/certified-grokking), [Verified Circuits](https://github.com/brian-naughton/verified-circuits), both inspected 29 October 2026.
- Automata extraction is not automatically certified equivalence: sampled agreement requires a sound abstraction/equivalence argument before transferring all-word properties. [Lattice-automata extraction, 26 September 2025; corrected 10 February 2026](https://arxiv.org/abs/2509.22489).

**Q3 — A new loss making latent reasoning a finite exact machine?**

**Discrete representations and stability losses: yes. The complete guarantee: not located.**

Codebook Features already quantizes internal activations, including finite-state experiments and language models up to 410M parameters. [26 October 2023](https://arxiv.org/abs/2310.17230). Token Assorted mixes VQ latent codes with text; DLR converts rendered reasoning traces into discrete latent tokens. [5 February 2025](https://arxiv.org/abs/2502.03275); [29 June 2026](https://arxiv.org/abs/2606.29712).

These compress or discretize reasoning; they do not certify the complete recurrent state-transition system. A finite token vocabulary is insufficient when continuous caches or growing histories remain.

**Q4 — Strongest striking latent-reasoning evidence by October 2026?**

“Shocked researchers” is not measurable. Strong relevant demonstrations include:

- **HRM/TRM:** small puzzle specialists, not retained pretrained LMs. TRM reports approximately **45% ARC-AGI-1 / 8% ARC-AGI-2** with 7M parameters. [HRM, 26 June 2025](https://arxiv.org/abs/2506.21734); [TRM, 6 October 2025](https://arxiv.org/abs/2510.04871).
- **URM:** **53.8% / 16.0% pass@1**, explicitly scoped to its small-model comparison setting. [16 December 2025](https://arxiv.org/abs/2512.14693).
- **Looped Flows:** **58.8% / 12.2% pass@2**, using recurrent denoising/flow computation. Different metric from URM; not a language-preservation demonstration. [10 September 2026, Table 1](https://arxiv.org/html/2609.11801v1).
- **BDH-CQ:** company-reported **29.5% ARC-AGI-1 pass@2**, 150M parameters, $0.00070/task; latent computation with candidate-answer decoding. The announcement places general language/math extensions in future work. [Pathway, 11 August 2026](https://pathway.com/research/introducing-bdh-cq).

Huginn/Ouro are language models with recurrent computation; Shapiro directly tests retrofit retention. None of these sources supplies C1’s all-program exactness.

**Q5 — No fifth question was supplied; interpreted as the practical base choice.**

My recommendation is **Ouro-1.4B for native C1/C4**, **recurrent TinyLlama for cheaper experimentation**, and **RWKV-7 for C3 state-tracking experiments**. Treat C2 as a separate compositional-semantics project. Browser deployment and quantization require their own validation.

**Base-model table**

Model-card facts below were checked **29 October 2026**; dates identify paper/release provenance where available. “No certificate located” applies to every row.

| HF ID / provenance date | Size; licence | Test-time recurrence | Extrapolation and exactness evidence |
|---|---|---|---|
| [ByteDance/Ouro-1.4B](https://huggingface.co/ByteDance/Ouro-1.4B), [Ouro-2.6B](https://huggingface.co/ByteDance/Ouro-2.6B); 29 Oct 2025 | 1.4B / 2.6B; Apache-2.0 | Configurable `total_ut_steps`, default 4; adaptive exit | Native depth loops. More loops can degrade performance; STARS improves robustness. No certified latent arithmetic in released bases located. |
| [tomg-group-umd/huginn-0125](https://huggingface.co/tomg-group-umd/huginn-0125); 7 Feb 2025 paper | 3.5B; Apache-2.0 | Arbitrary `num_steps`; fewer than 4 discouraged | Card reports improvement to roughly 64 steps, generally plateauing thereafter. Heavy browser compute; no exact executor report located. |
| [smcleish/Recurrent-TinyLlama-3T-train-recurrence-32](https://huggingface.co/smcleish/Recurrent-TinyLlama-3T-train-recurrence-32); Nov 2025 | ~0.8B; Apache-2.0 | Configurable `num_steps`; 4/8/16/32-trained variants | Small released retrofit; no certified long-depth algorithmic extrapolation located. |
| [smcleish/Recurrent-OLMo-2-0425-train-recurrence-32](https://huggingface.co/smcleish/Recurrent-OLMo-2-0425-train-recurrence-32); Nov 2025 | ~1B; Apache-2.0 | Configurable `num_steps`; Huginn-derived runtime | Useful open retrofit; raw-text model, not instruction-tuned. No exact arithmetic report located. |
| [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct); Shapiro experiment July 2026 | 0.49B; Apache-2.0 | **Base has no native depth loop** | Shapiro’s procedure extrapolates imperfectly to depth 18. I did not verify a public retrofit checkpoint ID. |
| [RWKV/RWKV7-1.5B-20260805](https://huggingface.co/RWKV/RWKV7-1.5B-20260805); checkpoint 5 Aug 2026 | 1.5B; Apache-2.0 | Matrix-state recurrence per token; no native repeated-depth knob | Constant recurrent state. Architecture has regular-language expressivity; checkpoint correctness does not follow. |
| [linear-moe-hub/Gated-Deltanet-1.3B](https://huggingface.co/linear-moe-hub/Gated-Deltanet-1.3B); available March 2025 | 1.3B; Apache-2.0 | Token-recurrent matrix state | Research base; negative-eigenvalue/DeltaProduct results cannot automatically be transferred to these weights. |
| [Qwen/Qwen3.5-0.8B-Base](https://huggingface.co/Qwen/Qwen3.5-0.8B-Base), [4B-Base](https://huggingface.co/Qwen/Qwen3.5-4B-Base); cards checked 29 Oct 2026 | 0.8B / 4B; Apache-2.0 | Gated DeltaNet–attention hybrids; no native depth-loop knob | Relevant matrix-state substrates. Long-context support is not an exact state-tracking guarantee. |

**Browser feasibility is an estimate:** raw four-bit weights require approximately \(0.5P\) GB for \(P\) billion parameters, before scales, buffers, activations and caches. Small parameter count does not establish browser kernel support or practical latency.

**Defensible contribution claim:** “A learned executor in a pretrained depth-recurrent LM, with a checked invariant reducing arbitrary-duration execution to finite local verification, under explicit memory and numerical assumptions, with program-synthesis accuracy and language retention evaluated separately.”