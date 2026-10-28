<script lang="ts">
	/**
	 * Panel 2 for a number-mode run (ARITH_FORMAT): the two numbers as a written sum, one column per tick from the right,
	 * the carry entering each column above it and the digit written below; then the tick at the playhead (its two
	 * forwards, the row it reads and both margins) and the output tape building up the sum.
	 */
	import { columnsAround, mealyRowText, sumSoFar } from './mealy.ts';
	import { int, type Trace, type TraceStep } from './trace.ts';

	let {
		trace,
		cur,
		onseek,
		pending = false
	}: {
		trace: Trace;
		cur: TraceStep;
		onseek: (i: number) => void;
		/** still certifying: `cur` is the row being checked */
		pending?: boolean;
	} = $props();

	const WIDTH = 13;
	const count = $derived(trace.steps.length);
	const total = $derived(trace.llm?.file.input.events?.length ?? count);
	const at = $derived(pending ? -1 : cur.i);
	const cols = $derived(columnsAround(trace, at, WIDTH));
	const rows = $derived(trace.program.rows);
	const row = $derived(cur.row >= 0 ? rows[cur.row] : undefined);
	const sum = $derived(pending ? null : sumSoFar(trace.steps, at));
	const fmt = (m: number | undefined) =>
		m !== undefined && Number.isFinite(m) ? m.toFixed(2) : '—';
	/** empty cells on the left when the sum has fewer columns than the view */
	const blanks = $derived(Array.from({ length: Math.max(0, WIDTH - cols.length) }, (_, k) => k));
	const below = $derived(cols.length ? cols[cols.length - 1].i : 0);
</script>

<div class="mealy">
	<div class="sheet-wrap">
		<div class="label">
			the two numbers, a column per tick from the right{#if total > WIDTH && cols.length}
				<span class="num">
					· columns {int(below + 1)} to {int(cols[0].i + 1)} of {int(total)}</span
				>{/if}
		</div>
		<div
			class="sheet num"
			style:--cols={WIDTH}
			role="group"
			aria-label="The sum, column by column, around the current column"
		>
			<span class="k">carry</span>
			{#each blanks as k (k)}<span></span>{/each}
			{#each cols as c (c.i)}
				<span class={['carry', c.now && 'now']}>{c.cin ?? ''}</span>
			{/each}

			<span class="k">first</span>
			{#each blanks as k (k)}<span></span>{/each}
			{#each cols as c (c.i)}
				<button
					class={['d', c.padA && 'pad', c.now && 'now', c.done && 'done']}
					disabled={pending || c.i >= count}
					tabindex={c.now ? 0 : -1}
					aria-label="Column {c.i + 1}: {c.a} + {c.b}"
					onclick={() => onseek(c.i)}>{c.a}</button
				>
			{/each}

			<span class="k">second</span>
			{#each blanks as k (k)}<span></span>{/each}
			{#each cols as c (c.i)}
				<span class={['d', c.padB && 'pad', c.now && 'now', c.done && 'done']}>{c.b}</span>
			{/each}

			<span class="rule" style:grid-column="2 / -1"></span>

			<span class="k">sum</span>
			{#each blanks as k (k)}<span></span>{/each}
			{#each cols as c (c.i)}
				<span class={['d', 'out', c.now && 'now']}>{c.o ?? ''}</span>
			{/each}
		</div>
		<div class="mini" aria-hidden="true">
			<span class="fill" style:width="{pending ? 0 : ((cur.i + 1) / Math.max(1, total)) * 100}%"
			></span>
		</div>
	</div>

	<div class="step num">
		{#if pending}
			<span
				>certifying row {int(cur.row + 1)} of {int(rows.length)}: <b>{cur.s}</b>
				{cur.pair?.[0]} + {cur.pair?.[1]} → <b>{cur.t}</b>, writes <b>{cur.o}</b></span
			>
			<span class="quiet"
				>{Number.isFinite(cur.margin)
					? `margins ${fmt(cur.margin)} on the carry, ${fmt(cur.m2)} on the digit`
					: 'two forwards over the cached table'} · then {int(total)} columns, two forwards each</span
			>
		{:else}
			<span
				>carry <b>{cur.s}</b>, <b>{cur.pair?.[0]}</b> + <b>{cur.pair?.[1]}</b> → carry
				<b>{cur.t}</b>, writes <b>{cur.o}</b></span
			>
			<span class="quiet">
				{#if cur.row < 0}
					no row: the run left the table
				{:else if cur.lookup}
					read from certified row {int(cur.row)}: {mealyRowText(row)}, not run (lookup mode)
				{:else}
					row {int(cur.row)} of {int(rows.length)}: {mealyRowText(row)}
				{/if}
			</span>
			<span class="quiet"
				>margins {fmt(cur.margin)} on the carry, {fmt(cur.m2)} on the digit{cur.lookup
					? ''
					: cur.eq
						? ' · both forwards bitwise equal to the certified row'
						: ' · not equal to a certified row'}</span
			>
		{/if}
	</div>

	{#if sum}
		<div class="tape">
			<div class="label num">
				the sum so far · {int(sum.digits)} of {int(total)} digits, the newest first
			</div>
			<p class="digits num" aria-label="The sum so far">
				<span class="new">{sum.newest}</span>{sum.rest}
			</p>
		</div>
	{/if}
</div>

<style>
	.mealy {
		display: flex;
		flex-direction: column;
		gap: 12px;
		min-height: 0;
	}
	.label {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-ink-3);
	}
	.label .num {
		text-transform: none;
		letter-spacing: 0;
	}
	.sheet-wrap {
		display: grid;
		gap: 5px;
	}
	.sheet {
		display: grid;
		grid-template-columns: 6ch repeat(var(--cols), minmax(0, 1fr));
		align-items: center;
		row-gap: 1px;
		font-family: var(--font-mono);
		font-size: var(--text-xs);
	}
	.sheet > span,
	.sheet > button {
		height: 21px;
		line-height: 21px;
		text-align: center;
	}
	.k {
		text-align: left !important;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.carry {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.carry.now {
		color: var(--color-ink);
	}
	.d {
		color: var(--color-ink-3);
	}
	.d.done {
		color: var(--color-ink-2);
	}
	.d.pad {
		opacity: 0.45;
	}
	.d.now {
		color: var(--color-void);
		background: var(--color-ink);
		opacity: 1;
	}
	.out {
		color: var(--color-ink);
	}
	button.d {
		padding: 0;
		border: 0;
		background: transparent;
		font: inherit;
		cursor: pointer;
	}
	button.d.now {
		background: var(--color-ink);
	}
	button.d:disabled {
		cursor: default;
	}
	.rule {
		height: 1px !important;
		background: var(--color-rule);
		margin: 2px 0;
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
		overflow-wrap: anywhere;
	}
	.quiet {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.tape {
		display: grid;
		gap: 4px;
		min-height: 0;
	}
	.digits {
		margin: 0;
		max-height: 4.6em;
		overflow-y: auto;
		font-family: var(--font-mono);
		font-size: var(--text-xs);
		line-height: 1.5;
		color: var(--color-ink-2);
		overflow-wrap: anywhere;
		word-break: break-all;
	}
	.new {
		color: var(--color-void);
		background: var(--color-ink);
		padding: 0 1px;
	}
</style>
