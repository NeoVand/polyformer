# Whiteboard: settled meanings and global addresses

21 October 2026. A reading note, no experiments. It follows the REVISE null (every arm above softmax at
2k; report in the `claude/exciting-antonelli-dc7582` worktree) and Neo's correction of two insights that
the REVISE design had misread. Three literature sweeps were run on the three cells that survived a
SCAMPER pass; their load-bearing claims were checked against primary sources. Numbers carry their
protocol; "reported" marks a claim read only from an abstract or a secondary source.

## 0. The two insights, stated correctly

1. **Type-level stability.** After enough training on all of language, some vocabulary types have a settled
   meaning and need no contextual computation; others never settle and always need it. This is a property
   of the type acquired across the corpus, not a property of a token within one document (which is what
   REVISE built and the model declined).
2. **Address.** The meaning of a word is its address in the hypergraph of all sentences: the orbit of the
   hypergraph's automorphism group, computed once from the whole corpus. The address shifts as the corpus
   grows; for some words it converges, for others it never does. (Assumption used below: the address is a
   global coordinate computed from the corpus, not something computed at read time from the context.)

## 1. What the literature says, cell by cell

### A. Units: tokenization as the choice of addresses

- No tokenizer anywhere selects units by representational stability. The nearest relatives: SaGe prunes
  BPE tokens whose corpus contexts are ambiguous (skip-gram likelihood; BERT at a 24-GPU-hour budget, QNLI
  66.2→74.8, NER F1 .71→.75; ~12% more tokens) [Yehezkel & Pinter 2023]; branching entropy and PMI merges
  are counting proxies for "stable contexts" [Hu 2025; Nouri 2026]; Rajaraman et al. prove that on
  Markov sources a good tokenizer lets a unigram model over tokens be near-optimal, i.e. good units absorb
  context dependence [NeurIPS 2024].
- **SuperBPE is not the free win it looks like.** At 8B with matched training FLOPs and matched context in
  bytes: +4.0 points over 30 tasks and +8.2 MMLU, but bits-per-byte is slightly *worse* (0.7465 BPE vs
  0.7482 SuperBPE), the paper says BPB and downstream rankings "are not consistent", and the footnote says
  higher compression does not necessarily help. Below 8B only BPB is reported: SuperBPE wins when
  under-trained and the parameter-matched version loses when over-trained. Two independent small-vocabulary
  replications are null (Arcee Trinity, reported; Chowdhury & Woolf 2026, worse by 0.01–0.06 BPB on
  non-English). What SuperBPE does change is the per-token loss distribution: fewer very-low-loss and
  very-high-loss predictions.
- **Two results make "settled units get their own address" testable without a new tokenizer:**
  - *Over-Tokenized Transformer* [Huang et al., ICML 2025]: keep the tokenizer, add hashed 2-gram and
    3-gram input embeddings (12.8M rows, low-rank slices) summed with the 1-gram embedding. Loss falls
    log-linearly in the table size (about 0.015 per 4× rows at 1.3B MoE); extra FLOPs under 0.5%; a 400M
    model with the large table is reported to match a 2.5× larger baseline; improvements are claimed from
    151M up (qualitative at the smallest size). Scaling the *output* vocabulary hurts small models. This
    is an input-side address for multi-token units, chosen by hashing every n-gram rather than by any
    criterion.
  - *Inner lexicon* [Kaplan et al., ICLR 2025]: models reassemble multi-token words at the last token in
    early–middle layers; feeding that settled hidden state back in as a new input embedding works with
    no finetuning, shortening inputs at little or no accuracy cost. A settled meaning literally becomes an
    address. Selection there is by decodability, not by stability.
- Vocabulary itself is under-scaled: the optimal vocabulary grows with compute (N_v ∝ N_nv^0.83; 33M–3B)
  [Tao et al., NeurIPS 2024]; at 25M parameters most of a vocabulary-size gain survives byte-matching
  [Lester et al. 2024].
- Methodology: per-token loss is incomparable across vocabularies; report bits-per-byte *and* downstream,
  match bytes and context in bytes, hold vocabulary size and embedding parameters fixed, and treat
  downstream below 150M as near noise.

### B. Depth: do settled types need less computation?

- Probes on frozen models disagree on the sign for function versus content words (DoLa: function words
  settle mid-depth; Shan 2024: determiners converge later than nouns; Gupta 2025 with a tuned lens:
  determiners by layer 5, content words by 20), so raw logit-lens claims are probe-dependent.
- The robust fact is about frequency and scale: on Pythia 70M–1.4B, low-frequency tokens converge at
  0.78–0.90 of depth and high-frequency at 0.61–0.72, and the gap grows from 0.06 of depth (about half a
  layer at 70M) to 0.29 (about seven layers at 1.4B); it survives tuned-lens calibration and is not
  embedding norm [Makou et al., TMLR 2026, the frequency analysis inside "Many Circuits, One Mechanism"].
  At our scale every type converges at nearly the same depth, so a router has nothing to separate.
- **Skippability is not a property of the type.** Balogh 2026 (GPT-2 Medium and Large, Pythia
  160M–2.8B): a gate deciding whether an MLP can be replaced by a linear map scores AUC 0.567 from the
  token embedding alone against 0.605 from context and 0.609 from the full activation; per-token
  "no-fly" lists built on one corpus transfer with r below 0.05; token identity explains 0.2–1.3% of
  variance. Yet 25–56% of MLP calls can go linear at under 1% perplexity cost, because the cost is skewed
  across positions, not across types.
- Mixture-of-depths gains (up to 1.5% at equal FLOPs, 60M–3B) do not replicate at small scale: Lawson &
  Aitchison 2025 (GPT-2-small shape, 10B tokens) find no gain over shallower dense models and gates that
  collapse without regularisation; RankMoD (ICML 2026 workshop, reported) finds MoD scales more slowly
  than dense. Our −1.5% at 22M is the same result.
- Lookup memories pay, but from a size: memory layers from a 134M base on factual QA [Berges 2024];
  Large Lookup Layers from a 400M-parameter decoder (iso-FLOP perplexity 22.0→20.2; static routing by
  token identity into up to 512 embeddings per token, allocated by LZW codeword frequency; beats
  iso-sparse MoE at every sparsity) [Tseng & De Sa, ICML 2026]; Engram from 0.56B active (hashed suffix
  2/3-grams, gated by the hidden state, at two layers; 27B: MMLU +3.4, BBH +5.0 at iso-parameter and
  iso-FLOP) [DeepSeek 2026]. Layer-pruning robustness also grows with size [Gromov 2024].
- Reading: the stability-as-depth claim is true and scale-dependent, and the variable it tracks so far is
  frequency. Whether representational stability predicts convergence depth or scaling slope *beyond*
  frequency is untested.

### C. Global addresses

- Exact orbits are useless on real corpora: random graphs are asymptotically asymmetric, so the orbit
  partition of a corpus hypergraph is almost surely discrete except for words with identical incidence.
  Every usable address is a coarse orbit-invariant: Weisfeiler–Leman colours (the coarsest equitable
  partition; same orbit implies same colour, never the converse) or spectral coordinates (projector
  diagonals, equal to random-walk return probabilities, are well-defined and orbit-invariant; raw
  eigenvectors are not even well-defined). The two are incomparable and both coarser than orbits.
  Hypergraph Laplacians reduce to clique- or star-expansion graph Laplacians, so a sentence-hyperedge
  spectral embedding is a weighted co-occurrence embedding. Which means the modern form of the global
  address is PPMI-SVD/GloVe (word2vec factorises the same matrix implicitly), plus orbit-invariant
  structural coordinates that nobody has computed for words.
- Address drift, measured naively, is mostly noise. Hamilton's laws (frequent words drift slowly,
  polysemous words faster) largely reproduce on chronologically shuffled corpora: displacement correlates
  with frequency at r = −0.92 (counts) on same-year resamples, so the frequency law is sampling noise and
  the polysemy law is mostly frequency [Dubossarsky, Weinshall & Grossman 2017]. A real "différance"
  measurement must subtract a same-size null; nobody has done this per type against corpus size.
- Global addresses as LM input help only rare words: pretrained frozen embeddings beat random by 15
  perplexity points on an LSTM, and the gap falls to 0.9 once words with fewer than five occurrences are
  removed [Welch 2020]; frozen rare-token embeddings change nothing at scale [Yu 2022]; a 2026 attempt to
  initialise from spectral profiles finds no gain [Garbers & Oh, reported]. Inside training, frequent and
  function words converge early and low-frequency words keep their initialisation bias to the end
  [Papadimitriou & Prince 2025]. That is the slot a structural prior would fill, and it is a small slot.
- Pythia is the free instrument for both insights: 154 checkpoints, identical data order across 70M–12B,
  preshuffled deduplicated Pile published, so "corpus up to step k" is literally what the model saw.

## 2. What this does to the insights

- **Stability is real, frequency-shaped, and scale-dependent.** The depth a type needs separates with
  model size and is not visible at 22M. It cannot be exploited by routing at our scale (predicted null,
  observed null). It *can* be exploited by addresses, because embedding parameters are nearly free in
  FLOPs: give settled multi-token units their own input address. The field does this by hashing every
  n-gram (Over-Tokenized) or by frequency (L³, SuperBPE); nobody does it by stability. That is the one
  place the insight adds a criterion the field lacks, and it is testable in our regime.
- **The global address already exists in the model** as the embedding table, learned by factorising the
  same co-occurrence structure a spectral hypergraph embedding would. Supplying it from outside helps rare
  words and nothing else. Orbit-invariant structural coordinates for words are untested; I would not bet
  on them for loss, but they are the right object for measuring drift, since they need no alignment.
- **Différance is measurable only against a null.** The existing laws are confounded; the clean per-type
  measurement against corpus size, with same-size resamples and frequency partialled out, has not been
  done and costs no GPU.

## 3. Three tests, cheapest first

**T1. Measure, no training (CPU plus forward passes of public models; well under $20).**
On the preshuffled Pile at the fractions that match Pythia steps: PPMI-SVD addresses (fixed 100k
vocabulary, rank 300) on nested prefixes plus five same-size resamples per fraction; per-type drift after
Procrustes on frequent anchors, minus the null. Per type from Pythia 70M–2.8B: contextual variance after
standardising dimensions and subtracting the layer mean (Ethayarajh with the Timkey correction),
tuned-lens convergence depth, and loss-versus-size slope. Regress drift, depth and slope on stability with
log frequency, sense count, part of speech and subword position as covariates; report partial R² and a
frequency-matched version. Positive result: stability predicts depth and slope with frequency partialled
out, and the effect grows with size (the frequency-only baseline is the 0.06→0.29 gap). This is the test of
the insight itself, and the result is a paper either way: a law, or the demonstration that "stability" is
frequency by another name.

**T2. Stable units as input addresses (our harness, about $30).**
Over-tokenized input embeddings in the 22M model: hashed 2-gram and 3-gram tables summed into the input,
tables of 1M rows in low-rank slices, under 1% extra FLOPs. Arms: softmax; plus hashed n-gram addresses
(the published mechanism, expected to gain if the 151M claim holds down here); plus addresses only for
units selected by stability from a public model (T1's measure) against the same number selected by
frequency, with the frequency-stratified control. Report bits-per-byte at equal bytes and equal FLOPs,
buckets, and the per-token loss distribution. This is the candidate quick win: a published small-scale
gain, with the stability criterion as the new part.

**T3. Settled meanings as embeddings (our harness, about $20).**
Kaplan's expansion at training time: for stable multi-token units, initialise their single-token input
embedding from the settled last-token hidden state of a teacher pass, then train. Compared with random and
with frequency-selected units. Tests the literal form of "a settled meaning becomes an address".

Order: T1 first, because T2 and T3 both need its stability measure and because its result decides
whether the criterion is anything beyond frequency.

## 4. Closed

Routing by a learned gate at 22M (predicted and observed null); revisable in-context memory (REVISE);
holonomy frames on prose (EVENTS); naive drift laws; superword tokenizers as a free win below 8B.

## 5. Open for Neo

Whether the address is a global coordinate computed once from the corpus (assumed here) or something
else; and whether "stable" should mean low contextual variance in a trained model, convergence under
corpus growth, or convergence under model growth, since T1 measures all three and they need not agree.

## Sources

Tokenization: Sennrich 2016 (1508.07909); Kudo 2018 (1804.10959); Yehezkel & Pinter 2023, SaGe
(2210.07095); Hu 2025 (2506.15889); Nouri 2026 (2603.19261); Liu 2025, SuperBPE (2503.13423); Schmidt
2025, BoundlessBPE (2504.00178); Tănase & Pelican, SupraTok (2508.11857); Schmidt 2024 (2402.18376);
Rajaraman 2024 (2404.08335); Tao 2024 (2407.13623); Huang 2025, Over-Tokenized (2501.16975); Kaplan 2025
(2410.05864); Feucht 2024 (2406.20086); Lester 2024 (2404.03626); Vemula & Krishnamurthy 2026
(2608.17325); Arcee Trinity 2026 (2602.17004); Chowdhury & Woolf 2026 (aclanthology 2026.mellm-1.27);
Ethayarajh 2019 (1909.00512); Timkey & van Schijndel 2021 (2109.04404).

Depth and lookup: Chuang 2023, DoLa (2309.03883); Geva 2022 (2203.14680); Shan 2024 (2412.01455); Gupta
2025 (2510.18871); Makou 2026 (2606.06267); Balogh 2026 (2603.03459); Luo 2025, FlexiDepth (2503.23798);
Raposo 2024, MoD (2404.02258); Lawson & Aitchison 2025 (2506.21103); Gromov 2024 (2403.17887); Lample
2019 (1907.05242); Berges 2024 (2412.09764); He 2024, PEER (2407.04153); Tseng & De Sa 2026, L³
(2601.21461); Cheng 2026, Engram (2601.07372); Roller 2021, Hash Layers (2106.04426); Belrose 2023
(2303.08112); Chung & Kim 2025 (2508.15390).

Addresses: Levy & Goldberg 2014 (NIPS); Levy, Goldberg & Dagan 2015 (TACL); Zhou, Huang & Schölkopf 2006;
Agarwal, Branson & Belongie 2006; Krebs & Verbitsky 2014 (1407.3175); Fürer 2017 (1704.01023); Rattan &
Seppelt 2023 (2103.02972); Zhang, Zhao & Maron 2024 (2406.04336); Erdős & Rényi 1963; Dwivedi 2022, RWPE
(2110.07875); Lim 2022, SignNet (2202.13013); Ferrer i Cancho & Solé 2001; Hamilton, Leskovec & Jurafsky
2016 (1605.09096); Dubossarsky, Weinshall & Grossman 2017 (EMNLP); Welch 2020 (2009.14109); Yu 2022
(2109.03127); Garbers & Oh 2026 (2607.09204); Papadimitriou & Prince 2025 (2510.07613); Park 2024/2025
(2311.03658, 2406.01506); Huh 2024 (2405.07987); Chang & Bergen 2022 (2110.02406); Biderman 2023, Pythia
(2304.01373).
