<script lang="ts">
	/**
	 * One trained holonomy head beside the ideal 3-dimensional representation of A5, for any of
	 * the 60 group elements. The recording (static/recorded/a5-irrep.json) holds the head's actual
	 * matrices after one common change of basis.
	 */
	import { asset } from '$app/paths';
	import type { A5Recording } from '#lib/viz/a5.ts';
	import A5Rotation from '#lib/viz/A5Rotation.svelte';

	let recording = $state.raw<A5Recording | null>(null);
	let element = $state(12);
	let visible = $state(false);

	/** Mount the two WebGL views, and fetch the recording, only when the figure comes near the screen. */
	function nearby(node: HTMLElement) {
		const io = new IntersectionObserver(
			(entries) => {
				if (!entries.some((e) => e.isIntersecting)) return;
				visible = true;
				io.disconnect();
				fetch(asset('recorded/a5-irrep.json'))
					.then((r) => (r.ok ? r.json() : null))
					.then((d: A5Recording | null) => (recording = d))
					.catch(() => {});
			},
			{ rootMargin: '400px 0px' }
		);
		io.observe(node);
		return () => io.disconnect();
	}
	const step = (d: number) => (element = (element + d + 60) % 60);
</script>

<div class="a5" {@attach nearby}>
	<div class="views">
		<div class="view">
			<div class="stage">
				{#if visible}<A5Rotation {element} model="ideal" {recording} />{/if}
			</div>
			<span class="who">Ideal rotation<small>computed from the group's multiplication</small></span>
		</div>
		<div class="view">
			<div class="stage">
				{#if visible && recording}<A5Rotation {element} model="recorded" {recording} />{/if}
			</div>
			<span class="who">Learned rotation<small>one trained head, labels only</small></span>
		</div>
	</div>
	<div class="controls">
		<button onclick={() => step(-1)} aria-label="Previous element">←</button>
		<input type="range" min="0" max="59" bind:value={element} aria-label="Group element" />
		<button onclick={() => step(1)} aria-label="Next element">→</button>
		<span class="num el">element {element + 1} of 60</span>
	</div>
	{#if recording}
		<p class="stats num">
			Held-out accuracy {(recording.training.result.bal_acc * 100).toFixed(2)}% · composition error {recording.homomorphismError.toFixed(
				3
			)} (0 is an exact representation) · head {recording.selectedHead + 1} of 85
		</p>
	{/if}
</div>

<style>
	.a5 {
		display: grid;
		gap: 14px;
		width: 100%;
		justify-items: center;
	}
	.views {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 20px;
		width: min(100%, 720px);
	}
	.view {
		display: grid;
		align-content: start;
		gap: 6px;
		justify-items: center;
	}
	.stage {
		position: relative;
		width: 100%;
		aspect-ratio: 1;
		max-height: 320px;
	}
	.who {
		display: grid;
		justify-items: center;
		font-size: var(--text-sm);
		color: var(--color-ink);
		text-align: center;
	}
	.who small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.controls {
		display: flex;
		align-items: center;
		gap: 10px;
		width: min(100%, 460px);
	}
	.controls button {
		width: 28px;
		height: 28px;
		flex: none;
		border-radius: var(--radius-ui);
		background: var(--color-lift);
		color: var(--color-ink);
	}
	.controls button:hover {
		background: var(--color-control);
	}
	.controls input {
		flex: 1;
		min-width: 0;
		accent-color: #f2f2f2;
	}
	.el {
		flex: none;
		min-width: 98px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.stats {
		margin: 0;
		text-align: center;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	@media (max-width: 520px) {
		.views {
			gap: 10px;
		}
		.el {
			min-width: 0;
		}
	}
</style>
