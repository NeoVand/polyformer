<script lang="ts">
	import { onMount } from 'svelte';
	import { explain, type TickView } from './pad.svelte.ts';
	import type { TickOp } from './protocol.ts';
	import { B, CELL, GLYPHS } from './sprites.ts';
	import { theme } from './theme.svelte.ts';

	interface Props {
		/** the last tick, or null before the first */
		last: TickView | null;
		/** the view the model will read next (shown before the first tick) */
		next: { op: TickOp; cells: string[] } | null;
		sprites: string;
	}

	let { last, next, sprites }: Props = $props();

	let img = $state.raw<HTMLImageElement | null>(null);

	onMount(() => {
		const i = new Image();
		i.onload = () => (img = i);
		i.src = sprites;
	});

	const showOp = (op: TickOp) => (op === 'ADD-FAST' ? 'ADD' : op);

	/** the strip: the pixels the worker fed the model, or the next view assembled from the same sprites */
	function paint(canvas: HTMLCanvasElement) {
		const ctx = canvas.getContext('2d');
		if (!ctx) return;
		ctx.fillStyle = '#fff';
		ctx.fillRect(0, 0, CELL, 3 * CELL);
		if (last) {
			ctx.putImageData(new ImageData(new Uint8ClampedArray(last.strip), CELL, 3 * CELL), 0, 0);
		} else if (next && img) {
			const sheet = img;
			next.cells.forEach((g, k) => {
				const gi = GLYPHS.indexOf(g);
				if (gi >= 0) ctx.drawImage(sheet, gi * CELL, k * CELL, CELL, CELL, 0, k * CELL, CELL, CELL);
			});
		}
	}

	const tokens = $derived(last ? last.out.map((t) => (t === B ? '_' : t)) : []);
</script>

<div class="inset">
	<div class="sees">
		<p class="cap">What the model sees</p>
		<canvas {@attach paint} width={CELL} height={3 * CELL}></canvas>
		<code class="prompt">
			{#if last || next}{showOp((last ?? next)!.op)} ▢ ={/if}
		</code>
	</div>
	<div class="writes">
		<p class="cap">What it writes</p>
		{#if last}
			<div class="tokens">
				{#each tokens as t, i (i)}<span>{t}</span>{/each}
			</div>
			<p class="means">{explain(last.op, last.out)}</p>
			<p class="meta num">
				{#if last.margin !== null}margin {last.margin.toFixed(2)} ·
				{/if}{last.ms.toFixed(0)} ms
			</p>
		{:else}
			<p class="means idle">Its answer appears here at each tick.</p>
		{/if}
	</div>
	{#if theme.current === 'dark'}
		<p class="truth">True input pixels: the model reads black on white.</p>
	{/if}
</div>

<style>
	.inset {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		column-gap: 20px;
		margin: 0;
	}
	.cap {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		margin-bottom: 8px;
		white-space: nowrap;
	}
	canvas {
		display: block;
		width: 48px;
		height: 144px;
		image-rendering: pixelated;
		border-radius: 2px;
	}
	.prompt {
		display: block;
		margin-top: 8px;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.tokens {
		display: flex;
		gap: 10px;
		font-family: var(--font-mono);
		font-size: 22px;
		line-height: 1.2;
		color: var(--color-ink);
	}
	.means {
		margin-top: 6px;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
		transition: color 250ms ease;
	}
	.means.idle {
		color: var(--color-ink-3);
	}
	.truth {
		grid-column: 1 / -1;
		margin-top: 10px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.meta {
		margin-top: 4px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
</style>
