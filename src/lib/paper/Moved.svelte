<script lang="ts">
	/**
	 * The old Learn and Report pages now forward to the paper. With JavaScript the reader lands
	 * on the matching section; without it, a meta refresh takes them to the top.
	 */
	import { resolve } from '$app/paths';
	import { movedAnchor } from './toc.ts';

	let { anchors, name }: { anchors: Record<string, string>; name: string } = $props();

	const paper = resolve('/paper');

	function forward() {
		const id = movedAnchor(anchors, location.hash);
		location.replace(id ? `${paper}#${id}` : paper);
	}
</script>

<svelte:head>
	<title>{name} has moved | Polyformer</title>
	<!-- only without JavaScript: a refresh would beat the script and drop the anchor -->
	<noscript><meta http-equiv="refresh" content="0; url={paper}" /></noscript>
	<link rel="canonical" href={paper} />
</svelte:head>

<main class="moved" {@attach forward}>
	<p>
		{name} is now part of one article.
		<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- resolved above -->
		<a href={paper}>Read Learning to compose</a>.
	</p>
</main>

<style>
	.moved {
		max-width: 680px;
		margin: 0 auto;
		padding: 80px clamp(16px, 4vw, 40px);
		color: var(--color-ink-2);
	}
	a {
		color: var(--color-ink);
		text-decoration: underline;
		text-underline-offset: 3px;
	}
</style>
