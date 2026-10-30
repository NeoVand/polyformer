# From dot products to the bleeding edge

### A field guide to sequence-model architecture research, 2017–2026, for someone who has implemented attention once and wants to do research on what comes next

*Written October 2026. Everything here is cited; where a result is a preprint or a vendor claim, the text says so. Equations are kept to the ones you need, and each is followed by a sentence saying what it means. Jargon is defined the first time it appears and collected in the glossary at the end.*

---

## How to read this

You know how to write scaled dot-product attention. You can train a small GPT. You want to know what the field has learned since 2017 about what that layer can and cannot do, what has been built to go beyond it, which of those things actually work at scale, and where the open problems are. This guide is organised around five questions, one per chapter:

1. **What is attention, really?** Three readings of the same equation (a kernel smoother, an associative memory, a fast-weight programmer). Each reading has spawned a research programme, and you cannot follow the programmes without the readings. (Chapter 1)
2. **What can a fixed stack of attention layers not compute, and what can it not learn?** Circuit complexity, groups and automata, the depth question, multi-token relations, and the difference between a function being representable and being findable by gradient descent. (Chapter 2)
3. **What replaces or augments attention along the sequence?** The linear-attention and state-space revival, the delta rule, the test-time-regression view, state tracking with matrix states, and the hybrid architectures now in production. (Chapter 3)
4. **What replaces depth?** The neuroscience of fast, shallow, recurrent cortex; looped and recurrent-depth language models; tiny recursive models on ARC; test-time compute and test-time training. (Chapter 4)
5. **Where do relations among many tokens live?** Multiplicative interactions, binding and vector-symbolic architectures, higher-order attention, dense associative memories, group structure. (Chapter 5)

Chapter 6 puts the pieces together into a picture of the bleeding edge as of late 2026, lists open problems with what would count as a result, and describes how to run an architecture experiment that will survive review. Appendices contain the mathematics that the chapters lean on: finite groups and representations, circuit classes, Fourier analysis on the hypercube and parity, associative-memory capacity, and the chunked scan that makes linear recurrences fast.

A note on history. Ideas in this field rarely have one author. Where a lineage is clear (the fast-weight lineage from Schmidhuber's 1992 paper to DeltaNet; the state-space lineage from Stanford's Hazy Research lab to Mamba; the circuit-complexity lineage from Hahn to Merrill), the text follows it, because knowing who was answering whom makes the papers much easier to read.

---

## Chapter 1. Attention, three ways

### 1.1 The problem and the residual stream

A language model reads a sequence of tokens $x_1, \dots, x_n$ (pieces of words, drawn from a vocabulary of size $V$) and, at each position $t$, outputs a probability distribution over the next token. Training minimises the cross-entropy

$$
\mathcal L = -\frac{1}{n}\sum_{t=1}^{n} \log p_\theta(x_{t+1} \mid x_1, \dots, x_t),
$$

averaged over tokens. Reported in nats per token (or converted to perplexity, $e^{\mathcal L}$), this single number is the currency of the field: almost every architecture claim is a claim about reaching a lower $\mathcal L$ at the same training cost. Keep this in mind when reading Chapter 6, because a lot of what is interesting about new architectures is *not* visible in $\mathcal L$.

Inside the model, each token owns a vector $h_t \in \mathbb R^d$ called its **residual stream**. A transformer is a stack of $L$ blocks, each of which reads the residual streams, computes an update, and adds it back:

$$
h_t \leftarrow h_t + \mathrm{Attn}(h_1, \dots, h_t), \qquad h_t \leftarrow h_t + \mathrm{MLP}(h_t).
$$

The additive form (He et al., 2016; Vaswani et al., 2017) means the residual stream is a shared workspace that every layer can read from and write to; Anthropic's interpretability work made this picture precise (Elhage et al., 2021). Attention is the only operation in which positions exchange information. The MLP acts on each position alone.

### 1.2 Scaled dot-product attention

Attention (Bahdanau, Cho and Bengio, 2014, for encoder–decoder translation; Luong et al., 2015, for the dot-product form; Vaswani et al., 2017, for the self-attention transformer) gives each token three vectors by learned linear maps: a **query** $q_t = W_Q h_t$, a **key** $k_t = W_K h_t$, and a **value** $v_t = W_V h_t$. Token $t$ scores every earlier token $s \le t$ by the dot product of its query with that token's key, turns the scores into weights with a softmax, and outputs the weighted average of the values:

$$
a_{ts} = \frac{\exp\!\big(q_t^\top k_s / \sqrt{d_k}\big)}{\sum_{s' \le t} \exp\!\big(q_t^\top k_{s'} / \sqrt{d_k}\big)}, \qquad
o_t = \sum_{s \le t} a_{ts}\, v_s .
$$

In words: $a_{ts}$ is how much token $t$ listens to token $s$; the weights are positive and sum to one; the output is what it hears. The division by $\sqrt{d_k}$ keeps the logits at unit variance when $q$ and $k$ have unit-variance coordinates, so the softmax does not saturate at initialisation. The restriction $s \le t$ is the **causal mask**, which makes the model usable for next-token prediction. Several heads run in parallel with their own $W_Q, W_K, W_V$ and their outputs are concatenated and projected by $W_O$.

Three facts about cost drive the whole field:

- **Training cost is quadratic in length.** Computing all $a_{ts}$ costs $O(n^2 d)$ per head. FlashAttention (Dao et al., 2022; FlashAttention-2, 2023; FlashAttention-3, Shah et al., 2024) removed the quadratic *memory* by never materialising the $n \times n$ matrix, computing softmax online in tiles, but the arithmetic is still quadratic.
- **Decoding cost is linear in length per token.** Generating token $n+1$ requires its query to be compared with all $n$ cached keys. The cache of past keys and values (the **KV cache**) grows linearly with context, and at long context it, not the weights, dominates memory traffic. This is why inference-efficiency work (grouped-query attention, Ainslie et al., 2023; multi-head latent attention in DeepSeek-V2, 2024; sparse attention, Chapter 3) targets the KV cache.
- **The state is unbounded.** Attention keeps every past token. A recurrent network keeps a fixed-size state. Everything in Chapter 3 is a negotiation between these two.

### 1.3 Reading one: attention is a kernel smoother

Write $K(q, k) = \exp(q^\top k / \sqrt{d_k})$. Then

$$
o_t = \frac{\sum_s K(q_t, k_s)\, v_s}{\sum_s K(q_t, k_s)} ,
$$

which statisticians will recognise as the **Nadaraya–Watson estimator** (Nadaraya, 1964; Watson, 1964): a locally weighted average of the values $v_s$, with weights given by how close each key is to the query under the kernel $K$. This is "local constant regression": the estimate at $q_t$ is a constant (a weighted mean) fitted to the neighbourhood. A local constant estimate is biased whenever the values vary systematically across the neighbourhood; the standard statistical fix is **local linear regression**, fitting a line instead of a constant.

That one observation is the origin of a 2025–26 line of work: Local Linear Attention (Zuo et al., 2025) replaces the weighted mean with a weighted ridge regression around each query; Parallax (Zuo et al., 2026) replaces the solve with a learned correction $w_{ts} = a_{ts}\,[1 - \rho_t^\top (k_s - \bar k_t)]$ and reports lower loss at language-model scale, with the gain depending on the optimiser (larger under Muon than under AdamW). The weights can go negative, which a softmax cannot do. The test-time-regression framework of Wang, Shi and Fox (2025; JMLR 2026) generalises this reading to all of Chapter 3: every sequence layer is a regression solved at test time, and the choices are the weighting, the function class, and the optimiser.

### 1.4 Reading two: attention is an associative memory

An **associative memory** stores pairs (key, value) and, given a possibly noisy key, returns the matching value. The classical model is the **Hopfield network** (Hopfield, 1982): $N$ binary neurons with symmetric weights $W = \sum_\mu \xi^\mu (\xi^\mu)^\top$ summing the outer products of the stored patterns $\xi^\mu$ (this sum is the **Hebbian rule**, "neurons that fire together wire together", Hebb, 1949). The network state descends an energy $E(s) = -\tfrac12 s^\top W s$ and the stored patterns are its minima. Its capacity is about $0.138\,N$ patterns (Amit, Gutfreund and Sompolinsky, 1985): beyond that the minima merge and recall fails.

Krotov and Hopfield (2016) noticed that the capacity is set by the energy function, not by the number of neurons. Replacing the quadratic energy $-\sum_\mu (\xi^\mu \cdot s)^2$ with a higher power $-\sum_\mu F(\xi^\mu \cdot s)$, $F(x) = x^k$, gives capacity growing like $N^{k-1}$; an exponential $F$ gives exponential capacity (Demircigil et al., 2017; the exact exponent is in Lucibello and Mézard, 2024). These are **dense associative memories**. Then Ramsauer et al. (2020, "Hopfield networks is all you need", from Sepp Hochreiter's group at JKU Linz) showed that for continuous states and the energy $E(s) = -\log \sum_\mu \exp(\xi^\mu \cdot s) + \tfrac12 \|s\|^2$, one step of the update rule *is* the attention formula: the query is the state, the stored patterns are the keys, and the retrieved pattern is the softmax-weighted average of the values. Attention is a dense associative memory with exponential capacity, doing one retrieval step.

Two consequences matter later. First, "higher-order" interactions have a precise meaning in this reading: they are the degree of the energy, and what they buy is capacity (Chapter 5). Second, if attention is a one-step memory, the question "why not iterate the step?" is natural; the Energy Transformer (Hoover et al., 2023) does exactly that, and Chapter 4 returns to iteration from a different direction.

### 1.5 Reading three: attention is a fast-weight programmer

Drop the softmax and the normalisation. Then

$$
o_t = \sum_{s \le t} (q_t^\top k_s)\, v_s = \Big(\sum_{s \le t} v_s k_s^\top\Big) q_t = S_t\, q_t, \qquad S_t = S_{t-1} + v_t k_t^\top .
$$

The quantity $S_t \in \mathbb R^{d_v \times d_k}$ is a matrix that accumulates outer products of values and keys; the output is that matrix applied to the query. Jürgen Schmidhuber proposed exactly this in 1992 under the name **fast weights**: one network (the slow one, trained by gradient descent) writes the weights of another (the fast one) as outer products of its activations, and the fast network is then applied to an input. Schlag, Irie and Schmidhuber (2021) showed that **linear attention** (Katharopoulos et al., 2020) is this construction, and pointed out its weakness: a sum of outer products can store only about $d_k$ associations before they interfere, and addition alone cannot overwrite. Their fix, the **delta rule**, is the central object of Chapter 3.

The same reading, with the softmax kept, underlies the theory of **in-context learning**: a transformer given examples $(x_i, y_i)$ in its context can learn to predict $y$ for a new $x$ without any weight update. Garg et al. (2022) showed transformers can be trained to do linear regression in context; Akyürek et al. (2022) and von Oswald et al. (2023) showed that a linear attention layer can implement one step of gradient descent on the in-context least-squares loss, so that a stack of layers runs an optimiser inside the forward pass (von Oswald's term is **mesa-optimisation**). In this reading, the "weights" written by attention are the in-context estimates, and depth is the number of optimiser steps. Chapter 3's test-time-training layers, Titans, and MesaNet are what you get when you make that optimiser explicit.

### 1.6 The MLP, and the multiplicative term that quietly won

The position-wise MLP, $\mathrm{MLP}(h) = W_2\, \sigma(W_1 h)$, holds most of a transformer's parameters. Geva et al. (2021) read it as another associative memory: the rows of $W_1$ are keys matched against $h$, the columns of $W_2$ are the values retrieved, and $\sigma$ decides which values fire.

Almost every model trained since 2021 uses a **gated** variant: $\mathrm{MLP}(h) = W_2\,[\sigma(W_1 h) \odot (W_3 h)]$, where $\odot$ is the element-wise (Hadamard) product. With $\sigma = \mathrm{SiLU}$ this is **SwiGLU** (Shazeer, 2020, building on the gated linear unit of Dauphin et al., 2017). It is a second-order polynomial in $h$: a multiplicative interaction. Jayakumar et al. (2020) argued on expressivity grounds that multiplicative interactions should be everywhere, and Rumelhart, Hinton and McClelland's "sigma-pi units" (1986) are the same idea forty years earlier. The 2025 Qwen study of gated attention (Qiu et al., NeurIPS 2025 best paper) tested thirty gating variants on 1.7B dense and 15B mixture-of-experts models and found that an element-wise sigmoid gate on the attention output improves loss, stability and tolerance of high learning rates while removing attention sinks. The lesson to carry into Chapter 5: the higher-order terms that have paid in production live in the value path and the state update, as products of features, not in the attention scores.

### 1.7 Position

Attention is permutation-equivariant: without positional information it cannot tell "dog bites man" from "man bites dog". Three families of fix:

- **Absolute positions**: add a learned or sinusoidal vector per index (Vaswani et al., 2017).
- **Relative positions**: make the score depend on $t - s$. Rotary embeddings (**RoPE**, Su et al., 2021) rotate $q_t$ and $k_s$ in each 2-D plane by angles $t\theta_i$ and $s\theta_i$, so that $q_t^\top k_s$ depends only on $t - s$. Note the mechanism: a rotation by $t\theta$ followed by a rotation by $-s\theta$ is a rotation by $(t-s)\theta$, which is to say that rotations compose and the composition tracks the offset. That is a representation of the integers under addition as a group of rotations; Chapter 5 and Appendix A generalise it. ALiBi (Press et al., 2021) instead subtracts a linear penalty $m|t-s|$ from the scores.
- **No positions** (NoPE): a causal transformer can recover position from the causal mask itself (Haviv et al., 2022; Kazemnejad et al., 2023), and some hybrids in Chapter 3 drop positional encodings from their attention layers entirely, leaving order to the recurrent layers.

### 1.8 Mechanistic basics: what trained attention does

Two findings from Anthropic's interpretability team are now background knowledge for architecture work. Elhage et al. (2021) showed that attention heads compose through the residual stream into **circuits**, and Olsson et al. (2022) identified the **induction head**: a two-layer circuit (a "previous-token" head in layer one, a "match-and-copy" head in layer two) that implements "the last time I saw token A it was followed by B, so predict B". Induction heads appear abruptly during training as a phase change and account for most in-context learning in small models. Two facts to remember: induction needs two layers because the key must carry information about the *previous* token, and a cheap way to give one layer that information is a short causal convolution on keys (Primer, So et al., 2021; "token shift" in RWKV; the "short conv" that every linear-attention model of Chapter 3 includes). Arora et al.'s Zoology (2023) and Based (2024) papers from Stanford's Hazy Research lab made **multi-query associative recall** (MQAR: "many key–value pairs appear earlier; recall the value for this key") the standard diagnostic separating attention from its cheaper alternatives.

### 1.9 The scaling-law frame, and why most architecture papers do not replicate

Kaplan et al. (2020) and Hoffmann et al. (2022, "Chinchilla") established that loss follows power laws in parameters $N$ and tokens $D$, that for a fixed compute budget there is an optimal ratio (roughly 20 tokens per parameter), and that architectural shape (depth versus width) matters surprisingly little at fixed $N$. Three consequences for architecture research:

1. **Compare at equal compute, not equal parameters.** A layer that costs more must be given fewer parameters or fewer tokens.
2. **Small-scale wins often vanish.** Narang et al. (2021) tested over forty transformer modifications at T5-base scale and found almost none transferred across tasks and codebases. Tay et al. (2022) found the best architecture changes with scale. In May 2026 a Tencent group re-ran the exercise with twenty post-2021 modifications at 1.2B and 3B parameters, with a multi-seed noise floor and downstream evaluation: two cleared Bonferroni correction at 1.2B, one of those failed to train stably at 3B, and modifications to the attention output could sit within 2–3% of baseline loss while losing 6–16 downstream points (Zhao et al., 2026). The gap between loss and downstream behaviour, noted earlier by Tay and colleagues, is itself a finding.
3. **Some effects live in the exponent.** 2-simplicial attention (Roy et al., 2025, Chapter 5) reports no gain below 2B active parameters and a change in the scaling exponent above it. An experiment at one small scale cannot see that.

So the honest version of "my layer beats attention" is: at three or more scales, with the noise floor on the plot, on downstream probes as well as loss, and with the compute of every extra operation counted. Chapter 6 gives the recipe. Keep this frame in mind through Chapters 3–5, where many results are from small models and preprints.

---

## Chapter 2. What a stack of attention layers cannot do

Two different questions hide under "transformers can't do X". **Expressivity**: is there *any* setting of the weights that computes X at every input length? **Learnability**: will gradient descent on reasonable data find it? The first is answered with circuit complexity and formal languages; the second with Fourier analysis and learning theory. Confusing them is the most common error in architecture papers, in both directions: claiming a capacity limit when only training failed, and dismissing a training failure because a construction exists.

### 2.1 Circuit classes in one page

A Boolean circuit takes $n$ input bits and computes an output through gates arranged in layers; its **depth** is the number of layers and its **size** the number of gates. Three classes matter here (Appendix B has the definitions in full):

- $\mathbf{AC^0}$: constant depth, polynomial size, AND/OR/NOT gates with unbounded fan-in. Cannot compute parity of $n$ bits (Furst, Saxe and Sipser, 1984; Håstad, 1987).
- $\mathbf{TC^0}$: the same but with **majority** (threshold) gates added. Can compute parity, addition, and anything that reduces to counting. Conjectured, not proved, to be strictly smaller than the next class.
- $\mathbf{NC^1}$: logarithmic depth, polynomial size, fan-in two. Contains everything that can be computed by a balanced tree of operations, such as evaluating a Boolean formula or multiplying $n$ elements of a fixed finite group.

A transformer layer is a constant-depth circuit: the softmax is a normalised sum (a threshold-like operation), the MLP is a fixed-depth network, and nothing in the layer depends on $n$ except the length of the sums. Hahn (2020) first proved limits for hard attention (each query attends to one key), showing it cannot compute parity or match brackets at all lengths; Hao, Angluin and Frank (2022) placed hard-attention transformers inside $\mathbf{AC^0}$. For the realistic case, **log-precision** transformers (numbers carried with $O(\log n)$ bits, enough to count to $n$), Merrill and Sabharwal (2023a) proved the whole fixed-depth model is in (uniform) $\mathbf{TC^0}$, and in a companion paper (2023b) gave a logic that exactly captures what such transformers can express. Strobl et al. (2024) survey the area; Weiss, Goldberg and Yahav (2021) give a programming language, RASP, in which you can write by hand the programs a transformer can represent, which is a good way to build intuition.

What the $\mathbf{TC^0}$ bound says: if a problem is not in $\mathbf{TC^0}$ (under the standard conjecture $\mathbf{TC^0} \ne \mathbf{NC^1}$), no fixed-depth transformer solves it at every length, however wide. The canonical such problems are the **word problem for a non-solvable finite group** and, relatedly, evaluating long compositions of permutations. The next section explains what those words mean, because the same objects reappear in Chapters 3 and 5.

### 2.2 Groups, automata and Barrington's theorem

A **group** is a set with an operation that combines two elements into a third, has an identity (an element that changes nothing), gives every element an inverse (an element that undoes it), and is associative (brackets do not matter). Rotations of a shape form a group; so do permutations of $n$ objects, written $S_n$ (there are $n!$ of them); so do the integers modulo $m$ under addition, written $\mathbb Z_m$. A group is **abelian** (commutative) if the order of combination never matters, as in $\mathbb Z_m$; $S_n$ for $n \ge 3$ is not: swapping objects 1 and 2 and then 2 and 3 is a different permutation from doing those swaps in the other order. A group is **solvable** if it can be built up from abelian pieces in a precise sense (Appendix A). $S_3$ and $S_4$ are solvable; $S_5$, and its half-size subgroup $A_5$ of even permutations (the rotation group of the icosahedron, with 60 elements), are not. This fact is why quintic equations have no formula in radicals (Galois), and it is the same fact that puts $S_5$ at the boundary of transformer expressivity.

The **word problem** for a group $G$: read a sequence $g_1 g_2 \cdots g_n$ of elements and output their product (or decide whether it is the identity). For $S_5$ this is "track a permutation of five objects through $n$ swaps", which is the same as the **state tracking** problem of a finite automaton whose transitions are permutations. Barrington (1989) proved a remarkable theorem: any function in $\mathbf{NC^1}$ can be computed by a **width-5 permutation branching program**, that is, by a sequence of $S_5$ elements, each chosen by looking at one input bit, whose product is the identity exactly when the function is 1. So the $S_5$ word problem is $\mathbf{NC^1}$-complete, and solving it at all lengths with a $\mathbf{TC^0}$ model would collapse $\mathbf{TC^0} = \mathbf{NC^1}$. Barrington and Thérien (1988) showed the solvable groups are exactly those whose word problems sit in $\mathbf{ACC^0} \subseteq \mathbf{TC^0}$, so non-solvability is the exact boundary.

Krohn and Rhodes (1965) proved that every finite automaton is a cascade (a sequence where each stage's transition may depend on the earlier stages' states) of two kinds of atom: **reset automata** (each input either leaves the state alone or overwrites it with a fixed value: write, erase, keep) and **simple-group automata** (the input multiplies the state by a group element). Keep these two atoms in mind. Softmax attention, gating, and the delta rule of Chapter 3 are reset-like operations; matrix products are group-like; and the architectures that track state at the end of Chapter 3 are, in effect, cascades of the two.

Liu et al. (2022, "Transformers learn shortcuts to automata", from Microsoft Research and CMU) connected all of this to transformers. Any automaton can be simulated with $O(\log n)$ attention layers (parallel prefix product), and solvable automata admit constant-depth "shortcut" constructions built from the Krohn–Rhodes decomposition. They also showed that trained transformers find shortcuts that work in-distribution and fail to generalise to longer inputs. Merrill, Petty and Sabharwal (2024, "The illusion of state in state-space models") extended the negative result to Mamba-style state-space models: with diagonal (hence commuting) transition matrices they too are in $\mathbf{TC^0}$ and cannot track $S_5$. What breaks the barrier is non-commuting, input-dependent transition matrices, and Chapter 3 follows that thread to DeltaProduct.

### 2.3 Depth is the resource that matters

Three results from 2024–25 quantify what depth buys.

- **Multi-hop needs log depth** (Sanford, Hsu and Telgarsky, 2024): the $k$-hop induction task ("follow the pointer $k$ times") requires about $\log_2 k$ attention layers, and this matches both a construction and a lower bound. The intuition is that each layer can at best double the length of the chain a token knows about, by attending to a token that already knows a chain.
- **Log depth suffices for state tracking** (Merrill and Sabharwal, 2025, "A little depth goes a long way"): transformers whose depth grows as $\Theta(\log n)$ recognise all regular languages and solve graph connectivity, both believed impossible at fixed depth. They also argue that growing depth is a more efficient route to these abilities than growing width or adding chain-of-thought tokens, and that the predicted depth matches what is needed in practice.
- **Depth helps composition at fixed parameters** (Petty et al., 2024): trading width for depth at a fixed parameter count improves compositional generalisation, with fast-diminishing returns beyond a few layers.

Chain of thought (Wei et al., 2022) is the other way to add computation at test time. Feng et al. (2023) and Merrill and Sabharwal (2024) showed that a fixed-depth transformer allowed to write $t$ intermediate tokens can simulate $t$ steps of sequential computation, so polynomially many chain-of-thought tokens lift the model from $\mathbf{TC^0}$ to polynomial time; Li et al. (2024) make the same point for "inherently serial" problems. Chapter 4 treats the third route, looping the layers, which gives depth without tokens.

### 2.4 Relations among three or more tokens

The attention score is a function of two tokens, the query and one key. Some tasks are about three. **Match-3** (Sanford, Hsu and Telgarsky, 2023): given $n$ numbers modulo $M$, does some triple sum to zero? A one-layer attention model needs width or precision growing polynomially in $n$ to solve it, by a communication-complexity argument: any two parties who each see part of the input must exchange a lot of information, and a pairwise score cannot carry it. Peng, Narayanan and Papadimitriou (2024) used the same tool to show one-layer transformers cannot compose two functions given as lookup tables, and that the obstruction compounds with more layers. The cleanest statement of why: if the three numbers are drawn uniformly subject to summing to zero, then any one or two of them look exactly uniform, so no pairwise statistic carries any signal. Only a product of all three does.

The constructive response is **higher-order attention**: a query scores pairs of keys with a trilinear form $\langle q_t, k_s \odot k_r\rangle$, at $O(n^3)$ cost. Clift et al. (2019) introduced it as 2-simplicial attention; Sanford et al. (2023) proved one such head solves Match-3; Alman and Song (2023) showed exact higher-order attention cannot be much cheaper than cubic under standard hardness assumptions; Kozachinskiy et al. (2025) proposed Strassen attention, a sub-cubic design that adds pairwise scores along the edges of a triangle; Chakrabarti, Pitassi and Alman (2026) unified these as "poly-attention". Chapter 5 reports what happened when Meta trained 2-simplicial attention at scale.

### 2.5 Representable is not learnable

**Parity** is the cleanest example. Parity of $k$ chosen bits out of $n$ is in $\mathbf{TC^0}$ and a two-layer network can represent it, but gradient descent takes about $n^{O(k)}$ steps to find it, with the loss flat for most of that time and then dropping abruptly. Barak et al. (2022) showed the plateau is "hidden progress": a weak Fourier signal in the gradient is being amplified all along. Abbe, Boix-Adserà and Misiakiewicz (2022, 2023) gave the general law for sparse Boolean targets: the **leap** of a target is the largest number of new input coordinates that must be learned at once (for a $k$-wise parity it is $k$; for a "staircase" $x_1 + x_1x_2 + x_1x_2x_3 + \cdots$ it is 1), and SGD time scales as $n^{\text{leap}}$. The mechanism is Fourier: a degree-$k$ parity has zero correlation with every function of fewer than $k$ bits, so nothing in the gradient points toward it until all $k$ coordinates are found together (Appendix C). Staircases are learnable because each step has leap one and the earlier steps provide a path.

Abbe et al. (2024, NeurIPS, "How far can transformers reason? The globality barrier and inductive scratchpad") carried this to transformers. The **globality degree** of a task is the number of tokens that must be looked at jointly before the target becomes correlated with the input; tasks with high globality are not learned efficiently by transformers; an **agnostic scratchpad** (extra tokens with no structure) does not help; an **educated scratchpad** (intermediate steps chosen to have low globality each) breaks the barrier; and an **inductive scratchpad** (steps that each apply the same rule to the previous state) breaks it and generalises out of distribution, with reported length generalisation up to 6× on arithmetic. The practical content: when a task is representable but not learned, the first lever is intermediate supervision, not a bigger model.

**Grokking** is the same phenomenon seen from the other side. Power et al. (2022) found that small transformers trained on modular arithmetic memorise first and generalise much later. Nanda et al. (2023) reverse-engineered the generalising solution: the network represents numbers as rotations (cosines and sines of $2\pi k x / p$) and adds them by multiplying rotations, a Fourier algorithm. Chughtai, Chan and Nanda (2023) showed the same for non-abelian groups: networks trained on group multiplication learn the group's irreducible representations (Appendix A) and multiply matrices; Stander et al. (2024) and Wu et al. (2024) refine and partly reconcile the account. Delétang et al. (2023) showed empirically that length generalisation of transformers and RNNs lines up with the Chomsky-hierarchy position of the task, with transformers failing on exactly the counting and state-tracking tasks the theory predicts.

### 2.6 What to take from this chapter

- Fixed-depth attention is a $\mathbf{TC^0}$ model. The things it provably cannot do at all lengths are the group-like ones: track a non-solvable automaton, multiply permutations, follow long chains. Everything else is a question about learnability.
- Depth (or loops, or chain-of-thought tokens) is how a transformer gets past $\mathbf{TC^0}$; log depth is enough for state tracking and multi-hop, and depth is the cheapest of the three.
- Pairwise scores cannot see a relation whose lower-order statistics vanish; a product over the tokens can.
- Learnability is governed by leap/globality: representable targets with high leap are found slowly or not at all, and the cure is intermediate structure (curriculum, scratchpad, deep supervision, or a native term that lowers the leap).

---

## Chapter 3. Along the sequence: linear attention, the delta rule, and matrix-valued state

This is the longest chapter because it is the lineage that produced the architectures now shipping. It is also the one where the history helps most, because the same equation was discovered four times under four names.

### 3.1 The lineage, briefly

- **1990s, IDSIA (Schmidhuber).** Fast weights (1992): one network writes another's weights as outer products of activations. The LSTM (Hochreiter and Schmidhuber, 1997) solves the vanishing-gradient problem of recurrent networks with gated memory cells and is the dominant sequence model until 2017.
- **2014–2017, Montréal and Google.** Attention (Bahdanau et al., 2014) and then the transformer (Vaswani et al., 2017) replace recurrence with parallel all-pairs comparison; training becomes fully parallel over the sequence, which is what made scale possible.
- **2020, EPFL/Idiap and Google.** Linear attention (Katharopoulos et al., 2020; Choromanski et al.'s Performer, 2020, with random features for the softmax kernel) removes the softmax so that the sum over the past can be accumulated as a fixed-size state, giving $O(n)$ training and $O(1)$ per-token decoding. Quality lagged softmax noticeably.
- **2021, IDSIA.** Schlag, Irie and Schmidhuber show linear attention is the 1992 fast-weight programmer and that its additive memory has a capacity limit; they introduce the delta-rule update (**DeltaNet**) to overwrite instead of add.
- **2021–2023, Stanford Hazy Research (Christopher Ré, Albert Gu, Tri Dao).** Structured state-space models: S4 (Gu, Goel and Ré, 2021) treats the sequence as a continuous-time linear system with carefully initialised dynamics; H3 and Hyena follow; **Mamba** (Gu and Dao, 2023) makes the dynamics input-dependent ("selective") and writes a hardware-aware scan, matching transformers on language at 1–3B scale. Tri Dao's FlashAttention (2022) is the other half of this lab's influence.
- **2023, Microsoft, MIT/CMU.** RetNet (Sun et al., 2023) and Gated Linear Attention (Yang, Wang, Shen, Panda and Kim, 2023) put learned decay gates into linear attention; RWKV (Peng et al., 2023) does the same from the RNN side as a community project.
- **2024, MIT/CMU and Princeton.** Yang et al. parallelise DeltaNet training over sequence length with a chunked algorithm (NeurIPS 2024); Dao and Gu's Mamba-2 (2024) proves state-space models and linear attention are the same family ("structured state-space duality"); Yang, Kautz and Hatamizadeh (NVIDIA, ICLR 2025) combine the delta rule with a forgetting gate: **Gated DeltaNet**. Songlin Yang's flash-linear-attention library becomes the shared implementation base for the field.
- **2024–2025, Freiburg/Hutter lab, IIT, and others.** Grazzi et al. (ICLR 2025) show that allowing negative eigenvalues in the transition unlocks state tracking; Siems et al. (NeurIPS 2025) generalise with products of Householder reflections (**DeltaProduct**); Yang et al. (2025) put accumulated Householder transforms into attention as a position encoding (**PaTH**).
- **2024–2026, Google.** Behrouz et al.'s Titans (2024), Miras (2025), Atlas (2025) and Nested Learning (2025); von Oswald et al.'s MesaNet (2025); the test-time-regression framework from Wang, Shi and Fox (Stanford, 2025). These treat the recurrent state as an explicitly optimised memory.
- **2025–2026, production.** Hybrids with a small fraction of attention layers ship from AI21 (Jamba), NVIDIA (Nemotron-H, Nemotron 3), Alibaba (Qwen3-Next, with Gated DeltaNet), Moonshot (Kimi Linear, with Kimi Delta Attention), and others; MiniMax publicly abandons its linear-attention hybrid for full attention; Gated DeltaNet-2 and Mamba-3 appear in 2026.

The rest of this chapter explains the mathematics these groups were arguing about.

### 3.2 Linear attention and the capacity problem

Replace $\exp(q^\top k)$ by $\phi(q)^\top \phi(k)$ for some feature map $\phi$ (the identity, a positive random-feature map, or a learned one). Then, as in §1.5,

$$
S_t = S_{t-1} + v_t\, \phi(k_t)^\top, \qquad o_t = S_t\, \phi(q_t) ,
$$

with a normaliser if desired. The state $S_t$ is a $d_v \times d_k$ matrix, fixed in size whatever $n$ is. Decoding costs $O(d_v d_k)$ per token and no KV cache. Training can be done either as a scan (sequential) or, because the sum is linear, as a matrix product over chunks (Appendix E), which is what makes it fast on GPUs.

The problem is interference. $S_t$ is a sum of outer products. Reading it with $\phi(q)$ returns $\sum_s v_s\, \phi(k_s)^\top \phi(q)$: the value you want plus every other value weighted by its key's overlap with the query. With $d_k$-dimensional keys only about $d_k$ keys can be orthogonal, so past that many associations recall degrades, and there is no way to remove an association once written. This is the Schlag–Irie–Schmidhuber capacity limit, and it is why early linear attention lost badly on recall-heavy benchmarks (Arora et al.'s Zoology analysis, 2023, documented the gap on MQAR).

### 3.3 The delta rule, and the test-time-regression view

The fix is to write what is *missing*, not what is new. Before adding $v_t k_t^\top$, read what the memory currently returns for $k_t$, namely $S_{t-1} k_t$, and add the difference:

$$
S_t = S_{t-1} + \beta_t\,(v_t - S_{t-1} k_t)\, k_t^\top = S_{t-1}\,(I - \beta_t k_t k_t^\top) + \beta_t\, v_t k_t^\top .
$$

This is the **delta rule** (Widrow and Hoff, 1960, in the context of adaptive filters; Schlag et al., 2021, in this context). The second form is the one to stare at: the old state is multiplied by $I - \beta_t k_t k_t^\top$, which for $\beta_t = 1$ and unit $k_t$ is a projection that erases whatever the memory stored along $k_t$, and then the new association is written. The transition is no longer the identity; it is an input-dependent matrix. That single change is responsible for most of what follows.

Why it is a regression. Minimising the in-context least-squares loss $\tfrac12 \sum_{s \le t} \|S k_s - v_s\|^2$ by one step of online gradient descent on the newest example gives exactly the delta update. This is the content of Wang, Shi and Fox's framework (2025): linear attention is one gradient step on an unregularised sum (which is why it interferes), the delta rule is online gradient descent, gated variants add a weight decay (forgetting), and softmax attention is the kernel-regression solution with a particular weighting. Choosing a different regressor or optimiser gives the other members of the family:

- **Titans** (Behrouz, Zhong and Mirrokni, 2024): a deep (MLP) memory updated by gradient descent with momentum at test time, plus a "surprise"-based gate.
- **Test-time-training layers** (Sun et al., 2024): the hidden state *is* a small model's weights, updated by self-supervised gradient steps on the context.
- **MesaNet** (von Oswald et al., 2025): solve the ridge-regression problem to optimality at every step using a stable chunkwise conjugate-gradient scheme, the explicit version of the mesa-optimisation that von Oswald et al. (2023) found transformers learn implicitly.
- **Atlas** (Behrouz et al., 2025) optimises the memory over a window of recent tokens rather than the latest one (the "Omega rule") and raises capacity with polynomial feature maps on keys; the same group's Miras (2025) treats the loss used to write memory ("attentional bias") and the retention rule as design axes, and Nested Learning (2025) extends the picture to the optimiser itself as a memory updated at a slower rate.
- **Local linear attention and Parallax** (Zuo et al., 2025, 2026) are the softmax-side members: keep the kernel weights, upgrade the regressor from a constant to a line (§1.3).

Once you see the family this way, the design questions become explicit: what loss does the memory minimise, with what feature map, what forgetting, and how many optimiser steps per token.

### 3.4 Gates, decay, and the chunkwise algorithm

A memory that never forgets is overrun by the past. RetNet, GLA and Mamba put a decay in the transition: $S_t = \alpha_t S_{t-1} + \ldots$ with $\alpha_t \in (0,1)$ scalar (per head) or diagonal (per channel). **Gated DeltaNet** (Yang, Kautz and Hatamizadeh, 2024) combines decay with the delta rule, $S_t = \alpha_t\, S_{t-1}(I - \beta_t k_t k_t^\top) + \beta_t v_t k_t^\top$, and was the first linear model to match or beat Mamba-2 and DeltaNet across language, recall and length extrapolation at 1.3B scale. Kimi Delta Attention (Moonshot, 2025) makes the decay channel-wise again while keeping the delta rule; Gated DeltaNet-2 (2026) separates the "erase" gate on the key side from the "write" gate on the value side, arguing that one scalar had been forced to carry two decisions; RWKV-7 (Peng et al., 2025) arrives at a generalised delta rule from the RNN side.

All of these train in parallel over the sequence. The trick (Appendix E): split the sequence into chunks of length $C$; within a chunk, the output is a small quadratic-attention computation; across chunks, the state is carried by a matrix product. The transition $\prod (I - \beta k k^\top)$ over a chunk is a product of rank-one updates, which Yang et al. (2024) write compactly with the WY representation of Householder products, so the whole thing is a few dense matrix multiplications. Wall-clock parity with FlashAttention at short context, and linear scaling beyond, is what made the family practical; without the kernels none of this would have shipped.

### 3.5 State tracking: what the transition matrix must look like

Here Chapter 2 pays off. The recurrent state is multiplied each step by a matrix $A_t$. The group of matrices that $A_t$ can range over decides what the layer can track (Appendix A explains representations: a group element "acts" on a state by a matrix, and products of elements correspond to products of matrices).

- **Diagonal transitions** (Mamba, GLA, RetNet) commute, so $A_1 A_2 = A_2 A_1$ and the state can only know *which* inputs arrived, never in what order. Merrill, Petty and Sabharwal (2024) prove such models are in $\mathbf{TC^0}$ and fail $S_5$; empirically they fail parity-like tasks at length.
- **Positive-eigenvalue rank-one updates** (DeltaNet with $\beta \in (0,1)$) can project but cannot reflect. Grazzi et al. (2025) showed that extending to $\beta \in (0,2)$, so that $I - \beta k k^\top$ has an eigenvalue in $(-1, 1)$ and can flip the sign along $k$, unlocks parity and modular counting in one layer and more generally the word problems of groups generated by reflections.
- **Products of Householder reflections** (DeltaProduct, Siems et al., 2025): take $n_h$ delta steps per token, so $A_t = \prod_{j=1}^{n_h} (I - \beta_{t,j} k_{t,j} k_{t,j}^\top)$. Every orthogonal matrix in $d$ dimensions is a product of at most $d$ reflections (Cartan–Dieudonné), so with enough factors the transition can be any rotation or reflection. The paper proves one layer with $n_h = n - 1$ tracks $S_n$, and reports better length extrapolation on language at 1.3B. A 2026 result sharpens the boundary from the other side: a single layer of DeltaProduct with $n_h \le 3$, or of Kimi Delta Attention, cannot track $S_5$ with any finite number of heads, by a spectral argument (each head's transition has at most one complex eigenvalue pair on the unit circle, and the commutator of two such rotations has order dividing 10, while $S_5$ needs a commutator that is a 3-cycle); the same paper, Complex KDA, shows that letting the channel-wise gates range over $[-1,1]$ and $\beta$ over $[0,2]$ gives each head a 2-D rotation and reaches the expressivity of DeltaProduct with $n_h = 2$ at diagonal-plus-rank-one cost. Mamba-3 (ICLR 2026) adds complex-valued state and a multi-input multi-output readout for the same reason and reports gains over Gated DeltaNet at 1.5B.
- **Accumulated Householders inside attention** (PaTH, Yang et al., 2025): instead of a recurrent state, modify the attention *score* so that the key is transported through the product of per-token Householder matrices between its position and the query's; this is a data-dependent generalisation of RoPE (which is a fixed rotation per offset) and gives attention state-tracking ability it otherwise lacks.

The pattern, in Krohn–Rhodes terms: the delta rule is the reset atom (write, erase along a direction), and the Householder products are the group atom (rotate, reflect). Architectures that have both, with the content of the token choosing which, are the ones that track state. A 2026 paper, "Rational Transductors", builds exactly this split explicitly, pairing attention (the aperiodic part) with a matrix-valued recurrence derived from weighted automata (the group part).

Two caveats from the same literature. Expressivity is at *some* weights; Siems et al. and Grazzi et al. both report that training finds the constructions on synthetic word problems but needs care with initialisation and curriculum, and Liu et al. (2022) report that transformers trained on automata often learn shortcuts instead. And "one layer tracks $S_5$" is a statement about a sequential scan whose depth is $n$; the circuit-complexity bounds are not violated, the computation has simply been moved into the recurrence.

### 3.6 Hybrids in production, and one public retreat

Pure linear models lose to attention on exact recall over long contexts (Jelassi et al., 2024, "Repeat after me"; the MQAR results above) because a fixed-size state cannot hold an arbitrary number of arbitrary key–value pairs. The practical answer since 2024 is a **hybrid**: mostly linear or state-space layers, with a few full-attention layers for retrieval.

- **Jamba** (AI21, 2024): Mamba and attention interleaved roughly 7:1, with mixture-of-experts MLPs. Samba (Microsoft, 2024) interleaves Mamba with sliding-window attention; Hymba (NVIDIA, 2024) runs attention and Mamba heads in parallel in each layer.
- **Nemotron-H** (NVIDIA, 2025): about 8% attention layers (4 of 52 in the 8B model, 10 of 118 in the 56B), the rest an even split of Mamba-2 and MLP layers; Nemotron 3 (late 2025) keeps the Mamba-2 + MoE recipe with a few attention layers.
- **Qwen3-Next** (Alibaba, September 2025): 48 layers in the pattern (3 × Gated DeltaNet → 1 × gated attention), 80B total and about 3B active parameters, 512 experts; reported to beat Qwen3-32B at under a tenth of the training cost with much higher long-context throughput (vendor claims).
- **Kimi Linear** (Moonshot, October 2025): 3:1 Kimi Delta Attention to multi-head latent attention, 48B total / 3B active, 1M-token context; the attention layers carry no positional encoding, leaving order entirely to the KDA layers.
- **Sliding-window hybrids**: Gemma 3 (Google, 2025) alternates local (sliding-window) and global attention 5:1; GPT-OSS (OpenAI, 2025) alternates banded and dense attention. These keep attention everywhere but make most of it cheap.
- **Sparse attention** is the other route to cheap long context: DeepSeek's Native Sparse Attention (2025) and the "lightning indexer" of DeepSeek Sparse Attention in V3.2 (late 2025), where a tiny indexer scores past tokens and full attention runs only over the top-$k$; Moonshot's MoBA (2025) is block-sparse. These reduce the $O(n^2)$ to $O(nk)$ without changing what attention computes.

And the counter-example. MiniMax trained its 456B MiniMax-01 (January 2025) with a 7:1 "lightning attention" hybrid, then, for MiniMax-M2 (October 2025), returned to full attention. Their public explanation: the hybrid matched full attention on standard benchmarks at small scale but showed "clear deficits in complex, multi-hop reasoning" at larger scale, the benchmarks were "lossy" measures that hid this, and "no efficient attention variant has yet demonstrated stable, superior performance over full attention in real-world industrial deployments." Read beside the Tencent replication study (§1.9), this is the state of play: hybrids are shipping and are real, but the burden of proof on multi-hop reasoning at scale has not been fully discharged, and loss alone does not discharge it.

### 3.7 What to take from this chapter

- Linear attention is a fast-weight memory; its state is a matrix; the delta rule makes the transition input-dependent and non-identity, which is both a capacity fix and a state-tracking fix.
- Every sequence layer is a regression solved at test time; pick the loss, the regressor, the forgetting and the optimiser.
- What the transition matrix can be (diagonal, rank-one with signed eigenvalues, products of reflections, full rotations) decides exactly which finite groups the layer can track, and the 2025–26 theory has pinned the boundary around $S_5$.
- Production models are hybrids with a small fraction of attention for recall; the open question is reasoning at scale, where loss is not a sufficient metric.

---

## Chapter 4. Instead of depth: recurrence, loops and test-time computation

Chapter 2 said depth is the resource that buys state tracking and multi-hop reasoning. A 100-layer model is expensive to train and slow to serve. Brains do not have 100 layers. This chapter follows the idea of getting depth by *reusing* layers, from the neuroscience that motivates it to the 2025–26 models that make it work.

### 4.1 What cortex actually does with few layers

The visual cortex recognises an object in about 100–150 ms (Thorpe, Fize and Marlot, 1996). Signals pass through roughly ten synaptic stages from retina to inferotemporal cortex (IT), each neuron taking around 10 ms to integrate and fire, so there is time for about one feedforward sweep. For thirty years this was the argument that core recognition is feedforward (DiCarlo, Zoccolan and Rust, 2012), and deep convolutional networks trained on ImageNet became the best models of IT responses. Three findings since 2019 changed the picture:

- **Recurrence is used, and used precisely when the feedforward sweep fails.** Kar, Kubilius, Schmidt, Issa and DiCarlo (2019, *Nature Neuroscience*) found images that monkeys recognise but feedforward networks get wrong, and showed that for those images the decodable object identity in IT emerges about 30 ms later than for matched control images; deeper networks and shallower recurrent networks both predicted the late responses, suggesting "a functional equivalence between additional nonlinear transformations and recurrence". Kietzmann et al. (2019, *PNAS*) showed recurrence is needed to capture the time course of human visual representations; Lamme and Roelfsema (2000) had argued earlier that feedforward processing gives a first pass and recurrent processing does the rest.
- **A single neuron is a deep network.** Beniaguev, Segev and London (2021, *Neuron*) fitted deep networks to a detailed model of a layer-5 pyramidal neuron and needed a temporal convolutional network five to eight layers deep to reproduce its input–output function at millisecond resolution, because of nonlinear (NMDA-receptor) integration in the dendrites; a point neuron needs one hidden unit. Gidon et al. (2020, *Science*) recorded a class of dendritic action potentials in human layer-2/3 neurons that lets a single neuron compute XOR, which a single-layer perceptron cannot. So the "layers" of cortex are each far deeper and more multiplicative than a weight matrix and a ReLU.
- **Working memory lives in fast synaptic state, not only in persistent activity.** Mongillo, Barak and Tsodyks (2008, *Science*) proposed that short-term synaptic facilitation (a calcium-driven increase in synaptic strength lasting about a second) holds working memory, with activity only refreshing it. That is, biologically, a fast-weight memory in the sense of §1.5 and Chapter 3: the state of the computation is stored in rapidly modified connection strengths, read out by activity.

The mapping to architecture is a heuristic, not a theorem, but it is a productive one: recurrence over time ↔ looping layers in depth with adaptive iteration counts; fast synapses ↔ matrix-valued fast-weight state updated at test time; dendritic nonlinearity ↔ multiplicative, gated units. Each of the three has a 2025–26 literature, and the rest of this chapter is the first; Chapter 3 was the second; Chapter 5 is the third.

### 4.2 Looped transformers: the idea and the theory

The **Universal Transformer** (Dehghani et al., 2018, Google Brain and Amsterdam) applied one shared transformer block repeatedly, with a per-position halting mechanism borrowed from Graves's **Adaptive Computation Time** (2016): a learned "ponder" probability decides how many iterations each position gets, with a small cost on the total. It was Turing-complete in principle, better on algorithmic tasks, and worse on language modelling per FLOP than a plain stack, and it sat in the literature for six years.

The theory caught up first. Giannou et al. (2023, "Looped transformers as programmable computers") showed a looped transformer with a fixed block can emulate a simple instruction set. Yang, Lee, Nowak and Papailiopoulos (2024) showed looped transformers learn in-context learning algorithms with far fewer parameters, consistent with the iterated-gradient-step picture of §1.5. Fan et al. (2025) showed loops help length generalisation on algorithmic tasks when the number of loops is tied to the problem size. Saunshi et al. (2025, ICLR, Google Research and TTIC, "Reasoning with latent thoughts") is the paper to read: a $k$-layer transformer looped $L$ times nearly matches a $kL$-layer transformer on synthetic reasoning (addition, $p$-hop), a 1B-parameter looped model trained on 250B tokens of the Pile reaches the same perplexity as its unlooped counterpart with stronger downstream reasoning, and $T$ loops can simulate $T$ steps of chain of thought, so loops are a *latent* chain of thought. Hao et al. (2024, Meta, "Coconut") made the same point from the chain-of-thought side by feeding the last hidden state back as the next input instead of a token.

### 4.3 Recurrent depth at scale (2025–2026)

Three systems took the idea to pretraining scale, and a cluster of 2026 papers worked out which design choices matter.

- **Huginn** (Geiping et al., 2025, NeurIPS; Maryland, LLNL, ELLIS/Max Planck). A 3.5B-parameter model with an untied **prelude** (a few layers that embed the input), a tied **recurrent core** run $r$ times, and an untied **coda** (a few layers that read out), trained on 800B tokens with the number of core iterations sampled randomly during training. At test time more iterations improve accuracy, most on mathematics and code, to a compute equivalent of roughly a 50B dense model; the design supports per-token adaptive compute, shared KV cache across iterations, and speculative decoding.
- **Ouro** (ByteDance Seed, October 2025, "Scaling latent reasoning via looped language models"). A fully tied stack looped up to four times with a learned exit gate, pretrained on 7.7T tokens at 1.4B and 2.6B parameters; the authors report parity with 4B and 8B standard transformers respectively.
- **Mixture-of-Recursions** (Bae et al., 2025, KAIST and Google). Adds token-level routing: a router decides, per token, how many recursions it receives, and the KV cache is shared across recursion steps, so compute is adaptive at the token level.

The 2026 follow-ups are where the useful engineering knowledge is:

- *Closing the Loop* (2026) reduces the training budget from Ouro's 7.7T tokens to 310B (210B pretraining plus 100B mid-training), with a warm-up on the exit gate and a larger KL coefficient to avoid gate collapse. Its controlled result: a 1.4B looped model with four iterations beats its parameter-matched dense twin on all twelve benchmarks it reports (about +14 GSM8K, +10 MATH, +22 DROP), while a dense model with 2.8× the parameters, at matched *inference* compute, is level or ahead everywhere, with a 2–9 point lead on knowledge and commonsense benchmarks. It also converts a pretrained dense checkpoint (Qwen3-1.7B) into a looped one and reports gains over an identically continued dense baseline.
- *Towards Looped Models Done Right* (2026) compares the Ouro-style (full-stack recurrence) and Huginn-style (prelude–core–coda) designs at 730M parameters and 336B tokens, then at MoE scale. The sandwich envelope gives the largest gains, concentrated on multi-step reasoning (MATH500 +12, GSM8K +7); re-injecting the prelude output at each loop helps code and context-dependent tasks (+5.5 HumanEval+) and hurts math; HRM-style shared high/low latent states give no consistent benefit. The looped MoE closes most of the gap to a 112-layer feedforward MoE with 75% more resident parameters.
- *Universal Transformers Need Memory* (2026) and *MeSH* (ICLR 2026) find that a single looped block needs explicit memory tokens or state highways to solve hard puzzles (Sudoku-Extreme), that memory and iteration count trade off, and that the standard halting-router initialisation makes most runs halt too early ("deep start" fixes it).

What loops buy, on the current evidence: better reasoning per parameter and adaptive test-time compute; not, yet, better loss per training FLOP than a larger dense model. Where they lose is knowledge-heavy tasks, which seems to need parameters rather than iterations, which is itself consistent with the view that MLPs are the long-term memory and attention/loops are the working memory (Geva et al., 2021; Behrouz et al., 2025).

### 4.4 Tiny recursive models and ARC

The **Abstraction and Reasoning Corpus** (Chollet, 2019; ARC-AGI-2 in 2025, Chollet et al.) poses grid puzzles: from two or three input–output examples, infer the rule and apply it to a new input. It was designed to resist memorisation, and until 2024 the best systems used hand-written program search.

Two 2025 models made recursion the headline. The **Hierarchical Reasoning Model** (Wang et al., Sapient Intelligence, June 2025): 27M parameters, two small recurrent modules at different timescales, trained on about a thousand examples per task family with heavy augmentation, claiming 40% on ARC-AGI-1. The ARC Prize team's independent analysis (August 2025) reproduced about 32% on the semi-private set and found that the two-module hierarchy contributed little compared with a same-size transformer, that the under-documented **outer refinement loop** (iterate the whole model on its own output, with supervision at each iteration) drove most of the gain, and that augmentation and some memorisation of evaluation-task formats did the rest. The **Tiny Recursive Model** (Jolicoeur-Martineau, Samsung SAIL Montréal, October 2025, "Less is more") took the lesson: one two-layer network of 7M parameters, a latent state $z$ and an answer $y$, updated as $z \leftarrow f(x, y, z)$ for several inner steps then $y \leftarrow g(y, z)$, repeated with **deep supervision** (a loss on $y$ after every outer step) and full backpropagation through the recursion instead of HRM's one-step gradient approximation. It reports 45% on ARC-AGI-1 and 8% on ARC-AGI-2, above most frontier LLMs at the time, with 0.01% of their parameters, and large gains on Sudoku-Extreme (87%) and Maze-Hard (85%).

Read these with care: they are trained per benchmark on the public task distribution with augmentation, and they are not language models. But they are the cleanest existing evidence for the thesis of this chapter and the last: a tiny network, iterated, with a loss at every iteration, solves puzzles that a single forward pass of a huge network does not. Deep supervision is the practical form of Abbe's "educated scratchpad" (§2.5): every iteration is a low-globality step.

### 4.5 Test-time computation: tokens, loops, or weights

Three ways to spend more computation on a hard input after training, all active research lines:

1. **Tokens.** Chain of thought (Wei et al., 2022) and its scaling (Snell et al., 2024); the reasoning models trained by reinforcement learning to produce long chains (OpenAI o1, September 2024; DeepSeek-R1, January 2025) made this the dominant industrial route. Theory (§2.3) says it is the least compute-efficient of the three per unit of added expressivity, but it is the one that works with existing models and gives a readable trace.
2. **Loops.** The latent route of §4.2–4.4. Merrill and Sabharwal (2025) argue depth is more efficient than chain-of-thought tokens for the same expressive gain, and the looped-model papers report exactly that on reasoning benchmarks, at the cost of interpretability of the intermediate state.
3. **Weights.** **Test-time training** (Sun et al., 2020, for distribution shift; Sun et al., 2024, as a sequence layer): update parameters on the test input itself. On ARC this was decisive. Akyürek et al. (2024, MIT) fine-tuned an 8B model on augmentations of each task's demonstration pairs at test time and reached 53% on the public validation set, 61.9% when ensembled with program synthesis; the ARC Prize 2024 report states that every top transduction entry used test-time training and that no static-inference transduction system scored above 11%. ARC Prize 2025 (ARC-AGI-2) was won by an NVIDIA Kaggle team ("NVARC") at 24% on the private set under the compute cap, with a refinement harness on Gemini 3 Pro (Poetiq) reaching 54% and the best verified single commercial model at the time (Claude Opus 4.5 with extended thinking) at 37.6%, at much higher cost per task.

The three are not exclusive, and the 2026 systems combine them: a looped model with memory tokens, trained with deep supervision, fine-tuned at test time on its demonstrations, producing a chain of thought. If you want one sentence for where test-time compute is going: *from tokens toward loops and weights, because they are cheaper per unit of depth, with tokens kept for the parts a human needs to read.*

### 4.6 What to take from this chapter

- Cortex is shallow in stages, deep in each unit, recurrent when the first pass fails, and keeps working memory in fast synaptic state. All three have architectural counterparts now.
- Looping a block gives depth without parameters: a $k$-layer block looped $L$ times approaches a $kL$-layer model on reasoning. The design that works is prelude–tied core–coda, with input injection, memory tokens, randomised iteration counts in training, and a carefully initialised halting gate.
- On puzzles, a tiny network iterated with deep supervision beats single-pass giants; the outer refinement loop and per-iteration loss are what matter, not the architecture inside the loop.
- Test-time computation can be spent as tokens, loops or weight updates; the field is moving toward the latter two.

---

## Chapter 5. Where relations live: multiplicative interactions, binding, higher-order attention and groups

"Higher order" is used in the literature for at least three different things, and keeping them apart is half the battle:

1. **Higher-order scores**: an attention weight that depends on three or more tokens at once (2-simplicial, Strassen, poly-attention). This raises the *arity* of selection.
2. **Higher-order state**: products of features carried along the sequence (outer products in fast weights, products of transition matrices, gated multiplications). This raises the *degree* of what the layer computes from the tokens it has already selected.
3. **Higher-order computation**: iterating a block (Chapter 4). This raises *depth*.

The first is the most expensive and the least proven; the second is where the practical wins of the last three years sit; the third is Chapter 4. This chapter covers the first two and the two bodies of older theory that explain them: binding, and associative-memory capacity. It ends with group structure, which ties the chapter back to Chapters 2 and 3.

### 5.1 Multiplicative interactions

A linear layer computes $Wx$; a bilinear layer computes $x^\top W y$ and can represent "$x$ *and* $y$" rather than "$x$ *or* $y$". Rumelhart, Hinton and McClelland (1986) called units that multiply their inputs sigma-pi units; hypernetworks (Ha, Dai and Le, 2016) let one network output another's weights, which is multiplicative; Jayakumar et al. (2020, DeepMind) showed bilinear maps strictly enlarge the hypothesis class of standard layers and unify gating, attention and hypernetworks as special cases. Where you meet them in current models:

- **Gated MLPs** (SwiGLU, §1.6) and **gated attention outputs** (Qwen, 2025): elementwise products of two linear maps of the same input.
- **Input-dependent decay** in GLA, Mamba, Gated DeltaNet: the state is multiplied by a gate computed from the token, so the recurrence is bilinear in (state, input).
- **The delta rule**: the state update $\beta_t (v_t - S_{t-1} k_t) k_t^\top$ is a product of the input with a function of the state.
- **Fast weights read by a query**: $S_t q_t$ is cubic in token features (value × key × query), summed over pairs (query, stored token), not over triples. This is the sense in which linear attention is already "third order" without being 2-simplicial.

The lesson of Chapter 3 restated: the multiplicative terms that shipped are in the write path and the state, where they are cheap (per token, not per pair or triple) and where gradient descent finds them.

### 5.2 Binding and vector-symbolic architectures

The **binding problem** asks how a distributed representation can say *which* attribute belongs to *which* object: "red square and blue circle" must not collapse into "red, blue, square, circle". Three solutions from the connectionist era, all multiplicative:

- **Tensor product representations** (Smolensky, 1990): bind a role vector $r$ to a filler $f$ as the outer product $r \otimes f$; superpose bindings by adding; unbind by contracting with the role. Exact but the dimension multiplies.
- **Holographic reduced representations** (Plate, 1995): replace the outer product with circular convolution, which keeps the dimension fixed; in the Fourier domain circular convolution is an elementwise product of complex phases, so a binding is a product of unit-modulus numbers and unbinding is multiplication by the conjugate. This is the Fourier HRR used in most modern work.
- **Hyperdimensional computing** (Kanerva, 2009) and the **MAP** architecture (Gayler, 2003): bind by elementwise multiplication of high-dimensional random vectors, bundle by addition, and encode *order* by a fixed permutation $\rho$, since elementwise multiplication is commutative and would lose "A before B". **Matrix binding of additive terms** (Gallant and Okaywe, 2013) binds with matrix multiplication, which is non-commutative and so encodes order on its own.

Why this matters now. Hrrformer (Alam et al., ICML 2023) recast self-attention as HRR binding of key–value pairs and superposition, with $O(T \log T)$ cost. Feng and Steinhardt (2023) found that language models bind entities to attributes in context with abstract "binding ID" vectors added to both, which is a superposition code of exactly this kind. Webb, Sinha and Cohen (2021) and Altabaa, Webb and Lafferty (2023, "Abstractors") showed that forcing a **relational bottleneck**, where a module sees only similarity relations between objects and not the objects' features, gives large sample-efficiency gains on relational reasoning, and that removing it from Slot Abstractors costs up to 52% on their tasks. A 2025 preprint ("Attention as binding") proposes reading queries and keys as role spaces, values as fillers, attention as soft unbinding and the residual stream as superposition. The connection to Chapter 3 is direct: a matrix fast-weight state $\sum v_s k_s^\top$ *is* a tensor-product binding store, the delta rule is its clean-up operation, and the commutativity problem of VSAs is the same problem that diagonal state-space models have with order (§3.5), with the same cure: non-commuting (matrix) binding.

### 5.3 Higher-order attention at scale

The theory of §2.4 says a trilinear score is needed for relations whose pairwise statistics vanish. The practical questions are cost and whether real data has such relations often enough to pay for it.

**Cost.** Exact 2-simplicial attention is $O(n^3)$ per head: each query scores every pair of keys. Alman and Song (2023) showed that, under the Strong Exponential Time Hypothesis, exact higher-order attention has no truly sub-cubic algorithm in general. The practical designs restrict the two key axes to windows, or linearise one axis.

**Evidence.** Roy et al. (2025, Meta, "Fast and Simplex") trained mixture-of-experts models from 1B to 3.5B active parameters (57B to 176B total) with every fourth layer a 2-simplicial attention layer over sliding windows of (512, 32) keys, in a Triton kernel. At fixed token budgets the 2-simplicial models reach lower loss on math, code and reasoning benchmarks, and the fitted scaling exponents change: GSM8K 0.142 → 0.168 (+18.5%), MMLU 0.126 → 0.136, MMLU-Pro 0.090 → 0.108 (+20%), MBPP 0.172 → 0.184. Two qualifications in the paper itself: below 2B active parameters there is no gain (the 1B models are slightly worse), and the authors frame the benefit for the regime where tokens, not compute, are the binding constraint. A 2026 follow-up, *Linearized 2-simplicial attention*, writes the trilinear score as an inner product between a composite query and a key, approximates the sum over one axis with positive random features so the whole past sits in a fixed-size state, keeps the other axis explicit over a short window, and combines the result with Kimi Delta Attention into a model with no softmax at all; it reports the highest mean downstream accuracy among the compared architectures at matched compute and a LAMBADA perplexity reduction from 716 to 603 over a KDA hybrid at 16k context. Higher-order Linear Attention (Zhang, Qin, Wang and Gu, 2025) computes second-order interactions from prefix sufficient statistics in a streaming scan, at linear cost, from the other direction.

**Reading the evidence.** Higher-order scores are real but expensive and only pay above a size threshold and in token-limited training; the linearised variants trade exactness for a fixed-size state and look like the direction that can ship. The relation to Chapter 3 is that a "higher-order linear attention" is a fast-weight memory whose state holds moments of order two or three, that is, a dense associative memory with a polynomial energy, which brings us to capacity.

### 5.4 Capacity: dense associative memory as the theory of higher order

Return to §1.4. A linear fast-weight memory with feature map $\phi$ stores associations $\sum v_s \phi(k_s)^\top$ and can hold about $\dim \phi$ of them before interference. A polynomial feature map of degree $k$ in $d$ dimensions has dimension about $d^k / k!$, so capacity grows polynomially with the degree; the softmax kernel corresponds to an infinite-degree map and gives the exponential capacity of Ramsauer et al. (2020). This is Krotov and Hopfield's dense-associative-memory argument (2016) transplanted into the sequence state, and it is why Atlas (Behrouz et al., 2025) reports that polynomial feature maps on keys and queries lower perplexity (an ablation summarised in secondary coverage as 22.1 → 20.0; check the paper's tables), and why Linearized 2-simplicial attention can keep a global reach in a fixed state. The exact capacity results are in Demircigil et al. (2017) and Lucibello and Mézard (2024); a 2026 ICLR paper (Kafraj, Krotov and Latham) shows how to get exponential capacity with a biologically plausible two-layer network, closing a known gap in which the hidden layer's capacity was only linear.

The Energy Transformer (Hoover et al., 2023, IBM and others) builds a transformer block as gradient descent on an energy whose two terms are an attention term (dense associative memory over tokens) and a Hopfield term (alignment with stored token patterns), so the whole block is a recurrent memory retrieval; it was evaluated on images and graphs, with a language-model follow-up reported by the same group. Krotov's ICML 2025 tutorial connects this line to transformers and diffusion models and is the best entry point.

Why a researcher should care: capacity is a *predictive* theory of where higher-order terms pay. They pay when the layer must hold many associations in a bounded state: long-context recall, retrieval-heavy tasks, in-context learning with many examples. They do not pay where the state is not the bottleneck. This is consistent with everything in §5.3 and §3.6.

### 5.5 Group structure, representations and equivariance

Chapters 2 and 3 used groups to say what a layer can track. The same mathematics says what a layer should *compute with*. A **representation** of a group $G$ assigns to each element $g$ a matrix $\rho(g)$ so that $\rho(gh) = \rho(g)\rho(h)$: combining elements is multiplying matrices (Appendix A). Every finite group has a finite list of **irreducible** representations (irreps), the building blocks of all others, and functions on the group have a Fourier expansion in them, which for abelian groups is the ordinary discrete Fourier transform.

Instances already in this guide: RoPE represents the integers under addition by 2-D rotations ($\rho(t) = R(t\theta)$, with $\rho(t)\rho(-s) = \rho(t-s)$); the grokked modular-addition network of Nanda et al. (2023) represents $\mathbb Z_p$ by the same rotations and adds by multiplying; the networks of Chughtai et al. (2023) represent $S_5$ by its irreps; DeltaProduct's Householder products are learned, input-dependent representations of whatever group the data composes in; PaTH is RoPE with the fixed rotation replaced by a learned reflection product. **Equivariant networks** (Cohen and Welling, 2016; Kondor and Trivedi, 2018) build known symmetries in by weight sharing over a group; the sequence-model literature is doing the converse, letting the model learn a representation from labels.

Two 2026 preprints push the idea to its limit and are worth knowing as signals rather than results: "The token is a group element" (Musialski, 2026) treats each token as an element of a matrix Lie group with the attention score a Lie-algebra distance, and "All You Need Is Non-Commutative Words" (Quispe Flores, Salvatierra and Cabrera, 2026) represents a sentence as an ordered product of unitary matrices, one per word, with no positional encoding; both are evaluated on small tasks.

The deeper point for research design: *the group a layer's features compose in sets what relations it can see.* Commuting features (phases, diagonal gates) see multisets; non-commuting features (rotations, reflections, permutations) see sequences. Barrington (§2.2) says non-commuting products of width five are universal for $\mathbf{NC^1}$. A sequence layer whose state composes in $S_5$ or $SO(5)$, with the element chosen by content, is therefore a complete primitive for everything attention lacks, and the architectures of §3.5 are approaching it from several sides.

### 5.6 What to take from this chapter

- Multiplicative terms are everywhere in current models; the ones that pay are in gates, the write path and the state, where they cost $O(n)$.
- Binding needs multiplication (outer products, phase products, matrix products), order needs non-commutativity, and the fast-weight state of Chapter 3 is a binding store; the thirty-year-old VSA literature is a map of the design space.
- Higher-order attention scores help at scale and in token-limited regimes, cost cubic time unless windowed or linearised, and the linearised forms are fast-weight memories with polynomial energies.
- Capacity theory (dense associative memory) predicts where higher-order terms pay: where a bounded state must hold many associations.
- Representations of finite groups are the right language for both what a layer can track and what it should compute with; non-commuting state of width five is in principle universal for the computations attention cannot do.

---

## Chapter 6. The bleeding edge, and how to work on it

### 6.1 The picture as of late 2026

Put the five chapters together and a single design emerges, assembled by different groups for different reasons:

1. **Along the sequence**, most layers are fast-weight memories with delta-rule writes, decay, and increasingly non-commuting transitions (Gated DeltaNet and its 2026 successors, Kimi Delta Attention, DeltaProduct, Mamba-3), with a minority of global attention layers, often sparse or latent, for exact recall. The theory (Chapters 2, 3) says this split is a cascade of the two Krohn–Rhodes atoms: content-gated reset plus group composition. Status: shipping at 50–100B total parameters; contested on multi-hop reasoning at the largest scales (MiniMax's retreat); the exact matrix structure needed for state tracking is now a theorem rather than a guess.
2. **Within a position**, multiplicative gating everywhere (SwiGLU, gated attention), and capacity-raising feature maps on memory keys (Atlas). Status: gating is settled; polynomial feature maps are one group's result.
3. **In depth**, a prelude–tied core–coda stack with the core looped a variable number of times, input re-injected each loop, memory tokens, randomised loop counts in training, and a halting gate initialised to run deep. Status: parameter-efficient and strong on reasoning at 1–4B; not yet better than a larger dense model at equal training compute; knowledge tasks still want parameters.
4. **At test time**, computation spent as chain-of-thought tokens (industrially dominant), as extra loops (cheaper per unit of depth), or as weight updates on the input (decisive on ARC). Status: converging; the combination is the 2026 frontier on puzzle benchmarks.
5. **Where relations are many-token**, either a windowed or linearised higher-order score (pays above about 2B active parameters in token-limited training) or, more often, a higher-order *state*. Status: one strong positive result at scale from Meta, linearisations in 2026, cost still the obstacle.
6. **Learning**, with deep supervision or scratchpads whenever the target has high globality, because representable is not learnable (Chapter 2) and every negative result in the architecture literature of the last three years has this shape.

If a first-year student asks "what is the current best architecture?", the honest answer is: a hybrid of (1) and a few attention layers, with (2), trained with the Muon optimiser (Jordan et al., 2024; Moonshot's scaled version, 2025), which consistently improves loss across architectures at small and medium scale and interacts with some layers (Parallax) more than others. If they ask "what will the architecture be in two years?", the evidence points at (3) and (4) being added to that, because they are the only known ways to get $\mathbf{NC^1}$-and-beyond computation without paying for it in parameters or tokens.

### 6.2 Open problems, with what would count as a result

1. **Do hybrids reason as well as full attention at scale?** MiniMax says no at 400B; the Tencent study says loss cannot tell you. *Result*: a multi-hop reasoning suite (not loss) across three scales showing where, if anywhere, a 7:1 or 3:1 hybrid falls behind, and whether more attention layers, PaTH-style transport, or DeltaProduct-style transitions close it.
2. **The compute-optimal looped model.** Looped models beat parameter-matched dense models and lose to compute-matched ones. *Result*: a scaling law with loop count as an axis, fitted across sizes, giving the frontier of loss (and reasoning accuracy) per training FLOP, with the point at which loops beat parameters.
3. **Do language models learn non-commuting state?** Synthetic word problems show the layers *can*. *Result*: probes on pretrained hybrids showing whether the transition matrices discover group structure for real sequential semantics (variable binding in code, entity tracking in narrative), and whether a curriculum helps.
4. **Capacity-aware memory design.** Dense-associative-memory theory predicts capacity from the feature map; Atlas is one data point. *Result*: a measured capacity–perplexity curve for polynomial and random-feature maps at fixed state size, across context lengths, with a theory that predicts it.
5. **Deep supervision in pretraining.** TRM and the globality theory both say per-iteration loss is what makes recursion learn. *Result*: a looped language model trained with per-loop losses (or a latent inductive scratchpad) that improves on the same model trained with final loss only, at equal tokens.
6. **Binding benchmarks for language.** MQAR tests recall; nothing standard tests binding plus composition (which variable holds which value after a sequence of operations). *Result*: a benchmark family with controlled globality, and architectures ranked on it against attention, with the relational-bottleneck idea tested inside a language model.
7. **Test-time training as a layer, at scale.** TTT layers, Titans and MesaNet are at 1–3B. *Result*: a 10B-class model with a test-time-optimised memory that beats a hybrid at equal inference cost on long-context tasks, with the training-time cost accounted.
8. **Theory of learnability for sequence models with loops and chain of thought.** Leap and globality are defined for weak learning and single-pass models. *Result*: a learnability measure that predicts which looped or scratchpad-equipped models learn which compositional tasks, verified on the synthetic suites of Chapters 2–3.
9. **Kernels for non-commuting state.** DeltaProduct's cost grows with the number of reflections; MIMO states (Mamba-3) trade training speed for quality. *Result*: a chunked algorithm for products of $k$ reflections with the same wall clock as $k = 1$, or a proof that none exists.
10. **Evaluation itself.** Noise floors, loss-versus-downstream gaps, and cross-scale stability are now prerequisites (§1.9). *Result*: a shared protocol and harness the community adopts, with the twenty modifications of the Tencent study as its first regression suite.

### 6.3 How to run an architecture experiment that survives review

1. **Define the compute.** Count FLOPs for every operation your layer adds, including scans, convolutions and read-outs; report wall clock separately. Train the baseline to *your* FLOPs, not your parameters.
2. **Three scales minimum**, spaced by about 3× in parameters, with tokens at or beyond the compute-optimal ratio for each. Fit the exponent. If you cannot afford three scales, say so and do not claim a scaling effect.
3. **Noise floor.** Three seeds at the smallest scale, and report the spread on every plot. A gain inside the spread is not a gain.
4. **Tune the baseline as hard as the candidate.** Learning-rate sweep per architecture per scale; the same optimiser; the same data order. Use Muon if you use it for the candidate.
5. **Downstream probes that target the claim.** For recall: MQAR and induction with distractors. For state tracking: $S_5$ word problems and parity at lengths beyond training. For multi-hop: $p$-hop at $p = 16$. For composition: function composition and Dyck. For long context: needle and multi-needle retrieval. Report length extrapolation.
6. **Pre-register the gate.** Write the effect size that counts, and the stopping rule, before the main runs. Report failed predictions as failed.
7. **Ablate inside the trained model.** Zero a branch at inference and measure the loss change; it tells you whether the model uses the branch, not whether the branch caused the gain. Say which.
8. **Use shared code.** flash-linear-attention (Songlin Yang and collaborators) for every linear and delta-rule layer with chunked kernels; modded-nanogpt (Keller Jordan and contributors) as a tuned small-scale baseline with Muon; the FlashAttention repository for the attention baseline. A result that reproduces in those harnesses will be believed.

### 6.4 A reading order

Read in this sequence; each paper assumes the previous ones.

1. Vaswani et al. (2017), then Elhage et al. (2021) and Olsson et al. (2022), to see what attention is and what it learns.
2. Schlag, Irie and Schmidhuber (2021), then Wang, Shi and Fox (2025), to see attention as memory and regression.
3. Gu and Dao (2023), Dao and Gu (2024), Yang, Kautz and Hatamizadeh (2024), to see the state-space and delta-rule lines meet.
4. Merrill and Sabharwal (2023a), Liu et al. (2022), Merrill, Petty and Sabharwal (2024), Grazzi et al. (2025), Siems et al. (2025), to see what state tracking requires.
5. Sanford, Hsu and Telgarsky (2023, 2024) and Roy et al. (2025), for multi-token relations and depth.
6. Barak et al. (2022), Abbe et al. (2023, 2024), Nanda et al. (2023), for learnability and what networks actually learn.
7. Dehghani et al. (2018), Saunshi et al. (2025), Geiping et al. (2025), the 2026 looped-model papers, Jolicoeur-Martineau (2025), for depth by iteration.
8. Krotov and Hopfield (2016), Ramsauer et al. (2020), Behrouz et al. (2025, Atlas), for capacity.
9. Plate (1995) and Altabaa, Webb and Lafferty (2023), for binding.
10. Kar et al. (2019), Beniaguev et al. (2021), Mongillo et al. (2008), for the brain.
11. Narang et al. (2021), Zhao et al. (2026), and MiniMax's M2 post, before you believe any architecture result, including your own.

### 6.5 Timeline

| Year | Who | What | Why it mattered |
|---|---|---|---|
| 1949 | Hebb | Hebbian learning | Outer-product memory writes |
| 1960 | Widrow and Hoff | Delta rule (LMS) | The write rule of DeltaNet |
| 1965 | Krohn and Rhodes | Cascade decomposition of automata | Reset and group atoms |
| 1982–85 | Hopfield; Amit, Gutfreund, Sompolinsky | Hopfield network and its 0.138N capacity | Associative memory as energy descent |
| 1986 | Rumelhart, Hinton, McClelland | Sigma-pi units | Multiplicative interactions |
| 1989 | Barrington | Width-5 permutation programs = NC¹ | S₅ is the boundary |
| 1990–95 | Smolensky; Plate | Tensor-product and holographic representations | Binding by multiplication |
| 1992 | Schmidhuber (IDSIA) | Fast weights | Linear attention, thirty years early |
| 1996 | Thorpe, Fize, Marlot | 150 ms recognition | The feedforward argument |
| 1997 | Hochreiter and Schmidhuber | LSTM | Gated recurrence |
| 2008 | Mongillo, Barak, Tsodyks | Synaptic working memory | Fast weights in cortex |
| 2014 | Bahdanau, Cho, Bengio (Montréal) | Attention | |
| 2016 | Krotov and Hopfield; Graves (DeepMind) | Dense associative memory; adaptive computation time | Capacity from energy degree; learned iteration count |
| 2017 | Vaswani et al. (Google Brain) | Transformer | |
| 2018 | Dehghani et al. (Google Brain, Amsterdam) | Universal Transformer | The first looped transformer |
| 2019 | Kar et al. (MIT, DiCarlo lab); Clift et al. | Recurrence in IT cortex; 2-simplicial attention | |
| 2020 | Katharopoulos (EPFL); Ramsauer (JKU Linz); Hahn; Kaplan (OpenAI); Shazeer (Google) | Linear attention; Hopfield = attention; AC⁰ limits; scaling laws; SwiGLU | |
| 2021 | Schlag, Irie, Schmidhuber; Gu, Goel, Ré (Stanford); Elhage (Anthropic); Narang et al. (Google); Beniaguev (HUJI); Su (RoPE) | DeltaNet; S4; circuits; "modifications don't transfer"; neurons are deep | |
| 2022 | Olsson (Anthropic); Barak et al.; Dao (Stanford); Hoffmann (DeepMind); Liu et al. (MSR/CMU); Wei et al. | Induction heads; hidden progress; FlashAttention; Chinchilla; shortcuts to automata; chain of thought | |
| 2023 | Gu and Dao; Yang et al. (GLA); Sun et al. (RetNet); Peng (RWKV); Sanford, Hsu, Telgarsky; Merrill and Sabharwal; Abbe et al. (leap); Nanda; Chughtai; von Oswald; Hoover (Energy Transformer); Alam (Hrrformer); Altabaa (Abstractors) | Mamba; gated linear attention; TC⁰ bound; Match-3; grokking circuits; mesa-optimisation | |
| 2024 | Yang et al. (parallel DeltaNet, Gated DeltaNet); Dao and Gu (Mamba-2); Grazzi et al.; Merrill, Petty, Sabharwal; Sanford et al. (log depth); Abbe et al. (globality); Lieber (Jamba); Behrouz (Titans); Sun et al. (TTT layers); Akyürek (TTT on ARC); Hao (Coconut); Petty et al.; Jordan (Muon) | The delta-rule family matures; state tracking theory; test-time training; looped theory | |
| 2025 | Siems (DeltaProduct); Yang (PaTH); Geiping (Huginn); Saunshi (looped); ByteDance (Ouro); Bae (MoR); Sapient (HRM); Jolicoeur-Martineau (TRM); Roy (2-simplicial, Meta); Wang, Shi, Fox; Behrouz (Miras, Atlas, Nested Learning); von Oswald (MesaNet); Qiu (gated attention, Qwen); Zuo (LLA); Alibaba (Qwen3-Next); Moonshot (Kimi Linear); NVIDIA (Nemotron-H); MiniMax (M1 hybrid, then M2 full attention); DeepSeek (NSA, DSA); Merrill and Sabharwal (log depth); Chollet (ARC-AGI-2) | Production hybrids; recurrent depth at scale; tiny recursive reasoners; higher-order at scale; the retreat | |
| 2026 | Gated DeltaNet-2; Complex KDA; Mamba-3; Rational Transductors; Parallax; Linearized 2-simplicial; Closing the Loop; Looped Done Right; UT Need Memory; MeSH; Kafraj–Krotov–Latham; Zhao et al. (Tencent) | Erase/write decoupled; the S₅ boundary theorem; complex and MIMO states; looped recipes; capacity; the replication study | |

---

## Appendix A. Groups, representations and why width five is special

**Groups.** A group $(G, \cdot)$ is a set with a binary operation such that (i) $g \cdot h \in G$ (closure), (ii) $(g \cdot h) \cdot k = g \cdot (h \cdot k)$ (associativity), (iii) there is an identity $e$ with $e \cdot g = g \cdot e = g$, and (iv) every $g$ has an inverse $g^{-1}$ with $g \cdot g^{-1} = e$. If also $g \cdot h = h \cdot g$ for all pairs, the group is **abelian**.

Examples. $\mathbb Z_m$: integers $\{0, \dots, m-1\}$ under addition modulo $m$; abelian. $S_n$: all permutations of $n$ objects under composition; $|S_n| = n!$; non-abelian for $n \ge 3$. $A_n$: the even permutations (those expressible as an even number of swaps), half of $S_n$. $SO(2)$: rotations of the plane; abelian (rotations about one axis add their angles). $SO(3)$: rotations of 3-space; non-abelian (rotate a book a quarter turn about two different axes in the two orders and compare). $A_4$ is the rotation group of the tetrahedron (12 elements); $A_5$ is the rotation group of the icosahedron (60 elements); both are subgroups of $SO(3)$.

**Subgroups, normal subgroups, quotients.** A subgroup $H \subseteq G$ is a subset closed under the operation. It is **normal** if $gHg^{-1} = H$ for every $g$; then the cosets $gH$ themselves form a group, the **quotient** $G/H$. A group is **simple** if its only normal subgroups are trivial. $A_5$ is the smallest non-abelian simple group.

**Solvable groups.** $G$ is solvable if there is a chain $\{e\} = G_0 \subset G_1 \subset \cdots \subset G_k = G$ with each $G_i$ normal in $G_{i+1}$ and each quotient $G_{i+1}/G_i$ abelian. Abelian groups are solvable. $S_3$ and $S_4$ are solvable ($S_4 \supset A_4 \supset V_4 \supset \{e\}$ with quotients $\mathbb Z_2$, $\mathbb Z_3$, $V_4$). $S_5$ is not, because $A_5$ is simple and non-abelian. Galois: a polynomial is solvable by radicals iff its Galois group is solvable; the general quintic has Galois group $S_5$.

**Why width five.** Barrington's construction needs a group with two elements $a, b$ whose commutator $aba^{-1}b^{-1}$ is not the identity and in fact generates "enough": the trick is that AND of two Boolean values can be computed by a commutator of two permutation programs, which is non-trivial only in a non-solvable group. $S_5$ is the smallest symmetric group containing a non-solvable subgroup, hence width five. Width-3 programs need exponential size for AND; the width-4 case is open.

**Representations.** A representation of $G$ on $\mathbb R^d$ is a map $\rho: G \to GL_d(\mathbb R)$ (invertible $d \times d$ matrices) with $\rho(gh) = \rho(g)\rho(h)$ and $\rho(e) = I$. If $\rho$ is injective it is **faithful** (no information lost). If no change of basis splits $\rho$ into independent blocks it is **irreducible** (an irrep). Every finite group has finitely many irreps up to equivalence, and their dimensions $d_i$ satisfy $\sum_i d_i^2 = |G|$. Examples: $\mathbb Z_m$ has $m$ one-dimensional complex irreps $\chi_k(x) = e^{2\pi i k x / m}$ (the characters), which pair up into $2 \times 2$ real rotations; $A_4$ has irreps of dimensions $1, 1, 1, 3$; $A_5$ has $1, 3, 3, 4, 5$ (note $1 + 9 + 9 + 16 + 25 = 60$); $S_5$ has $1, 1, 4, 4, 5, 5, 6$.

**Characters and Fourier analysis on groups.** The character of $\rho$ is $\chi_\rho(g) = \operatorname{tr} \rho(g)$. For abelian groups the characters are the irreps, they are orthogonal, and any function $f: G \to \mathbb C$ expands as $f = \sum_\chi \hat f(\chi)\, \chi$, the discrete Fourier transform. For non-abelian groups the same holds with matrix coefficients of irreps in place of characters (Peter–Weyl). A consequence used in Chapter 5: the indicator of the identity is $\delta_e(g) = \frac{1}{|G|}\sum_\rho d_\rho\, \chi_\rho(g)$, so "is this product the identity?" is a question whose answer is spread over all irreps weighted by dimension.

**Rotations, reflections, determinants.** Orthogonal matrices ($Q^\top Q = I$) have determinant $\pm 1$. Those with $+1$ form $SO(d)$, the rotations; a **Householder reflection** $I - 2uu^\top$ (unit $u$) has determinant $-1$. Every orthogonal $d \times d$ matrix is a product of at most $d$ reflections (Cartan–Dieudonné), and a product of an even number of reflections is a rotation. This is why DeltaProduct's $n_h$ Householder steps per token, with $n_h \ge d$, can realise any orthogonal transition, and why a single reflection (DeltaNet with $\beta = 2$) can represent sign flips but not general rotations. A representation of $S_n$ in which transpositions act as reflections has determinant equal to the sign of the permutation, so it does not fit in $SO(d)$; adding one dimension (or allowing reflections) fixes this.

**Exponential parametrisation.** Any rotation is $\exp(A)$ for a skew-symmetric $A$ ($A^\top = -A$), so a network can output a skew matrix and exponentiate it to get a rotation that stays a rotation during training (Lezcano-Casado and Martínez-Rubio, 2019); unitary RNNs (Arjovsky, Shah and Bengio, 2016) used related parametrisations to avoid exploding and vanishing gradients.

## Appendix B. Circuit classes

A **circuit family** $\{C_n\}$ has one circuit per input length. **Depth** is the longest input-to-output path, **size** the gate count. Classes:

- $\mathbf{AC^0}$: depth $O(1)$, size $\mathrm{poly}(n)$, gates AND, OR, NOT with unbounded fan-in. Cannot compute PARITY or MAJORITY.
- $\mathbf{ACC^0}$: $\mathbf{AC^0}$ plus $\mathrm{MOD}_m$ gates. Contains the word problems of solvable groups.
- $\mathbf{TC^0}$: $\mathbf{AC^0}$ plus MAJORITY (threshold) gates. Contains PARITY, iterated addition, multiplication, sorting. Believed strictly inside $\mathbf{NC^1}$ but not proved.
- $\mathbf{NC^1}$: depth $O(\log n)$, size $\mathrm{poly}(n)$, fan-in 2. Contains Boolean formula evaluation and all finite-group word problems; the non-solvable ones are complete for it (Barrington, 1989).
- $\mathbf{L}$, $\mathbf{NL}$, $\mathbf{P}$: logarithmic-space, nondeterministic log-space (graph reachability is complete), polynomial time.

**Uniformity.** A circuit family is uniform if a simple machine can write down $C_n$ given $n$; the transformer bounds are for uniform $\mathbf{TC^0}$, which rules out hiding computation in the circuit description.

**Where transformers sit.** Hard attention: $\mathbf{AC^0}$ (Hahn, 2020; Hao, Angluin and Frank, 2022). Soft attention with $O(\log n)$-bit numbers: uniform $\mathbf{TC^0}$ (Merrill and Sabharwal, 2023a). With $t$ chain-of-thought steps: roughly $t$ steps of a sequential machine, so polynomially many steps give $\mathbf{P}$ (Merrill and Sabharwal, 2024). With $\Theta(\log n)$ layers: regular languages and connectivity (Merrill and Sabharwal, 2025). Diagonal state-space models: $\mathbf{TC^0}$ (Merrill, Petty and Sabharwal, 2024). A linear recurrence with unrestricted non-commuting transitions is not covered by those bounds, because its scan is a sequential (or $\log$-depth parallel) product.

## Appendix C. Fourier analysis on the hypercube, parity and leap

Functions $f: \{-1, +1\}^n \to \mathbb R$ have an orthonormal basis of **parities** (Walsh functions) $\chi_S(x) = \prod_{i \in S} x_i$ for subsets $S \subseteq [n]$, so $f = \sum_S \hat f(S)\, \chi_S$. The degree of $f$ is the largest $|S|$ with $\hat f(S) \ne 0$. Under the uniform distribution, $\mathbb E[\chi_S \chi_T] = \mathbf 1[S = T]$.

**Why parity hides from gradient descent.** Let the target be $\chi_S$ with $|S| = k$, and consider any feature $g(x)$ that depends on fewer than $k$ coordinates, or more generally any function of degree less than $k$. Then $\mathbb E[g \cdot \chi_S] = 0$, because $g$ has no Fourier mass on $S$. The population gradient of a square loss with respect to any weight that enters through such a feature is therefore zero at initialisation, and the only signal comes from the degree-$k$ component of the network's own features, which is $n^{-\Theta(k)}$ small at random initialisation. Barak et al. (2022) show SGD nonetheless amplifies that small signal, taking about $n^{k}$ steps, with the loss flat until the end.

**Leap.** For a target $f$ on sparse coordinates, order its Fourier terms so that each new term introduces as few new coordinates as possible; the **leap** is the maximum number of new coordinates introduced at once. A single $k$-parity has leap $k$. The staircase $x_1 + x_1 x_2 + x_1 x_2 x_3$ has leap 1: learn $x_1$, then $x_2$ given $x_1$, and so on. Abbe, Boix-Adserà and Misiakiewicz (2022, 2023) prove that in the mean-field regime two-layer networks learn in time governed by the leap, and that merged staircases (where several chains share steps) are learnable. The **globality degree** of Abbe et al. (2024) is the transformer analogue: the minimum number of tokens one must look at jointly for the target to have non-trivial correlation with the input.

**The practical rule.** If your target has leap $k$ in the model's coordinates, either (a) change the coordinates so it has lower leap (a feature map, a native product term), or (b) supply intermediate targets that form a staircase (curriculum, scratchpad, deep supervision). Both are used; (b) is more general.

## Appendix D. Associative-memory capacity, in a page

**Linear memory with a feature map.** Store associations $S = \sum_{s=1}^m v_s \phi(k_s)^\top$. Reading with $\phi(k_j)$ gives $v_j\, \|\phi(k_j)\|^2 + \sum_{s \ne j} v_s\, \phi(k_s)^\top \phi(k_j)$. If the $\phi(k)$ are random with unit norm in $D = \dim \phi$ dimensions, the crosstalk term has standard deviation about $\sqrt{(m-1)/D}$ per unit of signal, so recall is reliable while $m \ll D$: capacity is proportional to $D$. A polynomial map of degree $p$ on $d$-dimensional keys has $D \approx \binom{d+p}{p}$, hence the polynomial capacity of dense memories with power-law energy. The delta rule removes crosstalk by projecting out the component along the key before writing, which is why it recalls exactly up to $m = D$ orthogonal keys and degrades gracefully after.

**Hopfield capacity.** With $\phi$ the identity and binary $\pm 1$ patterns, the signal-to-noise argument gives $m \approx N / (2 \ln N)$ for perfect recall (Krotov and Hopfield's criterion) and the Amit–Gutfreund–Sompolinsky analysis gives $0.138N$ for recall with a small error fraction.

**Dense memories.** With energy $E(s) = -\sum_\mu F(\xi^\mu \cdot s)$ and $F(x) = x^p$, the update aligns $s$ with the pattern whose overlap is largest, raised to the power $p$, and the signal-to-noise ratio improves by a factor $\sim m^{(p-1)/2}$ relative to the quadratic case; the capacity becomes $\sim N^{p-1}$. With $F = \exp$, the capacity is exponential in $N$ (Demircigil et al., 2017; exact constants in Lucibello and Mézard, 2024). Ramsauer et al. (2020) take $F = \exp$ with continuous states; the resulting update is the softmax-attention formula, so attention inherits the exponential capacity: it can single out one of exponentially many stored keys.

## Appendix E. The chunked scan that makes linear recurrences fast

Take a linear recurrence $S_t = A_t S_{t-1} + B_t$ with matrices $A_t$ (the transition) and $B_t$ (the write, for example $v_t k_t^\top$). Unrolling,

$$
S_t = \sum_{s \le t} \Big(\prod_{r = s+1}^{t} A_r\Big) B_s .
$$

A naive loop over $t$ is sequential. The chunked algorithm splits the sequence into blocks of length $C$ (typically 64). Within a block the outputs $o_t = S_t q_t$ for all $t$ in the block can be written as a $C \times C$ masked matrix of query–key interactions (the intra-chunk term, quadratic in $C$, cheap because $C$ is small) plus a term from the state at the start of the block (the inter-chunk term, one matrix product). The state at the end of the block is the state at the start multiplied by the product of the block's transitions, plus the block's accumulated writes. Across blocks this is a sequential scan of length $n / C$ with matrix products, or a parallel prefix scan of depth $\log(n/C)$.

For the delta rule, $A_t = I - \beta_t k_t k_t^\top$ is a rank-one perturbation of the identity, and a product of $C$ such matrices has the **WY form** $I - U T V^\top$ for $C$-column matrices $U, V$ and a $C \times C$ triangular $T$ (the representation used for Householder products in numerical linear algebra). Yang et al. (2024) use this to compute all of a chunk's transitions as dense matrix multiplications with one small triangular solve, which is how DeltaNet and Gated DeltaNet reach FlashAttention-class throughput. DeltaProduct's $n_h$ reflections per token are handled by treating the sequence as $n_h$ times longer; Mamba-3's MIMO form widens $B_t$ to multiple columns per token so that the matrix products do more useful work per byte moved.

## Glossary

- **Arity**: number of tokens an operation combines at once; attention scores have arity 2.
- **Associative memory**: a store of key–value pairs retrievable by (approximate) key.
- **Binding**: representing which attribute belongs to which object in a single vector; usually by a product.
- **Chunkwise parallel**: computing a recurrence over blocks with matrix products so training parallelises.
- **Cascade** (Krohn–Rhodes): automata composed so that each stage's transition depends on earlier stages' states.
- **Commutator**: $aba^{-1}b^{-1}$; the identity iff $a$ and $b$ commute.
- **Deep supervision**: a loss applied at every iteration or layer, not only at the end.
- **Delta rule**: $S \leftarrow S + \beta (v - Sk) k^\top$; write the error, not the value.
- **Dense associative memory**: a Hopfield-type memory with energy of degree above two; capacity grows with degree.
- **Fast weights**: parameters written by the network's own activations during a forward pass.
- **Globality degree**: the number of tokens that must be looked at jointly before the target correlates with the input.
- **Hybrid**: an architecture mixing fixed-state (linear, SSM) layers and attention layers.
- **Irrep**: irreducible representation; a building block of all representations of a group.
- **KV cache**: stored keys and values of past tokens for decoding.
- **Leap**: the largest number of new coordinates a learner must pick up at once; governs SGD time.
- **Looped / recurrent-depth model**: a block applied repeatedly with shared weights.
- **Mesa-optimisation**: an optimiser implemented inside a forward pass by the learned weights.
- **Non-solvable group**: a group not built from abelian quotients; $A_5$ and $S_5$ are the smallest examples.
- **Residual stream**: the per-token vector that every layer reads and adds to.
- **State tracking**: maintaining the composition of a sequence of transformations; the word problem of a group.
- **Test-time training**: updating weights on the test input before predicting.
- **$\mathbf{TC^0}$**: constant-depth threshold circuits; the class of fixed-depth transformers.
- **Word problem**: given a sequence of group elements, compute (or test) their product.

---

## References

Entries are alphabetical by first author. arXiv identifiers are given where the work is on arXiv; venue is given where the work was published. Preprints and vendor posts are marked as such.

- Abbe, E., Boix-Adserà, E., Brennan, M., Bresler, G., Nagaraj, D. (2022). The merged-staircase property. COLT. arXiv:2202.08658.
- Abbe, E., Boix-Adserà, E., Misiakiewicz, T. (2023). SGD learning on neural networks: leap complexity and saddle-to-saddle dynamics. COLT. arXiv:2302.11055.
- Abbe, E., Bengio, S., Lotfi, A., Sandon, C., Saremi, O. (2024). How far can transformers reason? The globality barrier and inductive scratchpad. NeurIPS. arXiv:2406.06467.
- Ainslie, J. et al. (2023). GQA: training generalized multi-query transformer models from multi-head checkpoints. arXiv:2305.13245.
- Akyürek, E., Schuurmans, D., Andreas, J., Ma, T., Zhou, D. (2022). What learning algorithm is in-context learning? ICLR 2023. arXiv:2211.15661.
- Akyürek, E., Damani, M., Qiu, L., Guo, H., Kim, Y., Andreas, J. (2024). The surprising effectiveness of test-time training for abstract reasoning. arXiv:2411.07279.
- Alam, M. M., Raff, E., Biderman, S., Oates, T., Holt, J. (2023). Recasting self-attention with holographic reduced representations. ICML. arXiv:2305.19534.
- Alman, J., Song, Z. (2023). How to capture higher-order correlations? Generalizing matrix softmax attention to Kronecker computation. ICLR 2024. arXiv:2310.04064.
- Altabaa, A., Webb, T., Cohen, J., Lafferty, J. (2023). Abstractors and relational cross-attention. ICLR 2024. arXiv:2304.00195.
- Amit, D. J., Gutfreund, H., Sompolinsky, H. (1985). Storing infinite numbers of patterns in a spin-glass model of neural networks. Physical Review Letters 55, 1530.
- Arjovsky, M., Shah, A., Bengio, Y. (2016). Unitary evolution recurrent neural networks. ICML. arXiv:1511.06464.
- Arora, S. et al. (2023). Zoology: measuring and improving recall in efficient language models. arXiv:2312.04927. (2024) Simple linear attention language models balance the recall-throughput tradeoff (Based). arXiv:2402.18668.
- Bae, S. et al. (2025). Mixture-of-Recursions: learning dynamic recursive depths for adaptive token-level computation. arXiv:2507.10524.
- Bahdanau, D., Cho, K., Bengio, Y. (2014). Neural machine translation by jointly learning to align and translate. ICLR 2015. arXiv:1409.0473.
- Barak, B., Edelman, B., Goel, S., Kakade, S., Malach, E., Zhang, C. (2022). Hidden progress in deep learning: SGD learns parities near the computational limit. NeurIPS. arXiv:2207.08799.
- Barrington, D. A. (1989). Bounded-width polynomial-size branching programs recognize exactly those languages in NC¹. JCSS 38(1), 150–164.
- Barrington, D. A. M., Thérien, D. (1988). Finite monoids and the fine structure of NC¹. JACM 35(4), 941–952.
- Behrouz, A., Zhong, P., Mirrokni, V. (2024). Titans: learning to memorize at test time. arXiv:2501.00663.
- Behrouz, A., Razaviyayn, M., Zhong, P., Mirrokni, V. (2025). It's all connected: a journey through test-time memorization, attentional bias, retention, and online optimization (Miras). ICLR 2026. arXiv:2504.13173.
- Behrouz, A. et al. (2025). Atlas: learning to optimally memorize the context at test time. ICML 2026. arXiv:2505.23735.
- Behrouz, A., Razaviyayn, M., Zhong, P., Mirrokni, V. (2025). Nested learning: the illusion of deep learning architectures. NeurIPS. arXiv:2512.24695.
- Beniaguev, D., Segev, I., London, M. (2021). Single cortical neurons as deep artificial neural networks. Neuron 109(17). bioRxiv 613141.
- ByteDance Seed (Zhu, R. et al.) (2025). Scaling latent reasoning via looped language models (Ouro). arXiv:2510.25741.
- Chakrabarti, S., Pitassi, T., Alman, J. (2026). Poly-attention: a general scheme for higher-order self-attention. ICLR. arXiv:2602.02422.
- Chiang, D., Cholak, P., Pillay, A. (2023). Tighter bounds on the expressivity of transformer encoders. ICML. arXiv:2301.10743.
- Chollet, F. (2019). On the measure of intelligence. arXiv:1911.01547. Chollet, F. et al. (2025). ARC-AGI-2: a new challenge for frontier AI reasoning systems. arXiv:2505.11831. ARC Prize 2024 technical report, arXiv:2412.04604; ARC Prize 2025 technical report, arXiv:2601.10904; "The hidden drivers of HRM's performance on ARC-AGI", arcprize.org, August 2025.
- Choromanski, K. et al. (2020). Rethinking attention with Performers. ICLR 2021. arXiv:2009.14794.
- Chughtai, B., Chan, L., Nanda, N. (2023). A toy model of universality: reverse engineering how networks learn group operations. ICML. arXiv:2302.03025.
- Clift, J., Doryn, D., Murfet, D., Wallbridge, J. (2019). Logic and the 2-simplicial transformer. ICLR 2020. arXiv:1909.00668.
- Cohen, T., Welling, M. (2016). Group equivariant convolutional networks. ICML. arXiv:1602.07576.
- Dao, T. et al. (2022). FlashAttention. NeurIPS. arXiv:2205.14135. Dao (2023) FlashAttention-2, arXiv:2307.08691. Shah, J. et al. (2024) FlashAttention-3, arXiv:2407.08608.
- Dao, T., Gu, A. (2024). Transformers are SSMs: generalized models and efficient algorithms through structured state space duality (Mamba-2). ICML. arXiv:2405.21060.
- Dauphin, Y., Fan, A., Auli, M., Grangier, D. (2017). Language modeling with gated convolutional networks. ICML. arXiv:1612.08083.
- DeepSeek-AI (2024). DeepSeek-V2 (multi-head latent attention). arXiv:2405.04434. Yuan, J. et al. (2025). Native sparse attention. arXiv:2502.11089. DeepSeek-AI (2025). DeepSeek-V3.2 (DeepSeek Sparse Attention). arXiv:2512.02556.
- Dehghani, M., Gouws, S., Vinyals, O., Uszkoreit, J., Kaiser, Ł. (2018). Universal transformers. ICLR 2019. arXiv:1807.03819.
- Delétang, G. et al. (2023). Neural networks and the Chomsky hierarchy. ICLR. arXiv:2207.02098.
- Demircigil, M., Heusel, J., Löwe, M., Upgang, S., Vermet, F. (2017). On a model of associative memory with huge storage capacity. J. Stat. Phys. arXiv:1702.01929.
- DiCarlo, J. J., Zoccolan, D., Rust, N. C. (2012). How does the brain solve visual object recognition? Neuron 73(3).
- Elhage, N. et al. (2021). A mathematical framework for transformer circuits. transformer-circuits.pub.
- Fan, Y., Du, Y., Ramchandran, K., Lee, K. (2024). Looped transformers for length generalization. ICLR 2025. arXiv:2409.15647.
- Feng, G., Zhang, B., Gu, Y., Ye, H., He, D., Wang, L. (2023). Towards revealing the mystery behind chain of thought. NeurIPS. arXiv:2305.15408.
- Feng, J., Steinhardt, J. (2023). How do language models bind entities in context? ICLR 2024. arXiv:2310.17191.
- Furst, M., Saxe, J., Sipser, M. (1984). Parity, circuits, and the polynomial-time hierarchy. Math. Systems Theory 17. Håstad, J. (1987). Computational limitations of small-depth circuits. MIT Press.
- Gallant, S. I., Okaywe, T. W. (2013). Representing objects, relations, and sequences. Neural Computation 25(8).
- Garg, S., Tsipras, D., Liang, P., Valiant, G. (2022). What can transformers learn in-context? A case study of simple function classes. NeurIPS. arXiv:2208.01066.
- Gayler, R. (2003). Vector symbolic architectures answer Jackendoff's challenges for cognitive neuroscience. ICCS/ASCS.
- Geiping, J. et al. (2025). Scaling up test-time compute with latent reasoning: a recurrent depth approach (Huginn). NeurIPS. arXiv:2502.05171.
- Geva, M., Schuster, R., Berant, J., Levy, O. (2021). Transformer feed-forward layers are key-value memories. EMNLP. arXiv:2012.14913.
- Giannou, A., Rajput, S., Sohn, J., Lee, K., Lee, J. D., Papailiopoulos, D. (2023). Looped transformers as programmable computers. ICML. arXiv:2301.13196.
- Gidon, A. et al. (2020). Dendritic action potentials and computation in human layer 2/3 cortical neurons. Science 367(6473).
- Graves, A. (2016). Adaptive computation time for recurrent neural networks. arXiv:1603.08983.
- Grazzi, R., Siems, J., Zela, A., Franke, J., Hutter, F., Pontil, M. (2025). Unlocking state-tracking in linear RNNs through negative eigenvalues. ICLR. arXiv:2411.12537.
- Gu, A., Goel, K., Ré, C. (2021). Efficiently modeling long sequences with structured state spaces (S4). ICLR 2022. arXiv:2111.00396.
- Gu, A., Dao, T. (2023). Mamba: linear-time sequence modeling with selective state spaces. arXiv:2312.00752.
- Ha, D., Dai, A., Le, Q. (2016). HyperNetworks. ICLR 2017. arXiv:1609.09106.
- Hahn, M. (2020). Theoretical limitations of self-attention in neural sequence models. TACL 8. arXiv:1906.06755.
- Hao, S. et al. (2024). Training large language models to reason in a continuous latent space (Coconut). arXiv:2412.06769.
- Hao, Y., Angluin, D., Frank, R. (2022). Formal language recognition by hard attention transformers: perspectives from circuit complexity. TACL. arXiv:2204.06618.
- Haviv, A., Ram, O., Press, O., Izsak, P., Levy, O. (2022). Transformer language models without positional encodings still learn positional information. arXiv:2203.16634.
- Hebb, D. O. (1949). The Organization of Behavior. Wiley.
- Hochreiter, S., Schmidhuber, J. (1997). Long short-term memory. Neural Computation 9(8).
- Hoffmann, J. et al. (2022). Training compute-optimal large language models (Chinchilla). arXiv:2203.15556.
- Hoover, B. et al. (2023). Energy Transformer. NeurIPS. arXiv:2302.07253.
- Hopfield, J. J. (1982). Neural networks and physical systems with emergent collective computational abilities. PNAS 79(8).
- Jayakumar, S. M. et al. (2020). Multiplicative interactions and where to find them. ICLR.
- Jelassi, S., Brandfonbrener, D., Kakade, S., Malach, E. (2024). Repeat after me: transformers are better than state space models at copying. ICML. arXiv:2402.01032.
- Jolicoeur-Martineau, A. (2025). Less is more: recursive reasoning with tiny networks (TRM). arXiv:2510.04871.
- Jordan, K. et al. (2024). Muon: an optimizer for hidden layers in neural networks. kellerjordan.github.io. Liu, J. et al. (Moonshot, 2025). Muon is scalable for LLM training. arXiv:2502.16982.
- Kafraj, M. S., Krotov, D., Latham, P. E. (2026). A biologically plausible dense associative memory with exponential capacity. ICLR. arXiv:2601.00984.
- Kanerva, P. (2009). Hyperdimensional computing. Cognitive Computation 1(2).
- Kaplan, J. et al. (2020). Scaling laws for neural language models. arXiv:2001.08361.
- Kar, K., Kubilius, J., Schmidt, K., Issa, E. B., DiCarlo, J. J. (2019). Evidence that recurrent circuits are critical to the ventral stream's execution of core object recognition behavior. Nature Neuroscience 22, 974–983.
- Katharopoulos, A., Vyas, A., Pappas, N., Fleuret, F. (2020). Transformers are RNNs: fast autoregressive transformers with linear attention. ICML. arXiv:2006.16236.
- Kazemnejad, A. et al. (2023). The impact of positional encoding on length generalization in transformers. NeurIPS. arXiv:2305.19466.
- Kietzmann, T. C. et al. (2019). Recurrence is required to capture the representational dynamics of the human visual system. PNAS 116(43).
- Kondor, R., Trivedi, S. (2018). On the generalization of equivariance and convolution in neural networks to the action of compact groups. ICML. arXiv:1802.03690.
- Kozachinskiy, A. et al. (2025). Strassen attention: unlocking compositional abilities in transformers. NeurIPS. arXiv:2501.19215.
- Krohn, K., Rhodes, J. (1965). Algebraic theory of machines, I. Trans. AMS 116.
- Krotov, D., Hopfield, J. J. (2016). Dense associative memory for pattern recognition. NeurIPS. arXiv:1606.01164.
- Lamme, V. A. F., Roelfsema, P. R. (2000). The distinct modes of vision offered by feedforward and recurrent processing. Trends in Neurosciences 23(11).
- Lezcano-Casado, M., Martínez-Rubio, D. (2019). Cheap orthogonal constraints in neural networks. ICML. arXiv:1901.08428.
- Li, Z., Liu, H., Zhou, D., Ma, T. (2024). Chain of thought empowers transformers to solve inherently serial problems. ICLR. arXiv:2402.12875.
- Lieber, O. et al. (AI21, 2024). Jamba: a hybrid transformer-Mamba language model. arXiv:2403.19887.
- Liu, B., Ash, J. T., Goel, S., Krishnamurthy, A., Zhang, C. (2022). Transformers learn shortcuts to automata. ICLR 2023. arXiv:2210.10749.
- Lucibello, C., Mézard, M. (2024). Exponential capacity of dense associative memories. Physical Review Letters 132. arXiv:2304.14964.
- Luong, M.-T., Pham, H., Manning, C. D. (2015). Effective approaches to attention-based neural machine translation. EMNLP. arXiv:1508.04025.
- Merrill, W., Sabharwal, A. (2023a). The parallelism tradeoff: limitations of log-precision transformers. TACL. arXiv:2207.00729. (2023b). A logic for expressing log-precision transformers. NeurIPS. arXiv:2210.02671. (2024). The expressive power of transformers with chain of thought. ICLR. arXiv:2310.07923. (2025). A little depth goes a long way: the expressive power of log-depth transformers. NeurIPS. arXiv:2503.03961.
- Merrill, W., Petty, J., Sabharwal, A. (2024). The illusion of state in state-space models. ICML. arXiv:2404.08819.
- MiniMax (2025). MiniMax-01: scaling foundation models with lightning attention. arXiv:2501.08313. MiniMax (2025). Why did M2 end up as a full attention model? minimax.io (vendor post).
- Mongillo, G., Barak, O., Tsodyks, M. (2008). Synaptic theory of working memory. Science 319(5869).
- Moonshot AI (2025). Kimi Linear: an expressive, efficient attention architecture. arXiv:2510.26692 (technical report). Lu, E. et al. (2025). MoBA: mixture of block attention. arXiv:2502.13189.
- Musialski, P. (2026). The token is a group element: on Lie-algebra attention over matrix Lie groups. arXiv:2606.20547 (preprint).
- Nadaraya, E. A. (1964). On estimating regression. Theory Prob. Appl. 9. Watson, G. S. (1964). Smooth regression analysis. Sankhyā A 26.
- Nanda, N., Chan, L., Lieberum, T., Smith, J., Steinhardt, J. (2023). Progress measures for grokking via mechanistic interpretability. ICLR. arXiv:2301.05217.
- Narang, S. et al. (2021). Do transformer modifications transfer across implementations and applications? EMNLP. arXiv:2102.11972.
- NVIDIA (2025). Nemotron-H: a family of accurate and efficient hybrid Mamba-Transformer models. arXiv:2504.03624. NVIDIA (2025). Nemotron 3. arXiv:2512.20856. Dong, X. et al. (2024). Hymba. arXiv:2411.13676.
- Olsson, C. et al. (2022). In-context learning and induction heads. transformer-circuits.pub. arXiv:2209.11895.
- OpenAI (2025). gpt-oss model card. arXiv:2508.10925. Google (2025). Gemma 3 technical report. arXiv:2503.19786.
- Peng, B. et al. (2023). RWKV: reinventing RNNs for the transformer era. arXiv:2305.13048. Peng, B. et al. (2025). RWKV-7 "Goose" with expressive dynamic state evolution. arXiv:2503.14456.
- Peng, B., Narayanan, S., Papadimitriou, C. (2024). On limitations of the transformer architecture. arXiv:2402.08164.
- Petty, J. et al. (2024). The impact of depth on compositional generalization in transformer language models. NAACL. arXiv:2310.19956.
- Plate, T. A. (1995). Holographic reduced representations. IEEE Trans. Neural Networks 6(3).
- Power, A., Burda, Y., Edwards, H., Babuschkin, I., Misra, V. (2022). Grokking. arXiv:2201.02177.
- Press, O., Smith, N., Lewis, M. (2021). Train short, test long: attention with linear biases (ALiBi). ICLR 2022. arXiv:2108.12409.
- Qiu, Z. et al. (Qwen, 2025). Gated attention for large language models: non-linearity, sparsity, and attention-sink-free. NeurIPS (best paper). arXiv:2505.06708.
- Quispe Flores, C. M., Salvatierra, S., Cabrera, R. (2026). All you need is non-commutative words. arXiv:2608.29314 (preprint).
- Qwen Team (2025). Qwen3-Next: towards ultimate training and inference efficiency. Model card and blog, September 2025.
- Ramsauer, H. et al. (2020). Hopfield networks is all you need. ICLR 2021. arXiv:2008.02217.
- Ren, L. et al. (Microsoft, 2024). Samba. arXiv:2406.07522.
- Roy, A. et al. (Meta, 2025). Fast and Simplex: 2-simplicial attention in Triton. arXiv:2507.02754.
- Rumelhart, D. E., Hinton, G. E., McClelland, J. L. (1986). A general framework for parallel distributed processing. In Parallel Distributed Processing, vol. 1. MIT Press.
- Sanford, C., Hsu, D., Telgarsky, M. (2023). Representational strengths and limitations of transformers. NeurIPS. arXiv:2306.02896. (2024). Transformers, parallel computation, and logarithmic depth. ICML. arXiv:2402.09268.
- Saunshi, N. et al. (2025). Reasoning with latent thoughts: on the power of looped transformers. ICLR. arXiv:2502.17416.
- Schlag, I., Irie, K., Schmidhuber, J. (2021). Linear transformers are secretly fast weight programmers. ICML. arXiv:2102.11174.
- Schmidhuber, J. (1992). Learning to control fast-weight memories: an alternative to dynamic recurrent networks. Neural Computation 4(1). Ba, J., Hinton, G., Mnih, V., Leibo, J., Ionescu, C. (2016). Using fast weights to attend to the recent past. NeurIPS. arXiv:1610.06258.
- Shazeer, N. (2020). GLU variants improve transformer. arXiv:2002.05202.
- Siems, J., Carstensen, T., Zela, A., Hutter, F., Pontil, M., Grazzi, R. (2025). DeltaProduct: improving state-tracking in linear RNNs via Householder products. NeurIPS. arXiv:2502.10297.
- Smolensky, P. (1990). Tensor product variable binding and the representation of symbolic structures in connectionist systems. Artificial Intelligence 46.
- Snell, C., Lee, J., Xu, K., Kumar, A. (2024). Scaling LLM test-time compute optimally can be more effective than scaling model parameters. arXiv:2408.03314. DeepSeek-AI (2025). DeepSeek-R1. arXiv:2501.12948.
- So, D. R. et al. (2021). Primer: searching for efficient transformers for language modeling. NeurIPS. arXiv:2109.08668.
- Stander, D., Yu, Q., Fan, H., Biderman, S. (2024). Grokking group multiplication with cosets. ICML. arXiv:2312.06581. Wu, W., Jaburi, L., Drori, J., Gross, J. (2024). Unifying and verifying mechanistic interpretations: a case study with group operations. arXiv:2410.07476.
- Strobl, L., Merrill, W., Weiss, G., Chiang, D., Angluin, D. (2024). What formal languages can transformers express? A survey. TACL. arXiv:2311.00208.
- Su, J. et al. (2021). RoFormer: enhanced transformer with rotary position embedding. arXiv:2104.09864.
- Sun, Y. et al. (2020). Test-time training with self-supervision for generalization under distribution shifts. ICML. arXiv:1909.13231. Sun, Y. et al. (2024). Learning to (learn at test time): RNNs with expressive hidden states. arXiv:2407.04620.
- Sun, Y. et al. (Microsoft, 2023). Retentive network. arXiv:2307.08621.
- Tay, Y. et al. (2022). Scaling laws vs model architectures: how does inductive bias influence scaling? arXiv:2207.10551.
- Thorpe, S., Fize, D., Marlot, C. (1996). Speed of processing in the human visual system. Nature 381.
- Vaswani, A. et al. (2017). Attention is all you need. NeurIPS. arXiv:1706.03762.
- von Oswald, J. et al. (2023). Transformers learn in-context by gradient descent. ICML. arXiv:2212.07677. von Oswald, J. et al. (2025). MesaNet: sequence modeling by locally optimal test-time training. ICLR 2026. arXiv:2506.05233.
- Wang, G. et al. (Sapient Intelligence, 2025). Hierarchical reasoning model. arXiv:2506.21734.
- Wang, K. A., Shi, J., Fox, E. B. (2025). Test-time regression: a unifying framework for designing sequence models with associative memory. JMLR 27 (2026). arXiv:2501.12352.
- Webb, T., Sinha, I., Cohen, J. (2021). Emergent symbols through binding in external memory. ICLR. arXiv:2012.14601. Webb, T. et al. (2024). The relational bottleneck as an inductive bias for efficient abstraction. Trends in Cognitive Sciences. arXiv:2309.06629.
- Wei, J. et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. NeurIPS. arXiv:2201.11903.
- Weiss, G., Goldberg, Y., Yahav, E. (2021). Thinking like transformers (RASP). ICML. arXiv:2106.06981.
- Widrow, B., Hoff, M. E. (1960). Adaptive switching circuits. IRE WESCON Convention Record.
- Yang, S., Wang, B., Shen, Y., Panda, R., Kim, Y. (2023). Gated linear attention transformers with hardware-efficient training. ICML 2024. arXiv:2312.06635.
- Yang, S., Wang, B., Zhang, Y., Shen, Y., Kim, Y. (2024). Parallelizing linear transformers with the delta rule over sequence length. NeurIPS. arXiv:2406.06484.
- Yang, S., Kautz, J., Hatamizadeh, A. (2024). Gated delta networks: improving Mamba2 with delta rule. ICLR 2025. arXiv:2412.06464.
- Yang, S. et al. (2025). PaTH attention: position encoding via accumulating Householder transformations. arXiv:2505.16381.
- Yang, S., Zhang, Y. et al. flash-linear-attention. github.com/fla-org/flash-linear-attention.
- Yang, L., Lee, K., Nowak, R., Papailiopoulos, D. (2024). Looped transformers are better at learning learning algorithms. ICLR. arXiv:2311.12424.
- Zhang, Y., Qin, Z., Wang, M., Gu, Q. (2025). Higher-order linear attention. arXiv:2510.27258.
- Zhao, Y., Lu, J., Huang, B., Zhang, G., Zhou, J. (Tencent, 2026). Most transformer modifications still do not transfer at 1–3B: a 2020–2026 update to Narang et al. (2021) with downstream evaluation and a noise floor. arXiv:2605.20798 (preprint).
- Zuo, Y. et al. (2025). Local linear attention: an optimal interpolation of linear and softmax attention for test-time regression. arXiv:2510.01450. Zuo, Y. et al. (2026). Parallax: parameterized local linear attention for language modeling. arXiv:2605.29157.
- 2026 preprints cited in Chapters 3–4 (titles as listed on arXiv): Gated DeltaNet-2: decoupling erase and write in linear attention, arXiv:2605.22791; Complex KDA: understanding and enhancing the expressivity of Kimi Delta Attention, arXiv:2609.24797; Mamba-3: improved sequence modeling using state space principles, ICLR 2026, arXiv:2603.15569; Rational Transductors, arXiv:2602.07599; Linearized 2-simplicial attention, arXiv:2608.09307; Closing the loop: practical training recipes for looped language models, arXiv:2610.00673; Towards looped models done right, arXiv:2610.23036; Sapunov, G., Universal transformers need memory: depth-state trade-offs in adaptive recursive reasoning, arXiv:2604.21999; MeSH: memory-as-state-highways for recursive transformers, ICLR 2026; Attention as binding: a vector-symbolic perspective on transformer reasoning, arXiv:2512.14709.
