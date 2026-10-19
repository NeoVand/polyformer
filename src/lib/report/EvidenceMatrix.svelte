<script lang="ts">
	/** Every accuracy the project has measured, by task and model, with where it came from. */
	import { EVIDENCE, MODELS, TASKS, type Cell } from './evidence.ts';
	import { pct } from '#lib/ui/format.ts';

	/** Best accuracy per task, to mark the winners in each column. */
	const best = Object.fromEntries(
		TASKS.map((t) => [t.id, Math.max(...Object.values(EVIDENCE[t.id]).map((c) => c?.acc ?? 0))])
	);
	const shade = (c: Cell) => Math.round(24 + Math.pow(c.acc, 2.2) * 200);
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
						style:--g={shade(c)}
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
	<div class="legend">
		<span><i class="swatch"></i>Measured in this browser's engine</span>
		<span><i class="swatch harness"></i>Offline research harness, one seed</span>
		<span><b>≈</b> stalled at the majority rate</span>
	</div>
</div>

<style>
	.matrix {
		overflow-x: auto;
	}
	.grid {
		display: grid;
		grid-template-columns: 132px repeat(var(--cols), minmax(64px, 1fr));
		gap: 4px;
		align-items: stretch;
		min-width: 520px;
	}
	.col-head {
		display: grid;
		align-content: end;
		gap: 2px;
		padding: 0 4px 8px;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
		transition: color 120ms ease;
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
		display: flex;
		align-items: center;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
		transition: color 120ms ease;
	}
	.col-head.on,
	.row-head.on {
		color: var(--color-ink);
	}
	.cell {
		display: grid;
		place-items: center;
		height: 30px;
		border-radius: 4px;
		background: rgb(var(--g) var(--g) var(--g));
		color: var(--color-void);
		font-size: var(--text-sm);
		font-weight: 500;
	}
	.cell.harness {
		background: transparent;
		border: 1.5px solid rgb(var(--g) var(--g) var(--g));
		color: rgb(var(--g) var(--g) var(--g));
	}
	.cell.win {
		box-shadow:
			0 0 0 1.5px var(--color-void),
			0 0 0 2.5px var(--color-ink);
	}
	.cell.empty {
		background: transparent;
		color: var(--color-edge);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 22px;
		margin-top: 14px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 8px;
	}
	.swatch {
		width: 14px;
		height: 14px;
		border-radius: 3px;
		background: var(--color-ink-2);
	}
	.swatch.harness {
		background: transparent;
		border: 1.5px solid var(--color-ink-2);
	}
</style>
