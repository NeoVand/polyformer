<script lang="ts">
	import { asset, resolve } from '$app/paths';
	import { onMount } from 'svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import { Feynman, Newton, Simplex } from '#lib/ui/icons.ts';
	import A5Rotation from '#lib/viz/A5Rotation.svelte';
	import {
		cycleLabel,
		elements,
		idealRotations,
		identity,
		multiply,
		type A5Recording
	} from '#lib/viz/a5.ts';

	let recording = $state.raw<A5Recording | null>(null);
	let loadError = $state(false);
	let model = $state<'ideal' | 'recorded'>('ideal');
	let element = $state(13);
	let orderStep = $state(2);
	const a = 1;
	const b = 12;
	const rotationA = $derived(recording?.elements[a].ideal ?? idealRotations[a]);
	const rotationB = $derived(recording?.elements[b].ideal ?? idealRotations[b]);
	const leftProduct = $derived(
		orderStep === 0 ? identity : orderStep === 1 ? rotationA : multiply(rotationB, rotationA)
	);
	const rightProduct = $derived(
		orderStep === 0 ? identity : orderStep === 1 ? rotationB : multiply(rotationA, rotationB)
	);
	const selected = $derived(cycleLabel(elements[element]));

	onMount(() => {
		const controller = new AbortController();
		fetch(asset('recorded/a5-irrep.json'), { signal: controller.signal })
			.then((response) => {
				if (!response.ok) throw new Error('Recording unavailable');
				return response.json();
			})
			.then((data: A5Recording) => {
				recording = data;
				model = 'recorded';
			})
			.catch((error) => {
				if (error.name !== 'AbortError') loadError = true;
			});
		return () => controller.abort();
	});
</script>

<svelte:head>
	<title>Holonomy · Polyformer</title>
	<meta
		name="description"
		content="Inspect the sixty rotations learned by a holonomy attention head, and see why the order of composition matters."
	/>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'tensor', label: 'Cubic', icon: Simplex, href: resolve('/explore') },
		{ id: 'diagrams', label: 'Feynman', icon: Feynman, href: resolve('/explore/diagrams') },
		{ id: 'newton', label: 'Newton', icon: Newton, href: resolve('/explore/newton') },
		{ id: 'groups', label: 'Holonomy', icon: Simplex, href: resolve('/explore/groups') }
	]}
	active="groups"
>
	<div class="lab">
		<header>
			<p class="eyebrow">Composition lab</p>
			<h1>Learning to turn</h1>
			<p class="intro">
				An icosahedron has 60 rotational symmetries. Can a neural layer discover them from labels
				alone?
			</p>
		</header>
		<section class="experiment" aria-label="Compare ideal and learned rotations">
			<div class="toolbar">
				<span class="selection"
					>Element <strong>{String(element).padStart(2, '0')}</strong><span>{selected}</span></span
				>
				<div class="model-switch" role="group" aria-label="Model">
					<span>Model</span>
					<button
						aria-pressed={model === 'ideal'}
						onclick={() => {
							model = 'ideal';
						}}>Ideal</button
					>
					<button
						disabled={!recording}
						aria-pressed={model === 'recorded'}
						onclick={() => {
							model = 'recorded';
						}}>Recorded</button
					>
				</div>
			</div>
			<div class="comparison">
				<figure>
					<div class="solid"><A5Rotation {element} {recording} /></div>
					<figcaption>
						<strong>Ideal symmetry</strong><span>Computed from the group law</span>
					</figcaption>
				</figure>
				<figure>
					<div class="solid"><A5Rotation {element} {model} {recording} /></div>
					<figcaption>
						<strong
							>{model === 'recorded'
								? `Learned head ${(recording?.selectedHead ?? 0) + 1}`
								: 'Ideal reference'}</strong
						>
						<span
							>{model === 'recorded'
								? 'One head, aligned to the same axes'
								: 'Switch to Recorded to compare'}</span
						>
					</figcaption>
				</figure>
			</div>
			<p class="figure-note">
				The solid dot tracks one vertex. The open dot marks its starting point. A symmetry returns
				the shape to itself while moving its vertices.
			</p>
			<div class="element-heading">
				<span>Choose a rotation</span><span class="quiet">All 60 group elements</span>
			</div>
			<div class="elements" role="group" aria-label="Group element">
				{#each elements as permutation, index (permutation.join(''))}
					<button
						aria-label={`Element ${index}: ${cycleLabel(permutation)}`}
						aria-pressed={element === index}
						onclick={() => {
							element = index;
						}}>{String(index).padStart(2, '0')}</button
					>
				{/each}
			</div>
		</section>
		<aside aria-label="What the recording shows">
			<h2>A rotation for each token</h2>
			<p>
				<strong>A group</strong> is a collection of reversible moves that stays inside the
				collection when moves are combined. Here the moves are the rotations of an icosahedron; the
				group is called <strong>A₅</strong>.
			</p>
			<p>
				A <strong>representation</strong> gives each move a matrix, so combining moves agrees with multiplying
				their matrices. The model learns a 3 × 3 rotation for every token.
			</p>
			<h2>What was measured</h2>
			{#if recording}
				<dl>
					<div>
						<dt>Held-out balanced accuracy</dt>
						<dd>{(recording.training.result.bal_acc * 100).toFixed(2)}%</dd>
					</div>
					<div>
						<dt>Composition error</dt>
						<dd>{recording.homomorphismError.toFixed(3)}</dd>
					</div>
					<div>
						<dt>Training steps</dt>
						<dd>{recording.training.result.steps.toLocaleString('en-US')}</dd>
					</div>
					<div>
						<dt>Seed / head dimension</dt>
						<dd>0 / 3</dd>
					</div>
				</dl>
				<p class="small">
					Composition error compares “multiply the two learned rotations” with “look up the learned
					product,” averaged over all 3,600 pairs. Zero would be an exact representation.
				</p>
				<p class="small">
					This is the head with the lowest error among 85 heads, selected after training. A single
					change of axes aligns it to the ideal; the recorded matrices are otherwise unchanged.
				</p>
				<a class="source" href={asset('recorded/a5-irrep.json')} download
					>Download matrices and provenance ↗</a
				>
			{:else}
				<p class="small">
					{loadError
						? 'The recording could not be loaded. The computed ideal remains available.'
						: 'Loading the recorded model…'}
				</p>
			{/if}
			<p class="small">
				Training task: mark each token that belongs to an in-order triple whose combined move does
				nothing. Holonomy attention reads sums of ordered matrix products over subsets containing
				that token. No rotation target was supplied. This is a fresh run of the registered
				configuration.
			</p>
		</aside>
		<section class="order" aria-label="Order matters">
			<div class="order-copy">
				<h2>Same moves. Different ending.</h2>
				<p>
					Apply rotation A then B, or B then A. The marked vertex ends in different places: these
					moves do not commute. A is element 01; B is element 12.
				</p>
				<div class="steps" role="group" aria-label="Composition step">
					{#each [{ value: 0, label: 'Start' }, { value: 1, label: 'First move' }, { value: 2, label: 'Both moves' }] as step (step.value)}
						<button
							aria-pressed={orderStep === step.value}
							onclick={() => {
								orderStep = step.value;
							}}>{step.label}</button
						>
					{/each}
				</div>
			</div>
			<figure>
				<div class="order-solid">
					<A5Rotation {recording} matrix={leftProduct} label="Rotation A followed by B" />
				</div>
				<figcaption>
					<strong>A → B</strong><span
						>{orderStep === 0 ? 'Start' : orderStep === 1 ? 'After A' : 'After both moves'}</span
					>
				</figcaption>
			</figure>
			<figure>
				<div class="order-solid">
					<A5Rotation {recording} matrix={rightProduct} label="Rotation B followed by A" />
				</div>
				<figcaption>
					<strong>B → A</strong><span
						>{orderStep === 0 ? 'Start' : orderStep === 1 ? 'After B' : 'After both moves'}</span
					>
				</figcaption>
			</figure>
		</section>
	</div>
</PageFrame>

<style>
	.lab {
		max-width: 1480px;
		margin: 0 auto;
		padding: 26px 32px 24px;
		display: grid;
		grid-template-columns: minmax(0, 1fr) 284px;
		gap: 20px 36px;
	}
	header {
		grid-column: 1;
	}
	.eyebrow {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.14em;
		color: var(--color-ink-3);
		margin-bottom: 6px;
	}
	h1 {
		font-size: 32px;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-weight: 400;
		line-height: 1.15;
	}
	.intro {
		font-size: 13px;
		color: var(--color-ink-2);
		max-width: 65ch;
		line-height: 1.6;
		margin-top: 8px;
	}
	.experiment {
		min-width: 0;
		grid-column: 1;
	}
	.toolbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		font-size: 12px;
	}
	.selection {
		display: flex;
		gap: 12px;
		color: var(--color-ink-3);
		align-items: baseline;
	}
	.selection strong {
		color: var(--color-ink);
		font-family: var(--font-mono);
		font-weight: 500;
	}
	.model-switch,
	.steps {
		display: flex;
		align-items: center;
		gap: 14px;
	}
	.model-switch > span {
		color: var(--color-ink-3);
		margin-right: 2px;
		font-size: 11px;
	}
	button {
		border: 0;
		border-radius: 0;
		background: transparent;
		padding: 5px 0;
		font-size: 12px;
		color: var(--color-ink-3);
		cursor: pointer;
	}
	button:hover,
	button[aria-pressed='true'] {
		color: var(--color-ink);
	}
	button:disabled {
		opacity: 0.4;
		cursor: default;
	}
	button[aria-pressed='true'] {
		text-decoration: underline;
		text-underline-offset: 7px;
		text-decoration-thickness: 1px;
	}
	.comparison {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 30px;
	}
	figure {
		margin: 0;
		min-width: 0;
	}
	.solid {
		height: min(30vh, 290px);
		min-height: 240px;
	}
	figcaption {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		font-size: 12px;
		line-height: 1.4;
		text-align: center;
	}
	figcaption strong {
		font-weight: 450;
		color: var(--color-ink);
	}
	figcaption span {
		color: var(--color-ink-3);
		font-size: 11px;
	}
	.figure-note {
		font-size: 11px;
		color: var(--color-ink-3);
		margin: 17px auto 20px;
		max-width: 82ch;
		text-align: center;
		line-height: 1.55;
	}
	.element-heading {
		display: flex;
		justify-content: space-between;
		font-size: 11px;
		color: var(--color-ink-2);
		margin-bottom: 10px;
	}
	.quiet {
		color: var(--color-ink-3);
	}
	.elements {
		display: grid;
		grid-template-columns: repeat(20, 1fr);
		gap: 7px 2px;
	}
	.elements button {
		font-family: var(--font-mono);
		font-size: 11px;
		padding: 6px 0;
		min-height: 26px;
	}
	aside {
		grid-column: 2;
		grid-row: 1 / 3;
		padding-top: 2px;
	}
	h2 {
		font-size: 13px;
		font-weight: 500;
		margin-bottom: 10px;
		line-height: 1.4;
	}
	aside p {
		font-size: 12px;
		line-height: 1.65;
		color: var(--color-ink-2);
		margin-bottom: 16px;
	}
	aside strong {
		font-weight: 500;
		color: var(--color-ink);
	}
	aside h2:not(:first-child) {
		margin-top: 26px;
	}
	aside p.small {
		font-size: 11px;
		color: var(--color-ink-3);
		line-height: 1.65;
	}
	dl {
		margin: 0 0 16px;
	}
	dl div {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		font-size: 11px;
		padding: 6px 0;
	}
	dt {
		color: var(--color-ink-2);
	}
	dd {
		font-family: var(--font-mono);
		color: var(--color-ink);
	}
	.source {
		display: block;
		font-size: 11px;
		color: var(--color-ink-2);
		margin: 4px 0 20px;
	}
	.order {
		grid-column: 1 / -1;
		display: grid;
		grid-template-columns: minmax(210px, 1fr) minmax(140px, 0.6fr) minmax(140px, 0.6fr);
		gap: 30px;
		align-items: center;
		padding-top: 10px;
	}
	.order-copy {
		max-width: 42ch;
	}
	.order-copy p {
		color: var(--color-ink-2);
		font-size: 12px;
		line-height: 1.65;
		margin-bottom: 16px;
	}
	.order-solid {
		height: 170px;
	}
	.steps {
		gap: 18px;
	}
	.steps button {
		font-size: 11px;
	}
	@media (max-width: 1050px) {
		.lab {
			grid-template-columns: minmax(0, 1fr) 245px;
			gap: 20px 24px;
			padding: 24px;
		}
		.selection > span {
			display: none;
		}
		.elements {
			grid-template-columns: repeat(15, 1fr);
		}
	}
	@media (max-width: 760px) {
		.lab {
			grid-template-columns: 1fr;
			padding: 24px 20px 36px;
			gap: 24px;
		}
		aside {
			grid-column: 1;
			grid-row: auto;
		}
		.order {
			grid-column: 1;
			grid-row: 3;
			grid-template-columns: 1fr 1fr;
			gap: 16px;
			padding-top: 0;
		}
		.order-copy {
			grid-column: 1 / -1;
			max-width: none;
		}
		.order-solid {
			height: 160px;
		}
		.solid {
			min-height: 0;
			height: 170px;
		}
		.comparison {
			gap: 10px;
		}
		.elements {
			grid-template-columns: repeat(10, 1fr);
			gap: 4px 0;
		}
		.elements button {
			min-height: 30px;
		}
		.toolbar {
			gap: 8px;
		}
		.model-switch {
			gap: 11px;
		}
		.figure-note {
			margin-top: 16px;
			text-align: left;
		}
		h1 {
			font-size: 30px;
		}
	}
</style>
