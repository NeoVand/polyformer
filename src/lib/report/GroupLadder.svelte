<script lang="ts">
	import { CEILINGS, GROUP_ROWS } from './groupResults.ts';
	let { group, compact = false }: { group?: 'a4' | 'a5'; compact?: boolean } = $props();
	let pitch = $derived(compact ? 27 : 35);
	const groups = [
		{ id: 'a4', label: 'A₄ · tetrahedral rotations', index: 1, ceiling: CEILINGS.a4 },
		{ id: 'a5', label: 'A₅ · icosahedral rotations', index: 3, ceiling: CEILINGS.a5 }
	];
	const x = (value: number) => 128 + (value - 50) * 3.48;
</script>

<div class="ladders" class:single={!!group}>
	{#each groups.filter((entry) => !group || entry.id === group) as entry (entry.id)}
		<div class="ladder">
			<h4>{entry.label}</h4>
			<svg
				viewBox={`0 0 356 ${compact ? 254 : 310}`}
				role="img"
				aria-label={`${entry.label}: balanced accuracy at 6,000 steps. Dashed line is the exact order-blind ceiling, ${entry.ceiling} percent.`}
			>
				<text x="0" y="17" class="quiet">Accuracy %</text>
				{#each [50, 75, 100] as tick (tick)}
					<text x={x(tick)} y="17" text-anchor="middle" class="quiet">{tick}</text>
				{/each}
				<line
					x1={x(entry.ceiling)}
					x2={x(entry.ceiling)}
					y1="32"
					y2={compact ? 247 : 303}
					class="ceiling"
				/>
				{#each GROUP_ROWS as row, i (row.id)}
					{@const value = row.values[entry.index]}
					<text x="0" y={48 + i * pitch}>{row.short}</text>
					<circle
						cx={x(value.mean)}
						cy={44 + i * pitch}
						r="3.5"
						class:muted={row.id === 'h2' || row.id === 'newton'}
					/>
					<text x="356" y={48 + i * pitch} text-anchor="end" class="value">{value.display}</text>
				{/each}
			</svg>
			<p><span class="dash" aria-hidden="true"></span>Order-blind ceiling · {entry.ceiling}%</p>
		</div>
	{/each}
</div>

<style>
	.ladders {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 30px;
		width: 100%;
		color: var(--color-ink);
	}
	.ladders.single {
		grid-template-columns: minmax(0, 1fr);
		max-width: 356px;
		margin-inline: auto;
	}
	h4 {
		margin: 0 0 10px;
		font-size: 13px;
		font-weight: 500;
	}
	svg {
		display: block;
		width: 100%;
		overflow: visible;
	}
	text {
		fill: currentColor;
		font: 12px var(--font-sans);
	}
	.quiet {
		fill: var(--color-ink-3);
		font-size: 11px;
	}
	.value {
		font-variant-numeric: tabular-nums;
	}
	circle {
		fill: currentColor;
	}
	circle.muted {
		fill: var(--color-ink-3);
	}
	.ceiling {
		stroke: var(--color-ink-3);
		stroke-width: 1;
		stroke-dasharray: 3 4;
	}
	p {
		display: flex;
		align-items: center;
		gap: 8px;
		margin: 6px 0 0;
		font-size: 11px;
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.dash {
		display: inline-block;
		flex: 0 0 14px;
		border-top: 1px dashed currentColor;
	}
	@media (max-width: 620px) {
		.ladders {
			grid-template-columns: 1fr;
			gap: 26px;
		}
	}
</style>
