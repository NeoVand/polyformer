<script lang="ts">
	/**
	 * One token's Feynman attention computation tree drawn as a textbook Feynman diagram:
	 * straight propagators with mid-line arrows, dot vertices, photon lines to
	 * hatched mode blobs, dashed carries. Rounds run left to right from the
	 * tokens' values to the probed state. A path's flow (the product of its
	 * option weights) sets its weight and brightness.
	 */
	import type { Snippet } from 'svelte';
	import type { DiagramHead } from '#lib/engine/protocol.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import { layoutDiagram, type ExpandOptions, type Term } from './feynman.ts';

	let {
		head,
		n,
		rounds,
		modes,
		root,
		options = {},
		reveal = Infinity,
		highlight = [],
		row,
		output = '\\hat y',
		onterm
	}: {
		head: DiagramHead;
		n: number;
		rounds: number;
		modes: number;
		/** Sequence position whose state is expanded. */
		root: number;
		options?: ExpandOptions;
		/** Draw rounds up to this one at full strength; later rounds stay ghosted. */
		reveal?: number;
		/** Tokens whose labels stay bright (e.g. the true pointer path). */
		highlight?: number[];
		/** Label for a token's external leg, drawn left of round 0. */
		row?: Snippet<[number]>;
		/** TeX label at the end of the output leg. */
		output?: string;
		onterm?: (term: Term | null) => void;
	} = $props();

	let width = $state(900);
	let height = $state(520);
	const L = $derived(
		layoutDiagram(
			head,
			n,
			rounds,
			modes,
			root,
			{ width, height, padLeft: 96, padRight: 150, padTop: 36, padBottom: 12 },
			options
		)
	);
	let hovered = $state<number | null>(null);
	const lit = (round: number) => round <= reveal;
	const strokeW = (flow: number) => 1 + 1.3 * Math.sqrt(flow);
	const alpha = (flow: number, round: number, term: number) => {
		const base = 0.28 + 0.72 * Math.sqrt(flow);
		if (!lit(round)) return base * 0.08;
		if (hovered !== null && term !== hovered && term !== -1) return base * 0.25;
		return base;
	};
	const hi = $derived(new Set(highlight));

	/** A small arrowhead at the middle of a segment, pointing along it. */
	function arrow(from: [number, number], to: [number, number], size: number): string | null {
		const dx = to[0] - from[0];
		const dy = to[1] - from[1];
		const len = Math.hypot(dx, dy);
		if (len < 26) return null;
		const ux = dx / len;
		const uy = dy / len;
		const mx = from[0] + dx * 0.5 + ux * size * 0.5;
		const my = from[1] + dy * 0.5 + uy * size * 0.5;
		const bx = mx - ux * size;
		const by = my - uy * size;
		const w = size * 0.42;
		return `M${mx.toFixed(1)},${my.toFixed(1)} L${(bx - uy * w).toFixed(1)},${(by + ux * w).toFixed(1)} L${(bx + uy * w).toFixed(1)},${(by - ux * w).toFixed(1)} Z`;
	}

	function enter(term: number) {
		hovered = term;
		onterm?.(term >= 0 ? L.terms[term] : null);
	}
	function leave() {
		hovered = null;
		onterm?.(null);
	}
</script>

<div class="feyn" bind:clientWidth={width} bind:clientHeight={height}>
	<svg
		{width}
		{height}
		viewBox="0 0 {width} {height}"
		role="img"
		aria-label="Computation tree of one token as a Feynman diagram"
	>
		<defs>
			<pattern
				id="fy-hatch"
				width="3"
				height="3"
				patternUnits="userSpaceOnUse"
				patternTransform="rotate(45)"
			>
				<line x1="0" y1="0" x2="0" y2="3" stroke="#f2f2f2" stroke-width="0.9" />
			</pattern>
		</defs>

		{#each L.edges as e (e.id)}
			{@const op = alpha(e.flow, e.round, e.term)}
			<path d={e.d} class="edge {e.style}" stroke-width={strokeW(e.flow)} stroke-opacity={op} />
			{#if e.style === 'line'}
				{@const tip = arrow(e.from, e.to, 5 + 2 * Math.sqrt(e.flow))}
				{#if tip}<path d={tip} class="tip" fill-opacity={op} />{/if}
			{/if}
			{#if e.term >= 0}
				<path
					d={e.d}
					class="hit"
					role="presentation"
					onpointerenter={() => enter(e.term)}
					onpointerleave={leave}
				/>
			{/if}
		{/each}

		{#each L.nodes as s (s.key)}
			{#if s.round > 0 && s.key !== L.root.key}
				<circle
					class="dot"
					cx={s.x}
					cy={s.y}
					r={1.8 + 1.4 * Math.sqrt(s.flow)}
					opacity={lit(s.round) ? 0.5 + 0.5 * Math.sqrt(s.flow) : 0.08}
				/>
			{/if}
		{/each}

		{#each L.vertices as v (v.id)}
			{@const on = lit(v.round)}
			{#if v.kind === 'mode'}
				<circle
					class="blob"
					cx={v.x}
					cy={v.y}
					r={6.5 + 2 * Math.sqrt(v.flow)}
					opacity={on ? 1 : 0.1}
				/>
			{:else}
				<circle
					class="dot"
					cx={v.x}
					cy={v.y}
					r={2.6 + 1.6 * Math.sqrt(v.flow)}
					opacity={on ? 1 : 0.1}
				/>
			{/if}
		{/each}

		<circle class="dot" cx={L.root.x} cy={L.root.y} r="4" />
	</svg>

	{#each L.columns as c (c.round)}
		<span class="col-head" class:dim={!lit(c.round)} style:left="{c.x}px">
			<MathTex tex={c.round === 0 ? 'v' : `\\Phi^{${c.round}}`} />
		</span>
	{/each}
	{#each L.vertices as v (v.id)}
		{#if v.kind === 'mode' && lit(v.round)}
			<span class="blob-label" style:left="{v.x}px" style:top="{v.y + 14}px"
				><MathTex tex={`\\Psi_{${v.m}}`} /></span
			>
		{/if}
	{/each}
	<span class="out" style:left="{L.root.x + 72}px" style:top="{L.root.y}px"
		><MathTex tex={output} /></span
	>
	{#if row}
		{#each L.rows as r (r.token)}
			<span
				class="row-label"
				class:hi={hi.has(r.token)}
				style:top="{r.y}px"
				style:width="{L.columns[0].x - 12}px"
			>
				{@render row(r.token)}
			</span>
		{/each}
	{/if}
</div>

<style>
	.feyn {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 280px;
	}
	svg {
		position: absolute;
		inset: 0;
		display: block;
		overflow: visible;
	}
	.edge {
		fill: none;
		stroke: #f2f2f2;
		stroke-linecap: round;
		stroke-linejoin: round;
		transition: stroke-opacity 360ms ease;
	}
	.edge.dashed {
		stroke-dasharray: 3.5 4;
	}
	.tip {
		fill: #f2f2f2;
		transition: fill-opacity 360ms ease;
	}
	.hit {
		fill: none;
		stroke: transparent;
		stroke-width: 12;
		pointer-events: stroke;
		cursor: crosshair;
	}
	.dot {
		fill: #f2f2f2;
		transition: opacity 360ms ease;
	}
	.blob {
		fill: url(#fy-hatch);
		stroke: #f2f2f2;
		stroke-width: 1.2;
		transition: opacity 360ms ease;
	}
	.col-head,
	.blob-label,
	.out {
		position: absolute;
		pointer-events: none;
		white-space: nowrap;
	}
	.col-head {
		top: 0;
		transform: translateX(-50%);
		font-size: 15px;
		transition: opacity 360ms ease;
	}
	.col-head :global(.katex) {
		color: var(--color-ink-3);
	}
	.col-head.dim {
		opacity: 0.35;
	}
	.blob-label {
		transform: translateX(-50%);
		font-size: 13px;
	}
	.out {
		transform: translateY(-50%);
		font-size: 17px;
	}
	.row-label {
		position: absolute;
		left: 0;
		transform: translateY(-50%);
		display: flex;
		justify-content: flex-end;
		align-items: center;
		pointer-events: none;
		opacity: 0.5;
	}
	.row-label.hi {
		opacity: 1;
	}
</style>
