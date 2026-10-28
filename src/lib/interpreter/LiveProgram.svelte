<script lang="ts">
	/**
	 * A run in this browser before its table exists: the model reading the question, then writing its program token
	 * by token. The five panels take over once the clock has parsed the program and the first register is certified.
	 */
	import type { Attachment } from 'svelte/attachments';
	import StageLine from './StageLine.svelte';
	import { int } from './trace.ts';
	import { SAVANT } from './webgpu/config.ts';
	import type { LiveRun } from './webgpu/live-view.ts';

	let { run }: { run: LiveRun } = $props();

	const text = $derived(run.compile.text.replace(/<exec\/>$/, ''));
	const rate = $derived(
		run.compile.seconds > 0.3 ? Math.round(run.compile.tokens / run.compile.seconds) : null
	);
	const writing = $derived(run.stage === 'compile');

	/** keeps the newest line in view while the program grows */
	const bottom: Attachment<HTMLElement> = (el) => {
		void text;
		el.scrollTop = el.scrollHeight;
	};
</script>

<section class="liveprog" aria-label="The model at work">
	<StageLine {run} />
	<div class="cols">
		<pre
			class="code"
			{@attach bottom}
			aria-label="The program as it is written">{text}{#if writing}<span
					class="caret"
					aria-hidden="true"></span>{/if}{#if !text && !writing}<span class="placeholder"
					>{run.stage === 'queued'
						? `Waiting for ${SAVANT.short} to finish loading.`
						: 'The program appears here as the model writes it.'}</span
				>{/if}</pre>
		<div class="side">
			{#if run.stage === 'prefill' || run.stage === 'queued'}
				<p class="big num">
					<b>{int(run.prefill.done)}</b> of {int(run.prefill.total)} tokens read
				</p>
				<p class="quiet">
					{SAVANT.short} reads your question once; the keys and values it computes stay on the GPU and
					the program and the answer are written after them.
				</p>
			{:else}
				<p class="big num">
					<b>{int(run.compile.tokens)}</b> tokens written{#if rate}<span class="sep">·</span>{rate} per
						second{/if}
				</p>
				<p class="quiet">
					It writes a literal table: one row <code>state event next-state</code> for every pair, and
					a
					<code>tape:</code> line quoting the words just before and just after the events in your
					question. When it writes <code>&lt;exec/&gt;</code>, the clock takes over: it parses the
					table from these tokens, finds the events, certifies every row, and runs it.
				</p>
			{/if}
		</div>
	</div>
</section>

<style>
	.liveprog {
		display: flex;
		flex-direction: column;
		gap: 14px;
		padding: 16px;
		min-height: 0;
		flex: 1;
	}
	.cols {
		flex: 1;
		min-height: 0;
		display: grid;
		grid-template-columns: minmax(0, 1.4fr) minmax(220px, 1fr);
		gap: 24px;
	}
	.code {
		margin: 0;
		min-height: 260px;
		max-height: calc(100dvh - var(--bar-h) - 140px);
		overflow: auto;
		padding: 14px 16px;
		border-left: 1px solid var(--color-edge);
		font-family: var(--font-mono);
		font-size: var(--text-xs);
		line-height: 1.6;
		color: var(--color-ink-2);
		white-space: pre-wrap;
		overflow-wrap: anywhere;
	}
	.caret {
		display: inline-block;
		width: 0.6ch;
		height: 1.1em;
		margin-left: 1px;
		vertical-align: text-bottom;
		background: var(--color-ink);
		animation: blink 1s steps(2, start) infinite;
	}
	@keyframes blink {
		to {
			visibility: hidden;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.caret {
			animation: none;
		}
	}
	.placeholder {
		color: var(--color-ink-3);
	}
	.side {
		display: grid;
		align-content: start;
		gap: 10px;
	}
	.big {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.big b {
		font-size: var(--text-lg);
		font-weight: 500;
		color: var(--color-ink);
	}
	.sep {
		margin: 0 7px;
		color: var(--color-ink-3);
	}
	.quiet {
		font-size: var(--text-2xs);
		line-height: 1.6;
		color: var(--color-ink-3);
	}
	code {
		font-family: var(--font-mono);
		color: var(--color-ink-2);
	}
	@media (max-width: 860px) {
		.cols {
			grid-template-columns: 1fr;
		}
		.code {
			min-height: 180px;
			max-height: 50vh;
		}
	}
</style>
