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
	/** Radii of the junctions: a merge is a dot, ⊙ a small ring, Σ a ring big enough to read. */
	const JR = { merge: 2.5, hadamard: 6.5, pool: 10 } as const;
	type P = { x: number; y: number };
	/** Half-height of an op box. */
	const BOX = 12;
	type End = P & { input: boolean; rim: (d: P) => number };
	/** A node's centre, and how far its outline is from the centre in direction d. */
	const at = (id: string): End => {
		const n = graph.nodes.find((v) => v.id === id);
		if (n?.kind === 'op') {
			const hw = (n.w ?? 60) / 2;
			return {
				x: n.x,
				y: n.y,
				input: false,
				rim: (d) =>
					Math.min(hw / Math.max(Math.abs(d.x), 1e-6), BOX / Math.max(Math.abs(d.y), 1e-6))
			};
		}
		if (n) return { x: n.x, y: n.y, input: n.kind === 'input', rim: () => n.r ?? R };
		const j = graph.joins.find((v) => v.id === id);
		if (j) return { x: j.x, y: j.y, input: false, rim: () => JR[j.op] };
		throw new Error(`compute graph: no node ${id}`);
	};
	const unit = (x: number, y: number) => {
		const l = Math.hypot(x, y) || 1;
		return { x: x / l, y: y / l };
	};
	/** A direction in degrees, TikZ style: 0 is right, 90 is up (SVG y points down). */
	const dir = (deg: number) => ({
		x: Math.cos((deg * Math.PI) / 180),
		y: -Math.sin((deg * Math.PI) / 180)
	});

	/**
	 * A cubic from boundary to boundary that leaves and arrives in set directions, as TikZ's
	 * `out` and `in`: edges run level and then turn, so neighbouring streams stay parallel.
	 */
	function geometry(e: GraphEdge) {
		const a = at(e.from);
		const b = at(e.to);
		const straight = (Math.atan2(a.y - b.y, b.x - a.x) * 180) / Math.PI;
		// the input fans out at most of each target's angle, as in the notebook's figure
		const u = dir(e.out ?? (a.input ? 0.8 * straight : 0));
		const v = dir(e.enter ?? 0);
		const ra = a.rim(u);
		const rb = b.rim(v);
		const p0 = { x: a.x + u.x * ra, y: a.y + u.y * ra };
		const p1 = { x: b.x - v.x * rb, y: b.y - v.y * rb };
		// each end keeps its direction for a length that suits the turn it makes: a long level
		// run that drops into a junction keeps level until the drop, instead of arching over
		const dist = Math.hypot(p1.x - p0.x, p1.y - p0.y);
		const k = e.loose ?? 1;
		const L0 =
			k * Math.min(0.45 * dist, (0.55 * Math.abs(p1.x - p0.x)) / Math.max(Math.abs(u.x), 0.3));
		const L1 =
			k *
			(Math.abs(v.y) > 0.05
				? Math.min(0.45 * dist, (0.8 * Math.abs(p1.y - p0.y)) / Math.abs(v.y))
				: 0.45 * dist);
		const [r0, r1] = e.reach ?? [L0, L1];
		const c1 = { x: p0.x + u.x * r0, y: p0.y + u.y * r0 };
		const c2 = { x: p1.x - v.x * r1, y: p1.y - v.y * r1 };
		const point = (t: number) => {
			const s = 1 - t;
			return {
				x: s * s * s * p0.x + 3 * s * s * t * c1.x + 3 * s * t * t * c2.x + t * t * t * p1.x,
				y: s * s * s * p0.y + 3 * s * s * t * c1.y + 3 * s * t * t * c2.y + t * t * t * p1.y
			};
		};
		const tangent = (t: number) => {
			const s = 1 - t;
			return unit(
				3 * s * s * (c1.x - p0.x) + 6 * s * t * (c2.x - c1.x) + 3 * t * t * (p1.x - c2.x),
				3 * s * s * (c1.y - p0.y) + 6 * s * t * (c2.y - c1.y) + 3 * t * t * (p1.y - c2.y)
			);
		};
		// the arrowhead sits a little past the middle, as in the notebook's TikZ
		const m = point(e.arrowAt ?? 0.55);
		const d = tangent(e.arrowAt ?? 0.55);
		const sz = 4.2;
		const tip = `M${m.x + d.x * sz},${m.y + d.y * sz} L${m.x - d.x * sz - d.y * sz * 0.62},${m.y - d.y * sz + d.x * sz * 0.62} L${m.x - d.x * sz + d.y * sz * 0.62},${m.y - d.y * sz - d.x * sz * 0.62} Z`;
		const lt = point(e.labelAt ?? 0.5);
		const ln = tangent(e.labelAt ?? 0.5);
		const side = e.side ?? -1;
		const label = { x: lt.x - ln.y * 11 * side, y: lt.y + ln.x * 11 * side };
		return {
			d: `M${p0.x},${p0.y} C${c1.x},${c1.y} ${c2.x},${c2.y} ${p1.x},${p1.y}`,
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
					<circle class="merge" cx={j.x} cy={j.y} r={JR.merge} />
				{:else}
					<circle class="join" cx={j.x} cy={j.y} r={JR[j.op]} />
					{#if j.op === 'hadamard'}
						<circle class="merge" cx={j.x} cy={j.y} r="1.8" />
					{:else}
						<text class="sigma" x={j.x} y={j.y + 0.5}>Σ</text>
					{/if}
				{/if}
			{/each}
			{#each graph.nodes as v (v.id)}
				{#if v.kind === 'op'}
					<rect
						class="node op"
						x={v.x - (v.w ?? 60) / 2}
						y={v.y - BOX}
						width={v.w ?? 60}
						height={BOX * 2}
						rx="4"
					/>
				{:else}
					<circle class="node {v.kind}" cx={v.x} cy={v.y} r={v.r ?? R} />
				{/if}
			{/each}
		</svg>
		{#each graph.nodes as v (v.id)}
			<span
				class="lab node-lab"
				class:op={v.kind === 'op'}
				style:left={pct(v.x, graph.w)}
				style:top={pct(v.y, graph.h)}><MathTex tex={v.tex} /></span
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
	.node.op {
		fill: var(--color-void);
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
		font-size: 12px;
		fill: #e6e6e6;
		text-anchor: middle;
		dominant-baseline: central;
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
	.node-lab.op {
		font-size: calc(10.5cqw * 100 / var(--gw));
		color: var(--color-ink-2);
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
