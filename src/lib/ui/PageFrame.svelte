<script lang="ts" module>
	import type { IconData } from './icons.ts';

	export interface RailItem {
		id: string;
		label: string;
		icon: IconData;
		/** A resolved link to another screen; in-page sections omit it. */
		href?: string;
	}
</script>

<script lang="ts">
	/**
	 * Page body: a labelled icon rail of in-page sections beside the content.
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
		<!-- eslint-disable svelte/no-navigation-without-resolve -- screen links arrive resolved; the rest are in-page anchors -->
		{#each rail as item (item.id)}
			{#if onselect && !item.href}
				<!-- a view switcher, not a place on the page -->
				<button
					class={{ item: true, on: active === item.id }}
					aria-pressed={active === item.id}
					onclick={() => onselect(item.id)}
				>
					<Icon icon={item.icon} size={20} />
					<span>{item.label}</span>
				</button>
			{:else}
				<a
					href={item.href ?? `#${item.id}`}
					class={{ item: true, on: active === item.id }}
					aria-current={active === item.id ? 'page' : undefined}
				>
					<Icon icon={item.icon} size={20} />
					<span>{item.label}</span>
				</a>
			{/if}
		{/each}
		<!-- eslint-enable svelte/no-navigation-without-resolve -->
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
		gap: 4px;
		padding-top: 12px;
		border-right: 1px solid #1a1a1a;
		background: var(--color-void);
	}
	.item {
		display: grid;
		place-items: center;
		gap: 6px;
		width: 64px;
		padding: 10px 0 9px;
		font-size: var(--text-2xs);
		text-align: center;
		line-height: 1;
		border: 0;
		border-radius: var(--radius-ui);
		background: transparent;
		color: var(--color-ink-3);
		cursor: pointer;
		transition:
			color 120ms ease,
			background 120ms ease;
	}
	.item:hover {
		color: var(--color-ink);
		background: var(--color-panel);
	}
	.item.on {
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
