# The Loop That Closes

*Machines that read long sequences drift off course, and writing down their work does not save them. A 1958 definition of what a "state" is has given them a way to stay exact, and a proof of why ordinary training never could.*

*An imagined article, written as an exercise in storytelling. The outside voices are composites and are deliberately unnamed.*

---

Here is a test that sounds too easy for modern artificial intelligence. Take four variables, each holding a 0 or a 1. Write a short Python program that shuffles them: copy this one into that one, set this one to 1, add those two and keep the remainder after dividing by 2. Now make the program 1,024 lines long, and ask what is in each variable at the end.

A patient child with a pencil could do it. The task is tedious, not hard. Yet it defeats the machines we are told can reason. A language model fine-tuned for exactly this job, and allowed to write the four values down after every single line, gets programs of 16 lines right every time. By line 64 it is wrong on a large share of programs. By line 256 it is wrong on most of them. It never makes an arithmetic mistake on any one line. It simply loses its place.

A new paper describes a system that does the same task without writing anything down at all. It reads each line through the same kind of language model, keeps a small internal state, and at the end reports the four values. It was trained only on programs of 16 lines or fewer. On 512 programs of 1,024 lines it is right on every program, on every one of three independent training runs: 64 times longer than anything it saw.

The difference is not more data, more parameters or a cleverer architecture. It is one extra demand made during training, and the idea behind it is almost seventy years old.

## A watch that passes inspection

Every system that reads a sequence one step at a time faces the same hazard. It carries a summary of what it has seen so far, updates that summary at each step, and uses it to answer questions. If the update is slightly wrong, the error does not stay small. It is carried forward, and the next step adds its own. A navigator doing dead reckoning knows the problem: a heading that is off by a fraction of a degree is harmless for an hour and fatal for a week.

Neural networks are usually trained by asking them to predict the next item of sequences of some fixed length, and penalizing their errors. The natural assumption is that a network that predicts well has learned the right update, and that if it drifts on longer inputs, more data or more training will cure it.

The paper's first result says this assumption is wrong, and says exactly why. Imagine a watch that loses one second a day. Inspect it for an hour and it passes. No inspection that lasts an hour, however careful, can tell that watch from a perfect one, because the error it is looking for is smaller than anything an hour can reveal.

Training is that hour-long inspection. The authors prove that an error per step small enough to be invisible over the training length changes the training loss by less than the loss's own irreducible floor. The loss literally cannot tell the exact update from one that will fail at a longer length. Beyond a fixed multiple of the training length, set by how confident the model's final answers are, there are many updates that score identically in training and diverge afterwards, and which one training lands on is left to chance.

"We kept expecting the drift to wash out with more data," one of the authors said. "The theorem told us it can't. The loss is looking through a window that is too short to see the error, and adding more windows of the same size doesn't help."

That leaves a question. If the loss cannot see the error, what can?

## What a state really is

In 1958 the logician Anil Nerode, studying the abstract machines that would become the foundation of computer science, asked what it means for a machine to be in a particular state. His answer is one of those definitions that seems obvious once you hear it and turns out to be bottomless.

Two histories, Nerode said, are equivalent if no future can tell them apart. If every possible continuation produces the same outputs after history A as after history B, then nothing about the difference between A and B will ever matter again. The state of the machine is not a thing it stores. It is the set of all pasts that the future cannot distinguish.

Chess players know this without the vocabulary. Two different move orders often lead to the same position, a "transposition." A strong player does not care which order produced the board in front of them; the position is the position. A player who did care, who remembered the route rather than the destination, would be carrying information that can never help and could only confuse.

Nerode's definition yields something remarkable: for any task of this kind there is a smallest possible machine that performs it, with exactly one state per class of interchangeable pasts, and it is unique. Computer scientists call it the minimal automaton. It forgets everything that does not matter and keeps everything that does.

The new work turns Nerode's definition into a training signal. Many tasks come with a referee that can certify when two different histories lead to the same place. A proof assistant can certify that two chains of algebraic rewrites end at the same expression. A Python interpreter can certify that two programs leave every variable with the same value. The rules of a group can certify that two strings of moves multiply out to the same element. So the authors added one requirement: whenever the referee certifies that two histories arrive at the same place, the network's internal states for those two histories must be the same.

"The referee never tells the model what the state is," another author said. "It only says that two roads arrive at the same town. That turns out to be enough."

## Why a loop is better than a test

The reason this works where ordinary training fails is a matter of how each signal responds to a small error.

The ordinary loss responds to drift the way the floor of a wide, flat valley responds to a marble placed slightly off center: barely at all. Near the right answer its slope is almost zero, and its curvature carries the loss floor as a factor, so it is almost perfectly flat exactly where precision is needed.

The new signal responds like a spring. Two equivalent histories that have drifted apart by a small amount produce a penalty proportional to that amount, with a stiffness that does not depend on how confident the model is or how small its loss has become. The error that the ordinary loss cannot see is precisely the error this signal measures.

There is a geometric picture behind this that the authors find hard to resist. Two histories that the referee certifies as equivalent leave the same starting point and arrive at the same destination, so together they form a closed loop. A model whose state is exact closes every such loop: carry the state around one path and back along the other, and you return to where you began.

A drifting state does not. It is like carrying an arrow around a loop on the surface of a sphere, keeping it as straight as you can at every step, and finding when you return that it no longer points where it started. Mathematicians call that mismatch holonomy, and it measures the curvature of the surface. In the paper's language, drift is curvature, and the training signal asks the model's internal geometry to be flat on every loop the referee can certify.

One more ingredient turned out to matter. Constancy on equivalent histories is not quite enough, because a network can hide a counter in some corner of its state that the final readout ignores, let it tick upward step by step, and have it leak out later. The authors pair the referee's signal with a second, self-supervised one that a group published in 2025: the network must predict its own next internal state from its current one. Together with ordinary next-step prediction, the three requirements say that outputs agree, that the state is consistent with itself over time, and that equivalent histories meet. The paper proves that, given enough coverage in training, the only state satisfying all three is Nerode's minimal automaton, and that its readout is then exact at every length.

## Five hundred times longer

The first test used the Lean proof assistant, a program that mathematicians use to check proofs line by line, as the referee. The task was to track an algebraic expression through a chain of rewrites, the elementary moves of school algebra: swap the order of a sum, regroup a product. With four symbols there are 960 distinct expressions. A small recurrent network read one rewrite at a time and reported the current expression. It was trained on chains of eight rewrites.

Trained the ordinary way, it was perfect at eight and drifted beyond. Trained with the referee's signal and self-prediction together, it was exact on every one of three training runs at 4,096 rewrites, 512 times the training length. A transformer, the architecture behind today's language models, trained on the same data with the same supervision and twice the computation per step, was not exact even at eight rewrites and fell close to zero by 64.

The same pattern held when the referee was the multiplication table of a 120-element group and when it was a code interpreter. And it held with a pretrained language model in the loop: the program-execution result at the top of this article uses a frozen, off-the-shelf code model with half a billion parameters to read each line, with the small exact state carried alongside it.

An exact state also turns out to be useful in a way that matters to anyone building systems that search for proofs. Every call to a proof checker costs time. A search that moves through the network's predicted states instead of asking the checker at every step needs to consult the checker only once per solved problem, to confirm the final answer. A search that checks every step needed between 64 and 442 calls for the same success.

## A machine appears inside the network

What does an exact state look like from the inside? The authors looked.

For the 960 expressions of the rewrite task, the trained network had placed every visit to a given expression into one tight cluster, one cluster per expression, each far from the others. Visit the same expression after ten rewrites or after four thousand, by any route, and the state lands in the same small spot. The network's continuous space of 128 numbers had been carved into exactly 960 islands. It had built Nerode's minimal automaton out of real numbers. The plain network, trained without the referee, showed no such structure: states of a single expression smeared across much of the space.

Then the authors kicked it. Midway through a chain they pushed the network's state off its island by a random amount and watched what happened. The exact network pulled itself back to the correct island within about ten steps and carried on as if nothing had happened, for every kick up to a sizable fraction of the distance between islands. Beyond that, it lost the thread.

That behavior has a famous precedent. Long-distance telegraph lines and, later, digital networks work because repeaters along the way do not merely amplify the signal; they restore it, snapping a noisy voltage back to a clean 0 or 1 before passing it on. Noise below a threshold never accumulates, however long the line. The trained network had learned to be its own repeater. Training had turned an analog system into a digital one.

"What surprised me was that nobody told it to correct errors," one of the authors said. "We asked equivalent histories to meet. Error correction is what meeting looks like when you're allowed to be slightly wrong."

The picture also gave a practical tool. Because drift is the part of the error that accumulates, the distance between two certified-equivalent states grows along the sequence in a model that will drift and stays flat in one that will not. Measured early, at lengths seen in training, that growth predicts which training runs will fail far beyond the training length.

## Consistency is not knowledge

The most instructive part of the paper may be where the method stops.

The authors made the programs harder: eight variables holding numbers from 0 to 15, with addition, subtraction, multiplication and conditionals. The small exact state could not even learn programs of the training length. Deeper networks did not help. Neither did training on more varied programs.

Their explanation is a theorem with a plain-language moral: the referee's signal adds consistency, not knowledge. Every equivalence the interpreter can certify, such as reordering independent lines, is respected just as well by a model that gets subtraction wrong as by one that gets it right. The signal can select an exact state only among updates the network can already compute. And a single flat vector, it turned out, is bad at one specific thing: keeping track of which named variable is which. Trained on single lines, it learned every operation that does not care about the order of its two inputs, like addition, and failed the ones that do, like subtraction. Give the state one slot per variable, read and written by name, and the training-length programs were learned at once.

Then came a result that reframes the most popular technique in modern AI. The language model that writes its state after every line had failed at length. Was that a failure of reasoning? The authors tested two changes. First, they cut the model's context down to just its own last written state and the current line, instead of the whole growing history. The collapse stopped; accuracy settled at a level instead of falling to zero. Second, they trained that one-step update on states drawn at random from all possible values, instead of the near-zero states that short programs produce. Now the language model was exact at 1,024 lines on every training run, making about one error in a hundred thousand steps, each one repaired when the affected variable was later overwritten.

Think of a bookkeeper. One rereads the entire ledger from the first entry every time a new line arrives; as the ledger grows, so does the chance of losing the place. Another carries forward a running balance and only ever looks at the balance and the new entry. The second bookkeeper can go forever. Chain of thought, as usually practiced, is the first bookkeeper.

"It wasn't failing at arithmetic," one author said. "It was failing at bookkeeping. Once it only had to look at its own last line, and had practiced on the kind of lines it would actually see, it was exact."

In the paper's terms, the explanation is the same one that drives everything else. A model that reads only its last state line treats two histories that reach the same state identically, by construction: equal states, equal contexts. The loop closes because there is nowhere for the difference to hide.

## Where the referee falls silent

The method needs a referee, and the authors are candid about where none exists or where it is not enough.

They tried it on real mathematics, on proofs from the large library of formalized mathematics that Lean users maintain. There the question was whether a model could predict, several steps into a proof, whether the checker would accept a given next step. Even a model handed the checker's own exact description of the proof state did no better than a lookup table keyed on the first word of the proposed step. At the scale they could afford, the content of mathematics, what a tactic actually does to a goal, was the bottleneck, not keeping track of the state.

"It's a clean negative, and an honest one," said a researcher who builds automated provers and was not involved in the work. "It tells you the tracking problem and the understanding problem are separate. They've solved the first one in the settings where the second one is easy. The interesting question is what happens when you bolt this onto a model that already understands mathematics."

Language is harder still. Two paraphrases of a sentence plausibly lead to the same meaning, but no referee certifies it, and an early attempt to use paraphrases as equivalences collapsed. A theorist who studies the limits of transformers, also unaffiliated with the paper, pointed to the scale: "Four variables, 960 expressions. These are toys, and the state lives in a small module next to the language model, not in the model itself. The theory is the part I'd bet on. Whether the engineering scales is a separate question."

The authors agree on the facts and differ on the emphasis. The domains are small, they say, because exactness is only meaningful where it can be checked, and the theorems do not depend on size.

## Invariants all the way down

In 1872 the mathematician Felix Klein proposed a way to organize all of geometry: a geometry is defined not by its objects but by the transformations it ignores. Euclidean geometry is what stays unchanged when you slide and rotate; projective geometry is what survives perspective. What is real, in Klein's view, is what is invariant.

The new work makes a similar move about computation. A model's state, in this view, is not a list of numbers to be stored correctly. It is whatever stays the same across every history that a referee certifies as interchangeable. Training stops asking only "Did you predict the next thing?" and starts asking "Do you treat as the same everything that is the same?"

That reframing points in several directions at once. It suggests a new role for the formal tools that mathematicians and programmers have spent decades building. Proof assistants, compilers and type checkers are usually used at the end, to grade an answer. Here they act at the start, as teachers, certifying which histories must agree, and the model that learns from them can stand in for them during search.

It also bears on an emerging debate about whether machines should reason in words at all. Writing every step down is expensive, and the paper shows it is fragile for a reason that has nothing to do with reasoning. A small state that never writes anything, held to the standard of Nerode's definition, stays exact where the words fall apart.

And it suggests a question about language that the authors have not answered. If meaning is what survives every way of saying the same thing, then the meaning of a sentence is something like its address in the vast space of all the sentences that are interchangeable with it. Natural language has no referee to certify those equivalences. Finding one, or learning one, may be the long road from programs and proofs to everyday text.

For now, the picture the paper leaves is a simple one. Two paths leave the same point and arrive at the same place. A model that understands the task closes the loop. One that does not leaves a small gap, too small for any test of ordinary length to notice, that grows with every step it takes. The difference between them is a single question asked during training, borrowed from a definition written in 1958: did you end up in the same place?
