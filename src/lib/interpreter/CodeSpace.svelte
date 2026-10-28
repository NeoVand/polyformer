<script lang="ts">
	/**
	 * The program's state codes in 3-D (their top three principal directions) and the head's output before the snap,
	 * which lands on the code of the state written. Drag to turn the view.
	 */
	import { Tween, prefersReducedMotion } from 'svelte/motion';
	import { cubicInOut } from 'svelte/easing';
	import type { Xyz } from './trace.ts';

	let {
		names,
		xyz,
		y,
		lit,
		fast
	}: { names: string[]; xyz: Xyz[]; y: Xyz | null; lit: number; fast: boolean } = $props();

	let yaw = $state(0.65);
	let pitch = $state(0.38);
	const point = Tween.of(() => y ?? ([0, 0, 0] as Xyz), { duration: 240, easing: cubicInOut });
	/** During a replay a step lasts a few milliseconds, so the point jumps instead of gliding. */
	const still = $derived(fast || prefersReducedMotion.current);

	const S = 240;
	const R = 92;
	function project([x, y_, z]: Xyz) {
		const cy = Math.cos(yaw);
		const sy = Math.sin(yaw);
		const cp = Math.cos(pitch);
		const sp = Math.sin(pitch);
		const x1 = x * cy + z * sy;
		const z1 = -x * sy + z * cy;
		const y1 = y_ * cp - z1 * sp;
		const z2 = y_ * sp + z1 * cp;
		const k = 1 / (1 + z2 * 0.18);
		return { x: S / 2 + x1 * R * k, y: S / 2 - y1 * R * k, z: z2 };
	}
	const pts = $derived(xyz.map((p, i) => ({ i, ...project(p) })).sort((a, b) => b.z - a.z));
	const litPt = $derived(project(xyz[lit] ?? [0, 0, 0]));
	const yPt = $derived(y ? project(still ? y : point.current) : null);
	const axes = $derived(
		(
			[
				[1, 0, 0],
				[0, 1, 0],
				[0, 0, 1]
			] as Xyz[]
		).map((a) => project(a))
	);
	const labelAll = $derived(names.length <= 12);
	const r = $derived(names.length > 100 ? 1.6 : names.length > 24 ? 2.2 : 3.2);

	let drag: { x: number; y: number; yaw: number; pitch: number } | null = null;
	function down(e: PointerEvent) {
		drag = { x: e.clientX, y: e.clientY, yaw, pitch };
		(e.currentTarget as Element).setPointerCapture(e.pointerId);
	}
	function move(e: PointerEvent) {
		if (!drag) return;
		yaw = drag.yaw + (e.clientX - drag.x) * 0.01;
		pitch = Math.max(-1.4, Math.min(1.4, drag.pitch + (e.clientY - drag.y) * 0.01));
	}
	function key(e: KeyboardEvent) {
		const d = {
			ArrowLeft: [-0.1, 0],
			ArrowRight: [0.1, 0],
			ArrowUp: [0, -0.1],
			ArrowDown: [0, 0.1]
		}[e.key];
		if (!d) return;
		e.preventDefault();
		yaw += d[0];
		pitch = Math.max(-1.4, Math.min(1.4, pitch + d[1]));
	}
</script>

<svg
	viewBox="0 0 {S} {S}"
	role="slider"
	tabindex="0"
	aria-label="State codes in three dimensions; drag or use the arrow keys to turn"
	aria-valuetext="lit code {names[lit]}"
	aria-valuenow={lit}
	onpointerdown={down}
	onpointermove={move}
	onpointerup={() => (drag = null)}
	onpointercancel={() => (drag = null)}
	onkeydown={key}
>
	{#each axes as a, k (k)}
		<line x1={S / 2} y1={S / 2} x2={a.x} y2={a.y} class="axis" />
	{/each}
	{#each pts as p (p.i)}
		<circle cx={p.x} cy={p.y} {r} class="code" style:opacity={0.45 + 0.35 * (1 - (p.z + 1) / 2)} />
		{#if labelAll}
			<text x={p.x + 6} y={p.y - 5} class={['lab', p.i === lit && 'on']}>{names[p.i]}</text>
		{/if}
	{/each}
	<circle cx={litPt.x} cy={litPt.y} r={r + 4.5} class="ring" />
	{#if yPt}
		<line x1={yPt.x} y1={yPt.y} x2={litPt.x} y2={litPt.y} class="gap" />
		<circle cx={yPt.x} cy={yPt.y} r={2.6} class="y" />
	{/if}
	{#if !labelAll}
		<text x={litPt.x + r + 7} y={litPt.y + 3} class="lab on">{names[lit]}</text>
	{/if}
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: 100%;
		touch-action: none;
		cursor: grab;
		font-family: var(--font-mono);
		overflow: visible;
	}
	svg:active {
		cursor: grabbing;
	}
	.axis {
		stroke: var(--color-edge);
		stroke-width: 0.8;
	}
	.code {
		fill: var(--color-ink-3);
	}
	.ring {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1;
	}
	.y {
		fill: var(--color-ink);
	}
	.gap {
		stroke: var(--color-ink);
		stroke-width: 0.8;
	}
	.lab {
		font-size: 9px;
		fill: var(--color-ink-3);
	}
	.lab.on {
		fill: var(--color-ink);
	}
</style>
