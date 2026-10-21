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

	const captioned = $derived(terms.some((t) => t.caption));
</script>

<div class="sum" class:captioned role="img" aria-label="Diagram expansion">
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
	/* every diagram, operator and the left side share one centre line; captions hang
	   below their diagram without changing its box */
	.sum {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: center;
		gap: 10px 7px;
		margin: 8px 0 16px;
	}
	.sum.captioned {
		row-gap: 30px;
		margin-bottom: 34px;
	}
	figure {
		position: relative;
		margin: 0;
		line-height: 0;
	}
	figcaption {
		position: absolute;
		top: calc(100% + 6px);
		left: 50%;
		transform: translateX(-50%);
		font-size: 12px;
		line-height: 1;
		white-space: nowrap;
		color: var(--color-ink-3);
	}
	figcaption :global(.katex) {
		color: var(--color-ink-3);
	}
	.op {
		display: inline-flex;
		align-items: center;
		font-size: 17px;
		line-height: 1;
	}
	/* KaTeX centres its box, not the math axis that + and = sit on */
	.op :global(.katex) {
		position: relative;
		top: -0.09em;
	}
</style>
