# SKETCHPAD3 prior-art gate (30 Oct 2026)

I opened every arXiv abstract page cited here today (50 pages), and read the Cai 2017 PDF for its proof method. **OPEN** means not found in this search; it does not prove absence. This gate extends `sketchpad_gate/` and `penpaper_gate/` (29 Oct).

## 1. Calculator-complete exact arithmetic, certified, in a pretrained VLM on a canvas: **NARROW**

| Work | What it does | What it does not do |
|---|---|---|
| Cai, Shin & Song 2017, [1704.06611](https://arxiv.org/abs/1704.06611) | Learned programs (grade-school addition, sorting) with *provably perfect generalization*: a verification set covers every base case and reduction | Symbolic scratch pad, not pixels; trained from scratch; no ×, ÷ or √ |
| Lai et al. 2024 (CAEF), [2410.07896](https://arxiv.org/abs/2410.07896) | LLaMA-3.1-8B steps through seven operators, including division, on a text tape; "nearly 100%" up to 100 digits | Not exact, no certificate, no √ or gcd; one LoRA per operator |
| Price, Zaremba & Sutskever 2016, [1611.00736](https://arxiv.org/abs/1611.00736) | Neural GPU learns all decimal arithmetic operations at arbitrary length | From scratch; fails on symmetric inputs such as 0…02 × 0…02; no certificate |
| Wei 2026, [2603.29069](https://arxiv.org/abs/2603.29069) and [2602.01651](https://arxiv.org/abs/2602.01651) | Neural cellular automata on a grid: exact multiplication at 683× the training range; addition up to 1M digits | From scratch; binary; tested on samples; one operation per model |
| OccamLLM 2024, [2406.06576](https://arxiv.org/abs/2406.06576); IGC 2025, [2501.00684](https://arxiv.org/abs/2501.00684) | Exact (100%, or 98–99%) +, −, ×, ÷, √ … *inside* an LLM in one step | Built-in symbolic or hand-built calculator, not a learned procedure; bounded sizes; no certificate |
| Giannou et al. 2023, [2301.13196](https://arxiv.org/abs/2301.13196); Loom 2026, [2604.08816](https://arxiv.org/abs/2604.08816) | Hand-set transformer weights run a calculator, or C programs at one instruction per forward pass | Not learned, not a language model |

**Also checked:**
- Goat [2305.14201](https://arxiv.org/abs/2305.14201): near-perfect + and −, with × and ÷ decomposed.
- MathGLM [2309.03241](https://arxiv.org/abs/2309.03241): decimals and fractions at almost 100%.
- Lee et al. [2307.03381](https://arxiv.org/abs/2307.03381): √ approximated; length generalisation is still a problem.
- RevOrder [2402.03822](https://arxiv.org/abs/2402.03822): division is the weak operation.
- Charton gcd [2308.15594](https://arxiv.org/abs/2308.15594): only partial gcd coverage.
- Kasliwal [2610.09003](https://arxiv.org/abs/2610.09003): long-division scratchpad reaches 86.7%, and **0%** at unseen 4-digit operands.
- DFST [2511.22751](https://arxiv.org/abs/2511.22751): exact + and × at thousands of times the training length, trained from scratch.
- Back de Luca [2502.16763](https://arxiv.org/abs/2502.16763): an exactness proof (NTK), not an audit of trained weights.
- Quirke [2402.02619](https://arxiv.org/abs/2402.02619): >99.999%, not a certificate.
- Balter [2604.18203](https://arxiv.org/abs/2604.18203): VLMs read the digits (>99%) but fail the multiplication.
- Also: Abacus [2405.17399](https://arxiv.org/abs/2405.17399), Nye [2112.00114](https://arxiv.org/abs/2112.00114), NALU [1808.00508](https://arxiv.org/abs/1808.00508), Neural GPU [1511.08228](https://arxiv.org/abs/1511.08228), Visual Sketchpad [2406.09403](https://arxiv.org/abs/2406.09403), Whiteboard-of-Thought [2406.14562](https://arxiv.org/abs/2406.14562), MVoT [2501.07542](https://arxiv.org/abs/2501.07542), Chain-of-Sketch [2410.08165](https://arxiv.org/abs/2410.08165), Madan [2607.09061](https://arxiv.org/abs/2607.09061).

**What stays new.** Each piece already exists somewhere:
- exact arithmetic at any length (Neural GPU, Wei, DFST);
- certification of a learned program (Cai);
- a pretrained LM running procedures that include division (CAEF);
- exact arithmetic inside an LLM (OccamLLM, IGC, compiled transformers).

What I did not find is all of these together: a pretrained LM or VLM, the canvas as its only state, an exhaustive certificate over every rendered view, and that certificate re-checked on the deployed device. I also found no learned, length-general digit-by-digit √, no certified Knuth division, and no exact gcd.

**Assumptions to flag:**
- Today the system does + and ×; "calculator-complete" is still the plan.
- "Inside its own forward passes" is true per step, but the loop, the painting and the crop run outside the model.

**Narrowest true sentence (today):** "To our knowledge, the first pretrained vision-language model to do exact addition and long multiplication at any length, with a rendered sheet as its only state, certified by checking all 1,795 local views and re-checked on the user's GPU." Add −, ÷, √, gcd and decimals only once each passes the same certificate.

## 2. Polynomial algebra by a learned executor, not a CAS: **NARROW** (the broad form is KILLED)

| Work | What it does | What it does not do |
|---|---|---|
| Lample & Charton 2019, [1912.01412](https://arxiv.org/abs/1912.01412) | A seq2seq transformer integrates and solves ODEs, beating Mathematica and Matlab | Answers are end-to-end guesses, with no exactness by construction |
| Minerva 2022, [2206.14858](https://arxiv.org/abs/2206.14858) | An LLM does algebra in its chain of thought with no tool | Not exact |
| Agarwal et al. 2021, [2104.14095](https://arxiv.org/abs/2104.14095) | Transformers simplify polynomials step by step; they fail at numeric multiplication, which is fixed by offloading it to a calculator | No interpolation; the arithmetic is offloaded |
| Kera et al. [2311.12904](https://arxiv.org/abs/2311.12904), [2505.23696](https://arxiv.org/abs/2505.23696); CALT [2506.08600](https://arxiv.org/abs/2506.08600) | Transformers learn Gröbner bases and polynomial products; a border-basis oracle keeps its output guarantee | The guarantee comes from the classical algorithm around the network, the reverse of our split |
| Feng et al. 2023, [2305.15408](https://arxiv.org/abs/2305.15408) | Proves that constant-size transformers with chain of thought solve arithmetic and linear equations | Theory plus small models; no expansion |
| Petruzzellis et al. 2024, [2402.17407](https://arxiv.org/abs/2402.17407) | A learned Selector, Solver and Combiner rewrite nested formulas | No exactness guarantee |

Also checked: ConPoLe [2106.09146](https://arxiv.org/abs/2106.09146) and polynomial decomposition [2508.15766](https://arxiv.org/abs/2508.15766).

**What stays new.** I found no learned system that uses evaluation and interpolation, or Kronecker substitution. Both are classical computer-algebra methods, so the algorithm is not ours. What is new is that every arithmetic step runs on a certified learned executor.

**Assumptions to flag:**
- The algebra lives in the fixed work-order recipe: the choice of points and the interpolation formula. The model supplies arithmetic and transcription.
- Expect a reviewer to say "a certified calculator driven by a CAS recipe."
- State the bounds: Kronecker substitution needs a base larger than any coefficient, and its handling of negative coefficients must be spelled out; interpolation needs a degree bound.
- Substitution certifies each root found, not that all roots were found.

**Narrowest true sentence:** "Polynomial expansion and equation solving in which every arithmetic step is done by a learned, certified neural executor, by reducing algebra to integer arithmetic (Kronecker substitution, evaluation and interpolation)."

## 3. One model decides mid-conversation to run its own certified procedure: **NARROW**

| Work | What it does | What it does not do |
|---|---|---|
| Toolformer [2302.04761](https://arxiv.org/abs/2302.04761); ToRA [2309.17452](https://arxiv.org/abs/2309.17452); ReTool [2504.11536](https://arxiv.org/abs/2504.11536); ToolRL [2504.13958](https://arxiv.org/abs/2504.13958) | The model decides when to call a tool and keeps reasoning with the result | The tool is external (an interpreter or API) |
| OccamLLM [2406.06576](https://arxiv.org/abs/2406.06576); IGC [2501.00684](https://arxiv.org/abs/2501.00684); Neural Comprehension [2304.01665](https://arxiv.org/abs/2304.01665) | An arithmetic or rule module inside the LLM is used mid-generation, with no tool call | The module is symbolic or compiled, not the model's own learned skill; no canvas, no certificate |
| Chain of Code [2312.04474](https://arxiv.org/abs/2312.04474) | The LM emulates an interpreter (an "LMulator") for lines that cannot run | Uncertified; a real interpreter runs everything else |
| Self-Imagine [2401.08025](https://arxiv.org/abs/2401.08025); MathCanvas [2510.14958](https://arxiv.org/abs/2510.14958) | The same model draws its own image and reads it back; MathCanvas learns when to draw | Diagrams, not exact computation; no certificate |
| Recursive LMs [2512.24601](https://arxiv.org/abs/2512.24601) | The model calls itself on sub-problems through a REPL | External REPL; no certificate |

Also: Percepta's [transformer-vm](https://github.com/Percepta-Core/transformer-vm) (2026, GitHub; no arXiv paper) compiles a WebAssembly interpreter into hand-set weights. It is not conversational and not learned.

**What stays new.** Deciding when to act is standard (Toolformer), and "no external tool" is already done by built-in modules. I found no case of the same weights both conversing and acting as the certified executor on their own canvas.

**Assumptions to flag:**
- The runtime (painter, crop mover, work-order parser) is a harness, so say "the runtime does no arithmetic."
- The transcription into the work order is not certified.
- If chat and execution switch the LoRA on and off, adapter switching is known (X-LoRA, [2402.07148](https://arxiv.org/abs/2402.07148)), so "one model" must mean one set of weights plus a gate.

**Narrowest true sentence:** "A small VLM that, mid-conversation, writes a work order, carries it out itself on its own canvas under a certificate, and continues its reply with the results; the runtime only paints glyphs and moves the crop."
