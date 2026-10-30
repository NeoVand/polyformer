"""Venue, year and evidence for every reference, plus the document's frame (intro, themes, hostile list).

Each venue is fixed by the strongest available record, named in 'evidence':
  DBLP key  - a conference or journal key carried by the Semantic Scholar record (e.g. conf/iclr/...25)
  OpenReview - an accepted-paper venue string on OpenReview, matched on the exact title
  Crossref  - the publisher's DOI record (journal, volume, pages, year)
  arXiv     - the arXiv record (journal_ref or author comment), or 'preprint' when nothing else exists
  S2        - the Semantic Scholar record (used only where nothing stronger exists, and said so)
'short' is the label used in the hostile-reviewer table.
"""

PENDING = "PENDING"

V = {
    # 1 state tracking
    "deletang2023": dict(venue="International Conference on Learning Representations (ICLR) 2023", evidence="arXiv; OpenReview 'ICLR 2023 notable top 25%'", short="ICLR 2023"),
    "liu2023shortcuts": dict(venue="ICLR 2023", evidence="arXiv; OpenReview 'ICLR 2023 notable top 5%'", short="ICLR 2023"),
    "merrill2024illusion": dict(venue='ICML 2024', evidence="arXiv comment 'To appear at ICML 2024'; OpenReview 'ICML 2024 Poster'", short="ICML 2024"),
    "grazzi2025negative": dict(venue="ICLR 2025", evidence="arXiv; DBLP conf/iclr/GrazziSZFHP25", short="ICLR 2025"),
    "siems2025deltaproduct": dict(venue="Advances in Neural Information Processing Systems 38 (NeurIPS 2025)", evidence="arXiv; DBLP conf/nips/SiemsCZHPG25", short="NeurIPS 2025"),
    "terzic2025pdssm": dict(venue='Advances in Neural Information Processing Systems 38 (NeurIPS 2025), spotlight', evidence="arXiv comment 'NeurIPS 2025 Spotlight'; OpenReview 'NeurIPS 2025 spotlight'", short="NeurIPS 2025"),
    "sarrof2024ssm": dict(venue="Advances in Neural Information Processing Systems 37 (NeurIPS 2024)", evidence="arXiv journal_ref; DBLP conf/nips/SarrofV024", short="NeurIPS 2024"),
    "anil2022length": dict(venue='Advances in Neural Information Processing Systems 35 (NeurIPS 2022)', evidence="arXiv; OpenReview 'NeurIPS 2022 Accept'", short="NeurIPS 2022"),
    "kazemnejad2023nope": dict(venue="Advances in Neural Information Processing Systems 36 (NeurIPS 2023)", evidence="arXiv; DBLP conf/nips/KazemnejadPRDR23", short="NeurIPS 2023"),
    # 2 arithmetic
    "mcleish2024abacus": dict(venue='Advances in Neural Information Processing Systems 37 (NeurIPS 2024)', evidence="arXiv; OpenReview 'NeurIPS 2024 poster'", short="NeurIPS 2024"),
    "cho2024coupling": dict(venue="Advances in Neural Information Processing Systems 37 (NeurIPS 2024)", evidence="arXiv; DBLP conf/nips/0002CAB0Y24", short="NeurIPS 2024"),
    "zhou2024robust": dict(venue='arXiv preprint (2024); poster at the ME-FoMo 2024 workshop', evidence="arXiv; OpenReview 'ME-FoMo 2024 Poster' (a workshop; no archival venue found)", short="2024"),
    "zhou2024raspl": dict(venue="ICLR 2024", evidence="arXiv; DBLP conf/iclr/ZhouBLRSSBN24", short="ICLR 2024"),
    "lee2024teaching": dict(venue='ICLR 2024', evidence="arXiv; OpenReview 'ICLR 2024 poster'", short="ICLR 2024"),
    "lee2025selfimproving": dict(venue='ICML 2025', evidence="arXiv; OpenReview 'ICML 2025 poster'", short="ICML 2025"),
    "kaiser2016neuralgpu": dict(venue='ICLR 2016', evidence="arXiv; OpenReview dblp record 'ICLR (Poster) 2016'", short="ICLR 2016"),
    # 3 next-token
    "bachmann2024pitfalls": dict(venue="International Conference on Machine Learning (ICML) 2024", evidence="arXiv; DBLP conf/icml/BachmannN24", short="ICML 2024"),
    "ross2011dagger": dict(venue="International Conference on Artificial Intelligence and Statistics (AISTATS) 2011, JMLR W&CP 15, 627–635", evidence="arXiv; DBLP journals/jmlr/RossGB11; S2 pages 627–635", short="AISTATS 2011"),
    "bengio2015scheduled": dict(venue="Advances in Neural Information Processing Systems 28 (NIPS 2015)", evidence="arXiv; DBLP conf/nips/BengioVJS15", short="NIPS 2015"),
    # 4 world models
    "nerode1958": dict(venue="Proceedings of the American Mathematical Society 9(4), 541–544 (1958)", evidence="Crossref", short="Proc. AMS 1958"),
    "vafa2024worldmodel": dict(venue="Advances in Neural Information Processing Systems 37 (NeurIPS 2024)", evidence="arXiv; DBLP conf/nips/VafaCRKM24", short="NeurIPS 2024"),
    "li2023othello": dict(venue='ICLR 2023', evidence="arXiv comment 'ICLR 2023 oral (notable-top-5%)'; OpenReview 'ICLR 2023'", short="ICLR 2023"),
    "nanda2023linear": dict(venue="BlackboxNLP Workshop on Analyzing and Interpreting Neural Networks for NLP (at EMNLP 2023), 16–30", evidence="arXiv; OpenReview dblp record 'BlackboxNLP@EMNLP 2023'; S2 pages", short="BlackboxNLP 2023"),
    # 5 automata
    "angluin1987": dict(venue="Information and Computation 75(2), 87–106 (1987)", evidence="Crossref; DBLP journals/iandc/Angluin87", short="Inf. Comput. 1987"),
    "weiss2018extracting": dict(venue="ICML 2018", evidence="arXiv journal_ref 'ICML 2018'; DBLP conf/icml/WeissGY18", short="ICML 2018"),
    "hsu2012spectral": dict(venue="Journal of Computer and System Sciences 78(5), 1460–1480 (2012)", evidence="arXiv journal_ref; S2", short="JCSS 2012"),
    "balle2014spectral": dict(venue="Machine Learning 96(1–2), 33–63 (2014; online 2013)", evidence="Crossref (published-print 2014-07, online 2013-10-03)", short="Mach. Learn. 2014",
                              title="Spectral learning of weighted automata: A forward-backward perspective"),
    "hokalman1966": dict(venue="at – Automatisierungstechnik (Crossref container) 14, 545–548 (1966)", evidence="Crossref; record carries an 'Editorial:' title prefix and a Greek capital Beta in the first initial, both corrected here", short="1966",
                         title="Effective construction of linear state-variable models from input/output functions", authors=["B. L. Ho", "R. E. Kalman"]),
    # 6 computational mechanics
    "crutchfield1989": dict(venue="Physical Review Letters 63(2), 105–108 (1989)", evidence="Crossref", short="PRL 1989"),
    "shalizi2001compmech": dict(venue="Journal of Statistical Physics 104, 817–879 (2001)", evidence="arXiv journal_ref; S2 journal record (pages 817–879; arXiv journal_ref says 816–879)", short="J. Stat. Phys. 2001"),
    "littman2002psr": dict(title="Predictive Representations of State", authors=["Michael L. Littman", "Richard S. Sutton", "Satinder P. Singh"], venue='Advances in Neural Information Processing Systems 14 (NIPS 2001)', evidence="S2 record with DBLP conf/nips/LittmanSS01; OpenReview dblp record 'NIPS 2001'; no DOI or arXiv id exists (REACH.md's '2002' is the proceedings-year citation)", short="NIPS 14"),
    "singh2004psr": dict(venue="Conference on Uncertainty in Artificial Intelligence (UAI) 2004, 512–518", evidence="arXiv; S2 venue and pages", short="UAI 2004"),
    "boots2011psr": dict(venue="The International Journal of Robotics Research 30(7), 954–966 (2011)", evidence="arXiv; DBLP journals/ijrr/BootsSG11; S2 journal record", short="IJRR 2011"),
    "shai2024belief": dict(venue="Advances in Neural Information Processing Systems 37 (NeurIPS 2024)", evidence="arXiv; DBLP conf/nips/ShaiTOMR24", short="NeurIPS 2024"),
    # 7 bisimulation
    "givan2003": dict(venue="Artificial Intelligence 147(1–2), 163–223 (2003)", evidence="Crossref; DBLP journals/ai/GivanDG03", short="Artif. Intell. 2003"),
    "ferns2004": dict(venue="Conference on Uncertainty in Artificial Intelligence (UAI) 2004", evidence="arXiv comment 'Appears in Proceedings of the Twentieth Conference on Uncertainty in Artificial Intelligence (UAI2004)'; S2 maps the id to a two-page AAAI 2004 abstract of the same title", short="UAI 2004"),
    "gelada2019deepmdp": dict(venue="ICML 2019", evidence="arXiv; DBLP conf/icml/GeladaKBNB19", short="ICML 2019"),
    "zhang2021dbc": dict(venue="ICLR 2021", evidence="arXiv; DBLP conf/iclr/0001MCGL21", short="ICLR 2021"),
    "castro2021mico": dict(venue="Advances in Neural Information Processing Systems 34 (NeurIPS 2021)", evidence="arXiv; DBLP conf/nips/CastroKPR21", short="NeurIPS 2021"),
    "subramanian2022ais": dict(venue='Journal of Machine Learning Research (2022)', evidence="arXiv; OpenReview dblp record 'J. Mach. Learn. Res. 2022'", short="JMLR 2022"),
    "schwarzer2021spr": dict(venue="ICLR 2021", evidence="arXiv; DBLP conf/iclr/SchwarzerAGHCB21", short="ICLR 2021"),
    "tang2023selfpredictive": dict(venue="ICML 2023", evidence="arXiv; DBLP conf/icml/TangGRPCMRALL0T23", short="ICML 2023"),
    "ni2024bridging": dict(venue="ICLR 2024", evidence="arXiv; DBLP conf/iclr/NiESMGMB24", short="ICLR 2024"),
    "grimm2020ve": dict(venue="Advances in Neural Information Processing Systems 33 (NeurIPS 2020)", evidence="arXiv; DBLP conf/nips/GrimmBSS20", short="NeurIPS 2020"),
    "grimm2021pve": dict(venue="Advances in Neural Information Processing Systems 34 (NeurIPS 2021)", evidence="arXiv journal_ref 'NeurIPS 2021'; DBLP conf/nips/GrimmBFSS21", short="NeurIPS 2021"),
    "schrittwieser2020muzero": dict(venue="Nature 588, 604–609 (2020)", evidence="arXiv; DBLP journals/nature/SchrittwieserAH20; S2 journal record", short="Nature 2020"),
    "hafner2023dreamerv3": dict(doi="10.1038/s41586-025-08744-2", venue='Nature 640(8059), 647–653 (2025), published as "Mastering diverse control tasks through world models"', evidence='arXiv; Crossref (Nature version, doi:10.1038/s41586-025-08744-2)', short="2023"),
    # 8 latent reasoning
    "hao2024coconut": dict(venue='Conference on Language Modeling (COLM) 2025', evidence="arXiv comment 'Accepted to COLM 2025'; OpenReview 'COLM 2025'", short="2024"),
    "aghajohari2025markovian": dict(venue='arXiv preprint (2025)', evidence='arXiv; no accepted venue on OpenReview or S2', short="2025"),
    "teoh2025nextlat": dict(venue='arXiv preprint (2025); PLAN-FM Bridge workshop at AAAI 2026', evidence="arXiv comment 'Microsoft Research Preprint'; OpenReview 'PLAN-FM Bridge @ AAAI 2026' (a workshop)", short="2025"),
    "deng2024stepwise": dict(venue='arXiv preprint (2024)', evidence='arXiv; OpenReview shows only an ICLR 2025 submission, not an acceptance', short="2024"),
    "geiping2025recurrent": dict(venue='Advances in Neural Information Processing Systems 38 (NeurIPS 2025), spotlight', evidence="arXiv; OpenReview 'NeurIPS 2025 spotlight'", short="NeurIPS 2025"),
    # 9 context distillation
    "askell2021lab": dict(venue="arXiv preprint (2021)", evidence="arXiv; S2 (no venue)", short="arXiv 2021"),
    "snell2022context": dict(venue='arXiv preprint (2022)', evidence='arXiv; no venue on OpenReview or S2', short="2022"),
    # 10 contrastive invariance
    "bevilacqua2023hintrelic": dict(venue='ICML 2023, 2272–2288', evidence="arXiv comment 'ICML 2023, Camera Ready'; OpenReview 'ICML 2023 Poster'; S2 pages", short="ICML 2023"),
    "mitrovic2021relic": dict(venue='ICLR 2021', evidence="arXiv; OpenReview 'ICLR 2021 Poster'", short="ICLR 2021"),
    "jain2021contracode": dict(venue="Conference on Empirical Methods in Natural Language Processing (EMNLP) 2021, 5954–5971", evidence="arXiv; DBLP conf/emnlp/0001JZA0S21; S2 pages", short="EMNLP 2021"),
    # 11 reliable computation
    "vonneumann1956": dict(title="Probabilistic Logics and the Synthesis of Reliable Organisms From Unreliable Components", authors=["J. von Neumann"], doi="10.1515/9781400882618-003", venue='In Automata Studies (AM-34), 43–98. Princeton University Press (1956)', evidence='Crossref (book chapter); no arXiv id', short="1956"),
    "bausch2024alphaqubit": dict(venue="Nature 635(8040), 834–840 (2024)", evidence="Crossref; arXiv journal_ref 'Nature 635, 834-840 (2024)' (arXiv title: 'Learning to Decode the Surface Code with a Recurrent, Transformer-Based Neural Network')", short="Nature 2024"),
    # 12 simulators
    "sanchezgonzalez2020gns": dict(venue='ICML 2020', evidence="arXiv comment 'Accepted at ICML 2020'; OpenReview dblp record 'ICML 2020'", short="ICML 2020"),
    "brandstetter2022mpnn": dict(venue="ICLR 2022", evidence="arXiv; DBLP conf/iclr/BrandstetterWW22", short="ICLR 2022"),
    "lippe2023pderefiner": dict(venue="Advances in Neural Information Processing Systems 36 (NeurIPS 2023)", evidence="arXiv; DBLP conf/nips/LippeVPTB23", short="NeurIPS 2023"),
    "kochkov2024neuralgcm": dict(venue="Nature 632(8027), 1060–1066 (2024)", evidence="Crossref; DBLP journals/nature/KochkovYLNSMKLRDHBSWBH24", short="Nature 2024"),
    "wattmeyer2023ace": dict(venue='arXiv preprint (2023); Tackling Climate Change with Machine Learning workshop at NeurIPS 2023', evidence="arXiv comment 'Accepted at Tackling Climate Change with Machine Learning: workshop at NeurIPS 2023'", short="2023"),
    "greydanus2019hnn": dict(venue="Advances in Neural Information Processing Systems 32 (NeurIPS 2019)", evidence="arXiv; DBLP conf/nips/GreydanusDY19", short="NeurIPS 2019"),
    # 13 Turing completeness
    "siegelmann1995": dict(venue="Journal of Computer and System Sciences 50(1), 132–150 (1995)", evidence="Crossref", short="JCSS 1995"),
    "perez2021attention": dict(venue="ICLR 2019", evidence="arXiv; DBLP conf/iclr/PerezMB19 (the journal version, 'Attention is Turing-complete', JMLR 2021, was not verifiable here: JMLR issues no DOIs)", short="ICLR 2019"),
    "schuurmans2023memory": dict(venue='arXiv preprint (2023)', evidence='arXiv; no venue on OpenReview or S2', short="2023"),
    "schuurmans2024autoregressive": dict(venue='arXiv preprint (2024)', evidence='arXiv; OpenReview has only the dblp CoRR record', short="2024"),
    "hou2024turingprograms": dict(venue='ICML 2025', evidence="arXiv; OpenReview 'ICML 2025 poster'", short="2024"),
    # 14 cognitive maps
    "whittington2020tem": dict(venue="Cell 183(5), 1249–1263.e23 (2020)", evidence="Crossref; PubMed 33181068", short="Cell 2020"),
    "george2021cscg": dict(venue="Nature Communications 12, 2392 (2021)", evidence="Crossref (article number 2392)", short="Nat. Commun. 2021"),
    "whittington2022transformers": dict(venue='ICLR 2022', evidence="arXiv; OpenReview 'ICLR 2022 Poster'", short="ICLR 2022"),
    # added 25 Oct 2026
    "buitrago2025length": dict(venue="International Conference on Machine Learning (ICML) 2025", evidence="arXiv; DBLP conf/icml/RuizG25; OpenReview 'ICML 2025 poster'", short="ICML 2025"),
    "damour2022underspec": dict(venue="Journal of Machine Learning Research 23(226), 1–61 (2022)", evidence="arXiv; jmlr.org/papers/v23/20-1335.html citation metadata (JMLR issues no DOIs); DBLP journals/jmlr/DAmourHMAABCDEH22", short="JMLR 2022"),
    "dziri2023faith": dict(venue="Advances in Neural Information Processing Systems 36 (NeurIPS 2023), spotlight", evidence="arXiv; OpenReview 'NeurIPS 2023 spotlight'", short="NeurIPS 2023"),
    "mccoy2024embers": dict(venue="Proceedings of the National Academy of Sciences 121(41) (2024)", evidence="Crossref doi:10.1073/pnas.2322420121 (published title differs from the arXiv preprint 2309.13638)", short="PNAS 2024"),
    "chang2025count": dict(venue="ICLR 2025", evidence="arXiv; DBLP conf/iclr/ChangB25; OpenReview 'ICLR 2025 Poster'", short="ICLR 2025"),
    "yehudai2024count": dict(venue="Conference on Uncertainty in Artificial Intelligence (UAI) 2026", evidence="OpenReview 'UAI 2026 Poster' (earlier rejected at ICLR 2025); arXiv", short="UAI 2026"),
    "fu2024letters": dict(venue="arXiv preprint (2024)", evidence="arXiv; no venue on Semantic Scholar, DBLP (CoRR only) or OpenReview", short="arXiv 2024"),
    "kim2023entity": dict(venue="Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), 3835–3855 (2023)", evidence="Crossref doi:10.18653/v1/2023.acl-long.213; arXiv comment 'ACL 2023 Camera-ready'", short="ACL 2023"),
    "vodrahalli2024michelangelo": dict(venue="arXiv preprint (2024)", evidence="arXiv; Semantic Scholar, DBLP (CoRR) and OpenReview give no venue", short="arXiv 2024"),
    "tyen2024mistakes": dict(venue="Findings of the Association for Computational Linguistics: ACL 2024, 13894–13908", evidence="Crossref doi:10.18653/v1/2024.findings-acl.826; arXiv comment 'ACL 2024 Findings'", short="Findings of ACL 2024"),
    "huang2024selfcorrect": dict(venue="ICLR 2024", evidence="arXiv comment 'ICLR 2024'; DBLP conf/iclr/0009CMZYSZ24; OpenReview 'ICLR 2024 poster'", short="ICLR 2024"),
    "kwa2025horizon": dict(venue="Advances in Neural Information Processing Systems 38 (NeurIPS 2025)", evidence="arXiv journal_ref 'NeurIPS 2025'; DBLP conf/nips/KwaWBDGHJKRABBD25; OpenReview 'NeurIPS 2025 poster'", short="NeurIPS 2025"),
}

THEMES = [
    ("state", "1. Length generalisation and state tracking"),
    ("arith", "2. Arithmetic length generalisation"),
    ("nexttoken", "3. Limits of next-token training and compounding error"),
    ("worldmodel", "4. World models and the Nerode lens"),
    ("automata", "5. Automata learning and minimal realisation"),
    ("compmech", "6. Computational mechanics and predictive state representations"),
    ("bisim", "7. Bisimulation, value equivalence and self-predictive reinforcement learning"),
    ("latent", "8. Latent reasoning and Markov chain of thought"),
    ("ctxdist", "9. Context distillation"),
    ("contrast", "10. Contrastive invariance"),
    ("reliable", "11. Reliable computation and error correction"),
    ("simulators", "12. Neural simulators and rollout stability"),
    ("turing", "13. Turing completeness and universal computation"),
    ("neuro", "14. Cognitive maps: TEM and CSCG"),
    ("llmfail", "15. What large language models get wrong (for the introduction)"),
]

HOSTILE = [
    ("bachmann2024pitfalls", "The blindness theorem (T1) reads as a quantitative version of its claim that teacher-forced next-token training can fail to learn the right predictor."),
    ("angluin1987", "'The minimal automaton from equivalence information' is L*'s guarantee; the checker looks like an equivalence oracle, so the recipe will be called gradient-based L*."),
    ("ross2011dagger", "Compounding error, and the fix 'train on the states it will meet' (E13, the Markov control), is the DAgger result."),
    ("vafa2024worldmodel", "Already uses Myhill-Nerode to judge sequence-model world models; the reviewer will ask what is new beyond turning the metric into a loss."),
    ("li2023othello", "The standard counter-evidence that next-token training alone learns world state."),
    ("subramanian2022ais", "Its information state, sufficient to predict the output and its own next value, is the first two clauses of the recipe, with approximation bounds."),
    ("shalizi2001compmech", "Proves the minimal predictive state (causal states) is unique; 'the target is the minimal predictive quotient' is not new."),
    ("mcleish2024abacus", "The arithmetic length-generalisation result every reader knows; E6 must be compared with it."),
    ("kaiser2016neuralgpu", "Error-free long binary addition far beyond 20-bit training, by architecture alone, a decade ago."),
    ("bevilacqua2023hintrelic", "The closest method: invariance of next-step predictions across inputs that share an algorithmic step, aimed at out-of-distribution size."),
]

INTRO = """# Literature: exact state from certified equivalences

Systematic review for the paper whose thesis is in `research/CONTRIBUTIONS.md`, with the reach and missing references
of `research/REACH.md`. {n} works in 15 themes. Each entry gives the exact author list and title as the source record
gives them, the venue and year, the arXiv id or DOI, whether the current draft cites it, and one sentence on how it
bears on our claims, including where it pre-empts or weakens them.

**How every entry was verified.** No citation was taken from memory. `research/literature/verify_refs.py` queried the
arXiv API (authors, title, first-version date, journal_ref), the Semantic Scholar Graph API (venue, DBLP key, DOI) and
Crossref (journal, volume, pages) for every candidate, and flagged any id whose retrieved title did not match;
`verify_venues.py` added OpenReview accepted-paper venues and arXiv author comments where Semantic Scholar's year was
the preprint year; `content_checks.py` fetched abstracts for the non-arXiv works (PubMed, Semantic Scholar, Crossref).
The raw records are in `research/literature/refs_verified.json`; the evidence for each venue is printed with the entry.
Relation sentences rest on the abstracts as fetched; where a sentence relies on a paper's body, it says so.

**Draft checked:** `paper/nmi/main.md` on `{branch}` (`{commit}`). 'Cited' means the work's arXiv id, DOI or title
appears in the draft's reference list.
"""

HOSTILE_NOTE = """Runners-up, in order: Givan, Dean and Greig 2003 (bisimulation as model minimisation; entry {givan2003}), Grimm et al.
2020 (value equivalence; entry {grimm2020ve}), Hou et al. 2024 (Turing Programs, chain of thought that does length-generalise,
against E2; entry {hou2024turingprograms}), Lee et al. 2025 (self-improvement to 100-digit addition without architectural change, against
E6 and E14; entry {lee2025selfimproving}), Snell et al. 2022 (context distillation, against E14; entry {snell2022context}), Brandstetter et al. 2022 (the
pushforward trick, against E15; entry {brandstetter2022mpnn}) and Terzić et al. 2025 (closure and exact automaton emulation by
parametrisation; entry {terzic2025pdssm}, cited)."""

REACH_NOTES = """## Notes on the lists in REACH.md and CONTRIBUTIONS.md

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
"""
