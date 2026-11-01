# R7 mapper: interlinear glossing

## 1. Objects and techniques

Objects:
- *interlinear glossed text* (IGT): source, morpheme, gloss and free-translation lines;
- the *FLEx/Toolbox lexicon*, SIL's morpheme dictionary that proposes glosses for a linguist to approve;
- closed grammatical labels (1SG, ERG, PST).

Techniques:
- the *Leipzig Glossing Rules* (2008), whose Rule 2 aligns morphemes and glosses one to one;
- *two-level morphology* (Koskenniemi 1983), in which bounded-window rules over aligned symbol pairs compile to finite-state transducers;
- *Kaplan & Kay 1994*: a cascade of rewrite rules is one transducer if no rule reapplies to its own output.

## 2. Map to the problem

- **P1:** documentary linguists and archives (ELAR, PARADISEC) must answer for every gloss, and glossing is the documentation bottleneck.
- **P2:** only a speaker can check a gloss, but glosses are local, so one lexicon review replaces checking every word.
- **P3:** community data rules (OCAP) forbid cloud upload, so the work runs offline.
- **P4:** the state is a morpheme slot and the rule is allomorphy within a bounded window. Long polysynthetic words are the all-lengths case.
- **P5:** the gloss tier lets a non-speaker audit the free translation.
- **P6:** the SIGMORPHON 2023 glossing shared task.
- **P7:** auditors trust a lexicon they can read, not a list of margins.

## 3. Map from the problem

Two-level morphology had "bounded window plus finite check covers all lengths" in 1983, so the prior art predates Cai 2017. Our chain-of-thought theorem mirrors the Kaplan–Kay ban on a rule reapplying to its own output. A glosser that reads its own earlier glosses cannot be certified; a windowed one can.

## 4. Ideas

**A. The view table as an auditable grammar.** An adapter glosses each morpheme from a bounded view (the morpheme, its neighbours, and stems reduced to a class token). The views are finite, so the model's whole behaviour is a table that a linguist reviews like a lexicon. Editing a row provably changes every occurrence of that view and nothing else, so review scales with views, not corpus size, and the audit writes the spec.
- Who cares: documentation projects, SIL, funders.
- Breaks: "arithmetic" and "the product is the computation".
- Kill: on Arapaho or Tsez, any one of these: accuracy more than 5 points below the best 2023 system, more than 10,000 views, or a frequency-table baseline within 1 point.

**B. Glossed programs.** The chat model aligns each program literal and operation one to one with a span of the prompt, using ∅ for implied quantities. A local checker tests the alignment, and flagged items fall back to answering in the head, which exposes translation errors (the cause of the GSM8K loss).
- Breaks: "the certificate covers outputs only".
- Kill: on fresh GSM8K items, the fallback does not recover the 5.8-point loss, or the checker catches under 50% of wrong programs at 10% false alarms.

## 5. Grade

A: **FRAME**. We already have the table extraction; only the use is new (finite human review where no checker exists), not a mechanism.
