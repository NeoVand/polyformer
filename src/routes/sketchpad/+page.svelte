<script lang="ts">
	import { onMount } from 'svelte';
	import { asset } from '$app/paths';
	import { AddSheet } from '#lib/sketchpad/adder.ts';
	import Certificate from '#lib/sketchpad/Certificate.svelte';
	import Chat from '#lib/sketchpad/Chat.svelte';
	import Inset from '#lib/sketchpad/Inset.svelte';
	import { MODELS, type Kind } from '#lib/sketchpad/models.ts';
	import { pad } from '#lib/sketchpad/pad.svelte.ts';
	import type { TickOp } from '#lib/sketchpad/protocol.ts';
	import Sheet from '#lib/sketchpad/Sheet.svelte';
	import { sourceOf } from '#lib/sketchpad/sources.ts';
	import { theme } from '#lib/sketchpad/theme.svelte.ts';

	const SPRITES = asset('sketchpad/sprites.png');
	let modelsBase = '';
	let spritesUrl = '';

	const rnd = (n: number) =>
		Array.from({ length: n }, (_, i) =>
			i === 0 ? 1 + Math.floor(Math.random() * 9) : Math.floor(Math.random() * 10)
		).join('');

	let a = $state('482917305561');
	let b = $state('739104826637');
	const LIMIT: Record<Kind, number> = { add: 2000, mul: 20 };

	const presets: { label: string; op: Kind; n: number; m: number }[] = [
		{ label: '40-digit sum', op: 'add', n: 40, m: 40 },
		{ label: '1,000-digit sum', op: 'add', n: 1000, m: 1000 },
		{ label: '4 × 4', op: 'mul', n: 4, m: 4 },
		{ label: '6 × 6', op: 'mul', n: 6, m: 6 },
		{ label: '10 × 10', op: 'mul', n: 10, m: 10 }
	];

	onMount(() => {
		spritesUrl = new URL(SPRITES, location.href).href;
		// the weights sit beside the sprites: static/sketchpad/models/<program or base>/
		modelsBase = new URL('models/', spritesUrl).href;
		void pad.probe(modelsBase);
		pad.stage(a, b);
		// local checks and the screenshot script drive the page through this handle
		if (import.meta.env.DEV) Object.assign(globalThis, { sketchpad: pad });
		return theme.watch();
	});

	const source = $derived(pad.sheet ? sourceOf(pad.sheet) : null);
	const cert = $derived(pad.cert);
	const tickMs = $derived(pad.last?.ms ?? 160);
	const next = $derived.by((): { op: TickOp; cells: string[] } | null => {
		void pad.version;
		const s = pad.sheet;
		if (!s || s.done) return null;
		return { op: s instanceof AddSheet ? 'ADD-FAST' : s.op, cells: s.view() };
	});
	const progress = $derived.by(() => {
		void pad.version;
		const s = pad.sheet;
		if (!s) return '';
		if (s instanceof AddSheet) return `${fmt(s.columnsDone)} of ${fmt(s.n)} columns`;
		return `digit ${Math.min(s.j + 1, s.m)} of ${s.m} of b`;
	});

	const fmt = (n: number) => n.toLocaleString('en-US');
	/** a download size as a visitor reads it: KB below a megabyte, MB below a gigabyte, GB above */
	const bytes = (n: number) =>
		n >= 1e9
			? `${(n / 1e9).toFixed(2)} GB`
			: n >= 1e6
				? `${fmt(Math.round(n / 1e6))} MB`
				: `${fmt(Math.max(1, Math.round(n / 1e3)))} KB`;
	const mb = (n: number) => fmt(Math.round(n / 1e6));
	const duration = (s: number) =>
		s < 90 ? `${s.toFixed(s < 10 ? 1 : 0)} s` : `${Math.floor(s / 60)} min ${Math.round(s % 60)} s`;

	/** what loading this operation's program costs now: one graph once the shared base is cached */
	const cost = $derived(pad.costs[pad.op]);
	const missing = $derived(pad.available[pad.op] === false);
	const certBusy = $derived(cert.status === 'running');
	const certFailed = $derived(
		(cert.status === 'done' || cert.status === 'cached') && cert.pass < cert.rows
	);
	const loadNote = $derived.by(() => {
		const l = pad.lastLoad;
		if (!l || !pad.ready || l.id !== MODELS[pad.op].id) return '';
		if (!l.network)
			return `Loaded in ${l.seconds.toFixed(1)} s, all ${bytes(l.cached)} from this browser’s cache.`;
		const parts = [`${bytes(l.network)} fetched`];
		if (l.cached) parts.push(`${bytes(l.cached)} from this browser’s cache`);
		return `Loaded in ${l.seconds.toFixed(1)} s: ${parts.join(', ')}.`;
	});

	function digits(v: string) {
		return v.replace(/\D/g, '').slice(0, LIMIT[pad.op]);
	}

	/** what is typed is what the sheet shows, until a run takes it over */
	function type(which: 'a' | 'b', el: HTMLInputElement) {
		const v = digits(el.value);
		if (which === 'a') a = v;
		else b = v;
		// drop anything that is not a digit from the field itself too
		if (el.value !== v) el.value = v;
		pad.stage(a, b);
	}

	/** switch the operation (a run in progress stops first); returns whether this switch took effect */
	async function setOp(k: Kind) {
		await pad.setOp(k);
		if (pad.op !== k) return false;
		if (k === 'mul' && (a.length > LIMIT.mul || b.length > LIMIT.mul)) {
			a = rnd(6);
			b = rnd(6);
		}
		pad.stage(a, b);
		return true;
	}

	async function preset(p: (typeof presets)[number]) {
		if (!(await setOp(p.op))) return;
		if (pad.running) return;
		a = rnd(p.n);
		b = rnd(p.m);
		pad.stage(a, b);
		if (pad.canRun) void pad.run(a, b);
	}

	function edit(r: number, c: number, by: number) {
		if (!source) return false;
		const [row, x] = source.address(r, c);
		return pad.bump(row, x, by);
	}

	function load() {
		pad.load(modelsBase, spritesUrl);
	}
</script>

<svelte:head>
	<title>Sketchpad · polyformer</title>
	<meta
		name="description"
		content="Qwen3.5-0.8B does exact arithmetic on a sheet that is its only working memory, reading it through its own vision tower, in your browser."
	/>
</svelte:head>

<main class="page">
	<!-- the problem -->
	<div class="row top">
		<header class="c">
			<h1>Sketchpad</h1>
			<p class="lede">
				Qwen3.5-0.8B, a small vision-language model, does exact arithmetic on a sheet of paper that
				is its only working memory. It reads the sheet through its own vision tower, one strip of
				three cells at a time, and writes its answer back onto the page.
			</p>
			<p class="thesis">
				<em>Grown, not built.</em> A small adapter on the pretrained model learned the arithmetic. Nothing
				in it was compiled by hand.
			</p>

			<div class="controls">
				<div class="ops" role="group" aria-label="Operation">
					<button aria-pressed={pad.op === 'add'} onclick={() => setOp('add')}>Add</button>
					<button aria-pressed={pad.op === 'mul'} onclick={() => setOp('mul')}>Multiply</button>
				</div>

				<div class="nums">
					<label>
						<span class="sign" aria-hidden="true"></span>
						<input
							value={a}
							oninput={(e) => type('a', e.currentTarget)}
							inputmode="numeric"
							autocomplete="off"
							spellcheck="false"
							disabled={pad.running}
							aria-label="First number"
						/>
						<span class="count num">{a.length > 14 ? `${fmt(a.length)} digits` : ''}</span>
					</label>
					<label>
						<span class="sign" aria-hidden="true">{pad.op === 'add' ? '+' : '×'}</span>
						<input
							value={b}
							oninput={(e) => type('b', e.currentTarget)}
							inputmode="numeric"
							autocomplete="off"
							spellcheck="false"
							disabled={pad.running}
							aria-label="Second number"
						/>
						<span class="count num">{b.length > 14 ? `${fmt(b.length)} digits` : ''}</span>
					</label>
				</div>

				<div class="actions">
					{#if pad.gpuOk === false}
						<p class="note">{pad.gpuReason}</p>
					{:else if missing}
						<p class="note">
							The files for {MODELS[pad.op].name} are not on this server (static/sketchpad/models/).
						</p>
					{:else if pad.loading}
						{@const kind = pad.progressKind ?? pad.loading}
						{@const total = pad.expect}
						<div class="loading">
							<span class="num">
								{#if pad.loadStage === 'compile'}
									Preparing the GPU for {MODELS[kind].name}
								{:else if total === 0}
									Reading {MODELS[kind].name} from this browser’s cache
								{:else}
									Downloading {MODELS[kind].name}: {mb(pad.received)} of {total ? mb(total) : '…'} MB
								{/if}
								{#if kind !== pad.loading}<span class="dim">, then {MODELS[pad.loading].name}</span
									>{/if}
							</span>
							<span class="bar"
								><i
									style:width="{pad.loadStage === 'compile' || total === 0
										? 100
										: total
											? Math.min(100, (pad.received / total) * 100)
											: 0}%"
								></i></span
							>
						</div>
						{#if MODELS[pad.loading].id !== MODELS[pad.op].id}
							<button class="next" onclick={load}>Load {MODELS[pad.op].name} next</button>
						{/if}
					{:else if !pad.ready}
						<button class="primary" onclick={load} disabled={pad.gpuOk === null}>
							Load {MODELS[pad.op].name}{cost === null
								? ''
								: cost === 0
									? ' · cached'
									: ` · ${bytes(cost)}`}
						</button>
					{:else if pad.running}
						<button class="primary" onclick={() => pad.stop()}>Stop</button>
					{:else}
						<button class="primary" disabled={!pad.canRun} onclick={() => pad.run(a, b)}>Run</button
						>
						{#if certBusy}<span class="hint">after the certificate</span>
						{:else if certFailed}<span class="hint"
								>off: {fmt(cert.rows - cert.pass)} table rows fail on this device</span
							>{/if}
					{/if}
				</div>
				{#if loadNote && !pad.running}<p class="note load">{loadNote}</p>{/if}
				{#if pad.loadError}<p class="note err">{pad.loadError}</p>{/if}

				<div class="presets">
					{#each presets as p (p.label)}
						<button disabled={pad.running} onclick={() => preset(p)}>{p.label}</button>
					{/each}
				</div>
			</div>
		</header>

		<aside class="r">
			<Certificate
				{cert}
				device={pad.ready ? (pad.lastLoad?.gpu ?? null) : null}
				canCheck={pad.ready && !pad.running && !certBusy}
				oncheck={() => pad.certify()}
			/>
		</aside>
	</div>

	<!-- the sheet -->
	<div class="row work">
		<div class="wide">
			<Sheet {source} version={pad.version} {tickMs} sprites={SPRITES} onedit={edit} />
		</div>
		<aside class="r inset">
			<Inset last={pad.last} {next} sprites={SPRITES} />
		</aside>
	</div>

	<div class="row">
		<div class="c status num" aria-live="polite">
			{#if pad.running}
				<span>tick {fmt(pad.ticks)}</span>
				<span>{(pad.computeMs / Math.max(1, pad.ticks)).toFixed(0)} ms per tick</span>
				<span>{progress}</span>
				{#if pad.sheet && pad.sheet.edits}<span
						>{pad.sheet.edits} {pad.sheet.edits === 1 ? 'edit' : 'edits'}</span
					>{/if}
			{:else if pad.result}
				{@const r = pad.result}
				<p class="verdict">
					<strong>{r.ok ? 'Exact.' : 'Wrong.'}</strong>
					{#if r.ok}
						{#if r.got.length <= 40}
							{r.operands[0]} {pad.op === 'add' ? '+' : '×'} {r.operands[1]} = {r.got}.
						{:else}
							All {fmt(r.got.length)} digits of the {pad.op === 'add' ? 'sum' : 'product'} match.
						{/if}
					{:else}
						The sheet says {r.got.length > 60 ? `${r.got.slice(0, 60)}…` : r.got}, the answer is {r
							.want.length > 60
							? `${r.want.slice(0, 60)}…`
							: r.want}.
					{/if}
				</p>
				<p class="facts">
					{fmt(r.ticks)} ticks, {r.msPerTick.toFixed(0)} ms per tick, {duration(r.seconds)}.
					{#if r.edits}
						You changed {r.edits} unread {r.edits === 1 ? 'digit' : 'digits'} during the run; the answer
						is checked against the edited numbers.
					{/if}
					{#if r.certified}
						Certified: every view it can read passed on this device.
					{:else if r.unchecked === 0}
						Not certified as a whole ({fmt(cert.rows - cert.pass)} of {fmt(cert.rows)} table rows fail
						on this device), but every one of the {fmt(r.views)} views this run read passed.
					{:else}
						Not certified: this run read {r.unchecked}
						{r.unchecked === 1 ? 'view' : 'views'} that did not pass on this device (<span
							class="mono">{r.uncheckedLabels.slice(0, 3).join(', ')}</span
						>).
					{/if}
				</p>
			{:else if pad.runError}
				<p class="facts">{pad.runError === 'stopped' ? 'Stopped.' : pad.runError}</p>
			{:else if pad.ready && !certBusy}
				<p class="facts">
					Press Run, then click a digit the model has not reached yet to change it ({pad.op ===
					'add'
						? 'any digit of a or b left of the window'
						: 'a digit of b for a later pass'}).
				</p>
			{/if}
		</div>
	</div>

	<!-- chat -->
	<div class="row chat">
		<p class="m label">Ask it</p>
		<div class="c">
			<Chat turns={pad.chat} ready={pad.chatReady} busy={pad.chatBusy} onask={(q) => pad.ask(q)} />
			<p class="small">
				The same weights still chat: your question goes through the chat template with thinking off,
				up to 120 new tokens.
			</p>
		</div>
	</div>

	<!-- why -->
	<div class="row prose">
		<p class="m label">What you see</p>
		<div class="c">
			<p>
				Each tick, the window crops three cells from the sheet: a 32 × 96 pixel image, three vision
				tokens. The model answers in tokens. For addition it writes the sum digit and whether to
				carry; for multiplication, two glyphs and the name of its next step. The runtime stamps
				those glyphs on the sheet and moves the window. Nothing else carries over from one tick to
				the next.
			</p>
		</div>
	</div>
	<div class="row prose">
		<p class="m label">Why it is exact</p>
		<div class="c">
			<p>
				The model can only ever see so many strips: 242 for addition, 1,553 for multiplication.
				Before a run, this page checks every one of them on your device, and the right answer has to
				beat every other token by a positive margin. The sheet is the only state, so a run of any
				length is a chain of checked steps: a 1,000-digit sum is as exact as a three-digit one.
			</p>
		</div>
	</div>
	<div class="row prose">
		<p class="m label">The boundary</p>
		<div class="c">
			<p>
				You type the problem; reading a photographed page is future work. The runtime does no
				arithmetic: it stamps the glyphs the model writes and moves the window where the model says.
				In addition the window steps one column left each tick until the model writes halt; in
				multiplication the model names its next step, and the runtime clears the carry and product
				cells the model has just read.
			</p>
		</div>
	</div>
</main>

<style>
	/*
	 * Light theme: the site is dark-only today, so these tokens apply only when <html data-theme="light"> is set
	 * (theme.svelte.ts). The top bar and the body read the same tokens.
	 */
	:global(:root[data-theme='light']) {
		color-scheme: light;
		--color-void: #f3f3f3;
		--color-well: #ececec;
		--color-panel: #e6e6e6;
		--color-lift: #dedede;
		--color-control: #d6d6d6;
		--color-edge: #d0d0d0;
		--color-rule: #a3a3a3;
		--color-ink-3: #6b6b6b;
		--color-ink-2: #404040;
		--color-ink: #0d0d0d;
		--logo-ink: #1a1a1a;
	}
	:global(:root[data-theme='light'] ::selection) {
		background: #0d0d0d;
		color: #f3f3f3;
	}
	:global(:root[data-theme='light']) .page {
		--field: #e8e8e8;
		--field-hover: #e1e1e1;
		--track: #dcdcdc;
		--track-on: #8a8a8a;
		--primary-hover: #000000;
	}

	.page {
		--margin-w: 112px;
		--gutter: 40px;
		--right-w: 248px;
		/* tones for fields, tracks and the primary button, so both themes share the rules below */
		--field: #111111;
		--field-hover: #171717;
		--track: #1c1c1c;
		--track-on: #5a5a5a;
		--primary-hover: #ffffff;
		display: grid;
		grid-template-columns: var(--margin-w) minmax(0, 1fr) var(--right-w);
		column-gap: var(--gutter);
		max-width: 1240px;
		margin: 0 auto;
		padding: 44px 40px 120px;
	}
	.row {
		grid-column: 1 / -1;
		display: grid;
		grid-template-columns: subgrid;
		align-items: start;
	}
	.m {
		grid-column: 1;
	}
	.c {
		grid-column: 2;
		min-width: 0;
	}
	.r {
		grid-column: 3;
		min-width: 0;
	}
	.wide {
		grid-column: 1 / 3;
		min-width: 0;
	}

	h1 {
		font-size: 28px;
		font-weight: 500;
		letter-spacing: -0.02em;
		line-height: 1.15;
	}
	.lede {
		margin-top: 12px;
		max-width: 64ch;
		color: var(--color-ink-2);
	}
	.thesis {
		margin-top: 10px;
		max-width: 64ch;
		color: var(--color-ink-3);
	}
	.thesis em {
		font-style: normal;
		color: var(--color-ink);
	}

	/* controls: tone and spacing, no outlines */
	.controls {
		margin-top: 28px;
	}
	.ops {
		display: flex;
		gap: 18px;
	}
	.ops button,
	.presets button {
		border: 0;
		padding: 0;
		background: none;
		font: inherit;
		cursor: pointer;
		transition: color 250ms ease;
	}
	.ops button {
		font-size: var(--text-ui);
		color: var(--color-ink-3);
	}
	.ops button:hover:not(:disabled) {
		color: var(--color-ink-2);
	}
	.ops button[aria-pressed='true'] {
		color: var(--color-ink);
	}
	.ops button:disabled {
		cursor: default;
	}
	.nums {
		display: grid;
		gap: 6px;
		margin-top: 14px;
	}
	.nums label {
		display: grid;
		grid-template-columns: 14px minmax(0, 1fr) 92px;
		align-items: center;
		gap: 10px;
	}
	.sign {
		font-family: var(--font-mono);
		color: var(--color-ink-3);
		text-align: center;
	}
	.nums input {
		height: 32px;
		min-width: 0;
		padding: 0 10px;
		border: 0;
		border-radius: 4px;
		background: var(--field);
		color: var(--color-ink);
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		letter-spacing: 0.04em;
		transition: background 250ms ease;
	}
	.nums input:hover:not(:disabled),
	.nums input:focus {
		background: var(--field-hover);
		outline: none;
	}
	.nums input:disabled {
		color: var(--color-ink-2);
	}
	.count {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.actions {
		display: flex;
		align-items: center;
		gap: 14px;
		min-height: 32px;
		margin-top: 16px;
		padding-left: 24px;
	}
	.primary {
		height: 30px;
		padding: 0 16px;
		border: 0;
		border-radius: 4px;
		background: var(--color-ink);
		color: var(--color-void);
		font: inherit;
		font-size: var(--text-sm);
		font-weight: 500;
		cursor: pointer;
		transition:
			background 250ms ease,
			color 250ms ease;
	}
	.primary:hover:not(:disabled) {
		background: var(--primary-hover);
	}
	.primary:disabled {
		background: var(--color-lift);
		color: var(--color-ink-3);
		cursor: default;
	}
	.next {
		flex: none;
		border: 0;
		padding: 0;
		background: none;
		font: inherit;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		cursor: pointer;
		transition: color 250ms ease;
	}
	.next:hover {
		color: var(--color-ink);
	}
	.hint,
	.note {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.note.load {
		margin-top: 8px;
		padding-left: 24px;
	}
	.loading .dim {
		color: var(--color-ink-3);
	}
	.note.err {
		margin-top: 8px;
		padding-left: 24px;
	}
	.loading {
		display: grid;
		gap: 8px;
		width: min(100%, 360px);
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.bar {
		position: relative;
		height: 2px;
		background: var(--track);
	}
	.bar i {
		position: absolute;
		inset: 0 auto 0 0;
		background: var(--color-ink-2);
		transition: width 250ms ease;
	}
	.presets {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 16px;
		margin-top: 14px;
		padding-left: 24px;
	}
	.presets button {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.presets button:hover:not(:disabled) {
		color: var(--color-ink);
	}
	.presets button:disabled {
		cursor: default;
	}

	.work {
		margin-top: 36px;
	}
	.inset {
		padding-top: 4px;
	}
	.status {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 18px;
		min-height: 48px;
		margin-top: 14px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.verdict {
		width: 100%;
		color: var(--color-ink-2);
		font-size: var(--text-sm);
		overflow-wrap: anywhere;
	}
	.verdict strong {
		font-weight: 500;
		color: var(--color-ink);
	}
	.facts {
		width: 100%;
		max-width: 72ch;
	}
	.facts .mono {
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
	}

	.chat {
		margin-top: 28px;
	}
	.label {
		padding-top: 8px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		text-align: right;
	}
	.small {
		margin-top: 14px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		max-width: 64ch;
	}
	.prose {
		margin-top: 40px;
	}
	.prose + .prose {
		margin-top: 22px;
	}
	.prose .label {
		padding-top: 2px;
	}
	.prose p:not(.label) {
		max-width: 64ch;
		color: var(--color-ink-2);
	}

	@media (max-width: 1099px) {
		.page {
			grid-template-columns: var(--margin-w) minmax(0, 1fr);
			--margin-w: 92px;
			--gutter: 28px;
			padding: 36px 28px 96px;
		}
		.r {
			grid-column: 2;
			margin-top: 28px;
		}
		.inset {
			padding-top: 0;
		}
	}

	@media (max-width: 719px) {
		.page {
			grid-template-columns: minmax(0, 1fr);
			--margin-w: 50px;
			--gutter: 10px;
			padding: 24px 16px 80px;
		}
		.m,
		.c,
		.r,
		.wide {
			grid-column: 1;
		}
		.label {
			padding-top: 0;
			margin-bottom: 8px;
			text-align: left;
		}
		.actions,
		.presets,
		.note.load {
			margin-top: 8px;
			padding-left: 24px;
		}
		.loading .dim {
			color: var(--color-ink-3);
		}
		.note.err {
			padding-left: 0;
		}
		.nums label {
			grid-template-columns: 12px minmax(0, 1fr) 0;
			gap: 8px;
		}
		.count {
			display: none;
		}
		.work {
			margin-top: 28px;
		}
		.prose {
			margin-top: 32px;
		}
		/* on a phone the sheet comes straight after the problem; the certificate follows the run */
		.top {
			display: contents;
		}
		.top > .r {
			order: 5;
			margin-top: 36px;
		}
		.chat {
			order: 6;
		}
		.prose {
			order: 7;
		}
		.inset {
			margin-top: 20px;
		}
	}
</style>
