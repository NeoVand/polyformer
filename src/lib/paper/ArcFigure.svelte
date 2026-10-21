<script lang="ts">
	/**
	 * Algebraic ARC (research/NEXT.md, experiment 2). Top: a puzzle drawn from the same kind of
	 * generator: a hidden composition of grid moves and a recolouring, three examples, one test.
	 * Bottom: exact-match accuracy on the invertible tier, seeds 1–3.
	 */
	import { mulberry32 } from '#lib/set/rng.ts';

	const N = 6;
	const SHADES = ['#121212', '#4b4b4b', '#7c7c7c', '#b4b4b4', '#f2f2f2'];
	type Grid = number[][];
	type Move = { name: string; apply: (g: Grid) => Grid };

	const rot: Move = {
		name: 'turn a quarter',
		apply: (g) => g.map((row, r) => row.map((_, c) => g[N - 1 - c][r]))
	};
	const flip: Move = { name: 'mirror', apply: (g) => g.map((row) => [...row].reverse()) };
	const shift = (dx: number, dy: number): Move => ({
		name: `slide ${dx} right, ${dy} down`,
		apply: (g) => g.map((row, r) => row.map((_, c) => g[(r - dy + N) % N][(c - dx + N) % N]))
	});
	const recolour = (perm: number[]): Move => ({
		name: 'swap shades',
		apply: (g) => g.map((row) => row.map((v) => (v === 0 ? 0 : perm[v - 1])))
	});

	function puzzle(seed: number, depth: number) {
		const rng = mulberry32(seed * 7919 + depth);
		const pick = () => {
			const k = Math.floor(rng() * 4);
			if (k === 0) return rot;
			if (k === 1) return flip;
			if (k === 2) return shift(1 + Math.floor(rng() * 5), Math.floor(rng() * 6));
			const p = [1, 2, 3, 4];
			for (let i = 3; i > 0; i--) {
				const j = Math.floor(rng() * (i + 1));
				[p[i], p[j]] = [p[j], p[i]];
			}
			return recolour(p);
		};
		const moves = Array.from({ length: depth }, pick);
		const grid = (): Grid =>
			Array.from({ length: N }, () =>
				Array.from({ length: N }, () => (rng() < 0.42 ? 1 + Math.floor(rng() * 4) : 0))
			);
		const run = (g: Grid) => moves.reduce((acc, m) => m.apply(acc), g);
		const examples = Array.from({ length: 3 }, () => {
			const g = grid();
			return { input: g, output: run(g) };
		});
		const test = grid();
		return { moves, examples, test, answer: run(test) };
	}

	let depth = $state(2);
	let seed = $state(3);
	let reveal = $state(false);
	const p = $derived(puzzle(seed, depth));

	const RESULTS = [
		{ depth: 1, models: 24.48, seeds: '20.31, 28.12, 25.00' },
		{ depth: 2, models: 15.1, seeds: '17.19, 15.62, 12.50' },
		{ depth: 3, models: 11.46, seeds: '6.25, 14.06, 14.06' },
		{ depth: 4, models: 2.6, seeds: '4.69, 1.56, 1.56' }
	];
</script>

{#snippet gridView(g: Grid, label: string)}
	<svg viewBox="0 0 {N * 10} {N * 10}" class="grid" role="img" aria-label={label}>
		{#each g as row, r (r)}
			{#each row as v, c (c)}
				<rect x={c * 10 + 0.5} y={r * 10 + 0.5} width="9" height="9" rx="1" fill={SHADES[v]} />
			{/each}
		{/each}
	</svg>
{/snippet}

<div class="arc">
	<div class="controls">
		<div class="seg" role="group" aria-label="Number of hidden moves">
			{#each [1, 2, 3, 4] as d (d)}
				<button aria-pressed={depth === d} onclick={() => ((depth = d), (reveal = false))}
					>{d} {d === 1 ? 'move' : 'moves'}</button
				>
			{/each}
		</div>
		<button class="plain" onclick={() => ((seed += 1), (reveal = false))}>New puzzle</button>
	</div>
	<div class="pairs">
		{#each p.examples as ex, i (i)}
			<div class="pair">
				{@render gridView(ex.input, `Example ${i + 1} input`)}
				<span class="arrow" aria-hidden="true">→</span>
				{@render gridView(ex.output, `Example ${i + 1} output`)}
			</div>
		{/each}
		<div class="pair test">
			{@render gridView(p.test, 'Test input')}
			<span class="arrow" aria-hidden="true">→</span>
			{#if reveal}
				{@render gridView(p.answer, 'Test answer')}
			{:else}
				<button class="ask" onclick={() => (reveal = true)}>?</button>
			{/if}
		</div>
	</div>
	<p class="rule">
		{#if reveal}
			The hidden rule: {p.moves.map((m) => m.name).join(', then ')}.
		{:else}
			Three examples of one hidden rule, then a test grid. Press <b>?</b> to see the answer and the rule.
		{/if}
	</p>

	<div class="results" role="img" aria-label="Exact-match accuracy by number of hidden moves">
		<div class="r-head">
			<span>Hidden moves</span>
			<span>Trained models, exact grids</span>
			<span class="num">Solver</span>
		</div>
		{#each RESULTS as r (r.depth)}
			<div class="r-row">
				<span class="d num">{r.depth}</span>
				<div class="track">
					<span class="bar" style:width="{r.models}%"></span>
					<span class="v num">{r.models.toFixed(2)}%</span>
				</div>
				<span class="solver num">100%</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.arc {
		display: grid;
		gap: 16px;
		width: 100%;
		justify-items: center;
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 10px 16px;
		align-items: center;
		justify-content: center;
	}
	.plain {
		height: 28px;
		padding: 0 12px;
		border-radius: var(--radius-ui);
		background: var(--color-lift);
		font-size: var(--text-xs);
		color: var(--color-ink);
	}
	.plain:hover {
		background: var(--color-control);
	}
	.pairs {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 18px;
		width: min(100%, 760px);
	}
	.pair {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
		gap: 6px;
		align-items: center;
	}
	.pair.test {
		padding-left: 14px;
		border-left: 1px solid var(--color-edge);
	}
	.grid {
		width: 100%;
		display: block;
	}
	.arrow {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.ask {
		aspect-ratio: 1;
		width: 100%;
		border-radius: 2px;
		background: #121212;
		font-size: 18px;
		color: var(--color-ink);
	}
	.ask:hover {
		background: var(--color-lift);
	}
	.rule {
		margin: 0;
		max-width: 60ch;
		text-align: center;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.rule b {
		color: var(--color-ink);
		font-weight: 500;
	}
	.results {
		display: grid;
		gap: 8px;
		width: min(100%, 520px);
		margin-top: 6px;
	}
	.r-head,
	.r-row {
		display: grid;
		grid-template-columns: 86px minmax(0, 1fr) 54px;
		gap: 12px;
		align-items: center;
	}
	.r-head {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.r-head .num,
	.solver {
		text-align: right;
	}
	.d {
		font-size: var(--text-sm);
		color: var(--color-ink-2);
	}
	.track {
		position: relative;
		display: flex;
		align-items: center;
		gap: 8px;
		height: 14px;
	}
	.bar {
		height: 10px;
		min-width: 2px;
		border-radius: 1px;
		background: var(--color-ink);
	}
	.v,
	.solver {
		font-size: var(--text-sm);
		color: var(--color-ink);
	}
	@media (max-width: 640px) {
		.pairs {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
		.pair.test {
			padding-left: 0;
			border-left: 0;
		}
	}
</style>
