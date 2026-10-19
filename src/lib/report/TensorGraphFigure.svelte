<script lang="ts">
	/**
	 * Figure 2 of the report: one cubic head on twelve SET cards, as a score tensor and as
	 * attention on hyperedges, with one shared query. A slow tour visits every card in a
	 * SET until the reader picks a card or a voxel.
	 */
	import { onMount } from 'svelte';
	import { dealTable, strongestEdges, tourStops } from '#lib/explore/deal.ts';
	import { LAYOUT_SIZE } from '#lib/set/cards.ts';
	import SetCard from '#lib/ui/SetCard.svelte';
	import Hypergraph3D from '#lib/viz/Hypergraph3D.svelte';
	import TensorCube from '#lib/viz/TensorCube.svelte';

	const table = dealTable(3);
	const { layout, sets, volume } = table;
	const STOPS = tourStops(table);

	let query = $state(STOPS[0].i);
	let pick = $state<{ j: number; k: number } | null>(STOPS[0].pair);
	let stop = 0;
	let touring = $state(false);
	const edges = $derived(strongestEdges(table, query));
	const selected = $derived(pick ?? (edges[0] ? { j: edges[0].j, k: edges[0].k } : null));
	const inSet = $derived(
		selected ? sets.some((s) => [query, selected.j, selected.k].every((c) => s.includes(c))) : false
	);

	onMount(() => {
		touring = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	});
	$effect(() => {
		if (!touring) return;
		const id = setInterval(() => {
			if (document.hidden) return;
			stop = (stop + 1) % STOPS.length;
			query = STOPS[stop].i;
			pick = STOPS[stop].pair;
		}, 4200);
		return () => clearInterval(id);
	});
</script>

<div class="pair">
	<div class="view">
		<TensorCube
			values={volume}
			n={LAYOUT_SIZE}
			{query}
			{selected}
			spin={0.6}
			label="The attention tensor of twelve SET cards"
			onpick={(c) => {
				touring = false;
				query = c.i;
				pick = { j: c.j, k: c.k };
			}}
		/>
	</div>
	<div class="view">
		<Hypergraph3D
			{layout}
			{query}
			{edges}
			{selected}
			{sets}
			spin={1}
			onquery={(c) => {
				touring = false;
				query = c;
				pick = null;
			}}
			onedge={(e) => {
				touring = false;
				pick = e;
			}}
		/>
	</div>
</div>
{#if selected}
	<p class="readout" aria-live="polite">
		<span class="cards">
			<SetCard card={layout[query]} width={18} />
			<SetCard card={layout[selected.j]} width={18} />
			<SetCard card={layout[selected.k]} width={18} />
		</span>
		Query card {query + 1} with cards {selected.j + 1} and {selected.k + 1}: {inSet
			? 'a SET, so the score is maximal'
			: 'not a SET'}.
	</p>
{/if}

<style>
	.pair {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 12px;
	}
	.view {
		position: relative;
		height: 340px;
	}
	.readout {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 6px 0 0;
		min-height: 22px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.cards {
		display: inline-flex;
		gap: 4px;
	}
	@media (max-width: 760px) {
		.pair {
			grid-template-columns: minmax(0, 1fr);
		}
		.view {
			height: 300px;
		}
	}
</style>
