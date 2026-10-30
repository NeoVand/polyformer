# The Loop That Closes

*Machines that read long sequences drift off course, and writing down their work does not save them. A 1958 definition of what it means to be "in a state" has given them a way to stay exact, along with a proof of why ordinary training never could.*

*An imagined article, written as an exercise in finding the story. The outside voices are composites and are deliberately unnamed.*

---

Here is a test that sounds too easy for modern artificial intelligence. Take four variables, each holding a 0 or a 1. Write a short Python program that shuffles them: copy this one into that one, set this one to 1, add those two and keep the remainder after dividing by 2. Now make the program 1,024 lines long, and ask what each variable holds at the end.

A patient child with a pencil could do it. The task is tedious, not hard. Yet it defeats the machines we are told can reason. Take a language model, fine-tune it for exactly this job, and let it write the four values down after every line, the way a student shows their work. On programs of 16 lines it is perfect. By line 64 it gets a large share of programs wrong, and by line 256 most of them. Its mistakes are not arithmetic; on short programs it gets every line right. It simply loses its place, and why it does so turns out to be one of the more surprising lessons of a new paper.

That paper describes a system that does the same task without writing anything down at all. It reads each line through the same kind of language model, keeps a small internal state of 128 numbers, and at the end reports the four values. It was trained only on programs of 16 lines or fewer. Given 512 programs of 1,024 lines, it gets every one exactly right, on each of three independent training runs: 64 times longer than anything it saw.

The difference is not more data, more parameters or a cleverer architecture. It is one extra question asked during training, and the idea behind it is almost seventy years old.

## A watch that passes inspection

Every system that reads a sequence one step at a time faces the same hazard. It carries a summary of what it has seen so far, updates that summary at each step and uses it to answer questions. If the update is slightly wrong, the error does not stay small. It is carried forward, and the next step adds its own. Sailors navigating by dead reckoning knew the problem: a heading off by a fraction of a degree is harmless for an hour and fatal for a week.

Neural networks learn these updates by practicing on sequences of some fixed length and being penalized for wrong predictions. The natural assumption is that a network that predicts well has learned the right update, and that if it drifts on longer inputs, more data or more training will cure it.

The paper's first result says that assumption is wrong, and says exactly why. Picture a watch that loses one second a day. Inspect it for an hour and it passes. No hour-long inspection, however careful, can tell that watch from a perfect one, because the error it is looking for is smaller than anything an hour can reveal.

Training is the hour-long inspection. The authors prove that an error per step small enough to escape notice over the training length changes the training loss by less than the loss's own unavoidable floor. The loss cannot tell the exact update from one that will fail at greater lengths. Beyond a fixed multiple of the training length, set by how confident the model's answers are, many different updates score identically in training and diverge afterwards, and which one training lands on is left to chance.

"We kept expecting the drift to wash out with more data," one of the authors said. "The theorem told us it can't. The loss is looking through a window that is too short to see the error, and more windows of the same size don't help."

## A long detour

The project did not begin with that theorem. It began, the authors say, as a hunt for a better building block for language models, a successor to the attention mechanism at the heart of the transformer. For months they built and tested new kinds of layers: attention over triples of words instead of pairs, layers that carry geometric frames along a sentence, recurrent loops bolted onto transformers. Some learned elegant structure on puzzles designed for them. On ordinary text, nearly all of them tied with the standard transformer, and the few gains were too small to matter.

"At some point we stopped asking what the next layer should be," the lead author said, "and asked what the thing we were trying to compute is. What is a state supposed to be? That question had an answer, and the answer was old."

## What a state really is

In 1958 the logician Anil Nerode, studying the abstract machines that underlie computer science, asked what it means for a machine to be in a particular state. His answer is one of those definitions that seems obvious once you hear it and turns out to be bottomless.

Two histories, Nerode said, are equivalent if no future can tell them apart. If every possible continuation produces the same outcomes after history A as after history B, then the difference between A and B will never matter again. A state, on this view, is not a thing a machine stores. It is the set of all pasts that the future cannot distinguish.

Chess players know this without the vocabulary. Two different move orders often lead to the same position, a "transposition." A strong player does not care which order produced the board in front of them; the position is the position. A player who remembered the route rather than the destination would be carrying information that can never help and could only confuse.

From this definition follows something remarkable. For any task with finitely many such classes of interchangeable pasts, there is a smallest machine that performs it, with exactly one state per class, and it is unique. Computer scientists call it the minimal automaton. It forgets everything that does not matter and keeps everything that does.

The new work turns Nerode's definition into a training signal. Many tasks come with a referee that can certify when two different histories lead to the same place. A proof assistant can certify that two chains of algebraic rewrites end at the same expression. A Python interpreter can certify that two programs leave every variable with the same value. The rules of a mathematical group can certify that two strings of moves multiply out to the same element. So the authors added one requirement: whenever the referee certifies that two histories arrive at the same place, the network's internal states for those two histories must coincide.

"The referee never tells the model what the state is," another author said. "It only says that two roads arrive at the same town. That turns out to be enough."

## Why a loop beats a test

Why does this succeed where ordinary training fails? It comes down to how each signal responds to a small error.

The ordinary loss responds to drift the way the floor of a wide, flat valley responds to a marble placed slightly off center: hardly at all. Near the right answer it is almost perfectly flat, precisely where precision is needed. The new signal responds like a spring. Two equivalent histories whose states have drifted apart by a small amount produce a pull proportional to that amount, with a stiffness that does not fade as the model grows confident. The error the ordinary loss cannot see is exactly the error this signal measures.

There is a geometric picture here that the authors find hard to resist. Two histories the referee certifies as equivalent leave the same starting point and arrive at the same destination, so together they form a closed loop. A model whose state is exact closes every such loop: follow either path and you arrive at the same internal state.

A drifting model does not. It is like walking an arrow around a loop on the surface of a globe, keeping it as straight as you can at every step, and finding when you return that it no longer points where it started. Mathematicians call the mismatch holonomy, and it measures the curvature of the surface. In the paper's language, drift is curvature, and the new training signal asks the model's internal geometry to be flat around every loop a referee can certify.

Roboticists will recognize a cousin of the idea. A robot mapping a building by dead reckoning accumulates drift until it recognizes a place it has already been; at that moment it can measure the gap and correct its whole map, a step called loop closure. Here the referee supplies the closed loops, thousands of them, during training.

One subtlety mattered. A network can satisfy the referee and still cheat over time, by hiding a counter in a corner of its state that the final readout ignores and letting it tick upward until it leaks into the answer. The authors close that door with a second signal, published by another group in 2025: the network must also predict its own next internal state. The paper then states three requirements on a single state: predict the next output, stay consistent with yourself, and meet your equivalents. It proves that, with enough variety in training, the only state that satisfies all three is Nerode's minimal automaton, and that a model holding it is exact at every length.

## Five hundred times longer

The first test used Lean, a proof assistant that mathematicians use to check proofs line by line, as the referee. The task was to track an algebraic expression through a chain of rewrites, the elementary moves of school algebra: swap the two sides of a sum, regroup a product. With four symbols there are 960 possible expressions. A small network read one rewrite at a time and reported the current expression. It practiced on chains of eight rewrites.

Trained the ordinary way, it was perfect at eight and drifted beyond. Trained with the referee's signal and self-prediction together, it was exact on every one of three training runs at 4,096 rewrites, 512 times the length it practiced on. A transformer given the same data, the same supervision and twice the computation per step was not exact even at eight rewrites and was near zero by 64.

The pattern held when the referee was the multiplication table of a 120-element group and when it was a code interpreter. And it held with a pretrained language model in the loop: the result at the top of this article uses an off-the-shelf code model with half a billion parameters, frozen, to read each line, with the small exact state carried beside it.

An exact state is also useful to anyone building machines that search for proofs, because every call to a proof checker costs time. On the algebra puzzles, a search that moved through the network's predicted states consulted the checker only once per solved problem, to confirm the final answer. A search that checked every step needed between 64 and 442 calls to solve as many.

## A machine appears

What does an exact state look like from the inside? The authors looked.

For the 960 expressions of the algebra task, the trained network had placed every visit to a given expression into one tight cluster, one cluster per expression, each far from the others. Reach an expression after ten rewrites or four thousand, by any route, and the state lands in the same small spot. The network's continuous space of 128 numbers had been carved into exactly 960 islands. It had built Nerode's minimal automaton out of real numbers. The network trained without the referee showed nothing of the kind: the states for a single expression were smeared across much of the space.

Then the authors kicked it. Midway through a chain they shoved the network's state off its island and watched. The exact network pulled itself back to the right island within about ten steps and carried on as if nothing had happened, for kicks up to a sizable fraction of the distance between islands. Larger shoves knocked it onto the wrong island.

That behavior has a famous precedent. Long telegraph lines, and later digital networks, work because repeaters along the way do not merely amplify the signal; they restore it, snapping a noisy voltage back to a clean 0 or 1 before passing it on. Noise below a threshold never accumulates, however long the line. The trained network had learned to be its own repeater. Training had turned an analog system into a digital one.

"Nobody told it to correct errors," one of the authors said. "We asked equivalent histories to meet. Error correction is what meeting looks like when you're allowed to be slightly wrong."

The picture also yields a practical tool. Because drift is the part of the error that accumulates, the gap between two certified-equivalent states keeps widening along the sequence in a model that will drift and stays put in one that will not. Measured early, at lengths seen in training, that widening predicts which training runs will fail far beyond them.

## Consistency is not knowledge

The most instructive part of the paper may be where the method stops.

The authors made the programs harder: eight variables holding numbers from 0 to 15, with addition, subtraction, multiplication and conditionals. Now the small exact state could not even learn programs of the training length. Deeper networks did not help, and neither did more varied practice.

The explanation is a theorem with a plain moral: the referee's signal adds consistency, not knowledge. Every equivalence the interpreter can certify, such as swapping two lines that do not touch the same variables, is respected just as well by a model that gets subtraction wrong as by one that gets it right. The signal can select an exact state only among the updates a network can already compute. And a single undifferentiated list of numbers turned out to be bad at one specific job: keeping track of which named variable is which. Trained on single lines, it learned every operation that does not care about the order of its inputs, like addition, and failed the ones that do, like subtraction. Give the state one slot per variable, read and written by name, and programs of the training length were learned at once, though over a thousand lines that version still settled at about three programs in four.

Then came the result that reframes the most popular technique in modern AI. The language model that writes its state after every line had failed at length. Was that a failure of reasoning? The authors changed two things. First, they cut the model's view down to just its own last written state and the current line, instead of the whole growing transcript. The collapse stopped. Second, they trained that single-step update on states drawn at random from every possible value, instead of the mostly zero states that short programs produce. Now the language model was exact at 1,024 lines on every training run, on the hard arithmetic programs, making about one error in a hundred thousand steps, each repaired when the affected variable was later overwritten.

Think of two bookkeepers. One rereads the entire ledger from the first entry every time a new line arrives; as the ledger grows, so do the chances of losing the place. The other carries forward a running balance and only ever looks at the balance and the newest entry. The second can keep going indefinitely. Chain of thought, as usually practiced, is the first bookkeeper.

"It wasn't failing at arithmetic," one author said. "It was failing at bookkeeping. Once it only had to look at its own last line, and it had practiced on the kinds of lines it would actually see, it was exact."

The explanation is the same idea that drives the rest of the paper. A model that reads only its last state treats any two histories that reach the same state identically, by construction: equal states, equal views. The loop closes because there is nowhere left for the difference to hide.

## Where the referee falls silent

The method needs a referee, and the authors are candid about where there is none, or where one is not enough.

They tried it on real mathematics, on proofs from the large library of formalized mathematics that Lean users maintain. The question was whether a model could predict, several steps into a proof, whether the checker would accept a given next move. Even a model handed the checker's own exact description of where the proof stood did no better than a lookup table keyed on the first word of the proposed move. At the scale the authors could afford, the content of mathematics, what a proof step actually does, was the bottleneck, not keeping track of the state.

"It's a clean negative, and an honest one," said a researcher who builds automated provers and was not involved in the work. "It separates the tracking problem from the understanding problem. They've solved the first one where the second one is easy. The real question is what happens when you put this inside a model that already understands mathematics."

Language is harder still. Two paraphrases plausibly mean the same thing, but nothing certifies it, and the authors report that an early attempt to treat paraphrases as equivalent histories collapsed. A theorist who studies the limits of transformers, also unaffiliated with the paper, pointed to scale: "Four variables, 960 expressions. These are small worlds, and the state lives in a little module next to the language model, not inside it. The theory is the part I'd bet on. Whether it scales is a separate question."

The authors accept the facts and weigh them differently. The worlds are small, they say, because exactness only means something where it can be checked, and nothing in the theorems depends on size.

## What stays the same

In 1872 the mathematician Felix Klein proposed a way to organize all of geometry: a geometry is defined not by its objects but by the transformations it ignores. Euclidean geometry is whatever is unchanged when you slide and rotate; projective geometry is whatever survives a change of perspective. What is real, for Klein, is what is invariant.

The new work makes the same move about computation. A model's state is not a list of numbers to be kept accurate. It is whatever stays the same across every history a referee certifies as interchangeable. Training stops asking only "Did you predict the next thing?" and starts asking "Do you treat as the same everything that is the same?"

That shift points in several directions. It gives a new job to the formal tools that mathematicians and programmers have spent decades building. Proof assistants, interpreters and type checkers are usually brought in at the end, to grade an answer. Here they act at the start, as teachers that certify which histories must agree, and a model that learns from them can stand in for them during search.

The stakes extend well beyond puzzles. AI systems are increasingly asked to act as agents that carry out long tasks, editing a codebase over thousands of steps or following a procedure across a long session, and they fail in exactly the way this paper describes: each step looks fine, and somewhere along the way they lose track of where things stand. A model that can carry an exact state, and a way to tell during training which runs will drift, address that failure at its root.

It also bears on the growing debate over whether machines should reason in words at all. Writing every step down is expensive, and the paper shows it is fragile for reasons that have nothing to do with reasoning. A small state that writes nothing, held to Nerode's standard, stays exact where the words fall apart; and when words are used, they work best as a running balance rather than a transcript.

And it leaves a question about language open. If meaning is what survives every way of saying the same thing, then a sentence's meaning is something like its address in the vast space of all the sentences interchangeable with it. Everyday language has no referee to certify those equivalences. Finding one, or learning one, may be the long road from programs and proofs to ordinary text.

For now, the picture the paper leaves is simple. Two paths leave the same point and arrive at the same place. A model that has grasped the task closes the loop. One that has not leaves a small gap, too small for any test of ordinary length to notice, that grows with every step it takes. What separates the two is a single question asked during training, borrowed from a definition written in 1958: did you end up in the same place?
