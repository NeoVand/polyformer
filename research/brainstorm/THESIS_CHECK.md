# Thesis check, 28 Oct 2026 (orchestrator, from our verified prior-art map; no new search)

**Sentence checked:** "The exact computer is already inside every pretrained model. A sandbox that keeps only the
right state makes it provably exact. The hard part is choosing that state."

**Taken:**
- **Lewandowski, Machado & Schuurmans 2026** (arXiv 2601.08061), "Universal computation is intrinsic to language model
  decoding":
  - A prompt found by search makes Llama-4 execute all 1,857 U(15,2) rules.
  - A fresh-call harness (a sandbox that keeps only the window) plus per-rule checks gives exactness at unbounded
    length.
  - So clauses 1–2 are theirs, for one model, by prompt search.
- **Abbe et al. 2024**, the inductive scratchpad: each step sees only the question and the last state. This is the
  pinned policy without a certificate.
- **PENCIL** (ICML 2025): learned erasure, from scratch, for space efficiency.

**Ours:**
- **Remembering breaks it.**
  - The negative theorem: no finite test certifies decoding with history in context (Lean).
  - It is measured on their own construction (REGVM: pinned exact to 30k; with history, failure at 1,811–4,193)
    and in the drift anatomy (BRIDGE).
  - Lewandowski et al. never test history in context; their argument depends silently on its absence.
- **The necessity half of Theorem P.**
- **The policy inside one run:** a KV-cache policy, not external fresh calls.
- **Universality across 10 families and emergence during pretraining:** UNIVERSAL ("elicitable, not latent"; rank-1).
- **A chat model that writes its own programs and keeps its language** (Savant).
- **Abstraction measured as the bottleneck:** 71% of REASON's failures are in what Savant carries in.
- ~~Learned, certified abstraction is open. Everyone else hand-designs what is kept.~~ **FALSE as written**
  (REDTEAM_D). Small networks learn what to keep and are certified (Brandoit, Bugaud, Nerem COLT 2026). Pretrained
  LLMs choose what to carry, with no certificate (MemAgent, MEM1, Delethink, Context-Folding, RLM, Recursion of
  Thought, ACL 2023).
- **Open (REDTEAM_D, about a dozen searches):** certifying that the state a pretrained LM chose to keep from a
  natural-language question is *sufficient*. The well-posed form: the LM's self-chosen table is certified against an
  executable reference by a finite Moore/Chow test with a justified state bound and no per-question human reference.
  Savant's certificate then covers execution.

**Thesis, narrowed:** "An LLM's exact computation is certifiable only if it forgets (proved, and measured on
every model), and the open problem is learning *what* to keep."

**Next:** the REMEMBER run tests the "ours" half across all 10 models. r5 targets learned abstraction.
