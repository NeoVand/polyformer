<script lang="ts">
	/**
	 * Figure 1 of the report: what arity is, why it is algebra, and what it costs.
	 * (a) One query card in zero-sum relations of arity 2, 3 and 4.
	 * (b) Each card is a phase per character; a zero-sum triple makes every channel agree,
	 *     any other triple splits the channels three ways and cancels.
	 * (c) Power sums and Newton's identities give every arity in one pass; the cost next to
	 *     dense order-k attention.
	 * Every card and angle is computed, not drawn by hand.
	 */
	import type { Card } from '#lib/set/cards.ts';
	import CardFace from '#lib/ui/CardFace.svelte';

	const card = (...v: number[]) => v as unknown as Card;
	const add = (...cs: Card[]) => [0, 1, 2, 3].map((a) => cs.reduce((s, c) => s + c[a], 0) % 3);
	const neg = (...cs: Card[]) => card(...add(...cs).map((v) => (3 - v) % 3));

	// (a) the query and one relation of each arity, all checked to sum to zero
	const q = card(1, 0, 2, 1);
	const pair = [neg(q)];
	const triple = [card(0, 2, 2, 0)];
	triple.push(neg(q, triple[0]));
	const quad = [card(0, 0, 0, 1), card(2, 2, 1, 0)];
	quad.push(neg(q, ...quad));

	const S = 30; // card glyph size
	const Q = { x: 142, y: 150 };
	const at = {
		pair: [{ x: 52, y: 64 }],
		triple: [
			{ x: 248, y: 70 },
			{ x: 268, y: 162 }
		],
		quad: [
			{ x: 40, y: 232 },
			{ x: 128, y: 262 },
			{ x: 226, y: 246 }
		]
	};
	const hull = (pts: { x: number; y: number }[]) => pts.map((p) => `${p.x},${p.y}`).join(' ');

	// (b) phases for two characters of Z_3^4, for the query and its SET partners
	const TAU = Math.PI * 2;
	const chars = [card(1, 0, 0, 0), card(1, 1, 0, 2)];
	const dot = (c: Card, x: Card) => (c[0] * x[0] + c[1] * x[1] + c[2] * x[2] + c[3] * x[3]) % 3;
	const setCards = [q, ...triple];
	const arrow = (cx: number, cy: number, r: number, k: number) => {
		const a = (TAU * k) / 3;
		return { x2: cx + r * Math.cos(a), y2: cy - r * Math.sin(a) };
	};

	// (c) the pipeline, with sub- and superscripts as tspans
	type Seg = [string, '' | 'sub' | 'sup'];
	const STEPS: { what: string; eq: Seg[] }[] = [
		{
			what: 'Phases of every token',
			eq: [
				['φ(x', ''],
				['t', 'sub'],
				[')', '']
			]
		},
		{
			what: 'Pooled power sums',
			eq: [
				['P', ''],
				['j', 'sub'],
				[' = Σ', ''],
				['t', 'sub'],
				[' φ(x', ''],
				['t', 'sub'],
				[')', ''],
				['j', 'sup']
			]
		},
		{
			what: "Newton's identities",
			eq: [
				['e', ''],
				['1', 'sub'],
				[', e', ''],
				['2', 'sub'],
				[', …, e', ''],
				['K', 'sub']
			]
		},
		{
			what: 'Counts with the query, per k',
			eq: [
				['N', ''],
				['q,2', 'sub'],
				[' … N', ''],
				['q,K', 'sub']
			]
		}
	];

	// (c) cost of one head at n = 64 tokens, in pair-, triple-, ... token visits
	const N = 64;
	const COSTS = [
		{ label: 'Pairwise', tex: 'n²', v: N ** 2 },
		{ label: 'Cubic', tex: 'n³', v: N ** 3 },
		{ label: 'Quartic', tex: 'n⁴', v: N ** 4 },
		{ label: 'Quintic', tex: 'n⁵', v: N ** 5 },
		{ label: 'Newton, every k ≤ 6', tex: '6n', v: 6 * N, ours: true }
	];
	const LOGMAX = Math.log10(N ** 5);
	const fmt = (v: number) =>
		v >= 1e9
			? `${(v / 1e9).toFixed(1)}B`
			: v >= 1e6
				? `${(v / 1e6).toFixed(1)}M`
				: v >= 1e3
					? `${(v / 1e3).toFixed(1)}k`
					: String(v);
</script>

<div class="fig1">
	<svg viewBox="0 0 310 300" role="img" aria-labelledby="fig1a">
		<title id="fig1a">
			One query card in zero-sum relations of arity two, three and four with other cards.
		</title>
		<text class="tag" x="0" y="16">(a)</text>
		<text class="head" x="22" y="16">One card, three arities</text>
		<polygon class="edge e4" points={hull([Q, ...at.quad])} />
		<polygon class="edge e3" points={hull([Q, ...at.triple])} />
		<line class="edge e2" x1={Q.x} y1={Q.y} x2={at.pair[0].x} y2={at.pair[0].y} />
		<text class="k" x="78" y="118">k = 2</text>
		<text class="k" x="214" y="128">k = 3</text>
		<text class="k" x="120" y="222">k = 4</text>
		{#each [...at.pair, ...at.triple, ...at.quad] as p, i (i)}
			{@const c = [...pair, ...triple, ...quad][i]}
			<rect class="well" x={p.x - S / 2 - 3} y={p.y - S / 2 - 3} width={S + 6} height={S + 6} />
			<CardFace card={c} x={p.x - S / 2} y={p.y - S / 2} width={S} />
		{/each}
		<rect class="well query" x={Q.x - S / 2 - 4} y={Q.y - S / 2 - 4} width={S + 8} height={S + 8} />
		<CardFace card={q} x={Q.x - S / 2} y={Q.y - S / 2} width={S} />
		<text class="note" x={Q.x + S / 2 + 8} y={Q.y + 4}>query</text>
	</svg>

	<svg viewBox="0 0 310 300" role="img" aria-labelledby="fig1b">
		<title id="fig1b">
			Each card as a phase per character. For a SET every character's product points the same way;
			for any other triple the products split evenly and cancel.
		</title>
		<text class="tag" x="0" y="16">(b)</text>
		<text class="head" x="22" y="16">A relation is agreement of phases</text>
		{#each setCards as c, i (i)}
			<CardFace card={c} x={34 + i * 58} y={34} width={24} />
		{/each}
		<text class="op" x="214" y="52">product</text>
		{#each chars as ch, row (row)}
			{@const cy = 96 + row * 46}
			<text class="chan" x="0" y={cy + 4}>χ{row + 1}</text>
			{#each setCards as c, i (i)}
				{@const a = arrow(46 + i * 58, cy, 15, dot(ch, c))}
				<circle class="unit" cx={46 + i * 58} {cy} r="15" />
				<line class="phasor" x1={46 + i * 58} y1={cy} x2={a.x2} y2={a.y2} />
				{#if i < 2}<text class="op" x={70 + i * 58} y={cy + 4}>×</text>{/if}
			{/each}
			<text class="op" x="196" y={cy + 4}>=</text>
			<circle class="unit" cx="232" {cy} r="15" />
			<line class="phasor strong" x1="232" y1={cy} x2="247" y2={cy} />
		{/each}
		<g transform="translate(78 236)">
			<circle class="unit" r="34" />
			<line class="phasor sum" x1="0" y1="0" x2="34" y2="0" />
			<text class="cap" y="52" text-anchor="middle">a SET: all 81 agree</text>
		</g>
		<g transform="translate(222 236)">
			<circle class="unit" r="34" />
			{#each [0, 1, 2] as k (k)}
				{@const a = arrow(0, 0, 34, k)}
				<line class="phasor split" x1="0" y1="0" x2={a.x2} y2={a.y2} />
			{/each}
			<text class="cap" y="52" text-anchor="middle">otherwise: 27 + 27 + 27, sum 0</text>
		</g>
	</svg>

	<svg viewBox="0 0 310 300" role="img" aria-labelledby="fig1c">
		<title id="fig1c">
			Newton's identities turn pooled power sums into counts for every arity in one pass, at a cost
			linear in the number of tokens, where dense order-k attention grows as n to the k.
		</title>
		<text class="tag" x="0" y="16">(c)</text>
		<text class="head" x="22" y="16">Every arity in one pass</text>
		{#each STEPS as step, i (i)}
			<text class="step" x="0" y={46 + i * 30}>{step.what}</text>
			<text class="eq" x="310" y={46 + i * 30} text-anchor="end"
				>{#each step.eq as [t, k], j (j)}<tspan
						class={k}
						baseline-shift={k === 'sub' ? '-3' : k === 'sup' ? '5' : undefined}>{t}</tspan
					>{/each}</text
			>
			{#if i < 3}<line class="flow" x1="6" y1={51 + i * 30} x2="6" y2={67 + i * 30} />{/if}
		{/each}
		<text class="sub" x="0" y="182">Cost of one head at n = {N}, log scale</text>
		{#each COSTS as c, i (c.label)}
			{@const y = 198 + i * 20}
			{@const w = Math.max(4, (Math.log10(c.v) / LOGMAX) * 150)}
			<text class="bar-label" class:ours={c.ours} x="0" y={y + 9}>{c.label}</text>
			<rect class="bar" class:ours={c.ours} x="118" {y} width={w} height="11" rx="1.5" />
			<text class="bar-v" class:ours={c.ours} x={124 + w} y={y + 9}>{c.tex} = {fmt(c.v)}</text>
		{/each}
	</svg>
</div>

<style>
	.fig1 {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 28px;
	}
	svg {
		width: 100%;
		height: auto;
		overflow: visible;
		font-family: var(--font-sans);
	}
	.tag {
		font-family: 'KaTeX_Main', serif;
		font-size: 13px;
		fill: var(--color-ink-3);
	}
	.head {
		font-size: 12.5px;
		font-weight: 500;
		fill: var(--color-ink);
	}
	.edge {
		stroke-linejoin: round;
	}
	.e2 {
		stroke: rgb(255 255 255 / 0.55);
		stroke-width: 1.4;
	}
	.e3 {
		fill: rgb(255 255 255 / 0.1);
		stroke: rgb(255 255 255 / 0.4);
		stroke-width: 1;
	}
	.e4 {
		fill: rgb(255 255 255 / 0.05);
		stroke: rgb(255 255 255 / 0.22);
		stroke-width: 1;
	}
	.k {
		font-family: 'KaTeX_Main', serif;
		font-style: italic;
		font-size: 12px;
		fill: var(--color-ink-2);
	}
	.well {
		fill: var(--color-void);
		rx: 5px;
	}
	.well.query {
		fill: #161616;
	}
	.note,
	.chan,
	.cap,
	.op,
	.sub {
		font-size: 10.5px;
		fill: var(--color-ink-3);
	}
	.chan {
		font-family: 'KaTeX_Main', serif;
		font-style: italic;
		font-size: 12px;
	}
	.unit {
		fill: none;
		stroke: #333;
		stroke-width: 1;
	}
	.phasor {
		stroke: var(--color-ink-2);
		stroke-width: 1.4;
		stroke-linecap: round;
	}
	.phasor.strong,
	.phasor.sum {
		stroke: var(--color-ink);
		stroke-width: 2;
	}
	.phasor.sum {
		stroke-width: 3;
	}
	.phasor.split {
		stroke: var(--color-ink-3);
		stroke-width: 1.6;
	}
	.cap {
		fill: var(--color-ink-2);
	}
	.step {
		font-size: 11.5px;
		fill: var(--color-ink-2);
	}
	.eq {
		font-family: 'KaTeX_Main', serif;
		font-style: italic;
		font-size: 12.5px;
		fill: var(--color-ink);
	}
	.eq .sub,
	.eq .sup {
		font-size: 9px;
	}
	.flow {
		stroke: #3a3a3a;
		stroke-width: 1;
	}
	.bar-label,
	.bar-v {
		font-size: 10.5px;
		fill: var(--color-ink-3);
	}
	.bar {
		fill: #3a3a3a;
	}
	.bar.ours {
		fill: var(--color-ink);
	}
	.bar-label.ours,
	.bar-v.ours {
		fill: var(--color-ink);
	}
	@media (max-width: 760px) {
		.fig1 {
			grid-template-columns: minmax(0, 1fr);
			max-width: 360px;
		}
	}
</style>
