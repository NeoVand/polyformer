<script lang="ts">
	import { resolve } from '$app/paths';
	import { getBench, TOTAL_STEPS } from '#lib/engine/bench.svelte.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { Book, Chip, Flask, Note } from '#lib/ui/icons.ts';

	const bench = getBench();
	let section = $state('session');

	const session = $derived.by(() => {
		void bench.version;
		return bench.runs.map((r) => {
			const h = bench.history[r.id];
			return {
				id: r.id,
				label: r.label,
				step: h.step,
				acc: h.evalAccuracy.at(-1),
				ms: h.msMedian
			};
		});
	});
	const anyTrained = $derived(session.some((s) => s.step > 0));
</script>

<svelte:head>
	<title>Notes | Polyformer</title>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'session', label: 'This session', icon: Flask },
		{ id: 'claims', label: 'What the bench shows', icon: Note },
		{ id: 'context', label: 'Related work', icon: Book },
		{ id: 'build', label: 'How it runs', icon: Chip }
	]}
	active={section}
	onselect={(id) => (section = id)}
>
	<article class="notes">
		<header>
			<h1 class="page-title">Research log</h1>
			<p class="lede">
				What the demo measures, what it does not, and where the idea sits among related work.
			</p>
		</header>

		<section id="session">
			<h2>This session</h2>
			{#if anyTrained}
				<table>
					<thead>
						<tr
							><th>Model</th><th class="r">Step</th><th class="r">Held-out token acc.</th><th
								class="r">Time / step</th
							></tr
						>
					</thead>
					<tbody>
						{#each session as s (s.id)}
							<tr>
								<td>{s.label}</td>
								<td class="r num"
									>{s.step.toLocaleString('en-US')} / {TOTAL_STEPS.toLocaleString('en-US')}</td
								>
								<td class="r num">{pct(s.acc)}</td>
								<td class="r num">{s.ms ? `${s.ms.toFixed(1)} ms` : '—'}</td>
							</tr>
						{/each}
					</tbody>
				</table>
				<p class="hint">Backend: {bench.device ?? 'not started'}, seed {bench.seed}.</p>
			{:else}
				<p>
					Nothing has trained yet in this tab. Start the <a href={resolve('/compare')}>SET bench</a
					>; the numbers you produce show up here.
				</p>
			{/if}
		</section>

		<section id="claims">
			<h2>What the bench shows</h2>
			<ul>
				<li>
					On SET membership with 12 cards, one cubic layer goes from chance to near-perfect held-out
					accuracy within about a thousand steps. Strassen, tree and standard attention, with the
					same width, data and optimizer, stay well below it after {TOTAL_STEPS.toLocaleString(
						'en-US'
					)}
					steps. In earlier offline runs this held on two seeds.
				</li>
				<li>
					Every number on the bench is produced in your browser from the seed shown. Change the seed
					to check that the ordering is not luck.
				</li>
				<li>
					The cubic layer costs more per step. The compute axis on the bench plots accuracy against
					training FLOPs so the comparison is per unit of compute, not just per step.
				</li>
			</ul>
			<h3>What it does not show</h3>
			<ul>
				<li>
					A general win. On two-hop composition every one-layer triple mechanism solves the task;
					cubic attention helps where the task needs a query-dependent three-way relation.
				</li>
				<li>
					Scale. The sequences here have 13 tokens; the <MathTex tex="O(n^3 d)" /> cost matters at length
					and needs sparse or windowed variants.
				</li>
			</ul>
		</section>

		<section id="context">
			<h2>Related work</h2>
			<p>
				The operator, trilinear scores over a query and an ordered key pair with Hadamard pair
				values, is the 2-simplicial family: Clift et al. (ICLR 2020), Sanford et al. (2023) and Roy
				et al. (2025, “Fast and Simplex”). Polyformer is an independent 2023 derivation of the same
				idea, revisited here with a concrete task where degree matters.
			</p>
			<p>
				Columbia’s poly-attention (arXiv 2602.02422) studies attention over graphs of token roles.
				The tree and Strassen baselines here follow its definition, with Hadamard values indexed at
				the key positions <MathTex tex="j" /> and <MathTex tex="k" />. All of them are degree 2 in
				the token features, which is the property the
				<a href={resolve('/learn')}>coupling barrier</a>
				is about.
			</p>
		</section>

		<section id="build">
			<h2>How it runs</h2>
			<ul>
				<li>
					jax-js trains every model in a module Web Worker, on WebGPU when the browser offers it and
					WebAssembly otherwise. Nothing leaves the page.
				</li>
				<li>
					Scores and values are batched GEMMs, <MathTex tex={'(Q_i \\odot K^1)K^{2\\top}'} /> and
					<MathTex tex="P_i V^2" />, so no <MathTex tex="n^3 d" /> tensor is built. AdamW, clipping and
					the schedule are fused into one compiled step per model.
				</li>
				<li>
					The batch for step <MathTex tex="s" /> is a pure function of the seed and
					<MathTex tex="s" />, so every model sees identical data even when trained at different
					times.
				</li>
			</ul>
		</section>
	</article>
</PageFrame>

<style>
	.notes {
		max-width: 760px;
		padding: 28px 28px 80px 40px;
	}
	header {
		padding-bottom: 18px;
		border-bottom: 1px solid var(--color-edge);
	}
	section {
		padding: 22px 0 8px;
		border-bottom: 1px solid #1c1c1c;
		scroll-margin-top: calc(var(--bar-h) + 12px);
	}
	section:last-child {
		border-bottom: 0;
	}
	h2 {
		font-size: var(--text-lg);
		font-weight: 500;
		margin-bottom: 10px;
	}
	h3 {
		font-size: var(--text-ui);
		font-weight: 500;
		margin: 14px 0 6px;
	}
	p,
	li {
		color: var(--color-ink-2);
		line-height: 1.65;
		max-width: 68ch;
	}
	p {
		margin: 0 0 12px;
	}
	ul {
		margin: 0 0 12px;
		padding-left: 18px;
		list-style: none;
	}
	li {
		position: relative;
		margin-bottom: 8px;
	}
	li::before {
		content: '';
		position: absolute;
		left: -14px;
		top: 0.72em;
		width: 5px;
		height: 1px;
		background: var(--color-rule);
	}
	a {
		color: var(--color-ink);
		text-decoration: underline;
		text-decoration-color: var(--color-rule);
		text-underline-offset: 3px;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
		margin-bottom: 8px;
	}
	th {
		text-align: left;
		font-weight: 400;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		padding: 6px 10px 6px 0;
		border-bottom: 1px solid #222;
	}
	td {
		padding: 7px 10px 7px 0;
		border-bottom: 1px solid #1c1c1c;
		color: var(--color-ink-2);
	}
	.r {
		text-align: right;
	}
	@media (max-width: 760px) {
		.notes {
			padding: 18px 16px 60px;
		}
	}
</style>
