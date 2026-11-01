## L*: the missing object is a learned distinguishing experiment

**Objects:** residual language \(u^{-1}L\); observation table \(T(s,e)=1[se\in L]\); counterexample \(c\) separating a conjectured DFA from the target.

**Techniques:** Angluin’s closed-and-consistent table construction; counterexample-guided addition of distinguishing suffixes; discrimination trees that identify states through adaptive membership experiments.

**HIT, conditional:** L* learns the minimal DFA with polynomial query complexity given exact membership and equivalence queries. The transferable mechanism is **actively repairing false state merges with concrete future witnesses**. Its guarantee does not transfer when equivalence queries become heuristic searches.

### To the problem

Here “check” means an observable test, not necessarily a certificate.

| Problem | State / rule / check / search; transfer |
|---|---|
| **P1 representation** | Residual / concatenation / differing suffix answers / distinguishing-suffix search. A \(k\)-way term can score a jointly specified experiment; L* supplies no theorem that this requires order \(k\). **FRAME** |
| **P2 learning** | Table row / transition between rows / consistency violation / counterexample refinement. Labelled witnesses split false merges; closedness adds missing states. **HIT** |
| **P3 memory** | Distinct row / representative transition / unresolved row collisions / add experiments. Store representatives and a growing experiment dictionary instead of all histories. Compression is provisional until the dictionary separates states. **TOOL** |
| **P4 retrieval** | Future-answer signature / match signatures / challenge with another suffix / targeted membership query. Retrieve by predicted experimental behavior. **TOOL** |
| **P5 language** | Protocol residual / dialogue action / legal continuation / adversarial continuation. Best fit: tool-use protocols, permissions and commitments with executable outcomes. Unrestricted prose lacks a membership oracle. **LOW** |
| **P6 verification** | Hypothesis DFA / learned transition / equivalence oracle / counterexample. Closedness and consistency certify table agreement, not target equivalence; bounded conformance needs explicit assumptions. **TOOL** |
| **P7 capability** | Learned protocol state / inferred rules / held-out executions / active probes. A user teaches an unfamiliar workflow through examples and corrections, then gets long-horizon execution. **TOOL** |
| **P8 test** | Ground-truth residual / hidden DFA / exact partition comparison / shortest counterexamples. Measure false merges and oracle cost, not just sequence accuracy. **TOOL** |

### From the problem

Nerode identifies observation rows as approximations to states, not ordinary embeddings. Dilution suggests replacing an average future-distance objective with actively discovered separating suffixes: rare decisive continuations must retain training weight.

Higher-order attention suggests scoring triples **(history, candidate representative, suffix)** to select a witness. But ternary arguments alone prove no cubic advantage. The language tensor \(1[uxe\in L]\) already factors through DFA transitions; interaction order and minimal-state count are different quantities.

### Proposal: counterexample-trained state retrieval

Maintain representatives keyed by predicted suffix-answer vectors. Search for continuations that disprove proposed merges, then retain their labelled answers as supervised constraints. Compare cubic witness selection against bilinear selection while keeping the partition-refinement mechanism identical.

**Experiment:** hidden 32–64-state DFAs, four arms crossing active/random suffix selection with cubic/bilinear scoring; evaluate at 16× training length with irrelevant-symbol insertion. Kill the active-learning proposal if it cannot halve membership-query cost at 99% exact state identification; kill the higher-order component if it saves under 20%.

**Closest prior art:** Angluin’s L* (1987); Rivest–Schapire counterexample processing (1993); Kearns–Vazirani discrimination-tree learning (1994).