<script lang="ts">
	import { asset, resolve } from '$app/paths';
	import { untrack } from 'svelte';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import type { Knockout, NewtonProbe } from '#lib/engine/protocol.ts';
	import {
		CLASSES,
		cardPhases,
		charValue,
		classStrength,
		countFound,
		fitChannels,
		type ChannelFit
	} from '#lib/explore/characters.ts';
	import { DECK, cardId, dealLayout, type Card } from '#lib/set/cards.ts';
	import { mulberry32 } from '#lib/set/rng.ts';
	import { zeroSumMembers } from '#lib/tasks/matchk.ts';
	import Icon from '#lib/ui/Icon.svelte';
	import MathTex from '#lib/ui/Math.svelte';
	import PageFrame from '#lib/ui/PageFrame.svelte';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { pct } from '#lib/ui/format.ts';
	import { Dice, Download, Feynman, Newton, Pause, Play, Simplex } from '#lib/ui/icons.ts';

	const bench = getBench('match4');
	const RUN = 'newton';
	const SIZE = 9;
	const TAU = 2 * Math.PI;

	/** As in the other labs: a layer recorded in a browser, the ideal construction, or a live run. */
	type Source = 'recorded' | 'ideal' | 'live';
	let source = $state<Source>('recorded');

	// ── the table under inspection ───────────────────────────────────────────
	/** The deal that has a recorded model's answers. */
	const RECORDED_SEED = 1;
	let seed = $state(RECORDED_SEED);
	const layout = $derived(dealLayout(mulberry32(seed * 7919 + 11), SIZE));
	const members = $derived(zeroSumMembers(layout, 4));
	/** A card of the table to follow on the wheel, or null. */
	let focus = $state<number | null>(null);

	// ── what the layer learned: recorded in a browser, or live from this tab ──
	interface Recording {
		recordedAt: string;
		device: string;
		step: number;
		order: number;
		accuracy: number;
		/** Best resultant per class, and the channel that reaches it. */
		strength: number[];
		/** Null for a class no channel is closest to yet. */
		best: (Omit<ChannelFit, 'cls'> | null)[];
		/** Per class: every card's [angle, length] on its best channel, or null. */
		phases: ([number, number][] | null)[];
		layout: Card[];
		probs: number[];
		knockout: { full: number; without: number[] };
		/** [step, characters found, held-out accuracy] through training. */
		history: [number, number, number][];
	}
	let recording = $state.raw<Recording | null>(null);
	function loadRecording() {
		fetch(asset('recorded/newton.json'))
			.then((r) => (r.ok ? r.json() : null))
			.then(
				(j) => (recording = j?.strength ? j : null),
				() => {}
			);
	}
	$effect(loadRecording);

	const step = $derived.by(() => {
		void bench.version;
		return bench.history[RUN].step;
	});
	const liveAccuracy = $derived.by(() => {
		void bench.version;
		return bench.history[RUN].evalAccuracy.at(-1) ?? null;
	});
	const training = $derived(bench.status === 'training' || bench.status === 'pausing');

	let probe = $state.raw<NewtonProbe | null>(null);
	let knock = $state.raw<Knockout | null>(null);
	/** Re-probe every 50 steps, and knock arities out every 250 (six full evaluations). */
	const checkpoint = $derived(Math.floor(step / 50));
	const knockpoint = $derived(Math.floor(step / 250));
	function subscribeToNewtonProbe() {
		if (source !== 'live' || step === 0) return;
		void checkpoint;
		const l = layout;
		let cancelled = false;
		bench.newton(RUN, l).then(
			(r) => !cancelled && (probe = r),
			() => {}
		);
		return () => {
			cancelled = true;
		};
	}
	$effect(subscribeToNewtonProbe);
	function subscribeToKnockouts() {
		if (source !== 'live' || step === 0) return;
		void knockpoint;
		void training;
		let cancelled = false;
		bench.knockout(RUN).then(
			(r) => !cancelled && (knock = r),
			() => {}
		);
		return () => {
			cancelled = true;
		};
	}
	$effect(subscribeToKnockouts);

	const fits = $derived(probe ? fitChannels(probe) : []);
	/** Characters found and accuracy at every live probe, for the chart. */
	let liveHistory = $state.raw<[number, number, number][]>([]);
	function resetLiveHistory() {
		if (step === 0) liveHistory = [];
	}
	$effect(resetLiveHistory);
	const liveBest = $derived.by(() => {
		const best: (ChannelFit | null)[] = CLASSES.map(() => null);
		for (const f of fits) if (!best[f.cls] || f.R > best[f.cls]!.R) best[f.cls] = f;
		return best;
	});

	interface View {
		step: number;
		order: number;
		accuracy: number | null;
		strength: ArrayLike<number>;
		best: (Omit<ChannelFit, 'cls'> | null)[];
		phasesOf: (cls: number) => { angle: number; length: number }[] | null;
		probs: ArrayLike<number> | null;
		knockout: { full: number; without: number[] } | null;
		history: [number, number, number][];
	}
	const live = $derived(source === 'live' && step > 0);
	/** What is on screen: the recording falls back to the ideal layer until one exists. */
	const showing = $derived<Source>(source === 'recorded' && !recording ? 'ideal' : source);
	const majority = $derived(bench.majority);
	/** Theorem 5's layer: one channel per character and a read-out of the arity-4 count alone. */
	const ideal = $derived<View>({
		step: 0,
		order: 5,
		accuracy: 1,
		strength: CLASSES.map(() => 1),
		best: CLASSES.map((_, k) => ({ head: 0, channel: k, sign: 1, R: 1, offset: 0 })),
		phasesOf: (cls) =>
			DECK.map((x) => ({ angle: (TAU * charValue(CLASSES[cls], x)) / 3, length: 1 })),
		probs: members.map((m) => (m ? 1 : 0)),
		knockout: { full: 1, without: [1, 1, 1, majority, 1] },
		history: []
	});
	const view = $derived.by<View | null>(() => {
		if (showing === 'ideal') return ideal;
		if (live) {
			const p = probe;
			return {
				step,
				order: p?.order ?? 5,
				accuracy: liveAccuracy,
				strength: classStrength(fits),
				best: liveBest,
				phasesOf: (cls) => (p && liveBest[cls] ? cardPhases(p, liveBest[cls]!) : null),
				probs: p?.probs ?? null,
				knockout: knock,
				history: liveHistory
			};
		}
		const r = recording;
		if (showing !== 'recorded' || !r) return null;
		return {
			step: r.step,
			order: r.order,
			accuracy: r.accuracy,
			strength: r.strength,
			best: r.best,
			phasesOf: (cls) => r.phases[cls]?.map(([angle, length]) => ({ angle, length })) ?? null,
			probs: seed === RECORDED_SEED ? r.probs : null,
			knockout: r.knockout,
			history: r.history ?? []
		};
	});

	const found = $derived(view ? countFound(Float32Array.from(view.strength)) : 0);
	// a live probe adds a point once its characters are counted
	function recordLiveCheckpoint() {
		const p = probe;
		if (!p || !live) return;
		const n = countFound(classStrength(fits));
		const acc = bench.history[RUN].evalAccuracy.at(-1) ?? 0.5;
		const last = untrack(() => liveHistory.at(-1));
		if (!last || last[0] < p.step) liveHistory = [...untrack(() => liveHistory), [p.step, n, acc]];
	}
	$effect(recordLiveCheckpoint);

	// ── found and accuracy through training, on one axis ─────────────────────
	const CW = 420;
	const CH = 104;
	const PAD = { l: 22, r: 34, t: 6, b: 18 };
	const STEPS = 4000;
	const cx = (step: number) => PAD.l + (step / STEPS) * (CW - PAD.l - PAD.r);
	const cy = (found: number) =>
		CH - PAD.b - (Math.max(0, Math.min(40, found)) / 40) * (CH - PAD.t - PAD.b);
	/** Accuracy on the same axis: ½ + ½ · found/40, the paper's law, maps one onto the other. */
	const accAsFound = (acc: number) => (acc - 0.5) * 80;
	const line = (pts: [number, number][]) =>
		pts.map(([x, y], i) => `${i ? 'L' : 'M'}${cx(x).toFixed(1)} ${cy(y).toFixed(1)}`).join(' ');
	/** The class on the wheel: the one picked, or the strongest. */
	let picked = $state<number | null>(null);
	const strongest = $derived.by(() => {
		if (!view) return 0;
		let k = 0;
		for (let i = 1; i < CLASSES.length; i++) if (view.strength[i] > view.strength[k]) k = i;
		return k;
	});
	const cls = $derived(picked ?? strongest);
	const fit = $derived(view?.best[cls] ?? null);
	const phases = $derived(view && fit ? view.phasesOf(cls) : null);

	// ── the characters grid ─────────────────────────────────────────────────
	const COLS = 8;
	const CELL = 30;
	const GAP = 6;
	const gridW = COLS * (CELL + GAP) - GAP;
	const gridH = (CLASSES.length / COLS) * (CELL + GAP) - GAP;
	/** Resultant to grey: noise stays dark, a character is white. */
	const shade = (R: number) => {
		const v = Math.max(0, Math.min(1, (R - 0.35) / 0.6)) ** 1.6;
		const l = Math.round(24 + v * (238 - 24));
		return `rgb(${l} ${l} ${l})`;
	};
	const label = (c: Card) => c.join('');

	// ── the phase wheel ─────────────────────────────────────────────────────
	const W = 420;
	const C0 = W / 2;
	const RIM = 148;
	const DOT = 4.4;
	const BINS = 120;
	const VALUE_FILL = ['#f2f2f2', '#9b9b9b', '#5a5a5a'];
	const polar = (a: number, r: number) => ({ x: C0 + r * Math.cos(a), y: C0 - r * Math.sin(a) });
	/** Every card as a dot, stacked inward from the rim where phases coincide: a polar histogram. */
	const dots = $derived.by(() => {
		if (!phases) return [];
		const c = CLASSES[cls];
		const depth = new Array<number>(BINS).fill(0);
		return phases.map((p, x) => {
			const bin = Math.round((p.angle / TAU) * BINS) % BINS;
			const r = RIM - 7 - depth[bin]++ * (DOT * 1.15);
			return { id: x, ...polar((bin / BINS) * TAU, Math.max(r, 12)), value: charValue(c, DECK[x]) };
		});
	});
	/**
	 * The table's cards just outside the rim at their phase. Cards that share a phase fan out
	 * along the rim, centred on it, so a cluster stays a cluster and never leaves the wheel.
	 */
	const MARK_R = RIM + 24;
	const MARK_STEP = 25 / MARK_R;
	const tableMarks = $derived.by(() => {
		if (!phases) return [];
		const nb = BINS / 4;
		const bins = layout.map((card) => Math.round((phases[cardId(card)].angle / TAU) * nb) % nb);
		const seen = new Array<number>(nb).fill(0);
		return layout.map((card, i) => {
			const bin = bins[i];
			const size = bins.filter((b) => b === bin).length;
			const a = (bin / nb) * TAU + (seen[bin]++ - (size - 1) / 2) * MARK_STEP;
			return { i, card, a, ...polar(a, MARK_R) };
		});
	});

	// ── arity knockouts ─────────────────────────────────────────────────────
	const bar = (v: number) => Math.max(0, Math.min(1, (v - majority) / (1 - majority)));

	// ── controls ────────────────────────────────────────────────────────────
	async function train() {
		source = 'live';
		if (training) {
			await bench.pause();
			return;
		}
		await bench.start({ only: [RUN] });
	}
	function deal() {
		seed += 1;
		focus = null;
	}
	/** Save what the live layer learned, in the format of the recorded file. */
	function exportView() {
		if (!probe || !view || !live) return;
		const r = (v: number) => +v.toFixed(4);
		const data: Recording = {
			recordedAt: new Date().toISOString().slice(0, 10),
			device: bench.device ?? 'unknown',
			step: probe.step,
			order: probe.order,
			accuracy: r(liveAccuracy ?? 0),
			strength: Array.from(view.strength, r),
			// a class no channel is closest to yet has no channel to record
			best: liveBest.map((f) =>
				f
					? { head: f.head, channel: f.channel, sign: f.sign, R: r(f.R), offset: r(f.offset) }
					: null
			),
			phases: liveBest.map((f) =>
				f ? cardPhases(probe!, f).map((p) => [+p.angle.toFixed(3), +p.length.toFixed(3)]) : null
			),
			layout: layout.map((c) => [...c]),
			probs: Array.from(probe.probs, r),
			knockout: knock
				? { full: r(knock.full), without: knock.without.map(r) }
				: { full: 0, without: [] },
			history: liveHistory.map(([s, f, a]) => [s, f, r(a)])
		};
		const url = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: 'application/json' }));
		const a = document.createElement('a');
		a.href = url;
		a.download = 'newton.json';
		a.click();
		URL.revokeObjectURL(url);
	}
	const trainLabel = $derived(
		bench.status === 'booting'
			? 'Starting'
			: training
				? 'Pause'
				: step >= 4000
					? 'Finished'
					: step > 0
						? 'Resume'
						: 'Train'
	);
</script>

<svelte:head>
	<title>Explore Newton attention | Polyformer</title>
</svelte:head>

<PageFrame
	rail={[
		{ id: 'tensor', label: 'Cubic', icon: Simplex, href: resolve('/explore') },
		{ id: 'diagrams', label: 'Feynman', icon: Feynman, href: resolve('/explore/diagrams') },
		{ id: 'newton', label: 'Newton', icon: Newton, href: resolve('/explore/newton') },
		{ id: 'groups', label: 'Holonomy', icon: Simplex, href: resolve('/explore/groups') }
	]}
	active="newton"
>
	<div class="lab">
		<header class="head">
			<h1>Newton attention</h1>
			<p class="sub">
				Each card becomes a phase per channel, and pooled powers of the phases count relations of
				every size. One layer on four-card tables, opened up: which characters of the deck its
				channels carry, and which arity it relies on.
			</p>
		</header>

		<section class="stage" aria-label="What the layer learned">
			<div class="view chars">
				<div class="view-label">
					<span>Characters found</span>
					<small>One square per character, up to conjugation. White: some channel is it.</small>
				</div>
				<div class="tally">
					<span class="big num">{view ? found : '–'}</span>
					<span class="of">of 40</span>
				</div>
				<svg
					class="grid"
					viewBox="-4 -4 {gridW + 8} {gridH + 8}"
					role="group"
					aria-label="The 40 character classes"
				>
					{#each CLASSES as c, k (k)}
						{@const R = view ? view.strength[k] : 0}
						<rect
							role="button"
							tabindex="0"
							aria-label="Character {label(c)}, resultant {R.toFixed(2)}"
							aria-pressed={k === cls}
							class:on={!!view && k === cls}
							x={(k % COLS) * (CELL + GAP)}
							y={Math.floor(k / COLS) * (CELL + GAP)}
							width={CELL}
							height={CELL}
							rx="3"
							fill={shade(R)}
							onclick={() => (picked = k)}
							onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && (picked = k)}
						/>
					{/each}
				</svg>
				<svg
					class="history"
					viewBox="0 0 {CW} {CH}"
					aria-label="Characters found and held-out accuracy through training"
				>
					{#each [0, 20, 40] as v (v)}
						<line class="hgrid" x1={PAD.l} x2={CW - PAD.r} y1={cy(v)} y2={cy(v)} />
						<text class="hl" x={PAD.l - 6} y={cy(v)}>{v}</text>
						<text class="hr" x={CW - PAD.r + 6} y={cy(v)}>{50 + (v / 40) * 50}%</text>
					{/each}
					<text class="hx" x={PAD.l} y={CH - 2}>0</text>
					<text class="hx end" x={CW - PAD.r} y={CH - 2}>4,000 steps</text>
					{#if view && view.history.length > 1}
						<path
							class="acc"
							d={line(view.history.map(([s, , a]) => [s, accAsFound(a)] as [number, number]))}
						/>
						<path
							class="found"
							d={line(view.history.map(([s, f]) => [s, f] as [number, number]))}
						/>
					{/if}
				</svg>
				<div class="view-foot">
					{#if showing === 'ideal'}
						The ideal layer is built with every character, so nothing is learned over time. Train a
						layer live to watch the count rise.
					{:else}
						<span class="key-line solid"></span>characters found, left
						<span class="key-line dashed"></span>held-out accuracy, right{#if view?.accuracy != null},
							now
							{pct(view.accuracy, 1)}{/if}. In the paper's runs the two lines track each other.
					{/if}
				</div>
			</div>

			<div class="view wheel-view">
				<div class="view-label">
					<span>
						Phases on <MathTex tex={`\\chi = (${CLASSES[cls].join(',\\,')})`} />
					</span>
					<small>
						{#if fit && showing === 'ideal'}
							The ideal layer's channel for this character: three exact phases
						{:else if fit}
							Head {fit.head + 1}, channel {fit.channel + 1}, resultant {fit.R.toFixed(3)}
						{:else}
							Every card's learned phase on the channel closest to this character.
						{/if}
					</small>
				</div>
				<svg class="wheel" viewBox="0 0 {W} {W}" aria-label="Every card's phase on one channel">
					<circle class="rim" cx={C0} cy={C0} r={RIM} />
					{#each [0, 1, 2] as v (v)}
						{@const p = polar((v * TAU) / 3, RIM)}
						<line class="spoke" x1={C0} y1={C0} x2={p.x} y2={p.y} />
					{/each}
					{#each dots as d (d.id)}
						<circle
							class="dot"
							class:dim={focus !== null && cardId(layout[focus]) !== d.id}
							cx={d.x}
							cy={d.y}
							r={DOT / 2 + 0.4}
							fill={VALUE_FILL[d.value]}
						/>
					{/each}
					{#each tableMarks as m (m.i)}
						<g
							class="mark"
							class:dim={focus !== null && focus !== m.i}
							transform="translate({m.x - 11} {m.y - 11})"
						>
							<foreignObject width="22" height="22">
								<SetCard card={m.card} width={22} />
							</foreignObject>
						</g>
					{/each}
					{#if !view}
						<text class="empty" x={C0} y={C0}>Train to see the phases</text>
					{/if}
				</svg>
				<div class="view-foot">
					Dots: the 81 cards, shaded by the character's value, stacked where phases coincide. Cards:
					this table.
				</div>
			</div>
		</section>

		<aside class="inspector" aria-label="Arities and the table">
			<div class="block">
				<h2>Arities it uses</h2>
				<p class="note">
					Held-out accuracy with one arity's term switched off. A four-card relation needs arity 4.
				</p>
				{#if view?.knockout && view.knockout.without.length}
					{@const ko = view.knockout}
					<div class="bars">
						{#each ko.without as acc, k (k)}
							<span class="k"><MathTex tex={`k = ${k + 1}`} /></span>
							<svg class="track" viewBox="0 0 100 10" preserveAspectRatio="none" aria-hidden="true">
								<rect class="bg" x="0" y="3" width="100" height="4" />
								<rect class="fill" x="0" y="2" width={bar(acc) * 100} height="6" />
								<line class="full" x1={bar(ko.full) * 100} x2={bar(ko.full) * 100} y1="0" y2="10" />
							</svg>
							<span class="num v" class:drop={ko.full - acc > 0.05}>{pct(acc, 1)}</span>
						{/each}
					</div>
					<p class="note">
						Bars run from always answering the majority ({pct(majority, 0)}) to 100%; the tick is
						the full layer, {pct(ko.full, 1)}.
					</p>
				{:else}
					<p class="note empty-note">Train the layer to switch its arities off one at a time.</p>
				{/if}
			</div>

			<div class="block">
				<h2>This table</h2>
				<p class="note">
					A card is positive when it and three others sum to zero. Bars: the layer's probability; a
					dot marks the true answer. Pick a card to follow it on the wheel.
				</p>
				<div class="table">
					{#each layout as card, i (i)}
						<button
							class="cell"
							class:on={focus === i}
							aria-pressed={focus === i}
							aria-label="Card {i + 1}{members[i] ? ', positive' : ''}"
							onclick={() => (focus = focus === i ? null : i)}
						>
							<SetCard {card} width={32} />
							<span class="p">
								{#if view?.probs}
									<span class="pfill" style:width="{view.probs[i] * 100}%"></span>
								{/if}
							</span>
							<span class="truth" class:pos={members[i]}></span>
						</button>
					{/each}
				</div>
			</div>

			<div class="source block">
				<h2>
					{showing === 'ideal'
						? 'Ideal layer'
						: showing === 'recorded'
							? 'Recorded layer'
							: 'Live layer'}
				</h2>
				{#if showing === 'ideal'}
					<p class="note">
						Built by hand, not learned: one channel per character of the deck, and a read-out of the
						arity-4 count alone, as in Theorem 5 of the report. Recorded and Live show what gradient
						descent finds.
					</p>
				{:else if showing === 'recorded' && recording}
					<p class="note">
						Trained in a browser on {recording.device === 'webgpu' ? 'WebGPU' : recording.device},
						{recording.recordedAt}: one layer of width 128, four heads, arities 1 to {recording.order},
						{recording.step.toLocaleString('en-US')} steps on four-card tables. Train it live to watch
						the squares light up.
					</p>
				{:else}
					<p class="note num">
						{step === 0
							? 'Not trained yet.'
							: `Step ${step.toLocaleString('en-US')} of 4,000, in this tab on ${bench.device === 'webgpu' ? 'WebGPU' : bench.device}.`}
						The same run as Compare's four-card suite.
					</p>
				{/if}
				<div class="formula">
					<MathTex
						display
						tex={String.raw`R = \frac{\big|\sum g\, e^{\,i(\theta - 2\pi\langle c, x\rangle/3)}\big|}{\sum g}`}
					/>
				</div>
				<p class="note">
					How close a channel is to the character <MathTex tex="c" />, over every card at every
					position. A square counts as found above 0.9.
				</p>
			</div>
		</aside>

		<footer class="transport" aria-label="Lab controls">
			<div class="group">
				<span class="t-label">Model</span>
				<div class="seg" role="group" aria-label="Model">
					<button
						aria-pressed={showing === 'recorded'}
						disabled={!recording}
						title={recording ? 'A layer trained earlier in a browser' : 'No recording yet'}
						onclick={() => (source = 'recorded')}>Recorded</button
					>
					<button aria-pressed={showing === 'ideal'} onclick={() => (source = 'ideal')}
						>Ideal</button
					>
					<button aria-pressed={showing === 'live'} onclick={() => (source = 'live')}>Live</button>
				</div>
			</div>
			<div class="group keys">
				<button
					class="key play"
					onclick={train}
					disabled={bench.status === 'booting' || (!training && step >= 4000)}
				>
					<Icon icon={training ? Pause : Play} size={17} /><span>{trainLabel}</span>
				</button>
				<button class="key" onclick={deal}><Icon icon={Dice} size={17} /><span>Deal</span></button>
				<button class="key" onclick={exportView} disabled={!live || !probe}
					><Icon icon={Download} size={17} /><span>Export</span></button
				>
			</div>
			<div class="group right">
				<span class="t-label num"
					>{members.filter(Boolean).length} of {SIZE} cards positive on this table</span
				>
			</div>
		</footer>
	</div>
</PageFrame>

<style>
	.lab {
		--transport-h: 60px;
		display: grid;
		grid-template-columns: minmax(0, 1fr) 312px;
		grid-template-rows: auto minmax(360px, 1fr);
		grid-template-areas:
			'head insp'
			'stage insp';
		gap: 0 20px;
		height: calc(100dvh - var(--bar-h) - var(--transport-h));
		padding: 18px 0 0 28px;
	}
	.head {
		grid-area: head;
	}
	h1 {
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.025em;
		line-height: 1.1;
	}
	.sub {
		margin-top: 6px;
		max-width: 76ch;
		color: var(--color-ink-3);
		font-size: var(--text-sm);
	}

	.stage {
		grid-area: stage;
		display: grid;
		grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
		gap: 28px;
		min-height: 0;
		margin-top: 8px;
		padding-bottom: 12px;
	}
	.view {
		position: relative;
		display: flex;
		flex-direction: column;
		min-height: 0;
		min-width: 0;
		padding: 8px 0 30px;
	}
	/* labels flow with the content, so a wrapped line never runs into what follows */
	.view-label {
		margin-bottom: 8px;
		display: flex;
		flex-direction: column;
		gap: 2px;
		font-size: 15px;
		font-weight: 500;
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
	.view-foot {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 4px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}

	.tally {
		display: flex;
		align-items: baseline;
		gap: 8px;
		margin: 6px 0 14px;
	}
	.big {
		font-size: 40px;
		font-weight: 500;
		letter-spacing: -0.03em;
		line-height: 1;
		color: var(--color-ink);
	}
	.of {
		font-size: var(--text-sm);
		color: var(--color-ink-3);
	}
	.grid {
		width: 100%;
		max-width: 380px;
		min-height: 0;
	}
	.grid rect {
		cursor: pointer;
		transition: fill 600ms ease;
	}
	.grid rect:focus-visible {
		outline: none;
		stroke: var(--color-ink-2);
		stroke-width: 1.5;
	}
	.history {
		width: 100%;
		max-width: 380px;
		margin-top: 18px;
		overflow: visible;
	}
	.hgrid {
		stroke: #1c1c1c;
	}
	.history text {
		font-size: 10px;
		fill: var(--color-ink-3);
		dominant-baseline: middle;
	}
	.hl {
		text-anchor: end;
	}
	.hx {
		dominant-baseline: auto;
	}
	.hx.end {
		text-anchor: end;
	}
	.history path {
		fill: none;
		stroke-linejoin: round;
	}
	.found {
		stroke: var(--color-ink);
		stroke-width: 1.6;
	}
	.acc {
		stroke: #8c8c8c;
		stroke-width: 1.2;
		stroke-dasharray: 4 3;
	}
	.chars .view-foot {
		position: static;
		margin-top: 6px;
	}
	.key-line {
		display: inline-block;
		width: 16px;
		margin: 0 5px 3px 0;
		vertical-align: middle;
		border-top: 1.6px solid var(--color-ink);
	}
	.key-line.dashed {
		margin-left: 10px;
		border-top: 1.2px dashed #8c8c8c;
	}
	.grid rect.on {
		stroke: var(--color-ink);
		stroke-width: 2;
		paint-order: stroke;
	}

	.wheel {
		flex: 1;
		width: 100%;
		max-height: 440px;
		min-height: 0;
		overflow: visible;
	}
	.rim {
		fill: none;
		stroke: #262626;
	}
	.spoke {
		stroke: #1d1d1d;
		stroke-dasharray: 2 4;
	}
	.dot {
		transition:
			cx 600ms ease,
			cy 600ms ease,
			opacity 300ms ease;
	}
	.dot.dim {
		opacity: 0.18;
	}
	.mark {
		transition: opacity 300ms ease;
	}
	.mark.dim {
		opacity: 0.25;
	}
	.empty {
		fill: var(--color-ink-3);
		font-size: 13px;
		text-anchor: middle;
		dominant-baseline: middle;
	}

	.inspector {
		grid-area: insp;
		align-self: stretch;
		overflow-y: auto;
		margin-top: -18px;
		padding: 18px 22px 24px;
		background: #0c0c0c;
		border-left: 1px solid #1a1a1a;
	}
	h2 {
		font-size: 15px;
		font-weight: 500;
		color: var(--color-ink);
		margin-bottom: 4px;
	}
	.block {
		padding: 4px 0 18px;
	}
	.note {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		line-height: 1.5;
	}
	.empty-note {
		margin-top: 8px;
	}
	.bars {
		display: grid;
		grid-template-columns: 44px 1fr 48px;
		gap: 7px 8px;
		align-items: center;
		margin: 12px 0 10px;
		font-size: 13px;
	}
	.track {
		width: 100%;
		height: 10px;
	}
	.track .bg {
		fill: #1c1c1c;
	}
	.track .fill {
		fill: var(--color-ink-2);
	}
	.track .full {
		stroke: var(--color-ink);
		stroke-width: 1.5;
		vector-effect: non-scaling-stroke;
	}
	.v {
		text-align: right;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.v.drop {
		color: var(--color-ink);
	}

	.table {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 10px 8px;
		margin-top: 12px;
	}
	.cell {
		display: grid;
		justify-items: center;
		gap: 5px;
		padding: 6px 4px;
		border: 0;
		border-radius: 6px;
		background: transparent;
		cursor: pointer;
	}
	.cell:hover {
		background: #121212;
	}
	.cell.on {
		background: #171717;
	}
	.p {
		position: relative;
		width: 32px;
		height: 3px;
		background: #1f1f1f;
	}
	.pfill {
		position: absolute;
		inset: 0 auto 0 0;
		background: var(--color-ink);
		transition: width 400ms ease;
	}
	.truth {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		border: 1px solid #3a3a3a;
	}
	.truth.pos {
		border-color: var(--color-ink);
		background: var(--color-ink);
	}
	.formula {
		font-size: 15px;
		margin: 10px 0 2px;
	}
	.formula :global(.katex-display) {
		margin: 0.2em 0;
		text-align: left;
	}

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

	@media (max-width: 1100px) {
		.lab {
			height: auto;
			grid-template-columns: minmax(0, 1fr);
			grid-template-areas: 'head' 'stage' 'insp';
			padding: 16px 16px var(--transport-h);
		}
		.stage {
			grid-template-columns: minmax(0, 1fr);
			grid-auto-rows: auto;
		}
		.wheel {
			flex: none;
			height: min(86vw, 400px);
		}
		.view {
			padding: 0 0 12px;
		}
		.view-foot {
			position: static;
		}
		.view-foot {
			margin-top: 6px;
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
	}
</style>
