# NEW_MODEL: the register model

Fable 5.1, 30 Oct 2026, for Neo and the orchestrator. Read-only analysis; nothing here was run. Every number carries its
record; numbers from the orchestrator's 29 Oct runs are marked *unaudited* as they are in `WEFT.md`.

## 0. To Neo, first

You asked what the dream was. `NEO_CONDITIONS.md` has it in your words, and it is a good dream: one normal model that
writes a short program for a plain question and runs it inside its own forward passes, exactly, with a certificate,
and stays a normal model. Here is the uncomfortable and the comfortable fact at once. **Every part of that model has
been built and measured in the last four days, in three different worktrees, and nobody put them in one model.**

- The **executor** exists: Savant's pinned tick runs unseen tables with every tick bitwise equal to a certified row
  (G1: 512/512 and 511/512 held-out tables, 160,000 ticks; `PROMPTBOX.md` §6.7).
- The **control** exists: Savant r3, with no training on it, ran 13 register-machine programs with loops, branches,
  memory and pointers, 11,882 real ticks, all bitwise equal to certified rows, all answers equal to Python's
  (`REGVM.md` §H.1). The programs were 1–37 lines, not 200 rows.
- The **ALU** exists, in the untouched pretrained weights: base Qwen3-4B certifies digit add with carry 200/200,
  digit multiply 100/100, compare 100/100 from a few lines of prompt, on an H100 and on your M4 in the browser
  stack (`WEFT.md` §8, §14; *unaudited*).
- The **language repair** exists: 400 steps of the Stage 2r mix put GSM8K back to 91.5% and perplexity ratios at or
  under 1.06 (`PROMPTBOX.md` §6.11).
- The **architecture statement** exists: the pinned tick is ordinary greedy decoding under one cache policy, and it
  is the only exact cell of a 40-cell factorial plus three published eviction baselines (`BIGIDEA.md` H2b).

WEFT took the ALU and gave the algorithm to the host. Savant took the executor and gave it 200-row tables. REGVM took
the control and kept the ALU as 648 rows of in-context tables, at 52 seconds for a 4-digit multiply. The model you
asked for is the three of them in one set of weights, with the tables gone. That is a week of assembly and training,
not a leap of theory, and I will not pretend otherwise. But it is your model, it meets ten of your twelve conditions
outright, and it has an honest theorem and an honest demo. The two conditions it does not fully meet (generalisation
to adversarial rule families, and the from-scratch architecture) are the funding ask, and I say exactly why below.

## 1. Where my week plan conflicts with your conditions, and the revision

My §3.0 week plan in `META_REPORT.md` was written to Neo's "one week, $1–2k" before I had `NEO_CONDITIONS.md`. It
conflicts in four places, and the orchestrator was right that it shrank the dream.

| my plan said | condition it breaks | revision |
|---|---|---|
| "No new model is trained this week" | 2, 3, 10 | Train. The recipe is known and cheap: Stage 1 was $11.9 per seed, Stage 2r about $3, a full gate about $8 (`PROMPTBOX.md` §6.7, §6.11). The week trains one model, two seeds, under $150 of GPU. |
| "The harness as a scheduler" running library ops, scan, stack | 2 | The harness is a **bus**: it moves tokens by address and evicts; it never chooses an algorithm. The algorithm is the model's program. The ALU's internal schedule (a carry-lookahead over the model's own digit forwards) is a fixed certified microarchitecture, as in every CPU, and is labelled as such. |
| Gate A: "a surface syntax chosen by measured zero-shot compile accuracy" | 6, 8 | P4 killed zero-shot compile (20/88 against the trained table compiler's 41/88; `WEFT.md` §12). Notation does not fix comprehension; training does. The compiler is trained, on the register ISA, and the 88 items are a registered prediction, not a gate for choosing syntax. |
| Three program kinds, library arithmetic first | 6, 7 | One machine, one ISA, every program in it: arithmetic, the robot, the cube trackers, Dyck and boolean via the stack, judge-then-count. No "library arithmetic" path that bypasses the model's control. |

What stands from my plan: the frozen claim table, the live prior-art gate before any pitch, one builder and one
auditor, no decisions after 23:00, no public push before the audit gate, and the sentence that a Nature-calibre
theoretical advance is not a one-week object. The week produces a model, an arXiv paper nobody can embarrass, and a
demo that does not disappoint. The theory depth comes with funding, and §2.3 says what it is.

## 2. The model: Savant-R, a decoder with a register and a bus

Working names: the architecture is **register decoding**; the model is **Savant-R**; the language is **Weft**
(keep the loom: lanes are registers). Names are the orchestrator's to change.

### 2.1 The machine

A pretrained chat decoder (Qwen3-4B) fine-tuned with a small adapter, run under one cache policy. Four parts, three of
them the model's.

**Inside the model (every one of these is a forward pass of the model's own weights):**
1. **The compiler.** From a plain question the model writes a program of a few lines in a register ISA
   (REGVM_FORMAT's machine: a program counter, a flag, named registers holding digit strings, a small cell memory,
   18 opcodes). "What is 50!?" is four lines. A cubie tracker is two. Routing is the model's: it writes a program for
   a computation and answers in words otherwise (Stage 2r: 0% programs on GSM8K, `<exec/>` on 767/768 family
   prompts; `PROMPTBOX.md` §6.11).
2. **The control.** Fetch and decode are the model's lookups: (line label, field) in its own program, (opcode, flag)
   in the fixed CTRL table. Savant r3 does this today with 100% of P and CTRL rows and margins of 3.5–12.9
   (`REGVM.md` §H.1). The six fetch lookups of one instruction are independent, so they pack into one forward
   (SCAN's block-diagonal mask).
3. **The ALU.** Every digit operation is a forward on a micro-prompt the model already knows how to answer: `dadd`,
   `dmul`, `cmp`, `band`, `bor`, `succ`, `pred`. No table in context. Base Qwen3-4B certifies these in full
   (*unaudited*); training must keep them certified (Savant r3's `dadd` fell to 183/200 after table training,
   `WEFT.md` §8, so the ALU rows go into the training mix as rows, with a registered bar).
4. **The register.** The state between ticks is one block of a few tokens, the model's own argmax outputs, held in a
   fixed cache slot, replaced every tick. The context never grows. The user never sees it.

**Outside the model, the bus (about 20 lines, fixed, program-independent, computes nothing about values):**
- `READ(addr)`: copy the addressed token (a register's digit, a memory cell, the next event of the input) into the
  window.
- `WRITE(addr, token)`: put the model's output token into the addressed slot.
- `EVICT`: drop the finished (state, event) block from the cache, keep the persistent prefix Π, restart positions.
- The ALU microarchitecture: for `add` over n digits, the fixed carry schedule over the model's `dadd` forwards
  (sequential fold, or SCAN's log-depth packed schedule as a labelled speed option with the same certificate).

The bus is the clock, shrunk to its floor. §2.5 says why there is a floor.

### 2.2 Each choice against the record

| choice | the alternative | why this one |
|---|---|---|
| the state is a token in a fixed cache slot | a vector in the residual stream (LATENT-1) | A finite certificate needs a finite state. LATENT-1's 0.5B state was "exact" at the 0.99 bar on 4 of 5 seeds, never certified, after a full fine-tune that destroyed language (INSIDE: WikiText 19 → 2×10⁴). In-model latent recurrence collapsed (INMODEL), QINTERP2's in-layer program reader got 0/32, L-AIM collapsed. The token is the snap, and the snap is what makes Theorem P's certificate finite. |
| the policy is Π + a fresh pair + restarted positions | sliding windows, StreamingLLM, H₂O, TOVA, Delethink chunks | H2b: the pinned cell is 8/8 exact; every other of 43 cells fails 3–8 of 8 runs; StreamingLLM as published and H₂O/TOVA at equal budget are 0/8 and evict most of the program (`BIGIDEA.md` H2b, F1–F9). |
| control inside, by lookup | control in the host (WEFT) | REGVM §H.1: 13/13 programs, 1,754 instructions, every control tick bitwise. Zero-shot. |
| the ALU native, in the weights | 648 rows of ROM in Π (REGVM) | WEFT §8/§14 (*unaudited*): 200/200, 100/100, 100/100 on H100 and M4. REGVM's 4-digit multiply took 1,169 ticks and 52 s with the ROM in context; the ALU rows disappear from Π and the digit function stays one forward. |
| compact programs | 200-row tables | ASKQ: the right table is among 16 samples for 25–45 of 88; DAUDIT: 2/3 of state tables fail to compile. REGVM's programs are 1–37 lines. 70 tokens against 1,100. |
| compile trained on a generator, not zero-shot | zero-shot compile into a nicer surface | P4 KILL: 20/88 zero-shot against 41/88 trained (`WEFT.md` §12). Held-out phrasings already 96–97% when trained (`PROMPTBOX.md` §6.10). |
| language term from step 1 | repair at the end | Stage 2r fixed GSM8K from 4% to 91.5% in 400 steps and nothing fell; there is no reason to pay the collapse first. |
| no RL this week | GRPO for unprompted use | PROMPTBOX HR1–HR3 all fail: RL "kept everything and taught nothing new"; routing was already right from SFT (`PROMPTBOX.md` §6.12). |
| one adapter, one model | per-skill adapters (FIVE) | The skills are programs in context; the one thing in the weights is the executor and the ALU. DIAG put ten skills in the weights and lost language (ratio 2,340). |

### 2.3 The architecture statement, and the from-scratch model it points at

**The statement.** A decoder-only transformer under the register policy is a recurrent network whose state is a
discrete symbol in its own cache. The policy is not a harness trick; it is the recurrent cell. H2b is the evidence
that this cell is unique among the natural cache policies, and Theorem P is the proof that under this cell a finite
check is necessary and sufficient for exactness at every length. "The clock is attention" (BIGIDEA H2) is true for the
cell and false for addressing (§2.5).

**What the funded, from-scratch model changes (condition 10).** Three things become native:
1. **The register as cache slots**: a fixed set of KV slots that the model writes by emitting a token and reads by
   attention; the bus's `WRITE` and `EVICT` become the cache update rule.
2. **Role-additive lookup heads.** ANATOMY found Savant's lookup heads are about 95% role-additive with a 2–5 nat
   context-dependent residual, "so there is no weights-level certificate N* for this model" (`anatomy/circuits`
   report). A from-scratch architecture whose fetch heads are exactly role-additive (a constructed-attention form,
   learned) would make the control certificate program-independent: **certified once for all programs**, which the
   fine-tuned model cannot honestly claim (§2.5). That is the theoretical object worth a year, and it is the one
   Percepta reaches by construction and we would reach by learning.
3. **Addressing in attention** for bounded memories: Percepta's cumulative-sum instruction pointer is the constructed
   precedent; the question is whether a learned one certifies.

The week's model is the proof of concept for all three. The pitch sentence: "Here is a 4B chat model that writes
and runs its own programs exactly, with a certificate, and still talks. Here is the architecture that makes the
certificate program-independent. We need N months to train it."

### 2.4 Training

From base Qwen3-4B, LoRA (PROMPTBOX's rank and layers), two seeds and an answer-only twin, one stage of about
1,200 steps, then the 2r mix for 400 steps. The mix, from day one:
- **Executor rows** (as Stage 1): random pinned tables over the screened name pool, REGVM-shaped P tables with filler
  destinations and halts, hub tables (REGVM's `laglike_table` lesson: the hub self-pair and the halt after a hub row).
- **Control rows**: CTRL and G as fixed tables; fetch rows over random programs in the ISA.
- **ALU rows**: the native micro-prompts for `dadd`, `dmul`, `cmp`, `band`, `bor`, `succ`, `pred`, every case,
  weighted so the margin rises rather than falls (registered bar: `dadd` ≥ 198/200 with the hybrid prompt, min margin
  ≥ 3; kill at < 190).
- **Compile targets** from a procedural generator: PROMPTBOX's `gen` families, REGVM §D's multiply/GCD/boolean, and
  the demo families (calculator ops, dead-reckoning robot, cubie trackers, Dyck/boolean via the stack register,
  judge-then-count). Six phrasings per family, two held out; the registered 88 items never in training.
- **Language**: 25% ordinary data in the base's style, 20% general, KL to the base on both at coefficient 1.0
  (`PROMPTBOX.md` §3.9, §6.11). GSM8K, MMLU, WikiText-2 and HumanEval ratios are a gate, not a report.

Cost at the measured H100 rate ($5.22/h): training about $30 for two seeds and the twin, gates about $40, the ONNX
export about $40 (webexport did it once), DAUDIT about $20. Under $150 GPU for the model, under $300 with the demo.

### 2.5 The certificate, honestly

**Theorem R (to state and prove this week; a composition of what is in Lean).** Fix the register policy and a program
P. The run of P is exact on every input of every length iff every micro-row the run reaches is exact, where the
micro-rows are of three kinds:
1. **ISA rows**: (op, operand digits) → result. Program-independent. Finite: 200 + 100 + 100 + 4 + 4 + 20 cases.
   Certified once per device and runtime, cached (SCAN: the H100 certificate passes, the L4 one fails and certifies
   its own; the browser caches it in IndexedDB).
2. **Control rows**: (line, field) → token and (opcode, flag) → next. CTRL is fixed and certified once. The program's
   own fetch rows are **per program**: six per line, computed in one packed forward when the program is written.
3. **Bus correctness**: a classical program of about 20 lines, tested by ordinary means and open on the page.

Sufficiency is Theorem P (Lean) composed by Theorem C (Lean) with the ALU schedule lemma (SCAN, corrected version).
Necessity is Theorem P's converse, row by row: a reachable uncertified row has an input that exposes it.

**What a skeptic will say, and the answers we can give.**
- *"Certified once? The fetch rows are per program."* Yes. The ALU and CTRL are once per device; the program's control
  certificate is six rows per line, about one forward. We say "certified per device for the machine, per program for
  the program, at the program's own size". The once-for-all control certificate needs role-additive heads, which this
  model does not have (ANATOMY) and the from-scratch model is designed to have. Never write "every program inherits
  exactness" without that qualifier.
- *"The state token is chain of thought."* No, and the wording matters. The context holds the program and one
  (state, event) pair; it never grows; nothing is written for the user to read; the register is replaced every tick.
  Call it **a register, not a transcript**: "no chain of thought in context". Do not write "no tokens". Then give the
  reason it is a token: Theorem P needs a finite state; a continuous latent state has no finite certificate, and
  every attempt at one in these weights collapsed or destroyed language (§2.2).
- *"The host still does something."* The bus. It moves tokens by address and evicts. Here is why there is a floor and
  not a zero: a certifiable executor has a finite window (Theorem P enumerates it), and H2 showed that a decoder
  seeing only Π and a bounded window cannot locate the next event of a long tape, because that needs log T bits the
  window does not carry (`BIGIDEA.md` §2). So addressing of unbounded memory cannot be inside the certified function.
  The bus is that addressing and nothing else, specified in three operations, and the page shows its source.
- *"Python wins on arithmetic."* For numbers the user typed, yes, and the page says so. The model's reason to exist is
  programs over its own context that mix judgment and exactness (§4), and the scientific claim about what a network's
  forward passes can be.
- *"The ALU is just the pretrained model answering 7+8."* Yes: that is the point. The instruction set of this computer
  is competence the model already had, certified exhaustively. Nobody has certified a pretrained model's inherited
  arithmetic exhaustively and used it as an ISA (as far as the 30 Oct searches went; §5 re-checks).

### 2.6 The twelve conditions

| # | condition | this week | note |
|---|---|---|---|
| 1 | one model, many abilities, no adapters | **met** | skills are programs; one adapter holds the executor, control and ALU |
| 2 | the LLM itself computes; shrink the clock | **met at the floor** | every digit function and every control decision is a forward; the bus moves and evicts; §2.5 says why the floor is not zero |
| 3 | plain prompt → program → run inside, unprompted | **met** | routing by SFT (0% on GSM8K, 100% on families); "inside its own reasoning" means the run precedes the words, as PROMPTBOX's `<exec/>` does |
| 4 | no chain of thought | **met as "no transcript"** | one-token register, evicted each tick; wording in §2.5 |
| 5 | exact, certified, skeptic-proof | **met** | Theorem R; every tick bitwise equal to its row; audit script; the four answers above |
| 6 | compact code | **met** | 1–37 lines; 70 tokens against 1,100 |
| 7 | one executor certified once | **half** | ISA and CTRL once per device; control per program at program size; the full form is the from-scratch design |
| 8 | generalises to new families and wording | **wording yes, adversarial families no** | held-out phrasings 96–97%; held-out *families* were 2–77% and P4 showed the failure is comprehension of adversarial rule text. Print it. Target the demo at families where compile is reliable. |
| 9 | language intact | **met** | the 2r mix from day one; gate L bars |
| 10 | a new model pointing at a new architecture | **the model yes; the architecture is the ask** | §2.3 |
| 11 | a live browser demo that does not disappoint | **met at honest sizes** | 86 ms per tick in the browser on the 4B (`polyformer-demo` note): about 700 ticks a minute; 100-digit arithmetic and 200-move robots in the browser, 1,000-digit and 10,000-move runs on the server GPU behind the page (DEMOLIVE exists). Say which is which on the page. |
| 12 | a week, $1–2k | **met** | §3: under $500 planned, over $1k in reserve |

### 2.7 The orchestrator's seed, torn apart as asked

The seed is right in its skeleton and wrong in three joints.
1. **"Compile into compact Weft code, trained on a procedural generator."** Right, and REGVM's ISA is the target, not
   a Python subset: the model must execute what it writes, and it executes lookups. Expect a modest compile gain over
   tables (register it: ≥ 45/88 against r4's 41; kill ≤ 41). The generator's job is adversarial rule phrasings, which
   is where P4's 40 wrong programs came from.
2. **"Control flow and register addressing in attention under a fixed mask, no host loop."** Half. Control, yes
   (REGVM proves it). Addressing of unbounded memory, no, for the reason in §2.5; the seed would either lose the finite
   certificate or fail on long tapes as every windowed cell did (H2 R2: 0–2 of 12). Keep the bus, specify it, show it.
3. **"The certificate over the ISA, finite, certified once; every program inherits exactness."** Only the ALU half.
   Theorem P's necessity says a reachable fetch row that is wrong gives a wrong run, and REGVM §H.3 shows fetch rows
   can go wrong after a top-up (7 of 10 P tables, ties at margin 0.0). The control certificate is per program, small,
   instant. Say so.
4. **"RL so it invokes unprompted."** Drop it this week. PROMPTBOX's RL changed nothing a registered metric could see;
   the unprompted use came from the SFT mix. Spend the money on generator diversity.
5. **Visible trace and latent steps.** Resolved in §2.5: a register is not a transcript, and latent steps are not on
   the table at this scale with language intact. Three negatives and one language-destroying positive are enough.
6. **What is new against Percepta, MicroPy and looped transformers.** (a) a pretrained chat model, learned, language
   intact; none of them is a language model or keeps one. (b) a certificate of trained weights with a machine-checked
   necessary-and-sufficient theorem; theirs are by construction (Percepta) or absent (MicroPy). (c) the ISA is
   inherited pretrained competence, certified exhaustively; none has this. (d) the model writes the program from a
   plain question; none does. (e) the architecture statement with the factorial behind it. The race risk is Percepta's
   stated next step, "combine with an LLM and train it to invoke the execution path" (`prior_art/L1` §1.4). That is
   why the arXiv date matters more than another week of polish.

### 2.8 Why it is likely to work, and the two ways it fails

Likely, because nothing in it is a hope. The executor transfers to unseen tables and to a register machine it never
saw; the ALU is already certified in the base weights on two devices; the language recipe worked once at $3; the
policy's uniqueness is measured; the demo page and the in-browser runtime exist and ran Savant r2.

It fails in two ways, each with a registered kill in §3:
1. **Training the executor erodes the native ALU** (Savant r3: `dadd` 183/200). Mitigation: ALU rows in the mix, KL to
   the base, the hybrid prompt. If `dadd` stays under 190 after one data fix, the ALU goes back to in-context ROM
   (REGVM's, certified once per model) and the "inherited instruction set" claim is dropped from the paper. The model
   still stands.
2. **Compile does not improve on tables.** Then the demo is the four families the model compiles reliably and the
   paper's compile section reports the 88 items as they are. The model still stands; the generalisation claim shrinks
   to wording.

## 3. Pilot R1 (under $50, within 24 hours), then the path

### 3.1 Pilot R1: assembly before training

**Question.** Do the three measured parts compose in one set of weights before any new training? Take **Savant r3**
(it executes REGVM's P and CTRL at 100%) and run REGVM's 13 fixture programs with (a) the ROM removed from Π and every
digit operation done by WEFT's native micro-prompt forwards on the *same* weights, and (b) the six fetch lookups of
each instruction packed in one forward. Code to join: `regvm_model.py` (ticks, certificates), `weft.py` (native ops,
packing), `bi_engine.py` (explicit per-slot cache, masks per sequence). One H100 job; estimate $10–15 including a
smoke run and a bug-fix rerun.

**Registered predictions (fix before the run).**

| id | prediction | kill |
|---|---|---|
| R1.1 | Savant r3's native ALU on the batched path: `dadd` hybrid ≥ 190/200, `dmul` ≥ 98/100, `cmp` ≥ 98/100 (r3 was 183/200 and 98/100 on single prompts, `WEFT.md` §8) | `dadd` < 170: r3 cannot carry the ALU; the pilot continues with the ROM for failing rows (hybrid), and Stage A's ALU rows become mandatory |
| R1.2 | the 10 fixture P tables and CTRL certify whole on r3, margins ≥ 3 (REGVM §H.1: 10/10, 3.5–5.75) | < 8/10 |
| R1.3 | ≥ 12 of 13 programs exact, every control tick bitwise equal to its certified row and every ALU forward equal to its certified case; every miss attributable to an uncertified ALU row | < 10/13, or any exact-certified tick that is wrong (that would be a bus bug or a Theorem R gap; stop and find it) |
| R1.4 | total forwards ≤ 5,000 against REGVM's 11,882 ticks; the 4-digit multiply under 20 s on the H100 (was 52 s) | > 9,000 forwards: packing did not land; still a pass on exactness |
| R1.5 | the bus's source is under 60 lines and reads no digit, flag or label value (REGVM_FORMAT §0's rule), checked by a reviewer who did not write it | any value read in the bus |

**What R1 settles.** If R1.2–R1.3 hold, the register model exists on r3 today, with the ROM gone where the ALU
certifies, and the week is about training the compiler and the ALU rows, the export and the page. If R1.3 fails on
control, the pinned executor does not transfer to the one-forward fetch block, and Stage A trains it (the fetch rows
are in the mix); R1 has then told us the data we need. If it fails on the bus (R1.5), fix it before anything else.

### 3.2 The path (days 1–7; gates registered the night before each run)

| day | work | gate | GPU |
|---|---|---|---|
| **1 (Fri 31)** | R1 above. Neo reads `READING.md` when it lands. Orchestrator writes the training mix and the generator's demo families; Astra/Argon run §5's searches | R1.1–R1.5 | ≤ $15 |
| **2 (Sat)** | **Stage A**: two seeds + twin, 1,200 steps, the §2.4 mix. Export pipeline rehearsed on r3 meanwhile (no cost beyond the one export) | training completes; validation curve every 300 steps: executor rows, ALU rows, compile on trained families, GSM8K-100 | ≤ $40 |
| **3 (Sun)** | **Gate 1** on the selected step (rule: highest trained-compile cell with GSM8K-100 ≥ 86, ties to the later step): G1-lite 128 held-out tables ≥ 126; ALU `dadd` ≥ 198, `dmul` 100, `cmp` 100; the 13 fixture programs 13/13 with every forward certified; compile: trained families ≥ 95%, held-out phrasings ≥ 85%, the 88 items ≥ 45 (kill ≤ 41); language: WikiText ≤ 1.10, GSM8K-400 ≥ 86.5, MMLU within 3 | pass → Stage 2r (400 steps, about $3 per seed) and the gate-L bars; fail on ALU → §2.8 fallback 1; fail on compile → §2.8 fallback 2 | ≤ $40 |
| **4 (Mon)** | Export the selected adapter merged to ONNX q4f16 (webexport); on-device ALU certificate on the M4 (WEFT §14 took 82 s for `dadd`); port the bus to the page (`weft.py` and the REGVM clock → TS; the pinned runtime exists in `src/lib/interpreter/webgpu/`); DAUDIT rerun on the new model against base and r4 | **Gate 2**: the new model beats base on DAUDIT's shared items and shows 0 certified-but-wrong answers; in-browser ticks bitwise equal to the H100's rows on 8 trained families (as the r2 export was) | ≤ $60 |
| **5 (Tue)** | Paper: Theorem R stated and proved from the Lean pieces (lean-p agent if the composition is mechanical; otherwise a paper proof with the Lean theorems cited); frozen claims table; Codex hostile read with a checklist; references verified by script | draft | API |
| **6 (Wed)** | Demo page with §4's five moments on the new model; honest-size labels (browser vs server); the audit script downloadable; release repo with run records | arXiv-ready; one human hostile read if available | $0 |
| **7 (Thu)** | Buffer; submit; ten slides: the model, the theorem, the factorial, the audit, the from-scratch architecture, the ask | done | $0 |

**Budget:** GPU ≤ $200 planned, $100 reserve; agents (Codex, agy) ≤ $200; **total ≤ $500**, leaving $1k+ untouched.
One builder agent and one auditor at a time. Every number on the page and in the paper comes from a record an auditor
has read.

## 4. The demo moment this model makes possible

The current page shows a table running. The new page shows **the model programming itself**. Five moments, one
machine, one adapter, no tables anywhere:

1. **"What is 50!?"** The model writes four lines of assembly. The page shows the program counter walking the
   model's own lines, the register filling digit by digit, every tick lit as it matches its certificate, and the
   65 digits matched by BigInt at the end. Then "and 2^200?" with the same four lines and a different constant.
   (Server GPU for these sizes; in the browser, "What is 30!?".)
2. **Poke the program, not the brain.** Mid-run, the user edits one line of the model's program (`mul` → `add`) and the
   run follows the new program from the next tick. Then the existing poke: change the register and the run follows
   the register. Together they show that what runs is the program the model wrote, executed by the model.
3. **The ghost cube as twenty two-line programs.** A corner cubie is a 72-state automaton (24 positions × 3
   orientations), an edge a 48-state one; every corner shares one program, every edge another. Twenty lanes run in
   one packed forward per move, 10,000 scrambles, the cube rendered from the twenty registers and checked against a
   simulator. The message is the compact-code message in a picture: the cube is not 4×10¹⁹ states, it is two
   programs and twenty registers. (Cubie move tables as a few lines in the program, not 1,296 rows; the certificate
   is the reached rows, about 2,200, in a handful of packed forwards.)
4. **Dead reckoning.** "A robot starts at the origin facing north and follows these 2,000 moves. Where is it?" Three
   registers, signed digits, the model's own `cmp` deciding the sign. The page draws the path from the registers.
5. **"Of these 800 invoice lines, how many are over $100?"** Judgment is a forward; the count is the model's own
   adder; the error split (judgment vs control, with control exactly 0) printed as SEMANTIC's Theorem S requires.
   This is the moment that is not a tool call: the same weights judge and add, and the certificate of the exact half
   is the same object as the margin report of the judgment half.

Every moment ends with the same line: *every step was one forward pass of this model; every forward pass equals a
row it certified before it ran; here is the audit script.*

## 5. Prior-art risk and the searches to run before any pitch

**The core claim, worded to survive:** *a pretrained chat model, fine-tuned with a small adapter and run under one
cache policy, writes a register program for a plain question and executes it with its own forward passes, exactly at
every length, with a machine-checked necessary-and-sufficient certificate whose ALU half is the model's inherited
arithmetic certified exhaustively, while remaining a normal chat model.*

**Known neighbours, to cite and not to compete with.** Lewandowski–Machado–Schuurmans 2026 (fresh-call universal
decoding; our necessity theorem is what they do not test); Schuurmans 2024; Cai–Shin–Song 2017 (finite verification
⇒ unbounded correctness); Chow 1978 / Moore 1956; Percepta 2026 (constructed interpreters, margin by construction;
announced LLM integration); Xu et al. 2026 MicroPy (59.5M from scratch, no certificate); CAEF (LoRA on LLaMA-3.1-8B
executing arithmetic steps, not exact); Giannou 2023 looped transformers (constructed program counter); Codified FSMs
ICLR 2026, Chain of Code, LOTUS (judgment plus code outside the model); StreamingLLM, H₂O, TOVA, Delethink (the
policies H2b beat); RMT / Memformer / Block-Recurrent Transformer (continuous memory tokens carried across segments,
the architectural cousin of the register; ours is discrete and certified); Certified Grokking 2026 (exhaustive margin
certificate of one learned model).

**Exact searches for Astra and Argon** (live, with dates; each result graded "kills", "forces rewording", or
"context"):
1. `"register machine" language model "KV cache" exact execution 2026`
2. `fine-tuned LLM executes its own program "every step" exact certificate attention sink`
3. `"certified" OR "verified" "instruction set" transformer arithmetic exhaustive margin pretrained`
4. `pretrained language model digit addition "all 200" OR "exhaustive" certification inherited arithmetic`
5. `"Percepta" LLM integration 2026 spotlight-vm chat` and `Tzamos transformer computer LLM fine-tune`
6. `CAEF follow-up exact arithmetic LoRA LLaMA 2026 length generalization "100%"`
7. `"Markovian" OR "Delethink" OR "chunked" reasoning carryover exact state tracking theorem`
8. `recurrent memory transformer discrete memory tokens exact state certificate` (RMT, Memformer, Titans, Infini)
9. `"program counter" attention learned exact "length generalization" interpreter fine-tune LLM 2025 2026`
10. `language model "writes a program" "executes" "without tools" "in-context" interpreter exact 2026`
11. `"Codified" OR "codified finite state" LLM predicate next_state exact 2026` (ICLR 2026 and follow-ups)
12. `neural ALU pretrained LLM "lookup table" digits certified browser WebGPU 2026`

**Kill gate for the pitch.** If any result shows a pretrained chat LLM, fine-tuned, executing self-written programs
exactly at length with a certificate of the trained weights, the claim is rewritten to the delta before anyone says
"new". If Percepta has shipped LLM integration, the paper leads with the certificate and the factorial, and the
system is "the learned counterpart", as `prior_art/L1` §1.4 already advises.

**Never claim:** "runs programs in its own forward passes" as new (Percepta, Lewandowski); "universal computation
inside an LLM" (done); "certified once for all programs" (not this model; §2.5); "no tokens" (§2.5); "the base model
already executes" (BIGIDEA H1: it does not); any number that exists only in an agent's final message.

## 6. Three decisions for Neo

1. **The wording of condition 4.** "No chain of thought in context; a one-token register, evicted every tick." If
   you want "no tokens at all", the honest answer is that no model at this scale has it with language intact, and a
   certificate of it does not exist. I would not spend the week there.
2. **The clock's floor.** Accept the bus as the architecture's memory controller, specified in three operations and
   shown on the page, with the from-scratch model as the place it goes native. If you want it at zero this week, I do
   not know how to keep the certificate.
3. **The demo's honesty labels.** Browser sizes and server sizes, printed. A 1,000-digit factorial live in a browser
   tab on a 4B model at 86 ms a tick is not this week's object; a 30! is.

Everything else is the orchestrator's to run. R1 first; register the numbers tonight; train tomorrow.
