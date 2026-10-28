<script lang="ts">
	/** Where a panel's data comes from. Mock data says so in words, in the panel's own heading. */
	import type { PanelSource } from './trace.ts';

	let {
		source,
		short,
		none = 'not recorded'
	}: { source: PanelSource | null | undefined; short?: string; none?: string } = $props();

	const kind = $derived(!source || !source.source ? 'none' : source.mock ? 'mock' : 'measured');
	const word = $derived(kind === 'mock' ? 'mock' : kind === 'measured' ? 'measured' : none);
</script>

<span class={['src', kind]} title={source?.note}>
	<span class="word">{word}</span>{#if short}<span class="short">{short}</span>{/if}
</span>

<style>
	.src {
		display: inline-flex;
		align-items: baseline;
		gap: 6px;
		min-width: 0;
		font-size: var(--text-2xs);
		line-height: 1.3;
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.word {
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-size: 10px;
	}
	.short {
		overflow: hidden;
		text-overflow: ellipsis;
	}
	/* mock is the one label that must never be missed: full ink and a dashed rule under the word */
	.mock .word {
		color: var(--color-ink);
		font-weight: 500;
		text-decoration: underline dashed;
		text-underline-offset: 3px;
		text-decoration-thickness: 1px;
	}
	.mock .short {
		color: var(--color-ink-2);
	}
	.none .word {
		color: var(--color-ink-3);
	}
</style>
