<script lang="ts">
	/**
	 * Theorem 5, live: deal a table of SET cards, count for every card the zero-sum
	 * k-subsets it belongs to by Newton's identities in the character domain, and
	 * check every count against brute-force enumeration. The smallest k with a
	 * witness is the arity this card's relation needs.
	 */
	import { mulberry32 } from '#lib/set/rng.ts';
	import type { Card } from '#lib/set/cards.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { bruteCounts, newtonCounts } from './newton.ts';

	const K = 6;
	const N_CARDS = 9;
	let seed = $state(7);

	const result = $derived.by(() => {
		const rng = mulberry32(seed * 3301 + 5);
		const ids: number[] = [];
		while (ids.length < N_CARDS) {
			const v = Math.floor(rng() * 81);
			if (!ids.includes(v)) ids.push(v);
		}
		const cards = ids.map((v) => Array.from({ length: 4 }, (_, a) => Math.floor(v / 3 ** a) % 3));
		const newton = newtonCounts(cards, K);
		const brute = bruteCounts(cards, K);
		const agree = newton.every((row, i) => row.every((v, k) => v === brute[i][k]));
		return { cards: cards as unknown as Card[], newton, agree };
	});
	/** Timing on a bigger table, where the difference in growth shows. */
	const BIG = 27;
	let timing = $state<{ newton: number; brute: number } | null>(null);
	function time() {
		const rng = mulberry32(seed * 911 + 17);
		const ids: number[] = [];
		while (ids.length < BIG) {
			const v = Math.floor(rng() * 81);
			if (!ids.includes(v)) ids.push(v);
		}
		const cards = ids.map((v) => Array.from({ length: 4 }, (_, a) => Math.floor(v / 3 ** a) % 3));
		const t0 = performance.now();
		newtonCounts(cards, K);
		const t1 = performance.now();
		bruteCounts(cards, K);
		timing = { newton: t1 - t0, brute: performance.now() - t1 };
	}
	const smallest = (row: number[]) => {
		for (let k = 3; k <= K; k++) if (row[k] > 0) return k;
		return null;
	};
	const KS = [3, 4, 5, 6];
</script>

<figure class="demo">
	<table>
		<thead>
			<tr>
				<th>Card</th>
				{#each KS as k (k)}<th class="num"><MathTex tex={`k=${k}`} /></th>{/each}
				<th>Arity it needs</th>
			</tr>
		</thead>
		<tbody>
			{#each result.newton as row, i (i)}
				{@const s = smallest(row)}
				<tr>
					<td><SetCard card={result.cards[i]} width={22} /></td>
					{#each KS as k (k)}
						<td class="num" class:zero={row[k] === 0} class:first={k === s}>{row[k]}</td>
					{/each}
					<td class="need">{s ? `${s} cards` : 'none up to 6'}</td>
				</tr>
			{/each}
		</tbody>
	</table>
	<div class="controls">
		<button onclick={() => (seed += 1)}>Deal another table</button>
		<span class="check" class:ok={result.agree}>
			{result.agree ? 'Every count matches brute-force enumeration' : 'Mismatch with brute force'}
		</span>
		<button class="quiet" onclick={time}>Time it on {BIG} cards</button>
		{#if timing}
			<span class="num time">
				{BIG} cards, every k up to {K}: {timing.newton.toFixed(1)} ms by Newton's identities,
				{timing.brute.toFixed(0)} ms by enumeration
			</span>
		{/if}
	</div>
	<figcaption>
		For each of nine cards, the number of ways to pick <MathTex tex="k-1" /> other cards so that all
		<MathTex tex="k" /> sum to zero in <MathTex tex={String.raw`\mathbb Z_3^4`} />. The counts come
		from power sums of character vectors, combined by Hadamard products: no tuple is ever
		enumerated. The highlighted entry is the smallest arity at which the card takes part in a
		zero-sum relation.
	</figcaption>
</figure>

<style>
	.demo {
		margin: 18px 0 24px;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	thead th {
		border-bottom: 1px solid #262626;
		padding: 0 6px 8px;
		font-weight: 400;
		text-align: left;
		color: var(--color-ink-3);
	}
	tbody tr:last-child td {
		border-bottom: 1px solid #262626;
	}
	td {
		padding: 4px 6px;
		color: var(--color-ink-2);
	}
	td.num,
	th.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
	td.zero {
		color: #444;
	}
	td.first {
		color: var(--color-ink);
		font-weight: 600;
	}
	td.need {
		color: var(--color-ink-3);
		font-size: var(--text-xs);
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px 16px;
		margin-top: 10px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	button {
		height: 28px;
		padding: 0 12px;
		border: 0;
		border-radius: var(--radius-ui);
		background: var(--color-lift);
		color: var(--color-ink);
		font: inherit;
		cursor: pointer;
	}
	button:hover {
		background: var(--color-control);
	}
	button.quiet {
		background: transparent;
		color: var(--color-ink-2);
		text-decoration: underline;
		text-underline-offset: 3px;
		padding: 0;
	}
	.check.ok {
		color: var(--color-ink);
	}
	.time {
		margin-left: auto;
	}
	figcaption {
		margin-top: 10px;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
</style>
