<script lang="ts">
	/**
	 * A Feynman attention probe as a spacetime diagram, every token at once. Time runs left to
	 * right through the rounds; each token is a faint world line. Every state gets
	 * the Feynman vertex of what it mostly does (a dot for a hop, a triangle for a
	 * cubic vertex, a ring for an exchange, a square for its own value, nothing for a
	 * carry), and the reads between rounds are drawn as propagators. One root's
	 * backward cone, the states its readout depends on, is lit, with a current
	 * running along it toward the readout. Hover a row to see that token's cone;
	 * click it to choose it.
	 */
	import type { Snippet } from 'svelte';
	import { fade } from 'svelte/transition';
	import type { DiagramHead, DiagramSector } from '#lib/engine/protocol.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import { backwardCone, dominant, flowEdges, stateAt } from './diagramFlow.ts';
	import { photon } from './feynman.ts';

	let {
		head,
		n,
		rounds,
		rows,
		root,
		onroot,
		label,
		annotate,
		output = '\\hat y',
		note,
		pitch = 18,
		column = 92,
		fit = false,
		animate = true,
		description = 'Every token and round of a Feynman attention model; the lit lines are what one token reads'
	}: {
		head: DiagramHead;
		n: number;
		rounds: number;
		/** Token positions to draw, in groups (a small gap separates groups). */
		rows: number[][];
		/** Token whose final state is read out; its backward cone is lit. */
		root: number;
		onroot?: (t: number) => void;
		/** A row's label (a card, an id). */
		label: Snippet<[number]>;
		/** Small text beside a lit state, such as the payload it holds. */
		annotate?: (r: number, t: number) => string | null;
		/** TeX at the end of the readout leg. */
		output?: string;
		note?: string;
		/** Largest row pitch and column spacing, in pixels. */
		pitch?: number;
		column?: number;
		/** Fill the parent's height, shrinking the row pitch (never past `pitch`) to fit. */
		fit?: boolean;
		animate?: boolean;
		description?: string;
	} = $props();

	let width = $state(0);
	let boxHeight = $state(0);
	let hovered = $state<number | null>(null);
	const focus = $derived(hovered ?? root);

	const cone = $derived(backwardCone(head, n, rounds, focus, 0.08));
	const edges = $derived(flowEdges(head, n, rounds, cone, 0.08, 0.09));
	/** Lit lines scale with the share of the readout they carry, saturating at half. */
	const strength = (flow: number) => Math.min(1, flow / 0.5);

	// ── geometry: content-sized, so the view stays compact ───────────────────
	const TOP = 26;
	const LABEL = 46;

	const GAP = 0.55;
	const geo = $derived.by(() => {
		// fixed room right of the last round for the readout and its note, so a note
		// appearing never moves the drawing
		const OUT = 124;
		const span = rows.reduce((s, g) => s + g.length, 0) - 1 + (rows.length - 1) * GAP;
		const p =
			fit && boxHeight > 0
				? Math.max(8, Math.min(pitch, (boxHeight - TOP - 20) / Math.max(1, span)))
				: pitch;
		const y: number[] = Array.from({ length: n }, () => NaN);
		let u = 0;
		rows.forEach((g, gi) => {
			if (gi) u += GAP;
			for (const t of g) {
				y[t] = TOP + 8 + u * p;
				u += 1;
			}
		});
		const height = TOP + 8 + (u - 1) * p + 12;
		const col = Math.max(40, Math.min(column, (width - LABEL - OUT - 16) / rounds));
		// centre the drawing when the tile is wider than it needs
		const left = Math.max(0, (width - (LABEL + 12 + rounds * col + 30 + OUT)) / 2);
		const x = Array.from({ length: rounds + 1 }, (_, r) => left + LABEL + 12 + r * col);
		return { y, x, height, left, out: x[rounds] + 30 };
	});

	type Glyph = DiagramSector | 'value';
	/** The vertex each state draws: what it mostly does, and how sure it is. */
	const vertices = $derived.by(() => {
		const out: { r: number; t: number; kind: Glyph; mass: number; lit: boolean }[] = [];
		for (const g of rows)
			for (const t of g)
				for (let r = 0; r <= rounds; r++) {
					if (r === 0) {
						out.push({ r, t, kind: 'value', mass: 1, lit: cone[0].has(t) });
						continue;
					}
					const st = stateAt(head, n, r, t);
					if (!st) continue;
					const kind = dominant(st);
					out.push({ r, t, kind, mass: st.sectors[kind], lit: cone[r].has(t) });
				}
		return out;
	});

	const pathOf = (e: (typeof edges)[number]) => {
		const { x, y } = geo;
		const x0 = x[e.r - 1] + 3;
		const x1 = x[e.r] - 3;
		const y0 = y[e.from];
		const y1 = y[e.to];
		if (e.kind === 'exchange') return photon(x0, y0, x1, y1, 1.6, 6);
		// a cubic read joins its partner at a trivalent vertex just before the state
		if (e.kind === 'cubic') {
			const jx = x1 - Math.min(14, (x1 - x0) * 0.22);
			return `M${x0.toFixed(1)},${y0.toFixed(1)} L${jx.toFixed(1)},${y1.toFixed(1)} L${x1.toFixed(1)},${y1.toFixed(1)}`;
		}
		return `M${x0.toFixed(1)},${y0.toFixed(1)} L${x1.toFixed(1)},${y1.toFixed(1)}`;
	};
	const visible = (e: (typeof edges)[number]) =>
		!Number.isNaN(geo.y[e.from]) && !Number.isNaN(geo.y[e.to]);
</script>

<div
	class="flow"
	class:animate
	role="img"
	aria-label={description}
	bind:clientWidth={width}
	bind:clientHeight={boxHeight}
	class:fit
	style:height={fit ? undefined : `${geo.height}px`}
>
	{#if width > 0}
		<svg {width} height={geo.height} aria-hidden="true">
			<!-- round columns and world lines -->
			{#each geo.x as cx, r (r)}
				<line x1={cx} x2={cx} y1={TOP - 2} y2={geo.height - 6} class="guide" />
			{/each}
			{#each rows.flat() as t (t)}
				<line
					x1={geo.x[0]}
					x2={geo.x[rounds]}
					y1={geo.y[t]}
					y2={geo.y[t]}
					class="world"
					class:on={t === focus}
				/>
			{/each}

			<!-- reads: faint everywhere, lit inside the cone -->
			{#each edges as e, i (i)}
				{#if visible(e)}
					<path
						d={pathOf(e)}
						class="edge {e.kind}"
						class:lit={e.lit}
						style:--w={e.w}
						style:--f={strength(e.flow)}
						stroke-dasharray={e.kind === 'carry' ? '2 3' : undefined}
					/>
				{/if}
			{/each}
			{#if animate}
				<g class="currents">
					{#each edges as e, i (i)}
						{#if e.lit && e.flow >= 0.18 && visible(e) && e.kind !== 'carry' && e.kind !== 'leaf'}
							<path d={pathOf(e)} class="current" transition:fade={{ duration: 800 }} />
						{/if}
					{/each}
				</g>
			{/if}

			<!-- the readout leg -->
			{#if !Number.isNaN(geo.y[focus])}
				<!-- glides to the focused row instead of jumping -->
				<g class="readout" style:transform="translateY({geo.y[focus]}px)">
					<line x1={geo.x[rounds] + 6} x2={geo.out - 4} y1="0" y2="0" class="leg" />
					<circle cx={geo.x[rounds]} cy="0" r="5.5" class="root-ring" />
				</g>
			{/if}

			<!-- states -->
			{#each vertices as v (`${v.r}-${v.t}`)}
				{@const cx = geo.x[v.r]}
				{@const cy = geo.y[v.t]}
				<g class="v {v.kind}" class:lit={v.lit} style:--m={v.mass}>
					{#if v.kind === 'value' || v.kind === 'leaf'}
						<rect x={cx - 1.9} y={cy - 1.9} width="3.8" height="3.8" />
					{:else if v.kind === 'hop'}
						<circle {cx} {cy} r="2.1" />
					{:else if v.kind === 'cubic'}
						<path d="M{cx},{cy - 3} L{cx + 2.7},{cy + 1.8} L{cx - 2.7},{cy + 1.8} Z" />
					{:else if v.kind === 'exchange'}
						<circle {cx} {cy} r="2.3" class="ring" />
					{:else}
						<circle {cx} {cy} r="1.1" />
					{/if}
				</g>
				{#if v.lit && annotate}
					{@const a = annotate(v.r, v.t)}
					{#if a}<text x={cx + 4} y={cy - 4} class="ann">{a}</text>{/if}
				{/if}
			{/each}
		</svg>

		<!-- column heads, row labels and the readout, in HTML for KaTeX and cards -->
		{#each geo.x as cx, r (r)}
			<span class="col" style:left="{cx}px"><MathTex tex={r === 0 ? 'v' : `\\Phi^{${r}}`} /></span>
		{/each}
		{#each rows.flat() as t (t)}
			<button
				class="row"
				class:on={t === focus}
				style:top="{geo.y[t]}px"
				style:left="{geo.left}px"
				style:width="{geo.x[rounds] - geo.left + 8}px"
				aria-label="Show what token {t} reads"
				onpointerenter={() => (hovered = t)}
				onpointerleave={() => (hovered = null)}
				onfocus={() => (hovered = t)}
				onblur={() => (hovered = null)}
				onclick={() => onroot?.(t)}
			>
				<span class="lab">{@render label(t)}</span>
			</button>
		{/each}
		{#if !Number.isNaN(geo.y[focus])}
			<span class="out" style:left="{geo.out}px" style:top="{geo.y[focus]}px">
				<MathTex tex={output} />
				{#if note && focus === root}<small class="num">{note}</small>{/if}
			</span>
		{/if}
	{/if}
</div>

<style>
	.flow {
		position: relative;
		width: 100%;
		min-width: 0;
	}
	.flow.fit {
		height: 100%;
		min-height: 120px;
	}
	svg {
		position: absolute;
		inset: 0;
		display: block;
		overflow: visible;
	}
	.guide {
		stroke: rgb(255 255 255 / 0.05);
	}
	.world {
		stroke: rgb(255 255 255 / 0.06);
	}
	.world {
		transition: stroke 1100ms cubic-bezier(0.37, 0, 0.63, 1);
	}
	.world.on {
		stroke: rgb(255 255 255 / 0.16);
	}
	.edge {
		fill: none;
		stroke: #8a8a8a;
		stroke-width: 0.8;
		stroke-linecap: round;
		opacity: calc(0.12 + 0.4 * var(--w));
		/* a new focus fades in rather than switching: weight, tone and width all ease */
		transition:
			opacity 1100ms cubic-bezier(0.37, 0, 0.63, 1),
			stroke 1100ms cubic-bezier(0.37, 0, 0.63, 1),
			stroke-width 1100ms cubic-bezier(0.37, 0, 0.63, 1);
	}
	.edge.lit {
		stroke: #f2f2f2;
		stroke-width: calc(0.7 + 1.4 * var(--f));
		opacity: calc(0.28 + 0.72 * var(--f));
	}
	.current {
		fill: none;
		stroke: #fff;
		stroke-width: 1.6;
		stroke-linecap: round;
		stroke-dasharray: 1 11;
		animation: run 1.2s linear infinite;
	}
	.currents {
		filter: drop-shadow(0 0 2px rgb(255 255 255 / 0.9));
	}
	@keyframes run {
		from {
			stroke-dashoffset: 12;
		}
		to {
			stroke-dashoffset: 0;
		}
	}
	.readout {
		transition: transform 1100ms cubic-bezier(0.37, 0, 0.63, 1);
	}
	.leg {
		stroke: #f2f2f2;
		stroke-width: 1.6;
	}
	.root-ring {
		fill: none;
		stroke: #f2f2f2;
		stroke-width: 1;
		opacity: 0.7;
	}
	.v {
		transition:
			fill 1100ms cubic-bezier(0.37, 0, 0.63, 1),
			opacity 1100ms cubic-bezier(0.37, 0, 0.63, 1);
		fill: #5c5c5c;
		opacity: calc(0.45 + 0.55 * var(--m));
	}
	.v.lit {
		fill: #f5f5f5;
		opacity: 1;
	}
	.v .ring {
		fill: none;
		stroke: #5c5c5c;
		stroke-width: 1.1;
	}
	.v.lit .ring {
		stroke: #f5f5f5;
	}
	.ann {
		font-size: 9px;
		fill: var(--color-ink-2);
		font-variant-numeric: tabular-nums;
	}
	.col {
		position: absolute;
		top: 2px;
		transform: translateX(-50%);
		font-size: 12px;
		color: var(--color-ink-3);
		pointer-events: none;
	}
	.row {
		position: absolute;
		height: 16px;
		display: flex;
		align-items: center;
		padding: 0;
		border: 0;
		border-radius: 3px;
		background: transparent;
		transition: background 300ms ease;
		transform: translateY(-50%);
		cursor: pointer;
	}
	.row:hover,
	.row.on {
		background: rgb(255 255 255 / 0.035);
	}
	.row:focus {
		outline: none;
	}
	.row:focus-visible {
		box-shadow: inset 0 0 0 1px rgb(255 255 255 / 0.4);
	}
	.lab {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 3px;
		width: 44px;
		padding-right: 4px;
		font-size: 10.5px;
		line-height: 1;
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.row.on .lab {
		color: var(--color-ink);
	}
	.out {
		position: absolute;
		display: flex;
		align-items: baseline;
		gap: 6px;
		transform: translateY(-50%);
		transition: top 1100ms cubic-bezier(0.37, 0, 0.63, 1);
		font-size: 13px;
		white-space: nowrap;
		pointer-events: none;
	}
	.out small {
		font-size: 10px;
		color: var(--color-ink-3);
	}
	@media (prefers-reduced-motion: reduce) {
		.current {
			animation: none;
		}
	}
</style>
