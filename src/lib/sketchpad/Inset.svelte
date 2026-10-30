<script lang="ts">
	import { onMount } from 'svelte';
	import { MODELS, kindOf } from './models.ts';
	import { explain, type TickView } from './pad.svelte.ts';
	import type { TickOp } from './protocol.ts';
	import { B, CELL, GLYPHS } from './sprites.ts';
	import { SHEET, theme } from './theme.svelte.ts';

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

	// the word the model actually reads before the image, from the loaded program's prompts
	const showOp = (op: TickOp) => MODELS[kindOf(op)].prompts[op] ?? op;

	const rgb = (hex: string) => {
		const n = parseInt(hex.slice(1), 16);
		return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
	};

	/**
	 * The strip: the pixels the worker fed the model, or the next view assembled from the same sprites. Those pixels are
	 * black ink on white; on a dark page they are shown in the sheet's own colours (each pixel's ink, 255 - grey, laid
	 * on the sheet's paper), the same transform the sheet uses, so the strip reads as a piece of the sheet.
	 */
	function paint(canvas: HTMLCanvasElement) {
		const ctx = canvas.getContext('2d', { willReadFrequently: true });
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
		if (theme.current !== 'dark') return;
		const pal = SHEET.dark;
		const [pr, pg, pb] = rgb(pal.paper);
		const [ir, ig, ib] = rgb(pal.ink);
		const d = ctx.getImageData(0, 0, CELL, 3 * CELL);
		for (let i = 0; i < d.data.length; i += 4) {
			const a = (255 - d.data[i]) / 255;
			d.data[i] = pr + (ir - pr) * a;
			d.data[i + 1] = pg + (ig - pg) * a;
			d.data[i + 2] = pb + (ib - pb) * a;
		}
		ctx.putImageData(d, 0, 0);
	}

	const tokens = $derived(last ? last.out.map((t) => (t === B ? '_' : t)) : []);
</script>

<figure class="sp-panel eye">
	<figcaption class="sp-cap">
		<span class="sp-title">One tick</span>
		<span class="sp-sub">what the model sees, and what it writes</span>
	</figcaption>
	<div class="sp-body">
		<div class="tick">
			<div class="sees">
				<!-- the frame is a real border around the strip, inside this panel, so nothing can clip it -->
				<div class="frame">
					<canvas {@attach paint} width={CELL} height={3 * CELL}></canvas>
				</div>
				<code class="prompt">
					{#if last || next}{showOp((last ?? next)!.op)} ▢ ={/if}
				</code>
			</div>
			<div class="writes">
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
		</div>
	</div>
	<p class="sp-foot">
		{#if theme.current === 'dark'}<span class="sp-dim"
				>Drawn inverted here; the model reads black on white.</span
			>{:else}<span class="sp-dim">The model's input pixels, as it reads them.</span>{/if}
	</p>
</figure>

<style>
	.tick {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		column-gap: 18px;
		align-content: start;
	}
	.frame {
		width: fit-content;
		border: 1px solid var(--color-rule);
		border-radius: 3px;
		overflow: hidden;
		line-height: 0;
	}
	canvas {
		display: block;
		width: 48px;
		height: 144px;
		image-rendering: pixelated;
	}
	.prompt {
		display: block;
		margin-top: 6px;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		line-height: 16px;
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.writes {
		min-width: 0;
	}
	.tokens {
		height: 28px;
		display: flex;
		gap: 10px;
		font-family: var(--font-mono);
		font-size: 22px;
		line-height: 28px;
		color: var(--color-ink);
	}
	.means {
		margin-top: 6px;
		height: 3.9em;
		overflow: hidden;
		font-size: var(--text-sm);
		line-height: 1.3;
		color: var(--color-ink-2);
		transition: color 250ms ease;
	}
	.means.idle {
		color: var(--color-ink-3);
	}
	.meta {
		margin-top: 4px;
		font-size: var(--text-2xs);
		line-height: 16px;
		color: var(--color-ink-3);
	}
	.sp-foot {
		font-size: var(--text-2xs);
	}
</style>
