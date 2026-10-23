<script lang="ts" module>
	export interface SeedRow {
		name: string;
		/** One entry per length: the seeds' exact-match values, or null where it was not measured. */
		cells: (number[] | null)[];
	}
</script>

<script lang="ts">
	/**
	 * Exactness by seed and length on one grid: a filled dot is a seed exact at that length
	 * (exact match ≥ 0.99), a ring is one that is not, filled in proportion to its exact match.
	 */
	let {
		lengths,
		rows,
		axis,
		label
	}: { lengths: number[]; rows: SeedRow[]; axis: string; label: string } = $props();

	const EXACT = 0.99;
	const LEFT = 104;
	const COL = 50;
	const ROW = 26;
	const TOP = 30;
	const R = 3.7;
	const GAP = 11;
	const W = $derived(LEFT + lengths.length * COL + 4);
	const H = $derived(TOP + rows.length * ROW + 22);
	const cx = (j: number, k: number, n: number) =>
		LEFT + j * COL + COL / 2 + (k - (n - 1) / 2) * GAP;
	const cy = (i: number) => TOP + i * ROW + ROW / 2;
	const fmt = (v: number) => v.toFixed(3);
</script>

<svg viewBox="0 0 {W} {H}" class="sg" role="img" aria-label={label}>
	{#each lengths as n, j (n)}
		<text class="tick" x={LEFT + j * COL + COL / 2} y="14" text-anchor="middle"
			>{n.toLocaleString('en')}</text
		>
	{/each}
	{#each rows as row, i (row.name)}
		<text class="name" x="0" y={cy(i) + 3.6}>{row.name}</text>
		{#each row.cells as seeds, j (j)}
			{#if seeds}
				{#each seeds as v, k (k)}
					{@const x = cx(j, k, seeds.length)}
					<g>
						<title>{row.name}, {lengths[j].toLocaleString('en')}, seed {k}: {fmt(v)}</title>
						{#if v >= EXACT}
							<circle class="exact" cx={x} cy={cy(i)} r={R} />
						{:else}
							<circle class="ring" cx={x} cy={cy(i)} r={R} />
							{#if v > 0}<circle class="part" cx={x} cy={cy(i)} r={R * Math.sqrt(v)} />{/if}
						{/if}
					</g>
				{/each}
			{:else}
				<text class="tick" x={LEFT + j * COL + COL / 2} y={cy(i) + 3.6} text-anchor="middle">–</text
				>
			{/if}
		{/each}
	{/each}
	<text class="tick" x={W - 4} y={H - 4} text-anchor="end">{axis}</text>
</svg>

<style>
	.sg {
		width: min(100%, 420px);
		height: auto;
		display: block;
		margin: 0 auto;
		font-family: var(--font-sans);
	}
	.exact {
		fill: var(--color-ink);
	}
	.ring {
		fill: none;
		stroke: var(--color-ink-3);
		stroke-width: 1;
	}
	.part {
		fill: var(--color-ink-3);
	}
	.tick {
		font-size: 9.5px;
		fill: var(--color-ink-3);
		font-variant-numeric: tabular-nums;
	}
	.name {
		font-size: 10.5px;
		fill: var(--color-ink);
	}
</style>
