<script lang="ts">
	/** Key to the spacetime view's vertex glyphs, drawn exactly as the view draws them. */
	let { compact = false }: { compact?: boolean } = $props();
	const KEYS = [
		{ kind: 'hop', says: 'reads one token' },
		{ kind: 'cubic', says: 'reads two at once' },
		{ kind: 'exchange', says: 'via a virtual mode' },
		{ kind: 'leaf', says: 'its own value' },
		{ kind: 'carry', says: 'keeps its state' }
	] as const;
</script>

<ul class="legend" class:compact>
	{#each KEYS as k (k.kind)}
		<li>
			<svg width="16" height="10" viewBox="-8 -5 16 10" aria-hidden="true">
				{#if k.kind === 'hop'}
					<circle r="2.4" />
				{:else if k.kind === 'cubic'}
					<path d="M0,-3.2 L2.9,1.9 L-2.9,1.9 Z" />
				{:else if k.kind === 'exchange'}
					<circle r="2.5" class="ring" />
				{:else if k.kind === 'leaf'}
					<rect x="-2" y="-2" width="4" height="4" />
				{:else}
					<path d="M-7,0 H7" class="dash" />
				{/if}
			</svg>
			{k.says}
		</li>
	{/each}
	<li class="lit">
		<svg width="22" height="10" viewBox="0 -5 22 10" aria-hidden="true"
			><path d="M1,0 H21" class="line" /></svg
		>
		what the chosen token reads
	</li>
</ul>

<style>
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.legend.compact {
		gap: 3px 10px;
	}
	li {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		white-space: nowrap;
	}
	svg {
		display: block;
		fill: #f5f5f5;
	}
	.ring {
		fill: none;
		stroke: #f5f5f5;
		stroke-width: 1.1;
	}
	.dash {
		stroke: #bdbdbd;
		stroke-dasharray: 2 3;
	}
	.line {
		stroke: #f2f2f2;
		stroke-width: 1.8;
	}
</style>
