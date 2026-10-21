<script lang="ts" module>
	export interface Series {
		name: string;
		points: { ctx: number; pct: number; seeds: number }[];
		dashed?: boolean;
	}
</script>

<script lang="ts">
	/**
	 * Change in held-out loss against the strengthened softmax control (rotary positions, forget
	 * gate, gated output, value residual) at equal modeled training FLOPs, by context length
	 * (research/EVENTS.md). Below zero is better than softmax.
	 */
	let { series }: { series: Series[] } = $props();
	const W = 560;
	const H = 250;
	const L = 54;
	const R = 128;
	const T = 16;
	const B = 36;
	const CTX = [512, 2048, 8192];
	const xs = (c: number) => L + (Math.log2(c / 512) / 4) * (W - L - R);
	const lo = $derived(Math.min(-1, ...series.flatMap((s) => s.points.map((p) => p.pct))));
	const hi = $derived(Math.max(0.5, ...series.flatMap((s) => s.points.map((p) => p.pct))));
	const ys = (v: number) => T + ((hi - v) / (hi - lo)) * (H - T - B);
	const ticks = $derived(
		Array.from(
			{ length: Math.floor(hi * 2) - Math.ceil(lo * 2) + 1 },
			(_, i) => (Math.ceil(lo * 2) + i) / 2
		)
	);
</script>

<svg
	viewBox="0 0 {W} {H}"
	class="cf"
	role="img"
	aria-label="Change against softmax by context length"
>
	{#each ticks as t (t)}
		<line class={t === 0 ? 'zero' : 'grid'} x1={L} x2={W - R} y1={ys(t)} y2={ys(t)} />
		<text class="tick" x={L - 8} y={ys(t) + 3.5} text-anchor="end">{t > 0 ? '+' : ''}{t}%</text>
	{/each}
	{#each CTX as c (c)}
		<text class="tick" x={xs(c)} y={H - B + 18} text-anchor="middle">{c.toLocaleString('en')}</text>
	{/each}
	<text class="tick" x={L + (W - L - R) / 2} y={H - 2} text-anchor="middle">context, tokens</text>
	<text class="tick" x={W - R} y={ys(0) - 6} text-anchor="end">softmax</text>
	{#each series as s (s.name)}
		{@const pts = s.points.map((p) => [xs(p.ctx), ys(p.pct)] as const)}
		<polyline class="line" class:dashed={s.dashed} points={pts.map((p) => p.join(',')).join(' ')} />
		{#each s.points as p (p.ctx)}
			<circle cx={xs(p.ctx)} cy={ys(p.pct)} r="3.8" class:hollow={s.dashed} />
			<text class="val" x={xs(p.ctx)} y={ys(p.pct) - 8} text-anchor="middle"
				>{p.pct > 0 ? '+' : ''}{p.pct.toFixed(2)}</text
			>
		{/each}
		{@const last = pts[pts.length - 1]}
		<text class="name" x={last[0] + 12} y={last[1] + 4}>{s.name}</text>
	{/each}
</svg>

<style>
	.cf {
		width: min(100%, 600px);
		height: auto;
		display: block;
		margin: 0 auto;
		font-family: var(--font-sans);
	}
	.grid {
		stroke: var(--color-edge);
	}
	.zero {
		stroke: var(--color-rule);
		stroke-dasharray: 3 3;
	}
	.line {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1.5;
	}
	.line.dashed {
		stroke: var(--color-ink-2);
		stroke-dasharray: 5 4;
	}
	circle {
		fill: var(--color-ink);
	}
	circle.hollow {
		fill: var(--color-void);
		stroke: var(--color-ink-2);
		stroke-width: 1.5;
	}
	.tick {
		font-size: 10px;
		fill: var(--color-ink-3);
	}
	.val {
		font-size: 10px;
		fill: var(--color-ink-2);
		font-variant-numeric: tabular-nums;
	}
	.name {
		font-size: 11px;
		fill: var(--color-ink);
	}
</style>
