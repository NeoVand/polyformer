# The Neural Idea Zoo: a first definition (Neo + Fable, 30 Oct 2026)

Neo: standard deep-learning courses cover a hundredth of the ideas that matter; a maintained, structured zoo of compute
graphs, key ideas and what was proven could accelerate research. This file defines what the thing is, what exists
already, and the smallest version worth building.

## What it is

A knowledge graph whose nodes are **ideas** (mechanisms, objectives, architectures, theorems, phenomena) and whose edges
are **typed relations** between them, maintained by agents and read by people. Each node carries, in this order:

1. **Plain-words card** (the glossary entry): what it is, who/when, why it matters.
2. **Compute graph**: the minimal diagram and the minimal runnable code (jax-js, so it runs in the browser on the page).
3. **What is proven**: each theorem as a statement *with its hypotheses*, source and section; what is only measured.
4. **Minimal distinguishing experiment**: the smallest test that tells this idea from its nearest neighbour.
5. **Lineage**: typed edges — generalises / special case of / pre-empted by / refuted by / composed from / same as under
   renaming — each with a citation and a one-line justification.
6. **Open questions** and known failure modes.

Edge types are what make it more than a wiki: "pre-empted by" and "same as under renaming" are the two edges this
project paid $6,300 to discover by hand in October.

## What exists (and what it lacks)

- Papers with Code's methods taxonomy (archived 2025) listed methods by category with papers; no proofs, no code graphs,
  no relations beyond "uses".
- The Neural Network Zoo poster (van Veen, 2016): architectures as diagrams; a snapshot, no claims.
- Distill (2016–2021): a few dozen interactive explanations of ideas; depth without coverage, no graph.
- Connected Papers, ResearchRabbit, Litmaps: citation graphs; edges are "cites", not "pre-empts" or "refutes".
- Open Research Knowledge Graph (ORKG): structured claims across science; general, sparse for ML, no compute graphs.
- alphaXiv, Hugging Face Papers, Semantic Scholar: discussion and summaries per paper, not per idea.
- Lilian Weng's blog, d2l.ai, Transformer Circuits: excellent explanations; not structured, not maintained as a graph.

None keeps the triple that matters: compute graph + theorem with hypotheses + typed relation to neighbours, with an
agent that answers "has X been done, and under which hypotheses" with evidence. Our own prior-art gates produce exactly
that triple, ad hoc, in `research/audit/*/out.md`.

## The smallest version worth building

- **Seed content**: the glossary (`GLOSSARY.md`, tags `[zoo]`), the audit gates (`research/audit/*/out.md`), the
  reading brief's six papers, and the theorems file. About 150 nodes on day one, all from material we already wrote.
- **Format**: one Markdown file per idea in `research/zoo/<slug>.md` with a YAML header (name, kind, year, sources,
  edges as `relation: target-slug # justification`), body in the six sections above. Agents can write it; people can
  read it raw; the app renders it.
- **App**: a route in the polyformer SvelteKit app ("Zoo") that renders the graph (force layout by lineage, filters by
  kind and year), each node's card with the compute graph drawn by the existing Feynman/TikZ renderer and the minimal
  code run live in jax-js. The viz primitives already exist from the Learn and Explore pages.
- **Agent loop**: a "gate" command that, given a new idea written as a card, retrieves the nearest nodes, searches live,
  and returns the kill/narrow/open verdict with proposed edges, for a human to accept. This is the audit we ran four
  times this week, made repeatable and cumulative.
- **Not in the MVP**: coverage of all of ML; automatic ingestion of arXiv; anything that claims novelty without a human
  accepting the edge.

## Why it could accelerate research

Every dead end this project hit in October was an existing node with a missing edge: Lewandowski's harness, Brandoit's
contract-and-separate, Meridian's coprocessor, Neural GPU's local rule. A graph with those edges and a gate that walks
it would have turned four weeks into four days. The product is not the content; it is the edges and the gate.
EOF
echo wrote IDEA_ZOO.md