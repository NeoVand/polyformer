<script lang="ts">
	// Sketchpad moved to its own site, with its paper and demo; this route sends visitors there.
	const DEMO = 'https://neovand.github.io/sketchpad/demo';
	const PAPER = 'https://neovand.github.io/sketchpad/';
</script>

<svelte:head>
	<title>Sketchpad · moved</title>
	<meta http-equiv="refresh" content="0; url={DEMO}" />
	<link rel="canonical" href={DEMO} />
</svelte:head>

<main class="moved">
	<h1>Sketchpad has moved</h1>
	<p>
		The demo is now at <a href={DEMO}>neovand.github.io/sketchpad/demo</a>, next to its
		<a href={PAPER}>paper</a>.
	</p>
</main>

<style>
	.moved {
		max-width: 640px;
		margin: 96px auto;
		padding: 0 16px;
	}
	h1 {
		font-size: 28px;
		font-weight: 500;
	}
	p {
		margin-top: 12px;
		font-size: 14px;
	}
</style>
