<script lang="ts">
	/**
	 * Held-out balanced accuracy through training, mean over seeds, one panel per task. The
	 * shape matters as much as the end point: a model of the right order sits at chance and
	 * then snaps, as the leap of a k-way relation predicts.
	 */
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import { pct } from '#lib/ui/format.ts';

	interface Row {
		task: string;
		model: string;
		curves?: [number, number][][];
	}
	let {
		rows,
		panels,
		models
	}: {
		rows: Row[];
		panels: { task: string; title: string }[];
		models: { id: string; label: string; tone: number; dash?: string; emphasis?: boolean }[];
	} = $props();

	function series(task: string): Series[] {
		const out: Series[] = [];
		for (const m of models) {
			const row = rows.find((r) => r.task === task && r.model === m.id);
			const curves = row?.curves?.filter((c) => c.length) ?? [];
			if (!curves.length) continue;
			const len = Math.min(...curves.map((c) => c.length));
			const xs = curves[0].slice(0, len).map((p) => p[0]);
			const ys = xs.map((_, i) => curves.reduce((s, c) => s + c[i][1], 0) / curves.length);
			out.push({
				id: m.id,
				label: m.label,
				tone: m.tone,
				dash: m.dash ?? '',
				emphasis: m.emphasis,
				xs,
				ys
			});
		}
		return out;
	}
	/** The axis ends where the plotted curves end, not at the longest run of the task. */
	const xMax = (task: string) =>
		Math.max(1, ...series(task).map((s) => s.xs[s.xs.length - 1] ?? 0));
</script>

<div class="curves" style:--n={panels.length}>
	{#each panels as p (p.task)}
		<div class="chart">
			<p class="sub">{p.title}</p>
			<LineChart
				label="{p.title}: held-out balanced accuracy through training"
				series={series(p.task)}
				xMax={xMax(p.task)}
				yMin={0.4}
				yMax={1}
				yTicks={[0.5, 0.75, 1]}
				formatY={(v) => pct(v, 0)}
				reference={{ y: 0.5, label: 'Chance' }}
				height={200}
			/>
		</div>
	{/each}
</div>
<p class="legend">
	{#each models.filter( (m) => panels.some( (p) => series(p.task).some((s) => s.id === m.id) ) ) as m (m.id)}
		<span
			><svg width="26" height="8" viewBox="0 0 26 8" aria-hidden="true"
				><line
					x1="1"
					x2="25"
					y1="4"
					y2="4"
					style:stroke="rgb({Math.round(m.tone * 242)}
					{Math.round(m.tone * 242)}
					{Math.round(m.tone * 242)})"
					stroke-width={m.emphasis ? 2.2 : 1.3}
					stroke-dasharray={m.dash || undefined}
				/></svg
			>{m.label}</span
		>
	{/each}
</p>

<style>
	.curves {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 24px;
	}
	.chart {
		min-width: 0;
	}
	.sub {
		margin: 0 0 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 18px;
		margin: 8px 0 0;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	@media (max-width: 760px) {
		.curves {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
