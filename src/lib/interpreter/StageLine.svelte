<script lang="ts">
	/** The loop's six stages in a row, the current one lit: where a run in this browser is. */
	import type { LiveRun } from './webgpu/live-view.ts';

	let { run }: { run: LiveRun } = $props();

	const STAGES = [
		{ id: 'prefill', label: 'read the question' },
		{ id: 'compile', label: 'write the program' },
		{ id: 'tape', label: 'read the tape' },
		{ id: 'certify', label: 'certify' },
		{ id: 'run', label: 'run' },
		{ id: 'answer', label: 'answer' }
	] as const;

	const at = $derived(
		run.stage === 'done'
			? STAGES.length
			: run.stage === 'queued'
				? -1
				: STAGES.findIndex((s) => s.id === run.stage)
	);
</script>

<ol class="stages" aria-label="Stages of the run">
	{#each STAGES as s, k (s.id)}
		<li class={[k < at && 'done', k === at && 'now']} aria-current={k === at ? 'step' : undefined}>
			<span class="dot" aria-hidden="true"></span>{s.label}
		</li>
	{/each}
</ol>

<style>
	.stages {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	li {
		display: flex;
		align-items: center;
		gap: 6px;
		white-space: nowrap;
		transition: color 200ms ease-in-out;
	}
	.dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		border: 1px solid var(--color-rule);
		transition:
			background 200ms ease-in-out,
			border-color 200ms ease-in-out;
	}
	li.done {
		color: var(--color-ink-2);
	}
	li.done .dot {
		background: var(--color-ink-2);
		border-color: var(--color-ink-2);
	}
	li.now {
		color: var(--color-ink);
	}
	li.now .dot {
		background: var(--color-ink);
		border-color: var(--color-ink);
		box-shadow: 0 0 0 3px rgb(255 255 255 / 0.12);
		animation: pulse 1.4s ease-in-out infinite;
	}
	@keyframes pulse {
		50% {
			box-shadow: 0 0 0 5px rgb(255 255 255 / 0.04);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		li.now .dot {
			animation: none;
		}
	}
</style>
