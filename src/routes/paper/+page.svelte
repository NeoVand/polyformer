<script lang="ts">
	import '#lib/paper/paper.css';
	import { REFERENCES } from '#lib/learn/references.ts';
	import { PARTS } from '#lib/paper/toc.ts';
	import Question from '#lib/paper/parts/Question.svelte';
	import Pairs from '#lib/paper/parts/Pairs.svelte';
	import Feynman from '#lib/paper/parts/Feynman.svelte';
	import Newton from '#lib/paper/parts/Newton.svelte';
	import Language from '#lib/paper/parts/Language.svelte';
	import Turn from '#lib/paper/parts/Turn.svelte';
	import Results from '#lib/paper/parts/Results.svelte';
	import Limits from '#lib/paper/parts/Limits.svelte';
	import Memory from '#lib/paper/parts/Memory.svelte';
	import Lessons from '#lib/paper/parts/Lessons.svelte';

	const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'];

	/** A thin bar under the top bar shows how far down the article the reader is. */
	let progress = $state(0);
	function track() {
		const update = () => {
			const max = document.documentElement.scrollHeight - window.innerHeight;
			progress = max > 0 ? Math.min(1, window.scrollY / max) : 0;
		};
		update();
		window.addEventListener('scroll', update, { passive: true });
		window.addEventListener('resize', update);
		return () => {
			window.removeEventListener('scroll', update);
			window.removeEventListener('resize', update);
		};
	}
</script>

<svelte:head>
	<title>Learning to compose | Polyformer</title>
	<meta
		name="description"
		content="A research story about attention, higher-order relations and composition: what layers that look at groups of tokens can learn, where they fail, and what that teaches about finding structure."
	/>
</svelte:head>

<div class="progress" style:transform="scaleX({progress})" aria-hidden="true" {@attach track}></div>

<main class="paper">
	<header class="title-block">
		<h1>Learning to compose</h1>
		<p class="subtitle">
			From attention over pairs to layers that learn symmetry: what we tried, what worked, and what
			it taught us.
		</p>
		<p class="byline">
			<span><b>Mostafa “Neo” Mohsenvand</b></span>
			<span>October 2026</span>
			<span>Working paper, with live figures</span>
		</p>
	</header>

	<nav class="toc" aria-label="Contents">
		<h2>Contents</h2>
		<ol>
			{#each PARTS as part, i (part.id)}
				<li>
					<span class="roman">{ROMAN[i]}</span>
					<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- in-page anchor -->
					<a class="part-link" href="#{part.id}">{part.title}</a>
					<span class="chapters"
						>{#each part.sections as s (s.id)}<span
								><!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- in-page anchor --><a
									href="#{s.id}">{s.title}</a
								></span
							>{/each}</span
					>
				</li>
			{/each}
		</ol>
	</nav>

	<Question />
	<Pairs />
	<Feynman />
	<Newton />
	<Language />
	<Turn />
	<Results />
	<Limits />
	<Memory />
	<Lessons />

	<section class="refs part" id="references">
		<header class="part-head">
			<h2>References</h2>
		</header>
		<ol>
			{#each REFERENCES as r (r.id)}
				<li id="ref-{r.id}">
					<span class="who">{r.authors}.</span>
					{#if r.url}
						<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- external link -->
						<a href={r.url} rel="external noopener noreferrer" target="_blank">{r.title}</a>.
					{:else}
						{r.title}.
					{/if}
					{r.venue}, {r.year}.
				</li>
			{/each}
		</ol>
	</section>
</main>

<style>
	.progress {
		position: fixed;
		top: var(--bar-h);
		left: 0;
		right: 0;
		z-index: 19;
		height: 2px;
		background: var(--color-ink-3);
		transform-origin: 0 50%;
		pointer-events: none;
	}
</style>
