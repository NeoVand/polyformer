<script lang="ts">
	/** One Feynman rule as a small diagram, drawn with the same primitives as the full diagrams. */
	import type { DiagramSector } from '#lib/engine/protocol.ts';
	import { line, photon } from './feynman.ts';

	let { kind, width = 72, height = 30 }: { kind: DiagramSector; width?: number; height?: number } = $props();

	const m = $derived(height / 2);
	const w = $derived(width);

	/** Arrowhead at the middle of a segment. */
	function tip(x1: number, y1: number, x2: number, y2: number, size = 5.5) {
		const len = Math.hypot(x2 - x1, y2 - y1);
		const ux = (x2 - x1) / len;
		const uy = (y2 - y1) / len;
		const mx = (x1 + x2) / 2 + ux * size * 0.5;
		const my = (y1 + y2) / 2 + uy * size * 0.5;
		const bx = mx - ux * size;
		const by = my - uy * size;
		const s = size * 0.42;
		return `M${mx},${my} L${bx - uy * s},${by + ux * s} L${bx + uy * s},${by - ux * s} Z`;
	}
</script>

<svg {width} {height} viewBox="0 0 {width} {height}" aria-hidden="true">
	<defs>
		<pattern id="rule-hatch" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
			<line x1="0" y1="0" x2="0" y2="3" stroke="#f2f2f2" stroke-width="0.9" />
		</pattern>
	</defs>
	{#if kind === 'leaf'}
		<path d={line(2, m, w - 6, m)} class="l" />
		<path d={tip(2, m, w - 6, m)} class="t" />
		<circle cx={w - 5} cy={m} r="2.6" class="d" />
	{:else if kind === 'hop'}
		<circle cx="5" cy={m} r="2" class="d" />
		<path d={line(5, m, w - 6, m)} class="l" />
		<path d={tip(5, m, w - 6, m)} class="t" />
		<circle cx={w - 5} cy={m} r="2.6" class="d" />
	{:else if kind === 'cubic'}
		{@const vx = w * 0.55}
		<path d={line(4, 4, vx, m)} class="l" />
		<path d={line(4, height - 4, vx, m)} class="l" />
		<path d={line(vx, m, w - 5, m)} class="l" />
		<path d={tip(vx, m, w - 5, m, 5)} class="t" />
		<circle cx={vx} cy={m} r="3" class="d" />
	{:else if kind === 'exchange'}
		{@const vx = w * 0.62}
		<path d={line(4, 5, vx, 5)} class="l" />
		<path d={line(vx, 5, w - 5, 5)} class="l" />
		<path d={photon(vx * 0.4, height - 6, vx, 5, 2.2, 7)} class="l" />
		<circle cx={vx} cy="5" r="2.8" class="d" />
		<circle cx={vx * 0.4} cy={height - 6} r="5" class="b" />
	{:else}
		<path d={line(4, m, w - 5, m)} class="l dash" />
		<circle cx={w - 5} cy={m} r="2.6" class="d" />
	{/if}
</svg>

<style>
	svg {
		display: block;
		overflow: visible;
	}
	.l {
		fill: none;
		stroke: #f2f2f2;
		stroke-width: 1.4;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.dash {
		stroke-dasharray: 3.5 4;
	}
	.t,
	.d {
		fill: #f2f2f2;
	}
	.b {
		fill: url(#rule-hatch);
		stroke: #f2f2f2;
		stroke-width: 1.1;
	}
</style>
