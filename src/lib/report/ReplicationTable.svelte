<script lang="ts">
	/**
	 * Replicated results: mean balanced accuracy per task and model, with every seed
	 * drawn as a dot on a 50–100% strip so the spread is visible, not just the mean.
	 * With metric 'tok' the cells show plain accuracy instead. A row with no seeds is a
	 * published number: its mean is shown with the published standard deviation, if any.
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
		floor = 0.5,
		metric = 'bal',
		caption
	}: {
		rows: Row[];
		tasks: { id: string; label: string; floor?: number }[];
		models: { id: string; label: string }[];
		/** Chance level for the strip's left edge, unless a task sets its own. */
		floor?: number;
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
	const x = (v: number, f: number) => 4 + Math.max(0, Math.min(1, (v - f) / (1 - f))) * 52;
</script>

<div class="wrap" style:--n={tasks.length}>
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
					<td class="name">{m.label}</td>
					{#each tasks as t (t.id)}
						{@const c = cell(t.id, m.id)}
						<td class="r">
							{#if c}
								{@const v = values(c)}
								<span class="v" class:top={mean(c) >= best(t.id) - 0.005}>
									<span class="num">{(mean(c) * 100).toFixed(1)}</span>
									{#if v.length}
										<svg
											width="60"
											viewBox="0 0 60 10"
											height="10"
											aria-label="Seeds: {v.map((b) => (b * 100).toFixed(0)).join(', ')}%"
										>
											<line x1="4" x2="56" y1="5" y2="5" class="axis" />
											{#each v as b, i (i)}<circle
													cx={x(b, t.floor ?? floor)}
													cy="5"
													r="2.4"
												/>{/each}
										</svg>
									{:else}
										<span class="pub"
											>{c.sd === undefined ? '' : `± ${(c.sd * 100).toFixed(1)}`}</span
										>
									{/if}
								</span>
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
		container-type: inline-size;
		overflow-x: auto;
		margin: 12px 0 18px;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	caption {
		caption-side: top;
		margin-bottom: 8px;
		text-align: left;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	thead th {
		border-bottom: 1px solid #262626;
		padding: 0 8px 8px 0;
		font-weight: 400;
		text-align: left;
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	tbody tr:last-child td {
		border-bottom: 1px solid #262626;
	}
	td {
		padding: 6px 8px 6px 0;
	}
	.r {
		text-align: right;
	}
	.name {
		white-space: nowrap;
	}
	.v {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		color: var(--color-ink-2);
	}
	.v.top {
		color: var(--color-ink);
		font-weight: 500;
	}
	.num {
		min-width: 34px;
		font-variant-numeric: tabular-nums;
	}
	svg {
		display: block;
	}
	.pub {
		width: 60px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		text-align: left;
	}
	.axis {
		stroke: #262626;
	}
	circle {
		fill: #8a8a8a;
	}
	.v.top circle {
		fill: #f2f2f2;
	}
	.na {
		color: #444;
	}
	/* narrow: each model's name gets its own line, its numbers sit under it */
	@container (max-width: 520px) {
		table,
		thead,
		tbody,
		caption {
			display: block;
		}
		tr {
			display: grid;
			grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		}
		thead th:first-child {
			display: none;
		}
		thead th {
			padding-right: 0;
		}
		td {
			padding-right: 0;
		}
		td.name {
			grid-column: 1 / -1;
			padding: 10px 0 0;
			color: var(--color-ink-3);
			font-size: var(--text-xs);
		}
		tbody td:not(.name) {
			padding-top: 2px;
			padding-bottom: 8px;
		}
		tbody tr:last-child {
			border-bottom: 1px solid #262626;
		}
		tbody tr:last-child td {
			border-bottom: 0;
		}
		svg {
			width: 44px;
		}
	}
</style>
