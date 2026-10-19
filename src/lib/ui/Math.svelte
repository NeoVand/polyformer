<script lang="ts">
	/** KaTeX, rendered at prerender time. Math serif is reserved for equations. */
	import katex from 'katex';

	let { tex, display = false }: { tex: string; display?: boolean } = $props();

	const html = $derived(
		katex.renderToString(tex, { displayMode: display, throwOnError: false, output: 'html' })
	);
</script>

<!-- eslint-disable-next-line svelte/no-at-html-tags -- KaTeX output from our own TeX strings -->
<span class={['math', display && 'display']}>{@html html}</span>

<style>
	.math.display {
		display: block;
		overflow-x: auto;
		overflow-y: hidden;
		padding: 2px 0;
	}
	.math.display :global(.katex-display) {
		margin: 0.4em 0;
		text-align: left;
	}
</style>
