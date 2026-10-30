<script lang="ts">
	import { onMount } from 'svelte';
	import { asset } from '$app/paths';
	import { AddSheet } from '#lib/sketchpad/adder.ts';
	import Certificate from '#lib/sketchpad/Certificate.svelte';
	import Chat from '#lib/sketchpad/Chat.svelte';
	import Inset from '#lib/sketchpad/Inset.svelte';
	import Lens from '#lib/sketchpad/Lens.svelte';
	import Machine from '#lib/sketchpad/Machine.svelte';
	import StateSpace from '#lib/sketchpad/StateSpace.svelte';
	import '#lib/sketchpad/panel.css';
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

	/** what loading this operation's program costs now: one graph once the shared base is cached */
	const cost = $derived(pad.costs[pad.op]);
	const missing = $derived(pad.available[pad.op] === false);
	const certBusy = $derived(cert.status === 'running');
	/** the shipped table's weakest rows are being checked on this device (runs may start meanwhile) */
	const spotBusy = $derived(!!cert.spot?.running);
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
	<!-- the stage: everything a run does, on one screen -->
	<section class="stage">
		<header class="bar">
			<h1>Sketchpad</h1>
			<p class="lede">
				Qwen3.5-0.8B does exact arithmetic on a sheet it reads with its own eyes, three cells at a
				time. <em>Grown, not built.</em>
			</p>
		</header>

		<div class="controls">
			<div class="ops" role="group" aria-label="Operation">
				<button aria-pressed={pad.op === 'add'} onclick={() => setOp('add')}>Add</button>
				<button aria-pressed={pad.op === 'mul'} onclick={() => setOp('mul')}>Multiply</button>
			</div>
			<div class="nums">
				<input
					value={a}
					oninput={(e) => type('a', e.currentTarget)}
					inputmode="numeric"
					autocomplete="off"
					spellcheck="false"
					disabled={pad.running}
					aria-label="First number"
				/>
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
			</div>
			<div class="actions">
				{#if pad.gpuOk === false}
					<p class="note">{pad.gpuReason}</p>
				{:else if missing}
					<p class="note">The model files are not on this server (static/sketchpad/models/).</p>
				{:else if pad.loading}
					{@const kind = pad.progressKind ?? pad.loading}
					{@const total = pad.expect}
					<div class="loading">
						<span class="num">
							{#if pad.loadStage === 'compile'}
								Preparing the GPU
							{:else if total === 0}
								Reading {MODELS[kind].name} from this browser’s cache
							{:else}
								Downloading: {mb(pad.received)} of {total ? mb(total) : '…'} MB
							{/if}
						</span>
						<span class="bar-track"
							><i
								style:width="{pad.loadStage === 'compile' || total === 0
									? 100
									: total
										? Math.min(100, (pad.received / total) * 100)
										: 0}%"
							></i></span
						>
					</div>
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
					<button class="primary" disabled={!pad.canRun} onclick={() => pad.run(a, b)}>Run</button>
					{#if certBusy}<span class="hint">after the certificate</span>
					{:else if certFailed}<span class="hint"
							>off: {fmt(cert.rows - cert.pass)} views fail on this device</span
						>{/if}
				{/if}
			</div>
			<div class="presets">
				{#each presets as p (p.label)}
					<button disabled={pad.running} onclick={() => preset(p)}>{p.label}</button>
				{/each}
			</div>
			<button
				class="pace"
				aria-pressed={pad.pace > 0}
				onclick={() => (pad.pace = pad.pace > 0 ? 0 : 900)}
				title="Pause between ticks so the inside of the model can be followed"
				>{pad.pace > 0 ? 'Slow' : 'Fast'}</button
			>
		</div>
		{#if pad.loadError}<p class="note err">{pad.loadError}</p>{/if}

		<!-- the sheet (the model's only memory), what the model reads and writes, and the machine it runs -->
		<div class="band">
			<div class="sheet-col">
				<Sheet {source} version={pad.version} {tickMs} sprites={SPRITES} onedit={edit} compact />
				<!-- two fixed lines: what happened, then the facts behind it -->
				<div class="status num" aria-live="polite">
					{#if pad.running}
						<p>
							<span>tick {fmt(pad.ticks)}</span><span
								>{(pad.computeMs / Math.max(1, pad.ticks)).toFixed(0)} ms per tick</span
							><span>{progress}</span>
						</p>
						<p>
							{#if pad.sheet && pad.sheet.edits}<span
									>{pad.sheet.edits} {pad.sheet.edits === 1 ? 'digit' : 'digits'} changed</span
								>{/if}{#if pad.pushes}<span
									>{pad.pushes} {pad.pushes === 1 ? 'tick' : 'ticks'} pushed</span
								>{/if}
						</p>
					{:else if pad.result}
						{@const r = pad.result}
						<p class="verdict">
							<strong>{r.ok ? 'Exact.' : 'Wrong.'}</strong>
							{#if r.ok}
								{#if r.operands[0].length + r.operands[1].length + r.got.length <= 48}
									{r.operands[0]} {pad.op === 'add' ? '+' : '×'} {r.operands[1]} = {r.got}
								{:else}
									All {fmt(r.got.length)} digits of the {pad.op === 'add' ? 'sum' : 'product'} match.
								{/if}
							{:else}
								The sheet says {r.got.length > 30 ? `${r.got.slice(0, 30)}…` : r.got}.
							{/if}
						</p>
						<p>
							<span>{fmt(r.ticks)} ticks, {r.msPerTick.toFixed(0)} ms each</span><span
								>{#if r.certified && r.certSource === 'shipped'}certified (shipped, rechecked here){:else if r.certified}certified
									on this device{:else if r.unchecked === 0}every view it read passed{:else}{r.unchecked}
									unchecked {r.unchecked === 1 ? 'view' : 'views'}{/if}</span
							>{#if r.pushes}<span>{r.pushes} pushed</span>{/if}{#if r.edits}<span
									>{r.edits} changed</span
								>{/if}
						</p>
					{:else if pad.runError}
						<p>{pad.runError === 'stopped' ? 'Stopped.' : pad.runError}</p>
					{:else if pad.ready && !certBusy}
						<p title={loadNote}>
							{pad.op === 'add'
								? 'Run, then click an unread digit to change it,'
								: 'Run, then click a later digit of b to change it.'}
						</p>
						{#if pad.op === 'add'}<p>or a number in the state space to push a tick.</p>{/if}
					{/if}
				</div>
			</div>
			<div class="eye">
				<Inset last={pad.last} {next} sprites={SPRITES} />
			</div>
			<Machine last={pad.last} kind={pad.op} />
		</div>

		<!-- the inside of the model -->
		<div class="instruments">
			<Lens
				seen={pad.last?.inside ?? null}
				kind={pad.op}
				ready={!!pad.insideMeta}
				slow={pad.pace > 0}
			/>
			<StateSpace
				seen={pad.last?.inside ?? null}
				wrote={pad.last ? pad.last.out[0] : null}
				meta={pad.insideMeta}
				kind={pad.op}
				runKey={pad.sheet}
				slow={pad.pace > 0}
				push={pad.push}
				canPush={pad.ready && pad.op === 'add' && !!pad.insideMeta}
				onpush={(c) => (pad.push = c)}
			/>
			<Certificate
				{cert}
				device={pad.ready ? (pad.lastLoad?.gpu ?? null) : null}
				canCheck={pad.ready && !pad.running && !certBusy && !spotBusy}
				oncheck={() => pad.certify()}
				walk={pad.walk}
			/>
		</div>
	</section>

	<!-- below the stage -->
	<div class="more">
		<div class="block">
			<p class="label">Ask it</p>
			<div>
				<Chat
					turns={pad.chat}
					ready={pad.chatReady}
					busy={pad.chatBusy}
					onask={(q) => pad.ask(q)}
				/>
				<p class="small">The same weights still chat (thinking off, up to 120 new tokens).</p>
			</div>
		</div>
		<div class="block">
			<p class="label">How it works</p>
			<div class="prose">
				<p>
					Each tick the runtime crops three cells of the sheet, a 32 × 96 pixel image, and the model
					answers in tokens: for addition the column's sum code, for multiplication two glyphs and
					the name of its next step. The runtime stamps the glyphs and moves the window; nothing
					else carries over between ticks.
				</p>
				<p>
					The model can only ever see 242 strips in addition and 1,553 in multiplication. The page
					checks every one on your device before a run, so a run of any length is a chain of checked
					steps.
				</p>
				<p>
					Inside, the program's graph also returns the state at every layer. The lens reads each
					layer through the model's own output head; the state space is a 3D slice of the
					1,024-dimensional state chosen to separate the answers. Pushing adds the difference of two
					answers' mean states to the stream entering layer 20, right after the full-attention layer
					that writes the decision.
				</p>
			</div>
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

	/*
	 * One screen: the problem, the sheet, and the inside of the model side by side, so a run can be watched (and
	 * filmed) without scrolling. Explanations sit below the stage.
	 */
	.page {
		/* the sheet's row labels and its gap (Sheet.svelte reads these) */
		--margin-w: 44px;
		--gutter: 14px;
		/* tones for fields, tracks and the primary button, so both themes share the rules below */
		--field: #111111;
		--field-hover: #171717;
		--track: #1c1c1c;
		--track-on: #5a5a5a;
		--primary-hover: #ffffff;
		max-width: 1440px;
		margin: 0 auto;
		padding: 18px 32px 96px;
	}
	.stage {
		display: grid;
		gap: 12px;
	}

	.bar {
		display: flex;
		align-items: baseline;
		gap: 18px;
		flex-wrap: wrap;
	}
	h1 {
		font-size: 20px;
		font-weight: 500;
		letter-spacing: -0.01em;
	}
	.lede {
		max-width: none;
		font-size: var(--text-sm);
		color: var(--color-ink-3);
	}
	.lede em {
		font-style: normal;
		color: var(--color-ink-2);
	}

	/* controls: one line, tone and spacing, no outlines */
	.controls {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px 22px;
	}
	.ops {
		display: flex;
		gap: 14px;
	}
	.ops button,
	.presets button,
	.pace {
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
	.nums {
		display: flex;
		align-items: center;
		gap: 8px;
		flex: 1 1 340px;
		min-width: 0;
		max-width: 520px;
	}
	.sign {
		font-family: var(--font-mono);
		color: var(--color-ink-3);
	}
	.nums input {
		flex: 1 1 0;
		height: 30px;
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
	.actions {
		display: flex;
		align-items: center;
		gap: 12px;
		min-height: 30px;
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
		white-space: nowrap;
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
	.hint,
	.note {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.loading {
		display: grid;
		gap: 6px;
		width: 260px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.bar-track {
		position: relative;
		height: 2px;
		background: var(--track);
	}
	.bar-track i {
		position: absolute;
		inset: 0 auto 0 0;
		background: var(--color-ink-2);
		transition: width 250ms ease;
	}
	.presets {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
	}
	.presets button {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.presets button:hover:not(:disabled),
	.pace:hover {
		color: var(--color-ink);
	}
	.presets button:disabled {
		cursor: default;
	}
	.pace {
		margin-left: auto;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.pace[aria-pressed='true'] {
		color: var(--color-ink);
	}

	/*
	 * The band: sheet, eye and machine in fixed columns and a fixed height, so nothing a tick writes (a longer answer,
	 * a status line, a wider sheet) moves its neighbours.
	 */
	.band {
		display: grid;
		grid-template-columns: minmax(0, 1fr) 250px 290px;
		grid-template-rows: 236px;
		column-gap: 40px;
		margin-top: 4px;
	}
	.sheet-col {
		min-width: 0;
		min-height: 0;
		display: grid;
		grid-template-rows: auto auto;
		align-content: start;
		gap: 8px;
		overflow: hidden;
	}
	.eye {
		min-width: 0;
		min-height: 0;
		overflow: hidden;
		padding-top: 4px;
	}
	.band :global(.sp-panel) {
		grid-row: auto;
		grid-template-rows: auto minmax(0, 1fr) auto;
		height: 236px;
	}
	/* two fixed lines under the sheet; a line that is too long ends in an ellipsis instead of pushing anything */
	.status {
		display: grid;
		grid-template-rows: 18px 18px;
		height: 36px;
		padding-left: 12px;
	}
	.status p {
		min-width: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.status span + span::before {
		content: ' · ';
	}

	/* the inside of the model: three panels on one grid (panel.css: captions, figures and notes share rows) */
	.instruments {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.6fr) minmax(0, 0.9fr);
		/* the figures take what the window leaves, so the whole stage fits from 800 px tall screens up */
		grid-template-rows: auto clamp(220px, calc(100dvh - 595px), 360px) 4.4em;
		column-gap: 40px;
		margin-top: 6px;
		padding-top: 16px;
		border-top: 1px solid var(--color-edge);
	}

	/* below the stage */
	.more {
		margin-top: 64px;
		display: grid;
		gap: 28px;
		max-width: 900px;
	}
	.block {
		display: grid;
		grid-template-columns: 96px minmax(0, 1fr);
		gap: 24px;
	}
	.label {
		padding-top: 6px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
		text-align: right;
	}
	.small {
		margin-top: 10px;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	.prose {
		display: grid;
		gap: 12px;
		max-width: 68ch;
		color: var(--color-ink-2);
	}

	@media (max-width: 1279px) {
		.band {
			grid-template-columns: minmax(0, 1fr) 250px;
			grid-template-rows: 236px 236px;
			row-gap: 16px;
		}
		.band :global(.machine) {
			grid-column: 1 / -1;
		}
		.instruments {
			grid-template-columns: repeat(2, minmax(0, 1fr));
			grid-template-rows: auto 320px 4.4em auto 320px 4.4em;
			row-gap: 10px;
		}
	}
	@media (max-width: 719px) {
		.page {
			padding: 16px 16px 72px;
			--margin-w: 52px;
			--gutter: 6px;
		}
		/* a phone has the height to spare: the status may wrap */
		.status {
			height: auto;
			grid-template-rows: auto;
		}
		.status p {
			white-space: normal;
		}
		.band {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: auto 236px 236px;
		}
		.instruments {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: repeat(3, auto 300px auto);
		}
		.pace {
			margin-left: 0;
		}
		.block {
			grid-template-columns: minmax(0, 1fr);
			gap: 8px;
		}
		.label {
			text-align: left;
			padding-top: 0;
		}
	}
</style>
