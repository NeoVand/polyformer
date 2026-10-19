<script lang="ts">
	import { resolve } from '$app/paths';
	import { getBench, TOTAL_STEPS } from '#lib/engine/bench.svelte.ts';
	import { EVIDENCE, MODELS, TASKS, type Cell } from '#lib/notes/evidence.ts';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { Book, Chip, Flask, Grid, Note } from '#lib/ui/icons.ts';

	const bench = getBench();
	let section = $state('evidence');

	const session = $derived.by(() => {
		void bench.version;
		return bench.runs.map((r) => {
			const h = bench.history[r.id];
			return { id: r.id, label: r.label, step: h.step, acc: h.evalAccuracy.at(-1), ms: h.msMedian };
		});
	});
	const anyTrained = $derived(session.some((s) => s.step > 0));

	/** Best accuracy per task, to mark the winners in each column. */
	const best = Object.fromEntries(
		TASKS.map((t) => [t.id, Math.max(...Object.values(EVIDENCE[t.id]).map((c) => c?.acc ?? 0))])
	);
	const shade = (c: Cell) => Math.round(24 + Math.pow(c.acc, 2.2) * 200);
	let hovered = $state<{ model: string; task: string } | null>(null);
</script>

<svelte:head>
	<title>Notes | Polyformer</title>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'evidence', label: 'Evidence', icon: Grid },
		{ id: 'session', label: 'Session', icon: Flask },
		{ id: 'claims', label: 'Claims', icon: Note },
		{ id: 'context', label: 'Related', icon: Book },
		{ id: 'build', label: 'Runtime', icon: Chip }
	]}
	active={section}
	onselect={(id) => (section = id)}
>
	<div class="notes">
		<article class="text">
			<header>
				<h1>Research log</h1>
				<p class="lede">
					What the demo measures, what it does not, and where the idea sits among related work. Every accuracy the
					project has measured is in the matrix, with where it came from.
				</p>
			</header>

			<section id="claims">
				<h2>What the evidence shows</h2>
				<ul>
					<li>
						On SET, one cubic layer goes from chance to 100% held-out accuracy, all tables right, within about 500
						steps in this browser. Strassen reaches 95.8%, the Columbia tree 76.4%, and standard attention stays near
						the majority rate after {TOTAL_STEPS.toLocaleString('en-US')} steps.
					</li>
					<li>
						Order matters, not just size. Four-card SET defeats every model whose logit is at most cubic, including
						DS-PA; a quartic head learns it. Deciding whether <MathTex tex="k" /> tokens match needs a
						<MathTex tex="k" />-way term.
					</li>
					<li>
						On pointer chasing, where each example needs one to three hops, one DS-PA layer reaches 100%. Three
						standard layers reach 94.2% and one cubic layer 84.5%. The trained model's computation tree follows the
						true pointer path round by round; see
						<a href={resolve('/explore/diagrams')}>Diagrams</a>.
					</li>
					<li>
						The cubic layer costs more per step. The compute axis on the <a href={resolve('/compare')}>bench</a>
						plots accuracy against training FLOPs so the comparison is per unit of compute, not just per step.
					</li>
				</ul>
				<h3>What it does not show</h3>
				<ul>
					<li>
						A general win. On three-hop composition an untied hyperchain and two standard layers succeed while every
						tied triple mechanism, DS-PA included, stalls near 60%.
					</li>
					<li>
						Robustness. Most numbers are one seed; the SET ordering held on two seeds offline. Change the seed on
						the bench to check it yourself.
					</li>
					<li>
						Scale. The sequences have 13 or 14 tokens; the <MathTex tex="O(n^3 d)" /> cost matters at length and
						needs sparse or windowed variants.
					</li>
				</ul>
			</section>

			<section id="session">
				<h2>This session</h2>
				{#if anyTrained}
					<table>
						<thead>
							<tr><th>Model</th><th class="r">Step</th><th class="r">Held-out accuracy</th><th class="r">Time / step</th></tr>
						</thead>
						<tbody>
							{#each session as s (s.id)}
								<tr>
									<td>{s.label}</td>
									<td class="r num">{s.step.toLocaleString('en-US')} / {TOTAL_STEPS.toLocaleString('en-US')}</td>
									<td class="r num">{pct(s.acc)}</td>
									<td class="r num">{s.ms ? `${s.ms.toFixed(1)} ms` : '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
					<p class="hint">Backend: {bench.device ?? 'not started'}, seed {bench.seed}.</p>
				{:else}
					<p>
						Nothing has trained in this tab yet. Start the <a href={resolve('/compare')}>bench</a>; the numbers you
						produce show up here.
					</p>
				{/if}
			</section>

			<section id="context">
				<h2>Related work</h2>
				<p>
					The operator, trilinear scores over a query and an ordered key pair with Hadamard pair values, is the
					2-simplicial family: Clift et al. (ICLR 2020), Sanford et al. (2023) and Roy et al. (2025, “Fast and
					Simplex”). Polyformer is an independent 2023 derivation of the same idea, revisited here with tasks where
					degree matters.
				</p>
				<p>
					Columbia's poly-attention (arXiv 2602.02422) studies attention over graphs of token roles. The tree and
					Strassen baselines follow its definition, with Hadamard values indexed at the key positions
					<MathTex tex="j" /> and <MathTex tex="k" />. Its released implementation indexes one value at the query
					instead, which drops SET to chance with the same scores. All of these are degree 2 in the token features,
					which is what the <a href={resolve('/learn')}>coupling barrier</a> is about.
				</p>
				<p>
					DS-PA borrows its structure from the Dyson–Schwinger equations of quantum field theory, whose iteration
					generates Feynman diagrams: a state is a weighted sum of trees of interactions, and the weights are learned.
				</p>
			</section>

			<section id="build">
				<h2>How it runs</h2>
				<ul>
					<li>
						jax-js trains every model in a module Web Worker, on WebGPU when the browser offers it and WebAssembly
						otherwise. Nothing leaves the page.
					</li>
					<li>
						Scores and values are batched GEMMs, <MathTex tex={'(Q_i \\odot K^1)K^{2\\top}'} /> and
						<MathTex tex="P_i V^2" />, so no <MathTex tex="n^3 d" /> tensor is built. AdamW, clipping and the schedule
						are fused into one compiled step per model.
					</li>
					<li>
						The batch for step <MathTex tex="s" /> is a pure function of the seed and <MathTex tex="s" />, so every
						model sees identical data even when trained at different times.
					</li>
				</ul>
			</section>
		</article>

		<aside class="matrix" id="evidence" aria-label="Evidence matrix">
			<h2>Evidence matrix</h2>
			<p class="m-sub">Held-out token accuracy. Brighter is better; the ringed cell is the best in its column.</p>
			<div class="grid" style:--cols={TASKS.length}>
				<span></span>
				{#each TASKS as t (t.id)}
					<span class="col-head" class:on={hovered?.task === t.id}><b>{t.label}</b><small>{t.detail}</small></span>
				{/each}
				{#each MODELS as m (m.id)}
					<span class="row-head" class:on={hovered?.model === m.id}>{m.label}</span>
					{#each TASKS as t (t.id)}
						{@const c = EVIDENCE[t.id][m.id]}
						{#if c}
							<span
								class="cell num"
								class:win={c.acc === best[t.id]}
								class:harness={c.source === 'harness'}
								style:--g={shade(c)}
								role="img"
								aria-label="{m.label} on {t.label}: {pct(c.acc, 1)}, {c.source === 'browser'
									? 'measured in the browser'
									: 'offline harness'}"
								onpointerenter={() => (hovered = { model: m.id, task: t.id })}
								onpointerleave={() => (hovered = null)}>{c.approx ? '≈' : ''}{pct(c.acc, 0)}</span
							>
						{:else}
							<span class="cell empty" aria-label="Not run">·</span>
						{/if}
					{/each}
				{/each}
			</div>
			<div class="legend">
				<span><i class="swatch"></i>Measured in this browser's engine</span>
				<span><i class="swatch harness"></i>Offline research harness</span>
				<span><b>≈</b> stalled at the majority rate</span>
			</div>
		</aside>
	</div>
</PageFrame>

<style>
	.notes {
		display: grid;
		grid-template-columns: minmax(0, 580px) minmax(0, 1fr);
		gap: 48px;
		padding: 0 32px 0 40px;
	}
	.text {
		padding: 36px 0 120px;
	}
	header {
		padding-bottom: 6px;
	}
	h1 {
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 38px;
		font-weight: 400;
		line-height: 1.1;
	}
	.lede {
		margin-top: 12px;
		font-size: 15px;
		line-height: 1.6;
		color: var(--color-ink-2);
	}
	section {
		padding: 26px 0 6px;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	section:last-child {
		border-bottom: 0;
	}
	h2 {
		font-size: 19px;
		font-weight: 500;
		letter-spacing: -0.015em;
		margin-bottom: 12px;
	}
	h3 {
		font-size: 14px;
		font-weight: 500;
		margin: 16px 0 8px;
	}
	p,
	li {
		color: var(--color-ink-2);
		font-size: 15px;
		line-height: 1.7;
	}
	p {
		margin: 0 0 14px;
	}
	ul {
		margin: 0 0 12px;
		padding-left: 18px;
		list-style: none;
	}
	li {
		position: relative;
		margin-bottom: 10px;
	}
	li::before {
		content: '';
		position: absolute;
		left: -16px;
		top: 0.8em;
		width: 6px;
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
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		padding: 6px 10px 6px 0;
		border-bottom: 1px solid var(--color-edge);
	}
	td {
		padding: 8px 10px 8px 0;
		border-bottom: 1px solid var(--color-lift);
		color: var(--color-ink-2);
	}
	.r {
		text-align: right;
	}

	/* the evidence matrix */
	.matrix {
		position: sticky;
		top: calc(var(--bar-h) + 28px);
		align-self: start;
		margin-top: 36px;
		scroll-margin-top: calc(var(--bar-h) + 16px);
	}
	.m-sub {
		font-size: var(--text-sm);
		margin-bottom: 18px;
	}
	.grid {
		display: grid;
		grid-template-columns: 132px repeat(var(--cols), minmax(64px, 1fr));
		gap: 4px;
		align-items: stretch;
	}
	.col-head {
		display: grid;
		align-content: end;
		gap: 2px;
		padding: 0 4px 8px;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
		transition: color 120ms ease;
	}
	.col-head b {
		font-weight: 500;
	}
	.col-head small {
		font-size: 11px;
		color: var(--color-ink-3);
		line-height: 1.3;
	}
	.row-head {
		display: flex;
		align-items: center;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
		transition: color 120ms ease;
	}
	.col-head.on,
	.row-head.on {
		color: var(--color-ink);
	}
	.cell {
		display: grid;
		place-items: center;
		height: 32px;
		border-radius: 4px;
		background: rgb(var(--g) var(--g) var(--g));
		color: rgb(8 8 8);
		font-size: var(--text-sm);
		font-weight: 500;
	}
	.cell:not(.empty) {
		color: var(--color-void);
	}
	.cell.harness {
		background: transparent;
		border: 1.5px solid rgb(var(--g) var(--g) var(--g));
		color: rgb(var(--g) var(--g) var(--g));
	}
	.cell.win {
		box-shadow:
			0 0 0 1.5px var(--color-void),
			0 0 0 2.5px var(--color-ink);
	}
	.cell.empty {
		background: transparent;
		color: var(--color-edge);
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 22px;
		margin-top: 18px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 8px;
	}
	.swatch {
		width: 14px;
		height: 14px;
		border-radius: 3px;
		background: var(--color-ink-2);
	}
	.swatch.harness {
		background: transparent;
		border: 1.5px solid var(--color-ink-2);
	}

	@media (max-width: 1200px) {
		.notes {
			grid-template-columns: minmax(0, 1fr);
			padding: 0 20px;
		}
		.matrix {
			position: static;
			order: -1;
			overflow-x: auto;
		}
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 36px;
		}
	}
</style>
