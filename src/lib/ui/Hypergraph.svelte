<script lang="ts">
	/**
	 * The layout as a role-labelled hypergraph. Cards sit on a ring; each has a
	 * node on the inner ring. A hyperedge (i, j, k) is a membrane between three
	 * nodes whose opacity is the query's weight on that pair. Ports encode roles
	 * by shape: circle = query i, square = role 1 j, diamond = role 2 k.
	 */
	import type { Card } from '#lib/set/cards.ts';
	import type { Hyperedge } from '#lib/explore/analysis.ts';
	import CardFace from './CardFace.svelte';

	let {
		layout,
		query,
		edges,
		selected,
		truth,
		onquery,
		onedge
	}: {
		layout: Card[];
		query: number;
		edges: Hyperedge[];
		selected: { j: number; k: number } | null;
		/** Pairs that complete a true SET with the query. */
		truth: [number, number][];
		onquery?: (card: number) => void;
		onedge?: (e: { j: number; k: number }) => void;
	} = $props();

	const W = 640;
	const H = 460;
	const cx = W / 2;
	const cy = H / 2;
	const RX = 252;
	const RY = 170;
	const CARD = 64;
	const CARD_H = (CARD * 2) / 3;

	const angle = (t: number) => -Math.PI / 2 + (2 * Math.PI * t) / layout.length;
	const cardPos = (t: number) => ({
		x: cx + RX * Math.cos(angle(t)),
		y: cy + RY * Math.sin(angle(t))
	});
	// nodes alternate between two inner rings so neighbouring triples keep some area
	const node = (t: number) => {
		const r = t % 2 ? 0.46 : 0.7;
		return { x: cx + RX * r * Math.cos(angle(t)), y: cy + RY * r * Math.sin(angle(t)) };
	};
	const pts = (...ts: number[]) =>
		ts
			.map(node)
			.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`)
			.join(' ');

	const maxW = $derived(Math.max(1e-6, ...edges.map((e) => e.weight)));
	const isSelected = (e: { j: number; k: number }) =>
		!!selected &&
		((selected.j === e.j && selected.k === e.k) || (selected.j === e.k && selected.k === e.j));

	const sel = $derived(
		selected ? { i: node(query), j: node(selected.j), k: node(selected.k) } : null
	);
	const diamond = (x: number, y: number, r: number) =>
		`${x},${y - r} ${x + r},${y} ${x},${y + r} ${x - r},${y}`;
	/** Nudge a label away from the ring centre. */
	const outward = (p: { x: number; y: number }, d: number) => {
		const dx = p.x - cx;
		const dy = p.y - cy;
		const len = Math.hypot(dx, dy) || 1;
		return { x: p.x - (dx / len) * d, y: p.y - (dy / len) * d };
	};
</script>

<svg
	viewBox="0 0 {W} {H}"
	class="hg"
	role="group"
	aria-label="Layout hypergraph for the selected query card"
>
	<defs>
		<filter id="hg-glow" x="-30%" y="-30%" width="160%" height="160%">
			<feGaussianBlur stdDeviation="3.2" result="b" />
			<feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
		</filter>
	</defs>

	<!-- spokes from cards to their nodes -->
	{#each layout.keys() as t (t)}
		{@const c = cardPos(t)}
		{@const p = node(t)}
		<line x1={c.x} y1={c.y} x2={p.x} y2={p.y} class="spoke" />
	{/each}

	<!-- true SETs with the query, as dashed outlines -->
	{#each truth as [a, b] (`${a}-${b}`)}
		<polygon points={pts(query, a, b)} class="truth" />
	{/each}

	<!-- model hyperedges, weakest first -->
	{#each [...edges].reverse() as e (`${e.j}-${e.k}`)}
		{@const on = isSelected(e)}
		<polygon
			points={pts(query, e.j, e.k)}
			class={['membrane', on && 'on']}
			style:fill-opacity={on ? 0.26 : 0.04 + 0.2 * (e.weight / maxW)}
			style:stroke-opacity={on ? 1 : 0.25 + 0.55 * (e.weight / maxW)}
			role="button"
			tabindex="0"
			aria-label="Pair {e.j + 1} and {e.k + 1}, weight {(e.weight * 100).toFixed(1)}%"
			onclick={() => onedge?.({ j: e.j, k: e.k })}
			onkeydown={(ev) => (ev.key === 'Enter' || ev.key === ' ') && onedge?.({ j: e.j, k: e.k })}
		/>
	{/each}

	{#if sel}
		<polygon
			points="{sel.i.x},{sel.i.y} {sel.j.x},{sel.j.y} {sel.k.x},{sel.k.y}"
			class="glow"
			filter="url(#hg-glow)"
		/>
	{/if}

	<!-- nodes -->
	{#each layout.keys() as t (t)}
		{@const p = node(t)}
		<circle cx={p.x} cy={p.y} r="3.2" class={['dot', t === query && 'q']} />
	{/each}

	<!-- role ports on the selected hyperedge -->
	{#if sel}
		{@const li = outward(sel.i, 16)}
		{@const lj = outward(sel.j, 16)}
		{@const lk = outward(sel.k, 16)}
		<circle cx={sel.i.x} cy={sel.i.y} r="6.5" class="port" />
		<rect x={sel.j.x - 5.5} y={sel.j.y - 5.5} width="11" height="11" class="port" />
		<polygon points={diamond(sel.k.x, sel.k.y, 7)} class="port" />
		<text x={li.x} y={li.y} class="role">i</text>
		<text x={lj.x} y={lj.y} class="role">j</text>
		<text x={lk.x} y={lk.y} class="role">k</text>
	{/if}

	<!-- cards -->
	{#each layout as card, t (t)}
		{@const c = cardPos(t)}
		<g
			class="slot"
			role="button"
			tabindex="0"
			aria-label="Query card {t + 1}"
			aria-pressed={t === query}
			onclick={() => onquery?.(t)}
			onkeydown={(ev) => (ev.key === 'Enter' || ev.key === ' ') && onquery?.(t)}
		>
			<CardFace
				{card}
				x={c.x - CARD / 2}
				y={c.y - CARD_H / 2}
				width={CARD}
				selected={t === query}
			/>
			<text x={c.x} y={c.y + CARD_H / 2 + 12} class="idx">{t + 1}</text>
		</g>
	{/each}
</svg>

<style>
	.hg {
		display: block;
		width: 100%;
		height: 100%;
		overflow: visible;
	}
	.spoke {
		stroke: #2a2a2a;
		stroke-width: 1;
	}
	.truth {
		fill: none;
		stroke: var(--color-ink-2);
		stroke-width: 1;
		stroke-dasharray: 3 4;
	}
	.membrane {
		fill: #f5f5f5;
		stroke: #d0d0d0;
		stroke-width: 1;
		stroke-linejoin: round;
		cursor: pointer;
		transition: fill-opacity 160ms ease;
	}
	.membrane:hover {
		fill-opacity: 0.32;
	}
	.membrane:focus-visible {
		outline: none;
		stroke: #fff;
		stroke-width: 2;
	}
	.membrane.on {
		stroke: #fff;
		stroke-width: 1.5;
	}
	.glow {
		fill: none;
		stroke: rgb(255 255 255 / 0.65);
		stroke-width: 2;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.dot {
		fill: #3a3a3a;
		stroke: #6a6a6a;
		stroke-width: 1;
	}
	.dot.q {
		fill: #f5f5f5;
		stroke: #f5f5f5;
	}
	.port {
		fill: var(--color-void);
		stroke: var(--color-ink);
		stroke-width: 1.5;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.role {
		fill: var(--color-ink);
		font-family: KaTeX_Math, 'Times New Roman', serif;
		font-style: italic;
		font-size: 15px;
		text-anchor: middle;
		dominant-baseline: middle;
		pointer-events: none;
	}
	.slot {
		cursor: pointer;
		outline: none;
	}
	.slot:focus-visible :global(.face) {
		stroke: var(--color-ink);
	}
	.idx {
		fill: var(--color-ink-3);
		font-size: 10px;
		text-anchor: middle;
	}
</style>
