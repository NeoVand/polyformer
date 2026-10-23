<script lang="ts">
	/**
	 * Latent execution (EXEC_LM, registered batch, seeds 0 / 1 / 2): exact final state of Python
	 * programs of 4 bit variables against program length, trained on 4 to 16 statements, for a slot
	 * reading each statement through frozen Qwen2.5-Coder-0.5B (with and without the objective) and
	 * the same model fine-tuned to write its state after every statement or only at the end; the
	 * shallow last-write table as a dashed floor. Beside it, the tokens each arm generates per
	 * statement.
	 */
	interface Arm {
		id: string;
		name: string;
		seeds: number[][];
	}
	const LENGTHS = [16, 64, 256, 1024];
	const ARMS: Arm[] = [
		{
			id: 'obj',
			name: 'slot + objective',
			seeds: [
				[1, 1, 1, 0.965],
				[1, 1, 1, 0.844],
				[1, 1, 1, 0.729]
			]
		},
		{
			id: 'cot',
			name: 'chain of thought',
			seeds: [
				[1, 0.498, 0.055, 0.062],
				[1, 0.809, 0.316, 0.281],
				[1, 0.898, 0.367, 0.25]
			]
		},
		{
			id: 'direct',
			name: 'final state only',
			seeds: [
				[0.361, 0.34, 0.316, 0.141],
				[0.367, 0.342, 0.281, 0.125],
				[0.535, 0.34, 0.188, 0.031]
			]
		},
		{
			id: 'plain',
			name: 'slot alone',
			seeds: [
				[1, 0.881, 0.072, 0.029],
				[1, 0.826, 0.053, 0.027],
				[0.957, 0.689, 0.137, 0.021]
			]
		}
	];
	const FLOOR = [0.506, 0.453, 0.447, 0.424];
	const TOKENS = [
		{ id: 'cot', name: 'chain of thought', value: 8, label: '8' },
		{ id: 'direct', name: 'final state only', value: 0.5, label: '8 / n' },
		{ id: 'obj', name: 'slot + objective', value: 0, label: '0' },
		{ id: 'plain', name: 'slot alone', value: 0, label: '0' }
	];

	const H = 226;
	const T = 18;
	const B = 36;
	const W = 330;
	const L = 36;
	const STEP = 34; // pixels per doubling, 6 doublings from 16 to 1,024
	const xs = (n: number) => L + (Math.log2(n) - 4) * STEP;
	const ys = (v: number) => T + (1 - v) * (H - T - B);
	const mean = (rows: number[][]) =>
		rows[0].map((_, j) => rows.reduce((s, r) => s + r[j], 0) / rows.length);
	const pts = (vals: number[]) => vals.map((v, j) => `${xs(LENGTHS[j])},${ys(v)}`).join(' ');

	/** Each name sits right of its line's last point, nudged apart where two would collide. */
	const lines = (() => {
		const rows = [
			...ARMS.map((a) => ({ ...a, mean: mean(a.seeds), labelY: 0 })),
			{ id: 'floor', name: 'shallow floor', seeds: [] as number[][], mean: FLOOR, labelY: 0 }
		].map((r) => ({ ...r, labelY: ys(r.mean[3]) }));
		const order = [...rows].sort((p, q) => p.labelY - q.labelY);
		for (let i = 1; i < order.length; i++) {
			if (order[i].labelY - order[i - 1].labelY < 12) order[i].labelY = order[i - 1].labelY + 12;
		}
		return rows;
	})();
	const arms = $derived(lines.filter((l) => l.id !== 'floor'));
	const floor = $derived(lines.find((l) => l.id === 'floor'));

	// the token panel: same height and plot band as the first, one row per arm
	const TW = 214;
	const TL = 96;
	const TR = 22;
	const tx = (v: number) => TL + (v / 8) * (TW - TL - TR);
	const ty = (i: number) => T + ((i + 0.5) / TOKENS.length) * (H - T - B);
</script>

<div
	class="xf"
	role="img"
	aria-label="Exact final state against program length, and tokens generated per statement"
>
	<svg viewBox="0 0 {W} {H}" class="chart main">
		{#each [0, 0.5, 1] as t (t)}
			<line class="grid" x1={L} x2={xs(1024)} y1={ys(t)} y2={ys(t)} />
			<text class="tick" x={L - 7} y={ys(t) + 3.5} text-anchor="end">{t * 100}%</text>
		{/each}
		{#each LENGTHS as n (n)}
			<text class="tick" x={xs(n)} y={H - B + 16} text-anchor="middle"
				>{n.toLocaleString('en')}</text
			>
		{/each}
		<text class="tick" x={xs(16)} y={H - B + 28} text-anchor="start">trained to 16</text>
		<text class="tick" x={xs(1024)} y={H - B + 28} text-anchor="end">statements</text>
		<text class="tick" x={L} y="9" text-anchor="start">exact final state</text>
		{#if floor}
			<polyline class="floor" points={pts(floor.mean)} />
			<text class="name dim" x={xs(1024) + 8} y={floor.labelY + 3.5}>{floor.name}</text>
		{/if}
		{#each arms as a (a.id)}
			{#each a.seeds as row, k (k)}
				{#each row as v, j (j)}
					<circle class="seed {a.id}" cx={xs(LENGTHS[j]) + (k - 1) * 3} cy={ys(v)} r="1.8" />
				{/each}
			{/each}
			<polyline class="line {a.id}" points={pts(a.mean)} />
			{#each a.mean as v, j (j)}
				<circle class="dot {a.id}" cx={xs(LENGTHS[j])} cy={ys(v)} r="2.4" />
			{/each}
			<text class="name" x={xs(1024) + 8} y={a.labelY + 3.5}>{a.name}</text>
		{/each}
	</svg>
	<svg viewBox="0 0 {TW} {H}" class="chart side">
		<text class="tick" x="0" y="9" text-anchor="start">tokens generated per statement</text>
		<line class="grid" x1={tx(0)} x2={tx(0)} y1={T} y2={H - B} />
		{#each TOKENS as r, i (r.id)}
			<text class="name" x={TL - 8} y={ty(i) + 3.5} text-anchor="end">{r.name}</text>
			{#if r.value > 0}
				<rect class="bar {r.id}" x={tx(0)} y={ty(i) - 4} width={tx(r.value) - tx(0)} height="8" />
			{/if}
			<text class="tick val" x={tx(r.value) + 5} y={ty(i) + 3.5}>{r.label}</text>
		{/each}
		{#each [0, 4, 8] as t (t)}
			<text class="tick" x={tx(t)} y={H - B + 16} text-anchor="middle">{t}</text>
		{/each}
	</svg>
</div>

<style>
	.xf {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: flex-start;
		gap: 10px 22px;
		width: 100%;
		font-family: var(--font-sans);
	}
	.chart {
		height: auto;
		display: block;
		overflow: visible;
	}
	.main {
		width: min(100%, 330px);
	}
	.side {
		width: min(100%, 214px);
	}
	.grid {
		stroke: var(--color-edge);
		stroke-width: 1;
	}
	.floor {
		fill: none;
		stroke: var(--color-ink-3);
		stroke-width: 1;
		stroke-dasharray: 4 3;
	}
	.line {
		fill: none;
		stroke-width: 1.6;
	}
	.line.obj,
	.line.plain {
		stroke: var(--color-ink);
	}
	.line.plain {
		stroke-dasharray: 5 3;
	}
	.line.cot,
	.line.direct {
		stroke: var(--color-ink-3);
	}
	.line.direct {
		stroke-dasharray: 2 3;
	}
	.dot.obj,
	.dot.plain,
	.seed.obj,
	.seed.plain {
		fill: var(--color-ink);
	}
	.dot.cot,
	.dot.direct,
	.seed.cot,
	.seed.direct {
		fill: var(--color-ink-3);
	}
	.seed {
		opacity: 0.4;
	}
	.bar.cot,
	.bar.direct {
		fill: var(--color-ink-3);
	}
	.tick {
		font-size: 10px;
		fill: var(--color-ink-3);
		font-variant-numeric: tabular-nums;
	}
	.val {
		fill: var(--color-ink-2);
	}
	.name {
		font-size: 10.5px;
		fill: var(--color-ink);
	}
	.name.dim {
		fill: var(--color-ink-3);
	}
</style>
