# Leap-2 Gate: Independent Prior-Art Audit (2023–Oct 2026)

| Candidate | Verdict | Closest Prior Art (Link, Date) | What Remains Open (One Line) |
| :--- | :--- | :--- | :--- |
| **C1: Crystallized Loop in Pretrained LM** | **NARROW** | [Brandoit et al., arXiv:2609.32447](https://arxiv.org/abs/2609.32447) (26 Sep 2026); [Shapiro, arXiv:2608.11233](https://arxiv.org/abs/2608.11233) (31 Jul 2026) | Installing a **universal multi-instruction register/stack VM** inside a **pretrained LM's latent loop** via codebook-snap + margin + KL loss so finite enumeration certifies unbounded-step execution without CoT. |
| **C2: Programs as Weights (Certified LoRA Codebook)** | **NARROW** | [PAW, arXiv:2607.02512](https://arxiv.org/abs/2607.02512) (2 Jul 2026); [Ouroboros, arXiv:2604.02051](https://arxiv.org/abs/2604.02051) (2 Apr 2026) | Compiling multi-step algorithms into a **discrete, finite-certified instruction codebook of low-rank deltas** executed iteratively inside a contractive loop. |
| **C3: Homomorphism Loss for Parallel-Prefix Tracking** | **KILLED** | [Brandoit et al., arXiv:2609.32447](https://arxiv.org/abs/2609.32447) (26 Sep 2026); [Pert et al., arXiv:2605.26035](https://arxiv.org/abs/2605.26035) (25 May 2026) | Nothing foundational: Brandoit et al. snap states to finite monoid $T_d$, run exact $O(\log N)$ parallel scans, and certify $N\to\infty$ on generators; Pert et al. train $O(\log N)$ reductions with associativity loss $\mathcal{L}_{\text{assoc}}$. |
| **C4: Compile Then Dissolve (ALTA/Tracr $\to$ Looped LM)** | **NARROW / OPEN** | [Tracr-Injection, arXiv:2505.10719](https://arxiv.org/abs/2505.10719) (15 May 2025); [ALTA, arXiv:2410.18077](https://arxiv.org/abs/2410.18077) (23 Oct 2024) | Distilling a **looped** compiled interpreter (ALTA/SUBLEQ) into a pretrained LM's **looped core** with a contractive snap and finite-enumeration certificate before discarding the teacher. |
| **C5: Browser-Feasible ($\le 4\text{B}$) Looped / Matrix-State LMs** | **OPEN (Target Gap)** | [ByteDance/Ouro-1.4B](https://huggingface.co/ByteDance/Ouro-1.4B) (28 Oct 2025); [Shapiro, arXiv:2608.11233](https://arxiv.org/abs/2608.11233) (31 Jul 2026) | Every open $\le 4\text{B}$ looped or linear-RNN LM drifts, cycles, or collapses after $8\text{--}64$ latent steps; **none** executes exact multi-digit arithmetic or unbounded state tracking in latent space without CoT. |

---

## Evidence per Candidate (`C1`–`C5`)

### C1: Crystallized Loop inside a Pretrained LM (`NARROW`)

1. **The theoretical pillar (attractor snap + margin + finite-enumeration certificate) is published for RNNs.**
   - **Brandoit et al., *Length-Independent State Tracking Under a Parallel Scan*** ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), **26 Sep 2026**; [site](https://julienbrandoit.github.io/length-independent-state-tracking/)).
   - **Thms. 3.1–3.3** prove length-independent finite-precision realization ($\eta$-trajectories) reduces to three 1-step conditions on disjoint attractor basins $U=\bigsqcup_{q\in Q} U_q$: **(R1) Decodable code** ($\pi\circ\iota=\mathrm{id}_Q$), **(R2) Restoration** ($\Phi_x(U)\oplus\bar{B}_\eta\subseteq U$, snapping the $\eta$-ball onto the code every step), and **(R3) Margin transition** ($\Phi_x(U_q)\oplus\bar{B}_\eta\subseteq U_{\delta_x(q)}$).
   - Their **NFSM (§6)** uses hardmax one-hot snapping $\mathrm{rd}(h)=\mathbf{1}_{\arg\max_j \mathbf{1}_j^\top h}$ trained via straight-through Gumbel-softmax. In **Props. G.2–G.3 & App. H.6**, they extract transition tables $\sigma_x$, check margins $\gamma(\theta)>2\|\Delta\|_\infty$, and run **finite BFS enumeration** over reachable $(s,x)\in Q\times\Sigma$ to certify 100% exactness for all $L\to\infty$ (verified to $L=10^6$ on $\mathbb{Z}_{16}, S_4, A_5, M_{11}$, Flip-Flop). Precursors: **BMRU** ([arXiv:2601.09495](https://arxiv.org/abs/2601.09495), **14 Jan 2026**) and **CMRU** ([arXiv:2605.11855](https://arxiv.org/abs/2605.11855), **12 May 2026**).
2. **Retrofitting a LoRA loop into Qwen with per-step supervision is published—and collapses without a snap.**
   - **Shapiro, *Retrofitting Recurrent Depth into a Pretrained Language Model*** ([arXiv:2608.11233](https://arxiv.org/abs/2608.11233), **31 Jul 2026**; [code](https://github.com/mshapiro123/recurrent-qwen-svgd)): Splits `Qwen2.5-0.5B-Instruct` into Prelude (L0–5), weight-tied Recurrent Block (L6–17), and Coda (L18–23) with a 6.01M rank-16 LoRA adapter (base frozen), supervised on per-loop pointer chasing ($N=16,24$).
   - **Limit**: Without a codebook snap or margin hinge, drift kills extrapolation past **$1.44\times\text{--}1.50\times$ supervised depth** (trained to $d=12$ on $N=24$: 97.7% at $d=12$, 70.3% at $d=18$, **10.9% at $d=22$**). Learned halting collapsed to constant depth (9.11%), and adding a second task caused catastrophic interference in 100 steps.
3. **Snapping looped states onto discrete vocabulary embeddings is published for multi-hop QA.**
   - **DiscoLoop, Fu et al.** ([arXiv:2607.00341](https://arxiv.org/abs/2607.00341), **1 Jul 2026**): Loop-1 states drift in angle ($\cos\approx 0.266$) from clean token embeddings $\mathbf{W}[b]$. Snapping $\mathbf{H}_1^{(1)}$ toward $\mathrm{Norm}(\mathbf{W}[\arg\max(\mathbf{W}\mathbf{H}_1^{(1)})])$ lifts 2-hop OOD accuracy from **8.3% to ~100%**.
4. **Contractive / fixed-point looped LMs enforce static equilibria, not multi-step state machines.**
   - **Viakhirev et al.** ([arXiv:2608.18222](https://arxiv.org/abs/2608.18222), **18 Aug 2026**), **STARS** ([arXiv:2605.26733](https://arxiv.org/abs/2605.26733), **26 May 2026**), **Fixed-Point Reasoners** ([arXiv:2606.18206](https://arxiv.org/abs/2606.18206), **18 Jun 2026**), **Attractor Models** ([arXiv:2605.12466](https://arxiv.org/abs/2605.12466), **12 May 2026**), and **SCORE** ([arXiv:2603.10544](https://arxiv.org/abs/2603.10544), **11 Mar 2026**) all drive the loop to a **single static fixed point** $F(z^*)=z^*$, preventing multi-step transitions $U_q\to U_{\delta(q)}$.
5. **Open in C1**: Combining Shapiro's LoRA-retrofitted LM (`2608.11233`) with Brandoit et al.'s attractor-snap + full-domain margin certificate (`2609.32447`) to install a **multi-instruction universal register/stack ISA** inside a pretrained LM while preserving base fluency ($L_{\text{KL}}$).

---

### C2: Programs as Weights (`NARROW`)

1. **The literal name "Program-as-Weights" and LoRA basis-codebook compilation into `Qwen3-0.6B` are taken.**
   - **PAW, Zhang et al., *Program-as-Weights: A Programming Paradigm for Fuzzy Functions*** ([arXiv:2607.02512](https://arxiv.org/abs/2607.02512), **2 Jul 2026**, NeurIPS 2026; [programasweights.com](https://programasweights.com/)): A `Qwen3-4B` compiler maps natural-language specs to mixing coefficients $\alpha_{l,m,n}^{A,B}$ over a **shared basis codebook of $N=64$ rank-64 LoRA matrices** injected into a frozen `Qwen3-0.6B` interpreter.
   - **Limit**: Single-pass "fuzzy functions" (classification, JSON repair) on a feed-forward model—no loop, no discrete transitions, no certificate.
2. **Dynamic LoRA basis modulation inside a looped Qwen block is also published.**
   - **Ouroboros, Jaber & Jaber** ([arXiv:2604.02051](https://arxiv.org/abs/2604.02051), **2 Apr 2026**; [code](https://github.com/RightNow-AI/ouroboros)): Splits `Qwen2.5-3B` into Prelude (8L), looped layer 18 ($N$ steps), and Coda (8L). Freezes SVD-initialized LoRA bases $A,B$ and trains a 0.7M Controller emitting per-step modulation $B\cdot\mathrm{diag}(z_k)\cdot A$.
   - **Limit**: Continuous LM perplexity recovery only (fails held-out WikiText when Coda is frozen); no discrete codebook or exact execution.
3. **Other neighbours**: **Mixture of LoRAs (MoL)** ([arXiv:2512.12880](https://arxiv.org/abs/2512.12880), **14 Dec 2025**, token-routed LoRA bank in recursive FFN); **PoLar** ([arXiv:2606.06574](https://arxiv.org/abs/2606.06574), **4 Jun 2026**, layer-skip/loop schedules); **Text-to-LoRA** ([arXiv:2506.06105](https://arxiv.org/abs/2506.06105), **6 Jun 2025**) & **DnD** ([arXiv:2506.16406](https://arxiv.org/abs/2506.16406), **19 Jun 2025**); **Titans** ([arXiv:2501.00663](https://arxiv.org/abs/2501.00663), **31 Dec 2024**) & **SEAL** ([arXiv:2506.10943](https://arxiv.org/abs/2506.10943), **12 Jun 2025**).

---

### C3: Homomorphism Loss for Parallel-Prefix State Tracking (`KILLED`)

- **Killed on both fronts** in May–September 2026:
  1. **Finite-monoid snap + $O(\log N)$ parallel prefix scan + generator certificate**: **Brandoit et al.** ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), **26 Sep 2026**) prove any finite-precision scan recurrence acts as a submonoid of $T_K$ ($K\le 2^b$, **Prop. 5.2**), prove affine linear RNNs (Mamba, DeltaNet, RWKV-7, DeltaProduct) realize **at most definite automata** at finite precision (**Thm. 4.1**), snap NFSM states to $d$ one-hot attractors so each token emits $\sigma_x\in T_d$ composed in $O(\log N)$ depth via integer `gather`, and **certify $N\to\infty$ exactness on generators and margins** (**Prop. G.3**).
  2. **Explicit associativity loss for $O(\log N)$ reductions**: **Pert, Alrajeh, & Russo, *MLP-LDRU*** ([arXiv:2605.26035](https://arxiv.org/abs/2605.26035), **25 May 2026**) train binary operator $\odot_\theta(h_i,h_j)$ in an $O(\log N)$ tree reduction with explicit **associativity loss** (App. G, Eqs. 10–14):
     $$\mathcal{L}_{\text{assoc}}=\mathbb{E}\big[(1-\cos(\odot_\theta(\odot_\theta(h_a,h_b),h_c),\odot_\theta(h_a,\odot_\theta(h_b,h_c))))^2\big]$$
     achieving 100% OOD length generalization on 18/21 regular/monoid tasks and lifting ListOps OOD from 56.8% to 69.3%.
  3. **Linear-RNN precursors**—**Negative-Eigenvalue Mamba** ([arXiv:2411.12537](https://arxiv.org/abs/2411.12537), **19 Nov 2024**), **DeltaProduct** ([arXiv:2502.10297](https://arxiv.org/abs/2502.10297), **14 Feb 2025**), and **RWKV-7** ([arXiv:2503.14456](https://arxiv.org/abs/2503.14456), **18 Mar 2025**)—fail on $S_4/A_5$ by $L=82\text{--}1922$ under finite-precision scans ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), Table 3).

---

### C4: Compile Then Dissolve (`NARROW / OPEN`)

1. **Feed-forward "Compile Then Dissolve" via linear map + IIT + KL is published—and fails OOD length.**
   - **Tracr-Injection, Vergara-Browne & Soto** ([arXiv:2505.10719](https://arxiv.org/abs/2505.10719), **15 May 2025**; [code](https://github.com/tvergara/tracr-injection)): Compiles RASP via `tracr`, aligns `GPT-2-large` residual streams via $P_{\text{linear}}$ ($L_{\text{ALG}}=\frac{1}{k}\sum_{i=0}^k(1-\cos(P_{\text{linear}}h_{\text{model}}^i,h_{\text{compiled}}^i))$), enforces causal usage via an **IIT orthogonal-complement roll**, preserves fluency via $L_{\text{KL}}$ on FineWeb, and **discards the compiled model at inference**.
   - **Limit**: Feed-forward only, no contractive snap or certificate, collapsing OOD (0.9% on 4-digit addition, 2.8% on $3\times$ length counting).
2. **Looped compilation (UT + SUBLEQ) exists in ALTA, but was never dissolved into an LM.**
   - **ALTA, Shaw et al.** ([arXiv:2410.18077](https://arxiv.org/abs/2410.18077), **23 Oct 2024**; [code](https://github.com/google-deepmind/alta)): Compiles parity, addition, SCAN, and a **SUBLEQ interpreter** into looped **Universal Transformers**, training MLPs from traces (§3.2) while keeping compiled attention. **App. C.1** notes linear-probe distillation without compiled parameters at inference *"is out of scope."*
3. **2026 WASM-in-Transformer systems retain compiled weights at inference.**
   - **Percepta** ([percepta.ai/blog/constructing-llm-computer](https://www.percepta.ai/blog/constructing-llm-computer), **25 Mar 2026**) and **Meridian** ([HF link](https://huggingface.co/eastlondoner/nanochat-wasm-fused-preview-01), **26 Mar 2026**) keep the compiled 2D hull-KVS / 840K-param WASM coprocessor at inference and emit explicit trace tokens.
4. **Open in C4**: Distilling a **looped** ALTA/SUBLEQ interpreter into a pretrained LM's **looped core** with a **contractive codebook snap + finite-enumeration certificate**, then discarding the teacher.

---

## Specific Questions (`Q1`–`Q4`)

### Q1: How many latent steps has any *trained* looped transformer actually run?

- **Tiny from-scratch / compiled models with hard constraints extrapolate to $10^2\text{--}10^6$ steps:**
  - **Giannou et al.** ([arXiv:2301.13196](https://arxiv.org/abs/2301.13196), **30 Jan 2023**) & **ALTA** ([arXiv:2410.18077](https://arxiv.org/abs/2410.18077), **23 Oct 2024**): Hand-compiled SUBLEQ / UTs run $10^2\text{--}10^3+$ steps.
  - **Fan et al.** ([arXiv:2409.15647](https://arxiv.org/abs/2409.15647), **24 Sep 2024**, ICLR 2025): Trained from scratch on $n$-RASP-L (Parity, Copy, Addition), extrapolating to **50–100+ loop steps**.
  - **Zhang, Hu, Peng, & Xie** ([arXiv:2607.20594](https://arxiv.org/abs/2607.20594), **22 Jul 2026**): Trained on $A_5,S_5$ word problems ($L_{\text{train}}=64$), generalizing to $L=256$ (**8–16 loop steps**).
  - **Ito, Puri, Campbell, & Ram** ([arXiv:2608.31067](https://arxiv.org/abs/2608.31067), **31 Aug 2026**): 280-param constrained UT trained on depth $\le 4$ Boolean/arithmetic trees achieves **100% accuracy to depth 11** via **hard masked attention**.
- **Pretrained or retrofitted LMs collapse or plateau after 8–64 steps:**
  - **Huginn-0125 (3.5B)** ([arXiv:2502.05171](https://arxiv.org/abs/2502.05171), **7 Feb 2025**): Trained with $r\sim\text{LogNormal}(32)$, max 128; peaks at **$r=32\text{--}64$** and settles to static/cyclic fixed points ([arXiv:2608.18222](https://arxiv.org/abs/2608.18222); [arXiv:2604.11791](https://arxiv.org/abs/2604.11791)).
  - **Ouro-1.4B / 2.6B** ([arXiv:2510.25741](https://arxiv.org/abs/2510.25741), **29 Oct 2025**): Trained at $R=4$; peaks at **$R=4\text{--}8$**, degrading at $R\ge 16$ from drift ([arXiv:2604.11791](https://arxiv.org/abs/2604.11791), Fig. 4).
  - **Shapiro's Retrofitted Qwen-0.5B** ([arXiv:2608.11233](https://arxiv.org/abs/2608.11233), **31 Jul 2026**): Supervised to depth 12; holds 70.3% at $d=18$, **collapsing to 10.9% at $d=22$**.
  - **Blunt answer**: **Zero** pretrained or retrofitted LMs execute exact multi-step programs in latent space past ~20 steps without token CoT.

### Q2: Has anyone certified a trained neural step by finite enumeration?

1. **Unbounded-length inductive certificate on a trained RNN**: **Brandoit et al.** ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), **26 Sep 2026**, Props. G.2–G.3 & App. H.6) extract the $|Q|\times|\Sigma|$ table $\sigma_x$, check margin $\gamma(\theta)/2$, and **verify by finite BFS enumeration over reachable states and generators that $c\circ\sigma_x=\delta_x\circ c$**, proving 100% exactness for all $L\in\mathbb{N}$.
2. **Exhaustive finite-input verification + Lean 4**: **Brian Naughton's trilogy**—[`verified-circuits`](https://github.com/brian-naughton/verified-circuits) (**14 Jun 2026**, $256^2=65{,}536$ inputs), [`certified-grokking`](https://github.com/brian-naughton/certified-grokking) (**2 Jul 2026**, $\mathbb{Z}_{113}$ over $113^2=12{,}769$ inputs via interval arithmetic), and [`certified-inference`](https://github.com/brian-naughton/certified-inference) (**4 Jul 2026**). Certifies a *finite input table*, not an unbounded loop.
3. **Bounded-box / terminal / DFA extraction**: **Hadad, Katz, & Bassan** ([arXiv:2602.16823](https://arxiv.org/abs/2602.16823), **18 Feb 2026**, Marabou/CROWN); **Viakhirev et al.** ([arXiv:2608.18222](https://arxiv.org/abs/2608.18222), **18 Aug 2026**, terminal margin); **Discrete Transformer, Zhang et al.** ([arXiv:2601.05770](https://arxiv.org/abs/2601.05770), **9 Jan 2026**) & **Wang et al.** ([arXiv:2601.10918](https://arxiv.org/abs/2601.10918), **16 Jan 2026**).

### Q3: Has anyone put a discrete bottleneck / VQ / Gumbel snap inside a recurrent reasoning loop?

- **Yes, in five 2026 works, though none installs a universal ISA inside a pretrained LM:**
  1. **Brandoit et al. NFSM** ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), **26 Sep 2026**): Hardmax one-hot snap $\mathrm{rd}(h)$ with straight-through Gumbel-softmax in an RNN.
  2. **De Geeter et al. BMRU** ([arXiv:2601.09495](https://arxiv.org/abs/2601.09495), **14 Jan 2026**) & **Brandoit et al. CMRU** ([arXiv:2605.11855](https://arxiv.org/abs/2605.11855), **12 May 2026**): Multi-attractor Heaviside step snaps.
  3. **DiscoLoop, Fu et al.** ([arXiv:2607.00341](https://arxiv.org/abs/2607.00341), **1 Jul 2026**): Snaps loop hidden states onto discrete vocabulary embeddings $\mathbf{W}[v]$.
  4. **Discrete Transformer, Zhang et al.** ([arXiv:2601.05770](https://arxiv.org/abs/2601.05770), **9 Jan 2026**): Temperature-annealed Gumbel-Softmax bottleneck in the residual stream.
  5. **Heuristic Latent-CoT Codebooks**: **SALR** ([arXiv:2609.20398](https://arxiv.org/abs/2609.20398), **17 Sep 2026**), **Abstract-CoT** ([arXiv:2604.22709](https://arxiv.org/abs/2604.22709), **23 Apr 2026**), and **VQLC** ([arXiv:2602.02726](https://arxiv.org/abs/2602.02726), **2 Feb 2026**).

### Q4: What happened after HRM (`2506.21734`) and TRM (`2510.04871`)?

- **Rapid tiny-model scaling on ARC/Sudoku, followed by skeptical audits:**
  - **HRM, Wang et al.** ([arXiv:2506.21734](https://arxiv.org/abs/2506.21734), **26 Jun 2025**, 27M, 40.3% ARC-1) $\to$ **TRM, Jolicoeur-Martineau** ([arXiv:2510.04871](https://arxiv.org/abs/2510.04871), **6 Oct 2025**, 2-layer 7M net, **45% ARC-1**, **87.4% Sudoku**) $\to$ **URM, Gao et al.** ([arXiv:2512.14693](https://arxiv.org/abs/2512.14693), **16 Dec 2025**, ConvSwiGLU + TBPTL, **53.8% ARC-1**, **16.0% ARC-2**) $\to$ **LoopViT, Shu et al.** ([arXiv:2602.02156](https://arxiv.org/abs/2602.02156), **2 Feb 2026**, 18M, **65.8% ARC-1**) $\to$ **Attractor Models** ([arXiv:2605.12466](https://arxiv.org/abs/2605.12466), **12 May 2026**, **91.4% Sudoku**), **GRAM, Baek et al.** ([arXiv:2605.19376](https://arxiv.org/abs/2605.19376), **19 May 2026**), and **DRM** ([arXiv:2604.18839](https://arxiv.org/abs/2604.18839), **18 Apr 2026**).
  - **Skeptical Audits**: **Ren & Liu** ([arXiv:2601.10679](https://arxiv.org/abs/2601.10679), **16 Jan 2026**) and **Neri et al.** ([arXiv:2610.26666](https://arxiv.org/abs/2610.26666), **19 Oct 2026**) show ARC gains heavily depend on **$1000\times$ task augmentations, puzzle-ID embeddings, and majority voting**.
  - **Does any variant keep an LM intact?** **No.** HRM/TRM/URM/LoopViT are grid-only encoders. TRM-inspired looped LMs—**Loopie** ([arXiv:2511.12424](https://arxiv.org/abs/2511.12424), **15 Nov 2025**), **LOTUS** ([arXiv:2602.02855](https://arxiv.org/abs/2602.02855), **2 Feb 2026**), and **Nanbeige4.2-3B** ([arXiv:2607.15269](https://arxiv.org/abs/2607.15269), **21 Jul 2026**)—retain language fluency but rely on token CoT and cannot execute long-horizon algorithms in latent space.

---

## Base-Model Table (`C5`: Browser-Feasible $\le 4\text{B}$ Checkpoints)

| Model | HuggingFace ID & Date | Params & License | Architecture & Training Loop | Test-Time Extrapolation & Failure Mode | Exact Arithmetic / State Tracking in Loop (No CoT)? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ouro-1.4B / 2.6B** (+`-Thinking`) | [`ByteDance/Ouro-1.4B`](https://huggingface.co/ByteDance/Ouro-1.4B), [`ByteDance/Ouro-2.6B`](https://huggingface.co/ByteDance/Ouro-2.6B) (**28 Oct 2025**, [arXiv:2510.25741](https://arxiv.org/abs/2510.25741)) | 1.4B, 2.6B (`apache-2.0`) | Weight-tied 24L/32L looped $R=4$ times with exit gate. | Holds to $R=4\text{--}8$; degrades at $R\ge 16$ as states drift without fixed point ([arXiv:2604.11791](https://arxiv.org/abs/2604.11791), Fig. 4). | **No.** Needs token CoT (`-Thinking`) for multi-step math; zero-CoT loop fails exact long-horizon tracking. |
| **Huginn-0125** | [`tomg-group-umd/huginn-0125`](https://huggingface.co/tomg-group-umd/huginn-0125) (**8 Jan 2025** / paper **7 Feb 2025**, [arXiv:2502.05171](https://arxiv.org/abs/2502.05171)) | 3.5B (`apache-2.0`) | Prelude(2) + Recurrent(4L$\times r$, input injection) + Coda(2); $r\sim\text{LogNormal}(32)$, max 128. | Peaks at $r=32\text{--}64$, degrades past $r=128$; settles to static/cyclic fixed points ([arXiv:2608.18222](https://arxiv.org/abs/2608.18222); [arXiv:2604.11791](https://arxiv.org/abs/2604.11791)). | **No.** States orbit on toy modular counting; multi-digit math and code execution require token CoT. |
| **Nanbeige4.2-3B** | [`Nanbeige/Nanbeige4.2-3B`](https://huggingface.co/Nanbeige/Nanbeige4.2-3B) (**21 Jul 2026**, [arXiv:2607.15269](https://arxiv.org/abs/2607.15269)) | 3.0B (`apache-2.0`) | Native depth-recurrent LM ($R=2\text{--}4$ steps/token) + RL. | Fixed shallow recurrence ($R\le 4$); unstable for deep unrolling ($R\gg 8$). | **No.** Relies on long token CoT for AIME/LiveCodeBench; loop is only a depth multiplier. |
| **Qwen2.5-0.5B / Qwen3-0.6B–4B** (+LoRA Loop) | [`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) (**27 Apr 2025**); retrofitted in [Shapiro, arXiv:2608.11233](https://arxiv.org/abs/2608.11233) (**31 Jul 2026**) & [Ouroboros, arXiv:2604.02051](https://arxiv.org/abs/2604.02051) (**2 Apr 2026**) | 0.5B–4.0B (`apache-2.0`) | Dense base; Shapiro retrofits L6–17 with 6.01M rank-16 LoRA loop supervised to $d=12$. | Un-snapped LoRA loop extrapolates to **$1.44\times\text{--}1.50\times$** ($d=18$: 70.3%), **collapsing to 10.9% at $d=22$**. | **Partial (18 hops max).** Tracks exact pointer chasing in latent space for 12–18 hops without CoT before drifting. |
| **RWKV-7 "Goose"** | [`BlinkDL/rwkv7-g1`](https://huggingface.co/BlinkDL/rwkv7-g1) (**7 Mar 2025** / paper **18 Mar 2025**, [arXiv:2503.14456](https://arxiv.org/abs/2503.14456)) | 0.1B–2.9B (`apache-2.0`) | Temporal matrix-state RNN with generalized non-symmetric delta rule. | Tracks $S_5$ short-horizon; proven by [Brandoit et al., arXiv:2609.32447](https://arxiv.org/abs/2609.32447) (Thm. 4.1) to decay/drift over unbounded length at finite precision. | **Short-horizon temporal only.** Tracks $S_5$ across tokens (not depth per token); fails at $L\ge 10^3$ without a snap. |
| **Gated DeltaNet / DeltaProduct** | [`fla-hub/delta_net-1.3B-100B`](https://huggingface.co/fla-hub/delta_net-1.3B-100B) (**27 Nov 2024**); [`linear-moe-hub/MoM-Gated-Deltanet-1.3B`](https://huggingface.co/linear-moe-hub/MoM-Gated-Deltanet-1.3B) (**28 Feb 2025**); [arXiv:2412.06464](https://arxiv.org/abs/2412.06464), [arXiv:2502.10297](https://arxiv.org/abs/2502.10297) | 0.34B–2.7B (`apache-2.0` / MIT) | Temporal Householder / gated delta-rule matrix-state recurrence. | Degrades to chance on $S_5/A_5$ by $L=266\text{--}1922$ under finite-precision scan ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), Table 3). | **Short-horizon temporal only.** No unbounded exact tracking or per-token latent depth execution. |

### Blunt Recommendation for Polyformer Leap-2

1. **Kill C3**: Brandoit et al. ([arXiv:2609.32447](https://arxiv.org/abs/2609.32447), 26 Sep 2026) and Pert et al. ([arXiv:2605.26035](https://arxiv.org/abs/2605.26035), 25 May 2026) own parallel-scan monoid snapping, generator certification, and associativity loss.
2. **Do not claim the attractor-snap + finite-enumeration theorem in isolation**: Cite Brandoit et al. (`2609.32447`) for temporal RNNs, and Shapiro (`2608.11233`) and Tracr-Injection (`2505.10719`) as un-snapped LM baselines collapsing at $1.5\times$ depth / OOD length.
3. **Target `C1 + C4` on `Ouro-1.4B` or `Qwen3-0.6B`**: Distil an ALTA/SUBLEQ looped interpreter (`C4`) into a LoRA-retrofitted or native looped LM (`C1`/`C5`) with **codebook snapping + full-domain margin + FineWeb KL**, discard the teacher, and certify the loop operator by finite enumeration to extrapolate to **$d=10{,}000+$ exact latent steps in WebGPU**.
