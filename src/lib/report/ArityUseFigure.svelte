<script lang="ts">
	/**
	 * Figure 8 of the report: which arity a trained Newton attention layer uses. For each task,
	 * the share of its above-chance accuracy that is lost when one arity's read-out is switched
	 * off. A tall bar is an arity the model cannot do without.
	 */
	interface Row {
		task: string;
		label: string;
		chance: number;
		runs: number;
		bal: number;
		knockout: number[];
	}
	let { rows }: { rows: Row[] } = $props();

	const K = $derived(rows[0]?.knockout.length ?? 6);
	const X0 = 190;
	const COL = 72;
	const ROW = 46;
	const BAR = 30;
	/** Fraction of the above-chance accuracy that this arity's read-out carries. */
	const lost = (r: Row, k: number) =>
		Math.max(0, Math.min(1, (r.bal - r.knockout[k]) / Math.max(1e-6, r.bal - r.chance)));
</script>

<svg
	viewBox="0 0 {X0 + K * COL} {30 + rows.length * ROW}"
	role="img"
	aria-label="Accuracy lost when each arity of a trained Newton attention layer is switched off"
>
	{#each Array.from({ length: K }, (_, k) => k) as k (k)}
		<text class="col" x={X0 + k * COL + COL / 2} y="14" text-anchor="middle">k = {k + 1}</text>
	{/each}
	{#each rows as r, i (r.task)}
		{@const y = 30 + i * ROW}
		<text class="task" x="0" y={y + BAR / 2 + 4}>{r.label}</text>
		<text class="acc" x={X0 - 22} y={y + BAR / 2 + 4} text-anchor="end"
			>{(r.bal * 100).toFixed(0)}%</text
		>
		<line class="base" x1={X0} x2={X0 + K * COL - 14} y1={y + BAR} y2={y + BAR} />
		{#each r.knockout.keys() as k (k)}
			{@const f = lost(r, k)}
			{@const h = Math.max(1, f * BAR)}
			<rect
				class="bar"
				class:used={f > 0.25}
				x={X0 + k * COL + COL / 2 - 14}
				y={y + BAR - h}
				width="28"
				height={h}
				rx="1.5"
			/>
			{#if f > 0.05}
				<text class="val" class:used={f > 0.25} x={X0 + k * COL + COL / 2 + 18} y={y + BAR - h + 8}
					>{(f * 100).toFixed(0)}%</text
				>
			{/if}
		{/each}
	{/each}
</svg>

<style>
	svg {
		width: 100%;
		max-width: 640px;
		height: auto;
		overflow: visible;
		font-family: var(--font-sans);
	}
	.col {
		font-family: 'KaTeX_Main', serif;
		font-style: italic;
		font-size: 12px;
		fill: var(--color-ink-3);
	}
	.task {
		font-size: 12px;
		fill: var(--color-ink-2);
	}
	.acc {
		font-size: 11px;
		fill: var(--color-ink-3);
		font-variant-numeric: tabular-nums;
	}
	.base {
		stroke: #262626;
		stroke-width: 1;
	}
	.bar {
		fill: #333;
	}
	.bar.used {
		fill: var(--color-ink);
	}
	.val {
		font-size: 10px;
		fill: var(--color-ink-3);
		font-variant-numeric: tabular-nums;
	}
	.val.used {
		fill: var(--color-ink-2);
	}
</style>
