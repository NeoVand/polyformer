<script lang="ts">
	import { fmtMargin, rowLabel, type Cert } from './pad.svelte.ts';

	interface Props {
		cert: Cert;
		/** the GPU as the browser names it */
		device: string | null;
		oncheck?: () => void;
		/** can the table be checked now (the model is loaded and idle) */
		canCheck: boolean;
	}

	let { cert, device, oncheck, canCheck }: Props = $props();

	let canvas: HTMLCanvasElement | null = null;
	let width = $state(240);
	let hover = $state<number | null>(null);

	/** The grid: the adder's 242 rows as two 11 x 11 blocks (carry blank, carry 1; top digit down, bottom across);
	 * the multiplier's 1,553 rows in op groups (MUL, ADD, ADZ, then FLS and NXT). */
	const grid = $derived.by(() => {
		const n = cert.rows;
		const x = new Float32Array(n);
		const y = new Float32Array(n);
		if (cert.kind === 'add') {
			const size = 8;
			const pitch = 10;
			const block = 11 * pitch + 8;
			for (let i = 0; i < n; i++) {
				const c = Math.floor(i / 121);
				x[i] = c * block + (i % 11) * pitch;
				y[i] = Math.floor((i % 121) / 11) * pitch;
			}
			return { x, y, size, w: 2 * block - 8 - (pitch - size), h: 11 * pitch - (pitch - size) };
		}
		const size = 4;
		const pitch = 5;
		const cols = Math.max(20, Math.floor((width + 1) / pitch));
		const groups: [number, number][] = [
			[0, 1100],
			[1100, 1320],
			[1320, 1540],
			[1540, 1553]
		];
		let top = 0;
		for (const [a, b] of groups) {
			for (let i = a; i < b; i++) {
				// FLS (2 rows) and NXT (11) share the last line, one cell apart
				const k = i - a + (a === 1540 && i >= 1542 ? 1 : 0);
				x[i] = (k % cols) * pitch;
				y[i] = top + Math.floor(k / cols) * pitch;
			}
			const k = b - a + (a === 1540 ? 1 : 0);
			top += Math.ceil(k / cols) * pitch + 4;
		}
		return { x, y, size, w: cols * pitch - 1, h: top - 4 - 1 };
	});

	/** the grid's width follows its column */
	function measure(box: HTMLDivElement) {
		const ro = new ResizeObserver(() => (width = box.clientWidth));
		ro.observe(box);
		return () => ro.disconnect();
	}

	/** one cell per row: filled when it passes, hollow when it fails, dark until checked */
	function paint(el: HTMLCanvasElement) {
		canvas = el;
		void cert.version;
		const g = grid;
		const h = hover;
		const dpr = Math.max(1, globalThis.devicePixelRatio || 1);
		el.width = Math.round(g.w * dpr);
		el.height = Math.round(g.h * dpr);
		el.style.width = `${g.w}px`;
		el.style.height = `${g.h}px`;
		const ctx = el.getContext('2d')!;
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
		ctx.clearRect(0, 0, g.w, g.h);
		const s = g.size;
		for (let i = 0; i < cert.rows; i++) {
			const m = cert.margins[i];
			if (Number.isNaN(m)) {
				ctx.fillStyle = '#1c1c1c';
				ctx.fillRect(g.x[i], g.y[i], s, s);
			} else if (m > 0) {
				ctx.fillStyle = i === h ? '#ffffff' : '#c8c8c8';
				ctx.fillRect(g.x[i], g.y[i], s, s);
			} else {
				// a failing row is a hole: hollow, and ringed when pointed at
				ctx.strokeStyle = '#f5f5f5';
				ctx.lineWidth = 1;
				ctx.clearRect(g.x[i] - 0.5, g.y[i] - 0.5, s + 1, s + 1);
				ctx.strokeRect(g.x[i] + 0.5, g.y[i] + 0.5, s - 1, s - 1);
				if (i === h) ctx.strokeRect(g.x[i] - 1.5, g.y[i] - 1.5, s + 3, s + 3);
			}
		}
		if (h !== null && Number.isNaN(cert.margins[h])) {
			ctx.fillStyle = '#4a4a4a';
			ctx.fillRect(g.x[h], g.y[h], s, s);
		}
	}

	function onpointermove(e: PointerEvent) {
		if (!canvas) return;
		const r = canvas.getBoundingClientRect();
		const px = e.clientX - r.left;
		const py = e.clientY - r.top;
		const g = grid;
		const pad = (g.size === 4 ? 1 : 2) / 2;
		let found: number | null = null;
		for (let i = 0; i < cert.rows; i++)
			if (
				px >= g.x[i] - pad &&
				px < g.x[i] + g.size + pad &&
				py >= g.y[i] - pad &&
				py < g.y[i] + g.size + pad
			) {
				found = i;
				break;
			}
		hover = found;
	}

	const fmt = (n: number) => n.toLocaleString('en-US');
	/** the model's answer, spaced like the table's ("33A" -> "3 3 A") */
	const spaced = (g: string | null) => (g ? [...g].join(' ') : '?');
	const when = $derived(
		cert.when
			? new Date(cert.when).toLocaleString('en-GB', {
					day: 'numeric',
					month: 'short',
					hour: '2-digit',
					minute: '2-digit'
				})
			: null
	);
	const readout = $derived.by(() => {
		if (hover === null) return null;
		const m = cert.margins[hover];
		return {
			label: rowLabel(cert.kind, hover),
			margin: Number.isNaN(m) ? 'not checked yet' : `margin ${fmtMargin(m)}`
		};
	});
</script>

<section class="cert" aria-label="Certificate">
	<div class="head">
		<span class="k">Certificate</span>
		{#if cert.status === 'running'}
			<span class="state num">checking {fmt(cert.checked)} of {fmt(cert.rows)}</span>
		{:else if cert.status === 'none'}
			<span class="state">not checked yet</span>
		{/if}
	</div>

	<div class="headline">
		<span class="big num" class:dim={cert.status !== 'done' && cert.status !== 'cached'}>
			{cert.checked ? fmtMargin(cert.minMargin) : '–'}
		</span>
		<span class="cap"
			>{cert.status === 'running' ? 'lowest margin so far' : 'lowest margin on this device'}</span
		>
	</div>

	<div class="grid" {@attach measure}>
		<canvas
			{@attach paint}
			{onpointermove}
			onpointerleave={() => (hover = null)}
			aria-label="One cell per table row; filled when it passes, hollow when it fails"
		></canvas>
	</div>

	<p class="line num">
		{#if readout}
			<span class="mono">{readout.label}</span><br /><span class="dim">{readout.margin}</span>
		{:else if cert.status === 'none'}
			{fmt(cert.rows)} views: every strip the model can meet.
		{:else}
			{fmt(cert.pass)} of {fmt(cert.status === 'running' ? cert.checked : cert.rows)} pass · {cert.seconds.toFixed(
				0
			)} s{#if device}<br /><span class="dim">{device}</span>{/if}
		{/if}
	</p>

	{#if cert.status === 'cached'}
		<p class="note">
			Checked on this device{when ? `, ${when}` : ''}, for these exact files.
			{#if oncheck}<button class="link" disabled={!canCheck} onclick={oncheck}>Check again</button
				>{/if}
		</p>
	{/if}

	{#if cert.failures.length}
		<div class="fails">
			<p class="k">{cert.failures.length} failing {cert.failures.length === 1 ? 'row' : 'rows'}</p>
			<ul>
				{#each cert.failures.slice(0, 12) as f (f.index)}
					<li
						class="mono"
						onpointerenter={() => (hover = f.index)}
						onpointerleave={() => (hover = null)}
					>
						{f.label}<span class="dim">, wrote {spaced(f.got)}</span>
					</li>
				{/each}
			</ul>
			{#if cert.failures.length > 12}<p class="dim small">
					and {cert.failures.length - 12} more
				</p>{/if}
		</div>
	{/if}
</section>

<style>
	.cert {
		font-size: var(--text-sm);
	}
	.head {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		color: var(--color-ink-3);
		font-size: var(--text-xs);
	}
	.k {
		color: var(--color-ink-2);
	}
	.headline {
		display: flex;
		align-items: baseline;
		gap: 10px;
		margin: 6px 0 12px;
	}
	.big {
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.02em;
		color: var(--color-ink);
		transition: color 250ms ease;
	}
	.big.dim {
		color: var(--color-ink-3);
	}
	.cap {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.grid {
		width: 100%;
	}
	canvas {
		display: block;
	}
	.line {
		margin-top: 10px;
		min-height: 2.9em;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.mono {
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		white-space: pre;
	}
	.dim {
		color: var(--color-ink-3);
	}
	.note {
		margin-top: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.link {
		border: 0;
		padding: 0;
		background: none;
		color: var(--color-ink-2);
		font: inherit;
		text-decoration: underline;
		text-underline-offset: 3px;
		text-decoration-color: #444;
		cursor: pointer;
		transition: color 250ms ease;
	}
	.link:hover:not(:disabled) {
		color: var(--color-ink);
	}
	.link:disabled {
		color: var(--color-ink-3);
		cursor: default;
	}
	.fails {
		margin-top: 12px;
	}
	.fails ul {
		margin-top: 4px;
		display: grid;
		gap: 2px;
	}
	.fails li {
		cursor: default;
		transition: color 250ms ease;
	}
	.fails li:hover {
		color: var(--color-ink);
	}
	.small {
		font-size: var(--text-2xs);
	}
</style>
