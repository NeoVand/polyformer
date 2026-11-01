**Objects:** follower sets \(F(u)=\{v:uv\in\mathcal L(X)\}\); right-resolving labeled graphs presenting sofic shifts; word-growth entropy \(h(X)=\lim_n n^{-1}\log|\mathcal L_n(X)|\).

**Three transferable results:** finite follower-set count characterizes sofic shifts; a finite right-resolving presentation gives \(h=\log\rho(A)\); every proper subshift of an irreducible sofic shift has strictly smaller entropy. Sources: [Weiss, 1973](https://cris.huji.ac.il/en/publications/subshifts-of-finite-type-and-sofic-systems/), [Lind–Marcus, 1995](https://www.cambridge.org/core/books/abs/an-introduction-to-symbolic-dynamics-and-coding/entropy/A611373E07F376DC3D2040A8157291C5), [entropy-minimality theorem](https://www.cambridge.org/core/journals/ergodic-theory-and-dynamical-systems/article/encoding-subshifts-through-sliding-block-codes/861CDCF1FD91F8CEFD86C9C8C3A448D8).

**To the problem:** each row specifies state / rule / check / search.

| Problem | Transfer | Yield |
|---|---|---|
| P1 representation | Follower class / forbidden blocks / legal continuation count / higher-order constraint discovery. | TOOL |
| P2 learning | Candidate follower partition / symbol transitions / queried distinguishing continuations / split states where overgeneration appears. Positive observations alone cannot identify support. | TOOL |
| P3 memory | Follower vertex / graph walk / continuation-language equality / merge equivalent vertices. Entropy measures branching, not required state count. | TOOL |
| P4 retrieval | Follower signature / continuation compatibility / suffix acceptance / retrieve states admitting the requested future. | FRAME |
| P5 language | Protocol-document state / cross-field constraints / legal completion / search structured text containing checksums, permissions, or linked fields. Ordinary prose lacks crisp forbidden words. | FRAME |
| P6 verification | Candidate graph / allowed transitions / entropy plus language inclusion / search counterexample words. | HIT |
| P7 capability | Persistent constraint state / admissible block generation / zero illegal completions / enumerate alternatives after an edit. | TOOL |
| P8 test | Learned graph / hidden parity blocks / validity and entropy / sweep dilution and block arity. | TOOL |

The P6 import is conditional but exact: if \(X\subseteq Y\), \(Y\) is irreducible sofic, and \(h(X)=h(Y)\), then \(X=Y\). **Entropy equality alone certifies nothing**, and numerical agreement is not exact equality.

**From the problem:** Nerode classes identify follower sets, but equal future *growth rates* do not imply equal future languages. Higher-order terms expose constraints invisible to lower-order projections: uniformly distributed binary \(k\)-tuples with fixed parity have every proper marginal uniform, yet only \(2^{k-1}\) admissible tuples. Ignoring that interaction doubles the continuation count; this is a support-level obstruction to direct lower-order logits, not a lower bound against deep pairwise networks.

**Proposal: entropy-guided discovery of parity-conditioned follower states.**

A recurrent memory tracks a hidden mode selecting even or odd parity for delimited \(k\)-bit records, with long neutral spans between updates. A query-conditioned product \(q_s\prod_i x_i\) scores joint legality, while an extracted deterministic graph measures excess continuation growth. Train with legality queries targeting candidate-generated forbidden records, splitting memory classes when their futures differ.

Experiment: \(k=4,6\), train at 128 tokens, test at 4,096; compare pairwise, product-only, and product-plus-follower-training models at matched compute. Kill the proposal if the combined model fails 99.9% record validity or improves fewer than tenfold in violation rate across five seeds.

Closest prior art: Weiss’s sofic systems (1973), Lind–Marcus’s entropy and coding framework (1995); novelty lies in the training mechanism.