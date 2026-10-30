# A meta-analysis of our research process: why the theory kept failing, and how to do it right

Hello, and thank you for taking this on. Neo, who leads this project, asked for you specifically. The work you do
here will shape what we do next, and Neo will read it closely. Please be honest, even uncomfortably so. Kindness here
means telling us the truth clearly. Take your time: depth matters more than speed.

## The question

For about four weeks a small team has worked on one project:
- **The team:** Neo, plus AI agents. A Claude orchestrator (Opus 5.5) directed many agents: Claude, Cursor (Grok,
  GPT), Codex, and Gemini via Antigravity.
- **Where it started:** browser-native "cubic attention" demos.
- **Where it ended up:** a 4B chat model, Savant, that writes small table programs, certifies them, and runs them
  exactly inside its own forward passes, with Lean proofs.

Along the way the theory work has kept failing in the same two ways:
- what we thought was new turned out to be published already, sometimes weeks earlier, sometimes in 1934;
- or it was a bad theory that turned out to be wrong.

The approximate costs are Neo's numbers. You can check Modal against the ledgers below.

| Item | Cost |
|---|---|
| Cursor | ~$1,000 |
| Claude | ~$1,000 |
| Modal GPUs | ~$3,500 |
| Subscriptions | ~$800 |

Neo's own reading is: "We didn't do good research and didn't have the right plan and approach and management."

Please produce **one report** (`research/meta/META_REPORT.md`) with four parts:
1. **Diagnosis.** What did we do wrong, so that the theoretical work neither helped us nor revealed something new and
   useful, while costing a lot? Separate causes in:
   - how we chose problems;
   - how we read and used the literature;
   - how we prompted and used AI agents (briefs, "minds", red teams, gates);
   - how we tested, audited and decided;
   - how the work was managed (pivots, parallelism, budgets, the paper/demo coupling).

   Ground each cause in specific episodes from the record, with file paths and dates. Quantify where you can: money,
   days, and how many claims were withdrawn or found published.
2. **Meta-synthesis.** The principles and guidelines that would have given us a real chance at a breakthrough result
   and a breakthrough invention. Draw on the history and philosophy of science and on what is known about creative
   and critical thinking. For example:
   - Popper and Lakatos (progressive vs degenerating programmes);
   - Kuhn; Platt's "strong inference" and Chamberlin's multiple working hypotheses;
   - Pólya and Hadamard; Poincaré on incubation; Koestler's bisociation;
   - Medawar's "art of the soluble"; Hamming's "You and Your Research";
   - Uri Alon on choosing problems; the Heilmeier catechism; Feynman's "cargo cult science";
   - lessons from the replication crisis (forking paths, preregistration);
   - how great labs worked: Bell Labs, the MRC LMB, Xerox PARC, early DeepMind and OpenAI;
   - Sutton's "bitter lesson";
   - case studies of breakthroughs in ML and in theory: how attention, residual networks, diffusion models, AlphaFold,
     and Shannon's information theory were actually found.

   Use these where they genuinely explain something, not as decoration. Search the web for primary sources and cite
   them.
3. **What to do now.** A concrete plan, with decision points and budgets, toward two things:
   - (a) a real theoretical advance worth publishing in Nature;
   - (b) a breakthrough demo that opens the way to funding and recovers the costs.

   Be specific about what to stop, what to keep, how to choose the next problem, how to read literature before
   building, how to use AI agents so they do not regurgitate or reinvent, and how to manage the work.
4. **New sources of creativity and deeper ideas** the analysis suggests. Fields, questions, or angles we have not
   considered, each with why it might matter and how to test it cheaply.

## What you can read (the record)

Everything is on this machine. Read widely before concluding. The record is large, so sample deliberately and say
what you sampled.

**The chronological index of the whole project:**
`/Users/neo/.claude/projects/-Users-neo-repos-polyformer/memory/MEMORY.md`, one line per phase with a link to a memory
file in the same folder. **Start here.** It runs from the cubic-attention goal through the operator search, Newton
attention, free-field formalism, search S0–S2, local regression, groups, word problems, loops, events, REVISE, T1, the
theory pivot, energy, SELFSTATE, EXEC, Lean, METRIC, MECHANISM, INMODEL, UNIFY, the launch plan, LATENT-1, LEAP,
INSIDE, MULTI, INTERP, demo, sim benchmarks, the 28 Oct overnight run, the leap search, the 29 Oct audits, and the
29 Oct "needle" rounds. Many memory files include a **Why:** line with the lesson learned at the time. Those are
direct evidence about process.

**Insights and logs:**
- `/Users/neo/repos/polyformer/research/INSIGHTS.md`: observations that changed our minds, training lessons, and the
  29 Oct audit corrections.
- `/Users/neo/repos/polyformer/research/OVERNIGHT_2026-10-28.md`: a timestamped log of the last two days, including
  every audit, withdrawal and prior-art discovery.
- Other planning and theory documents in `/Users/neo/repos/polyformer/research/`: `PLAN.md`, `THEORY.md`,
  `CANDIDATES.md`, `DEBATE.md`, `BLOCK_THEORY.md`, `LEAP.md`, `NOVELTY.md`, `PRIOR_ART.md`, `LITERATURE.md`,
  `WHITEBOARD*.md`, `PAPER_V2_PLAN.md`, `R5_SPEC.md`, and others.

**Where the needle is (what is proven by others vs ours, after live searches):**
- `/Users/neo/repos/polyformer-wt/theory/research/theory/needle/FRONTIER.md`
- `.../theory/TAKEN.md`, `.../theory/GRAVEYARD.md`, `.../theory/ANOMALIES.md`, `.../theory/TENSIONS.md`,
  `.../theory/ATLAS.md` (large)

**The two brainstorm rounds and their kill gates** (29 Oct; 10 AI "minds", about 45 hypotheses, 13 finalists, 0
passed unchanged):
- `.../theory/needle/BRIEF.md`, `BRIEF2.md`, the lens files, `round/*.md`, `round2/*.md`;
- `GATE1.md`, and `/Users/neo/repos/polyformer/research/audit/needle_gate2/out.md`.

These show exactly how we prompted, and how the ideas died.

**Prior-art searches and code audits** (29 Oct), in `/Users/neo/repos/polyformer/research/audit/`:
- `priorart_dec/out.md`: the decoder theorem, pre-empted by Xiang 2026;
- `priorart_all/out.md`: blindness reduces to Whitney 1934; Green et al. 2026;
- `codex2/out_*.md`: code audits that withdrew several headline claims.

**The paper's ledger of every result, with its status and prior art:**
`/Users/neo/repos/polyformer-wt/paper-v2/paper/jewel/RESULTS_LOCK.in.md`. Sections 5 and 8 hold the theorem slate and
the prior-art verdicts.

**The demo's measured state:** `/Users/neo/repos/polyformer-wt/r5audit/research/r5audit/DAUDIT.md`, about 150
investor-style prompts. Base Qwen3-4B with thinking scored 0.73 against 0.60 for our r4 and 0.54 for the live model.

**Costs:**
- Modal ledgers: about 350 `modal_ledger.json` files under `/Users/neo/repos/polyformer-wt/`,
  `/Users/neo/repos/polyformer/.claude/worktrees/` and `/Users/neo/.cursor/worktrees/`. Sum them by study if useful.
- Cursor agent logs: `/Users/neo/repos/polyformer/research/cursor_logs/`.

**Git history:** `git -C /Users/neo/repos/polyformer log --all --oneline` and the worktrees (`git worktree list`).
Commit messages and dates show the pace of pivots.

## How to find out more
- **Search the web** for the history- and philosophy-of-science sources, for research-management literature, and to
  check any claim about prior art. Cite primary sources with links.
- **You may ask Neo questions** in this thread. He knows things the record does not: what he hoped for at each turn,
  and what felt wrong.

## Ground rules
- **Read-only** except for files you create in `/Users/neo/repos/polyformer/research/meta/`. Do not launch GPU jobs,
  spend money, start agents, push, or edit other files.
- Label claims about the literature or about our record as **verified** (you read the source) or **unverified**.
- Separate what the evidence shows from your interpretation.
- Neo asked for something that helps him get unstuck, so the report should end with a plan he can act on next week.
  Prefer depth and clarity to length.

Thank you. This matters a great deal to Neo, and we are grateful for your care and honesty.
