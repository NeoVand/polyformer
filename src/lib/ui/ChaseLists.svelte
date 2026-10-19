<script lang="ts">
	/**
	 * A pointer-chase instance as its linked lists: each node shows its id and a
	 * payload chip; the list the query starts in is lit and its start is ringed.
	 */
	import { solveChase, type ChaseInstance } from '#lib/chase/chase.ts';

	let { instance, compact = false }: { instance: ChaseInstance; compact?: boolean } = $props();

	const answer = $derived(solveChase(instance));
	const lists = $derived.by(() => {
		const byId = new Map(instance.nodes.map((nd, i) => [nd.id, i]));
		const pointed = new Set(
			instance.nodes.filter((nd) => nd.pointer !== nd.id).map((nd) => byId.get(nd.pointer)!)
		);
		const out: number[][] = [];
		instance.nodes.forEach((_, i) => {
			if (pointed.has(i)) return;
			const list = [i];
			let cur = i;
			for (;;) {
				const nx = byId.get(instance.nodes[cur].pointer)!;
				if (nx === cur) break;
				list.push(nx);
				cur = nx;
			}
			out.push(list);
		});
		return out.sort((a, b) => b.length - a.length);
	});
</script>

<div class="lists" class:compact role="img" aria-label="Linked lists; the query starts at node {instance.start}">
	{#each lists as list, li (li)}
		<div class="list" class:on={list.includes(answer.path[0])}>
			{#each list as i, at (i)}
				{@const nd = instance.nodes[i]}
				{#if at > 0}<span class="arrow" aria-hidden="true">→</span>{/if}
				<span class="chip" class:start={nd.id === instance.start}><b>{nd.id}</b><i>{nd.payload}</i></span>
			{/each}
			<span class="arrow" aria-hidden="true">⟲</span>
		</div>
	{/each}
</div>

<style>
	.lists {
		display: flex;
		flex-wrap: wrap;
		gap: 6px 22px;
	}
	.lists.compact {
		gap: 6px 16px;
	}
	.list {
		display: flex;
		align-items: baseline;
		gap: 6px;
		color: var(--color-ink-3);
	}
	.list.on {
		color: var(--color-ink);
	}
	.chip {
		font-size: var(--text-sm);
		font-variant-numeric: tabular-nums;
	}
	.chip b {
		font-weight: 500;
	}
	/* the payload, as a quiet subscript */
	.chip i {
		margin-left: 1px;
		font-style: normal;
		font-size: 10px;
		opacity: 0.6;
		vertical-align: sub;
	}
	.chip.start b {
		text-decoration: underline;
		text-underline-offset: 3px;
	}
	.arrow {
		font-size: var(--text-2xs);
		opacity: 0.5;
	}
</style>
