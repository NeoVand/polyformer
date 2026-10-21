<script lang="ts">
	/**
	 * Replicated results: mean balanced accuracy per task and model, with the seeds written
	 * small underneath, and the best mean in each column in bold. With metric 'tok' the cells
	 * show plain accuracy instead. A row with no seeds is a published number: its mean is
	 * shown with the published standard deviation, if any.
	 */
	interface Row {
		task: string;
		model: string;
		seeds: number[];
		bal: number[];
		bal_mean: number;
		tok?: number[];
		/** Published standard deviation, for rows without seeds. */
		sd?: number;
		params: number;
	}
	let {
		rows,
		tasks,
		models,
		metric = 'bal',
		caption
	}: {
		rows: Row[];
		tasks: { id: string; label: string }[];
		models: { id: string; label: string }[];
		/** Balanced accuracy, or plain accuracy over scored tokens. */
		metric?: 'bal' | 'tok';
		caption: string;
	} = $props();

	const values = (r: Row) => (metric === 'tok' ? (r.tok ?? []) : r.bal);
	const mean = (r: Row) => {
		const v = values(r);
		return metric === 'bal' || !v.length ? r.bal_mean : v.reduce((a, b) => a + b, 0) / v.length;
	};
	const cell = (task: string, model: string) =>
		rows.find((r) => r.task === task && r.model === model);
	const best = (task: string) => Math.max(...rows.filter((r) => r.task === task).map(mean));
	const pct = (v: number) => (v * 100).toFixed(1);
</script>

<div class="wrap">
	<table>
		<caption>{caption}</caption>
		<thead>
			<tr>
				<th>Model</th>
				{#each tasks as t (t.id)}<th class="r">{t.label}</th>{/each}
			</tr>
		</thead>
		<tbody>
			{#each models as m (m.id)}
				<tr>
					<th class="name">{m.label}</th>
					{#each tasks as t (t.id)}
						{@const c = cell(t.id, m.id)}
						<td class="r">
							{#if c}
								{@const v = values(c)}
								<span class="v" class:top={mean(c) >= best(t.id) - 0.005}>{pct(mean(c))}</span>
								{#if v.length > 1}
									<small>{v.map(pct).join(', ')}</small>
								{:else if c.sd !== undefined}
									<small>± {pct(c.sd)}</small>
								{/if}
							{:else}
								<span class="na">·</span>
							{/if}
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.wrap {
		overflow-x: auto;
		margin: 12px 0 18px;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
		line-height: 1.45;
		font-variant-numeric: tabular-nums;
	}
	/* read by screen readers; on screen the figure's own caption says the same */
	caption {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
		white-space: nowrap;
	}
	thead {
		border-top: 1px solid var(--color-ink-3);
		border-bottom: 1px solid var(--color-rule);
	}
	thead th {
		padding: 7px 14px 7px 0;
		font-size: var(--text-xs);
		font-weight: 400;
		text-align: left;
		color: var(--color-ink-3);
	}
	tbody {
		border-bottom: 1px solid var(--color-ink-3);
	}
	th.name,
	td {
		padding: 7px 14px 7px 0;
		vertical-align: top;
	}
	th.name {
		font-weight: 400;
		text-align: left;
		color: var(--color-ink);
	}
	th:last-child,
	td:last-child {
		padding-right: 0;
	}
	.r {
		text-align: right;
		white-space: nowrap;
	}
	.v {
		color: var(--color-ink-2);
	}
	.v.top {
		color: var(--color-ink);
		font-weight: 600;
	}
	small {
		display: block;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.na {
		color: var(--color-ink-3);
	}
	@media (max-width: 640px) {
		table {
			font-size: var(--text-xs);
		}
		th.name,
		td,
		thead th {
			padding-right: 10px;
		}
		small {
			white-space: normal;
		}
	}
</style>
