<script lang="ts">
	/** The margin over the whole run, the smallest per bucket so no dip is averaged away, drawn down to zero. */
	import { marginBuckets, type TraceStep } from './trace.ts';

	let {
		steps,
		step,
		off,
		offLabel = 'head off',
		onseek
	}: {
		steps: TraceStep[];
		step: number;
		off: boolean;
		offLabel?: string;
		onseek: (i: number) => void;
	} = $props();

	const W = 300;
	const H = 64;
	const PAD = 2;
	const buckets = $derived(marginBuckets(steps, 150));
	const max = $derived(Math.max(...buckets.map((b) => b.m)) * 1.15);
	const min = $derived(buckets.reduce((a, b) => (b.m < a.m ? b : a), buckets[0]));
	const sx = (i: number) => PAD + (i / Math.max(1, steps.length - 1)) * (W - 2 * PAD);
	const sy = (m: number) => H - 1 - (Math.max(0, m) / max) * (H - 8);
	const line = $derived(buckets.map((b, k) => `${k ? 'L' : 'M'}${sx(b.i)},${sy(b.m)}`).join(' '));

	function seek(e: PointerEvent & { currentTarget: SVGSVGElement }) {
		if (e.type === 'pointermove' && e.buttons !== 1) return;
		const box = e.currentTarget.getBoundingClientRect();
		const f = Math.max(0, Math.min(1, (e.clientX - box.left) / box.width));
		onseek(Math.round(f * (steps.length - 1)));
	}
</script>

<div class="trace">
	<div class="legend num">
		<span>margin, every step</span>
		<span class="quiet">smallest {min.m.toFixed(2)} at step {min.i + 1}</span>
	</div>
	<svg
		viewBox="0 0 {W} {H}"
		preserveAspectRatio="none"
		role="presentation"
		onpointerdown={seek}
		onpointermove={seek}
	>
		<line x1="0" x2={W} y1={sy(0)} y2={sy(0)} class="zero" />
		<path d={line} class={['m', off && 'off']} />
		<line x1={sx(step)} x2={sx(step)} y1="0" y2={H} class="head" />
	</svg>
	<div class="axis num">
		<span>0</span><span
			>{off ? `${offLabel}: no margin to show` : `${steps[step].margin.toFixed(2)} here`}</span
		>
	</div>
</div>

<style>
	.trace {
		display: grid;
		gap: 4px;
	}
	.legend,
	.axis {
		display: flex;
		justify-content: space-between;
		gap: 8px;
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.axis {
		color: var(--color-ink-3);
	}
	.quiet {
		color: var(--color-ink-3);
	}
	svg {
		display: block;
		width: 100%;
		height: 52px;
		cursor: pointer;
		touch-action: none;
	}
	.zero {
		stroke: var(--color-rule);
		stroke-width: 1;
		stroke-dasharray: 3 3;
		vector-effect: non-scaling-stroke;
	}
	.m {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1.2;
		vector-effect: non-scaling-stroke;
	}
	.m.off {
		stroke: var(--color-rule);
	}
	.head {
		stroke: var(--color-ink-2);
		stroke-width: 1;
		vector-effect: non-scaling-stroke;
	}
</style>
