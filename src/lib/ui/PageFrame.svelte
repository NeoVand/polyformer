<script lang="ts" module>
	import type { IconData } from './icons.ts';

	export interface RailItem {
		id: string;
		label: string;
		icon: IconData;
	}
</script>

<script lang="ts">
	/**
	 * Page body: a 48px icon rail of in-page sections beside the content.
	 * The rail mirrors the page's own structure; it never lists unrelated tools.
	 */
	import type { Snippet } from 'svelte';
	import Icon from './Icon.svelte';

	let {
		rail,
		active,
		onselect,
		children
	}: {
		rail: RailItem[];
		active?: string;
		onselect?: (id: string) => void;
		children: Snippet;
	} = $props();
</script>

<div class="frame">
	<aside class="rail" aria-label="Sections">
		{#each rail as item (item.id)}
			<a
				href="#{item.id}"
				class={{ on: active === item.id }}
				title={item.label}
				aria-label={item.label}
				onclick={() => onselect?.(item.id)}
			>
				<Icon icon={item.icon} size={18} />
			</a>
		{/each}
	</aside>
	<main>
		{@render children()}
	</main>
</div>

<style>
	.frame {
		display: grid;
		grid-template-columns: var(--rail-w) minmax(0, 1fr);
		min-height: calc(100dvh - var(--bar-h));
	}
	.rail {
		position: sticky;
		top: var(--bar-h);
		height: calc(100dvh - var(--bar-h));
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6px;
		padding-top: 10px;
		border-right: 1px solid var(--color-edge);
		background: var(--color-void);
	}
	.rail a {
		display: grid;
		place-items: center;
		width: 34px;
		height: 34px;
		border-radius: var(--radius-ui);
		color: var(--color-ink-3);
		transition:
			color 120ms ease,
			background 120ms ease;
	}
	.rail a:hover {
		color: var(--color-ink);
		background: var(--color-panel);
	}
	.rail a.on {
		color: var(--color-ink);
		background: var(--color-control);
	}
	main {
		min-width: 0;
	}
	@media (max-width: 640px) {
		.frame {
			grid-template-columns: minmax(0, 1fr);
		}
		.rail {
			display: none;
		}
	}
</style>
