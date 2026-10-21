<script lang="ts">
	/**
	 * The loss-dilution test (research/NEXT.md, experiment 1, seeds 1–3). Top: how few tokens
	 * carry the answer. Bottom: paired exact accuracy under ordinary and decision-weighted loss.
	 */
	const SPLITS = {
		id: {
			label: 'Held-out stories',
			ops: '13.6 operations on average',
			share: 0.01048,
			owner: 14.45,
			rows: [
				{ arm: 'Softmax', loss: 'ordinary', value: 0.91 },
				{ arm: 'Composition hybrid', loss: 'ordinary', value: 0.91 },
				{ arm: 'Softmax', loss: 'decision-weighted', value: 17.58 },
				{ arm: 'Composition hybrid', loss: 'decision-weighted', value: 13.93 }
			]
		},
		short: {
			label: 'Short stories',
			ops: '8 operations',
			share: 0.01695,
			owner: 26.17,
			rows: [
				{ arm: 'Softmax', loss: 'ordinary', value: 1.17 },
				{ arm: 'Composition hybrid', loss: 'ordinary', value: 0.91 },
				{ arm: 'Softmax', loss: 'decision-weighted', value: 34.64 },
				{ arm: 'Composition hybrid', loss: 'decision-weighted', value: 27.99 }
			]
		}
	} as const;
	let split = $state<keyof typeof SPLITS>('id');
	const s = $derived(SPLITS[split]);
	const cells = $derived(Math.round(1 / s.share));
	const MAX = 40;
</script>

<div class="dil">
	<div class="seg" role="group" aria-label="Story length">
		{#each Object.entries(SPLITS) as [id, v] (id)}
			<button aria-pressed={split === id} onclick={() => (split = id as keyof typeof SPLITS)}
				>{v.label}</button
			>
		{/each}
	</div>
	<div class="strip-wrap">
		<div class="strip" aria-label="One answer token among {cells} tokens">
			{#each Array.from({ length: cells }, (_, i) => i) as i (i)}
				<span class:hot={i === cells - 1}></span>
			{/each}
		</div>
		<p class="strip-note">
			One token in about {cells} carries the answer ({(s.share * 100).toFixed(2)}% of tokens, {s.ops}).
			Ordinary loss averages over all of them.
		</p>
	</div>
	<div class="bars" role="img" aria-label="Paired accuracy by model and loss">
		<div class="head">
			<span></span>
			<div class="scale">
				<span style:left="{(s.owner / MAX) * 100}%" class="owner">guess the first owner</span>
				<span style:left="100%">{MAX}%</span>
			</div>
			<span></span>
		</div>
		{#each s.rows as r, i (i)}
			<div class="row" class:first={i === 2}>
				<div class="name">{r.arm}<small>{r.loss} loss</small></div>
				<div class="track">
					<span class="owner-line" style:left="{(s.owner / MAX) * 100}%"></span>
					<span class="bar" class:lit={r.loss !== 'ordinary'} style:width="{(r.value / MAX) * 100}%"
					></span>
				</div>
				<span class="val num">{r.value.toFixed(2)}%</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.dil {
		display: grid;
		gap: 18px;
		width: 100%;
		justify-items: center;
	}
	.strip-wrap {
		display: grid;
		gap: 8px;
		width: min(100%, 560px);
	}
	.strip {
		display: flex;
		flex-wrap: wrap;
		gap: 3px;
	}
	.strip span {
		width: 8px;
		height: 8px;
		border-radius: 1px;
		background: #262626;
	}
	.strip span.hot {
		background: var(--color-ink);
	}
	.strip-note {
		margin: 0;
		font-size: var(--text-xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.bars {
		display: grid;
		gap: 10px;
		width: min(100%, 560px);
	}
	.head,
	.row {
		display: grid;
		grid-template-columns: minmax(120px, 0.8fr) minmax(0, 1.4fr) 56px;
		gap: 12px;
		align-items: center;
	}
	.row.first {
		margin-top: 8px;
	}
	.scale {
		position: relative;
		height: 16px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.scale span {
		position: absolute;
		top: 0;
		transform: translateX(-50%);
		white-space: nowrap;
	}
	.scale span:last-child {
		transform: translateX(-100%);
	}
	.name {
		display: grid;
		font-size: var(--text-sm);
		line-height: 1.3;
		color: var(--color-ink);
	}
	.name small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.track {
		position: relative;
		height: 10px;
		background: #141414;
		border-radius: 1px;
	}
	.bar {
		position: absolute;
		inset: 0 auto 0 0;
		min-width: 2px;
		background: #555;
		border-radius: 1px;
	}
	.bar.lit {
		background: var(--color-ink);
	}
	.owner-line {
		position: absolute;
		top: -5px;
		bottom: -5px;
		border-left: 1px dashed var(--color-ink-3);
	}
	.val {
		text-align: right;
		font-size: var(--text-sm);
		color: var(--color-ink);
	}
</style>
