<script lang="ts">
	/**
	 * A computation graph in the style of the original Polyformer notebook (TikZ): tensors as
	 * circles, projections as labelled arrows from the input, Hadamard products and merges as
	 * small junctions, and each derived tensor's formula written beside it. The geometry lives
	 * in a spec (computeGraphs.ts); this component only draws it. KaTeX labels sit in an HTML
	 * layer whose type scales with the figure, so the graph reads the same at any width.
	 */
	import MathTex from '#lib/ui/Math.svelte';
	import type { Graph, GraphEdge } from './computeGraphs.ts';

	let { graph, label }: { graph: Graph; label: string } = $props();

	const R = 15;
	const JR = 5.5;
	type P = { x: number; y: number };
	const at = (id: string): P & { r: number } => {
		const n = graph.nodes.find((v) => v.id === id);
		if (n) return { x: n.x, y: n.y, r: n.r ?? R };
		const j = graph.joins.find((v) => v.id === id);
		if (j) return { x: j.x, y: j.y, r: j.op === 'merge' ? 2.5 : JR };
		throw new Error(`compute graph: no node ${id}`);
	};
	const unit = (x: number, y: number) => {
		const l = Math.hypot(x, y) || 1;
		return { x: x / l, y: y / l };
	};

	/** A quadratic curve from boundary to boundary, bent sideways by `bend` of its length. */
	function geometry(e: GraphEdge) {
		const a = at(e.from);
		const b = at(e.to);
		const dx = b.x - a.x;
		const dy = b.y - a.y;
		const len = Math.hypot(dx, dy);
		const n = { x: -dy / len, y: dx / len };
		const bend = e.bend ?? 0;
		const c = { x: (a.x + b.x) / 2 + n.x * bend * len, y: (a.y + b.y) / 2 + n.y * bend * len };
		if (e.via) Object.assign(c, e.via);
		const ua = unit(c.x - a.x, c.y - a.y);
		const ub = unit(b.x - c.x, b.y - c.y);
		const p0 = { x: a.x + ua.x * a.r, y: a.y + ua.y * a.r };
		const p1 = { x: b.x - ub.x * b.r, y: b.y - ub.y * b.r };
		const point = (t: number) => ({
			x: (1 - t) ** 2 * p0.x + 2 * (1 - t) * t * c.x + t * t * p1.x,
			y: (1 - t) ** 2 * p0.y + 2 * (1 - t) * t * c.y + t * t * p1.y
		});
		const tangent = (t: number) =>
			unit(
				2 * (1 - t) * (c.x - p0.x) + 2 * t * (p1.x - c.x),
				2 * (1 - t) * (c.y - p0.y) + 2 * t * (p1.y - c.y)
			);
		// the arrowhead sits a little past the middle, as in the notebook's TikZ
		const m = point(e.arrowAt ?? 0.55);
		const d = tangent(e.arrowAt ?? 0.55);
		const s = 4.2;
		const tip = `M${m.x + d.x * s},${m.y + d.y * s} L${m.x - d.x * s - d.y * s * 0.62},${m.y - d.y * s + d.x * s * 0.62} L${m.x - d.x * s + d.y * s * 0.62},${m.y - d.y * s - d.x * s * 0.62} Z`;
		const lt = point(e.labelAt ?? 0.5);
		const ln = tangent(e.labelAt ?? 0.5);
		const side = e.side ?? -1;
		const label = { x: lt.x - ln.y * 11 * side, y: lt.y + ln.x * 11 * side };
		return {
			d: `M${p0.x},${p0.y} Q${c.x},${c.y} ${p1.x},${p1.y}`,
			tip,
			label,
			arrow: e.arrow !== false
		};
	}
	const edges = $derived(graph.edges.map((e) => ({ e, g: geometry(e) })));
	const pct = (v: number, of: number) => `${(v / of) * 100}%`;
</script>

<figure class="cg" style:--gw={graph.w} style:max-width="{graph.w}px">
	<div class="canvas" style:aspect-ratio="{graph.w} / {graph.h}">
		<svg viewBox="0 0 {graph.w} {graph.h}" role="img" aria-label={label}>
			{#each edges as { e, g }, i (i)}
				<path class="edge" class:soft={e.soft} d={g.d} />
				{#if g.arrow}<path class="tip" class:soft={e.soft} d={g.tip} />{/if}
			{/each}
			{#each graph.joins as j (j.id)}
				{#if j.op === 'merge'}
					<circle class="merge" cx={j.x} cy={j.y} r="2.5" />
				{:else}
					<circle class="join" cx={j.x} cy={j.y} r={JR} />
					{#if j.op === 'hadamard'}
						<circle class="merge" cx={j.x} cy={j.y} r="1.5" />
					{:else}
						<text class="sigma" x={j.x} y={j.y + 3.2} text-anchor="middle">Σ</text>
					{/if}
				{/if}
			{/each}
			{#each graph.nodes as v (v.id)}
				<circle class="node {v.kind}" cx={v.x} cy={v.y} r={v.r ?? R} />
			{/each}
		</svg>
		{#each graph.nodes as v (v.id)}
			<span class="lab node-lab" style:left={pct(v.x, graph.w)} style:top={pct(v.y, graph.h)}
				><MathTex tex={v.tex} /></span
			>
		{/each}
		{#each edges as { e, g }, i (i)}
			{#if e.tex}
				<span
					class="lab edge-lab"
					style:left={pct(g.label.x, graph.w)}
					style:top={pct(g.label.y, graph.h)}><MathTex tex={e.tex} /></span
				>
			{/if}
		{/each}
		{#each graph.notes as n, i (i)}
			<span
				class="lab note {n.align ?? 'left'}"
				style:left={pct(n.x, graph.w)}
				style:top={pct(n.y, graph.h)}><MathTex tex={n.tex} /></span
			>
		{/each}
	</div>
</figure>

<style>
	.cg {
		container-type: inline-size;
		margin: 14px 0 18px;
	}
	.canvas {
		position: relative;
		width: 100%;
	}
	svg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		overflow: visible;
	}
	.edge {
		fill: none;
		stroke: #9a9a9a;
		stroke-width: 1;
	}
	.tip {
		fill: #9a9a9a;
	}
	.edge.soft {
		stroke: #555;
		stroke-dasharray: 2 3;
	}
	.tip.soft {
		fill: #555;
	}
	.node {
		stroke-width: 1;
	}
	.node.input {
		fill: var(--color-void);
		stroke: var(--color-ink);
	}
	.node.proj {
		fill: #161616;
		stroke: #8a8a8a;
	}
	.node.mid {
		fill: #222;
		stroke: #9a9a9a;
	}
	.node.output {
		fill: var(--color-void);
		stroke: var(--color-ink);
		stroke-width: 1.4;
	}
	.join {
		fill: var(--color-void);
		stroke: #9a9a9a;
		stroke-width: 1;
	}
	.merge {
		fill: #cfcfcf;
	}
	.sigma {
		font-family: 'KaTeX_Main', serif;
		font-size: 8.5px;
		fill: #cfcfcf;
	}
	/* type scales with the figure: 1cqw is a hundredth of its width */
	.lab {
		position: absolute;
		white-space: nowrap;
		pointer-events: none;
		line-height: 1;
	}
	.node-lab {
		transform: translate(-50%, -50%);
		font-size: calc(12.5cqw * 100 / var(--gw));
		color: var(--color-ink);
	}
	.edge-lab {
		transform: translate(-50%, -50%);
		font-size: calc(10.5cqw * 100 / var(--gw));
		color: var(--color-ink-2);
	}
	.note {
		transform: translateY(-50%);
		font-size: calc(10.5cqw * 100 / var(--gw));
		color: var(--color-ink-3);
	}
	.note.center {
		transform: translate(-50%, -50%);
	}
	.note.right {
		transform: translate(-100%, -50%);
	}
</style>
