<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import type { Card } from '#lib/set/cards.ts';
	import { number } from '../toc.ts';

	// a SET (number, shading and colour all differ, shape the same) and a near miss that
	// differs from it only in the third card's colour
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
</script>

<section class="part" id="part-question">
	<header class="part-head">
		<span class="roman">Part I</span>
		<h2>The question</h2>
	</header>

	<section class="chapter" id="intro">
		<h3><span class="n">{number('intro')}</span>What this is about</h3>
		<p>
			Transformers, the networks behind today's language models, are built around one operation:
			<em>attention</em>. Attention lets each token in a sequence look at the others, one pair at a
			time. A token asks a question (its query), every other token offers an answer (its key), and
			the best matches pass their information along. Whatever a transformer knows about how three or
			four tokens relate, it has to assemble from these pairwise comparisons, layer after layer.
		</p>
		<p>
			This article follows a research project that started from a simple question. What if a layer
			could look at groups of tokens directly, three or four at once, instead of in pairs? Would it
			learn things pairwise attention cannot? And would that make better language models?
		</p>
		<p>
			The answer came in three parts. On puzzles built around relations among several tokens, layers
			that look at groups win decisively, often going from chance to perfect. On real text, at the
			scale we could afford, none of our higher-order layers beat ordinary attention by the margin
			we had set in advance. And the reason they won on the puzzles turned out to be different from
			what we first thought. It was not how many tokens a layer looks at. It was how the layer
			combines what it finds: whether it can <em>compose</em> operations, the way rotations compose, and
			keep track of the order in which they happen.
		</p>
		<h4>The short version</h4>
		<ol class="lede-list">
			<li>
				<span
					>Pairwise attention is blind to some relations. On the card game SET, one layer that
					scores whole triples reaches 100% in your browser; two layers of ordinary attention reach
					64%.</span
				>
			</li>
			<li>
				<span
					>A layer can offer every group size at once, at a cost that grows only linearly with the
					sequence (Newton attention). It solves Match-3 and Match-4 exactly by learning the Fourier
					basis of the cards, and a run is exact when it has found all of that basis.</span
				>
			</li>
			<li>
				<span
					>On language, nothing higher-order cleared our bar of 1% lower loss at equal compute. Once
					the softmax baseline uses rotary positions, recurrent networks that multiply matrices
					along the sequence beat it by only 0.1–0.3%. A hybrid of recurrence and attention beats it
					by 0.8–0.9%, but a softmax model given two published parts closes that gap at 512 tokens;
					the hybrid leads again, by 0.66% on three seeds, at 8,192.</span
				>
			</li>
			<li>
				<span
					>What mattered was composition. Softmax attention handed the perfect features still could
					not learn the relation; what it lacks is multiplication. A layer that multiplies learned
					rotations discovers the symmetry group of an icosahedron from yes/no labels alone.</span
				>
			</li>
			<li>
				<span
					>Forgetting order has an exact price. A layer whose operations commute has a provable
					accuracy ceiling on these tasks (77.23% on one of them), and layers with non-commuting
					rotations go past it.</span
				>
			</li>
			<li>
				<span
					>Composition still did not pay on language, nor when we re-weighted the loss, nor on
					ARC-style grid puzzles. The common thread: building the right structure into a layer is
					easy; getting gradient descent to find and use it is the hard part.</span
				>
			</li>
		</ol>
		<p>
			You need only a working idea of neural networks and training; everything else is built up as
			we go. Most figures are computed live in your browser and many respond to clicks. Each section
			says where its content comes from:
		</p>
		<ul class="legend">
			<li><span class="mark prior"></span>Prior work, with references</li>
			<li><span class="mark new"></span>New in this project</li>
			<li><span class="mark measured"></span>Measured, in the browser or on cloud GPUs</li>
		</ul>
		<p class="after-legend">
			Two other tabs hold larger interactive labs: <a href={resolve('/explore')}>Explore</a>, where
			you can inspect trained layers token by token, and <a href={resolve('/compare')}>Compare</a>,
			where you can train the models yourself.
		</p>
	</section>

	<section class="chapter" id="puzzles">
		<h3><span class="n">{number('puzzles')}</span>The puzzles</h3>
		<p class="src">
			<span class="mark prior"></span>SET is a published card game <Cite id="davis" />; pointer
			chasing and Match3 are standard tests <Cite id={['chakrabarti07', 'sanford']} />;
			<span class="mark new inline"></span>Match-<MathTex tex="k" /> beyond three and the other variants
			are new here
		</p>
		<p>
			Every experiment starts from small puzzles whose answers a program can check. They are
			generated fresh as training runs, so there is no fixed dataset: a model almost never sees the
			same puzzle twice, and it is always scored on puzzles it has not trained on. Each puzzle is
			built so that its answer depends on several pieces at once, and so that we know exactly how
			many. We call that number the <em>arity</em> of the relation.
		</p>
		<p>
			<strong>SET.</strong> SET is a card game. Each card has four attributes: how many symbols it
			shows (one, two or three), their shape (here spade, heart or club), their shading (solid,
			striped or open) and their colour (blue, green or purple). Every combination appears once, so
			the deck has <MathTex tex="3^4 = 81" /> cards. Three cards form a SET when, for every attribute
			separately, the three cards are either all the same or all different.
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
			The task deals twelve cards and asks, for every card, whether it belongs to at least one SET
			on the table: yes or no, per card. On a random table a little over half the cards, about 54%,
			are in some SET. No single card and no pair of cards settles the answer. It is a fact about
			three cards at once, which is what makes SET a useful test.
		</p>
		<p>
			<strong>Match-<MathTex tex="k" />.</strong> Write each attribute value as 0, 1 or 2. Then "all
			the same or all different" is the same as "the three values add up to a multiple of 3": 0 + 0
			+ 0, 1 + 1 + 1 and 0 + 1 + 2 do, and 0 + 0 + 1 does not. So a SET is three cards whose values
			add up to a multiple of 3 in every attribute. Match-<MathTex tex="k" /> asks the same question about
			groups of <MathTex tex="k" /> distinct cards. SET is Match-3. Match-4 and Match-5 deal nine cards,
			so that again about half the cards are positive. A related task, <em>smallest arity</em>, asks
			for the smallest group size, 3, 4 or 5, at which a card completes such a group, or "none".
		</p>
		<p>
			<strong>Pointer chasing.</strong> Twelve nodes form a few linked lists. Each node has an id, a pointer
			to the next node's id, and a payload, a number from 0 to 7; the last node of each list points to
			itself. A query names a start node, and the answer is the payload at the end of that node's list,
			zero to three hops away. Unlike SET, the answer needs a chain of lookups whose length changes from
			puzzle to puzzle.
		</p>
		<p>
			<strong>Three-hop composition.</strong> Three lookup tables <MathTex tex="f_1, f_2, f_3" /> each
			map the numbers 0 to 7 to 0 to 7, followed by a starting number <MathTex tex="x" />. The
			answer is <MathTex tex="f_3(f_2(f_1(x)))" />: always three lookups, in a fixed order.
		</p>
		<p>
			Later parts add puzzles built from other groups of operations, small programs and real text.
			Each is introduced where it is first used. The figure lets you look at one example of each
			puzzle above.
		</p>
		<div class="figure wide"><LearnFigure section="puzzles" /></div>
	</section>

	<section class="chapter" id="encoding">
		<h3><span class="n">{number('encoding')}</span>How a puzzle becomes tokens</h3>
		<p class="src">
			<span class="mark new"></span>This project's setup, the same in the browser and in the
			research harness
		</p>
		<p>
			A network does not see cards. It sees a sequence of <em>tokens</em>, each a list of numbers,
			and here every card is one token. Each of a card's four attribute values is written as a
			<em>one-hot</em> vector of length 4: a 1 in the slot for its value and 0 elsewhere, with a
			fourth slot no card uses. The four vectors side by side give 16 numbers per card. A learned
			linear map turns them into a vector of width <MathTex tex="d" /> (64 in the browser), and a learned
			vector for the token's position is added. The order of the cards carries no meaning; the network
			has to learn to ignore it.
		</p>
		<div class="figure wide"><LearnFigure section="encoding" /></div>
		<p>
			Position 0 holds one extra token that is not a card, the <em>sink</em>. It uses the unused
			fourth slot of every attribute, so it looks like no card. Attention must spend all of its
			weight somewhere (section {number('pairwise')} explains why), and the sink gives it a harmless place
			to put weight when nothing on the table fits.
		</p>
		<p>
			<strong>Training.</strong> On SET the network outputs, for every card, the probability that the
			card is in some SET. Training lowers the cross-entropy between those probabilities and the true
			labels, summed over the cards. Every step draws a fresh batch of 128 random tables from a seeded
			generator, so every model sees the same tables in the same order. The optimiser is AdamW. A browser
			run takes 4,000 steps; the cloud runs take 4,000 to 20,000.
		</p>
		<p>
			<strong>Scoring.</strong> After training, a model labels 1,024 tables it has never seen, drawn
			once with a different seed. Its <em>held-out accuracy</em> is the share of cards it labels
			correctly. The bar to beat is <em>chance</em>: the score of a model that ignores the table and
			always gives the more common answer, about 54% on SET. When the two answers are unevenly
			common, the cloud results report <em>balanced accuracy</em> instead, the average of the
			accuracy on positive and on negative cards, so that chance is exactly 50% and a model cannot
			look good by favouring one answer. Cloud results use three <em>seeds</em>: three independent
			runs with different initial weights and data, which show how much a result depends on luck.
		</p>
		<p>
			The other puzzles follow the same pattern. In pointer chasing, a node is one token holding its
			id, pointer and payload; the query is a last token holding only a pointer, and the network
			answers at the query by choosing one of eight payloads, so chance is 12.5%.
		</p>
	</section>
</section>

<style>
	.examples {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 12px 28px;
		margin-bottom: 18px;
	}
	.example {
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
		line-height: 1.45;
		color: var(--color-ink-3);
	}
	.after-legend {
		margin-top: 14px;
	}
	@media (max-width: 520px) {
		.examples {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
