<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import CompositionFigure from '#lib/learn/CompositionFigure.svelte';
	import { CHARACTER_ROWS } from '#lib/report/groupResults.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import { number } from '../toc.ts';

	const eq = {
		representation: String.raw`\rho(ab)=\rho(a)\,\rho(b)`,
		sectors: String.raw`F_r(i)=\sum_{\substack{s_1<\cdots<s_r\\i\in\{s_1,\ldots,s_r\}}} M_{s_1}M_{s_2}\cdots M_{s_r}`,
		polynomial: String.raw`\prod_{t=1}^{n}(I+zM_t)=\sum_{r=0}^{n}z^r E_r`,
		recurrence: String.raw`E_r(t)=E_r(t-1)+E_{r-1}(t-1)\,M_t`,
		readout: String.raw`F_r(i)=\sum_{a+b=r-1}L_a(i)\,M_i\,R_b(i)`
	};
</script>

<section class="part" id="part-turn">
	<header class="part-head">
		<span class="roman">Part VI</span>
		<h2>The turn: composition</h2>
		<p class="part-lede">
			Newton attention won on the puzzles. Was that because it found the right features, or because
			of what it does with them? Separating the two led to the main result of this project.
		</p>
	</header>

	<section class="chapter" id="coordinates">
		<h3><span class="n">{number('coordinates')}</span>Good coordinates are not enough</h3>
		<p class="src">
			<span class="mark new"></span>The experiment; <span class="mark measured inline"></span>cloud
			GPUs, three seeds, 6,000 steps (GROUPS §5.1)
		</p>
		<p>
			There are two ways to explain Newton attention's success. Maybe it only needed the right
			coordinates, the characters, and any layer given them would do as well. Or maybe the essential
			ingredient is the product it computes from them. We separated the two directly: give ordinary
			softmax attention every character of the card group in advance, as fixed input features, and
			see whether it can learn Match-4.
		</p>
		<p>
			Each card was fed in as the cosine and sine of all 40 character pairs, 80 numbers that never
			change during training. We trained softmax attention with an MLP, one or two layers of width
			192. Two controls: the same 80 numbers rotated into different coordinates, and ordinary
			learned embeddings. (A subtle point: the 80 character features are the card's one-hot code
			seen in a rotated basis, so the test really asks whether softmax can learn the multiplication
			when it is handed every ingredient.)
		</p>
		<p>
			Both depths finished at <strong>50.0% on Match-4 on every seed</strong>, exactly chance, and
			the same on Match-5. Training a two-layer model for 20,000 steps instead of 6,000 still gave
			50.0% on every seed. On Match-3 the character inputs did slightly worse than learned
			embeddings. Newton attention reaches 100% on Match-4.
		</p>
		<div class="figure wide"><CompositionFigure section="features" /></div>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr
						><th>Model</th>{#each ['Match-3', 'Match-4', 'Match-5'] as t (t)}<th class="num">{t}</th
							>{/each}</tr
					></thead
				>
				<tbody>
					{#each CHARACTER_ROWS as row (row.id)}
						<tr class:quiet={row.id === 'newton'}
							><th>{row.label}</th>{#each row.values as v, i (i)}<td class="num"
									>{v.display}{#if v.seeds}<small>{v.seeds}</small>{/if}</td
								>{/each}</tr
						>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Balanced accuracy %, mean with the three seeds below it. Newton attention is the earlier
			reference run, not a new arm of this experiment.
		</p>
		<p>
			This is a result about learning, not an impossibility theorem. A softmax layer that spreads
			its weight evenly can collect every character sum, and a wide enough MLP can then carry out
			Newton's identities on this finite set of cards; the computation exists inside the model
			class. Training did not find it. Newton attention supplies the multiplication directly, and
			that turned out to be the part that matters. The rest of the article follows this thread: <strong
				>the content of a "higher-order" layer is how it combines features, not how many tokens it
				touches.</strong
			>
		</p>
	</section>

	<section class="chapter" id="order">
		<h3><span class="n">{number('order')}</span>When order changes the answer</h3>
		<p class="src">
			<span class="mark prior"></span>Standard group theory;
			<span class="mark new inline"></span>the ordered Match-3 task
		</p>
		<p>
			Multiplying phases adds clock moves, and clock moves commute: the order of the cards never
			matters. Many structures are not like that. Take a triangle and label its corners A, B and C.
			Turning it a third of a turn, or flipping it across its vertical axis, returns the unlabelled
			triangle to the same outline, so both moves are <em>symmetries</em>. There are six such moves,
			including doing nothing, and they form a group. But watch the labels: turn then flip ends in a
			different arrangement from flip then turn. These operations do not commute; the group is
			<em>non-abelian</em>. Brackets still don't matter (associativity holds), but order does.
		</p>
		<div class="figure wide"><CompositionFigure section="order" /></div>
		<p>
			To test this, we built <em>ordered Match-3</em>. Every token names an operation from a group.
			A token is positive when it sits in some three positions whose operations, applied in sequence
			order, add up to doing nothing; we write that as <MathTex tex="abc = e" />, with <MathTex
				tex="e"
			/> the identity. We used four groups, two of each kind and two of each size: the clocks <MathTex
				tex={String.raw`\mathbb Z_{12}`}
			/> and <MathTex tex={String.raw`\mathbb Z_{60}`} />, where order cannot matter, and <MathTex
				tex="A_4"
			/> and <MathTex tex="A_5" />, the 12 rotations of a tetrahedron and the 60 rotations of an
			icosahedron, where it can. The small groups use sequences of six tokens, the large ones
			eleven. Reversing an <MathTex tex="A_5" /> sequence changes 46% of its labels; reversing a <MathTex
				tex={String.raw`\mathbb Z_{60}`}
			/> sequence changes none.
		</p>
	</section>

	<section class="chapter" id="representations">
		<h3><span class="n">{number('representations')}</span>Operations as rotations</h3>
		<p class="src">
			<span class="mark prior"></span>Standard representation theory; learned group algorithms <Cite
				id="chughtai"
			/>
		</p>
		<p>
			A clock move can be stored as a rotation of the plane, and multiplying rotations then does the
			same as combining moves. That is a <em>representation</em>: an assignment of a matrix
			<MathTex tex={String.raw`\rho(g)`} /> to each operation <MathTex tex="g" /> such that multiplying
			matrices agrees with combining operations,
		</p>
		<MathTex display tex={eq.representation} />
		<p>
			A representation is <em>faithful</em> if different operations get different matrices, so it
			loses nothing. It is <em>irreducible</em>, an <em>irrep</em> for short, if no change of coordinates
			splits it into smaller independent blocks; irreps are the building blocks every other representation
			is made of. The phases of Part IV were exactly the irreps of a commuting group, two-dimensional
			rotations in disguise.
		</p>
		<p>
			Rotations in the plane always commute. Rotations in three dimensions do not: turn a book a
			quarter about one axis and then another, and compare with the reverse. That gives room to
			represent operations whose order matters. <MathTex tex="A_4" /> and <MathTex tex="A_5" /> are literally
			groups of three-dimensional rotations, so each has a faithful representation by 3×3 rotation matrices;
			<MathTex tex="A_5" /> in fact has two different ones, plus irreps of dimension 4 and 5. Step through
			the 60 rotations of the icosahedron below.
		</p>
		<div class="figure wide"><CompositionFigure section="representations" /></div>
		<p>
			The models in the next sections receive only token identities and yes/no labels, never these
			matrices. The question is whether what they learn obeys the same multiplication rule.
		</p>
	</section>

	<section class="chapter" id="holonomy">
		<h3><span class="n">{number('holonomy')}</span>Holonomy attention</h3>
		<p class="src">
			<span class="mark prior"></span>Ordered subsequence sums <Cite id="seq2tens" />, learned group
			products <Cite id="development" />, orthogonal parameterisation <Cite id="orthogonal" />;
			<span class="mark new inline"></span>the gated, per-token, per-size read-out studied here
		</p>
		<p>
			<em>Holonomy attention</em> is Newton attention with rotations in place of phases. In every
			head, each token gets a learned rotation matrix <MathTex tex="U" /> and a gate <MathTex
				tex="g"
			/>
			between 0 and 1 that sets how strongly it takes part; write <MathTex tex="M = gU" />. To
			relate a group of tokens, multiply their matrices <em>in the order they appear</em>. To read
			token
			<MathTex tex="i" />, add up those ordered products over every group that contains it, keeping
			each group size separate:
		</p>
		<MathTex display tex={eq.sectors} />
		<p>
			The figure spells it out for four tokens read at b: every term contains B, every product keeps
			the tokens' left-to-right order, and each row collects the groups of one size. A learned
			read-out turns these sums into features for the rest of the network, exactly as in Newton
			attention. The rotations come from exponentiating a learned skew-symmetric matrix, a standard
			way to keep them rotations throughout training.
		</p>
		<div class="figure wide"><CompositionFigure section="holonomy" /></div>
		<p>
			Two facts make it the natural next layer. With 2×2 rotations, every matrix commutes and the
			layer is exactly Newton attention (we checked this numerically to <MathTex
				tex={String.raw`2 \times 10^{-16}`}
			/>). With 3×3 or larger rotations, the products can keep track of order, without any position
			embeddings: order enters only through the products. The name comes from geometry, where
			carrying a frame around a path accumulates a rotation called the holonomy.
		</p>
		<details class="more">
			<summary>How it avoids listing every group</summary>
			<p>
				A bookkeeping variable <MathTex tex="z" /> records group size. In the product below, choosing
				<MathTex tex="I" /> skips a token and choosing <MathTex tex="zM" /> includes it, so the coefficient
				<MathTex tex="E_r" /> holds every size-<MathTex tex="r" /> product in order:
			</p>
			<MathTex display tex={eq.polynomial} />
			<p>Processing one token at a time gives a running update:</p>
			<MathTex display tex={eq.recurrence} />
			<p>
				For a marked token <MathTex tex="i" />, run it from both ends: <MathTex tex="L_a(i)" /> holds
				the products of <MathTex tex="a" /> tokens before <MathTex tex="i" />, and <MathTex
					tex="R_b(i)"
				/> of
				<MathTex tex="b" /> tokens after it. Then
			</p>
			<MathTex display tex={eq.readout} />
			<p>
				The cost is <MathTex tex="O(nK^2Hd^3)" /> for <MathTex tex="n" /> tokens, largest size <MathTex
					tex="K"
				/>, <MathTex tex="H" /> heads and <MathTex tex="d \times d" /> matrices. Each size is divided
				by its number of groups and rescaled before the shared read-out. It is a real computation across
				the sequence, not a constant-time trick.
			</p>
		</details>
	</section>
</section>
