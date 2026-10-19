<script lang="ts">
	import { getBench, TOTAL_STEPS, BATCH, EVAL_LAYOUTS } from '#lib/engine/bench.svelte.ts';
	import { evalPositiveRate, firstLayoutOfBatch } from '#lib/engine/data.ts';
	import { getOperator } from '#lib/model/operators/index.ts';
	import { setMembership } from '#lib/set/cards.ts';
	import Icon from '#lib/ui/Icon.svelte';
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { compact, duration, flops, ms, pct } from '#lib/ui/format.ts';
	import { Cards, Compare, Layers, Pause, Play, Reset, Timer } from '#lib/ui/icons.ts';

	const bench = getBench();

	type Axis = 'steps' | 'compute';
	let axis = $state<Axis>('steps');
	let section = $state('bench');

	const positive = evalPositiveRate(EVAL_LAYOUTS);
	const majority = Math.max(positive, 1 - positive);

	const running = $derived(bench.status === 'training' || bench.status === 'pausing');
	const finished = $derived(bench.step >= TOTAL_STEPS);
	const flopsOf = (id: string) => bench.runInfo(id)?.trainFlopsPerStep ?? 0;
	const maxFlops = $derived(Math.max(1, ...bench.info.map((r) => r.trainFlopsPerStep)));

	/** Scale x for the compute axis, in TFLOP. */
	const xs = (id: string, steps: number[]) =>
		axis === 'steps' ? steps : steps.map((s) => (s * flopsOf(id)) / 1e12);

	function ema(values: number[], alpha = 0.06): number[] {
		const out = new Array<number>(values.length);
		let m = values[0] ?? 0;
		for (let i = 0; i < values.length; i++) {
			m = i ? m + alpha * (values[i] - m) : values[i];
			out[i] = m;
		}
		return out;
	}

	const accuracySeries = $derived.by((): Series[] => {
		void bench.version;
		return bench.runs.map((r) => ({
			id: r.id,
			label: r.label,
			tone: r.tone,
			dash: r.dash,
			emphasis: r.id === 'cubic',
			xs: xs(r.id, bench.history[r.id].evalSteps),
			ys: bench.history[r.id].evalAccuracy
		}));
	});
	const layoutSeries = $derived.by((): Series[] => {
		void bench.version;
		return bench.runs.map((r) => ({
			id: r.id,
			label: r.label,
			tone: r.tone,
			dash: r.dash,
			emphasis: r.id === 'cubic',
			xs: xs(r.id, bench.history[r.id].evalSteps),
			ys: bench.history[r.id].evalLayout
		}));
	});
	const lossSeries = $derived.by((): Series[] => {
		void bench.version;
		return bench.runs.map((r) => ({
			id: r.id,
			label: r.label,
			tone: r.tone,
			dash: r.dash,
			emphasis: r.id === 'cubic',
			xs: xs(r.id, bench.history[r.id].steps),
			ys: ema(bench.history[r.id].loss)
		}));
	});

	const xMax = $derived(axis === 'steps' ? TOTAL_STEPS : (TOTAL_STEPS * maxFlops) / 1e12);
	const xLabel = $derived(axis === 'steps' ? 'Step' : 'Training compute, TFLOP');
	const formatX = $derived(
		axis === 'steps' ? (v: number) => String(Math.round(v)) : (v: number) => v.toFixed(1)
	);

	const rows = $derived.by(() => {
		void bench.version;
		return bench.runs.map((r) => {
			const h = bench.history[r.id];
			const info = bench.runInfo(r.id);
			const hit = h.evalAccuracy.findIndex((a) => a >= 0.95);
			return {
				spec: r,
				op: getOperator(r.operator),
				params: info?.params,
				flops: info?.trainFlopsPerStep,
				ms: h.msMedian,
				step: h.step,
				token: h.evalAccuracy.at(-1),
				layout: h.evalLayout.at(-1),
				reached: hit >= 0 ? h.evalSteps[hit] : undefined
			};
		});
	});

	// The shared input: the first layout of the batch the models are seeing now.
	const shownStep = $derived(Math.floor(bench.step / 25) * 25);
	const layout = $derived(firstLayoutOfBatch(bench.seed, shownStep));
	const members = $derived(setMembership(layout));
	const memberCount = $derived(members.filter(Boolean).length);

	function toggle() {
		if (running) bench.pause();
		else bench.start();
	}

	const primaryLabel = $derived(
		bench.status === 'booting'
			? 'Starting…'
			: running
				? bench.status === 'pausing'
					? 'Pausing…'
					: 'Pause'
				: finished
					? 'Finished'
					: bench.step > 0
						? 'Resume'
						: 'Start training'
	);

	function changeSeed(delta: number) {
		bench.reset(Math.max(0, bench.seed + delta));
	}
</script>

<svelte:head>
	<title>SET bench | Polyformer</title>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'bench', label: 'Learning curves', icon: Compare },
		{ id: 'runs', label: 'Runs', icon: Layers },
		{ id: 'task', label: 'Shared input', icon: Cards }
	]}
	active={section}
	onselect={(id) => (section = id)}
>
	<div class="page">
		<header class="head">
			<div>
				<h1 class="page-title">SET bench</h1>
				<p class="lede">
					Five attention mechanisms learn the same task from identical batches, trained live in this
					browser. Only the attention operator differs.
				</p>
			</div>
			<dl class="spec">
				<div>
					<dt>Batch</dt>
					<dd class="num">{BATCH} layouts</dd>
				</div>
				<div>
					<dt>Steps</dt>
					<dd class="num">{TOTAL_STEPS.toLocaleString('en-US')}</dd>
				</div>
				<div>
					<dt>Optimizer</dt>
					<dd>AdamW, 2e-3, cosine</dd>
				</div>
				<div>
					<dt>Held out</dt>
					<dd class="num">{EVAL_LAYOUTS.toLocaleString('en-US')} layouts</dd>
				</div>
			</dl>
		</header>

		<div class="body">
			<section class="charts" id="bench" aria-label="Learning curves">
				<div class="panel">
					<div class="panel-head">
						<div class="panel-title">
							<Icon icon={Compare} size={16} />Held-out token accuracy
						</div>
						<div class="seg" role="group" aria-label="Horizontal axis">
							<button aria-pressed={axis === 'steps'} onclick={() => (axis = 'steps')}>Steps</button
							>
							<button aria-pressed={axis === 'compute'} onclick={() => (axis = 'compute')}
								>Compute</button
							>
						</div>
					</div>
					<div class="chart-pad">
						<LineChart
							label="Held-out token accuracy by training step"
							series={accuracySeries}
							version={bench.version}
							{xMax}
							{xLabel}
							{formatX}
							yMin={0.4}
							yMax={1}
							yTicks={[0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]}
							formatY={(v) => pct(v, 0)}
							reference={{ y: majority, label: `Majority class ${pct(majority)}` }}
							height={300}
						/>
					</div>
				</div>

				<div class="pair">
					<div class="panel">
						<div class="panel-head">
							<div class="panel-title">Training loss</div>
							<span class="hint">Cross-entropy, smoothed, log scale</span>
						</div>
						<div class="chart-pad">
							<LineChart
								label="Training loss by step"
								series={lossSeries}
								version={bench.version}
								{xMax}
								{xLabel}
								{formatX}
								log
								yMin={1e-4}
								yMax={1}
								yTicks={[1e-4, 1e-3, 1e-2, 1e-1, 1]}
								formatY={(v) => (v >= 0.01 ? v.toFixed(2) : v.toExponential(0))}
								height={200}
							/>
						</div>
					</div>
					<div class="panel">
						<div class="panel-head">
							<div class="panel-title">Layouts fully correct</div>
							<span class="hint">All 12 cards right</span>
						</div>
						<div class="chart-pad">
							<LineChart
								label="Share of held-out layouts with every card correct"
								series={layoutSeries}
								version={bench.version}
								{xMax}
								{xLabel}
								{formatX}
								yMin={0}
								yMax={1}
								yTicks={[0, 0.25, 0.5, 0.75, 1]}
								formatY={(v) => pct(v, 0)}
								height={200}
							/>
						</div>
					</div>
				</div>

				<div class="panel" id="runs">
					<div class="panel-head">
						<div class="panel-title"><Icon icon={Layers} size={16} />Runs</div>
						<span class="hint">d = 64, 4 heads, one block unless noted</span>
					</div>
					<div class="table-wrap">
						<table>
							<thead>
								<tr>
									<th class="check"><span class="sr">Train</span></th>
									<th>Model</th>
									<th>Scores</th>
									<th class="r">Params</th>
									<th class="r">Compute / step</th>
									<th class="r">Time / step</th>
									<th class="r">Step</th>
									<th class="r">Token acc.</th>
									<th class="r">Layouts</th>
									<th class="r">Reached 95%</th>
								</tr>
							</thead>
							<tbody>
								{#each rows as row (row.spec.id)}
									<tr class={{ lead: row.spec.id === 'cubic' }}>
										<td class="check">
											<input
												type="checkbox"
												aria-label="Train {row.spec.label}"
												bind:checked={bench.enabled[row.spec.id]}
												disabled={running}
											/>
										</td>
										<td>
											<span class="model">
												<svg width="22" height="8" aria-hidden="true">
													<line
														x1="0"
														y1="4"
														x2="22"
														y2="4"
														stroke="rgb({70 + row.spec.tone * 175} {70 + row.spec.tone * 175} {70 +
															row.spec.tone * 175})"
														stroke-width={row.spec.id === 'cubic' ? 2 : 1.5}
														stroke-dasharray={row.spec.dash}
													/>
												</svg>
												{row.spec.label}
											</span>
										</td>
										<td class="tex"><MathTex tex={row.op.logitTex} /></td>
										<td class="r num">{row.params ? compact(row.params) : '—'}</td>
										<td class="r num">{row.flops ? flops(row.flops) : '—'}</td>
										<td class="r num">{ms(row.ms)}</td>
										<td class="r num">{row.step.toLocaleString('en-US')}</td>
										<td class="r num strong">{pct(row.token)}</td>
										<td class="r num">{pct(row.layout)}</td>
										<td class="r num">{row.reached ? `step ${row.reached}` : '—'}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			</section>

			<aside class="task panel" id="task" aria-label="Shared input">
				<div class="panel-head">
					<div class="panel-title"><Icon icon={Cards} size={16} />Shared input</div>
					<span class="hint num">batch {shownStep}</span>
				</div>
				<div class="task-body">
					<p class="task-q">For each card: is it part of any SET on the table?</p>
					<div class="cards">
						{#each layout as card, i (i)}
							<div class={['slot', members[i] && 'in']}>
								<SetCard {card} width={64} dim={!members[i]} />
								<span class="mark" aria-label={members[i] ? 'in a SET' : 'not in a SET'}></span>
							</div>
						{/each}
					</div>
					<p class="hint">
						{memberCount} of 12 cards belong to a SET. Every model sees this layout, plus {BATCH -
							1}
						more, at this step.
					</p>
					<div class="rule">
						<p>Three cards form a SET when each attribute is all the same or all different.</p>
						<MathTex display tex={'a + b + c \\equiv 0 \\pmod 3 \\ \\text{in every attribute}'} />
					</div>
				</div>
			</aside>
		</div>

		<footer class="transport" aria-label="Training controls">
			<button
				class="btn icon-only"
				onclick={() => bench.reset()}
				disabled={bench.status === 'booting'}
				title="Reset to step 0"
				aria-label="Reset to step 0"
			>
				<Icon icon={Reset} size={16} />
			</button>
			<button
				class="btn primary go"
				onclick={toggle}
				disabled={bench.status === 'booting' ||
					bench.status === 'pausing' ||
					(finished && !running)}
			>
				<Icon icon={running ? Pause : Play} size={16} />{primaryLabel}
			</button>

			<div class="progress" aria-label="Training progress">
				<div class="bar">
					<div class="fill" style:width="{(bench.step / TOTAL_STEPS) * 100}%"></div>
				</div>
				<span class="num"
					>{bench.step.toLocaleString('en-US')} / {TOTAL_STEPS.toLocaleString('en-US')}</span
				>
			</div>

			<div class="seed">
				<span class="hint">Seed</span>
				<button
					class="btn icon-only ghost"
					aria-label="Previous seed"
					onclick={() => changeSeed(-1)}
					disabled={running || bench.seed === 0}>−</button
				>
				<span class="num seed-v">{bench.seed}</span>
				<button
					class="btn icon-only ghost"
					aria-label="Next seed"
					onclick={() => changeSeed(1)}
					disabled={running}>+</button
				>
			</div>

			<span class="elapsed hint num"
				><Icon icon={Timer} size={14} />{duration(bench.elapsedMs)}</span
			>

			{#if bench.error}
				<span class="error" role="alert">{bench.error}</span>
			{/if}
		</footer>
	</div>
</PageFrame>

<style>
	.page {
		display: flex;
		flex-direction: column;
		gap: 16px;
		padding: 20px 20px 0;
		min-height: calc(100dvh - var(--bar-h));
	}
	.head {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: 24px;
		flex-wrap: wrap;
	}
	.spec {
		display: flex;
		gap: 22px;
		margin: 0;
	}
	.spec div {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.spec dt {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.spec dd {
		margin: 0;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
	}
	.body {
		display: grid;
		grid-template-columns: minmax(0, 1fr) 300px;
		gap: 16px;
		align-items: start;
	}
	.charts {
		display: flex;
		flex-direction: column;
		gap: 16px;
		min-width: 0;
	}
	.pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
	}
	.chart-pad {
		padding: 14px 6px 14px 4px;
	}

	.table-wrap {
		overflow-x: auto;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-sm);
	}
	th {
		text-align: left;
		font-weight: 400;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		padding: 10px 12px 8px;
		border-bottom: 1px solid #222;
		white-space: nowrap;
	}
	td {
		padding: 9px 12px;
		border-bottom: 1px solid #1e1e1e;
		color: var(--color-ink-2);
		white-space: nowrap;
	}
	tr:last-child td {
		border-bottom: 0;
	}
	tr.lead td {
		color: var(--color-ink);
	}
	.r {
		text-align: right;
	}
	.strong {
		color: var(--color-ink);
	}
	.check {
		width: 28px;
		padding-right: 0;
	}
	.model {
		display: inline-flex;
		align-items: center;
		gap: 10px;
	}
	.tex {
		font-size: 12px;
	}
	input[type='checkbox'] {
		appearance: none;
		width: 14px;
		height: 14px;
		border: 1px solid var(--color-rule);
		border-radius: 3px;
		background: transparent;
		display: grid;
		place-items: center;
		cursor: pointer;
	}
	input[type='checkbox']:checked {
		background: var(--color-ink);
		border-color: var(--color-ink);
	}
	input[type='checkbox']:checked::after {
		content: '';
		width: 7px;
		height: 4px;
		border: 1.5px solid var(--color-void);
		border-top: 0;
		border-right: 0;
		transform: translateY(-1px) rotate(-45deg);
	}
	input[type='checkbox']:disabled {
		opacity: 0.5;
		cursor: default;
	}
	.sr {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
	}

	.task {
		position: sticky;
		top: calc(var(--bar-h) + 16px);
	}
	.task-body {
		display: flex;
		flex-direction: column;
		gap: 12px;
		padding: 14px;
	}
	.task-q {
		color: var(--color-ink);
	}
	.cards {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 8px 4px;
		justify-items: center;
	}
	.slot {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 5px;
	}
	.mark {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		border: 1px solid var(--color-rule);
	}
	.slot.in .mark {
		background: var(--color-ink);
		border-color: var(--color-ink);
	}
	.rule {
		padding-top: 12px;
		border-top: 1px solid #222;
		color: var(--color-ink-2);
		font-size: var(--text-sm);
	}

	.transport {
		position: sticky;
		bottom: 0;
		margin: auto -20px 0;
		display: flex;
		align-items: center;
		gap: 14px;
		height: 52px;
		padding: 0 20px;
		background: rgb(8 8 8 / 0.94);
		border-top: 1px solid var(--color-edge);
		backdrop-filter: blur(6px);
	}
	.go {
		min-width: 132px;
	}
	.progress {
		display: flex;
		align-items: center;
		gap: 10px;
		flex: 1;
		max-width: 420px;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
	}
	.progress .bar {
		flex: 1;
		height: 2px;
		background: var(--color-control);
	}
	.progress .fill {
		height: 100%;
		background: var(--color-ink);
	}
	.seed {
		display: flex;
		align-items: center;
		gap: 4px;
	}
	.seed-v {
		min-width: 18px;
		text-align: center;
	}
	.elapsed {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.error {
		font-size: var(--text-xs);
		color: var(--color-ink);
		border: 1px solid var(--color-rule);
		padding: 3px 8px;
		border-radius: var(--radius-ui);
	}

	@media (max-width: 1180px) {
		.body {
			grid-template-columns: minmax(0, 1fr);
		}
		.task {
			position: static;
		}
		.cards {
			grid-template-columns: repeat(6, 1fr);
		}
	}
	@media (max-width: 760px) {
		.pair {
			grid-template-columns: minmax(0, 1fr);
		}
		.spec {
			flex-wrap: wrap;
			gap: 12px 18px;
		}
		.cards {
			grid-template-columns: repeat(4, 1fr);
		}
		.page {
			padding: 16px 16px 0;
		}
		.transport {
			margin: auto -16px 0;
			padding: 0 16px;
			gap: 10px;
		}
		.seed,
		.elapsed {
			display: none;
		}
		.go {
			min-width: 0;
		}
	}
</style>
