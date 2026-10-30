# Voice: own the work (Neo, 25 Oct)

"The passive voice and a passive account of the contributions ... we should confidently own it, because this is not a
report about the paper. This is the paper itself."

## Rules for the whole paper
- First person plural, active verbs, for every contribution: we prove, we introduce, we identify, we show, we certify,
  we carry. Never "this paper argues", "the table has one row", "one object explains", "the recipe is tested".
- Name the method once and use the name: **Nerode training** (certified equivalence, next-state prediction and closure
  on the readout's sphere, on top of the output loss).
- Claims are stated as findings, not as descriptions of figures. Figures support sentences; sentences do not narrate
  figures.
- Limits are stated once, plainly, in our voice ("On S5 it holds on two seeds of three; there next-state prediction
  with closure is what we need").
- Nature's summary-paragraph shape for the abstract: the problem, "Here we ...", the results with numbers, what follows.
- No em dashes.

## Abstract (proposed; integrate, adjusting only for facts)
Sequence models learn to track state from data and lose it at length. A model trained on short programs, proofs or
stories follows them exactly and then drifts, as a small error in the state it carries compounds. We prove that
next-token training cannot prevent this: its loss carries the model's own error rate as a factor, so beyond a fixed
multiple of the training length no value of the loss separates exact models from failing ones. We identify what
exactness at length requires: coverage of the states met at length, a state space closed under the dynamics, and a
state-level signal that the readout's confidence does not damp. Here we introduce Nerode training, which supplies that
signal from a checker the domain already has. An interpreter, a proof kernel or a simulator certifies pairs of
histories that end in the same state, and we train the model to agree. With the state held on a sphere, the joint
minimiser is the task's minimal automaton. Across seven settings, from program execution and Lean rewrites to stories
in varied English, Nerode training makes trackers exact on every seed at 64 to 128 times their training length in six
and on two seeds of three in the seventh. We certify snapped trackers exact on every input at every length, and we
carry the method into a language model's own chain of thought, raising exactness at 16 times its training length from
zero to 0.77 and 0.95 with no state information beyond that length.

## Introduction, paragraphs 2-4 (proposed)
The failure belongs to the objective, not to the architecture. We prove that next-token prediction prices a rare
per-step state error at a cost carrying the loss floor as a factor. A model whose state drifts slowly therefore sits in
a valley of the training loss as deep as the exact model's (Fig. 1a), and no amount of fitting at the training length
tells the two apart.

We identify three conditions for exactness at length. The first is *coverage*: every state the model will meet at
length, with every next event, must be met in training, as Buitrago Ruiz and Gu showed for recurrent models [24]. The
second is *closure*: the carried state must not leave the set it was trained on, and we enforce it by projecting the
state onto a fixed sphere after every event. The third is a *stiff state-level signal*, one whose gradient and
curvature along a drift carry no factor of the readout's error probability. We introduce Nerode training to supply it.
A checker the domain already has, an interpreter, a proof kernel or a simulator, certifies that two histories end in
the same state, and we train the model to agree. The checker never names the state. By the Myhill-Nerode theorem [25],
which histories are interchangeable is exactly the information that defines it, and we prove that with closure the
joint minimiser of "predict the output, predict the next state, merge certified-equivalent histories" is the minimal
automaton, exact at every length.

We test Nerode training in one ablation across seven settings (Table 1, Fig. 1c): program execution read through a
frozen code model, certified Lean rewrite chains, words in the symmetric group S5, long addition with and without long
carries, counting, and stories in varied English. It is exact on every seed in six settings at 64 to 128 times the
training length, and on two seeds of three in S5, where next-state prediction with closure is what holds. We explain the
whole table with one object, the error cocycle: the linearised dynamics of the state's error over the automaton's
transition graph. We show that the trained state is the minimal automaton, with basins that correct errors, and we
certify snapped Lean trackers exact on every input at every length. Finally, we carry the method into a 0.5-billion-
parameter language model and raise its own chain of thought from 0 to 0.77 and 0.95 exact at 16 times its training
length, with no interpreter state beyond that length.
