# REDTEAM_A: prior art for I1, I7, I11 and I6

Red-team prior-art hunt, 28 Oct 2026. All citations were checked live on 2026-10-28 (arXiv API, Crossref,
or the lab or journal page). Items I could not verify are in §6. L1–L6 are not repeated except where a
verdict depends on them.

## Verdict table

| Idea | Verdict | Who got there first (closest) | What is still genuinely ours |
|---|---|---|---|
| **I1. Exact imagination** | **PARTLY DONE, and the headline is taken** | **Agostinelli & Soltani, RLC 2024 (DeepCubeAI):** pixels of a Rubik's cube → binary latent rounded every step → 10,000-step open-loop rollouts "without accumulating any error", plan in imagination, 100% solved. **Soltani & Agostinelli, RLJ 2026 (SPAR):** the same under 16–18 visual nuisances and on real phone photos of a cube. Also Latplan (Asai et al. 2018–2022), Neural Game Engine (Bamford & Lucas 2020), GNWM "grid snapping" (Kermiche 2026). | (a) A *learned* snapped state that must carry hidden objects under partial observability (occluder, egocentric views) and stay exact for 10⁴ occluded steps; every exact precedent is fully observable (state = encode(current frame)). (b) Blind execution of 1,000+-move plans; DeepCubeAI's plans are 23–33 moves. (c) A stated finite certificate plus the blindness theorem; the certificate is close to trivial for a discrete deterministic model and is practised already on cellular automata. |
| **I7. The glass mind** | **PARTLY DONE (every component exists separately)** | Markovian bottleneck for faithful CoT (Viteri et al., ICLR 2026); context isolation per reasoning node (**CausalCoT, Dominici, McMillan, Barez et al., 22 Oct 2026**); deterministic re-execution that *provably* bounds steganographic capacity (**Rinberg et al. 2025**); "make the channel structurally absent and prove it" (ServeGuard, Sep 2026); red-team steganography methodology (Roger & Greenblatt 2023; Mathew et al. 2024; Skaf et al. 2025); forecasting intervention effects (causal abstraction, Geiger et al. 2021–23; steering side-effect forecasts, Jul 2026). Classical root: Lampson 1973 (confinement and covert channels). | A theorem that, under the pinned cache policy *and* a per-row certificate, the only information crossing ticks is the declared table state (zero excess capacity), at universal power; the plain-vs-pinned smuggler contrast with a proof behind it; long-run (10⁵-tick) prediction of activation edits inside an LLM. Writing the program stays ordinary, unmonitored thought. |
| **I11. Silent execution** | **PARTLY DONE (fast-moving, high race risk)** | Latent loops inside *pretrained* LMs that do one task step per loop: **PAR (Wang et al., 20 Oct 2026)**, **Shapiro (31 Jul 2026)**, McLeish et al. 2025, LoopUS 2026, Huginn, Ouro; programs in the input executed by fixed weights (Fixed Universal Transformers, NeurIPS 2026; Giannou et al. 2023; Percepta 2026, constructed); neurally compiled libraries inside LLaMA3 (Saldyt & Kambhampati 2024, preliminary); discrete latent reasoning tokens (DLR, Jun 2026; Abstract-CoT, Apr 2026; Token Assorted, 2025). | Three things together that no paper found does: the *same model writes* the table in context and a looped block of its own layers *reads and executes* it; the loop state is *snapped* to a finite code each iteration (PAR uses norm anchoring, LoopUS uses a gate); *exactness at 10³–10⁴ steps with a certificate*. Note that I11 works against I7: two Oct 2026 papers measure *reduced* monitorability in looped LMs. |
| **I6. Certified shortcuts / practice speed-up** | **PARTLY DONE (classical; low novelty)** | Macro-operators (Korf 1985), explanation-based generalisation (Mitchell, Keller & Kedar-Cabelli 1986), Soar chunking (Laird, Rosenbloom & Newell 1986), production compilation (Taatgen & Lee 2003), instance theory (Logan 1988); **the utility problem (Minton 1990) is B2's own kill criterion**; LLM step-skipping (Liu et al., NeurIPS 2024); neurosymbolic proceduralization (NeSyPr, NeurIPS 2025); exact multi-token jumps (CLLMs, ICML 2024); library learning (DreamCoder, PLDI 2021). | Only the narrow combination: a neural executor whose composite rows are certified against its own certified single-step rows under the pin, with exactness kept at length. For a deterministic table this is composition in the transition monoid; table size grows as \|Q\|·\|Σ\|ᵏ, which is the utility problem again. |

**Ranked by kill strength:** I1 (the snap-in-a-world-model news is two years old) > I6 (forty years old) > I7 (the parts exist; the combination and the theorem do not) > I11 (the combination is open, but PAR and Shapiro are one step away).

**New blind-spot items that matter beyond these four ideas** (none appear in L1–L6):
- Agostinelli & Soltani 2024 and SPAR 2026: the snap plus 10,000-step exactness, in a learned pixel world model.
- Nerem, Chen, Dasgupta & Wang 2025 (arXiv 2503.19173): GNNs trained to minimise a sparsity-regularised loss on a *small finite set* of shortest-path instances provably implement Bellman–Ford exactly at any size. This is a finite-check-to-all-sizes theorem for a trained network, so it is relevant to Theorem P, I4 and I8.
- Lampson 1973: the confinement problem, the origin of covert-channel analysis.
- Rinberg et al. 2025: inference verification by re-execution, with a theorem bounding steganographic exfiltration.

---

## 1. I1. Exact imagination

### 1.1 The papers that take the headline

**Agostinelli & Soltani. "Learning Discrete World Models for Heuristic Search." RLJ/RLC 2024, vol. 4, pp. 1781–1792.**
PDF https://rlj.cs.umass.edu/2024/papers/RLJ_RLC_2024_225.pdf; code https://github.com/misaghsoltani/DeepCubeAI (both live
2026-10-28). Workshop precursor: "Learning Discrete World Models for Classical Planning Problems", NeurIPS 2023 workshop,
https://mlanthology.org/neuripsw/2023/agostinelli2023neuripsw-learning/. **Read in full (methods, §5.1 model performance,
§6).**
- **Inputs.** The cube is shown as two 32×32 RGB images (three faces each). Sokoban uses 40×40 RGB; IceSlider and
  DigitJump use 64×64 RGB.
- **The snap.**
  - The encoder ends in a logistic layer rounded to {0,1}, trained with a straight-through estimator; the latent has
    400 bits for the cube.
  - The transition model predicts the next latent, and "every time the model is applied, a rounding operation is
    applied to its output to correct errors and prevent error accumulation".
  - The encoder and model are co-trained so that each is pulled towards the other's rounded output (their Eq. 2).
- **Data.** Offline random play: 10,000 episodes of 30 random actions for the cube and Sokoban, and 20 actions for
  IceSlider and DigitJump.
- **Rollouts.** 10 sequences of **10,000 random actions** (333× the training episode), reconstructed by the decoder.
  - The abstract says the model runs "for thousands of steps without accumulating any error".
  - A continuous ablation with the same architecture drifts on the cube; on the three easier domains neither model
    drifts.
- **Planning in imagination.** Q* search (a weighted A* for DQNs) solves 100% of 1,000 cube instances and 100% on
  Sokoban, IceSlider and DigitJump. Cube plans with reversed start and goal solve 99.9%. Goals are given as images and
  encoded.
- **Limits they report.** In the one failure, "an error of greater than 0.5 was made by the model during search, meaning
  rounding was unable to correct it". There is no certificate. Plans are short (mean length 22.85 on the cube, 33.12 on
  Sokoban). Domains are deterministic and fully observable.
- **Against B1.**
  - B1's demo of "10,000-action dreams at 300× the clips, the cube exact, plan and execute" is this paper's §5.1 and §5.2.
  - B1's kill clause, "if DreamerV3's categorical latents are already exact, the snap is not the news", is answered by a
    stronger fact: *this group already made the snap the news, on a pixel cube, in 2024.*

**Soltani & Agostinelli. "Stable Planning through Aligned Representations in Model-Based Reinforcement Learning" (SPAR).
Reinforcement Learning Journal 2026.** PDF https://rlj.cs.umass.edu/2026/papers/Paper20.pdf (live). **Read: cover page,
intro, related work, method.**
- The method trains the discrete world model on clean frames. An alignment network then maps noisy frames to the clean
  latent, and its output is rounded, so the noisy frame snaps to the exact clean code.
- It solves over 89% (cube) and 96% (Sokoban) of instances across 16 and 18 visual transformations: lighting,
  background, camera, blur and colour.
- It solves the cube from **real phone photographs**, never seen in training.
- Its stated principle is the same: "provided errors remain below 0.5, rounding each bit eliminates compounding errors
  in long rollouts".
- **Against B1.** This retires B1's named risk that "the encoder cannot snap a noisy first frame". For a cube, it can,
  and it is published.

**Asai & Fukunaga, "Classical Planning in Deep Latent Space: Bridging the Subsymbolic-Symbolic Boundary", AAAI-18
(arXiv 1705.00154); Asai & Muise, IJCAI 2020 (arXiv 2004.12850); Asai, Kajino, Fukunaga & Muise, JAIR (arXiv
2107.00110).**
- Latplan learns a *complete propositional PDDL action model* from unlabeled image pairs: 8-puzzle, 15-puzzle,
  Blocksworld, Sokoban and LightsOut.
- It plans in the symbolic latent space with off-the-shelf planners and returns a visualised plan.
- The Cube-Space prior makes action effects state-independent bit sets and clears, i.e. a *factored local rule table*.
- **Against B1.** This is the oldest form of "pixels in, discrete state, exact symbolic transitions, renderer out, plan
  blind". The local-rule part of the "world-model Theorem P" is Latplan's effect structure.

**Bamford & Lucas. "Neural Game Engine: Accurate learning of generalizable forward models from pixels." arXiv
2003.10520 (2020).**
- It learns forward models of 10 deterministic GVGAI games directly from pixels.
- "Many of the games' models [are] learned perfectly both in terms of pixel predictions and reward predictions".
- It generalises to level sizes it was not trained on, and its convolutional (Neural GPU) update is a local rule.

**Lucas, Dockhorn, Volz et al. "A Local Approach to Forward Model Learning: Results on the Game of Life Game." arXiv
1903.12508 (IEEE CoG 2019 submission).**
- It learns the *local cell transition function* and gets "perfect forward models by observing only a few complete
  state transitions" (lookup table, decision tree or NN).
- Learning the full-frame transition with conv autoencoders worked worse.
- **Against B1.** This is the local-row certificate in its plainest form.

**Miotti, Niklasson, Randazzo & Mordvintsev. "Differentiable Logic Cellular Automata." arXiv 2506.04912; Google blog
https://google-research.github.io/self-organising-systems/difflogic-ca/ (3 Mar 2025).**
- The model trains on a grid containing "all 512 possible" 3×3 configurations and yields a discrete circuit that
  "perfectly simulates the Game of Life".
- It then runs that circuit on larger grids. There is no formal all-grids guarantee, but the exhaustive local check is
  the whole content of a local Theorem P.

**Kermiche. "The Global Neural World Model: Spatially Grounded Discrete Topologies for Action-Conditioned Planning."
arXiv 2604.16585 (Apr 2026).** The paper claims grid "snapping" acts "as a native error-correction mechanism" that
"prevents manifold drift during autoregressive rollouts". It is a single author with no numbers in the abstract. *Abstract
only.*

### 1.2 Next tier (cite; each removes one sub-claim)

**Certificates for learned world models (2026).**
- **Wang, "Certified World Models: Predictability Across Configuration, Horizon, and Resolution"** (arXiv 2606.13092).
  - Theorem A: under exact equivariance, rollout error is invariant over the monoid of k primitive symmetries and is
    certified from the k generators.
  - The setting is continuous. It certifies an error *horizon*, not exact rollouts.
  - Related papers by the same author: 2606.24945 (conservation-law horizons) and 2607.01537 (sensing clocks).
- **Lu, Wu, Lu & Li, "World Models in Pieces: Structural Certification for General Agents"** (ICML 2026, arXiv
  2606.24842). Transition-local, entry-wise error bounds on an agent's internal world model, O(1/n)+O(δ).
- **Against I1.** Neither certifies exact rollouts, but both own the phrase "certified world model". Use different
  words.

**Exact dynamics on cellular automata.** Guo & Liu, "Why Do Conventional World Models Fail to Learn Cellular Automata?"
(arXiv 2609.39604, Sep 2026).
- A CNN predicts 96.3% of cells but completes 18.9% of rollouts.
- Fixes for locality and stability reach 99.9–100% on unseen rules.
- **Read beyond the abstract:** the rollouts are only 8 predicted frames on an 8×8 torus, there is no snapping and no
  theorem ("this work contains no mathematical proofs").
- **Against I1.** It owns "conventional world models cannot learn exact dynamics" at short horizons. It does not test
  long horizons.

**Discrete representations.**
- Meyer, White & Machado, "Harnessing Discrete Representations for Continual RL" (RLC 2024, arXiv 2312.01203).
  Multi-one-hot VQ latents give more accurate world models than continuous ones over 30-step rollouts, and the benefit
  comes from binary sparsity, not discreteness.
- Bizzaro & Serafini, "Discrete World Models via Regularization" (arXiv 2603.01748): Boolean world models without
  reconstruction, plus a training scheme robust to discrete roll-outs.
- Xu et al., "Vector-Quantized World Model" (arXiv 2610.25600, Oct 2026): discrete latent search plus feedback
  control, 100% on a physical Tower of Hanoi from short-play data.
- DreamerV2 (Hafner et al., ICLR 2021, arXiv 2010.02193); DreamerV3 (arXiv 2301.04104; Nature 2025). The DreamerV3
  hyperparameter table gives imagination horizon H = 15, and the text says prediction horizon T = 16. Checked in the
  v2 PDF.

**Explicit persistent state with a neural renderer (the B1 architecture, with the state programmed rather than learned).**
- "Programmable World Model" (Huang et al., arXiv 2609.10540, Sep 2026). An explicit persistent global state,
  "including off-screen entities", drives a video model as renderer.
- StateCraft (Venturoli, Savov, Wang, Pollefeys & Van Gool, arXiv 2610.19795, Oct 2026). An LLM-held abstract state
  conditions a video diffusion model, so actions can change parts of the state that are not currently visible.
- **Against I1.** The "hide a key, come back" demo is these papers' stated goal. Their state comes from a program or an
  LLM, not from learning.

**Object permanence and memory.**
- Traub, Becker, Otte & Butz, Loci-Looped (arXiv 2310.10372): slot-based object permanence from video, tracking
  through occlusion, approximate and short.
- iSEE (arXiv 2610.01201, Oct 2026): self-supervised slot permanence.
- WROP / PWM (arXiv 2609.28654, Sep 2026): 150 object-permanence tasks and a 16B video world model trained on them,
  scored by Elo.
- Memory Maze (Pasukonis, Lillicrap & Hafner, arXiv 2210.13383) is the standard "remember objects out of view"
  benchmark.
- R2I (Samsami et al., ICLR 2024, arXiv 2403.04253); long-context SSM video world models (Po et al., arXiv 2505.20171);
  WorldMem (Xiao et al., arXiv 2504.12369).
- **Against I1.** All of these are approximate. None claims exactness, and none goes past about 10³ steps.

**Video world models and their memory spans (background for the "why it seems impossible" slide).**
- Genie (arXiv 2402.15391).
- Genie 3 (DeepMind blog, 5 Aug 2025): consistent "for a few minutes", visual memory "as far back as one minute ago",
  720p at 24 fps.
- GameNGen (ICLR 2025, arXiv 2408.14837).
- Oasis (Decart and Etched, 31 Oct 2024, https://oasis-model.github.io/), which lists "limited memory over long
  horizons" with a 3-second figure.
- DIAMOND (NeurIPS 2024, arXiv 2405.12399), IRIS (ICLR 2023, arXiv 2209.00588), STORM (arXiv 2310.09615), TWM (ICLR
  2023, arXiv 2303.07109).
- Exposure-bias fixes: Diffusion Forcing (arXiv 2407.01392) and Self Forcing (NeurIPS 2025, arXiv 2506.08009). Neither
  certifies a rollout.
- Object-centric dynamics: C-SWM (ICLR 2020, arXiv 1911.12247), SlotFormer (ICLR 2023, arXiv 2210.05861), OCVT (ICML
  2021, arXiv 2107.09240).

**Code world models (the law lives outside the network; B3 already concedes WorldCoder).**
- WorldCoder (Tang, Key & Ellis, arXiv 2402.12275).
- PoE-World (Piriyakulkij et al., arXiv 2505.10819).
- AutumnSynth (Das, Tenenbaum, Solar-Lezama & Tavares, POPL 2023, doi:10.1145/3571249).
- GIF-MCTS (Dainese et al., NeurIPS 2024, arXiv 2405.15383).
- Code World Models for General Game Playing (Lehrach et al., DeepMind, arXiv 2510.04542).
- Mind-Studio (arXiv 2606.16070).
- **Schwoebel et al., "World-Time Compute with Verified Code World Models"** (arXiv 2609.09163, Jul 2026). Its
  synthesised-then-checked dynamics are "exact over 20-step rollouts" and answer 10× out-of-distribution probes 100%,
  while per-step LLM and MLP predictors "compound error and collapse".

**Theory already in L4.** You et al. 2026 (arXiv 2607.10362) and Vafa et al. 2024 (arXiv 2406.03689).

### 1.3 What remains, stated precisely

1. **Partial observability.** Every exact learned world model I found is Markov in the current frame: DeepCubeAI, SPAR,
   Latplan, NGE and the cellular-automaton work.
   - A snapped *history-dependent* state that keeps hidden objects exact for 10⁴ occluded steps is not in the
     literature.
   - The approximate attempts are Loci-Looped, Memory Maze agents and SSM video models.
   - This is the defensible core of I1, and it is v1's tracker with an encoder.
2. **Long blind plans.** No learned pixel world model I found executes a 1,000+-move plan open-loop. DeepCubeAI's plans
   are 23–33 moves.
3. **The certificate as a theorem.** "Every reachable (local) row correct ⇒ every rollout exact" is induction for a
   discrete deterministic model. Lucas 2019 and DiffLogic CA already check all local rows exhaustively. A Lean statement
   adds rigour, not news. The new part would be certifying *reachable* factored rows of a neural simulator in a game with
   objects and occlusion, against reality.
4. **The blindness theorem as the explanation** of why video-likelihood scaling (Genie, GameNGen) drifts while the snap
   does not. This is ours (see L4), and DeepCubeAI's continuous-versus-discrete ablation is its natural empirical
   partner.

**Required rewording.**
- Do not claim "first neural world model that does not drift" or "snap fixes compounding error".
- Say instead: "exact under occlusion, with a certificate and a theorem for why likelihood cannot get there; DeepCubeAI
  showed the fully observable case".
- The B1 48-hour arm must include a DeepCubeAI-style rounded binary latent as the baseline, not only an RSSM.

---

## 2. I7. The glass mind

### 2.1 Closest papers (read beyond the abstract where marked)

**Dominici, McMillan, Barez, Langheinrich & Gjoreski. "Causal Chain of Thought: Mitigating Attention Leakage via Context
Isolation" (CausalCoT). arXiv 2610.31639, 22 Oct 2026.** **Read: method, limitations and results.**
- The LLM first emits a DAG of sub-questions. Each node is then answered in an "isolated context window" holding only
  its direct parents' answers (a "FINDING" summary), with "no global input and no sibling branches".
- Their wording is "This Markovian structure removes attention pathways to non-parent content". Causal sensitivity of
  intermediate steps rises by 12 points on average and by up to 21.
- What they do *not* claim:
  - No formal information-flow guarantee: it "should not be interpreted as a guarantee of mechanistic faithfulness".
  - Node outputs are free text.
  - There is no steganography or smuggling experiment in the part I read.
- **Against I7.** "Isolate each step's context so the visible chain is the only carrier" was published six days ago.
  I7's distinct part is the *bitwise-certified, finite-alphabet* carrier and the proof.

**Rinberg, Karvonen, Hoover, Reuter & Warr. "Verifying LLM Inference to Detect Model Weight Exfiltration." arXiv
2511.02620 (2025).** **Read: threat model, mechanism, theorems.**
- A compromised server hides data in responses by steganography.
- The verifier re-runs prefill on logged traffic, scores each sampled token by a fixed-seed sampling likelihood, and
  accepts only tokens explainable by legitimate nondeterminism.
- Theorem 5.1 bounds exfiltration by the bits in the accepted-token sets, roughly Σ log₂|A_t(τ)|.
- On a 30B MoE model, exfiltratable information falls below 0.5% at a false-positive rate below 0.01% (abstract).
- Kezins (arXiv 2608.23375, Aug 2026) attacks it by inflating entropy.
- **Against I7.** "Deterministic, re-checkable decoding bounds the covert channel, with a theorem" is published. Under
  full determinism their bound goes to one admissible token per step, i.e. zero capacity, though they do not state that
  case cleanly. I7's pin is the same idea applied *between reasoning steps*, with the per-row certificate fixing each
  symbol's meaning.

**Viteri, Lamparth, Chatain & Barrett. "Markovian Transformers for Informative Language Modeling." arXiv 2404.18988;
ICLR 2026 (per arXiv comment).**
- All information from question to answer must pass through a bounded CoT, an autoencoder-style bottleneck.
- They argue that the KL penalty and the inductive bias of gradient descent "discourage steganographic encoding". This
  is an empirical argument, not a guarantee.

**Dahlem & Vieira. "ServeGuard: Verifiable, Bounded-Residual Confinement of Operator-Invisible Channels…" arXiv
2609.21515 (Sep 2026).**
- Instead of detecting a hidden channel, "we make it structurally absent and prove that we did", using a zero-knowledge
  proof that an adapter reads input only through monitored directions.
- The context is different (adapter supply chain), but the rhetoric is I7's.

**Lampson. "A note on the confinement problem." CACM 16(10):613–615, 1973. doi:10.1145/362375.362389 (Crossref).**
- This is the origin of covert-channel analysis. Any security reviewer will read "glass mind" as confinement of a
  deterministic process.
- Cite it, and state the result as a confinement theorem for the pinned executor.

### 2.2 Steganography and monitorability (the "why it seems impossible" literature; not in L1–L6)

**Red-team and elicitation papers.**
- Roger & Greenblatt 2023 (arXiv 2310.18512): models can be trained to use encoded reasoning. Context-aware
  paraphrasing limits the best schemes to "3 bits of information per KB".
- Mathew et al. (IJCNLP-AACL 2025 oral, arXiv 2410.03768): steganographic collusion emerges under misspecified reward,
  and paraphrasing is "not fully effective".
- Skaf et al. (NeurIPS 2025, arXiv 2506.01926): steganographic CoT is learned and generalised under process
  supervision.
- Motwani et al. (arXiv 2402.07510): secret collusion.
- Zolkowski et al. (arXiv 2507.02737); Karpov et al. (arXiv 2505.03439); Karpov, NEST (arXiv 2602.14095).
- Schulz, Fülle & Fruengel (arXiv 2609.39838, NeurIPS 2026 workshop oral): steganographic *reasoning* is far harder to
  learn than steganographic messaging.
- Rippin et al. (arXiv 2606.28425): tool use enables undetectable stegosystems.
- Codetta (arXiv 2609.28900).
- de Witt et al. (arXiv 2210.14889): perfectly secure steganography via minimum-entropy coupling, so detection is
  impossible in general when sampling is free. The pin removes the sampling freedom, which is the honest argument for
  I7.

**Measurement and theory.**
- Anwar et al. (arXiv 2602.23163): a decision-theoretic "steganographic gap".
- Anwar, Bakker et al. (arXiv 2602.18297): information-theoretic monitorability.
- Fang & Marks (arXiv 2512.01222): decoding encoded reasoning with interpretability.

**Monitorability as a safety property.**
- Korbak et al. 2025 (arXiv 2507.11473).
- Chen et al. 2025 (arXiv 2505.05410).
- Baker et al. 2025 (arXiv 2503.11926).
- Emmons et al. 2025 (arXiv 2507.05246): when CoT is computation, models struggle to evade monitors.
- Lanham et al. 2023 (arXiv 2307.13702).
- Kirchner et al. 2024 (arXiv 2407.13692).
- Factor(T,U) (Sandoval & Rushing, arXiv 2512.02157): isolated subtasks strengthen monitoring from 41% to 63% safety.

**Hidden channels in activations.** Li et al., "Your Model Is Leaking: Covert Information Transfer through LLM Residual
Streams" (arXiv 2609.27996): 91–100% recovery from injected residual codewords, with detectors near chance. This is a
real activation channel, and the pin must address it if exported activations exist.

**Predicting intervention effects (the "edit any activation, predict the next million ticks" half).**
- Causal abstraction and interchange interventions: Geiger et al., NeurIPS 2021 (arXiv 2106.02997); IIT (arXiv
  2112.00826); DAS (arXiv 2303.02536).
- Othello board edits: Li et al. (ICLR 2023, arXiv 2210.13382) and Nanda et al. (arXiv 2309.00941).
- 2026 forecasting of steering side effects: Ong et al. (arXiv 2608.11227); Duan (arXiv 2606.08365).
- All of these predict *one forward pass or one move*. None predicts long-run trajectories after an edit.

### 2.3 What remains

1. **A confinement theorem.**
   - Statement: under the pinned cache policy (program plus current (state, event), positions restarted) and a per-row
     certificate, the only information that crosses ticks is the declared state symbol, so channel capacity beyond the
     table is zero, at universal power.
   - The pieces exist (CausalCoT isolation, Rinberg determinism, Markovian bottlenecks, Lampson). The combination with a
     certificate, and the proof, do not.
   - Caveat for the paper: the channel through *which table the model writes* is open. This matches B1's own limit.
2. **The red-team contrast with a proof behind it.** The methodology is standard (Roger & Greenblatt; Mathew; Skaf). The
   novelty is "pinned: zero, provably", not "plain leaks".
3. **Long-run prediction of activation edits** in a pretrained LLM executing an automaton. This is not found. Once each
   state is certified, though, the prediction is "run the table from the flipped state"; the content is the *flip map*
   (where edits flip, and to which named state). Frame it that way, or a reviewer will call it trivial.

---

## 3. I11. Silent execution

### 3.1 Closest papers

**PAR (Wang et al., arXiv 2610.27628, 20 Oct 2026).** Already in L2 §1.3:
- a weight-tied core inside Qwen2.5-0.5B, one state per loop;
- S5 at 16× the training length;
- norm anchoring, no certificate, language not measured.

**Shapiro. "Retrofitting Recurrent Depth into a Pretrained Language Model: Installation, Extrapolation, Transfer, and
Retention at Two Parameter Budgets." arXiv 2608.11233 (31 Jul 2026). Not in L1–L6.**
- Qwen2.5-0.5B-Instruct is split into prelude, weight-tied recurrent block and coda. The retrofit uses 6M adapter
  parameters or a 180M full block.
- "The model computes one task step per loop and persists when only final answers are graded."
- It extrapolates to about 1.5× the supervised depth at 70% accuracy, and is non-inferior to the base model on an ARC
  battery at loop 1.
- **Against I11.** This is the nearest "a program step per loop inside a pretrained LM". It is not exact, does not snap
  and has no in-context program.

**Other loops in pretrained or pretrained-scale LMs.**
- McLeish et al. 2025 (arXiv 2511.07384; in L1/L2).
- LoopUS (Park et al., arXiv 2605.11011): an encoder, looped block and decoder carved from a pretrained LLM, with a
  selective gate "to mitigate hidden-state drift".
- Huginn (Geiping et al., in L1); Ouro (in L1/L2).
- Persistent latent state across tokens: Thinking States (Amos et al., arXiv 2602.08332; in L5), LIFT (Tirosh, Amos &
  Geva, arXiv 2609.38149, Sep 2026), Recirculation (Mozer et al., arXiv 2608.17981).
- Fast–slow latent recurrence for train-short, test-long (Takashiro et al., arXiv 2604.01577).
- The looped-LM literature is moving weekly: about 20 arXiv titles with "looped … language model" between 30 Sep and
  25 Oct 2026.

**The program lives in the input; fixed weights execute it.**
- Fixed Universal Transformers (Liu, Andoni & Hsu, NeurIPS 2026, arXiv 2605.31423).
- Looped Transformers as Programmable Computers (Giannou et al., arXiv 2301.13196).
- Percepta 2026 (constructed, not an LLM; L1 §1.4).
- Saldyt & Kambhampati, "Algorithmic Language Models with Neurally Compiled Libraries" (arXiv 2407.04899). Adds memory,
  registers, operations and adaptive recurrence to a LLaMA3-based transformer, with algorithms compiled into a
  differentiable library. Preliminary.

**Discrete latent reasoning (snapping thoughts to a codebook, but not executing programs).**
- DLR (Chang et al., arXiv 2606.29712).
- Abstract-CoT (Ramji, Naseem & Astudillo, arXiv 2604.22709).
- Token Assorted (Su et al., arXiv 2502.03275).

**Monitorability of looped LMs (the tension with I7).**
- Wang, Balappanawar & Zhang, "On the Chain-of-Thought Monitorability of Looped Language Models" (arXiv 2610.02741):
  task-dependent *reductions* in monitorability.
- Olszowiec et al., "Monitoring latent reasoning in looped language models" (arXiv 2610.18127).

### 3.2 What remains

- **The combination is open.** No paper found has all three of the following:
  1. the same LLM writes a program (transition table) in context, and a looped block of its own layers reads it by
     attention and executes it with no tokens emitted;
  2. the loop state is snapped to a finite code each iteration;
  3. exactness at 10³–10⁴ steps, with a certificate.
- **Race risk.** It is high. PAR (snapping is one step from norm anchoring) and Shapiro (one step per loop) each need one
  addition.
- **Partial overlap with our own record.** LATENT-1 and INSIDE already showed exact latent state in Qwen-0.5B at 4,096,
  so the claim must be "the model's own written program", not "latent exact state".
- **Pitch problem.** Silent execution is the opposite of the glass mind; looped LMs are already measured as less
  monitorable. If both I7 and I11 are kept, I11 needs the certificate to stand in for the visible trace.

---

## 4. I6. Certified multi-step shortcuts (lower priority)

**Classical: the idea and its known failure mode.**
- Korf, "Macro-operators: A weak method for learning", *Artificial Intelligence* 26:35–77 (1985).
- Mitchell, Keller & Kedar-Cabelli, "Explanation-based generalization: A unifying view", *Machine Learning* 1:47–80
  (1986). Composite rules that are *deductively* correct by construction: a certified shortcut.
- Laird, Rosenbloom & Newell, "Chunking in Soar", *Machine Learning* 1:11–46 (1986).
- Taatgen & Lee, "Production Compilation", *Human Factors* 45:61–76 (2003).
- Logan, "Toward an instance theory of automatization", *Psychological Review* 95:492–527 (1988). The race model B2
  invokes.
- **Minton, "Quantitative results concerning the utility of explanation-based learning", *Artificial Intelligence*
  42:363–391 (1990). Learned macros can slow the system down, because matching cost grows with the rule base.** This is
  exactly B2's kill condition ("wall-clock does not fall because tick cost rises", the "fan effect"). It is a 36-year-old
  result to cite and pre-register against.

**Neural and LLM.**
- Liu et al., "Can Language Models Learn to Skip Steps?" (NeurIPS 2024, arXiv 2411.01855). Models are iteratively
  refined on their own shorter, *accurate* paths and gain speed without losing accuracy. This is practice-driven
  shortcutting with a correctness filter.
- NeSyPr (Choi, Kim & Woo, NeurIPS 2025, arXiv 2510.19429). Multi-step symbolic plans are compiled into single-step LM
  inference, "akin to human knowledge compilation".
- CLLMs (Kou et al., ICML 2024, arXiv 2403.00835). Multi-token jumps whose output equals autoregressive decoding by the
  Jacobi fixed point.
- Liu et al., "Transformers Learn Shortcuts to Automata" (ICLR 2023, arXiv 2210.10749).
- DreamCoder (Ellis et al., PLDI 2021, doi:10.1145/3453483.3454080). Library learning that speeds up search with
  practice.
- Speculative decoding re-verifies each token, as B2 says.

**What remains.** A neural executor that promotes a k-event row only after it agrees with k of its own certified single
ticks, with exactness at length kept. For a deterministic table this is composition in the transition monoid. Row count
grows as |Q|·|Σ|ᵏ, so the utility problem decides the outcome. It is narrow, and a reviewer will cite EBL and Minton. I
recommend dropping it as a headline and keeping it as a measurement ("how many events fit in one certified tick").

---

## 5. Searches run (all on 2026-10-28)

**arXiv API** (`export.arxiv.org/api/query`, abstract-field Boolean queries; relevance-sorted unless stated):

*I1.*
- world model AND (compounding error OR drift) AND discrete
- world model AND exact AND long horizon
- world model AND (error-free | without drift | drift-free | no drift)
- world model AND Rubik
- world model AND (finite state | automaton) AND pixels
- object permanence AND occlusion AND long
- world model AND certif*
- world model AND verif* AND rollout
- au:Agostinelli AND world model
- discrete world model AND (heuristic | planning | search)
- world model AND (snap | snapping | error correction)
- world model AND vector quantiz* AND (drift | compounding)
- world model AND Nerode
- world model AND bisimulation AND exact
- learned simulator AND exact AND long
- world model AND object permanence AND memory
- Looping LOCI / object permanence AND slot AND video
- WorldMem
- world model AND occlusion AND memory AND consisten*
- code world model(s)
- world model AND program synthesis AND exact
- object-centric AND world model AND long-horizon
- world model AND discrete AND partially observable AND exact
- au:Asai AND Latplan / latent space / Cube-Space
- WorldCoder
- AutumnSynth
- Memory Maze
- neural game engine AND (persistent | explicit state | memory)
- Differentiable Logic Cellular Automata
- Game of Life AND neural AND (exact | all 512)
- cellular automat* AND world model
- local rule AND learned AND exact
- neural cellular automata AND extrapolat*
- Neural Game Engine
- forward model AND pixels AND unseen levels
- video world model AND (persistent | permanence) AND explicit
- object permanence benchmark
- discrete AND world model AND exact AND rollout

*I7.*
- steganograph* AND (chain of thought | reasoning) AND language model
- "encoded reasoning"
- steganograph* AND language model AND (provabl* | guarantee | capacity)
- "hidden channel" AND language model
- "covert channel" AND (language model | LLM)
- Markovian AND chain of thought AND (faithful | monitor | load-bearing | informative)
- monitorab* AND steganograph*
- interchange intervention AND (recurrent | automaton)
- causal abstraction
- predict AND effect AND activation AND intervention
- steering AND long-horizon effects
- faithful by construction
- constrained decoding AND (steganograph* | monitorab* | transparen*)
- paraphras* AND steganograph*
- factored cognition
- emergent world representation AND intervention
- title lookups for Korbak, Chen, Mathew, Motwani, Baker, Emmons, de Witt, Geiger IIT and Kirchner

*I11.*
- latent reasoning AND (vector quantiz* | codebook | discrete latent)
- looped AND language model AND (program | algorithm) AND execut* AND latent
- neurally compiled
- latent AND execution AND without tokens AND exact
- looped AND (quantiz* | discretiz* | snap)
- recurrent depth AND state tracking AND pretrained
- in-context AND looped transformer AND program
- hidden state AND interpreter AND language model
- state tracking AND (recurrence | looped | weight-tied) AND language model (date-sorted)
- latent AND program AND execut* AND recurren*
- depth-recurrent
- ti:looped AND ti:"language model" (date-sorted, last 25)
- looped AND discrete AND (perfect | exact)
- neural algorithmic reasoning AND (provabl* | guarantee) AND extrapolat*
- Nerem et al. title lookup

*I6.*
- Can Language Models Learn to Skip Steps
- CLLMs
- power law of practice AND (neural network | language model)
- macro AND action AND verified AND compos*
- automatization AND practice
- multi-step AND shortcut AND verified
- production / knowledge compilation AND language model
- learn to skip reasoning steps
- amortiz* reasoning cache
- thought cache / Buffer of Thoughts
- transition monoid AND (transformer | neural)
- skill library AND verified AND faster

**Web search** (general engine, standard and extended):
- Agostinelli and Soltani, RLC 2024
- DreamerV3 imagination horizon and drift
- Genie 3 consistency and memory
- Genie 4 (nothing found)
- Agostinelli and Soltani 2025–26 follow-ups
- provably zero-capacity steganography with deterministic decoding
- context isolation and KV reset against hidden transfer
- LLM latent execution in looped layers
- retrofitted recurrence executing in-context automata
- Coconut and state tracking at length

**Venues and pages opened directly.**
- RLJ 2024 issue page and the PDFs of papers 84 and 225; RLJ 2026 Paper 20.
- mlanthology (NeurIPS 2023 workshops).
- DeepMind Genie 3 blog.
- Oasis project page.
- Google DiffLogic CA blog.
- DeepCubeAI GitHub.
- arXiv HTML of 2610.31639 (CausalCoT), 2511.02620 (Rinberg), 2609.39604 (Guo & Liu) and 2606.13092 (Wang).
- DreamerV3 v2 PDF.
- Crossref records for Korf, Laird, Mitchell, Minton, Logan, Taatgen & Lee, DeepCubeA, DreamCoder, AutumnSynth and
  Lampson.

**Read beyond the abstract (the closest papers).**
- DeepCubeAI: methods, results and future work.
- SPAR: cover page, introduction, related work and method.
- CausalCoT: method, limitations and numbers.
- Rinberg et al.: threat model, mechanism and theorems.
- Guo & Liu: protocol and horizons.
- DreamerV3: hyperparameter table.

**Searched and empty or irrelevant (counts as CLEAR for those phrasings).**
- An exact world model under partial observability or occlusion at 10³+ steps.
- A provable zero-capacity channel under deterministic or pinned decoding for CoT.
- A looped LLM that snaps its latent state each loop.
- An LLM that executes an in-context transition table latently with exactness at length.
- Long-run (beyond one step) prediction of activation-edit effects in an LLM.

## 6. Unverified or partly verified (not used for any verdict)

- **"Genie 4".** The label appears in the navigation of DeepMind's Genie 3 blog page (fetched 2026-10-28). A web search
  found no announcement. Unverified.
- **GameNGen's "about 3 seconds" of memory** (B1's figure). I did not check it in the GameNGen paper. The 3-second
  figure I verified is on the *Oasis* page.
- **GNWM (Kermiche 2026).** Abstract only; no rollout lengths or numbers seen.
- **SPAR.** I verified the RLJ 2026 PDF (cover page says "Reinforcement Learning Journal 2026"), not the volume or page
  numbers.
- **Loci-Looped venue.** The arXiv record carries no venue comment; it may be ICML 2024 but is not checked.
- **Secondary sources not checked.** A Reddit summary of a Coconut chain-length ablation; "Kohli et al. 2026" (named in
  a web-search summary); the "History Swapping" paper; the DeepXube package paper (arXiv 2603.23873). Not opened.
- **CausalCoT appendix.** The last ~66k characters of the HTML (appendix tail) were not read, so a smuggling experiment
  there cannot be ruled out.
- **Rinberg et al. discussion section.** The last ~100k characters (Section 8 onward) were not read.
- **DiffLogic CA.** The blog claims convergence on all 512 configurations; no per-configuration table was seen.
