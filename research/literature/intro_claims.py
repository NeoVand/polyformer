"""The introduction's claims about what large language models get wrong (orchestrator's list, 25 Oct 2026), each with
the sentence the paper may make from its sources and what that sentence rests on. Sources are keys of refs_verified.json;
render_literature.py prints entry numbers and venues. A sentence goes no further than the cited text: an abstract, or the
body section named in 'basis'."""

CLAIMS = [
    ("Multi-digit multiplication and compositional arithmetic", ["dziri2023faith"],
     "On multi-digit multiplication, the accuracy of large language models, GPT-4 included, falls to near zero as the "
     "number of digits grows (Dziri et al., 2023).",
     "abstract; body section 2 ('accuracy decreases to near zero as task complexity increases')"),
    ("Counting", ["mccoy2024embers", "chang2025count", "yehudai2024count", "fu2024letters"],
     "Large language models miscount: GPT-4 counts the characters or words in a list far more accurately when the answer "
     "is a common number than a rare one (McCoy et al., 2024), and models trained to count fail beyond the counts they "
     "were trained on unless the architecture supplies the right inductive bias (Chang & Bisk, 2025; Yehudai et al., 2026).",
     "McCoy et al.: body section 6.6 (PNAS, peer-reviewed); Chang & Bisk and Yehudai et al.: abstracts. The familiar "
     "letter-in-a-word failure ('r' in 'strawberry') is documented only in a preprint (Fu et al., 2024): cite it as a "
     "preprint or not at all"),
    ("Entity and state tracking in text", ["kim2023entity"],
     "Language models pretrained on text alone did not track the state of entities through a described series of "
     "operations; among the models tested, only GPT-3.5 models, pretrained also on code, did (Kim & Schuster, 2023).",
     "abstract"),
    ("Long-context state tracking", ["vodrahalli2024michelangelo"],
     "When a task requires tracking a latent structure through a long context, such as a list changed by a long sequence "
     "of operations, frontier models' scores drop sharply within the first 32K tokens (Vodrahalli et al., 2024).",
     "body sections 2.1 (Latent List) and 5.2 ('Degradation before 32K Context'); a preprint"),
    ("Finding their own mistakes", ["tyen2024mistakes", "huang2024selfcorrect"],
     "Large language models generally fail to locate the mistakes in their own reasoning, even in unambiguous cases, "
     "although they can correct a mistake once told where it is (Tyen et al., 2024); without external feedback, "
     "self-correction does not improve their reasoning (Huang et al., 2024).",
     "abstracts"),
    ("Agents fail more as tasks lengthen", ["kwa2025horizon"],
     "AI agents succeed less often the longer a task takes a human, and the length of task that frontier models complete "
     "half the time has doubled about every seven months since 2019 (Kwa et al., 2025).",
     "abstract (time horizon, doubling); body (success falls with log human time, R² about 0.8)"),
    ("Incoherent world models despite good next-token prediction", ["vafa2024worldmodel"],
     "Transformers trained on taxi rides in Manhattan predict a valid next turn nearly 100% of the time, yet "
     "Myhill-Nerode tests show that the street map they imply is incoherent, which makes them fragile on related tasks "
     "(Vafa et al., 2024).",
     "abstract (incoherence, fragility); body section 2 (valid next turn nearly 100% of the time)"),
    ("Length generalisation needs state coverage (related work)", ["buitrago2025length"],
     "Recurrent models fail to length-generalise when training visits only part of the states they can reach, and "
     "widening that coverage restores generalisation to sequences orders of magnitude longer (Buitrago Ruiz & Gu, 2025).",
     "abstract"),
    ("Equal held-out performance does not fix behaviour (related work)", ["damour2022underspec"],
     "Training pipelines return many predictors with equally strong held-out performance that behave very differently "
     "once deployed (D'Amour et al., 2022); next-token loss leaves the state underspecified in the same way.",
     "abstract; the second half of the sentence is the paper's own claim (T1)"),
]
