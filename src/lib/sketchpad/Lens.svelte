<script lang="ts">
	import { DEPTH, FULL_ATTENTION, SUM_CODES, sumValue, type InsideTick } from './inside.ts';

	interface Props {
		seen: InsideTick | null;
		/** the program has inside data */
		ready: boolean;
		/** ticks are paced: let each tick rise through the layers */
		slow: boolean;
	}

	let { seen, ready, slow }: Props = $props();

	const CW = 14;
	const CH = 11;
	const GAP = 12;
	const cols = $derived.by(() => {
		if (!seen) return [];
		let x = 0;
		return seen.lens.map((r) => {
			const c = { read: r, x, K: r.group.alphabet.length };
			x += c.K * CW + GAP;
			return c;
		});
	});
	const W = $derived(
		cols.length ? cols[cols.length - 1].x + cols[cols.length - 1].K * CW : 21 * CW
	);
	const show = (alphabet: string, c: string) =>
		alphabet === SUM_CODES ? (c === 'H' ? 'H' : sumValue(c)!) : c === '_' ? '·' : c;
	const decided = $derived(seen?.lens[0]?.decided ?? null);
	/** depth 0 (the input) at the bottom, the output at the top */
	const y = (l: number) => (DEPTH - 1 - l) * CH;
	const LAYERS = Array.from({ length: DEPTH }, (_, l) => l);
</script>

<figure class="sp-panel lens">
	<figcaption class="sp-cap">
		<span class="sp-title">Layer by layer</span>
		<span class="sp-sub">each of the 24 layers read as a guess at the answer</span>
	</figcaption>
	<div class="sp-body">
		{#if seen && seen.lens.length}
			<svg viewBox="-26 -30 {W + 70} {DEPTH * CH + 34}" role="img" aria-label="Logit lens by layer">
				{#each cols as col (col.read.group.name)}
					<text class="glab" x={col.x} y="-19">{col.read.group.name}</text>
					{#each [...col.read.group.alphabet] as c, k (k)}
						<text
							class="clab"
							class:on={k === col.read.top}
							x={col.x + k * CW + CW / 2 - 0.5}
							y="-4"
							text-anchor="middle">{show(col.read.group.alphabet, c)}</text
						>
					{/each}
					{#each LAYERS as l (l)}
						{#each Array.from({ length: col.K }, (_, k) => k) as k (k)}
							<rect
								class="cell"
								x={col.x + k * CW}
								y={y(l)}
								width={CW - 2}
								height={CH - 2}
								style:opacity={0.05 + 0.95 * col.read.probs[l * col.K + k]}
								style:transition-delay="{slow ? l * 22 : 0}ms"
							/>
						{/each}
					{/each}
				{/each}
				{#each [0, 4, 8, 12, 16, 20, 24] as l (l)}
					<text class="ylab" x="-10" y={y(l) + CH - 2.5} text-anchor="end">{l}</text>
				{/each}
				{#each FULL_ATTENTION as l (l)}
					<!-- the stream right after a full-attention layer -->
					<rect class="fa" x="-6" y={y(l + 1)} width="3" height={CH - 2} />
				{/each}
				{#if decided !== null}
					<line class="dec" x1="-6" x2={W + 4} y1={y(decided) + CH - 1} y2={y(decided) + CH - 1} />
					<text class="declab" x={W + 8} y={y(decided) + CH - 2}>layer {decided}</text>
				{/if}
			</svg>
		{:else}
			<p class="sp-empty">
				{ready ? 'Run a problem to see each layer.' : 'Load the model to look inside.'}
			</p>
		{/if}
	</div>
	<p class="sp-foot">
		{#if decided !== null}The answer leads for good from layer {decided} (dashed line).{/if}
		<span class="sp-dim key"
			><i></i>after a full-attention layer (6 of 24; the rest are Gated DeltaNet)</span
		>
	</p>
</figure>

<style>
	svg {
		display: block;
		width: 100%;
		height: 100%;
		overflow: visible;
	}
	.cell {
		fill: var(--color-ink);
		transition: opacity 320ms cubic-bezier(0.22, 1, 0.36, 1);
	}
	.glab {
		font-size: 12px;
		fill: var(--color-ink-3);
	}
	.clab {
		font-family: var(--font-mono);
		font-size: 10px;
		fill: var(--color-ink-3);
	}
	.clab.on {
		fill: var(--color-ink);
	}
	.ylab {
		font-family: var(--font-mono);
		font-size: 10.5px;
		fill: var(--color-ink-3);
	}
	.fa {
		fill: var(--color-ink-2);
	}
	.dec {
		stroke: var(--color-ink-2);
		stroke-width: 0.8;
		stroke-dasharray: 2 2;
	}
	.declab {
		font-size: 10.5px;
		fill: var(--color-ink-2);
	}
	.key {
		display: block;
		font-size: var(--text-2xs);
	}
	.key i {
		display: inline-block;
		vertical-align: middle;
		width: 3px;
		height: 8px;
		margin-right: 5px;
		background: var(--color-ink-2);
	}
</style>
