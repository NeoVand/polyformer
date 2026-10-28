<script lang="ts">
	/**
	 * A two-state Mealy register as a machine: carry 0 and carry 1, the table's rows merged into four edges, each
	 * labelled with when it is taken and the digit it writes (when its rows follow the adder's rule, else its row
	 * count). The edge taken at the playhead is lit, with its digit pair and output.
	 */
	import { mealyEdges, type MealyEdge } from './mealy.ts';
	import { int, type Trace } from './trace.ts';

	let {
		trace,
		from,
		to,
		pair,
		output
	}: {
		trace: Trace;
		from: number;
		to: number;
		/** the digit pair at the playhead and the digit written, or null (certifying, or the run is off) */
		pair: [string, string] | null;
		output: string | null;
	} = $props();

	const uid = $props.id();
	const W = 260;
	const H = 190;
	const R = 17;
	const Y = 100;
	const states = $derived(trace.program.states);
	const pts = [
		{ x: 60, y: Y },
		{ x: 200, y: Y }
	];
	const edges = $derived(mealyEdges(trace.program.rows, states));

	/** Each edge's path, its label's place, and where its second line (row count, or the pair now) goes. */
	function geometry(e: Pick<MealyEdge, 'from' | 'to'>) {
		const p = pts[e.from];
		if (e.from === e.to) {
			// a loop on top of the node, its label above it
			const a1 = -Math.PI / 2 - 0.5;
			const a2 = -Math.PI / 2 + 0.5;
			const top = p.y - R - 30;
			return {
				d: `M${p.x + Math.cos(a1) * R},${p.y + Math.sin(a1) * R} C${p.x - 22},${top} ${p.x + 22},${top} ${p.x + Math.cos(a2) * R},${p.y + Math.sin(a2) * R}`,
				lx: p.x,
				ly: p.y - R - 50,
				sub: -12
			};
		}
		const q = pts[e.to];
		// 0 → 1 bows over the top, 1 → 0 under the bottom
		const up = e.from < e.to ? -1 : 1;
		const dir = q.x > p.x ? 1 : -1;
		const sx = p.x + dir * Math.cos(Math.PI / 6) * R;
		const ex = q.x - dir * (Math.cos(Math.PI / 6) * R + 2);
		const sy = p.y + up * Math.sin(Math.PI / 6) * R;
		const ey = q.y + up * Math.sin(Math.PI / 6) * R;
		return {
			d: `M${sx},${sy} Q${(sx + ex) / 2},${Y + up * 60} ${ex},${ey}`,
			lx: (sx + ex) / 2,
			ly: up < 0 ? Y - 40 : Y + 48,
			sub: up < 0 ? -12 : 12
		};
	}
	const current = $derived(edges.find((e) => e.from === from && e.to === to));
</script>

<svg viewBox="0 0 {W} {H}" role="img" aria-label="The adder as a machine: carry 0 and carry 1">
	<defs>
		<marker
			id="{uid}-a"
			viewBox="0 0 8 8"
			refX="7"
			refY="4"
			markerWidth="6"
			markerHeight="6"
			orient="auto-start-reverse"
		>
			<path d="M0,0.8 L7.2,4 L0,7.2 Z" class="head-faint" />
		</marker>
		<marker
			id="{uid}-b"
			viewBox="0 0 8 8"
			refX="7"
			refY="4"
			markerWidth="6"
			markerHeight="6"
			orient="auto-start-reverse"
		>
			<path d="M0,0.8 L7.2,4 L0,7.2 Z" class="head-on" />
		</marker>
	</defs>
	{#each edges as e (e.key)}
		{@const g = geometry(e)}
		{@const on = e === current && pair !== null}
		<path d={g.d} class={['edge', on && 'on']} marker-end="url(#{uid}-{on ? 'b' : 'a'})" />
		<text x={g.lx} y={g.ly} class={['elabel', on && 'on']}>{e.rule ?? `${int(e.rows)} rows`}</text>
		{#if on}
			<text x={g.lx} y={g.ly + g.sub} class="now">{pair[0]}+{pair[1]} / {output}</text>
		{:else if e.rule}
			<text x={g.lx} y={g.ly + g.sub} class="count">{int(e.rows)} rows</text>
		{/if}
	{/each}
	{#each pts as p, i (i)}
		<circle
			cx={p.x}
			cy={p.y}
			r={R}
			class={['node', i === to && 'to', i === from && i !== to && 'from']}
		/>
		<text x={p.x} y={p.y + 4.5} class={['nlabel', i === to && 'dark']}>{states[i]}</text>
		<text x={p.x} y={p.y + R + 13} class="caption">carry</text>
	{/each}
	<text x={W / 2} y={H - 6} class="caption">each edge: when it is taken / the digit written</text>
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: 100%;
		overflow: visible;
		font-family: var(--font-mono);
	}
	.edge {
		fill: none;
		stroke: var(--color-rule);
		stroke-width: 0.9;
	}
	.edge.on {
		stroke: var(--color-ink);
		stroke-width: 1.5;
	}
	.head-faint {
		fill: var(--color-rule);
	}
	.head-on {
		fill: var(--color-ink);
	}
	.node {
		fill: #121212;
		stroke: var(--color-rule);
		stroke-width: 0.9;
		transition:
			fill 160ms ease-in-out,
			stroke 160ms ease-in-out;
	}
	.node.from {
		stroke: var(--color-ink);
		stroke-width: 1.3;
	}
	.node.to {
		fill: var(--color-ink);
		stroke: var(--color-ink);
	}
	.nlabel {
		font-size: 13px;
		text-anchor: middle;
		fill: var(--color-ink);
	}
	.nlabel.dark {
		fill: var(--color-void);
		font-weight: 600;
	}
	.elabel {
		font-size: 9.5px;
		text-anchor: middle;
		fill: var(--color-ink-3);
	}
	.elabel.on {
		fill: var(--color-ink-2);
	}
	.count {
		font-size: 8px;
		text-anchor: middle;
		fill: var(--color-ink-3);
		opacity: 0.75;
	}
	.now {
		font-size: 11px;
		text-anchor: middle;
		fill: var(--color-ink);
	}
	.caption {
		font-size: 8px;
		text-anchor: middle;
		fill: var(--color-ink-3);
	}
</style>
