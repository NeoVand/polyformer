<script lang="ts">
	/** A row of diagrams read as an equation: lhs = term + term + … , each term optionally captioned. */
	import MathTex from '#lib/ui/Math.svelte';
	import QedDiagram, { type QedKind } from './QedDiagram.svelte';

	let {
		lhs,
		terms,
		width = 84,
		more = true
	}: {
		lhs: QedKind;
		terms: { kind: QedKind; caption?: string }[];
		width?: number;
		/** End with "+ …". */
		more?: boolean;
	} = $props();
</script>

<div class="sum" role="img" aria-label="Diagram expansion">
	<figure><QedDiagram kind={lhs} {width} /></figure>
	<span class="op"><MathTex tex="=" /></span>
	{#each terms as t, i (i)}
		{#if i > 0}<span class="op"><MathTex tex="+" /></span>{/if}
		<figure>
			<QedDiagram kind={t.kind} {width} />
			{#if t.caption}<figcaption><MathTex tex={t.caption} /></figcaption>{/if}
		</figure>
	{/each}
	{#if more}<span class="op"><MathTex tex="+ \cdots" /></span>{/if}
</div>

<style>
	.sum {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px 7px;
		margin: 8px 0 16px;
	}
	figure {
		display: grid;
		justify-items: center;
		gap: 4px;
		margin: 0;
	}
	figcaption {
		font-size: 12px;
		color: var(--color-ink-3);
	}
	figcaption :global(.katex) {
		color: var(--color-ink-3);
	}
	.op {
		font-size: 17px;
	}
</style>
