<script lang="ts">
	/**
	 * Figure 1 of the report: what arity is, why it is algebra, and what it costs.
	 * (a) One query card in zero-sum relations of arity 2, 3 and 4, written as card sums.
	 * (b) Under a character each card is a phase. A SET makes every character's product
	 *     point the same way; any other triple splits the characters three ways and cancels.
	 * (c) Power sums pooled once and Newton's identities give every arity in one pass.
	 * (d) What one head costs, next to dense order-k attention.
	 * Four panels of one size on one grid: (a) and (b) share three rows, (c) and (d) share five,
	 * so every row lines up across the figure. Every card and every angle is computed, none is
	 * drawn by hand, and text never sits on a line.
	 */
	import type { Card } from '#lib/set/cards.ts';
	import CardFace from '#lib/ui/CardFace.svelte';

	/** Which panels to draw; fewer than all three stack in one column (Learn's side figure). */
	let { panels = ['a', 'b', 'c', 'd'] }: { panels?: ('a' | 'b' | 'c' | 'd')[] } = $props();
	const single = $derived(panels.length < 3);
	/** The rows every panel shares: three for (a) and (b), five for (c) and (d). */
	const ROW3 = [54, 108, 162];
	const ROW5 = [42, 77, 112, 147, 182];

	const card = (...v: number[]) => v as unknown as Card;
	const sum = (...cs: Card[]) => [0, 1, 2, 3].map((a) => cs.reduce((s, c) => s + c[a], 0) % 3);
	const neg = (...cs: Card[]) => card(...sum(...cs).map((v) => (3 - v) % 3));
	const dot = (c: number[], x: Card) => (c[0] * x[0] + c[1] * x[1] + c[2] * x[2] + c[3] * x[3]) % 3;

	// ── (a) the query and one relation of each arity, each checked to sum to zero ──
	const q = card(1, 0, 2, 1);
	const j = card(0, 2, 2, 0);
	const a4 = card(0, 0, 0, 1);
	const b4 = card(2, 2, 1, 0);
	const ROWS = [
		{ k: 2, cards: [q, neg(q)], what: 'its complement' },
		{ k: 3, cards: [q, j, neg(q, j)], what: 'a SET' },
		{ k: 4, cards: [q, a4, b4, neg(q, a4, b4)], what: 'a four-card zero sum' }
	];
	const C = 26; // card glyph
	const STEP = 46; // card + operator
	const X0 = 52; // first card

	// ── (b) a SET and a near miss, under one character that tells them apart ──────
	const set = [q, j, neg(q, j)];
	const miss = [q, j, a4];
	const chars: number[][] = [];
	for (let v = 1; v < 81; v++) chars.push([0, 1, 2, 3].map((a) => Math.floor(v / 3 ** a) % 3));
	/** The first character under which the near miss does not cancel and no card sits at zero. */
	const chi =
		chars.find(
			(c) => dot(c, card(...sum(...miss))) !== 0 && [...miss, ...set].every((x) => dot(c, x) !== 0)
		) ?? chars[0];
	const TAU = Math.PI * 2;
	const tip = (r: number, k: number) => ({
		x: r * Math.cos((TAU * k) / 3),
		y: -r * Math.sin((TAU * k) / 3)
	});
	const phases = (cs: Card[]) => cs.map((x) => dot(chi, x));
	const total = (cs: Card[]) => phases(cs).reduce((s, p) => s + p, 0) % 3;
	const SIDES = [
		{ name: 'A SET', cs: set, x0: 0, verdict: 'agree: the sum is 81', agree: true },
		{
			name: 'Not a SET',
			cs: miss,
			x0: 222,
			verdict: 'split 27, 27, 27: the sum is 0',
			agree: false
		}
	];

	// ── (c) the pipeline and the cost of one head at n = 64 ────────────────────────
	type Seg = [string, '' | 'sub' | 'sup'];
	const STAGES: { what: string; eq: Seg[]; cost: string }[] = [
		{
			what: 'Tokens',
			cost: '',
			eq: [
				['x', ''],
				['1', 'sub'],
				[' … x', ''],
				['n', 'sub']
			]
		},
		{
			what: 'Phases',
			cost: 'one map per token',
			eq: [
				['φ(x', ''],
				['t', 'sub'],
				[')', '']
			]
		},
		{
			what: 'Power sums',
			cost: 'one pass over the tokens',
			eq: [
				['P', ''],
				['1', 'sub'],
				[' … P', ''],
				['K', 'sub']
			]
		},
		{
			what: "Newton's identities",
			cost: 'K² products, no tokens',
			eq: [
				['e', ''],
				['1', 'sub'],
				[' … e', ''],
				['K', 'sub']
			]
		},
		{
			what: 'Counts, every arity',
			cost: 'one product per token',
			eq: [
				['N', ''],
				['q,2', 'sub'],
				[' … N', ''],
				['q,K', 'sub']
			]
		}
	];
	const N = 64;
	const COSTS = [
		{ label: 'Pairwise', tex: 'n²', v: N ** 2 },
		{ label: 'Cubic', tex: 'n³', v: N ** 3 },
		{ label: 'Quartic', tex: 'n⁴', v: N ** 4 },
		{ label: 'Quintic', tex: 'n⁵', v: N ** 5 },
		{ label: 'Newton, k ≤ 6', tex: '6n', v: 6 * N, ours: true }
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

{#snippet math(eq: Seg[], x: number, y: number)}
	<text class="eq" {x} {y}
		>{#each eq as [t, k], i (i)}<tspan
				class={k}
				baseline-shift={k === 'sub' ? '-3' : k === 'sup' ? '5' : undefined}>{t}</tspan
			>{/each}</text
	>
{/snippet}

{#snippet phasor(cx: number, cy: number, r: number, k: number, strong: boolean)}
	{@const p = tip(r, k)}
	<circle class="unit" {cx} {cy} {r} />
	<line class="ph" class:strong x1={cx} y1={cy} x2={cx + p.x} y2={cy + p.y} />
	<circle class="hub" {cx} {cy} r="1.4" />
{/snippet}

<div class="fig1" class:single>
	{#if panels.includes('a')}
		<svg class="a" viewBox="0 0 420 200" role="img" aria-labelledby="fig1a">
			<title id="fig1a">
				The same query card in zero-sum relations of arity two, three and four, written as sums of
				cards.
			</title>
			<text class="tag" x="0" y="13">(a)</text>
			<text class="head" x="22" y="13">One card, three arities</text>
			{#each ROWS as row, r (row.k)}
				{@const y = ROW3[r]}
				<text class="k" x="0" y={y + 4}>k = {row.k}</text>
				{#each row.cards as c, i (i)}
					{@const x = X0 + i * STEP}
					<rect
						class="well"
						class:query={i === 0}
						x={x - 4}
						y={y - C / 2 - 4}
						width={C + 8}
						height={C + 8}
						rx="6"
					/>
					<CardFace card={c} {x} y={y - C / 2} width={C} />
					{#if i < row.cards.length - 1}
						<text class="op" x={x + C + 10} y={y + 5} text-anchor="middle">+</text>
					{/if}
				{/each}
				<text class="op" x={X0 + row.cards.length * STEP - 6} y={y + 5}>= 0</text>
				<text class="what" x={X0 + 4 * STEP + 30} y={y + 4}>{row.what}</text>
			{/each}
		</svg>
	{/if}

	{#if panels.includes('b')}
		<svg class="b" viewBox="0 0 420 200" role="img" aria-labelledby="fig1b">
			<title id="fig1b">
				Under one character each card is a phase. For a SET the phases add to zero under every one
				of the 81 characters; for any other triple the characters split three ways and cancel.
			</title>
			<text class="tag" x="0" y="13">(b)</text>
			<text class="head" x="22" y="13">A relation is agreement of phases</text>
			{#each SIDES as side (side.name)}
				{@const ph = phases(side.cs)}
				<text class="side" x={side.x0} y="34">{side.name}</text>
				{#each side.cs as c, i (i)}
					<CardFace card={c} x={side.x0 + i * 40 + 3} y={ROW3[0] - 9} width={18} />
					{@render phasor(side.x0 + i * 40 + 12, ROW3[1] - 6, 11, ph[i], false)}
					{#if i < 2}
						<text class="op" x={side.x0 + i * 40 + 32} y={ROW3[1] - 1} text-anchor="middle">×</text>
					{/if}
				{/each}
				<text class="op" x={side.x0 + 128} y={ROW3[1] - 1} text-anchor="middle">=</text>
				{@render phasor(side.x0 + 150, ROW3[1] - 6, 11, total(side.cs), true)}
				<text class="note" x={side.x0} y={ROW3[1] + 20}>under one character</text>
				<g transform="translate({side.x0 + 22} {ROW3[2] + 2})">
					<circle class="unit" r="20" />
					{#if side.agree}
						<line class="ph sum" x1="0" y1="0" x2="20" y2="0" />
					{:else}
						{#each [0, 1, 2] as k (k)}
							{@const p = tip(20, k)}
							<line class="ph split" x1="0" y1="0" x2={p.x} y2={p.y} />
						{/each}
					{/if}
					<circle class="hub" r="1.6" />
				</g>
				<text class="note" x={side.x0 + 52} y={ROW3[2] - 4}>under all 81 characters</text>
				<text class="res" x={side.x0 + 52} y={ROW3[2] + 12}>{side.verdict}</text>
			{/each}
		</svg>
	{/if}

	{#if panels.includes('c')}
		<svg class="c" viewBox="0 0 420 200" role="img" aria-labelledby="fig1c">
			<title id="fig1c">
				Tokens become phases, phases are pooled once into power sums, Newton's identities turn them
				into elementary symmetric polynomials, and those give each token's count of relations of
				every arity, each step linear in the number of tokens.
			</title>
			<text class="tag" x="0" y="13">(c)</text>
			<text class="head" x="22" y="13">Every arity in one pass</text>
			<line class="flow" x1="150" x2="150" y1={ROW5[0]} y2={ROW5[4]} />
			{#each STAGES as st, i (i)}
				{@const y = ROW5[i]}
				<text class="stage" x="0" y={y + 4}>{st.what}</text>
				<circle class="step" cx="150" cy={y} r="2.6" />
				{#if i > 0}
					<path class="arrow" d="M146.5,{y - 13} l3.5,5 l3.5,-5 z" />
				{/if}
				{@render math(st.eq, 166, y + 4.5)}
				<text class="what" x="420" y={y + 4} text-anchor="end">{st.cost}</text>
			{/each}
		</svg>
	{/if}

	{#if panels.includes('d')}
		<svg class="d" viewBox="0 0 420 200" role="img" aria-labelledby="fig1d">
			<title id="fig1d">
				The cost of one head at sequence length 64 on a log scale: pairwise, cubic, quartic and
				quintic attention grow as n to the k; Newton attention with every arity up to six grows as
				6n.
			</title>
			<text class="tag" x="0" y="13">(d)</text>
			<text class="head" x="22" y="13">What one head costs at n = {N}, log scale</text>
			{#each COSTS as c, i (c.label)}
				{@const y = ROW5[i]}
				{@const w = Math.max(3, (Math.log10(c.v) / LOGMAX) * 196)}
				<text class="bar-label" class:ours={c.ours} x="0" y={y + 4}>{c.label}</text>
				<rect class="bar" class:ours={c.ours} x="96" y={y - 4} width={w} height="8" rx="1" />
				<text class="bar-v" class:ours={c.ours} x={104 + w} y={y + 4}>{c.tex} = {fmt(c.v)}</text>
			{/each}
		</svg>
	{/if}
</div>

<style>
	.fig1 {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 22px 44px;
	}
	.fig1.single {
		grid-template-columns: minmax(0, 1fr);
		gap: 26px;
		/* near the drawing's own size, so its type matches the page */
		width: 100%;
		max-width: 540px;
		margin: 0 auto;
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
	.k,
	.eq {
		font-family: 'KaTeX_Main', serif;
		font-style: italic;
		font-size: 13px;
		fill: var(--color-ink-2);
	}
	.eq {
		fill: var(--color-ink);
	}
	.eq .sub,
	.eq .sup {
		font-size: 9px;
	}
	.well {
		fill: #121212;
	}
	.well.query {
		fill: #1d1d1d;
	}
	.op {
		font-family: 'KaTeX_Main', serif;
		font-size: 14px;
		fill: var(--color-ink-3);
	}
	.what,
	.note,
	.stage,
	.bar-label,
	.bar-v {
		font-size: 10.5px;
		fill: var(--color-ink-3);
	}
	.side {
		font-size: 11.5px;
		font-weight: 500;
		fill: var(--color-ink-2);
	}
	.res {
		font-size: 11px;
		fill: var(--color-ink-2);
	}
	.unit {
		fill: none;
		stroke: #333;
		stroke-width: 1;
	}
	.hub {
		fill: var(--color-ink-3);
	}
	.ph {
		stroke: var(--color-ink-2);
		stroke-width: 1.4;
		stroke-linecap: round;
	}
	.ph.strong {
		stroke: var(--color-ink);
		stroke-width: 1.8;
	}
	.ph.sum {
		stroke: var(--color-ink);
		stroke-width: 2.6;
	}
	.ph.split {
		stroke: var(--color-ink-3);
		stroke-width: 1.4;
	}
	.stage {
		fill: var(--color-ink-2);
	}
	.flow {
		stroke: #3a3a3a;
		stroke-width: 1;
	}
	.arrow {
		fill: #5a5a5a;
	}
	.step {
		fill: var(--color-ink-2);
	}
	.bar {
		fill: #3a3a3a;
	}
	.bar.ours,
	.bar-label.ours,
	.bar-v.ours {
		fill: var(--color-ink);
	}
	@media (max-width: 760px) {
		.fig1 {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
