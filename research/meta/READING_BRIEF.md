# Reading brief: six papers, one coherent read

You are preparing a reading document for Neo, who will read it once, closely, on 31 Oct 2026, before a one-week
sprint. Your job is to turn six papers into one coherent, honest read: what each proves, under exactly what
hypotheses, what it leaves open, and how the six fit together as one map. You are a reader and a cartographer, not a
brainstormer: propose nothing, pitch nothing, judge novelty only where the papers' own text settles it.

## The project, in four lines (so you know what to look for)

Savant is a Qwen3-4B chat model fine-tuned to write a small finite-state program from a question, certify every row
of that program with its own forward passes, and run it inside its own decoding under a fixed KV-cache policy
("pinned": keep the program's cache, show only the current (state, event) block, restart positions). Theorems in Lean
say the per-row certificate is necessary and sufficient for exactness at every length under that policy, and that no
finite test certifies decoding that keeps its history. The programs are currently literal transition tables (200 rows
for addition); the next step is a language in which programs are a few tokens, facts live in the weights, and control
structures are cache policies (fold = pinned ticks, scan = packed log-depth forwards, stack = canonical frames, map =
packed forwards). The question Neo is reading to answer: *what, exactly, is already proven or built by others, and
where is the honest edge?*

## The six papers (fetch the full text; the abstract is not enough)

1. **Lewandowski, Machado & Schuurmans (2026).** *Universal computation is intrinsic to language model decoding.*
   arXiv 2601.08061 (use the latest version). Companion: Schuurmans, Dai & Zanini (2024), *Autoregressive large
   language models are computationally universal*, arXiv 2410.03170, for the Lag-system construction.
2. **Cai, Shin & Song (2017).** *Making neural programming architectures generalize via recursion.* ICLR 2017,
   arXiv 1704.06611. Read §3.3 (verification) with care.
3. **Chow (1978).** *Testing software design modeled by finite-state machines.* IEEE Trans. Software Eng. SE-4(3):
   178–187. If the PDF is unreachable, substitute **Lee & Yannakakis (1996)**, *Principles and methods of testing
   finite state machines: a survey*, Proc. IEEE 84(8), and say so; read the W-method, the state-bound assumption, and
   checking sequences. Note Moore (1956, *Gedanken-experiments on sequential machines*, Automata Studies) as the
   origin of the negative result; quote its Theorem 2 if you can reach the text.
4. **Patel et al. (2024/2025).** *Semantic operators: a declarative model for rich, AI-based analytics over text*
   (the LOTUS system), arXiv 2407.11418 (latest version). Read the operator definitions, the optimizer, and exactly
   where the LLM is called versus where ordinary code runs.
5. **Li et al. (2024).** *Chain of Code: reasoning with a language model-augmented code emulator.* ICML 2024,
   arXiv 2312.04474. Read the LMulator design and the ablation where the LM alone emulates code.
6. **Brandoit, Fyon, Braipson, Clara, De Geeter, Sacré, Ernst & Drion (2026).** *Length-independent state tracking
   under a parallel scan.* arXiv 2609.32447. Read Definition 2.1, Theorems 3.1–3.3 and 4.1 and Appendix F.

Optional seventh if time allows: **Abbe, Bengio, Lotfi, Sandon & Saremi (2024)**, *How far can transformers reason?
The globality barrier and inductive scratchpad*, arXiv 2406.06467, §3.2.2 and Appendix C.2 (history removal and
position re-indexing).

## Rules (these matter more than speed)

- **Fetch and read the full text** of each paper (arXiv HTML or PDF). Do not write from memory or from the abstract.
  If a paper or section cannot be reached, say "not reached" and do not fill the gap.
- **Quote every theorem statement verbatim**, with its hypotheses, and give the section or page. Where a hypothesis is
  defined elsewhere in the paper, trace it and quote that too. A theorem without its hypotheses is useless to Neo.
- **No numbers from memory.** Every number carries its table or section. If two sources disagree, say so.
- **Label every sentence of your own as INTERPRETATION** when it is not a quotation or a paraphrase of the text.
- **Do not pitch, propose or rank ideas.** Do not write "this suggests a new approach". Your output is a map.
- **Do not grade novelty beyond the text.** You may say "this paper states X" and "this paper does not treat Y";
  you may not say "therefore Savant's claim is new".
- Read-only. Spend nothing. Write one file: `research/meta/READING.md`. No other outputs.

## What to write (one document, 5,000–7,000 words, in this order)

**0. How to read this document** (100 words). Reading order for the six, with an estimated time for each, and which
sections of each paper Neo should read in the original afterwards.

**1. One section per paper**, in the order above. For each:
- *The claim in one sentence*, in plain words.
- *The exact statements*: each main theorem or construction quoted verbatim with hypotheses and location.
- *The model of computation they assume* (what the "machine" is: a prompted LLM with fresh calls; an NPI with an
  external call stack; an FSM with a bounded state count; a dataframe with LLM-backed operators; a code emulator; a
  recurrent network under a parallel scan). Be concrete about what is inside the network and what is outside it.
- *What is checked, and how*: what their verification or certificate covers, what it assumes, who runs it, and its
  cost. Quote the sentence where they say what their check does *not* cover.
- *Measured results*, with table references.
- *What the paper explicitly leaves open*, quoted from its limitations or future-work text.
- *Where it touches Savant*: two or three sentences, as INTERPRETATION, saying which of the project's elements this
  paper already contains (fresh-call harness, per-rule check, history removal, finite verification set, semantic
  operator, LM emulation of code, per-step cell condition) and which it does not mention.

**2. The map** (the synthesis Neo actually needs):
- A table with one row per paper and these columns: machine · what the model writes · what runs inside the network ·
  what runs outside · certificate (yes/no; of what; who checks) · length guarantee (none / empirical / proven, with the
  hypotheses in five words) · scale (model size, steps or digits reached).
- Three lineages, each in a paragraph with quotations: (a) finite verification ⇒ unbounded correctness (Cai → Schuurmans
  → Lewandowski; and Moore/Chow as the testing-theory ancestry); (b) exact state in recurrent networks (Brandoit, with
  Casey 1996 and Bugaud 2026 named as neighbours if the paper cites them); (c) LLM judgment plus ordinary code (LOTUS,
  Chain of Code), with the exact boundary between the two in each system.
- A glossary mapping each paper's notation to one common vocabulary (program/table Π, state, event, view, pinned
  policy, certificate, row), so Neo can read all six in one language.
- *Disagreements*: where two papers assume different things about the same object (for example, Lewandowski's fresh
  calls vs Abbe's in-context history removal; Chow's output-sequence semantics vs a final-output check), stated
  without resolving them.

**3. Questions to hold while reading** (ten at most, one line each). These are the questions whose answers decide the
sprint, for example: Does Lewandowski's harness correspond to the pinned policy inside one decoding run, or only to
fresh calls? What state bound does Chow's completeness need, and who supplies it for a decoder? Where exactly does
LOTUS call the LLM, and could that call be the same forward as the aggregation? What does Chain of Code's LM-only
ablation score, and on what? Does Brandoit's Theorem 3.2 cover blocks of several steps or only single steps? Write
the question, then the paper and section where Neo will find the answer.

**4. What you could not verify**, in a list: unreachable texts, quotes you could not locate, claims in the project's
own prior-art notes (`RESULTS_LOCK` §8, `FRONTIER.md` §A) that the papers' text does not support as worded. This list
is as valuable as the rest.

## Style

Plain sentences. No bullet-point confetti inside the per-paper sections; write paragraphs with quotations set off.
Every quotation under 60 words. No praise of any paper, and no praise of the project. Neo will read every line.
