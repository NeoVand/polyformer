# Follow-up: turn Candidate 1 into a theorem a referee will accept, and stress-test it

This continues your report, *Deep reading: finite certification, restoration and long-horizon exactness in sequence
models*. Reuse its notation and tags ([V] verified quote, [A] your own argument, [U] unverified). Read new papers
**in full**, proofs and appendices included.

## 1. Write the full proof of Candidate 1
Produce a complete, referee-grade proof of Candidate 1 (fixed-margin causal softmax attention realises only
definite-modulo-length languages), with explicit constants.
1. **Hypotheses, minimal and exact.**
   - **RoPE.** Show that rotary positions keep |σ| ≤ A on reachable activations, or find where they do not.
   - **Mechanics.** Handle multi-head attention, the residual stream, pre-norm with ε > 0, gated MLPs (SwiGLU), and
     the final readout.
   - **"Recognise with margin γ at every length".** State it precisely, and say whether it is per position or only
     at the final position.
2. **The causal influence lemma**, with the recurrence, its solution with constants, and the matching Cesàro lower
   bound. Check the weight-change term (the normaliser Z) carefully. Does the bound depend on the reachable
   activations staying bounded, and is that automatic under pre-norm?
3. **The class theorem, (a) to (c),** including the exact n₀ and the single-substitution connectivity argument.
   - Is "definite modulo length" exactly the right class?
   - Is the converse (c) correct with **soft** attention at a finite temperature, or does it need hard attention?
     State the tightest version of each.
4. **The autoregressive version (the most important one).** Consider a decoder that keeps its full context and
   generates tokens. The context holds a fixed transition table Π (|Q| states, |Σ| events) at the start, followed by
   an input stream. The decoder's task is to emit the automaton's state after each event.
   - **(i)** Prove, or refute, this claim: no such decoder can emit the correct state with a fixed margin at every
     length for every table in a class rich enough that two tables differ in one row whose first use occurs after
     an arbitrarily long delay. This is the "first-use" corollary. The generated state tokens in the context do
     **not** rescue it, because the row's destination appears nowhere but in Π until it is first used.
   - **(ii)** After a row has been used once, its correct output sits in the recent context. Can a decoder sustain a
     fixed margin by copying from its own history (induction)? What does that imply when an earlier output was
     wrong, so that a wrong copy now competes with the single correct copy in Π? Give the cleanest statement you can,
     and its limits.
   - **(iii)** Contrast this with a decoder whose context is reset at each step to (Π, current state, current
     event), with positions restarted. The context length is fixed, so the theorem does not apply. State the exact
     dividing line between the two.
5. **The one-sentence statement and the one-page proof** you would put in a journal paper, plus the list of known
   escapes, each with the hypothesis it violates.

## 2. Prior-art stress test for Candidate 1
Read these in full (add any you find relevant). For each, say whether it states, implies, or contradicts Candidate 1
or its autoregressive version, and quote the relevant theorem.
- Strobl, Merrill, Weiss, Chiang & Angluin (2024). *What Formal Languages Can Transformers Express? A Survey.* TACL,
  plus any 2025–2026 update.
- Hahn & Rofin (2024). *Why are Sensitive Functions Hard for Transformers?* ACL.
- Chiang, Cholak & Pillay (2023). *Tighter Bounds on the Expressivity of Transformer Encoders.* ICML.
- Yang, Chiang & Angluin (2024). *Masked Hard-Attention Transformers Recognize Exactly the Star-Free Languages.*
- Barbero et al. (2024). *Transformers Need Glasses! Information Over-squashing in Language Tasks*, arXiv:2406.04267.
- Edelman, Goel, Kakade & Zhang (2022). *Inductive Biases and Variable Creation in Self-Attention Mechanisms.*
- Sanford, Hsu & Telgarsky (2023, 2024): representational strengths and limitations of transformers; transformers,
  parallel computation and logarithmic depth.
- Bhattamishra, Ahuja & Goyal (2020). *On the Ability and Limitations of Transformers to Recognize Formal Languages.*
- Zhou et al. (2024). *What Algorithms Can Transformers Learn? A Study in Length Generalization* (RASP-L), and Zhou
  et al. (2024), *Transformers Can Achieve Length Generalization But Not Robustly.*
- Length-generalisation constructions that seem to escape: position coupling (Cho et al. 2024), Abacus embeddings
  (McLeish et al. 2024), looped transformers (Fan et al. 2024). **For each, identify exactly which hypothesis of
  Candidate 1 it violates, or whether it claims no fixed margin.**
- Kozachinskiy and co-authors, and others, on lower bounds for softmax attention or fixed-precision transformers.
- Induction-head theory: Olsson et al. (2022); Bietti et al. (2023), *Birth of a Transformer: A Memory Viewpoint*;
  Edelman et al. (2024) on statistical induction heads. These feed §1 item 4(ii).
- Anything from 2025–2026 on "attention dilution", "context rot" or "effective context length" that states a
  theorem.
- **Must-read, found after the first report.** These change what is new:
  - Köver, Butoi, Svete, Hahn & Cotterell (2026), arXiv:2606.08768, Cor. 3.3–3.4 and Prop. 3.5. Fixed-margin
    recognition for **encoders** (layer norm with ε > 0, final EOS) gives constant-per-length languages. Candidate
    1's encoder form is therefore taken.
    - **Question:** does their proof extend to causal masking, and if not, exactly where does it break?
    - **Note:** Hahn & Rofin (2024) state that the decoder case is open.
  - Li & Cotterell (2026), arXiv:2605.00768, Thm 4.2 with Thm 2.2: fixed-precision, no-PE transformers with k-local
    heads recognise exactly the definite languages.
  - Nowak, Cotterell & Boumasmoud (2026), arXiv:2607.26988: sliding windows of width one recognise only definite
    languages.
  - Chowdhury (2026), arXiv:2603.10123: the Cesàro matrix M_ij = 1/i for uniform causal attention, and an exact
    formula for M^H. This corrects §2 A2 of your first report, which said no paper gives a matching construction.
  - Wu, Wang, Jegelka & Jadbabaie (ICML 2025), Lemma 4.4 and Thm 4.5: positional decay under ALiBi-type recency in
    attention rollout.

## 3. Candidates 2 and 4: proofs and boundaries
- **Candidate 2.** Give the full proof: architectural budget ⇒ an m-state fault domain ⇒ W-method completeness;
  plus the black-box lower bound via Vasilevskii's lock automata, against white-box per-transition checking.
  - **The critical question:** for **softmax transformers with a reset context** (the decoder in 4(iii)), is the
    reachable context set finite and successor-closed? Then per-transition (white-box) checking is complete and
    polynomial, while black-box testing is exponential or impossible.
  - State the exact gap, with constants.
- **Candidate 4.** Make (ii), necessity, precise for a **restricted** class (bounded-logit transformers), not only for
  all next-token maps. Does Candidate 1 trivialise it, as you warned, or is there a clean statement?

## 4. Synthesis
1. **The main theorem**, as you would state it for a general scientific audience, in one paragraph, with the
   hypotheses in plain words.
2. **Its three closest predecessors** (Maass–Sontag, Brandoit Theorem 4.1, Hahn) and exactly what it adds to each.
3. **Three measurable predictions** about pretrained transformers that follow from it, each testable with forward
   passes alone:
   - for example, how the margin of a table lookup decays with context length when the table sits at the start;
   - the "first-use delay" signature;
   - the role of the logit range A.
4. **The weakest point:** what a hostile referee would attack first, and the best defence.

## Format
- One Markdown report: proofs first, then the prior-art table (paper → states / implies / contradicts / unrelated,
  with quotes), then Candidates 2 and 4, then the synthesis.
- Verified citations with links.
- A short list of what you could not read or verify.
