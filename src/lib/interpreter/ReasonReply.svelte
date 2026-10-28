<script lang="ts">
	/**
	 * A reply with calls in the middle (REASON_FORMAT): the model's words, each call compact in its place with its result,
	 * an error line where the clock could not run one, and the words after. Finished, a header line counts the calls and
	 * says whether every one that ran was certified; while it runs, the call the clock has now and the words being
	 * written follow the finished ones.
	 */
	import CallLine from './CallLine.svelte';
	import Reply from './Reply.svelte';
	import { int, type ReasonCall, type ReasonSegment } from './trace.ts';
	import type { LiveRun } from './webgpu/live-view.ts';

	let {
		segments,
		calls,
		live = null,
		shown = null,
		onshow
	}: {
		segments: ReasonSegment[];
		calls: ReasonCall[];
		/** the run while it goes */
		live?: LiveRun | null;
		/** the call the page's panels show */
		shown?: number | null;
		onshow?: (k: number) => void;
	} = $props();

	const byK = $derived(new Map(calls.map((c) => [c.k, c])));
	/** e.g. "3 calls · all certified", "3 calls · 2 run, both certified · call 2 got an error line" */
	const header = $derived.by(() => {
		const n = calls.length;
		const ran = calls.filter((c) => c.certified !== null);
		const failed = ran.filter((c) => !c.certified);
		const errors = calls.filter((c) => c.error && c.error !== 'hard stop');
		const names = (cs: ReasonCall[]) => cs.map((c) => `call ${c.k}`).join(', ');
		const parts = [`${int(n)} call${n === 1 ? '' : 's'}`];
		if (!ran.length) parts.push('none ran');
		else if (failed.length) parts.push(`${names(failed)} not certified`);
		else if (ran.length === n) parts.push(n === 1 ? 'certified' : 'all certified');
		else parts.push(`${int(ran.length)} ran, ${ran.length === 2 ? 'both' : 'all'} certified`);
		if (errors.length)
			parts.push(`${names(errors)} got ${errors.length > 1 ? 'error lines' : 'an error line'}`);
		if (calls.some((c) => c.error === 'hard stop')) parts.push('the 12th call ended the response');
		return parts.join(' · ');
	});
	/** while it goes: the words being written since the last final, up to a program that has begun */
	const writing = $derived.by(() => {
		if (!live || live.reason?.current || live.stage !== 'compile') return null;
		const text = live.compile.text;
		const at = text.indexOf('<program>');
		return { words: at < 0 ? text : text.slice(0, at), program: at >= 0 };
	});
	const nextK = $derived(calls.length + 1);
</script>

<div class="reason">
	{#if !live}
		<p class="summary num">{header}</p>
	{/if}
	{#each segments as s, i (i)}
		{#if s.kind === 'text'}
			{#if s.text.trim()}
				<div class="msg answer"><Reply text={s.text} /></div>
			{/if}
		{:else}
			{@const c = byK.get(s.k)}
			{#if c}
				<CallLine
					k={c.k}
					program={c.program}
					call={c}
					shown={shown === c.k}
					onshow={onshow ? () => onshow(c.k) : undefined}
				/>
			{/if}
		{/if}
	{/each}
	{#if live?.reason?.current}
		<CallLine k={live.reason.current.k} program={live.reason.current.program} live />
	{:else if writing}
		{#if writing.words.trim()}
			<p class="msg answer streaming">{writing.words.trim()}</p>
		{/if}
		{#if writing.program}
			<CallLine
				k={nextK}
				program={live?.compile.text.slice(live.compile.text.indexOf('<program>')) ?? ''}
				live
			/>
		{/if}
	{/if}
</div>

<style>
	.reason {
		display: grid;
		gap: 7px;
		min-width: 0;
	}
	.summary {
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.msg {
		font-size: var(--text-sm);
		line-height: 1.55;
		color: var(--color-ink);
		overflow-wrap: anywhere;
		min-width: 0;
	}
	.answer {
		font-size: var(--text-ui);
	}
	.streaming {
		color: var(--color-ink-2);
		white-space: pre-wrap;
	}
</style>
