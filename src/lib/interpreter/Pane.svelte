<script lang="ts">
	/** One of the five views of the inside of the model: a numbered heading with its data source, then the view. */
	import type { Snippet } from 'svelte';
	import type { PanelSource } from './trace.ts';
	import SourceLabel from './SourceLabel.svelte';

	let {
		n,
		title,
		source,
		short,
		none,
		class: className = '',
		children
	}: {
		n: number;
		title: string;
		source: PanelSource | null | undefined;
		short?: string;
		/** the source label's word when there is no data */
		none?: string;
		class?: string;
		children: Snippet;
	} = $props();
</script>

<section class={['pane', className]} aria-label={title}>
	<header>
		<h2><span class="n num">{n}</span>{title}</h2>
		<SourceLabel {source} {short} {none} />
	</header>
	<div class="body">{@render children()}</div>
</section>

<style>
	.pane {
		display: flex;
		flex-direction: column;
		height: 100%;
		min-width: 0;
		min-height: 0;
		padding: 12px 16px 14px;
	}
	header {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 12px;
		min-width: 0;
		margin-bottom: 10px;
	}
	h2 {
		display: flex;
		align-items: baseline;
		gap: 9px;
		font-size: var(--text-sm);
		font-weight: 500;
		line-height: 1.3;
		white-space: nowrap;
	}
	.n {
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		font-weight: 400;
		color: var(--color-ink-3);
	}
	.body {
		flex: 1;
		min-height: 0;
		display: flex;
		flex-direction: column;
	}
	.body > :global(*) {
		flex: 1;
		min-height: 0;
	}
</style>
