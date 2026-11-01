**C1a — PARTIAL; the architectural core is owned.** [Clift, Doryn, Murfet & Wallbridge (2020, ICLR), *Logic and the 2-Simplicial Transformer*](https://arxiv.org/abs/1909.00668) apply three-way attention and tensor-product values to entity representations, restricting key pairs to learned, attention-updated “virtual entities” in BoxWorld. These are temporary computational slots, not persistent, coreference-deduplicated discourse memory. The latter, evaluated under long-context dilution, remains a defensible distinction.

The requested adjacent work supplies components, not that complete combination:

- [Santoro et al. (2018, NeurIPS), *Relational recurrent neural networks*](https://arxiv.org/abs/1806.01822): pairwise multihead attention between recurrent memory slots.
- [Goyal et al. (2019, arXiv:1909.10893), *RIMs*](https://arxiv.org/abs/1909.10893): selectively updated recurrent modules with sparse attention-mediated communication.
- [Henaff et al. (2017, ICLR), *EntNet*](https://openreview.net/pdf?id=rJTKKKqeg): maintains and updates entity-like memory while reading text.
- [Locatello et al. (2020, NeurIPS), *Slot Attention*](https://arxiv.org/abs/2006.15055): competitive attention learns exchangeable object slots.
- [Altabaa, Webb, Cohen & Lafferty (2023, arXiv:2304.00195; ICLR 2024), *Abstractors*](https://arxiv.org/abs/2304.00195): separates pairwise relational information from object features.
- [Wang et al. (2026, arXiv:2603.09466), *TopoOR*](https://arxiv.org/abs/2603.09466): higher-order attention over operating-room entities and topological cells, without discourse-memory learning.
- [Das, Dhruman Gupta & Debayan Gupta (2026, arXiv:2608.09307), *Linearized 2-Simplicial Attention*](https://arxiv.org/abs/2608.09307): compresses one token axis into recurrent statistics; no entity deduplication.

**C1b — OPEN as the specific causal diagnosis, not an established fact.** No verified paper found identifying repeated-mention/filler tuple domination and prescribing entity-equivalence binding as its remedy. Counting irrelevant tuples alone does not establish attention failure; learned weights matter.

- [Roy et al. (2025, arXiv:2507.02754), *Fast and Simplex*](https://arxiv.org/abs/2507.02754): token-level trilinear attention improves token efficiency on language/reasoning benchmarks, contradicting blanket failure.
- [Sanford, Hsu & Telgarsky (2023, NeurIPS), *Representational Strengths and Limitations of Transformers*](https://arxiv.org/abs/2306.02896): proves triple-detection expressivity bounds, not the proposed dilution mechanism.
- [Kim & Schuster (2023, ACL), *Entity Tracking in Language Models*](https://aclanthology.org/2023.acl-long.213/): benchmarks discourse-state tracking; does not diagnose higher-order tuples.

**C1c — OWNED as a representation-learning principle.** Exact language-specific “iff all suffixes agree” guarantees remain a narrower contribution.

- [Amy Zhang et al. (2019/2021, arXiv:1906.10437), *Learning Causal State Representations*](https://arxiv.org/abs/1906.10437): trains recurrent history encoders toward predictive causal states and connects them to bisimulation.
- [Hong, Dragan & Levine (2024, ICLR), *Offline RL with Observation Histories*](https://proceedings.iclr.cc/paper_files/paper/2024/hash/1c3d419b754cb4de0a67a453cb28d959-Abstract-Conference.html): explicitly trains history representations with on-policy bisimulation loss, including GPT-2 Wordle experiments.
- [Zhang et al. (2021, ICLR), *DBC*](https://arxiv.org/abs/2006.10742): trains latent distances to match bisimulation and suppress visual distractors.
- [Castro (2020, AAAI)](https://arxiv.org/abs/1911.09291): introduces policy-conditioned similarity and differentiable metric approximation.
- [Castro, Kastner, Panangaden & Rowland (2021, NeurIPS), *MICo*](https://arxiv.org/abs/2106.08229): shapes RL representations with sample-estimated behavioral distances.
- [Abichandani et al. (2026, arXiv:2610.33012), *Recursive Semantic Divergence*](https://arxiv.org/abs/2610.33012): uses bisimulation-inspired rollout disagreement as an LLM fine-tuning reward, not exact Nerode supervision.

**C2 — PARTIAL.** The ingredients exist; distinguishing-suffix state training specifically preventing dilution collapse remains unverified.

- [Ferns, Panangaden & Precup (2004, UAI), *Metrics for Finite MDPs*](https://arxiv.org/abs/1207.4114): defines action-maximized bisimulation metrics.
- [Weiss, Goldberg & Yahav (2018, ICML)](https://proceedings.mlr.press/v80/weiss18a.html): uses queries/counterexamples to extract automata from trained RNNs.
- [Carr et al. (2019, IJCAI)](https://arxiv.org/abs/1903.08428): counterexamples drive RNN-policy retraining, without L*-style suffix representation losses.
- [Akyürek, Wang, Kim & Andreas (2024, ICML)](https://arxiv.org/abs/2401.12973): studies in-context regular-language learning and n-gram heads, not equivalence-objective training.

**C3 — PARTIAL.** [Polyvyanyy, Solti, Weidlich, Di Ciccio & Mendling (2020, ACM TOSEM)](https://doi.org/10.1145/3387909) use entropy-derived, strictly monotone measures to characterize language coverage/equality for discovered specifications. A neural-generator certificate remains open: establish subshift support \(Y\subseteq X\), irreducible-sofic \(X\), and exact \(h_{\mathrm{top}}(Y)=h_{\mathrm{top}}(X)\). Estimated entropy or perplexity does not suffice.

Search cutoff: **November 1, 2026**. Semantic Scholar direct access failed; indexed searches supplemented arXiv, OpenReview and ACL. OPEN means no verified match found.

**Most dangerous for C1: Clift et al.** Novelty requires persistent entity deduplication plus controlled evidence that tuple contamination causes dilution failures and that entity-level higher-order binding fixes them beyond matched token-attention and pairwise-slot baselines.