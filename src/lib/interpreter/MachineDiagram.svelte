<script lang="ts">
	/**
	 * The program as a machine: its states at the layout the trace carries, its transitions (all of them when the
	 * table is small, else only the one being taken), the state read lit in outline and the state written filled.
	 */
	import type { Trace } from './trace.ts';

	let { trace, from, to, event }: { trace: Trace; from: number; to: number; event: string } =
		$props();

	const uid = $props.id();
	const diagram = $derived(trace.program.diagram!);
	const states = $derived(trace.program.states);
	const n = $derived(states.length);
	const aspect = $derived.by(() => {
		const d = diagram.dims;
		if (diagram.kind === 'ring' || !d) return 1.25;
		return Math.min(2.4, Math.max(0.9, (d[0] / d[1]) * (diagram.kind === 'grid' ? 1 : 0.9)));
	});
	const W = 320;
	const H = $derived(Math.round(W / aspect));
	const r = $derived(Math.min(15, Math.max(3.2, 70 / Math.sqrt(n))));
	const pad = $derived(r + (n <= 12 ? (states.every((s) => s.length <= 2) ? 18 : 30) : 8));
	const pts = $derived(
		diagram.pos.map(([x, y]) => ({ x: pad + x * (W - 2 * pad), y: pad + y * (H - 2 * pad) }))
	);
	const index = $derived(
		Object.fromEntries(states.map((s, i) => [s, i])) as Record<string, number>
	);
	const showAll = $derived(trace.program.rows.length <= 64);
	const labelAll = $derived(n <= 12);
	const labelEdges = $derived(labelAll && trace.program.rows.length <= 24);

	interface Edge {
		key: string;
		a: number;
		b: number;
		label: string;
	}
	/** Transitions merged per (from, to), labelled by their events. */
	const edges = $derived.by(() => {
		const m: Record<string, Edge> = {};
		for (const row of trace.program.rows) {
			const a = index[row.s];
			const b = index[row.t];
			const key = `${a}>${b}`;
			if (m[key]) m[key].label += ` ${row.b}`;
			else m[key] = { key, a, b, label: row.b };
		}
		return Object.values(m);
	});
	const pairs = $derived(new Set(edges.map((e) => e.key)));

	/** Short names sit inside their node; longer ones outside it, away from the centre. */
	const inside = $derived(labelAll && states.every((s) => s.length <= 2));
	const radial = (p: { x: number; y: number }) =>
		Math.atan2(p.y - H / 2, p.x - W / 2) || -Math.PI / 2;

	function geometry(a: number, b: number) {
		const p = pts[a];
		const q = pts[b];
		if (a === b) {
			// a small loop beside the node, turned off the outward direction where a long label sits
			const ang = radial(p) + (inside ? 0 : 1.35);
			const ux = Math.cos(ang);
			const uy = Math.sin(ang);
			const lx = p.x + ux * (r + 9);
			const ly = p.y + uy * (r + 9);
			const s1 = { x: p.x + Math.cos(ang - 0.5) * r, y: p.y + Math.sin(ang - 0.5) * r };
			const s2 = { x: p.x + Math.cos(ang + 0.5) * r, y: p.y + Math.sin(ang + 0.5) * r };
			return {
				d: `M${s1.x},${s1.y} C${lx + uy * 9},${ly - ux * 9} ${lx - uy * 9},${ly + ux * 9} ${s2.x},${s2.y}`,
				lx: p.x + ux * (r + 15),
				ly: p.y + uy * (r + 15)
			};
		}
		const dx = q.x - p.x;
		const dy = q.y - p.y;
		const len = Math.hypot(dx, dy) || 1;
		const ux = dx / len;
		const uy = dy / len;
		// a pair of opposite transitions bows apart so both stay readable
		const bow = pairs.has(`${b}>${a}`) ? Math.min(18, len * 0.18) : 0;
		const sx = p.x + ux * (r + 1.5);
		const sy = p.y + uy * (r + 1.5);
		const ex = q.x - ux * (r + 3);
		const ey = q.y - uy * (r + 3);
		const mx = (sx + ex) / 2 - uy * bow;
		const my = (sy + ey) / 2 + ux * bow;
		return { d: `M${sx},${sy} Q${mx},${my} ${ex},${ey}`, lx: mx - uy * 7, ly: my + ux * 7 };
	}

	const current = $derived(geometry(from, to));
	const showLabel = (i: number) =>
		labelAll || i === from || i === to || (diagram.kind === 'chain' && i % 10 === 0);
</script>

<svg viewBox="0 0 {W} {H}" role="img" aria-label="The program as a state machine">
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
	{#if showAll}
		{#each edges as e (e.key)}
			{@const g = geometry(e.a, e.b)}
			<path d={g.d} class="edge" marker-end="url(#{uid}-a)" />
			{#if labelEdges && !(e.a === from && e.b === to)}
				<text x={g.lx} y={g.ly + 3} class="elabel">{e.label}</text>
			{/if}
		{/each}
	{/if}
	{#each pts as p, i (i)}
		<circle
			cx={p.x}
			cy={p.y}
			{r}
			class={['node', i === to && 'to', i === from && i !== to && 'from']}
		/>
		{#if showLabel(i)}
			{@const out = labelAll && !inside}
			{@const ang = radial(p)}
			<text
				x={out ? p.x + Math.cos(ang) * (r + 13) : p.x}
				y={out ? p.y + Math.sin(ang) * (r + 11) + 3.4 : inside ? p.y + 3.6 : p.y - r - 4}
				class={[
					'nlabel',
					labelAll && 'big',
					(i === to || i === from) && 'lit',
					i === to && inside && 'dark'
				]}>{states[i]}</text
			>
		{/if}
	{/each}
	<path d={current.d} class="edge on" marker-end="url(#{uid}-b)" />
	<text x={current.lx} y={current.ly + 3} class="elabel on">{event}</text>
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
		stroke-width: 0.8;
		opacity: 0.7;
	}
	.edge.on {
		stroke: var(--color-ink);
		stroke-width: 1.5;
		opacity: 1;
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
		font-size: 9px;
		text-anchor: middle;
		fill: var(--color-ink-3);
	}
	.nlabel.big {
		font-size: 9.5px;
		fill: var(--color-ink-2);
	}
	.nlabel.lit {
		fill: var(--color-ink);
	}
	.nlabel.dark {
		fill: var(--color-void);
		font-weight: 600;
	}
	.elabel {
		font-size: 8.5px;
		text-anchor: middle;
		fill: var(--color-ink-3);
	}
	.elabel.on {
		fill: var(--color-ink);
		font-size: 9.5px;
	}
</style>
