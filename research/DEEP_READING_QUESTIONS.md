# Deep reading: finite certification, restoration and long-horizon exactness in sequence models

## Your task
Read the papers below **in full**: main text, proofs and appendices. Do not stop at abstracts or summaries. Then
answer the questions and write the synthesis in §4. Precision matters more than coverage.
- Quote theorem statements **verbatim**, with their numbering.
- State every assumption a result depends on, including assumptions hidden in the proofs.
- Mark anything you could not verify.

If a paper is unavailable, say so, and use the closest available version (arXiv, journal, thesis).

## 1. Papers (read all; the core set first)

**Core set:**
1. Hahn, M. (2020). *Theoretical Limitations of Self-Attention in Neural Sequence Models.* TACL 8:156–171.
2. Chiang, D. & Cholak, P. (2022). *Overcoming a Theoretical Limitation of Self-Attention.* ACL 2022.
3. Bansal et al. (2025). arXiv:2512.13898. In particular, the attention-dilution lemmas (2.2 and 2.3) and how the
   required score gap grows with context length.
4. Brandoit, Fyon, Braipson, Clara, De Geeter, Sacré, Ernst, Drion (2026). *Length-Independent State Tracking Under a
   Parallel Scan.* arXiv:2609.32447.
5. Bugaud (2026). *Which Regular Languages Admit Provably Correct RNN Implementations? A Lattice-Theoretic
   Characterisation via Forward-Invariant Sets*, and *Combining Theory and Benchmarks for Length Generalisation:
   Formal Certificates Meet Large-Scale Evaluation* (ICML 2026 workshops; OpenReview).
6. Casey, M. (1996). *The Dynamics of Discrete-Time Computation, with Application to Recurrent Neural Networks and
   Finite State Machine Extraction.* Neural Computation 8(6).
7. Maass, W. & Sontag, E. (1999). *Analog Neural Nets with Gaussian or Other Common Noise Distributions Cannot
   Recognize Arbitrary Regular Languages.* Neural Computation 11. Also Maass & Orponen (1998).
8. Lewandowski, Machado & Schuurmans (2026). *Universal Computation Is Intrinsic to Language Model Decoding.*
   arXiv:2601.08061. Also its predecessor, Schuurmans, Dai & Zanini (2024), *Autoregressive Large Language Models
   Are Computationally Universal.*
9. Abbe, Bengio, Lotfi, Sandon & Saremi (2024). *How Far Can Transformers Reason? The Globality Barrier and Inductive
   Scratchpad.* NeurIPS 2024, arXiv:2406.06467.
10. Chow, T. S. (1978). *Testing Software Design Modeled by Finite-State Machines.* IEEE TSE SE-4. Also Vasilevskii
    (1973) and Huang & Peleska, arXiv:2105.11786.

**Second set:**
11. Cai, Shin & Song (2017). *Making Neural Programming Architectures Generalize via Recursion.* ICLR 2017.
12. Liu, Ash, Goel, Krishnamurthy & Zhang (2023). *Transformers Learn Shortcuts to Automata.* ICLR 2023.
13. Merrill & Sabharwal. *The Expressive Power of Transformers with Chain of Thought* (ICLR 2024), and Merrill,
    Petty & Sabharwal (2024), *The Illusion of State in State-Space Models.*
14. Yang, Srebro, McAllester & Li (2025). *PENCIL: Long Thoughts with Short Memory.* ICML 2025, arXiv:2503.14337.
15. Jelassi, Brandfonbrener, Kakade & Malach (2024). *Repeat After Me: Transformers Are Better than State Space
    Models at Copying.* arXiv:2402.01032. Also Wen, Zhang, Chen & Lyu (2026), arXiv:2607.16072.
16. Blum, A. & Mitchell, T. (1998). *Combining Labeled and Unlabeled Data with Co-Training.* Also Dasgupta, Littman &
    McAllester (2001), *PAC Generalization Bounds for Co-Training*, and Platanios et al. (2014 and 2016) on
    estimating accuracy from the agreement of classifiers.
17. Goldman & Kearns (1995). *On the Complexity of Teaching.* Also de la Higuera (1997) on characteristic samples
    for DFAs.
18. Blondel & Tsitsiklis (2000), on the undecidability of boundedness for products of matrices; Jungers (2009), *The
    Joint Spectral Radius*; and the counterexamples to the finiteness conjecture (Bousch–Mairesse 2002;
    Blondel–Theys–Vladimirov 2003).
19. Amit, Goldwasser, Paradise & Rothblum (2025). *Models That Prove Their Own Correctness.* NeurIPS 2025.

## 2. Notes to write for each paper (half a page to two pages)
- **Setting:** the model class, the precision, and what "correct" means.
- **Main results**, quoted verbatim, with the proof technique in 3–6 lines.
- **Assumptions,** explicit and hidden: boundedness, normalisation, positional encoding, causal masking, precision,
  noise model, fixed or growing depth.
- **What is necessary and what is only sufficient.** Is there a converse?
- **Limitations and open problems the authors state.** Quote them.
- **Constants and rates:** how the bounds scale with sequence length, depth, width and margin.

## 3. Questions
**A. Influence decay in attention (1, 2, 3, 13).**
1. What exactly does Hahn's Lemma 5, or its equivalent, assume? Does it hold with causal masking, pre-layer-norm, a
   normalisation epsilon, rotary positions, QK-normalisation and multi-head attention? Where would the proof break
   for each?
2. With causal attention, intermediate positions normalise over their own prefixes. What is the correct rate:
   O(1/n), or O(log^{D−1} n / n) for depth D? Is it tight? Give the best known lower and upper bounds.
3. What escapes the decay? Length-scaled temperature (Chiang & Cholak), unbounded scores, attention sinks, hard
   attention. For each, what is the minimum change that restores constant sensitivity?
4. How does Bansal et al.'s dilution bound relate to Hahn's? Do they imply a "horizon" (the length at which a fixed
   margin can no longer be guaranteed) as an explicit function of the score gap?

**B. Restoration and exact state tracking in continuous systems (4, 5, 6, 7, 18).**
1. State Brandoit's Theorems 3.1, 3.2, 3.3 and 4.1 and Casey's main theorem exactly. How do they relate? Which
   direction does each prove?
2. Brandoit Theorem 4.1 says affine recurrences either violate restoration or realise only definite automata. What
   precisely is "affine" there? Does the result extend to any recurrence that admits an associative parallel scan,
   or only to linear ones? Is there a known positive result for a *nonlinear, restoring* associative combine
   operator?
3. Bugaud's forward-invariant certificate iff: what is the exact statement, and how does the lattice
   characterisation work? Which regular languages are excluded, and why ("absorbing" versus "non-absorbing")?
4. Maass–Sontag: what is the exact class recognised under full-support noise? Does any of these papers address
   *structured* perturbations, where the perturbation is a deterministic function of the input history, rather than
   random noise?
5. Is there any published connection between the joint spectral radius of the error dynamics along an automaton's
   transitions and length generalisation of learned trackers? What would one-step contraction versus product
   stability imply?

**C. Finite certification of unbounded behaviour (8, 9, 10, 11, 17, 19).**
1. Lewandowski et al. and Cai et al. both certify unbounded-length correctness from finitely many checks. What exact
   property of their execution model makes the check finite? What do they say, if anything, about executions whose
   context grows with the history?
2. The W-method: state the completeness theorem under an m-state bound precisely, including the exact suite. What
   are the best known lower bounds on the size of a complete test suite as a function of n, m and |Σ|? Is the
   exponential dependence on m − n unavoidable?
3. How do characteristic samples and teaching sets for DFAs relate to complete test suites? Are they the same object
   in different words? Where do they differ?
4. Self-proving models: what exactly is proved, about which outputs, and under what verifier? How does that relate to
   checking every step of an execution?

**D. Agreement between two channels as verification (16).**
1. State the co-training conditional-independence assumption and the Dasgupta–Littman–McAllester bound on error in
   terms of disagreement exactly. What happens when the views are only weakly dependent? Are there quantitative
   results?
2. Platanios et al.: how is accuracy estimated from agreement alone, and under what independence assumptions? What is
   known when errors are correlated?
3. Is there a known **irreducible floor**: a result that agreement between two predictors sharing a common latent
   misinterpretation cannot certify correctness, with a matching lower bound? Cite it exactly if it exists.
4. Combine the two: if one predictor is a finite-state machine and the other answers queries on a complete test suite
   (C2), what can be proved about the probability that agreement on the suite certifies a wrong machine, as a function
   of the oracle's per-query error, the suite size and the dependence between the two?

**E. Bounded-context computation (8, 9, 14).**
1. What exactly does each of the inductive scratchpad, PENCIL and the Lewandowski harness keep in context, and what is
   discarded? Does any of them prove that what is kept is *necessary*, not just sufficient?
2. Is there a formal statement, anywhere, that relates the information retained in context to whether length
   generalisation or exactness is possible?

**F. Copying and positional reading (15).**
1. State Jelassi et al.'s copying theorem exactly, and which direction is proved. What does Wen et al. prove about
   repeated substrings?
2. Ukkonen (1992) and Pevzner (1995) give the condition under which a string is uniquely reconstructible from its
   q-grams. Has anyone proved the corresponding *iff* for copying by attention? If not, what is the gap?

## 4. Synthesis (the most important part)
1. **Tensions:** pairs of results that appear to conflict, or that answer the same question differently. For each,
   what resolves it?
2. **Open problems stated by the authors,** grouped by theme.
3. **Five candidate theorems** that live at the intersection of at least two of the areas A–F, and that no paper
   above states. For each:
   - a precise statement;
   - which existing lemmas would prove it;
   - the closest existing result, and exactly how the candidate differs;
   - what would refute it.
4. **The one unifying statement,** if there is one. For example: is there a single principle under which training on
   finitely many examples, testing on finitely many cases, and checking agreement on finitely many queries all fail
   to see unbounded-length errors, and under which they all succeed? Say what is genuinely new about it relative to
   teaching-dimension and complete-testing theory, or say plainly that nothing is.

## 5. Format
- One Markdown report, with sections for the per-paper notes, the answers A–F and the synthesis.
- Full citations with links, verified.
- A short list of what you could not read or verify.
