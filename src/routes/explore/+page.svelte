<script lang="ts">
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { ProbeResult } from '#lib/engine/protocol.ts';
	import {
		cardTensor,
		pairMoment,
		querySlice,
		setAlignment,
		setPartners,
		sinkMass,
		topHyperedges,
		valueRow
	} from '#lib/explore/analysis.ts';
	import { OPERATORS } from '#lib/model/operators/index.ts';
	import { dealLayout, findSets, LAYOUT_SIZE, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import FeatureStrip from '#lib/ui/FeatureStrip.svelte';
	import Heatmap from '#lib/ui/Heatmap.svelte';
	import Hypergraph from '#lib/ui/Hypergraph.svelte';
	import Icon from '#lib/ui/Icon.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import VoxelCube from '#lib/ui/VoxelCube.svelte';
	import { pct } from '#lib/ui/format.ts';
	import {
		ArrowLeft,
		ArrowRight,
		Cube,
		Dice,
		FunctionIcon,
		Grid,
		Network,
		Play
	} from '#lib/ui/icons.ts';

	const bench = getBench();
	const C = LAYOUT_SIZE;

	type Mode = 'tensor' | 'relations' | 'linked';
	let mode = $state<Mode>('linked');
	let section = $state('tensor');

	// ── the layout under inspection ──────────────────────────────────────────
	let dealSeed = $state(1);
	/** Deal a layout with at least two SETs so there is structure to look at. */
	function deal(seed: number): Card[] {
		const rng = mulberry32(seed * 7717 + 3);
		for (;;) {
			const l = dealLayout(rng);
			if (findSets(l).length >= 2) return l;
		}
	}
	const layout = $derived(deal(dealSeed));
	const sets = $derived(findSets(layout));

	const firstMember = (l: Card[]) => findSets(l)[0]?.[0] ?? 0;
	let query = $state(firstMember(deal(1)));
	let headChoice = $state<number | 'auto'>('auto');
	let pick = $state<{ j: number; k: number } | null>(null);

	function newLayout() {
		dealSeed += 1;
		query = firstMember(deal(dealSeed));
		pick = null;
	}

	// ── probe the cubic model ────────────────────────────────────────────────
	let probe = $state.raw<ProbeResult | null>(null);
	let probeError = $state<string | null>(null);

	const cubic = $derived.by(() => {
		void bench.version;
		const h = bench.history.cubic;
		return { step: h.step, acc: h.evalAccuracy.at(-1) };
	});
	const training = $derived(bench.status === 'training' || bench.status === 'pausing');

	// Re-probe when the layout changes, and at most twice a second while training.
	$effect(() => {
		const l = layout;
		const step = cubic.step;
		void step;
		let cancelled = false;
		const timer = setTimeout(
			async () => {
				try {
					await bench.ensure();
					const engine = bench.engineHandle;
					if (!engine || cancelled) return;
					const r = await engine.probe('cubic', l);
					if (!cancelled) {
						probe = r;
						probeError = null;
					}
				} catch (e) {
					if (!cancelled) probeError = e instanceof Error ? e.message : String(e);
				}
			},
			training ? 500 : 0
		);
		return () => {
			cancelled = true;
			clearTimeout(timer);
		};
	});

	function trainCubic() {
		bench.start({ only: ['cubic'], until: Math.max(1500, cubic.step + 500) });
	}

	// ── read-outs ────────────────────────────────────────────────────────────
	const partners = $derived(setPartners(sets, query));
	const alignment = $derived(
		probe ? [0, 1, 2, 3].map((h) => setAlignment(querySlice(probe!, h, query), partners)) : []
	);
	const head = $derived(
		headChoice !== 'auto'
			? headChoice
			: alignment.length
				? alignment.indexOf(Math.max(...alignment))
				: 0
	);
	const slice = $derived(probe ? querySlice(probe, head, query) : new Float32Array(C * C));
	const edges = $derived(probe ? topHyperedges(slice, 6, query) : []);
	const selected = $derived(pick ?? (edges[0] ? { j: edges[0].j, k: edges[0].k } : null));
	const tensor = $derived(probe ? cardTensor(probe, head) : null);
	const slices = $derived(
		probe ? Array.from({ length: C }, (_, i) => querySlice(probe!, head, i)) : []
	);
	const moment = $derived(probe ? pairMoment(probe, head, query) : null);
	const sink = $derived(probe ? sinkMass(probe, head, query) : 0);

	const weightJK = $derived(selected ? slice[selected.j * C + selected.k] : 0);
	const weightKJ = $derived(selected ? slice[selected.k * C + selected.j] : 0);
	const selectedIsSet = $derived(
		!!selected &&
			partners.some(
				([a, b]) => (a === selected.j && b === selected.k) || (a === selected.k && b === selected.j)
			)
	);

	const v1 = $derived(probe && selected ? valueRow(probe.v1, probe, head, selected.j + 1) : null);
	const v2 = $derived(probe && selected ? valueRow(probe.v2, probe, head, selected.k + 1) : null);
	const d = $derived(v1 && v2 ? v1.map((x, c) => x * v2[c]) : null);
	const vmax = $derived(
		v1 && v2 ? Math.max(...Array.from(v1, Math.abs), ...Array.from(v2, Math.abs)) : 1
	);
	const dmax = $derived(d ? Math.max(1e-6, ...Array.from(d, Math.abs)) : 1);
	const momentMax = $derived(moment ? Math.max(1e-6, ...Array.from(moment, Math.abs)) : 1);
	const trueCells = $derived(
		partners.flatMap(([a, b]) => [[a, b] as [number, number], [b, a] as [number, number]])
	);
	const prob = $derived(probe ? probe.probs[query] : undefined);
	const isMember = $derived(partners.length > 0);

	function setQuery(t: number) {
		query = t;
		pick = null;
	}
	function step(delta: number) {
		setQuery((query + delta + C) % C);
	}
</script>

<svelte:head>
	<title>Linked tensor lab | Polyformer</title>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'tensor', label: 'Tensor', icon: Cube },
		{ id: 'relations', label: 'Relations', icon: Network },
		{ id: 'maps', label: 'Maps', icon: Grid },
		{ id: 'algebra', label: 'Algebra', icon: FunctionIcon }
	]}
	active={section}
	onselect={(id) => (section = id)}
>
	<div class="lab" data-mode={mode}>
		<header class="head">
			<div class="title">
				<h1 class="page-title">Cubic attention</h1>
				<div class="seg" role="group" aria-label="View">
					<button aria-pressed={mode === 'tensor'} onclick={() => (mode = 'tensor')}>Tensor</button>
					<button aria-pressed={mode === 'relations'} onclick={() => (mode = 'relations')}
						>Relations</button
					>
					<button aria-pressed={mode === 'linked'} onclick={() => (mode = 'linked')}>Linked</button>
				</div>
			</div>
			<p class="lede">
				One trained cubic head, read three ways. Pick a query card: the cube, the hypergraph and the
				slice all show where it puts its weight over ordered pairs of other cards.
			</p>
			<div class="model">
				{#if cubic.step === 0}
					<span class="hint">The cubic model is untrained, so its weights are diffuse.</span>
					<button
						class="btn primary"
						onclick={trainCubic}
						disabled={training || bench.status === 'booting'}
					>
						<Icon icon={Play} size={14} />Train cubic to step 1,500
					</button>
				{:else}
					<span class="hint num">
						Cubic model at step {cubic.step.toLocaleString('en-US')}{cubic.acc !== undefined
							? `, ${pct(cubic.acc)} held-out token accuracy`
							: ''}
					</span>
					{#if !training && cubic.step < 1500}
						<button class="btn" onclick={trainCubic}
							><Icon icon={Play} size={14} />Keep training</button
						>
					{/if}
				{/if}
				{#if probeError}<span class="hint">{probeError}</span>{/if}
			</div>
		</header>

		<div class="stage">
			<section class="panel view cube-view" id="tensor" aria-label="Attention tensor">
				<div class="panel-head">
					<div class="panel-title">
						<Icon icon={Cube} size={16} />Normalized weights <MathTex tex={'P_{ijk}'} />
					</div>
					<span class="hint">Drag to orbit, click a bright cell</span>
				</div>
				<div class="cube-wrap">
					<VoxelCube
						values={tensor}
						n={C}
						{query}
						{selected}
						onpick={(c) => {
							query = c.i;
							pick = { j: c.j, k: c.k };
						}}
					/>
				</div>
			</section>

			<section class="panel view graph-view" id="relations" aria-label="Hypergraph">
				<div class="panel-head">
					<div class="panel-title">
						<Icon icon={Network} size={16} />Top hyperedges of query {query + 1}
					</div>
					<span class="legend">
						<span class="lg"
							><svg width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4.5" /></svg
							>query <i>i</i></span
						>
						<span class="lg"
							><svg width="12" height="12" aria-hidden="true"
								><rect x="2" y="2" width="8" height="8" /></svg
							>role 1 <i>j</i></span
						>
						<span class="lg"
							><svg width="12" height="12" aria-hidden="true"
								><polygon points="6,1 11,6 6,11 1,6" /></svg
							>role 2 <i>k</i></span
						>
						<span class="lg"
							><svg width="16" height="12" aria-hidden="true"
								><line x1="1" y1="6" x2="15" y2="6" class="dash" /></svg
							>true SET</span
						>
					</span>
				</div>
				<div class="graph-wrap">
					<Hypergraph
						{layout}
						{query}
						{edges}
						{selected}
						truth={partners}
						onquery={setQuery}
						onedge={(e) => (pick = e)}
					/>
				</div>
			</section>

			<aside class="panel inspector" id="algebra" aria-label="Selected interaction">
				<div class="panel-head"><div class="panel-title">Selected interaction</div></div>
				{#if selected}
					<div class="roles">
						<div class="role">
							<svg width="12" height="12" aria-hidden="true"><circle cx="6" cy="6" r="4.5" /></svg>
							<span>Query <i>i</i></span>
							<SetCard card={layout[query]} width={44} />
						</div>
						<div class="role">
							<svg width="12" height="12" aria-hidden="true"
								><rect x="2" y="2" width="8" height="8" /></svg
							>
							<span>Role 1 <i>j</i></span>
							<SetCard card={layout[selected.j]} width={44} />
						</div>
						<div class="role">
							<svg width="12" height="12" aria-hidden="true"
								><polygon points="6,1 11,6 6,11 1,6" /></svg
							>
							<span>Role 2 <i>k</i></span>
							<SetCard card={layout[selected.k]} width={44} />
						</div>
					</div>

					<div class="block">
						<div class="label">Attention score</div>
						<MathTex display tex={OPERATORS.cubic.logitTex} />
						<dl class="kv">
							<div>
								<dt><MathTex tex={'P_{ijk}'} /></dt>
								<dd class="num">{pct(weightJK, 2)}</dd>
							</div>
							<div>
								<dt><MathTex tex={'P_{ikj}'} /></dt>
								<dd class="num">{pct(weightKJ, 2)}</dd>
							</div>
							<div>
								<dt>Sink</dt>
								<dd class="num">{pct(sink, 1)}</dd>
							</div>
							<div>
								<dt>Is a SET</dt>
								<dd>{selectedIsSet ? 'Yes' : 'No'}</dd>
							</div>
						</dl>
					</div>

					<div class="block">
						<div class="label">Value interaction</div>
						<MathTex display tex={'D_{jk} = V^1_j \\odot V^2_k'} />
						{#if v1 && v2 && d}
							<div class="strips">
								<MathTex tex="V^1_j" /><FeatureStrip
									values={v1}
									max={vmax}
									label="Role 1 value features"
								/>
								<MathTex tex="V^2_k" /><FeatureStrip
									values={v2}
									max={vmax}
									label="Role 2 value features"
								/>
								<MathTex tex={'D_{jk}'} /><FeatureStrip
									values={d}
									max={dmax}
									label="Pair value features"
								/>
							</div>
						{/if}
					</div>

					<div class="block">
						<div class="label">Prediction for query {query + 1}</div>
						<p class="pred">
							<span class="num">{pct(prob)}</span> in a SET.
							<span class="hint">{isMember ? 'It is in one.' : 'It is in none.'}</span>
						</p>
					</div>
				{/if}
			</aside>
		</div>

		<div class="maps" id="maps">
			<section class="panel map" aria-label="Query slice">
				<div class="panel-head">
					<div class="panel-title">Query slice <MathTex tex={'P_{i,:,:}'} /></div>
					<span class="hint">rows <i>j</i>, columns <i>k</i>; dots mark true SETs</span>
				</div>
				<div class="map-body">
					<Heatmap
						values={slice}
						rows={C}
						cols={C}
						size={216}
						selected={selected ? [selected.j, selected.k] : null}
						marks={trueCells}
						label="Query slice of P for query {query + 1}"
						onpick={([j, k]) => j !== k && (pick = { j, k })}
					/>
				</div>
			</section>

			<section class="panel map" aria-label="Pair moment">
				<div class="panel-head">
					<div class="panel-title">Pair moment <MathTex tex={'M_i = V^{1\\top} P_i V^2'} /></div>
				</div>
				<div class="map-body">
					{#if moment && probe}
						<Heatmap
							values={moment}
							rows={probe.dh}
							cols={probe.dh}
							size={216}
							scale="signed"
							max={momentMax}
							diagonal
							label="Pair moment matrix for query {query + 1}"
						/>
					{/if}
					<p class="hint cap">
						Every feature pair the head could bind. Its outlined diagonal is the Hadamard output
						<MathTex tex={'Y_i = \\sum_{jk} P_{ijk} D_{jk}'} />.
					</p>
				</div>
			</section>

			<section class="panel map ribbon" aria-label="All query slices">
				<div class="panel-head">
					<div class="panel-title">Query slices of <MathTex tex="P" /></div>
					<span class="hint"
						>head {head + 1}{headChoice === 'auto' ? ', most SET-aligned' : ''}</span
					>
				</div>
				<div class="thumbs">
					{#each slices as s, i (i)}
						<button
							class={['thumb', i === query && 'on']}
							onclick={() => setQuery(i)}
							aria-label="Query card {i + 1}"
						>
							<span class="hint num"><i>i</i> = {i + 1}</span>
							<Heatmap
								values={s}
								rows={C}
								cols={C}
								size={60}
								gap={0}
								label="Slice for query {i + 1}"
							/>
						</button>
					{/each}
				</div>
			</section>
		</div>

		<footer class="transport" aria-label="Lab controls">
			<span class="hint">Query <i>i</i></span>
			<button class="btn icon-only" aria-label="Previous query" onclick={() => step(-1)}
				><Icon icon={ArrowLeft} size={16} /></button
			>
			<span class="num q">{query + 1}</span>
			<button class="btn icon-only" aria-label="Next query" onclick={() => step(1)}
				><Icon icon={ArrowRight} size={16} /></button
			>
			<span class="divider"></span>
			<span class="hint">Head</span>
			<div class="seg" role="group" aria-label="Attention head">
				<button aria-pressed={headChoice === 'auto'} onclick={() => (headChoice = 'auto')}
					>Auto</button
				>
				{#each [0, 1, 2, 3] as h (h)}
					<button
						aria-pressed={headChoice === h}
						onclick={() => (headChoice = h)}
						title={alignment.length ? `${pct(alignment[h])} of weight on true SETs` : undefined}
						>{h + 1}</button
					>
				{/each}
			</div>
			<span class="divider"></span>
			<button class="btn" onclick={newLayout}><Icon icon={Dice} size={16} />Deal new layout</button>
			<span class="hint sets num">{sets.length} SETs on the table</span>
		</footer>
	</div>
</PageFrame>

<style>
	.lab {
		display: flex;
		flex-direction: column;
		gap: 14px;
		padding: 18px 20px 0;
		min-height: calc(100dvh - var(--bar-h));
	}
	.head {
		display: grid;
		grid-template-columns: auto 1fr auto;
		align-items: center;
		gap: 6px 24px;
	}
	.title {
		display: flex;
		align-items: center;
		gap: 16px;
	}
	.head .lede {
		margin: 0;
		font-size: var(--text-sm);
		max-width: 62ch;
	}
	.model {
		display: flex;
		align-items: center;
		gap: 12px;
		justify-content: flex-end;
	}

	.stage {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.08fr) 292px;
		gap: 14px;
		min-height: 440px;
	}
	.lab[data-mode='tensor'] .stage {
		grid-template-columns: minmax(0, 1fr) 292px;
	}
	.lab[data-mode='tensor'] .graph-view,
	.lab[data-mode='relations'] .cube-view {
		display: none;
	}
	.lab[data-mode='relations'] .stage {
		grid-template-columns: minmax(0, 1fr) 292px;
	}
	.view {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}
	.cube-wrap,
	.graph-wrap {
		position: relative;
		flex: 1;
		min-height: 380px;
	}
	.graph-wrap {
		padding: 10px 18px 18px;
	}
	.legend {
		display: flex;
		gap: 12px;
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.lg {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		white-space: nowrap;
	}
	.lg svg,
	.role svg {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1.3;
	}
	.lg .dash {
		stroke: var(--color-ink-2);
		stroke-dasharray: 3 3;
	}

	.inspector {
		display: flex;
		flex-direction: column;
		min-width: 0;
	}
	.roles {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 6px;
		padding: 12px 14px;
		border-bottom: 1px solid #222;
	}
	.role {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6px;
		padding: 8px 4px;
		border: 1px solid var(--color-edge);
		border-radius: var(--radius-ui);
		background: var(--color-well);
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.block {
		padding: 12px 14px;
		border-bottom: 1px solid #222;
	}
	.block:last-child {
		border-bottom: 0;
	}
	.label {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.kv {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 4px 16px;
		margin: 2px 0 0;
		font-size: var(--text-sm);
	}
	.kv div {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
	}
	.kv dt {
		color: var(--color-ink-2);
	}
	.kv dd {
		margin: 0;
	}
	.strips {
		display: grid;
		grid-template-columns: 34px auto;
		align-items: center;
		gap: 6px 8px;
		margin-top: 2px;
	}
	.pred {
		margin-top: 4px;
		font-size: var(--text-sm);
	}

	.maps {
		display: grid;
		grid-template-columns: auto auto minmax(0, 1fr);
		gap: 14px;
	}
	.map-body {
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding: 14px;
	}
	.cap {
		max-width: 216px;
	}
	.thumbs {
		display: grid;
		grid-template-columns: repeat(6, max-content);
		gap: 10px 12px;
		padding: 12px 14px;
		justify-content: start;
	}
	.thumb {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		padding: 4px;
		border: 1px solid transparent;
		border-radius: var(--radius-ui);
		background: none;
		color: inherit;
		font: inherit;
		cursor: pointer;
	}
	.thumb:hover {
		border-color: var(--color-edge);
	}
	.thumb.on {
		border-color: var(--color-ink);
		box-shadow: 0 0 10px rgb(255 255 255 / 0.18);
	}

	.transport {
		position: sticky;
		bottom: 0;
		margin: auto -20px 0;
		display: flex;
		align-items: center;
		gap: 10px;
		height: 52px;
		padding: 0 20px;
		background: rgb(8 8 8 / 0.94);
		border-top: 1px solid var(--color-edge);
		backdrop-filter: blur(6px);
	}
	.q {
		min-width: 18px;
		text-align: center;
	}
	.divider {
		width: 1px;
		height: 20px;
		background: var(--color-edge);
		margin: 0 6px;
	}
	.sets {
		margin-left: auto;
	}

	@media (max-width: 1320px) {
		.stage {
			grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		}
		.inspector {
			grid-column: 1 / -1;
		}
		.maps {
			grid-template-columns: auto auto;
		}
		.ribbon {
			grid-column: 1 / -1;
		}
		.head {
			grid-template-columns: 1fr;
		}
		.model {
			justify-content: flex-start;
		}
	}
	@media (max-width: 760px) {
		.lab {
			padding: 14px 16px 0;
		}
		.stage,
		.lab[data-mode] .stage {
			grid-template-columns: minmax(0, 1fr);
		}
		.maps {
			grid-template-columns: minmax(0, 1fr);
		}
		.thumbs {
			grid-template-columns: repeat(4, max-content);
		}
		.legend {
			display: none;
		}
		.transport {
			margin: auto -16px 0;
			padding: 0 16px;
			overflow-x: auto;
		}
		.sets {
			display: none;
		}
	}
</style>
