<script lang="ts">
	import { CHARACTER_ROWS } from './groupResults.ts';
	const rows = [CHARACTER_ROWS[0], CHARACTER_ROWS[1], CHARACTER_ROWS[6]];
	const labels = ['Softmax · 1 layer', 'Softmax · 2 layers', 'Newton attention'];
</script>

<div class="experiment">
	<div class="axis">
		<span>Match-4 · balanced accuracy</span><span>50% chance</span><span>100%</span>
	</div>
	<div class="rows">
		{#each rows as row, i (row.id)}
			<div class="row">
				<div class="label">
					{labels[i]}<small
						>{row.id === 'newton'
							? 'Native phase products · reference'
							: 'All characters supplied · 3 seeds'}</small
					>
				</div>
				<div class="track" aria-hidden="true">
					<span style:left={`${(row.values[1].mean - 50) * 2}%`}></span>
				</div>
				<span class="value">{row.values[1].display}%</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.experiment {
		color: var(--color-ink);
		width: 100%;
	}
	.axis {
		display: grid;
		grid-template-columns: minmax(180px, 1fr) 1fr 50px;
		gap: 18px;
		align-items: end;
		margin-bottom: 18px;
		color: var(--color-ink-3);
		font-size: 11px;
	}
	.axis span:last-child {
		text-align: right;
	}
	.rows {
		display: grid;
		gap: 24px;
	}
	.row {
		display: grid;
		grid-template-columns: minmax(180px, 1fr) 1fr 50px;
		gap: 18px;
		align-items: center;
	}
	.label {
		font-size: 13px;
		line-height: 1.5;
	}
	small {
		display: block;
		color: var(--color-ink-3);
		font-size: 10px;
	}
	.track {
		position: relative;
		height: 1px;
		margin-right: 4px;
		background: var(--color-rule);
	}
	.track span {
		position: absolute;
		top: -3px;
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: var(--color-ink);
		transform: translateX(-50%);
	}
	.value {
		text-align: right;
		font-size: 13px;
		font-variant-numeric: tabular-nums;
	}
	@media (max-width: 620px) {
		.axis,
		.row {
			grid-template-columns: 144px minmax(0, 1fr) 42px;
			gap: 12px;
		}
		.axis {
			font-size: 10px;
		}
		.axis span:first-child {
			max-width: 132px;
		}
		.label {
			font-size: 12px;
		}
		small {
			max-width: 140px;
			font-size: 9px;
		}
	}
</style>
