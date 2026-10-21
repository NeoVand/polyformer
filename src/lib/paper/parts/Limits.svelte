<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import ArcFigure from '../ArcFigure.svelte';
	import DilutionFigure from '../DilutionFigure.svelte';
	import LanguageFigure, { COMBINED } from '../LanguageFigure.svelte';
	import { number } from '../toc.ts';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	// final held-out loss, nats per token (research/BEYOND_REPORT.md); the study was stopped
	// before the recurrent networks' second seed and every arm's third seed finished
	const losses = [
		{ label: 'Softmax', s1: '3.6616', s2: '3.6492' },
		{ label: 'Softmax + short convolution', s1: '3.6126', s2: '3.6094' },
		{ label: 'Parallax + short convolution', s1: '3.6072', s2: '3.5981' },
		{ label: 'Combined layer B', s1: '3.6424', s2: '3.6355' },
		{ label: 'Gated DeltaNet', s1: '3.5758', s2: 'stopped' },
		{ label: 'Gated DeltaProduct', s1: '3.5648', s2: 'stopped' }
	];
</script>

<section class="part" id="part-limits">
	<header class="part-head">
		<span class="roman">Part VIII</span>
		<h2>Where composition does not pay</h2>
		<p class="part-lede">
			By now we had three ingredients that each helped somewhere: selection, a better estimate, and
			order-keeping composition. Three final studies asked whether they add up to something useful
			outside the puzzles. All three said no, and each says something about why.
		</p>
	</header>

	<section class="chapter" id="combined">
		<h3><span class="n">{number('combined')}</span>One layer with everything</h3>
		<p class="src">
			<span class="mark new"></span>The combinations; <span class="mark prior inline"></span>their
			components <Cite id={['parallax', 'path', 'gdn', 'deltaproduct']} />;
			<span class="mark measured inline"></span>pre-registered screen and language comparison
			(BEYOND)
		</p>
		<p>
			The idea was to keep softmax for selection, add Parallax's correction for a better estimate,
			and add rotations for composition, then compare the result with both softmax and the strongest
			modern recurrent networks at the same compute. All three designs used small 5×5 rotations,
			each built from four learned reflections per token, multiplied along the sequence. They
			differed in how the parts meet. Design A carries each selected value through the rotation
			between its position and the reader's, close to the published PaTH attention <Cite
				id="path"
			/>. Design B runs the rotation branch beside attention and adds the two. Design C lets
			attention steer the rotations.
		</p>
		<p>
			<strong>The screen.</strong> Before any language run, each design had to match softmax on
			retrieval and induction and match a recurrent reader on <MathTex tex="A_5" /> and <MathTex
				tex="S_5"
			/> tracking, on three fresh seeds. All three were perfect on the seed used for tuning. On fresh
			seeds, A failed four of its <MathTex tex="S_5" /> cells, with scores as low as 1.7%, and C failed
			two-layer <MathTex tex="S_5" /> on all three (3.3%, 6.8% and 1.6%). Only B passed all 18 cells.
			The failures were failures to learn, visible across whole training curves: another case of a computation
			the layer can express but training does not reliably find.
		</p>
		<p>
			A side result changed the baselines. Plain softmax could not learn to retrieve the value
			stored under a key within the screen's budget (about 10%, chance level), while Gated DeltaNet
			reached 99.7%. A short causal convolution on the queries, keys and values, a known
			modification <Cite id="primer" />, fixed it, so every attention model in the language
			comparison got the same convolution.
		</p>
		<p>
			<strong>Language.</strong> B then went through the same FineWeb-Edu protocol as Part V, with Muon,
			against five controls, each given at least B's compute.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<LanguageFigure groups={COMBINED} />
				<figcaption>
					Change in held-out loss against softmax with the short convolution; lower is better. Small
					numbers are the seeds completed before we stopped the study: two for the attention models,
					one for the recurrent networks.
				</figcaption>
			</figure>
		</div>
		<div class="table-scroll">
			<table class="bt">
				<thead><tr><th>Model</th><th class="num">Seed 1</th><th class="num">Seed 2</th></tr></thead>
				<tbody>
					{#each losses as r (r.label)}
						<tr><th>{r.label}</th><td class="num">{r.s1}</td><td class="num">{r.s2}</td></tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Final held-out loss in nats per token, about 400M tokens. Parameter counts are not matched:
			the DeltaProduct model has 33M non-embedding parameters against softmax's 19M.
		</p>
		<p>
			B lost to softmax with the convolution by 0.8% and 0.7%, and to Parallax with the convolution
			as well. Switching off its composition branch on the trained model raised the loss by only
			0.035 to 0.038 nats, while switching off the estimation correction raised it by 1.8 to 1.9:
			the model uses both, but the composition part contributes little.
		</p>
		<p>
			Two findings stand out more than B itself. The short convolution, a tiny local mixing step,
			was worth 1.1% to 1.3% to softmax, more than any change to attention in this project. And on
			the one seed that finished, the two recurrent networks, which compose matrices along the
			sequence, had the lowest losses of all: 1.0% and 1.3% below convolved softmax, at slightly
			more compute and with more parameters. That is a single seed, and we stopped before confirming
			it. But it is the one place in this project where composition paid on language, and it paid as
			recurrence, not as attention.
		</p>
	</section>

	<section class="chapter" id="dilution">
		<h3><span class="n">{number('dilution')}</span>Is the loss hiding it?</h3>
		<p class="src">
			<span class="mark new"></span>The task and test;
			<span class="mark measured inline"></span>three seeds, predictions committed first (NEXT,
			experiment 1)
		</p>
		<p>
			One explanation for the language results is about measurement, not layers. Ordinary training
			loss averages over every token, and the tokens whose prediction depends on tracking state are
			rare. If composition helps a lot on those few tokens, the average could hide it.
		</p>
		<p>
			We tested this on generated stories in which objects change hands: transfers, aliases,
			revocations and overwrites, 8 to 32 operations long, ending with a question about who holds an
			object. Stories come in pairs that differ in one early operation and have different answers,
			and a model gets a pair right only if it answers both. Two models (softmax with the
			convolution, and the same with the composition branch) were trained in two ways: with ordinary
			loss on every token, and with the loss placed only on the final answer.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<DilutionFigure />
				<figcaption>
					Paired accuracy: both stories of a pair answered correctly. Three-seed means. The dashed
					line is a shortcut that ignores everything after the first owner.
				</figcaption>
			</figure>
		</div>
		<p>
			The dilution is real. The answers are 0.5% to 1.7% of the tokens, and with ordinary loss both
			models learn the narration perfectly well while staying at chance on the answer (0.9% paired
			accuracy). Putting the loss on the answer lifts both. But softmax gains more than the
			composition model (17.6% against 13.9% on held-out stories), both stop near the shortcut of
			guessing the first owner, and switching off the composition branch changes its score by 0.13
			points. The loss was hiding the task; it was not hiding a composition advantage.
		</p>
	</section>

	<section class="chapter" id="arc">
		<h3><span class="n">{number('arc')}</span>Grid puzzles in the style of ARC</h3>
		<p class="src">
			<span class="mark prior"></span>The ARC benchmark <Cite id="chollet" />;
			<span class="mark new inline"></span>the algebraic version;
			<span class="mark measured inline"></span>three seeds (NEXT, experiment 2)
		</p>
		<p>
			ARC is a benchmark of grid puzzles: from a few input–output examples, infer the rule and apply
			it to a new grid. Many ARC rules are compositions of symmetries, recolourings and moves, which
			made it look like natural ground for composition. We built a clean version: 6×6 grids, a
			hidden rule made of one to four moves (quarter turns, mirrors, cyclic slides, recolourings),
			three examples and one test. A harder tier added moves that cannot be undone, such as
			cropping, gravity and filling. Try one:
		</p>
		<div class="figure wide">
			<figure class="pf">
				<ArcFigure />
				<figcaption>
					Top: a puzzle from the same kind of generator, in greys. Bottom: exact-grid accuracy on
					the invertible tier, three-seed means. "Solver" infers the rule from the three examples in
					closed form.
				</figcaption>
			</figure>
		</div>
		<p>
			Softmax with and without test-time training on the examples, and the same model with the
			composition branch, all scored the same to within one puzzle: 24.5%, 15.1%, 11.5% and 2.6% for
			one to four moves. The reason is exact. The tasks they solved are precisely the tasks whose
			moves cancel out spatially, leaving only a recolouring, which attention can copy cell by cell.
			They solved none of the tasks that actually move the grid. A solver that works out the
			operator from the three examples solved 100% at every depth. On a single fixed quarter turn,
			the composition branch even hurt (0% against 61%): it reads the grid as a one-dimensional
			sequence of cells, the wrong shape for an operation that moves the whole grid at once. The
			irreversible tier stayed at 13% or less.
		</p>
		<p>
			The examples contain all the information needed. What the trained models lack is a way to
			infer an operator from examples and then apply it, and our composition layer does not provide
			one.
		</p>
		<p class="foot">
			Full protocols and per-seed tables:
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/BEYOND_REPORT.md`}>BEYOND_REPORT</a>
			and
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/NEXT.md`}>NEXT</a>.
		</p>
	</section>
</section>
