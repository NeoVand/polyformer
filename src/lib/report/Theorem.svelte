<script lang="ts" module>
	export type Evidence = 'proved' | 'checked' | 'measured' | 'prior' | 'open';
	export const EVIDENCE_LABEL: Record<Evidence, string> = {
		proved: 'Proved here',
		checked: 'Proved, and checked numerically',
		measured: 'Measured',
		prior: 'Known result',
		open: 'Open'
	};
</script>

<script lang="ts">
	/**
	 * A numbered result in the report: kind and number, an optional name, how well
	 * it is established, the statement, and a proof that opens on request.
	 */
	import type { Snippet } from 'svelte';

	let {
		kind = 'Theorem',
		n,
		name,
		evidence,
		id,
		children,
		proof
	}: {
		kind?:
			'Theorem' | 'Proposition' | 'Lemma' | 'Definition' | 'Construction' | 'Corollary' | 'Remark';
		n?: string | number;
		name?: string;
		evidence?: Evidence;
		id?: string;
		children: Snippet;
		proof?: Snippet;
	} = $props();
	let open = $state(false);
</script>

<div class="thm" class:def={kind === 'Definition' || kind === 'Remark'} {id}>
	<div class="head">
		<span class="kind">{kind}{n !== undefined ? ` ${n}` : ''}</span>
		{#if name}<span class="name">({name})</span>{/if}
		{#if evidence}<span class="ev {evidence}">{EVIDENCE_LABEL[evidence]}</span>{/if}
	</div>
	<div class="body">{@render children()}</div>
	{#if proof}
		<button class="toggle" aria-expanded={open} onclick={() => (open = !open)}>
			{open ? 'Hide the proof' : 'Show the proof'}
		</button>
		{#if open}
			<div class="proof">
				{@render proof()}
				<span class="qed" aria-label="End of proof">∎</span>
			</div>
		{/if}
	{/if}
</div>

<style>
	.thm {
		margin: 22px 0;
		padding: 2px 0 2px 16px;
		border-left: 2px solid #3a3a3a;
	}
	.thm.def {
		border-left-color: #222;
	}
	.head {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 4px 8px;
		margin-bottom: 6px;
	}
	.kind {
		font-weight: 600;
		color: var(--color-ink);
	}
	.name {
		color: var(--color-ink-2);
	}
	.ev {
		margin-left: auto;
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.ev::before {
		content: '';
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink-3);
	}
	.ev.proved::before,
	.ev.checked::before {
		background: var(--color-ink);
	}
	.ev.measured::before {
		background: transparent;
		box-shadow: inset 0 0 0 1.5px var(--color-ink-2);
	}
	.ev.open::before {
		background: transparent;
		box-shadow: inset 0 0 0 1px #555;
	}
	.body :global(p) {
		margin: 0 0 8px;
	}
	.body {
		font-style: normal;
		color: var(--color-ink);
	}
	.toggle {
		margin-top: 2px;
		padding: 0;
		border: 0;
		background: none;
		color: var(--color-ink-3);
		font: inherit;
		font-size: var(--text-xs);
		text-decoration: underline;
		text-underline-offset: 3px;
		cursor: pointer;
	}
	.toggle:hover {
		color: var(--color-ink);
	}
	.proof {
		margin-top: 8px;
		padding: 10px 14px 12px;
		border-radius: 6px;
		background: #0e0e0e;
		color: var(--color-ink-2);
	}
	.proof :global(p) {
		margin: 0 0 8px;
	}
	.qed {
		display: block;
		text-align: right;
		color: var(--color-ink-3);
	}
</style>
