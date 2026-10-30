You are doing an independent prior-art search with live web search. Be adversarial: the goal is to find any earlier
paper that already states or implies the results below. Read each candidate (abstract, theorem statements, and
appendix where needed). For each candidate give: full citation with link, the exact theorem or sentence quoted
verbatim, and a verdict: STATES (same result), IMPLIES (follows directly), PARTIAL (which part), or UNRELATED.
Search arXiv, OpenReview (ICLR/NeurIPS/ICML/COLT/ACL 2023–2026), ACL Anthology, and Google Scholar. Search terms to
use include: causal masking fixed margin transformer, decoder-only expressivity margin, layer norm epsilon margin
transformer language recognition, definite languages transformer, attention influence decay 1/n, Cesàro attention,
sensitivity causal transformer, autoregressive transformer table lookup long context theorem, ALiBi locality
theorem, "definite modulo length".

Results to check:
1. **Causal influence bound.** For a fixed-depth causal pre-norm transformer (layer norm with ε > 0, bounded
   embeddings, uniformly bounded and Lipschitz attention scores, Lipschitz MLP blocks and readout), changing one input
   token at position p changes the last position's depth-L residual by O((1+ln(n/p))^{L−1}/n) when position biases
   are flat, and by O((1+n−p)^{L−1} e^{−m(n−p)}) under an ALiBi-type bias of slope m. Both rates are sharp in the
   class (width-2 witnesses; the flat one is the Cesàro matrix of uniform causal attention).
2. **Class theorem.** If such a model recognises a language with a fixed margin γ > 0 at every length, then for
   n ≥ n₀ membership depends only on (n, the last token): only on the last token if there is no additive positional
   embedding. Under ALiBi it depends only on (n, the last k symbols), with k explicit in m, γ and model constants.
   Conversely, every language that is k-definite modulo length is recognised with margin by a hard-window model.
3. **Autoregressive corollary.** Two contexts of length n that agree at the last position and differ in P earlier
   coordinates cannot carry opposite margin-γ next-token labels once P·C(1+ln n)^{L−1}/n < 2γ. Consequence: a decoder
   with a lookup table at the start of its context cannot keep a fixed margin on the first use of a row whose
   destination occurs nowhere else, once the use is far enough from the table. Contrast: a decoder whose context is
   reset to (table, state, event) with positions restarted has a fixed length, and a finite per-row check is
   complete for it.
4. **W-method erratum.** For Moore machines whose output is read only at the end of the input (final-output
   semantics), Chow's / Vasilevskii's suite P·Σ^{≤m−n}·W is not complete unless the empty word ε is in W.

Known prior art to locate and compare precisely (not to re-report as new):
- Köver, Butoi, Svete, Hahn & Cotterell 2026 (arXiv 2606.08768): encoder (bidirectional) fixed-margin result.
- Hahn & Rofin 2024 (arXiv 2402.09963): say the causal case is open. Has anyone closed it since? Search 2024–2026.
- Chowdhury 2026 (arXiv 2603.10123), Li & Cotterell 2026 (arXiv 2605.00768), Nowak, Cotterell & Boumasmoud 2026
  (arXiv 2607.26988), Wu, Wang, Jegelka & Jadbabaie ICML 2025, Chiang & Cholak 2022, Hahn 2020, Edelman et al. 2022,
  Barbero et al. 2024 (over-squashing), Yang, Chiang & Angluin 2024.

Finish with a table: result 1–4 × verdict (NEW as far as searched / PARTIALLY KNOWN / KNOWN), with the decisive
citation for each, and a list of what you could not access.
