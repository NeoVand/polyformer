<script lang="ts">
	/**
	 * One call in a reply with calls in the middle (REASON_FORMAT), compact: the program as one line, what the clock made
	 * of it (certified, its rows, whether the run is its table's run) and the result. Opened, the run and the
	 * certificate as the page's panels show them. While the model or the clock still has the call (`live`), only its
	 * program line shows: the chat's status line says how far it is.
	 */
	import CertificatePanel from './CertificatePanel.svelte';
	import RunPanel from './RunPanel.svelte';
	import { asTrace, int, type ReasonCall } from './trace.ts';

	let {
		k,
		program,
		call = null,
		live = false,
		shown = false,
		onshow
	}: {
		k: number;
		/** the call's text, <program> to <exec/> */
		program: string;
		/** the finished call; null while the clock has it */
		call?: ReasonCall | null;
		/** the model is writing it or the clock has it */
		live?: boolean;
		/** the page's panels show this call */
		shown?: boolean;
		onshow?: () => void;
	} = $props();

	let open = $state(false);
	let reg = $state(0);
	/** the playhead in the opened panels; null follows the last step */
	let step = $state<number | null>(null);

	/** the program as one line: its `task:` line, else its first line */
	const task = $derived.by(() => {
		const lines = program
			.split('\n')
			.map((l) => l.trim())
			.filter((l) => l && l !== '<program>');
		return lines.find((l) => l.startsWith('task:')) ?? lines[0] ?? program.slice(0, 80);
	});
	const regs = $derived(call?.run.registers ?? []);
	const trace = $derived(
		call && regs.length ? asTrace(call.run, Math.min(reg, regs.length - 1)) : null
	);
	const count = $derived(trace?.steps.length ?? 0);
	const at = $derived(step === null ? count - 1 : Math.min(step, count - 1));
	const cur = $derived(trace && count ? trace.steps[at] : null);
	const rows = $derived(regs.reduce((a, r) => a + r.program.rows.length, 0));
	const wrong = $derived(regs.reduce((a, r) => a + (r.certificate.rows_wrong ?? 0), 0));
	const status = $derived.by(() => {
		if (!call) return '';
		if (call.error === 'hard stop') return 'not run: the 12th call ends the response';
		if (call.error) return `error: ${call.error}`;
		return [
			call.certified ? 'certified' : `not certified, ${int(wrong)} of ${int(rows)} rows wrong`,
			call.certified ? `${int(rows)} rows` : null,
			regs.every((r) => r.exact !== false) ? 'run exact' : 'the run left its table'
		]
			.filter(Boolean)
			.join(' · ');
	});
	/** where each number or the tape was read: the question, the notes, or an earlier result */
	const reads = $derived.by(() => {
		if (!call) return [];
		let located = 0;
		return call.read.map((r, i) => {
			const cited = 'result' in r.from;
			const how = cited ? null : call.how[located++];
			return {
				which: call.mode === 'numbers' ? (i ? 'second' : 'first') : 'tape',
				from:
					'result' in r.from
						? `result ${r.from.result}`
						: r.from.source === 0
							? 'the question'
							: 'the notes',
				how,
				text:
					call.mode === 'numbers' || cited
						? r.text
						: `${int(call.run.input.events?.length ?? 0)} events`
			};
		});
	});
</script>

<div class={['call', open && 'open', live && 'live']}>
	<button
		class="head"
		aria-expanded={call ? open : undefined}
		disabled={!call}
		onclick={() => (open = !open)}
	>
		<span class="k num">call {k}</span>
		<code class="prog">{task}</code>
		{#if call}<span class="chev" aria-hidden="true">{open ? '−' : '+'}</span>{/if}
	</button>
	{#if call}
		<p class={['status', 'num', call.error && 'err']}>
			<span>{status}</span>
			{#if call.value !== null}
				<span class="val" aria-label="Result {k}">→ {call.value}</span>
			{/if}
		</p>
	{/if}
	{#if open && call}
		<div class="detail">
			{#if reads.length}
				<ul class="reads num">
					{#each reads as r, i (i)}
						<li>
							<span class="k">{r.which}</span>
							<span class="v">{r.text}</span>
							<span class="from"
								>from {r.from}{r.how === 'relaxed' ? ', whitespace relaxed' : ''}</span
							>
						</li>
					{/each}
				</ul>
			{/if}
			{#if regs.length > 1}
				<div class="regs" role="group" aria-label="Register">
					<span class="k">register</span>
					{#each regs as r, i (r.name)}
						<button
							aria-pressed={i === Math.min(reg, regs.length - 1)}
							onclick={() => {
								reg = i;
								step = null;
							}}>{r.name}</button
						>
					{/each}
				</div>
			{/if}
			{#if trace && cur}
				<div class="panels">
					<RunPanel {trace} {cur} stuck={null} onseek={(i) => (step = i)} />
					<CertificatePanel {trace} {cur} stuck={null} />
				</div>
				<p class="quiet">
					Π built fresh for this call, its rows at positions 0 …, never where the call sits in the
					words.{#if onshow && !shown}
						<button class="link show" onclick={onshow}>Show it in the panels</button>{/if}
				</p>
			{:else}
				<pre class="src">{program}</pre>
				{#if call.run.note}<p class="quiet">{call.run.note}.</p>{/if}
			{/if}
		</div>
	{/if}
</div>

<style>
	.call {
		display: grid;
		gap: 1px;
		min-width: 0;
	}
	.head {
		display: flex;
		align-items: baseline;
		gap: 8px;
		min-width: 0;
		padding: 2px 0;
		border: 0;
		background: transparent;
		color: inherit;
		font: inherit;
		text-align: left;
		cursor: pointer;
	}
	.head:disabled {
		cursor: default;
	}
	.k {
		flex: none;
		font-size: 10px;
		letter-spacing: 0.04em;
		color: var(--color-ink-3);
	}
	.prog {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		white-space: nowrap;
		text-overflow: ellipsis;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.head:hover .prog,
	.open .prog {
		color: var(--color-ink);
	}
	.chev {
		flex: none;
		width: 1ch;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.status {
		display: flex;
		flex-wrap: wrap;
		gap: 0 10px;
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-3);
		min-width: 0;
	}
	.status.err {
		color: var(--color-ink-2);
	}
	.val {
		color: var(--color-ink);
		font-family: var(--font-mono);
		overflow-wrap: anywhere;
		min-width: 0;
	}
	.detail {
		display: grid;
		gap: 6px;
		margin-top: 4px;
		min-width: 0;
	}
	.reads {
		display: grid;
		gap: 2px;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: var(--text-2xs);
	}
	.reads li {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0 8px;
		min-width: 0;
	}
	.reads .k {
		min-width: 5.5ch;
	}
	.reads .v {
		font-family: var(--font-mono);
		color: var(--color-ink-2);
		overflow-wrap: anywhere;
		min-width: 0;
	}
	.reads .from {
		color: var(--color-ink-3);
	}
	.regs {
		display: flex;
		align-items: baseline;
		gap: 10px;
		font-size: var(--text-2xs);
	}
	.regs button {
		border: 0;
		background: transparent;
		padding: 2px 0;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		cursor: pointer;
	}
	.regs button:hover,
	.regs button[aria-pressed='true'] {
		color: var(--color-ink);
	}
	.regs button[aria-pressed='true'] {
		text-decoration: underline;
		text-underline-offset: 4px;
	}
	/* the page's panels, flush with the chat's text */
	.panels {
		display: grid;
		min-width: 0;
	}
	.panels > :global(.pane) {
		padding: 8px 0 10px;
	}
	.quiet {
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.link {
		border: 0;
		padding: 0;
		background: transparent;
		color: var(--color-ink-2);
		font: inherit;
		text-decoration: underline;
		text-decoration-color: var(--color-rule);
		text-underline-offset: 3px;
		cursor: pointer;
	}
	.link:hover {
		color: var(--color-ink);
	}
	.show {
		margin-left: 0.4em;
	}
	.src {
		margin: 0;
		max-height: 180px;
		overflow: auto;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		line-height: 1.5;
		white-space: pre-wrap;
		overflow-wrap: anywhere;
		color: var(--color-ink-3);
	}
</style>
