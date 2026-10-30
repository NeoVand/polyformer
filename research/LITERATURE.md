# Literature: exact state from certified equivalences

Systematic review for the paper whose thesis is in `research/CONTRIBUTIONS.md`, with the reach and missing references
of `research/REACH.md`. 85 works in 15 themes. Each entry gives the exact author list and title as the source record
gives them, the venue and year, the arXiv id or DOI, whether the current draft cites it, and one sentence on how it
bears on our claims, including where it pre-empts or weakens them.

**How every entry was verified.** No citation was taken from memory. `research/literature/verify_refs.py` queried the
arXiv API (authors, title, first-version date, journal_ref), the Semantic Scholar Graph API (venue, DBLP key, DOI) and
Crossref (journal, volume, pages) for every candidate, and flagged any id whose retrieved title did not match;
`verify_venues.py` added OpenReview accepted-paper venues and arXiv author comments where Semantic Scholar's year was
the preprint year; `content_checks.py` fetched abstracts for the non-arXiv works (PubMed, Semantic Scholar, Crossref).
The raw records are in `research/literature/refs_verified.json`; the evidence for each venue is printed with the entry.
Relation sentences rest on the abstracts as fetched; where a sentence relies on a paper's body, it says so.

**Draft checked:** `paper/nmi/main.md` on `claude/gracious-panini-dde55f` (`d549b5c`). 'Cited' means the work's arXiv id, DOI or title
appears in the draft's reference list.


## 1. Length generalisation and state tracking

1. Grégoire Delétang, Anian Ruoss, Jordi Grau-Moya, Tim Genewein, Li Kevin Wenliang, Elliot Catt, Chris Cundy, Marcus Hutter, Shane Legg, Joel Veness, Pedro A. Ortega. Neural Networks and the Chomsky Hierarchy. *International Conference on Learning Representations (ICLR) 2023*; arXiv:2207.02098. (cited in the draft as [6]; verified: arXiv; OpenReview 'ICLR 2023 notable top 25%')  
   Across 20,910 models it shows that fitting the training length never implies generalising beyond it and groups failures by architecture class; it supports our premise but locates the cause in architecture, and since its LSTMs did generalise on regular tasks, a reviewer may ask why our recurrent trackers drift at all (our answer: the objective leaves drift unpenalised at scale, T1).

2. Bingbin Liu, Jordan T. Ash, Surbhi Goel, Akshay Krishnamurthy, Cyril Zhang. Transformers Learn Shortcuts to Automata. *ICLR 2023*; arXiv:2210.10749. (cited in the draft as [4]; verified: arXiv; OpenReview 'ICLR 2023 notable top 5%')  
   Shallow transformers represent automata by shortcut solutions that standard training finds and whose brittleness the paper investigates; this supports our reading of the NoPE baseline's 5-8 rewrite horizon (E4) and our claim that the exact state is the automaton itself.

3. William Merrill, Jackson Petty, Ashish Sabharwal. The Illusion of State in State-Space Models. *ICML 2024*; arXiv:2404.08819. (cited in the draft as [5]; verified: arXiv comment 'To appear at ICML 2024'; OpenReview 'ICML 2024 Poster')  
   Proves that state-space models stay in TC⁰ and so cannot express permutation composition (the S5 word problem); it underwrites T12 and our choice of S5, and our non-linear recurrent state sits outside its bound, so it is support, not competition.

4. Riccardo Grazzi, Julien Siems, Arber Zela, Jörg K. H. Franke, Frank Hutter, Massimiliano Pontil. Unlocking State-Tracking in Linear RNNs Through Negative Eigenvalues. *ICLR 2025*; arXiv:2411.12537. (cited in the draft as [50]; verified: arXiv; DBLP conf/iclr/GrazziSZFHP25)  
   Allowing negative eigenvalues gives linear RNNs parity and broader state tracking; it is an architectural route to expressivity, whereas our claim is that an expressive state still drifts unless the objective selects exactness, so it is complementary.

5. Julien Siems, Timur Carstensen, Arber Zela, Frank Hutter, Massimiliano Pontil, Riccardo Grazzi. DeltaProduct: Improving State-Tracking in Linear RNNs via Householder Products. *Advances in Neural Information Processing Systems 38 (NeurIPS 2025)*; arXiv:2502.10297. (cited in the draft as [51]; verified: arXiv; DBLP conf/nips/SiemsCZHPG25)  
   Householder-product transitions improve state tracking in linear RNNs; it is our strongest architectural baseline, and E4 (not exact at 4,096 with or without the signal) is the comparison a reviewer will look for first.

6. Aleksandar Terzić, Nicolas Menet, Michael Hersche, Thomas Hofmann, Abbas Rahimi. Structured Sparse Transition Matrices to Enable State Tracking in State-Space Models. *Advances in Neural Information Processing Systems 38 (NeurIPS 2025), spotlight*; arXiv:2509.22284. (cited in the draft as [52]; verified: arXiv comment 'NeurIPS 2025 Spotlight'; OpenReview 'NeurIPS 2025 spotlight')  
   A one-hot-times-diagonal transition emulates any N-state automaton in one layer with a BIBO-stable recurrence, so closure and exact emulation come from the parametrisation; it partly pre-empts our closure ingredient (T4) and a reviewer may ask whether PD-SSM is exact at length without any certified signal.

7. Yash Sarrof, Yana Veitsman, Michael Hahn. The Expressive Capacity of State Space Models: A Formal Language Perspective. *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*; arXiv:2405.17394. (**not cited in the draft**; verified: arXiv journal_ref; DBLP conf/nips/SarrofV024)  
   Shows state-space models implement exact solutions to star-free state tracking and that non-negative gates limit them; existence of an exact solution is not selection by training, which is the gap our blindness theorem (T1) addresses.

8. Cem Anil, Yuhuai Wu, Anders Andreassen, Aitor Lewkowycz, Vedant Misra, Vinay Ramasesh, Ambrose Slone, Guy Gur-Ari, Ethan Dyer, Behnam Neyshabur. Exploring Length Generalization in Large Language Models. *Advances in Neural Information Processing Systems 35 (NeurIPS 2022)*; arXiv:2207.04901. (cited in the draft as [7]; verified: arXiv; OpenReview 'NeurIPS 2022 Accept')  
   Length-generalisation deficiencies of language models persist independent of scale, and scratchpad prompting improves them markedly; it supports the premise and is also the token-based remedy our latent state is compared against (already cited).

9. Amirhossein Kazemnejad, Inkit Padhi, Karthikeyan Natesan Ramamurthy, Payel Das, Siva Reddy. The Impact of Positional Encoding on Length Generalization in Transformers. *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*; arXiv:2305.19466. (cited in the draft as [9]; verified: arXiv; DBLP conf/nips/KazemnejadPRDR23)  
   No positional encoding generalises better than common encodings on reasoning tasks; it motivates our NoPE baseline, whose short horizon (E4) shows the remedy is insufficient for exact state (already cited).

10. Ricardo Buitrago Ruiz, Albert Gu. Understanding and Improving Length Generalization in Recurrent Models. *International Conference on Machine Learning (ICML) 2025*; arXiv:2507.02782. (**not cited in the draft**; verified: arXiv; DBLP conf/icml/RuizG25; OpenReview 'ICML 2025 poster')  
   Shows that recurrent models (state-space models, linear attention) fail to length-generalise when training covers only part of the attainable states, and that widening state coverage (a Gaussian or another sequence's final state as the initial state, about 500 post-training steps) restores generalisation from 2k to 128k tokens; it pre-empts the coverage half of our Markov-step result (E13, uniform-state training) and must be cited there, while exactness at length still needs closure and the certified signal.

## 2. Arithmetic length generalisation

11. Sean McLeish, Arpit Bansal, Alex Stein, Neel Jain, John Kirchenbauer, Brian R. Bartoldson, Bhavya Kailkhura, Abhinav Bhatele, Jonas Geiping, Avi Schwarzschild, Tom Goldstein. Transformers Can Do Arithmetic with the Right Embeddings. *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*; arXiv:2405.17399. (**not cited in the draft**; verified: arXiv; OpenReview 'NeurIPS 2024 poster')  
   Per-digit position embeddings with input injection and recurrence reach 99% on 100-digit addition from 20-digit training (about 6x); it is the baseline a reader will set against E6 (exact at 128x), and the contrast is architecture-specific addressing versus an objective that needs no task-specific embedding.

12. Hanseul Cho, Jaeyoung Cha, Pranjal Awasthi, Srinadh Bhojanapalli, Anupam Gupta, Chulhee Yun. Position Coupling: Improving Length Generalization of Arithmetic Transformers Using Task Structure. *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*; arXiv:2405.20671. (**not cited in the draft**; verified: arXiv; DBLP conf/nips/0002CAB0Y24)  
   Coupling position ids of same-significance digits gives 30-to-200-digit addition (6.67x) with a 1-layer existence proof; it injects task structure through the architecture, as our certified pairs inject it through the loss, so a reviewer may argue the two encode the same knowledge.

13. Yongchao Zhou, Uri Alon, Xinyun Chen, Xuezhi Wang, Rishabh Agarwal, Denny Zhou. Transformers Can Achieve Length Generalization But Not Robustly. *arXiv preprint (2024); poster at the ME-FoMo 2024 workshop*; arXiv:2402.09371. (cited in the draft as [8]; verified: arXiv; OpenReview 'ME-FoMo 2024 Poster' (a workshop; no archival venue found))  
   With the right format and encoding, transformers reach 2.5x the training length on addition but vary strongly across seeds; it supports our emphasis on per-seed exactness and on fragility (already cited).

14. Hattie Zhou, Arwen Bradley, Etai Littwin, Noam Razin, Omid Saremi, Josh Susskind, Samy Bengio, Preetum Nakkiran. What Algorithms can Transformers Learn? A Study in Length Generalization. *ICLR 2024*; arXiv:2310.16028. (**not cited in the draft**; verified: arXiv; DBLP conf/iclr/ZhouBLRSSBN24)  
   Proposes that transformers length-generalise when a short RASP program solves the task at all lengths; it offers a rival, architecture-side explanation of which tasks extrapolate that a reviewer may use against our objective-side account.

15. Nayoung Lee, Kartik Sreenivasan, Jason D. Lee, Kangwook Lee, Dimitris Papailiopoulos. Teaching Arithmetic to Small Transformers. *ICLR 2024*; arXiv:2307.03381. (**not cited in the draft**; verified: arXiv; OpenReview 'ICLR 2024 poster')  
   Shows that simple formatting changes (in the paper's body, chiefly reversing the output digits) and intermediate-step data make arithmetic learnable by next-token training; it is a data-format remedy for the same failure and is consistent with T1, since the format changes what the loss can see.

16. Nayoung Lee, Ziyang Cai, Avi Schwarzschild, Kangwook Lee, Dimitris Papailiopoulos. Self-Improving Transformers Overcome Easy-to-Hard and Length Generalization Challenges. *ICML 2025*; arXiv:2502.01612. (**not cited in the draft**; verified: arXiv; OpenReview 'ICML 2025 poster')  
   Self-generated curricula take a standard transformer from 10-digit to 100-digit addition without changing the architecture; it pre-empts the claim that only a new objective can extend arithmetic far beyond training length and competes directly with our self-distillation (E14).

17. Łukasz Kaiser, Ilya Sutskever. Neural GPUs Learn Algorithms. *ICLR 2016*; arXiv:1511.08228. (**not cited in the draft**; verified: arXiv; OpenReview dblp record 'ICLR (Poster) 2016')  
   A convolutional gated-recurrent Neural GPU trained on binary numbers of up to 20 bits made no errors on much longer additions and multiplications; it shows extreme length generalisation by architecture alone and weakens any claim that exact long arithmetic is new.

## 3. Limits of next-token training and compounding error

18. Gregor Bachmann, Vaishnavh Nagarajan. The pitfalls of next-token prediction. *International Conference on Machine Learning (ICML) 2024*; arXiv:2403.06963. (**not cited in the draft**; verified: arXiv; DBLP conf/icml/BachmannN24)  
   Argues that teacher-forced next-token training can fail to learn an accurate predictor at all, beyond compounding at inference, and proposes teacherless objectives; it is the closest conceptual ally of T1, which turns the qualitative point into a bound for state, and leaving it uncited would read as an omission.

19. Stephane Ross, Geoffrey J. Gordon, J. Andrew Bagnell. A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning. *International Conference on Artificial Intelligence and Statistics (AISTATS) 2011, JMLR W&CP 15, 627–635*; arXiv:1011.0686. (**not cited in the draft**; verified: arXiv; DBLP journals/jmlr/RossGB11; S2 pages 627–635)  
   Shows that compounding error in sequential prediction comes from training on states the learner never visits and is removed by training on its own state distribution; our coverage result (E13) and 'trained on the states it will meet' are this insight, so it must be credited, and it partly pre-empts the claim that compounding is a property of the objective.

20. Samy Bengio, Oriol Vinyals, Navdeep Jaitly, Noam Shazeer. Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks. *Advances in Neural Information Processing Systems 28 (NIPS 2015)*; arXiv:1506.03099. (**not cited in the draft**; verified: arXiv; DBLP conf/nips/BengioVJS15)  
   Feeds the model's own predictions back during training to reduce exposure bias; it is an early training-side remedy for drift at length, related to our next-state term trained at length.

21. Alexander D'Amour, Katherine Heller, Dan Moldovan, Ben Adlam, Babak Alipanahi, Alex Beutel, Christina Chen, Jonathan Deaton, Jacob Eisenstein, Matthew D. Hoffman, Farhad Hormozdiari, Neil Houlsby, Shaobo Hou, Ghassen Jerfel, Alan Karthikesalingam, Mario Lucic, Yian Ma, Cory McLean, Diana Mincu, Akinori Mitani, Andrea Montanari, Zachary Nado, Vivek Natarajan, Christopher Nielson, Thomas F. Osborne, Rajiv Raman, Kim Ramasamy, Rory Sayres, Jessica Schrouff, Martin Seneviratne, Shannon Sequeira, Harini Suresh, Victor Veitch, Max Vladymyrov, Xuezhi Wang, Kellie Webster, Steve Yadlowsky, Taedong Yun, Xiaohua Zhai, D. Sculley. Underspecification Presents Challenges for Credibility in Modern Machine Learning. *Journal of Machine Learning Research 23(226), 1–61 (2022)*; arXiv:2011.03395. (**not cited in the draft**; verified: arXiv; jmlr.org/papers/v23/20-1335.html citation metadata (JMLR issues no DOIs); DBLP journals/jmlr/DAmourHMAABCDEH22)  
   Shows that ML pipelines return many predictors with equivalent held-out performance that behave very differently in deployment (underspecification), across vision, NLP, medical imaging and genomics; T1 is a sequence-model instance with a mechanism (next-token loss cannot separate a drifting tracker from the exact one) and the certified signal is the missing specification.

## 4. World models and the Nerode lens

22. A. Nerode. Linear automaton transformations. *Proceedings of the American Mathematical Society 9(4), 541–544 (1958)*; doi:10.1090/S0002-9939-1958-0135681-9. (cited in the draft as [34]; verified: Crossref)  
   Defines the right-congruence whose classes form the minimal automaton, the object T4 identifies as the joint minimiser (already cited).

23. Keyon Vafa, Justin Y. Chen, Ashesh Rambachan, Jon Kleinberg, Sendhil Mullainathan. Evaluating the World Model Implicit in a Generative Model. *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*; arXiv:2406.03689. (cited in the draft as [55]; verified: arXiv; DBLP conf/nips/VafaCRKM24)  
   Uses Myhill-Nerode metrics to show that generative models with good next-token accuracy hold incoherent world models; it pre-empts the Nerode lens on sequence models, and our contribution is the converse step, training with Nerode equivalences and proving why likelihood leaves the incoherence (already cited).

24. Kenneth Li, Aspen K. Hopkins, David Bau, Fernanda Viégas, Hanspeter Pfister, Martin Wattenberg. Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task. *ICLR 2023*; arXiv:2210.13382. (cited in the draft as [56]; verified: arXiv comment 'ICLR 2023 oral (notable-top-5%)'; OpenReview 'ICLR 2023')  
   Next-token training on Othello yields a board state recoverable by non-linear probes; it is the standard evidence that likelihood alone learns state, against which we argue that approximate state at training length is not exact state at length (already cited).

25. Neel Nanda, Andrew Lee, Martin Wattenberg. Emergent Linear Representations in World Models of Self-Supervised Sequence Models. *BlackboxNLP Workshop on Analyzing and Interpreting Neural Networks for NLP (at EMNLP 2023), 16–30*; arXiv:2309.00941. (**not cited in the draft**; verified: arXiv; OpenReview dblp record 'BlackboxNLP@EMNLP 2023'; S2 pages)  
   Finds the Othello board linearly in 'mine/theirs' coordinates and steers the model with it; it strengthens the counter-position that next-token training finds world state, so it should be cited beside Li et al. with the same exactness-at-length contrast.

## 5. Automata learning and minimal realisation

26. Dana Angluin. Learning regular sets from queries and counterexamples. *Information and Computation 75(2), 87–106 (1987)*; doi:10.1016/0890-5401(87)90052-6. (**not cited in the draft**; verified: Crossref; DBLP journals/iandc/Angluin87)  
   L* learns the minimal automaton in polynomial time from membership and equivalence queries; our checker plays an equivalence oracle on pairs of histories and T4's minimiser is L*'s target, so a reviewer will call the recipe 'gradient-based L*' unless the paper says how it differs (no hypothesis queries, a continuous state, length exactness under closure).

27. Gail Weiss, Yoav Goldberg, Eran Yahav. Extracting Automata from Recurrent Neural Networks Using Queries and Counterexamples. *ICML 2018*; arXiv:1711.09576. (cited in the draft as [11]; verified: arXiv journal_ref 'ICML 2018'; DBLP conf/icml/WeissGY18)  
   Uses L* with a trained RNN as the teacher to extract automata; it is the extraction counterpart of our training-time use of equivalences (already cited).

28. Daniel Hsu, Sham M. Kakade, Tong Zhang. A Spectral Algorithm for Learning Hidden Markov Models. *Journal of Computer and System Sciences 78(5), 1460–1480 (2012)*; arXiv:0811.4413. (**not cited in the draft**; verified: arXiv journal_ref; S2)  
   A provably correct spectral algorithm for learning hidden Markov models, with sample complexity governed by the model's spectral properties; a non-gradient route to a predictive state that a reviewer may ask us to compare with.

29. Borja Balle, Xavier Carreras, Franco M. Luque, Ariadna Quattoni. Spectral learning of weighted automata: A forward-backward perspective. *Machine Learning 96(1–2), 33–63 (2014; online 2013)*; doi:10.1007/s10994-013-5416-x. (**not cited in the draft**; verified: Crossref (published-print 2014-07, online 2013-10-03))  
   Derives the spectral method for learning weighted automata (per its record, an expository derivation stressing intuition); the same non-gradient comparison as spectral HMMs, from the automata side.

30. B. L. Ho, R. E. Kalman. Effective construction of linear state-variable models from input/output functions. *at – Automatisierungstechnik (Crossref container) 14, 545–548 (1966)*; doi:10.1524/auto.1966.14.112.545. (**not cited in the draft**; verified: Crossref; record carries an 'Editorial:' title prefix and a Greek capital Beta in the first initial, both corrected here)  
   The classical construction of minimal realisations of linear state-variable systems from input-output data; the linear-systems antecedent of 'the minimal state is determined by behaviour'.

## 6. Computational mechanics and predictive state representations

31. James P. Crutchfield, Karl Young. Inferring statistical complexity. *Physical Review Letters 63(2), 105–108 (1989)*; doi:10.1103/PhysRevLett.63.105. (**not cited in the draft**; verified: Crossref)  
   Reconstructs minimal models of a process from the recursive structure of its measurement sequences and defines statistical complexity; its states (later named causal states: pasts with the same conditional future) are the stochastic counterpart of Nerode classes, so 'the state is the minimal predictive quotient' predates us.

32. Cosma Rohilla Shalizi, James P. Crutchfield. Computational Mechanics: Pattern and Prediction, Structure and Simplicity. *Journal of Statistical Physics 104, 817–879 (2001)*; arXiv:cond-mat/9907176. (**not cited in the draft**; verified: arXiv journal_ref; S2 journal record (pages 817–879; arXiv journal_ref says 816–879))  
   Proves the causal-state partition is the unique minimal sufficient statistic for prediction; it pre-empts the theory half of 'the target is the minimal predictive state', leaving the training signal and the length guarantee as our contribution.

33. Michael L. Littman, Richard S. Sutton, Satinder P. Singh. Predictive Representations of State. *Advances in Neural Information Processing Systems 14 (NIPS 2001)*. (**not cited in the draft**; verified: S2 record with DBLP conf/nips/LittmanSS01; OpenReview dblp record 'NIPS 2001'; no DOI or arXiv id exists (REACH.md's '2002' is the proceedings-year citation))  
   Predictive state representations define state as predictions of future tests, so histories with equal predictions are equivalent; it is the RL form of predictive (Nerode) equivalence.

34. Satinder Singh, Michael James, Matthew Rudary. Predictive State Representations: A New Theory for Modeling Dynamical Systems. *Conference on Uncertainty in Artificial Intelligence (UAI) 2004, 512–518*; arXiv:1207.4167. (**not cited in the draft**; verified: arXiv; S2 venue and pages)  
   Develops the theory of PSRs, which represent state as predictions of the outcomes of experiments and are closely related to observable-operator models; theory of state from predictive equivalence, without any length-exactness guarantee.

35. Byron Boots, Sajid M. Siddiqi, Geoffrey J. Gordon. Closing the Learning-Planning Loop with Predictive State Representations. *The International Journal of Robotics Research 30(7), 954–966 (2011)*; arXiv:0912.2385. (**not cited in the draft**; verified: arXiv; DBLP journals/ijrr/BootsSG11; S2 journal record)  
   Learns a predictive-state model directly from action-observation sequences and plans in it to a near-optimal policy; practical evidence that a predictive state can be learned, with no claim about exactness over long horizons.

36. Adam S. Shai, Sarah E. Marzen, Lucas Teixeira, Alexander Gietelink Oldenziel, Paul M. Riechers. Transformers represent belief state geometry in their residual stream. *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*; arXiv:2405.15943. (**not cited in the draft**; verified: arXiv; DBLP conf/nips/ShaiTOMR24)  
   Transformers trained only on next-token prediction linearly represent belief-state geometry, including fractal geometry predicted by computational mechanics; it is in tension with the blindness claim, and the answer is that belief geometry at the training length does not guarantee exact state at length.

## 7. Bisimulation, value equivalence and self-predictive reinforcement learning

37. Robert Givan, Thomas Dean, Matthew Greig. Equivalence notions and model minimization in Markov decision processes. *Artificial Intelligence 147(1–2), 163–223 (2003)*; doi:10.1016/S0004-3702(02)00376-4. (**not cited in the draft**; verified: Crossref; DBLP journals/ai/GivanDG03)  
   Defines stochastic bisimulation as MDP model minimisation; our three clauses are the bisimulation conditions applied to histories, so it should be cited as the formal antecedent of 'merge equivalent states into the minimal model'.

38. Norman Ferns, Prakash Panangaden, Doina Precup. Metrics for Finite Markov Decision Processes. *Conference on Uncertainty in Artificial Intelligence (UAI) 2004*; arXiv:1207.4114. (cited in the draft as [22]; verified: arXiv comment 'Appears in Proceedings of the Twentieth Conference on Uncertainty in Artificial Intelligence (UAI2004)'; S2 maps the id to a two-page AAAI 2004 abstract of the same title)  
   Bisimulation metrics turn state equivalence into a distance; our certified-pair distance is a sampled, checker-supervised version (already cited).

39. Carles Gelada, Saurabh Kumar, Jacob Buckman, Ofir Nachum, Marc G. Bellemare. DeepMDP: Learning Continuous Latent Space Models for Representation Learning. *ICML 2019*; arXiv:1906.02736. (**not cited in the draft**; verified: arXiv; DBLP conf/icml/GeladaKBNB19)  
   Trains a latent model by predicting reward and the next latent state and proves bisimulation-style guarantees; it pre-empts the first two clauses of our recipe in RL, and our additions are external certified pairs, closure and exactness at length.

40. Amy Zhang, Rowan McAllister, Roberto Calandra, Yarin Gal, Sergey Levine. Learning Invariant Representations for Reinforcement Learning without Reconstruction. *ICLR 2021*; arXiv:2006.10742. (cited in the draft as [23]; verified: arXiv; DBLP conf/iclr/0001MCGL21)  
   Learns representations whose distances match bisimulation distances; a direct relative of the equivalence term, without checker supervision or length claims (already cited).

41. Pablo Samuel Castro, Tyler Kastner, Prakash Panangaden, Mark Rowland. MICo: Improved representations via sampling-based state similarity for Markov decision processes. *Advances in Neural Information Processing Systems 34 (NeurIPS 2021)*; arXiv:2106.08229. (cited in the draft as [24]; verified: arXiv; DBLP conf/nips/CastroKPR21)  
   A sampling-based bisimulation-like distance for learned representations (already cited).

42. Jayakumar Subramanian, Amit Sinha, Raihan Seraj, Aditya Mahajan. Approximate information state for approximate planning and reinforcement learning in partially observed systems. *Journal of Machine Learning Research (2022)*; arXiv:2010.08843. (**not cited in the draft**; verified: arXiv; OpenReview dblp record 'J. Mach. Learn. Res. 2022')  
   Defines an (approximate) information state as a function of history sufficient to predict reward and its own next value, with loss bounds; it is our 'predict the output, predict the next state' pair in POMDP form and pre-empts T5's framing, so it should be cited where T5 is stated.

43. Max Schwarzer, Ankesh Anand, Rishab Goel, R Devon Hjelm, Aaron Courville, Philip Bachman. Data-Efficient Reinforcement Learning with Self-Predictive Representations. *ICLR 2021*; arXiv:2007.05929. (cited in the draft as [27]; verified: arXiv; DBLP conf/iclr/SchwarzerAGHCB21)  
   Self-predictive representations predict their own future latents for data-efficient RL; the origin of our next-state term (already cited).

44. Yunhao Tang, Zhaohan Daniel Guo, Pierre Harvey Richemond, Bernardo Ávila Pires, Yash Chandak, Rémi Munos, Mark Rowland, Mohammad Gheshlaghi Azar, Charline Le Lan, Clare Lyle, András György, Shantanu Thakoor, Will Dabney, Bilal Piot, Daniele Calandriello, Michal Valko. Understanding Self-Predictive Learning for Reinforcement Learning. *ICML 2023*; arXiv:2212.03319. (cited in the draft as [57]; verified: arXiv; DBLP conf/icml/TangGRPCMRALL0T23)  
   Explains how self-predictive objectives avoid collapse through optimisation dynamics; relevant to our readout criterion (T6), which gives a different, architectural condition against collapse (already cited).

45. Tianwei Ni, Benjamin Eysenbach, Erfan Seyedsalehi, Michel Ma, Clement Gehring, Aditya Mahajan, Pierre-Luc Bacon. Bridging State and History Representations: Understanding Self-Predictive RL. *ICLR 2024*; arXiv:2401.08898. (cited in the draft as [28]; verified: arXiv; DBLP conf/iclr/NiESMGMB24)  
   Unifies state and history abstractions as self-predictive; the closest RL theory, and our answer is that self-prediction alone has class-splitting zeros (T5) that certified pairs remove (already cited).

46. Christopher Grimm, André Barreto, Satinder Singh, David Silver. The Value Equivalence Principle for Model-Based Reinforcement Learning. *Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*; arXiv:2011.03506. (**not cited in the draft**; verified: arXiv; DBLP conf/nips/GrimmBSS20)  
   Value equivalence calls two models equivalent when they give the same Bellman updates for chosen policies and functions; it is a task-defined equivalence that contrasts with our checker-certified one, and a reviewer from model-based RL will expect it.

47. Christopher Grimm, André Barreto, Gregory Farquhar, David Silver, Satinder Singh. Proper Value Equivalence. *Advances in Neural Information Processing Systems 34 (NeurIPS 2021)*; arXiv:2106.10316. (**not cited in the draft**; verified: arXiv journal_ref 'NeurIPS 2021'; DBLP conf/nips/GrimmBFSS21)  
   Shows the set of value-equivalent models shrinks to the true model as policies and functions are added; the analogue of our result that enough certified pairs leave only the minimal automaton.

48. Julian Schrittwieser, Ioannis Antonoglou, Thomas Hubert, Karen Simonyan, Laurent Sifre, Simon Schmitt, Arthur Guez, Edward Lockhart, Demis Hassabis, Thore Graepel, Timothy Lillicrap, David Silver. Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model. *Nature 588, 604–609 (2020)*; arXiv:1911.08265. (**not cited in the draft**; verified: arXiv; DBLP journals/nature/SchrittwieserAH20; S2 journal record)  
   Plans with a learned model that predicts only the quantities relevant to planning (reward, policy and value), with no requirement that its latents match a true state; the canonical case of predictive latents without state exactness, useful for the world-model paragraph.

49. Danijar Hafner, Jurgis Pasukonis, Jimmy Ba, Timothy Lillicrap. Mastering Diverse Domains through World Models. *Nature 640(8059), 647–653 (2025), published as "Mastering diverse control tasks through world models"*; arXiv:2301.04104; doi:10.1038/s41586-025-08744-2. (**not cited in the draft**; verified: arXiv; Crossref (Nature version, doi:10.1038/s41586-025-08744-2))  
   Learns a recurrent world model and acts by imagined latent rollouts across many domains; long imagined rollouts are where drift bites, so it is the natural RL application a reviewer will name.

## 8. Latent reasoning and Markov chain of thought

50. Shibo Hao, Sainbayar Sukhbaatar, DiJia Su, Xian Li, Zhiting Hu, Jason Weston, Yuandong Tian. Training Large Language Models to Reason in a Continuous Latent Space. *Conference on Language Modeling (COLM) 2025*; arXiv:2412.06769. (cited in the draft as [49]; verified: arXiv comment 'Accepted to COLM 2025'; OpenReview 'COLM 2025')  
   Feeds the last hidden state back as a continuous thought instead of tokens; reasoning without words but with no guarantee at length (already cited).

51. Milad Aghajohari, Kamran Chitsaz, Amirhossein Kazemnejad, Sarath Chandar, Alessandro Sordoni, Aaron Courville, Siva Reddy. The Markovian Thinker: Architecture-Agnostic Linear Scaling of Reasoning. *arXiv preprint (2025)*; arXiv:2510.06557. (cited in the draft as [41]; verified: arXiv; no accepted venue on OpenReview or S2)  
   Reasoning in fixed-size chunks with a short carried-over textual state gives linear compute; it pre-empts the 'read only the last state' Markov control (HOLD), whose distinct contribution must be exactness at length and the coverage diagnosis (already cited).

52. Jayden Teoh, Manan Tomar, Kwangjun Ahn, Edward S. Hu, Tim Pearce, Pratyusha Sharma, Akshay Krishnamurthy, Riashat Islam, Alex Lamb, John Langford. Next-Latent Prediction Transformers Learn Compact World Models. *arXiv preprint (2025); PLAN-FM Bridge workshop at AAAI 2026*; arXiv:2511.05963. (cited in the draft as [29]; verified: arXiv comment 'Microsoft Research Preprint'; OpenReview 'PLAN-FM Bridge @ AAAI 2026' (a workshop))  
   Next-latent prediction makes transformer latents converge to belief states; it is our next-state clause on a transformer, and the paper already notes it extrapolates far on proof chains, so the certified signal must be shown to add exactness beyond it (already cited).

53. Yuntian Deng, Yejin Choi, Stuart Shieber. From Explicit CoT to Implicit CoT: Learning to Internalize CoT Step by Step. *arXiv preprint (2024)*; arXiv:2405.14838. (cited in the draft as [48]; verified: arXiv; OpenReview shows only an ICLR 2025 submission, not an acceptance)  
   Internalises chain of thought by gradually removing steps; token-free reasoning without a length guarantee (already cited).

54. Jonas Geiping, Sean McLeish, Neel Jain, John Kirchenbauer, Siddharth Singh, Brian R. Bartoldson, Bhavya Kailkhura, Abhinav Bhatele, Tom Goldstein. Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach. *Advances in Neural Information Processing Systems 38 (NeurIPS 2025), spotlight*; arXiv:2502.05171. (**not cited in the draft**; verified: arXiv; OpenReview 'NeurIPS 2025 spotlight')  
   A 3.5B-parameter model reasons by iterating a recurrent block in latent space at test time; the large-scale latent-recurrence alternative a reviewer will raise against 'small recurrent module beside a frozen model'.

## 9. Context distillation

55. Amanda Askell, Yuntao Bai, Anna Chen, Dawn Drain, Deep Ganguli, Tom Henighan, Andy Jones, Nicholas Joseph, Ben Mann, Nova DasSarma, Nelson Elhage, Zac Hatfield-Dodds, Danny Hernandez, Jackson Kernion, Kamal Ndousse, Catherine Olsson, Dario Amodei, Tom Brown, Jack Clark, Sam McCandlish, Chris Olah, Jared Kaplan. A General Language Assistant as a Laboratory for Alignment. *arXiv preprint (2021)*; arXiv:2112.00861. (**not cited in the draft**; verified: arXiv; S2 (no venue))  
   Introduces context distillation, training a model without a prompt to match its own prompted behaviour (the abstract does not name it; the attribution is the citing literature's, 89 contexts on Semantic Scholar); the origin of the method our self-distillation (E14) specialises.

56. Charlie Snell, Dan Klein, Ruiqi Zhong. Learning by Distilling Context. *arXiv preprint (2022)*; arXiv:2209.15189. (**not cited in the draft**; verified: arXiv; no venue on OpenReview or S2)  
   Context distillation internalises instructions and scratchpads into weights; our in-model self-distillation pulls predictions after a long history to those after a certified short equivalent, i.e. certified context distillation, so it partly pre-empts E14's mechanism.

## 10. Contrastive invariance

57. Beatrice Bevilacqua, Kyriacos Nikiforou, Borja Ibarz, Ioana Bica, Michela Paganini, Charles Blundell, Jovana Mitrovic, Petar Veličković. Neural Algorithmic Reasoning with Causal Regularisation. *ICML 2023, 2272–2288*; arXiv:2302.10258. (cited in the draft as [33]; verified: arXiv comment 'ICML 2023, Camera Ready'; OpenReview 'ICML 2023 Poster'; S2 pages)  
   Hint-ReLIC makes a neural algorithmic reasoner's next-step prediction invariant across inputs on which the algorithm takes the same step and improves out-of-distribution size generalisation; the closest prior method, relating inputs one step at a time where we relate whole certified histories (already cited as causal regularisation).

58. Jovana Mitrovic, Brian McWilliams, Jacob Walker, Lars Buesing, Charles Blundell. Representation Learning via Invariant Causal Mechanisms. *ICLR 2021*; arXiv:2010.07922. (**not cited in the draft**; verified: arXiv; OpenReview 'ICLR 2021 Poster')  
   ReLIC enforces invariant predictions across augmentations with an explicit invariance penalty; the generic objective of which our equivalence term is a history-level, checker-defined instance.

59. Paras Jain, Ajay Jain, Tianjun Zhang, Pieter Abbeel, Joseph E. Gonzalez, Ion Stoica. Contrastive Code Representation Learning. *Conference on Empirical Methods in Natural Language Processing (EMNLP) 2021, 5954–5971*; arXiv:2007.04973. (**not cited in the draft**; verified: arXiv; DBLP conf/emnlp/0001JZA0S21; S2 pages)  
   Contrastive pre-training over compiler-generated semantically equivalent programs; checker-certified program equivalence as a training signal predates us, for representations rather than for exact state at length.

## 11. Reliable computation and error correction

60. J. von Neumann. Probabilistic Logics and the Synthesis of Reliable Organisms From Unreliable Components. *In Automata Studies (AM-34), 43–98. Princeton University Press (1956)*; doi:10.1515/9781400882618-003. (**not cited in the draft**; verified: Crossref (book chapter); no arXiv id)  
   Restoring organs built from majority voting make reliable computation from unreliable components possible below an error threshold; our repair equilibrium (T7, T9) is a learned restoring organ, and the analogy is ours to state.

61. Johannes Bausch, Andrew W. Senior, Francisco J. H. Heras, Thomas Edlich, Alex Davies, Michael Newman, Cody Jones, Kevin Satzinger, Murphy Yuezhen Niu, Sam Blackwell, George Holland, Dvir Kafri, Juan Atalaya, Craig Gidney, Demis Hassabis, Sergio Boixo, Hartmut Neven, Pushmeet Kohli. Learning high-accuracy error decoding for quantum processors. *Nature 635(8040), 834–840 (2024)*; arXiv:2310.05900; doi:10.1038/s41586-024-08148-8. (**not cited in the draft**; verified: Crossref; arXiv journal_ref 'Nature 635, 834-840 (2024)' (arXiv title: 'Learning to Decode the Surface Code with a Recurrent, Transformer-Based Neural Network'))  
   A recurrent, transformer-based decoder for the surface code; the arXiv version reports that it sustains its accuracy far beyond the 25 cycles it was trained on, which is learned state tracking that extrapolates in length in a domain with an exact checker, so it is both support and prior art (REACH's figure of up to 100,000 rounds appears in neither abstract and was not checked).

## 12. Neural simulators and rollout stability

62. Alvaro Sanchez-Gonzalez, Jonathan Godwin, Tobias Pfaff, Rex Ying, Jure Leskovec, Peter W. Battaglia. Learning to Simulate Complex Physics with Graph Networks. *ICML 2020*; arXiv:2002.09405. (**not cited in the draft**; verified: arXiv comment 'Accepted at ICML 2020'; OpenReview dblp record 'ICML 2020')  
   Injecting noise into training inputs keeps graph-network simulators stable over long rollouts; a training-side repair of drift that our theory would read as forced contraction.

63. Johannes Brandstetter, Daniel Worrall, Max Welling. Message Passing Neural PDE Solvers. *ICLR 2022*; arXiv:2202.03376. (**not cited in the draft**; verified: arXiv; DBLP conf/iclr/BrandstetterWW22)  
   Poses the stability of autoregressive neural PDE solvers as domain adaptation (the 'pushforward trick' of the paper's body, training on the model's own predicted inputs); next-state prediction at length by another name, so the physics claims (E15) must be compared with it.

64. Phillip Lippe, Bastiaan S. Veeling, Paris Perdikaris, Richard E. Turner, Johannes Brandstetter. PDE-Refiner: Achieving Accurate Long Rollouts with Neural PDE Solvers. *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*; arXiv:2308.05732. (**not cited in the draft**; verified: arXiv; DBLP conf/nips/LippeVPTB23)  
   Locates long-rollout failure of neural PDE solvers in neglected high-frequency content and fixes it with iterative refinement; a rival diagnosis of drift that a physics reviewer will set beside T1.

65. Dmitrii Kochkov, Janni Yuval, Ian Langmore, Peter Norgaard, Jamie Smith, Griffin Mooers, Milan Klöwer, James Lottes, Stephan Rasp, Peter Düben, Sam Hatfield, Peter Battaglia, Alvaro Sanchez-Gonzalez, Matthew Willson, Michael P. Brenner, Stephan Hoyer. Neural general circulation models for weather and climate. *Nature 632(8027), 1060–1066 (2024)*; arXiv:2311.07222; doi:10.1038/s41586-024-07744-y. (**not cited in the draft**; verified: Crossref; DBLP journals/nature/KochkovYLNSMKLRDHBSWBH24)  
   A hybrid of a differentiable dynamical core and learned physics tracks climate metrics for multiple decades; closure supplied by physics, a strong comparison for T13 and E15.

66. Oliver Watt-Meyer, Gideon Dresdner, Jeremy McGibbon, Spencer K. Clark, Brian Henn, James Duncan, Noah D. Brenowitz, Karthik Kashinath, Michael S. Pritchard, Boris Bonev, Matthew E. Peters, Christopher S. Bretherton. ACE: A fast, skillful learned global atmospheric model for climate prediction. *arXiv preprint (2023); Tackling Climate Change with Machine Learning workshop at NeurIPS 2023*; arXiv:2310.02074. (**not cited in the draft**; verified: arXiv comment 'Accepted at Tackling Climate Change with Machine Learning: workshop at NeurIPS 2023')  
   A purely learned atmospheric emulator stays stable for 100 years and nearly conserves moisture without explicit constraints; it weakens any claim that one-step-trained surrogates must drift, and E15 should say what differs.

67. Sam Greydanus, Misko Dzamba, Jason Yosinski. Hamiltonian Neural Networks. *Advances in Neural Information Processing Systems 32 (NeurIPS 2019)*; arXiv:1906.01563. (**not cited in the draft**; verified: arXiv; DBLP conf/nips/GreydanusDY19)  
   Learns a Hamiltonian so that energy is conserved by construction; closure onto the energy shell by architecture, the case T13 says cannot be repaired by an objective.

## 13. Turing completeness and universal computation

68. H.T. Siegelmann, E.D. Sontag. On the Computational Power of Neural Nets. *Journal of Computer and System Sciences 50(1), 132–150 (1995)*; doi:10.1006/jcss.1995.1013. (**not cited in the draft**; verified: Crossref)  
   Recurrent networks with rational weights are Turing complete (no abstract was retrievable; this is the standard statement of its result); expressivity is not the bottleneck, which is why our claims concern selection by the objective rather than representability.

69. Jorge Pérez, Javier Marinković, Pablo Barceló. On the Turing Completeness of Modern Neural Network Architectures. *ICLR 2019*; arXiv:1901.03429. (**not cited in the draft**; verified: arXiv; DBLP conf/iclr/PerezMB19 (the journal version, 'Attention is Turing-complete', JMLR 2021, was not verifiable here: JMLR issues no DOIs))  
   Transformers and the Neural GPU are Turing complete with arbitrary-precision internal representations; same role as Siegelmann and Sontag for attention models.

70. Dale Schuurmans. Memory Augmented Large Language Models are Computationally Universal. *arXiv preprint (2023)*; arXiv:2301.04589. (**not cited in the draft**; verified: arXiv; no venue on OpenReview or S2)  
   An unmodified 540B language model with an external read-write memory exactly simulates a universal Turing machine; exactness achieved by moving state into an exact external store, the alternative to our learned latent state.

71. Dale Schuurmans, Hanjun Dai, Francesco Zanini. Autoregressive Large Language Models are Computationally Universal. *arXiv preprint (2024)*; arXiv:2410.03170. (**not cited in the draft**; verified: arXiv; OpenReview has only the dblp CoRR record)  
   Shows that extended autoregressive decoding is computationally universal via Lag systems; formal support for chain of thought as computation, which our E2 compares against empirically.

72. Kaiying Hou, David Brandfonbrener, Sham Kakade, Samy Jelassi, Eran Malach. Universal Length Generalization with Turing Programs. *ICML 2025*; arXiv:2407.03310. (**not cited in the draft**; verified: arXiv; OpenReview 'ICML 2025 poster')  
   A chain-of-thought format that mimics a Turing machine's tape gives robust length generalisation on algorithmic tasks; it weakens the general claim that chain of thought fails beyond the training length, so E2 should be stated as a result about whole-history chain of thought.

## 14. Cognitive maps: TEM and CSCG

73. James C.R. Whittington, Timothy H. Muller, Shirley Mark, Guifen Chen, Caswell Barry, Neil Burgess, Timothy E.J. Behrens. The Tolman-Eichenbaum Machine: Unifying Space and Relational Memory through Generalization in the Hippocampal Formation. *Cell 183(5), 1249–1263.e23 (2020)*; doi:10.1016/j.cell.2020.10.024. (**not cited in the draft**; verified: Crossref; PubMed 33181068)  
   Separates a learned structural basis (entorhinal cells resembling grid, band and border cells) from its bindings to sensory input (hippocampal place and landmark cells) and transfers structure across environments; the neuroscience instance of 'state from structure plus loop closure' that REACH draws on.

74. Dileep George, Rajeev V. Rikhye, Nishad Gothoskar, J. Swaroop Guntupalli, Antoine Dedieu, Miguel Lázaro-Gredilla. Clone-structured graph representations enable flexible learning and vicarious evaluation of cognitive maps. *Nature Communications 12, 2392 (2021)*; doi:10.1038/s41467-021-22559-5. (**not cited in the draft**; verified: Crossref (article number 2392))  
   Learns cognitive maps whose hidden states are context-specific clones of each observation, separating or merging aliased observations with a probabilistic sequence model; a learned latent automaton in cognitive mapping, without our length claims.

75. James C. R. Whittington, Joseph Warren, Timothy E. J. Behrens. Relating transformers to models and neural representations of the hippocampal formation. *ICLR 2022*; arXiv:2112.04035. (**not cited in the draft**; verified: arXiv; OpenReview 'ICLR 2022 Poster')  
   Transformers with recurrent position encodings reproduce hippocampal place and grid cells and relate to TEM; the bridge from TEM to transformer state, relevant if the paper links exact state to cognitive maps.

## 15. What large language models get wrong (for the introduction)

76. Nouha Dziri, Ximing Lu, Melanie Sclar, Xiang Lorraine Li, Liwei Jiang, Bill Yuchen Lin, Peter West, Chandra Bhagavatula, Ronan Le Bras, Jena D. Hwang, Soumya Sanyal, Sean Welleck, Xiang Ren, Allyson Ettinger, Zaid Harchaoui, Yejin Choi. Faith and Fate: Limits of Transformers on Compositionality. *Advances in Neural Information Processing Systems 36 (NeurIPS 2023), spotlight*; arXiv:2305.18654. (cited in the draft as [16]; verified: arXiv; OpenReview 'NeurIPS 2023 spotlight')  
   Shows that transformer LLMs (GPT-3, ChatGPT, GPT-4) fail on multi-digit multiplication, logic grid puzzles and a dynamic-programming task, with accuracy falling to near zero as problem size grows (body, section 2), and argues they match linearised subgraphs rather than compose; the standard citation for compositional arithmetic failure.

77. R. Thomas McCoy, Shunyu Yao, Dan Friedman, Mathew D. Hardy, Thomas L. Griffiths. Embers of autoregression show how large language models are shaped by the problem they are trained to solve. *Proceedings of the National Academy of Sciences 121(41) (2024)*; arXiv:2309.13638; doi:10.1073/pnas.2322420121. (**not cited in the draft**; verified: Crossref doi:10.1073/pnas.2322420121 (published title differs from the arXiv preprint 2309.13638))  
   Shows that GPT-3.5 and GPT-4 accuracy on deterministic tasks tracks the probability of the task, input and output; in counting characters or words in a list (body, section 6.6) GPT-4 is far more accurate when the count is a common number (e.g. 100) than a rare one (e.g. 83); the strongest peer-reviewed evidence for LLM counting failures.

78. Yingshan Chang, Yonatan Bisk. Language Models Need Inductive Biases to Count Inductively. *ICLR 2025*; arXiv:2405.20131. (**not cited in the draft**; verified: arXiv; DBLP conf/iclr/ChangB25; OpenReview 'ICLR 2025 Poster')  
   Trains RNNs, transformers, state-space models and RWKV to count and finds that traditional RNNs count inductively while transformers need positional embeddings to count out of domain and modern RNNs underperform traditional ones; peer-reviewed counting-generalisation evidence for trained models, close to our counting task (E6).

79. Gilad Yehudai, Haim Kaplan, Guy Dar, Royi Rassin, Asma Ghandeharioun, Mor Geva, Amir Globerson. When Can Transformers Count to n?. *Conference on Uncertainty in Artificial Intelligence (UAI) 2026*; arXiv:2407.15160. (**not cited in the draft**; verified: OpenReview 'UAI 2026 Poster' (earlier rejected at ICLR 2025); arXiv)  
   Proves that a transformer keeps exact token counts only when its embedding dimension is at least the vocabulary size, shows catastrophic out-of-distribution failure beyond that when training from scratch, and reports similar failures in pretrained models; theoretical support for counting failures.

80. Tairan Fu, Raquel Ferrando, Javier Conde, Carlos Arriaga, Pedro Reviriego. Why Do Large Language Models (LLMs) Struggle to Count Letters?. *arXiv preprint (2024)*; arXiv:2412.18626. (**not cited in the draft**; verified: arXiv; no venue on Semantic Scholar, DBLP (CoRR only) or OpenReview)  
   Measures letter-counting errors across many LLMs (the 'r' in 'strawberry'): models recognise the letters but miscount, errors grow with the number of repeated letters, and word frequency does not explain them; the closest study of character counting, but a preprint only.

81. Najoung Kim, Sebastian Schuster. Entity Tracking in Language Models. *Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), 3835–3855 (2023)*; arXiv:2305.02363; doi:10.18653/v1/2023.acl-long.213. (cited in the draft as [20]; verified: Crossref doi:10.18653/v1/2023.acl-long.213; arXiv comment 'ACL 2023 Camera-ready')  
   With a probe that asks for an entity's final state after a series of described state-changing operations, finds that only GPT-3.5 models pretrained on code track entity state, not Flan-T5 or GPT-3, and that a fine-tuned T5 degrades on harder splits; the standard citation for entity and state tracking in text, and the task our stories domain (E7) certifies.

82. Kiran Vodrahalli, Santiago Ontanon, Nilesh Tripuraneni, Kelvin Xu, Sanil Jain, Rakesh Shivanna, Jeffrey Hui, Nishanth Dikkala, Mehran Kazemi, Bahare Fatemi, Rohan Anil, Ethan Dyer, Siamak Shakeri, Roopali Vij, Harsh Mehta, Vinay Ramasesh, Quoc Le, Ed Chi, Yifeng Lu, Orhan Firat, Angeliki Lazaridou, Jean-Baptiste Lespiau, Nithya Attaluri, Kate Olszewska. Michelangelo: Long Context Evaluations Beyond Haystacks via Latent Structure Queries. *arXiv preprint (2024)*; arXiv:2409.12640. (**not cited in the draft**; verified: arXiv; Semantic Scholar, DBLP (CoRR) and OpenReview give no venue)  
   Introduces Latent Structure Queries, including Latent List (a Python list changed by a long sequence of operations, then queried), and finds that frontier models' scores drop sharply already within 32K tokens of context (body, sections 2.1 and 5.2); evidence that long-context state tracking fails, and Latent List is the closest public analogue of our code-execution domain (E1).

83. Gladys Tyen, Hassan Mansoor, Victor Carbune, Peter Chen, Tony Mak. LLMs cannot find reasoning errors, but can correct them given the error location. *Findings of the Association for Computational Linguistics: ACL 2024, 13894–13908*; arXiv:2311.08516; doi:10.18653/v1/2024.findings-acl.826. (**not cited in the draft**; verified: Crossref doi:10.18653/v1/2024.findings-acl.826; arXiv comment 'ACL 2024 Findings')  
   Benchmarks LLMs on locating the first logical mistake in chain-of-thought traces (BIG-Bench Mistake) and finds they generally fail even in unambiguous cases, while they correct well once told where the mistake is; a motivation for certificates that come from outside the model.

84. Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou. Large Language Models Cannot Self-Correct Reasoning Yet. *ICLR 2024*; arXiv:2310.01798. (**not cited in the draft**; verified: arXiv comment 'ICLR 2024'; DBLP conf/iclr/0009CMZYSZ24; OpenReview 'ICLR 2024 poster')  
   Shows that intrinsic self-correction, without external feedback, does not improve and often degrades LLM reasoning; with Tyen et al. it supports the claim that models cannot police their own errors.

85. Thomas Kwa, Ben West, Joel Becker, Amy Deng, Katharyn Garcia, Max Hasin, Sami Jawhar, Megan Kinniment, Nate Rush, Sydney Von Arx, Ryan Bloom, Thomas Broadley, Haoxing Du, Brian Goodrich, Nikola Jurkovic, Luke Harold Miles, Seraphina Nix, Tao Lin, Chris Painter, Neev Parikh, David Rein, Lucas Jun Koba Sato, Hjalmar Wijk, Daniel M. Ziegler, Elizabeth Barnes, Lawrence Chan. Measuring AI Ability to Complete Long Software Tasks. *Advances in Neural Information Processing Systems 38 (NeurIPS 2025)*; arXiv:2503.14499. (**not cited in the draft**; verified: arXiv journal_ref 'NeurIPS 2025'; DBLP conf/nips/KwaWBDGHJKRABBD25; OpenReview 'NeurIPS 2025 poster')  
   Defines the 50%-task-completion time horizon and finds that agents' success rate falls steadily with the logarithm of the time a task takes a human (R² about 0.8, body), with the horizon doubling about every seven months since 2019 (first arXiv version titled 'Measuring AI Ability to Complete Long Tasks').

## The ten references a hostile reviewer would most expect

| # | Reference | Why a hostile reviewer expects it | Cited in the draft? |
|---|---|---|---|
| 1 | Gregor Bachmann & Vaishnavh Nagarajan, ICML 2024 (entry 18) | The blindness theorem (T1) reads as a quantitative version of its claim that teacher-forced next-token training can fail to learn the right predictor. | **no** |
| 2 | Dana Angluin, Inf. Comput. 1987 (entry 26) | 'The minimal automaton from equivalence information' is L*'s guarantee; the checker looks like an equivalence oracle, so the recipe will be called gradient-based L*. | **no** |
| 3 | Stephane Ross et al., AISTATS 2011 (entry 19) | Compounding error, and the fix 'train on the states it will meet' (E13, the Markov control), is the DAgger result. | **no** |
| 4 | Keyon Vafa et al., NeurIPS 2024 (entry 23) | Already uses Myhill-Nerode to judge sequence-model world models; the reviewer will ask what is new beyond turning the metric into a loss. | yes, [55] |
| 5 | Kenneth Li et al., ICLR 2023 (entry 24) | The standard counter-evidence that next-token training alone learns world state. | yes, [56] |
| 6 | Jayakumar Subramanian et al., JMLR 2022 (entry 42) | Its information state, sufficient to predict the output and its own next value, is the first two clauses of the recipe, with approximation bounds. | **no** |
| 7 | Cosma Rohilla Shalizi & James P. Crutchfield, J. Stat. Phys. 2001 (entry 32) | Proves the minimal predictive state (causal states) is unique; 'the target is the minimal predictive quotient' is not new. | **no** |
| 8 | Sean McLeish et al., NeurIPS 2024 (entry 11) | The arithmetic length-generalisation result every reader knows; E6 must be compared with it. | **no** |
| 9 | Łukasz Kaiser & Ilya Sutskever, ICLR 2016 (entry 17) | Error-free long binary addition far beyond 20-bit training, by architecture alone, a decade ago. | **no** |
| 10 | Beatrice Bevilacqua et al., ICML 2023 (entry 57) | The closest method: invariance of next-step predictions across inputs that share an algorithmic step, aimed at out-of-distribution size. | yes, [33] |

Runners-up, in order: Givan, Dean and Greig 2003 (bisimulation as model minimisation; entry 37), Grimm et al.
2020 (value equivalence; entry 46), Hou et al. 2024 (Turing Programs, chain of thought that does length-generalise,
against E2; entry 72), Lee et al. 2025 (self-improvement to 100-digit addition without architectural change, against
E6 and E14; entry 16), Snell et al. 2022 (context distillation, against E14; entry 56), Brandstetter et al. 2022 (the
pushforward trick, against E15; entry 63) and Terzić et al. 2025 (closure and exact automaton emulation by
parametrisation; entry 6, cited).

## Introduction claims: what large language models get wrong

Each row gives the sentence the paper may make, its sources (entry numbers above) and what the sentence rests on.

| # | Claim | Sentence the paper may make | Sources | Rests on |
|---|---|---|---|---|
| 1 | Multi-digit multiplication and compositional arithmetic | On multi-digit multiplication, the accuracy of large language models, GPT-4 included, falls to near zero as the number of digits grows (Dziri et al., 2023). | entry 76 (NeurIPS 2023, cited) | abstract; body section 2 ('accuracy decreases to near zero as task complexity increases') |
| 2 | Counting | Large language models miscount: GPT-4 counts the characters or words in a list far more accurately when the answer is a common number than a rare one (McCoy et al., 2024), and models trained to count fail beyond the counts they were trained on unless the architecture supplies the right inductive bias (Chang & Bisk, 2025; Yehudai et al., 2026). | entry 77 (PNAS 2024); entry 78 (ICLR 2025); entry 79 (UAI 2026); entry 80 (arXiv 2024) | McCoy et al.: body section 6.6 (PNAS, peer-reviewed); Chang & Bisk and Yehudai et al.: abstracts. The familiar letter-in-a-word failure ('r' in 'strawberry') is documented only in a preprint (Fu et al., 2024): cite it as a preprint or not at all |
| 3 | Entity and state tracking in text | Language models pretrained on text alone did not track the state of entities through a described series of operations; among the models tested, only GPT-3.5 models, pretrained also on code, did (Kim & Schuster, 2023). | entry 81 (ACL 2023, cited) | abstract |
| 4 | Long-context state tracking | When a task requires tracking a latent structure through a long context, such as a list changed by a long sequence of operations, frontier models' scores drop sharply within the first 32K tokens (Vodrahalli et al., 2024). | entry 82 (arXiv 2024) | body sections 2.1 (Latent List) and 5.2 ('Degradation before 32K Context'); a preprint |
| 5 | Finding their own mistakes | Large language models generally fail to locate the mistakes in their own reasoning, even in unambiguous cases, although they can correct a mistake once told where it is (Tyen et al., 2024); without external feedback, self-correction does not improve their reasoning (Huang et al., 2024). | entry 83 (Findings of ACL 2024); entry 84 (ICLR 2024) | abstracts |
| 6 | Agents fail more as tasks lengthen | AI agents succeed less often the longer a task takes a human, and the length of task that frontier models complete half the time has doubled about every seven months since 2019 (Kwa et al., 2025). | entry 85 (NeurIPS 2025) | abstract (time horizon, doubling); body (success falls with log human time, R² about 0.8) |
| 7 | Incoherent world models despite good next-token prediction | Transformers trained on taxi rides in Manhattan predict a valid next turn nearly 100% of the time, yet Myhill-Nerode tests show that the street map they imply is incoherent, which makes them fragile on related tasks (Vafa et al., 2024). | entry 23 (NeurIPS 2024, cited) | abstract (incoherence, fragility); body section 2 (valid next turn nearly 100% of the time) |
| 8 | Length generalisation needs state coverage (related work) | Recurrent models fail to length-generalise when training visits only part of the states they can reach, and widening that coverage restores generalisation to sequences orders of magnitude longer (Buitrago Ruiz & Gu, 2025). | entry 10 (ICML 2025) | abstract |
| 9 | Equal held-out performance does not fix behaviour (related work) | Training pipelines return many predictors with equally strong held-out performance that behave very differently once deployed (D'Amour et al., 2022); next-token loss leaves the state underspecified in the same way. | entry 21 (JMLR 2022) | abstract; the second half of the sentence is the paper's own claim (T1) |

## Draft references whose venue is out of date

- [51] Siems, J. et al. DeltaProduct: improving state-tracking in linear RNNs via Householder pro... is listed as a preprint; verified venue: Advances in Neural Information Processing Systems 38 (NeurIPS 2025) (arXiv; DBLP conf/nips/SiemsCZHPG25).
- [52] Terzić, A. et al. Structured sparse transition matrices to enable state tracking in state-... is listed as a preprint; verified venue: Advances in Neural Information Processing Systems 38 (NeurIPS 2025), spotlight (arXiv comment 'NeurIPS 2025 Spotlight'; OpenReview 'NeurIPS 2025 spotlight').
- [49] Hao, S. et al. Training large language models to reason in a continuous latent space. Prep... is listed as a preprint; verified venue: Conference on Language Modeling (COLM) 2025 (arXiv comment 'Accepted to COLM 2025'; OpenReview 'COLM 2025').

## Notes on the lists in REACH.md and CONTRIBUTIONS.md

- "Hint-ReLIC" is the method of Bevilacqua et al. 2023, already in the draft as reference 33 ("causal regularisation").
- Littman, Sutton and Singh's PSR paper is NIPS 14 (2001 conference); REACH's "2002" is the proceedings-year
  citation. It has no DOI or arXiv id; DBLP and OpenReview's dblp mirror were the verification.
- DreamerV3 was published in Nature in 2025 under a different title ("Mastering diverse control tasks through world
  models"); cite the Nature version.
- AlphaQubit: the arXiv abstract says accuracy is sustained far beyond the 25 training cycles. REACH's "to check: 25 to
  100,000 rounds" is in neither abstract and remains unchecked.
- ACE (Watt-Meyer et al.) is a NeurIPS 2023 workshop paper, not an archival venue; cite it as a preprint.
- Pérez et al.: the verifiable version is ICLR 2019 ("On the Turing completeness of modern neural network
  architectures"); the JMLR 2021 version ("Attention is Turing-complete") could not be checked because JMLR issues no
  DOIs.
- Ho and Kalman 1966: Crossref's record has an "Editorial:" prefix and a Greek capital Beta in "B. L. Ho"; both are
  corrected in the entry.

Draft checked: `paper/nmi/main.md` at `claude/gracious-panini-dde55f` (`d549b5c`), 62 references; 26 of the 85 works here are cited in it.
