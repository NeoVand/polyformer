<script lang="ts">
	/**
	 * One SET card as a square glyph inside a parent <svg>, top-left at (x, y): no
	 * face, no frame, just 1:1 symbols. One sits centred, two side by side, three
	 * in a triangle, so every card fits the same square. Colour is allowed here and
	 * only here.
	 */
	import type { Card } from '#lib/set/cards.ts';
	import { SET_COLOURS, SHAPE_SIZE, SHAPES } from './setShapes.ts';

	let {
		card,
		x = 0,
		y = 0,
		width = 40,
		selected = false,
		dim = false
	}: {
		card: Card;
		x?: number;
		y?: number;
		/** Side of the square. */
		width?: number;
		selected?: boolean;
		dim?: boolean;
	} = $props();

	const uid = $props.id();
	const count = $derived(card[0] + 1);
	const colour = $derived(SET_COLOURS[card[3]]);
	const path = $derived(SHAPES[card[1]]);
	/** Symbol size as a share of the square, and centres in units of the square. */
	const LAYOUT: Record<number, { h: number; at: [number, number][] }> = {
		1: { h: 0.6, at: [[0, 0]] },
		2: {
			h: 0.4,
			at: [
				[-0.25, 0],
				[0.25, 0]
			]
		},
		3: {
			h: 0.36,
			at: [
				[0, -0.215],
				[-0.225, 0.195],
				[0.225, 0.195]
			]
		}
	};
	const lay = $derived(LAYOUT[count]);
	const scale = $derived((lay.h * width) / SHAPE_SIZE);
	const fill = $derived(card[2] === 0 ? colour : card[2] === 1 ? `url(#stripe-${uid})` : 'none');
	/** Stripes 2.2 px apart on screen, whatever the size. */
	const pitch = $derived(2.2 / scale);
</script>

<g transform="translate({x} {y})" class={['card', selected && 'selected', dim && 'dim']}>
	<defs>
		<pattern id="stripe-{uid}" width={pitch * 4} height={pitch} patternUnits="userSpaceOnUse">
			<line x1="0" y1={pitch * 0.5} x2={pitch * 4} y2={pitch * 0.5} stroke={colour} stroke-width={0.8 / scale} />
		</pattern>
	</defs>
	{#if selected}
		<circle class="ring" cx={width / 2} cy={width / 2} r={width * 0.5} />
	{/if}
	{#each lay.at as [dx, dy], i (i)}
		<path
			d={path}
			transform="translate({width / 2 + dx * width} {width / 2 + dy * width}) scale({scale})"
			{fill}
			stroke={colour}
			stroke-width={1.3 / scale}
			stroke-linejoin="round"
		/>
	{/each}
</g>

<style>
	.ring {
		fill: none;
		stroke: rgb(245 245 245 / 0.8);
		stroke-width: 1;
	}
	.card.dim {
		opacity: 0.32;
	}
</style>
