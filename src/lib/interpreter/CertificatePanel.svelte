<script lang="ts">
	/**
	 * Panel 4: the certificate. Every (state, event) row stepped once from exact codes before the run, with its margin;
	 * the size bound N* that makes the answer exact at every input length. REGS: the composition certificate.
	 */
	import MealyCertGrid from './MealyCertGrid.svelte';
	import Pane from './Pane.svelte';
	import { int, type Trace, type TraceStep } from './trace.ts';

	let {
		trace,
		cur,
		stuck,
		pending = false
	}: {
		trace: Trace;
		cur: TraceStep;
		stuck: string | null;
		/** a run in this browser is still certifying this register */
		pending?: boolean;
	} = $props();

	const c = $derived(trace.certificate);
	const isRegs = $derived(trace.kind === 'regs');
	const isLlm = $derived(trace.kind === 'llm');
	const rows = $derived(trace.program.rows);
	const A = $derived(trace.program.events.length);
	const N = $derived(trace.program.states.length);
	const cols = $derived.by(() => {
		const n = rows.length;
		const raw = Math.max(A, Math.ceil(Math.sqrt(n * 5)));
		return A <= 8 ? Math.ceil(raw / A) * A : raw;
	});
	const mealy = $derived(!!trace.program.mealy);
	const checked = $derived(rows.filter((r) => r.m !== undefined && !Number.isNaN(r.m)));
	/** both cells' margins for a Mealy register */
	const all = $derived(
		checked.flatMap((r) => (mealy && r.m2 !== undefined ? [r.m!, r.m2] : [r.m!]))
	);
	const lo = $derived(all.length ? Math.min(...all) : 0);
	const hi = $derived(all.length ? Math.max(...all) : 0);
	const inBrowser = $derived(trace.llm?.file.where === 'browser');
	/** lookup mode: steps read from their certified rows instead of run */
	const looked = $derived(trace.llm?.file.registers[trace.llm.register]?.ticks.lookup ?? 0);
	const fmt = (m: number) => (Number.isFinite(m) ? m.toFixed(2) : '—');
	const shade = (m: number) => (hi > lo ? 0.35 + (0.6 * (m - lo)) / (hi - lo) : 0.8);
	const CELL = 9;
	const tables = $derived(Object.entries(c.tables ?? {}));
	const verdict = $derived(c.all_ok && c.certified && !pending);
	const source = $derived({
		source: trace.panels.run.source,
		mock: false,
		note: isRegs
			? 'REGS Theorem R1, checked on this machine'
			: mealy
				? 'arith_core.certify: every row as one tick of two forwards on the run’s own code path'
				: isLlm
					? 'pb_pin.certify: every row as one tick on the run’s own code path'
					: 'INTERP one-step map on every row, on this machine'
	});
	const passed = $derived(
		rows.filter((r) => r.ok === true || (r.ok === undefined && !pending)).length
	);
</script>

<Pane
	n={4}
	title="The certificate"
	{source}
	short={isRegs ? 'composition, checked here' : pending ? 'checking now' : 'checked before the run'}
>
	<div class="cert">
		{#if isRegs}
			<p class="big num">
				<b>{int(c.lookups_checked ?? 0)}</b> consumed lookups checked<span class="sep">·</span
				>smallest margin <b>{c.min_margin.toFixed(2)}</b>
			</p>
			<table class="tables num">
				<thead>
					<tr><th>table</th><th>names</th><th>column</th><th>N*</th><th></th></tr>
				</thead>
				<tbody>
					{#each tables as [k, t] (k)}
						<tr>
							<td>{k}</td>
							<td>{t.N}</td>
							<td>{t.column}</td>
							<td>{t.N_star}</td>
							<td class={t.inside ? 'ok' : 'bad'}>{t.inside ? 'inside' : 'outside'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<p class="big num">
				{#if isLlm}
					<b>{int(passed)} of {int(rows.length)}</b> rows certified{pending ? ' so far' : ''}<span
						class="sep">·</span
					>smallest margin <b>{fmt(c.min_margin)}</b>
				{:else}
					<b>{int(c.pairs_checked ?? rows.length)} of {int(rows.length)}</b> steps checked<span
						class="sep">·</span
					>smallest margin <b>{c.min_margin.toFixed(2)}</b>
				{/if}
			</p>
			{#if mealy}
				<MealyCertGrid
					{rows}
					states={trace.program.states}
					current={stuck === null ? cur.row : -1}
					{pending}
				/>
			{:else}
				<svg
					class="grid"
					style:width="min(100%, {cols * 15}px)"
					viewBox="0 0 {cols * CELL} {Math.ceil(rows.length / cols) * CELL}"
					role="img"
					aria-label="Every row's margin; all rows pass"
				>
					{#each rows as r, k (k)}
						{@const x = (k % cols) * CELL}
						{@const y = Math.floor(k / cols) * CELL}
						<rect
							{x}
							{y}
							width={CELL - 1.5}
							height={CELL - 1.5}
							rx="1"
							class={['cell', r.ok === false && 'wrong', r.ok === undefined && pending && 'todo']}
							style:opacity={r.ok === false
								? 1
								: r.ok === undefined && pending
									? 1
									: shade(r.m ?? 0)}
						/>
						{#if k === cur.row && stuck === null}
							<rect
								x={x - 1.25}
								y={y - 1.25}
								width={CELL + 1}
								height={CELL + 1}
								rx="1.5"
								class="now"
							/>
						{/if}
					{/each}
				</svg>
			{/if}
			{#if mealy}
				<p class="note num">
					A block per carry, the first digit down and the second across. Left half: the carry cell;
					right half: the digit written; lighter for a larger margin ({lo.toFixed(2)} to {hi.toFixed(
						2
					)}){rows.some((r) => r.ok === false)
						? '; an outlined half is a cell whose argmax is not what the row wrote'
						: ''}{pending ? '; hollow: not checked yet' : ''}. A row passes when both forwards'
					argmaxes over the whole vocabulary are what it wrote{inBrowser
						? ', on this GPU and the run’s own code path'
						: ''}.
				</p>
			{:else if isLlm}
				<p class="note num">
					One square per row, lighter for a larger margin ({lo.toFixed(2)} to {hi.toFixed(
						2
					)}){rows.some((r) => r.ok === false)
						? '; an outlined square is a row whose argmax is not its destination'
						: ''}{pending ? '; a hollow square is a row not checked yet' : ''}. Each row runs once
					as a tick over the cached table ({inBrowser
						? 'batch 1, on this GPU, the same code path as every tick of the run'
						: 'batch 1, bf16, SDPA'}); it passes when its argmax over the whole vocabulary is the
					destination it was written with.
				</p>
			{:else}
				<p class="note num">
					One square per row, lighter for a larger margin ({lo.toFixed(2)} to {hi.toFixed(2)}). Each
					row stepped once from exact codes; a row passes when its right name wins.
				</p>
			{/if}
		{/if}
		<p class={['verdict', verdict || pending ? 'ok' : 'bad']}>
			{#if pending}
				Checking row {int(Math.min(rows.length, (cur.row ?? 0) + 1))} of {int(rows.length)}: the
				{mealy && cur.pair
					? `blocks [${cur.s}][${cur.pair[0]}][${cur.pair[1]}] and [${cur.s}][${cur.pair[0]}][${cur.pair[1]}][${cur.t}], each`
					: `block [${cur.s}][${cur.event}]`} after the cached table.
			{:else if verdict && mealy}
				Certified: {N} carries and {A} digit pairs, both cells of every row right.
			{:else if verdict && isLlm}
				Certified: {N} states and {A} events, every row right.
			{:else if verdict}
				Certified{isRegs
					? ''
					: `: ${N} states and ${A} events, inside N* = ${c.N_star} at ${c.A_column} events`}.
			{:else if isLlm}
				Not certified: {int(c.rows_wrong ?? rows.length - passed)} rows wrong, so the run carries no guarantee.
			{:else}
				Not certified.
			{/if}
		</p>
		{#if isLlm && c.ticks_real !== undefined && !(mealy && pending)}
			<p class="note num">
				In the run, {int(c.ticks_equal ?? 0)} of {int(c.ticks_real)}
				{mealy ? 'columns had both forwards' : 'ticks had logits'} bitwise equal to their certified row's.{#if looked}
					The other {int(looked)} steps were read from their certified rows (lookup mode).{/if}
			</p>
		{/if}
		<p class="covers">Covers {c.covers}.</p>
	</div>
</Pane>

<style>
	.cert {
		display: flex;
		flex-direction: column;
		gap: 9px;
		min-height: 0;
		height: 100%;
	}
	.big {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		line-height: 1.5;
	}
	.big b {
		font-weight: 500;
		font-size: var(--text-lg);
		color: var(--color-ink);
	}
	.sep {
		margin: 0 7px;
		color: var(--color-ink-3);
	}
	.grid {
		display: block;
		width: 100%;
		max-width: 260px;
		max-height: 120px;
	}
	.cell {
		fill: var(--color-ink);
	}
	.cell.todo {
		fill: none;
		stroke: var(--color-rule);
		stroke-width: 0.8;
	}
	.cell.wrong {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1;
		stroke-dasharray: 1.5 1;
	}
	.now {
		fill: none;
		stroke: var(--color-ink);
		stroke-width: 1.2;
	}
	.note,
	.covers {
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.verdict {
		font-size: var(--text-xs);
		color: var(--color-ink);
	}
	.verdict.bad,
	.bad {
		color: var(--color-ink-2);
		text-decoration: underline wavy;
	}
	.tables {
		border-collapse: collapse;
		font-size: var(--text-2xs);
		width: 100%;
		max-width: 300px;
	}
	.tables th {
		font-weight: 400;
		color: var(--color-ink-3);
		text-align: left;
		padding: 0 8px 3px 0;
	}
	.tables td {
		padding: 2px 8px 2px 0;
		font-family: var(--font-mono);
		color: var(--color-ink-2);
		border-top: 1px solid #222;
	}
	.tables td.ok {
		color: var(--color-ink);
	}
</style>
