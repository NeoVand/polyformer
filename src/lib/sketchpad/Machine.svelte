<script lang="ts">
	import { SUM_CODES } from './inside.ts';
	import type { TickView } from './pad.svelte.ts';
	import { B } from './sprites.ts';

	interface Props {
		last: TickView | null;
		kind: 'add' | 'mul';
	}

	let { last, kind }: Props = $props();

	/** the adder: the carry on the sheet is the machine's state; each view the model reads is one arrow */
	const add = $derived.by(() => {
		if (!last || last.op !== 'ADD-FAST') return null;
		const from = last.cells[0] === '1' ? 1 : 0;
		const v = SUM_CODES.indexOf(last.out[0]);
		const to: number | 'halt' | null = v < 0 ? null : v === 20 ? 'halt' : v >= 10 ? 1 : 0;
		return { from, to, sum: v >= 0 && v < 20 ? v : null };
	});
	const on = (from: number, to: number | 'halt') => !!add && add.from === from && add.to === to;
	const addWords = $derived.by(() => {
		if (!last || !add) return '';
		if (add.to === 'halt') return 'Nothing left to add: halt.';
		if (add.sum === null) return `It wrote ${last.out[0]}.`;
		const [c, t, b] = last.cells;
		const parts = [t, b, c].filter((g) => g !== B);
		const sum = parts.reduce((x, g) => x + Number(g), 0);
		const s = add.sum;
		const write = `write ${s % 10}${s >= 10 ? ', carry 1' : ''}`;
		const lhs = parts.length ? parts.join(' + ') : '0';
		// a pushed tick can write a sum that is not the column's
		return s === sum ? `${lhs} = ${s}: ${write}.` : `${lhs} = ${sum}, but it wrote ${s}: ${write}.`;
	});

	/** the multiplier's steps; the model names the next one with its third token */
	const NODES: Record<string, { x: number; y: number; word: string }> = {
		MUL: { x: 34, y: 66, word: 'MUL' },
		ADD: { x: 118, y: 20, word: 'ADD' },
		ADZ: { x: 118, y: 112, word: 'ADZ' },
		FLS: { x: 202, y: 112, word: 'FLS' },
		NXT: { x: 202, y: 20, word: 'NXT' },
		H: { x: 262, y: 66, word: 'halt' }
	};
	const LETTER: Record<string, string> = {
		M: 'MUL',
		A: 'ADD',
		Z: 'ADZ',
		F: 'FLS',
		N: 'NXT',
		H: 'H'
	};
	const EDGES = [
		{ from: 'MUL', to: 'ADD', letter: 'A', bend: -12 },
		{ from: 'ADD', to: 'MUL', letter: 'M', bend: -12 },
		{ from: 'MUL', to: 'ADZ', letter: 'Z', bend: 0 },
		{ from: 'ADZ', to: 'FLS', letter: 'F', bend: 0 },
		{ from: 'FLS', to: 'NXT', letter: 'N', bend: 0 },
		{ from: 'NXT', to: 'MUL', letter: 'M', bend: -30 },
		{ from: 'NXT', to: 'H', letter: 'H', bend: 0 }
	];
	const mul = $derived.by(() => {
		if (!last || last.op === 'ADD-FAST') return null;
		return { from: last.op as string, to: LETTER[last.out[2]] ?? null, letter: last.out[2] };
	});
	const mulWords = $derived.by(() => {
		if (!mul) return '';
		return `${mul.from}, then it wrote ${mul.letter}: ${mul.to === 'H' ? 'halt' : `next step ${mul.to}`}.`;
	});

	function arc(x1: number, y1: number, x2: number, y2: number, bend: number, r = 16) {
		const dx = x2 - x1;
		const dy = y2 - y1;
		const d = Math.hypot(dx, dy) || 1;
		const ux = dx / d;
		const uy = dy / d;
		const sx = x1 + ux * r;
		const sy = y1 + uy * r;
		const ex = x2 - ux * (r + 2);
		const ey = y2 - uy * (r + 2);
		const mx = (sx + ex) / 2 - uy * bend;
		const my = (sy + ey) / 2 + ux * bend;
		return { d: `M${sx},${sy} Q${mx},${my} ${ex},${ey}`, lx: mx - uy * 9, ly: my + ux * 9 };
	}
</script>

<figure class="machine">
	<figcaption>The machine <span>state on the sheet, every arrow by the model</span></figcaption>
	{#if kind === 'add'}
		<svg viewBox="-4 -4 276 142" role="img" aria-label="The adder as a two-state machine">
			<defs>
				<marker
					id="ma"
					viewBox="0 0 8 8"
					refX="7"
					refY="4"
					markerWidth="6"
					markerHeight="6"
					orient="auto"
				>
					<path d="M0,0 L8,4 L0,8 z" class="head" />
				</marker>
				<marker
					id="ma-on"
					viewBox="0 0 8 8"
					refX="7"
					refY="4"
					markerWidth="6"
					markerHeight="6"
					orient="auto"
				>
					<path d="M0,0 L8,4 L0,8 z" class="head on" />
				</marker>
			</defs>
			{#each [{ s: 0, x: 60 }, { s: 1, x: 200 }] as n (n.s)}
				{@const self = on(n.s, n.s)}
				<path
					class="edge"
					class:on={self}
					d="M{n.x - 11},{48} C{n.x - 34},{2} {n.x + 34},{2} {n.x + 11},{48}"
					marker-end={self ? 'url(#ma-on)' : 'url(#ma)'}
				/>
				<text class="elab" class:on={self} x={n.x} y="8" text-anchor="middle"
					>{n.s === 0 ? 'sum < 10' : 'sum ≥ 10'}</text
				>
			{/each}
			<path
				class="edge"
				class:on={on(0, 1)}
				d="M80,58 Q130,40 180,58"
				marker-end={on(0, 1) ? 'url(#ma-on)' : 'url(#ma)'}
			/>
			<text class="elab" class:on={on(0, 1)} x="130" y="40" text-anchor="middle">sum ≥ 10</text>
			<path
				class="edge"
				class:on={on(1, 0)}
				d="M180,80 Q130,98 80,80"
				marker-end={on(1, 0) ? 'url(#ma-on)' : 'url(#ma)'}
			/>
			<text class="elab" class:on={on(1, 0)} x="130" y="106" text-anchor="middle">sum &lt; 10</text>
			<path
				class="edge"
				class:on={on(0, 'halt')}
				d="M60,89 L60,114"
				marker-end={on(0, 'halt') ? 'url(#ma-on)' : 'url(#ma)'}
			/>
			<text class="node-t" class:on={on(0, 'halt')} x="60" y="130" text-anchor="middle">halt</text>
			{#each [{ s: 0, x: 60 }, { s: 1, x: 200 }] as n (n.s)}
				<circle class="node" class:on={add?.from === n.s} cx={n.x} cy="69" r="19" />
				<text class="node-t" class:on={add?.from === n.s} x={n.x} y="73" text-anchor="middle"
					>carry {n.s}</text
				>
			{/each}
		</svg>
		<p class="words num">{addWords || 'Each view the model reads is one arrow.'}</p>
	{:else}
		<svg viewBox="0 -4 290 140" role="img" aria-label="The multiplier's steps as a machine">
			<defs>
				<marker
					id="mm"
					viewBox="0 0 8 8"
					refX="7"
					refY="4"
					markerWidth="6"
					markerHeight="6"
					orient="auto"
				>
					<path d="M0,0 L8,4 L0,8 z" class="head" />
				</marker>
				<marker
					id="mm-on"
					viewBox="0 0 8 8"
					refX="7"
					refY="4"
					markerWidth="6"
					markerHeight="6"
					orient="auto"
				>
					<path d="M0,0 L8,4 L0,8 z" class="head on" />
				</marker>
			</defs>
			{#each EDGES as e (e.from + e.to)}
				{@const a = NODES[e.from]}
				{@const b = NODES[e.to]}
				{@const g = arc(a.x, a.y, b.x, b.y, e.bend)}
				{@const lit = !!mul && mul.from === e.from && mul.to === e.to}
				<path class="edge" class:on={lit} d={g.d} marker-end={lit ? 'url(#mm-on)' : 'url(#mm)'} />
				<text class="elab mono" class:on={lit} x={g.lx} y={g.ly + 3} text-anchor="middle"
					>{e.letter}</text
				>
			{/each}
			{#each Object.entries(NODES) as [k, n] (k)}
				<circle class="node" class:on={mul?.from === k} cx={n.x} cy={n.y} r="16" />
				<text class="node-t" class:on={mul?.from === k} x={n.x} y={n.y + 4} text-anchor="middle"
					>{n.word}</text
				>
			{/each}
		</svg>
		<p class="words num">{mulWords || 'The model names its next step with its third token.'}</p>
	{/if}
</figure>

<style>
	.machine {
		margin: 0;
		min-width: 0;
	}
	figcaption {
		font-size: var(--text-xs);
		color: var(--color-ink);
		margin-bottom: 8px;
	}
	figcaption span {
		color: var(--color-ink-3);
		margin-left: 6px;
	}
	svg {
		display: block;
		width: 100%;
		max-width: 300px;
		height: auto;
		overflow: visible;
	}
	.words {
		margin-top: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		min-height: 1.5em;
	}
	.mono {
		font-family: var(--font-mono);
	}
	.edge {
		fill: none;
		stroke: var(--color-rule);
		stroke-width: 1;
		transition: stroke 400ms cubic-bezier(0.22, 1, 0.36, 1);
	}
	.edge.on {
		stroke: var(--color-ink);
		stroke-width: 1.8;
	}
	.head {
		fill: var(--color-rule);
	}
	.head.on {
		fill: var(--color-ink);
	}
	.elab {
		font-size: 10px;
		fill: var(--color-ink-3);
		transition: fill 400ms cubic-bezier(0.22, 1, 0.36, 1);
	}
	.elab.on {
		fill: var(--color-ink);
	}
	.node {
		fill: var(--color-void, #000);
		stroke: var(--color-rule);
		stroke-width: 1;
		transition:
			stroke 400ms cubic-bezier(0.22, 1, 0.36, 1),
			fill 400ms cubic-bezier(0.22, 1, 0.36, 1);
	}
	.node.on {
		stroke: var(--color-ink);
		fill: var(--color-lift, #222);
	}
	.node-t {
		font-size: 10px;
		fill: var(--color-ink-3);
		font-family: var(--font-mono);
	}
	.node-t.on {
		fill: var(--color-ink);
	}
</style>
