<script lang="ts">
	/**
	 * The certified rewrite chains (LEAN_S1, registered batch: research/results/lean_s1/
	 * {Rp,RIp,Rctrlp,Tp}_a4_s{0,1,2}.json). Left: free-running exact match of the decoded tree at the
	 * last step of held-out chains, by chain length; trained at 8 steps. Right: centred-cosine
	 * distance between the states of held-out certified-equivalent pairs (not evaluated at 1,024).
	 * Thin lines are seeds, the heavy line their mean.
	 */
	interface Arm {
		id: string;
		name: string;
		exact: number[][];
		pair: number[][];
	}
	const LENGTHS = [8, 64, 256, 1024];
	const ARMS: Arm[] = [
		{
			id: 'term',
			name: 'recurrence + term',
			exact: [
				[1, 1, 1, 1],
				[1, 1, 1, 1],
				[1, 1, 1, 1]
			],
			pair: [
				[0.0003, 0.0003, 0.0003],
				[0.0002, 0.0002, 0.0002],
				[0.0002, 0.0002, 0.0002]
			]
		},
		{
			id: 'rec',
			name: 'recurrence',
			exact: [
				[1, 0.615, 0.004, 0],
				[1, 0.914, 0.027, 0],
				[1, 0.986, 0.891, 0.738]
			],
			pair: [
				[0.1126, 0.4322, 0.8135],
				[0.1083, 0.223, 0.9145],
				[0.1028, 0.1178, 0.1568]
			]
		},
		{
			id: 'ctrl',
			name: 'control',
			exact: [
				[1, 0.019, 0.006, 0],
				[1, 0.084, 0.01, 0.016],
				[1, 0.082, 0.031, 0.019]
			],
			pair: [
				[0.0005, 0.0044, 0.0047],
				[0.0005, 0.0031, 0.0037],
				[0.0005, 0.0028, 0.003]
			]
		},
		{
			id: 'tf',
			name: 'transformer',
			exact: [
				[0.764, 0.031, 0.019, 0.012],
				[0.762, 0.041, 0.012, 0],
				[0.703, 0.039, 0.01, 0]
			],
			pair: [
				[0.2965, 0.7204, 0.7891],
				[0.2929, 0.758, 0.8349],
				[0.3338, 0.757, 0.8457]
			]
		}
	];
	const mean = (rows: number[][]) =>
		rows[0].map((_, j) => rows.reduce((s, r) => s + r[j], 0) / rows.length);

	const W = 320;
	const H = 226;
	const T = 18;
	const B = 36;
	const L = 40;
	/** The two panels share one x scale, so the 8, 64 and 256 columns line up across them. */
	const STEP = 36; // pixels per doubling, 7 doublings from 8 to 1,024
	const xs = (n: number) => L + (Math.log2(n) - 3) * STEP;
	const yExact = (v: number) => T + (1 - v) * (H - T - B);
	const yPair = (v: number) => T + ((0 - Math.log10(v)) / 4) * (H - T - B); // 1 down to 1e-4
	const path = (xs: number[], ys: number[]) => xs.map((x, i) => `${x},${ys[i]}`).join(' ');
	const fmtLen = (n: number) => n.toLocaleString('en');

	const exactArms = ARMS.map((a) => ({
		...a,
		seeds: a.exact.map((row) => path(LENGTHS.map(xs), row.map(yExact))),
		mean: mean(a.exact),
		meanPath: path(LENGTHS.map(xs), mean(a.exact).map(yExact))
	}));
	const pairLengths = LENGTHS.slice(0, 3);
	/** Names sit to the right of each line's last point, nudged apart where two would collide. */
	const pairArms = (() => {
		const arms = ARMS.map((a) => ({
			...a,
			seeds: a.pair.map((row) => path(pairLengths.map(xs), row.map(yPair))),
			mean: mean(a.pair),
			meanPath: path(pairLengths.map(xs), mean(a.pair).map(yPair)),
			labelY: yPair(mean(a.pair)[2])
		}));
		const order = [...arms].sort((p, q) => p.labelY - q.labelY);
		for (let i = 1; i < order.length; i++) {
			if (order[i].labelY - order[i - 1].labelY < 12) order[i].labelY = order[i - 1].labelY + 12;
		}
		return arms;
	})();
	const pairTicks = [1, 0.1, 0.01, 0.001, 0.0001];
	const exactTicks = [0, 0.5, 1];
</script>

<div class="ef" role="img" aria-label="Exact match and pair distance against chain length">
	<svg viewBox="0 0 {W} {H}" class="chart">
		{#each exactTicks as t (t)}
			<line class="grid" x1={L} x2={xs(1024)} y1={yExact(t)} y2={yExact(t)} />
			<text class="tick" x={L - 7} y={yExact(t) + 3.5} text-anchor="end">{t * 100}%</text>
		{/each}
		{#each LENGTHS as n (n)}
			<text class="tick" x={xs(n)} y={H - B + 16} text-anchor="middle">{fmtLen(n)}</text>
		{/each}
		<text class="tick" x={xs(8)} y={H - B + 28} text-anchor="start">trained here</text>
		<text class="tick" x={xs(1024)} y={H - B + 28} text-anchor="end">rewrite steps</text>
		<text class="tick" x={L} y={9} text-anchor="start">exact match of the state</text>
		{#each exactArms as a (a.id)}
			{#each a.seeds as d, i (i)}
				<polyline class="seed {a.id}" points={d} />
			{/each}
			<polyline class="line {a.id}" points={a.meanPath} />
			{#each a.mean as v, i (i)}
				<circle class={a.id} cx={xs(LENGTHS[i])} cy={yExact(v)} r="2.4" />
			{/each}
		{/each}
		<text class="name" x={xs(1024)} y={yExact(1) - 8} text-anchor="end">recurrence + term</text>
		<text class="name" x={xs(1024)} y={yExact(exactArms[1].mean[3]) - 8} text-anchor="end"
			>recurrence</text
		>
		<text class="name" x={xs(8) + 8} y={yExact(exactArms[3].mean[0]) + 3.5}>transformer</text>
		<text class="name" x={xs(1024)} y={yExact(exactArms[2].mean[3]) - 7} text-anchor="end"
			>control</text
		>
	</svg>
	<svg viewBox="0 0 {W} {H}" class="chart">
		{#each pairTicks as t (t)}
			<line class="grid" x1={L} x2={xs(256)} y1={yPair(t)} y2={yPair(t)} />
			<text class="tick" x={L - 7} y={yPair(t) + 3.5} text-anchor="end">{t}</text>
		{/each}
		{#each pairLengths as n (n)}
			<text class="tick" x={xs(n)} y={H - B + 16} text-anchor="middle">{fmtLen(n)}</text>
		{/each}
		<text class="tick" x={xs(256)} y={H - B + 28} text-anchor="end">rewrite steps</text>
		<text class="tick" x={L} y={9} text-anchor="start">distance of equivalent pairs</text>
		{#each pairArms as a (a.id)}
			{#each a.seeds as d, i (i)}
				<polyline class="seed {a.id}" points={d} />
			{/each}
			<polyline class="line {a.id}" points={a.meanPath} />
			{#each a.mean as v, i (i)}
				<circle class={a.id} cx={xs(pairLengths[i])} cy={yPair(v)} r="2.4" />
			{/each}
			<text class="name" x={xs(256) + 8} y={a.labelY + 3.5}>{a.name}</text>
		{/each}
	</svg>
</div>

<style>
	.ef {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 10px 20px;
		width: 100%;
		font-family: var(--font-sans);
	}
	.chart {
		width: min(100%, 320px);
		height: auto;
		display: block;
		overflow: visible;
	}
	.grid {
		stroke: var(--color-edge);
		stroke-width: 1;
	}
	.seed {
		fill: none;
		stroke-width: 0.8;
		opacity: 0.45;
	}
	.line {
		fill: none;
		stroke-width: 1.6;
	}
	.term {
		stroke: var(--color-ink);
	}
	.rec {
		stroke: var(--color-ink);
		stroke-dasharray: 5 3;
	}
	.ctrl {
		stroke: var(--color-ink-3);
		stroke-dasharray: 2 3;
	}
	.tf {
		stroke: var(--color-ink-3);
	}
	circle.term,
	circle.rec {
		fill: var(--color-ink);
		stroke: none;
	}
	circle.ctrl,
	circle.tf {
		fill: var(--color-ink-3);
		stroke: none;
	}
	.tick {
		font-size: 10px;
		fill: var(--color-ink-3);
		font-variant-numeric: tabular-nums;
	}
	.name {
		font-size: 10.5px;
		fill: var(--color-ink);
	}
</style>
