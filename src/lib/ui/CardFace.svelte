<script lang="ts">
	/**
	 * One SET card drawn inside a parent <svg>, top-left at (x, y).
	 * Landscape face, upright symbols side by side. Colour is allowed here and only here.
	 */
	import type { Card } from '#lib/set/cards.ts';
	import { SET_COLOURS, SHAPES } from './setShapes.ts';

	let {
		card,
		x = 0,
		y = 0,
		width = 120,
		selected = false,
		dim = false
	}: {
		card: Card;
		x?: number;
		y?: number;
		width?: number;
		selected?: boolean;
		dim?: boolean;
	} = $props();

	const uid = $props.id();
	const height = $derived(width * (2 / 3));
	const scale = $derived((height * 0.62) / 56);
	const count = $derived(card[0] + 1);
	const colour = $derived(SET_COLOURS[card[3]]);
	const path = $derived(SHAPES[card[1]]);
	const gap = $derived(30 * scale);
	const offsets = $derived(Array.from({ length: count }, (_, i) => (i - (count - 1) / 2) * gap));
	const fill = $derived(card[2] === 0 ? colour : card[2] === 1 ? `url(#stripe-${uid})` : 'none');
</script>

<g transform="translate({x} {y})" class={['card', selected && 'selected', dim && 'dim']}>
	<defs>
		<pattern id="stripe-{uid}" width="4" height="3.2" patternUnits="userSpaceOnUse">
			<line x1="0" y1="0.8" x2="4" y2="0.8" stroke={colour} stroke-width="1" />
		</pattern>
	</defs>
	<rect class="face" x="0.5" y="0.5" width={width - 1} height={height - 1} rx="4" />
	{#each offsets as dx, i (i)}
		<path
			d={path}
			transform="translate({width / 2 + dx} {height / 2}) scale({scale})"
			{fill}
			stroke={colour}
			stroke-width={1.6 / scale}
			stroke-linejoin="round"
		/>
	{/each}
</g>

<style>
	.face {
		fill: #121212;
		stroke: var(--color-edge);
		stroke-width: 1;
		transition: stroke 120ms ease;
	}
	.card.selected .face {
		stroke: var(--color-ink);
		stroke-width: 1.5;
		filter: drop-shadow(0 0 6px rgb(255 255 255 / 0.35));
	}
	.card.dim {
		opacity: 0.38;
	}
</style>
