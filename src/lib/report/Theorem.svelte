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
	<p class="head">
		<span class="kind">{kind}{n !== undefined ? ` ${n}` : ''}</span>
		{#if name}<span class="name">{name}</span>{/if}
		{#if evidence}<span class="ev {evidence}">{EVIDENCE_LABEL[evidence]}</span>{/if}
	</p>
	<div class="body">{@render children()}</div>
	{#if proof}
		<button class="toggle" aria-expanded={open} onclick={() => (open = !open)}>
			{open ? 'Hide the proof' : 'Proof'}
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
	/* no boxes or rules: the statement is set in full ink, the prose around it is not */
	.thm {
		position: relative;
		margin: 18px 0 20px;
	}
	.head {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 2px 10px;
		margin: 0 0 4px;
	}
	.kind {
		font-weight: 600;
		color: var(--color-ink);
	}
	.name {
		color: var(--color-ink-3);
	}
	.ev {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	/* in the margin when there is one */
	@media (min-width: 1180px) {
		.ev {
			position: absolute;
			top: 4px;
			left: calc(100% + 40px);
			width: 200px;
		}
	}
	.ev::before {
		content: '';
		flex: none;
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink);
	}
	.ev.measured::before {
		background: var(--color-ink-3);
	}
	.ev.open::before {
		background: #444;
	}
	.body {
		color: var(--color-ink);
	}
	.def .body {
		color: var(--color-ink-2);
	}
	.body :global(p) {
		margin: 0 0 8px;
	}
	.toggle {
		padding: 0;
		border: 0;
		background: none;
		color: var(--color-ink-3);
		font: inherit;
		font-size: var(--text-xs);
		font-style: italic;
		cursor: pointer;
	}
	.toggle:hover {
		color: var(--color-ink);
	}
	.proof {
		margin-top: 6px;
		padding-left: 18px;
		font-size: 14px;
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
