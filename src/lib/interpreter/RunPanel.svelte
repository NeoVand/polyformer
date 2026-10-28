<script lang="ts">
	/**
	 * Panel 2: the run. The input tape at the playhead, the head's attention as arrows to the table rows it reads
	 * (the read row held at the centre), and the step the row encodes. REGS adds the machine's memory.
	 */
	import Pane from './Pane.svelte';
	import RegsMemory from './RegsMemory.svelte';
	import { int, type Trace, type TraceStep } from './trace.ts';

	let {
		trace,
		cur,
		stuck,
		onseek,
		pending = false
	}: {
		trace: Trace;
		cur: TraceStep;
		stuck: string | null;
		onseek: (i: number) => void;
		/** a run in this browser is still certifying: `cur` is the row being checked */
		pending?: boolean;
	} = $props();

	const isRegs = $derived(trace.kind === 'regs');
	const isLlm = $derived(trace.kind === 'llm');
	const att = $derived(trace.llm ? trace.llm.file.registers[trace.llm.register]?.attention : null);
	/** LLM runs made in this browser have no attention pass (the export does not return attention) */
	const noAttn = $derived(isLlm && !att);
	const tapeTotal = $derived(trace.llm?.file.input.events?.length ?? trace.steps.length);
	const count = $derived(trace.steps.length);
	/** Cells either side of the current event: fewer, wider cells when event names are long. */
	const half = $derived(Math.max(...trace.program.events.map((e) => e.length)) > 4 ? 5 : 6);
	/** the question's events: the run's own steps, or (while certifying) the tape the clock read */
	const events = $derived(trace.llm?.file.input.events ?? null);
	const tape = $derived.by(() => {
		const out: { i: number; ev: string }[] = [];
		const at = pending ? half : cur.i;
		for (let k = at - half; k <= at + half; k++)
			out.push({
				i: k,
				ev:
					k >= 0 && k < count
						? trace.steps[k].event
						: pending && events && k >= 0 && k < events.length
							? events[k]
							: ''
			});
		return out;
	});

	/** The rows around the read row; REGS reads whole program lines. */
	const ROWS = 7;
	const rowText = $derived.by(() => {
		if (isRegs) {
			const listing = trace.program.text.split('\n');
			return (k: number) => listing[k]?.replace(/^\s*\d+\s+/, '') ?? '';
		}
		return (k: number) => {
			const r = trace.program.rows[k];
			return r ? `${r.s}  ${r.b} → ${r.t}` : '';
		};
	});
	const rowCount = $derived(isRegs ? (trace.program.lines ?? 0) : trace.program.rows.length);
	const visible = $derived.by(() => {
		const w = new Map(cur.attn);
		const out: { k: number; w: number; text: string }[] = [];
		for (let d = -((ROWS - 1) / 2); d <= (ROWS - 1) / 2; d++) {
			const k = cur.row + d;
			out.push({ k, w: w.get(k) ?? 0, text: k >= 0 && k < rowCount ? rowText(k) : '' });
		}
		return out;
	});
	const off = $derived(stuck !== null);
	const RH = 21;
	const top = $derived(cur.attn[0]?.[1] ?? 0);
	const elsewhere = $derived(
		cur.attn.filter(([k]) => Math.abs(k - cur.row) > (ROWS - 1) / 2).reduce((a, [, w]) => a + w, 0)
	);
	const fmtW = (w: number) =>
		w >= 0.9995 ? w.toFixed(5) : w >= 0.001 ? w.toFixed(3) : w.toExponential(0);
	const short = $derived(
		isRegs
			? 'REGS on the frozen INTERP core'
			: isLlm
				? `${trace.llm?.file.where === 'browser' ? 'Savant-4B' : 'Qwen3-4B'}, one tick per event`
				: 'the frozen INTERP core'
	);
	const readsLabel = $derived(
		off
			? isLlm
				? 'adapter switched off'
				: 'head switched off'
			: pending
				? 'certifying row'
				: isLlm && att?.head
					? `head ${att.head} reads`
					: noAttn
						? 'the tick reads'
						: 'head reads'
	);
</script>

<Pane n={2} title="The run" source={trace.panels.run} {short}>
	<div class={['run', isRegs && 'regs']}>
		<div class="main">
			<div class="tape-wrap">
				<div class="label">{isRegs ? 'instructions' : 'input tape'}</div>
				<div
					class="tape"
					style:--cells={2 * half + 1}
					role="group"
					aria-label="Input tape around the current step"
				>
					{#each tape as c (c.i)}
						<button
							class={['cell', c.i === cur.i && !pending && 'now', c.i < cur.i && 'done']}
							disabled={!c.ev || pending}
							tabindex={c.i === cur.i ? 0 : -1}
							aria-label={c.ev ? `Step ${c.i + 1}: ${c.ev}` : undefined}
							onclick={() => onseek(c.i)}>{c.ev}</button
						>
					{/each}
				</div>
				<div class="mini" aria-hidden="true">
					<span
						class="fill"
						style:width="{pending ? 0 : ((cur.i + 1) / Math.max(count, tapeTotal)) * 100}%"
					></span>
				</div>
			</div>

			<div class="read">
				<div class="head">
					<span class="label">{readsLabel}</span>
					<span class="query">
						{#if isRegs}
							line {cur.s}
						{:else}
							({stuck ?? cur.s}, {cur.event})
						{/if}
					</span>
					<span class="meta num">
						{#if off}
							{isLlm ? 'base weights' : 'output zeroed'}
						{:else if pending}
							{int(cur.row + 1)} of {int(rowCount)}
						{:else if noAttn}
							{cur.row >= 0 ? `row ${int(cur.row)}` : 'no row: off the table'}
						{:else if isLlm && !cur.attn.length}
							no row read
						{:else}
							weight {fmtW(top)}
						{/if}
					</span>
				</div>
				<svg
					class="arrows"
					viewBox="0 0 60 {RH * ROWS}"
					preserveAspectRatio="none"
					aria-hidden="true"
				>
					{#if !off}
						{#each visible as r (r.k)}
							{#if r.w > 0}
								{@const y = (r.k - cur.row + (ROWS - 1) / 2) * RH + RH / 2}
								<path
									d="M0,{(RH * ROWS) / 2} C30,{(RH * ROWS) / 2} 30,{y} 56,{y}"
									style:opacity={Math.max(0.12, r.w)}
									style:stroke-width={0.6 + r.w * 1.1}
								/>
							{/if}
						{/each}
					{/if}
				</svg>
				<ol class="rows" style:--rh="{RH}px" aria-label={isRegs ? 'Program lines' : 'Table rows'}>
					{#each visible as r (r.k)}
						<li class={[r.k === cur.row && !off && 'lit', !r.text && 'empty']}>
							<span class="k num">{r.text ? r.k : ''}</span>
							<span class="t">{r.text}</span>
							{#if r.w > 0 && !off}<span class="w num">{fmtW(r.w)}</span>{/if}
						</li>
					{/each}
				</ol>
			</div>
			{#if noAttn && !off}
				<p class="how">
					The lit row is the one whose state and event the tick carries. Attention weights are not
					measured in the browser: the exported model does not return them.
				</p>
			{/if}
			{#if !off && elsewhere > 1e-6}
				<p class="foot num">weight on rows out of view {fmtW(elsewhere)}</p>
			{/if}
			{#if isLlm && att && !att.error}
				<p class="how">
					Attention measured once per certified row in a separate eager pass, not on the tick's own
					code path; the head with the most weight on the matching row ({att.mean_on_matching_row.toFixed(
						3
					)} on average, top on {att.rows_where_matching_row_is_top} of {att.rows} rows) was picked after
					the fact.
				</p>
			{/if}

			<div class="step num">
				{#if pending}
					<span><b>{cur.s}</b> —{cur.event}→ <b>{cur.t}</b> as written</span>
					<span class="quiet"
						>{Number.isFinite(cur.margin)
							? `argmax ${cur.margin > 0 ? 'matches' : 'checked'}, margin ${cur.margin.toFixed(2)}`
							: 'one tick over the cached table'} · then {int(tapeTotal)} ticks, one per event</span
					>
				{:else if off && isLlm}
					<span>the base weights give <b>{stuck}</b></span>
					<span class="quiet"
						>with the adapter on, this tick gives {cur.t}{stuck === cur.t ? ' too' : ''}</span
					>
				{:else if off}
					<span>state stays <b>{stuck}</b></span>
					<span class="quiet">with the head off, the readout falls back to one name every step</span
					>
				{:else if isLlm && cur.lookup}
					<span><b>{cur.s}</b> —{cur.event}→ <b>{cur.t}</b></span>
					<span class="quiet"
						>read from certified row {int(cur.row)}, not run (lookup mode) · margin {cur.margin.toFixed(
							2
						)}</span
					>
				{:else if isLlm}
					<span><b>{cur.s}</b> —{cur.event}→ <b>{cur.t}</b></span>
					<span class="quiet"
						>margin {cur.margin.toFixed(2)} · {cur.row >= 0
							? `row ${int(cur.row)} of ${int(rowCount)}`
							: 'no row: the run left the table'} · logits {cur.eq
							? 'bitwise equal to the certified row'
							: 'not equal to a certified row'}</span
					>
				{:else if isRegs}
					<span><b>{cur.event}</b> {cur.note}</span>
					<span class="quiet"
						>next line {cur.t} · smallest margin {cur.margin.toFixed(2)} ({cur.ms})</span
					>
				{:else}
					<span><b>{cur.s}</b> —{cur.event}→ <b>{cur.t}</b></span>
					<span class="quiet"
						>margin {cur.margin.toFixed(2)} · row {int(cur.row)} of {int(rowCount)}</span
					>
				{/if}
			</div>
		</div>
		{#if isRegs}
			<div class="side">
				<div class="label">memory after this instruction</div>
				<RegsMemory {trace} step={cur.i} />
			</div>
		{/if}
	</div>
</Pane>

<style>
	.run {
		display: grid;
		gap: 14px;
		align-content: start;
		min-height: 0;
	}
	.main,
	.side {
		display: flex;
		flex-direction: column;
		gap: 12px;
		min-width: 0;
		min-height: 0;
	}
	.side {
		gap: 6px;
	}
	@media (min-width: 1181px) {
		.run.regs {
			grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
			gap: 28px;
		}
	}
	.label {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-ink-3);
	}
	.tape-wrap {
		display: grid;
		gap: 5px;
	}
	.tape {
		display: grid;
		grid-template-columns: repeat(var(--cells), minmax(0, 1fr));
		gap: 2px;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
	}
	.cell {
		height: 24px;
		padding: 0;
		border: 0;
		border-bottom: 1px solid var(--color-edge);
		background: transparent;
		color: var(--color-ink-3);
		font: inherit;
		overflow: hidden;
		text-overflow: clip;
		white-space: nowrap;
		cursor: pointer;
	}
	.cell.done {
		color: var(--color-ink-2);
		border-bottom-color: var(--color-rule);
	}
	.cell.now {
		color: var(--color-void);
		background: var(--color-ink);
		border-bottom-color: var(--color-ink);
		border-radius: 2px 2px 0 0;
	}
	.cell:disabled {
		border-bottom-color: transparent;
		cursor: default;
	}
	.mini {
		height: 2px;
		background: var(--color-edge);
		border-radius: 1px;
		overflow: hidden;
	}
	.fill {
		display: block;
		height: 100%;
		background: var(--color-ink-2);
	}
	.read {
		display: grid;
		grid-template-columns: minmax(72px, auto) 40px minmax(0, 1fr);
		align-items: center;
	}
	.head {
		display: grid;
		gap: 3px;
		justify-items: start;
	}
	.query {
		font-family: var(--font-mono);
		font-size: var(--text-xs);
		color: var(--color-ink);
	}
	.meta {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.arrows {
		width: 100%;
		height: calc(21px * 7);
		overflow: visible;
	}
	.arrows path {
		fill: none;
		stroke: var(--color-ink);
		vector-effect: non-scaling-stroke;
	}
	.rows {
		margin: 0;
		padding: 0;
		list-style: none;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
	}
	.rows li {
		display: flex;
		align-items: center;
		gap: 10px;
		height: var(--rh);
		padding: 0 8px;
		color: var(--color-ink-3);
		white-space: nowrap;
		overflow: hidden;
		border-left: 1px solid transparent;
	}
	.rows li.lit {
		color: var(--color-ink);
		background: rgb(255 255 255 / 0.05);
		border-left-color: var(--color-ink);
	}
	.k {
		width: 3.5ch;
		text-align: right;
		color: var(--color-ink-3);
		flex: none;
	}
	.t {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.w {
		flex: none;
		color: var(--color-ink-2);
	}
	.foot {
		margin-top: -6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		text-align: right;
	}
	.step {
		display: grid;
		gap: 2px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.step b {
		font-weight: 500;
		font-family: var(--font-mono);
		color: var(--color-ink);
	}
	.step span {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.quiet {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.how {
		font-size: 10px;
		line-height: 1.45;
		color: var(--color-ink-3);
	}
</style>
