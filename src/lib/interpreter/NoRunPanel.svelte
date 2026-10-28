<script lang="ts">
	/** A Qwen3-4B question that never reached the run: what the model wrote, and where the loop stopped. */
	import { adapterName, cpuName, int, type LlmTrace } from './trace.ts';

	let { file }: { file: LlmTrace } = $props();

	const anchors = $derived(file.input?.anchors ?? null);
	const score = $derived(file.score ?? null);
</script>

<section class="norun" aria-label="No run">
	<p class="eyebrow">{file.title}</p>
	<h2>No run: the loop stopped before the first tick</h2>
	<p class="why">{file.note ?? 'The model wrote no table that could run'}.</p>
	{#if anchors}
		<p class="quiet">
			It quoted the tape as starting after <code>{JSON.stringify(anchors[0])}</code> and ending
			before <code>{JSON.stringify(anchors[1])}</code>; the clock looks for both in the question to
			find the events.
		</p>
	{/if}
	{#if score}
		<p class="quiet">
			Against the question's own program, the table is {score.table_exact
				? 'exact'
				: `wrong in ${score.rows_wrong ?? 'some'} rows`}. With no run there is no answer{file.truth
				? ` (truth: ${file.truth})`
				: ''}.
		</p>
	{/if}
	{#if file.compile?.text}
		<pre class="src">{file.compile.text}</pre>
	{/if}
	<p class="prov num">
		{#if file.where === 'browser'}
			Written by {file.model.name} in this browser on {file.host.gpu ?? 'this GPU'}{file.compile
				? `, ${int(file.compile.tokens)} tokens in ${file.compile.seconds.toFixed(1)} s`
				: ''}
		{:else}
			Written by {file.model.name} with the compile adapter {adapterName(
				file.model.compile_adapter
			)}{file.compile
				? `, ${int(file.compile.tokens)} tokens in ${file.compile.seconds.toFixed(1)} s`
				: ''} · {file.live ? 'run live' : 'recorded'} on {file.host.gpu ?? 'an unknown GPU'}, {cpuName(
				file.host
			)}{file.provenance ? ` · recorded ${file.provenance.recorded_at.slice(0, 10)}` : ''}
		{/if}
	</p>
</section>

<style>
	.norun {
		display: flex;
		flex-direction: column;
		gap: 10px;
		max-width: 760px;
		padding: 28px 32px;
		overflow-y: auto;
	}
	.eyebrow {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.14em;
		color: var(--color-ink-3);
	}
	h2 {
		font-size: var(--text-sm);
		font-weight: 500;
	}
	.why {
		font-size: var(--text-xs);
	}
	.quiet {
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	code {
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
	}
	.src {
		margin-top: 4px;
		padding: 12px 14px;
		border: 1px solid #222;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		line-height: 1.5;
		white-space: pre-wrap;
		color: var(--color-ink-2);
	}
	.prov {
		font-size: 10px;
		color: var(--color-ink-3);
	}
</style>
