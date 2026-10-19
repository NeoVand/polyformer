<script lang="ts">
	import { asset, resolve } from '$app/paths';
	import type { ChaseInstance } from '#lib/chase/chase.ts';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import { SUITES, type SuiteId } from '#lib/engine/runs.ts';
	import { querySlice, topHyperedges } from '#lib/explore/analysis.ts';
	import { exactProbe, scoreSlice } from '#lib/explore/exact.ts';
	import { dealLayout, findSets, isSet, LAYOUT_SIZE, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { pct } from '#lib/ui/format.ts';
	import ChaseFlow from '#lib/viz/ChaseFlow.svelte';
	import Hypergraph3D from '#lib/viz/Hypergraph3D.svelte';
	import TensorCube from '#lib/viz/TensorCube.svelte';

	const C = LAYOUT_SIZE;
	/** Tiles are drawn on the well colour; the 3D canvases match it. */
	const TILE = 0x0e0e0e;

	// ── one deal of twelve cards, scored by the hand-built cubic head ────────
	function deal(seed: number): Card[] {
		const rng = mulberry32(seed * 7717 + 3);
		for (;;) {
			const l = dealLayout(rng);
			if (findSets(l).length >= 3) return l;
		}
	}
	const layout = deal(3);
	const sets = findSets(layout);
	const exact = exactProbe(layout, 3);

	/** The score tensor, normalised and sharpened so SET cells stand out (as in the lab). */
	const volume = (() => {
		const flat = new Float32Array(C * C * C);
		for (let i = 0; i < C; i++) flat.set(scoreSlice(exact, i), i * C * C);
		let lo = Infinity;
		let hi = -Infinity;
		for (const v of flat)
			if (!Number.isNaN(v)) {
				lo = Math.min(lo, v);
				hi = Math.max(hi, v);
			}
		const span = hi - lo || 1;
		return flat.map((v) => (Number.isNaN(v) ? 0 : ((v - lo) / span) ** 3.25));
	})();
	const strongest = (q: number) => {
		const top = topHyperedges(querySlice(exact, 0, q), 5, q);
		const w = top[0]?.weight || 1;
		return top.map((e) => ({ j: e.j, k: e.k, weight: e.weight / w }));
	};

	// ── the cube and the hypergraph share one query and one selected triple ──
	let query = $state(sets[0][0]);
	let pick = $state<{ j: number; k: number } | null>(null);
	const edges = $derived(strongest(query));
	const selected = $derived(pick ?? (edges[0] ? { j: edges[0].j, k: edges[0].k } : null));
	const trio = $derived(selected ? [query, selected.j, selected.k] : null);
	const trioIsSet = $derived(!!trio && isSet(layout[trio[0]], layout[trio[1]], layout[trio[2]]));

	// ── recordings: the bench curves and one trained DS-PA diagram ───────────
	interface RecordedRun {
		evalSteps: number[];
		evalAccuracy: number[];
		params: number;
	}
	interface RecordedDiagram {
		recordedAt: string;
		accuracy: number;
		instance: ChaseInstance;
		diagram: DiagramResult;
	}
	let suite = $state<SuiteId>('set');
	const recordings: Record<SuiteId, Record<string, RecordedRun> | null> = $state({
		set: null,
		chase: null
	});
	let recordedDiagram = $state.raw<RecordedDiagram | null>(null);
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
			(j) => j?.diagram && (recordedDiagram = j),
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
	<title>Polyformer | Attention over triples</title>
	<meta
		name="description"
		content="Cubic attention scores each query against pairs of keys. See the tensor, the hypergraph, a trained model's diagram and the bench, all computed in your browser."
	/>
</svelte:head>

<main class="deck">
	<!-- ── the idea ─────────────────────────────────────────────────────── -->
	<section class="intro">
		<h1>Attention that reads three tokens at once</h1>
		<div class="eq">
			<MathTex tex={'A_{ijk} = \\langle\\, Q_i,\\; K^{1}_{j} \\odot K^{2}_{k} \\,\\rangle'} />
		</div>
		<p>
			A transformer head compares a query with one key at a time. A cubic head scores it against
			every pair of keys, so one layer sees relations that exist only among three tokens. DS-PA goes
			further and learns, step by step, how many tokens to combine. Everything here was trained in a
			browser.
		</p>
		<div class="ctas">
			<a class="cta primary" href={resolve('/learn')}>Read how it works</a>
			<a class="cta" href={resolve('/compare')}>Run the bench</a>
		</div>
	</section>

	<!-- ── the tensor ───────────────────────────────────────────────────── -->
	<section class="tile cube">
		<header>
			<h2>The attention tensor</h2>
			<p>
				One block per triple <MathTex tex="(i, j, k)" /> of twelve SET cards, sized by its score.
			</p>
		</header>
		<div class="stage">
			<TensorCube
				values={volume}
				n={C}
				{query}
				{selected}
				background={TILE}
				label="The attention tensor of twelve SET cards"
				onpick={(c) => {
					query = c.i;
					pick = { j: c.j, k: c.k };
				}}
			/>
		</div>
		{#if trio}
			<footer>
				<span class="trio"
					>{#each trio as t, n (n)}<SetCard card={layout[t]} width={22} />{/each}</span
				>
				<span>
					Query <MathTex tex={`i = ${query + 1}`} />, the solid plane.
					{trioIsSet ? 'Its outlined block is a SET.' : 'The outlined block is not a SET.'}
				</span>
			</footer>
		{/if}
	</section>

	<!-- ── the trained model, every token and round ─────────────────────── -->
	<section class="tile flow">
		<header>
			<h2>What a trained DS-PA model does</h2>
			<p>
				Pointer chasing: follow links from the query to a payload. Each node learned to read the
				node it points to, so payloads climb their lists one link per round until one reaches the
				query.
			</p>
		</header>
		<div class="stage">
			{#if recordedDiagram}
				{@const d = recordedDiagram.diagram}
				<ChaseFlow
					head={d.perHead[0]}
					n={d.n}
					rounds={d.rounds}
					instance={recordedDiagram.instance}
					probs={d.probs}
				/>
			{/if}
		</div>
		<footer class="legend">
			<span
				><svg width="26" height="8" aria-hidden="true"><path d="M1 4 H25" class="k-hop" /></svg
				>reads another token</span
			>
			<span
				><svg width="26" height="8" aria-hidden="true"><path d="M1 4 H25" class="k-carry" /></svg
				>keeps its state</span
			>
			<span><b class="k-reg">4</b>payload a state holds</span>
			<span class="lit-note">Bright: what the answer depends on</span>
		</footer>
	</section>

	<!-- ── the same cards as a hypergraph ───────────────────────────────── -->
	<section class="tile graph">
		<header>
			<h2>The same cards as a hypergraph</h2>
			<p>
				Every SET is a membrane; the lit triangle is the query's strongest triple. Click a card.
			</p>
		</header>
		<div class="stage">
			<Hypergraph3D
				{layout}
				{query}
				{edges}
				{selected}
				{sets}
				background={TILE}
				onquery={(q) => {
					query = q;
					pick = null;
				}}
				onedge={(e) => (pick = e)}
			/>
		</div>
	</section>

	<!-- ── the bench ────────────────────────────────────────────────────── -->
	<section class="tile chart">
		<header class="row">
			<div>
				<h2>Held-out accuracy</h2>
				<p>Same data and seed for every model, recorded on WebGPU.</p>
			</div>
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
	/* One screen, four instruments: the idea, the tensor, a trained model and the bench. */
	.deck {
		display: grid;
		height: calc(100dvh - var(--bar-h));
		min-height: 640px;
		grid-template-columns: minmax(300px, 0.92fr) minmax(0, 1.5fr) minmax(320px, 1fr);
		grid-template-rows: minmax(0, 1.06fr) minmax(0, 1fr);
		grid-template-areas:
			'intro flow graph'
			'cube flow chart';
		gap: 12px;
		padding: 12px 16px 16px;
	}

	/* ── the idea ──────────────────────────────────────────────────────── */
	.intro {
		grid-area: intro;
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 0 14px 0 10px;
	}
	h1 {
		margin: 0;
		font-size: clamp(28px, 4.6vh, 46px);
		font-weight: 500;
		line-height: 1.04;
		letter-spacing: -0.024em;
		text-wrap: balance;
	}
	.eq {
		margin: 2.6vh 0 1.8vh;
		font-size: clamp(18px, 2.5vh, 24px);
	}
	.intro p {
		margin: 0;
		max-width: 44ch;
		font-size: clamp(13px, 1.65vh, 15px);
		line-height: 1.58;
		color: var(--color-ink-2);
	}
	.ctas {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-top: 2.6vh;
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
		background: var(--color-well);
		overflow: hidden;
	}
	.tile header {
		position: relative;
		z-index: 2;
		padding: 13px 16px 0;
		pointer-events: none;
	}
	.tile header.row {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
		pointer-events: auto;
	}
	h2 {
		margin: 0;
		font-size: var(--text-ui);
		font-weight: 500;
		color: var(--color-ink);
	}
	.tile header p {
		margin: 3px 0 0;
		max-width: 62ch;
		font-size: var(--text-xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.stage {
		position: relative;
		flex: 1;
		min-height: 0;
	}
	.tile footer {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 0 16px 12px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.trio {
		display: inline-flex;
		gap: 3px;
		flex: none;
	}

	.cube {
		grid-area: cube;
	}
	.graph {
		grid-area: graph;
	}
	.flow {
		grid-area: flow;
	}
	.flow .stage {
		margin: 4px 10px 0 4px;
	}
	.cube .stage {
		margin-bottom: 30px;
	}
	.legend {
		flex-wrap: wrap;
		gap: 6px 18px !important;
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 7px;
	}
	.legend svg {
		display: block;
	}
	.k-hop,
	.k-carry {
		stroke: var(--color-ink);
		stroke-width: 1.6;
	}
	.k-carry {
		stroke-dasharray: 3 4;
		stroke-width: 1.2;
	}
	.k-reg {
		display: inline-grid;
		place-items: center;
		width: 20px;
		height: 16px;
		border-radius: 4px;
		background: #2c2c2c;
		color: var(--color-ink);
		font-size: 10px;
		font-weight: 400;
	}
	.lit-note {
		margin-left: auto;
	}

	/* ── the bench ─────────────────────────────────────────────────────── */
	.chart {
		grid-area: chart;
	}
	.plot {
		flex: 1;
		min-height: 0;
		padding: 6px 8px 0 0;
	}
	.board {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 3px 16px;
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

	/* short laptop screens: the tensor tile keeps its picture and drops the caption */
	@media (max-height: 860px) and (min-width: 1101px) {
		.cube footer {
			display: none;
		}
		.cube .stage {
			margin-bottom: 18px;
		}
	}

	/* ── smaller screens scroll, one instrument after another ──────────── */
	@media (max-width: 1100px) {
		.deck {
			height: auto;
			grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
			grid-template-rows: auto 640px 380px 400px;
			grid-template-areas:
				'intro intro'
				'flow flow'
				'cube graph'
				'chart chart';
		}
		.intro {
			padding: 28px 8px 20px;
		}
	}
	@media (max-width: 700px) {
		.deck {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: auto 620px 380px 380px 420px;
			grid-template-areas: 'intro' 'flow' 'cube' 'graph' 'chart';
			padding: 8px 12px 16px;
		}
		.lit-note {
			margin-left: 0;
		}
	}
</style>
