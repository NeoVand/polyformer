<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import CompositionFigure from '#lib/learn/CompositionFigure.svelte';
	import DiagramSum from '#lib/learn/DiagramSum.svelte';
	import { REFERENCES } from '#lib/learn/references.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import type { Card } from '#lib/set/cards.ts';
	import { Atom, Book, Cards, Cube, Matrix, Note } from '#lib/ui/icons.ts';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { CUBIC, FEYNMAN, GENERAL, NEWTON, PAIRWISE } from '#lib/viz/computeGraphs.ts';

	const PARTS = [
		{ id: 'part-setting', label: 'Setting', icon: Cards, title: 'The setting' },
		{ id: 'part-known', label: 'Known', icon: Book, title: 'What was known' },
		{ id: 'part-new', label: 'New here', icon: Cube, title: 'What this project adds' },
		{ id: 'part-beyond', label: 'Beyond', icon: Atom, title: 'Letting the data choose the arity' },
		{ id: 'part-algebra', label: 'Algebra', icon: Matrix, title: 'Arity is algebra' },
		{ id: 'part-compose', label: 'Compose', icon: Matrix, title: 'Learning to compose' },
		{ id: 'references', label: 'Sources', icon: Note, title: 'References' }
	];
	const CHAPTERS: { id: string; title: string; part: string }[] = [
		{ id: 'puzzles', title: 'The puzzles', part: 'part-setting' },
		{ id: 'encoding', title: 'What a model sees', part: 'part-setting' },
		{ id: 'pairwise', title: 'Pairwise attention', part: 'part-known' },
		{ id: 'product', title: 'A generalized dot product', part: 'part-known' },
		{ id: 'cubic', title: 'Cubic polyattention', part: 'part-known' },
		{ id: 'cost', title: 'What it costs', part: 'part-known' },
		{ id: 'degree2', title: 'Cheaper, degree-2 relatives', part: 'part-known' },
		{ id: 'barrier', title: 'The coupling barrier', part: 'part-new' },
		{ id: 'set', title: 'SET is Match3', part: 'part-new' },
		{ id: 'head', title: 'A head built by hand', part: 'part-new' },
		{ id: 'binding', title: 'Values as binding', part: 'part-new' },
		{ id: 'training', title: 'What training shows', part: 'part-new' },
		{ id: 'arity', title: 'Putting the k-way term in reach', part: 'part-new' },
		{ id: 'feynman', title: 'Where Feynman diagrams come from', part: 'part-beyond' },
		{ id: 'dyson', title: 'Summing them all at once', part: 'part-beyond' },
		{ id: 'diagrams', title: 'Sum over diagrams', part: 'part-beyond' },
		{ id: 'sectors', title: 'Making it train', part: 'part-beyond' },
		{ id: 'chase', title: 'What Feynman attention learns', part: 'part-beyond' },
		{ id: 'composition', title: 'Composing arity does not train', part: 'part-algebra' },
		{ id: 'groups', title: 'A group is a rule for combining', part: 'part-algebra' },
		{ id: 'characters', title: 'A relation is agreement of phases', part: 'part-algebra' },
		{ id: 'newton', title: 'Every arity at once', part: 'part-algebra' },
		{ id: 'newtonattn', title: 'Newton attention', part: 'part-algebra' },
		{ id: 'transfer', title: 'Small relations teach large ones', part: 'part-algebra' },
		{ id: 'language', title: 'The language result is negative', part: 'part-compose' },
		{ id: 'features', title: 'Good coordinates are not enough', part: 'part-compose' },
		{ id: 'order', title: 'When order changes the answer', part: 'part-compose' },
		{ id: 'representations', title: 'Representing operations as rotations', part: 'part-compose' },
		{ id: 'holonomy', title: 'Compose first, then read', part: 'part-compose' },
		{ id: 'group-results', title: 'What the rotation heads learn', part: 'part-compose' },
		{ id: 'limits', title: 'What is proved, and under what rules', part: 'part-compose' },
		{ id: 'programs', title: 'A second test: execute a program', part: 'part-compose' },
		{ id: 'meaning', title: 'What the result means', part: 'part-compose' }
	];
	const COMPOSITION_CHAPTERS = new Set([
		'groups',
		...CHAPTERS.filter((c) => c.part === 'part-compose').map((c) => c.id)
	]);
	const number = (id: string) => CHAPTERS.findIndex((c) => c.id === id) + 1;

	let section = $state('puzzles');
	const part = $derived(CHAPTERS.find((c) => c.id === section)?.part ?? section);

	/** The chapter crossing the middle band of the viewport drives the figure. */
	function watch(el: HTMLElement) {
		const io = new IntersectionObserver(
			(entries) => {
				for (const e of entries) if (e.isIntersecting) section = e.target.id;
			},
			{ rootMargin: window.innerWidth <= 1100 ? '-50% 0px -45% 0px' : '-40% 0px -55% 0px' }
		);
		el.querySelectorAll('section[id]').forEach((s) => io.observe(s));
		return () => io.disconnect();
	}

	// the opening example: a SET (number, shading and colour all differ, shape the same) and a
	// near miss that differs from it only in the third card's colour
	const SET_EXAMPLE: Card[] = [
		[0, 0, 0, 0],
		[1, 0, 1, 1],
		[2, 0, 2, 2]
	];
	const MISS_EXAMPLE: Card[] = [
		[0, 0, 0, 0],
		[1, 0, 1, 1],
		[2, 0, 2, 1]
	];

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

<svelte:head>
	<title>Learn to compose | Polyformer</title>
</svelte:head>

<PageFrame rail={PARTS.map(({ id, label, icon }) => ({ id, label, icon }))} active={part}>
	<div class="learn">
		<article class="text" {@attach watch}>
			<header class="intro">
				<h1>Learning to compose</h1>
				<p class="lede">
					Attention compares tokens in pairs. Some relations only appear when several tokens meet,
					and giving a layer those interactions makes a decisive difference on controlled puzzles.
					On language, that success did not carry over. The useful question became: what should the
					layer do when tokens meet? Follow the path from pairwise scores to adding clock hands,
					then to multiplying rotations that preserve the order of a sequence. You need only a
					working idea of neural networks and training; the mathematics is built here.
				</p>
				<p class="lede">
					The figure beside the text follows the chapter you are reading, and most figures are
					computed live in your browser. Every chapter says where its content comes from:
				</p>
				<ul class="legend">
					<li><span class="mark prior"></span>Prior work, with references</li>
					<li><span class="mark new"></span>New in this project</li>
					<li><span class="mark measured"></span>Measured in the browser or research harness</li>
				</ul>
				<nav class="toc" aria-label="Chapters">
					{#each PARTS.filter((p) => p.id !== 'references') as p (p.id)}
						<div class="toc-part">
							<span class="toc-title">{p.title}</span>
							<ol>
								{#each CHAPTERS.filter((c) => c.part === p.id) as c (c.id)}
									<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- in-page anchor -->
									<li><a href="#{c.id}"><span class="num">{number(c.id)}</span>{c.title}</a></li>
								{/each}
							</ol>
						</div>
					{/each}
				</nav>
			</header>

			<!-- ── Part 0 ─────────────────────────────────────────────────── -->
			<h2 class="part" id="part-setting">The setting</h2>
			<p class="part-lede">
				Before any architecture: the puzzles every experiment uses, and how a puzzle becomes
				something a network can read.
			</p>

			<section id="puzzles">
				<h3><span class="n">{number('puzzles')}</span>The puzzles</h3>
				<p class="src">
					<span class="mark prior"></span>SET is a published card game <Cite id="davis" />, pointer
					chasing and Match3 are standard tests <Cite id={['chakrabarti07', 'sanford']} />;
					<span class="mark new inline"></span>Match-<MathTex tex="k" /> beyond three and the other variants
					are new here
				</p>
				<p>
					Every experiment uses small puzzles whose answers a program can check. They are generated
					fresh as training runs, so there is no fixed dataset: a model rarely sees the same puzzle
					twice, and it is scored on puzzles it has never trained on. Each puzzle is built so that
					its answer depends on several pieces at once, and so that the number of pieces, the
					<em>arity</em> of the relation, is known exactly.
				</p>
				<p>
					<strong>SET.</strong> SET is a card game. Each card has four attributes: how many symbols
					it shows (one, two or three), their shape (here spade, heart or club), their shading
					(solid, striped or open) and their colour (blue, green or purple). Every combination
					appears exactly once, so the deck has <MathTex tex="3^4 = 81" /> cards. Three cards form a SET
					when, for every attribute separately, the three cards are either all the same or all different.
				</p>
				<div class="examples">
					<div class="example">
						<div class="trio">
							{#each SET_EXAMPLE as card, i (i)}<SetCard {card} width={30} />{/each}
						</div>
						<div class="case-name">A SET</div>
						<div class="hint">number, shading and colour all differ; shape is the same</div>
					</div>
					<div class="example">
						<div class="trio">
							{#each MISS_EXAMPLE as card, i (i)}<SetCard {card} width={30} />{/each}
						</div>
						<div class="case-name">Not a SET</div>
						<div class="hint">colour is blue, green, green: two the same, one different</div>
					</div>
				</div>
				<p>
					The task deals twelve cards and asks, for every card, whether it belongs to at least one
					SET on the table: yes or no per card. On a random table a little over half of the cards,
					about 54%, are in some SET. No single card, and no pair of cards, settles the answer; it
					is a fact about three cards at once, which is what makes SET a useful test.
				</p>
				<p>
					<strong>Match-<MathTex tex="k" />.</strong> Write each attribute value as 0, 1 or 2. Then
					"all the same or all different" is the same as "the three values add up to a multiple of
					3": 0 + 0 + 0, 1 + 1 + 1 and 0 + 1 + 2 do, and 0 + 0 + 1 does not. So a SET is three cards
					whose values add up to a multiple of 3 in every attribute. Match-<MathTex tex="k" /> asks the
					same question about groups of <MathTex tex="k" /> distinct cards: is this card part of some
					group of <MathTex tex="k" /> cards on the table whose values add up to a multiple of 3 in every
					attribute? SET is Match-3. Match-4 and Match-5 deal nine cards, so that again about half the
					cards are positive. A related task, <em>smallest arity</em>, asks for the smallest group
					size, 3, 4 or 5, at which a card completes such a group, or "none": four answers instead
					of two.
				</p>
				<p>
					<strong>Pointer chasing.</strong> Twelve nodes form a few linked lists. Each node has an id,
					a pointer to the next node's id, and a payload, a number from 0 to 7; the last node of each
					list points to itself. A query names a start node, and the answer is the payload at the end
					of that node's list, zero to three hops away. Unlike SET, the answer needs a chain of lookups,
					and its length changes from puzzle to puzzle.
				</p>
				<p>
					<strong>Three-hop composition.</strong> Three lookup tables <MathTex
						tex="f_1, f_2, f_3"
					/>
					each map the numbers 0 to 7 to 0 to 7, written out as 24 tokens of the form (slot, value), followed
					by a starting number <MathTex tex="x" />. The answer is <MathTex
						tex="f_3(f_2(f_1(x)))"
					/>: always three lookups, in a fixed order.
				</p>
				<p>
					<strong>Text.</strong> One experiment uses real text instead: enwik8, the first 100 MB of an
					English Wikipedia dump, read one byte at a time, to check whether any of this helps a language
					model.
				</p>
			</section>

			<section id="encoding">
				<h3><span class="n">{number('encoding')}</span>What a model sees</h3>
				<p class="src">
					<span class="mark new"></span>This project's setup, the same in the browser and in the
					research harness
				</p>
				<p>
					A network does not see cards. It sees a sequence of <em>tokens</em>, each a list of
					numbers, and here every card is one token. A card's four attribute values are each written
					as a <em>one-hot</em> vector of length 4: a 1 in the slot for its value and 0 elsewhere,
					with a fourth slot no card uses. The four vectors side by side give 16 numbers per card. A
					learned linear map turns them into a vector of width <MathTex tex="d" /> (64 in the browser),
					and a learned vector for the token's position is added. The order of the cards carries no meaning;
					the network has to learn to ignore it.
				</p>
				<p>
					Position 0 holds one extra token that is not a card, the <em>sink</em>. It uses the fourth
					slot of every attribute, so it looks like no card. Attention, as chapter {number(
						'pairwise'
					)}
					explains, must spend all of its weight somewhere; the sink gives it a harmless place to put
					weight when nothing on the table fits.
				</p>
				<p>
					<strong>Outputs and training.</strong> On SET the network outputs, for every card, a probability
					that the card is in some SET. Training lowers the cross-entropy between those probabilities
					and the true labels, summed over the cards (the sink has no label). Every training step draws
					a fresh batch of 128 random tables from a seeded generator, so every model on the bench sees
					the same tables in the same order, and the optimiser is AdamW. A browser run takes 4,000 steps;
					the cloud runs take 4,000 to 20,000.
				</p>
				<p>
					<strong>Scoring.</strong> After training, a model labels 1,024 tables that were drawn
					once, with a different seed, and never trained on. Its <em>held-out accuracy</em> is the
					share of cards it labels correctly. The bar to beat is <em>chance</em>, the score of a
					model that ignores the table and always gives the more common answer: about 54% on SET.
					When the two answers are unevenly common, the research tables report
					<em>balanced accuracy</em>, the average of the accuracy on positive cards and on negative
					cards, so that chance is exactly 50% and a model cannot look good by favouring one answer.
					Cloud results use three
					<em>seeds</em>, three independent runs with different initial weights and data, to show
					how much a result depends on luck.
				</p>
				<p>
					The other puzzles follow the same pattern. A pointer-chasing node is one token holding its
					id, pointer and payload, and the query is a last token that holds only a pointer; the
					network answers at the query, choosing one of eight payloads, so chance is 12.5%.
				</p>
			</section>

			<!-- ── Part I ─────────────────────────────────────────────────── -->
			<h2 class="part" id="part-known">What was known</h2>

			<section id="pairwise">
				<h3><span class="n">{number('pairwise')}</span>Pairwise attention</h3>
				<p class="src"><span class="mark prior"></span>Prior work <Cite id="vaswani" /></p>
				<p>
					A transformer holds one vector of width <MathTex tex="d" /> per token (chapter {number(
						'encoding'
					)} showed how a card becomes one) and refines those vectors layer by layer. The step that lets
					tokens exchange information is <em>attention</em>. Each token <MathTex tex="i" /> makes three
					vectors from its own, each by a learned linear map: a <em>query</em>
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
					Dividing by <MathTex tex={String.raw`\sqrt{d}`} /> keeps the scores in a sensible range as the
					width grows. A layer runs several of these computations side by side, called
					<em>heads</em>, each with its own maps, and then passes every token through a small
					two-layer network of its own (the MLP). Stacking layers lets later ones combine what
					earlier ones gathered.
				</p>
				<ComputeGraph graph={PAIRWISE} label="Computation graph of pairwise attention" />
				<p>
					How to read these graphs, here and below: circles are tensors, with the input
					<MathTex tex="X" /> on the left and the output <MathTex tex="Y" /> on the right; a labelled
					arrow is a learned linear map; a small dot is where two streams meet, here a dot product followed
					by the softmax; and each formula sits beside the tensor it defines.
				</p>
				<p>
					Every score involves exactly two tokens, the query and one key. This page calls the number
					of tokens a single score joins its <em>arity</em>, so ordinary attention has arity 2. A
					fact about three tokens at once has to be assembled in steps: one layer gathers pairs, a
					later layer combines them. For some simple three-token tasks, Match3 among them (chapter {number(
						'cubic'
					)}), a one-layer transformer with sufficiently restricted width and precision cannot do
					this <Cite id={['hahn', 'sanford']} />. The cost is
					<MathTex tex="O(n^2 d)" /> per head for <MathTex tex="n" /> tokens, since every pair of tokens
					gets a score.
				</p>
			</section>

			<section id="product">
				<h3><span class="n">{number('product')}</span>A generalized dot product</h3>
				<p class="src"><span class="mark prior"></span>Standard multilinear algebra</p>
				<p>
					The dot product multiplies two vectors coordinate by coordinate and adds the results.
					Nothing stops at two factors. The <em>trilinear form</em> multiplies three vectors
					coordinate by coordinate and adds. It can be written as an ordinary dot product of one
					vector with the coordinate-wise product of the other two, called the
					<em>Hadamard product</em>
					and written
					<MathTex tex={String.raw`\odot`} />:
				</p>
				<MathTex
					display
					tex="\langle a, b \rangle = \sum_c a_c b_c \qquad\longrightarrow\qquad \langle a, b, e \rangle = \sum_c a_c\, b_c\, e_c = \langle a,\, b \odot e \rangle"
				/>
				<p>
					The sum is large only when all three vectors are large on the same coordinates, which
					makes it a test of three things at once. Each coordinate <MathTex tex="c" /> contributes its
					own three-way pattern, so a form of width <MathTex tex="d" /> can mix up to <MathTex
						tex="d"
					/> different patterns. Chapter {number('barrier')} uses that count: one query of a cubic head
					can ask for up to <MathTex tex="d" /> different pairings of tokens.
				</p>
				<p>
					One more word for later. The <em>degree</em> of a score is how many token vectors are
					multiplied together in each of its terms: a dot product has degree 2, a trilinear form
					degree 3. Arity counts the tokens a score involves; degree counts the vectors multiplied
					at once. Chapter {number('degree2')} shows a score with arity 3 but degree 2.
				</p>
			</section>

			<section id="cubic">
				<h3><span class="n">{number('cubic')}</span>Cubic polyattention</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['clift', 'sanford', 'roy']} />,
					derived independently in this project's notebook <Cite id="neo" />
				</p>
				<p>
					Cubic attention lets a query score pairs of tokens instead of single tokens. Each token
					makes one query and, for each of two <em>roles</em>, its own key and value. Query <MathTex
						tex="i"
					/> scores the ordered pair <MathTex tex="(j, k)" />, with <MathTex tex="j" /> in role 1 and
					<MathTex tex="k" /> in role 2, using the trilinear form of chapter {number('product')},
					and a single softmax runs over all pairs together:
				</p>
				<MathTex
					display
					tex={"\\begin{gathered} A_{ijk} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\rangle, \\qquad P_{ijk} = \\frac{\\exp(A_{ijk}/\\sqrt{d})}{\\sum_{j'k'} \\exp(A_{ij'k'}/\\sqrt{d})}, \\\\[4pt] Y_i = \\sum_{j,k} P_{ijk}\\,\\bigl(V^1_j \\odot V^2_k\\bigr) \\end{gathered}"}
				/>
				<p>
					What a chosen pair passes back is the Hadamard product of <MathTex tex="j" />'s first
					value and <MathTex tex="k" />'s second, so the pair itself, not either token alone,
					decides the output. On SET a query card wants the pair that completes a SET with it, and
					one head of this kind can find it exactly (chapter {number('head')}).
				</p>
				<ComputeGraph graph={CUBIC} label="Computation graph of cubic polyattention" />
				<p>
					Clift et al. introduced this operator as 2-simplicial attention. Sanford et al. studied it
					as tensor attention and proved that one head solves <em>Match3</em>: given numbers
					<MathTex tex="x_1, \dots, x_n" /> modulo some <MathTex tex="M" />, say for each <MathTex
						tex="i"
					/> whether two other entries add up with <MathTex tex="x_i" /> to a multiple of <MathTex
						tex="M"
					/>. Their lower bound requires a one-layer pairwise model to grow in width or precision as
					the problem grows. Roy et al. made the operator fast enough to train at scale. The
					Polyformer notebook arrived at the same operator independently in April 2023 under the
					name cubic polyattention, which this app keeps.
				</p>
				<p>
					The scores fill an <MathTex tex="n \times n \times n" /> tensor, one entry per query and pair.
					A SET needs three different cards, so pairs that repeat a token or reuse the query are
					<em>masked</em>: given no weight at all. A query with no SET to find still has to put its
					weight somewhere; it puts it on the sink token of chapter {number('encoding')}, and that
					is how the head says no.
				</p>
			</section>

			<section id="cost">
				<h3><span class="n">{number('cost')}</span>What it costs</h3>
				<p class="src"><span class="mark prior"></span>Prior work <Cite id={['roy', 'alman']} /></p>
				<p>
					A cubic head computes <MathTex tex="n^2" /> scores for each of <MathTex tex="n" /> queries,
					<MathTex tex="n^3" /> in all. It never has to hold an <MathTex
						tex="n \times n \times d"
					/> array in memory, because one query's whole <MathTex tex="n \times n" /> table of scores is
					a single matrix product. Stack the role-1 keys as the rows of a matrix <MathTex
						tex="K^1"
					/>, multiply every row by the query coordinate by coordinate, and multiply the result by
					the role-2 keys; the values factor the same way, with <MathTex tex="P_i" /> the query's table
					of pair weights:
				</p>
				<MathTex
					display
					tex={'S_i = \\bigl(Q_i \\odot K^1\\bigr)\\,K^{2\\top} \\in \\mathbb{R}^{n \\times n}, \\qquad Y_i = \\sum_j V^1_j \\odot \\bigl(P_i V^2\\bigr)_j'}
				/>
				<p>
					That is <MathTex tex="O(n^2 d)" /> work per query and <MathTex tex="O(n^3 d)" /> per head, a
					factor of <MathTex tex="n" /> more than ordinary attention. Roy et al. let each role look only
					at a window of <MathTex tex="w" /> nearby keys, which costs <MathTex tex="O(n\,w^2 d)" /> and
					makes long sequences practical, at the price of only seeing triples of nearby tokens. Alman
					and Song ask whether exact higher-order attention can ever be much cheaper, and find that the
					answer depends on how large the entries of the score tensor are allowed to be. The puzzles here
					have 13 or 14 tokens, so cost does not matter in this app; it matters for long text.
				</p>
			</section>

			<section id="degree2">
				<h3><span class="n">{number('degree2')}</span>Cheaper, degree-2 relatives</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['kozachinskiy', 'chakrabarti']} />
				</p>
				<p>
					A cheaper way to involve three tokens is to add up ordinary pairwise scores along the
					edges of the triangle <MathTex tex="(i, j, k)" />. The score still involves three tokens,
					so its arity is 3, but each term multiplies only two token vectors, so its degree is 2:
				</p>
				<MathTex
					display
					tex={'\\begin{aligned}A^{\\text{tree}}_{ijk} &= \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle \\\\ A^{\\text{Strassen}}_{ijk} &= \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle + \\langle Q_i, K^2_k \\rangle\\end{aligned}'}
				/>
				<p>
					Tree attention scores the path <MathTex tex="i - j - k" />; Strassen attention scores all
					three edges. Because no term mentions all three indices, the work can be reorganised into
					ordinary matrix products, and Strassen attention, named after Strassen's fast
					matrix-multiplication algorithm, runs in less than <MathTex tex="n^3" /> time. Chakrabarti,
					Pitassi and Alman fold all of these into one scheme, poly-attention: a score is a polynomial
					over a small graph whose nodes are token roles, and the shape of the graph decides both the
					cost and what the score can compute. The next chapter shows what degree 2 gives up.
				</p>
			</section>

			<!-- ── Part II ────────────────────────────────────────────────── -->
			<h2 class="part" id="part-new">What this project adds</h2>

			<section id="barrier">
				<h3><span class="n">{number('barrier')}</span>The coupling barrier</h3>
				<p class="src"><span class="mark new"></span>New in this project</p>
				<p>
					Fix a query <MathTex tex="i" /> and look at all of its scores at once: an <MathTex
						tex="n \times n"
					/> table over pairs <MathTex tex="(j, k)" />. In a degree-2 score every term involves at
					most two of the three tokens, so it has the form
				</p>
				<MathTex display tex={'A_{ijk} = f(i,j) + g(j,k) + h(i,k)'} />
				<p>
					Exponentiating turns the sum into a product, so the softmax weight splits into three
					factors:
				</p>
				<MathTex
					display
					tex={'P_{ijk} = \\frac{1}{Z_i}\\; \\underbrace{e^{f(i,j)}}_{\\text{row weight}}\\; \\underbrace{e^{g(j,k)}}_{\\text{shared kernel}}\\; \\underbrace{e^{h(i,k)}}_{\\text{column weight}}'}
				/>
				<p>
					The middle factor, <MathTex tex={'G_{jk} = e^{g(j,k)}'} />, does not mention the query at
					all. The first depends only on the query and <MathTex tex="j" />, the last only on the
					query and
					<MathTex tex="k" />. So every query sees the same table <MathTex tex="G" /> of which pairs go
					together. A query can make whole rows and columns of it heavier or lighter, that is, make individual
					keys more or less likely, but it cannot change which <MathTex tex="j" /> goes with which <MathTex
						tex="k"
					/>.
				</p>
				<p>
					<strong>Why, precisely.</strong> <em>Double centring</em> a table subtracts each row's
					mean and each column's mean and adds back the overall mean. Anything that depends on the
					row alone, or on the column alone, disappears. Applied to a query's scores, it removes <MathTex
						tex="f(i,j)"
					/> and <MathTex tex="h(i,k)" /> and leaves the centred <MathTex tex="g" />, the same table
					for every query. ∎
				</p>
				<p>
					On SET this is exactly what is needed and missing. For a query card <MathTex tex="x" />,
					the right partners are the pairs <MathTex tex="(y, z)" /> with <MathTex
						tex="y + z = -x"
					/>
					(chapter {number('set')}). Which <MathTex tex="j" /> goes with which <MathTex tex="k" /> depends
					on the query, so a degree-2 head cannot aim its weight at the completing pair. A cubic head
					can: its centred score
				</p>
				<MathTex
					display
					tex={'\\tilde A^{\\text{cubic}}_{i,jk} = \\sum_{c=1}^{d} Q_{ic}\\; \\bigl(K^1_{\\cdot c} \\otimes K^2_{\\cdot c}\\bigr)^{\\sim}_{jk}'}
				/>
				<p>
					is a mix of up to <MathTex tex="d" /> pairing patterns, one per coordinate (<MathTex
						tex={String.raw`\otimes`}
					/> builds a table from two vectors, every entry of one times every entry of the other), with
					weights set by the query.
				</p>
				<p>
					The barrier limits which pair a head can select, not what the layer can compute. A
					degree-2 head still multiplies the values of every pair it weighs, and the network after
					it can search that average for the signature of a SET. This is the likely route by which
					Strassen attention reaches 96% on SET in chapter {number('training')}: slowly, and not
					exactly. The cubic head picks the pair itself and jumps to 100%.
				</p>
			</section>

			<section id="set">
				<h3><span class="n">{number('set')}</span>SET is Match3, and pairs are blind to it</h3>
				<p class="src">
					<span class="mark prior"></span>Match3 <Cite id="sanford" />, SET geometry <Cite
						id="davis"
					/>, leaps <Cite id="abbe" />;
					<span class="mark new inline"></span>the reduction and the averaging argument are new here
				</p>
				<p>
					Chapter {number('puzzles')} claimed that "all the same or all different" means "adds up to a
					multiple of 3". Here is why. If the three values are equal, the sum is <MathTex
						tex="3v"
					/>. If they are all different, it is <MathTex tex="0 + 1 + 2 = 3" />. If exactly two are
					equal, it is <MathTex tex="2u + v" /> with <MathTex tex="v \ne u" />, and that is never a
					multiple of 3. So a card is a vector of four numbers counted modulo 3, an element of <MathTex
						tex={'\\mathbb{Z}_3^4'}
					/>, and three cards form a SET exactly when <MathTex tex="a + b + c \equiv 0 \pmod 3" /> in
					every coordinate. SET is Match3 with vectors in place of numbers.
				</p>
				<p>
					Two consequences. Any two cards determine the third: <MathTex tex="c = -(a + b)" />,
					coordinate by coordinate. And every pair of cards lies in exactly one SET, so the deck
					holds
					<MathTex tex={String.raw`81 \cdot 80 / 6 = 1{,}080`} /> SETs among its 85,320 triples. (Geometrically,
					SETs are the lines of the four-dimensional space over three elements, and two points lie on
					exactly one line.)
				</p>
				<p>
					For one attribute, the rule splits into pairwise agreement and one genuinely three-way
					term. Write <MathTex tex={'\\delta_{ab}'} /> for 1 if cards <MathTex tex="a" /> and <MathTex
						tex="b"
					/> agree on the attribute and 0 if not:
				</p>
				<MathTex
					display
					tex={'\\mathbb{1}[\\text{rule holds}] = 1 - (\\delta_{ab} + \\delta_{bc} + \\delta_{ac}) + 3\\,\\mathbb{1}[a = b = c]'}
				/>
				<p>
					Below, the three cases for the first attribute, the number of symbols (ignore the others):
					one minus the number of agreeing pairs, plus 3 if all three agree.
				</p>
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
					<strong>Pairwise scores are blind on average.</strong> Suppose a model scores a triple of
					cards by adding up a score for each of its three pairs, <MathTex
						tex={'S(T) = \\sum_{\\{a,b\\} \\subset T} \\varphi(a,b)'}
					/>. Every pair of cards lies in exactly one SET and in 79 triples, so pairs are
					represented in the same proportions among SETs as among all triples. The average of <MathTex
						tex="S"
					/> over SETs therefore equals its average over all triples: on average, a score built from pairs
					cannot tell SETs from other triples. Only the three-way term separates them. ∎
				</p>
				<p>
					<strong>Why that makes training hard.</strong> Pick a SET at random. Any one of its cards
					is a uniformly random card, and any two of them are a uniformly random pair; only all
					three together are special. At the start of training a gradient step moves the weights
					toward whatever correlates with the label, and here nothing built from fewer than three
					cards does. The model has to compute a three-way product before training has anything to
					improve. Abbe et al. call the number of inputs that must be learned together the
					<em>leap</em>
					of a task; for SET it is 3, and for Match-<MathTex tex="k" /> it is <MathTex tex="k" />.
					Pairwise models still beat chance a little (60 to 64% in chapter {number('training')}):
					the argument is about averages, and weaker cues remain.
				</p>
			</section>

			<section id="head">
				<h3><span class="n">{number('head')}</span>A head built by hand</h3>
				<p class="src"><span class="mark new"></span>New in this project</p>
				<p>
					One cubic head can compute the rule exactly, with weights written down rather than
					trained. Put each attribute value <MathTex tex="v" /> on a circle at the angle <MathTex
						tex="2\pi v/3"
					/>: a third of a turn per step. Adding values then adds angles, and a multiple of 3 is a
					whole number of turns, so for three cards with values <MathTex tex="a, b, c" /> on one attribute
				</p>
				<MathTex
					display
					tex={'\\cos\\tfrac{2\\pi}{3}(a + b + c) = \\begin{cases} 1 & \\text{if } a + b + c \\equiv 0 \\pmod 3 \\\\ -\\tfrac12 & \\text{otherwise} \\end{cases}'}
				/>
				<p>
					The cosine of a sum of three angles expands into four terms, each a product of one
					function of the first angle, one of the second and one of the third (<MathTex tex="c" /> for
					cosine,
					<MathTex tex="s" /> for sine):
				</p>
				<MathTex
					display
					tex="\cos(\alpha + \beta + \gamma) = c_\alpha c_\beta c_\gamma - c_\alpha s_\beta s_\gamma - s_\alpha c_\beta s_\gamma - s_\alpha s_\beta c_\gamma"
				/>
				<p>
					That is a trilinear form with four channels. Give the query card the vector <MathTex
						tex="(c_\alpha, -c_\alpha, -s_\alpha, -s_\alpha)"
					/>, its role-1 key <MathTex tex="(c_\beta, s_\beta, c_\beta, s_\beta)" /> and its role-2 key
					<MathTex tex="(c_\gamma, s_\gamma, s_\gamma, c_\gamma)" />, and their trilinear form is
					<MathTex tex="\cos(\alpha + \beta + \gamma)" />. Do this for each of the four attributes,
					sixteen channels in all, and the score of a triple is the sum over attributes:
				</p>
				<MathTex
					display
					tex={'A_{ijk} = \\sum_{t=1}^{4} \\cos\\tfrac{2\\pi}{3}\\bigl(a_t + b_t + c_t\\bigr) = 4 - \\tfrac{3}{2}\\,m'}
				/>
				<p>
					Each attribute that obeys the rule adds 1 and each one that breaks it adds <MathTex
						tex="-\tfrac12"
					/>, so with <MathTex tex="m" /> broken attributes the score is <MathTex
						tex="4 - \tfrac32 m"
					/>: every SET scores 4 and every other triple at most 2.5. The sink pair gets a fixed
					score of 3.25, in between. Divide all scores by a small temperature before the softmax and
					a card in some SET puts nearly all of its weight on its SET pairs, while a card in none
					puts it on the sink. The head's answer is the weight that did not go to the sink. This
					head is the default in
					<a href={resolve('/explore')}>Explore, Cubic</a>, so its pictures there are exact before
					anything has been trained.
				</p>
			</section>

			<section id="binding">
				<h3><span class="n">{number('binding')}</span>Values as binding</h3>
				<p class="src">
					<span class="mark prior"></span>Bilinear values <Cite id="clift" />, Hadamard values <Cite
						id="chakrabarti"
					/>;
					<span class="mark new inline"></span>the indexing check is new here
				</p>
				<p>
					Scores choose pairs; values decide what a chosen pair passes back. Clift et al. combine a
					pair's two value vectors with a full bilinear map, every coordinate of one times every
					coordinate of the other, mixed by a learned table. The Hadamard value keeps only matching
					coordinates, which costs the same as computing the scores. Both read off one object, the
					<em>pair moment</em>: the weighted sum over pairs of the table of products of the two
					values. Its diagonal is the Hadamard output:
				</p>
				<MathTex
					display
					tex={'M_i = V^{1\\top} P_i\\, V^2 = \\sum_{j,k} P_{ijk}\\, V^1_j V^{2\\top}_k, \\qquad \\operatorname{diag}(M_i) = Y_i'}
				/>
				<p>
					Whichever form is used, the values have to come from the two partner tokens <MathTex
						tex="j"
					/> and <MathTex tex="k" />, not from the query. The definition of poly-attention does
					this, but its released code for the tree mechanism reads the second value at the query's
					position. With cubic scores held fixed and only the values changed, that indexing leaves
					SET at chance (54%), while Hadamard and full-moment values reach 100% in about 800 steps.
				</p>
			</section>

			<section id="training">
				<h3><span class="n">{number('training')}</span>What training shows</h3>
				<p class="src">
					<span class="mark measured"></span>Measured with this app's engine <Cite id="jaxjs" />
				</p>
				<p>
					Every model on the bench (the <a href={resolve('/compare')}>Compare</a> tab) sees the same
					batches of SET tables; only the attention operator differs. Each has one layer of width 64
					with four heads of 16, trained for 4,000 steps of AdamW from seed 0, and is scored on the
					1,024 held-out tables of chapter {number('encoding')}. "Standard" means ordinary pairwise
					attention. Feynman attention, the operator of chapter {number('diagrams')}, is listed now
					so the whole bench can be compared.
				</p>
				<table class="nums">
					<thead
						><tr><th>Model</th><th>Held-out accuracy</th><th>Reaches 95%</th><th>ms / step</th></tr
						></thead
					>
					<tbody>
						<tr class="hi"><td>Cubic</td><td>100%</td><td>step 500</td><td>12.2</td></tr>
						<tr><td>Feynman, 2 rounds</td><td>100%</td><td>step 700</td><td>35.7</td></tr>
						<tr><td>Strassen</td><td>95.8%</td><td>step 2,350</td><td>11.3</td></tr>
						<tr><td>Tree</td><td>76.4%</td><td>never</td><td>11.0</td></tr>
						<tr><td>Standard, 2 layers</td><td>64.4%</td><td>never</td><td>15.5</td></tr>
						<tr><td>Standard, 1 layer</td><td>60.5%</td><td>never</td><td>8.4</td></tr>
					</tbody>
				</table>
				<p>
					Always answering yes, the more common answer, scores 53.5%. The cubic head sits at chance
					until step 400 and is at 99% by step 500: the three-way rule is found all at once rather
					than gradually, the jump that the leap of chapter {number('set')} predicts. Strassen attention
					climbs slowly to 95.8% by the route of chapter {number('barrier')}; tree attention, degree
					2 with one edge fewer, stops at 76.4%. At this length the cubic head costs about the same
					time per step as the degree-2 ones. The ordering held on a second seed in offline runs.
				</p>
			</section>

			<section id="arity">
				<h3>
					<span class="n">{number('arity')}</span><span
						>Putting the <MathTex tex="k" />-way term in reach</span
					>
				</h3>
				<p class="src">
					<span class="mark prior"></span>Match-<MathTex tex="t" /> and <MathTex tex="t" />-tensor
					attention
					<Cite id="sanford" />; <span class="mark new inline"></span>the four-card test is new here
				</p>
				<p>
					Now ask whether four cards add up to zero, Match-4 from chapter {number('puzzles')}. The
					argument of chapter {number('set')} moves up one order. Three cards fix the fourth,
					<MathTex tex="d = -(a + b + c)" />, so in a random group of four that sums to zero, any
					three are just a random triple: only the complete four-card relation supplies the signal.
					That suggests a learning obstacle for lower-order terms, and in these runs cubic attention
					stalls at chance, as pairwise attention did on SET. A quartic head, the same construction
					one order up, can learn it:
				</p>
				<MathTex
					display
					tex={'A_{ijkl} = \\langle Q_i,\\; K^1_j \\odot K^2_k \\odot K^3_l \\rangle'}
				/>
				<p>
					The figure shows cloud runs on eight-card tables, where answering no is right 63% of the
					time: standard, Strassen and cubic attention sit exactly there, and only the quartic head
					is above it. In longer runs with three seeds (chapter {number('composition')}), quartic
					attention learns Match-4 on two seeds of three, after a long plateau.
				</p>
				<p>
					Every order has the same shape, the general polyattention of the original notebook: a
					query against ordered groups of role-specific keys, with the values multiplied along the
					group.
				</p>
				<ComputeGraph graph={GENERAL} label="Computation graph of polyattention of order N" />
				<p>
					A head of fixed order is a fixed bet. An order-<MathTex tex="k" /> head pays <MathTex
						tex="n^k"
					/> whether the data needs pairs, triples or more, and the right order can change from one example
					to the next. Part III asks whether one layer can choose.
				</p>
			</section>

			<!-- ── Part III ───────────────────────────────────────────────── -->
			<h2 class="part" id="part-beyond">Letting the data choose the arity</h2>
			<p class="part-lede">
				A head of order <MathTex tex="k" /> pays for <MathTex tex="k" />-way terms whether the data
				needs them or not. Physics faced a similar problem in the 1940s: how to add up interactions
				among any number of particles. Its answer was a picture language, Feynman diagrams, and
				equations that add up all the pictures at once. This part tells that story, then borrows it
				to build Feynman attention: a layer whose softmax chooses, for every token and every round,
				between keeping its own value, copying one other token (a hop) and multiplying two (a
				three-way vertex). Chained over rounds, hops follow pointers and vertices build larger
				products. It solves SET and pointer chasing in one layer, and it fails on Match-4; Part IV
				explains that failure and fixes it.
			</p>

			<section id="feynman">
				<h3><span class="n">{number('feynman')}</span>Where Feynman diagrams come from</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['feynman', 'dyson']} />
				</p>
				<p>
					In quantum electrodynamics, the theory of electrons and light, the quantity you want is an
					<em>amplitude</em>: a number whose square gives the probability of a process, say two
					electrons flying at each other and leaving with given momenta. The theory cannot be solved
					exactly. What it offers instead is a small number, the electron's charge <MathTex
						tex="e"
					/>, with <MathTex tex="\alpha = e^2/4\pi \approx 1/137" />. So the amplitude is computed
					as a power series in <MathTex tex="e" />: perturbation theory.
				</p>
				<p>
					In 1949 Feynman showed that every term of that series can be drawn. A straight line is a
					particle moving freely (a <em>propagator</em>), a wavy line is a photon, and a dot where
					three lines meet is an <em>interaction</em>, the place where an electron emits or absorbs
					a photon. Each dot contributes one factor of <MathTex tex="e" />, so a diagram with <MathTex
						tex="V"
					/> dots is a term of order <MathTex tex="e^V" />. The same year Dyson showed that the
					pictures follow exactly from the formal calculations of Schwinger and Tomonaga, which
					turned them from a heuristic into a method. For two electrons scattering:
				</p>
				<DiagramSum
					lhs="blob"
					width={64}
					terms={[
						{ kind: 'tree-t', caption: 'e^2' },
						{ kind: 'tree-u', caption: 'e^2' },
						{ kind: 'vacuum', caption: 'e^4' },
						{ kind: 'vertex', caption: 'e^4' },
						{ kind: 'box', caption: 'e^4' }
					]}
				/>
				<p>
					The hatched blob is everything that can happen; the right side lists the ways it can
					happen. At lowest order the electrons exchange one photon, either way round. At the next
					order the photon briefly becomes an electron–positron pair (the loop), or one electron
					emits and reabsorbs a photon of its own, or the electrons trade two photons. Every picture
					is one term, with exact rules for turning it into a number: a factor for each line, a
					coupling for each vertex, an integral for each loop.
				</p>
				<p>
					Two ideas carry over to attention. A complicated interaction among many particles is built
					from one small vertex, used over and over; read "particles" as "tokens". And nobody
					decides in advance how many particles take part: the theory adds up all the diagrams, and
					the couplings decide how much each one contributes. In attention that would mean nobody
					fixes the arity in advance: a layer adds up terms of every size and learned weights decide
					which matter.
				</p>
			</section>

			<section id="dyson">
				<h3><span class="n">{number('dyson')}</span>Summing them all at once</h3>
				<p class="src">
					<span class="mark prior"></span>Prior work <Cite id={['dyson', 'schwinger']} />
				</p>
				<p>
					Listing diagrams one at a time never ends. Dyson and Schwinger found equations that add up
					whole families of them at once. The simplest is for a single particle. Draw as a double
					line everything that can happen to an electron on its way from one point to another, all
					the emissions and reabsorptions included; physicists call this the <em>dressed</em>
					propagator, and the plain single line, the electron with nothing happening, the bare one. Let
					the blob
					<MathTex tex="\Sigma" />, the <em>self-energy</em>, stand for every way the electron can
					interact with itself in one stretch that cannot be cut in two by snipping a single line;
					longer histories are chains of such stretches. Then
				</p>
				<DiagramSum
					lhs="dressed"
					width={92}
					more={false}
					terms={[{ kind: 'bare' }, { kind: 'bare-sigma-dressed' }]}
				/>
				<MathTex display tex="G = G_0 + G_0\, \Sigma\, G" />
				<p>
					The dressed line appears on both sides, so the equation is self-consistent. Substituting
					it into itself unrolls it into an infinite series:
				</p>
				<DiagramSum
					lhs="dressed"
					width={92}
					terms={[
						{ kind: 'bare' },
						{ kind: 'bare-sigma-bare' },
						{ kind: 'bare-sigma-bare-sigma-bare' }
					]}
				/>
				<MathTex
					display
					tex={'G = G_0 + G_0 \\Sigma G_0 + G_0 \\Sigma G_0 \\Sigma G_0 + \\cdots = G_0\\,\\bigl(1 - \\Sigma\\, G_0\\bigr)^{-1}'}
				/>
				<p>
					Solving the equation sums every term of that series in one go. In the full theory <MathTex
						tex="\Sigma"
					/> itself depends on dressed propagators and vertices, so the equations form a tower that is
					cut off in practice; stopping after <MathTex tex="R" /> substitutions keeps exactly the diagrams
					up to depth <MathTex tex="R" />.
				</p>
				<p>
					That is the shape Feynman attention borrows. Read "a particle's dressed line" as "a
					token's state", "one more application of the interaction" as "one more round of
					attention", and "the couplings" as "softmax weights". A token's final state is then a sum
					over diagrams up to depth <MathTex tex="R" />, built from one vertex. One difference
					matters: in physics the coupling <MathTex tex="e" /> is a constant of nature, while here the
					weights are computed fresh from the input, for every token and every round.
				</p>
			</section>

			<section id="diagrams">
				<h3><span class="n">{number('diagrams')}</span>Sum over diagrams</h3>
				<p class="src"><span class="mark new"></span>New in this project: Feynman attention</p>
				<p>
					Feynman attention gives every token a <em>state</em>
					<MathTex tex="\Phi_t" /> and rebuilds it for <MathTex tex="R" /> rounds from the previous round's
					states. Round 0 is the token's own value, <MathTex tex="\Phi^0_t = v_t" />. In each later
					round the token chooses, with one softmax, among five kinds of term, called
					<em>sectors</em>:
				</p>
				<MathTex
					display
					tex={'\\begin{aligned}\\Phi^{r}_t = \\;& \\pi_{\\text{leaf}}\\, v_t + \\sum_j \\pi_j\\, \\Phi^{r-1}_j \\\\ &+ \\sum_{jk} \\pi_{jk}\\, \\Phi^{r-1}_j \\odot \\Phi^{r-1}_k \\\\ &+ \\sum_{jm} \\pi_{jm}\\, \\Phi^{r-1}_j \\odot \\Psi^{r}_m + \\pi_{\\text{carry}}\\, \\Phi^{r-1}_t\\end{aligned}'}
				/>
				<p>
					Term by term: keep your own value (a <em>leaf</em>); copy another token's state (a
					<em>hop</em>, the analogue of a propagator); multiply two tokens' states (a
					<em>cubic vertex</em>); multiply one token's state by a virtual mode (an
					<em>exchange</em>, explained below); or keep what you had (a <em>carry</em>). The weights
					<MathTex tex="\pi" /> are one softmax over all the options of all five sectors together, and
					they differ for every token <MathTex tex="t" /> and every round <MathTex tex="r" />. After
					the last round, each token's state goes through the usual output map and MLP. The
					dictionary between the two pictures:
				</p>
				<table class="dict">
					<thead><tr><th>Field theory</th><th>Feynman attention</th></tr></thead>
					<tbody>
						<tr
							><td>a particle's dressed line</td><td>a token's state <MathTex tex="\Phi_t" /></td
							></tr
						>
						<tr
							><td>the bare propagator <MathTex tex="G_0" /></td><td
								>the token's own value <MathTex tex="v_t" /></td
							></tr
						>
						<tr><td>the interaction vertex</td><td>one trilinear score</td></tr>
						<tr
							><td>the coupling <MathTex tex="e" /></td><td
								>a softmax weight <MathTex tex="\pi" /></td
							></tr
						>
						<tr><td>order in perturbation theory</td><td>the round <MathTex tex="r" /></td></tr>
						<tr><td>a virtual photon</td><td>a virtual mode <MathTex tex="\Psi_m" /></td></tr>
						<tr><td>the vacuum</td><td>a vacuum token whose value is all ones</td></tr>
					</tbody>
				</table>
				<ComputeGraph graph={FEYNMAN} label="Computation graph of Feynman attention" />
				<p>
					<strong>One vertex scores everything.</strong> Every option is scored the same way: the
					token's query, adjusted by a learned vector <MathTex tex="\tau_r" /> for the round (so a token
					can ask for different things in different rounds), against the Hadamard product of two keys,
					<MathTex tex="\langle q_t \odot \tau_r,\; u_\alpha \odot w_\beta \rangle" />. Each key
					slot holds a real token, the <em>vacuum</em> token or a virtual mode, and the sectors are
					the combinations: vacuum with vacuum is a leaf, a token with the vacuum is a hop, two
					tokens make a cubic vertex. A <em>virtual mode</em>
					<MathTex tex="\Psi^r_m" /> is a learned summary of pairs,
				</p>
				<MathTex
					display
					tex={'\\Psi^r_m = \\sum_{kl} \\rho_{m,kl}\\, \\Phi^{r-1}_k \\odot \\Phi^{r-1}_l'}
				/>
				<p>
					where <MathTex tex="\rho_m" /> is the mode's own softmax over pairs. Multiplying a token's state
					by a mode therefore reaches three other tokens at once, which is why after <MathTex
						tex="R"
					/>
					rounds a token's state can draw on anything from one token up to <MathTex tex="3^R" /> of them.
					Each round costs <MathTex tex="O(n^3 d + n^2 M d)" /> for <MathTex tex="M" /> modes, like one
					cubic layer.
				</p>
				<p>
					<strong>Two worked expansions.</strong> On SET, one cubic vertex is enough: a card's round-1
					state reads the product of the two cards that complete a SET with it,
				</p>
				<MathTex
					display
					tex={'\\Phi^1_i \\approx \\sum_{(j,k)\\,\\in\\,\\text{SETs}(i)} \\pi_{jk}\\; v_j \\odot v_k'}
				/>
				<p>
					On pointer chasing (chapter {number('puzzles')}) the query needs a chain of hops. Say the
					query points at node <MathTex tex="a" />, which points to <MathTex tex="b" />, which
					points to the last node <MathTex tex="c" />. Reading from the end: the query's round-4
					state copies node
					<MathTex tex="a" />'s round-3 state, which copied <MathTex tex="b" />'s, which copied <MathTex
						tex="c"
					/>'s, which carries <MathTex tex="c" />'s own value, the payload:
				</p>
				<MathTex
					display
					tex="\Phi^4_q \approx \Phi^3_a \approx \Phi^2_b \approx \Phi^1_c \approx v_c"
				/>
				<p>
					One hop per round, with carries once the end is reached. In the language of chapter {number(
						'feynman'
					)} the first is a single vertex and the second a long propagator; the same layer can be either,
					and the weights decide. The figure draws these trees in the style of TikZ-Feynman
					<Cite id="ellis" />; <a href={resolve('/explore/diagrams')}>Explore, Feynman</a> draws them
					for a model training live.
				</p>
			</section>

			<section id="sectors">
				<h3><span class="n">{number('sectors')}</span>Making it train</h3>
				<p class="src"><span class="mark new"></span>New in this project</p>
				<p>
					The first versions did not learn: on SET and on pointer chasing they stayed near chance.
					Three changes fixed that, each for a reason that can be stated.
				</p>
				<p>
					<strong>Chemical potentials.</strong> The sectors offer very different numbers of options:
					one leaf and one carry, about <MathTex tex="n" /> hops, about <MathTex tex="n^2" /> cubic pairs,
					<MathTex tex="nM" /> exchanges. When all scores start out about equal, a softmax gives each
					sector weight in proportion to its number of options, so at the start nearly all the weight
					goes to cubic and exchange terms and the simple, useful hops are drowned out. A fixed offset
					per sector <MathTex tex="s" />, the negative log of its number of options <MathTex
						tex="|S_s|"
					/>, gives every sector the same total weight at the start, one fifth:
				</p>
				<MathTex
					display
					tex={"\\mu_s = -\\log |S_s| \\quad\\Longrightarrow\\quad \\sum_{o \\in S_s} \\frac{e^{\\mu_s}}{\\sum_{s'} |S_{s'}|\\, e^{\\mu_{s'}}} = \\frac{1}{5}"}
				/>
				<p>
					In physics a chemical potential sets how many particles of each kind a system holds on
					average, which is the role this offset plays.
				</p>
				<p>
					<strong>An RMS read-out.</strong> Hadamard products of numbers below 1 shrink with every round,
					so the final state is divided by its root mean square (the square root of the average of its
					squared entries), which restores its scale.
				</p>
				<p>
					<strong>An absorbing carry.</strong> Without a way to keep its state, a token must rebuild everything
					every round, and an answer found in round 1 is overwritten in round 2. The carry lets a finished
					answer stay put from round to round.
				</p>
			</section>

			<section id="chase">
				<h3><span class="n">{number('chase')}</span>What Feynman attention learns</h3>
				<p class="src"><span class="mark measured"></span>Measured with this app's engine</p>
				<p>
					Pointer chasing (chapter {number('puzzles')}) asks for a number of lookup steps that
					changes from puzzle to puzzle <Cite id="chakrabarti07" />. Each node is one token holding
					its id, its pointer and its payload; the query is a last token holding only a pointer. The
					network answers at the query by choosing one of the eight payloads, so chance is 12.5%.
					Four rounds are enough: one to read the start node, then one per hop, at most three.
				</p>
				<table class="nums">
					<thead
						><tr><th>Model</th><th>Held-out accuracy</th><th>Parameters</th><th>ms / step</th></tr
						></thead
					>
					<tbody>
						<tr class="hi"
							><td>Feynman, 4 rounds, 1 layer</td><td>100%</td><td>61k</td><td>103</td></tr
						>
						<tr><td>Standard, 3 layers</td><td>94.2%</td><td>154k</td><td>43</td></tr>
						<tr><td>Standard, 2 layers</td><td>88.9%</td><td>104k</td><td>28</td></tr>
						<tr><td>Cubic, 1 layer</td><td>84.5%</td><td>63k</td><td>20</td></tr>
						<tr><td>Standard, 1 layer</td><td>64.5%</td><td>54k</td><td>15</td></tr>
					</tbody>
				</table>
				<p>
					Feynman attention passes 95% by step 250. Expanding a trained token's computation tree
					(the diagram view in <a href={resolve('/explore/diagrams')}>Explore, Feynman</a>) shows it
					following the true pointer path one hop per round, the same algorithm as the worked
					expansion of chapter
					{number('diagrams')}. It is not a universal winner. On Match-4 it stays at chance. On
					three-hop composition (chapter {number('puzzles')}) it succeeds on two of three seeds in
					the cloud runs, well above three ordinary layers (52%) but not reliably: one set of
					weights, reused every round, has to perform three different lookups.
				</p>
			</section>

			<!-- ── Part IV ────────────────────────────────────────────────── -->
			<h2 class="part" id="part-algebra">Arity is algebra</h2>
			<p class="part-lede">
				Part III let one softmax choose among arities, and it still failed on Match-4. This part
				asks what an arity really is, why building it from smaller pieces does not train, and how
				one layer can offer every arity at once, at a cost that grows only linearly with the number
				of tokens.
			</p>

			<section id="composition">
				<h3><span class="n">{number('composition')}</span>Composing arity does not train</h3>
				<p class="src">
					<span class="mark measured"></span>Measured on cloud GPUs with the research harness, three
					seeds per model, balanced accuracy (chance 50%)
				</p>
				<p>
					The cloud runs score every operator on Match-3, Match-4 and Match-5 (chapter {number(
						'puzzles'
					)}). Standard attention, at every depth we tried, reaches at most 66% on Match-3 and stays
					at chance on Match-4 and Match-5. Cubic attention and Feynman attention solve Match-3 and
					stay at chance above it. Dense quartic attention learns Match-4 on two seeds of three,
					after a long plateau.
				</p>
				<p>
					The most telling run gave Feynman attention every building block of the construction in
					chapter {number('newton')}: sums of tokens, products of a token with itself, and products
					of those sums. In principle, multiplying these pieces over two rounds produces the
					four-way term Match-4 needs, and its width (up to 192) was larger than the 81 cards of the
					deck. It still stayed at exactly chance on Match-4. The answer could be represented;
					gradient descent never found it.
				</p>
				<p>
					The leap of chapter {number('set')} suggests an explanation. In a group of <MathTex
						tex="k"
					/> cards that adds up to zero, any fewer than <MathTex tex="k" /> of them look exactly like
					random cards. This property of an isolated positive tuple helps explain the weak signal for
					lower-order features. It does not prove that every network gradient vanishes on a whole table.
					The experiments motivate putting a full <MathTex tex="k" />-way product directly in the
					layer, instead of asking training to build it from smaller pieces <Cite id="abbe" />.
				</p>
			</section>

			<section id="groups">
				<h3><span class="n">{number('groups')}</span>A group is a rule for combining</h3>
				<p class="src">
					<span class="mark prior"></span>Standard group theory; SET arithmetic <Cite id="davis" />
				</p>
				<p>
					A <em>group</em> is a collection of operations with a rule for combining them. Combining
					two operations gives another in the collection; there is an operation that does nothing,
					called the <em>identity</em>; and every operation has an <em>inverse</em> that undoes it.
					Finally, regrouping three operations leaves the answer unchanged. You may compute the
					first two first, or the last two first. This rule is called <em>associativity</em>.
				</p>
				<p>
					Think of a clock with three positions, 0, 1 and 2. An operation moves its hand forward by
					zero, one or two ticks, wrapping around after 2. One tick followed by two is zero ticks
					overall. Zero is the identity; one and two undo each other. This is addition
					<em>modulo 3</em>, written <MathTex tex={String.raw`\mathbb Z_3`} />. The same idea makes
					a 12-position clock, <MathTex tex={String.raw`\mathbb Z_{12}`} />.
				</p>
				<p>
					A SET card carries four such clocks, one per attribute. Add cards by adding their four
					values separately and wrapping each at 3. The notation <MathTex
						tex={String.raw`\mathbb Z_3^4`}
					/>
					means exactly those four clocks. A SET is three cards whose combined move is zero on all four.
					Here one move then another equals the reverse order: addition <em>commutes</em>. A group
					with this property is called <em>abelian</em>, or commutative.
				</p>
				<p>
					The next chapter draws the clock hand as a point on a circle. Its angle is its
					<em>phase</em>. In complex-number notation, multiplying two such points adds their angles.
					A product of clock hands is therefore a sum of moves in different coordinates.
				</p>
			</section>

			<section id="characters">
				<h3><span class="n">{number('characters')}</span>A relation is agreement of phases</h3>
				<p class="src">
					<span class="mark prior"></span>Characters of finite abelian groups, classical;
					<span class="mark new inline"></span>their use in the Newton layer is studied here
				</p>
				<p>
					Give every card a <em>phase</em>, a point on the unit circle, in a way that turns adding
					cards into multiplying phases. Pick a vector <MathTex
						tex={String.raw`c \in \mathbb Z_3^4`}
					/>
					and send card <MathTex tex="x" /> to
				</p>
				<MathTex
					display
					tex={String.raw`\phi_c(x) = \omega^{\langle c, x\rangle}, \qquad \omega = e^{2\pi i/3}, \qquad \phi_c(x)\,\phi_c(y) = \phi_c(x + y)`}
				/>
				<p>
					Here <MathTex tex="\omega" /> is a third of a turn, <MathTex
						tex={String.raw`\langle c, x\rangle`}
					/> is the dot product taken modulo 3, and the phase of a card is that many thirds of a turn.
					Because adding cards adds their dot products with <MathTex tex="c" />, multiplying phases
					adds cards, which is the last identity.
				</p>
				<p>
					<strong>An example.</strong> Take <MathTex tex="c = (1, 0, 0, 0)" />. Then <MathTex
						tex={String.raw`\langle c, x\rangle`}
					/> is just the card's number value, so the SET of chapter {number('puzzles')}, with
					numbers 0, 1 and 2, gets phases <MathTex tex={String.raw`1, \omega, \omega^2`} /> whose product
					is
					<MathTex tex={String.raw`\omega^3 = 1`} />. The near miss of that chapter differs only in
					colour, so under this <MathTex tex="c" /> its phases also multiply to 1: one character can be
					fooled. Under <MathTex tex="c = (0, 0, 0, 1)" />, which reads colour, the near miss's
					product is <MathTex tex={String.raw`\omega^2`} /> instead.
				</p>
				<p>
					A SET's phases multiply to 1 under all 81 choices of <MathTex tex="c" />, because its
					cards add up to zero. Any other triple adds up to some nonzero vector <MathTex tex="s" />,
					and then the 81 choices of <MathTex tex="c" /> split evenly into three groups whose products
					are
					<MathTex tex={String.raw`1, \omega, \omega^2`} />, which cancel. So averaging over all of
					them detects SETs exactly:
				</p>
				<MathTex
					display
					tex={String.raw`\frac{1}{81}\sum_{c} \phi_c(x)\,\phi_c(y)\,\phi_c(z) \;=\; \mathbf 1\big[x + y + z = 0\big]`}
				/>
				<p>
					These <MathTex tex={String.raw`\phi_c`} /> are the <em>characters</em> of this group: maps
					that turn a sum into a product of phases. Together they form a <em>Fourier basis</em>, a
					complete set of wave-like coordinates for functions on the cards. One of them, <MathTex
						tex="c = 0"
					/>, sends every card to 1 and carries no information. The other 80 come in pairs <MathTex
						tex="c"
					/> and <MathTex tex="-c" /> whose phases are mirror images, so 40 distinct ones are worth learning,
					a number chapter {number('newtonattn')} comes back to. In this basis a <MathTex
						tex="k"
					/>-way relation is a product of <MathTex tex="k" /> phases, averaged over characters. The figure
					also shows <MathTex tex="k = 2" />: a card and its complement <MathTex tex="-x" /> always add
					up to zero. Networks are known to find Fourier features for arithmetic in a group <Cite
						id="nanda"
					/>; chapter {number('newtonattn')} shows an attention layer finding these.
				</p>
			</section>

			<section id="newton">
				<h3><span class="n">{number('newton')}</span>Every arity at once</h3>
				<p class="src">
					<span class="mark prior"></span>Classical Newton identities;
					<span class="mark new inline"></span>their use in this relational layer
				</p>
				<p>
					Counting relations directly means listing groups of cards, and the number of groups of
					size
					<MathTex tex="k" /> grows like <MathTex tex="n^k" />. There is a shortcut. Start small:
					three tokens with phases <MathTex tex="a, b, c" /> on one channel. Their sum over pairs is
				</p>
				<MathTex
					display
					tex={String.raw`ab + bc + ac \;=\; \tfrac12\Big((a + b + c)^2 - (a^2 + b^2 + c^2)\Big)`}
				/>
				<p>
					Square the sum, take away the squares, halve. The right side needs only two quantities,
					the sum of the phases and the sum of their squares, each one pass over the tokens however
					many there are. These are <em>power sums</em>, <MathTex
						tex={String.raw`P_j = \sum_t \phi(x_t)^{\odot j}`}
					/>, the sum over tokens of each phase raised to the power <MathTex tex="j" /> (a new <MathTex
						tex="P"
					/>, unrelated to the attention weights of chapter {number('pairwise')}). Newton's
					identities do the same for groups of every size: the
					<em>elementary symmetric polynomial</em>
					<MathTex tex="e_m" />, the sum over every group of <MathTex tex="m" /> distinct tokens of the
					product of their phases, follows from the power sums by a short recursion:
				</p>
				<MathTex
					display
					tex={String.raw`m\, e_m \;=\; \sum_{j=1}^{m} (-1)^{j-1}\, e_{m-j} \odot P_j, \qquad e_m = \sum_{|S| = m}\; \bigodot_{t \in S} \phi(x_t)`}
				/>
				<p>
					With <MathTex tex="m = 2" /> it is the example above. Now combine this with chapter {number(
						'characters'
					)}: give each of the 81 characters its own channel, so a card has one phase per channel.
					For a card <MathTex tex="x" />, take <MathTex tex={String.raw`e_{k-1}`} /> of the other cards
					in every channel, so every group of <MathTex tex="k - 1" /> others is present as the product
					of its phases; multiply by
					<MathTex tex="x" />'s own phase and average over the channels. A group that adds up to
					zero with <MathTex tex="x" /> contributes 1 and every other group contributes 0, so the result
					is the number of size-<MathTex tex="k" /> relations <MathTex tex="x" /> takes part in. A handful
					of power sums count every card's relations of every size, with no group ever listed: one pass
					over the tokens per power, plus a recursion that does not depend on <MathTex tex="n" />.
					The figure deals nine cards, counts every card's relations of size 3, 4 and 5 this way,
					and checks each count against listing the groups one by one.
				</p>
			</section>

			<section id="newtonattn">
				<h3><span class="n">{number('newtonattn')}</span>Newton attention</h3>
				<p class="src">
					<span class="mark new"></span>New in this project;
					<span class="mark measured inline"></span>measured on cloud GPUs, three seeds per model
				</p>
				<p>
					Newton attention makes the construction of chapter {number('newton')} learnable. It is a different
					kind of layer from the ones before: it has no softmax, no keys and no values. Each token gets
					<MathTex tex="r" /> complex channels (a new <MathTex tex="r" />, not the round of Part
					III). A channel is a point in the plane with an angle and a length: the angle is a learned
					linear function of the token's vector, and the length is a learned gate between 0 and 1. A
					character's angle, <MathTex tex={String.raw`2\pi\langle c, x\rangle/3`} />, is itself a
					linear function of a card's attributes, so a channel can become exactly a character.
				</p>
				<p>
					The rest is fixed algebra. For each query token: power sums over the other tokens (the
					query's own phases are left out), Newton's identities to get <MathTex tex="e_m" /> for every
					group size <MathTex tex="m" />, and the query's phases times <MathTex tex="e_m" />. In
					each channel that is the sum, over every group of <MathTex tex="m" /> other tokens, of the product
					of the group's phases and the query's: the quantity chapter {number('newton')} averaged over
					characters to count the relations of arity <MathTex tex="m + 1" /> the query is in. Here a learned
					linear read-out does the averaging, so it can weight channels as the task needs. The cap <MathTex
						tex="K"
					/> is the largest arity offered, and every arity up to <MathTex tex="K" /> costs <MathTex
						tex="O(nKr)"
					/>, linear in the number of tokens.
				</p>
				<ComputeGraph graph={NEWTON} label="Computation graph of Newton attention" />
				<p>
					With every arity up to six on offer, it solves SET (Match-3), Match-4 and the
					smallest-arity task on every seed; on smallest arity, where chance is 25%, the best
					fixed-order operator reaches 54%. On Match-5 it reaches 85% at the standard size and 97.5%
					with twice the channels. Cap the arities below the task's, offering at most three on
					Match-4, and it falls to exactly chance. Two details made it exact. Each arity's features
					are rescaled to the same size before the read-out, because high arities are products of
					many numbers below one and otherwise barely learn. And one read-out is shared by all
					arities, with a learned scale per arity, because the same characters count relations of
					every size.
				</p>
				<p>
					Two probes show what it learned. Switch off one arity at a time: on Match-3 only arity 3
					matters, on Match-4 only arity 4, and on the smallest-arity task exactly arities 3, 4 and
					5. Nothing told it which arities the task has. And its channels become characters. Every
					run that solves its task has found all 40 (chapter {number('characters')}), and a run that
					falls short has accuracy close to linear in how many it found.
				</p>
			</section>

			<section id="transfer">
				<h3><span class="n">{number('transfer')}</span>Small relations teach large ones</h3>
				<p class="src">
					<span class="mark measured inline"></span>Measured on cloud GPUs, three seeds per model
				</p>
				<p>
					A character that counts triples also counts groups of four and five. So train one layer on
					Match-3, 4 and 5 at once, with the first token of each table saying which <MathTex
						tex="k"
					/>
					it asks about, and score it on each. Each arity sees only a third of the data, yet the mixed
					layer is exact on all three on every seed, where the same layer trained on Match-5 alone reaches
					85%. Even the layer before the fixes of chapter {number('newtonattn')} went from 57% to 83%
					on Match-5 this way. The easy relations find the characters and the hard ones reuse them. Abbe
					et al. describe exactly this: a learner crosses a large leap when easier, related targets lead
					up to it like steps <Cite id="abbe" />.
				</p>
				<p>
					This is a strong result on puzzles built from modular addition. It leaves two questions:
					does the gain survive on language, and what changes when the operations no longer commute?
					The answers lead to the final part of the course.
				</p>
			</section>

			<!-- ── Part V ─────────────────────────────────────────────────── -->
			<h2 class="part" id="part-compose">Learning to compose</h2>
			<p class="part-lede">
				The road began with more tokens per interaction. It ends with the operation that combines
				them, and with the information that operation preserves.
			</p>

			<section id="language">
				<h3><span class="n">{number('language')}</span>The language result is negative</h3>
				<p class="src">
					<span class="mark measured"></span>Research harness, three seeds; SEARCH §8 and LOCAL §0
				</p>
				<p>
					A language model predicts the next token. Its held-out <em>loss</em> measures how much probability
					it gives the correct next tokens; lower is better. The first searches, S0–S2, found no advantage
					for our higher-order layers over softmax at the tested scale, including comparisons with equal
					computation. Success on SET did not imply success on text.
				</p>
				<p>
					The later S6 experiment did find small gains. <em>Local-linear attention</em>
					<Cite id="lla" /> fits a local linear predictor where softmax takes a weighted average. It improved
					loss by about 0.4% at equal computation. <em>Parallax</em>
					<Cite id="parallax" />, a published correction using pairwise terms, improved it by about
					0.75%. Both fell short of the registered 1% threshold. Parallax also beat the version with
					more available arities. That comparison changes more than arity, so it suggests, but does
					not prove, that the small gain came from the correction rather than higher order.
				</p>
				<p>
					The honest conclusion is narrower than “higher order wins”: these layers help on relations
					we designed them to expose. No benefit from higher arity on language was established at
					our scale. The <a href={resolve('/report')}>report</a> gives the protocols and full results.
				</p>
			</section>

			<section id="features">
				<h3><span class="n">{number('features')}</span>Good coordinates are not enough</h3>
				<p class="src">
					<span class="mark measured"></span>GROUPS §5.1; three seeds, 6,000 steps, balanced
					accuracy
				</p>
				<p>
					Maybe Newton attention won only because it found the right coordinates. Test that
					directly: give softmax every nontrivial character of the card group in advance, as fixed
					input features. It gets the clock hands without having to learn them. Use one or two
					layers of width 192, and test Match-4 on fresh tables.
				</p>
				<p>
					Both depths finish at <strong>50.0% on all three seeds</strong>, exactly chance. Rotating
					the feature coordinates before training gives the same result. The Newton reference
					reaches
					<strong>100%</strong>. Supplying the useful coordinates did not make these softmax models
					learn the needed products within this budget.
				</p>
				<p>
					This is a result about learning, not an impossibility theorem about softmax. Transformers
					can learn modular arithmetic <Cite id="nanda" />, and sufficiently large fixed-length
					models can represent these tasks. Newton supplies the multiplication directly. The next
					experiment asks what that multiplication must retain when the sequence order matters.
				</p>
			</section>

			<section id="order">
				<h3><span class="n">{number('order')}</span>When order changes the answer</h3>
				<p class="src">
					<span class="mark prior"></span>Standard group theory;
					<span class="mark new inline"></span>the ordered Match-3 benchmark
				</p>
				<p>
					A triangle gives a different group. Label its corners A, B and C. Turn it one third of a
					turn, or flip it across its vertical axis. Both moves return the unlabelled triangle to
					the same outline, so they are <em>symmetries</em>: operations that preserve its shape.
					There are six such moves, including doing nothing. They obey the group rules from chapter
					{number('groups')}.
				</p>
				<p>
					Now watch the labels. Turn then flip ends in a different arrangement from flip then turn.
					These operations do not commute. Their group is <em>nonabelian</em>. Associativity still
					holds: changing the brackets is harmless; changing the order is not.
				</p>
				<p>
					In <em>ordered Match-3</em>, every token names a group operation. A token is positive when
					it belongs to three distinct positions whose operations, composed in sequence order, give
					the identity. “Product” now means this composition, written
					<MathTex tex="abc=e" />, with <MathTex tex="e" /> denoting the do-nothing operation. For clocks,
					the task is still addition. For noncommuting operations, swapping two tokens can change which
					triples work.
				</p>
			</section>

			<section id="representations">
				<h3>
					<span class="n">{number('representations')}</span>Representing operations as rotations
				</h3>
				<p class="src">
					<span class="mark prior"></span>Standard representation theory; learned group algorithms <Cite
						id="chughtai"
					/>
				</p>
				<p>
					A <em>representation</em> assigns a matrix to each group operation so that multiplying the
					matrices agrees with combining the operations. Write that assignment as
					<MathTex tex="\rho" />. Its defining rule is
					<MathTex tex="\rho(ab)=\rho(a)\rho(b)" />. Such a rule-preserving map is also called a
					<em>homomorphism</em>. A representation is <em>faithful</em> if distinct operations get distinct
					matrices: it loses none of the group's identity information.
				</p>
				<p>
					The clocks were already representations. A phase is a rotation in a two-dimensional plane.
					In three dimensions, rotations around different axes need not commute. That creates room
					to represent operations for which order matters.
				</p>
				<p>
					The experiments use two particularly concrete groups. <MathTex tex="A_4" /> has the 12 rotations
					of a tetrahedron, the solid with four triangular faces.
					<MathTex tex="A_5" /> has the 60 rotations of an icosahedron, the solid with 20 triangular faces
					shown beside the text. Each operation can therefore be stored as a 3 by 3 rotation matrix. These
					representations are <em>irreducible</em>: no change of coordinates splits them into
					smaller independent matrix blocks. “Irrep” is simply an abbreviation for this word.
				</p>
				<p>
					The model receives token identities and task labels, not these geometric constructions.
					The question is whether its learned matrices acquire the same multiplication rule.
				</p>
			</section>

			<section id="holonomy">
				<h3><span class="n">{number('holonomy')}</span>Compose first, then read</h3>
				<p class="src">
					<span class="mark prior"></span>Ordered subsequences in Seq2Tens <Cite id="seq2tens" />;
					learned group products in path development <Cite id="development" />;
					<span class="mark new inline"></span>the marked matrix readout studied here
				</p>
				<p>
					<em>Holonomy attention</em> gives every token, in every head, a learned rotation matrix and
					a gate between zero and one. The gate controls how strongly the token participates. To relate
					a subset of tokens, multiply their gated matrices in the order they appear. To read a token,
					add up those ordered products over every subset containing it, keeping each subset size separate.
					A learned readout turns those sums into features for the next stage.
				</p>
				<p>
					For three tokens, the size-three term is their one ordered product. For a longer sequence,
					the size-three term adds all candidate triples containing the token being read. Running
					summaries from the left and right reuse partial products, so the layer need not list every
					subset. The name “holonomy” comes from geometry, where following a path accumulates
					transformations.
				</p>
				<p>
					In two dimensions, all these rotations commute. This gives the same phase-product
					construction as Newton attention. In three or more dimensions, they can preserve order.
					The experiments give these layers no position embeddings: order enters through the
					products. A scan inside a layer still performs work across the sequence; “one layer” does
					not mean one arithmetic operation.
				</p>
				<p>
					Neither ordered-subsequence sums nor learned rotation products originated here. Seq2Tens
					and path development are the closest predecessors. The specific object studied here is the
					gated matrix version with a separate readout for each token and each subset size.
				</p>
			</section>

			<section id="group-results">
				<h3><span class="n">{number('group-results')}</span>What the rotation heads learn</h3>
				<p class="src">
					<span class="mark measured"></span>GROUPS §5.2; three seeds, 6,000 steps; longer runs
					explicitly exploratory
				</p>
				<p>
					On the 12- and 60-position clock groups, Newton and every tested rotation dimension reach
					100.0%. On the noncommuting groups, their paths split. Newton reaches 80.7% on
					<MathTex tex="A_4" /> and 76.1% on <MathTex tex="A_5" />. Two-dimensional holonomy reaches
					81.1% and 73.1%. These are useful scores, but below the exact limits of what an
					order-blind model can know. The next chapter explains those limits.
				</p>
				<p>
					Three-dimensional holonomy reaches 100.0% on <MathTex tex="A_4" />. On
					<MathTex tex="A_5" />, the ladder at 6,000 steps is 73.1%, 94.1%, 99.5%, 100.0%, 100.0%
					for dimensions 2, 3, 4, 5 and 8. The 100.0% mean at dimension 5 is rounded in the results:
					its three seeds are 99.97%, 99.96% and 99.98%.
				</p>
				<p>
					Dimension 3 was between the two registered decision thresholds, so that comparison was
					undecided. Exploratory runs extended to 20,000 steps reach 99.21%, 99.38% and 99.34%. The
					small representation can learn nearly all of this task; the finite runs do not prove exact
					convergence.
				</p>
				<p>
					The heads also learn approximate group structure. Their matrices can be checked directly:
					does the matrix for <MathTex tex="a" /> times the matrix for <MathTex tex="b" /> match the matrix
					for <MathTex tex="ab" />? The discrepancy is the <em>homomorphism error</em>. The sum of a
					matrix’s diagonal entries is its <em>trace</em>. Small errors and matching traces identify
					approximate tetrahedral and icosahedral representations. These diagnostics are evidence,
					not certificates of exact equality. The
					<a href={resolve('/explore/groups')}>rotation lab</a> shows an actual trained head.
				</p>
			</section>

			<section id="limits">
				<h3><span class="n">{number('limits')}</span>What is proved, and under what rules</h3>
				<p class="src">
					<span class="mark new"></span>Task-specific results in THEORY §§2–4; the definitions and
					decision principle are standard
				</p>
				<p>
					<strong>Information lost cannot be recovered.</strong> If a layer sees the marked token
					and the other tokens with their counts, but loses their order, some inputs with different
					answers become identical to it. Even an unlimited classifier after that layer cannot tell
					those inputs apart. The best achievable balanced accuracy, called the
					<em>order-blind ceiling</em>, is exactly <strong>83.0546984493%</strong> on the six-token
					<MathTex tex="A_4" /> benchmark and <strong>77.2287515874%</strong> on the eleven-token
					<MathTex tex="A_5" /> benchmark.
				</p>
				<p>
					This bound applies to position-free Newton and commuting holonomy layers with a tokenwise
					readout. It does not apply once positions, causal masks, or earlier order-aware layers
					reveal the missing order. The measured scores sit below these ceilings; the proof does not
					say training must reach them.
				</p>
				<p>
					<strong>A faithful representation is sufficient, with enough selection.</strong> For
					ordered Match-3, enough heads with token-dependent gates can separate candidate triples by
					their contents. An <em>orthogonal</em> matrix preserves lengths and angles. A faithful
					orthogonal representation, together with a sufficiently wide readout that keeps the marked
					token's identity, then distinguishes successful triples exactly. Our implemented rotations
					must fit that representation, as <MathTex tex="A_4" /> and <MathTex tex="A_5" />
					do in dimension 3. For arbitrary Match-<MathTex tex="k" />, the separate construction also
					requires gates that select positions. Neither construction proves efficient learning.
				</p>
				<p>
					<strong>Faithful is sufficient, not necessary.</strong> Under exact representations, unrestricted
					token gates and a sufficiently wide readout, the precise Match-3 condition is that every pair
					of operations that fails to commute is kept noncommuting in at least one head. Several heads
					can share that job. There is no universal theorem saying the smallest faithful dimension is
					necessary, or that softmax cannot solve the task.
				</p>
			</section>

			<section id="programs">
				<h3><span class="n">{number('programs')}</span>A second test: execute a program</h3>
				<p class="src">
					<span class="mark new"></span>The task; <span class="mark measured inline"></span>GROUPS
					§7, three seeds
				</p>
				<p>
					Start with four variables holding 0, 1, 2 and 3. An instruction swaps the contents of two
					variables. Three such instructions form a tiny program. Interleave the instructions of two
					independent programs, then ask for one variable's final value. The model must select the
					relevant instructions and compose them in order. It receives instruction tokens, not
					precomputed permutation matrices.
				</p>
				<p>
					The exact order-blind ceiling is <MathTex tex="67/108" />, or 62.037…%. Newton reaches
					62.05% and commuting holonomy 62.02%. Noncommuting holonomy at dimensions 3 and 4 reaches
					100.00% on every seed. But so does a matrix-state recurrent network, which carries a
					matrix forward through the instructions. Positional softmax reaches 98.95% with one layer
					and 100.00% with two or three.
				</p>
				<p>
					This second benchmark confirms the loss from discarding order. It shows no advantage over
					the order-aware baselines, and the models are not matched in parameter count or
					computation. These are short synthetic programs, not evidence about natural code or long
					programs.
				</p>
				<!-- WORD-PROBLEMS -->
				<p>
					A separate word-problem test asks models to compose an entire sequence of group
					operations; results pending.
				</p>
			</section>

			<section id="meaning">
				<h3><span class="n">{number('meaning')}</span>What the result means</h3>
				<p class="src">
					<span class="mark new"></span>Synthesis of this project's evidence;
					<span class="mark prior inline"></span>composition as a sequence-model principle <Cite
						id={['seq2tens', 'development']}
					/>
				</p>
				<p>
					The important design choice is what happens when features meet. Pairwise attention
					compares and retrieves. Newton multiplies phases, which adds clock moves but loses their
					order. Holonomy multiplies rotations, which can preserve it. On these controlled tasks,
					that difference predicts an information limit and points toward a learnable computation.
				</p>
				<p>
					The next questions are practical: can a model select relevant operations among many
					distractors, keep composing on longer sequences, and improve a real task at equal
					computation? The language experiments give no permission to assume the last answer is yes.
					The contribution is a concrete layer, a precise restricted separation, and inspectable
					evidence of learned symmetry. That is enough to make the next experiments worth doing.
				</p>
				<p>
					<a href={resolve('/explore/groups')}>Inspect the rotations</a> or read the
					<a href={resolve('/report')}>full report</a>.
				</p>
			</section>

			<section id="references" class="refs">
				<h2 class="part">References</h2>
				<ol>
					{#each REFERENCES as r (r.id)}
						<li id="ref-{r.id}">
							<span class="who">{r.authors}.</span>
							{#if r.url}
								<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
								<a href={r.url} rel="external noopener noreferrer" target="_blank">{r.title}</a>.
							{:else}
								<span class="title">{r.title}</span>.
							{/if}
							<span class="venue">{r.venue}, {r.year}.</span>
						</li>
					{/each}
				</ol>
			</section>
		</article>

		<aside class="figure" aria-live="polite">
			{#if COMPOSITION_CHAPTERS.has(section)}
				<CompositionFigure {section} />
			{:else}
				<LearnFigure {section} />
			{/if}
		</aside>
	</div>
</PageFrame>

<style>
	/* text first: a column of about 80 characters and a figure a little narrower, centred
	   together and growing with the screen, so neither hugs an edge on a wide display */
	.learn {
		--read: clamp(14px, calc(10px + 0.28vw), 15px);
		/* the app's type tokens, scaled with the reading size inside this page */
		--text-2xs: calc(var(--read) * 0.733);
		--text-xs: calc(var(--read) * 0.8);
		--text-sm: calc(var(--read) * 0.867);
		--text-ui: calc(var(--read) * 0.933);
		--text-lg: calc(var(--read) * 1.067);
		--measure: calc(var(--read) * 40);
		--gap: clamp(40px, 3.5vw, 96px);
		--pad: clamp(32px, 3vw, 72px);
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr);
		gap: var(--gap);
		max-width: calc(var(--measure) * 1.9 + var(--gap) + 2 * var(--pad));
		margin: 0 auto;
		padding: 0 var(--pad);
		font-size: var(--read);
	}
	.text {
		padding: 32px 0 30vh;
	}
	h1 {
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: calc(var(--read) * 2.533);
		font-weight: 400;
		line-height: 1.1;
	}
	.lede {
		margin-top: 12px;
		font-size: var(--read);
		line-height: 1.65;
		color: var(--color-ink-2);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 6px 20px;
		margin-top: 10px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.legend li {
		display: inline-flex;
		align-items: center;
	}
	.mark {
		display: inline-block;
		flex: none;
		width: 7px;
		height: 7px;
		margin-right: 6px;
		border-radius: 50%;
		border: 1px solid var(--color-ink-3);
		vertical-align: 0;
	}
	.mark.new {
		border-color: var(--color-ink);
		background: var(--color-ink);
	}
	.mark.measured {
		border-color: var(--color-ink-2);
		background: radial-gradient(circle, var(--color-ink-2) 0 1.5px, transparent 2px);
	}
	.mark.inline {
		margin-left: 4px;
	}
	.toc {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 18px;
		margin-top: 26px;
		padding-top: 18px;
		border-top: 1px solid var(--color-rule);
	}
	.toc-title {
		display: block;
		margin-bottom: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.toc ol {
		display: grid;
		gap: 3px;
	}
	.toc a {
		display: flex;
		gap: 8px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		text-decoration: none;
	}
	.toc a:hover {
		color: var(--color-ink);
	}
	.toc a .num {
		min-width: 14px;
	}
	h2.part {
		margin: 56px 0 4px;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: calc(var(--read) * 1.733);
		font-weight: 400;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	section {
		padding: 26px 0 4px;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	h3 {
		display: flex;
		align-items: baseline;
		gap: 12px;
		font-size: calc(var(--read) * 1.2);
		font-weight: 500;
		letter-spacing: -0.01em;
	}
	.n {
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: var(--read);
		color: var(--color-ink-3);
		min-width: 14px;
	}
	.src {
		margin: 4px 0 12px 26px;
		line-height: 1.6;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	p {
		color: var(--color-ink-2);
		font-size: var(--read);
		line-height: 1.7;
		margin: 0 0 12px;
	}
	p :global(.katex) {
		color: var(--color-ink);
	}
	strong {
		font-weight: 500;
		color: var(--color-ink);
	}
	em {
		font-style: italic;
		color: var(--color-ink);
	}
	.part-lede {
		margin-top: 10px;
		color: var(--color-ink-2);
	}
	.dict {
		width: 100%;
		margin: 2px 0 16px;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	.dict th {
		padding: 0 12px 6px 0;
		text-align: left;
		font-weight: 400;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.dict td {
		padding: 4px 12px 4px 0;
		color: var(--color-ink-2);
	}
	.dict td:last-child {
		color: var(--color-ink);
	}
	a {
		color: var(--color-ink);
		text-decoration: underline;
		text-decoration-color: var(--color-rule);
		text-underline-offset: 3px;
	}
	a:hover {
		text-decoration-color: var(--color-ink);
	}
	section :global(.math.display) {
		margin: 4px 0 14px;
		padding: 6px 0;
		overflow-x: auto;
		font-size: calc(var(--read) * 1.033);
	}
	.cases {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
		margin: 2px 0 16px;
	}
	.examples {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 12px 28px;
		margin: 2px 0 16px;
	}
	.example {
		display: flex;
		flex-direction: column;
		gap: 5px;
	}
	.example .hint {
		font-size: var(--text-xs);
		line-height: 1.45;
		color: var(--color-ink-3);
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
	.nums {
		width: 100%;
		margin: 2px 0 14px;
		border-collapse: collapse;
		font-size: var(--text-sm);
		font-variant-numeric: tabular-nums;
	}
	.nums th {
		padding: 0 10px 6px 0;
		text-align: left;
		font-weight: 400;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.nums td {
		padding: 4px 10px 4px 0;
		color: var(--color-ink-2);
	}
	.nums tr.hi td {
		color: var(--color-ink);
	}
	.refs ol {
		display: grid;
		gap: 10px;
		margin-top: 14px;
		padding-left: 22px;
		list-style: decimal;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.refs li:target {
		color: var(--color-ink);
	}
	.refs .who,
	.refs .title {
		color: var(--color-ink-2);
	}

	/* a display equation wider than the column scrolls instead of being clipped */
	.text :global(.katex-display) {
		overflow-x: auto;
		overflow-y: hidden;
		padding: 2px 0;
	}
	/* the sticky figure */
	.figure {
		position: sticky;
		top: calc(var(--bar-h) + 20px);
		height: calc(100dvh - var(--bar-h) - 40px);
		display: grid;
		align-items: center;
	}

	/* phones and tablets: the figure pins under the bar and the text scrolls beneath it */
	@media (max-width: 1100px) {
		.learn {
			grid-template-columns: minmax(0, 1fr);
			gap: 0;
			padding: 0 16px;
		}
		.figure {
			order: -1;
			z-index: 5;
			top: var(--bar-h);
			height: 38dvh;
			margin: 0 -16px;
			padding: 10px 16px;
			background: var(--color-void);
			border-bottom: 1px solid var(--color-rule);
			overflow: hidden;
		}
		section,
		h2.part {
			scroll-margin-top: calc(var(--bar-h) + 38dvh + 16px);
		}
		.text {
			padding: 20px 0 80px;
		}
		.toc {
			grid-template-columns: minmax(0, 1fr);
		}
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 30px;
		}
		.cases,
		.examples {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
