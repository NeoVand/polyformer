<script lang="ts">
	/** A standalone SET card. */
	import { VALUE_NAMES, type Card } from '#lib/set/cards.ts';
	import CardFace from './CardFace.svelte';

	let {
		card,
		width = 72,
		selected = false,
		dim = false
	}: { card: Card; width?: number; selected?: boolean; dim?: boolean } = $props();

	const label = $derived(
		`${VALUE_NAMES[0][card[0]]} ${VALUE_NAMES[2][card[2]]} ${VALUE_NAMES[3][card[3]]} ${VALUE_NAMES[1][card[1]]}${card[0] ? 's' : ''}`
	);
</script>

<svg
	{width}
	height={(width * 2) / 3}
	viewBox="-2 -2 {width + 4} {(width * 2) / 3 + 4}"
	role="img"
	aria-label={label}
	class="set-card"
>
	<CardFace {card} {width} {selected} {dim} />
</svg>

<style>
	.set-card {
		display: block;
		overflow: visible;
	}
</style>
