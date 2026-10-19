<script lang="ts" module>
	export type Scale = 'weight' | 'signed';

	/** Grayscale level for a value: weights map 0 → black, max → white; signed maps 0 → mid-gray. */
	export function shade(v: number, max: number, scale: Scale): number {
		if (scale === 'weight') {
			const f = max > 0 ? Math.min(1, Math.max(0, v / max)) : 0;
			return Math.round(14 + Math.pow(f, 0.6) * (245 - 14));
		}
		const f = max > 0 ? Math.max(-1, Math.min(1, v / max)) : 0;
		return Math.round(52 + (f >= 0 ? f * (245 - 52) : f * (52 - 6)));
	}
</script>

<script lang="ts">
	/**
	 * A crisp grayscale matrix on canvas with a selected-cell bracket, an
	 * optional outlined diagonal, and hover readout. Rows run top to bottom.
	 */
	let {
		values,
		rows,
		cols,
		size = 240,
		scale = 'weight',
		max,
		selected = null,
		marks = [],
		diagonal = false,
		gap = 1,
		label,
		onhover,
		onpick
	}: {
		values: ArrayLike<number>;
		rows: number;
		cols: number;
		size?: number;
		scale?: Scale;
		/** Value mapped to full brightness; defaults to the max |value|. */
		max?: number;
		selected?: [number, number] | null;
		/** Cells to mark with a small dot (e.g. true SET pairs). */
		marks?: [number, number][];
		diagonal?: boolean;
		gap?: number;
		label: string;
		onhover?: (cell: [number, number] | null) => void;
		onpick?: (cell: [number, number]) => void;
	} = $props();

	const cell = $derived((size - gap) / Math.max(rows, cols));
	const width = $derived(cols * cell + gap);
	const height = $derived(rows * cell + gap);
	const top = $derived.by(() => {
		if (max !== undefined) return max;
		let m = 0;
		for (let i = 0; i < rows * cols; i++) m = Math.max(m, Math.abs(values[i] ?? 0));
		return m;
	});

	function draw(canvas: HTMLCanvasElement) {
		const dpr = window.devicePixelRatio || 1;
		canvas.width = Math.round(width * dpr);
		canvas.height = Math.round(height * dpr);
		const g = canvas.getContext('2d');
		if (!g) return;
		g.setTransform(dpr, 0, 0, dpr, 0, 0);
		g.fillStyle = '#080808';
		g.fillRect(0, 0, width, height);
		for (let r = 0; r < rows; r++) {
			for (let c = 0; c < cols; c++) {
				const s = shade(values[r * cols + c] ?? 0, top, scale);
				g.fillStyle = `rgb(${s} ${s} ${s})`;
				g.fillRect(gap + c * cell, gap + r * cell, cell - gap, cell - gap);
			}
		}
		if (diagonal) {
			g.strokeStyle = 'rgba(245,245,245,0.55)';
			g.lineWidth = 1;
			for (let d = 0; d < Math.min(rows, cols); d++)
				g.strokeRect(gap + d * cell + 0.5, gap + d * cell + 0.5, cell - gap - 1, cell - gap - 1);
		}
		for (const [r, c] of marks) {
			const s = shade(values[r * cols + c] ?? 0, top, scale);
			g.fillStyle = s > 140 ? '#080808' : '#f5f5f5';
			g.beginPath();
			g.arc(
				gap + c * cell + (cell - gap) / 2,
				gap + r * cell + (cell - gap) / 2,
				Math.max(1.5, cell * 0.09),
				0,
				Math.PI * 2
			);
			g.fill();
		}
	}

	function cellAt(e: PointerEvent): [number, number] | null {
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const c = Math.floor((e.clientX - rect.left - gap / 2) / cell);
		const r = Math.floor((e.clientY - rect.top - gap / 2) / cell);
		return r >= 0 && r < rows && c >= 0 && c < cols ? [r, c] : null;
	}
</script>

<div class="heat" style:width="{width}px" style:height="{height}px" role="img" aria-label={label}>
	<canvas
		{@attach draw}
		style:width="{width}px"
		style:height="{height}px"
		aria-hidden="true"
		onpointermove={(e) => onhover?.(cellAt(e))}
		onpointerleave={() => onhover?.(null)}
		onclick={(e) => {
			const at = cellAt(e as unknown as PointerEvent);
			if (at) onpick?.(at);
		}}
		class={{ pickable: !!onpick }}
	></canvas>
	{#if selected}
		<span
			class="sel"
			style:left="{gap / 2 + selected[1] * cell - 1}px"
			style:top="{gap / 2 + selected[0] * cell - 1}px"
			style:width="{cell + 2}px"
			style:height="{cell + 2}px"
		></span>
	{/if}
</div>

<style>
	.heat {
		position: relative;
		flex: none;
	}
	canvas {
		display: block;
		border-radius: 2px;
	}
	canvas.pickable {
		cursor: pointer;
	}
	.sel {
		position: absolute;
		border: 1.5px solid var(--color-ink);
		border-radius: 2px;
		box-shadow: 0 0 10px 1px rgb(255 255 255 / 0.35);
		pointer-events: none;
	}
</style>
