<script lang="ts">
	import { onMount } from 'svelte';
	import { asset, resolve } from '$app/paths';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import { SUITES, type SuiteId } from '#lib/engine/runs.ts';
	import { dealTable, strongestEdges, tourStops } from '#lib/explore/deal.ts';
	import { LAYOUT_SIZE } from '#lib/set/cards.ts';
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import { pct } from '#lib/ui/format.ts';
	import Hypergraph3D from '#lib/viz/Hypergraph3D.svelte';
	import TensorCube from '#lib/viz/TensorCube.svelte';
	import A5Rotation from '#lib/viz/A5Rotation.svelte';

	const C = LAYOUT_SIZE;
	/** The tiles fall to the page's black where the figures sit; the 3D canvases match it. */
	const TILE = 0x080808;

	// ── one deal of twelve cards, scored by the hand-built cubic head ────────
	const table = dealTable(3);
	const { layout, sets, volume } = table;

	// ── the cube, the hypergraph and the trained model share one query card ──
	let query = $state(sets[0][0]);
	let pick = $state<{ j: number; k: number } | null>(null);
	const edges = $derived(strongestEdges(table, query));
	const selected = $derived(pick ?? (edges[0] ? { j: edges[0].j, k: edges[0].k } : null));

	// ── the tour: every card in a SET, once per SET it belongs to ────────────
	const STOPS = tourStops(table);
	const STEP_MS = 3600;
	let touring = $state(false);
	let stop = $state(0);
	let rotation = $state(1);
	function goTo(n: number) {
		stop = (n + STOPS.length) % STOPS.length;
		query = STOPS[stop].i;
		pick = STOPS[stop].pair;
	}
	/** Anything the visitor clicks takes over from the tour, which resumes once they stop. */
	let resume = 0;
	function takeOver() {
		touring = false;
		clearTimeout(resume);
		if (!reduced) resume = window.setTimeout(() => (touring = true), 9000);
	}
	function choose(card: number) {
		takeOver();
		query = card;
		pick = null;
	}
	let reduced = false;
	onMount(() => {
		goTo(0);
		reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		touring = !reduced;
		const id = setInterval(() => {
			if (!touring || document.hidden) return;
			goTo(stop + 1);
			rotation = (rotation + 7) % 60;
		}, STEP_MS);
		return () => {
			clearTimeout(resume);
			clearInterval(id);
		};
	});

	// ── recordings: bench curves and two trained Feynman attention diagrams ──────────────
	interface RecordedRun {
		evalSteps: number[];
		evalAccuracy: number[];
		params: number;
	}
	let suite = $state<SuiteId>('set');
	const recordings: Record<SuiteId, Record<string, RecordedRun> | null> = $state({
		set: null,
		chase: null,
		match4: null
	});
	onMount(() => {
		const get = (path: Parameters<typeof asset>[0]) =>
			fetch(asset(path)).then((r) => (r.ok ? r.json() : null));
		get('recorded/set.json').then(
			(j) => j?.runs && (recordings.set = j.runs),
			() => {}
		);
		get('recorded/chase.json').then(
			(j) => j?.runs && (recordings.chase = j.runs),
			() => {}
		);
	});

	const runs = $derived(SUITES[suite].runs.filter((r) => recordings[suite]?.[r.id]));
	const series = $derived<Series[]>(
		runs.map((r) => {
			const rec = recordings[suite]![r.id];
			return {
				id: r.id,
				label: r.label,
				tone: r.tone,
				dash: r.dash,
				emphasis: r.tone === 1,
				xs: rec.evalSteps,
				ys: rec.evalAccuracy
			};
		})
	);
	const board = $derived(
		runs
			.map((r) => ({ ...r, acc: recordings[suite]![r.id].evalAccuracy.at(-1) ?? 0 }))
			.sort((a, b) => b.acc - a.acc)
	);
	const majority = $derived(getBench(suite).majority);
	const toneOf = (t: number) => {
		const v = Math.round(70 + t * (245 - 70));
		return `rgb(${v} ${v} ${v})`;
	};
	let chartH = $state(0);
</script>

<svelte:head>
	<title>Learning to compose | Polyformer</title>
	<meta
		name="description"
		content="From higher-order attention to learned group representations. Explore the experiments, the limits, and the rotations a neural network learns from relational labels."
	/>
</svelte:head>

<main class="deck">
	<!-- ── the idea ─────────────────────────────────────────────────────── -->
	<section class="intro">
		<h1>Learning to compose</h1>
		<p class="lede">What should one layer be able to do?</p>
		<p>
			Attention compares tokens in pairs. Some relations only appear when several tokens come
			together. Higher-order attention gives a layer that operation directly—and wins on puzzles
			built around it.
		</p>
		<p>
			Language did not reward more order at our scale. The useful turn was composition: learning how
			small operations combine. Clock hands add without caring about order. Rotations can remember
			it.
		</p>
		<p>
			Given only answers to a relational task, a layer learns rotations that nearly obey the
			symmetries of an icosahedron. The route from token pairs to those rotations is the story here.
		</p>
		<p class="small">
			A course, working paper and experiments. Browser-trained baselines; recorded group results.
		</p>
		<div class="ctas">
			<a class="cta primary" href={resolve('/learn')}>Read how it works</a>
			<a class="cta" href={resolve('/report')}>Read the paper</a>
		</div>
	</section>

	<!-- ── the tensor ───────────────────────────────────────────────────── -->
	<section class="tile cube">
		<header>
			<h2>Scores for whole triples</h2>
			<p>
				A standard head fills a matrix, one score per query and key. A higher-order head fills a
				tensor: every query against every pair of keys, so one step can weigh how two tokens bear on
				a third.
			</p>
			<div class="t-math">
				<MathTex
					tex={'A_{ij} = \\langle Q_i,\\, K_j \\rangle \\quad\\longrightarrow\\quad A_{ijk} = \\langle Q_i,\\, K^{1}_{j} \\odot K^{2}_{k} \\rangle'}
				/>
			</div>
		</header>
		<div class="stage">
			<TensorCube
				values={volume}
				n={C}
				{query}
				{selected}
				background={TILE}
				spin={0.9}
				label="The attention tensor of twelve SET cards"
				onpick={(c) => {
					takeOver();
					query = c.i;
					pick = { j: c.j, k: c.k };
				}}
			/>
		</div>
	</section>

	<!-- ── the same cards as a hypergraph ───────────────────────────────── -->
	<section class="tile graph">
		<header>
			<h2>Attention on hyperedges</h2>
			<p>
				The same scores as a graph. Weight lands on triangles, not edges: the query reads what a
				group of tokens holds together, so a relation that exists only in the group takes one step.
			</p>
			<div class="t-math">
				<MathTex
					tex={'y_i = \\sum_{j,k} \\operatorname{softmax}_{jk}\\big(A_{ijk}\\big)\\; V^{1}_{j} \\odot V^{2}_{k}'}
				/>
			</div>
		</header>
		<div class="stage">
			<Hypergraph3D
				{layout}
				{query}
				{edges}
				{selected}
				{sets}
				background={TILE}
				spin={1.4}
				onquery={choose}
				onedge={(e) => {
					takeOver();
					pick = e;
				}}
			/>
		</div>
	</section>

	<!-- The composition learned by the group models. -->
	<section class="tile flow">
		<header class="row">
			<h2>Relations as composition</h2>
			<p>
				A token becomes a rotation. A layer multiplies rotations in sequence order, then reads
				relations among subsets. The learned heads approximate the symmetries shown here.
			</p>
		</header>
		<div class="stage rotation-stage">
			<A5Rotation element={rotation} model="ideal" background={TILE} />
		</div>
		<footer>
			<span>Ideal icosahedral symmetry</span>
			<a href={resolve('/explore/groups')}>Inspect the learned rotations</a>
		</footer>
	</section>

	<!-- ── the bench ────────────────────────────────────────────────────── -->
	<section class="tile chart">
		<header class="row">
			<div class="head-line">
				<h2>More per layer</h2>
				<div class="seg" role="group" aria-label="Task">
					<button
						class:on={suite === 'set'}
						aria-pressed={suite === 'set'}
						onclick={() => (suite = 'set')}>SET</button
					>
					<button
						class:on={suite === 'chase'}
						aria-pressed={suite === 'chase'}
						onclick={() => (suite = 'chase')}>Chase</button
					>
				</div>
			</div>
			<p>
				{#if suite === 'set'}
					On these three-way relations, cubic attention reaches 100.0% held-out accuracy. The
					softmax baselines stay behind within this training budget.
				{:else}
					Following a chain needs repeated composition. The recorded Feynman model learns chains of
					single hops.
				{/if}
				Held-out accuracy, trained in the browser.
			</p>
		</header>
		<div class="plot" bind:clientHeight={chartH}>
			{#if series.length && chartH > 60}
				<LineChart
					label="Held-out accuracy, recorded"
					{series}
					xMax={4000}
					yMin={suite === 'set' ? 0.4 : 0}
					yMax={1}
					yTicks={suite === 'set' ? [0.4, 0.6, 0.8, 1] : [0, 0.5, 1]}
					formatY={(v) => pct(v, 0)}
					reference={{ y: majority, label: `Majority ${pct(majority, 0)}` }}
					height={chartH}
				/>
			{/if}
		</div>
		<ol class="board">
			{#each board as r (r.id)}
				<li class:lead={r.tone === 1}>
					<svg width="18" height="8" aria-hidden="true"
						><line
							x1="1"
							y1="4"
							x2="17"
							y2="4"
							stroke={toneOf(r.tone)}
							stroke-width={r.tone === 1 ? 2 : 1.4}
							stroke-dasharray={r.dash || undefined}
						/></svg
					>
					<span class="b-name">{r.label}</span>
					<span class="num">{pct(r.acc, 1)}</span>
				</li>
			{/each}
		</ol>
	</section>
</main>

<style>
	/* One screen: the idea on the left, four instruments on the right. */
	.deck {
		display: grid;
		height: calc(100dvh - var(--bar-h));
		min-height: 660px;
		grid-template-columns: minmax(300px, 0.74fr) minmax(0, 1fr) minmax(0, 1fr);
		grid-template-rows: minmax(0, 1fr) minmax(0, 1fr);
		grid-template-areas:
			'intro cube graph'
			'intro flow chart';
		gap: 12px;
		padding: 12px 16px 16px;
	}

	/* ── the idea ──────────────────────────────────────────────────────── */
	.intro {
		grid-area: intro;
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 0 16px 2vh 12px;
	}
	h1 {
		margin: 0;
		font-size: clamp(30px, 3.8vh, 38px);
		font-weight: 500;
		line-height: 1.02;
		letter-spacing: -0.028em;
		text-wrap: balance;
	}
	.intro p {
		margin: 1.4vh 0 0;
		max-width: 44ch;
		font-size: clamp(13px, 1.7vh, 15px);
		line-height: 1.6;
		color: var(--color-ink-2);
	}
	.intro p.lede {
		margin-top: 2.6vh;
		color: var(--color-ink);
	}
	.intro p.small {
		margin-top: 1.6vh;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.ctas {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-top: 3vh;
	}
	.cta {
		display: inline-flex;
		align-items: center;
		height: 34px;
		padding: 0 14px;
		border-radius: var(--radius-ui);
		background: var(--color-lift);
		color: var(--color-ink);
		font-size: var(--text-sm);
		text-decoration: none;
		transition: background 120ms ease;
	}
	.cta:hover {
		background: var(--color-control);
	}
	.cta.primary {
		background: var(--color-ink);
		color: var(--color-void);
	}
	.cta.primary:hover {
		background: #fff;
	}
	/* ── tiles ─────────────────────────────────────────────────────────── */
	.tile {
		position: relative;
		display: flex;
		flex-direction: column;
		min-width: 0;
		min-height: 0;
		border-radius: 12px;
		/* soft grey behind the words, falling slowly to the page's black where the figure sits */
		background: linear-gradient(
			180deg,
			#171717 0%,
			#131313 16%,
			#0e0e0e 34%,
			#0a0a0a 46%,
			var(--color-void) 56%
		);
		overflow: hidden;
	}
	.tile header {
		position: relative;
		z-index: 2;
		padding: 13px 16px 0;
		pointer-events: none;
	}
	.tile header.row {
		pointer-events: auto;
	}
	/* the task switch shares the title's line, so the text below gets the full width */
	.head-line {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
	}
	.head-line .seg {
		margin: -5px -4px -5px 0;
	}
	h2 {
		margin: 0;
		font-size: var(--text-ui);
		font-weight: 500;
		color: var(--color-ink);
	}
	.tile header p {
		margin: 3px 0 0;
		max-width: 64ch;
		font-size: var(--text-xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.t-math {
		margin-top: 7px;
		font-size: 13px;
		color: var(--color-ink-2);
		overflow-x: auto;
		overflow-y: hidden;
	}
	.stage {
		position: relative;
		flex: 1;
		min-height: 0;
		/* the canvases fade in over the gradient instead of showing their own edge */
		--feather-top: 72px;
	}
	.tile footer {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 0 16px 12px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.cube {
		grid-area: cube;
	}
	.graph {
		grid-area: graph;
	}
	/* room for the role labels that sit right of the outer nodes */
	.graph .stage {
		margin: 0 30px 6px 6px;
	}
	.flow {
		grid-area: flow;
	}
	.rotation-stage {
		min-height: 190px;
	}
	.tile footer {
		justify-content: space-between;
		flex-wrap: wrap;
	}
	.tile footer a {
		color: var(--color-ink-2);
		text-underline-offset: 3px;
	}

	/* ── the bench ─────────────────────────────────────────────────────── */
	.chart {
		grid-area: chart;
	}
	.plot {
		flex: 1;
		min-height: 0;
		padding: 4px 8px 0 0;
	}
	.board {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2px 16px;
		margin: 0;
		padding: 0 16px 12px;
		list-style: none;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.board li {
		display: flex;
		align-items: center;
		gap: 7px;
		min-width: 0;
	}
	.board svg {
		display: block;
		flex: none;
	}
	.b-name {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.board li.lead {
		color: var(--color-ink);
	}
	.seg {
		display: inline-flex;
		flex: none;
		padding: 2px;
		border-radius: 6px;
		background: var(--color-panel);
	}
	.seg button {
		height: 24px;
		padding: 0 10px;
		border: 0;
		border-radius: var(--radius-ui);
		background: transparent;
		color: var(--color-ink-3);
		font: inherit;
		font-size: var(--text-xs);
		cursor: pointer;
	}
	.seg button.on {
		background: var(--color-control);
		color: var(--color-ink);
	}

	/* short laptop screens: captions give way to the pictures */
	@media (max-height: 860px) and (min-width: 1101px) {
		.board {
			display: none;
		}
	}

	/* ── smaller screens scroll, one instrument after another ──────────── */
	@media (max-width: 1100px) {
		.deck {
			height: auto;
			grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
			grid-template-rows: auto 460px 460px;
			grid-template-areas:
				'intro intro'
				'cube graph'
				'flow chart';
		}
		.intro {
			padding: 28px 8px 20px;
		}
	}
	@media (max-width: 700px) {
		.board {
			grid-template-columns: minmax(0, 1fr);
		}
		.b-name {
			white-space: normal;
			overflow: visible;
			text-overflow: clip;
		}
		.deck {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: auto 390px 390px 360px 480px;
			grid-template-areas: 'intro' 'cube' 'graph' 'flow' 'chart';
			padding: 8px 12px 16px;
		}
	}
</style>
