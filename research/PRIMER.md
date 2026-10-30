# A primer on learned exact state

## 1 The problem

Imagine five cards in a row, initially:

```text
A B C D E
```

An event says either “swap cards at positions $i$ and $j$” or “do nothing.” After every event, the answer must be the current order.

```text
Start:       A B C D E
Swap 1, 3:   C B A D E
Swap 2, 5:   C E A D B
Do nothing:  C E A D B
```

There are $5!=5\times4\times3\times2\times1=120$ possible orders. The history can grow forever, but the information needed to continue fits into one of 120 possibilities.

A language model may understand every instruction and still lose track after many events. Knowing what a swap means does not ensure that its internal representation of the cards remains reliable through thousands of updates. A small representational error can survive, accumulate, or grow until the model reports another order.

This distinction motivates **learned exact state**: learning an internal memory whose decoded answer stays exactly correct as events continue. “Exact” describes the discrete answer; the internal numbers can vary.

The project trains mostly on sequences of about 16 events, or 32 for arithmetic and the cube, then tests up to 4,096 events, or 10,000 for the cube. This tests **length generalization**: whether a rule learned on short sequences continues working on long ones.

Throughout this document, “exact at a length” means at least 99% of the 512 test problems at that length (507 or more) end in the right state. Some runs reach all 512; the bar is 99%. A **seed** identifies an independently trained copy, with its own training randomness. “10/10” means ten copies were all exact under that test. Neither expression means every possible input has been proved correct.

The central question is therefore more demanding than “Did the network learn the swap rule?” It is:

> Did it learn a representation that preserves the right distinctions while repairing the small errors introduced by repeated updates?

To answer that, we first need to say precisely what the network should remember.

## 2 What a “state” really is

A **history** is the sequence of events already seen. Two histories can differ greatly while leaving exactly the same information relevant to the future.

Starting from `A B C D E`, compare:

```text
History 1: do nothing
History 2: swap 1, 3; swap 1, 3
```

Both finish at `A B C D E`. Give them any identical continuation, and every subsequent answer will match.

Call such histories **equivalent**. In symbols, write $h\sim h'$ when histories $h$ and $h'$ produce the same answers under every possible continuation, including asking for the answer immediately.

This is **Nerode equivalence**, expressed for a task that reports answers. The essential phrase is *every possible continuation*. Matching on one observed answer is generally weaker.

For cards, the current answer reveals the entire relevant state, so matching orders is sufficient. In program execution, two runs might currently print the same number while storing different values in another variable. A later statement could reveal that difference. The state must retain everything that can affect a future answer.

An **equivalence class** collects all histories equivalent to one another. A true task state is one such class. For cards, there are exactly 120 classes, one per order. Histories with different orders are distinguishable immediately; histories with the same order stay indistinguishable under identical future swaps.

A **finite automaton** is a machine with finitely many states and a rule for updating its state after each event. Here it also reports an answer. Let $q$ denote a true state, $a$ an event, and $\delta(q,a)$ the next true state. Then:

$$
q_{t+1}=\delta(q_t,a_t).
$$

The subscript $t$ counts events. For “do nothing,” $\delta(q,a)=q$.

The **minimal automaton** uses the fewest states sufficient to reproduce every answer. Myhill–Nerode theory explains why its states correspond to these equivalence classes: merging distinguishable histories loses information; separating equivalent histories adds unnecessary memory.

Counting gives the same idea with an important boundary. Counting modulo five—wrapping from four back to zero—needs five states. Unbounded exact counting needs infinitely many distinguishable counts. A fixed finite memory cannot represent all of them indefinitely. Length generalization must therefore be understood together with the task’s allowed state range.

A **checker** is a trusted procedure that applies the task’s rules. For cards, it literally performs the swaps. For programs, it executes the specified instructions.

The checker can produce **certified pairs**: pairs of histories known to be equivalent. For example, inserting the same swap twice preserves a card history’s final state. These pairs supply supervision about what the network should forget.

“Certified” here concerns the pair’s equivalence. It does not certify the neural network.

A related idea is **bisimulation**: matching states by their outputs and by how their possible next steps correspond. Ferns et al. (2004) developed **bisimulation metrics**, numerical measures of behavioural similarity in probabilistic decision systems. This is related background, rather than the same learning objective or guarantee. [Ferns et al., *Metrics for Finite Markov Decision Processes*](https://arxiv.org/abs/1207.4114)

## 3 A network that carries a state

The **tracker** is the learned mechanism that updates memory after each event. Its memory is a vector: an ordered list of numbers. Write that vector as $z_t$ and its update rule as $F_a$:

$$
z_{t+1}=F_{a_t}(z_t).
$$

This resembles the true update $\delta$, but there is a crucial difference. The true state is one of 120 card orders. The neural state can occupy many numerical positions.

The **host** is the architecture in which this tracker lives. The project studies three arrangements:

- A frozen language model with about 0.5 billion parameters, plus a state slot containing 128 numbers. “Frozen” means the pretrained language-model weights stay fixed during tracker training.
- A small network trained from scratch, without starting from a pretrained language model.
- A tracker learned inside the language model’s own hidden state, its internal numerical activations.

These arrangements may support different error behaviour even when trained on the same symbolic task.

The **readout** converts neural memory into an answer. Write it as $R(z)$. For cards, it selects one of 120 orders. Correct tracking requires:

$$
R(z_t)=q_t.
$$

This does not require $z_t$ to equal a unique numerical code. Many vectors can decode to the same order.

A **view** is the representation of memory used for a particular measurement or loss. It might be the whole state vector, or a selected transformation of it. Write $v=V(z)$ for a view obtained by applying a function $V$. A picture of well-separated states in one view is useful evidence, but it does not automatically describe every aspect of the full memory.

For simplicity, the geometry below uses $z$ directly. Any certificate must apply to the representation actually carried forward, or justify why the chosen view is sufficient.

**Closure** means that updating a valid state leaves another valid state. If $S$ is the allowed set of representations, mathematical closure says $F_a(S)\subseteq S$ for every allowed event.

The training recipes use closure constraints to discipline the representation. Fixed-norm closure controls its overall magnitude; centred closure controls the representation relative to a centre. A **norm**, written $\|z\|$, measures vector size; here we can think of ordinary straight-line distance.

A closure loss encourages the desired condition on training examples. It is not, by itself, a proof that every point in the allowed set obeys it. Nor does controlling magnitude automatically preserve card identity. We also need readable, separated states and reliable transitions between them.

## 4 Geometry: readout cells, class centres, safety balls, cell radius, margin

Imagine the neural state space as a large room divided into regions. Every point in one region is read as `A B C D E`; another region means `C B A D E`.

A **readout cell** is the collection of vectors producing one answer:

$$
C_q=\{z:R(z)=q\}.
$$

These cells need not be round, equally sized, or even connected.

A **class centre**, $c_q$, is a representative vector for true state $q$. It might summarize the vectors reached by histories in that equivalence class. It is a reference point, not a claim that every correct history lands there exactly.

A **safety ball** is a neighbourhood around that centre containing only correctly decoded vectors. A ball of radius $r$ is:

$$
B(c_q,r)=\{z:\|z-c_q\|\le r\}.
$$

Think of placing a small ball entirely inside the region labelled with the correct card order. Every point inside the ball is safe to read.

The **cell radius**, measured from the chosen centre, is the distance to the nearest wrong-answer boundary: the largest safe radius, with appropriate care at boundaries and ties. Call it $r_q$. It is not the distance between centres, and it does not describe the cell’s entire shape.

The **margin** is the remaining clearance before a wrong answer becomes possible. If the current state is distance $e$ from its centre and we have a certified safety radius $r$, then $r-e$ is a conservative margin.

For example, suppose $r=0.20$ and the current error is $e=0.05$. There is at least $0.15$ of clearance according to this ball. If the error grows to $0.19$, the answer may remain correct, but the clearance has almost disappeared.

A readout loss can reward both vectors because both give the right answer. Geometry distinguishes them: one is comfortably inside the cell; the other is near trouble.

Even a large safety ball only guarantees the current answer. To keep tracking, the next event must carry the state into the correct next region. That brings us from geometry to dynamics: how the points move.

## 5 Errors: the miss, drift, contraction and the shrink factor

Define the **error vector** as the displacement from the centre of the correct class:

$$
e_t=z_t-c_{q_t}.
$$

Its size is $\|e_t\|$. This is representational error, not necessarily an incorrect answer.

There are two sources of next-step displacement. First, even an update starting exactly at the current centre may miss the next centre. This **miss** is:

$$
m(q,a)=F_a(c_q)-c_{\delta(q,a)}.
$$

Second, an existing displacement can be stretched, preserved, rotated, or shrunk by the update.

**Drift** is the resulting movement away from the intended representation over repeated events. The miss can inject fresh error each step; the update’s local behaviour determines what happens to old error.

**Contraction** means nearby representations move closer together under an update. A **shrink factor** $\rho<1$ quantifies that reduction. If the miss has size at most $b$, a useful bound is:

$$
\|e_{t+1}\|\le \rho\|e_t\|+b.
$$

This says: shrink the inherited error, then allow for fresh error.

Without a fresh miss, an error of size one shrinking by $0.7$ becomes:

```text
Step:    0     1     2      3       4        10
Error:   1    0.7   0.49   0.343   0.2401   0.0282
```

After ten steps, about $0.03$ remains.

With a fresh miss of $0.01$ each step, the error need not reach zero. The bound approaches $0.01/(1-0.7)\approx0.033$. Contraction continually removes enough old error to balance the new error.

At factor $1.0$, old error persists. If each event adds another $0.01$ in the same direction, the total becomes $0.10$ after ten events and $1.00$ after a hundred. Randomly oriented errors can behave differently, but there is no automatic restoring force.

Picture a marble near the bottom of a valley. A nudge is corrected as it rolls back. On a flat plateau, a nudge leaves it displaced, and repeated nudges can carry it away.

There is also a distinction between the **error direction**, the direction in which the tracker is actually displaced, and the **worst-case stretch**, the largest amplification over all possible small displacement directions.

On the measured card trackers, one event shrinks errors along the error direction by about $0.68$ on 99% of steps. Yet the worst-case one-event stretch is about $1.8$, in directions those errors do not take. A network can therefore repair its observed errors while being locally expansive elsewhere.

The **top Lyapunov factor** summarizes the strongest long-run, per-event growth of very small perturbations along an input trajectory. Roughly, if $G_T$ is the largest amplification through $T$ successive local updates, this factor is the long-run value of $G_T^{1/T}$. Below one indicates eventual contraction along that trajectory; above one indicates growth.

It is not simply the largest one-event stretch. Updates can rotate directions, so the most expansive directions at successive steps may not line up.

**Transient gain** is temporary amplification before eventual shrinkage. An error of $0.08$ might first grow to $0.16$ and later fall to $0.04$. If the safety radius is $0.12$, eventual recovery comes too late: an intermediate answer may already be wrong.

Chung et al. (2026) establish a relevant limitation: affine recurrences—linear transformations plus offsets—cannot correct errors in state-separating directions once they preserve the state representations under their assumptions. Preserving distinctions and correcting deviations require different behaviour. [Chung et al., *Rethinking State Tracking in Recurrent Models Through Error Control Dynamics*](https://arxiv.org/abs/2605.07755)

## 6 The blindness theorem

A **training trajectory** is the sequence of neural states reached while processing a training example. Training exposes the network to many such paths through its state space.

The blindness theorem identifies missing information in objectives that inspect only those reached states: their values do not determine whether nearby errors shrink or grow.

Consider a simple local coordinate $x$ measuring displacement sideways from a training path. Suppose every training example has $x=0$. Two candidate update rules could behave as:

$$
x_{\text{next}}=0.7x
\qquad\text{or}\qquad
x_{\text{next}}=1.1x.
$$

On the path, both return zero. They can have identical predictions, identical reached representations, and identical losses there. Away from the path, one corrects a displacement and the other enlarges it.

This is an information limitation. A sufficiently flexible model can agree with another model at all sampled states while differing nearby. An objective depending only on those agreements cannot distinguish their stability.

The marble picture makes this concrete. Imagine a narrow route painted along the bottom of a valley. Now imagine the same painted route across a plateau—or along a ridge. The observations exactly on the route can match. A sideways push reveals the difference.

**Next-token likelihood**, the probability assigned to the correct next text piece, is a special case. Maximizing it rewards correct predictions on the supplied histories. If two networks make the same predictions along those histories, that objective cannot distinguish their responses to an unobserved internal displacement.

Even directly rewarding correct next-state values does not automatically solve this problem. Two update rules can hit the same target from a sampled starting point while behaving differently around it.

The claim is not that ordinary training can never discover stability. Architecture, shared parameters, and optimization can favour stable solutions. The language-model host appears to provide useful structure of this kind.

Nor is the theorem about objectives that explicitly examine perturbations or local sensitivity; those inspect additional information. Its scope is losses restricted to behaviour on the training states themselves.

The sharp question for a proposed objective is therefore: *What observation would make it prefer the valley to the plateau?* If the answer is “none,” stability is being left to other influences.

## 7 The remedy: probe off the path

A **kick** deliberately perturbs a neural state before continuing the computation. If $u$ is a direction of length one and $\epsilon$ is the **kick size**, then:

$$
z^{\text{kick}}=z+\epsilon u.
$$

The kick moves the marble sideways so training can observe the restoring behaviour.

Kick size matters. A tiny kick may reveal only extremely local behaviour or be obscured by numerical precision. A very large kick may cross into a region representing another legitimate card order. The useful question is whether plausible errors inside the intended state’s neighbourhood are repaired.

An **aimed kick** chooses the direction purposefully rather than perturbing arbitrarily. One can aim toward a known displacement or along the observed error direction. A different strategy aims along the worst-case stretch direction.

These strategies ask different questions. The worst-case direction asks whether *every* small displacement contracts. The error direction asks whether the network corrects the displacement it is actually developing.

A **window** is the number of events run after the kick before assessing recovery. For a four-event window, the perturbed state experiences four successive updates. This can reveal recovery that is not visible after just one event.

For example, factors $1.5$, $0.5$, $0.5$, and $0.5$ give an overall factor of $0.1875$. The initial expansion is followed by substantial shrinkage. Such a window can detect that behaviour, although intermediate readout safety still matters.

The measured card dynamics explain why a shorter test may suffice. Along the error direction, a single event usually already shrinks the displacement, by about $0.68$ on 99% of steps. There is then no need to wait four events merely to observe repair.

That finding motivates replacing a multi-event window with one event along the error direction. It does **not** imply that every direction contracts, every event succeeds, or arbitrary inputs are certified.

The project’s single-loss experiments reflect this distinction: the one-event version aimed along the worst-case direction failed, while the one-event version along the error direction is being tested. The measurement supports the experiment; its final training outcome remains open.

Perturbation training itself has precedents. Oliva and Lago-Fernández (2021) showed that noise training can produce stable clusters resembling automaton states, with recovery after perturbations. The present questions concern how to target that repair, measure it, and connect it to exact tracking. [Oliva and Lago-Fernández, *Stability of Internal States in Recurrent Neural Networks Trained on Regular Languages*](https://arxiv.org/abs/2006.10828)

## 8 What the remedy buys: robust cells

A **robust cell** represents a true state with enough room for small numerical errors, while ensuring that every allowed event sends it into the appropriate next cell.

For cards, imagine 120 labelled balls. A swap carries the entire ball for `A B C D E` safely inside the ball for `C B A D E`. “Do nothing” keeps the ball inside itself. The network need not hit a single exact point; it must preserve the correct region.

A useful ball-based form of the **robust Myhill–Nerode theorem** combines the symbolic equivalence classes with this geometric condition. Suppose all balls have radius $r$, decode correctly, and every event satisfies:

$$
F_a(B(c_q,r))
\subseteq
B(c_{\delta(q,a)},\,\rho r+b),
\qquad
\rho r+b<r.
$$

Here $\rho$ bounds inherited-error amplification throughout the ball, and $b$ bounds the centre miss. Every event carries each ball into a smaller ball around the correct next centre.

The proof is simple **induction**: establish the claim initially, then show one correct step preserves it. Start inside the correct ball. The next event lands inside the next correct ball. Apply the same reasoning again, as many times as desired. Sequence length never enters the condition.

The symbolic part explains which histories may share a cell. The geometric part explains how imperfect numerical representations can implement those states reliably.

Robust-cell ideas have substantial prior history. Casey (1996) connects recurrent computation to the state structure of minimal automata. Brandoit et al. (2026) characterize length-independent tracking at finite precision through a one-event cell condition equivalent to exactness at every length in their setting. The convenient shrinking-ball condition above is a sufficient geometric route; arbitrary exact implementations need not use round balls or this particular uniform bound. [Casey, *The Dynamics of Discrete-Time Computation*](https://pubmed.ncbi.nlm.nih.gov/8768390/), [Brandoit et al., *Length-Independent State Tracking Under a Parallel Scan*](https://arxiv.org/abs/2609.32447)

A **certificate** is a computer-checkable proof that the required conditions hold. It must cover every relevant state and event, correct decoding, the initial state, and the numerical implementation. Checking many sampled points inside a ball is evidence, not a proof about its entire interior.

**Snapping** simplifies the problem. After each neural update, replace the result with its nearest class centre. The system then carries one of finitely many representatives.

For cards, there are ten distinct swaps and one “do nothing” event. With 120 centres, there are $120\times11=1,320$ centre-event transitions to check, together with initialization and decoding. If all transitions are correct under the specified numerical and tie-breaking rules, induction proves exactness for every input at every length.

The project’s snapped trackers are certified exact this way. The continuous trackers—the ones that keep their numerical outputs without snapping—are not yet certified. Their per-event miss is about as large as their safety balls, leaving insufficient room for the desired bound. Snapping changes the system, so its certificate cannot be transferred to the continuous tracker.

Now add bounded noise of size at most $\eta$ after every event. A sufficient safety condition becomes:

$$
\rho r+b+\eta<r.
$$

In an illustrative example, $r=0.20$, $\rho=0.70$, and $b=0.02$ leave room for noise below $0.04$ per event. These numbers illustrate the condition; they are not measured project values.

The **noise threshold** is the noise level at which exactness breaks under a specified test. Empirically, the current method tolerates about twice the per-event noise of other recipes. The top Lyapunov factor alone ranks tolerance with rank correlation $0.95$—a measure near one meaning the two orderings closely agree.

This is **learned analog error correction**: continuously varying numbers are repeatedly repaired so they continue to carry an exact discrete meaning. Under their noise assumptions, Maass and Orponen (1998) show that noisy analog networks have at most finite-state language-recognition power, providing theoretical context for this connection. [Maass and Orponen, *On the Effect of Analog Noise in Discrete-Time Analog Computations*](https://igi-web.tugraz.at/people/maass/psfiles/87a.pdf)

## 9 Typical inputs versus every input

An **input law** is the probability rule generating event sequences. “In law” means a claim concerns behaviour under that rule, rather than every possible sequence.

For example, a generator may independently choose among the eleven card events with equal probability. Long random sequences then contain varied swaps and occasional runs of “do nothing.”

A tracker can be highly reliable under that law while failing on an unusual sequence. Repeating “do nothing” thousands of times is a particularly revealing test: the symbolic state should remain unchanged, while the same neural update is applied repeatedly.

If that update leaves a tiny systematic miss, repetition can accumulate it in one direction. Varied events might rotate or remove the displacement, hiding the weakness in typical testing.

This is an observed failure, not merely a possibility. Repeating one input long enough breaks 8–13 of 20 trained card trackers under every loss tried. Consequently, long random-test exactness and favourable measured contraction do not establish exactness on every input.

**Coverage** means which states, events, histories, and nearby numerical regions an evaluation actually examines. Seeing all 120 card states and all eleven events does not necessarily cover their dangerous combinations or the displaced states reached after unusual histories.

A **counterexample** is an input on which the claimed behaviour fails. A **counterexample loop** repeatedly proposes a tracker, searches for a failure, adds that failure to the training or analysis set, and tries again.

For cards, useful searches include repeated events and short cycles such as applying the same swap twice. Each cycle returns the true state to where it started, while potentially exposing accumulated neural drift.

Angluin’s 1987 work established a foundational framework for learning minimal automata through queries and counterexamples. It provides a clear precedent for using failures to refine a proposed state machine. Neural training adds difficulties: repairing one behaviour may disturb another, and a practical search need not find every failure. [Angluin, *Learning Regular Sets from Queries and Counterexamples*](https://people.eecs.berkeley.edu/~dawnsong/teaching/s10/papers/angluin87.pdf)

Failure to find another counterexample is useful evidence. A certificate is the step that turns such evidence into a universal claim.

## 10 The training recipes we compared and what each ablation taught us

A training **arm** is one recipe in a comparison. An **ablation** removes or changes a component to investigate its contribution.

The components address different questions: Can the answer be read? Are equivalent histories represented similarly? Does the representation remain controlled? Are displaced states repaired?

| Name | Meaning |
|---|---|
| **O** | Readout loss only, with no closure. |
| **O+N** | Readout loss with fixed-norm closure. |
| **O+Nc** | Readout loss with centred closure. |
| **NS** | Next-state prediction; this component was dropped. |
| **EQ** | An equivalence term pulling certified-equivalent histories’ states together. |
| **FULL+Nc** | The older four-part recipe, using centred closure. |
| **M** | The current method: readout + EQ + centred closure + aimed kick term. |
| **SH4** | A single-loss version that kicks the state, then runs four events. |
| **SH1** | A single-loss version using one event, kicked along the worst-case direction; it failed. |
| **SH1f** | A single-loss version using one event along the error direction; testing is ongoing. |

For intuition, EQ rewards small distances between states reached by certified-equivalent histories. A simple illustrative penalty would be $\|z(h)-z(h')\|^2$ when $h\sim h'$. This discourages the network from retaining irrelevant details of how it reached a card order.

NS instead asks the network to predict a target next-state representation. Its removal should not be read as evidence that state transitions are unimportant. Predicting sampled next states and controlling behaviour around them are different requirements.

On the language-model host, the ablations used ten seeds. Removing closure left only 0–1/10 exact across the tested tasks. Closure was therefore needed everywhere in that comparison.

Removing EQ left 3/10 exact on programs, 1/10 on counting, and 0/10 on stories. EQ was not needed on addition or reversible programs in those experiments. A **reversible program** uses updates that can be undone. These results show that the value of equivalence supervision depends on the task; they do not establish a universal rule about all reversible computations.

Removing the aimed kick caused no reported need for it on that host. The explanation is that each event rewrites much of the state, so closure alone already produces shrinking errors. The explicit kick term can therefore be redundant in an architecture whose updates supply the relevant repair.

The small network trained from scratch tells a different story. On cards, also called **S5**, the task of permutations of five objects, exactness rose from 12/20 without the aimed kick to 20/20 with it. Here the kick was needed for reliable success across seeds.

These comparisons separate a mechanism from a particular loss term. Error correction can be necessary even when an explicit error-correction term is unnecessary because the host already supplies it.

The single-loss experiments pursue a cleaner recipe. SH1’s failure cautions against forcing contraction in the wrong directions. SH1f tests the more targeted hypothesis suggested by the measured error dynamics. Its outcome is not yet known.

## 11 What we have shown, and what is still open

The reported experiments show exact tracking at 64–256 times training length across cards, Lean proof rewriting, program execution, reversible programs, addition, counting, and natural-language stories. Lean is a system for writing and checking formal proofs; proof rewriting changes a proof expression through permitted steps.

The cube tracker remained exact for 10,000 moves. In the reported comparisons without tools, frontier models—Claude Fable 5.1, GPT-6 Astra, and Gemini 4 Argon—lost track by 256–1,024 moves.

Those models can solve some long tasks by writing out every step, using tens of thousands of reasoning tokens: text pieces generated as intermediate reasoning. They still fail on others; the reported 1,024-event card test had 4 of 15 correct. These are results under the tested conditions, not claims about every possible prompting strategy.

Inside a 0.5-billion-parameter language model’s own hidden state, one of three seeds tracked an eight-variable program exactly for 4,096 statements. More seeds are running. This is evidence that the mechanism can live inside the model, with replication and breadth still unresolved.

The evidence supports three distinct conclusions. Long extrapolation is achievable on the tested tasks. Error dynamics help explain reliability and noise tolerance. Snapping enables a certificate for the resulting discrete tracker.

The remaining questions are substantial:

- **A cleaner principle:** Can one objective reliably replace the collection of terms? A fresh search is running.
- **Every-input continuous exactness:** Can the trained network satisfy a verified robust-cell condition without snapping?
- **Replication inside the model:** Does the in-model result hold across more seeds and tasks?
- **A general model:** Can this become part of a fine-tuned model—a pretrained model further trained for new behaviour—that supports broader tasks?

For research feedback, the useful habit is to keep three questions separate: what was tested, which mechanism explains the result, and what has been proved. Each contributes something different to understanding learned exact state.

## 12 A glossary

**Ablation.** A comparison that removes or changes a training component to test its contribution.

**Aimed kick.** A deliberate state perturbation in a selected direction, used to train or measure recovery.

**Analog error correction.** Repairing continuously varying numerical representations so they preserve exact discrete meanings.

**Arm.** One training recipe in an experiment.

**Bisimulation.** A relation matching states by their outputs and corresponding future transitions.

**Bisimulation metric.** A numerical measure of behavioural similarity between states.

**Cell radius.** Distance from a chosen class centre to the nearest wrong-answer boundary.

**Centred closure.** A closure constraint controlling the representation relative to a centre.

**Certificate.** A computer-checkable proof covering a stated claim, such as correctness for every input length.

**Certified pair.** Two histories whose future equivalence has been established by a trusted procedure.

**Checker.** A trusted implementation of the task rules.

**Class centre.** A representative vector for one true task state.

**Closure.** The property that valid representations update to valid representations; a closure loss encourages it.

**Contraction.** Reduction of distances between nearby representations under an update.

**Counterexample.** An input that demonstrates failure of a proposed correctness claim.

**Counterexample loop.** Repeatedly finding failures and using them to improve a candidate system.

**Coverage.** The states, inputs, histories, and numerical regions actually examined.

**Drift.** Movement away from an intended representation over repeated updates.

**Equivalence class.** All histories with identical relevant future behaviour.

**EQ.** A training term pulling representations of certified-equivalent histories together.

**Error direction.** The direction of the tracker’s displacement from its intended representative.

**Exact at a length.** The final state is right on at least 99% of the 512 test problems at that length (507 or more).

**Finite automaton.** A machine with finitely many states and an event-dependent update rule.

**Finite precision.** Numerical storage and arithmetic using a limited number of bits.

**History.** The sequence of events already processed.

**Host.** The architecture containing the tracker.

**In law.** With respect to a specified probability rule for inputs.

**Induction.** Proving an initial case and a preservation step, thereby covering every finite number of steps.

**Kick.** A deliberate perturbation of neural memory; its size is the displacement magnitude.

**Length generalization.** Successful operation on longer sequences than those used in training.

**Margin.** Clearance between a representation and a wrong-answer boundary.

**Minimal automaton.** The smallest state machine sufficient to reproduce the task’s behaviour.

**Miss.** The discrepancy between an updated class centre and the correct next centre.

**Nerode equivalence.** Equivalence of histories that no possible continuation can distinguish.

**Next-token likelihood.** The probability assigned to the correct next piece of text.

**Noise threshold.** The noise level at which exactness breaks under a specified evaluation.

**Norm.** A measure of vector size; ordinary straight-line length is one example.

**Readout.** The function converting neural memory into an answer.

**Readout cell.** All neural representations decoded as the same answer.

**Robust cell.** A correctly decoded region whose updates remain inside appropriate next-state regions.

**S5.** The permutations of five objects, underlying the five-card task.

**Safety ball.** A ball around a class centre entirely inside its correct readout cell.

**Seed.** The random initialization and training randomness identifying an independently trained copy.

**Shrink factor.** The multiplier describing reduction of an inherited displacement.

**Snapping.** Replacing an updated neural state with its nearest class centre.

**State.** The information from the past needed to determine relevant future behaviour.

**Top Lyapunov factor.** The strongest long-run per-event growth factor of tiny perturbations along a trajectory.

**Tracker.** The learned mechanism carrying and updating state.

**Training trajectory.** The sequence of neural states reached on a training example.

**Transient gain.** Temporary perturbation growth before possible later shrinkage.

**View.** A chosen representation of memory used for measurement or a loss.

**Window.** The number of events run after a kick before assessing its effect.

**Worst-case stretch.** The largest local amplification over all small perturbation directions.