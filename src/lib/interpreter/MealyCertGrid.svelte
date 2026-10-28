<script lang="ts">
	/**
	 * A Mealy register's certificate: one square per row, a block per carry with the first digit down and the second
	 * across, each square split into its two cells, the carry (left) and the digit written (right), each shaded by its
	 * own margin. A cell whose argmax is not what the row wrote is outlined; a row not checked yet is hollow.
	 */
	import { certLayout } from './mealy.ts';
	import type { ProgramRow } from './trace.ts';

	let {
		rows,
		states,
		current,
		pending = false
	}: {
		rows: ProgramRow[];
		states: string[];
		/** the row the playhead reads, or -1 */
		current: number;
		pending?: boolean;
	} = $props();

	const CELL = 9;
	const TOP = 9;
	const layout = $derived(certLayout(rows, states));
	const margins = $derived(
		rows.flatMap((r) => [r.m, r.m2]).filter((m): m is number => m !== undefined && !Number.isNaN(m))
	);
	const lo = $derived(margins.length ? Math.min(...margins) : 0);
	const hi = $derived(margins.length ? Math.max(...margins) : 0);
	const shade = (m: number | undefined) =>
		m === undefined || Number.isNaN(m) ? 1 : hi > lo ? 0.35 + (0.6 * (m - lo)) / (hi - lo) : 0.8;
	const top = $derived(layout.blocks.length ? TOP : 0);
	const half = (CELL - 1.5) / 2 - 0.25;
</script>

<svg
	class="grid"
	style:width="min(100%, {layout.cols * 13}px)"
	viewBox="0 0 {layout.cols * CELL} {layout.height * CELL + top}"
	role="img"
	aria-label="Every row's two cells and their margins"
>
	{#each layout.blocks as b (b.x)}
		<text x={b.x * CELL} y={6} class="blabel">carry {b.label}</text>
	{/each}
	{#each layout.cells as c (c.k)}
		{@const r = rows[c.k]}
		{@const x = c.x * CELL}
		{@const y = c.y * CELL + top}
		{@const todo = r.ok === undefined && pending}
		{@const badT = r.ok === false && r.argmax !== undefined}
		{@const badO = r.ok === false && r.argmax2 !== undefined}
		<rect
			{x}
			{y}
			width={half}
			height={CELL - 1.5}
			rx="0.6"
			class={['cell', todo && 'todo', badT && 'wrong']}
			style:opacity={todo || badT ? 1 : shade(r.m)}
		/>
		<rect
			x={x + half + 0.5}
			{y}
			width={half}
			height={CELL - 1.5}
			rx="0.6"
			class={['cell', todo && 'todo', badO && 'wrong']}
			style:opacity={todo || badO ? 1 : shade(r.m2)}
		/>
		{#if c.k === current}
			<rect x={x - 1.25} y={y - 1.25} width={CELL + 1} height={CELL + 1} rx="1.5" class="now" />
		{/if}
	{/each}
</svg>

<style>
	.grid {
		display: block;
		width: 100%;
		max-width: 300px;
		overflow: visible;
	}
	.blabel {
		font-family: var(--font-mono);
		font-size: 6px;
		fill: var(--color-ink-3);
	}
	.cell {
		fill: var(--color-ink);
	}
	.cell.todo {
		fill: none;
		stroke: var(--color-rule);
		stroke-width: 0.6;
	}
	.cell.wrong {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 0.9;
		stroke-dasharray: 1.2 0.8;
	}
	.now {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1.2;
	}
</style>
