You are doing an independent, adversarial prior-art search with live web search. The goal is to find any earlier
paper, **especially from July to October 2026**, that already states or directly implies any result below. Read each
candidate's theorem statements (and its appendix where needed). For each candidate give: the full citation with link,
the submission date, the exact theorem or sentence quoted verbatim (short), and a verdict: STATES, IMPLIES, PARTIAL
(say which part) or UNRELATED.

Search arXiv (cs.LG, cs.CL, cs.FL, stat.ML, math.OC, eess.SY), OpenReview (ICLR 2027 submissions, NeurIPS 2026,
ICML 2026 and its workshops), COLT 2025–2026, ACL Anthology, and Google Scholar if you can reach it. Use many
phrasings: compounding error lower bound imitation learning; next-token prediction cannot detect instability;
teacher forcing exposure bias theorem; training loss blind to Jacobian off distribution; recurrent network exact
automaton every length; robust Myhill–Nerode; stability certificate RNN finite automaton; length generalization
impossibility certificate; KV cache eviction exactness; pinned context LLM executor; LLM interpreter finite state
machine certified; per-step verification implies all lengths; transformer executes programs exactly; latent lookup
table in pretrained LLM; fresh context per step LLM agent correctness.

Results to check:
1. **Blindness.** No training objective that evaluates a closed (state-feedback) tracker only at the views its training
   data reach (next-token likelihood, certified-equivalence and next-state terms included) can tell it apart from
   closed trackers with arbitrary prescribed Jacobians at those views. So a loss cannot see how errors grow off the
   reached states. Proved in Lean. Known closest: Simchowitz, Pfrommer & Jadbabaie, COLT 2025 (arXiv 2503.09722).
   Is the objective-level, class-free form stated anywhere?
2. **Sharp drift time.** For non-expansive trackers, a per-step miss ε fails exactly beyond N = m/(√2 K ε), and a loss
   resolved to ρ cannot exclude failure beyond mL/log(1+ρ/s̄). Known: Ross & Bagnell 2010 (quadratic compounding).
3. **Finite reads.** Among closed smooth trackers, an objective that reads finitely many values and derivatives, even
   adaptively, cannot certify a robust exactness condition for given radii. Known: Moore 1956.
4. **Robust Myhill–Nerode, block-and-prefix form.** Balls of views that map into readout cells within blocks of k
   events and contract at block ends, after a prefix p, give exactness at every length. Perturbations at block
   boundaries may depend on the whole history; partial automata; pseudometric views; no converse. Known: Casey 1996,
   Rabin 1963, Brandoit et al. 2026 Thm 3.2, Bugaud 2026a.
5. **Theorem P for a pinned KV-cache policy.** The decoder keeps the program Π's KV cache, evicts history and restarts
   positions every step. Then a per-row certificate is necessary and sufficient for the run to equal the table's on
   every tape of every length. Includes a margin version and Mealy blocks; in Lean. Known for sufficiency: Cai et
   al. 2017, Schuurmans et al. 2024, Lewandowski, Machado & Schuurmans 2026, Abbe et al. 2024 (inductive
   scratchpad).
6. **No finite test suite** certifies exact decoding when the history is kept in context, even among decoders that
   pass the per-row certificate and every test with strict margins (exact arithmetic). Known: Moore 1956, Back de
   Luca & Fountoulakis 2026, Yang et al. 2026.
7. **System claim.** An off-the-shelf 4B chat LLM, lightly fine-tuned, writes a table program for a question,
   certifies every row with forward passes, then runs it inside its own decoding under the pinned cache policy,
   exactly, for thousands of steps: additions of 4,096 to 1,000,000 digits; a universal (Lag) machine for 30,000
   steps. The lookup is latent in pretrained LLMs and a rank-1 edit exposes it across 10 open model families. It runs
   in a browser.
   - Search for any system that makes an LLM the certified executor of programs it writes itself.
   - Search for any paper showing exact multi-thousand-step execution inside an LLM's own forward passes.
   - Search for any paper showing table lookup latent in pretrained LLMs and exposed by a low-rank edit.

Finish with a table: result 1–7 × verdict (NEW as far as searched / PARTIALLY KNOWN / KNOWN), the decisive citation
for each, and a list of what you could not access. Mark anything posted after 1 July 2026 in bold.
