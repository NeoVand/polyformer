<script lang="ts">
	import { resolve } from '$app/paths';
	import Cite from '#lib/learn/Cite.svelte';
	import CompositionFigure from '#lib/learn/CompositionFigure.svelte';
	import LearnFigure from '#lib/learn/LearnFigure.svelte';
	import { number } from '../toc.ts';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	const notes = [
		{ file: 'research/SEARCH.md', what: 'the staged language search, S0–S2' },
		{ file: 'research/LOCAL.md', what: 'local-linear attention and Parallax, S6' },
		{ file: 'research/FORMALISM.md', what: 'subset attention and the walk sector' },
		{ file: 'research/GROUPS.md', what: 'groups, word problems and swap programs' },
		{ file: 'research/THEORY.md', what: 'the theorems and exact ceilings' },
		{ file: 'research/PRIOR_ART.md', what: 'the verified literature audit' },
		{ file: 'research/BEYOND_REPORT.md', what: 'the combined layers' },
		{ file: 'research/NEXT.md', what: 'loss dilution and algebraic ARC' }
	];
</script>

<section class="part" id="part-lessons">
	<header class="part-head">
		<span class="roman">Part IX</span>
		<h2>What we learned</h2>
	</header>

	<section class="chapter" id="lessons">
		<h3><span class="n">{number('lessons')}</span>Finding structure is the hard part</h3>
		<p class="src"><span class="mark new"></span>Our synthesis of the evidence</p>
		<p>
			The project set out to give attention more than pairs. What it found is better stated in terms
			of combining than counting. Softmax attention compares and averages. Newton attention
			multiplies phases, which adds clock moves and forgets their order. Holonomy attention
			multiplies rotations, which keeps it. On tasks built from a group, that choice sets what a
			layer can learn: commuting layers stop at an exact, computable ceiling, and layers that
			multiply rotations go past it by learning the group's own representations, from nothing but
			yes/no labels.
		</p>
		<div class="figure wide"><CompositionFigure section="principles" /></div>
		<p>
			Underneath that result runs a second thread, and it appears in every part of the story. The
			hard step was almost never representing the right structure. It was getting training to find
			it.
		</p>
		<ul class="list">
			<li>
				Feynman attention could represent the four-way term Match-4 needs and never found it
				(section
				{number('composition')}).
			</li>
			<li>
				Newton attention is exact precisely when it has found every character, and otherwise its
				accuracy grows in step with how many it has (section {number('newtonattn')}).
			</li>
			<li>
				Softmax handed every character could, in principle, compute the answer, and stayed at chance
				(section {number('coordinates')}).
			</li>
			<li>
				The smallest faithful rotations learn <em>A</em><sub>5</sub> fully, only more slowly; short
				products made long ones easier to learn (sections {number('learned')} and {number(
					'word-problems'
				)}).
			</li>
			<li>
				Two of three combined layers solved every task on one seed and failed on fresh ones (section
				{number('combined')}).
			</li>
			<li>
				With the loss on the answer, both models still stopped at a shortcut (section {number(
					'dilution'
				)}).
			</li>
			<li>
				On ARC-style grids, the trained models solved none of the tasks that move the grid, while a
				solver that infers the operator from the examples solved all of them (section {number(
					'arc'
				)}).
			</li>
		</ul>
		<p>
			Seen this way, the language results stop looking like a separate failure. At our scale, text
			rewards the things that are easy to find, nearby tokens and pairwise matches, and the few
			gains we measured came from exactly those (a short convolution, a better local estimate). The
			structure our layers could represent was either rare in the data or too hard to discover, and
			we cannot yet tell which.
		</p>
	</section>

	<section class="chapter" id="next">
		<h3><span class="n">{number('next')}</span>What we would try next</h3>
		<p class="src"><span class="mark new"></span>Open directions</p>
		<ol class="list">
			<li>
				<strong>Finish the recurrent comparison.</strong> The one sign of composition paying on
				language came from matrix-state recurrent networks, on a single seed (section {number(
					'combined'
				)}). Two more seeds, at matched parameters as well as compute, would settle whether it is
				real.
			</li>
			<li>
				<strong>Infer operators from examples.</strong> Parallax-style layers fit a small linear model
				to the context. The ARC result suggests fitting a transformation instead: estimate the operator
				that maps each example input to its output, then apply it to the query. The closed-form solver
				shows the information is there.
			</li>
			<li>
				<strong>Select, then compose.</strong> Real programs interleave relevant and irrelevant steps.
				Layers that choose which operations to compose by content, tested on longer programs against matrix
				recurrences and positional softmax, are the natural next experiment.
			</li>
			<li>
				<strong>Go larger.</strong> Higher-order attention has been reported to help at billions of
				parameters on reasoning and code <Cite id="roy" />. Our budget could not reach that regime.
			</li>
		</ol>
	</section>

	<section class="chapter" id="related">
		<h3><span class="n">{number('related')}</span>What is new here, and what is not</h3>
		<p class="src">
			<span class="mark prior"></span>Verified against the literature; see
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/PRIOR_ART.md`}>PRIOR_ART</a>, 36 arXiv records checked
		</p>
		<p>
			<strong>Prior work.</strong> Scoring triples is 2-simplicial or tensor attention <Cite
				id={['clift', 'sanford', 'roy']}
			/>, and degree-2 alternatives and a general scheme exist <Cite
				id={['kozachinskiy', 'chakrabarti']}
			/>. Summing ordered products over subsequences is the feature map of Seq2Tens <Cite
				id="seq2tens"
			/>, and multiplying learned group elements along a sequence is the path development network <Cite
				id="development"
			/>; signature methods are the wider family <Cite
				id={['iteratedsums', 'deepsignatures', 'roughtransformers']}
			/>. Input-dependent Householder products already appear in attention scores in PaTH attention <Cite
				id="path"
			/>. Networks trained on group operations are known to learn group representations <Cite
				id="chughtai"
			/> and Fourier features <Cite id="nanda" />. Matrix-state recurrent networks track non-abelian
			groups <Cite id={['deltaproduct', 'gdn']} />, and transformers learn shortcuts to automata <Cite
				id="automata"
			/>. Local-linear attention and Parallax are published <Cite id={['lla', 'parallax']} />.
		</p>
		<p>
			<strong>New here.</strong> The coupling barrier for degree-2 scores; the hand-built SET head; Feynman
			attention and the fixes that make it train; Newton attention, the characters law and transfer across
			arities; the finding that softmax given every character still cannot learn Match-4; holonomy attention's
			specific form (gated rotations, read per token and per subset size); the exact order-blind ceilings
			and the qualified theorems; and the measurements throughout, including the negative ones. We did
			not find the complete holonomy construction in the literature, but two closely related theses could
			not be checked in full, so we make no claim to be first.
		</p>
		<div class="figure wide"><LearnFigure section="timeline" /></div>
	</section>

	<section class="chapter" id="methods">
		<h3><span class="n">{number('methods')}</span>Methods, cost and reproducibility</h3>
		<p class="src"><span class="mark measured"></span>How the numbers were produced</p>
		<p>
			<strong>Two engines.</strong> The browser results (the SET and pointer-chase benches, and
			every live figure) come from this app's engine, written with jax-js <Cite id="jaxjs" /> and run
			on WebGPU, so you can reproduce them in the <a href={resolve('/compare')}>Compare</a> tab. The cloud
			results come from a JAX research harness on rented L4 and H100 GPUs.
		</p>
		<p>
			<strong>Discipline.</strong> Puzzle results use balanced accuracy on held-out data and three seeds.
			Every language and later study wrote its predictions and pass/fail thresholds into the repository
			before its main runs, tuned each model's learning rate on its own, and matched training compute.
			Where a prediction was changed after a pilot, the change and the reason are recorded. Failed predictions
			are reported as failed.
		</p>
		<p>
			<strong>Cost.</strong> The three language searches S0–S2 cost about $64, the S6 study $58, the group
			experiments about $3, the word problems about $15, the combined-layer study about $76 before we
			stopped it, and the dilution and ARC tests $3.76: small budgets by design, which is also why every
			language claim here is about small models.
		</p>
		<p>
			<strong>Where everything is.</strong> Each study has a research note with its full protocol:
		</p>
		<ul class="list">
			{#each notes as n (n.file)}
				<li>
					<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
					<a href={`${repo}${n.file}`}>{n.file.replace('research/', '')}</a>: {n.what}
				</li>
			{/each}
		</ul>
		<p>
			Raw per-run results live in <code>research/results</code>, and every number in this article is
			copied from them or from these notes.
		</p>
	</section>
</section>
