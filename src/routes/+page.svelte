<script lang="ts">
	import { onMount } from 'svelte';
	import { asset, resolve } from '$app/paths';
	import { CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import { SUITES, type SuiteId } from '#lib/engine/runs.ts';
	import { querySlice, topHyperedges } from '#lib/explore/analysis.ts';
	import { exactProbe, scoreSlice } from '#lib/explore/exact.ts';
	import { dealLayout, findSets, LAYOUT_SIZE, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import Icon from '#lib/ui/Icon.svelte';
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { Pause, Play } from '#lib/ui/icons.ts';
	import { flowGroups, heldPayloads } from '#lib/viz/chaseFlow.ts';
	import DiagramFlow from '#lib/viz/DiagramFlow.svelte';
	import FlowLegend from '#lib/viz/FlowLegend.svelte';
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

	// ── the cube, the hypergraph and the trained model share one query card ──
	let query = $state(sets[0][0]);
	let pick = $state<{ j: number; k: number } | null>(null);
	const edges = $derived(strongest(query));
	const selected = $derived(pick ?? (edges[0] ? { j: edges[0].j, k: edges[0].k } : null));

	// ── the tour: every card in a SET, once per SET it belongs to ────────────
	interface Stop {
		i: number;
		pair: { j: number; k: number } | null;
	}
	const STOPS: Stop[] = (() => {
		const out: Stop[] = [];
		const members = [...new Set(sets.flat())].sort((a, b) => a - b);
		for (const i of members)
			for (const s of sets.filter((x) => x.includes(i))) {
				const [j, k] = s.filter((c) => c !== i);
				out.push({ i, pair: { j, k } });
			}
		// one card in no SET, to show what nothing looks like
		const loner = layout.findIndex((_, c) => !sets.some((s) => s.includes(c)));
		if (loner >= 0) out.splice(Math.ceil(out.length / 2), 0, { i: loner, pair: null });
		return out;
	})();
	const STEP_MS = 3600;
	let touring = $state(false);
	let stop = $state(0);
	let chaseStop = $state(0);
	function goTo(n: number) {
		stop = (n + STOPS.length) % STOPS.length;
		query = STOPS[stop].i;
		pick = STOPS[stop].pair;
	}
	/** Anything the visitor clicks takes over from the tour. */
	function takeOver() {
		touring = false;
	}
	function choose(card: number) {
		takeOver();
		query = card;
		pick = null;
	}
	onMount(() => {
		goTo(0);
		touring = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
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

	// ── recordings: bench curves and two trained DS-PA diagrams ──────────────
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
		chase: null
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
		content="Higher-order attention: cubic heads that read triples and DS-PA, which learns how many tokens to combine. See the tensor, the hypergraph, a trained model and the bench, all computed in your browser."
	/>
</svelte:head>

<main class="deck">
	<!-- ── the idea ─────────────────────────────────────────────────────── -->
	<section class="intro">
		<h1>Higher-order attention</h1>
		<div class="eq">
			<MathTex
				display
				tex={'\\begin{aligned} A_{ij} &= \\langle Q_i,\\, K_j \\rangle && \\text{pairs} \\\\ A_{ijk} &= \\langle Q_i,\\, K^{1}_{j} \\odot K^{2}_{k} \\rangle && \\text{triples} \\end{aligned}'}
			/>
		</div>
		<p>
			A transformer head scores a query against one key at a time, so it sees pairs. Higher-order
			heads score whole tuples: cubic attention reads the query with every pair of keys, and DS-PA
			learns how many tokens each step should combine. On tasks built from triples and chains, both
			win with fewer layers and fewer parameters.
		</p>
		<p class="small">
			Every model on this page was trained in a browser with jax-js. There is no server.
		</p>
		<div class="ctas">
			<a class="cta primary" href={resolve('/learn')}>Read how it works</a>
			<a class="cta" href={resolve('/explore')}>Explore the models</a>
		</div>
		<div class="tour" aria-label="Tour of the SETs on the table">
			<button
				class="tour-btn"
				aria-pressed={touring}
				onclick={() => (touring = !touring)}
				title={touring ? 'Pause the tour' : 'Play the tour'}
			>
				<Icon icon={touring ? Pause : Play} size={13} />
				{touring ? 'Touring the SETs' : 'Tour paused'}
			</button>
			<span class="dots">
				{#each STOPS as s, n (n)}
					<button
						class="dot"
						class:on={n === stop}
						class:loner={!s.pair}
						aria-label="Card {s.i + 1}{s.pair
							? ` with cards ${s.pair.j + 1} and ${s.pair.k + 1}`
							: ', in no SET'}"
						onclick={() => {
							takeOver();
							goTo(n);
						}}
					></button>
				{/each}
			</span>
		</div>
	</section>

	<!-- ── the tensor ───────────────────────────────────────────────────── -->
	<section class="tile cube">
		<header>
			<h2>The attention tensor</h2>
			<p>
				Every triple of the twelve cards gets one score, a block sized by its value; the solid plane
				is the query's slice. This hand-built head counts the attributes <MathTex tex="m" /> where the
				three cards fail, so it scores 4 exactly on a SET:
			</p>
			<div class="t-math">
				<MathTex
					tex={'A_{ijk} = \\sum_{t=1}^{4} \\cos \\tfrac{2\\pi}{3}\\big(a_t + b_t + c_t\\big) = 4 - \\tfrac{3}{2}\\, m_{ijk}'}
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
				The same cards. The weight lands on triangles, not edges: the query spreads one softmax over
				every pair and reads the product of their values. Each SET on the table is a membrane; the
				lit one is where the weight went.
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

	<!-- ── what a trained DS-PA model does ──────────────────────────────── -->
	<section class="tile flow">
		<header class="row">
			<div>
				<h2>What a trained DS-PA model does</h2>
				<p>
					Each round, one softmax picks what a token reads: its value, one token, two at once or a
					virtual mode.
					{#if flowTask === 'set'}
						On SET, every card in a SET learned to read its two partners at one cubic vertex.
					{:else}
						On pointer chasing, every node learned to read the node it points to.
					{/if}
				</p>
			</div>
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
			<div>
				<h2>Held-out accuracy</h2>
				<p>
					{#if suite === 'set'}
						Each card is labelled by whether it belongs to a SET on the table. One cubic layer
						reaches 100%; two standard layers, with more parameters, reach 64%.
					{:else}
						The query must return the payload at the end of its start node's list. DS-PA reaches
						100% with 61k parameters; three standard layers reach 94% with 154k.
					{/if}
				</p>
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
		<div class="t-math pad">
			{#if suite === 'set'}
				<MathTex
					tex={'y_i = \\mathbf{1}\\big[\\, \\exists\\, j,k :\\ \\{i,j,k\\} \\text{ is a SET} \\,\\big]'}
				/>
			{:else}
				<MathTex
					tex={'\\hat y = \\text{payload}\\big(\\text{next}^{\\,h}(\\text{start})\\big),\\quad h \\le 3'}
				/>
			{/if}
		</div>
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
	.eq {
		margin: 2.4vh 0 1.6vh;
		font-size: clamp(15px, 2.1vh, 19px);
		color: var(--color-ink);
	}
	.eq :global(.katex-display) {
		margin: 0;
	}
	.intro p {
		margin: 0;
		max-width: 44ch;
		font-size: clamp(13px, 1.7vh, 15px);
		line-height: 1.6;
		color: var(--color-ink-2);
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
	.tour {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px 14px;
		margin-top: 3.4vh;
	}
	.tour-btn {
		display: inline-flex;
		align-items: center;
		gap: 7px;
		padding: 0;
		border: 0;
		background: none;
		color: var(--color-ink-3);
		font: inherit;
		font-size: var(--text-xs);
		cursor: pointer;
	}
	.tour-btn:hover,
	.tour-btn[aria-pressed='true'] {
		color: var(--color-ink-2);
	}
	.dots {
		display: inline-flex;
		gap: 5px;
	}
	.dot {
		width: 7px;
		height: 7px;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: #2a2a2a;
		cursor: pointer;
		transition:
			background 200ms ease,
			transform 200ms ease;
	}
	.dot.loner {
		background: transparent;
		box-shadow: inset 0 0 0 1px #3a3a3a;
	}
	.dot:hover {
		background: #555;
	}
	.dot.on {
		background: var(--color-ink);
		transform: scale(1.25);
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
	.cube .stage {
		margin-bottom: 22px;
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
