# Novelty check (23 October 2026)

**Our claim.** An invariance loss over Nerode-equivalent histories, measured in the readout's normalisation
and started after a representation exists, makes a per-event state tracker exact far past its training
length (64–128×, exactness 1.000 on every seed), with a theorem explaining why (first-order sensitivity to
per-step drift where the next-token loss is second-order), and with every training pair certified by a proof
kernel. Verified prior art, closest first:

1. **NextLat, Teoh et al. (Langford's group), arXiv 2511.05963, Nov 2025 / v4 Jun 2026.** Next-token loss plus
   prediction of the next hidden state given the next token (stop-gradient target, d-step rollouts) and a KL
   term; a theorem that the optimum is a belief state; on the A5 word problem a 2-layer transformer trained at
   12 tokens does not generalise, but its co-trained RNN-style latent dynamics model reaches > 95% at 36
   tokens (3×). **Closest in spirit** (belief state as the target; the action-conditioned next-latent loss is
   our SELFSTATE S2 brave variant, which learned the transport to 2–4% residual and still drifted at 256).
   Differences: prediction of the next state versus invariance over equivalent histories; 3× at > 95% versus
   64–128× at 1.000; no certified pairs, no kernel, no exactness theorem, no analysis of the trivial minima.
   **Action:** NextLat becomes a registered baseline arm in stage-one hardening, alone and combined with the
   invariance term.
2. **Learning minimal automata with RNNs, Aichernig et al., SoSyM 2024.** A regulariser pushing states to
   one-hot corners, post-hoc minimisation, iterative architecture shrinking; Tomita grammars and BLE protocol
   models; no length extrapolation measured; equivalence handled by minimisation after training, not by a
   loss on equivalent prefixes. Distinct; cite.
3. **State-regularised RNNs, Wang & Niepert, ICML 2019 (1901.08817).** States pulled toward learned
   centroids; improves extrapolation; no equivalence pairs. Distinct; cite as the "discrete state helps"
   precedent.
4. **Forward-invariant certificates, Bugaud, ICML 2026.** Length generalisation of Elman RNNs characterised by
   forward-invariant positive-margin sets; absorbing-state languages; a characterisation, no objective.
   Complementary theory; cite.
5. **SIRE, Cohen-Karlik et al. 2020 (2010.13055).** A soft penalty making an RNN's state invariant to
   permutations of its input; the same shape of idea (invariance across equivalent inputs as a loss) in a
   different setting (sets, not automata), no exactness or length claim. Cite as the nearest "invariance as a
   regulariser" precedent.
6. **Corder (2009.02731) and ContraCode.** Contrastive learning over semantically equivalent code (renaming,
   statement swaps) for retrieval and summarisation embeddings. Same equivalences we use in the code domain,
   different purpose (no state tracking, no length). Cite.
7. **Bisimulation metrics, MDP homomorphisms, path independence** (POSITIONING.md B1–B2): the lineage; no
   prior result on length extrapolation from such objectives (recorded as not found).
8. **State-tracking literature 2025–26** (2502.20129, 2503.02854, 2602.18333): documents the collapse past a
   cutoff length and suggests loss changes without testing one; our result is the tested loss change.

**Verdict.** We are not repeating anyone. The nearest work (NextLat) shares the belief-state target and a
3× generalisation on A5 from a next-latent loss; ours is a different objective with a theorem, certification
and two orders of magnitude more extrapolation at exactness. The paper must cite NextLat prominently, run it
as a baseline, and state the comparison plainly.
