<script lang="ts">
	/** Panel 3: the state is digital. The head's output lands on one code at every step, with a margin above zero. */
	import CodeSpace from './CodeSpace.svelte';
	import MarginTrace from './MarginTrace.svelte';
	import Pane from './Pane.svelte';
	import { mealyWords } from './mealy.ts';
	import type { Trace, TraceStep } from './trace.ts';

	let {
		trace,
		cur,
		stuck,
		fast,
		onseek
	}: {
		trace: Trace;
		cur: TraceStep;
		stuck: string | null;
		fast: boolean;
		onseek: (i: number) => void;
	} = $props();

	const isRegs = $derived(trace.kind === 'regs');
	const isLlm = $derived(trace.kind === 'llm');
	const w = $derived(mealyWords(trace));
	/** a run in this browser before its rows are all certified: no view to draw yet */
	const waiting = $derived(trace.codebook.names.length === 0);
	const index = $derived(new Map(trace.codebook.names.map((s, i) => [s, i])));
	const lit = $derived(index.get(stuck ?? cur.t) ?? 0);
	const source = $derived({
		source: trace.panels.run.source,
		mock: false,
		note: trace.codebook.projection
	});
</script>

<Pane
	n={3}
	title="The state is digital"
	{source}
	short={isRegs
		? 'next-line lookup'
		: isLlm
			? 'logits on the state names'
			: 'head output before the snap'}
>
	<div class="state">
		{#if waiting}
			<p class="wait">
				The state view is drawn from the certified rows' own logits, so it appears when every row of
				this register is certified.
			</p>
		{:else}
			<div class="space">
				<CodeSpace
					names={trace.codebook.names}
					xyz={trace.codebook.xyz}
					y={stuck === null ? (cur.xyz ?? null) : null}
					{lit}
					{fast}
				/>
			</div>
			<p class="read num">
				{#if stuck !== null && isLlm}
					Adapter off: the base weights pick <b>{stuck}</b> here.
				{:else if stuck !== null}
					Head off: the readout sees no output and picks <b>{stuck}</b> every step.
				{:else if isLlm && !trace.steps.length}
					The first tick lands here once the run starts.
				{:else if isLlm && cur.o !== undefined}
					Lands on {w.state} <b>{cur.t}</b>, {cur.margin.toFixed(2)} above the next token in the whole
					vocabulary, among {trace.codebook.names.length}
					{w.states} ({(trace.codebook.variance_kept * 100).toFixed(0)}% of the rows' spread in this
					view); the second forward writes
					<b>{cur.o}</b>{#if cur.m2 !== undefined}, {cur.m2.toFixed(2)} above the next{/if}.
				{:else if isLlm}
					Lands on <b>{cur.t}</b>, {cur.margin.toFixed(2)} above the next token in the whole vocabulary,
					among {trace.codebook.names.length} state names ({(
						trace.codebook.variance_kept * 100
					).toFixed(0)}% of the rows' spread in this view).
				{:else if isRegs}
					Lands on line <b>{cur.t}</b>, the next instruction, among {trace.codebook.names.length} line
					codes.
				{:else}
					Lands on <b>{cur.t}</b>{#if cur.d !== undefined}, {cur.d.toFixed(3)} from its code{/if},
					among {trace.codebook.names.length}
					codes.
				{/if}
			</p>
			{#if trace.steps.length}
				<MarginTrace
					steps={trace.steps}
					step={cur.i}
					off={stuck !== null}
					offLabel={isLlm ? 'adapter off' : 'head off'}
					{onseek}
				/>
			{/if}
		{/if}
	</div>
</Pane>

<style>
	.state {
		display: flex;
		flex-direction: column;
		gap: 8px;
		height: 100%;
		min-height: 0;
	}
	.space {
		flex: 1;
		min-height: 150px;
		display: flex;
		justify-content: center;
	}
	.space :global(svg) {
		max-width: 300px;
	}
	.wait {
		margin: auto 0;
		font-size: var(--text-2xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.read {
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
		line-height: 1.45;
	}
	.read b {
		font-family: var(--font-mono);
		font-weight: 500;
		color: var(--color-ink);
	}
</style>
