<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import MarginalDemo from '#lib/report/MarginalDemo.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import type { Card } from '#lib/set/cards.ts';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { CUBIC, GENERAL, PAIRWISE } from '#lib/viz/computeGraphs.ts';
	import { number } from '../toc.ts';

	// one attribute, the three cases
	const cases: { name: string; cards: Card[]; e: number; all: number }[] = [
		{
			name: 'All equal',
			cards: [
				[1, 0, 0, 0],
				[1, 1, 1, 1],
				[1, 2, 2, 2]
			],
			e: 3,
			all: 1
		},
		{
			name: 'Two equal',
			cards: [
				[1, 0, 0, 0],
				[1, 1, 1, 1],
				[2, 2, 2, 2]
			],
			e: 1,
			all: 0
		},
		{
			name: 'All different',
			cards: [
				[0, 0, 0, 0],
				[1, 1, 1, 1],
				[2, 2, 2, 2]
			],
			e: 0,
			all: 0
		}
	];
</script>

<section class="part" id="part-pairs">
	<header class="part-head">
		<span class="roman">Part II</span>
		<h2>Attention beyond pairs</h2>
		<p class="part-lede">
			How ordinary attention works, why it cannot see a SET in one step, and what happens when a
			layer is allowed to score three tokens at once.
		</p>
	</header>

	<section class="chapter" id="pairwise">
		<h3><span class="n">{number('pairwise')}</span>Attention compares pairs</h3>
		<p class="src"><span class="mark prior"></span>Prior work <Cite id="vaswani" /></p>
		<p>
			A transformer keeps one vector of width <MathTex tex="d" /> per token and refines those vectors
			layer by layer. The step that lets tokens exchange information is attention. Each token
			<MathTex tex="i" /> makes three vectors from its own, each with a learned linear map: a
			<em>query</em>
			<MathTex tex="Q_i" />, what it is looking for; a <em>key</em>
			<MathTex tex="K_i" />, what it offers; and a <em>value</em>
			<MathTex tex="V_i" />, what it passes on when chosen. Token
			<MathTex tex="i" /> scores every token <MathTex tex="j" /> by the dot product of its query with
			<MathTex tex="j" />'s key. A <em>softmax</em> (exponentiate each score, then divide by the total)
			turns the scores into weights that are positive and add up to 1, and the output is the weighted
			average of the values:
		</p>
		<MathTex
			display
			tex={"P_{ij} = \\frac{\\exp\\left(\\langle Q_i, K_j \\rangle/\\sqrt{d}\\right)}{\\sum_{j'} \\exp\\left(\\langle Q_i, K_{j'} \\rangle/\\sqrt{d}\\right)}, \\qquad Y_i = \\sum_j P_{ij}\\, V_j"}
		/>
		<p>
			In words: <MathTex tex={String.raw`P_{ij}`} /> is how much token <MathTex tex="i" /> listens to
			token
			<MathTex tex="j" />, and <MathTex tex="Y_i" /> is what it hears. Dividing by
			<MathTex tex={String.raw`\sqrt{d}`} /> keeps the scores in a sensible range as the width grows.
			A layer runs several of these computations side by side, called <em>heads</em>, and then
			passes every token through a small two-layer network of its own, the MLP. Stacking layers lets
			later ones combine what earlier ones gathered.
		</p>
		<div class="figure wide"><LearnFigure section="pairwise" /></div>
		<p>
			We will draw every layer in this article as a computation graph like the one below. Circles
			are tensors, with the input <MathTex tex="X" /> on the left and the output <MathTex tex="Y" />
			on the right; a labelled arrow is a learned linear map; a small dot is where two streams meet, here
			a dot product followed by the softmax.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={PAIRWISE} label="Computation graph of pairwise attention" />
		</div>
		<p>
			Every score involves exactly two tokens, the query and one key, so the arity of ordinary
			attention is 2. A fact about three tokens at once has to be assembled in steps: one layer
			gathers pairs, a later layer combines them. For some simple three-token tasks, Match3 among
			them, a one-layer transformer with limited width and precision provably cannot do this <Cite
				id={['hahn', 'sanford']}
			/>. Attention costs <MathTex tex="O(n^2 d)" /> per head for <MathTex tex="n" /> tokens, since every
			pair gets a score.
		</p>
	</section>

	<section class="chapter" id="blind">
		<h3><span class="n">{number('blind')}</span>Why pairs are blind to SET</h3>
		<p class="src">
			<span class="mark prior"></span>Match3 <Cite id="sanford" />, SET geometry <Cite
				id="davis"
			/>, leaps <Cite id="abbe" />; <span class="mark new inline"></span>the reduction and the
			averaging argument are new here
		</p>
		<p>
			Section {number('puzzles')} claimed that "all the same or all different" means "adds up to a multiple
			of 3". Here is why. If the three values are equal, the sum is <MathTex tex="3v" />. If they
			are all different, it is <MathTex tex="0 + 1 + 2 = 3" />. If exactly two are equal, it is
			<MathTex tex="2u + v" /> with <MathTex tex="v \ne u" />, which is never a multiple of 3. So a
			card is a vector of four numbers counted modulo 3, written <MathTex
				tex={'\\mathbb{Z}_3^4'}
			/>, and three cards form a SET exactly when <MathTex tex="a + b + c \equiv 0 \pmod 3" /> in every
			coordinate. SET is Match3 with vectors in place of numbers.
		</p>
		<p>
			Two consequences. Any two cards determine the third: <MathTex tex="c = -(a + b)" />,
			coordinate by coordinate. And every pair of cards lies in exactly one SET, so the deck holds
			<MathTex tex={String.raw`81 \cdot 80 / 6 = 1{,}080`} /> SETs among its 85,320 triples. (Geometrically,
			SETs are the lines of a four-dimensional space over three elements, and two points lie on exactly
			one line.)
		</p>
		<p>
			For one attribute, the rule splits into pairwise agreement plus one genuinely three-way term.
			Write <MathTex tex={'\\delta_{ab}'} /> for 1 if cards <MathTex tex="a" /> and <MathTex
				tex="b"
			/> agree on the attribute and 0 if not:
		</p>
		<MathTex
			display
			tex={'\\mathbb{1}[\\text{rule holds}] = 1 - (\\delta_{ab} + \\delta_{bc} + \\delta_{ac}) + 3\\,\\mathbb{1}[a = b = c]'}
		/>
		<p>Here are the three cases for the number of symbols, ignoring the other attributes:</p>
		<div class="cases">
			{#each cases as c (c.name)}
				<div class="case">
					<div class="trio">
						{#each c.cards as card, i (i)}<SetCard {card} width={30} />{/each}
					</div>
					<div class="case-name">{c.name}</div>
					<div class="hint num">1 − {c.e} + 3·{c.all} = {1 - c.e + 3 * c.all}</div>
				</div>
			{/each}
		</div>
		<p>
			<strong>Pairwise scores are blind on average.</strong> Suppose a model scores a triple by adding
			up a score for each of its three pairs. Every pair of cards lies in exactly one SET and in 79 triples,
			so each pair is represented in the same proportion among SETs as among all triples. The average
			pairwise score over SETs therefore equals its average over all triples, whatever the pairwise scores
			are. On average, a score built from pairs cannot tell SETs from other triples; only the three-way
			term separates them. Try it below: draw random scores built from single cards and pairs, and the
			two averages always coincide.
		</p>
		<div class="figure wide"><MarginalDemo /></div>
		<p>
			<strong>Why that makes training hard.</strong> Pick a SET at random. Any one of its cards is a
			uniformly random card, and any two of them are a uniformly random pair; only all three
			together are special. Early in training, gradient descent moves the weights toward whatever
			correlates with the label, and here nothing built from fewer than three cards does. The model
			has to compute a three-way product before training has anything to improve. Abbe et al. call
			the number of inputs that must be learned together the <em>leap</em> of a task <Cite
				id="abbe"
			/>; for SET it is 3, and for Match-<MathTex tex="k" /> it is <MathTex tex="k" />. Pairwise
			models still beat chance a little, because the argument is about averages and weaker cues
			remain.
		</p>
		<div class="figure wide"><LearnFigure section="set" /></div>
	</section>

	<section class="chapter" id="cubic">
		<h3><span class="n">{number('cubic')}</span>Scoring whole triples</h3>
		<p class="src">
			<span class="mark prior"></span>Prior work <Cite id={['clift', 'sanford', 'roy']} />, derived
			independently in this project's notebook <Cite id="neo" />
		</p>
		<p>
			The dot product multiplies two vectors coordinate by coordinate and adds up the results.
			Nothing forces it to stop at two. The <em>trilinear form</em> multiplies three vectors
			coordinate by coordinate and adds. It is an ordinary dot product of one vector with the
			coordinate-wise product of the other two, the <em>Hadamard product</em>, written <MathTex
				tex={String.raw`\odot`}
			/>:
		</p>
		<MathTex
			display
			tex="\langle a, b \rangle = \sum_c a_c b_c \qquad\longrightarrow\qquad \langle a, b, e \rangle = \sum_c a_c\, b_c\, e_c = \langle a,\, b \odot e \rangle"
		/>
		<p>
			The sum is large only where all three vectors are large on the same coordinates, which makes
			it a test of three things at once. Each coordinate contributes its own three-way pattern, so a
			form of width <MathTex tex="d" /> can mix up to <MathTex tex="d" /> different patterns.
		</p>
		<div class="figure wide"><LearnFigure section="product" /></div>
		<p>
			<em>Cubic attention</em> lets a query score pairs of tokens instead of single tokens. Each
			token makes one query and, for each of two roles, its own key and value. Query <MathTex
				tex="i"
			/> scores the pair <MathTex tex="(j, k)" /> with the trilinear form, and one softmax runs over all
			pairs together:
		</p>
		<MathTex
			display
			tex={"\\begin{gathered} A_{ijk} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\rangle, \\qquad P_{ijk} = \\frac{\\exp(A_{ijk}/\\sqrt{d})}{\\sum_{j'k'} \\exp(A_{ij'k'}/\\sqrt{d})}, \\\\[4pt] Y_i = \\sum_{j,k} P_{ijk}\\,\\bigl(V^1_j \\odot V^2_k\\bigr) \\end{gathered}"}
		/>
		<p>
			What a chosen pair passes back is the Hadamard product of its two values, so the pair itself,
			not either token alone, decides the output. On SET, a query card wants the pair that completes
			a SET with it, and one head of this kind can find it exactly (section {number('head')}). The
			scores fill an <MathTex tex="n \times n \times n" /> tensor, one entry per query and pair. Pairs
			that repeat a token or reuse the query are <em>masked</em> (given no weight); a card with no SET
			to find puts its weight on the sink, and that is how the head says no.
		</p>
		<div class="figure wide"><LearnFigure section="cubic" /></div>
		<div class="figure wide graph">
			<ComputeGraph graph={CUBIC} label="Computation graph of cubic attention" />
		</div>
		<p>
			Clift et al. introduced this operator as 2-simplicial attention. Sanford et al. studied it as
			tensor attention and proved that one head solves Match3, where a one-layer pairwise model has
			to grow in width or precision as the problem grows. Roy et al. made it fast enough to train at
			scale. The Polyformer notebook arrived at the same operator independently in April 2023, under
			the name cubic polyattention.
		</p>
		<details class="more">
			<summary>What it costs</summary>
			<p>
				A cubic head computes <MathTex tex="n^2" /> scores for each of <MathTex tex="n" /> queries,
				<MathTex tex="n^3" /> in all, a factor of <MathTex tex="n" /> more than ordinary attention. It
				never needs an <MathTex tex="n \times n \times d" /> array in memory, because one query's table
				of pair scores is a single matrix product:
			</p>
			<MathTex
				display
				tex={'S_i = \\bigl(Q_i \\odot K^1\\bigr)\\,K^{2\\top}, \\qquad Y_i = \\sum_j V^1_j \\odot \\bigl(P_i V^2\\bigr)_j'}
			/>
			<p>
				Roy et al. let each role look only at a window of <MathTex tex="w" /> nearby keys, which costs
				<MathTex tex="O(n\,w^2 d)" /> and makes long sequences practical <Cite id="roy" />; Alman
				and Song ask whether exact higher-order attention can ever be much cheaper <Cite
					id="alman"
				/>. The puzzles here have 13 or 14 tokens, so cost does not matter for them; it matters for
				long text.
			</p>
			<div class="figure"><LearnFigure section="cost" /></div>
		</details>
	</section>

	<section class="chapter" id="barrier">
		<h3><span class="n">{number('barrier')}</span>Cheaper relatives, and what they miss</h3>
		<p class="src">
			<span class="mark prior"></span>Degree-2 designs <Cite
				id={['kozachinskiy', 'chakrabarti']}
			/>;
			<span class="mark new inline"></span>the coupling barrier is new here
		</p>
		<p>
			A cheaper way to involve three tokens is to add up ordinary pairwise scores along the edges of
			the triangle <MathTex tex="(i, j, k)" />. The score still involves three tokens, but each term
			multiplies only two token vectors. We say its <em>degree</em> is 2, while a trilinear form has degree
			3:
		</p>
		<MathTex
			display
			tex={'\\begin{aligned}A^{\\text{tree}}_{ijk} &= \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle \\\\ A^{\\text{Strassen}}_{ijk} &= \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle + \\langle Q_i, K^2_k \\rangle\\end{aligned}'}
		/>
		<p>
			Tree attention scores the path <MathTex tex="i - j - k" />; Strassen attention scores all
			three edges and, because no term mentions all three tokens, runs in less than <MathTex
				tex="n^3"
			/> time. Chakrabarti, Pitassi and Alman fold these into one scheme, poly-attention, where the shape
			of a small graph of token roles decides both the cost and what the score can compute.
		</p>
		<div class="figure wide"><LearnFigure section="degree2" /></div>
		<p>
			<strong>The coupling barrier.</strong> Fix a query <MathTex tex="i" /> and look at all its pair
			scores at once, an <MathTex tex="n \times n" /> table over <MathTex tex="(j, k)" />. A
			degree-2 score has the form <MathTex tex={'A_{ijk} = f(i,j) + g(j,k) + h(i,k)'} />, and
			exponentiating turns the sum into a product:
		</p>
		<MathTex
			display
			tex={'P_{ijk} = \\frac{1}{Z_i}\\; \\underbrace{e^{f(i,j)}}_{\\text{row weight}}\\; \\underbrace{e^{g(j,k)}}_{\\text{shared table}}\\; \\underbrace{e^{h(i,k)}}_{\\text{column weight}}'}
		/>
		<p>
			The middle factor does not mention the query at all. So every query sees the same table of
			which pairs go together; it can make whole rows and columns heavier or lighter, but it cannot
			change which <MathTex tex="j" /> goes with which <MathTex tex="k" />. On SET that is exactly
			what is needed: the right partners for card <MathTex tex="x" /> are the pairs with
			<MathTex tex="y + z = -x" />, which depend on the query. A cubic head can do it, because its
			pairing table is a mix of up to <MathTex tex="d" /> patterns weighted by the query. The figure removes
			each query's row and column averages (that is the precise version of the argument) and shows three
			queries side by side: the degree-2 head gives the same table three times, the cubic head three different
			ones.
		</p>
		<div class="figure wide"><LearnFigure section="barrier" /></div>
		<p>
			The barrier limits which pair a head can select, not what the whole layer can compute. A
			degree-2 head still multiplies the values of every pair it weighs, and the network after it
			can search that average for the signature of a SET. That is the likely route by which Strassen
			attention reaches 96% on SET in section {number('training')}: slowly, and not exactly.
		</p>
	</section>

	<section class="chapter" id="head">
		<h3><span class="n">{number('head')}</span>A head built by hand</h3>
		<p class="src"><span class="mark new"></span>New in this project</p>
		<p>
			One cubic head can compute the SET rule exactly, with weights written down instead of trained.
			Put each attribute value <MathTex tex="v" /> on a circle at the angle <MathTex
				tex="2\pi v/3"
			/>, a third of a turn per step. Adding values then adds angles, and a multiple of 3 is a whole
			number of turns, so for three cards with values <MathTex tex="a, b, c" /> on one attribute
		</p>
		<MathTex
			display
			tex={'\\cos\\tfrac{2\\pi}{3}(a + b + c) = \\begin{cases} 1 & \\text{if } a + b + c \\equiv 0 \\pmod 3 \\\\ -\\tfrac12 & \\text{otherwise} \\end{cases}'}
		/>
		<p>
			The cosine of a sum of three angles expands into four terms, each a product of one function of
			each angle, so it is a trilinear form with four channels:
		</p>
		<MathTex
			display
			tex="\cos(\alpha + \beta + \gamma) = c_\alpha c_\beta c_\gamma - c_\alpha s_\beta s_\gamma - s_\alpha c_\beta s_\gamma - s_\alpha s_\beta c_\gamma"
		/>
		<p>
			(<MathTex tex="c" /> for cosine, <MathTex tex="s" /> for sine.) Give the query, the first key and
			the second key the matching cosines and sines, do this for each of the four attributes, sixteen
			channels in all, and the score of a triple is
		</p>
		<MathTex
			display
			tex={'A_{ijk} = \\sum_{t=1}^{4} \\cos\\tfrac{2\\pi}{3}\\bigl(a_t + b_t + c_t\\bigr) = 4 - \\tfrac{3}{2}\\,m'}
		/>
		<p>
			where <MathTex tex="m" /> is the number of attributes that break the rule. Every SET scores 4 and
			every other triple at most 2.5. The sink gets a fixed score of 3.25, in between. With a small softmax
			temperature, a card in some SET puts nearly all its weight on its SET pairs, and a card in none
			puts it on the sink. This head is the default in
			<a href={resolve('/explore')}>Explore, Cubic</a>, so its pictures there are exact before
			anything has been trained.
		</p>
		<div class="figure wide"><LearnFigure section="head" /></div>
		<details class="more">
			<summary>What the chosen pair passes back</summary>
			<p>
				Scores choose pairs; values decide what a chosen pair returns. Clift et al. combine a pair's
				two values with a full bilinear map <Cite id="clift" />; the Hadamard value keeps only
				matching coordinates
				<Cite id="chakrabarti" />. Both read off one object, the <em>pair moment</em>, whose
				diagonal is the Hadamard output:
			</p>
			<MathTex
				display
				tex={'M_i = \\sum_{j,k} P_{ijk}\\, V^1_j V^{2\\top}_k, \\qquad \\operatorname{diag}(M_i) = Y_i'}
			/>
			<p>
				The values must come from the two partner tokens, not from the query. Poly-attention's
				definition does this, but its released code for the tree mechanism reads the second value at
				the query's position. With cubic scores held fixed, that indexing leaves SET at chance
				(54%), while Hadamard and full-moment values reach 100% in about 800 steps.
			</p>
			<div class="figure"><LearnFigure section="binding" /></div>
		</details>
	</section>

	<section class="chapter" id="training">
		<h3><span class="n">{number('training')}</span>What training shows</h3>
		<p class="src">
			<span class="mark measured"></span>Measured with this app's in-browser engine <Cite
				id="jaxjs"
			/>
		</p>
		<p>
			Every model on the <a href={resolve('/compare')}>Compare</a> bench sees the same batches of SET
			tables; only the attention layer differs. Each has one layer of width 64 with four heads, trained
			for 4,000 steps from seed 0, and is scored on 1,024 held-out tables. "Standard" means ordinary attention.
			Feynman attention, the layer of Part III, is listed now so the bench can be compared in one place.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr
						><th>Model</th><th class="num">Held-out accuracy</th><th class="num">Reaches 95%</th><th
							class="num">ms / step</th
						></tr
					></thead
				>
				<tbody>
					<tr class="hi"
						><th>Cubic</th><td class="num">100%</td><td class="num">step 500</td><td class="num"
							>12.2</td
						></tr
					>
					<tr
						><th>Feynman, 2 rounds</th><td class="num">100%</td><td class="num">step 700</td><td
							class="num">35.7</td
						></tr
					>
					<tr
						><th>Strassen</th><td class="num">95.8%</td><td class="num">step 2,350</td><td
							class="num">11.3</td
						></tr
					>
					<tr
						><th>Tree</th><td class="num">76.4%</td><td class="num">never</td><td class="num"
							>11.0</td
						></tr
					>
					<tr
						><th>Standard, 2 layers</th><td class="num">64.4%</td><td class="num">never</td><td
							class="num">15.5</td
						></tr
					>
					<tr
						><th>Standard, 1 layer</th><td class="num">60.5%</td><td class="num">never</td><td
							class="num">8.4</td
						></tr
					>
				</tbody>
			</table>
		</div>
		<p class="caption">
			SET, one layer unless stated, seed 0, WebGPU. Always answering yes scores 53.5%.
		</p>
		<p>
			The cubic head sits at chance until about step 400 and is at 99% by step 500: the three-way
			rule is found all at once, the jump the leap of section {number('blind')} predicts. Strassen attention
			climbs slowly to 95.8% by the route of section {number('barrier')}; tree attention, with one
			edge fewer, stops at 76.4%. At this length the cubic head costs about the same time per step
			as the degree-2 ones. The ordering held on a second seed in offline runs.
		</p>
		<div class="figure wide"><LearnFigure section="training" /></div>
	</section>

	<section class="chapter" id="arity">
		<h3><span class="n">{number('arity')}</span>Four cards need a four-way term</h3>
		<p class="src">
			<span class="mark prior"></span>Higher-order tensor attention <Cite id="sanford" />;
			<span class="mark new inline"></span>the four-card test is new here
		</p>
		<p>
			Now ask whether four cards add up to zero: Match-4. The argument of section {number('blind')}
			moves up one order. Three cards fix the fourth, so in a group of four that sums to zero, any three
			look like a random triple, and only the complete four-card relation carries the signal. In these
			runs cubic attention stalls at chance on Match-4, just as pairwise attention did on SET. A quartic
			head, the same construction one order up, can learn it:
		</p>
		<MathTex display tex={'A_{ijkl} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\odot K^3_l \\rangle'} />
		<div class="figure wide"><LearnFigure section="arity" /></div>
		<p>
			Every order has the same shape, the general polyattention of the original notebook: a query
			against ordered groups of role-specific keys, with values multiplied along the group.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={GENERAL} label="Computation graph of polyattention of order N" />
		</div>
		<p>
			But a head of fixed order is a fixed bet. An order-<MathTex tex="k" /> head pays <MathTex
				tex="n^k"
			/> whether the data needs pairs, triples or more, and the right order can change from one example
			to the next. The next part asks whether one layer can choose for itself.
		</p>
	</section>
</section>

<style>
	.cases {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 12px;
		margin-bottom: 16px;
	}
	.case {
		display: flex;
		flex-direction: column;
		gap: 5px;
	}
	.trio {
		display: flex;
		gap: 6px;
	}
	.case-name {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.hint {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	@media (max-width: 480px) {
		.cases {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
