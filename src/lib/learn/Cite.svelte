<script lang="ts">
	/** Numbered citation(s) linking to a reference list, e.g. [3, 4]. Learn's list by default. */
	import { REFERENCES, type Reference } from './references.ts';

	let { id, refs = REFERENCES }: { id: string | string[]; refs?: Reference[] } = $props();
	const ids = $derived(Array.isArray(id) ? id : [id]);
	const cite = (r: string) => refs.findIndex((x) => x.id === r) + 1;
</script>

<span class="cite"
	>[{#each ids as r, i (r)}{#if i > 0},&nbsp;{/if}<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- in-page anchor --><a
			href="#ref-{r}">{cite(r)}</a
		>{/each}]</span
>

<style>
	.cite {
		font-size: 0.82em;
		color: var(--color-ink-3);
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
	}
	.cite a {
		color: inherit;
		text-decoration: none;
	}
	.cite a:hover {
		color: var(--color-ink);
	}
</style>
