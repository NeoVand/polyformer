<script lang="ts">
	import { asset, resolve } from '$app/paths';
	import { CHASE_QUERY_POS, dealChase, solveChase, type ChaseInstance } from '#lib/chase/chase.ts';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { DiagramHead, DiagramResult, DiagramSector } from '#lib/engine/protocol.ts';
	import { dealLayout, findSets, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import Icon from '#lib/ui/Icon.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { Dice, Feynman, Next, Pause, Play, Previous, Scissors, Simplex } from '#lib/ui/icons.ts';
	import ChaseLists from '#lib/ui/ChaseLists.svelte';
	import { flowGroups, heldPayloads } from '#lib/viz/chaseFlow.ts';
	import DiagramFlow from '#lib/viz/DiagramFlow.svelte';
	import FeynmanDiagram from '#lib/viz/FeynmanDiagram.svelte';
	import FlowLegend from '#lib/viz/FlowLegend.svelte';
	import FeynmanRule from '#lib/viz/FeynmanRule.svelte';
	import { autoThreshold, flowOn, idealChase, idealSet, type Term } from '#lib/viz/feynman.ts';

	type TaskKey = 'chase' | 'set';
	type Source = 'recorded' | 'ideal' | 'trained';
	let task = $state<TaskKey>('set');
	let source = $state<Source>('recorded');
	let seed = $state(4);
	/** Prune threshold the user set, or null to choose one per diagram. */
	let manualThreshold = $state<number | null>(null);
	/** Head the user picked, or null to show the one that follows the true path best. */
	let pickedHead = $state<number | null>(null);

	// ── the example under the microscope ─────────────────────────────────────
	const chase = $derived.by(() => {
		const rng = mulberry32(seed * 9973 + 1);
		// prefer instances that need the full three hops: the deepest diagrams
		let best: ChaseInstance = dealChase(rng);
		for (let tries = 0; tries < 30 && solveChase(best).hops < 3; tries++) best = dealChase(rng);
		return best;
	});
	const answer = $derived(solveChase(chase));
	const layout = $derived.by(() => {
		// seed 4 deals the landing page's twelve cards, which have a recorded model
		const rng = mulberry32((seed - 1) * 7717 + 3);
		for (;;) {
			const l: Card[] = dealLayout(rng);
			if (findSets(l).length >= 3) return l;
		}
	});
	const sets = $derived(findSets(layout));
	const setCard = $derived(sets[0][0]);

	// ── a model recorded in a browser, the ideal construction, or a live run ──
	interface Recording {
		diagram: DiagramResult;
	}
	/** The examples that have a recorded model: the first deal of each task. */
	const RECORDED_SEED = 4;
	let recorded = $state.raw<Record<TaskKey, Recording | null>>({ set: null, chase: null });
	$effect(() => {
		const get = (path: Parameters<typeof asset>[0]) =>
			fetch(asset(path)).then((r) => (r.ok ? r.json() : null));
		Promise.all([get('recorded/set-diagram.json'), get('recorded/chase-diagram.json')]).then(
			([set, chase]) =>
				(recorded = { set: set?.diagram ? set : null, chase: chase?.diagram ? chase : null }),
			() => {}
		);
	});
	const hasRecording = $derived(seed === RECORDED_SEED && !!recorded[task]);
	const showingRecorded = $derived(source === 'recorded' && hasRecording);

	const bench = $derived(getBench(task));
	const step = $derived.by(() => {
		void bench.version;
		return bench.history.dspa?.step ?? 0;
	});
	const training = $derived(bench.status === 'training' || bench.status === 'pausing');
	let trained = $state.raw<DiagramResult | null>(null);
	const example = $derived<unknown>(task === 'chase' ? chase : layout.map((c) => [...c]));
	/** Re-probe every 50 steps while training (steps arrive faster than a probe takes). */
	const checkpoint = $derived(Math.floor(step / 50));
	const token = $derived(task === 'chase' ? CHASE_QUERY_POS : setCard + 1);

	/** The token whose diagram is expanded; clicking a row in the flow picks another. */
	let rootPick = $state<number | null>(null);
	const root = $derived(rootPick ?? token);
	// a new task or example starts from the ideal view until its first probe returns
	$effect(() => {
		void task;
		void example;
		trained = null;
		rootPick = null;
	});
	$effect(() => {
		if (source !== 'trained' || step === 0) return;
		void checkpoint;
		const b = bench;
		const ex = example;
		const t = token;
		let cancelled = false;
		b.diagram('dspa', ex, t, 4).then(
			(r) => !cancelled && (trained = r),
			() => {}
		);
		return () => {
			cancelled = true;
		};
	});

	interface View {
		head: DiagramHead;
		n: number;
		rounds: number;
		modes: number;
		heads: number;
	}
	const bestHead = $derived.by(() => {
		if (!trained) return 0;
		const r = trained;
		const scores = r.perHead.map((h) => flowOn(h, r.n, r.rounds, r.modes, token, highlight));
		return scores.indexOf(Math.max(...scores));
	});
	const headIndex = $derived(pickedHead ?? bestHead);
	const view = $derived.by<View>(() => {
		if (showingRecorded) {
			const d = recorded[task]!.diagram;
			return { head: d.perHead[0], n: d.n, rounds: d.rounds, modes: d.modes, heads: 1 };
		}
		if (source === 'trained' && trained) {
			const h = Math.min(headIndex, trained.heads - 1);
			return {
				head: trained.perHead[h],
				n: trained.n,
				rounds: trained.rounds,
				modes: trained.modes,
				heads: trained.heads
			};
		}
		return task === 'chase'
			? { head: idealChase(chase, 4), n: CHASE_QUERY_POS + 1, rounds: 4, modes: 0, heads: 1 }
			: { head: idealSet(layout, 2), n: layout.length + 1, rounds: 2, modes: 0, heads: 1 };
	});
	const showingTrained = $derived(source === 'trained' && !!trained);
	const threshold = $derived(
		manualThreshold ?? autoThreshold(view.head, view.n, view.rounds, view.modes, root)
	);

	// ── the root's sector spectrum, round by round ───────────────────────────
	const SECTORS: { id: DiagramSector; label: string; shade: number; tex: string; says: string }[] =
		[
			{
				id: 'leaf',
				label: 'Leaf',
				shade: 0.32,
				tex: '\\pi_{\\text{leaf}}\\, v_t',
				says: 'its own value'
			},
			{
				id: 'hop',
				label: 'Hop',
				shade: 0.95,
				tex: '\\pi_j\\, \\Phi^{r-1}_j',
				says: 'another token'
			},
			{
				id: 'cubic',
				label: 'Cubic',
				shade: 0.72,
				tex: '\\pi_{jk}\\, \\Phi_j \\odot \\Phi_k',
				says: 'two tokens at once'
			},
			{
				id: 'exchange',
				label: 'Exchange',
				shade: 0.52,
				tex: '\\pi_{jm}\\, \\Phi_j \\odot \\Psi_m',
				says: 'via a virtual mode'
			},
			{
				id: 'carry',
				label: 'Carry',
				shade: 0.18,
				tex: '\\pi_{\\text{carry}}\\, \\Phi^{r-1}_t',
				says: 'keep the state'
			}
		];
	const spectrum = $derived(
		Array.from({ length: view.rounds }, (_, r) => view.head.states[r * view.n + root]?.sectors)
	);

	// ── reveal: build the diagram from the values to the readout ─────────────
	let reveal = $state(Infinity);
	let playing = $state(false);
	$effect(() => {
		if (!playing) return;
		const R = view.rounds;
		const id = setInterval(() => {
			const next = reveal >= R + 1 ? 0 : reveal + 1;
			reveal = next;
			if (next === R + 1) playing = false;
		}, 850);
		return () => clearInterval(id);
	});
	function play() {
		if (playing) {
			playing = false;
			return;
		}
		reveal = 0;
		playing = true;
	}
	const stage = $derived(Number.isFinite(reveal) ? reveal : view.rounds + 1);
	function stepTo(r: number) {
		playing = false;
		reveal = Math.max(0, Math.min(view.rounds + 1, r));
	}

	// ── hover ────────────────────────────────────────────────────────────────
	let term = $state<Term | null>(null);
	const describe = (t: Term) => {
		const name = (p: number) => tokenName(p);
		switch (t.sector) {
			case 'leaf':
				return `${name(t.token)} reads its own value`;
			case 'hop':
				return `${name(t.token)} reads ${name(t.j!)}`;
			case 'cubic':
				return `${name(t.token)} reads ${name(t.j!)} ⊙ ${name(t.k!)}`;
			case 'exchange':
				return `${name(t.token)} reads ${name(t.j!)} ⊙ Ψ${t.m}${t.pair ? `, which binds ${name(t.pair[0])} and ${name(t.pair[1])}` : ''}`;
			case 'carry':
				return `${name(t.token)} keeps its state`;
		}
	};

	function tokenName(p: number): string {
		if (p === 0) return 'BOS';
		if (task === 'chase') {
			if (p === CHASE_QUERY_POS) return 'the query';
			return `node ${chase.nodes[p - 1].id}`;
		}
		return `card ${p}`;
	}

	function newExample() {
		seed += 1;
		reveal = Infinity;
		playing = false;
	}
	function train() {
		source = 'trained';
		bench.start({ only: ['dspa'], until: Math.max(task === 'chase' ? 3000 : 2000, step + 1000) });
	}
	const highlight = $derived(
		task === 'chase'
			? [CHASE_QUERY_POS, ...answer.path.map((i) => i + 1)]
			: [setCard + 1, ...sets[0].slice(1).map((c) => c + 1)]
	);

	const probs = $derived(
		showingRecorded
			? recorded[task]!.diagram.probs
			: showingTrained && trained
				? trained.probs
				: null
	);
	const predicted = $derived(probs ? probs.indexOf(Math.max(...probs)) : null);
	/** Rows of the every-token view: lists in pointer order for chase, the table for SET. */
	const flowRows = $derived(
		task === 'chase' ? flowGroups(chase) : [Array.from({ length: layout.length }, (_, i) => i + 1)]
	);
	const held = $derived(
		task === 'chase' ? heldPayloads(view.head, view.n, view.rounds, chase) : null
	);
	const rootHighlight = $derived(root === token ? highlight : [root]);
	const rootOutput = $derived(
		root !== token
			? `\\Phi^{${view.rounds}}`
			: task === 'chase'
				? `\\hat y = ${predicted ?? answer.payload}`
				: '\\hat y'
	);
</script>

<svelte:head>
	<title>Diagrams | Polyformer</title>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'tensor', label: 'Cubic', icon: Simplex, href: resolve('/explore') },
		{ id: 'diagrams', label: 'Feynman', icon: Feynman, href: resolve('/explore/diagrams') }
	]}
	active="diagrams"
>
	<div class="screen">
		<header class="head">
			<div class="title-row">
				<h1>Sum over diagrams</h1>
				<div class="seg" role="group" aria-label="Task">
					<button aria-pressed={task === 'set'} onclick={() => (task = 'set')}>SET</button>
					<button aria-pressed={task === 'chase'} onclick={() => (task = 'chase')}
						>Pointer chase</button
					>
				</div>
			</div>
			<p class="sub">
				Feynman attention rebuilds every token for several rounds from a sum of terms. On the left,
				every token at once; on the right, one token's sum expanded into its Feynman diagram. Click
				a row to expand that token.
			</p>
		</header>

		<section class="diagram" aria-label="Computation">
			<div class="d-head">
				<span>
					{#if task === 'chase'}
						{#if root === CHASE_QUERY_POS}
							The query's state <MathTex tex={`\\Phi^{${view.rounds}}_q`} /> must hold the payload at
							the end of its list.
						{:else}
							Node {chase.nodes[root - 1]?.id}'s state <MathTex tex={`\\Phi^{${view.rounds}}`} />,
							built from what it points to.
						{/if}
					{:else}
						Card {root}'s state <MathTex tex={`\\Phi^{${view.rounds}}_{${root}}`} /> must say whether
						it is in a SET.
					{/if}
				</span>
				<span class="status num" class:live={showingTrained || showingRecorded}>
					{#if showingRecorded}
						{@const d = recorded[task]!.diagram}
						Recorded in a browser, step {d.step.toLocaleString('en-US')}, head {d.perHead[0].head +
							1} of {d.heads}
					{:else if showingTrained}
						Trained, step {step.toLocaleString('en-US')}, head {headIndex + 1}
					{:else}
						Ideal computation
					{/if}
				</span>
			</div>
			<div class="panes">
				<div class="pane every">
					<h3 class="p-title">Every token</h3>
					<DiagramFlow
						head={view.head}
						n={view.n}
						rounds={view.rounds}
						rows={flowRows}
						{root}
						onroot={(t) => (rootPick = t === token ? null : t)}
						pitch={task === 'chase' ? 27 : 32}
						column={task === 'chase' ? 74 : 124}
						annotate={held
							? (r, t) => {
									const v = held[r]?.[t];
									return v === null || v === undefined ? null : String(v);
								}
							: undefined}
						output={rootOutput}
					>
						{#snippet label(t)}
							{#if task === 'chase'}
								{#if t === CHASE_QUERY_POS}<MathTex tex="q" />{:else}{chase.nodes[t - 1]?.id}{/if}
							{:else}
								<SetCard card={layout[t - 1]} width={15} />
							{/if}
						{/snippet}
					</DiagramFlow>
					<div class="p-legend"><FlowLegend compact /></div>
				</div>
				<div class="pane one">
					<h3 class="p-title">
						{task === 'chase'
							? root === CHASE_QUERY_POS
								? 'The query, expanded'
								: `Node ${chase.nodes[root - 1]?.id}, expanded`
							: `Card ${root}, expanded`}
					</h3>
					<div class="canvas">
						{#key `${task}-${source}-${root}`}
							<FeynmanDiagram
								head={view.head}
								n={view.n}
								rounds={view.rounds}
								modes={view.modes}
								{root}
								options={{ threshold, perRound: 9 }}
								{reveal}
								highlight={rootHighlight}
								output={rootOutput}
								onterm={(t) => (term = t)}
							>
								{#snippet row(t)}
									{#if t === 0}
										<span class="leg"><MathTex tex="\varnothing" /></span>
									{:else if task === 'chase'}
										<span class="leg"
											><MathTex
												tex={t === CHASE_QUERY_POS ? 'q' : `v_{${chase.nodes[t - 1].id}}`}
											/></span
										>
									{:else}
										<SetCard card={layout[t - 1]} width={22} />
									{/if}
								{/snippet}
							</FeynmanDiagram>
						{/key}
					</div>
				</div>
			</div>
		</section>

		<section class="strip" aria-label="The example">
			{#if task === 'chase'}
				<span class="s-label">Lists</span>
				<ChaseLists instance={chase} />
			{:else}
				<span class="s-label">Table</span>
				<div class="cards">
					{#each layout as c, i (i)}
						<SetCard
							card={c}
							width={30}
							selected={sets[0].includes(i)}
							dim={!sets.some((s) => s.includes(i))}
						/>
					{/each}
				</div>
			{/if}
		</section>

		<aside class="inspector" aria-label="Rules and readouts">
			<h2>Dyson–Schwinger sum</h2>
			<div class="eq">
				<MathTex
					display
					tex={'\\begin{aligned}\\Phi^{r}_t =\\;& \\pi_{\\text{leaf}}\\, v_t + \\textstyle\\sum_j \\pi_j\\, \\Phi^{r-1}_j \\\\ &+ \\textstyle\\sum_{jk} \\pi_{jk}\\, \\Phi^{r-1}_j \\odot \\Phi^{r-1}_k \\\\ &+ \\textstyle\\sum_{jm} \\pi_{jm}\\, \\Phi^{r-1}_j \\odot \\Psi^{r}_m + \\pi_{\\text{carry}}\\, \\Phi^{r-1}_t\\end{aligned}'}
				/>
			</div>
			<p class="note">
				One softmax <MathTex tex="\pi" /> over every term, scored by a single trilinear vertex. Each term
				is a Feynman rule:
			</p>
			<div class="rules-head">
				<span>Rule</span>
				<span class="rh-mass">
					{#each Array.from({ length: view.rounds }, (_, r) => r) as r (r)}<i
							><MathTex tex={`\\Phi^{${r + 1}}`} /></i
						>{/each}
				</span>
			</div>
			<ul class="rules">
				{#each SECTORS as sec (sec.id)}
					{@const last = spectrum.at(-1)?.[sec.id] ?? 0}
					<li class:dominant={last >= 0.5}>
						<FeynmanRule kind={sec.id} width={52} height={22} />
						<span class="r-name">{sec.label}<small>{sec.says}</small></span>
						<span
							class="r-mass"
							role="img"
							aria-label="{sec.label}: {pct(last, 0)} of the mass in the last round"
						>
							{#each spectrum as sm, r (r)}
								{@const v = sm?.[sec.id] ?? 0}
								<i title="Round {r + 1}: {pct(v, 1)}"
									><b style:height="{Math.max(v > 0.004 ? 1.5 : 0, v * 100)}%"></b></i
								>
							{/each}
						</span>
						<span class="r-pct num"
							>{last >= 0.995 ? '100%' : last < 0.005 ? '<1%' : pct(last, 0)}</span
						>
					</li>
				{/each}
			</ul>
			<p class="note mass-note">
				Bars: how much of {task === 'chase' && root === CHASE_QUERY_POS
					? "the query's"
					: task === 'chase'
						? "this node's"
						: "this card's"}
				state each rule supplies, round by round.
			</p>

			<h3>Under the pointer</h3>
			<p class="note hover">
				{#if term}
					<span class="num">Round {term.round}:</span>
					{describe(term)}, {pct(term.flow, 1)} of the root.
				{:else}
					Hover a line to read its term.
				{/if}
			</p>

			<h3>
				{showingRecorded
					? 'Recorded model'
					: showingTrained
						? 'Trained model'
						: 'Ideal computation'}
			</h3>
			{#if showingRecorded}
				<p class="note">
					Trained for {recorded[task]!.diagram.step.toLocaleString('en-US')} steps on WebGPU and saved,
					so it shows without waiting. Live trains a fresh model here.
				</p>
			{/if}
			{#if !showingTrained && !showingRecorded}
				<p class="note">
					{#if task === 'chase'}
						A perfect model hops one pointer per round, and the query hops to its start. Here the
						answer is payload
						{answer.payload}, {answer.hops}
						{answer.hops === 1 ? 'hop' : 'hops'} from the start.
					{:else}
						A perfect model needs one cubic vertex: each card multiplies the values of its two SET
						partners.
					{/if}
				</p>
			{:else if probs}
				<p class="note num">
					{#if task === 'chase'}
						Predicts payload {predicted} at {pct(probs[predicted ?? 0], 0)}; the true payload is {answer.payload}.
					{:else}
						Says card {setCard + 1} is in a SET with probability {pct(probs[1] ?? probs[0], 0)}.
					{/if}
				</p>
			{/if}
			{#if source === 'trained'}
				<p class="note num live-note">
					{#if bench.status === 'booting'}
						Starting the engine…
					{:else if bench.status === 'error'}
						{bench.error}
					{:else if training}
						Training on {bench.device === 'webgpu'
							? 'WebGPU'
							: bench.device === 'wasm'
								? 'WebAssembly'
								: bench.device}, step {step.toLocaleString('en-US')}. The diagram redraws as it
						learns.
					{:else if step > 0}
						Trained to step {step.toLocaleString('en-US')}.
						<button class="link-btn" onclick={train}>Train 1,000 more</button>
					{:else}
						<button class="btn primary" onclick={train}
							><Icon icon={Play} size={13} />Train Feynman</button
						>
					{/if}
				</p>
			{/if}
		</aside>

		<footer class="transport" aria-label="Diagram controls">
			<div class="group timeline" role="group" aria-label="Build the diagram">
				{#each Array.from({ length: view.rounds + 2 }, (_, r) => r) as r (r)}
					{#if r > 0}<span class="rail-line" class:on={stage >= r}></span>{/if}
					<button
						class="tick"
						class:on={stage >= r}
						class:at={stage === r}
						onclick={() => stepTo(r)}
					>
						<span class="dot"></span>
						<span class="t-name"
							>{r === 0 ? 'Values' : r === view.rounds + 1 ? 'Readout' : `Round ${r}`}</span
						>
					</button>
				{/each}
			</div>
			<div class="group keys-row">
				<button class="key" onclick={() => stepTo(stage - 1)}
					><Icon icon={Previous} size={17} /><span>Back</span></button
				>
				<button class="key play" onclick={play}
					><Icon icon={playing ? Pause : Play} size={17} /><span>{playing ? 'Pause' : 'Build'}</span
					></button
				>
				<button class="key" onclick={() => stepTo(stage + 1)}
					><Icon icon={Next} size={17} /><span>Step</span></button
				>
			</div>
			<div class="group prune">
				<Icon icon={Scissors} size={16} />
				<label class="t-label" for="prune">Prune</label>
				<input
					id="prune"
					type="range"
					min="0.0025"
					max="0.1"
					step="0.0025"
					value={threshold}
					oninput={(e) => (manualThreshold = +e.currentTarget.value)}
				/>
				<span class="num val">{pct(threshold, 1)}</span>
				<button
					class="auto"
					aria-pressed={manualThreshold === null}
					onclick={() => (manualThreshold = null)}>Auto</button
				>
			</div>
			<div class="group">
				<div class="seg" role="group" aria-label="Model">
					<button
						aria-pressed={showingRecorded}
						disabled={!hasRecording}
						title={hasRecording
							? 'A model trained earlier in a browser'
							: 'Recorded for the first deal only'}
						onclick={() => (source = 'recorded')}>Recorded</button
					>
					<button
						aria-pressed={source === 'ideal' || (source === 'recorded' && !hasRecording)}
						onclick={() => (source = 'ideal')}>Ideal</button
					>
					<button aria-pressed={source === 'trained'} onclick={() => (source = 'trained')}
						>Live</button
					>
				</div>
				{#if showingTrained && view.heads > 1}
					<div class="seg" role="group" aria-label="Head">
						{#each Array.from({ length: view.heads }, (_, h) => h) as h (h)}
							<button aria-pressed={headIndex === h} onclick={() => (pickedHead = h)}
								>H{h + 1}</button
							>
						{/each}
					</div>
				{/if}
			</div>
			<div class="group right">
				<button class="key" onclick={newExample}
					><Icon icon={Dice} size={17} /><span>Deal</span></button
				>
			</div>
		</footer>
	</div>
</PageFrame>

<style>
	.screen {
		--transport-h: 60px;
		display: grid;
		grid-template-columns: minmax(0, 1fr) 312px;
		grid-template-rows: auto minmax(300px, 1fr) auto;
		grid-template-areas:
			'head insp'
			'diagram insp'
			'strip insp';
		gap: 0 20px;
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
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-size: 32px;
		font-weight: 400;
		line-height: 1.1;
	}
	.sub {
		margin-top: 6px;
		max-width: 76ch;
		color: var(--color-ink-3);
		font-size: var(--text-sm);
		line-height: 1.5;
	}

	.diagram {
		grid-area: diagram;
		display: grid;
		grid-template-rows: auto minmax(0, 1fr);
		min-height: 0;
		margin-top: 14px;
	}
	.d-head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 16px;
		font-size: var(--text-sm);
		color: var(--color-ink-2);
	}
	.status {
		flex: none;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.status.live {
		color: var(--color-ink);
	}
	.panes {
		display: grid;
		grid-template-columns: minmax(280px, 0.8fr) minmax(0, 1.2fr);
		gap: 22px;
		min-height: 0;
		padding-top: 12px;
	}
	.pane {
		display: flex;
		flex-direction: column;
		min-width: 0;
		min-height: 0;
	}
	.pane.every {
		overflow-y: auto;
		padding-right: 18px;
		border-right: 1px solid #191919;
	}
	.p-title {
		margin: 0 0 8px;
		font-size: var(--text-xs);
		font-weight: 500;
		color: var(--color-ink-2);
	}
	.p-legend {
		margin-top: 12px;
	}
	.canvas {
		flex: 1;
		min-height: 0;
		padding: 2px 0 8px;
	}
	.leg {
		font-size: 15px;
	}

	.strip {
		grid-area: strip;
		display: flex;
		align-items: center;
		gap: 18px;
		padding: 10px 0 14px;
	}
	.s-label {
		flex: none;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.cards {
		display: flex;
		gap: 8px;
	}

	/* inspector */
	.inspector {
		grid-area: insp;
		align-self: stretch;
		overflow-y: auto;
		margin-top: -18px;
		padding: 18px 22px 24px;
		background: #0c0c0c;
		border-left: 1px solid #1a1a1a;
	}
	.inspector h2 {
		font-size: 15px;
		font-weight: 500;
	}
	h3 {
		margin: 18px 0 8px;
		font-size: var(--text-xs);
		font-weight: 500;
		color: var(--color-ink-2);
	}
	.eq {
		margin: 4px 0 2px;
		font-size: 14px;
		overflow-x: auto;
	}
	.eq :global(.katex-display) {
		margin: 0.4em 0;
		text-align: left;
	}
	.note {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		line-height: 1.55;
	}
	.rules {
		display: grid;
		gap: 6px;
		margin-top: 10px;
	}
	.rules li {
		display: grid;
		grid-template-columns: 52px 1fr auto 34px;
		gap: 10px;
		align-items: center;
	}
	.r-name {
		display: grid;
		font-size: var(--text-xs);
		color: var(--color-ink);
		line-height: 1.25;
	}
	.r-name small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.rules-head {
		display: grid;
		grid-template-columns: 52px 1fr auto 34px;
		gap: 10px;
		margin-top: 12px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.rules-head > span:first-child {
		grid-column: 1 / 3;
	}
	.rh-mass,
	.r-mass {
		display: flex;
		gap: 3px;
	}
	.rh-mass i {
		width: 14px;
		font-size: 9px;
		font-style: normal;
		text-align: center;
	}
	.r-mass i {
		position: relative;
		width: 14px;
		height: 20px;
		border-radius: 2px;
		background: #1a1a1a;
		overflow: hidden;
	}
	.r-mass b {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		background: #8f8f8f;
	}
	.rules li.dominant .r-mass b {
		background: #f2f2f2;
	}
	.r-pct {
		width: 34px;
		font-size: var(--text-2xs);
		text-align: right;
		color: var(--color-ink-3);
	}
	.rules li.dominant .r-pct {
		color: var(--color-ink);
	}
	.mass-note {
		margin-top: 8px;
	}
	.hover {
		min-height: 36px;
	}
	.live-note {
		margin-top: 8px;
		color: var(--color-ink-2);
	}
	.live-note .btn {
		margin-top: 2px;
	}
	.link-btn {
		padding: 0;
		border: 0;
		background: none;
		color: var(--color-ink);
		text-decoration: underline;
		text-underline-offset: 3px;
		font: inherit;
		cursor: pointer;
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
	.group.right {
		margin-left: auto;
	}
	.timeline {
		gap: 0;
	}
	.tick {
		display: grid;
		justify-items: center;
		gap: 5px;
		min-width: 54px;
		padding: 0;
		border: 0;
		background: transparent;
		color: var(--color-ink-3);
		font-size: var(--text-2xs);
		cursor: pointer;
	}
	.tick .dot {
		width: 9px;
		height: 9px;
		border: 1px solid var(--color-ink-3);
		border-radius: 50%;
		background: var(--color-void);
		transition:
			background 200ms ease,
			border-color 200ms ease;
	}
	.tick.on {
		color: var(--color-ink-2);
	}
	.tick.on .dot {
		border-color: var(--color-ink-2);
	}
	.tick.at {
		color: var(--color-ink);
	}
	.tick.at .dot {
		border-color: var(--color-ink);
		background: var(--color-ink);
	}
	.rail-line {
		width: 18px;
		height: 1px;
		margin: 0 -10px 16px;
		background: #262626;
	}
	.rail-line.on {
		background: var(--color-ink-3);
	}
	.t-label {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.keys-row {
		gap: 2px;
	}
	.key {
		display: grid;
		justify-items: center;
		gap: 3px;
		min-width: 44px;
		padding: 5px 4px 3px;
		border: 0;
		border-radius: 6px;
		background: transparent;
		color: var(--color-ink-3);
		font-size: var(--text-2xs);
		cursor: pointer;
	}
	.key:hover {
		color: var(--color-ink);
		background: #141414;
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
	.prune input {
		width: 90px;
	}
	.prune :global(svg) {
		color: var(--color-ink-3);
	}
	.val {
		min-width: 36px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.auto {
		height: 24px;
		padding: 0 9px;
		border: 0;
		border-radius: 5px;
		background: transparent;
		color: var(--color-ink-3);
		font-size: var(--text-xs);
		cursor: pointer;
	}
	.auto[aria-pressed='true'] {
		background: #222;
		color: var(--color-ink);
	}

	@media (max-width: 1200px) {
		.screen {
			height: auto;
			grid-template-columns: minmax(0, 1fr);
			grid-template-areas: 'head' 'diagram' 'strip' 'insp';
			grid-template-rows: auto 460px auto auto;
			padding: 16px 16px var(--transport-h);
		}
		.inspector {
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
		.strip {
			flex-wrap: wrap;
		}
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 26px;
		}
		.title-row {
			flex-wrap: wrap;
			gap: 10px;
		}
	}
</style>
