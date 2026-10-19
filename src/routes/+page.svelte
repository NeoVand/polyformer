<script lang="ts">
	import { onMount } from 'svelte';
	import { asset, resolve } from '$app/paths';
	import { CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import { SUITES, type SuiteId } from '#lib/engine/runs.ts';
	import { dealTable, strongestEdges, tourStops } from '#lib/explore/deal.ts';
	import { LAYOUT_SIZE } from '#lib/set/cards.ts';
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { flowGroups, heldPayloads } from '#lib/viz/chaseFlow.ts';
	import DiagramFlow from '#lib/viz/DiagramFlow.svelte';
	import FlowLegend from '#lib/viz/FlowLegend.svelte';
	import Hypergraph3D from '#lib/viz/Hypergraph3D.svelte';
	import TensorCube from '#lib/viz/TensorCube.svelte';

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
	let chaseStop = $state(0);
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
		return () => clearTimeout(resume);
	});
	$effect(() => {
		if (!touring) return;
		const id = setInterval(() => {
			if (document.hidden) return;
			goTo(stop + 1);
			chaseStop += 1;
		}, STEP_MS);
		return () => clearInterval(id);
	});

	// ── recordings: bench curves and two trained Feynman attention diagrams ──────────────
	interface RecordedRun {
		evalSteps: number[];
		evalAccuracy: number[];
		params: number;
	}
	interface ChaseRecording {
		accuracy: number;
		instance: ChaseInstance;
		diagram: DiagramResult;
	}
	interface SetRecording {
		accuracy: number;
		diagram: DiagramResult;
	}
	let suite = $state<SuiteId>('set');
	let flowTask = $state<SuiteId>('set');
	const recordings: Record<SuiteId, Record<string, RecordedRun> | null> = $state({
		set: null,
		chase: null,
		match4: null
	});
	let chaseRec = $state.raw<ChaseRecording | null>(null);
	let setRec = $state.raw<SetRecording | null>(null);
	$effect(() => {
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
		get('recorded/chase-diagram.json').then(
			(j) => j?.diagram && (chaseRec = j),
			() => {}
		);
		get('recorded/set-diagram.json').then(
			(j) => j?.diagram && (setRec = j),
			() => {}
		);
	});
	const chaseGroups = $derived(chaseRec ? flowGroups(chaseRec.instance) : []);
	/** On the chase tab the tour visits the query and the head of every other list. */
	const chaseRoots = $derived(chaseGroups.map((g) => g[0]));
	const chaseRoot = $derived(
		chaseRoots.length ? chaseRoots[chaseStop % chaseRoots.length] : CHASE_QUERY_POS
	);
	const chaseHeld = $derived(
		chaseRec
			? heldPayloads(
					chaseRec.diagram.perHead[0],
					chaseRec.diagram.n,
					chaseRec.diagram.rounds,
					chaseRec.instance
				)
			: null
	);
	const chaseAnswer = $derived.by(() => {
		const p = chaseRec?.diagram.probs;
		return p ? p.indexOf(Math.max(...p)) : null;
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
	const CARD_ROWS = [Array.from({ length: C }, (_, i) => i + 1)];
</script>

<svelte:head>
	<title>Polyformer | Higher-order attention</title>
	<meta
		name="description"
		content="Higher-order attention: cubic heads that read triples and Feynman attention, which learns how many tokens to combine. See the tensor, the hypergraph, a trained model and the bench, all computed in your browser."
	/>
</svelte:head>

<main class="deck">
	<!-- ── the idea ─────────────────────────────────────────────────────── -->
	<section class="intro">
		<h1>Higher-order attention</h1>
		<p class="lede">
			You can tell whether a photo shows an animal in about 150 milliseconds, time for only a dozen
			or so neural stages in a row. The brain manages with few layers because each one does a lot: a
			single neuron combines its inputs more like a small network than a weighted sum.
		</p>
		<p>
			Transformers go the other way. A head compares tokens two at a time, so anything that depends
			on three tokens at once has to be assembled over many layers. Polyformer looks for layers that
			do more per step: attention that relates whole groups of tokens at once, and learns how large
			those groups should be.
		</p>
		<p>
			Hints of this run from the 2-simplicial transformer to proofs that attention over triples
			beats pairs and kernels that train it at scale. Our two ideas, cubic attention and Feynman
			attention, solve SET in one layer and pointer chasing with 40% of the parameters of the
			deepest baseline.
		</p>
		<p class="small">
			Every model on this page was trained in a browser with jax-js. There is no server.
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

	<!-- ── what a trained Feynman attention model does ──────────────────────────────── -->
	<section class="tile flow">
		<header class="row">
			<div class="head-line">
				<h2>Letting the data choose the arity</h2>
				<div class="seg" role="group" aria-label="Task">
					<button
						class:on={flowTask === 'set'}
						aria-pressed={flowTask === 'set'}
						onclick={() => (flowTask = 'set')}>SET</button
					>
					<button
						class:on={flowTask === 'chase'}
						aria-pressed={flowTask === 'chase'}
						onclick={() => (flowTask = 'chase')}>Chase</button
					>
				</div>
			</div>
			<p>
				How many tokens should one step relate? Feynman attention leaves it to learning: each round,
				every token reads its own value, one token, two at once or a learned summary. Unrolled, that
				is a sum over diagrams, and this is the one a trained model drew.
				{#if flowTask === 'set'}
					Asked to find matching triples, it chose triples.
				{:else}
					Asked to follow pointers, it chose chains of single hops.
				{/if}
			</p>
		</header>
		<div class="t-math pad">
			<MathTex
				tex={'\\Phi^{r}_t = \\pi_{\\text{leaf}}\\, v_t + \\sum_j \\pi_j\\, \\Phi^{r-1}_j + \\sum_{jk} \\pi_{jk}\\, \\Phi^{r-1}_j \\odot \\Phi^{r-1}_k + \\cdots'}
			/>
		</div>
		<div class="stage flow-stage">
			{#if flowTask === 'set' && setRec}
				{@const d = setRec.diagram}
				<DiagramFlow
					head={d.perHead[0]}
					n={d.n}
					rounds={d.rounds}
					rows={CARD_ROWS}
					root={query + 1}
					onroot={(t) => choose(t - 1)}
					pitch={17}
					column={120}
					fit
					output="\hat y"
					note={STOPS.some((s) => s.i === query && s.pair) ? 'in a SET' : 'no SET'}
				>
					{#snippet label(t)}<SetCard card={layout[t - 1]} width={14} />{/snippet}
				</DiagramFlow>
			{:else if flowTask === 'chase' && chaseRec}
				{@const d = chaseRec.diagram}
				{@const inst = chaseRec.instance}
				<DiagramFlow
					head={d.perHead[0]}
					n={d.n}
					rounds={d.rounds}
					rows={chaseGroups}
					root={chaseRoot}
					onroot={(t) => {
						takeOver();
						chaseStop = Math.max(0, chaseRoots.indexOf(t));
					}}
					pitch={16}
					column={78}
					fit
					annotate={(r, t) => {
						const v = chaseHeld?.[r]?.[t];
						return v === null || v === undefined ? null : String(v);
					}}
					output={chaseRoot === CHASE_QUERY_POS
						? `\\hat y = ${chaseAnswer ?? ''}`
						: `\\Phi^{${d.rounds}}`}
					note={chaseRoot === CHASE_QUERY_POS ? pct(d.probs[chaseAnswer ?? 0] ?? 0, 1) : undefined}
				>
					{#snippet label(t)}
						{#if t === CHASE_QUERY_POS}<MathTex tex="q" />{:else}{inst.nodes[t - 1].id}{/if}
					{/snippet}
				</DiagramFlow>
			{/if}
		</div>
		<footer><FlowLegend compact /></footer>
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
					On a task built from three-way relations, one higher-order layer is exact, and stacking
					pairwise layers does not catch up.
				{:else}
					On following chains, a layer that chooses its arity matches a deeper pairwise model with
					40% of its parameters.
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
		font-size: clamp(34px, 6vh, 58px);
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
	.t-math.pad {
		margin: 6px 0 0;
		padding: 0 16px;
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
	.flow-stage {
		padding: 2px 14px 0 8px;
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
		.deck {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: auto 440px 440px auto 460px;
			grid-template-areas: 'intro' 'cube' 'graph' 'flow' 'chart';
			padding: 8px 12px 16px;
		}
		.flow-stage {
			padding-bottom: 8px;
		}
	}
</style>
