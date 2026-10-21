<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import CompositionFigure from '#lib/learn/CompositionFigure.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { NEWTON } from '#lib/viz/computeGraphs.ts';
	import { resolve } from '$app/paths';
	import { number } from '../toc.ts';
</script>

<section class="part" id="part-newton">
	<header class="part-head">
		<span class="roman">Part IV</span>
		<h2>Every arity at once</h2>
		<p class="part-lede">
			Letting one softmax choose among arities still failed on Match-4. This part asks why, what an
			arity really is, and how one layer can offer relations of every size at once, at a cost that
			grows only linearly with the number of tokens.
		</p>
	</header>

	<section class="chapter" id="composition">
		<h3><span class="n">{number('composition')}</span>Big relations do not grow from small ones</h3>
		<p class="src">
			<span class="mark measured"></span>Cloud GPUs, three seeds per model, balanced accuracy
			(chance 50%)
		</p>
		<p>
			The cloud runs score every layer on Match-3, Match-4 and Match-5. Standard attention, at every
			depth we tried, reaches at most 66% on Match-3 and stays at chance above it. Cubic and Feynman
			attention solve Match-3 and stay at chance above it. Dense quartic attention learns Match-4 on
			two seeds of three, after a long plateau.
		</p>
		<p>
			The most telling run gave Feynman attention every building block of the construction in
			section
			{number('newton')}: sums of tokens, products of a token with itself, and products of those
			sums. Multiplying these pieces over two rounds can produce exactly the four-way term Match-4
			needs, and the layer was wider (up to 192) than the 81 cards of the deck. It still stayed at
			chance. The answer could be represented; gradient descent never found it.
		</p>
		<div class="figure wide"><LearnFigure section="composition" /></div>
		<p>
			The leap of section {number('blind')} suggests why. In a group of <MathTex tex="k" /> cards that
			adds up to zero, any fewer than <MathTex tex="k" /> of them look exactly like random cards, so partial
			products carry almost no signal for training to follow. This helps explain the weak signal; it does
			not prove that every gradient vanishes. The experiments point one way: put the full
			<MathTex tex="k" />-way product directly in the layer, instead of asking training to build it
			from pieces <Cite id="abbe" />. To do that cheaply, we need a little algebra.
		</p>
	</section>

	<section class="chapter" id="groups">
		<h3><span class="n">{number('groups')}</span>A group is a rule for combining</h3>
		<p class="src">
			<span class="mark prior"></span>Standard group theory; SET arithmetic <Cite id="davis" />
		</p>
		<p>
			A <em>group</em> is a collection of operations with a rule for combining them. Combining two
			operations gives another one in the collection; there is an operation that does nothing, the
			<em>identity</em>; and every operation has an <em>inverse</em> that undoes it. Finally,
			regrouping three operations does not change the result: you may combine the first two first,
			or the last two. That last rule is <em>associativity</em>.
		</p>
		<p>
			Think of a clock with three positions, 0, 1 and 2. An operation moves its hand forward by
			zero, one or two ticks, wrapping around after 2. One tick followed by two ticks is zero ticks
			overall. Zero is the identity; one and two undo each other. This is addition <em>modulo 3</em
			>, written
			<MathTex tex={String.raw`\mathbb Z_3`} />. A twelve-position clock gives <MathTex
				tex={String.raw`\mathbb Z_{12}`}
			/>.
		</p>
		<p>
			A SET card carries four such clocks, one per attribute; <MathTex
				tex={String.raw`\mathbb Z_3^4`}
			/> means exactly those four clocks. Add cards by adding their four values separately, each wrapped
			at 3. A SET is three cards whose combined move is zero on all four clocks. And here one move then
			another equals the same moves in the other order: addition <em>commutes</em>. A group with
			that property is called <em>abelian</em>, or commutative. Remember the word; it becomes the
			hinge of the whole story in Part VI.
		</p>
		<div class="figure wide"><CompositionFigure section="groups" /></div>
	</section>

	<section class="chapter" id="characters">
		<h3><span class="n">{number('characters')}</span>Relations as agreeing phases</h3>
		<p class="src">
			<span class="mark prior"></span>Characters of finite abelian groups, classical;
			<span class="mark new inline"></span>their use in a relational layer is studied here
		</p>
		<p>
			Here is the idea that makes everything cheap. Draw each clock position as a point on a circle,
			a third of a turn apart. Multiplying two such points, treated as complex numbers of length 1,
			adds their angles, so multiplying points does the same thing as adding clock moves. Now give
			every card a <em>phase</em>, one point on the circle, in a way that turns adding cards into
			multiplying phases. Pick a vector <MathTex tex={String.raw`c \in \mathbb Z_3^4`} /> and send card
			<MathTex tex="x" /> to
		</p>
		<MathTex
			display
			tex={String.raw`\begin{gathered} \phi_c(x) = \omega^{\langle c, x\rangle}, \qquad \omega = e^{2\pi i/3}, \\ \phi_c(x)\,\phi_c(y) = \phi_c(x + y) \end{gathered}`}
		/>
		<p>
			<MathTex tex="\omega" /> is a third of a turn, <MathTex
				tex={String.raw`\langle c, x\rangle`}
			/> is the dot product counted modulo 3, and the phase of a card is that many thirds of a turn. The
			last identity is the whole point: multiplying phases is the same as adding cards.
		</p>
		<p>
			<strong>An example.</strong> Take <MathTex tex="c = (1, 0, 0, 0)" />. The phase then reads
			only the number of symbols, so the SET of section {number('puzzles')}, with numbers 0, 1 and
			2, gets phases
			<MathTex tex={String.raw`1, \omega, \omega^2`} />, whose product is <MathTex
				tex={String.raw`\omega^3 = 1`}
			/>. The near miss differs only in colour, so this phase is fooled too. Under <MathTex
				tex="c = (0, 0, 0, 1)"
			/>, which reads colour, the near miss's product is <MathTex tex={String.raw`\omega^2`} /> instead.
		</p>
		<p>
			A SET's phases multiply to 1 under all 81 choices of <MathTex tex="c" />, because its cards
			add up to zero. Any other triple adds up to some nonzero vector, and then the 81 choices split
			evenly into three groups whose products are <MathTex tex={String.raw`1, \omega, \omega^2`} />,
			which cancel. So averaging over every choice detects SETs exactly:
		</p>
		<MathTex
			display
			tex={String.raw`\frac{1}{81}\sum_{c} \phi_c(x)\,\phi_c(y)\,\phi_c(z) \;=\; \mathbf 1\big[x + y + z = 0\big]`}
		/>
		<p>
			These <MathTex tex={String.raw`\phi_c`} /> are the <em>characters</em> of the group: maps that
			turn sums into products of phases. Together they form a <em>Fourier basis</em>, a complete set
			of wave-like coordinates for functions on the cards. One of them, <MathTex tex="c = 0" />,
			sends every card to 1 and carries no information. The other 80 come in mirror-image pairs, so
			40 distinct ones are worth learning, a number that comes back below. In this basis, a <MathTex
				tex="k"
			/>-way relation is a product of <MathTex tex="k" /> phases, averaged over characters. Networks are
			known to find Fourier features for arithmetic <Cite id="nanda" />; we will see an attention
			layer find these.
		</p>
		<div class="figure wide"><LearnFigure section="characters" /></div>
	</section>

	<section class="chapter" id="newton">
		<h3><span class="n">{number('newton')}</span>Newton's shortcut</h3>
		<p class="src">
			<span class="mark prior"></span>Classical Newton identities;
			<span class="mark new inline"></span>their use in this relational layer
		</p>
		<p>
			Counting relations directly means listing groups of cards, and the number of groups of size
			<MathTex tex="k" /> grows like <MathTex tex="n^k" />. There is a shortcut. Take three tokens
			with phases <MathTex tex="a, b, c" /> on one channel. Their sum over pairs is
		</p>
		<MathTex
			display
			tex={String.raw`ab + bc + ac \;=\; \tfrac12\Big((a + b + c)^2 - (a^2 + b^2 + c^2)\Big)`}
		/>
		<p>
			Square the sum, take away the squares, halve. The right side needs only two numbers, the sum
			of the phases and the sum of their squares, each one pass over the tokens however many there
			are. These are <em>power sums</em>, <MathTex tex={String.raw`P_j = \sum_t \phi(x_t)^{j}`} />.
			Newton's identities do the same for groups of every size: the sum over every group of <MathTex
				tex="m"
			/>
			distinct tokens of the product of their phases, written <MathTex tex="e_m" />, follows from
			the power sums by a short recursion:
		</p>
		<MathTex
			display
			tex={String.raw`m\, e_m \;=\; \sum_{j=1}^{m} (-1)^{j-1}\, e_{m-j}\, P_j, \qquad e_m = \sum_{|S| = m}\; \prod_{t \in S} \phi(x_t)`}
		/>
		<p>
			With <MathTex tex="m = 2" /> it is the example above. Now combine it with characters: give every
			character its own channel. For a card <MathTex tex="x" />, take <MathTex
				tex={String.raw`e_{k-1}`}
			/> of the other cards in every channel, multiply by <MathTex tex="x" />'s own phase and
			average over channels. A group that adds up to zero with <MathTex tex="x" /> contributes 1 and every
			other group contributes 0, so the result counts the size-<MathTex tex="k" /> relations <MathTex
				tex="x"
			/> is in, without listing a single group. Try it in the figure: it deals nine cards, counts every
			card's relations of size 3, 4 and 5 this way, and checks each count against listing the groups one
			by one.
		</p>
		<div class="figure wide"><LearnFigure section="newton" /></div>
	</section>

	<section class="chapter" id="newtonattn">
		<h3><span class="n">{number('newtonattn')}</span>Newton attention</h3>
		<p class="src">
			<span class="mark new"></span>New in this project;
			<span class="mark measured inline"></span>measured on cloud GPUs, three seeds per model
		</p>
		<p>
			Newton attention makes that construction learnable. It is a different kind of layer from the
			ones before: it has no softmax, no keys and no values. Each token gets <MathTex tex="r" /> complex
			channels. A channel is a point in the plane: its angle is a learned linear function of the token's
			vector, and its length is a learned gate between 0 and 1. A character's angle is itself a linear
			function of a card's attributes, so a channel can become exactly a character, if training finds
			it.
		</p>
		<p>
			The rest is fixed algebra. For each token: power sums over the other tokens, Newton's
			identities to get <MathTex tex="e_m" /> for every group size, and the token's own phases times
			<MathTex tex="e_m" />. A learned read-out then plays the role of the average over characters.
			Every arity up to a cap <MathTex tex="K" /> costs <MathTex tex="O(nKr)" />, linear in the
			number of tokens.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={NEWTON} label="Computation graph of Newton attention" />
		</div>
		<p>
			With every arity up to six on offer, it solves SET, Match-4 and the smallest-arity task on
			every seed; on smallest arity, where chance is 25%, the best fixed-order layer reaches 54%. On
			Match-5 it reaches 85% at the standard size and 97.5% with twice the channels. Cap the arities
			below the task's, offering at most three on Match-4, and it falls to exactly chance. Two
			details made it exact: each arity's features are rescaled to the same size before the
			read-out, because high arities are products of many small numbers; and one read-out is shared
			by all arities, because the same characters count relations of every size.
		</p>
		<p>
			Two probes show what it learned. Switch off one arity at a time: on Match-3 only arity 3
			matters, on Match-4 only arity 4, and on the smallest-arity task exactly arities 3, 4 and 5.
			Nothing told it which arities the task has. And its channels become characters. Every run that
			solves its task has found all 40, and a run that falls short has accuracy close to linear in
			how many it found: within 5 points of <MathTex tex="1/2 + F/80" /> across 74 runs, where <MathTex
				tex="F"
			/> counts the characters found. We call this the <em>characters law</em>. You can watch the
			phases form in
			<a href={resolve('/explore/newton')}>Explore, Newton</a>.
		</p>
		<div class="figure wide"><LearnFigure section="newtonattn" /></div>
	</section>

	<section class="chapter" id="transfer">
		<h3><span class="n">{number('transfer')}</span>Small relations teach large ones</h3>
		<p class="src">
			<span class="mark measured"></span>Cloud GPUs, three seeds per model
		</p>
		<p>
			A character that counts triples also counts groups of four and five. So train one layer on
			Match-3, 4 and 5 at once, with the first token of each table saying which <MathTex tex="k" /> it
			asks about. Each arity sees only a third of the data, yet the mixed layer is exact on all three
			on every seed, where the same layer trained on Match-5 alone reaches 85%. The easy relations find
			the characters and the hard ones reuse them, as if climbing steps toward a large leap <Cite
				id="abbe"
			/>.
		</p>
		<div class="figure wide"><LearnFigure section="transfer" /></div>
		<p>
			At this point the puzzles were solved. A layer that multiplies the right features, summed over
			groups of every size, learns relations that pairwise attention cannot touch. The obvious next
			question was whether any of this helps a language model.
		</p>
	</section>
</section>
