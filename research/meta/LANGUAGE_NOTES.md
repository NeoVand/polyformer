# LANGUAGE_NOTES: designing a language for the machine we actually have

For the orchestrator (Opus), who is designing the in-model language at Neo's request, 30 Oct 2026. This is a
thinking-partner memo, not a spec. Facts from the record carry their file; the history is from my own knowledge and is
marked *unverified* where I did not fetch a source. The seed ideas in the request are labelled *(seed)*.

The short version: **the language is the instruction set of a new machine, and the machine is "a pretrained decoder
under a cache policy".** Its instructions are certified finite functions evaluated by one forward pass; its control
structures are cache policies (pin, pack, scan, stack); its memory is the context; its compiler is the model itself,
and that compiler is the weak part. Design for the compiler first, the certificate second, the speed third. Keep the
core tiny. Put the facts in the weights, the program in a few tokens, and the scheduling in the harness.

---

## 1. First question: what is the machine?

Before any syntax, write the machine's datasheet. From the record:

| Resource | What it is | Cost / limit | Source |
|---|---|---|---|
| **Instruction** | one forward pass on (header Π, local view) → one token | 30–60 ms per sequential tick on H100; ~86 ms/tick in the browser; packed block-diagonal forwards amortise | REGVM, DEMO page notes |
| **Native facts** | the weights already compute single-digit sums/products, comparisons, character classes, word meanings | base model gets 33.8 % of *table* rows right but knows the *facts*; one 2,560-number vector reaches 99.7 % of rows | BIGIDEA, UNIVERSAL |
| **Lookup** | attention = content-addressed fetch over the context; a finder head exists in every tested model | fails on near-duplicate names (cosine > 0.3), hubs with 249 events, tables > 2–4k rows | CIRCUITS, REGVM, ANOMALIES A3–A5 |
| **Memory** | the KV cache; segments with restarted positions can be reused (pin, packing) | position must be adjacent to Π (gap of 4 drops certification 55→45/55); caches carry their history unless built cold | INSIGHTS §2.8, GATE2 G5 |
| **Pointer** | where we are in the input | the weakest organ: plain decoding fails at the pointer first; a bounded window cannot hold it (PTR theorem) | BRIDGE, THEOREMS PTR |
| **Parallelism** | packed forwards with a block-diagonal mask | 4,096-digit add in 3.2 s H100 / 9.3 s browser; certificates are per runtime (L4 margins differ) | SCAN, scan-fix, WEBSCAN |
| **Stack** | canonical-KV frames owned by the host | Dyck/Boolean exact to depth 4,096; host compiles and keeps the stack | STACK |
| **Certificate** | enumerate the finite view set, one forward each | cost = |views|; 200 rows ≈ 3 min first time in the browser, then cached | ARITH_FORMAT, r5-harness |
| **Judgment** | a forward that answers "is this item X?" | not certifiable; measured error rate; the thing Python cannot do | SEMANTIC, Theorem C's error split |
| **Compiler** | the model writing the program from the question | **the bottleneck**: held-out compile 41/88; right program among 16 samples 25–45/88; wrong 200-row tables at > 99 % confidence | REASON, ASKQ |

Two things follow at once. First, a 200-row table is a program written in *microcode* by a compiler that errs: 200
chances to write a fact it already knows wrongly, at 99 % confidence, and 1,100 tokens of output for "2 + 2". The
representation was chosen for the certificate's convenience (DEMO_DESIGN: "the expanded table is both the certificate
and the executable") and never for the compiler's. Second, the pieces of a proper language already exist in the
record as separate harness features: the pinned tick (fold), packed forwards (map/zip), the scan (associative
reduce), canonical frames (stack), `use` lines (a library), anchors (reading in place), Theorem C (composition). Nobody
has yet called them a language or given them a type system.

## 2. What the history says, instruction by instruction

Each item: the historical move, then the lesson for this machine. Attribution is from memory and *unverified* unless
noted; check before citing.

**Wilkes, microprogramming (1951).** The instruction set of a computer is itself a program for a lower machine, held
in a control store as a table. *Lesson:* Savant's tables are microcode. The leap is to build the layer above it: a
small instruction set (certified macro-ops) that the compiler targets, so that programs are a few instructions and
the microcode is certified once per device, never rewritten per question. Microcode also made CISC possible: one
instruction = many micro-steps. Here: one library op = one packed forward or a short certified fold.

**Backus, FORTRAN (1957), and his 1978 Turing lecture "Can programming be liberated from the von Neumann style?".**
FORTRAN won because its compiler produced code as good as hand-written assembly; the compiler, not the syntax, was
the product. The lecture proposed FP: function-level programming with a handful of *combining forms* (composition,
construction, insert = fold, apply-to-all = map, condition) and an *algebra of programs* that lets you reason about
compositions. *Lesson:* (i) the compile step is the product: measure tokens-per-program and compile accuracy before
anything else; (ii) the combining forms are the language; the primitives are a library; (iii) an algebra of programs
is exactly what a certificate-by-composition needs (Theorem C is one law of that algebra; P² for scan and the STACK
lemma are two more).

**McCarthy, Lisp (1960).** Code is data; `eval` is written in the language it evaluates; the program is a list the
machine can inspect and rewrite. *Lesson:* the program already lives in the context as tokens the model can read, so
the model can be its own metacircular evaluator *and* its own program editor. A repair loop that resubmits the same
call verbatim (REASON: 928/967) is a machine without the ability to read its own program; design the program as data
the model is trained to inspect (e.g. the short counterexample from a failed check).

**Iverson, APL (1962) and "Notation as a Tool of Thought" (1979 Turing lecture; the five criteria are, from memory:
ease of expressing constructs, suggestivity, subordination of detail, economy, amenability to formal proof).**
Arrays as the data, a few operators (reduce `/`, scan `\`, outer product) lifting scalar functions to arrays by rank.
*Lesson:* rank polymorphism is the right abstraction for a machine whose parallelism is "the same forward on many
blocks": a scalar certified function plus a combinator is a certified array program. Use Iverson's five criteria as
the design checklist; "subordination of detail" is the direct cure for 200 rows.

**Chuck Moore, Forth (1970).** A stack machine with a tiny inner interpreter, words defined from words, and a
dictionary that grows. *Lesson:* STACK's canonical-KV frames are a Forth machine; the library is the dictionary; new
words are certified by composition of old ones. Forth's inner interpreter is a few lines, like the 40-line clock. The
risk Forth also teaches: postfix is dense but unfamiliar; the model's prior over Forth is thin.

**Codd, the relational model (1970) and SQL.** Say what, not how; a closed algebra (operators take relations to
relations) so compositions always type-check; an optimizer chooses the plan. *Lesson:* for programs over items in the
context (lists, logs, documents), a declarative query is the natural surface, the *harness* is the optimizer that
picks pin/pack/scan/stack, and closure is what makes composition certifiable. Prior art lives here (LOTUS, BlendSQL,
Palimpzest): the delta is execution inside the model under certificate.

**Church, Schönfinkel, Curry, Turner: λ-calculus, SKI, and combinator compilation (SASL, 1979).** Everything from
three combinators; compile a rich surface to a tiny core; de Bruijn indices make variables roles instead of names.
*Lesson:* certification cost is proportional to the core, not the surface. A core of five combinators and a dozen
native functions is a certificate of a few thousand forwards, once. The record's own LEAP.md asked for de Bruijn
roles ("alpha-equivalence by construction"); the separation law (near-duplicate names cause errors) says the same:
let the harness allocate names from a screened, maximally separated pool, never the model.

**Hoare logic (1969) and compositional verification.** Correctness of a composition from the correctness of parts and
a rule per combinator. *Lesson:* the certificate of a program should be a *derivation*, not an enumeration: one rule
per combinator (P for fold, P² for scan, STACK's lemma for stack, trivial for map), applied to primitives certified
once. Per-program enumeration survives only for genuinely new primitives.

**RISC (Patterson, Hennessy, Cocke; 1980s).** Few instructions, each one cycle, and let the compiler work. *Lesson:*
the pinned tick is RISC; each library op should be one packed forward where possible; the compiler (the model)
chooses among few, well-separated instructions. Fewer instruction *kinds* also means the model's routing decision
("which program?") is a small classification, which is where it currently fails (ASKQ: held-out topologies 2–4/40).

**Leibniz ("calculemus"), Feynman diagrams, and Feynman on notation.** Leibniz wanted a notation in which reasoning
becomes calculation. Feynman's diagrams turned perturbation theory from pages of integrals into pictures with rules,
and the diagram *is* the computation. Feynman also tells (in *Surely You're Joking*, unverified wording) how he
invented his own trigonometric notation as a boy and dropped it because nobody else could read it. *Lesson:* a
notation is a tool for the mind that has to write it. Here that mind is a pretrained model: the notation it already
reads fluently (Python, spreadsheets, SQL, JSON) is worth more than an elegant one it has never seen. The elegance can
live in the core; the surface should be familiar.

**The pattern across all of them.** Every successful language for a new machine did three things: it exposed the
machine's real primitives (arrays for APL, the stack for Forth, relations for SQL), it hid the machine's bookkeeping
(registers, memory layout, plans), and it was judged by what its compiler could reliably produce. None of them began
by asking what certificate was easiest.

## 3. Critique of the seeds

**(seed) Native primitives in the weights, certified directly.** Right, and it is the single biggest win on offer.
Shape of the certificate: for a finite function f over domain D (the carry adder: 2 × 10 × 10 = 200 inputs, plus
the sum digit), fix a one-line instruction header Π_f ("add digits with carry") and check all |D| forwards under the
pinned policy on the deployment path, once per device; Theorem P's hypothesis is unchanged because the view is still
(Π_f, inputs) and the rows now live in the weights instead of the context. Cautions: (a) the base model's single-digit
arithmetic is "a bag of heuristics" (Nikankin et al. 2024, unverified), so expect a few rows to fail per device and
handle them by a tiny per-device patch table in context, not by retraining; (b) tokenisation: this works only for
domains whose elements are single tokens (digits in Qwen3 are; two-digit numbers are not), so the instruction set is
over *token-atomic* domains; (c) which functions are native is an empirical table to measure (digit add/mul/compare,
booleans, character class, "is this word a number"); (d) the prior art is Lewandowski–Machado–Schuurmans 2026 (per-rule
checks of a prompted model; `TAKEN.md`), so the claim is the *instruction set* and its composition, not "we check
rules". This changes what "program" means: from a table of facts to a composition of certified instructions.

**(seed) An APL-like array language with map, zip, scan, fold, stack-fold.** Right, and the key observation is one
the seed almost says: **the combinators *are* the cache policies.** map/zip = packed block-diagonal forwards with Π
shared; scan = the log-depth packed schedule over a certified monoid; fold = the pinned clock; stack-fold = canonical
frames. So the language's control structures are precisely the four things the project has already built and
certified, and the composition theorems (P, P², STACK's lemma, Theorem C) are the four typing rules. Cautions: (a)
scan needs associativity, which is a *type-level* fact about the monoid; certify it by enumeration (Light's test is
already in SCAN); (b) fold's state must be one token or a short fixed block, which bounds state alphabets; registers
(P3) and cascades are the escape; (c) arrays need a memory model: where they live in the context and who indexes them.
Given BRIDGE's pointer result, **the model must never index**; the harness streams elements into the local view, as
the clock does. The language should have no `a[i]` visible to the model, only combinators the harness executes; (d)
APL's surface is dense and the model's prior over it is thin; keep APL in the core and give the model a surface it
reads fluently (§4).

**(seed) Semantic primitives plus exact aggregation.** This is the demo and the honest answer to "why not Python",
provided it is stated with its error decomposition. The program `count(items, judge("is a complaint"))` has two parts:
a judgment the model makes per item (an error rate, measured, not certified) and an exact aggregate (certified, zero
error). Theorem C's split, P(wrong) ≤ P(a judgment wrong) + 0, is the claim, and the demo must print both numbers.
Cautions: (a) prior art is thick: LOTUS semantic operators (Patel et al. 2024), Chain of Code's LMulator, Codified
FSMs, BlendSQL/Palimpzest/DocETL; all run the exact half *outside* the model in Python or a database. The delta is
"the exact half runs in the same forwards, in the browser, under a certificate, with no runtime"; say exactly that
and search those terms first; (b) judgments can be packed into the same block-diagonal forward as the aggregation
(speed), and they should be, because that is the one thing the Python twin cannot do in one pass; (c) do not let
"semantic" become an excuse for untestable claims: every judgment primitive ships with a labelled held-out set and
a reported accuracy.

**(seed) The "why not Python?" answer.** A crisp form: *"Because here the judgment and the arithmetic are the same
kind of operation, a certified forward pass; there is no boundary to cross, no runtime to trust, and the certificate
of the exact half is the same object as the test of the judgment half."* And the honest limits, stated in the same
breath: for pure arithmetic on numbers typed by the user, Python wins and we say so; the language exists for programs
whose *data is the model's own context* (what it is reading) and whose *operations mix meaning and exactness*. A
reviewer who hears both halves will trust the second.

## 4. A design to argue with

Five layers, bottom up. Each layer is certified once, and each certificate is a derivation from the layer below.

**L0 Native instructions.** Finite functions over token-atomic domains, computed by the weights under a one-line
header: digit add-with-carry, digit multiply, digit compare, boolean and/or/not, "next state of a 2–4-state
automaton", character class, small modular counters. Certified per device by enumeration (hundreds of forwards each);
failures patched by a tiny in-context row, not retraining. Measure first which functions the base model gets at
≥ 99.9 % with a margin; that table *is* the ISA.

**L1 Library ops.** add, sub, compare, count, cycle, parity, match, and the semantic judges. Each is an L0 function
plus one combinator (add = scan over the {K,P,G} monoid then map, as SCAN already does; count = fold; match = fold of
a KMP table). Certified by the combinator's rule, cached per device. The `use` line of LIBRARY_FORMAT is the right
idea; the model should emit names, never rows.

**L2 Combinators = cache policies.** `map f xs`, `zip f xs ys` (packed), `scan m xs` (log-depth, m certified
associative), `fold f s xs` (pinned ticks), `stack g xs` (canonical frames, visibly pushdown), `filter p xs` and
`judge q xs` (packed semantic forwards, uncertified, measured). Typing rules: fold needs a finite state; scan needs a
monoid; stack needs a visibly pushdown alphabet; map needs nothing. The harness refuses a program whose types do not
fit (this alone removes "a finite-state table for a stack task", the BBH boolean 22 %).

**L3 Surface syntax.** What the model writes. Four candidates, with the test that decides between them in §6:
- *Python subset* (`sum(1 for x in items if is_complaint(x))`): the highest prior of any notation the model has
  seen; grammar-constrain decoding to the subset (type-constrained decoding exists); semantics mapped to L2 by a host
  translator. Risk: Python's semantics are not the machine's (indexing, mutation), so the subset must forbid them.
- *Spreadsheet formulas* (`=SUMIF(A:A, "complaint")`, running totals as a column): the most widely used programming
  notation on earth and extremely well represented in pretraining; declarative dataflow; columns are arrays, running
  totals are scans, SUMIF is judge-then-aggregate. A dark horse worth one pilot.
- *SQL-like* (`SELECT COUNT(*) FROM items WHERE judge('complaint')`): Codd's closure; prior art LOTUS is a Pandas-like
  API, so SQL is both familiar and differentiated.
- *APL/J-like* or *Forth-like*: densest, closest to the core, thinnest prior. Keep as the core's own notation, not
  the model's.
My bet before measurement: a Python subset over an FP/APL core, because compile accuracy will dominate. But the
record's lesson is to measure, not bet.

**L4 Natural language.** The question. Compile = L4 → L3. This is where 41/88 and 25–45/88 live. The language can
help the compiler in three concrete ways: short programs (tens of tokens, so fewer chances to err), a small
instruction set (routing becomes a small classification), and a *characteristic sample*: every compiled program comes
with its W-method suite of short cases rendered in the question's own words, so a wrong compile is caught by a
short test or by the user, which is the surviving form of "short teaches long" (BULLETIN_2, GATE2 G3).

**Cross-cutting rules.**
- *Reading in place:* operands are spans of the question, constrained at decode time (already done on 29 Oct); the
  program never restates data.
- *Names by the harness:* state and event names are allocated from a pool screened by embedding separation; the
  model never invents a name.
- *Observable state:* every intermediate value is a token stream (Turing's "note of instructions"), so a run is
  replayable and the page can show it.
- *The harness computes nothing about values; it schedules.* Packing, scan trees, frames, caching, name allocation
  and type checks are scheduling and bookkeeping. This keeps the "not a tool call" story honest and extends it: the
  runtime is a scheduler of certified forwards.
- *Certificate algebra:* a program's certificate is the conjunction of its primitives' cached certificates plus a
  type derivation. Enumeration only for new L0/L1 entries.

## 5. What this buys, in the record's own numbers

- "What is 4096 plus 77?": 1,100 tokens and ~4 minutes (ARITH_FORMAT, DAUDIT item 6) → one `use add` line and two
  anchors, 70 tokens, with the 200-row device certificate cached (r5-harness2, 29 Oct 03:53). With L0 native digits
  the 200-row certificate shrinks to a one-line header plus 200 forwards once per device.
- The compile failures ASKQ found on Mealy tables (wrong rows at > 99 % confidence) cannot occur when there are no
  rows to write.
- Speed: fold → scan is 250 s → 3.2 s on H100 for 4,096 digits (SCAN); in the browser 337 s → 9.3 s (WEBSCAN).
- Nesting: `stack` makes BBH boolean 250/250 where tables scored 22 % (STACK; note the host currently compiles the
  question with Python's `ast`, so the compile step is not yet the model's).
- The demo program fits on one line, which is what an ML researcher will read.

## 6. What to measure first (each ≤ $50, most $0)

1. **Which surface does the base model already compile?** Take the 88 held-out compile items and 30 of DAUDIT's
   prompts. Ask base Qwen3-4B (no training) to write each in the four L3 candidates, with a host parser and a host
   reference executor. Score: parse rate, semantic correctness against the reference, tokens per program. The syntax
   with the best zero-shot compile accuracy is the one the model "already speaks". $0 on CPU/laptop or a few dollars.
2. **The native ISA.** For digit add-with-carry, multiply, compare, boolean ops: 200–1,000 forwards each under a
   one-line header on the deployment path; record pass rate and margin distribution per device (H100, L4, M4). $0–10.
3. **One end-to-end program in the browser:** `count(judge(items, "complaint"))` over 1,000 items with packed judgment
   forwards and a certified scan; report judgment accuracy on a labelled set, the aggregate's certificate, and wall
   time. This is the demo's seed. ≤ $20.
4. **Characteristic samples:** for each compiled program, generate the W-method suite (Lean already has `w_method`)
   and measure how many wrong compiles from ASKQ's 88 a ≤ 8-case suite catches with a correct oracle (E3 found 57/60
   by 16 cases for tables). $0.

Register the four before running them, with the number that would make you drop a candidate syntax.

## 7. Prior art to search before any claim

Search terms, in the order of risk: "LLM semantic operators" (LOTUS, Patel et al. 2024; Palimpzest; BlendSQL;
DocETL); "Chain of Code LMulator"; "Codified finite state machines LLM"; "Large Language Model Programs" (Schlag et al.
2023); "program-aided language models" (PAL, PoT); "looped transformers as programmable computers" (Giannou 2023);
"Percepta WebAssembly interpreter transformer"; "universal computation intrinsic language model decoding"
(Lewandowski 2026, per-rule checks); "DSL in-context learning LLM new language"; "type-constrained decoding" (PLDI
2025, Synchromesh); "neural compilation"; "instruction set architecture for language models"; "Backus FP combinators
neural"; "spreadsheet formulas LLM" (there is a line of FlashFill/Excel-formula work from Gulwani's group); "semantic
parsing to SQL certified". Also check Iverson 1979 and Backus 1978 for the exact wording of the criteria before quoting
them.

## 8. Taste, and the traps I would avoid

- **Do not ship forty primitives.** Five combinators and a dozen natives. Every extra primitive is a routing error
  waiting to happen and a certificate to maintain.
- **The demo program must fit on one line and be readable by a stranger.** If the page needs a paragraph to explain
  the program, the language is wrong.
- **Do not hide the harness.** Print the scheduler's line count and say what it does (schedules, allocates names,
  checks types). The record's credibility came from "the clock is 40 lines and computes nothing"; keep that.
- **Do not let the certificate dictate the representation again.** That is the assumption that produced 200-row
  tables. The order is: compiler reliability → user-readable programs → certificate by composition → speed.
- **Name it.** The record's results that stuck had names (Savant, Loom, Theorem P). A language with a name and a
  one-page reference card is a thing people can argue about.
- **Beware the second Frankenstein.** Neo rejected K0⋈H as "an assembly". A language with Python syntax, APL core,
  SQL for queries and spreadsheet cells for state would be the same mistake. One surface. One core.
- **Keep the tempo.** This is programme twenty-six if it is run like the others. One spec, one set of four
  registered pilots, one decision, then the demo. The meta-report's rules apply here first.

## 9. Questions back

1. What fraction of DAUDIT's 156 prompts are expressible as `judge`+`aggregate`, `fold`, `scan` or `stack` programs
   over the question's own text? If it is under half, the demo battery, not the language, needs to change.
2. Is the base model's zero-shot compile into a Python subset already better than r4's trained compile into tables on
   the 88 items? If so, training has been teaching the wrong target language.
3. Which L0 natives pass at ≥ 99.9 % on Qwen3-4B's deployment path? That table decides whether "facts in the weights"
   is real or a hope.
4. Can the host's `ast` compile in STACK be replaced by the model writing the prefix form directly, and at what
   accuracy? That is the first test of L3 for nesting.
5. What is the one-sentence pitch when a researcher says "I'd just call Python"? Write it before the design, and make
   the design serve it.
