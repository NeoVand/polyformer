<script lang="ts">
	/**
	 * Figure 5 of the report: the tree expansion of Theorem 3 for two trained models, drawn as
	 * Feynman diagrams. On SET the probed card's state is one cubic vertex joining its two SET
	 * partners; on pointer chasing the query's state is a chain of hops along the list.
	 */
	import { asset } from '$app/paths';
	import { CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
	import type { DiagramResult } from '#lib/engine/protocol.ts';
	import type { Card } from '#lib/set/cards.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import FeynmanDiagram from '#lib/viz/FeynmanDiagram.svelte';
	import { autoThreshold } from '#lib/viz/feynman.ts';

	let setRec = $state.raw<{ layout: number[][]; diagram: DiagramResult } | null>(null);
	let chaseRec = $state.raw<{ instance: ChaseInstance; diagram: DiagramResult } | null>(null);
	$effect(() => {
		const get = (path: Parameters<typeof asset>[0]) =>
			fetch(asset(path)).then((r) => (r.ok ? r.json() : null));
		get('recorded/set-diagram.json').then(
			(j) => j?.diagram && (setRec = j),
			() => {}
		);
		get('recorded/chase-diagram.json').then(
			(j) => j?.diagram && (chaseRec = j),
			() => {}
		);
	});
	/** One gutter, row pitch and top edge for both panels, so their rows and rounds line up. */
	const box = {
		padLeft: 44,
		padRight: 100,
		padTop: 34,
		padBottom: 6,
		maxRow: 44,
		valign: 'top' as const
	};
	const threshold = (d: DiagramResult, root: number) =>
		autoThreshold(d.perHead[0], d.n, d.rounds, d.modes, root, 6);
</script>

<div class="pair">
	<div class="diagram">
		<p class="sub"><span class="tag">(a)</span> SET, two rounds: one card's state</p>
		{#if setRec}
			{@const d = setRec.diagram}
			{@const cards = setRec.layout as unknown as Card[]}
			<FeynmanDiagram
				head={d.perHead[0]}
				n={d.n}
				rounds={d.rounds}
				modes={d.modes}
				root={d.token}
				options={{ threshold: threshold(d, d.token), perRound: 7 }}
				{box}
			>
				{#snippet row(t)}
					{#if t === 0}
						<span class="leg"><MathTex tex="\varnothing" /></span>
					{:else}
						<SetCard card={cards[t - 1]} width={18} />
					{/if}
				{/snippet}
			</FeynmanDiagram>
		{/if}
	</div>
	<div class="diagram">
		<p class="sub"><span class="tag">(b)</span> Pointer chase, four rounds: the query's state</p>
		{#if chaseRec}
			{@const d = chaseRec.diagram}
			{@const nodes = chaseRec.instance.nodes}
			<FeynmanDiagram
				head={d.perHead[0]}
				n={d.n}
				rounds={d.rounds}
				modes={d.modes}
				root={CHASE_QUERY_POS}
				options={{ threshold: threshold(d, CHASE_QUERY_POS), perRound: 7 }}
				{box}
			>
				{#snippet row(t)}
					<span class="leg"
						><MathTex
							tex={t === 0
								? '\\varnothing'
								: t === CHASE_QUERY_POS
									? 'q'
									: `v_{${nodes[t - 1].id}}`}
						/></span
					>
				{/snippet}
			</FeynmanDiagram>
		{/if}
	</div>
</div>

<style>
	.pair {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 36px;
	}
	.diagram {
		display: flex;
		flex-direction: column;
		min-width: 0;
		height: calc(var(--read, 15px) * 21);
	}
	.diagram :global(.feyn) {
		flex: 1;
		min-height: 0;
	}
	.sub {
		margin: 0 0 4px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.tag {
		margin-right: 4px;
		font-family: 'KaTeX_Main', serif;
		color: var(--color-ink-3);
	}
	.leg {
		font-size: 13px;
		color: var(--color-ink-2);
	}
	@media (max-width: 760px) {
		.pair {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
