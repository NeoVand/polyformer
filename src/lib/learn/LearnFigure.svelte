<script lang="ts" module>
	/**
	 * Figures for the paper, one per section id. Everything is computed from the same code
	 * the app runs: the hand-built head, the operators' cost formulas, the Feynman attention
	 * sector sizes, and runs recorded with the in-browser engine. The data below is shared by
	 * every instance on the page, so it is computed once.
	 */
	import { asset } from '$app/paths';
	import { dealChase, solveChase, type ChaseInstance } from '#lib/chase/chase.ts';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import { majorityBaseline } from '#lib/engine/data.ts';
	import { pairMoment, querySlice, topHyperedges } from '#lib/explore/analysis.ts';
	import { exactProbe } from '#lib/explore/exact.ts';
	import { DECK, dealLayout, findSets, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import type { Series } from '#lib/ui/LineChart.svelte';
	import { idealChase, idealSet } from '#lib/viz/feynman.ts';
	import { zeroSumMembers } from '#lib/tasks/matchk.ts';
	import { barrierSlices, costCurves, scoreDistribution, sectorSizes, softmax } from './figures.ts';
	import { REFERENCES } from './references.ts';

	// ── one table shared by every figure ─────────────────────────────────────
	const layout: Card[] = (() => {
		const rng = mulberry32(21);
		for (;;) {
			const l = dealLayout(rng);
			if (findSets(l).length >= 3) return l;
		}
	})();
	const sets = findSets(layout);
	const query = sets[0][0];
	const inSet = layout.map((_, i) => sets.some((s) => s.includes(i)));

	// ── the puzzles, one example each ─────────────────────────────────────────
	const nine: Card[] = (() => {
		const rng = mulberry32(5);
		for (;;) {
			const l = dealLayout(rng, 9);
			const m = zeroSumMembers(l, 4);
			if (m.filter(Boolean).length >= 4 && m.filter(Boolean).length <= 6) return l;
		}
	})();
	const nineIn = zeroSumMembers(nine, 4);
	/** One group of four distinct cards on the nine-card table that sums to zero. */
	const quad = (() => {
		for (let a = 0; a < 9; a++)
			for (let b = a + 1; b < 9; b++)
				for (let c = b + 1; c < 9; c++)
					for (let d = c + 1; d < 9; d++)
						if (
							[0, 1, 2, 3].every(
								(t) => (nine[a][t] + nine[b][t] + nine[c][t] + nine[d][t]) % 3 === 0
							)
						)
							return [a, b, c, d];
		return [];
	})();
	// three lookup tables on 0…7 and a start, as in the three-hop task
	const tables = (() => {
		const rng = mulberry32(13);
		return Array.from({ length: 3 }, () => Array.from({ length: 8 }, () => Math.floor(rng() * 8)));
	})();
	const x0 = 2;
	const hops = tables.reduce((path, f) => [...path, f[path[path.length - 1]]], [x0]);
	const HX = (c: number) => 24 + c * 96;
	const HY = (v: number) => 18 + v * 24;

	// ── how a card becomes a token ───────────────────────────────────────────
	const ATTR_NAMES = ['number', 'shape', 'shading', 'colour'];
	/** The sink, then the first cards of the shared table. */
	const shown: (Card | null)[] = [null, ...layout.slice(0, 5)];
	const probe = exactProbe(layout, 3);
	const edges = topHyperedges(querySlice(probe, 0, query), 5, query);
	const top = edges[0];
	const selected = { j: top.j, k: top.k };
	const C = layout.length;
	const cubeValues = (() => {
		let lo = Infinity;
		let hi = -Infinity;
		for (const v of probe.scores)
			if (!Number.isNaN(v)) [lo, hi] = [Math.min(lo, v), Math.max(hi, v)];
		const out = new Float32Array(C * C * C);
		const n = probe.n;
		for (let i = 0; i < C; i++)
			for (let j = 0; j < C; j++)
				for (let k = 0; k < C; k++) {
					const v = probe.scores[((i + 1) * n + j + 1) * n + k + 1];
					out[(i * C + j) * C + k] = Number.isNaN(v) ? 0 : ((v - lo) / (hi - lo)) ** 3.2;
				}
		return out;
	})();

	const keyWeights = softmax([1.9, 0.3, -0.6, 1.1, -1.2, 0.2, 0.8]);
	const vecA = [0.9, -0.4, 0.7, 0.1, -0.8, 0.6, 0.2, -0.3];
	const vecB = [0.8, 0.5, 0.9, -0.2, -0.7, 0.1, 0.6, 0.4];
	const vecE = [0.7, -0.6, 0.8, 0.9, 0.9, -0.3, 0.1, -0.5];
	const triple = vecA.map((a, c) => a * vecB[c] * vecE[c]);
	const tripleSum = triple.reduce((a, b) => a + b, 0);

	const barrierQueries = [...new Set(sets.flat())].slice(0, 3);
	const barrier = barrierSlices(probe, barrierQueries);
	const moment = pairMoment(probe, 0, query);
	const scores = scoreDistribution(DECK);
	const maxShare = Math.max(...scores.map((s) => s.share));

	// cost: log–log axes over sequence length
	const COST_NS = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192];
	const cost = costCurves(COST_NS, 64, 128);
	const CW = 360;
	const CH = 240;
	const lx = (n: number) => 40 + ((Math.log2(n) - 4) / (Math.log2(8192) - 4)) * (CW - 120);
	const ly = (f: number) =>
		CH - 28 - ((Math.log10(f) - 4) / (Math.log10(4 * 8192 ** 3 * 64) - 4)) * (CH - 44);
	const poly = (key: 'pairwise' | 'cubic' | 'windowed') =>
		cost.map((c) => `${lx(c.n)},${ly(c[key])}`).join(' ');

	const sizes = sectorSizes(14, 16);
	const sizeTotal = sizes.reduce((a, s) => a + s.size, 0);
	const SHADES = [0.32, 0.95, 0.72, 0.52, 0.18];

	const majority3 = majorityBaseline('set', 600);

	const chase = (() => {
		const rng = mulberry32(8);
		let inst = dealChase(rng);
		while (solveChase(inst).hops < 3) inst = dealChase(rng);
		return inst;
	})();
	const chaseHead = idealChase(chase, 4);
	const setHead = idealSet(layout, 2);

	// recorded runs and trained models, each fetched once for the whole page
	interface RecordedRun {
		evalSteps: number[];
		evalAccuracy: number[];
	}
	// a plain cache of fetches shared by every figure on the page, never read reactively
	// eslint-disable-next-line svelte/prefer-svelte-reactivity
	const cache = new Map<string, Promise<unknown>>();
	function load<T>(path: Parameters<typeof asset>[0]): Promise<T | null> {
		if (!cache.has(path))
			cache.set(
				path,
				fetch(asset(path))
					.then((r) => (r.ok ? r.json() : null))
					.catch(() => null)
			);
		return cache.get(path) as Promise<T | null>;
	}

	const LABELS: Record<string, [string, number, string]> = {
		cubic: ['Cubic', 1, ''],
		dspa: ['Feynman', 0.86, '10 3'],
		strassen: ['Strassen', 0.72, '6 3'],
		tree: ['Tree (Columbia)', 0.56, '2 3'],
		std3: ['Standard, 3 layers', 0.6, '2 3'],
		std2: ['Standard, 2 layers', 0.48, '8 3 2 3'],
		std1: ['Standard, 1 layer', 0.38, '1 2']
	};
	const toSeries = (runs: Record<string, RecordedRun> | null, lead: string): Series[] =>
		runs
			? Object.entries(runs).map(([id, r]) => {
					const [label, tone, dash] = LABELS[id] ?? [id, 0.5, ''];
					return {
						id,
						label,
						tone: id === lead ? 1 : Math.min(tone, 0.86),
						dash: id === lead ? '' : dash,
						emphasis: id === lead,
						xs: r.evalSteps,
						ys: r.evalAccuracy
					};
				})
			: [];

	const TIMELINE = [
		{ year: 2017, ref: 'vaswani', what: 'Attention: every token scores every token' },
		{ year: 2020, ref: 'clift', what: '2-simplicial attention: a query scores pairs' },
		{ year: 2020, ref: 'seq2tens', what: 'Seq2Tens: ordered products over subsequences' },
		{ year: 2022, ref: 'development', what: 'Path development: group products along a sequence' },
		{ year: 2023, ref: 'sanford', what: 'Match3 separates pairwise from tensor attention' },
		{ year: 2023, ref: 'neo', what: 'Polyformer notebook: cubic attention, derived independently' },
		{ year: 2025, ref: 'kozachinskiy', what: 'Strassen attention: degree 2, faster' },
		{ year: 2025, ref: 'roy', what: 'Fast 2-simplicial attention at scale' },
		{ year: 2025, ref: 'path', what: 'PaTH: Householder products inside attention' },
		{ year: 2026, ref: 'chakrabarti', what: 'Poly-attention: a general scheme' },
		{
			year: 2026,
			ref: '',
			what: 'This project: Feynman, Newton and holonomy attention; order-blind ceilings'
		}
	];
	const refNo = (id: string) => REFERENCES.findIndex((r) => r.id === id) + 1;
</script>

<script lang="ts">
	import { CHASE_QUERY_POS } from '#lib/chase/chase.ts';
	import FeatureStrip from '#lib/ui/FeatureStrip.svelte';
	import Heatmap from '#lib/ui/Heatmap.svelte';
	import LineChart from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { flowGroups, heldPayloads } from '#lib/viz/chaseFlow.ts';
	import DiagramFlow from '#lib/viz/DiagramFlow.svelte';
	import FeynmanDiagram from '#lib/viz/FeynmanDiagram.svelte';
	import FlowLegend from '#lib/viz/FlowLegend.svelte';
	import Hypergraph3D from '#lib/viz/Hypergraph3D.svelte';
	import TensorCube from '#lib/viz/TensorCube.svelte';
	import { ARITY_RESULTS } from './figures.ts';
	import DiagramSum from './DiagramSum.svelte';
	import ArityFigure from '#lib/report/ArityFigure.svelte';
	import ArityUseFigure from '#lib/report/ArityUseFigure.svelte';
	import CharactersFigure from '#lib/report/CharactersFigure.svelte';
	import NewtonDemo from '#lib/report/NewtonDemo.svelte';
	import ReplicationTable from '#lib/report/ReplicationTable.svelte';
	import phaseA from '#lib/report/results/phase_a.json';
	import newtonB from '#lib/report/results/newton_b.json';
	import newtonE from '#lib/report/results/newton_e.json';
	import newtonDiag from '#lib/report/results/newton_diag.json';
	import QedDiagram from './QedDiagram.svelte';
	import ChaseLists from '#lib/ui/ChaseLists.svelte';

	let { section }: { section: string } = $props();

	let puzzle = $state<'set' | 'match4' | 'chase' | 'compose'>('set');
	let diagramTask = $state<'set' | 'chase'>('set');

	// only the figures that show recorded runs fetch them
	let recordedSet = $state.raw<Record<string, RecordedRun> | null>(null);
	let recordedChase = $state.raw<Record<string, RecordedRun> | null>(null);
	let chaseModel = $state.raw<{ instance: ChaseInstance; diagram: DiagramResult } | null>(null);
	let setModel = $state.raw<{ layout: number[][]; diagram: DiagramResult } | null>(null);
	$effect(() => {
		if (section === 'training')
			load<{ runs: Record<string, RecordedRun> }>('recorded/set.json').then(
				(j) => (recordedSet = j?.runs ?? null)
			);
		if (section === 'chase') {
			load<{ runs: Record<string, RecordedRun> }>('recorded/chase.json').then(
				(j) => (recordedChase = j?.runs ?? null)
			);
			load<{ instance: ChaseInstance; diagram: DiagramResult }>('recorded/chase-diagram.json').then(
				(j) => j?.diagram && (chaseModel = j)
			);
			load<{ layout: number[][]; diagram: DiagramResult }>('recorded/set-diagram.json').then(
				(j) => j?.diagram && (setModel = j)
			);
		}
	});

	// trained Feynman attention models, recorded in a browser, read token by token
	// the barrier heatmaps share the figure's width, three per row
	let barrierWidth = $state(420);
	const heatSize = $derived(Math.max(72, Math.min(104, Math.floor((barrierWidth - 84) / 3))));

	let learnedTask = $state<'chase' | 'set'>('chase');
	let learnedRoot = $state<number | null>(null);
	const chaseHeld = $derived(
		chaseModel
			? heldPayloads(
					chaseModel.diagram.perHead[0],
					chaseModel.diagram.n,
					chaseModel.diagram.rounds,
					chaseModel.instance
				)
			: null
	);
</script>

{#if section === 'puzzles'}
	<figure class="fig wide">
		<div class="fig-head">
			<div class="seg" role="group" aria-label="Puzzle">
				<button aria-pressed={puzzle === 'set'} onclick={() => (puzzle = 'set')}>SET</button>
				<button aria-pressed={puzzle === 'match4'} onclick={() => (puzzle = 'match4')}
					>Match-4</button
				>
				<button aria-pressed={puzzle === 'chase'} onclick={() => (puzzle = 'chase')}
					>Pointer chase</button
				>
				<button aria-pressed={puzzle === 'compose'} onclick={() => (puzzle = 'compose')}
					>Three-hop</button
				>
			</div>
		</div>
		{#if puzzle === 'set' || puzzle === 'match4'}
			{@const cards = puzzle === 'set' ? layout : nine}
			{@const label = puzzle === 'set' ? inSet : nineIn}
			{@const lit = puzzle === 'set' ? sets[0] : quad}
			<div class="table-grid" class:three={puzzle === 'match4'}>
				{#each cards as card, i (i)}
					<div class="slot">
						<SetCard {card} width={44} selected={lit.includes(i)} dim={!lit.includes(i)} />
						<span class="answer" class:yes={label[i]} aria-label={label[i] ? 'yes' : 'no'}></span>
					</div>
				{/each}
			</div>
			<figcaption>
				{#if puzzle === 'set'}
					Twelve cards, one table. A filled dot under a card means it is in at least one SET: that
					yes-or-no is what the network must output for every card. The bright cards are one SET.
				{:else}
					Nine cards. A filled dot means the card is in some group of four that adds up to a
					multiple of 3 in every attribute; the bright cards are one such group.
				{/if}
			</figcaption>
		{:else if puzzle === 'chase'}
			<div class="chase-wrap"><ChaseLists instance={chase} /></div>
			<figcaption>
				Twelve nodes in linked lists, each with its payload as the small number. The query names a
				start node (underlined); the answer is the payload at the end of its list, here
				{solveChase(chase).hops} hops away.
			</figcaption>
		{:else}
			<svg
				class="hops"
				viewBox="0 0 336 212"
				role="img"
				aria-label="Three lookup tables and a path"
			>
				{#each [0, 1, 2] as c (c)}
					{#each tables[c] as to, from (from)}
						<line
							class="map"
							class:on={hops[c] === from}
							x1={HX(c) + 6}
							y1={HY(from)}
							x2={HX(c + 1) - 6}
							y2={HY(to)}
						/>
					{/each}
					<text class="fn" x={(HX(c) + HX(c + 1)) / 2} y="208">f{c + 1}</text>
				{/each}
				{#each [0, 1, 2, 3] as c (c)}
					{#each Array.from({ length: 8 }, (_, v) => v) as v (v)}
						<circle class="num-dot" class:on={hops[c] === v} cx={HX(c)} cy={HY(v)} r="4" />
					{/each}
				{/each}
				{#each Array.from({ length: 8 }, (_, v) => v) as v (v)}
					<text class="val" x="8" y={HY(v) + 3.5}>{v}</text>
				{/each}
			</svg>
			<figcaption>
				Three lookup tables, each sending every number from 0 to 7 somewhere. Starting from x = {x0},
				the answer is f3(f2(f1({x0}))) = {hops[3]}.
			</figcaption>
		{/if}
	</figure>
{:else if section === 'encoding'}
	<figure class="fig wide">
		<svg class="tokens" viewBox="0 0 360 236" role="img" aria-label="The first tokens of a table">
			{#each ATTR_NAMES as a, r (a)}
				<text class="attr" x="62" y={70 + r * 24 + 4} text-anchor="end">{a}</text>
			{/each}
			{#each shown as card, t (t)}
				{@const x0 = 74 + t * 46}
				<text class="pos" x={x0 + 17} y="14" text-anchor="middle">{t}</text>
				{#if card}
					<foreignObject x={x0 + 5} y="22" width="24" height="24">
						<SetCard {card} width={24} />
					</foreignObject>
				{:else}
					<text class="sinkname" x={x0 + 17} y="39" text-anchor="middle">sink</text>
				{/if}
				{#each [0, 1, 2, 3] as attr (attr)}
					{#each [0, 1, 2, 3] as v (v)}
						<rect
							class="onehot"
							class:hot={(card ? card[attr] : 3) === v}
							x={x0 + v * 9}
							y={62 + attr * 24}
							width="7"
							height="16"
							rx="1"
						/>
					{/each}
				{/each}
				<text class="lab" x={x0 + 17} y="174" text-anchor="middle"
					>{card ? (inSet[t - 1] ? 'yes' : 'no') : '–'}</text
				>
			{/each}
			<text class="attr" x="62" y="178" text-anchor="end">label</text>
			<text class="more" x="352" y="118" text-anchor="end">…</text>
			<text class="note" x="74" y="206"
				>each column: one token, 4 attributes × 4 slots = 16 numbers</text
			>
			<text class="note" x="74" y="222">→ mapped to width 64, plus a position vector</text>
		</svg>
		<figcaption>
			The first tokens of the twelve-card table. Each attribute is one-hot over four slots: the
			three values and a fourth that only the sink uses. The bottom row is the label the network is
			trained to output.
		</figcaption>
	</figure>
{:else if section === 'pairwise'}
	<figure class="fig">
		<svg viewBox="0 0 420 300" class="star" aria-label="A query scoring seven keys">
			{#each keyWeights as w, t (t)}
				{@const y = 30 + t * 40}
				<path
					d="M80,150 L330,{y}"
					stroke-width={0.8 + 7 * w}
					stroke-opacity={0.25 + 0.75 * Math.sqrt(w)}
				/>
				<circle cx="336" cy={y} r="5" class="node" />
				<text x="350" y={y + 4} class="w num">{pct(w, 0)}</text>
			{/each}
			<circle cx="74" cy="150" r="9" class="node q" />
		</svg>
		<figcaption>
			<MathTex tex={'P_{ij}'} /> for one query over seven keys. Every line joins exactly two tokens.
		</figcaption>
	</figure>
{:else if section === 'product'}
	<figure class="fig">
		<div class="strips">
			<MathTex tex="a" /><FeatureStrip
				values={vecA}
				max={1}
				cell={24}
				height={24}
				label="Vector a"
			/>
			<MathTex tex="b" /><FeatureStrip
				values={vecB}
				max={1}
				cell={24}
				height={24}
				label="Vector b"
			/>
			<MathTex tex="e" /><FeatureStrip
				values={vecE}
				max={1}
				cell={24}
				height={24}
				label="Vector e"
			/>
			<MathTex tex="a \odot b \odot e" /><FeatureStrip
				values={triple}
				max={0.6}
				cell={24}
				height={24}
				label="Elementwise product"
			/>
		</div>
		<p class="sum"><MathTex tex={`\\langle a, b, e\\rangle = ${tripleSum.toFixed(2)}`} /></p>
		<figcaption>
			Bright is positive, dark is negative. A coordinate counts only where all three are large.
		</figcaption>
	</figure>
{:else if section === 'cubic'}
	<figure class="fig tall">
		<div class="three"><TensorCube values={cubeValues} n={C} {query} {selected} /></div>
		<figcaption>
			The <MathTex tex="12 \times 12 \times 12" /> score tensor of one table. The lit slab is query {query +
				1}'s slice; the brightest voxel is the pair that completes a SET with it.
		</figcaption>
	</figure>
{:else if section === 'cost'}
	<figure class="fig">
		<svg viewBox="0 0 {CW} {CH}" class="cost" aria-label="Cost of one head against sequence length">
			{#each [16, 128, 1024, 8192] as n (n)}
				<line x1={lx(n)} x2={lx(n)} y1="12" y2={CH - 28} class="grid" />
				<text x={lx(n)} y={CH - 12} class="tick">{n.toLocaleString('en-US')}</text>
			{/each}
			<line x1={lx(16)} x2={lx(16)} y1="12" y2={CH - 28} class="mark" />
			<polyline points={poly('pairwise')} class="c pair" />
			<polyline points={poly('windowed')} class="c win" />
			<polyline points={poly('cubic')} class="c cub" />
			<text x={lx(8192) + 6} y={ly(cost.at(-1)!.cubic) + 4} class="lab">cubic</text>
			<text x={lx(8192) + 6} y={ly(cost.at(-1)!.windowed) - 3} class="lab dim">window 128</text>
			<text x={lx(8192) + 6} y={ly(cost.at(-1)!.pairwise) + 12} class="lab dim">pairwise</text>
			<text x={lx(16) + 4} y="22" class="tick start">tasks here</text>
		</svg>
		<figcaption>
			FLOPs for one head of width 64, on log–log axes. Cubic grows as <MathTex tex="n^3" />;
			restricting each role to a window of 128 keys brings it back to linear in <MathTex tex="n" />.
			The tasks here have 13 or 14 tokens.
		</figcaption>
	</figure>
{:else if section === 'degree2'}
	<figure class="fig">
		<div class="tris">
			{#each [{ name: 'Standard', e: [1, 0, 0], f: false }, { name: 'Tree', e: [1, 1, 0], f: false }, { name: 'Strassen', e: [1, 1, 1], f: false }, { name: 'Cubic', e: [1, 1, 1], f: true }] as t (t.name)}
				<div class="tri">
					<svg viewBox="0 0 120 108" aria-hidden="true">
						{#if t.f}<polygon points="60,14 14,94 106,94" class="face" />{/if}
						<line x1="60" y1="14" x2="14" y2="94" class="edge" class:on={t.e[0]} />
						<line x1="14" y1="94" x2="106" y2="94" class="edge" class:on={t.e[1]} />
						<line x1="60" y1="14" x2="106" y2="94" class="edge" class:on={t.e[2]} />
						<circle cx="60" cy="14" r="6" class="v q" />
						<circle cx="14" cy="94" r="5" class="v" />
						<circle cx="106" cy="94" r="5" class="v" />
					</svg>
					<span>{t.name}</span>
				</div>
			{/each}
		</div>
		<div class="tri-keys">
			<MathTex tex="i" /> query (top), <MathTex tex="j" /> and <MathTex tex="k" /> keys
		</div>
		<figcaption>
			Which edges of the triangle carry a score. Degree-2 designs light up edges; the cubic head
			fills the face with one term that depends on all three tokens at once.
		</figcaption>
	</figure>
{:else if section === 'barrier'}
	<figure class="fig">
		<div class="grid3" bind:clientWidth={barrierWidth}>
			<span class="g-label">Degree 2</span>
			{#each barrier.degree2 as m, q (q)}
				<Heatmap
					values={m}
					rows={12}
					cols={12}
					size={heatSize}
					scale="signed"
					max={barrier.max2}
					label="Degree-2 slice"
				/>
			{/each}
			<span class="g-label">Cubic</span>
			{#each barrier.cubic as m, q (q)}
				<Heatmap
					values={m}
					rows={12}
					cols={12}
					size={heatSize}
					scale="signed"
					max={barrier.maxCubic}
					label="Cubic slice"
				/>
			{/each}
			<span></span>
			{#each barrierQueries as q (q)}<span class="q-label num">query {q + 1}</span>{/each}
		</div>
		<figcaption>
			Each query's pair scores with row and column averages removed (double centring), for three
			queries. A degree-2 head, here with random edge scores, gives the same table three times; the
			hand-built cubic head gives three different ones.
		</figcaption>
	</figure>
{:else if section === 'set'}
	<figure class="fig tall">
		<div class="three">
			<Hypergraph3D
				{layout}
				{query}
				edges={edges.map((e) => ({ j: e.j, k: e.k, weight: e.weight / top.weight }))}
				{selected}
				{sets}
			/>
		</div>
		<figcaption>
			The table as a hypergraph. Faint membranes are its {sets.length} SETs; the bright one is where query
			{query + 1} puts its weight.
		</figcaption>
	</figure>
{:else if section === 'head'}
	<figure class="fig">
		<div
			class="hist"
			role="img"
			aria-label="Distribution of the hand-built head's scores over every triple"
		>
			{#each scores as s (s.m)}
				<div class="h-col">
					<span class="h-val num">{pct(s.share, 1)}</span>
					<div
						class="h-bar"
						class:set={s.m === 0}
						style:height="{8 + (s.share / maxShare) * 150}px"
					></div>
					<span class="h-score"><MathTex tex={s.score.toString()} /></span>
					<span class="h-m num">{s.m === 0 ? 'SET' : `${s.m} broken`}</span>
				</div>
			{/each}
		</div>
		<figcaption>
			The hand-built head's score on all 85,320 triples of distinct cards. Exactly the 1,080 SETs
			score 4; every other triple scores 2.5 or less, a margin of 1.5 that the softmax temperature
			turns into near-certainty.
		</figcaption>
	</figure>
{:else if section === 'binding'}
	<figure class="fig">
		<Heatmap
			values={moment}
			rows={probe.dh}
			cols={probe.dh}
			size={300}
			scale="signed"
			diagonal
			label="Pair moment"
		/>
		<figcaption>
			The pair moment <MathTex tex="M_i" /> of the hand-built head for query {query + 1}: 16 value
			channels in role 1 against 16 in role 2. The outlined diagonal is the Hadamard output <MathTex
				tex="Y_i"
			/>.
		</figcaption>
	</figure>
{:else if section === 'training'}
	<figure class="fig wide">
		{#if recordedSet}
			<LineChart
				label="Held-out accuracy on SET, recorded"
				series={toSeries(recordedSet, 'cubic')}
				xMax={4000}
				yMin={0.4}
				yMax={1}
				yTicks={[0.4, 0.6, 0.8, 1]}
				formatY={(v) => pct(v, 0)}
				formatX={(v) => v.toLocaleString('en-US')}
				xLabel="Training step"
				reference={{ y: majority3, label: `Majority ${pct(majority3, 0)}` }}
				height={300}
			/>
		{/if}
		<figcaption>
			Held-out accuracy on SET, one layer each, recorded with this app's engine on WebGPU (seed 0).
			Cubic reaches 95% by step 500 and 100% after; Feynman attention by step 700.
		</figcaption>
	</figure>
{:else if section === 'arity'}
	<figure class="fig">
		<div class="results">
			{#each ARITY_RESULTS.tasks as t (t.id)}
				{@const base = t.id === 'match3' ? majority3 : ARITY_RESULTS.majority4}
				<h4>{t.label}</h4>
				{#each ARITY_RESULTS.models as m (m.id)}
					{@const acc = ARITY_RESULTS.accuracy[t.id][m.id]}
					<span class="m-label">{m.label}</span>
					<div class="track">
						<span class="base" style:left="{base * 100}%"></span>
						{#if acc !== null}<span class="fill" class:win={acc > 0.99} style:width="{acc * 100}%"
							></span>{/if}
					</div>
					<span class="m-val num">{acc === null ? 'not run' : pct(acc, 0)}</span>
				{/each}
			{/each}
		</div>
		<figcaption>
			Cloud runs, one layer, 4,000 steps, one seed, scored as the share of cards labelled correctly.
			The four-card task uses tables of eight cards, where answering no is right 63% of the time;
			the tick marks that rate.
		</figcaption>
	</figure>
{:else if section === 'feynman'}
	<figure class="fig">
		<div class="atlas">
			<span class="order"><MathTex tex="e^2" /><small>one photon exchanged</small></span>
			<div class="row">
				<div class="cell"><QedDiagram kind="tree-t" width={120} /><span>exchange</span></div>
				<div class="cell">
					<QedDiagram kind="tree-u" width={120} /><span>crossed exchange</span>
				</div>
			</div>
			<span class="order"><MathTex tex="e^4" /><small>one loop</small></span>
			<div class="row">
				<div class="cell">
					<QedDiagram kind="vacuum" width={120} /><span>vacuum polarization</span>
				</div>
				<div class="cell">
					<QedDiagram kind="vertex" width={120} /><span>vertex correction</span>
				</div>
				<div class="cell"><QedDiagram kind="box" width={120} /><span>box</span></div>
			</div>
		</div>
		<figcaption>
			Electron–electron scattering, expanded in the coupling. Each vertex costs a factor of <MathTex
				tex="e"
			/>, so diagrams with more vertices count for less: at <MathTex tex="\alpha \approx 1/137" /> each
			extra pair of vertices is about a hundred times smaller.
		</figcaption>
	</figure>
{:else if section === 'dyson'}
	<figure class="fig">
		<div class="dyson">
			<DiagramSum
				lhs="dressed"
				width={110}
				more={false}
				terms={[{ kind: 'bare' }, { kind: 'bare-sigma-dressed' }]}
			/>
			<MathTex display tex="G = G_0 + G_0\,\Sigma\,G" />
			<span class="unroll">unrolled</span>
			<DiagramSum
				lhs="dressed"
				width={84}
				terms={[
					{ kind: 'bare' },
					{ kind: 'bare-sigma-bare' },
					{ kind: 'bare-sigma-bare-sigma-bare' }
				]}
			/>
		</div>
		<figcaption>
			The Dyson equation for a dressed propagator (double line) in terms of the bare one (single
			line) and the self-energy (hatched blob). One self-consistent equation stands for the whole
			infinite series below it.
		</figcaption>
	</figure>
{:else if section === 'diagrams'}
	<figure class="fig tall">
		<div class="fig-head">
			<div class="seg" role="group" aria-label="Example">
				<button aria-pressed={diagramTask === 'set'} onclick={() => (diagramTask = 'set')}
					>SET</button
				>
				<button aria-pressed={diagramTask === 'chase'} onclick={() => (diagramTask = 'chase')}
					>Pointer chase</button
				>
			</div>
		</div>
		<div class="three">
			{#if diagramTask === 'set'}
				<FeynmanDiagram head={setHead} n={C + 1} rounds={2} modes={0} root={query + 1}>
					{#snippet row(t)}{#if t > 0}<SetCard card={layout[t - 1]} width={22} />{/if}{/snippet}
				</FeynmanDiagram>
			{:else}
				<FeynmanDiagram head={chaseHead} n={14} rounds={4} modes={0} root={13} output="\hat y">
					{#snippet row(t)}<MathTex
							tex={t === 13 ? 'q' : `v_{${chase.nodes[t - 1]?.id}}`}
						/>{/snippet}
				</FeynmanDiagram>
			{/if}
		</div>
		<figcaption>
			The ideal computation tree. On SET a card needs one cubic vertex; on pointer chasing the query
			needs a chain of hops as long as its list.
		</figcaption>
	</figure>
{:else if section === 'sectors'}
	<figure class="fig">
		<div class="mass">
			{#each [false, true] as balanced (balanced)}
				<span class="mass-label">{balanced ? 'With' : 'Without'} <MathTex tex="\mu_s" /></span>
				<div class="mass-bar">
					{#each sizes as s, i (s.id)}
						{@const share = balanced ? 1 / sizes.length : s.size / sizeTotal}
						<span
							style:flex-grow={share}
							style:background="rgb({255 * SHADES[i]}
							{255 * SHADES[i]}
							{255 * SHADES[i]})"
							title="{s.label} {pct(share, 1)}"
						></span>
					{/each}
				</div>
			{/each}
		</div>
		<div class="mass-keys">
			{#each sizes as s, i (s.id)}
				<span
					><i style:background="rgb({255 * SHADES[i]} {255 * SHADES[i]} {255 * SHADES[i]})"
					></i>{s.label}
					<b class="num">{s.size}</b></span
				>
			{/each}
		</div>
		<figcaption>
			Prior mass per sector for the query in pointer chase (14 tokens, 16 modes), before any
			learning. Without the bias, cubic and exchange start with 99% of the mass because they offer
			the most options.
		</figcaption>
	</figure>
{:else if section === 'chase'}
	<figure class="fig wide">
		<div class="fig-head">
			<div class="seg" role="group" aria-label="Task">
				<button
					aria-pressed={learnedTask === 'chase'}
					onclick={() => ((learnedTask = 'chase'), (learnedRoot = null))}>Pointer chase</button
				>
				<button
					aria-pressed={learnedTask === 'set'}
					onclick={() => ((learnedTask = 'set'), (learnedRoot = null))}>SET</button
				>
			</div>
		</div>
		{#if learnedTask === 'chase' && chaseModel}
			{@const d = chaseModel.diagram}
			{@const inst = chaseModel.instance}
			<DiagramFlow
				head={d.perHead[0]}
				n={d.n}
				rounds={d.rounds}
				rows={flowGroups(inst)}
				root={learnedRoot ?? CHASE_QUERY_POS}
				onroot={(t) => (learnedRoot = t)}
				pitch={18}
				column={76}
				annotate={(r, t) => {
					const v = chaseHeld?.[r]?.[t];
					return v === null || v === undefined ? null : String(v);
				}}
				output={(learnedRoot ?? CHASE_QUERY_POS) === CHASE_QUERY_POS
					? `\\hat y = ${d.probs.indexOf(Math.max(...d.probs))}`
					: `\\Phi^{${d.rounds}}`}
			>
				{#snippet label(t)}
					{#if t === CHASE_QUERY_POS}<MathTex tex="q" />{:else}{inst.nodes[t - 1].id}{/if}
				{/snippet}
			</DiagramFlow>
		{:else if learnedTask === 'set' && setModel}
			{@const d = setModel.diagram}
			{@const cards = setModel.layout as unknown as Card[]}
			<DiagramFlow
				head={d.perHead[0]}
				n={d.n}
				rounds={d.rounds}
				rows={[Array.from({ length: cards.length }, (_, i) => i + 1)]}
				root={learnedRoot ?? d.token}
				onroot={(t) => (learnedRoot = t)}
				pitch={19}
				column={120}
			>
				{#snippet label(t)}<SetCard card={cards[t - 1]} width={15} />{/snippet}
			</DiagramFlow>
		{/if}
		<div class="learned-key"><FlowLegend compact /></div>
		<p class="learned-note">
			{#if learnedTask === 'chase'}
				A Feynman attention model trained in a browser, every token and round. Each node learned to
				read the node it points to, so each list's payload climbs one link per round, and the query
				reads its start at the last round. Hover a row to see what that token reads.
			{:else}
				The same model family trained on SET. Each card in a SET reads its two partners through one
				cubic vertex, the triple a pairwise head cannot see. Cards in no SET keep their own value.
			{/if}
		</p>
		{#if recordedChase}
			<LineChart
				label="Held-out accuracy on pointer chase, recorded"
				series={toSeries(recordedChase, 'dspa')}
				xMax={4000}
				yMin={0}
				yMax={1}
				yTicks={[0, 0.25, 0.5, 0.75, 1]}
				formatY={(v) => pct(v, 0)}
				formatX={(v) => v.toLocaleString('en-US')}
				xLabel="Training step"
				height={300}
			/>
		{/if}
		<figcaption>
			Held-out accuracy on pointer chase, recorded with this app's engine. One Feynman attention
			layer (61k parameters) reaches 95% by step 250 and 100% after; three standard layers (154k)
			reach 94%.
		</figcaption>
	</figure>
{:else if section === 'composition'}
	<figure class="fig wide">
		<ReplicationTable
			rows={[...phaseA, ...newtonB, ...newtonE]}
			tasks={[
				{ id: 'zs3', label: 'Match-3' },
				{ id: 'zs4', label: 'Match-4' },
				{ id: 'zs5', label: 'Match-5' }
			]}
			models={[
				{ id: 'standard-3L', label: 'Standard, 3 layers' },
				{ id: 'cubic', label: 'Cubic' },
				{ id: 'quartic', label: 'Dense quartic' },
				{ id: 'dspa4', label: 'Feynman' },
				{ id: 'dspa5-d192', label: 'Feynman, Newton parts, width 192' },
				{ id: 'newton-K6-r256-h4-shared-fnorm', label: 'Newton attention' }
			]}
			caption="Balanced accuracy, chance 50%. Mean of three seeds; each dot is one seed."
		/>
		<figcaption>
			Only an operator with a native k-way term leaves chance on Match-k. Feynman attention with
			every part of the Newton construction, wider than the group, does not. Newton attention offers
			every arity natively.
		</figcaption>
	</figure>
{:else if section === 'characters'}
	<figure class="fig wide">
		<ArityFigure panels={['a', 'b']} />
		<figcaption>
			Top: one card in relations of three arities, each a zero sum. Bottom: under one character a
			SET's phases multiply to 1; under all 81 they agree, while any other triple's cancel.
		</figcaption>
	</figure>
{:else if section === 'newton'}
	<figure class="fig wide">
		<NewtonDemo />
	</figure>
{:else if section === 'newtonattn'}
	<figure class="fig wide">
		<ArityUseFigure rows={newtonDiag.knock} />
		<CharactersFigure examples={newtonDiag.examples} points={newtonDiag.scatter} />
		<figcaption>
			Top: the share of accuracy lost when one arity of a trained layer is switched off. Bottom:
			learned phases of the 81 cards on four channels fall into three clusters, a character; and
			accuracy rises with the number of characters a run finds, exact when it has all 40.
		</figcaption>
	</figure>
{:else if section === 'transfer'}
	<figure class="fig wide">
		<ReplicationTable
			rows={[
				...newtonB
					.filter((r) => r.model === 'newton-K6-r256-h4')
					.map((r) => ({ ...r, model: 'alone' })),
				...newtonE
					.filter((r) => r.model === 'newton-K6-r256-h4-shared-fnorm')
					.map((r) => ({ ...r, model: 'alone-final' })),
				...newtonDiag.mixed
			]}
			tasks={[
				{ id: 'zs3', label: 'Match-3' },
				{ id: 'zs4', label: 'Match-4' },
				{ id: 'zs5', label: 'Match-5' }
			]}
			models={[
				{ id: 'alone', label: 'First version, each task alone' },
				{ id: 'mix345-r256-s6000', label: 'First version, trained together' },
				{ id: 'alone-final', label: 'Newton attention, each task alone' },
				{ id: 'mix345-r256-shared-fnorm-s6000', label: 'Newton attention, trained together' }
			]}
			caption="Balanced accuracy, chance 50%. Mean of three seeds; each dot is one seed. Rank 256, 6,000 steps."
		/>
		<figcaption>
			One layer trained on three arities at once, scored on each. Each arity gets a third of the
			data and still does better than a layer trained on it alone.
		</figcaption>
	</figure>
{:else}
	<figure class="fig">
		<ol class="timeline">
			{#each TIMELINE as e, i (i)}
				<li class:ours={!e.ref || e.ref === 'neo'}>
					<span class="t-year num">{e.year}</span>
					<span class="t-dot" aria-hidden="true"></span>
					<span class="t-what"
						>{e.what}{#if e.ref}&nbsp;<span class="t-ref">[{refNo(e.ref)}]</span>{/if}</span
					>
				</li>
			{/each}
		</ol>
		<figcaption>
			Where the pieces come from. Filled dots are this project and its origin.
		</figcaption>
	</figure>
{/if}

<style>
	.fig {
		display: grid;
		justify-items: center;
		gap: 16px;
		width: 100%;
		animation: arrive 360ms ease both;
	}
	.fig.tall {
		height: clamp(360px, 72vw, 540px);
		grid-template-rows: minmax(0, 1fr) auto;
	}
	.fig.tall:has(.fig-head) {
		grid-template-rows: auto minmax(0, 1fr) auto;
	}
	.fig.wide {
		justify-items: stretch;
	}
	.learned-key {
		display: flex;
		justify-content: center;
		margin: 10px 0 8px;
	}
	.learned-note {
		max-width: 52ch;
		margin: 0 auto 22px;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
		text-align: center;
	}
	.three {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 300px;
	}
	figcaption {
		max-width: 52ch;
		justify-self: center;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
		text-align: center;
	}
	@keyframes arrive {
		from {
			opacity: 0;
		}
	}
	.star {
		width: min(100%, 400px);
	}
	.star path {
		fill: none;
		stroke: #f2f2f2;
		stroke-linecap: round;
	}
	.star .node {
		fill: var(--color-void);
		stroke: #f2f2f2;
		stroke-width: 1.25;
	}
	.star .node.q {
		fill: #f2f2f2;
	}
	.star .w {
		fill: var(--color-ink-3);
		font-size: 12px;
	}
	.strips {
		display: grid;
		grid-template-columns: 80px auto;
		gap: 10px 14px;
		align-items: center;
		justify-items: start;
		font-size: 18px;
	}
	.sum {
		font-size: 18px;
	}
	.cost {
		width: min(100%, 440px);
		overflow: visible;
	}
	.cost .grid {
		stroke: #1c1c1c;
	}
	.cost .mark {
		stroke: var(--color-ink-3);
		stroke-dasharray: 2 4;
	}
	.cost .tick {
		fill: var(--color-ink-3);
		font-size: 11px;
		text-anchor: middle;
	}
	.cost .tick.start {
		text-anchor: start;
	}
	.cost .c {
		fill: none;
		stroke: #f2f2f2;
		stroke-width: 1.6;
	}
	.cost .pair {
		stroke-opacity: 0.55;
		stroke-dasharray: 6 4;
	}
	.cost .win {
		stroke-opacity: 0.4;
		stroke-dasharray: 1.5 3;
	}
	.cost .lab {
		fill: var(--color-ink);
		font-size: 12px;
	}
	.cost .lab.dim {
		fill: var(--color-ink-3);
	}
	.tris {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 18px;
		width: min(100%, 480px);
	}
	.tri {
		display: grid;
		justify-items: center;
		gap: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.tri svg {
		width: 100%;
	}
	.tri .face {
		fill: rgb(242 242 242 / 0.16);
	}
	.tri .edge {
		stroke: #2c2c2c;
		stroke-width: 1.2;
	}
	.tri .edge.on {
		stroke: #f2f2f2;
		stroke-width: 1.8;
	}
	.tri .v {
		fill: var(--color-void);
		stroke: #f2f2f2;
		stroke-width: 1.2;
	}
	.tri .v.q {
		fill: #f2f2f2;
	}
	.tri-keys {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.grid3 {
		display: grid;
		width: min(100%, 420px);
		grid-template-columns: auto repeat(3, auto);
		gap: 10px 12px;
		align-items: center;
	}
	.g-label {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		text-align: right;
	}
	.q-label {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		text-align: center;
	}
	.hist {
		display: flex;
		align-items: flex-end;
		gap: 22px;
		height: 230px;
	}
	.h-col {
		display: grid;
		justify-items: center;
		gap: 6px;
	}
	.h-val {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.h-bar {
		width: 42px;
		border-radius: 2px;
		background: #3a3a3a;
	}
	.h-bar.set {
		background: var(--color-ink);
	}
	.h-score {
		font-size: 15px;
	}
	.h-m {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.results {
		display: grid;
		width: min(100%, 440px);
		grid-template-columns: minmax(84px, 140px) minmax(60px, 1fr) 52px;
		gap: 8px 12px;
		align-items: center;
	}
	.results h4 {
		grid-column: 1 / -1;
		margin-top: 8px;
		font-size: var(--text-xs);
		font-weight: 500;
		color: var(--color-ink-2);
	}
	.m-label {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.track {
		position: relative;
		height: 8px;
		background: #161616;
		border-radius: 2px;
	}
	.fill {
		position: absolute;
		inset: 0 auto 0 0;
		background: #555;
		border-radius: 2px;
	}
	.fill.win {
		background: var(--color-ink);
	}
	.base {
		position: absolute;
		top: -3px;
		bottom: -3px;
		z-index: 1;
		width: 1px;
		background: var(--color-ink-2);
	}
	.m-val {
		font-size: var(--text-xs);
		text-align: right;
	}
	.table-grid {
		display: grid;
		grid-template-columns: repeat(4, auto);
		gap: 14px 18px;
		justify-content: center;
	}
	.table-grid.three {
		grid-template-columns: repeat(3, auto);
	}
	.slot {
		display: grid;
		justify-items: center;
		gap: 6px;
	}
	.answer {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		border: 1px solid #555;
	}
	.answer.yes {
		border-color: var(--color-ink);
		background: var(--color-ink);
	}
	.chase-wrap {
		justify-self: center;
		max-width: 520px;
	}
	.hops,
	.tokens {
		width: 100%;
		max-width: 520px;
		overflow: visible;
	}
	.hops .map {
		stroke: #2c2c2c;
		stroke-width: 1;
	}
	.hops .map.on {
		stroke: var(--color-ink);
		stroke-width: 1.6;
	}
	.num-dot {
		fill: #1a1a1a;
		stroke: #555;
	}
	.num-dot.on {
		fill: var(--color-ink);
		stroke: var(--color-ink);
	}
	.hops text,
	.tokens text {
		font-size: 10px;
		fill: var(--color-ink-3);
	}
	.hops .fn {
		font-family: 'KaTeX_Main', serif;
		font-style: italic;
		font-size: 12px;
		text-anchor: middle;
		fill: var(--color-ink-2);
	}
	.onehot {
		fill: #1c1c1c;
	}
	.onehot.hot {
		fill: var(--color-ink);
	}
	.tokens .sinkname {
		fill: var(--color-ink-2);
	}
	.tokens .lab {
		fill: var(--color-ink);
	}
	.tokens .more {
		font-size: 16px;
	}
	.fig-head {
		display: flex;
		justify-content: center;
	}
	.mass {
		display: grid;
		grid-template-columns: 76px min(300px, 58vw);
		gap: 14px 12px;
		align-items: center;
	}
	.mass-label {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		text-align: right;
	}
	.mass-bar {
		display: flex;
		gap: 1px;
		height: 14px;
		border-radius: 2px;
		overflow: hidden;
	}
	.mass-bar span {
		flex-basis: 0;
		min-width: 1px;
	}
	.mass-keys {
		display: flex;
		flex-wrap: wrap;
		gap: 6px 14px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.mass-keys span {
		display: inline-flex;
		align-items: center;
		gap: 5px;
	}
	.mass-keys i {
		width: 8px;
		height: 8px;
		border-radius: 2px;
	}
	.mass-keys b {
		font-weight: 400;
		color: var(--color-ink-2);
	}
	.atlas {
		display: grid;
		grid-template-columns: 70px minmax(0, auto);
		gap: 18px 16px;
		align-items: center;
	}
	.order {
		display: grid;
		gap: 2px;
		font-size: 17px;
	}
	.order small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		gap: 16px 22px;
	}
	.cell {
		display: grid;
		justify-items: center;
		gap: 6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.dyson {
		display: grid;
		justify-items: center;
		gap: 6px;
		font-size: 17px;
	}
	.unroll {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.timeline {
		display: grid;
		gap: 14px;
		width: min(100%, 440px);
	}
	.timeline li {
		display: grid;
		grid-template-columns: 40px 12px 1fr;
		gap: 10px;
		align-items: baseline;
		font-size: var(--text-sm);
		color: var(--color-ink-3);
	}
	.timeline li.ours {
		color: var(--color-ink);
	}
	.t-dot {
		width: 7px;
		height: 7px;
		border: 1px solid var(--color-ink-3);
		border-radius: 50%;
		transform: translateY(-1px);
	}
	.timeline li.ours .t-dot {
		border-color: var(--color-ink);
		background: var(--color-ink);
	}
	.t-ref {
		font-size: 0.85em;
		color: var(--color-ink-3);
	}
</style>
