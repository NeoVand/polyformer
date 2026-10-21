<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import CompositionFigure from '#lib/learn/CompositionFigure.svelte';
	import GroupLadder from '#lib/report/GroupLadder.svelte';
	import { GROUP_ROWS, SWAP_ROWS } from '#lib/report/groupResults.ts';
	import Theorem from '#lib/report/Theorem.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import A5Figure from '../A5Figure.svelte';
	import { number } from '../toc.ts';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	const bayes = String.raw`\mathrm{BA}\le B^*=\frac12+\frac{\mathbb E\,|p(O)-\pi|}{4\pi(1-\pi)}`;

	// three-seed means from research/results/wp_main.jsonl, as rounded in GROUPS §7
	const wordRows = [
		{ label: 'Holonomy attention', scores: ['100.0', '100.0', '99.8', '98.4'], hi: true },
		{ label: 'Householder RNN', scores: ['98.9', '100.0', '99.9', '100.0'] },
		{ label: 'Orthogonal RNN', scores: ['100.0', '100.0', '71.4', '29.3'] },
		{ label: 'Newton attention (commuting)', scores: ['17.5', '5.5', '12.3', '4.5'] },
		{ label: 'Softmax, 1 layer', scores: ['14.0', '4.7', '7.3', '2.8'] },
		{ label: 'Softmax, 2 layers', scores: ['14.0', '4.8', '7.2', '2.4'] },
		{ label: 'DeltaProduct (minimal)', scores: ['14.2', '4.8', '10.4', '3.5'] }
	];
	const wordTasks = ['A₅ · 16', 'A₅ · 64', 'S₅ · 16', 'S₅ · 64'];
</script>

<section class="part" id="part-results">
	<header class="part-head">
		<span class="roman">Part VII</span>
		<h2>What each kind of layer can learn</h2>
		<p class="part-lede">
			Three kinds of layer, three ways of combining: softmax averages, Newton attention multiplies
			commuting phases, holonomy attention multiplies rotations in order. Here is what each one
			learns when order matters, what can be proved, and two harder tests.
		</p>
	</header>

	<section class="chapter" id="ceiling">
		<h3><span class="n">{number('ceiling')}</span>The price of forgetting order</h3>
		<p class="src">
			<span class="mark new"></span>The bound and its exact values (THEORY §§2–3);
			<span class="mark measured inline"></span>three seeds, 6,000 steps (GROUPS §5.2)
		</p>
		<p>
			A layer whose operations commute sees each token together with the collection of other tokens,
			but not their order. On ordered Match-3 over a non-abelian group, two sequences can contain
			the same tokens in different orders and still have different answers, and such a layer cannot
			tell them apart. However large the network after it, its accuracy has a ceiling. We call it
			the
			<em>order-blind ceiling</em>, and it can be computed exactly: <strong>83.05%</strong> on the
			<MathTex tex="A_4" /> task and <strong>77.23%</strong> on the <MathTex tex="A_5" /> task.
		</p>
		<p>
			Why so far above 50%? Because order does not always matter. If <MathTex tex="abc = e" />, then
			also <MathTex tex="bca = e" /> and <MathTex tex="cab = e" />: rotating a triple keeps it a
			solution. And three operations that happen to commute with each other work in every order. An
			order-blind layer can exploit all of that, and nothing more.
		</p>
		<p>
			The measurements land exactly where this predicts. Newton attention and two-dimensional
			holonomy attention reach 80.7% and 81.1% on <MathTex tex="A_4" />, and 76.1% and 73.1% on <MathTex
				tex="A_5"
			/>: at or under their ceilings. With 3×3 rotations, holonomy attention goes straight past:
			100% on <MathTex tex="A_4" />, and on <MathTex tex="A_5" /> 94.1%, 99.5% and 100.0% with rotations
			of size 3, 4 and 5. On the clock groups every Newton and holonomy layer is exact, as it should be.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<GroupLadder />
				<figcaption>
					Balanced accuracy, three-seed means at 6,000 steps. The dashed line is the exact
					order-blind ceiling for that task, computed in advance, not fitted. Softmax has position
					embeddings, so the ceiling does not bind it.
				</figcaption>
			</figure>
		</div>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr
						><th>Model</th>{#each ['Z₁₂', 'A₄', 'Z₆₀', 'A₅'] as g (g)}<th class="num">{g}</th
							>{/each}</tr
					></thead
				>
				<tbody>
					{#each GROUP_ROWS as row (row.id)}
						<tr
							><th>{row.label}</th>{#each row.values as v, i (i)}<td class="num"
									>{v.display}{#if v.seeds}<small>{v.seeds}</small>{/if}</td
								>{/each}</tr
						>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Balanced accuracy %, mean with seeds. Holonomy d = 5 on A₅ rounds to 100.0; its seeds are
			99.97, 99.96 and 99.98.
		</p>
		<p>
			Softmax attention, which has positions and so could in principle use order, tells a different
			story. On the 60-element groups it stays at chance with one layer or three, <em
				>even on the commuting clock group</em
			>, where every phase or rotation layer is exact. On the small groups, six tokens over twelve
			elements, three softmax layers learn to read the whole sequence and reach 99.7–100%: a
			small-universe effect, not composition.
		</p>
	</section>

	<section class="chapter" id="learned">
		<h3><span class="n">{number('learned')}</span>The heads learn the group</h3>
		<p class="src">
			<span class="mark measured"></span>Diagnostics of trained heads, GROUPS §5.2; longer runs are
			exploratory
		</p>
		<p>
			We can open up a trained head and test it directly. Take its learned matrix for <MathTex
				tex="a"
			/>, multiply it by its matrix for <MathTex tex="b" />, and compare with its matrix for
			<MathTex tex="ab" />. Averaged over every pair of elements, that mismatch is the
			<em>composition error</em>: 0 means the head is an exact representation, and random rotations
			sit near 1.4. A second test compares each head's traces (the sums of their diagonals) with the
			known traces of each irrep, which identifies which irrep a head holds.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr><th>Group</th><th>d = 2</th><th>d = 3</th><th>d = 4</th><th>d = 5</th></tr></thead
				>
				<tbody>
					<tr
						><th>A₄</th><td>none; 1′, 1″; 1′, 1″</td><td>3; 3; 3</td><td>3; none; 3</td><td
							>none (×3)</td
						></tr
					>
					<tr
						><th>A₅</th><td>none (×3)</td><td>3, 3′; 3, 3′; 3, 3′</td><td>3′; 4; 3, 4</td><td
							>5; 5; 4, 5</td
						></tr
					>
				</tbody>
			</table>
		</div>
		<p class="caption">
			Irreps found in heads with composition error below 0.5, per seed (irreps are named by their
			dimension). "None" can miss structure in heads whose gates switch some elements off.
		</p>
		<p>
			From nothing but yes/no labels, the heads become the groups' irreducible representations. With
			3×3 matrices on <MathTex tex="A_5" />, every seed found both three-dimensional irreps, the two
			ways of writing the icosahedron's rotations, with composition errors as low as 0.05. With
			larger matrices the heads tend to take the largest irrep that fits: dimension 4 or 5. On <MathTex
				tex="A_4"
			/> with 2×2 matrices, the heads find only the irreps 1′ and 1″, which are all a commuting layer
			can hold: they see <MathTex tex="A_4" /> through its quotient, a three-position clock.
		</p>
		<p>
			Below, a trained head is shown beside the ideal rotations. Pick any of the 60 elements: the
			two icosahedra move together. The head's matrices are only aligned to the ideal ones by a
			single change of axes for the whole group, with no per-element correction.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<A5Figure />
				<figcaption>
					The 60 rotations of the icosahedron: computed from the group's multiplication table (left)
					and learned by head 80 of a model trained only to answer ordered Match-3 (right). The
					solid dot tracks one vertex. More views in the <a href={resolve('/explore/groups')}
						>rotation lab</a
					>.
				</figcaption>
			</figure>
		</div>
		<p>
			How small can the rotations be? The smallest faithful representation of <MathTex tex="A_5" /> has
			dimension 3, and with it holonomy attention reached 94.1% at 6,000 steps, between the two thresholds
			we had registered for this question. In exploratory runs of 20,000 steps it reached 99.21%, 99.38%
			and 99.34%. We had predicted that accuracy would track the share of the group's "Fourier mass" a
			head can hold, which is only 31% for dimension 3. That prediction was wrong: a faithful representation
			is enough, and larger ones only learn faster.
		</p>
	</section>

	<section class="chapter" id="theory">
		<h3><span class="n">{number('theory')}</span>What is proved</h3>
		<p class="src">
			<span class="mark new"></span>Task-specific theorems with stated conditions; full statements
			in
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/THEORY.md`}>THEORY</a>, numerical checks in
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/results/theory_checks.json`}>theory_checks</a>
		</p>
		<p>
			Three results make the picture precise. They draw the line between <em
				>position-free layers that compose commutingly</em
			> and layers that keep the order that matters; they do not separate every softmax network from every
			holonomy network. Each statement opens to a proof sketch.
		</p>
		<Theorem n="1" name="Losing order has an exact price" evidence="proved">
			<p>
				If a predictor sees only the marked token and the unordered collection of the other tokens,
				its balanced accuracy is at most the order-blind ceiling. More width or a bigger classifier
				cannot recover discarded order.
			</p>
			{#snippet proof()}
				<p>
					Let <MathTex tex="O" /> be that order-blind observation, <MathTex tex="p(O)" /> the probability
					of a positive label given it, and <MathTex tex={String.raw`\pi`} /> the overall positive rate.
					The best prediction says yes exactly when <MathTex tex={String.raw`p(O) \ge \pi`} />,
					which gives
				</p>
				<MathTex tex={bayes} display />
				<p>
					For Match-3, fixing the marked element gives every other element a unique partner that
					would complete a solution if it came later; counting the orderings that avoid every such
					pair gives the exact conditional probability, and an integer dynamic program sums it to
					the two ceilings. The <MathTex tex="A_4" /> value also matches brute force over all 2,985,984
					sequences. The bound applies to one position-free Newton layer and to commuting holonomy heads
					with token-only gates; it does not apply once positions, causal masks or an earlier order-aware
					layer reveal the order.
				</p>
			{/snippet}
		</Theorem>
		<Theorem n="2" name="Faithful rotations are enough for Match-3" evidence="proved">
			<p>
				A faithful orthogonal representation, enough token-gated heads, and a wide enough read-out
				represent ordered Match-3 exactly at any fixed length. For <MathTex tex="A_4" /> and <MathTex
					tex="A_5"
				/>, 3×3 rotations suffice.
			</p>
			{#snippet proof()}
				<p>
					Pair each rotation head with an identity-matrix head that has the same gates. Different
					positive gate values separate candidate triples by their contents. For a fixed triple of
					elements, the orders that succeed have trace <MathTex tex="d" />, and the orders that fail
					share a smaller trace; the identity heads count candidates, so traces and counts together
					recover the exact number of successes. For a group of size <MathTex tex="m" />, at most
					<MathTex tex="(m+1)(m+2)" /> heads suffice, with gates from ¼, ½ and ¾. A hand-built version
					makes no errors on 64 test sequences for each group.
				</p>
			{/snippet}
		</Theorem>
		<Theorem kind="Corollary" n="3" name="Faithful is more than necessary" evidence="proved">
			<p>
				For heads that are exact representations, given enough gated copies and a wide read-out,
				exact Match-3 is possible if and only if the heads together keep every non-commuting pair
				non-commuting: whenever <MathTex tex="ab \ne ba" />, some head must tell the two orders
				apart.
			</p>
			{#snippet proof()}
				<p>
					If every head makes <MathTex tex="a" /> and <MathTex tex="b" /> commute, the triples
					<MathTex tex={String.raw`(a, b, (ab)^{-1})`} /> and <MathTex
						tex={String.raw`(b, a, (ab)^{-1})`}
					/> look identical to every head while their labels differ. Conversely, the counting construction
					of Theorem 2 only needs to separate the two orders of each order-sensitive triple. A representation
					of
					<MathTex tex={String.raw`A_5 \times \mathbb Z_3`} /> that ignores the <MathTex
						tex={String.raw`\mathbb Z_3`}
					/> factor is not faithful, yet it keeps every non-commuting pair, so it suffices.
				</p>
			{/snippet}
		</Theorem>
		<p>
			<strong>What is not claimed.</strong> Softmax can represent these tasks. At a fixed length, a softmax
			layer with positions and enough heads and width can recover the whole ordered sequence and represent
			any labelling of it; for commuting groups, even a position-free one can carry every character and
			leave Newton's identities to the MLP. So the claim is not "softmax cannot compose". It is about
			what training finds with realistic resources, and there the measurements speak.
		</p>
	</section>

	<section class="chapter" id="programs">
		<h3><span class="n">{number('programs')}</span>Running small programs</h3>
		<p class="src">
			<span class="mark new"></span>The task; <span class="mark measured inline"></span>predictions
			committed before the three-seed grid (GROUPS §8)
		</p>
		<p>
			A second test with a familiar feel. Start with four variables holding 0, 1, 2 and 3. An
			instruction swaps the contents of two variables. Interleave the instructions of two
			independent three-swap programs, then ask for one variable's final value. The model must pick
			out the relevant instructions and apply them in order: knowing which swaps happened is not
			enough, as the figure shows.
		</p>
		<div class="figure wide"><CompositionFigure section="programs" /></div>
		<div class="table-scroll">
			<table class="bt">
				<thead><tr><th>Model</th><th class="num">Balanced accuracy %</th></tr></thead>
				<tbody>
					{#each SWAP_ROWS as row (row.id)}
						<tr
							><th>{row.label}</th><td class="num"
								>{row.result.display}<small>{row.result.seeds}</small></td
							></tr
						>
					{/each}
					<tr class="quiet"
						><th>Exact order-blind ceiling</th><td class="num">62.04 (= 67/108)</td></tr
					>
				</tbody>
			</table>
		</div>
		<p class="caption">Mean with the three seeds. Swap programs, six instructions, one query.</p>
		<p>
			The commuting layers land on their exact ceiling again. Holonomy attention with 3×3 or 4×4
			rotations solves the task, but so does a recurrent network that carries a rotation matrix
			along the sequence, and so does softmax with positions (98.95% with one layer, 100% with two
			or three). This test confirms the cost of forgetting order and shows <em>no advantage</em> over
			order-aware models. With only three relevant instructions, it is also a small, finite problem.
		</p>
	</section>

	<section class="chapter" id="word-problems">
		<h3><span class="n">{number('word-problems')}</span>Long products: word problems</h3>
		<p class="src">
			<span class="mark measured"></span>294 runs, predictions committed before the main grid
			(GROUPS §7); <span class="mark prior inline"></span>state tracking <Cite
				id={['automata', 'deltaproduct']}
			/>
		</p>
		<p>
			The hardest test asks for the running product. The model reads a sequence of operations from
			<MathTex tex="A_5" /> or <MathTex tex="S_5" /> (all 120 permutations of five objects) and, at every
			position, names the product so far: one of 60 or 120 answers. This is a classic
			<em>word problem</em>, and for these two groups it is provably hard for fixed-depth softmax
			transformers under standard complexity assumptions <Cite id="automata" />. It is also the home
			ground of recurrent networks that multiply matrices along the sequence, such as DeltaProduct <Cite
				id="deltaproduct"
			/>.
		</p>
		<div class="table-scroll">
			<table class="bt" aria-label="Word-problem class accuracy">
				<thead
					><tr
						><th>Model</th>{#each wordTasks as t (t)}<th class="num">{t}</th>{/each}</tr
					></thead
				>
				<tbody>
					{#each wordRows as row (row.label)}
						<tr class:hi={row.hi}
							><th>{row.label}</th>{#each row.scores as s, i (i)}<td class="num">{s}</td>{/each}</tr
						>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Balanced accuracy %, every position, three-seed means; lengths 16 and 64. One layer, width 64,
			6,000 steps at length 16 and 12,000 at 64. The comparisons are not matched for parameters or
			compute. "DeltaProduct (minimal)" is a small re-implementation without the published short
			convolution, not a test of the method.
		</p>
		<p>
			<strong>The predicted limits held.</strong> Rotations track <MathTex tex="A_5" /> with 3×3 matrices
			and <MathTex tex="S_5" /> with 5×5 (or 4×4 with reflections). Newton attention stays under its commuting
			ceiling. One- and two-layer softmax manage only 0.8–1.7% in the second half of each sequence, and
			a second layer rescued none of the failing models.
		</p>
		<p>
			<strong>The surprise was learning speed.</strong> The full-length product inside holonomy
			attention is already a recurrent network with a rotation-matrix state. Given 20,000-step
			amendment runs, that recurrence alone reaches 100.0% at length 16 and 99.4% at 64 on <MathTex
				tex="S_5"
			/>. So the short products help it learn faster and more reliably within the budget, with no
			demonstrated capacity gain. Householder updates learn <MathTex tex="S_5" /> faster still.
		</p>
		<p>
			<strong>Some predictions failed.</strong> On a yes/no variant of the task, an available
			representation did not guarantee learning: <MathTex tex="A_5" /> holonomy with 3×3 rotations reached
			only 63.0% at length 16, while exploratory 4×4 runs reached 100.0%.
			<strong>Length generalisation held:</strong>
			trained at 16 and tested at 64, <MathTex tex="S_5" /> holonomy reached 97.3% (99.7, 96.9, 95.3),
			the Householder network 98.2%.
		</p>
	</section>
</section>
