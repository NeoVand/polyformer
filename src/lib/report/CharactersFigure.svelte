<script lang="ts">
	/**
	 * Figure 9 of the report: Newton attention learns the characters of the group.
	 * (a) Every card's learned phase on four channels of a model trained on Match-3, one dot per
	 *     card. Shaded by the value of the nearest character, the 81 dots fall into three tight
	 *     clusters a third of a turn apart: the channel is that character, up to a rotation.
	 * (b) Across runs, accuracy against the number of distinct characters (of 40, counting each
	 *     conjugate pair once) the trained layer contains, with the line ½ + ½ · found/40.
	 * The wheels sit two by two so both panels are the same height.
	 */
	interface Example {
		char: number[];
		R: number;
		phase: (number | null)[];
	}
	interface Point {
		task: string;
		seed: number;
		found: number;
		of: number;
		bal: number;
	}
	let { examples, points }: { examples: Example[]; points: Point[] } = $props();

	const F = 4;
	const digits = (v: number) => Array.from({ length: F }, (_, a) => Math.floor(v / 3 ** a) % 3);
	const value = (c: number[], v: number) => digits(v).reduce((s, x, a) => s + x * c[a], 0) % 3;
	const WR = 34;

	// scatter geometry
	const SX = 34;
	const SW = 256;
	const SY = 8;
	const SH = 160;
	const sx = (found: number, of: number) => SX + (found / of) * SW;
	const sy = (bal: number) => SY + (1 - (bal - 0.5) / 0.5) * SH;
	const SHAPES: Record<string, string> = {
		zs3: 'circle',
		zs4: 'square',
		zs5: 'triangle',
		arity: 'diamond'
	};
	const NAMES: Record<string, string> = {
		zs3: 'Match-3',
		zs4: 'Match-4',
		zs5: 'Match-5',
		arity: 'Smallest arity'
	};
	const tasks = $derived([...new Set(points.map((p) => p.task))]);
	const marker = (shape: string, x: number, y: number, r = 4) =>
		shape === 'square'
			? `M${x - r * 0.85},${y - r * 0.85}h${r * 1.7}v${r * 1.7}h${-r * 1.7}z`
			: shape === 'triangle'
				? `M${x},${y - r}L${x + r},${y + r * 0.8}L${x - r},${y + r * 0.8}z`
				: shape === 'diamond'
					? `M${x},${y - r * 1.1}L${x + r},${y}L${x},${y + r * 1.1}L${x - r},${y}z`
					: `M${x - r},${y}a${r},${r} 0 1,0 ${r * 2},0a${r},${r} 0 1,0 ${-r * 2},0`;
</script>

<div class="chars">
	<div class="wheels">
		<p class="sub"><span class="tag">(a)</span> Learned phases of the 81 cards, four channels</p>
		<svg
			viewBox="0 0 200 210"
			role="img"
			aria-label="Learned phases of every card on four channels"
		>
			{#each examples.slice(0, 4) as ex, i (i)}
				{@const cx = 50 + (i % 2) * 100}
				{@const cy = 40 + Math.floor(i / 2) * 104}
				<circle class="unit" {cx} {cy} r={WR} />
				{#each ex.phase as ph, v (v)}
					{#if ph !== null}
						{@const k = value(ex.char, v)}
						{@const rr = WR - 1}
						<circle
							class="dot k{k}"
							cx={cx + rr * Math.cos(ph)}
							cy={cy - rr * Math.sin(ph)}
							r="2.2"
						/>
					{/if}
				{/each}
				<text class="cap" x={cx} y={cy + WR + 15} text-anchor="middle"
					>χ = ({ex.char.join(', ')})</text
				>
				<text class="cap dim" x={cx} y={cy + WR + 27} text-anchor="middle"
					>R = {ex.R.toFixed(3)}</text
				>
			{/each}
		</svg>
	</div>
	<div class="scatter">
		<p class="sub"><span class="tag">(b)</span> Accuracy against characters found</p>
		<svg viewBox="0 0 300 210" role="img" aria-label="Accuracy against characters found, every run">
			{#each [0.5, 0.75, 1] as t (t)}
				<line class="grid" x1={SX} x2={SX + SW} y1={sy(t)} y2={sy(t)} />
				<text class="tick" x={SX - 6} y={sy(t) + 3.5} text-anchor="end">{t * 100}%</text>
			{/each}
			{#each [0, 10, 20, 30, 40] as t (t)}
				<text class="tick" x={sx(t, 40)} y={SY + SH + 14} text-anchor="middle">{t}</text>
			{/each}
			<text class="axis" x={SX + SW / 2} y={SY + SH + 30} text-anchor="middle"
				>distinct characters found, of 40</text
			>
			<line class="law" x1={sx(0, 40)} y1={sy(0.5)} x2={sx(40, 40)} y2={sy(1)} />
			{#each points as p, i (i)}
				<path
					class="pt {p.task}"
					d={marker(SHAPES[p.task] ?? 'circle', sx(p.found, p.of), sy(p.bal))}
				/>
			{/each}
		</svg>
		<p class="legend">
			{#each tasks as t (t)}
				<span
					><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"
						><path class="pt {t}" d={marker(SHAPES[t] ?? 'circle', 6, 6, 4)} /></svg
					>{NAMES[t] ?? t}</span
				>
			{/each}
			<span
				><svg width="16" height="12" viewBox="0 0 16 12" aria-hidden="true"
					><line class="law" x1="1" x2="15" y1="6" y2="6" /></svg
				>½ + ½ · found / 40</span
			>
		</p>
	</div>
</div>

<style>
	.chars {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.45fr);
		gap: 18px 44px;
		align-items: start;
		/* grows with the page's reading size (15px on a laptop) */
		max-width: calc(var(--read, 15px) * 52);
	}
	.sub {
		margin: 0 0 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.tag {
		margin-right: 4px;
		font-family: 'KaTeX_Main', serif;
		color: var(--color-ink-3);
	}
	svg {
		width: 100%;
		height: auto;
		overflow: visible;
		font-family: var(--font-sans);
	}
	.unit {
		fill: none;
		stroke: #2c2c2c;
	}
	.dot {
		fill-opacity: 0.85;
	}
	.dot.k0 {
		fill: var(--color-ink);
	}
	.dot.k1 {
		fill: #8a8a8a;
	}
	.dot.k2 {
		fill: #4d4d4d;
	}
	.cap {
		font-family: 'KaTeX_Main', serif;
		font-size: 10px;
		fill: var(--color-ink-2);
	}
	.cap.dim {
		fill: var(--color-ink-3);
	}
	.grid {
		stroke: #1f1f1f;
	}
	.tick,
	.axis {
		font-size: 10px;
		fill: var(--color-ink-3);
	}
	.law {
		stroke: #5a5a5a;
		stroke-width: 1;
		stroke-dasharray: 3 3;
	}
	.legend .law {
		stroke: #8a8a8a;
	}
	.pt {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1.2;
	}
	.pt.zs4 {
		stroke: #b0b0b0;
	}
	.pt.zs5 {
		stroke: #808080;
	}
	.pt.arity {
		stroke: #d8d8d8;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
		margin: 2px 0 0 34px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 5px;
	}
	.legend svg {
		width: auto;
	}
	@media (max-width: 760px) {
		.chars {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
