| Item | Verdict | Closest work, date | What remains open |
|---|---|---|---|
| **F** | **NARROW** | [Qwenputer](https://divagr.com/blog/qwenputer), 22 Oct 2026; [Schlag et al.](https://arxiv.org/abs/2102.11174), 22 Feb 2021 | LoRA-only learned register execution, without execution-trace tokens, with a sound deployed-numerics certificate. |
| **M1** | **NARROW** | [How Linear Attention Remembers](https://arxiv.org/abs/2609.33093), 27 Sep 2026 | A live, semantically meaningful paint/edit/resume interface for pretrained matrix memory. |
| **M2** | **NARROW** | [A Path to Universal NCA](https://arxiv.org/abs/2505.13058), 19 May 2025 | A certified discrete local executor integrated into a multimodal LM. |
| **M3** | **NARROW** | [Gilpin](https://arxiv.org/abs/1809.02942), 9 Sep 2018; [CellARC](https://arxiv.org/abs/2511.07908), 11 Nov 2025 | Perception-to-rule identification plus certified execution within an explicitly restricted process class. |
| **M4** | **NARROW** | [FlowVQA](https://arxiv.org/abs/2406.19237), 27 Jun 2024; [Flow2Code](https://arxiv.org/abs/2506.02073), 2 Jun 2025 | Verified image-to-state compilation and internal execution without textual reasoning. |

**Audit cutoff: 29 October 2026.** Previous gate’s table read; not reproduced. Negative findings mean **“not located.”** Results are author-reported, not independently reproduced. Mathematical objections below are this audit’s deductions, dated today.

**`out.md` could not be written: this session’s filesystem is read-only.**

**F — “The register is the state” has a direct predecessor.**

Qwenputer explicitly stores **code, data, registers and program counter in Gated DeltaNet state**. One-hot keys overwrite individual rows; one-hot queries read them; α and β are fixed to 1 for RAM. Its RISC-V implementation adds eleven compiled layers before Qwen’s layers. This kills novelty in “a computer’s addressable registers live inside Qwen3.5’s delta state.” [Announcement, 22 Oct 2026](https://divagr.com/blog/qwenputer); [repository, inspected 29 Oct](https://github.com/divagr18/qwenputer).

The distinction matters: these weights are compiled, not learned through projection-only LoRA; execution produces special trace tokens. The RISC-V driver loads firmware into state and excludes chip tokens from Qwen’s layers. The accelerated path executes the circuit’s intermediate representation. **It does not establish F’s full conjunction.** [Implementation notes, inspected 29 Oct 2026](https://raw.githubusercontent.com/divagr18/qwenputer/main/experimental/riscv/docs/rv32.md).

Schlag already presents delta updates as elementary fast-weight programming instructions. Independent erase/write control also has explicit successors: Gated DeltaNet-2 and Erase-then-Delta Attention. Renaming addresses “registers” supplies no mechanism novelty. [Schlag, 22 Feb 2021](https://arxiv.org/abs/2102.11174); [GDN-2, 21 May 2026](https://arxiv.org/abs/2605.22791); [EDA, 25 Jun 2026](https://arxiv.org/abs/2606.26560).

A particularly relevant new experiment fine-tunes hybrids on answer-only parity. Qwen3.5-4B reaches mean **0.55 at 128 flips**, versus **0.89 for OLMo-Hybrid**, after training through 64; capping OLMo’s β at 1 destroys extrapolation. This is a small, author-run experiment, but directly challenges “stock Qwen’s recurrence makes learning exact tracking straightforward.” [Agrawal, 22 Oct 2026; raw results](https://github.com/divagr18/hidden-reasoning).

The requested theoretical neighbors establish different things: negative-eigenvalue expressivity, Householder-product expressivity, REPL-trained variable tracking, and an optimization intervention. None supplies F’s certificate for a pretrained Qwen checkpoint. [Grazzi, 19 Nov 2024](https://arxiv.org/abs/2411.12537); [DeltaProduct, 14 Feb 2025](https://arxiv.org/abs/2502.10297); [Siems, 16 Feb 2026, revised 25 Jun](https://arxiv.org/abs/2602.14814); [Howe, 16 Jul 2026](https://arxiv.org/abs/2609.18966).

**The locality calculation is elementary; closing it indefinitely is the contribution.** For fixed update coefficients, unit register keys and \(G_{ij}=k_i^\top k_j\),

\[
(S'-S)k_j=(\alpha-1)Sk_j+
\beta(v-\alpha Sk_i)G_{ij}.
\]

Orthogonality eliminates write interference, **not global decay**. Small Gram entries provide one-step bounds, not arbitrary-duration correctness. You need bounded write residuals, numerical-error bounds and invariant basins for the complete transition—including control and other memory channels.

**Reject the architectural “iff” as stated.** Fixed-dimensional real state is not automatically finite; recurrent state is history-dependent. What helps is a sound finite abstraction of all behaviorally relevant state. Finite inductive proofs are not generally restricted to finite-state systems. A transformer that ignores its historical cache can be certifiable without a host. A Qwen hybrid still has attention caches, convolution state and positional machinery; pinning/windowing is an additional execution policy. Merrill’s result concerns specified SSM expressivity, not this proposed certifiability classification. [Merrill et al., ICML, 21–27 Jul 2024](https://proceedings.mlr.press/v235/merrill24a.html).

Also, Kimi’s channel-wise KDA and RWKV-7’s generalized delta dynamics require separate proofs; they are not interchangeable instances of the displayed scalar-gated equation. [Kimi Linear, 30 Oct 2025](https://arxiv.org/abs/2510.26692); [RWKV-7, 18 Mar 2025](https://arxiv.org/abs/2503.14456).

**M1 — Useful interface; weak standalone research novelty.**

The dimensions check out: Qwen3.5-0.8B has **18 recurrent layers, 16 state heads per layer, and 128×128 states**. It has 24 text layers total, correcting LEAP2’s pilot reference to “all 24 DeltaNet layers.” [Official configuration, inspected 29 Oct 2026](https://huggingface.co/Qwen/Qwen3.5-0.8B/raw/main/config.json).

Visual inspection of recurrent hidden states predates this by a decade. More decisively, September 2026 work already performs targeted edits and causal interventions on pretrained GDN memory; another paper swaps Qwen3.5 recurrent states between contexts and continues generation. [LSTMVis, 23 Jun 2016](https://arxiv.org/abs/1606.07461); [Lee et al., 27 Sep 2026](https://arxiv.org/html/2609.33093v1); [Afendulev et al., 3 Sep 2026](https://arxiv.org/abs/2609.04434).

**Not located:** the exact live matrix-painting interface proposed here. Its meaningful novelty would be reliable semantic edits with measured collateral effects. A heatmap alone is instrumentation. Rank-one updates need not look like localized strokes; arbitrary basis coordinates need not correspond to human concepts. With decay, the total state change includes a generally full-rank term.

**M2 — Drawn computation and learned local computation are established.**

Growing NCA already offers interactive damage-and-resume behavior. Springer–Kenyon studies CNNs learning Life. *A Path to Universal NCA* learns local computation over a fixed heterogeneous “hardware” scaffold, including matrix multiplication, transposition and neural-network emulation—particularly close to drawn systolic machinery. Its emulation is approximate, not certified. [Mordvintsev et al., 11 Feb 2020](https://distill.pub/2020/growing-ca/); [Springer–Kenyon, 3 Sep 2020](https://arxiv.org/abs/2009.01398); [Béna et al., 19 May 2025](https://arxiv.org/html/2505.13058v2).

ARC and broader reasoning are also occupied: task-trained NCA for ARC, and later local asynchronous NCA solving mazes, Sudoku and ARC with empirical size/rollout generalization. Training LMs on elementary-CA sequences is likewise established. [Xu–Miikkulainen, 18 Jun 2025](https://arxiv.org/abs/2506.15746); [Etcheverry et al., 28 Sep 2026](https://arxiv.org/abs/2609.36126); [Edge of Chaos, 3 Oct 2024](https://arxiv.org/abs/2410.02536).

**The certificate works only after enforcing its premises.** For a deterministic binary radius-one Moore rule, 512 neighborhoods suffice to establish local equivalence; global equivalence follows by induction, given matching boundaries and synchronous updates. Continuous hidden channels, global attention, stochastic updates or unverified image decoding invalidate that simple enumeration.

**Not located:** a multimodal LM containing the complete certified executor described here. Wireworld’s authors’ site returned HTTP 403; it was not treated as opened evidence.

**M3 — Learning rules from video is old; finite observations do not certify arbitrary processes.**

Gilpin explicitly learns CA dynamics from videos and constructs CNN representations of arbitrary finite CA rule tables. CellARC tests few-shot induction of hidden multicolor CA rules and explicitly controls neighborhood coverage. These are closer than generic video-generation demonstrations. [Gilpin, 9 Sep 2018](https://arxiv.org/html/1809.02942v2); [CellARC, 11 Nov 2025](https://arxiv.org/abs/2511.07908).

Veo 3 demonstrates zero-shot visual tasks and early reasoning, not certified million-step execution. Image-based intermediate reasoning and physical-law discovery from distorted video also predate M3. [Wiedemer et al., 24 Sep 2025](https://arxiv.org/abs/2509.20328); [Thinking with Generated Images, 28 May 2025](https://arxiv.org/abs/2505.22525); [Symbolic Pregression, 19 May 2020](https://arxiv.org/abs/2005.11212).

**Coverage is sufficient only within a known hypothesis class:** fixed alphabet, neighborhood, timing, boundaries and fully observed state. Two rules can agree on every observed frame and differ on an unseen neighborhood. Unknown hidden state or neighborhood radius makes “every neighborhood observed” itself unverified.

With those premises and exact local-rule verification, a million steps follows by induction; the number is not the breakthrough. **Not located:** one system delivering the proposed end-to-end guarantee across CA, sorting, arithmetic and cube videos.

**M4 — Image input is not the leap.**

FlowVQA already evaluates logical progression and decisions from flowchart images, including a zero-shot condition without explicit CoT prompting. Flow2Code evaluates executable-code generation from flowcharts across fifteen languages. Neither demonstrates verified compilation into recurrent state or trace-free internal interpretation. [FlowVQA, 27 Jun 2024](https://flowvqa.github.io/); [Flow2Code, 2 Jun 2025](https://arxiv.org/abs/2506.02073).

**Not located:** the complete image→internal program→certified execution pipeline. Answer-only output does not establish that pipeline. The surviving contribution requires a compiler correctness relation: the state must implement the pictured program, including arrows, operands and branch conditions.

**Qwen3.5 numerics — a serious obstruction, not a demonstrated universal kill.**

Implementation inspection dated **29 Oct 2026**:

- **HF:** \(g=-\exp(A_{\log})\,\mathrm{softplus}(a+dt_{\mathrm{bias}})\), \(\alpha=\exp(g)\), and \(\beta=\sigma(b)\). For finite real parameters, \(0<\alpha,\beta<1\); floating-point saturation can reach endpoints. The inspected fallback computes recurrent updates in fp32. Its gated RMSNorm includes epsilon, so read normalization is not perfectly scale-invariant. [HF source](https://raw.githubusercontent.com/huggingface/transformers/main/src/transformers/models/qwen3_5/modeling_qwen3_5.py).
- **FLA:** the inspected fused recurrent kernel accumulates in fp32 and allocates the returned state in fp32, even with lower-precision inputs. Output activations are cast back. [FLA source](https://raw.githubusercontent.com/fla-org/flash-linear-attention/main/fla/ops/gated_delta_rule/fused_recurrent.py).
- **Transformers.js/browser:** do not infer recurrent precision from weight precision or `kv_cache_dtype`. The inspected export lists fp16 KV caches for fp16/q4f16 and separately `mamba_ssm_dtype: float32`; that metadata does not establish every exported intermediate. Available WebGPU linear-attention kernels support fp16 or fp32 states. **Exact recurrent-state precision across the relevant shipped JS graph/kernel combinations was not established.** [Export configuration](https://huggingface.co/onnx-community/Qwen3.5-0.8B-ONNX/blob/3ce256c28db23722eef89191c5910de829c02398/config.json); [kernel contract](https://huggingface.co/kernels/webgpu-kernels/ai.onnx.LinearAttention).

**Deduction:** an untouched orthogonal register retains amplitude \(\prod_t\alpha_t\). At constant α=0.999, \(10^5\) steps leave approximately \(3.5\times10^{-44}\), already below fp32’s normal range. Keeping half its amplitude requires geometric-mean α≥0.9999931. Readout can fail much earlier through interference, casting and epsilon.

**Checkpoint-specific α distributions were not located.** Therefore neither “fp32 is fine” nor “bf16 dies around 1,000 steps” is supported. bf16 and fp32 share the normal exponent range; rounding behavior differs substantially. Persistent exact storage needs a proved invariant, exact retention, or refresh—not a favorable dtype label.