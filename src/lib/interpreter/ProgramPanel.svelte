<script lang="ts">
	/** Panel 1: the program, as its rules and as a machine (automaton) or as its listing (REGS). */
	import type { Attachment } from 'svelte/attachments';
	import MachineDiagram from './MachineDiagram.svelte';
	import Pane from './Pane.svelte';
	import { int, programLines, ruleLine, type Trace, type TraceStep } from './trace.ts';

	let { trace, cur, stuck }: { trace: Trace; cur: TraceStep; stuck: string | null } = $props();

	const lines = $derived(programLines(trace.program.text));
	const isRegs = $derived(trace.kind === 'regs');
	const isLlm = $derived(trace.kind === 'llm');
	const lit = $derived(
		isRegs
			? cur.row
			: stuck !== null
				? -1
				: isLlm
					? (trace.program.row_lines?.[cur.row] ?? -1)
					: ruleLine(lines, cur.event)
	);
	const next = $derived(isRegs ? Number(cur.t) : -1);
	const index = $derived(new Map(trace.program.states.map((s, i) => [s, i])));
	const from = $derived(index.get(stuck ?? cur.s) ?? 0);
	const to = $derived(index.get(stuck ?? cur.t) ?? 0);
	const size = $derived(
		`${trace.program.states.length} states × ${trace.program.events.length} events`
	);
	const short = $derived(
		isRegs
			? `hand-written listing, ${trace.program.lines} lines`
			: isLlm
				? `written by the model, ${size}`
				: `reference program, ${size}`
	);
	const llmFile = $derived(trace.llm?.file);

	/** Scrolls the text (not the page) so the lit line sits in the middle. */
	const centre =
		(k: number): Attachment<HTMLElement> =>
		(list) => {
			const el = list.children[k] as HTMLElement | undefined;
			if (el)
				list.scrollTop = Math.max(0, el.offsetTop - list.clientHeight / 2 + el.offsetHeight / 2);
		};
</script>

<Pane n={1} title="The program" source={trace.panels.program} {short}>
	<div class="wrap">
		<div class={['program', isRegs && 'regs']}>
			<ol class="text" {@attach centre(lit)} aria-label="Program text">
				{#each lines as line, i (i)}
					<li class={[i === lit && 'lit', i === next && i !== lit && 'next']}>
						{#if isRegs}<span class="mark" aria-hidden="true"
								>{i === lit ? '▸' : i === next ? '·' : ''}</span
							>{/if}{line || ' '}
					</li>
				{/each}
			</ol>
			{#if !isRegs && trace.program.diagram}
				<div class="diagram">
					<MachineDiagram
						{trace}
						{from}
						{to}
						event={stuck === null ? cur.event : isLlm ? 'adapter off' : 'head off'}
					/>
				</div>
			{/if}
		</div>
		{#if llmFile}
			{@const which =
				trace.program.registers && trace.program.registers.length > 1
					? `; this is register ${llmFile.registers[trace.llm?.register ?? 0]?.name} of ${trace.program.registers.join(', ')}`
					: ''}
			<p class="caveat">
				{#if llmFile.where === 'browser'}
					Written by {llmFile.model.name} in this browser in {int(llmFile.compile.tokens)} tokens and
					read back from those tokens. The table runs one tick per event on the same weights{which}.
				{:else}
					Written by {llmFile.model.name} with the compile adapter in {int(llmFile.compile.tokens)} tokens
					and read back from those tokens. The table runs one tick per event on the executor adapter{which}.
				{/if}
			</p>
		{:else if trace.panels.program.mock}
			<p class="caveat">
				Mock: a stand-in for the step where the model writes the program. Written by the question's
				generator, not by a model; the run that follows is real.
			</p>
		{:else if isRegs}
			<p class="caveat">
				Hand-written in REGS, not written by a model. Each instruction runs as 18 lookups of the
				same frozen core.
			</p>
		{/if}
	</div>
</Pane>

<style>
	.wrap {
		display: flex;
		flex-direction: column;
	}
	.program {
		flex: 1;
		display: grid;
		grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
		gap: 14px;
		min-height: 0;
	}
	.program.regs {
		grid-template-columns: minmax(0, 1fr);
	}
	.text {
		margin: 0;
		padding: 0;
		list-style: none;
		overflow: auto;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		line-height: 1.6;
		color: var(--color-ink-3);
		min-height: 0;
		max-height: 100%;
		position: relative;
	}
	.text li {
		white-space: pre-wrap;
		padding: 0 4px 0 calc(4px + 2ch);
		text-indent: -2ch;
		border-left: 1px solid transparent;
		transition:
			color 160ms ease-in-out,
			border-color 160ms ease-in-out;
	}
	.regs .text li {
		white-space: pre;
		padding-left: 4px;
		text-indent: 0;
	}
	.text li.lit {
		color: var(--color-ink);
		border-left-color: var(--color-ink);
		background: rgb(255 255 255 / 0.04);
	}
	.text li.next {
		color: var(--color-ink-2);
	}
	.mark {
		display: inline-block;
		width: 1.4ch;
		color: var(--color-ink);
	}
	.diagram {
		min-height: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.diagram :global(svg) {
		max-height: 100%;
	}
	.caveat {
		flex: none;
		margin-top: 8px;
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	@media (max-width: 1180px) {
		.text {
			max-height: 300px;
		}
	}
	@media (max-width: 560px) {
		.program {
			grid-template-columns: 1fr;
		}
		.text {
			max-height: 190px;
		}
		.diagram {
			max-height: 280px;
		}
	}
</style>
