<script lang="ts" module>
	/**
	 * Change in held-out language-model loss against the softmax baseline of the same study, at
	 * matched compute. Negative is better. Sources: research/SEARCH.md §8 (S0), research/LOCAL.md §0
	 * (S6), research/BEYOND_REPORT.md (the combined study; baseline is softmax with a short causal
	 * convolution, and every control received at least the candidate's modelled compute).
	 */
	export interface LanguageRow {
		label: string;
		detail: string;
		value: number;
		seeds: string;
	}
	export const EARLY: { study: string; rows: LanguageRow[] }[] = [
		{
			study: 'S0 · FineWeb-Edu, 400M tokens, AdamW · against softmax, 6 layers',
			rows: [
				{
					label: 'Free-field attention',
					detail: 'subsets of every size, 5 layers at 0.97× compute',
					value: 2.16,
					seeds: '+2.05, +2.24, +2.20'
				},
				{
					label: 'Free-field, higher arities off at start',
					detail: 'same layer, starting as softmax',
					value: 0.83,
					seeds: '+0.91, +0.77, +0.81'
				}
			]
		},
		{
			study: 'S6 · FineWeb-Edu, 400M tokens, Muon · against softmax at equal compute',
			rows: [
				{
					label: 'Local-linear attention',
					detail: 'an exact local fit in an 8-dimensional chart',
					value: -0.39,
					seeds: '−0.40, −0.39, −0.37'
				},
				{
					label: 'Parallax',
					detail: 'a learned linear correction · prior work',
					value: -0.75,
					seeds: '−0.64, −0.90, −0.71'
				}
			]
		}
	];
	export const COMBINED: { study: string; rows: LanguageRow[] }[] = [
		{
			study:
				'Combined study · against softmax with a short convolution, compute allowance ≥ candidate',
			rows: [
				{
					label: 'Softmax without the convolution',
					detail: 'the usual baseline',
					value: 1.23,
					seeds: '+1.35, +1.10'
				},
				{
					label: 'Combined layer B',
					detail: 'Parallax correction + matrix-state branch',
					value: 0.77,
					seeds: '+0.82, +0.72'
				},
				{
					label: 'Parallax with the convolution',
					detail: 'estimation correction alone',
					value: -0.23,
					seeds: '−0.15, −0.31'
				},
				{
					label: 'Gated DeltaNet',
					detail: 'matrix-state recurrent network · prior work',
					value: -1.02,
					seeds: 'one seed'
				},
				{
					label: 'Gated DeltaProduct',
					detail: 'four Householder updates per token · prior work',
					value: -1.32,
					seeds: 'one seed'
				}
			]
		}
	];
</script>

<script lang="ts">
	let { groups }: { groups: { study: string; rows: LanguageRow[] }[] } = $props();

	const LO = -1.6;
	const HI = 2.4;
	const x = (v: number) => ((v - LO) / (HI - LO)) * 100;
	const fmt = (v: number) => `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(2)}%`;
</script>

<div
	class="lang"
	role="img"
	aria-label="Change in language-model loss relative to softmax, by model"
>
	<div class="axis-head">
		<span></span>
		<div class="axis">
			<span class="tick" style:left="{x(-1)}%">−1%<small>the bar we set</small></span>
			<span class="tick zero" style:left="{x(0)}%">softmax</span>
			<span class="tick" style:left="{x(2)}%">+2%</span>
		</div>
		<span></span>
	</div>
	{#each groups as g (g.study)}
		<div class="study">{g.study}</div>
		{#each g.rows as r (r.label)}
			<div class="row">
				<div class="name">{r.label}<small>{r.detail}</small></div>
				<div class="track">
					<span class="gate" style:left="{x(-1)}%"></span>
					<span class="zero-line" style:left="{x(0)}%"></span>
					<span
						class="bar"
						class:good={r.value <= -1}
						class:better={r.value < 0 && r.value > -1}
						style:left="{x(Math.min(0, r.value))}%"
						style:width="{Math.abs(x(r.value) - x(0))}%"
					></span>
				</div>
				<div class="val num">{fmt(r.value)}<small>{r.seeds}</small></div>
			</div>
		{/each}
	{/each}
</div>

<style>
	.lang {
		display: grid;
		gap: 10px;
		width: 100%;
		max-width: 780px;
		margin: 0 auto;
	}
	.axis-head,
	.row {
		display: grid;
		grid-template-columns: minmax(118px, 0.9fr) minmax(0, 1.6fr) 74px;
		gap: 12px;
		align-items: center;
	}
	.axis {
		position: relative;
		height: 34px;
	}
	.tick {
		position: absolute;
		bottom: 0;
		transform: translateX(-50%);
		display: grid;
		justify-items: center;
		font-size: var(--text-2xs);
		line-height: 1.2;
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.tick small {
		order: -1;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.tick.zero {
		color: var(--color-ink-2);
	}
	.study {
		margin-top: 10px;
		padding-bottom: 4px;
		border-bottom: 1px solid var(--color-edge);
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.name {
		display: grid;
		font-size: var(--text-sm);
		line-height: 1.3;
		color: var(--color-ink);
	}
	.name small,
	.val small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.track {
		position: relative;
		height: 18px;
	}
	.zero-line {
		position: absolute;
		top: -6px;
		bottom: -6px;
		width: 1px;
		background: var(--color-ink-3);
	}
	.gate {
		position: absolute;
		top: -6px;
		bottom: -6px;
		border-left: 1px dashed var(--color-rule);
	}
	.bar {
		position: absolute;
		top: 4px;
		height: 10px;
		border-radius: 1px;
		background: #4a4a4a;
	}
	.bar.better {
		background: #9a9a9a;
	}
	.bar.good {
		background: var(--color-ink);
	}
	.val {
		display: grid;
		justify-items: end;
		font-size: var(--text-sm);
		line-height: 1.3;
		color: var(--color-ink);
	}
	@media (max-width: 560px) {
		.axis-head,
		.row {
			grid-template-columns: minmax(0, 1fr) 66px;
			gap: 4px 10px;
		}
		.axis-head > span:first-child {
			display: none;
		}
		.name {
			grid-column: 1 / -1;
		}
		.track {
			grid-column: 1;
		}
	}
</style>
