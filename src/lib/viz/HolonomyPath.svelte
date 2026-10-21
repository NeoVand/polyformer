<script lang="ts">
	/**
	 * "Carry a frame": how holonomy attention builds a term. Each token is a rotation (top row). Walk
	 * along the sequence carrying a frame and turn it only at the chosen tokens (bottom row); the
	 * frame at the end is the ordered product of their rotations, the term the layer reads for that
	 * group. Three tokens whose product is the identity bring the frame back unturned, and those are
	 * the tokens the A5 task asks the layer to mark. Rotations are drawn as tripods: the images of
	 * three axes, marked circle, square and diamond, in a fixed three-quarter view.
	 */
	import { prefersReducedMotion, Tween } from 'svelte/motion';
	import { cubicInOut } from 'svelte/easing';
	import Icon from '#lib/ui/Icon.svelte';
	import { Dice } from '#lib/ui/icons.ts';
	import { identity, multiply, type Matrix3 } from './a5.ts';
	import {
		carriedFrames,
		makeSequence,
		orderedProduct,
		project,
		turnDegrees
	} from './holonomyPath.ts';

	let { rotations, learned = false }: { rotations: Matrix3[]; learned?: boolean } = $props();

	let seed = $state(3);
	const sequence = $derived(makeSequence(seed));
	let chosen = $state<number[]>(makeSequence(3).planted);
	let hover = $state<number | null>(null);

	const N = 8;
	const W = 880;
	const H = 248;
	const colX = (t: number) => 138 + t * 80;
	const END_X = 820;
	const MOVE_Y = 74;
	const FRAME_Y = 168;

	const flat = (ms: Matrix3[]) => ms.flatMap((m) => m.flat());
	const moves = $derived(sequence.tokens.map((g) => rotations[g]));
	const frames = $derived(carriedFrames(rotations, sequence.tokens, chosen));
	const product = $derived(orderedProduct(rotations, sequence.tokens, chosen));
	const turned = $derived(turnDegrees(product));
	const swapped = $derived.by(() => {
		if (chosen.length < 2) return null;
		const [a, b, ...rest] = [...chosen].sort((x, y) => x - y);
		const order = [b, a, ...rest].map((t) => rotations[sequence.tokens[t]]);
		return turnDegrees(order.reduce((m, r) => multiply(m, r), identity));
	});

	const motion = {
		duration: () => (prefersReducedMotion.current ? 0 : 650),
		easing: cubicInOut
	};
	const moveTween = Tween.of(() => flat(moves), motion);
	const frameTween = Tween.of(() => flat(frames), motion);
	const unflat = (v: number[], i: number): Matrix3 => [
		v.slice(i * 9, i * 9 + 3),
		v.slice(i * 9 + 3, i * 9 + 6),
		v.slice(i * 9 + 6, i * 9 + 9)
	];

	/** The three axis tips of a rotation in screen space, back to front. */
	function tripod(m: Matrix3, r: number) {
		return [0, 1, 2]
			.map((k) => {
				const col = [m[0][k], m[1][k], m[2][k]];
				const len = Math.hypot(...col) || 1;
				const p = project(col.map((x) => x / len));
				return { k, x: p.x * r, y: p.y * r, z: p.z };
			})
			.sort((a, b) => a.z - b.z);
	}

	function toggle(t: number) {
		chosen = chosen.includes(t)
			? chosen.filter((x) => x !== t)
			: [...chosen, t].sort((a, b) => a - b);
	}
	function fresh() {
		seed = (seed * 7919 + 13) % 100003;
		chosen = makeSequence(seed).planted;
	}
	const list = (ts: number[]) =>
		ts.length === 1
			? `token ${ts[0] + 1}`
			: `tokens ${ts
					.slice(0, -1)
					.map((t) => t + 1)
					.join(', ')} and ${ts[ts.length - 1] + 1}`;
	const deg = (d: number) => `${d < 0.05 ? '0' : d < 9.95 ? d.toFixed(1) : d.toFixed(0)}°`;
	const closes = $derived(turned < (learned ? 15 : 0.05));
</script>

{#snippet axes(m: Matrix3, cx: number, cy: number, r: number, cls: string)}
	<circle class="ring {cls}" {cx} {cy} {r} />
	{#each tripod(m, r) as a (a.k)}
		<line class="axis {cls}" class:back={a.z < 0} x1={cx} y1={cy} x2={cx + a.x} y2={cy + a.y} />
		{#if a.k === 0}
			<circle class="tip {cls}" class:back={a.z < 0} cx={cx + a.x} cy={cy + a.y} r={r * 0.13} />
		{:else if a.k === 1}
			<rect
				class="tip {cls}"
				class:back={a.z < 0}
				x={cx + a.x - r * 0.12}
				y={cy + a.y - r * 0.12}
				width={r * 0.24}
				height={r * 0.24}
			/>
		{:else}
			<path
				class="tip {cls}"
				class:back={a.z < 0}
				d="M{cx + a.x} {cy + a.y - r * 0.17} L{cx + a.x + r * 0.17} {cy + a.y} L{cx + a.x} {cy +
					a.y +
					r * 0.17} L{cx + a.x - r * 0.17} {cy + a.y} Z"
			/>
		{/if}
	{/each}
{/snippet}

<div class="hp">
	<div class="scroll">
		<svg viewBox="0 0 {W} {H}" role="group" aria-label="A frame carried along eight tokens">
			<text class="row" x="0" y="26">token</text>
			<text class="row" x="0" y={MOVE_Y + 4}>its rotation</text>
			<text class="row" x="0" y={FRAME_Y + 4}>carried frame</text>
			<line class="path" x1={colX(0) - 44} x2={END_X - 40} y1={FRAME_Y} y2={FRAME_Y} />
			{@render axes(identity, colX(0) - 44, FRAME_Y, 13, 'ghost')}
			{#each sequence.tokens as g, t (t)}
				{@const on = chosen.includes(t)}
				<g
					class="col"
					class:on
					class:hover={hover === t}
					role="button"
					tabindex="0"
					aria-pressed={on}
					aria-label={`Token ${t + 1}, element ${g}${on ? ', chosen' : ''}`}
					onclick={() => toggle(t)}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							toggle(t);
						}
					}}
					onpointerenter={() => (hover = t)}
					onpointerleave={() => (hover = null)}
				>
					<rect class="hit" x={colX(t) - 38} y="6" width="76" height={H - 12} rx="4" />
					<text class="num" x={colX(t)} y="26">{t + 1}</text>
					{@render axes(unflat(moveTween.current, t), colX(t), MOVE_Y, 20, on ? 'lit' : 'dim')}
					{#if on}
						<path
							class="apply"
							d="M{colX(t)} {MOVE_Y + 30} L{colX(t)} {FRAME_Y - 36} M{colX(t) - 3.5} {FRAME_Y -
								42} L{colX(t)} {FRAME_Y - 36} L{colX(t) + 3.5} {FRAME_Y - 42}"
						/>
					{/if}
					{@render axes(unflat(frameTween.current, t), colX(t), FRAME_Y, 26, on ? 'lit' : 'kept')}
					{#if sequence.inLoop[t]}
						<circle class="loop" cx={colX(t)} cy={FRAME_Y + 44} r="3" />
					{/if}
				</g>
			{/each}
			<text class="row end" x={END_X} y="26">end and start</text>
			{@render axes(identity, END_X, FRAME_Y, 26, 'ghost')}
			{@render axes(unflat(frameTween.current, N - 1), END_X, FRAME_Y, 26, 'lit')}
			<text class="turn" x={END_X} y={FRAME_Y + 48}>{deg(turned)}</text>
		</svg>
	</div>
	<div class="read">
		<p class="lead">
			{#if chosen.length === 0}
				Choose tokens to turn the frame at.
			{:else}
				Turning at {list(chosen)}, the frame comes back
				<strong>{closes ? 'unturned' : `turned by ${deg(turned)}`}</strong
				>{#if closes && learned}&nbsp;(within {deg(turned)}){/if}.
				{#if closes && chosen.length === 3}These three moves undo each other.{/if}
			{/if}
		</p>
		{#if swapped !== null}
			<p>
				The same moves with the first two swapped leave it turned by {deg(swapped)}: the term
				depends on the order.
			</p>
		{/if}
		<p class="quiet">
			<span class="dot" aria-hidden="true"></span> marks each token that belongs to three tokens, in order,
			whose moves undo each other: what the task asks the layer to find. Click tokens to choose them.
		</p>
		<div class="actions">
			<button onclick={fresh}><Icon icon={Dice} size={14} /> New sequence</button>
			<button onclick={() => (chosen = sequence.planted)}>Show a loop</button>
		</div>
	</div>
</div>

<style>
	.hp {
		display: grid;
		gap: 10px;
	}
	.scroll {
		overflow-x: auto;
	}
	svg {
		display: block;
		width: 100%;
		min-width: 620px;
		height: auto;
		font-family: var(--font-sans);
	}
	.row {
		font-size: 11px;
		fill: var(--color-ink-3);
	}
	.row.end {
		text-anchor: middle;
	}
	.num {
		font-size: 11px;
		fill: var(--color-ink-3);
		text-anchor: middle;
		font-variant-numeric: tabular-nums;
	}
	.col.on .num,
	.col.hover .num {
		fill: var(--color-ink);
	}
	.col {
		cursor: pointer;
		outline: none;
	}
	.col:focus-visible .hit {
		stroke: var(--color-rule);
	}
	.hit {
		fill: transparent;
		stroke: none;
	}
	.path {
		stroke: var(--color-edge);
		stroke-width: 1;
	}
	.ring {
		fill: var(--color-void);
		stroke: var(--color-edge);
		stroke-width: 1;
	}
	.axis {
		stroke-width: 1.3;
		stroke-linecap: round;
		transition: opacity 250ms ease;
	}
	.tip {
		stroke-width: 1;
		transition: opacity 250ms ease;
	}
	.axis.lit {
		stroke: var(--color-ink);
	}
	.tip.lit {
		fill: var(--color-ink);
		stroke: var(--color-ink);
	}
	.axis.kept,
	.axis.dim {
		stroke: var(--color-ink-3);
	}
	.tip.kept,
	.tip.dim {
		fill: var(--color-ink-3);
		stroke: var(--color-ink-3);
	}
	.axis.dim,
	.tip.dim {
		opacity: 0.5;
	}
	.col.hover .axis.dim,
	.col.hover .tip.dim {
		opacity: 0.85;
	}
	.axis.ghost {
		stroke: var(--color-ink-3);
		stroke-dasharray: 2 2.5;
	}
	.tip.ghost {
		fill: none;
		stroke: var(--color-ink-3);
	}
	.back {
		opacity: 0.45;
	}
	.axis.dim.back,
	.tip.dim.back {
		opacity: 0.25;
	}
	.apply {
		fill: none;
		stroke: var(--color-ink-2);
		stroke-width: 1;
	}
	.loop {
		fill: var(--color-ink-2);
	}
	.turn {
		font-size: 13px;
		fill: var(--color-ink);
		text-anchor: middle;
		font-variant-numeric: tabular-nums;
	}
	.read {
		display: grid;
		gap: 6px;
		max-width: 72ch;
	}
	.read p {
		margin: 0;
		font-size: 12px;
		line-height: 1.6;
		color: var(--color-ink-2);
	}
	.read .lead {
		font-size: 13px;
		color: var(--color-ink);
	}
	.read strong {
		font-weight: 500;
	}
	.read .quiet {
		color: var(--color-ink-3);
		font-size: 11px;
	}
	.dot {
		display: inline-block;
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink-2);
		vertical-align: 1px;
	}
	.actions {
		display: flex;
		gap: 22px;
		margin-top: 4px;
	}
	.actions button {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		border: 0;
		background: transparent;
		padding: 4px 0;
		font-size: 12px;
		color: var(--color-ink-2);
		cursor: pointer;
	}
	.actions button:hover {
		color: var(--color-ink);
	}
</style>
