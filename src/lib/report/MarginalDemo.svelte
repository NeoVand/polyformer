<script lang="ts">
	/**
	 * Theorem 1, live: draw a random score built only from proper subsets of a
	 * triple over G = Z_3^2 and evaluate it on all 729 triples. The matching triples
	 * (sum zero) and the others have the same mean, whatever was drawn. Adding a
	 * genuinely three-way term separates them.
	 */
	import MathTex from '#lib/ui/Math.svelte';
	import { mulberry32 } from '#lib/set/rng.ts';

	const Q = 9;
	const add = (a: number, b: number) =>
		(((a % 3) + (b % 3)) % 3) + 3 * ((Math.floor(a / 3) + Math.floor(b / 3)) % 3);
	const cos3 = (a: number, b: number, c: number) => Math.cos((2 * Math.PI * (a + b + c)) / 3);
	let seed = $state(1);
	let threeWay = $state(false);

	const sample = $derived.by(() => {
		const rng = mulberry32(seed * 977 + 13);
		const gauss = () => {
			const u = Math.max(1e-12, rng());
			return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rng());
		};
		const table = (size: number) => Array.from({ length: size }, gauss);
		// one function per proper subset of the three roles
		const f1 = [table(Q), table(Q), table(Q)];
		const f2 = [table(Q * Q), table(Q * Q), table(Q * Q)];
		const pts: { v: number; y: boolean }[] = [];
		for (let a = 0; a < Q; a++)
			for (let b = 0; b < Q; b++)
				for (let c = 0; c < Q; c++) {
					let v =
						f1[0][a] + f1[1][b] + f1[2][c] + f2[0][a * Q + b] + f2[1][a * Q + c] + f2[2][b * Q + c];
					// the hand-built cubic head: a cosine of the sum, per attribute, reads all three at once
					if (threeWay)
						v +=
							1.5 *
							(cos3(a % 3, b % 3, c % 3) +
								cos3(Math.floor(a / 3), Math.floor(b / 3), Math.floor(c / 3)));
					pts.push({ v, y: add(add(a, b), c) === 0 });
				}
		const mean = (ys: boolean) => {
			const s = pts.filter((p) => p.y === ys);
			return s.reduce((t, p) => t + p.v, 0) / s.length;
		};
		const lo = Math.min(...pts.map((p) => p.v));
		const hi = Math.max(...pts.map((p) => p.v));
		return { pts, m1: mean(true), m0: mean(false), lo, hi };
	});

	const W = 560;
	const x = (v: number) => 12 + ((v - sample.lo) / (sample.hi - sample.lo || 1)) * (W - 24);
	const jitter = (i: number) => ((i * 2654435761) % 1000) / 1000;
</script>

<figure class="demo">
	<svg
		viewBox="0 0 {W} 150"
		role="img"
		aria-label="Scores of matching and non-matching triples, with their means"
	>
		<text x="0" y="16" class="lab">Matching triples (81)</text>
		<text x="0" y="96" class="lab">Other triples (648)</text>
		{#each sample.pts as p, i (i)}
			<circle cx={x(p.v)} cy={(p.y ? 34 : 112) + jitter(i) * 22} r="1.6" class:y={p.y} />
		{/each}
		<line x1={x(sample.m1)} x2={x(sample.m1)} y1="26" y2="62" class="mean" />
		<line x1={x(sample.m0)} x2={x(sample.m0)} y1="104" y2="140" class="mean" />
	</svg>
	<div class="controls">
		<button onclick={() => (seed += 1)}>Draw another score</button>
		<label
			><input type="checkbox" bind:checked={threeWay} /> add the cubic head's three-way term</label
		>
		<span class="num read">
			means <MathTex tex={String.raw`\bar f_{\text{match}} = ${sample.m1.toFixed(4)}`} />,
			<MathTex tex={String.raw`\bar f_{\text{other}} = ${sample.m0.toFixed(4)}`} />
		</span>
	</div>
	<figcaption>
		Every triple of <MathTex tex={String.raw`G=\mathbb Z_3^2`} />, scored by a random sum of
		functions of one or two of its elements. The two clouds differ in shape, but their means
		coincide for every draw (lines), as Theorem 1 says. Only a term that reads all three elements at
		once moves one mean away from the other.
	</figcaption>
</figure>

<style>
	.demo {
		margin: 18px 0 24px;
	}
	svg {
		display: block;
		width: 100%;
		height: auto;
	}
	.lab {
		font-size: 11px;
		fill: var(--color-ink-3);
	}
	circle {
		fill: #6b6b6b;
		opacity: 0.55;
	}
	circle.y {
		fill: #f2f2f2;
		opacity: 0.8;
	}
	.mean {
		stroke: #fff;
		stroke-width: 1.5;
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px 16px;
		margin-top: 8px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
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
	label {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		cursor: pointer;
	}
	.read {
		margin-left: auto;
	}
	figcaption {
		margin-top: 10px;
		font-size: var(--text-xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
</style>
