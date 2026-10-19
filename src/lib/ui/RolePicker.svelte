<script lang="ts">
	/**
	 * The three roles of a hyperedge as card tiles. Choosing a tile opens the whole
	 * table as a grid of cards, so you pick by sight rather than by number. Cards that
	 * would complete a SET with the other two roles carry a small dot.
	 */
	import { isSet, type Card } from '#lib/set/cards.ts';
	import SetCard from './SetCard.svelte';

	type Role = 'query' | 'j' | 'k';
	let {
		layout,
		query,
		j,
		k,
		onchange
	}: {
		layout: readonly Card[];
		query: number;
		j: number;
		k: number;
		onchange: (next: { query: number; j: number; k: number }) => void;
	} = $props();

	let open = $state<Role | null>(null);
	const ROLES: { id: Role; name: string; sym: string }[] = [
		{ id: 'query', name: 'Query', sym: 'i' },
		{ id: 'j', name: 'Role 1', sym: 'j' },
		{ id: 'k', name: 'Role 2', sym: 'k' }
	];
	const current = (r: Role) => (r === 'query' ? query : r === 'j' ? j : k);
	/** The other two roles' cards, for disabling repeats and marking SET completions. */
	const others = (r: Role) => (r === 'query' ? [j, k] : r === 'j' ? [query, k] : [query, j]);

	function choose(r: Role, t: number) {
		const next = { query, j, k, [r]: t };
		onchange(next);
		open = null;
	}

	function outside(el: HTMLElement) {
		const close = (e: PointerEvent) => {
			if (!el.contains(e.target as Node)) open = null;
		};
		const esc = (e: KeyboardEvent) => {
			if (e.key === 'Escape') open = null;
		};
		document.addEventListener('pointerdown', close);
		document.addEventListener('keydown', esc);
		return () => {
			document.removeEventListener('pointerdown', close);
			document.removeEventListener('keydown', esc);
		};
	}
</script>

<div class="picker" {@attach outside}>
	<div class="tiles">
		{#each ROLES as r (r.id)}
			<button
				class="tile"
				class:open={open === r.id}
				aria-expanded={open === r.id}
				aria-label="{r.name} {r.sym}: card {current(r.id) + 1}. Choose another card"
				onclick={() => (open = open === r.id ? null : r.id)}
			>
				<span class="t-label">{r.name} <i>{r.sym}</i></span>
				<SetCard card={layout[current(r.id)]} width={38} />
				<span class="t-no num">Card {current(r.id) + 1}</span>
			</button>
		{/each}
	</div>
	{#if open}
		{@const r = open}
		{@const [a, b] = others(r)}
		<div class="panel" role="listbox" aria-label="Choose the {ROLES.find((x) => x.id === r)?.name} card">
			{#each layout as card, t (t)}
				{@const taken = t === a || t === b}
				<button
					class="cell"
					class:on={t === current(r)}
					role="option"
					aria-selected={t === current(r)}
					disabled={taken}
					onclick={() => choose(r, t)}
				>
					<SetCard {card} width={30} dim={taken} />
					<span class="c-no num">{t + 1}</span>
					{#if !taken && isSet(card, layout[a], layout[b])}<span class="dot" title="Completes a SET"></span>{/if}
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	.picker {
		position: relative;
	}
	.tiles {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 8px;
	}
	.tile {
		display: grid;
		justify-items: center;
		gap: 6px;
		padding: 10px 4px 8px;
		border: 0;
		border-radius: 10px;
		background: #141414;
		color: var(--color-ink-3);
		cursor: pointer;
		transition: background 140ms ease;
	}
	.tile:hover,
	.tile.open {
		background: #1c1c1c;
	}
	.tile:focus {
		outline: none;
	}
	.tile:focus-visible {
		box-shadow: inset 0 0 0 1px var(--color-ink-2);
	}
	.t-label {
		font-size: var(--text-2xs);
	}
	.t-label i {
		font-family: var(--font-math);
		font-size: 1.2em;
		color: var(--color-ink);
	}
	.t-no {
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.panel {
		position: absolute;
		left: 0;
		right: 0;
		top: calc(100% + 6px);
		z-index: 20;
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 4px;
		padding: 8px;
		border-radius: 12px;
		background: #161616;
		box-shadow: 0 18px 40px rgb(0 0 0 / 0.6);
		animation: open 140ms ease both;
	}
	@keyframes open {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
	}
	.cell {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 3px;
		padding: 8px 0 5px;
		border: 0;
		border-radius: 8px;
		background: transparent;
		cursor: pointer;
	}
	.cell:hover:not(:disabled) {
		background: #222;
	}
	.cell.on {
		background: #262626;
	}
	.cell:disabled {
		cursor: default;
	}
	.cell:focus {
		outline: none;
	}
	.cell:focus-visible {
		box-shadow: inset 0 0 0 1px var(--color-ink-2);
	}
	.c-no {
		font-size: 10px;
		color: var(--color-ink-3);
	}
	.cell.on .c-no {
		color: var(--color-ink);
	}
	.dot {
		position: absolute;
		top: 6px;
		right: 8px;
		width: 5px;
		height: 5px;
		border-radius: 50%;
		background: var(--color-ink);
	}
</style>
