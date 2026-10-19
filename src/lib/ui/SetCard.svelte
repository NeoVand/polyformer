<script lang="ts">
	/** A standalone SET card glyph: a square of symbols, no face. */
	import { VALUE_NAMES, type Card } from '#lib/set/cards.ts';
	import CardFace from './CardFace.svelte';

	let {
		card,
		width = 40,
		selected = false,
		dim = false
	}: { card: Card; width?: number; selected?: boolean; dim?: boolean } = $props();

	const label = $derived(
		`${VALUE_NAMES[0][card[0]]} ${VALUE_NAMES[2][card[2]]} ${VALUE_NAMES[3][card[3]]} ${VALUE_NAMES[1][card[1]]}${card[0] ? 's' : ''}`
	);
</script>

<svg {width} height={width} viewBox="0 0 {width} {width}" role="img" aria-label={label} class="set-card">
	<CardFace {card} {width} {selected} {dim} />
</svg>

<style>
	.set-card {
		display: block;
		overflow: visible;
	}
</style>
