<script lang="ts">
	/** A feature vector as a strip of grayscale cells: 0 is mid-gray, + brighter, − darker. */
	import { shade } from './Heatmap.svelte';

	let {
		values,
		max,
		label,
		cell = 12
	}: { values: ArrayLike<number>; max: number; label: string; cell?: number } = $props();

	const cells = $derived(Array.from(values, (v) => shade(v, max, 'signed')));
</script>

<div class="strip" role="img" aria-label={label} style:--cell="{cell}px">
	{#each cells as s, i (i)}
		<span style:background="rgb({s} {s} {s})"></span>
	{/each}
</div>

<style>
	.strip {
		display: flex;
		gap: 1px;
		padding: 1px;
		background: var(--color-void);
		border-radius: 2px;
		width: max-content;
	}
	span {
		width: var(--cell);
		height: 14px;
	}
</style>
