<script lang="ts">
	/**
	 * Savant-4B in this browser: the one step before anything runs. Checks for WebGPU, offers the download (never
	 * starts it unasked), shows its progress and speed, then where the model runs. Compact once the chat has turns.
	 */
	import { onMount } from 'svelte';
	import { SAVANT, gb } from './webgpu/config.ts';
	import { savant } from './webgpu/savant.svelte.ts';

	let { compact = false }: { compact?: boolean } = $props();

	onMount(() => {
		savant.check();
	});

	const rate = $derived(savant.rate);

	/** the files report their sizes as they start; until the weights have, the known size stands in */
	const total = $derived(Math.max(savant.progress?.total ?? 0, SAVANT.bytes));
	const loaded = $derived(savant.progress?.loaded ?? 0);
	const frac = $derived(total ? Math.min(1, loaded / total) : 0);
	/** every byte is in and the runtime is building the model on the GPU */
	const preparing = $derived(savant.status === 'loading' && !!savant.progress && frac >= 0.999);
	const eta = $derived(rate > 0 && !preparing ? (total - loaded) / rate : null);
	const fileName = $derived(savant.progress?.file?.split('/').pop() ?? '');

	const mmss = (s: number) =>
		s >= 90 ? `about ${Math.round(s / 60)} min left` : `about ${Math.max(1, Math.round(s))} s left`;
	const size = $derived(savant.cached ? 'from this browser' : `~${gb(SAVANT.bytes)}`);
</script>

<section class={['model', compact && 'compact']} aria-label="The model">
	{#if compact}
		<div class="line">
			<span class="name">{SAVANT.name}</span>
			{#if savant.status === 'ready'}
				<span class="quiet num">running in this tab on {savant.loaded?.host.gpu}</span>
			{:else if savant.status === 'loading'}
				<span class="quiet num"
					>{preparing ? 'preparing the GPU…' : `downloading ${Math.round(frac * 100)}%`}</span
				>
				<span class="bar small" aria-hidden="true"
					><span class={[preparing && 'busy']} style:width="{frac * 100}%"></span></span
				>
			{:else if savant.status === 'unsupported'}
				<span class="quiet">cannot run in this browser; recordings replay</span>
			{:else}
				<button
					class="btn load-small"
					disabled={savant.status === 'checking'}
					onclick={() => savant.load()}>Load {SAVANT.short} · {size}</button
				>
			{/if}
		</div>
	{:else}
		<div class="head">
			<span class="name">{SAVANT.name}</span>
			<span class="word"
				>{savant.status === 'ready'
					? 'running here'
					: savant.status === 'loading'
						? preparing
							? 'preparing'
							: 'downloading'
						: savant.status === 'unsupported'
							? 'not here'
							: savant.cached
								? 'downloaded'
								: 'not loaded'}</span
			>
		</div>

		{#if savant.status === 'unsupported'}
			<p class="why">{savant.gpu?.reason}</p>
			<p class="quiet">
				The recorded runs still play back, step by step: pick one below. To run the model yourself,
				open this page in Chrome or Edge on a desktop computer.
			</p>
		{:else if savant.status === 'loading'}
			<div
				class="progress"
				role="progressbar"
				aria-label="Download"
				aria-valuemin={0}
				aria-valuemax={100}
				aria-valuenow={Math.round(frac * 100)}
			>
				<div class="bar">
					<span class={[preparing && 'busy']} style:width="{frac * 100}%"></span>
				</div>
				<p class="num nums">
					{#if preparing}
						Downloaded. Preparing the GPU: the weights move into GPU memory and the runtime compiles
						its shaders.
					{:else}
						<b>{gb(loaded)}</b> of {gb(total)} · {Math.round(frac * 100)}%{#if rate > 0}
							· {(rate / 1e6).toFixed(rate > 1e8 ? 0 : 1)} MB/s{/if}{#if eta !== null}
							· {mmss(eta)}{/if}
					{/if}
				</p>
				{#if fileName && !preparing}<p class="file num">{fileName}</p>{/if}
			</div>
		{:else if savant.status === 'ready'}
			<p class="ready num">
				Running in this tab on <b>{savant.loaded?.host.gpu}</b>, {savant.loaded?.dtype} weights, loaded
				in
				{savant.loaded?.seconds.toFixed(0)} s. Ask it anything below.
			</p>
		{:else}
			<button
				class="btn primary load"
				disabled={savant.status === 'idle' || savant.status === 'checking'}
				onclick={() => savant.load()}
			>
				<span class="main">Load {SAVANT.short}<span class="size num">{size}</span></span>
				<span class="dim">Runs on your GPU; nothing leaves your browser</span>
			</button>
			<p class="quiet">
				{savant.cached
					? 'Downloaded before: it loads from this browser’s cache.'
					: 'Downloaded once; this browser keeps it for next time.'} Made for desktop GPUs; it writes
				a program for your question, certifies it, then runs it one tick per event, all on your GPU.
			</p>
			{#if savant.gpu?.warn}<p class="warn">{savant.gpu.warn}</p>{/if}
			{#if savant.error}<p class="err">Loading stopped: {savant.error}</p>{/if}
		{/if}
		<p class="license">
			{SAVANT.short} is a research preview. Weights © the Polyformer authors, all rights reserved; licensed
			for use in this page only.
			<a href="https://huggingface.co/mohsenvand/savant-4b-preview" target="_blank" rel="noopener"
				>Model card</a
			>{#if savant.status === 'ready' || savant.cached}
				· <button
					class="link"
					onclick={() => savant.forget()}
					disabled={savant.status === 'loading'}>Forget the download</button
				>{/if}
		</p>
	{/if}
</section>

<style>
	.model {
		display: grid;
		gap: 8px;
		margin-top: 16px;
		padding: 12px 0 2px;
		border-top: 1px solid var(--color-edge);
	}
	.model.compact {
		margin: 0;
		padding: 8px 22px;
		border-top: 0;
		border-bottom: 1px solid #222;
	}
	.line {
		display: flex;
		align-items: center;
		gap: 10px;
		min-width: 0;
		font-size: var(--text-2xs);
		white-space: nowrap;
	}
	.line .quiet {
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.head {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 10px;
	}
	.name {
		font-size: var(--text-2xs);
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--color-ink);
		font-weight: 500;
	}
	.word {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--color-ink-3);
	}
	.load {
		display: grid;
		justify-items: start;
		gap: 2px;
		width: 100%;
		height: auto;
		padding: 9px 14px 10px;
		text-align: left;
		white-space: normal;
		line-height: 1.3;
	}
	.load .main {
		display: flex;
		width: 100%;
		justify-content: space-between;
		gap: 12px;
		font-size: var(--text-ui);
		font-weight: 500;
	}
	.load .size {
		font-weight: 400;
		font-size: var(--text-xs);
		opacity: 0.7;
	}
	.load .dim {
		font-size: var(--text-2xs);
		font-weight: 400;
		opacity: 0.72;
	}
	.load-small {
		height: 24px;
		padding: 0 9px;
		font-size: var(--text-2xs);
	}
	.quiet,
	.license,
	.file {
		font-size: var(--text-2xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.license a,
	.link {
		color: var(--color-ink-2);
		text-decoration: underline;
		text-decoration-color: var(--color-rule);
		text-underline-offset: 3px;
	}
	.link {
		border: 0;
		padding: 0;
		background: transparent;
		font: inherit;
		cursor: pointer;
	}
	.link:disabled {
		opacity: 0.5;
	}
	.why,
	.ready,
	.nums {
		font-size: var(--text-xs);
		line-height: 1.5;
		color: var(--color-ink-2);
	}
	.ready b,
	.nums b {
		color: var(--color-ink);
		font-weight: 500;
	}
	.warn,
	.err {
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-2);
		text-decoration: underline wavy var(--color-rule);
		text-underline-offset: 4px;
	}
	.progress {
		display: grid;
		gap: 6px;
	}
	.bar {
		height: 3px;
		background: var(--color-edge);
		border-radius: 2px;
		overflow: hidden;
	}
	.bar.small {
		flex: 1;
		min-width: 40px;
		height: 2px;
	}
	.bar span {
		display: block;
		height: 100%;
		background: var(--color-ink);
		transition: width 300ms ease-out;
	}
	.bar span.busy {
		width: 100% !important;
		background: linear-gradient(
			90deg,
			var(--color-rule) 0%,
			var(--color-ink) 50%,
			var(--color-rule) 100%
		);
		background-size: 200% 100%;
		animation: sweep 1.6s ease-in-out infinite;
	}
	@keyframes sweep {
		from {
			background-position: 100% 0;
		}
		to {
			background-position: -100% 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.bar span.busy {
			animation: none;
		}
	}
</style>
