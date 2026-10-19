<script lang="ts" module>
	export interface Series {
		id: string;
		label: string;
		/** Grayscale level 0…1 of the line. */
		tone: number;
		/** Canvas dash pattern, '' for solid. */
		dash: string;
		xs: ArrayLike<number>;
		ys: ArrayLike<number>;
		/** Thicker line for the series under study. */
		emphasis?: boolean;
		/** A recorded run drawn faintly behind the live ones, for the live run to race. */
		ghost?: boolean;
	}

	export interface ReferenceLine {
		y: number;
		label: string;
	}
</script>

<script lang="ts">
	/**
	 * A quiet canvas line chart: one y-axis, recessive grid, direct labels at
	 * line ends, crosshair + tooltip on hover. Identity is carried by tone,
	 * dash and label, never colour.
	 */
	let {
		series,
		version = 0,
		xMax,
		yMin,
		yMax,
		log = false,
		yTicks,
		formatY = (v: number) => v.toFixed(2),
		formatX = (v: number) => String(Math.round(v)),
		xLabel = 'Step',
		reference,
		height = 240,
		label
	}: {
		series: Series[];
		version?: number;
		xMax: number;
		yMin: number;
		yMax: number;
		log?: boolean;
		yTicks: number[];
		formatY?: (v: number) => string;
		formatX?: (v: number) => string;
		xLabel?: string;
		reference?: ReferenceLine;
		height?: number;
		label: string;
	} = $props();

	let width = $state(0);
	/** End labels need a right margin; on phones the tooltip and runs table carry identity instead. */
	const narrow = $derived(width > 0 && width < 520);
	const PAD = $derived({ l: 48, r: narrow ? 26 : 150, t: 12, b: 44 });
	let hoverX = $state<number | null>(null);

	const toneHex = (t: number) => {
		const v = Math.round(70 + t * (245 - 70));
		return `rgb(${v} ${v} ${v})`;
	};

	const plotW = $derived(Math.max(10, width - PAD.l - PAD.r));
	const plotH = $derived(height - PAD.t - PAD.b);
	const ty = (v: number) => {
		const lo = log ? Math.log10(yMin) : yMin;
		const hi = log ? Math.log10(yMax) : yMax;
		const c = log ? Math.log10(Math.max(v, yMin)) : v;
		const f = (Math.min(Math.max(c, lo), hi) - lo) / (hi - lo);
		return PAD.t + plotH * (1 - f);
	};
	const tx = (x: number) => PAD.l + (plotW * x) / Math.max(1, xMax);

	/** Index of the last sample with xs[i] ≤ x (binary search). */
	function lastAtOrBefore(xs: ArrayLike<number>, x: number): number {
		let lo = 0;
		let hi = xs.length - 1;
		if (hi < 0 || xs[0] > x) return -1;
		while (lo < hi) {
			const mid = (lo + hi + 1) >> 1;
			if (xs[mid] <= x) lo = mid;
			else hi = mid - 1;
		}
		return lo;
	}

	const xTicks = $derived.by(() => {
		const raw = xMax / 5;
		const mag = Math.pow(10, Math.floor(Math.log10(Math.max(raw, 1e-12))));
		const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? raw;
		const out: number[] = [];
		for (let v = 0; v <= xMax + 1e-9; v += step) out.push(v);
		return out;
	});

	/** End labels, nudged apart so they never collide. Ghosts are labelled only while nothing is live. */
	const endLabels = $derived.by(() => {
		void version;
		const live = series.some((s) => !s.ghost && s.xs.length > 0);
		const items = series
			.filter((s) => s.xs.length > 0 && !!s.ghost !== live)
			.map((s) => ({
				ghost: !!s.ghost,
				id: s.id,
				label: s.label,
				tone: s.tone,
				value: s.ys[s.ys.length - 1],
				x: tx(s.xs[s.xs.length - 1]),
				y: ty(s.ys[s.ys.length - 1])
			}))
			.sort((a, b) => a.y - b.y);
		for (let i = 1; i < items.length; i++)
			if (items[i].y - items[i - 1].y < 16) items[i].y = items[i - 1].y + 16;
		const overflow = items.length ? items[items.length - 1].y - (PAD.t + plotH) : 0;
		if (overflow > 0) for (const it of items) it.y -= overflow;
		return items;
	});

	const hover = $derived.by(() => {
		void version;
		if (hoverX === null) return null;
		const x = ((hoverX - PAD.l) / plotW) * xMax;
		if (x < 0 || x > xMax) return null;
		const rows = series
			.filter((s) => !s.ghost || !series.some((o) => !o.ghost && o.id === s.id && o.xs.length > 0))
			.map((s) => {
				const i = lastAtOrBefore(s.xs, x);
				return i < 0
					? null
					: {
							id: s.id + (s.ghost ? ':ghost' : ''),
							label: s.label + (s.ghost ? ' (recorded)' : ''),
							tone: s.tone,
							value: s.ys[i],
							at: s.xs[i]
						};
			})
			.filter((r) => r !== null)
			.sort((a, b) => b.value - a.value);
		if (!rows.length) return null;
		return { x, px: tx(x), rows, at: Math.max(...rows.map((r) => r.at)) };
	});

	function draw(canvas: HTMLCanvasElement) {
		void version;
		const w = width;
		if (!w) return;
		const dpr = window.devicePixelRatio || 1;
		canvas.width = Math.round(w * dpr);
		canvas.height = Math.round(height * dpr);
		const g = canvas.getContext('2d');
		if (!g) return;
		g.setTransform(dpr, 0, 0, dpr, 0, 0);
		g.clearRect(0, 0, w, height);

		// grid
		g.font = '12px "Geist Variable", system-ui, sans-serif';
		g.textBaseline = 'middle';
		g.lineWidth = 1;
		for (const t of yTicks) {
			const y = Math.round(ty(t)) + 0.5;
			g.strokeStyle = '#232323';
			g.beginPath();
			g.moveTo(PAD.l, y);
			g.lineTo(PAD.l + plotW, y);
			g.stroke();
			g.fillStyle = '#777777';
			g.textAlign = 'right';
			g.fillText(formatY(t), PAD.l - 8, y);
		}
		g.textAlign = 'center';
		g.textBaseline = 'top';
		for (const t of xTicks) {
			const x = Math.round(tx(t)) + 0.5;
			g.strokeStyle = '#1c1c1c';
			g.beginPath();
			g.moveTo(x, PAD.t);
			g.lineTo(x, PAD.t + plotH);
			g.stroke();
			g.fillStyle = '#777777';
			g.fillText(formatX(t), x, PAD.t + plotH + 8);
		}
		// baseline
		g.strokeStyle = '#555555';
		g.beginPath();
		g.moveTo(PAD.l, Math.round(PAD.t + plotH) + 0.5);
		g.lineTo(PAD.l + plotW, Math.round(PAD.t + plotH) + 0.5);
		g.stroke();

		if (reference) {
			const y = Math.round(ty(reference.y)) + 0.5;
			g.setLineDash([2, 4]);
			g.strokeStyle = '#555555';
			g.beginPath();
			g.moveTo(PAD.l, y);
			g.lineTo(PAD.l + plotW, y);
			g.stroke();
			g.setLineDash([]);
			// label below the line: baselines hover just above chance, not below it
			g.fillStyle = '#777777';
			g.textAlign = 'right';
			g.textBaseline = 'top';
			g.fillText(reference.label, PAD.l + plotW - 6, y + 4);
		}

		// series, dimmest first so the brightest sits on top
		const ordered = [...series].sort((a, b) => a.tone - b.tone);
		g.save();
		g.beginPath();
		g.rect(PAD.l, PAD.t - 2, plotW + 2, plotH + 4);
		g.clip();
		for (const s of ordered) {
			const n = s.xs.length;
			if (!n) continue;
			g.globalAlpha = s.ghost ? 0.3 : 1;
			g.strokeStyle = toneHex(s.tone);
			g.lineWidth = s.emphasis ? 2.25 : 1.5;
			g.setLineDash(s.dash ? s.dash.split(' ').map(Number) : []);
			g.lineJoin = 'round';
			g.beginPath();
			// thin to ~2 points per pixel
			const stride = Math.max(1, Math.floor(n / (plotW * 2)));
			for (let i = 0; i < n; i += stride) {
				const x = tx(s.xs[i]);
				const y = ty(s.ys[i]);
				if (i === 0) g.moveTo(x, y);
				else g.lineTo(x, y);
			}
			g.lineTo(tx(s.xs[n - 1]), ty(s.ys[n - 1]));
			g.stroke();
		}
		g.globalAlpha = 1;
		g.restore();
		g.setLineDash([]);

		// end markers
		for (const s of ordered) {
			const n = s.xs.length;
			if (!n || s.ghost) continue;
			g.fillStyle = toneHex(s.tone);
			g.beginPath();
			g.arc(tx(s.xs[n - 1]), ty(s.ys[n - 1]), s.emphasis ? 3 : 2.2, 0, Math.PI * 2);
			g.fill();
		}

		if (hover) {
			const x = Math.round(hover.px) + 0.5;
			g.strokeStyle = '#a6a6a6';
			g.lineWidth = 1;
			g.beginPath();
			g.moveTo(x, PAD.t);
			g.lineTo(x, PAD.t + plotH);
			g.stroke();
		}
	}
</script>

<figure
	class="chart"
	style:height="{height}px"
	style:--pad-r="{PAD.r}px"
	bind:clientWidth={width}
	aria-label={label}
>
	<canvas
		{@attach draw}
		style:width="{width}px"
		style:height="{height}px"
		onpointermove={(e) => {
			const r = e.currentTarget.getBoundingClientRect();
			hoverX = e.clientX - r.left;
		}}
		onpointerleave={() => (hoverX = null)}
	></canvas>

	{#each narrow ? [] : endLabels as l (l.id)}
		<span
			class="end num"
			class:ghost={l.ghost}
			style:top="{l.y}px"
			style:left="{l.x + 8}px"
			style:color={toneHex(l.tone)}
		>
			{l.label}
		</span>
	{/each}

	<span class="xlabel" style:left="{PAD.l + plotW / 2}px">{xLabel}</span>

	{#if hover}
		<div class="tip" style:left="{Math.min(hover.px + 12, width - 232)}px">
			<div class="tip-head num">{xLabel} {formatX(hover.at)}</div>
			{#each hover.rows as r (r.id)}
				<div class="tip-row">
					<span class="swatch" style:background={toneHex(r.tone)}></span>
					<span class="name">{r.label}</span>
					<span class="val num">{formatY(r.value)}</span>
				</div>
			{/each}
		</div>
	{/if}
</figure>

<style>
	.chart {
		position: relative;
		margin: 0;
		width: 100%;
		user-select: none;
	}
	canvas {
		display: block;
		cursor: crosshair;
	}
	.end {
		position: absolute;
		transform: translateY(-50%);
		font-size: var(--text-xs);
		white-space: nowrap;
		pointer-events: none;
	}
	.end.ghost {
		opacity: 0.55;
	}
	.xlabel {
		position: absolute;
		bottom: 2px;
		transform: translateX(-50%);
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		pointer-events: none;
	}
	.tip {
		position: absolute;
		top: 8px;
		width: 220px;
		padding: 8px 10px;
		background: rgb(21 21 21 / 0.96);
		border: 1px solid var(--color-rule);
		border-radius: var(--radius-ui);
		pointer-events: none;
		font-size: var(--text-xs);
	}
	.tip-head {
		color: var(--color-ink-2);
		margin-bottom: 4px;
	}
	.tip-row {
		display: grid;
		grid-template-columns: 10px 1fr auto;
		align-items: center;
		gap: 6px;
		line-height: 1.6;
	}
	.swatch {
		width: 10px;
		height: 2px;
	}
	.name {
		color: var(--color-ink-2);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.val {
		color: var(--color-ink);
	}
</style>
