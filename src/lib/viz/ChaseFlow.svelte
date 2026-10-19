<script lang="ts">
	/**
	 * DS-PA on pointer chasing with every token at once. Rows are tokens, grouped by
	 * linked list with each list's head on top; columns are rounds. Each state is a
	 * register showing the payload it holds, and curves show what it read from the
	 * round before, weighted by the learned option weight. A front sweeps the rounds
	 * so payloads can be seen climbing their lists, and the states the answer
	 * depends on (its backward cone) are lit.
	 */
	import { untrack } from 'svelte';
	import { CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
	import type { DiagramHead } from '#lib/engine/protocol.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import { backwardCone, flowEdges, flowGroups, heldPayloads } from './chaseFlow.ts';

	let {
		head,
		n,
		rounds,
		instance,
		probs = null,
		label = 'DS-PA reading a pointer-chasing example, every token and round'
	}: {
		head: DiagramHead;
		n: number;
		rounds: number;
		instance: ChaseInstance;
		/** The model's readout distribution over payloads, if known. */
		probs?: number[] | null;
		label?: string;
	} = $props();

	const Q = CHASE_QUERY_POS;

	const groups = $derived(flowGroups(instance));
	const held = $derived(heldPayloads(head, n, rounds, instance));
	const cone = $derived(backwardCone(head, n, rounds, Q));
	const edges = $derived(flowEdges(head, n, rounds, cone, 0.08));

	const answer = $derived(probs ? probs.indexOf(Math.max(...probs)) : held[rounds][Q]);
	const confidence = $derived(probs && answer !== null ? probs[answer] : null);

	// ── geometry ─────────────────────────────────────────────────────────────
	let width = $state(0);
	let height = $state(0);
	const PAD = $derived(
		width < 520
			? { top: 46, bottom: 22, left: 60, right: 58 }
			: { top: 46, bottom: 22, left: 92, right: 104 }
	);
	const CHIP = 12; // half a register's width, where lines attach
	const GROUP_GAP = 0.7;
	const geo = $derived.by(() => {
		const units = groups.reduce((s, g) => s + g.length, 0) - 1 + (groups.length - 1) * GROUP_GAP;
		const rowH = (height - PAD.top - PAD.bottom) / Math.max(1, units);
		/** Row centre per token; NaN for tokens not drawn. */
		const y: number[] = Array.from({ length: n }, () => NaN);
		let u = 0;
		groups.forEach((g, gi) => {
			if (gi) u += GROUP_GAP;
			for (const t of g) {
				y[t] = PAD.top + u * rowH;
				u += 1;
			}
		});
		const span = width - PAD.left - PAD.right;
		const x = Array.from({ length: rounds + 1 }, (_, r) => PAD.left + (r * span) / rounds);
		return { y, x, rowH, out: width - PAD.right + (width < 520 ? 34 : 62) };
	});

	// ── the sweep: a front crosses one round every STEP seconds ─────────────
	const STEP = 1.15;
	const HOLD = 2.8;
	const FADE = 0.7;
	let front = $state(Infinity);
	/** Highest round whose registers are shown; drives the HTML layer. */
	const shown = $derived(Math.floor(front));

	type P = [number, number];
	const bez = (a: P, b: P, t: number): P => {
		const mx = (a[0] + b[0]) / 2;
		const u = 1 - t;
		// control points (mx, a.y) and (mx, b.y): a smooth S between rounds
		const x = u * u * u * a[0] + 3 * u * u * t * mx + 3 * u * t * t * mx + t * t * t * b[0];
		const y = u * u * u * a[1] + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t * t * t * b[1];
		return [x, y];
	};

	/** Set up outside tracking: the loop reads state every frame and must not re-run the attachment. */
	const flow = (canvas: HTMLCanvasElement) => untrack(() => animate(canvas));

	function animate(canvas: HTMLCanvasElement) {
		const ctx = canvas.getContext('2d')!;
		const dpr = Math.min(window.devicePixelRatio || 1, 2);
		const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		// a soft round sprite for the moving pulses
		const sprite = document.createElement('canvas');
		sprite.width = sprite.height = 48;
		const sg = sprite.getContext('2d')!;
		const grad = sg.createRadialGradient(24, 24, 0, 24, 24, 24);
		grad.addColorStop(0, 'rgba(255,255,255,1)');
		grad.addColorStop(0.18, 'rgba(255,255,255,0.85)');
		grad.addColorStop(0.45, 'rgba(255,255,255,0.18)');
		grad.addColorStop(1, 'rgba(255,255,255,0)');
		sg.fillStyle = grad;
		sg.fillRect(0, 0, 48, 48);

		let visible = true;
		const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
		io.observe(canvas);

		function draw(f: number, fade: number) {
			const w = width;
			const h = height;
			if (w < 10 || h < 10) return;
			if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
				canvas.width = Math.round(w * dpr);
				canvas.height = Math.round(h * dpr);
			}
			ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
			ctx.clearRect(0, 0, w, h);
			const { x, y } = geo;
			const yTop = PAD.top - 18;
			const yBot = h - PAD.bottom + 8;

			// guides: round columns and token rows
			ctx.lineWidth = 1;
			for (let r = 0; r <= rounds; r++) {
				const reached = f >= r;
				ctx.strokeStyle = `rgba(255,255,255,${reached ? 0.07 : 0.035})`;
				ctx.beginPath();
				ctx.moveTo(x[r] + 0.5, yTop);
				ctx.lineTo(x[r] + 0.5, yBot);
				ctx.stroke();
			}
			ctx.strokeStyle = 'rgba(255,255,255,0.03)';
			for (const yy of y) {
				if (Number.isNaN(yy)) continue;
				ctx.beginPath();
				ctx.moveTo(x[0], Math.round(yy) + 0.5);
				ctx.lineTo(x[rounds], Math.round(yy) + 0.5);
				ctx.stroke();
			}

			// edges: faint before the front reaches them, drawn in as it passes
			const pulses: { p: P; lit: boolean; w: number }[] = [];
			for (const e of edges) {
				const y0 = y[e.from];
				const y1 = y[e.to];
				if (Number.isNaN(y0) || Number.isNaN(y1)) continue;
				const a: P = [x[e.r - 1] + CHIP + 2, y0];
				const b: P = [x[e.r] - CHIP - 2, y1];
				const p = Math.max(0, Math.min(1, f - (e.r - 1))) * (1 - fade);
				const grey = e.lit ? 242 : 150;
				const strength = e.lit ? 0.3 + 0.7 * e.w : 0.1 + 0.35 * e.w;
				ctx.setLineDash(e.kind === 'carry' ? [3, 4] : e.kind === 'exchange' ? [1, 3] : []);
				ctx.lineWidth = e.lit ? 0.9 + 1.5 * e.w : 0.7 + 0.6 * e.w;
				ctx.strokeStyle = `rgba(${grey},${grey},${grey},${(0.07 + 0.93 * p) * strength})`;
				// the lit path glows once the front has passed
				const glow = e.lit && p > 0.02;
				if (glow) {
					ctx.shadowColor = `rgba(255,255,255,${0.55 * p})`;
					ctx.shadowBlur = 9;
				}
				ctx.beginPath();
				ctx.moveTo(a[0], a[1]);
				const mx = (a[0] + b[0]) / 2;
				ctx.bezierCurveTo(mx, a[1], mx, b[1], b[0], b[1]);
				ctx.stroke();
				if (glow) ctx.shadowBlur = 0;
				if (p > 0 && p < 1 && fade === 0) pulses.push({ p: bez(a, b, p), lit: e.lit, w: e.w });
			}
			ctx.setLineDash([]);

			// the readout leg
			const yq = y[Q];
			if (!Number.isNaN(yq)) {
				const p = Math.max(0, Math.min(1, f - rounds)) * (1 - fade);
				const a: P = [x[rounds] + CHIP + 2, yq];
				const b: P = [geo.out - 22, yq];
				ctx.lineWidth = 2;
				ctx.strokeStyle = `rgba(242,242,242,${0.07 + 0.93 * p})`;
				ctx.shadowColor = `rgba(255,255,255,${0.55 * p})`;
				ctx.shadowBlur = 9;
				ctx.beginPath();
				ctx.moveTo(a[0], a[1]);
				ctx.lineTo(b[0], b[1]);
				ctx.stroke();
				ctx.shadowBlur = 0;
				if (p > 0 && p < 1 && fade === 0)
					pulses.push({ p: [a[0] + (b[0] - a[0]) * p, yq], lit: true, w: 1 });
			}

			// pulses at the front
			ctx.globalCompositeOperation = 'lighter';
			for (const q of pulses) {
				const s = q.lit ? 14 + 10 * q.w : 7 + 4 * q.w;
				ctx.globalAlpha = q.lit ? 0.95 : 0.35;
				ctx.drawImage(sprite, q.p[0] - s / 2, q.p[1] - s / 2, s, s);
			}
			ctx.globalAlpha = 1;
			ctx.globalCompositeOperation = 'source-over';
		}

		let raf = 0;
		let t0 = performance.now();
		let fadeAt = -1;
		const loop = () => {
			raf = requestAnimationFrame(loop);
			if (!visible || document.hidden) {
				t0 = performance.now() - (Number.isFinite(front) ? front * STEP * 1000 : 0);
				return;
			}
			const s = (performance.now() - t0) / 1000;
			const travel = (rounds + 1) * STEP;
			let fade = 0;
			let f = s / STEP;
			if (s > travel + HOLD) {
				fade = Math.min(1, (s - travel - HOLD) / FADE);
				f = rounds + 1;
				if (fadeAt < 0) fadeAt = s;
			}
			if (s > travel + HOLD + FADE + 0.35) {
				t0 = performance.now();
				fadeAt = -1;
				f = 0;
				fade = 0;
			}
			const next = fade > 0 ? -1 : f;
			if (Math.floor(next) !== Math.floor(front)) front = next;
			draw(f, fade);
		};
		if (reduced) {
			front = rounds + 1;
			const ro = new ResizeObserver(() => draw(rounds + 1, 0));
			ro.observe(canvas);
			return () => {
				ro.disconnect();
				io.disconnect();
			};
		}
		front = 0;
		loop();
		return () => {
			cancelAnimationFrame(raf);
			io.disconnect();
		};
	}

	const rowLabel = (t: number) => {
		if (t === Q) return { id: 'q', ptr: String(instance.start) };
		if (t === 0) return { id: 'BOS', ptr: '' };
		const nd = instance.nodes[t - 1];
		return { id: String(nd.id), ptr: nd.pointer === nd.id ? '' : String(nd.pointer) };
	};
</script>

<div class="flow" role="img" aria-label={label} bind:clientWidth={width} bind:clientHeight={height}>
	<canvas {@attach flow}></canvas>
	{#if width > 0}
		{#each geo.x as cx, r (r)}
			<span class="col" class:on={shown >= r} style:left="{cx}px">
				<MathTex tex={r === 0 ? 'v' : `\\Phi^{${r}}`} />
			</span>
		{/each}
		<span class="col on" style:left="{geo.out}px" class:dim={shown <= rounds}
			><MathTex tex="\hat y" /></span
		>

		{#each groups.flat() as t (t)}
			{@const yy = geo.y[t]}
			{@const l = rowLabel(t)}
			<span
				class="row"
				class:query={t === Q}
				class:bos={t === 0}
				style:top="{yy}px"
				style:right="{width - geo.x[0] + 22}px"
			>
				{#if t === Q}<MathTex tex="q" />{:else}{l.id}{/if}{#if l.ptr}<i>→{l.ptr}</i>{/if}
			</span>
			{#each held as col, r (r)}
				{@const v = col[t]}
				<span
					class="reg num"
					class:lit={cone[r]?.has(t)}
					class:answer={t === Q && r === rounds}
					class:on={r === 0 || shown >= r}
					style:left="{geo.x[r]}px"
					style:top="{yy}px">{v ?? '·'}</span
				>
			{/each}
		{/each}

		{#if answer !== null}
			<span class="out" class:on={shown > rounds} style:left="{geo.out}px" style:top="{geo.y[Q]}px">
				<b class="num">{answer}</b>
				{#if confidence !== null}<small class="num">{(confidence * 100).toFixed(1)}%</small>{/if}
			</span>
		{/if}
	{/if}
</div>

<style>
	.flow {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 300px;
		overflow: hidden;
	}
	canvas {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.col {
		position: absolute;
		top: 10px;
		transform: translateX(-50%);
		font-size: 15px;
		color: var(--color-ink-3);
		transition: color 300ms ease;
	}
	.col.on {
		color: var(--color-ink);
	}
	.col.dim {
		color: var(--color-ink-3);
	}
	.row {
		position: absolute;
		transform: translateY(-50%);
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		white-space: nowrap;
	}
	.row i {
		margin-left: 3px;
		font-style: normal;
		color: var(--color-ink-3);
	}
	.row.query {
		color: var(--color-ink);
		font-size: 15px;
	}
	.row.bos {
		color: var(--color-ink-3);
		font-size: 10px;
	}
	.reg {
		position: absolute;
		display: grid;
		place-items: center;
		width: 22px;
		height: 18px;
		transform: translate(-50%, -50%) scale(0.85);
		border-radius: 4px;
		background: #161616;
		color: var(--color-ink-3);
		font-size: 11px;
		opacity: 0.35;
		transition:
			opacity 360ms ease,
			transform 360ms ease,
			background 360ms ease,
			color 360ms ease;
	}
	.reg.on {
		opacity: 1;
		transform: translate(-50%, -50%);
	}
	.reg.lit.on {
		background: #2c2c2c;
		color: var(--color-ink);
	}
	.reg.answer.on {
		background: var(--color-ink);
		color: var(--color-void);
		font-weight: 600;
	}
	.out {
		position: absolute;
		display: grid;
		justify-items: center;
		gap: 2px;
		transform: translate(-50%, -14px);
		opacity: 0;
		transition: opacity 400ms ease;
	}
	.out.on {
		opacity: 1;
	}
	.out b {
		display: grid;
		place-items: center;
		width: 30px;
		height: 26px;
		border-radius: 5px;
		background: var(--color-ink);
		color: var(--color-void);
		font-size: 15px;
		box-shadow: 0 0 22px 2px rgb(255 255 255 / 0.25);
	}
	.out small {
		font-size: 10px;
		color: var(--color-ink-3);
	}
	@media (prefers-reduced-motion: reduce) {
		.reg,
		.out,
		.col {
			transition: none;
		}
	}
</style>
