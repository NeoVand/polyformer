"""Candidate references for research/LITERATURE.md: (key, theme, expected title, arXiv id, DOI).
Every field is checked against arXiv, Semantic Scholar and Crossref by verify_refs.py; nothing here is trusted."""
T1, T2, T3, T4, T5, T6, T7 = ("state", "arith", "nexttoken", "worldmodel", "automata", "compmech", "bisim")
T8, T9, T10, T11, T12, T13, T14 = ("latent", "ctxdist", "contrast", "reliable", "simulators", "turing", "neuro")
T15 = "llmfail"
C = [
    # 1 length generalisation and state tracking
    ("deletang2023", T1, "Neural Networks and the Chomsky Hierarchy", "2207.02098", None),
    ("liu2023shortcuts", T1, "Transformers Learn Shortcuts to Automata", "2210.10749", None),
    ("merrill2024illusion", T1, "The Illusion of State in State-Space Models", "2404.08819", None),
    ("grazzi2025negative", T1, "Unlocking State-Tracking in Linear RNNs Through Negative Eigenvalues", "2411.12537", None),
    ("siems2025deltaproduct", T1, "DeltaProduct: Improving State-Tracking in Linear RNNs via Householder Products", "2502.10297", None),
    ("terzic2025pdssm", T1, "Structured Sparse Transition Matrices to Enable State Tracking in State-Space Models", "2509.22284", None),
    ("sarrof2024ssm", T1, "The Expressive Capacity of State Space Models: A Formal Language Perspective", "2405.17394", None),
    ("anil2022length", T1, "Exploring Length Generalization in Large Language Models", "2207.04901", None),
    ("kazemnejad2023nope", T1, "The Impact of Positional Encoding on Length Generalization in Transformers", "2305.19466", None),
    # 2 arithmetic length generalisation
    ("mcleish2024abacus", T2, "Transformers Can Do Arithmetic with the Right Embeddings", "2405.17399", None),
    ("cho2024coupling", T2, "Position Coupling: Improving Length Generalization of Arithmetic Transformers Using Task Structure", "2405.20671", None),
    ("zhou2024robust", T2, "Transformers Can Achieve Length Generalization But Not Robustly", "2402.09371", None),
    ("zhou2024raspl", T2, "What Algorithms can Transformers Learn? A Study in Length Generalization", "2310.16028", None),
    ("lee2024teaching", T2, "Teaching Arithmetic to Small Transformers", "2307.03381", None),
    ("lee2025selfimproving", T2, "Self-Improving Transformers Overcome Easy-to-Hard and Length Generalization Challenges", "2502.01612", None),
    ("kaiser2016neuralgpu", T2, "Neural GPUs Learn Algorithms", "1511.08228", None),
    # 3 next-token limits and compounding error
    ("bachmann2024pitfalls", T3, "The pitfalls of next-token prediction", "2403.06963", None),
    ("ross2011dagger", T3, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning", "1011.0686", None),
    ("bengio2015scheduled", T3, "Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks", "1506.03099", None),
    # 4 world models and Nerode
    ("nerode1958", T4, "Linear automaton transformations", None, "10.1090/S0002-9939-1958-0135681-9"),
    ("vafa2024worldmodel", T4, "Evaluating the World Model Implicit in a Generative Model", "2406.03689", None),
    ("li2023othello", T4, "Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task", "2210.13382", None),
    ("nanda2023linear", T4, "Emergent Linear Representations in World Models of Self-Supervised Sequence Models", "2309.00941", None),
    # 5 automata learning
    ("angluin1987", T5, "Learning regular sets from queries and counterexamples", None, "10.1016/0890-5401(87)90052-6"),
    ("weiss2018extracting", T5, "Extracting Automata from Recurrent Neural Networks Using Queries and Counterexamples", "1711.09576", None),
    ("hsu2012spectral", T5, "A Spectral Algorithm for Learning Hidden Markov Models", "0811.4413", None),
    ("balle2014spectral", T5, "Spectral learning of weighted automata", None, "10.1007/s10994-013-5416-x"),
    ("hokalman1966", T5, "Effective construction of linear state-variable models from input/output functions", None, "10.1524/auto.1966.14.112.545"),
    # 6 computational mechanics and PSRs
    ("crutchfield1989", T6, "Inferring statistical complexity", None, "10.1103/PhysRevLett.63.105"),
    ("shalizi2001compmech", T6, "Computational Mechanics: Pattern and Prediction, Structure and Simplicity", "cond-mat/9907176", None),
    ("littman2002psr", T6, "Predictive representations of state", None, None),
    ("singh2004psr", T6, "Predictive State Representations: A New Theory for Modeling Dynamical Systems", "1207.4167", None),
    ("boots2011psr", T6, "Closing the Learning-Planning Loop with Predictive State Representations", "0912.2385", None),
    ("shai2024belief", T6, "Transformers represent belief state geometry in their residual stream", "2405.15943", None),
    # 7 bisimulation, value equivalence, self-predictive RL
    ("givan2003", T7, "Equivalence notions and model minimization in Markov decision processes", None, "10.1016/S0004-3702(02)00376-4"),
    ("ferns2004", T7, "Metrics for Finite Markov Decision Processes", "1207.4114", None),
    ("gelada2019deepmdp", T7, "DeepMDP: Learning Continuous Latent Space Models for Representation Learning", "1906.02736", None),
    ("zhang2021dbc", T7, "Learning Invariant Representations for Reinforcement Learning without Reconstruction", "2006.10742", None),
    ("castro2021mico", T7, "MICo: Improved representations via sampling-based state similarity for Markov decision processes", "2106.08229", None),
    ("subramanian2022ais", T7, "Approximate information state for approximate planning and reinforcement learning in partially observed systems", "2010.08843", None),
    ("schwarzer2021spr", T7, "Data-Efficient Reinforcement Learning with Self-Predictive Representations", "2007.05929", None),
    ("tang2023selfpredictive", T7, "Understanding Self-Predictive Learning for Reinforcement Learning", "2212.03319", None),
    ("ni2024bridging", T7, "Bridging State and History Representations: Understanding Self-Predictive RL", "2401.08898", None),
    ("grimm2020ve", T7, "The Value Equivalence Principle for Model-Based Reinforcement Learning", "2011.03506", None),
    ("grimm2021pve", T7, "Proper Value Equivalence", "2106.10316", None),
    ("schrittwieser2020muzero", T7, "Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model", "1911.08265", None),
    ("hafner2023dreamerv3", T7, "Mastering Diverse Domains through World Models", "2301.04104", None),
    # 8 latent reasoning and Markov chain of thought
    ("hao2024coconut", T8, "Training Large Language Models to Reason in a Continuous Latent Space", "2412.06769", None),
    ("aghajohari2025markovian", T8, "The Markovian Thinker", "2510.06557", None),
    ("teoh2025nextlat", T8, "Next-Latent Prediction Transformers Learn Compact World Models", "2511.05963", None),
    ("deng2024stepwise", T8, "From Explicit CoT to Implicit CoT: Learning to Internalize CoT Step by Step", "2405.14838", None),
    ("geiping2025recurrent", T8, "Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach", "2502.05171", None),
    # 9 context distillation
    ("askell2021lab", T9, "A General Language Assistant as a Laboratory for Alignment", "2112.00861", None),
    ("snell2022context", T9, "Learning by Distilling Context", "2209.15189", None),
    # 10 contrastive invariance
    ("bevilacqua2023hintrelic", T10, "Neural Algorithmic Reasoning with Causal Regularisation", "2302.10258", None),
    ("mitrovic2021relic", T10, "Representation Learning via Invariant Causal Mechanisms", "2010.07922", None),
    ("jain2021contracode", T10, "Contrastive Code Representation Learning", "2007.04973", None),
    # 11 reliable computation and error correction
    ("vonneumann1956", T11, "Probabilistic logics and the synthesis of reliable organisms from unreliable components", None, None),
    ("bausch2024alphaqubit", T11, "Learning to Decode the Surface Code with a Recurrent, Transformer-Based Neural Network", "2310.05900", "10.1038/s41586-024-08148-8"),
    # 12 neural simulators and rollout stability
    ("sanchezgonzalez2020gns", T12, "Learning to Simulate Complex Physics with Graph Networks", "2002.09405", None),
    ("brandstetter2022mpnn", T12, "Message Passing Neural PDE Solvers", "2202.03376", None),
    ("lippe2023pderefiner", T12, "PDE-Refiner: Achieving Accurate Long Rollouts with Neural PDE Solvers", "2308.05732", None),
    ("kochkov2024neuralgcm", T12, "Neural General Circulation Models for Weather and Climate", "2311.07222", "10.1038/s41586-024-07744-y"),
    ("wattmeyer2023ace", T12, "ACE: A fast, skillful learned global atmospheric model for climate prediction", "2310.02074", None),
    ("greydanus2019hnn", T12, "Hamiltonian Neural Networks", "1906.01563", None),
    # 13 Turing completeness
    ("siegelmann1995", T13, "On the computational power of neural nets", None, "10.1006/jcss.1995.1013"),
    ("perez2021attention", T13, "Attention is Turing-Complete", "1901.03429", None),
    ("schuurmans2023memory", T13, "Memory Augmented Large Language Models are Computationally Universal", "2301.04589", None),
    ("schuurmans2024autoregressive", T13, "Autoregressive Large Language Models are Computationally Universal", "2410.03170", None),
    ("hou2024turingprograms", T13, "Universal Length Generalization with Turing Programs", "2407.03310", None),
    # 14 TEM and CSCG
    ("whittington2020tem", T14, "The Tolman-Eichenbaum Machine: Unifying Space and Relational Memory through Generalization in the Hippocampal Formation", None, "10.1016/j.cell.2020.10.024"),
    ("george2021cscg", T14, "Clone-structured graph representations enable flexible learning and vicarious evaluation of cognitive maps", None, "10.1038/s41467-021-22559-5"),
    ("whittington2022transformers", T14, "Relating transformers to models and neural representations of the hippocampal formation", "2112.04035", None),
    # added 25 Oct 2026 (introduction: what large language models get wrong; plus two works the orchestrator named)
    ("buitrago2025length", T1, "Understanding and Improving Length Generalization in Recurrent Models", "2507.02782", None),
    ("damour2022underspec", T3, "Underspecification Presents Challenges for Credibility in Modern Machine Learning", "2011.03395", None),
    ("dziri2023faith", T15, "Faith and Fate: Limits of Transformers on Compositionality", "2305.18654", None),
    ("mccoy2024embers", T15, "Embers of Autoregression: Understanding Large Language Models Through the Problem They are Trained to Solve", "2309.13638", "10.1073/pnas.2322420121"),
    ("chang2025count", T15, "Language Models Need Inductive Biases to Count Inductively", "2405.20131", None),
    ("yehudai2024count", T15, "When Can Transformers Count to n?", "2407.15160", None),
    ("fu2024letters", T15, "Why Do Large Language Models (LLMs) Struggle to Count Letters?", "2412.18626", None),
    ("kim2023entity", T15, "Entity Tracking in Language Models", "2305.02363", "10.18653/v1/2023.acl-long.213"),
    ("vodrahalli2024michelangelo", T15, "Michelangelo: Long Context Evaluations Beyond Haystacks via Latent Structure Queries", "2409.12640", None),
    ("tyen2024mistakes", T15, "LLMs cannot find reasoning errors, but can correct them given the error location", "2311.08516", "10.18653/v1/2024.findings-acl.826"),
    ("huang2024selfcorrect", T15, "Large Language Models Cannot Self-Correct Reasoning Yet", "2310.01798", None),
    ("kwa2025horizon", T15, "Measuring AI Ability to Complete Long Software Tasks", "2503.14499", None),
]
