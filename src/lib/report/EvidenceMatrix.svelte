<script lang="ts">
	/** Every accuracy the project has measured, by task and model, with where it came from. */
	import { EVIDENCE, MODELS, TASKS } from './evidence.ts';
	import { pct } from '#lib/ui/format.ts';

	/** Best accuracy per task, to mark the winners in each column. */
	const best = Object.fromEntries(
		TASKS.map((t) => [t.id, Math.max(...Object.values(EVIDENCE[t.id]).map((c) => c?.acc ?? 0))])
	);
	let hovered = $state<{ model: string; task: string } | null>(null);
</script>

<div class="matrix" aria-label="Evidence matrix">
	<div class="grid" style:--cols={TASKS.length}>
		<span></span>
		{#each TASKS as t (t.id)}
			<span class="col-head" class:on={hovered?.task === t.id}
				><b>{t.label}</b><small>{t.detail}</small></span
			>
		{/each}
		{#each MODELS as m (m.id)}
			<span class="row-head" class:on={hovered?.model === m.id}>{m.label}</span>
			{#each TASKS as t (t.id)}
				{@const c = EVIDENCE[t.id][m.id]}
				{#if c}
					<span
						class="cell num"
						class:win={c.acc === best[t.id]}
						class:harness={c.source === 'harness'}
						role="img"
						aria-label="{m.label} on {t.label}: {pct(c.acc, 1)}, {c.source === 'browser'
							? 'measured in the browser'
							: 'offline harness'}"
						onpointerenter={() => (hovered = { model: m.id, task: t.id })}
						onpointerleave={() => (hovered = null)}>{c.approx ? '≈' : ''}{pct(c.acc, 0)}</span
					>
				{:else}
					<span class="cell empty" aria-label="Not run">·</span>
				{/if}
			{/each}
		{/each}
	</div>
	<p class="legend">
		Upright: measured in this browser's engine. <i>Italic</i>: offline research harness, one seed.
		<b>Bold</b>: best in its column. ≈ marks a run that stalled at the majority rate.
	</p>
</div>

<style>
	.matrix {
		overflow-x: auto;
	}
	.grid {
		display: grid;
		grid-template-columns: 120px repeat(var(--cols), minmax(56px, 1fr));
		align-items: baseline;
		min-width: 520px;
		font-size: var(--text-sm);
	}
	.grid > span {
		padding: 5px 6px;
	}
	.col-head {
		display: grid;
		align-content: end;
		gap: 2px;
		padding-bottom: 8px !important;
		border-bottom: 1px solid #262626;
		text-align: right;
		color: var(--color-ink-2);
		transition: color 120ms ease;
	}
	.grid > span:first-child {
		border-bottom: 1px solid #262626;
	}
	.col-head b {
		font-weight: 500;
	}
	.col-head small {
		font-size: 11px;
		color: var(--color-ink-3);
		line-height: 1.3;
	}
	.row-head {
		padding-left: 0 !important;
		color: var(--color-ink-2);
		transition: color 120ms ease;
	}
	.col-head.on,
	.row-head.on {
		color: var(--color-ink);
	}
	.cell {
		text-align: right;
		font-variant-numeric: tabular-nums;
		color: var(--color-ink-2);
	}
	.cell.harness {
		font-style: italic;
		color: var(--color-ink-3);
	}
	.cell.win {
		font-weight: 600;
		color: var(--color-ink);
	}
	.cell.empty {
		color: #3a3a3a;
	}
	.legend {
		margin: 10px 0 0;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.legend b {
		font-weight: 600;
		color: var(--color-ink-2);
	}
</style>
