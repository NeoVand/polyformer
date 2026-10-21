<script lang="ts">
	/**
	 * Forget-gate half-lives of two trained language models (LOOPS, seed 1; research/results/
	 * loops_probe_rope_forget_s1.json and loops_probe_hybrid_holo_forget_s1.json): one dot per head,
	 * the mean over 48 held-out windows of ln 2 / -log f, and the tokens on which each layer forgets most.
	 */
	const MODELS = [
		{
			name: 'Softmax with a forget gate',
			rows: [
				{ layer: 1, h: [109.2, 11.6, 8.9, 14.3, 53.3, 90.0, 8.7, 9.1], most: ['The', '⏎', '.', ':'] },
				{ layer: 2, h: [1.3, 41.3, 1.1, 2.7, 2.5, 56.5, 11.2, 8.2], most: ['.', '?', '⏎', ';'] },
				{ layer: 3, h: [6.6, 73.8, 11.9, 11.0, 67.8, 17.7, 1.9, 9.8], most: ['⏎', 'was', '.', 'is'] },
				{ layer: 4, h: [3.9, 36.3, 7.7, 2.1, 35.5, 46.0, 4.4, 66.2], most: ['?', '⏎', '.', 'but'] },
				{ layer: 5, h: [325.2, 5.0, 799.5, 3.6, 1009.8, 366.1, 333.4, 57.9], most: ['⏎', '?', '.', ')'] },
				{
					layer: 6,
					h: [102.7, 13252.8, 245.5, 1901.9, 302.8, 694.1, 69.9, 277.9],
					most: ['⏎', '?', 'The', ':']
				}
			]
		},
		{
			name: 'Hybrid, its attention layers',
			rows: [
				{ layer: 2, h: [232.2, 38.5, 7.9, 27.3, 64.2, 37.0, 87.3, 4621.7], most: ['⏎', '.', '?', 'The'] },
				{
					layer: 4,
					h: [1922.0, 279.8, 2755.6, 83.0, 8.7, 2921.6, 15.9, 1381.3],
					most: ['⏎', '?', '.', 'The']
				},
				{
					layer: 6,
					h: [10722.4, 43.3, 4433.2, 152.1, 7000.6, 5183.0, 96.6, 40135.0],
					most: ['⏎', '?', '.', '(']
				}
			]
		}
	];
	const W = 640;
	const L = 70;
	const R = 150;
	const ROW = 22;
	const LO = 0;
	const HI = 5; // 1 to 100,000 tokens, log scale
	const x = (h: number) => L + ((Math.log10(Math.max(h, 1)) - LO) / (HI - LO)) * (W - L - R);
	const ticks = [1, 10, 100, 1000, 10000, 100000];
	const label = (t: number) => (t >= 1000 ? `${t / 1000}k` : `${t}`);
	let y = 0;
	const layout = MODELS.map((m) => {
		const top = y + 22;
		y = top + m.rows.length * ROW + 10;
		return { ...m, top };
	});
	const H = y + 30;
</script>

<svg viewBox="0 0 {W} {H}" class="hl" role="img" aria-label="Forget-gate half-lives by layer">
	{#each ticks as t (t)}
		<line class="grid" x1={x(t)} x2={x(t)} y1="14" y2={H - 26} />
		<text class="tick" x={x(t)} y={H - 10} text-anchor="middle">{label(t)}</text>
	{/each}
	<line class="ctx" x1={x(512)} x2={x(512)} y1="14" y2={H - 26} />
	<text class="tick" x={x(512) + 4} y="10">context 512</text>
	<text class="head" x={W - R + 12} y="10">forgets most at</text>
	{#each layout as m (m.name)}
		<text class="model" x="0" y={m.top - 6}>{m.name}</text>
		{#each m.rows as r, i (r.layer)}
			{@const cy = m.top + i * ROW + ROW / 2}
			<text class="lay" x={L - 12} y={cy + 4} text-anchor="end">layer {r.layer}</text>
			<line class="lane" x1={L} x2={W - R} y1={cy} y2={cy} />
			{#each r.h as h, j (j)}
				<circle cx={x(h)} {cy} r="3.6" />
			{/each}
			<text class="most" x={W - R + 12} y={cy + 4}>{r.most.join('  ')}</text>
		{/each}
	{/each}
	<text class="tick" x={L + (W - L - R) / 2} y={H} text-anchor="middle">half-life in tokens</text>
</svg>

<style>
	.hl {
		width: min(100%, 680px);
		height: auto;
		display: block;
		margin: 0 auto;
		font-family: var(--font-sans);
	}
	.grid {
		stroke: var(--color-edge);
		stroke-width: 1;
	}
	.ctx {
		stroke: var(--color-rule);
		stroke-dasharray: 3 3;
	}
	.lane {
		stroke: var(--color-panel);
	}
	circle {
		fill: var(--color-ink);
		opacity: 0.85;
	}
	.tick,
	.head {
		font-size: 10px;
		fill: var(--color-ink-3);
	}
	.model {
		font-size: 11px;
		fill: var(--color-ink);
	}
	.lay {
		font-size: 10px;
		fill: var(--color-ink-2);
	}
	.most {
		font-size: 10px;
		fill: var(--color-ink-2);
		font-family: var(--font-mono);
	}
</style>
