<script lang="ts">
	/**
	 * Exactness along the statements on the arithmetic rung (data and provenance in arithSteps.ts):
	 * the language model as a Markov step, the register-shaped slot, and the same language model
	 * with its whole history in context. Seeds as light lines, their mean as the heavy line.
	 */
	import { HISTORY, MARKOV, REGISTER, type StepCurve } from './arithSteps.ts';

	const W = 330;
	const H = 200;
	const T = 18;
	const B = 36;
	const L = 36;
	const R = 92;
	const xs = (t: number) => L + ((Math.log2(t) - 3) / 7) * (W - L - R);
	const ys = (v: number) => T + (1 - v) * (H - T - B);
	/** The axis starts at statement 8: before it every arm is exact. */
	const FROM = 8;
	const path = (c: StepCurve) =>
		c
			.filter(([t]) => t >= FROM)
			.map(([t, v]) => `${xs(t)},${ys(v)}`)
			.join(' ');
	const mean = (cs: StepCurve[]): StepCurve =>
		cs[0].map(([t], j) => [t, cs.reduce((s, c) => s + c[j][1], 0) / cs.length]);
	const ARMS = [
		{ id: 'markov', name: 'Markov step', seeds: MARKOV },
		{ id: 'register', name: 'register slot', seeds: REGISTER },
		{ id: 'history', name: 'whole history', seeds: HISTORY }
	].map((a) => ({ ...a, mean: mean(a.seeds) }));
	const end = (c: StepCurve) => c[c.length - 1];
	const TICKS = [8, 16, 64, 256, 1024];
</script>

<svg
	viewBox="0 0 {W} {H}"
	class="af"
	role="img"
	aria-label="Exact state along the statements of arithmetic programs, three models"
>
	{#each [0, 0.5, 1] as t (t)}
		<line class="grid" x1={L} x2={xs(1024)} y1={ys(t)} y2={ys(t)} />
		<text class="tick" x={L - 7} y={ys(t) + 3.5} text-anchor="end">{t * 100}%</text>
	{/each}
	<line class="train" x1={xs(16)} x2={xs(16)} y1={T} y2={H - B} />
	{#each TICKS as n (n)}
		<text class="tick" x={xs(n)} y={H - B + 16} text-anchor="middle">{n.toLocaleString('en')}</text>
	{/each}
	<text class="tick" x={xs(16)} y={H - B + 28} text-anchor="middle">trained to 16</text>
	<text class="tick" x={xs(1024)} y={H - B + 28} text-anchor="end">statement</text>
	<text class="tick" x={L} y="9" text-anchor="start">exact state after the statement</text>
	{#each ARMS as a (a.id)}
		{#if a.seeds.length > 1}
			{#each a.seeds as c, k (k)}
				<polyline class="seed {a.id}" points={path(c)} />
			{/each}
		{/if}
		<polyline class="line {a.id}" points={path(a.mean)} />
		{@const [t, v] = end(a.mean)}
		<circle class="dot {a.id}" cx={xs(t)} cy={ys(v)} r="2.4" />
		<text class="name" x={xs(t) + 8} y={ys(v) + (a.id === 'history' ? -4 : 3.5)}>{a.name}</text>
	{/each}
</svg>

<style>
	.af {
		width: min(100%, 330px);
		height: auto;
		display: block;
		margin: 0 auto;
		overflow: visible;
		font-family: var(--font-sans);
	}
	.grid {
		stroke: var(--color-edge);
		stroke-width: 1;
	}
	.train {
		stroke: var(--color-rule);
		stroke-dasharray: 3 3;
	}
	.line {
		fill: none;
		stroke-width: 1.6;
	}
	.seed {
		fill: none;
		stroke-width: 0.8;
		opacity: 0.4;
	}
	.markov,
	.register {
		stroke: var(--color-ink);
	}
	.register {
		stroke-dasharray: 5 3;
	}
	.history {
		stroke: var(--color-ink-3);
	}
	.dot {
		stroke: none;
	}
	.dot.markov,
	.dot.register {
		fill: var(--color-ink);
	}
	.dot.history {
		fill: var(--color-ink-3);
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
