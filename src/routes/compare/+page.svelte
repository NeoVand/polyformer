<script lang="ts">
	import { onMount } from 'svelte';
	import { asset, resolve } from '$app/paths';
	import type { ChaseInstance } from '#lib/chase/chase.ts';
	import { BATCH, EVAL_LAYOUTS, getBench, TOTAL_STEPS } from '#lib/engine/bench.svelte.ts';
	import { firstExampleOfBatch } from '#lib/engine/data.ts';
	import type { SuiteId } from '#lib/engine/runs.ts';
	import { getOperator } from '#lib/model/operators/index.ts';
	import { setMembership, type Card } from '#lib/set/cards.ts';
	import { zeroSumMembers } from '#lib/tasks/matchk.ts';
	import ChaseLists from '#lib/ui/ChaseLists.svelte';
	import Icon from '#lib/ui/Icon.svelte';
	import LineChart, { type Series } from '#lib/ui/LineChart.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { compact, duration, flops, ms, pct } from '#lib/ui/format.ts';
	import {
		Cards,
		Chip,
		Download,
		Matrix,
		Pause,
		Play,
		Reset,
		Timer,
		Workflow
	} from '#lib/ui/icons.ts';

	import GroupLadder from '#lib/report/GroupLadder.svelte';
	import CharactersResult from '#lib/report/CharactersResult.svelte';
	let groups = $state(false);
	let suite = $state<SuiteId>('set');
	function selectSuite(id: string) {
		groups = id === 'groups';
		if (!groups) {
			suite = id as SuiteId;
			loadRecording();
		}
	}
	const bench = $derived(getBench(suite));

	type Axis = 'steps' | 'compute';
	let axis = $state<Axis>('steps');
	let heroHeight = $state(340);

	// ── recorded runs: the same engine, run once in a browser and saved ──────
	interface RecordedRun {
		evalSteps: number[];
		evalAccuracy: number[];
		evalLayout: number[];
		steps: number[];
		loss: number[];
		msMedian: number;
		params?: number;
		flops?: number;
	}
	interface Recorded {
		suite: SuiteId;
		recordedAt: string;
		device: string;
		seed: number;
		runs: Record<string, RecordedRun>;
	}
	const RECORDINGS: Record<SuiteId, string> = {
		set: asset('recorded/set.json'),
		chase: asset('recorded/chase.json'),
		match4: asset('recorded/match4.json')
	};
	let recorded = $state.raw<Recorded | null>(null);
	let recordingRequest = 0;
	function loadRecording() {
		const request = ++recordingRequest;
		recorded = null;
		fetch(RECORDINGS[suite])
			.then((r) => (r.ok ? r.json() : null))
			.then((j: Recorded | null) => {
				if (request === recordingRequest && j?.runs) recorded = j;
			})
			.catch(() => {});
	}
	onMount(() => {
		loadRecording();
		return () => {
			recordingRequest++;
		};
	});

	const running = $derived(bench.status === 'training' || bench.status === 'pausing');
	const finished = $derived(bench.step >= TOTAL_STEPS);
	const live = $derived.by(() => {
		void bench.version;
		return bench.runs.some((r) => bench.history[r.id].evalSteps.length > 0);
	});
	const flopsOf = (id: string) =>
		bench.runInfo(id)?.trainFlopsPerStep ?? recorded?.runs[id]?.flops ?? 0;
	const maxFlops = $derived(Math.max(1, ...bench.runs.map((r) => flopsOf(r.id))));
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

	/** Live series plus a recorded ghost for every run that has one. */
	function seriesOf(
		pick: (h: { steps: number[]; ys: number[] }) => number[],
		which: 'acc' | 'layout' | 'loss'
	) {
		void bench.version;
		const out: Series[] = [];
		for (const r of bench.runs) {
			const h = bench.history[r.id];
			const rec = recorded?.runs[r.id];
			const base = { id: r.id, label: r.label, tone: r.tone, dash: r.dash, emphasis: r.tone === 1 };
			const [currentSteps, currentValues] =
				which === 'acc'
					? [h.evalSteps, h.evalAccuracy]
					: which === 'layout'
						? [h.evalSteps, h.evalLayout]
						: [h.steps, h.loss];
			if (rec) {
				const [st, ys] =
					which === 'acc'
						? [rec.evalSteps, rec.evalAccuracy]
						: which === 'layout'
							? [rec.evalSteps, rec.evalLayout]
							: [rec.steps, rec.loss];
				out.push({
					...base,
					ghost: currentSteps.length > 0,
					xs: xs(r.id, st),
					ys: pick({ steps: st, ys })
				});
			}
			if (currentSteps.length) {
				out.push({
					...base,
					xs: xs(r.id, currentSteps),
					ys: pick({ steps: currentSteps, ys: currentValues })
				});
			}
		}
		return out;
	}
	const accuracySeries = $derived(seriesOf((h) => h.ys, 'acc'));
	const layoutSeries = $derived(seriesOf((h) => h.ys, 'layout'));
	const lossSeries = $derived(seriesOf((h) => ema(h.ys), 'loss'));

	const xMax = $derived(axis === 'steps' ? TOTAL_STEPS : (TOTAL_STEPS * maxFlops) / 1e12);
	const xLabel = $derived(axis === 'steps' ? 'Training step' : 'Training compute, TFLOP');
	const formatX = $derived(
		axis === 'steps' ? (v: number) => v.toLocaleString('en-US') : (v: number) => v.toFixed(1)
	);
	const majority = $derived(bench.majority);

	// ── the leaderboard ──────────────────────────────────────────────────────
	const rows = $derived.by(() => {
		void bench.version;
		return bench.runs.map((r) => {
			const h = bench.history[r.id];
			const rec = recorded?.runs[r.id];
			const isLive = h.evalSteps.length > 0;
			const accs = isLive ? h.evalAccuracy : (rec?.evalAccuracy ?? []);
			const steps = isLive ? h.evalSteps : (rec?.evalSteps ?? []);
			const hit = accs.findIndex((a) => a >= 0.95);
			return {
				spec: r,
				op: getOperator(r.operator),
				params: bench.runInfo(r.id)?.params ?? rec?.params,
				flops: bench.runInfo(r.id)?.trainFlopsPerStep ?? rec?.flops,
				ms: isLive ? h.msMedian : (rec?.msMedian ?? 0),
				acc: accs.at(-1),
				isLive,
				recordedOnly: !isLive && !!rec,
				reached: hit >= 0 ? steps[hit] : undefined
			};
		});
	});
	const best = $derived(Math.max(0, ...rows.map((r) => r.acc ?? 0)));

	// ── the shared input: the first example of the batch every model sees now ─
	const shownStep = $derived(Math.floor(bench.step / 25) * 25);
	const example = $derived(firstExampleOfBatch(bench.task.id, bench.seed, shownStep));
	const cardSuite = $derived(suite === 'set' || suite === 'match4');
	const layout = $derived(cardSuite ? (example as Card[]) : []);
	const members = $derived(
		suite === 'set' ? setMembership(layout) : suite === 'match4' ? zeroSumMembers(layout, 4) : []
	);

	function toggle() {
		if (running) bench.pause();
		else bench.start();
	}
	const primaryLabel = $derived(
		bench.status === 'booting'
			? 'Starting'
			: running
				? bench.status === 'pausing'
					? 'Pausing'
					: 'Pause'
				: finished
					? 'Finished'
					: bench.step > 0
						? 'Resume'
						: 'Train'
	);

	/** Download every run's history: the format of the recorded runs. */
	function exportRuns() {
		const thin = <T,>(a: T[], k: number) => a.filter((_, i) => i % k === 0 || i === a.length - 1);
		const data: Recorded = {
			suite,
			recordedAt: new Date().toISOString().slice(0, 10),
			device: bench.device ?? 'unknown',
			seed: bench.seed,
			runs: Object.fromEntries(
				bench.runs
					.filter((r) => bench.history[r.id].steps.length > 0)
					.map((r) => {
						const h = bench.history[r.id];
						const loss = ema(h.loss);
						return [
							r.id,
							{
								evalSteps: h.evalSteps,
								evalAccuracy: h.evalAccuracy.map((v) => +v.toFixed(4)),
								evalLayout: h.evalLayout.map((v) => +v.toFixed(4)),
								steps: thin(h.steps, 10),
								loss: thin(loss, 10).map((v) => +v.toPrecision(4)),
								msMedian: +h.msMedian.toFixed(2),
								params: bench.runInfo(r.id)?.params,
								flops: bench.runInfo(r.id)?.trainFlopsPerStep
							}
						];
					})
			)
		};
		const url = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'application/json' }));
		const a = document.createElement('a');
		a.href = url;
		a.download = `${suite}.json`;
		a.click();
		URL.revokeObjectURL(url);
	}

	const COPY: Record<SuiteId, { lede: string; question: string }> = {
		set: {
			lede: 'Every model sees the same batches of twelve cards and says, for each card, whether it belongs to a SET on the table. Only the attention operator differs.',
			question: 'For each card: is it part of any SET on the table?'
		},
		chase: {
			lede: 'Twelve nodes form linked lists. The query names a start node and must return the payload at the end of its list, one to three hops away. One Feynman attention layer against cubic and standard attention at one to three layers.',
			question: 'Follow the list from the ringed start node. What payload is at its end?'
		},
		match4: {
			lede: 'Nine cards. A card is positive when it and three others sum to zero, attribute by attribute. The tested lower-order models stay near chance within this training budget; Newton attention offers every arity at once, in time linear in the table.',
			question: 'For each card: does it complete a zero sum with three others?'
		}
	};
</script>

<svelte:head>
	<title
		>{groups
			? 'Group composition results'
			: suite === 'set'
				? 'SET bench'
				: suite === 'chase'
					? 'Pointer-chase bench'
					: 'Four-card bench'} | Polyformer</title
	>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'set', label: 'SET', icon: Cards },
		{ id: 'chase', label: 'Pointer chase', icon: Workflow },
		{ id: 'match4', label: 'Four cards', icon: Matrix },
		{ id: 'groups', label: 'Groups', icon: Workflow }
	]}
	active={groups ? 'groups' : suite}
	onselect={selectSuite}
>
	{#if groups}
		<div class="group-results">
			<header>
				<div class="title-row">
					<h1>What composition changes</h1>
					<div class="seg" role="group" aria-label="Task">
						<button onclick={() => selectSuite('set')}>SET</button>
						<button onclick={() => selectSuite('chase')}>Pointer chase</button>
						<button onclick={() => selectSuite('match4')}>Four cards</button>
						<button aria-pressed="true" onclick={() => selectSuite('groups')}>Groups</button>
					</div>
				</div>
				<p class="sub">
					Recorded research runs, three seeds. For the binary tasks plotted below, balanced accuracy
					weights positives and negatives equally, so chance is 50%. The dashed lines mark exact
					population limits for a model that cannot distinguish reorderings.
				</p>
			</header>
			<GroupLadder />
			<div class="group-reading">
				<section>
					<h2>A dimension ladder, with a qualification</h2>
					<p>
						In two dimensions rotations commute: their order makes no difference. Three-dimensional
						rotations can retain order, and the A₄ and A₅ tasks reward that distinction. A₄ and A₅
						are the rotation groups of the tetrahedron and icosahedron.
					</p>
					<p>
						The ladder shows learning after 6,000 steps, not a minimum dimension theorem. With
						20,000 steps, A₅ at d = 3 reaches 99.21%, 99.38%, 99.34% for seeds 0, 1, 2.
					</p>
					<p>
						<a href={resolve('/explore/groups')}>Inspect the learned rotations</a> or
						<a href={resolve('/report') + '#groups'}>read the protocol and full tables</a>.
					</p>
				</section>
				<section>
					<h2>The boundary on the claim</h2>
					<p>
						On interleaved swap programs, holonomy d = 3/4, the matrix-state RNN and two- and
						three-layer positional softmax all reach 100.00%. One-layer positional softmax reaches
						98.95%. This second task supports the value of order; it shows no holonomy advantage
						over the order-aware baselines.
					</p>
					<p>
						These are synthetic tasks. The language search found no higher-order gain meeting its 1%
						threshold. Holonomy training is recorded here and runs in the research harness.
					</p>
				</section>
			</div>
			<section class="character-check">
				<h2>Give softmax the coordinates</h2>
				<p>
					Characters are clock-hand features whose phases add under the group law. Supplying every
					character still leaves the measured softmax models at chance on Match-4 and Match-5.
					Newton attention explicitly multiplies those features.
				</p>
				<CharactersResult />
			</section>
			<p class="source">
				Sources: <a href="https://github.com/NeoVand/polyformer/blob/main/research/GROUPS.md"
					>GROUPS.md §5 and §7</a
				>,
				<a href="https://github.com/NeoVand/polyformer/blob/main/research/THEORY.md">THEORY.md §2</a
				>, and the
				<a href="https://github.com/NeoVand/polyformer/blob/main/research/results/grp_e2_long.jsonl"
					>20,000-step rows</a
				>. Model sizes and compute are not matched in the group comparison.
			</p>
		</div>
	{:else}
		<div class="bench">
			<header class="head">
				<div class="title-row">
					<h1>One task, many mechanisms</h1>
					<div class="seg" role="group" aria-label="Task">
						<button aria-pressed={suite === 'set'} onclick={() => selectSuite('set')}>SET</button>
						<button aria-pressed={suite === 'chase'} onclick={() => selectSuite('chase')}
							>Pointer chase</button
						>
						<button aria-pressed={suite === 'match4'} onclick={() => selectSuite('match4')}
							>Four cards</button
						>
						<button aria-pressed="false" onclick={() => selectSuite('groups')}>Groups</button>
					</div>
				</div>
				<p class="sub">{COPY[suite].lede}</p>
			</header>

			<section class="hero" aria-label="Held-out accuracy">
				<div class="h-row">
					<h2>Held-out accuracy</h2>
					<span class="badge" class:live>
						{live
							? 'Live in this browser'
							: recorded
								? `Recorded ${recorded.recordedAt} on ${recorded.device === 'webgpu' ? 'WebGPU' : recorded.device}`
								: 'Press Train to start'}
					</span>
					<div class="seg" role="group" aria-label="Horizontal axis">
						<button aria-pressed={axis === 'steps'} onclick={() => (axis = 'steps')}>Steps</button>
						<button aria-pressed={axis === 'compute'} onclick={() => (axis = 'compute')}
							>Compute</button
						>
					</div>
				</div>
				<div class="chart-fill" bind:clientHeight={heroHeight}>
					<LineChart
						label="Held-out token accuracy"
						series={accuracySeries}
						version={bench.version}
						{xMax}
						{xLabel}
						{formatX}
						yMin={cardSuite ? 0.4 : 0}
						yMax={1}
						yTicks={cardSuite ? [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1] : [0, 0.2, 0.4, 0.6, 0.8, 1]}
						formatY={(v) => pct(v, 0)}
						reference={{ y: majority, label: `Majority class ${pct(majority, 0)}` }}
						height={Math.max(220, heroHeight)}
					/>
				</div>
			</section>

			<section class="lower" aria-label="Loss and input">
				<div class="mini">
					<h3>Training loss <small>smoothed, log scale</small></h3>
					<LineChart
						label="Training loss"
						series={lossSeries}
						version={bench.version}
						{xMax}
						{xLabel}
						{formatX}
						log
						yMin={1e-4}
						yMax={cardSuite ? 1 : 3}
						yTicks={[1e-4, 1e-3, 1e-2, 1e-1, 1]}
						formatY={(v) => (v >= 0.01 ? v.toFixed(2) : v.toExponential(0))}
						height={160}
					/>
				</div>
				{#if suite === 'set'}
					<div class="mini">
						<h3>Tables fully right <small>all twelve cards</small></h3>
						<LineChart
							label="Share of held-out tables with every card right"
							series={layoutSeries}
							version={bench.version}
							{xMax}
							{xLabel}
							{formatX}
							yMin={0}
							yMax={1}
							yTicks={[0, 0.25, 0.5, 0.75, 1]}
							formatY={(v) => pct(v, 0)}
							height={160}
						/>
					</div>
				{/if}
				<div class="input">
					<h3>Shared input <small class="num">batch {shownStep.toLocaleString('en-US')}</small></h3>
					<p class="q">{COPY[suite].question}</p>
					{#if cardSuite}
						<div class="cards">
							{#each layout as card, i (i)}
								<span class="slot" class:in={members[i]}>
									<SetCard {card} width={30} dim={!members[i]} />
								</span>
							{/each}
						</div>
					{:else}
						<ChaseLists instance={example as ChaseInstance} compact />
					{/if}
				</div>
			</section>

			<aside class="board" aria-label="Runs">
				<div class="b-head">
					<h2>Runs</h2>
					<span class="hint">d = 64, 4 heads, one block unless noted</span>
				</div>
				<ol class="runs">
					{#each rows as row (row.spec.id)}
						<li class="run" class:lead={row.acc !== undefined && row.acc === best && best > 0}>
							<div class="r-top">
								<svg width="22" height="10" aria-hidden="true">
									<line
										x1="0"
										y1="5"
										x2="22"
										y2="5"
										stroke="rgb({70 + row.spec.tone * 175} {70 + row.spec.tone * 175} {70 +
											row.spec.tone * 175})"
										stroke-width={row.spec.tone === 1 ? 2.25 : 1.5}
										stroke-dasharray={row.spec.dash}
									/>
								</svg>
								<span class="name">{row.spec.label}</span>
								<span class="acc num" class:rec={row.recordedOnly}
									>{row.acc === undefined ? '—' : pct(row.acc, 0)}</span
								>
							</div>
							<div class="formula"><MathTex tex={row.op.logitTex} /></div>
							<div class="meta num">
								<span>{row.params ? `${compact(row.params)} params` : '—'}</span>
								<span>{row.flops ? `${flops(row.flops)} / step` : ''}</span>
								<span>{row.ms ? ms(row.ms) : ''}</span>
							</div>
							<div class="r-foot">
								<span class="hint num"
									>{row.reached !== undefined
										? `95% at step ${row.reached.toLocaleString('en-US')}`
										: row.acc !== undefined
											? 'Not at 95% yet'
											: 'Not trained'}{row.recordedOnly ? ' · recorded' : ''}</span
								>
								<label class="switch">
									<input
										type="checkbox"
										bind:checked={bench.enabled[row.spec.id]}
										disabled={running}
									/>
									<span>Train</span>
								</label>
							</div>
						</li>
					{/each}
				</ol>
				<dl class="spec">
					<div>
						<dt>Batch</dt>
						<dd class="num">{BATCH}</dd>
					</div>
					<div>
						<dt>Steps</dt>
						<dd class="num">{TOTAL_STEPS.toLocaleString('en-US')}</dd>
					</div>
					<div>
						<dt>Optimizer</dt>
						<dd>AdamW, cosine</dd>
					</div>
					<div>
						<dt>Held out</dt>
						<dd class="num">{EVAL_LAYOUTS.toLocaleString('en-US')}</dd>
					</div>
				</dl>
			</aside>

			<footer class="transport" aria-label="Training controls">
				<div class="group">
					<button
						class="key"
						onclick={() => bench.reset()}
						disabled={bench.status === 'booting' || running}
						aria-label="Reset to step 0"><Icon icon={Reset} size={17} /><span>Reset</span></button
					>
					<button
						class="key play"
						onclick={toggle}
						disabled={bench.status === 'booting' ||
							bench.status === 'pausing' ||
							(finished && !running)}
						><Icon icon={running ? Pause : Play} size={17} /><span>{primaryLabel}</span></button
					>
				</div>
				<div class="group grow">
					<div class="progress" aria-label="Training progress">
						<div class="bar">
							<div class="fill" style:width="{(bench.step / TOTAL_STEPS) * 100}%"></div>
						</div>
						<span class="num"
							>{bench.step.toLocaleString('en-US')} / {TOTAL_STEPS.toLocaleString('en-US')}</span
						>
					</div>
				</div>
				<div class="group seed-controls">
					<span class="t-label">Seed</span>
					<div class="stepper">
						<button
							onclick={() => bench.reset(Math.max(0, bench.seed - 1))}
							disabled={running || bench.seed === 0}
							aria-label="Previous seed">−</button
						>
						<span class="num">{bench.seed}</span>
						<button
							onclick={() => bench.reset(bench.seed + 1)}
							disabled={running}
							aria-label="Next seed">+</button
						>
					</div>
				</div>
				<div class="group telemetry">
					<span class="t-label num"><Icon icon={Timer} size={16} />{duration(bench.elapsedMs)}</span
					>
					<span class="t-label"
						><Icon icon={Chip} size={16} />{bench.device === 'webgpu'
							? 'WebGPU'
							: bench.device === 'wasm'
								? 'WebAssembly'
								: 'Starts on first run'}</span
					>
				</div>
				<div class="group right">
					<button class="key" onclick={exportRuns} disabled={!live}
						><Icon icon={Download} size={17} /><span>Export</span></button
					>
				</div>
				{#if bench.error}
					<span class="error" role="alert">{bench.error}</span>
				{/if}
			</footer>
		</div>
	{/if}
</PageFrame>

<style>
	.group-results {
		max-width: 960px;
		margin: 0 auto;
		padding: 26px 32px 60px;
	}
	.group-results > header {
		margin-bottom: 24px;
	}
	.group-results .title-row {
		justify-content: space-between;
		flex-wrap: wrap;
	}
	.group-results .sub {
		max-width: 92ch;
	}
	.group-reading {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 40px;
		margin: 28px 0 36px;
	}
	.group-results p {
		font-size: 13px;
		line-height: 1.65;
		color: var(--color-ink-2);
		margin-top: 10px;
	}
	.group-results a {
		color: var(--color-ink);
		text-underline-offset: 3px;
	}
	.character-check {
		max-width: 820px;
	}
	.character-check > p {
		margin-bottom: 20px;
		max-width: 78ch;
	}
	.group-results .source {
		margin-top: 28px;
		font-size: 12px;
		color: var(--color-ink-3);
	}
	@media (max-width: 640px) {
		.group-results {
			padding: 24px 18px 44px;
		}
		.group-reading {
			grid-template-columns: 1fr;
			gap: 24px;
		}
		.group-results .seg {
			flex-wrap: wrap;
		}
	}

	.bench {
		--transport-h: 60px;
		display: grid;
		grid-template-columns: minmax(0, 1fr) 330px;
		grid-template-rows: auto minmax(260px, 1fr) auto;
		grid-template-areas:
			'head board'
			'hero board'
			'lower board';
		gap: 0 22px;
		height: calc(100dvh - var(--bar-h) - var(--transport-h));
		padding: 18px 0 0 28px;
	}
	.head {
		grid-area: head;
	}
	.title-row {
		display: flex;
		align-items: center;
		gap: 18px;
	}
	h1 {
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.025em;
		line-height: 1.1;
	}
	.sub {
		margin-top: 6px;
		max-width: 84ch;
		color: var(--color-ink-3);
		font-size: var(--text-sm);
		line-height: 1.5;
	}
	h2 {
		font-size: 15px;
		font-weight: 500;
	}
	h3 {
		display: flex;
		align-items: baseline;
		gap: 8px;
		font-size: var(--text-xs);
		font-weight: 500;
		color: var(--color-ink-2);
		margin-bottom: 4px;
	}
	h3 small {
		font-size: var(--text-2xs);
		font-weight: 400;
		color: var(--color-ink-3);
	}

	.hero {
		grid-area: hero;
		display: grid;
		grid-template-rows: auto minmax(0, 1fr);
		min-height: 0;
		margin-top: 14px;
	}
	.h-row {
		display: flex;
		align-items: center;
		gap: 14px;
		margin-bottom: 4px;
	}
	.h-row .seg {
		margin-left: auto;
	}
	.badge {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.badge.live {
		color: var(--color-ink);
	}
	.chart-fill {
		min-height: 0;
		overflow: hidden;
	}

	.lower {
		grid-area: lower;
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
		gap: 24px;
		padding: 8px 0 12px;
	}
	.input .q {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		margin-bottom: 8px;
	}
	.cards {
		display: grid;
		grid-template-columns: repeat(6, max-content);
		gap: 6px 10px;
	}
	.slot {
		display: block;
	}

	/* leaderboard */
	.board {
		grid-area: board;
		align-self: stretch;
		overflow-y: auto;
		margin-top: -18px;
		padding: 18px 22px 22px;
		background: #0c0c0c;
		border-left: 1px solid #1a1a1a;
	}
	.b-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		padding-bottom: 4px;
	}
	.runs {
		display: grid;
	}
	.run {
		display: grid;
		gap: 4px;
		padding: 11px 0;
	}
	.r-top {
		display: grid;
		grid-template-columns: 22px 1fr auto;
		gap: 10px;
		align-items: center;
	}
	.name {
		font-size: var(--text-sm);
	}
	.acc {
		font-size: 19px;
		font-weight: 500;
		letter-spacing: -0.02em;
		color: var(--color-ink-2);
	}
	.acc.rec {
		opacity: 0.9;
	}
	.run.lead .acc {
		color: var(--color-ink);
	}
	.formula {
		font-size: 12.5px;
		color: var(--color-ink-2);
		overflow-x: auto;
	}
	.meta {
		display: flex;
		gap: 12px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.r-foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.r-foot .hint {
		font-size: var(--text-2xs);
	}
	.switch {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		cursor: pointer;
	}
	.spec {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 10px;
		margin-top: 14px;
	}
	.spec dt {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.spec dd {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}

	/* transport */
	.transport {
		position: fixed;
		left: var(--rail-w);
		right: 0;
		bottom: 0;
		z-index: 10;
		height: var(--transport-h);
		display: flex;
		align-items: center;
		gap: 28px;
		padding: 0 22px 0 28px;
		border-top: 1px solid #1a1a1a;
		background: var(--color-void);
	}
	.group {
		display: flex;
		align-items: center;
		gap: 8px;
	}
	.group.grow {
		flex: 1;
	}
	.t-label {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.progress {
		display: flex;
		align-items: center;
		gap: 12px;
		width: 100%;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.bar {
		flex: 1;
		height: 3px;
		border-radius: 2px;
		background: #222;
		overflow: hidden;
	}
	.fill {
		height: 100%;
		background: var(--color-ink);
		transition: width 200ms linear;
	}
	.stepper {
		display: flex;
		align-items: center;
		height: 28px;
		border-radius: 6px;
		background: #1a1a1a;
	}
	.stepper button {
		width: 28px;
		height: 100%;
		border: 0;
		background: transparent;
		color: var(--color-ink-3);
		font-size: 14px;
		cursor: pointer;
	}
	.stepper button:disabled {
		opacity: 0.35;
		cursor: default;
	}
	.stepper span {
		min-width: 22px;
		text-align: center;
		font-size: var(--text-sm);
	}
	.key {
		display: grid;
		justify-items: center;
		gap: 3px;
		min-width: 46px;
		padding: 5px 4px 3px;
		border: 0;
		border-radius: 6px;
		background: transparent;
		color: var(--color-ink-3);
		font-size: var(--text-2xs);
		cursor: pointer;
	}
	.key:hover:not(:disabled) {
		color: var(--color-ink);
		background: #141414;
	}
	.key:disabled {
		opacity: 0.4;
		cursor: default;
	}
	.key.play {
		color: var(--color-ink);
	}
	.key.play :global(svg) {
		box-sizing: content-box;
		padding: 5px;
		margin: -5px 0 0;
		border-radius: 6px;
		background: var(--color-ink);
		color: var(--color-void);
	}
	.error {
		font-size: var(--text-xs);
		color: var(--color-ink);
	}

	@media (max-width: 1200px) {
		.bench {
			height: auto;
			grid-template-columns: minmax(0, 1fr);
			grid-template-areas: 'head' 'hero' 'lower' 'board';
			grid-template-rows: auto auto auto auto;
			padding: 16px 16px var(--transport-h);
		}
		.board {
			margin: 0;
			border: 0;
			border-radius: 8px;
		}
		.transport {
			left: 0;
			gap: 18px;
			overflow-x: auto;
			padding: 0 16px;
		}
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 24px;
		}
		.title-row {
			flex-wrap: wrap;
			gap: 10px;
		}
		.transport {
			gap: 8px;
			padding: 0 10px;
			overflow-x: visible;
		}
		.transport .telemetry {
			display: none;
		}
		.transport .group {
			gap: 4px;
		}
		.transport .key {
			min-width: 40px;
		}
		.transport .grow {
			min-width: 0;
		}
		.transport .progress {
			flex-direction: column;
			gap: 6px;
			min-width: 0;
			font-size: 10px;
			white-space: nowrap;
		}
		.transport .bar {
			flex: none;
			width: 100%;
			height: 2px;
		}
		.transport .seed-controls {
			flex-direction: column;
			gap: 1px;
		}
		.seed-controls .t-label {
			font-size: 9px;
			line-height: 1;
		}
		.stepper {
			height: 26px;
		}
		.stepper button {
			width: 24px;
		}
		.stepper span {
			min-width: 18px;
		}
	}
</style>
