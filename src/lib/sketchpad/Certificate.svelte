<script lang="ts">
	import { fmtMargin, rowLabel, type Cert } from './pad.svelte.ts';
	import { GRID, theme } from './theme.svelte.ts';

	interface Props {
		cert: Cert;
		/** the GPU as the browser names it */
		device: string | null;
		oncheck?: () => void;
		/** can the table be checked now (the model is loaded and idle) */
		canCheck: boolean;
		/** the rows a run has read and the one it read last: the run's walk on the table */
		walk?: { current: number; visited: Set<number> } | null;
	}

	let { cert, device, oncheck, canCheck, walk = null }: Props = $props();

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
		void walk;
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
		const tone = GRID[theme.current];
		// during a run, the rows it has not read step back and the ones it has read stand out
		const w = walk && walk.visited.size ? walk : null;
		for (let i = 0; i < cert.rows; i++) {
			const m = cert.margins[i];
			ctx.globalAlpha = w && !w.visited.has(i) ? 0.3 : 1;
			if (Number.isNaN(m)) {
				ctx.fillStyle = tone.idle;
				ctx.fillRect(g.x[i], g.y[i], s, s);
			} else if (m > 0) {
				ctx.fillStyle = i === h || (w && w.visited.has(i)) ? tone.hot : tone.pass;
				ctx.fillRect(g.x[i], g.y[i], s, s);
			} else {
				// a failing row is a hole: hollow, and ringed when pointed at
				ctx.strokeStyle = tone.fail;
				ctx.lineWidth = 1;
				ctx.clearRect(g.x[i] - 0.5, g.y[i] - 0.5, s + 1, s + 1);
				ctx.strokeRect(g.x[i] + 0.5, g.y[i] + 0.5, s - 1, s - 1);
				if (i === h) ctx.strokeRect(g.x[i] - 1.5, g.y[i] - 1.5, s + 3, s + 3);
			}
		}
		ctx.globalAlpha = 1;
		if (w && w.current >= 0 && w.current < cert.rows) {
			const i = w.current;
			ctx.strokeStyle = tone.hot;
			ctx.lineWidth = 1;
			ctx.strokeRect(g.x[i] - 1.5, g.y[i] - 1.5, s + 3, s + 3);
		}
		if (h !== null && Number.isNaN(cert.margins[h])) {
			ctx.fillStyle = tone.pass;
			ctx.globalAlpha = 0.5;
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
	const stamp = (iso: string) =>
		new Date(iso).toLocaleString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
	const readout = $derived.by(() => {
		if (hover === null) return null;
		const m = cert.margins[hover];
		return {
			label: rowLabel(cert.kind, hover),
			margin: Number.isNaN(m) ? 'not checked yet' : `margin ${fmtMargin(m)}`
		};
	});
</script>

<section class="sp-panel cert" aria-label="Certificate">
	<div class="sp-cap">
		<span class="sp-title"
			>The table
			{#if cert.status === 'running'}
				<span class="state num">checking {fmt(cert.checked)} of {fmt(cert.rows)}</span>
			{:else if cert.status === 'shipped' && cert.spot?.running}
				<span class="state num">spot check {fmt(cert.spot.checked)} of {fmt(cert.spot.rows)}</span>
			{:else if cert.status === 'none'}
				<span class="state">not checked yet</span>
			{/if}</span
		>
		<span class="sp-sub">every view the model can meet, each one checked</span>
	</div>

	<div class="sp-body body">
		<div class="headline">
			<span
				class="big num"
				class:dim={cert.status !== 'done' && cert.status !== 'cached' && cert.status !== 'shipped'}
			>
				{cert.checked ? fmtMargin(cert.minMargin) : '–'}
			</span>
			<span class="cap"
				>{cert.status === 'running'
					? 'lowest margin so far'
					: cert.status === 'shipped'
						? 'lowest margin'
						: 'lowest margin on this device'}</span
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
			{:else if walk && walk.visited.size}
				This run has read {fmt(walk.visited.size)} of the {fmt(cert.rows)} views.
			{:else if cert.status === 'none'}
				{fmt(cert.rows)} views: every strip the model can meet.
			{:else}
				{fmt(cert.pass)} of {fmt(cert.status === 'running' ? cert.checked : cert.rows)} pass{#if cert.status !== 'shipped'}
					· {cert.seconds.toFixed(0)} s{/if}
			{/if}
		</p>
	</div>

	<div class="sp-foot">
		{#if cert.status === 'cached' || cert.status === 'done'}
			<p>
				Every view checked on this device{when ? `, ${when}` : ''}{device ? ` (${device})` : ''}.
				{#if oncheck}<button class="link" disabled={!canCheck} onclick={oncheck}>Check again</button
					>{/if}
			</p>
		{:else if cert.status === 'shipped' && cert.shippedFrom}
			{@const sp = cert.spot}
			<p>
				Shipped with the model, checked on {cert.shippedFrom.device}, {stamp(
					cert.shippedFrom.when
				)}.
				{#if sp && sp.checked}
					Its {fmt(sp.rows)} weakest views {sp.running
						? `are being checked here (${fmt(sp.pass)} of ${fmt(sp.checked)} pass)`
						: sp.pass === sp.checked
							? `pass here too (lowest ${fmtMargin(sp.min)})`
							: `: ${fmt(sp.checked - sp.pass)} fail here`}.
				{/if}
				{#if oncheck}<button class="link" disabled={!canCheck} onclick={oncheck}
						>Check every view here</button
					>{/if}
			</p>
		{/if}
		{#if cert.failures.length}
			<div class="fails">
				<p class="k">
					{cert.failures.length} failing {cert.failures.length === 1 ? 'row' : 'rows'}
				</p>
				<ul>
					{#each cert.failures.slice(0, 6) as f (f.index)}
						<li
							class="mono"
							onpointerenter={() => (hover = f.index)}
							onpointerleave={() => (hover = null)}
						>
							{f.label}<span class="dim">, wrote {spaced(f.got)}</span>
						</li>
					{/each}
				</ul>
				{#if cert.failures.length > 6}<p class="dim small">
						and {cert.failures.length - 6} more
					</p>{/if}
			</div>
		{/if}
	</div>
</section>

<style>
	.state {
		margin-left: 8px;
		color: var(--color-ink-3);
	}
	.body {
		place-items: start;
		align-content: start;
		justify-content: stretch;
		width: 100%;
	}
	.headline {
		display: flex;
		align-items: baseline;
		gap: 10px;
		margin-bottom: 12px;
	}
	.big {
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.02em;
		line-height: 1;
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
	.k {
		color: var(--color-ink-2);
	}
	.link {
		border: 0;
		padding: 0;
		background: none;
		color: var(--color-ink-2);
		font: inherit;
		text-decoration: underline;
		text-underline-offset: 3px;
		text-decoration-color: var(--color-rule);
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
		margin-top: 8px;
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
