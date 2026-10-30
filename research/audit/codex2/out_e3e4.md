**E3’s “60/60 within 64 cases” is false: it is 58/60. E4’s published arithmetic reproduces, but it establishes failure of this prompting/scoring procedure—not that the model cannot be its own oracle.** No files were edited.

1. **Independent recomputation — BUG for E3 exposure; OK for E4’s implemented scoring.**

   I ran read-only Python scripts. For E3, I reconstructed machines from the original clock records using the shared tokenizer/parser, then independently implemented product search, partition refinement, access-word construction, suite enumeration, and aggregation. For E4, I independently parsed all 4,383 replies, grouped by problem, computed Boolean events, Pearson correlations, and Wilson intervals.

   **E3 class counts reproduce:**

   | Population | Wrong | (a) | (b) | (c) | (d) |
   |---|---:|---:|---:|---:|---:|
   | R1 | 219 | 54 | 75 | 5 | 85 |
   | R2 | 45 | 6 | 32 | 1 | 6 |
   | Total | 264 | 60 | 107 | 6 | 91 |

   Thus class (a) is **24.66%, 13.33%, and 22.73%**, respectively. These match the report’s “54 of 219…6 of 45…60 of 264.” [E3.md:125–129](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:125)

   **Suite exposure, all 60 class-(a) problems:**

   | Origin / bound | ≤16, recomputed | ≤64, reported → actual |
   |---|---:|---:|
   | Reference / reference states | 57 | **60 → 59** |
   | Reference / written states + 2 | 49 | **51 → 50** |
   | Written / reference states | 54 | 55 → 55 |
   | Written / written states + 2 | 57 | **60 → 58** |

   The offending code executes additional words and then sets **`exposed64 = True`** whenever *any* of them disagrees. Fix: leave the first-64 flag immutable; record later exposure separately. [machines.py:469–482](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:469)

   Concrete false positives:

   - `r1a:108`: first written-suite disagreement is **case 85**, `W W W`.
   - `r2:20`: first written-suite disagreement is **case 345**, `down down down down up`; its reference/reference-bound witness is case **105**.

   Both saved records incorrectly say **`"exposed64": true`**. [e3_items.jsonl:109](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/e3_items.jsonl:109), [e3_items.jsonl:405](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/e3_items.jsonl:405)

   All reported suite cardinalities and size statistics reproduce. So do the distance histogram **{0:2, 1:51, 2:3, 3:2, 4:1, 5:1}**, template/anatomy tables, and correct-call counts **336 = 299 equivalent + 36 inequivalent + 1 unresolved**. The ten reference rebuilds and 476 transcript checks report zero mismatches when rerun. [E3.md:200–205](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:200), [E3.md:230–243](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:230)

   **E4, under the implemented amended parser:**

   | Oracle | Catch /60 | Shared /60 | False alarm /60 | Correct class-(a) cases | Correct control cases |
   |---|---:|---:|---:|---:|---:|
   | O1 | 13 | 0 | 35 | 78/517 | 115/944 |
   | O2 | 12 | 0 | 34 | 55/517 | 90/944 |
   | O3 | 9 | 0 | 36 | 35/517 | 83/944 |
   | O1∧O2 | 9 | — | 31 | — | — |
   | O1∨O3 | 16 | — | 59 | — | — |

   Every displayed proportion and Wilson endpoint matches to the reported precision. Correlations reproduce as **−0.058104, 0.134482, 0.587232**, each with n=27; the conditional means also match. [E4.md:83–111](/Users/neo/repos/polyformer-wt/theory/research/theory/E4.md:83)

   The item census also matches: **517/442 rendered/skipped class-(a) cases; 944/16 controls; 30 fully rendered problems; 27 rendered first separators; 16 unreadable program answers**. [E4.md:89](/Users/neo/repos/polyformer-wt/theory/research/theory/E4.md:89)

2. **Registered rules and mathematical validity — mixed verdicts.**

   - **OK: minimisation, equivalence, and observed class assignment.** Refinement starts from output classes and splits by successor classes; product search checks the union alphabet. My independent results agree. Classification implements the amendment: inequivalence first, unresolved next, then bad input, then good-but-wrong. The exact branch **`if any(x == "inequiv" for x in labels)`** implements class-(a) precedence. [machines.py:215–305](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:215), [measure.py:440–453](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/measure.py:440), [E3.md:106–110](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:106)

   - **BUG: “certifies” omits essential preconditions.** The code rejects only **`m_bound < n`**, then returns **`"certifies": True`**. It does not check the other machine’s state bound or matching alphabet. Five reference/reference-bound comparisons and eight written/written-plus-two comparisons exceed the bound on the other minimised machine; 27 pairs have different alphabets. Enforcing both prerequisites leaves **28, 25, 28, 25** eligible pairs in the four table rows above, rather than **60, 52, 55, 60**. Detection counts remain empirical observations. [machines.py:450–468](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:450), [machines.py:495–507](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:495)

     A wrong program **can pass the entire suite**: let the written machine loop on `a`, while the reference also accepts `b` and changes output on it. The written-built suite uses only **`spec_m.alphabet`**, never asks `b`, and returns agreement. I reproduced this with a two-state bound. Fix: establish a common external alphabet and enforce the implementation bound; distinguish suite construction from certification.

   - **BUG for general Moore final-output use; no numerical effect on these records.** The concatenation is correctly \(P\Sigma^{\le m-n}W\), but `characterise` starts with **`acc = []`**, rather than requiring ε. Furthermore, `run_from` returns the complete output trace: **`outs.append(m.out[s])`**. [machines.py:63–74](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:63), [machines.py:332–361](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:332), [machines.py:392–396](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:392)

     Counterexample: unary chain \(0→1→2→2\), outputs \((0,0,1)\). Code chooses \(W=\{a\}\). Change only the initial output to 1: every tested nonempty word has the same **final** output, while ε differs. Fix: include ε and construct/score W under the intended final-output semantics. Here, Moore outputs are state identities, so ε is already selected; my final-output rescore changes none of the observed exposure counts. [machines.py:53–55](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e3/machines.py:53)

   - **BUG: E4 results do not use the frozen parser.** Registration says **“O1 and O2 are parsed on the text before `<program`”**; implementation removes completed program blocks and requires an `Answer:` span. The report acknowledges this was **“fixed after the smoke”**. [E4.md:47](/Users/neo/repos/polyformer-wt/theory/research/theory/E4.md:47), [score.py:109–146](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/score.py:109), [E4.md:319](/Users/neo/repos/polyformer-wt/theory/research/theory/E4.md:319)

     Applying the literal frozen extraction gives O1/O2 **0/60 catches**, **0 correct cases**, and false alarms **2/60 and 0/60**. Fix the reporting by separating registered and amended analyses; do not describe these as unchanged preregistered measurements.

   - **DESIGN FLAW: E4 cannot isolate oracle reasoning from interface failure.** All **1,461 O1 and 1,461 O2 replies contain programs** despite the instruction; cap hits are **780/597/1,154**, and unparsed replies **479/588/1,218**. These diagnostics reproduce. [E4.md:315](/Users/neo/repos/polyformer-wt/theory/research/theory/E4.md:315)

     Parsing demonstrably loses correct answers: O1 says **“Total: 45 dollars.”**, matching reference 45, but is unparsed without `Answer:`. O2 similarly says **“The answer is 8.”**, matching reference 8. Correcting just these two cases raises class-(a) accuracies to **79/517** and **56/517**, without changing their problem-level catch counts. [O1.jsonl:192](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/results/e4-full/O1.jsonl:192), [items.json:4721](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/items.json:4721), [O2.jsonl:180](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/results/e4-full/O2.jsonl:180), [items.json:4438](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/items.json:4438)

     A perfect oracle could catch only **26/60** under the existing renderer and answer projection. The correlation also selects a *machine* separator, which need not separate answers: one stored case says **`"separates_machine": true`**, yet both answers are **1**. [build_items.py:338–351](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/build_items.py:338), [items.json:6267–6270](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/items.json:6267)

3. **Leakage — OK for inspected evaluation paths; limited training assurance.**

   E4 stores reference/program answers, but constructs model input exclusively from the question/paraphrase and rendered word: **`"user": user_text(body, case["rendered"], sentence)`**. Answers and class labels are not inserted. E3’s reference access is intentional oracle-assisted evaluation. [e4_oracle.py:48–60](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/e4_oracle.py:48), [E3.md:29](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:29)

   The inspected training generator explicitly calls **`RD.example(..., "train", ...)`**; held-out phrasings use a disjoint index range. This supports the generated-data split, but does not establish absence of overlap in the inherited adapter or auxiliary datasets. [reason_train.py:68–82](/Users/neo/repos/polyformer-wt/reason/research/reason/reason_train.py:68), [reason_data.py:68–72](/Users/neo/repos/polyformer-wt/reason/research/reason/reason_data.py:68), [train_record.json:10–29](/Users/neo/repos/polyformer-wt/reason/research/reason/results/reason-s1/train_record.json:10)

4. **Fair comparisons and checkpoint selection — OK for O1/O2; DESIGN FLAW for causal O1/O3 comparisons.**

   O1/O2 use the same freshly merged checkpoint, items, greedy decoding, and 512-token cap; paraphrasing is their intended difference. O3 changes adapter, thinking format, temperature, sampling, and cap to **4096** simultaneously. Consequently, its comparison cannot isolate training or oracle independence. [e4_oracle.py:129–172](/Users/neo/repos/polyformer-wt/theory/research/theory/tests/e4/e4_oracle.py:129)

   The adapter records **rank 64**, **500 steps**, **lr 0.0001**; O3 has no corresponding adaptation budget. Training applies pinned, Mealy, CE and applicable KL terms before saving checkpoints; E4 fixes `adapter_step500`, so no early-loss checkpoint-selection defect was found. [adapter_config.json:31](/Users/neo/repos/polyformer-wt/reason/research/reason/results/reason-s1/adapter_step500/adapter_config.json:31), [train_record.json:16–40](/Users/neo/repos/polyformer-wt/reason/research/reason/results/reason-s1/train_record.json:16), [reason_train.py:286–340](/Users/neo/repos/polyformer-wt/reason/research/reason/reason_train.py:286), [E4.md:51](/Users/neo/repos/polyformer-wt/theory/research/theory/E4.md:51)

5. **Figures/captions — OK: neither report contains plotted figures.** The relevant presentation defect is E3’s table caption: **“one of the shortest 16 or 64 words”** does not describe the buggy ≤64 calculation. [E3.md:211](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:211)

**BUGs by severity:** High: inflated ≤64 exposure; unsound certification flags. Medium: frozen/parser mismatch; missing mandatory ε for general final-output Moore use.

**Headline claims that survive:**

- **E3:** the recorded class-(a) machines are caught by sufficiently many suite cases with the reference oracle; **57/60 within 16 and 58/60 within 64**, not universal 64-case coverage.
- **E3 scope:** class (a) is **60/264 failures**; this is not all wrong programs—**36 inequivalent calls occur in correct-answer problems**. [E3.md:230–231](/Users/neo/repos/polyformer-wt/theory/research/theory/E3.md:230)
- **E4:** this deployed prompt/parser procedure is unreliable; the broader **“no self-oracle”** conclusion does not survive the interface confounds.

**Minimal re-runs:** E3 needs only CPU rescoring and corrected certificate checks, no model generation. E4 first needs rescoring of existing replies under both documented rules, then a controlled inference rerun replacing the original event log with the suite word, explicitly specifying the answer format, and matching decoding budgets across compared arms. No retraining is needed.