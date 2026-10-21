<script lang="ts">
	import Cite from '#lib/learn/Cite.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import ComputeGraph from '#lib/viz/ComputeGraph.svelte';
	import { EVENTS, FRAMES } from '#lib/viz/computeGraphs.ts';
	import ContextFigure, { type Series } from '../ContextFigure.svelte';
	import HalfLifeFigure from '../HalfLifeFigure.svelte';
	import { number } from '../toc.ts';

	const repo = 'https://github.com/neovand/polyformer/blob/main/';
	// final held-out loss on the val_big windows, nats per token, mean of seeds 1–3, equal modeled
	// training FLOPs, about 443M tokens for softmax (research/LOOPS_REPORT.md)
	const loops = [
		{ label: 'Softmax, learned positions', loss: '3.6137', vs: '+0.95%' },
		{ label: 'Softmax, rotary positions', loss: '3.5798', vs: '' },
		{ label: 'Forgetting Transformer (rotary + forget gate)', loss: '3.5709', vs: '−0.25%' },
		{ label: 'Gated DeltaNet', loss: '3.5772', vs: '−0.07%' },
		{ label: 'Gated DeltaProduct', loss: '3.5690', vs: '−0.30%' },
		{ label: 'Hybrid, rotary', loss: '3.5513', vs: '−0.80%' },
		{ label: 'Hybrid, carried frames + forget gate', loss: '3.5479', vs: '−0.89%', best: true }
	];
	// research/EVENTS.md, events_confirm: context 512, seeds 1–3
	const fair = [
		{
			label: 'Softmax: rotary, forget gate, gated output, value residual',
			loss: '3.5235',
			vs: '',
			wall: '1,241'
		},
		{
			label: 'Hybrid with the same parts, one head transported',
			loss: '3.5278',
			vs: '+0.12%',
			wall: '1,837'
		},
		{
			label: 'Softmax with its MLP widened to the hybrid’s parameters',
			loss: '3.5172',
			vs: '−0.18%',
			wall: '1,376',
			best: true
		}
	];
	// events_confirm, events_2k_b, events_8k: change against the strengthened softmax control
	const series: Series[] = [
		{
			name: 'Hybrid',
			points: [
				{ ctx: 512, pct: 0.12, seeds: 3 },
				{ ctx: 2048, pct: -0.07, seeds: 2 },
				{ ctx: 8192, pct: -0.66, seeds: 3 }
			]
		}
	];
	// loops_eval on the 8,192 headline checkpoints, seeds 1–3: loss of tokens by how far back they last
	// occurred in the window, hybrid against the strengthened softmax
	const buckets = [
		{ d: 'never', soft: '5.6106', hyb: '5.5792', vs: '−0.56%' },
		{ d: '1–32', soft: '1.6487', hyb: '1.6399', vs: '−0.53%' },
		{ d: '33–128', soft: '2.1597', hyb: '2.1545', vs: '−0.24%' },
		{ d: '129–256', soft: '2.8678', hyb: '2.8565', vs: '−0.39%' },
		{ d: '257–384', soft: '3.2687', hyb: '3.2464', vs: '−0.68%' },
		{ d: '385–1,024', soft: '3.7149', hyb: '3.6741', vs: '−1.10%' },
		{ d: '1,025–4,096', soft: '4.4018', hyb: '4.3284', vs: '−1.67%', best: true },
		{ d: 'over 4,096', soft: '4.8728', hyb: '4.8155', vs: '−1.18%' }
	];
	// one learned segmentation (events_8k seed 2, held-out text); │ marks the start of an event
	const segmented =
		'│ Predators│,│ like sharks│ and seals, will try to chew through the pens, oceans│ are unpredictable│ and│ human error is a risk│. The│ strategy is to minimize the impact they can have│.';
</script>

<section class="part" id="part-memory">
	<header class="part-head">
		<span class="roman">Part IX</span>
		<h2>Memory on text</h2>
		<p class="part-lede">
			Composition did not pay on text, but one model in that comparison did. This part asks why, how
			far it goes, and what it learns. At short range a stronger softmax baseline erases the gain.
			At long range it returns, and it comes from two parts: a recurrent memory that predicts new
			tokens better, and content-driven frames that retrieve repeated ones better, by more as the
			context grows. Along the way the models organise their memory into events on their own.
		</p>
	</header>

	<section class="chapter" id="two-memories">
		<h3><span class="n">{number('two-memories')}</span>Two memories on text</h3>
		<p class="src">
			<span class="mark new"></span>Carried frames; <span class="mark prior inline"></span>rotary
			positions, the forget gate and the recurrent layers <Cite id={['rope', 'fox', 'gdn']} />;
			<span class="mark measured inline"></span>three seeds, predictions committed first (LOOPS)
		</p>
		<p>
			The study carried the holonomy idea into attention for text. Each attention layer keeps a
			frame that is updated token by token, a rotation that depends on the content, and compares a
			query and a key in the frames of their own positions. A forget gate lets a layer discount the
			past
			<Cite id="fox" />. The strongest model alternates Gated DeltaNet layers <Cite id="gdn" />,
			which hold a matrix-valued memory, with these attention layers.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={FRAMES} label="Computation graph of attention in carried frames" />
		</div>
		<p class="caption">
			Every token supplies a move <MathTex tex="M_t" />, a rotation computed from its content, and a
			forget gate <MathTex tex="f_t" />. The running product of the moves is the token's frame, and
			a query meets a key through <MathTex tex={String.raw`F_i^{\top}F_j`} />, the rotation
			accumulated between them: the holonomy of the path. It is never formed per pair, since
			<MathTex tex={String.raw`q_i^{\top}F_i^{\top}F_jk_j = (F_iq_i)^{\top}(F_jk_j)`} />. The output
			gate and value residual of section {number('fair')} are left out.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead
					><tr
						><th>Model, context 512</th><th class="num">Loss</th><th class="num">vs rotary</th></tr
					></thead
				>
				<tbody>
					{#each loops as r (r.label)}
						<tr class:best={r.best}>
							<th>{r.label}</th><td class="num">{r.loss}</td><td class="num">{r.vs}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Held-out loss in nats per token, mean of three seeds, at equal modeled training compute; the
			per-seed values are in LOOPS.
		</p>
		<p>
			Almost all of the gain comes from known parts: alternating recurrent and attention layers is
			worth 0.80%, the forget gate 0.25% on its own, and the carried frames add 0.10% inside the
			hybrid. The frames do pay elsewhere. With values carried through the frame as well, one
			attention layer tracks <MathTex tex="A_5" /> at 98.5% on late positions, where rotary positions
			stay at chance. On text they change the loss by less than 0.1%.
		</p>
	</section>

	<section class="chapter" id="segments">
		<h3><span class="n">{number('segments')}</span>The models find events on their own</h3>
		<p class="src">
			<span class="mark measured"></span>Probes of trained checkpoints, seed 1, 48 held-out windows
		</p>
		<p>
			Nothing in training mentions sentences, yet the forget gates learn them. In every layer the
			gate forgets most at a full stop, a question mark, a line break or a sentence-initial
			<em>The</em>, so memory is cut at the ends of events. And the layers divide the timescales
			between them: the early layers keep about 1 to 100 tokens, and the last keeps up to 13,000 in
			the softmax model and 40,000 in the hybrid, longer than the window.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<HalfLifeFigure />
				<figcaption>
					Each dot is one head: how many tokens it takes for the head's memory to halve, on a log
					scale. Right: the tokens on which each layer forgets most (⏎ is a line break).
				</figcaption>
			</figure>
		</div>
		<p>
			The content-driven clocks of the hybrid read the same structure: the modules that stay on tick
			fastest at sentence ends, on clause words such as <em>who</em>, <em>which</em> and
			<em>when</em>, and on verbs, and nearly stop inside words.
		</p>
	</section>

	<section class="chapter" id="fair">
		<h3><span class="n">{number('fair')}</span>A stronger baseline erases it at short range</h3>
		<p class="src">
			<span class="mark prior"></span>Gated output and value residual <Cite
				id={['gatedattn', 'valueres']}
			/>; <span class="mark measured inline"></span>three seeds, predictions committed first
			(EVENTS)
		</p>
		<p>
			A reviewer's objection was that a fair comparison gives the baseline the best published parts
			too. Two cost almost nothing: a sigmoid gate on the attention output, computed from the
			layer's input <Cite id="gatedattn" />, and a value residual, which mixes the first layer's
			values into every later layer <Cite id="valueres" />. We put both into both models.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead>
					<tr
						><th>Model, context 512</th><th class="num">Loss</th><th class="num">vs softmax</th><th
							class="num">Seconds</th
						></tr
					>
				</thead>
				<tbody>
					{#each fair as r (r.label)}
						<tr class:best={r.best}>
							<th>{r.label}</th><td class="num">{r.loss}</td><td class="num">{r.vs}</td><td
								class="num">{r.wall}</td
							>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Mean of three seeds at equal modeled compute; seconds per run on one H100. The hybrid was
			above the softmax model on every seed (paired t = +5.6 across 1,024 held-out windows).
		</p>
		<p>
			The two parts lower the softmax model's loss by 1.33% and the hybrid's by only 0.57%, and the
			hybrid's lead is gone. The gate is a reset: it lets a layer switch its output off. The softmax
			model had no way to reset and gains six times as much from it as the hybrid, which had
			several.
		</p>
	</section>

	<section class="chapter" id="context">
		<h3><span class="n">{number('context')}</span>What pays at long context</h3>
		<p class="src">
			<span class="mark measured"></span>Contexts 512, 2,048 and 8,192; three seeds at 8,192,
			predictions committed first (EVENTS)
		</p>
		<p>
			At 512 tokens an attention score is a small part of a layer's cost and the window is short, so
			there is little for a second memory to add. The same two models, with the same parts, were
			trained at longer contexts.
		</p>
		<div class="figure wide">
			<figure class="pf">
				<ContextFigure {series} />
				<figcaption>
					Change in held-out loss against the strengthened softmax model at the same context and
					compute; below zero is better. Three seeds at 512 and 8,192, two at 2,048.
				</figcaption>
			</figure>
		</div>
		<p>
			The hybrid's margin grows with the context: <strong>−0.66% at 8,192</strong> (−0.72, −0.72 and −0.53
			on the three seeds; paired t = −23), against −0.07% at 2,048 and +0.12% at 512. It costs 1.35 times
			the wall clock in our implementation. Sorting the tokens by how far back they last appeared shows
			where the gain comes from.
		</p>
		<div class="table-scroll">
			<table class="bt">
				<thead>
					<tr
						><th>Last seen, tokens back</th><th class="num">Softmax</th><th class="num">Hybrid</th
						><th class="num">Change</th></tr
					>
				</thead>
				<tbody>
					{#each buckets as r (r.d)}
						<tr class:best={r.best}>
							<th>{r.d}</th><td class="num">{r.soft}</td><td class="num">{r.hyb}</td><td class="num"
								>{r.vs}</td
							>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="caption">
			Loss of the tokens in each group at context 8,192, mean of three seeds; "never" is a token not
			seen earlier in the window.
		</p>
		<p>
			The gain is largest on tokens that last occurred 1,000 to 4,000 positions back. At 2,048 the
			hybrid wins on the far tokens too but loses on the near ones; at 8,192 the far tokens weigh
			more and the near deficit disappears.
		</p>
		<p>
			<strong>Which part pays.</strong> The same hybrid with rotary positions in place of the carried
			frames (seed 1) is only 0.21% below softmax at 8,192, against 0.72% for the hybrid with frames on
			the same seed. So most of the long-context gain is the frames: 0.51% at 8,192 (paired t = −16.5),
			against 0.21% at 2,048 and about 0.1% at 512. The two parts help different tokens. The recurrent
			layers predict tokens not seen earlier in the window better (−0.7%) and cost on near repeats (+0.7%);
			the frames help on every token that has appeared before, by 0.6% to 1.4% at every distance, and
			not at all on new ones. Frames that depend on the content make repeated content easier to find again,
			and the longer the window, the more there is to find. They pay only beside the recurrent layers:
			softmax given the same frames gains 0.07%, because there they help far repeats but cost near ones
			(1 to 32 tokens back: +0.8%). Frames alone 0.07%, recurrence alone 0.21%, both together 0.72%.
		</p>
		<p>
			At three times the parameters (width 768, eight layers, one seed) the hybrid's margin at 8,192
			is 0.46%, against 0.72% for the base size on the same seed: in this one comparison it does not
			grow with size.
		</p>
	</section>

	<section class="chapter" id="event-model">
		<h3><span class="n">{number('event-model')}</span>Events as the unit of memory</h3>
		<p class="src">
			<span class="mark prior"></span>Learned chunking <Cite id="hnet" />;
			<span class="mark measured inline"></span>development screens and two seeds at each context
			(EVENTS)
		</p>
		<p>
			If the models cut memory at events anyway, a model could be built around them. Ours follows
			H-Net <Cite id="hnet" />: two recurrent layers read the tokens; a router marks where the
			content changes; the state at each mark becomes one event vector; six attention layers, with
			frames and forget gate, run over the events instead of the tokens; and two recurrent layers
			turn the result back into token predictions. At 8,192 tokens it costs a third less per token
			than softmax, so at equal compute it sees 1.5 times the text.
		</p>
		<div class="figure wide graph">
			<ComputeGraph graph={EVENTS} label="Computation graph of the event model" />
		</div>
		<p class="caption">
			Top row: the tokens, two Gated DeltaNet layers in and two out, the second pair cutting its
			state at each event boundary. Bottom row: the router compares neighbouring states, the state
			at each boundary becomes one event, six attention layers run over the events, and each token
			receives its event's smoothed output.
		</p>
		<p>
			It lost at every context: +3.6% against softmax at 2,048 and +3.1% to +6.6% at 8,192. Two
			things went wrong. The router held its target of one event per 8 tokens in short runs but
			drifted in long ones until its boundaries all but vanished (one per 42 to 1,074 tokens), so
			most long runs had almost no events. And even with working boundaries, an event vector loses
			the exact tokens it summarises: on a copying probe in the development runs the event models
			scored 0.18 against 0.23 to 0.25 for the token models, and in the long runs they were worst on
			every distance group above.
		</p>
		<p>
			Where the router did hold, it found clauses without being told. On one checkpoint 53% of its
			boundaries fall at punctuation, a line break or a clause word, against 26% of tokens:
		</p>
		<p class="evtext">
			{#each segmented.split('│').slice(1) as event, i (i)}<span class="cut" aria-hidden="true"
				></span>{event}{/each}
		</p>
		<p class="caption">
			Held-out text; each mark is where the router starts a new event (context 8,192, seed 2).
		</p>
	</section>

	<section class="chapter" id="why-text">
		<h3><span class="n">{number('why-text')}</span>Why text rewards resets, not groups</h3>
		<p class="src">
			<span class="mark prior"></span>Automata decompositions <Cite
				id={['automata', 'starfree']}
			/>;
			<span class="mark new inline"></span>our reading of the results
		</p>
		<p>
			The Krohn–Rhodes theorem splits any finite-state process into two kinds of part: resets, which
			overwrite state, and groups, which permute it reversibly. Masked hard attention without
			positions recognises exactly the star-free languages, whose automata need no groups at all <Cite
				id="starfree"
			/>. Every part that paid on text is a reset: the forget gate, the output gate, the recurrent
			layers' decay, and the event cuts the models learn for themselves. The group part, the
			non-commuting frames, is used by the trained models but rewarded only at long range and only
			beside a recurrent memory: worth about 0.1% at 512 tokens and 0.5% at 8,192, all of it on
			tokens that repeat, where finding the earlier occurrence depends on the order of what came
			between. Where order is the whole task, as in tracking <MathTex tex="A_5" />, the group part
			is the whole answer.
		</p>
		<p>
			The full record, with every registered prediction and how it fared, is in
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/LOOPS_REPORT.md`}>LOOPS</a> and
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
			<a href={`${repo}research/EVENTS_REPORT.md`}>EVENTS</a>.
		</p>
	</section>
</section>

<style>
	tr.best th,
	tr.best td {
		font-weight: 600;
		color: var(--color-ink);
	}
	.evtext {
		color: var(--color-ink-2);
	}
	.cut {
		display: inline-block;
		width: 1.5px;
		height: 1.05em;
		margin: 0 3px -0.18em;
		background: var(--color-ink);
	}
</style>
