# L3 prior art: interpretability, steering, fine-tuning mechanics and KV-cache policies

Area L3 of six. Claims checked: C4 (latent table executor in Qwen3-4B), C5 (the pinned clock as a cache policy),
C7 (mechanism), C8 (plain decoding drifts), with C1/C2 where the interpretability literature touches them.
Compiled 28 October 2026. Spend: $0.

**How every entry was verified.**
- **arXiv works (203 entries, plus two citing papers named in §6).** Each id was looked up on 28 October 2026
  through the arXiv API (`export.arxiv.org/api/query?id_list=…`). The returned title was checked against the intended paper; one
  placeholder id that returned an unrelated paper was dropped. Authors, first-version date, author comment, journal
  reference and abstract are saved in `research/prior_art/L3_verified_arxiv.json`.
- **Full text.** For the closest papers I read the method and results sections from the arXiv HTML full text:
  Prakash 2024, Yang 2026 (learned task vectors), Todd 2024 (including its appendix task list), Jain 2023,
  Petrov 2024, ReFT, StreamingLLM, Gur-Arieh 2026, Yang 2025 (symbolic mechanisms), Zhong & Andreas 2024,
  Sinii 2025 (small vectors), Wu 2025 (retrieval heads), Prakash 2025 (lookbacks), Block-Attention, Akyürek 2024,
  Markovian Thinker, PENCIL and Prompt Cache.
- **Non-arXiv pages (6).** Each was fetched live; the entry gives its URL.
- **Venues.** A venue is given only when one of these confirms it: the arXiv comment or journal reference, a
  fetched proceedings page, or a proceedings URL returned by search. Otherwise the entry gives the arXiv year alone.
  Semantic Scholar was rate-limited, so I stopped querying it.
- **Limits.**
  - The shared web-search budget ran out near the end. The items I could not verify are listed in §6.
  - Summaries of works I did not read in full rest on their abstracts.

**What the existing notes already cover.** `LITERATURE.md` has 85 works and `NOVELTY.md` covers v1. Neither covers
this area, apart from Kim & Schuster 2023 and the Markovian Thinker. The v2 `refs.bib`
(`paper-v2/paper/jewel/refs.bib`) cites none of the works below, and that includes the Markovian Thinker, which the
v1 draft did cite.

---

## 0. Verdict in five lines

- **C4 is safe in substance but not in framing.**
  - Two things are established already: fine-tuning sharpens a lookup circuit the base model already has (Prakash
    2024), and one learned vector at one middle layer switches on an in-context task (Todd 2024; Yang 2026; Sinii
    2025).
  - Our new content is narrower. The vector switches on an executor whose program arrives at run time, and the
    result is certified table by table and exact at length.
- **C5 is a known policy family plus one new ingredient.**
  - The known part: StreamingLLM's sink and window with positions assigned within the cache, and the Markovian
    Thinker's "keep the query, re-encode a carryover, delete the rest".
  - The new part is block alignment. It is the ingredient that makes decoding bitwise equal to the certified row,
    and the finite certificate that this identity makes sufficient.
- **C7 matches several mechanism papers.** The content-over-position fetch matches Gur-Arieh 2026 and the two-stage
  read-out matches Yang 2025 and Wiegreffe 2025. We should present ours as instances of these, with numbers, not as
  discoveries.
- **C8's attention shift has names already.** It is the attention decay of Li 2024 (instruction drift) and the
  lookback ratio of Chuang 2024 (contextual hallucination). We found no earlier measurement of it in a task where
  every step can be checked exactly.
- **Nobody in this literature certifies anything.** Every result here is an average accuracy or a faithfulness
  score. Per-row certificates and bitwise long runs are our distinct contribution in this area.

---

## 1. The five most dangerous papers (C4, C5, C7)

### 1.1 Prakash, Rott Shaham, Haklay, Belinkov, Bau. *Fine-Tuning Enhances Existing Mechanisms: A Case Study on Entity Tracking.* ICLR 2024. arXiv:2402.14811. <https://arxiv.org/abs/2402.14811>

**What they did (full text read).**
- **Task and models.** Their task is an in-context lookup table. Seven boxes each hold an object, and the model
  answers "Box X contains" with the object. Base Llama-7B gets 0.66; Goat-7B and FLoat-7B, both fine-tuned on
  arithmetic, get 0.82 (chance 0.14).
- **Circuit.** Path patching finds a 72-head circuit in four groups:
  - Value Fetcher, 40 heads at the last token, which attend to the correct object;
  - Position Transmitter, 7 heads;
  - Position Detector, 20 heads;
  - Structure Reader, 5 heads.
- **Base circuit in the fine-tuned models.** It recovers at least 88% of their performance. Their own circuits
  (175 heads) are roughly supersets of it.
- **Positional information.** Desiderata-based masking shows the circuit tracks entities mainly by position.
- **Cross-model patching.** Patching the fine-tuned models' Value Fetcher outputs into the base model lifts it to
  fine-tuned performance. Their conclusion: fine-tuning "enhances, rather than fundamentally alters" the mechanism.

**Overlap.**
- **C4: "the interpreter is already in the base model; thirty steps switch it on"** has the same structure as
  their result. The base finds the row (L7.H7, 92%), fails at the read-out (35% of rows), and fine-tuning
  strengthens value-reading heads. Their Value Fetchers are our destination-reading heads.
- **C7: the ~30–45-head committee** has the same order of size as their 40 Value Fetchers.

**Where we differ.**
- Our fine-tuning is on the task itself, and the edits that suffice are tiny.
- Our base model's bottleneck is the read-out specifically.
- Our fetch is by content, with the positional pointer unused, while theirs is positional.
- We certify per row and run exact at length.

**Reword.**
- *Do not say:* "we discover that the executor is latent and fine-tuning switches it on."
- *Say:* "As Prakash et al. found for entity tracking, a short fine-tune sharpens a lookup circuit the base model
  already has. Here the base model already selects the matched row (L7.H7, 92%) but fails to read its destination
  (35% of rows). The edit recruits destination-reading heads, and the result can be certified table by table."

**Tests it suggests.**
1. **Cross-model activation patching (CMAP).** Patch Savant's outputs from the ~45 recruited heads into base Qwen3-4B
   on the same inputs. If rows go from 35% to about 99%, the whole gain is in the read-out heads, as in their Value
   Fetcher result.
2. **Desiderata-based masking (their DCM; Davies 2023).** Label each committee head as carrying destination value,
   row position or (source, event) match.
3. **Head overlap.** Report the overlap between base and edited models in their format (e.g. 27/40 in Group A).

### 1.2 Yang, Cho, Ding, Inoue. *Task Vectors, Learned Not Extracted: Performance Gains and Mechanistic Insight.* ICLR 2026. arXiv:2509.24169. <https://arxiv.org/abs/2509.24169>

Read together with Todd et al. 2024 (*Function Vectors*, ICLR 2024, arXiv:2310.15213) and Hendel et al. 2023
(*In-Context Learning Creates Task Vectors*, Findings of EMNLP 2023, arXiv:2310.15916).

**What they did (full text read).**
- **The learned task vector (LTV).** A d-dimensional vector is added to one layer's hidden state and trained by
  gradient descent.
- **Accuracy.** With the vector at layer 16 of Llama-3.1-8B, last token, it reaches 83.5%. Extracted task vectors
  reach 37.8% and function vectors 37.3%.
- **Against other methods at the same parameter count** (SST-2): the LTV gets 92.9%, rank-1 LoRA 91.6% and prefix
  tuning 85.7%.
- **Mechanism.** The vector acts mainly through attention-head OV circuits. A small set of "key heads" sits just
  after the injection layer and in the final layers. Its propagation is close to linear: a rotation early, a
  rescaling late.

**What Todd and Hendel add.**
- **Function vectors.** The summed mean outputs of 10–100 causally selected heads, added at about L/3, switch on a
  task zero-shot. On GPT-J zero-shot accuracy goes from 5.5% to 57.5%; on Llama-2-70B from 8.2% to 83.8%.
- **The tasks include procedures over in-context items** (I checked the appendix list): "Choose First / Middle /
  Last of List", "Next-Item", "Previous-Item". The vector carries the procedure, not the answer.

**Overlap with C4.**
- Our "one vector of 2,560 numbers added to layer 18's output" is a learned task vector.
  - BIGIDEA's E8 adds it at every position, which makes it a bias on one layer (BitFit-like; a ReFT with W = 0).
  - BIGIDEA's E7 adds the same-sized vector at the tick's two positions only. That is the closer analogue of their
    last-token setting.
- So "a single learned vector at a middle layer switches on an in-context procedure the model cannot do zero-shot"
  is established.
- Also close:
  - Sinii et al. (EMNLP 2025): one RL-trained vector per layer matches full RL on maths;
  - Sinii et al. 2025: a single vector at layer 16 of Qwen2.5-Math-7B recovers 40.1 of the 43.8 maths score.

**What stays ours.**
- **The procedure is an executor.** Its program (the table) is new on every input, with up to thousands of rows
  matched on two keys.
- **Certification.** The vector certifies 431/512 held-out tables, and long runs on accepted tables are exact for
  10,000 steps.
- **Neither paper certifies anything or tests length.**

**Reword.**
- *Say:* "a learned task vector (Yang et al. 2026), i.e. a bias on layer 18's output".
- *Say:* "it switches on an executor whose program is supplied at run time".
- *Do not say:* "a single vector unlocks an algorithm", as if that were new.

**Tests it suggests.**
1. **Extract a function vector by Todd's method** from few-shot table-execution prompts. For the corrupted prompts,
   shuffle the destinations.
   - Add it at about layer 12 (L/3) and at layer 18.
   - Compare it with our vector: row accuracy, certified tables, cosine similarity.
   - If the function vector gets most of the way, say so: the executor is then an ICL task the base model already
     represents.
2. **Replicate their mechanism analysis.**
   - Reconstruct the effect through OV circuits only.
   - Find the key heads and their overlap with our destination-reading committee.
   - Fit one linear map per layer.
3. **Last-token-only versus all-position injection, and a layer sweep.**

### 1.3 Xiao, Tian, Chen, Han, Lewis. *Efficient Streaming Language Models with Attention Sinks* (StreamingLLM). ICLR 2024. arXiv:2309.17453. <https://arxiv.org/abs/2309.17453>

Read together with Aghajohari et al., *The Markovian Thinker* (arXiv:2510.06557, 2025).

**StreamingLLM (full text read).**
- **The policy.** It keeps the KV of 4 initial "sink" tokens plus a rolling window.
- **Positions.** It assigns positions "within the cache rather than those in the original text": keys are cached
  before RoPE and re-rotated each step, so the window always sits right after the sinks.
- **Window attention without sinks collapses.** On Llama-2-13B, perplexity is 5,158 for 0+1024 against 5.40 for
  4+1020.
- **Any token can be the sink.** Newlines serve as well as the original initial tokens.

**Markovian Thinker / Delethink (full text read).**
- **The policy.** Each chunk's context is the original query plus the last m tokens of the previous chunk. The cache
  is cleared at each boundary and the carryover re-encoded fresh, so everything else is deleted.
- **Off-the-shelf models already do this.** R1-Distill 1.5B–14B, GPT-OSS-120B and Qwen3-30B-A3B already reason
  "Markovianly" zero-shot under this policy.
- **Positions.** The paper does not say how positions are assigned.

**Overlap with C5.**
- **Our policy in StreamingLLM's terms.** "Keep Π as a sink, evict each 2-token block, restart positions after Π" is
  StreamingLLM with the sink set to Π and a window of one block, positions relative to the cache.
- **Our policy in Delethink's terms.** It is Delethink at the finest grain: the query is Π, and the carryover is
  the state plus the next event, re-encoded fresh.
- **Related ideas.**
  - PENCIL (ICML 2025): erasing finished thoughts lets a fixed transformer simulate any Turing machine in
    space-optimal context.
  - Oren et al. 2024: a bounded cache turns a transformer into a finite multi-state RNN.
- **Our own baseline already isolates the new ingredient.** BIGIDEA's SW2b is StreamingLLM with Π as the sink and
  cache-relative positions. It fails (5/8 runs exact, and no tick bitwise a certified row) only because a sliding
  window keeps each token's KV as it was computed, which carries history in through 36 layers.

**What is new.**
1. Block alignment, i.e. fresh re-encoding of exactly the current pair, is the ingredient that makes decoding equal
   the certified row bit for bit.
2. That identity makes a finite per-row certificate sufficient at every length.
3. A gap between Π and the block costs margin: positions must be adjacent, not just relative.

**Reword.**
- *Say:* "The pinned clock is StreamingLLM's sink-and-window policy with the program as the sink and a window of
  exactly one freshly encoded (state, event) block. That is the Markovian Thinker's chunking at a two-token grain."
- *Do not say* "StreamingLLM fails" without the qualifier "with the program as the sink, k = 2–4". Otherwise a
  reviewer will read the four-token default as a straw man.
- *Avoid calling Π a "sink".* In this literature a sink is an uninformative token that absorbs excess attention, and
  Π is the most informative part of the context. Write "the persistent prefix (StreamingLLM's sink slot)".

**Tests it suggests.**
1. **A factorial grid.** Sink = 4 tokens or Π; window sliding or block-aligned; positions cache-relative or textual.
2. **Delethink carryovers.** Fresh re-encoding with m = 2, 4, 8 and 32. Run it on Savant and on the base model plus
   the vector edit. The vector edit was not trained on fresh pairs, so this tests BIGIDEA's guess that history is
   noise only because the executor saw fresh pairs.
3. **StreamingLLM as published.** Four sink tokens and a window that must hold Π, to show what the default does.

### 1.4 Gur-Arieh, Geva, Geiger. *Mixing Mechanisms: How Language Models Retrieve Bound Entities In-Context.* ICLR 2026. arXiv:2510.06182. <https://arxiv.org/abs/2510.06182>

Read together with Prakash et al. 2025 (*Language Models use Lookbacks to Track Beliefs*, arXiv:2505.14685), Feng &
Steinhardt 2023 (*binding IDs*, arXiv:2310.17191) and Dai et al. 2024 (*ordering IDs*, arXiv:2409.05448).

**What they did (full text read).**
- **Setup.** Nine instruction-tuned models (Gemma-2, Qwen2.5, Llama-3.1; 2–72B) answer queries over up to 20 bound
  entity groups.
- **Three mechanisms**, separated by interchange interventions:
  - positional (the index of the queried group);
  - lexical (through the bound partner, i.e. by content);
  - reflexive (a direct pointer).
- **Where each dominates.** The positional mechanism controls behaviour mainly for the first and last groups. In
  the middle it explains about 20%, spread around the index, and lexical and reflexive retrieval take over.
- **Model fit.** A mixture of the three fits the next-token distributions with Jensen–Shannon similarity 0.95,
  against 0.44 for position alone.
- **Padding.** Up to 500 filler tokens between groups strengthens the positional mechanism.

**What the other three papers show.** Prakash 2025, Dai 2024 and Feng & Steinhardt 2023 show that ordering or
binding IDs work as pointers that are dereferenced by matching.

**Overlap with C7.** "A redundant committee reads the destination by content; a positional pointer exists (R² 0.80)
but is unused (≤ 1.4% of outputs)" is the lexical mechanism winning over the positional one. They report this
regime for lists longer than a few groups.

**What stays ours.**
- Tables of up to 4,096 rows matched on two keys.
- A quantified pointer that is unused.
- The positional signal inherited from the base model and left unused after the edit.

**Reword.** Present the pointer result as an instance: "consistent with Gur-Arieh et al., where positional retrieval
is reliable only at list ends and content-based retrieval dominates large lists." Do not present it as a finding
about LLMs in general.

**Tests it suggests.**
1. **Their counterfactual triad on Savant.** Swap rows so that positional, lexical and reflexive predictions
   disagree, and report the shares by table size and row index.
2. **Row 0 (WEIGHTS §6).** Their model predicts the ends behave differently, and row 0 is our weakest row. Check
   whether the positional mechanism, or sink behaviour (§1.3, H27–H29), explains it.
3. **Filler between rows.** Their padding result predicts more positional reliance.

### 1.5 Yang, Campbell, Huang, Wang, Cohen, Webb. *Emergent Symbolic Mechanisms Support Abstract Reasoning in Large Language Models.* ICML 2025. arXiv:2502.20332. <https://arxiv.org/abs/2502.20332>

Read together with Wiegreffe et al. 2025 (*Answer, Assemble, Ace*, ICLR 2025, arXiv:2407.15018) and Lieberum et al.
2023 (Chinchilla multiple choice, arXiv:2307.09458).

**What they did (full text read).** Llama-3.1-70B, whose rule induction is 95% accurate at 2 shots, works in three
stages:
1. symbol-abstraction heads, early;
2. symbolic-induction heads, intermediate, which predict an abstract variable (abstract RSA r = 0.69);
3. retrieval heads, late, which fetch the literal token bound to that variable (token RSA r = 0.55).

Ablating the top heads of each type takes accuracy to zero.

**What Wiegreffe adds.** In multiple-choice answering, a few middle layers' attention selects the answer symbol and
later layers raise its probability in vocabulary space.

**Overlap with C7.** "The answer is first the best of the table's states (layer ~24), then the vocabulary argmax
(~30)" is this two-stage read-out: select among in-context candidates, then promote the token. Our base model's
typical error, copying the current state, is an induction-style failure.

**Reword.** "the two-stage read-out also seen in abstract rule induction (Yang et al.) and multiple-choice answering
(Wiegreffe et al.)".

**Tests it suggests.**
1. **Confirm the layer numbers with a tuned lens** (Belrose 2023). The logit lens is biased in middle layers, and
   reviewers know it.
2. **Patch attention outputs only at layers 20–26.** This tests whether the state-selection stage is attention-driven,
   as in multiple-choice answering.
3. **Find "retrieval heads" by token RSA.** Do not confuse them with Wu et al.'s retrieval heads (A9 in §3).

### Runners-up (each must be cited; none pre-empts a claim)

| paper | claim | why it matters |
|---|---|---|
| Jain et al. 2023, *Mechanistically analyzing the effects of fine-tuning on procedurally defined tasks* (2311.12786) | C4 | Fine-tuning learns a "wrapper" over an existing capability. Pruning 5–15 neurons restores the old behaviour, and reverse fine-tuning revives it in 0.1–1K steps. This is the standard citation for "small, localised change". |
| Petrov, Torr, Bibi, ICLR 2024 (2310.19698) | C4 | Prefix tuning cannot change relative attention over content; it elicits or combines pretrained skills (90–98%) but fails at a new attention pattern (0%). This is the best citation for reading our soft-prompt result as elicitation. Their 2024 universality paper (2402.14753) shows the limit is not absolute in principle. |
| Zhong & Andreas, NeurIPS 2024 (2410.04368) | C4 | Random, frozen transformers with trained embeddings solve associative recall 100%. "Latent in the pretrained model" needs a random-weights or early-checkpoint control. |
| Wu et al., ICLR 2025, *Retrieval heads* (2404.15574) | C4, C7 | Fewer than 5% of heads copy from context. They exist in the base model and survive continued pretraining and chat tuning (correlation of scores > 0.8). This is the precedent for L7.H7 being inherited. |
| Li et al., COLM 2024, *instruction drift* (2402.10962); Chuang et al., EMNLP 2024, *Lookback Lens* (2407.07071) | C8 | Attention decays away from the system prompt and the context, and the ratio of attention to context against own generations predicts hallucination. This is our "attention to Π falls 17×, to history doubles". |
| Akyürek et al. 2024, *n-gram heads* (2401.12973) | C7 | Transformers learn regular languages in context with heads that attend to the token after earlier occurrences of the current 2-gram. Our (source, event) → destination fetch is a 2-gram induction. |
| Sinii et al., EMNLP 2025 (2505.18706) and 2025 (2509.06608); Ward et al. 2025 (2511.06739); Morris et al. 2026 (2602.04118); Schulman 2025 (*LoRA Without Regret*) | C4 | Tiny edits elicit large capability: one vector per layer ≈ full RL; rank-1 LoRA recovers 73–90%; 13 parameters reach 91% on GSM8K; rank-1 suffices for RL. Our edit curve sits inside this literature. |
| Gim et al., MLSys 2024, *Prompt Cache* (2311.04934) | C5 | They claim discontinuous position IDs are harmless "as long as the relative position of tokens is preserved". Our gap result (55/55 → 45/55 at a gap of 4) contradicts this at the margin level, which is worth one sentence. |
| Wang et al. 2026, *Random Attention* (2609.03430); Chen et al., ACL 2026, *Pitfalls of KV Cache Compression* (2510.00231) | C5 | Both support us: in reasoning, keeping the prompt intact is what matters, and compression silently drops instructions. |

---

## 2. Rewording table (one line per claim)

| claim | current wording risk | suggested wording |
|---|---|---|
| C4 latent executor | "the interpreter is already in the base model; 30 steps switch it on" reads as a discovery | "the base model already selects the matched row (L7.H7, 92%) but fails to read its destination; as in Prakash et al. 2024, a short fine-tune sharpens this existing circuit" |
| C4 single vector | "one 2,560-number vector unlocks the executor" | "a learned task vector (Yang et al. 2026), i.e. a bias on layer 18's output, switches on an executor whose program is supplied at run time; 431/512 tables certified" |
| C4 soft prompt | "no weight touched, so the executor is latent" | "a soft prompt elicits it; prefix-style edits elicit rather than create attention patterns (Petrov et al. 2024); language logits are bitwise unchanged by construction" |
| C4 rank / layers | "changes concentrate in layers 12–17 and rank 4" | cite intrinsic dimension (Aghajanyan 2021) and skill localisation (Panigrahi 2023); note that the RL subnetwork literature finds sparse but full-rank updates (Mukherjee 2025), while ours are low-rank |
| C5 pinned clock | "a KV-cache policy we introduce" | "StreamingLLM's sink-and-window with the program as the sink and a block-aligned window of one (state, event) pair, i.e. Markovian chunking (Aghajohari et al. 2025) at a two-token grain; alignment is what makes it bitwise" |
| C5 Π as "sink" | the term "sink" | "persistent prefix (StreamingLLM's sink slot)" |
| C5 "StreamingLLM fails" | reads as a straw man | "StreamingLLM with the whole program as the sink and sliding windows k = 2–4 fails (5/8, 0/8, 0/8)" |
| C7 content committee | "the fetch is by content; a pointer exists but is unused" | "an instance of the lexical-over-positional regime of Gur-Arieh et al. 2026, quantified: ≤ 1.4% of outputs follow the pointer" |
| C7 two-stage read-out | "first the best state, then the vocabulary" | "the two-stage read-out of Yang et al. 2025 and Wiegreffe et al. 2025, confirmed with a tuned lens" |
| C7 sharp steps | "robust cells inside an LLM" | cite stable regions (Janiak 2024) and activation plateaus (Ferreira da Silva & Heimersheim 2026); ours are measured between two discrete program states |
| C8 drift | "attention shifts from the program to the run's own history" | "the attention decay of Li et al. 2024 and the lookback ratio of Chuang et al. 2024, measured where every step can be checked" |
| naming | "clock" | Nanda 2023, Zhong 2023 and Kantamneni 2025 use "Clock" for a modular-arithmetic algorithm in which numbers sit on a circle; define ours on first use, or call it "pinned decoding" |

---

## 3. The annotated list

Closeness: **3** pre-empts part of a claim (reword needed); **2** overlaps a component (must cite, may need a
control); **1** related (cite if space allows); **0** background. All URLs were checked on 28 October 2026. arXiv
records were fetched through the API; pages marked *(page fetched)* were opened directly.

### A. Lookup, retrieval, induction and copying circuits

**A1. Elhage, Nanda, Olsson et al. (2021). A Mathematical Framework for Transformer Circuits.** Transformer
Circuits Thread. <https://transformer-circuits.pub/2021/framework/index.html> *(page fetched)*.
Splits each head into a QK circuit (where to attend) and an OV circuit (what to write), and treats the residual
stream as a communication channel. Head composition gives induction heads in two-layer models.
*Closeness 1 · C7.* Supplies the vocabulary for "scores near-additive in role": test it on the QK circuit, not on
attention weights.

**A2. Olsson, Elhage, Nanda et al. (2022). In-context Learning and Induction Heads.** arXiv:2209.11895.
<https://arxiv.org/abs/2209.11895>.
Induction heads complete [A][B]…[A] → [B]; they appear at the same point as a jump in in-context learning. The
evidence is causal for small attention-only models and correlational for large ones.
*Closeness 2 · C4, C7.* L7.H7, which picks the matched row, is an induction-type matcher over (source, event) keys.
Cite it as the origin of the row-matching mechanism.

**A3. Singh, Moskovitz, Hill et al. (2024). What needs to go right for an induction head?** arXiv:2404.07129.
<https://arxiv.org/abs/2404.07129>.
Causal study of how induction circuits form and which subcomponents they need.
*Closeness 1 · C7.* Background for the formation curve (Fig. 3a).

**A4. Akyürek, Wang, Kim, Andreas (2024). In-Context Language Learning: Architectures and Algorithms.**
arXiv:2401.12973. <https://arxiv.org/abs/2401.12973> *(full text read)*.
Random-DFA languages are learned in context. Transformers win, using "n-gram heads" that attend to the token after
earlier occurrences of the current 2-gram. Adding static n-gram heads lowers language-model perplexity by 2.6–6.7%.
*Closeness 2 · C7.* Our fetch is a 2-gram induction over (source, event) followed by a read of the destination.
Cite it, and test whether committee heads have n-gram-head attention signatures.

**A5. Feucht, Todd, Wallace, Bau (2025). The Dual-Route Model of Induction.** COLM 2025. arXiv:2504.03022.
<https://arxiv.org/abs/2504.03022>.
Concept-level induction heads copy whole multi-token words and token-level heads copy verbatim. The two routes are
independent, and ablating token heads makes the model paraphrase instead of copy.
*Closeness 2 · C7 (size limited by weak or fragment names).* This suggests a mechanism for our failures (` illeg`
vs ` illegal`, ` Zahl` vs ` zahl`): concept-level matching merges near-duplicates. Test by scoring committee heads
on token versus concept induction and ablating each.

**A6. Feucht, Atkinson, Wallace, Bau (2024). Token Erasure as a Footprint of Implicit Vocabulary Items in LLMs.**
arXiv:2406.20086. <https://arxiv.org/abs/2406.20086>.
The last-token representations of multi-token words "erase" their constituent tokens. That is evidence for implicit
word-level vocabulary items.
*Closeness 1 · C7.* A fragment name (` illeg`) is a token that is normally part of a word, so its representation
may be weak. This supports screening the name pool by tokenisation.

**A7. Crosbie & Shutova (2024). Induction Heads as an Essential Mechanism for Pattern Matching in In-context
Learning.** arXiv:2407.07011. <https://arxiv.org/abs/2407.07011>.
Even a minimal ablation of induction heads cuts abstract pattern-recognition ICL by up to about 32%, close to
random, in Llama-3-8B and InternLM2-20B. It also brings few-shot NLP performance close to zero-shot.
*Closeness 1 · C7.* Supports ablation as the test of the committee's necessity.

**A8. Yin & Steinhardt (2025). Which Attention Heads Matter for In-Context Learning?** ICML 2025.
arXiv:2502.14010. <https://arxiv.org/abs/2502.14010>.
Across 12 models, few-shot ICL depends mainly on function-vector heads, not induction heads. Many FV heads start as
induction heads during training.
*Closeness 2 · C4, C7.* Our row matcher is induction-like and our read-out heads may be FV-like. Classify the
committee heads by both scores.

**A9. Wu, Wang, Xiao, Peng, Fu (2025). Retrieval Head Mechanistically Explains Long-Context Factuality.** ICLR
2025. arXiv:2404.15574. <https://arxiv.org/abs/2404.15574> *(full text read)*.
"Retrieval heads" (copy-paste score ≥ 0.1 on needle tests) are 3–6% of heads. Their scores correlate above 0.8
between a base model and its long-context and chat derivatives. Masking them breaks needle retrieval and chain of
thought.
*Closeness 2 · C4, C7.* This is the precedent for an inherited, sparse lookup set that fine-tuning preserves. Our
committee (~30 heads) is larger than their always-on set (12 in Llama-2-7B). Do not call our heads "retrieval
heads" unless we compute their score.

**A10. Zhao, Yin, Durrett (2025). Understanding Synthetic Context Extension via Retrieval Heads.** ICML 2025.
arXiv:2410.22316. <https://arxiv.org/abs/2410.22316>.
Fine-tuning on synthetic long-context data teaches retrieval heads. How closely they match the heads learned on
real data predicts downstream performance.
*Closeness 2 · C4 ("thirty steps recruit ~45 destination-reading heads").* Recruiting heads by fine-tuning on
synthetic retrieval data is documented. Cite it beside Prakash.

**A11. Zhang, Yin, Yen et al. (2025). Query-Focused Retrieval Heads Improve Long-Context Reasoning and
Re-ranking.** EMNLP 2025. arXiv:2506.09944. <https://arxiv.org/abs/2506.09944>.
Identifies heads whose query-to-context attention ranks relevant passages, and uses them as a retriever.
*Closeness 1 · C7.* Supports using a single head's attention (L7.H7) as a row selector.

**A12. Kahardipraja, Achtibat, Wiegand et al. (2025). The Atlas of In-Context Learning.** NeurIPS 2025.
arXiv:2505.15807. <https://arxiv.org/abs/2505.15807>.
In retrieval-augmented QA, "in-context heads" read instructions and retrieve from context while "parametric heads"
hold relational knowledge. Function vectors from these heads change answers.
*Closeness 1 · C7.* A precedent for splitting heads into those that read context and those that read weights.

**A13. Bietti, Cabannes, Bouchacourt et al. (2023). Birth of a Transformer: A Memory Viewpoint.** NeurIPS 2023.
arXiv:2306.00802. <https://arxiv.org/abs/2306.00802>.
Treats weight matrices as associative memories and studies how induction heads form, in a controlled setting.
*Closeness 1 · C7.* Theory for the key-value view of the lookup.

**A14. Arora, Eyuboglu, Timalsina et al. (2023). Zoology: Measuring and Improving Recall in Efficient Language
Models.** arXiv:2312.04927. <https://arxiv.org/abs/2312.04927>.
82% of the quality gap between attention and gated-convolution models is explained by recall of information
mentioned earlier in context (associative recall). The paper formalises multi-query associative recall (MQAR).
*Closeness 1 · C7.* Associative recall is the standard name for our lookup's primitive.

**A15. Geva, Schuster, Berant, Levy (2021). Transformer Feed-Forward Layers Are Key-Value Memories.** EMNLP
2021. arXiv:2012.14913. <https://arxiv.org/abs/2012.14913>.
MLP keys detect input patterns and their values induce output distributions.
*Closeness 1 · C7.* Background on lookups held in the weights, which contrast with our in-context lookup.

**A16. Geva, Caciularu, Wang, Goldberg (2022). Transformer Feed-Forward Layers Build Predictions by Promoting
Concepts in the Vocabulary Space.** EMNLP 2022. arXiv:2203.14680. <https://arxiv.org/abs/2203.14680>.
FFN updates promote interpretable concepts in vocabulary space.
*Closeness 1 · C7.* A candidate account of the second, vocabulary stage of the read-out (layers ~24 → 30).

**A17. Meng, Bau, Andonian, Belinkov (2022). Locating and Editing Factual Associations in GPT (ROME).** NeurIPS
2022. arXiv:2202.05262. <https://arxiv.org/abs/2202.05262>.
Causal tracing localises factual recall to mid-layer MLPs at the subject token, and a rank-one weight edit changes
a fact.
*Closeness 1 · C4.* An early example of a rank-one edit with a targeted effect. Ours is rank-1 per module and
changes a procedure, not a fact.

**A18. Hernandez, Sharma, Haklay et al. (2023). Linearity of Relation Decoding in Transformer Language
Models.** arXiv:2308.09124. <https://arxiv.org/abs/2308.09124>.
Many relations are decoded by one affine map from the subject representation.
*Closeness 1 · C7.* Our "R² 0.80 linear probe for row position" and near-linear read-outs fit this picture.

**A19. Lindsey, Gurnee, Ameisen et al. (2025). On the Biology of a Large Language Model.** Transformer Circuits
Thread, 27 March 2025. <https://transformer-circuits.pub/2025/attribution-graphs/biology.html> *(page fetched)*.
Attribution graphs on Claude 3.5 Haiku. Addition uses "lookup table" features (e.g. inputs ending in 6 and 9
promote outputs ending in 5) in parallel with rough-magnitude paths.
*Closeness 1 · C4, C7.* "Lookup table" is already used for in-weight features. Say "in-context table" to avoid
confusion.

**A20. Chen, Plaat, van Stein (2026). Every Component Is a Lookup: One Linear Graph for Interaction, Composition
and Attribution.** arXiv:2605.23393. <https://arxiv.org/abs/2605.23393>.
Attention and MLPs share a key-value form. Freezing the selections turns the model into a linear graph for
attribution.
*Closeness 1 · C7.* A possible tool for the role-additivity analysis.

**A21. Wang, Variengien, Conmy et al. (2022). Interpretability in the Wild: a Circuit for Indirect Object
Identification in GPT-2 small.** arXiv:2211.00593. <https://arxiv.org/abs/2211.00593>.
A 26-head circuit with name movers, backup name movers and negative heads.
*Closeness 1 · C7.* Backup heads are the classic form of redundancy; our committee is a scaled-up case.

**A22. McDougall, Conmy, Rushing et al. (2023). Copy Suppression: Comprehensively Understanding an Attention
Head.** arXiv:2310.04625. <https://arxiv.org/abs/2310.04625>.
GPT-2 head L10H7 suppresses tokens that earlier heads copied, which explains self-repair.
*Closeness 1 · C7.* Check the committee for negative or copy-suppression heads, which may make "copy the current
state" errors.

**A23. Gould, Ong, Ogden, Conmy (2023). Successor Heads.** arXiv:2312.09230.
<https://arxiv.org/abs/2312.09230>.
Heads that increment ordinal tokens (Monday → Tuesday) recur across models.
*Closeness 1 · C7.* Relevant to the clock and counter families, which fail on rows that cross 12. The base model
may prefer its successor prior over the table.

**A24. Merullo, Eickhoff, Pavlick (2024). Circuit Component Reuse Across Tasks in Transformer Language Models.**
ICLR 2024. arXiv:2310.08744. <https://arxiv.org/abs/2310.08744>.
The IOI circuit is largely reused for a different task (Colored Objects).
*Closeness 1 · C4.* Supports "recycled circuitry" (INSIGHTS §5).

**A25. Lieberum, Rahtz, Kramár et al. (2023). Does Circuit Analysis Interpretability Scale? Evidence from
Multiple Choice Capabilities in Chinchilla.** arXiv:2307.09458. <https://arxiv.org/abs/2307.09458>.
In 70B Chinchilla, "correct letter" heads select the answer label given the answer text.
*Closeness 2 · C7.* An analogue of the state-selection stage: choose among in-context symbols, then emit.

**A26. Wiegreffe, Tafjord, Belinkov et al. (2025). Answer, Assemble, Ace: Understanding How LMs Answer Multiple
Choice Questions.** ICLR 2025. arXiv:2407.15018. <https://arxiv.org/abs/2407.15018>.
The answer symbol is chosen by middle-layer attention, and later layers raise its probability in vocabulary space.
*Closeness 2 · C7.* See §1.5.

**A27. Yang, Campbell, Huang et al. (2025). Emergent Symbolic Mechanisms Support Abstract Reasoning in Large
Language Models.** ICML 2025. arXiv:2502.20332. <https://arxiv.org/abs/2502.20332> *(full text read)*.
See §1.5.
*Closeness 2–3 · C7.*

**A28. Thavarasa & Sukumar (2026). Test, then Route: How Language Models Execute In-Context Conditional
Rules.** arXiv:2608.04183. <https://arxiv.org/abs/2608.04183>.
For in-context "if P then A else B" rules, a mid-stack residual band carries the predicate's truth value (patching
flips the outcome near 1.0 in 17/18 cells). The "router" is a token-bound direction that does not transfer.
*Closeness 2 · C7.* The closest 2026 study of in-context rule execution. Its split (an abstract test in the middle,
a token-bound read-out late) matches ours. Cite it, and note the contrast: our read-out generalises across tables.

**A29. Jobanputra, Veitsman, Sarrof et al. (2025). Born a Transformer — Always a Transformer?** NeurIPS 2025.
arXiv:2505.21785. <https://arxiv.org/abs/2505.21785>.
Pretrained models retrieve to the right of a query token (induction) better than to the left (anti-induction).
Targeted fine-tuning removes the asymmetry when theory guarantees length generalisation.
*Closeness 1 · C4.* Small fine-tunes reshape retrieval circuits in pretrained LMs. Our fetch reads the token after
the matched keys, which is the easy, induction direction.

**A30. Chan, Santoro, Lampinen et al. (2022). Data Distributional Properties Drive Emergent In-Context Learning
in Transformers.** NeurIPS 2022. arXiv:2205.05055. <https://arxiv.org/abs/2205.05055>.
Burstiness and many rare classes drive in-context learning.
*Closeness 0.* Background.

**A31. Zheng, Wang, Huang et al. (2024). Attention Heads of Large Language Models: A Survey.** arXiv:2409.03752.
<https://arxiv.org/abs/2409.03752>.
A taxonomy of head functions.
*Closeness 0.* Useful for naming the head types in the committee.

### B. Binding, entity tracking, pointers and state

**B1. Feng & Steinhardt (2023). How do Language Models Bind Entities in Context?** arXiv:2310.17191.
<https://arxiv.org/abs/2310.17191>.
Binding-ID vectors attached to entities and attributes form a continuous subspace, and distance in it predicts how
well bindings can be told apart. The mechanism appears in every large enough Pythia and LLaMA model.
*Closeness 2 · C7.* Our near-additive scores over role may be binding-ID-like. Its "discernibility" is the margin
our weak names lack.

**B2. Dai, Heinzerling, Inui (2024). Representational Analysis of Binding in Language Models.**
arXiv:2409.05448. <https://arxiv.org/abs/2409.05448>.
Localises a low-rank "ordering ID" subspace that causally sets which attribute is bound.
*Closeness 2 · C7.* Our R² 0.80 position probe is likely this ordering-ID signal, inherited and unused.

**B3. Davies, Nadeau, Prakash, Rott Shaham, Bau (2023). Discovering Variable Binding Circuitry with
Desiderata.** arXiv:2307.03637. <https://arxiv.org/abs/2307.03637>.
A mask-learning method finds the components that meet stated causal desiderata. It finds shared variable-binding
circuitry in LLaMA-13B.
*Closeness 1 · C7.* The method to label committee heads (§5, idea 4).

**B4. Prakash, Rott Shaham, Haklay, Belinkov, Bau (2024). Fine-Tuning Enhances Existing Mechanisms.** ICLR 2024.
arXiv:2402.14811. <https://arxiv.org/abs/2402.14811> *(full text read)*.
See §1.1.
*Closeness 3 · C4, C7.*

**B5. Prakash, Shapira, Sharma et al. (2025). Language Models use Lookbacks to Track Beliefs.**
arXiv:2505.14685. <https://arxiv.org/abs/2505.14685> *(full text read)*.
In Llama-3-70B, entities get ordering IDs. A "pointer" copied to a later token forms an attention query that
dereferences the matching "address", and the payload is then fetched (binding, answer and visibility lookbacks, in
layers 20–56).
*Closeness 2 · C7.* Their pointer and address language is the obvious vocabulary for our fetch. Their retrieval goes
through ordering IDs, ours through content. "Lookback" is also their name for it, so avoid it as a term.

**B6. Gur-Arieh, Geva, Geiger (2026). Mixing Mechanisms.** ICLR 2026. arXiv:2510.06182.
<https://arxiv.org/abs/2510.06182> *(full text read)*.
See §1.4.
*Closeness 3 · C7.*

**B7. Wu, Geiger, Millière (2025). How Do Transformers Learn Variable Binding in Symbolic Programs?** ICML 2025.
arXiv:2505.20896. <https://arxiv.org/abs/2505.20896>.
A small transformer trained on multi-hop variable dereferencing learns it (> 99.9%), with an interpretable
mechanism.
*Closeness 1 · C7.* From-scratch analogue of dereferencing. Our setting is a pretrained LLM.

**B8. Kim & Schuster (2023). Entity Tracking in Language Models.** ACL 2023. arXiv:2305.02363.
<https://arxiv.org/abs/2305.02363> (already in LITERATURE.md #81).
*Closeness 1 · C4.* The task of B4.

**B9. Li, Nye, Andreas (2021). Implicit Representations of Meaning in Neural Language Models.** ACL 2021.
arXiv:2106.00737. <https://arxiv.org/abs/2106.00737>.
Entity states are linearly decodable from LM representations.
*Closeness 1 · C4.* Background for the R² 0.80 probe.

**B10. Li, Hopkins, Bau et al. (2023). Emergent World Representations (Othello-GPT).** ICLR 2023.
arXiv:2210.13382. <https://arxiv.org/abs/2210.13382> (in LITERATURE.md).
*Closeness 1.*

**B11. Park, Lee, Lubana et al. (2025). ICLR: In-Context Learning of Representations.** ICLR 2025.
arXiv:2501.00070. <https://arxiv.org/abs/2501.00070>.
Given random walks on a graph in context, Llama-3.1-8B's representations suddenly reorganise to match the graph,
unless the concepts have strong pretrained semantics (days of the week).
*Closeness 1–2 · C4, C7.* Our tables are an in-context graph. A semantically loaded table (clock hours) fighting
the pretrained successor structure is the case they describe. This is one explanation for clock failures at 12.

**B12. Li, Guo, Andreas (2025). (How) Do Language Models Track State?** ICML 2025. arXiv:2503.02854.
<https://arxiv.org/abs/2503.02854>.
LMs trained on permutation composition learn an associative scan or a parity-then-scan mechanism.
*Closeness 1 · C8* (another agent's area). Our pinned decoding removes the need for an internal scan.

**B13. Zhang, Du, Jin et al. (2025). Finite State Automata Inside Transformers with Chain-of-Thought.**
arXiv:2502.20129. <https://arxiv.org/abs/2502.20129>.
With chain of thought, late-layer MLP neuron sets encode the automaton state almost perfectly.
*Closeness 1 · C7.* Our state-selection stage at layer ~24 is the LLM counterpart.

**B14. Chen, Hu, Liu, Sun (2024). States Hidden in Hidden States.** arXiv:2407.11421.
<https://arxiv.org/abs/2407.11421>.
Discrete intermediate-result states can be decoded from LLM hidden states.
*Closeness 1.*

**B15. Cabannes, Arnal, Bouaziz et al. (2024). Iteration Head: A Mechanistic Study of Chain-of-Thought.**
arXiv:2406.02128. <https://arxiv.org/abs/2406.02128>.
CoT training produces "iteration heads" that attend to the previous step's position.
*Closeness 1 · C8.* In plain decoding the pointer is an iteration head over the run's own history; the clock
removes the need for it.

### C. Read-out stages and lenses

**C1. nostalgebraist (2020). interpreting GPT: the logit lens.** LessWrong, 31 August 2020.
<https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens> *(page fetched)*.
Applies the unembedding to intermediate layers.
*Closeness 1 · C7.* The method behind "best state at ~24, argmax at ~30".

**C2. Belrose, Ostrovsky, McKinney et al. (2023). Eliciting Latent Predictions from Transformers with the Tuned
Lens.** arXiv:2303.08112. <https://arxiv.org/abs/2303.08112>.
Per-layer learned affine probes fix the logit lens's bias and brittleness.
*Closeness 2 · C7 (method).* Reviewers will ask for it. Rerun the read-out analysis with a tuned lens before
quoting layer numbers.

**C3. Wendler, Veselovsky, Monea, West (2024). Do Llamas Work in English?** arXiv:2402.10588.
<https://arxiv.org/abs/2402.10588>.
Three phases (input, concept, output space) under the logit lens.
*Closeness 1 · C7.* A precedent for the "abstract choice first, token later" read-out.

**C4. Geva, Bastings, Filippova, Globerson (2023). Dissecting Recall of Factual Associations.** EMNLP 2023.
arXiv:2304.14767. <https://arxiv.org/abs/2304.14767>.
Subject enrichment, relation propagation, then attribute extraction by attention.
*Closeness 1 · C7.*

**C5. Halawi, Denain, Steinhardt (2024). Overthinking the Truth.** arXiv:2307.09476.
<https://arxiv.org/abs/2307.09476>.
With incorrect demonstrations, behaviour diverges from the correct case at a "critical layer". Late-layer "false
induction heads" then copy the false labels, and ablating them reduces the effect.
*Closeness 1 · C7.* Late copying heads are a candidate account of the base model's "copy the current state"
errors.

**C6. Lad, Lee, Gurnee, Tegmark (2024). The Remarkable Robustness of LLMs: Stages of Inference?**
arXiv:2406.19384. <https://arxiv.org/abs/2406.19384>.
Layer deletion and swapping suggest four stages, ending in residual sharpening.
*Closeness 1 · C7.*

**C7. Merullo, Eickhoff, Pavlick (2024). Language Models Implement Simple Word2Vec-style Vector Arithmetic.**
NAACL 2024. arXiv:2305.16130. <https://arxiv.org/abs/2305.16130>.
For relational ICL tasks (capitals, uppercasing, past tense), a key step is a simple additive FFN update. The
mechanism is specific to retrieval from pretraining memory, not retrieval from local context.
*Closeness 1 · C7.* Contrast: our fetch is from local context, so this mechanism should not be expected. It is a
useful negative prediction to state.

**C8. Ghandeharioun, Caciularu, Pearce et al. (2024). Patchscopes.** ICML 2024. arXiv:2401.06102.
<https://arxiv.org/abs/2401.06102>.
A framework that decodes hidden states by patching them into an inspection prompt.
*Closeness 1 · C7.* An alternative to the logit lens for the state-selection stage.

**C9. Biran, Gottesman, Yang et al. (2024). Hopping Too Late.** EMNLP 2024. arXiv:2406.12775.
<https://arxiv.org/abs/2406.12775>.
In two-hop queries the bridge entity resolves too late, leaving too few layers for the second hop. Back-patching
fixes up to 66% of failures.
*Closeness 2 · C4.* A mechanistic precedent for "finds the row but cannot read it out in time". Test it on the base
model: back-patch the layer-~10 representation (after L7.H7 selects the row) into a later layer and see whether
the destination appears.

**C10. Orgad, Toker, Gekhman et al. (2024). LLMs Know More Than They Show.** arXiv:2410.02707.
<https://arxiv.org/abs/2410.02707>.
Internal states encode correctness better than the outputs reveal.
*Closeness 1 · C4.* Supports the "knowing versus saying" framing of the base model's 92% against 35%.

**C11. Billa (2026). Predicting Where Steering Vectors Succeed.** arXiv:2604.15557.
<https://arxiv.org/abs/2604.15557>.
A logit-lens accessibility profile per layer predicts steering success (ρ 0.86–0.91) and the best layer.
*Closeness 1 · C4.* Check whether layer 18 is where the destination becomes linearly accessible.

### D. Decision geometry, stable regions and robustness

**D1. Park, Choe, Veitch (2024). The Linear Representation Hypothesis and the Geometry of LLMs.** ICML 2024.
arXiv:2311.03658. <https://arxiv.org/abs/2311.03658>.
*Closeness 1 · C7.* Background for linear state codes.

**D2. Park, Choe, Jiang, Veitch (2025). The Geometry of Categorical and Hierarchical Concepts in LLMs.** ICLR
2025. arXiv:2406.01506. <https://arxiv.org/abs/2406.01506>.
Extends the linear representation hypothesis so that categorical concepts are polytopes, and relates hierarchy to
geometry (Gemma, LLaMA-3; 900+ WordNet concepts).
*Closeness 1 · C7.* A frame for "the table's states as a polytope" in the state-selection stage.

**D3. Marks & Tegmark (2024). The Geometry of Truth.** COLM 2024. arXiv:2310.06824.
<https://arxiv.org/abs/2310.06824>.
*Closeness 0.*

**D4. Engels, Michaud, Liao et al. (2025). Not All Language Model Features Are One-Dimensionally Linear.** ICLR
2025. arXiv:2405.14860. <https://arxiv.org/abs/2405.14860>.
Circular features for days and months are used causally in modular tasks.
*Closeness 1 · C7.* The clock family's states may sit on a pretrained circle that competes with the table (rows
crossing 12).

**D5. Gurnee & Tegmark (2023). Language Models Represent Space and Time.** arXiv:2310.02207.
<https://arxiv.org/abs/2310.02207>.
*Closeness 0.*

**D6. Janiak, Karwowski, Mangat et al. (2024). Characterizing stable regions in the residual stream of LLMs.**
SciForDL workshop. arXiv:2409.17113. <https://arxiv.org/abs/2409.17113>.
The output is insensitive inside large regions and changes sharply at their boundaries. The regions sharpen with
training and scale and align with semantic distinctions.
*Closeness 2 · C7 (sharp decision steps), C1/C2 (robust cells).* The closest precedent for "the destination flips
within Δα = 0.05". Ours are between two discrete program states, with noise thresholds (1.5–3× residual norm). Cite
it and use their interpolation protocol for comparison.

**D7. Lee & Heimersheim (2024). Investigating Sensitive Directions in GPT-2.** arXiv:2410.12555.
<https://arxiv.org/abs/2410.12555>.
Corrects the baselines for activation-plateau and sensitive-direction experiments.
*Closeness 1 · C7.* Use their baseline when reporting robustness to noise.

**D8. Ferreira da Silva & Heimersheim (2026). Evidence for feature-specific error correction in LLMs.**
arXiv:2606.24964. <https://arxiv.org/abs/2606.24964>.
Residual activations sit on plateaus that resist small perturbations, less so along feature directions than along
mixtures. They read this as error correction that privileges feature directions.
*Closeness 2 · C2, C7.* An LLM-native "regeneration" result. Test whether Savant's state boundary is sharper along
the s → s′ direction than along random mixtures.

**D9. Black, Sharkey, Grinsztajn et al. (2022). Interpreting Neural Networks through the Polytope Lens.**
arXiv:2211.12312. <https://arxiv.org/abs/2211.12312>.
*Closeness 0–1.*

**D10. Zhao, Nguyen, Grover (2024). Probing the Decision Boundaries of In-context Learning in LLMs.** NeurIPS
2024. arXiv:2406.11233. <https://arxiv.org/abs/2406.11233>.
ICL decision boundaries on simple classification are irregular and non-smooth.
*Closeness 1 · C7.* Contrast: our boundaries are sharp and regular after the edit.

**D11. Stolfo, Wu, Gurnee et al. (2024). Confidence Regulation Neurons in Language Models.** NeurIPS 2024.
arXiv:2406.16254. <https://arxiv.org/abs/2406.16254>.
Entropy and token-frequency neurons calibrate confidence.
*Closeness 0–1 · C7.* Possible late-layer contributors to margins.

### E. Committees, redundancy and the decomposition of attention scores

**E1. Voita, Talbot, Moiseev et al. (2019). Analyzing Multi-Head Self-Attention.** ACL 2019. arXiv:1905.09418.
<https://arxiv.org/abs/1905.09418>.
A few specialised heads do most of the work and the rest can be pruned.
*Closeness 1 · C7.*

**E2. Michel, Levy, Neubig (2019). Are Sixteen Heads Really Better than One?** NeurIPS 2019. arXiv:1905.10650.
<https://arxiv.org/abs/1905.10650>.
*Closeness 1 · C7.*

**E3. McGrath, Rahtz, Kramar et al. (2023). The Hydra Effect: Emergent Self-repair in Language Model
Computations.** arXiv:2307.15771. <https://arxiv.org/abs/2307.15771>.
Ablating one attention layer makes another compensate.
*Closeness 2 · C7 ("redundant committee").* Single-head ablations underestimate importance. Report cumulative
ablation curves and measure compensation.

**E4. Rushing & Nanda (2024). Explorations of Self-Repair in Language Models.** ICML 2024. arXiv:2402.15390.
<https://arxiv.org/abs/2402.15390>.
Self-repair works through final LayerNorm scaling and anti-erasure neurons.
*Closeness 2 · C7.* Same implication.

**E5. Wang (2026). The Communication Map of a Transformer.** arXiv:2608.22007.
<https://arxiv.org/abs/2608.22007>.
Graph decomposition of head communication. Joint ablation of a head community does far more damage than the sum of
its parts.
*Closeness 1 · C7.* Supports measuring the committee's non-additivity.

**E6. Bali, Stanley, Suresh et al. (2026). Quantifying LLM Attention-Head Stability.** arXiv:2602.16740.
<https://arxiv.org/abs/2602.16740>.
Middle-layer heads are the least stable across independent training runs.
*Closeness 1 · C7.* L7.H7 and the mid-depth committee may be model-instance-specific. Say "in Qwen3-4B", not "in
LLMs".

**E7. Wang (2026). Function-Vector Heads Are Two Populations: Writers and Cancellers.** arXiv:2606.07560.
<https://arxiv.org/abs/2606.07560>.
Among FV heads, writers support the correct answer and cancellers suppress it. Removing cancellers raises accuracy
by 2.4–6.8 points.
*Closeness 1 · C7.* Look for cancellers among the base model's heads that may cause its copy-the-state errors.

**E8. Merullo, Eickhoff, Pavlick (2024). Talking Heads: Understanding Inter-layer Communication.** NeurIPS 2024.
arXiv:2406.09519. <https://arxiv.org/abs/2406.09519>.
Models write features into low-rank residual subspaces that later layers read. In GPT-2 a particular 3-D subspace
indexes the positions of items in a list, and this explains the model's sensitivity to item order.
*Closeness 2 · C7 ("a positional pointer exists but is unused"), C4 ("rank 4 per module").* A precedent for a
low-rank positional index over list items. Test whether our R² 0.80 row-position signal lives in a comparable
low-dimensional subspace, and whether Savant's update writes into it.

**E9. Kamath, Ameisen, Lindsey et al. (2025). Tracing Attention Computation Through Feature Interactions.**
Transformer Circuits Thread. <https://transformer-circuits.pub/2025/attention-qk/index.html> *(page fetched; title
confirmed on the page; authors and July 2025 date from a search snippet only)*.
Decomposes attention scores into bilinear interactions between query-side and key-side features (QK attributions),
including negative contributions.
*Closeness 2 · C7 ("scores close to additive in role but not certifiably so").* This is the tool for the
additivity question. Decompose the matched-row score into (source, event, destination) feature-pair terms and
report the interaction share.

**E10. He, Wang, Lin et al. (2025). Towards Understanding the Nature of Attention with Low-Rank Sparse
Decomposition (Lorsa).** arXiv:2504.20938. <https://arxiv.org/abs/2504.20938>.
A sparse replacement for attention that recovers cleaner induction, successor and sink heads.
*Closeness 1 · C7.* An option for decomposing the committee.

**E11. Franco & Crovella (2024). Sparse Attention Decomposition Applied to Circuit Tracing.** arXiv:2410.00340.
<https://arxiv.org/abs/2410.00340>.
*Closeness 1 · C7.*

**E12. Kissane, Krzyzanowski, Bloom et al. (2024). Interpreting Attention Layer Outputs with Sparse
Autoencoders.** arXiv:2406.17759. <https://arxiv.org/abs/2406.17759>.
*Closeness 0–1.*

### F. Fine-tuning mechanics: enhancing latent mechanisms, intrinsic dimension, rank and localisation

**F1. Jain, Kirk, Lubana et al. (2023). Mechanistically analyzing the effects of fine-tuning on procedurally
defined tasks.** arXiv:2311.12786. <https://arxiv.org/abs/2311.12786> *(full text read)*.
- **Settings.** Tracr-compiled models, PCFG-trained models and TinyStories.
- **Main finding.** Fine-tuning mostly learns a "wrapper" over an existing capability, which probes still detect.
- **Evidence.** Pruning 5–15 neurons restores the pretraining behaviour, and reverse fine-tuning revives it in
  0.1–1K steps.
- **Conditions.** Wrappers are most likely at small learning rates and with spurious correlations.

*Closeness 2–3 · C4.* This is the standard citation for "small, localised change". It also predicts that our
executor edit could be undone or bypassed cheaply. That is a safety-style caveat worth one line.

**F2. Wang, Hu, Du et al. (2025). Towards Understanding Fine-Tuning Mechanisms of LLMs via Circuit Analysis.**
arXiv:2502.11812. <https://arxiv.org/abs/2502.11812>.
On maths tasks where fine-tuning helps a lot, circuit nodes stay similar while edges change substantially. This
differs from Prakash's "adds components".
*Closeness 2 · C4.* Our head-map correlation (0.93 after the pilot) is a node-level measure. Report an edge-level
measure too, or say we did not.

**F3. Zhou, Liu, Xu et al. (2023). LIMA: Less Is More for Alignment.** arXiv:2305.11206.
<https://arxiv.org/abs/2305.11206>.
The superficial alignment hypothesis: knowledge comes from pretraining and alignment teaches format.
*Closeness 1 · C4.*

**F4. Lin, Ravichander, Lu et al. (2024). The Unlocking Spell on Base LLMs (URIAL).** arXiv:2312.01552.
<https://arxiv.org/abs/2312.01552>.
Alignment tuning shifts mostly stylistic tokens, and in-context alignment of the base model matches it.
*Closeness 1 · C4.*

**F5. Raghavendra, Nath, Hendryx (2024). Revisiting the Superficial Alignment Hypothesis.** arXiv:2410.03717.
<https://arxiv.org/abs/2410.03717>.
Post-training gains in reasoning follow a power law in the number of examples, so the hypothesis is "at best an
over-simplification".
*Closeness 1 · C4.* Balances F3 and F4. Our case is genuinely latent at the circuit level, but whole-table
certification still needs 10⁵–10⁶ parameters.

**F6. Aghajanyan, Zettlemoyer, Gupta (2021). Intrinsic Dimensionality Explains the Effectiveness of Language
Model Fine-Tuning.** ACL 2021. arXiv:2012.13255. <https://arxiv.org/abs/2012.13255>.
Optimising 200 parameters, randomly projected back into the full space, reaches 90% of full fine-tuning on MRPC
with RoBERTa. Pretraining lowers the intrinsic dimension.
*Closeness 2 · C4 (rank-1 and the 2,560 vector).* The classic precedent. Quote our edit curve as an
intrinsic-dimension measurement for the executor.

**F7. Li, Farkhoor, Liu, Yosinski (2018). Measuring the Intrinsic Dimension of Objective Landscapes.** ICLR
2018. arXiv:1804.08838. <https://arxiv.org/abs/1804.08838>.
*Closeness 1 · C4.*

**F8. Hu, Shen, Wallis et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models.** arXiv:2106.09685.
<https://arxiv.org/abs/2106.09685>.
*Closeness 1 · C4.*

**F9. Biderman, Portes, Gonzalez Ortiz et al. (2024). LoRA Learns Less and Forgets Less.** TMLR.
arXiv:2405.09673. <https://arxiv.org/abs/2405.09673>.
LoRA underperforms full fine-tuning on code and maths but forgets less.
*Closeness 1 · C4.* Consistent with our small ΔNLL (0.05–0.48 nats) for weight edits.

**F10. Shuttleworth, Andreas, Torralba, Sharma (2024). LoRA vs Full Fine-tuning: An Illusion of
Equivalence.** arXiv:2410.21228. <https://arxiv.org/abs/2410.21228>.
LoRA introduces "intruder dimensions" (new high-ranking singular vectors) that full fine-tuning does not.
*Closeness 1 · C4.* Relevant to the "top 4 singular directions" analysis. Check for intruder dimensions in Savant's
update.

**F11. Schulman and Thinking Machines Lab (29 Sept 2025). LoRA Without Regret.**
<https://thinkingmachines.ai/blog/lora/> *(page fetched)*.
LoRA matches full fine-tuning when applied to all layers (especially the MLPs) and not capacity-limited. For RL,
rank 1 suffices, since RL carries O(1) bits per episode. Attention-only LoRA underperforms MLP-only LoRA.
*Closeness 2 · C4.* Our rank-1 LoRA is attention-only (q, k, v, o) and supervised, yet certifies 98.6%. That fits a
low-information executor that sits in attention. Say so, and cite this as the contrast.

**F12. Ward, Riechers, Shai (2025). Rank-1 LoRAs Encode Interpretable Reasoning Signals.** NeurIPS 2025
MechInterp workshop. arXiv:2511.06739. <https://arxiv.org/abs/2511.06739>.
A rank-1 LoRA on Qwen-2.5-32B-Instruct recovers 73–90% of a full reasoning fine-tune, and its scalar activations
are as interpretable as neurons.
*Closeness 2 · C4.* Precedent for "rank-1 elicits most of a capability". Their per-module rank-1 scalars could
also be read out in Savant as an interpretability check.

**F13. Morris, Mireshghallah, Ibrahim, Mahloujifar (2026). Learning to Reason in 13 Parameters.**
arXiv:2602.04118. <https://arxiv.org/abs/2602.04118>.
TinyLoRA projects a tiny trainable vector through fixed random tensors. With RL, a Qwen2.5 model of about 8B
parameters reaches 91% on GSM8K with 13 parameters. SFT needs 100–1000× larger updates.
*Closeness 2 · C4.* Raises the bar: "a 2,560-number vector" is not small by 2026 standards. A TinyLoRA-style sweep
below 2,560 dimensions would locate the executor's intrinsic dimension (§5, idea 6).

**F14. Panigrahi, Saunshi, Zhao, Arora (2023). Task-Specific Skill Localization in Fine-tuned Language
Models.** ICML 2023. arXiv:2302.06600. <https://arxiv.org/abs/2302.06600>.
Grafting about 0.01% of the fine-tuned parameters onto the base recovers over 95% of performance.
*Closeness 2 · C4 ("changes concentrate in layers 12–17").* The direct precedent for the layer-slice grafting in
WEIGHTS §2–3. Cite it and use "grafting" as the term.

**F15. Mukherjee, Yuan, Hakkani-Tur, Peng (2025). Reinforcement Learning Finetunes Small Subnetworks in Large
Language Models.** NeurIPS 2025. arXiv:2505.11711. <https://arxiv.org/abs/2505.11711>.
RL updates are sparse but nearly full-rank in almost every matrix.
*Closeness 1 · C4.* Contrast: our supervised executor update is low-rank (4 directions suffice).

**F16. Zhao, Gong, Chen et al. (2026). A Layer-wise Analysis of Supervised Fine-Tuning.** ACL 2026.
arXiv:2604.11838. <https://arxiv.org/abs/2604.11838>.
Middle layers (20–80% of depth) are stable and final layers sensitive. Tuning only the middle block beats LoRA by
up to 10.2% on GSM8K.
*Closeness 1–2 · C4.* Supports mid-depth localisation, though their "stable middle" framing differs from our
"useful update in the middle".

**F17. Harada, Yamauchi, Oda et al. (2025). Massive Supervised Fine-tuning Experiments.** EMNLP 2025.
arXiv:2506.14681. <https://arxiv.org/abs/2506.14681>.
Over many SFT runs, the largest weight changes are in upper layers but the most consequential ones are in the
middle.
*Closeness 1 · C4.* Same pattern as ours (layers 24–35 alone give 4/256).

**F18. Lee, Bai, Pres et al. (2024). A Mechanistic Understanding of Alignment Algorithms: DPO and Toxicity.**
arXiv:2401.01967. <https://arxiv.org/abs/2401.01967>.
DPO bypasses toxic capabilities rather than removing them, and a small offset reverts it.
*Closeness 1 · C4.*

**F19. Cho, Luo, Kato et al. (2025). Mechanistic Fine-tuning for In-context Learning (ABFT).**
arXiv:2505.14233. <https://arxiv.org/abs/2505.14233>.
Trains attention scores directly to focus on the correct label tokens in context, using about 0.01% of the data
of end-to-end methods.
*Closeness 1–2 · C4.* A mechanism-targeted objective for exactly our fetch. One option for building in
"one table head" (INSIGHTS N\*).

**F20. Yue, Chen, Lu et al. (2025). Does RL Really Incentivize Reasoning Capacity Beyond the Base Model?**
NeurIPS 2025 (oral). arXiv:2504.13837. <https://arxiv.org/abs/2504.13837>.
RL improves pass@1 but not pass@k at large k. Reasoning paths are already in the base model.
*Closeness 1 · C4.* Relevant to "RL taught nothing new" (INSIGHTS obs. 4).

**F21. Wang, Yang, Zeng et al. (2025). Reinforcement Learning for Reasoning with One Training Example.**
arXiv:2504.20571. <https://arxiv.org/abs/2504.20571>.
*Closeness 1 · C4.* Elicitation from almost no data.

**F22. Shao, Li, Xin et al. (2025). Spurious Rewards: Rethinking Training Signals in RLVR.** arXiv:2506.10947.
<https://arxiv.org/abs/2506.10947>.
RLVR with random rewards raises Qwen2.5-Math-7B on MATH-500 by 21.4 points (29.1 with true rewards), by
amplifying pretrained "code reasoning". The effect is Qwen-specific.
*Closeness 2 · C4.* A reviewer will ask whether "latent executor" is a Qwen property, perhaps from synthetic
mid-training data. Run the edit on a second model family (§5, idea 3).

**F23. Wu, Zhang, Dong et al. (2026). Reasoning or Memorization? Unreliable Results of RL Due to Data
Contamination.** AAAI 2026. arXiv:2507.10532. <https://arxiv.org/abs/2507.10532>.
Qwen2.5's surprising RL gains come partly from benchmark contamination and do not transfer to Llama.
*Closeness 1–2 · C4.* Same caveat. Our tables are random, so contamination is unlikely, but data of the "follow a
table" type in Qwen's mid-training is not ruled out.

**F24. Greenblatt, Roger, Krasheninnikov, Krueger (2024). Stress-Testing Capability Elicitation With
Password-Locked Models.** NeurIPS 2024. arXiv:2405.19550. <https://arxiv.org/abs/2405.19550>.
A few good demonstrations, sometimes one, fine-tune hidden capabilities back.
*Closeness 1 · C4.* Elicitation by few-step fine-tuning is well established.

**F25. Ben Zaken, Ravfogel, Goldberg (2022). BitFit.** ACL 2022. arXiv:2106.10199.
<https://arxiv.org/abs/2106.10199>.
Tuning only biases is competitive on small-to-medium data.
*Closeness 2 · C4.* Our 2,560-vector is a bias on one layer's output: a one-layer BitFit. Name it.

**F26. Lu, Grover, Abbeel, Mordatch (2021). Pretrained Transformers as Universal Computation Engines.**
arXiv:2103.05247. <https://arxiv.org/abs/2103.05247>.
A frozen language-pretrained transformer with only input, output and LayerNorm tuned solves non-language tasks,
better than a frozen random transformer.
*Closeness 1 · C4.* The earliest "frozen core, tiny interface" result, with a random-weights control we should copy.

**F27. Zhong & Andreas (2024). Algorithmic Capabilities of Random Transformers.** NeurIPS 2024.
arXiv:2410.04368. <https://arxiv.org/abs/2410.04368> *(full text read)*.
- **Setup.** In a random, frozen two-layer transformer of width 1024, only the token embedding, positional embedding
  and unembedding are trained.
- **Algorithmic tasks.** It solves needle-in-a-haystack (associative lookup), modular addition and decimal addition
  at 100%.
- **The mechanism is subspace selection.** The task is routed into a low-dimensional subspace, not into a sparse
  subnetwork.

*Closeness 2 · C4.* "A soft prompt switches it on, so it was latent" needs a control. Train the same soft prompt or
vector on a weight-shuffled or early-checkpoint model and show it fails.

**F28. Zhao, Lin, Mi, Jaggi, Schütze (2020). Masking as an Efficient Alternative to Finetuning.** EMNLP 2020.
arXiv:2004.12406. <https://arxiv.org/abs/2004.12406>.
*Closeness 0–1 · C4.*

### G. Steering, task and function vectors, ReFT, soft prompts and prefix tuning

**G1. Subramani, Suresh, Peters (2022). Extracting Latent Steering Vectors from Pretrained Language Models.**
Findings of ACL 2022. arXiv:2205.05124. <https://arxiv.org/abs/2205.05124>.
Optimised vectors added to hidden states make a frozen LM produce target sentences.
*Closeness 1 · C4.* The origin of optimised steering vectors.

**G2. Turner, Thiergart, Leech et al. (2023). Steering Language Models With Activation Engineering (ActAdd).**
arXiv:2308.10248. <https://arxiv.org/abs/2308.10248>.
*Closeness 1 · C4.*

**G3. Zou, Phan, Chen et al. (2023). Representation Engineering.** arXiv:2310.01405.
<https://arxiv.org/abs/2310.01405>.
*Closeness 1 · C4.*

**G4. Li, Patel, Viégas, Pfister, Wattenberg (2023). Inference-Time Intervention.** NeurIPS 2023.
arXiv:2306.03341. <https://arxiv.org/abs/2306.03341>.
Shifts the activations of selected heads along truthful directions.
*Closeness 1 · C4.* An intervention at head level. LoFiT (G16) is its trained version.

**G5. Panickssery, Gabrieli, Schulz et al. (2023). Steering Llama 2 via Contrastive Activation Addition.**
arXiv:2312.06681. <https://arxiv.org/abs/2312.06681>.
*Closeness 1 · C4.*

**G6. Liu, Ye, Xing, Zou (2023). In-context Vectors.** arXiv:2311.06668. <https://arxiv.org/abs/2311.06668>.
Replaces demonstrations with a latent shift computed from them.
*Closeness 1 · C4.*

**G7. Li, Liu, Hu et al. (2024). In-Context Learning State Vector with Inner and Momentum Optimization.**
arXiv:2404.11225. <https://arxiv.org/abs/2404.11225>.
*Closeness 1 · C4.*

**G8. Hendel, Geva, Globerson (2023). In-Context Learning Creates Task Vectors.** Findings of EMNLP 2023.
arXiv:2310.15916. <https://arxiv.org/abs/2310.15916>.
ICL compresses the demonstrations into a single task vector θ at an intermediate layer. Patching θ into a
zero-shot query reproduces the task.
*Closeness 2–3 · C4.* See §1.2.

**G9. Todd, Li, Sharma et al. (2024). Function Vectors in Large Language Models.** ICLR 2024. arXiv:2310.15213.
<https://arxiv.org/abs/2310.15213> *(full text read, including the appendix task list)*.
See §1.2. The tasks include "Choose First / Middle / Last of List" and "Next-Item": procedures, not fixed answers.
*Closeness 3 · C4.*

**G10. Yang, Cho, Ding, Inoue (2026). Task Vectors, Learned Not Extracted.** ICLR 2026. arXiv:2509.24169.
<https://arxiv.org/abs/2509.24169> *(full text read)*.
See §1.2.
*Closeness 3 · C4.*

**G11. Saglam, Hu, Yang et al. (2025). Learning Task Representations from In-Context Learning.** Findings of
ACL 2025. arXiv:2502.05390. <https://arxiv.org/abs/2502.05390>.
The task vector is learned as a causally optimised weighted sum of head outputs.
*Closeness 2 · C4.* Sits between FVs and LTVs, and is a cheap baseline: optimise weights over head outputs and
compare with the 2,560 vector.

**G12. Yang, Lin, Lee, Papailiopoulos, Nowak (2025). Task Vectors in In-Context Learning: Emergence,
Formation, and Benefit.** arXiv:2501.09240. <https://arxiv.org/abs/2501.09240>.
In models trained from scratch, task vectors emerge but are weak or non-local. An auxiliary loss makes them local.
*Closeness 1 · C4.*

**G13. Li, Campbell, Chan, Lampinen (2025). Just-in-time and distributed task representations in language
models.** arXiv:2509.04466. <https://arxiv.org/abs/2509.04466>.
Transferable task representations form sporadically and locally in context.
*Closeness 1 · C4.*

**G14. Ilharco, Ribeiro, Wortsman et al. (2023). Editing Models with Task Arithmetic.** ICLR 2023.
arXiv:2212.04089. <https://arxiv.org/abs/2212.04089>.
"Task vectors" in weight space.
*Closeness 0–1.* A naming collision with G8. If we say "task vector", say "activation-space".

**G15. Wu, Arora, Wang et al. (2024). ReFT: Representation Finetuning for Language Models.** NeurIPS 2024.
arXiv:2404.03592. <https://arxiv.org/abs/2404.03592> *(full text read)*.
- **Method.** LoReFT edits hidden states at chosen positions: h + Rᵀ(Wh + b − Rh). DiReFT drops the orthogonality.
- **Efficiency.** 15–65× more parameter-efficient than LoRA on commonsense and instruction tasks.
- **Weak spot.** It trails LoRA on arithmetic (LLaMA-7B: 42.6 against 46.9). The authors blame long chain-of-thought
  generations, which dilute the edit.

*Closeness 2 · C4.* Our vector is the W = 0, rank-0 limit applied at every position of one layer. Cite it as the
family and run LoReFT rank 1 at layer 18 as a baseline. Their weakness on long generations is a contrast: our
pinned tick re-applies the edit to a fresh short block every step, so there is no dilution.

**G16. Yin, Ye, Durrett (2024). LoFiT: Localized Fine-tuning on LLM Representations.** NeurIPS 2024.
arXiv:2406.01563. <https://arxiv.org/abs/2406.01563>.
Selects 3–10% of heads and trains bias offsets on their outputs.
*Closeness 2 · C4, C7.* Natural control: LoFiT restricted to the ~30 committee heads. If it certifies as well as
the layer-18 vector, the executor's "switch" lives in those heads.

**G17. Wu, Liu, Wang et al. (2024). Advancing Parameter Efficiency in Fine-tuning via Representation Editing
(RED).** arXiv:2402.15179. <https://arxiv.org/abs/2402.15179>.
Scaling and bias vectors per layer.
*Closeness 1 · C4.*

**G18. Dunefsky & Cohan (2025). One-shot Optimized Steering Vectors Mediate Safety-relevant Behaviors in
LLMs.** COLM 2025. arXiv:2502.18862. <https://arxiv.org/abs/2502.18862>.
A vector optimised on a single example generalises.
*Closeness 2 · C4.* Measure how few tables are needed to train the 2,560 vector.

**G19. Cao, Zhang, Cao et al. (2024). Personalized Steering via Bi-directional Preference Optimization
(BiPO).** arXiv:2406.00045. <https://arxiv.org/abs/2406.00045>.
*Closeness 1 · C4.*

**G20. Sinii, Gorbatovski, Cherepanov et al. (2025). Steering LLM Reasoning Through Bias-Only Adaptation.**
EMNLP 2025. arXiv:2505.18706. <https://arxiv.org/abs/2505.18706>.
One d-dimensional vector per layer, trained with RL on a frozen model, matches fully RL-tuned maths reasoning
(0.0016% extra parameters on 8B).
*Closeness 2 · C4.*

**G21. Sinii, Balagansky, Gerasimov et al. (2025). Small Vectors, Big Effects: A Mechanistic Study of
RL-Induced Reasoning via Steering Vectors.** arXiv:2509.06608. <https://arxiv.org/abs/2509.06608> *(full text
read)*.
- **Qwen2.5-Math-7B.** Base 14.3; full RL 43.8; all-layer vectors 42.9; one vector at layer 16 gives 40.1.
- **Last-layer vector.** It acts as a token bias ("To"), and appending "To" to the prompt reproduces about 75% of
  its gain.
- **Penultimate-layer vector.** It works through the MLP and the unembedding, not through attention patterns.

*Closeness 2 · C4.* A single middle-layer vector carries most of an RL gain. Their mechanism (value path, unchanged
attention) is the hypothesis to test for our vector: does it change attention patterns, or only what the read-out
heads write?

**G22. Venhoff, Arcuschin, Torr et al. (2025). Understanding Reasoning in Thinking Language Models via Steering
Vectors.** arXiv:2506.18167. <https://arxiv.org/abs/2506.18167>.
*Closeness 1 · C4.*

**G23. Zbeeb, Hammoud, Ghanem (2025). Reasoning Vectors: Transferring Chain-of-Thought Capabilities via Task
Arithmetic.** arXiv:2509.01363. <https://arxiv.org/abs/2509.01363>.
*Closeness 1 · C4.*

**G24. Wu, Arora, Geiger et al. (2025). AxBench: Steering LLMs? Even Simple Baselines Outperform Sparse
Autoencoders.** arXiv:2501.17148. <https://arxiv.org/abs/2501.17148>.
For steering, prompting beats every representation method, followed by fine-tuning. It introduces ReFT-r1.
*Closeness 1 · C4.* Reviewers may ask whether a prompt (instructions plus examples) does as well as the vector. We
have the answer: the base model with Π gets 33.8%. State it.

**G25. Belitsky, Kopiczko, Dorkenwald et al. (2025). KV Cache Steering for Controlling Frozen LLMs.**
arXiv:2507.08799. <https://arxiv.org/abs/2507.08799>.
A one-shot edit to the KV cache induces chain-of-thought behaviour.
*Closeness 1 · C4, C5.* Since Π's cache is fixed under the clock, a steering edit on Π's KV is a third way to
switch the executor on. It is cheap to try.

**G26. Bao, Li, Yu et al. (2026). Towards Steering without Sacrifice: Principled Training of Steering Vectors
for Prompt-only Interventions (PrOSV).** ICML 2026. arXiv:2605.05983.
<https://arxiv.org/abs/2605.05983>.
Steering vectors applied only to prompt positions avoid degrading generation.
*Closeness 2 · C4 (soft prompt "leaves the language logits bitwise unchanged").* "Intervene only where the task
lives" is a known design goal. Ours holds by construction, because the soft prompt is attached only to program
calls.

**G27. Fierro & Roger (2026). Steering Language Models with Weight Arithmetic.** ICLR 2026. arXiv:2511.05408.
<https://arxiv.org/abs/2511.05408>.
*Closeness 1 · C4.*

**G28. Li, Fastowski, Zaradoukas et al. (2026). Analysing the Safety Pitfalls of Steering Vectors.**
arXiv:2603.24543. <https://arxiv.org/abs/2603.24543>.
*Closeness 0–1.*

**G29. Bartoszcze, Munshi, Sukidi et al. (2025). Representation Engineering for LLMs: Survey and Research
Challenges.** arXiv:2502.17601. <https://arxiv.org/abs/2502.17601>.
*Closeness 0.* Survey.

**G30. Lester, Al-Rfou, Constant (2021). The Power of Scale for Parameter-Efficient Prompt Tuning.** EMNLP 2021.
arXiv:2104.08691. <https://arxiv.org/abs/2104.08691>.
Soft prompts on a frozen model approach full fine-tuning as scale grows.
*Closeness 2 · C4.* Our 8-vector soft prompt is prompt tuning. Name it as such.

**G31. Li & Liang (2021). Prefix-Tuning.** arXiv:2101.00190. <https://arxiv.org/abs/2101.00190>.
*Closeness 1 · C4.*

**G32. Petrov, Torr, Bibi (2024). When Do Prompting and Prefix-Tuning Work? A Theory of Capabilities and
Limitations.** ICLR 2024. arXiv:2310.19698. <https://arxiv.org/abs/2310.19698> *(full text read)*.
- **Theory.** A prefix only rescales the attention over content (A_ij(1 − A_i0)) and adds a constant bias, so it
  cannot change relative attention.
- **Toy experiments.** Prefix tuning elicits pretrained skills (90–98%) and combines them (93%). It fails at new
  attention patterns (0% at turning ascending sorting into descending, where full fine-tuning gets 85%).

*Closeness 2 · C4.* The best theoretical support for reading the soft-prompt result as elicitation. Caveats:
- Our soft prompt is input-level prompt tuning, which can change attention in later layers.
- G33 shows universality in principle.

So write "consistent with elicitation", not "proves latency".

**G33. Petrov, Torr, Bibi (2024). Prompting a Pretrained Transformer Can Be a Universal Approximator.**
arXiv:2402.14753. <https://arxiv.org/abs/2402.14753>.
Prefix-tuning even a single attention head can approximate any continuous function, in principle.
*Closeness 1 · C4.* The counterweight to G32.

**G34. Wang, Chauhan, Wang, Hsieh (2023). Universality and Limitations of Prompt Tuning.** arXiv:2305.18787.
<https://arxiv.org/abs/2305.18787>.
*Closeness 1 · C4.*

### H. KV-cache policies, attention sinks and Markovian decoding

**H1. Xiao, Tian, Chen, Han, Lewis (2024). Efficient Streaming Language Models with Attention Sinks
(StreamingLLM).** ICLR 2024. arXiv:2309.17453. <https://arxiv.org/abs/2309.17453> *(full text read)*.
See §1.3.
*Closeness 3 · C5.*

**H2. Zhang, Sheng, Zhou et al. (2023). H₂O: Heavy-Hitter Oracle.** arXiv:2306.14048.
<https://arxiv.org/abs/2306.14048>.
Keeps the "heavy hitter" tokens with the largest accumulated attention plus recent tokens, framed as a submodular
eviction problem.
*Closeness 2 · C5 (control).* At a budget of |Π| + 2, would H₂O keep Π and drop history on its own? A cheap
baseline for the policy figure.

**H3. Liu, Desai, Liao et al. (2023). Scissorhands.** arXiv:2305.17118. <https://arxiv.org/abs/2305.17118>.
Tokens important once tend to stay important ("persistence of importance").
*Closeness 1 · C5.*

**H4. Ge, Zhang, Liu et al. (2024). Model Tells You What to Discard (FastGen).** ICLR 2024. arXiv:2310.01801.
<https://arxiv.org/abs/2310.01801>.
Profiles each head's attention and adapts its cache. Local heads drop long-range context, special-token heads keep
only special tokens, and broad heads keep the full cache.
*Closeness 1 · C5.* A head-level policy. Under the clock, every head gets the same policy.

**H5. Li, Huang, Yang et al. (2024). SnapKV.** arXiv:2404.14469. <https://arxiv.org/abs/2404.14469>.
Compresses the prompt's KV per head, using the attention of an observation window at the end of the prompt.
*Closeness 2 · C5 (control).* Apply SnapKV to Π itself. How far can the program be compressed before certification
fails? Since any row can be needed, the prediction is "not far". This tests the claim that Π must be kept whole.

**H6. Cai, Zhang, Gao et al. (2024). PyramidKV.** arXiv:2406.02069. <https://arxiv.org/abs/2406.02069>.
*Closeness 1 · C5.*

**H7. Tang, Zhao, Zhu et al. (2024). Quest: Query-Aware Sparsity.** ICML 2024. arXiv:2406.10774.
<https://arxiv.org/abs/2406.10774>.
*Closeness 1 · C5.*

**H8. Han, Wang, Peng et al. (2024). LM-Infinite.** NAACL 2024. arXiv:2308.16137.
<https://arxiv.org/abs/2308.16137>.
Identifies three factors behind length-generalisation failure, argues that truncating the attention window or
relative position encoding alone cannot fix them, and gives a training-free method that lets models trained on
2K–4K tokens run on inputs of up to 200M tokens. I did not re-read the body today; my recollection is that the
method is a Λ-shaped mask over starting and recent tokens with a cap on distance.
*Closeness 2 · C5.* Another "start tokens + local window" policy. Our "positions restart" is the extreme case of
bounding distance: the distance between block and Π is constant.

**H9. Xiao, Tang, Zuo et al. (2024). DuoAttention.** arXiv:2410.10819. <https://arxiv.org/abs/2410.10819>.
Only "retrieval heads" need the full KV cache. All other heads, "streaming heads", keep sinks plus recent tokens.
*Closeness 2 · C5, C7.* Under our policy every head sees Π, but only the ~30 committee heads may need it. A
DuoAttention-style split (Π only for committee heads) would test how localised the read is, and would save memory.

**H10. Tang, Lin, Lin et al. (2024). RazorAttention.** arXiv:2407.15891. <https://arxiv.org/abs/2407.15891>.
Keeps the full cache only for retrieval heads and adds a compensation token.
*Closeness 1 · C5.*

**H11. Fu, Cai, Asi et al. (2025). Not All Heads Matter (HeadKV).** ICLR 2025. arXiv:2410.19258.
<https://arxiv.org/abs/2410.19258>.
*Closeness 1 · C5.*

**H12. Xiao, Zhang, Han et al. (2024). InfLLM.** arXiv:2402.04617. <https://arxiv.org/abs/2402.04617>.
*Closeness 1 · C5.*

**H13. Oren, Hassid, Yarden, Adi, Schwartz (2024). Transformers are Multi-State RNNs.** arXiv:2401.06104.
<https://arxiv.org/abs/2401.06104>.
A decoder with a bounded cache is a bounded multi-state RNN. Their TOVA policy evicts the tokens the current query
attends to least.
*Closeness 2 · C5.* The cleanest framing of what the clock does: it turns the LLM into a finite-state machine whose
state is one token. Cite it, and add TOVA to the policy baselines.

**H14. Liu, Tang, Dong et al. (2025). ChunkKV.** NeurIPS 2025. arXiv:2502.00299.
<https://arxiv.org/abs/2502.00299>.
Evicts semantic chunks rather than single tokens.
*Closeness 1–2 · C5.* A precedent for chunk-level eviction, with score-based chunks rather than block-aligned
recomputation.

**H15. Cai, Xiao, Sun et al. (2025). R-KV.** arXiv:2505.24133. <https://arxiv.org/abs/2505.24133>.
Redundancy-aware eviction for reasoning traces keeps about 100% of performance with 10% of the cache.
*Closeness 1 · C5.*

**H16. Kolawole & Smith (2026). EpiKV.** arXiv:2606.26472. <https://arxiv.org/abs/2606.26472>.
Under tight budgets, most accuracy loss in reasoning comes from looping. Keeping what recent queries point to
stops it.
*Closeness 1 · C5, C8.*

**H17. Wang, Qiu, Zhao et al. (2026). Random Attention: Rethinking KV Cache Eviction for Efficient
Reasoning.** arXiv:2609.03430. <https://arxiv.org/abs/2609.03430>.
Keeping the prompt and evicting the rest uniformly at random matches the best scored policies on four models and
six tasks. "The prompt is the fragile part of the cache." Reasoning traces protect themselves through redundancy
in the text and across heads.
*Closeness 2 · C5 (support).* The strongest 2026 evidence that "keep the program, drop the history" is the right
axis. Our bitwise and certificate claims are what it lacks.

**H18. Chen, Geh, Grover, Van den Broeck, Israel (2026). The Pitfalls of KV Cache Compression.** ACL 2026.
arXiv:2510.00231. <https://arxiv.org/abs/2510.00231>.
StreamingLLM, SnapKV, TOVA, H₂O and K-Norm make some instructions be ignored entirely and leak system prompts.
Fair retention across prompt parts helps.
*Closeness 2 · C5 (support).* Motivates keeping Π whole rather than compressed.

**H19. Aghajohari, Chitsaz, Kazemnejad et al. (2025). The Markovian Thinker (Delethink).** arXiv:2510.06557.
<https://arxiv.org/abs/2510.06557> *(full text read)*.
See §1.3. It was cited in the v1 draft and is missing from v2's `refs.bib`.
*Closeness 3 · C5.*

**H20. Yang, Srebro, McAllester, Li (2025). PENCIL: Long Thoughts with Short Memory.** ICML 2025.
arXiv:2503.14337. <https://arxiv.org/abs/2503.14337> *(full text read)*.
- **The rule.** C [CALL] T [SEP] A [RETURN] ⇒ C A erases finished thoughts.
- **Theory.** A fixed transformer with this rule simulates any Turing machine with O(T) tokens and O(S) context.
- **Results.** 97% on 5×5 Einstein puzzles, against 25% for chain of thought. How positions are handled after a
  reduction is not stated.

*Closeness 2 · C5, C8.* The theory precedent for "erase history, keep the program: space-efficient universal
computation". Our INSIGHTS §5 "Turing split" framing should cite it.

**H21. Zhang, Zhu, Sun et al. (2025). LightThinker.** EMNLP 2025. arXiv:2502.15589.
<https://arxiv.org/abs/2502.15589>.
*Closeness 1 · C5.* Compresses thoughts into gist tokens.

**H22. Yan, Shen, Liu et al. (2026). InftyThink.** ICLR 2026. arXiv:2503.06692.
<https://arxiv.org/abs/2503.06692>.
*Closeness 1 · C5.* Iterative summarise-and-discard reasoning.

**H23. Yu, Chen, Feng et al. (2026). MemAgent.** ICLR 2026 (oral). arXiv:2507.02259.
<https://arxiv.org/abs/2507.02259>.
*Closeness 1 · C5.* A fixed-size memory overwritten chunk by chunk.

**H24. Yuan & Xie (2026). Breaking the Capability Ceiling of LLM Post-Training by Reintroducing Markov
States.** arXiv:2603.19987. <https://arxiv.org/abs/2603.19987>.
Replacing "history as state" with explicit Markov states improves RL post-training on logic puzzles, with
sample-complexity guarantees.
*Closeness 1–2 · C5, C8.* The same thesis as our "remove the history as a second state", in RL.

**H25. Hutchins, Schlag, Wu et al. (2022). Block-Recurrent Transformers.** arXiv:2203.07852.
<https://arxiv.org/abs/2203.07852>.
*Closeness 1 · C5.*

**H26. Bulatov, Kuratov, Burtsev (2022). Recurrent Memory Transformer.** NeurIPS 2022. arXiv:2207.06881.
<https://arxiv.org/abs/2207.06881>.
*Closeness 1 · C5.*

**H27. Gu, Pang, Du et al. (2025). When Attention Sink Emerges in Language Models: An Empirical View.** ICLR
2025 (spotlight). arXiv:2410.10781. <https://arxiv.org/abs/2410.10781>.
Sinks emerge after effective optimisation on sufficient data and act like key biases that store extra attention.
*Closeness 2 · C5, C7.* Π is not a sink in this sense. Measure the BOS or first-token sink mass under the clock to
show Π's attention is content, not dumping. Row 0's weakness (WEIGHTS §6) may be sink interference.

**H28. Barbero, Arroyo, Gu et al. (2025). Why do LLMs attend to the first token?** arXiv:2504.02732.
<https://arxiv.org/abs/2504.02732>.
Sinks let a model avoid over-mixing.
*Closeness 1–2 · C7 (row 0).* One newline before Π raised row 0's margin by 1.5. That fits "give the model a sink
that is not row 0", and StreamingLLM also notes that newlines work as sinks.

**H29. Sun, Chen, Kolter, Liu (2024). Massive Activations in Large Language Models.** COLM 2024.
arXiv:2402.17762. <https://arxiv.org/abs/2402.17762>.
*Closeness 1 · C7.* Check whether row 0 or the token before Π carries a massive activation.

**H30. Cancedda (2024). Spectral Filters, Dark Signals, and Attention Sinks.** ACL 2024. arXiv:2402.09221.
<https://arxiv.org/abs/2402.09221>.
*Closeness 1.*

**H31. Yu, Wang, Fu et al. (2024). Unveiling and Harnessing Hidden Attention Sinks (ACT).** arXiv:2406.15765.
<https://arxiv.org/abs/2406.15765>.
Sinks also occur at later tokens, and calibrating them without training raises accuracy.
*Closeness 1 · C7.*

**H32. Guo, Pai, Bai et al. (2024). Active-Dormant Attention Heads.** arXiv:2410.13835.
<https://arxiv.org/abs/2410.13835>.
Heads go dormant, dumping attention on the sink, when their function is not needed.
*Closeness 1 · C7.* A committee member may be dormant on some rows. That would explain the context-dependent
scores.

**H33. Queipo-de-Llano, Arroyo, Barbero et al. (2025). Attention Sinks and Compression Valleys in LLMs are Two
Sides of the Same Coin.** arXiv:2510.06477. <https://arxiv.org/abs/2510.06477>.
Proposes three phases: broad mixing early, compressed computation in the middle, refinement late.
*Closeness 1 · C4, C7.* The useful update in layers 12–17 falls in their "compressed middle".

**H34. Qiu, Wang, Zheng et al. (2025). Gated Attention for Large Language Models.** arXiv:2505.06708.
<https://arxiv.org/abs/2505.06708>.
Output gating removes attention sinks.
*Closeness 1 · C5.* On a sink-free architecture the clock's "Π as sink" wording would be odd, which is another
reason to say "persistent prefix".

**H35. Su, Zhang, Wu et al. (2026). Attention Sink in Transformers: A Survey.** arXiv:2604.10098.
<https://arxiv.org/abs/2604.10098>.
Covers more than 180 studies on using, explaining and mitigating sinks.
*Closeness 1 · C5.* Cite it once as the map of the area.

**H36. He and Thinking Machines Lab (10 Sept 2025). Defeating Nondeterminism in LLM Inference.**
<https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/> *(page fetched)*.
- **The main cause of nondeterminism** is the lack of batch invariance. Only RMSNorm, matmul and attention need
  batch-invariant kernels.
- **Prefix caching and chunked prefill** must not change reduction order.
- **Split-KV needs a fixed split size.**
- **Result.** Qwen3-235B produces 80 distinct completions in 1,000 runs at temperature 0, and 1 with
  batch-invariant kernels.

*Closeness 2 · C5 ("bitwise").* Our bitwise claims hold per code path (INSIGHTS obs. 9). Cite this, and state the
kernel, batch size and cache layout in Methods.

**H37. Zheng, Yin, Xie et al. (2023). SGLang: Efficient Execution of Structured Language Model Programs.**
arXiv:2312.07104. <https://arxiv.org/abs/2312.07104>.
RadixAttention reuses prefix KV across calls.
*Closeness 1 · C5.* The clock can be deployed as prefix caching of Π.

### I. Positions: reuse, restart and RoPE distance

**I1. Su, Lu, Pan et al. (2021). RoFormer: Enhanced Transformer with Rotary Position Embedding.**
arXiv:2104.09864. <https://arxiv.org/abs/2104.09864>.
Attention depends only on relative position, with long-term decay.
*Closeness 2 · C5 ("a gap between Π and the block costs margin").* Cite it for both halves: shifting everything is
free (relative), while a gap changes the relative distances the model was tuned on.

**I2. Barbero, Vitvitskyi, Perivolaropoulos et al. (2024). Round and Round We Go! What makes Rotary Positional
Encodings useful?** arXiv:2410.06205. <https://arxiv.org/abs/2410.06205>.
Gemma uses RoPE's high frequencies for positional heads and its low frequencies for semantics.
*Closeness 1 · C5, C7.* The "positional pointer, unused" may live in the high-frequency bands. Probe them.

**I3. Gim, Chen, Lee et al. (2024). Prompt Cache: Modular Attention Reuse.** MLSys 2024. arXiv:2311.04934.
<https://arxiv.org/abs/2311.04934> *(full text read)*.
Precomputed module KV at fixed position ranges. They say LLMs "can operate on attention states with discontinuous
position IDs", with LongBench accuracy "comparable", though some tasks drop by more than 2.5 points.
*Closeness 2 · C5.* The closest systems precedent for "reuse Π's KV at fixed positions". Our gap result (a gap of 4
gives 45/55) shows that contiguity matters at the margin, even where average accuracy hides it.

**I4. Ma, Wang, Tian (2025). Block-Attention for Efficient Prefilling.** ICLR 2025. arXiv:2409.15355.
<https://arxiv.org/abs/2409.15355> *(full text read)*.
- **Method.** Blocks are encoded independently and re-rotated to their actual positions.
- **Without fine-tuning,** the RAG average falls from 66.1% to 49.9%. About 800 steps of block fine-tuning recover
  it.

*Closeness 2 · C5.* Shows models need training to tolerate independently encoded blocks. Our executor edit was
trained on fresh pairs, and that is plausibly why the block-aligned policy is exact while history hurts.

**I5. Ratner, Levine, Belinkov et al. (2023). Parallel Context Windows.** ACL 2023. arXiv:2212.10947.
<https://arxiv.org/abs/2212.10947>.
Cuts the context into windows, restricts attention to within each window and reuses position IDs across windows,
with no training.
*Closeness 2 · C5.* The original "chunk the context, restart positions" policy, applied in parallel at prefill.
Ours is the sequential, decode-time version.

**I6. Hao, Sun, Dong et al. (2022). Structured Prompting.** arXiv:2212.06713.
<https://arxiv.org/abs/2212.06713>.
*Closeness 1 · C5.* Demonstrations are encoded separately with designed position embeddings, then attended jointly by the test
example with rescaled attention.

**I7. Yao, Li, Liu et al. (2024). CacheBlend.** arXiv:2405.16444. <https://arxiv.org/abs/2405.16444>.
*Closeness 1 · C5.*

**I8. Hu, Huang, Wang et al. (2024). EPIC: Position-Independent Caching.** arXiv:2410.15332.
<https://arxiv.org/abs/2410.15332>.
Mitigates the inappropriate "attention sink" at every reused document's start.
*Closeness 1 · C5, C7.* The same row-0 or first-token effect.

**I9. Yang, Hou, Wei et al. (2025). KVLink.** arXiv:2502.16002. <https://arxiv.org/abs/2502.16002>.
*Closeness 1 · C5.*

**I10. Yang, Chen, Chen (2025). APE: Adaptive Parallel Encoding.** ICLR 2025. arXiv:2502.05431.
<https://arxiv.org/abs/2502.05431>.
*Closeness 1 · C5.*

**I11. Jin, Han, Yang et al. (2024). LLM Maybe LongLM: Self-Extend.** ICML 2024. arXiv:2401.01325.
<https://arxiv.org/abs/2401.01325>.
*Closeness 1 · C5.*

**I12. Chen, Wong, Chen, Tian (2023). Extending Context Window via Positional Interpolation.**
arXiv:2306.15595. <https://arxiv.org/abs/2306.15595>.
*Closeness 0.*

**I13. Kazemnejad, Padhi, Natesan Ramamurthy et al. (2023). The Impact of Positional Encoding on Length
Generalization.** NeurIPS 2023. arXiv:2305.19466. <https://arxiv.org/abs/2305.19466>.
*Closeness 1.*

**I14. Golovneva, Wang, Weston, Sukhbaatar (2024). Contextual Position Encoding (CoPE).** arXiv:2405.18719.
<https://arxiv.org/abs/2405.18719>.
Positions that count only selected tokens solve selective copy, counting and Flip-Flop.
*Closeness 1 · C8.* The pointer is a counter, and CoPE is the architectural fix the clock replaces.

**I15. Liu, Lin, Hewitt et al. (2024). Lost in the Middle.** TACL. arXiv:2307.03172.
<https://arxiv.org/abs/2307.03172>.
*Closeness 1 · C7.* Our median margins are flat to 4,096 rows. Report margin by row index to show we have no
middle dip.

**I16. Hsieh, Chuang, Li et al. (2024). Found in the Middle.** Findings of ACL 2024. arXiv:2406.16008.
<https://arxiv.org/abs/2406.16008>.
*Closeness 1 · C7.*

### J. Drift in long generation (C8) and interference

**J1. Li, Liu, Bashkansky et al. (2024). Measuring and Controlling Instruction (In)Stability in Language Model
Dialogs.** COLM 2024. arXiv:2402.10962. <https://arxiv.org/abs/2402.10962>.
Instructions drift within eight turns. They attribute it to attention decaying away from the system prompt, and
"split-softmax" restores the attention.
*Closeness 2 · C8.* Our "attention to Π's destination falls 17×" is this decay, measured exactly. Run split-softmax
on plain decoding as a cheap baseline (§5, idea 21). If it rescues plain runs, the clock's value shifts to the pointer and
the certificate.

**J2. Chuang, Qiu, Hsieh et al. (2024). Lookback Lens.** EMNLP 2024. arXiv:2407.07071.
<https://arxiv.org/abs/2407.07071>.
Per head, the ratio of attention to the context against attention to the model's own generations linearly predicts
contextual hallucination.
*Closeness 2 · C8.* Our attention shift is a falling lookback ratio. Test whether it predicts the first error in
plain runs before it happens.

**J3. Marwah, Garimella, Pallagani et al. (2026). Cognitive Fatigue in Autoregressive Transformers.** ICML
2026. arXiv:2605.30981. <https://arxiv.org/abs/2605.30981>.
A "Fatigue Index" combines decay of attention to the prompt, representational drift and entropy miscalibration. It
predicts degradation (AUROC 0.95) across nine models.
*Closeness 2 · C8.* An index of the same decay, built for monitoring. Ours is a mechanism with an exact error
signal, and the pinned clock's prompt attention is constant by construction.

**J4. Wang & Sun (2025). Unable to Forget: Proactive Interference Reveals Working Memory Limits in LLMs Beyond
Context Length.** ICML 2025 LCFM workshop. arXiv:2506.08184. <https://arxiv.org/abs/2506.08184>.
Streams of related key-value updates degrade retrieval of the latest value log-linearly with interference, and
errors retrieve overwritten values.
*Closeness 2 · C8, C7.*
- **C8.** It is the in-context, plain-decoding form of "history as a second state". The clock removes the
  interference by evicting old pairs.
- **C7.** Near-duplicate names are the within-table form of the same interference.

### K. Algorithmic circuits in pretrained LMs, and the "clock" name

**K1. Nanda, Chan, Lieberum et al. (2023). Progress measures for grokking via mechanistic interpretability.**
arXiv:2301.05217. <https://arxiv.org/abs/2301.05217>.
*Closeness 1 (naming).* "Clock" names the modular-addition algorithm.

**K2. Zhong, Liu, Tegmark, Andreas (2023). The Clock and the Pizza.** NeurIPS 2023. arXiv:2306.17844.
<https://arxiv.org/abs/2306.17844>.
*Closeness 1 (naming).*

**K3. Kantamneni & Tegmark (2025). Language Models Use Trigonometry to Do Addition.** arXiv:2502.00873.
<https://arxiv.org/abs/2502.00873>.
Numbers are represented on a generalised helix and added by a "Clock" manipulation in mid-size LLMs.
*Closeness 1 (naming) · C7.* Our clock family's wrap at 12 may meet this pretrained structure.

**K4. Zhou, Fu, Sharan, Jia (2024). Pre-trained LLMs Use Fourier Features to Compute Addition.**
arXiv:2406.03445. <https://arxiv.org/abs/2406.03445>.
*Closeness 0–1.*

**K5. Nikankin, Reusch, Mueller, Belinkov (2025). Arithmetic Without Algorithms: Language Models Solve Math With
a Bag of Heuristics.** arXiv:2410.21272. <https://arxiv.org/abs/2410.21272>.
*Closeness 1 · C4.* Contrast: our executor is an algorithm (a lookup) checked to be exact, not a bag of heuristics.

**K6. Stolfo, Belinkov, Sachan (2023). A Mechanistic Interpretation of Arithmetic Reasoning.** EMNLP 2023.
arXiv:2305.15054. <https://arxiv.org/abs/2305.15054>.
*Closeness 0–1.*

**K7. Hanna, Liu, Variengien (2023). How does GPT-2 compute greater-than?** NeurIPS 2023. arXiv:2305.00586.
<https://arxiv.org/abs/2305.00586>.
*Closeness 0–1.*

**K8. Yang, Li, Yang et al. (2025). Qwen3 Technical Report.** arXiv:2505.09388.
<https://arxiv.org/abs/2505.09388>.
*Closeness 0.* Host model reference.

**K9. Sawant & Krejčí (2026). Mechanistic Interpretability for Neural Networks: Circuits, Sparse Features and
Symbolic Reasoning.** arXiv:2607.07316. <https://arxiv.org/abs/2607.07316>.
*Closeness 0.* 2026 survey.

**K10. Kadem & Zheng (2026). Interpreting Transformers Through Attention Head Intervention.**
arXiv:2601.04398. <https://arxiv.org/abs/2601.04398>.
*Closeness 0.*

---

## 4. The frontier in 2026 (one paragraph)

By late 2026 four lines of work bear on us. All of them measure averages, and none certifies an individual
computation.

- **Steering has moved from extracted to learned vectors.** Learned task vectors are at ICLR 2026, prompt-only
  steering vectors at ICML 2026, and one RL-trained vector per layer matches full RL (EMNLP 2025). Alongside this
  come extreme parameter minimalism (13 trained parameters reach 91% on GSM8K; rank-1 LoRA is enough for RL) and
  diagnostics of where steering works (a logit-lens accessibility profile).
- **In-context retrieval is resolved into several mechanisms.**
  - positional, lexical and reflexive retrieval (ICLR 2026);
  - ordering-ID lookbacks with pointers and addresses;
  - symbolic induction followed by retrieval heads;
  - token versus concept induction;
  - FV writers and cancellers.

  New tools decompose attention scores into feature interactions (QK attributions, Lorsa, "every component is a
  lookup").
- **The fine-tuning consensus is that it reweights existing circuits.** Edges change more than nodes, the middle
  layers carry the useful change, and RL edits sparse subnetworks. There is a sharp caveat that Qwen's latent
  behaviours are partly a property of Qwen (spurious rewards, contamination).
- **KV-cache research for reasoning has converged on "keep the prompt, the rest is cheap".**
  - Random eviction that keeps the prompt matches scored policies.
  - Compression silently drops instructions.
  - A 2026 survey maps more than 180 sink papers.
  - Markovian chunking, erasure and memory agents bound the context.
  - Long-generation drift has a monitoring index built on decaying attention to the prompt.

The closest pieces are a sink-and-window policy (StreamingLLM), fresh re-encoding of a carryover with the query kept
(Delethink), a learned single-vector switch (learned task vectors), and a pretrained lookup circuit that fine-tuning
sharpens (Prakash). What we did not find anywhere is any of the following:
- a per-input certificate;
- a demonstration that block-aligned eviction makes decoding bitwise equal to a checked computation;
- an executor whose program arrives at run time and is switched on by a single vector, checked table by table and
  exact for 10,000 steps.

## 5. Ideas: analyses and controls

Ranked by how much each protects a claim per unit of compute. Each is cheap because Savant, the edits and the
CIRCUITS harness exist. **(R)** marks one needed to defend wording against a reviewer; **(O)** marks an optional
strengthening. These are proposals only; nothing has been run.

**C4: the latent executor and small edits**
1. **(R) Function vector against learned vector** (Todd 2024; Yang 2026; Hendel 2023).
   - Extract an FV from few-shot table prompts, using head average indirect effect with shuffled destinations as
     the corruption. Take the top 20–50 heads.
   - Extract Hendel's θ.
   - Add each at about layer 12 and at layer 18, zero-shot.
   - Report rows, certified tables and cosine to the 2,560 vector.
   - Also train Saglam's weighted-head vector.

   This tells us whether the executor is an ICL task the base model already represents, or needs a vector it cannot
   produce itself.
2. **(R) Pretraining dependence** (Zhong & Andreas 2024; Lu 2021). Train the same 2,560 vector and the 8-vector soft
   prompt on:
   - Qwen3-4B with each layer's weights permuted across heads, or re-initialised;
   - an open model with intermediate checkpoints (OLMo-2 or Pythia) at two or three pretraining stages.

   Expect failure on (a). The curve over checkpoints shows when the executor becomes latent.
3. **(R) Second model family** (Shao 2025; Wu 2026). Run the vector, soft prompt and rank-1 edits on Llama-3.2-3B or
   Gemma-3-4B. If only Qwen works, write "in Qwen3-4B".
4. **(R) Cross-model patching and head labels** (Prakash 2024; Davies 2023).
   - Patch Savant's head outputs into the base model, group by group.
   - Use desiderata masking to label heads as destination-value, row-position or key-match.
   - Report node overlap and an edge-level measure (Wang 2025).
5. **(O) Mechanism of the vector** (Yang 2026; Sinii 2025b).
   - Reconstruct its effect through OV circuits only.
   - Find its key heads and their overlap with the committee.
   - Check whether it changes attention patterns (Q/K) or only head outputs (V/O). Petrov 2024 predicts the
     latter for prefix-like edits.
6. **(O) Intrinsic dimension below 2,560** (Aghajanyan 2021; Morris 2026). Project a d-dimensional trainable vector
   through a fixed random matrix to 2,560, for d ∈ {8, 32, 128, 512}, and report certified tables against d. A
   one-line headline if it certifies at d ≈ 32.
7. **(O) Localised baselines** (LoFiT 2024; ReFT 2024; BitFit 2022).
   - LoFiT bias offsets on the ~30 committee heads only;
   - LoReFT rank 1 at layer 18;
   - BitFit on all biases.

   This shows where the switch lives.
8. **(O) Back-patching on the base model** (Biran 2024). Patch the residual stream after L7.H7 has selected the row
   into a later layer, to test "it finds the row but reads it too late".

**C5: the pinned clock as a cache policy**
9. **(R) Policy factorial** (StreamingLLM; Delethink; PCW).
   - Sink: 4 tokens or Π.
   - Window: sliding k ∈ {2, 3, 4} or block-aligned.
   - Positions: cache-relative or textual.
   - Plus Delethink carryovers m ∈ {2, 4, 8, 32} re-encoded fresh.

   Run it on Savant and on base + vector. This isolates alignment as the ingredient and tests whether "history is
   noise" holds for an executor never trained on pairs.
10. **(R) Score-based eviction at equal budget** (H₂O, SnapKV, TOVA, Random Attention). Budget |Π| + 2 and
    |Π| + 8, token by token. Also apply SnapKV to Π itself at 75%, 50% and 25% to show the program must stay whole.
11. **(O) Gap and position-ID scan against Prompt Cache's claim.**
    - Margin and certified tables against gap g ∈ {0, 1, 2, 4, 8, 16, 64}.
    - Same against a constant shift.
    - A fixed separator token between Π and the block.
    - Fit RoPE long-term decay.
12. **(O) Π-only for committee heads** (DuoAttention). Give non-committee heads a streaming cache (sink + block only)
    and keep Π for the ~30 heads. A memory saving, and a test of localisation.
13. **(R, writing only) Bitwise conditions** (He 2025). State the kernels, batch size, split-KV setting and cache
    layout in Methods. Optionally show which serving change breaks bitwise equality.

**C7: mechanism**
14. **(R) Positional, lexical and reflexive triad** (Gur-Arieh 2026). Use counterfactual row swaps by table size and
    row index, and filler between rows. Check whether row 0's weakness is positional or sink-related, measuring
    sink mass and massive activations on row 0 (Gu 2025; Sun 2024).
15. **(R) Tuned-lens confirmation of the two-stage read-out** (Belrose 2023), with attention-output patching at
    layers 20–26 (Wiegreffe 2025).
16. **(O) QK attribution for role additivity** (Kamath 2025). Decompose the matched-row score into source, event and
    destination feature terms plus their interactions, and report the interaction share per committee head.
17. **(O) Token versus concept induction** (Feucht 2025). Score committee heads, then ablate concept-induction heads
    and check whether near-duplicate-name errors (` illeg` / ` illegal`, ` Zahl` / ` zahl`) fall.
18. **(O) Redundancy curves** (McGrath 2023; Rushing & Nanda 2024). Ablate cumulatively, best-first and random, and
    measure compensation.
19. **(O) Stable-region comparison** (Janiak 2024; Ferreira da Silva 2026). Interpolate between s and s′ with their
    protocol, and test whether the boundary is sharper along s → s′ than along random mixtures.

**C8: drift**
20. **(R) Lookback ratio as an early warning** (Chuang 2024). Compute per-head attention to Π against attention to
    history along plain runs, and train a linear detector for "first error within the next n ticks".
21. **(R) Split-softmax baseline** (Li 2024). Re-weight attention toward Π during plain decoding.
    - If plain runs become exact at 8k, the clock's remaining value is the pointer and the certificate. The paper
      already says that; make it measured.
    - If they do not, the clock's eviction is necessary, not just its attention.

---

## 6. Unverified or unverifiable items

These were not used as evidence above, or are flagged where used.
- **Heimersheim & Mendel (2024)**, the "activation plateaus" LessWrong post. Not fetched; known only through D7 and
  D8.
- **Shinkle & Heimersheim (2025)**, cited by D8. Not found before the search budget ran out.
- **Llama 4 chunked local attention (Meta, 2025).** The search budget ran out before a primary source could be
  checked, so it is not cited. Find a primary URL if we want "chunked attention in production" as a precedent.
- **Kamath et al. (2025), E9.** The title was confirmed on the live page. The author list and July 2025 date come
  from a search snippet; check them before citing.
- **Two works I could not identify:**
  - "Shi et al. 2025", on attention dynamics of instruction hierarchy, cited by HIPO (arXiv:2603.16152);
  - "Lepori et al. 2025", on mid-layer answer decoding, cited by arXiv:2604.12426.
- **Venues.** Venues not given above were not checked (Jain 2023, Feng & Steinhardt 2023, Wang 2022 (IOI), LoRA,
  LIMA, Olsson 2022 and others). Use the arXiv ids until `verify_refs_v2.py` confirms venues.
- **Details the papers do not state:**
  - whether Delethink restarts position IDs per chunk;
  - how PENCIL assigns positions after a reduction.

  Our claim that "Delethink at a two-token grain" is our policy relies on its fresh re-encoding of query plus
  carryover, which the paper does state. Positions are the open detail.

## 7. Naming collisions to avoid in the paper

- **"Clock":** the modular-addition "Clock" algorithm (K1–K3).
- **"Sink":** an uninformative token absorbing excess attention (H1, H27, H28).
- **"Lookback":** Prakash 2025's mechanism, and the Lookback Lens.
- **"Retrieval heads":** Wu 2025's copy-paste-score definition, versus Yang 2025's late-stage heads.
- **"Task vector":** activation space (Hendel) versus weight space (Ilharco).
- **"Lookup table":** in-weight features (Lindsey 2025) versus our in-context table.

Prefer "pinned decoding" or define "clock" on first use, "persistent prefix", "destination-reading heads",
"activation-space task vector" and "in-context table".
