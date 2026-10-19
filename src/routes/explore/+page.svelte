<script lang="ts">
	import { resolve } from '$app/paths';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { ProbeResult } from '#lib/engine/protocol.ts';
	import {
		cardTensor,
		querySlice,
		setAlignment,
		setPartners,
		sinkMass,
		topHyperedges,
		valueRow
	} from '#lib/explore/analysis.ts';
	import { exactProbe, scoreSlice, type ExactProbe } from '#lib/explore/exact.ts';
	import { dealLayout, findSets, LAYOUT_SIZE, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import FeatureStrip from '#lib/ui/FeatureStrip.svelte';
	import Heatmap from '#lib/ui/Heatmap.svelte';
	import Icon from '#lib/ui/Icon.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import RolePicker from '#lib/ui/RolePicker.svelte';
	import { pct } from '#lib/ui/format.ts';
	import {
		Dice,
		Feynman,
		Newton,
		Next,
		Pause,
		Play,
		Previous,
		Reset,
		Simplex,
		Thermometer
	} from '#lib/ui/icons.ts';
	import Hypergraph3D from '#lib/viz/Hypergraph3D.svelte';
	import TensorCube from '#lib/viz/TensorCube.svelte';

	const bench = getBench();
	const C = LAYOUT_SIZE;

	type Mode = 'tensor' | 'relations' | 'linked';
	type Source = 'exact' | 'trained';
	type Quantity = 'scores' | 'weights';
	let mode = $state<Mode>('linked');
	let source = $state<Source>('exact');
	let quantity = $state<Quantity>('scores');
	let tau = $state(0.33);

	// ── the layout under inspection ──────────────────────────────────────────
	let dealSeed = $state(3);
	/** Deal a layout with at least three SETs so there is structure to look at. */
	function deal(seed: number): Card[] {
		const rng = mulberry32(seed * 7717 + 3);
		for (;;) {
			const l = dealLayout(rng);
			if (findSets(l).length >= 3) return l;
		}
	}
	const layout = $derived(deal(dealSeed));
	const sets = $derived(findSets(layout));
	const firstMember = (l: Card[]) => findSets(l)[0]?.[0] ?? 0;
	let query = $state(firstMember(deal(3)));
	let pick = $state<{ j: number; k: number } | null>(null);

	function newLayout() {
		dealSeed += 1;
		query = firstMember(deal(dealSeed));
		pick = null;
	}

	// ── heads: the exact construction, or the trained cubic model ────────────
	const exact = $derived(exactProbe(layout, 1 / tau));
	let trained = $state.raw<ProbeResult | null>(null);
	const cubicStep = $derived.by(() => {
		void bench.version;
		return bench.history.cubic.step;
	});
	const training = $derived(bench.status === 'training' || bench.status === 'pausing');

	/** Re-probe every 50 steps while training (steps arrive faster than a probe takes). */
	const checkpoint = $derived(Math.floor(cubicStep / 50));
	$effect(() => {
		if (source !== 'trained') return;
		const l = layout;
		void checkpoint;
		let cancelled = false;
		(async () => {
			await bench.ensure();
			const engine = bench.engineHandle;
			if (!engine || cancelled) return;
			const r = await engine.probe('cubic', l);
			if (!cancelled) trained = r;
		})().catch(() => {});
		return () => {
			cancelled = true;
		};
	});

	const probe = $derived<ProbeResult>(source === 'trained' && trained ? trained : exact);
	const hasScores = $derived(probe === exact);
	const shown = $derived<Quantity>(hasScores ? quantity : 'weights');

	const partners = $derived(setPartners(sets, query));
	/** For a trained model, read the head that lines up best with the true SETs. */
	const head = $derived.by(() => {
		if (probe.heads === 1) return 0;
		const a = Array.from({ length: probe.heads }, (_, h) =>
			setAlignment(querySlice(probe, h, query), partners)
		);
		return a.indexOf(Math.max(...a));
	});

	const slice = $derived(querySlice(probe, head, query));
	const edges = $derived(topHyperedges(slice, 5, query));
	const selected = $derived(pick ?? (edges[0] ? { j: edges[0].j, k: edges[0].k } : null));

	/** Normalise to [0, 1] for display; NaN (masked) cells stay NaN. */
	function unit(a: Float32Array): Float32Array {
		let lo = Infinity;
		let hi = -Infinity;
		for (const v of a)
			if (!Number.isNaN(v)) {
				lo = Math.min(lo, v);
				hi = Math.max(hi, v);
			}
		const span = hi - lo || 1;
		return a.map((v) => (Number.isNaN(v) ? NaN : (v - lo) / span));
	}

	const scoreSlices = $derived(
		hasScores ? Array.from({ length: C }, (_, i) => scoreSlice(probe as ExactProbe, i)) : []
	);
	const weightSlices = $derived(Array.from({ length: C }, (_, i) => querySlice(probe, head, i)));
	const ribbon = $derived.by(() => {
		const src = shown === 'scores' ? scoreSlices : weightSlices;
		const flat = new Float32Array(C * C * C);
		src.forEach((s, i) => flat.set(s, i * C * C));
		const u = unit(flat);
		return src.map((_, i) => {
			const sl = u.subarray(i * C * C, (i + 1) * C * C);
			// scores: emphasise the top of the range so SET cells stand out from the texture
			return shown === 'scores' ? sl.map((v) => (Number.isNaN(v) ? NaN : v ** 2.6)) : sl;
		});
	});
	const cubeValues = $derived.by(() => {
		if (shown === 'scores') {
			const u = new Float32Array(C * C * C);
			ribbon.forEach((s, i) =>
				u.set(
					s.map((v) => (Number.isNaN(v) ? 0 : v ** 1.25)),
					i * C * C
				)
			);
			return u;
		}
		return unit(cardTensor(probe, head));
	});
	const graphEdges = $derived.by(() => {
		const top = edges[0]?.weight || 1;
		return edges.map((e) => ({ j: e.j, k: e.k, weight: e.weight / top }));
	});

	// ── read-outs for the inspector ──────────────────────────────────────────
	const n = $derived(probe.n);
	const at = (i: number, j: number, k: number) => ((i + 1) * n + j + 1) * n + k + 1;
	const scoreA = $derived(
		hasScores && selected ? (probe as ExactProbe).scores[at(query, selected.j, selected.k)] : null
	);
	const weightP = $derived(selected ? slice[selected.j * C + selected.k] : 0);
	const weightSwap = $derived(selected ? slice[selected.k * C + selected.j] : 0);
	const sink = $derived(sinkMass(probe, head, query));
	const isSetPick = $derived(
		!!selected &&
			partners.some(
				([a, b]) => (a === selected.j && b === selected.k) || (a === selected.k && b === selected.j)
			)
	);
	const v1 = $derived(selected ? valueRow(probe.v1, probe, head, selected.j + 1) : null);
	const v2 = $derived(selected ? valueRow(probe.v2, probe, head, selected.k + 1) : null);
	const dvec = $derived(v1 && v2 ? v1.map((x, c) => x * v2[c]) : null);
	const vmax = $derived(
		v1 && v2 ? Math.max(1e-6, ...Array.from(v1, Math.abs), ...Array.from(v2, Math.abs)) : 1
	);
	const dmax = $derived(dvec ? Math.max(1e-6, ...Array.from(dvec, Math.abs)) : 1);
	const trueCells = $derived(
		partners.flatMap(([a, b]) => [[a, b] as [number, number], [b, a] as [number, number]])
	);

	// ── query tour ───────────────────────────────────────────────────────────
	let touring = $state(false);
	$effect(() => {
		if (!touring) return;
		const id = setInterval(() => step(1), 1400);
		return () => clearInterval(id);
	});
	function setQuery(t: number) {
		query = t;
		pick = null;
	}
	function step(delta: number) {
		setQuery((query + delta + C) % C);
	}
	function reset() {
		touring = false;
		tau = 0.33;
		quantity = 'scores';
		setQuery(firstMember(layout));
	}
	function trainCubic() {
		source = 'trained';
		bench.start({ only: ['cubic'], until: Math.max(1500, cubicStep + 500) });
	}
	let ribbonWidth = $state(1100);
	let innerWidth = $state(1600);

	// the dotted leader from the selected voxel to the query node
	let cubeAnchor = $state<{ x: number; y: number } | null>(null);
	let graphAnchor = $state<{ x: number; y: number } | null>(null);
	const link = $derived(
		mode === 'linked' && innerWidth > 1100 && cubeAnchor && graphAnchor
			? { a: cubeAnchor, b: graphAnchor }
			: null
	);
	/** Twelve slices across the ribbon: width minus gaps, padding and borders. */
	const sliceSize = $derived(
		Math.max(48, Math.min(84, Math.floor((ribbonWidth - 11 * 8 - 12 * 10) / C)))
	);
</script>

<svelte:head>
	<title>Linked tensor lab | Polyformer</title>
</svelte:head>
<svelte:window bind:innerWidth />

<PageFrame
	rail={[
		{ id: 'tensor', label: 'Cubic', icon: Simplex, href: resolve('/explore') },
		{ id: 'diagrams', label: 'Feynman', icon: Feynman, href: resolve('/explore/diagrams') },
		{ id: 'newton', label: 'Newton', icon: Newton, href: resolve('/explore/newton') }
	]}
	active="tensor"
>
	<div class="lab" data-mode={mode}>
		<header class="head">
			<div class="title-row">
				<h1>Cubic attention</h1>
				<div class="seg" role="group" aria-label="Layout">
					<button aria-pressed={mode === 'tensor'} onclick={() => (mode = 'tensor')}>Tensor</button>
					<button aria-pressed={mode === 'relations'} onclick={() => (mode = 'relations')}
						>Relations</button
					>
					<button aria-pressed={mode === 'linked'} onclick={() => (mode = 'linked')}>Linked</button>
				</div>
			</div>
			<p class="sub">
				One head scores every query against every ordered pair of other cards. Pick a card, a voxel
				or a membrane; all views follow.
			</p>
		</header>

		<section class="stage" aria-label="Linked views">
			<div class="view cube-view" id="tensor">
				<div class="view-label">
					<span
						>{shown === 'scores' ? 'Attention scores' : 'Attention weights'}
						<MathTex tex={shown === 'scores' ? 'A' : 'P'} /></span
					>
				</div>
				<TensorCube
					values={cubeValues}
					n={C}
					{query}
					{selected}
					onpick={(c) => {
						query = c.i;
						pick = { j: c.j, k: c.k };
					}}
					onanchor={(p) => (cubeAnchor = p)}
				/>
				<div class="view-foot">Drag to orbit. Click a bright voxel to select it.</div>
			</div>
			<div class="view graph-view" id="relations">
				<div class="view-label">
					<span>Linked view</span>
					<small>The selected hyperedge is the selected voxel.</small>
				</div>
				<Hypergraph3D
					{layout}
					{query}
					edges={graphEdges}
					{selected}
					{sets}
					onquery={setQuery}
					onedge={(e) => (pick = e)}
					onanchor={(p) => (graphAnchor = p)}
				/>
			</div>
		</section>

		<aside class="inspector" id="algebra" aria-label="Selected interaction">
			<div class="insp-head">
				<h2>Selected interaction</h2>
			</div>

			<div class="pickers">
				{#if selected}
					<RolePicker
						{layout}
						{query}
						j={selected.j}
						k={selected.k}
						onchange={(next) => {
							if (next.query !== query) setQuery(next.query);
							else pick = { j: next.j, k: next.k };
						}}
					/>
				{/if}
			</div>

			<div class="block">
				<h3>Attention score</h3>
				<div class="eq">
					<MathTex display tex={'A_{ijk} = \\langle Q_i,\\ K^1_j \\odot K^2_k \\rangle'} />
				</div>
				<p class="note">A query scores a pair of keys.</p>
			</div>

			<div class="block">
				<h3>Value interaction</h3>
				<div class="eq"><MathTex display tex={'D_{jk} = V^1_j \\odot V^2_k'} /></div>
				<p class="note">Pairs of values interact before aggregation.</p>
			</div>

			<div class="block">
				<h3>Value features</h3>
				{#if v1 && v2 && dvec}
					<div class="strips">
						<MathTex tex="V^1_j" /><FeatureStrip
							values={v1}
							max={vmax}
							cell={11}
							height={16}
							label="Role 1 value features"
						/>
						<MathTex tex="V^2_k" /><FeatureStrip
							values={v2}
							max={vmax}
							cell={11}
							height={16}
							label="Role 2 value features"
						/>
					</div>
					<h3 class="mt">Resulting feature vector</h3>
					<div class="strips">
						<MathTex tex={'D_{jk}'} /><FeatureStrip
							values={dvec}
							max={dmax}
							cell={11}
							height={16}
							label="Pair value features"
						/>
					</div>
				{/if}
			</div>

			<div class="block">
				<h3>Selected quantities</h3>
				<table class="qty">
					<tbody>
						<tr>
							<th><MathTex tex={'A_{ijk}'} /></th>
							<td>Scalar score</td>
							<td class="num">{scoreA === null ? '—' : scoreA.toFixed(2)}</td>
						</tr>
						<tr>
							<th><MathTex tex={'P_{ijk}'} /></th>
							<td>Scalar weight</td>
							<td class="num">{pct(weightP, 1)}</td>
						</tr>
						<tr>
							<th><MathTex tex={'P_{ikj}'} /></th>
							<td>Swapped roles</td>
							<td class="num">{pct(weightSwap, 1)}</td>
						</tr>
						<tr>
							<th>Sink</th>
							<td>No pair fits</td>
							<td class="num">{pct(sink, 1)}</td>
						</tr>
						<tr>
							<th>SET</th>
							<td>Do <i>i, j, k</i> form one?</td>
							<td>{isSetPick ? 'Yes' : 'No'}</td>
						</tr>
					</tbody>
				</table>
			</div>

			<div class="source block">
				<h3>{source === 'exact' ? 'Constructed head' : 'Trained head'}</h3>
				{#if source === 'exact'}
					<p class="note">
						Built by hand, not learned: 16 trilinear channels compute
						<MathTex tex={'\\sum_t \\cos\\tfrac{2\\pi}{3}(a_t+b_t+c_t)'} />, which is 4 for every
						SET and at most 2.5 otherwise. Switch the head to Trained to see what gradient descent
						finds.
					</p>
				{:else if cubicStep === 0}
					<p class="note">
						The cubic model has not trained yet, so this view still shows the constructed head.
					</p>
					<button class="btn primary" onclick={trainCubic} disabled={training}>
						<Icon icon={Play} size={14} />Train to step 1,500
					</button>
				{:else}
					<p class="note num">
						Learned by gradient descent, step {cubicStep.toLocaleString('en-US')}. Head {head + 1} lines
						up best with the true SETs.
					</p>
				{/if}
			</div>
		</aside>

		<section class="ribbon" id="maps" aria-label="Query slices">
			<div class="ribbon-head">
				<h2>Query slices of <MathTex tex={shown === 'scores' ? 'A' : 'P'} /></h2>
				<div class="seg" role="group" aria-label="Quantity">
					<button
						aria-pressed={shown === 'scores'}
						disabled={!hasScores}
						onclick={() => (quantity = 'scores')}>Scores</button
					>
					<button aria-pressed={shown === 'weights'} onclick={() => (quantity = 'weights')}
						>Weights</button
					>
				</div>
			</div>
			<div class="slices" bind:clientWidth={ribbonWidth}>
				{#each ribbon as s, i (i)}
					<button
						class="slice"
						class:on={i === query}
						onclick={() => setQuery(i)}
						aria-label="Query slice for card {i + 1}"
					>
						<span class="s-label"><i>i</i> = {i + 1}</span>
						<Heatmap
							values={s}
							rows={C}
							cols={C}
							size={sliceSize}
							max={1}
							selected={i === query && selected ? [selected.j, selected.k] : null}
							marks={i === query ? trueCells : []}
							label="Slice for card {i + 1}"
						/>
					</button>
				{/each}
			</div>
		</section>

		<footer class="transport" aria-label="Lab controls">
			<div class="group">
				<span class="t-label">Query <i>i</i></span>
				<div class="stepper">
					<button onclick={() => step(-1)} aria-label="Previous query"
						><Icon icon={Previous} size={16} /></button
					>
					<span class="num">{query + 1}</span>
					<button onclick={() => step(1)} aria-label="Next query"
						><Icon icon={Next} size={16} /></button
					>
				</div>
			</div>
			<div class="group temp">
				<Icon icon={Thermometer} size={16} />
				<label class="t-label" for="tau">Temperature <i>τ</i></label>
				<input
					id="tau"
					type="range"
					min="0.08"
					max="1.5"
					step="0.01"
					bind:value={tau}
					disabled={source !== 'exact'}
				/>
				<span class="num val">{tau.toFixed(2)}</span>
			</div>
			<div class="group">
				<span class="t-label">Head</span>
				<div class="seg" role="group" aria-label="Head">
					<button aria-pressed={source === 'exact'} onclick={() => (source = 'exact')}
						>Constructed</button
					>
					<button aria-pressed={source === 'trained'} onclick={() => (source = 'trained')}
						>Trained</button
					>
				</div>
			</div>
			<div class="group keys">
				<button class="key" onclick={reset}
					><Icon icon={Reset} size={17} /><span>Reset</span></button
				>
				<button class="key" onclick={() => step(-1)}
					><Icon icon={Previous} size={17} /><span>Back</span></button
				>
				<button class="key play" class:on={touring} onclick={() => (touring = !touring)}>
					<Icon icon={touring ? Pause : Play} size={17} /><span>{touring ? 'Pause' : 'Tour'}</span>
				</button>
				<button class="key" onclick={() => step(1)}
					><Icon icon={Next} size={17} /><span>Step</span></button
				>
				<button class="key" onclick={newLayout}
					><Icon icon={Dice} size={17} /><span>Deal</span></button
				>
			</div>
			<div class="group right">
				<span class="t-label num">{sets.length} SETs on the table</span>
			</div>
		</footer>
		{#if link}
			<svg class="link" aria-hidden="true">
				<line x1={link.a.x} y1={link.a.y} x2={link.b.x} y2={link.b.y} />
				<circle cx={link.a.x} cy={link.a.y} r="2.5" />
			</svg>
		{/if}
	</div>
</PageFrame>

<style>
	.lab {
		--transport-h: 60px;
		display: grid;
		grid-template-columns: minmax(0, 1fr) 312px;
		grid-template-rows: auto minmax(300px, 1fr) auto;
		grid-template-areas:
			'head insp'
			'stage insp'
			'ribbon insp';
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
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.025em;
		line-height: 1.1;
	}
	.sub {
		margin-top: 6px;
		max-width: 70ch;
		color: var(--color-ink-3);
		font-size: var(--text-sm);
	}

	.stage {
		grid-area: stage;
		display: grid;
		grid-template-columns: 1.08fr 1fr;
		min-height: 0;
		margin-top: 4px;
	}
	/* a single view takes the whole stage; the other is hidden, never squeezed to zero */
	.lab[data-mode='tensor'] .stage,
	.lab[data-mode='relations'] .stage {
		grid-template-columns: minmax(0, 1fr);
	}
	.lab[data-mode='tensor'] .graph-view,
	.lab[data-mode='relations'] .cube-view {
		display: none;
	}
	.view {
		position: relative;
		min-height: 0;
		min-width: 0;
	}
	.view-label {
		position: absolute;
		z-index: 2;
		top: 8px;
		left: 0;
		display: flex;
		flex-direction: column;
		gap: 2px;
		font-size: 15px;
		font-weight: 500;
		pointer-events: none;
	}
	.view-label > span {
		display: flex;
		gap: 6px;
		align-items: baseline;
	}
	.view-label small {
		font-size: var(--text-xs);
		font-weight: 400;
		color: var(--color-ink-3);
	}
	.graph-view .view-label {
		left: 12px;
	}
	.view-foot {
		position: absolute;
		left: 0;
		bottom: 6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		pointer-events: none;
	}

	/* inspector: one quiet column, spacing instead of boxes */
	.inspector {
		grid-area: insp;
		align-self: stretch;
		overflow-y: auto;
		margin-top: -18px;
		padding: 18px 22px 24px;
		background: #0c0c0c;
		border-left: 1px solid #1a1a1a;
	}
	.insp-head {
		padding-bottom: 6px;
	}
	h2 {
		display: flex;
		gap: 6px;
		align-items: baseline;
		font-size: 15px;
		font-weight: 500;
		color: var(--color-ink);
	}
	.pickers {
		padding: 12px 0 4px;
	}
	.t-label i,
	.s-label i {
		font-family: var(--font-math);
		font-size: 1.15em;
		color: var(--color-ink);
	}
	.block {
		padding: 14px 0 4px;
	}
	h3 {
		font-size: var(--text-xs);
		font-weight: 500;
		color: var(--color-ink-2);
		margin-bottom: 4px;
	}
	h3.mt {
		margin-top: 12px;
	}
	.eq {
		font-size: 18px;
	}
	.eq :global(.katex-display) {
		margin: 0.1em 0;
		text-align: left;
	}
	.note {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		line-height: 1.5;
	}
	.strips {
		display: grid;
		grid-template-columns: 30px 1fr;
		gap: 8px 6px;
		align-items: center;
		font-size: 14px;
	}
	.qty {
		width: 100%;
		border-collapse: collapse;
		font-size: var(--text-xs);
	}
	.qty th {
		width: 48px;
		text-align: left;
		font-weight: 400;
		font-size: 14px;
		color: var(--color-ink);
	}
	.qty td {
		padding: 5px 0;
		color: var(--color-ink-3);
	}
	.qty td.num {
		text-align: right;
		color: var(--color-ink);
	}
	.source .btn {
		margin-top: 10px;
	}

	/* ribbon */
	.ribbon {
		grid-area: ribbon;
		padding: 8px 0 12px;
	}
	.ribbon-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 6px;
	}
	.slices {
		display: flex;
		gap: 8px;
		overflow-x: auto;
		padding-bottom: 2px;
	}
	.slice {
		display: grid;
		gap: 4px;
		justify-items: center;
		padding: 5px;
		border: 0;
		border-radius: 6px;
		background: transparent;
		color: var(--color-ink-3);
		cursor: pointer;
	}
	.slice:hover {
		background: #121212;
	}
	.slice.on {
		background: #161616;
		color: var(--color-ink);
	}
	.s-label {
		font-size: var(--text-2xs);
		white-space: nowrap;
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
		gap: 30px;
		padding: 0 22px 0 28px;
		border-top: 1px solid #1a1a1a;
		background: var(--color-void);
	}
	.group {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	.group.right {
		margin-left: auto;
	}
	.t-label {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		white-space: nowrap;
	}
	.stepper {
		display: flex;
		align-items: center;
		height: 28px;
		border-radius: 6px;
		background: #1a1a1a;
	}
	.stepper button {
		display: grid;
		place-items: center;
		width: 28px;
		height: 100%;
		border: 0;
		background: transparent;
		color: var(--color-ink-3);
		cursor: pointer;
	}
	.stepper button:hover {
		color: var(--color-ink);
	}
	.stepper span {
		min-width: 24px;
		text-align: center;
		font-size: var(--text-sm);
	}
	.temp input {
		width: 140px;
	}
	.temp :global(svg) {
		color: var(--color-ink-3);
	}
	.val {
		min-width: 34px;
		font-size: var(--text-sm);
		color: var(--color-ink);
	}
	.keys {
		gap: 2px;
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

	.link {
		position: fixed;
		inset: 0;
		z-index: 5;
		width: 100%;
		height: 100%;
		pointer-events: none;
	}
	.link line {
		stroke: rgb(245 245 245 / 0.6);
		stroke-width: 1;
		stroke-dasharray: 1.5 4;
	}
	.link circle {
		fill: var(--color-ink);
	}

	@media (max-width: 1100px) {
		.lab {
			height: auto;
			grid-template-columns: minmax(0, 1fr);
			grid-template-areas: 'head' 'stage' 'ribbon' 'insp';
			padding: 16px 16px var(--transport-h);
		}
		.stage {
			grid-template-columns: minmax(0, 1fr);
			grid-auto-rows: 380px;
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
	}
	@media (max-width: 640px) {
		h1 {
			font-size: 24px;
		}
		.title-row {
			flex-wrap: wrap;
			gap: 10px;
		}
		.stage {
			grid-auto-rows: 320px;
		}
	}
</style>
