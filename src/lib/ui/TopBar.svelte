<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import Icon from './Icon.svelte';
	import { Chip } from './icons.ts';

	const bench = getBench();

	const nav = [
		{ label: 'Learn', href: resolve('/learn'), match: '/learn' },
		{ label: 'Explore', href: resolve('/explore'), match: '/explore' },
		{ label: 'Compare', href: resolve('/compare'), match: '/compare' },
		{ label: 'Notes', href: resolve('/notes'), match: '/notes' }
	];

	const titles: Record<string, string> = {
		'/learn': 'Learn / From pairs to triples',
		'/explore': 'Explore / Linked tensor lab',
		'/compare': 'Compare / SET bench',
		'/notes': 'Notes / Research log'
	};

	const route = $derived(page.route.id ?? '/');
	const crumb = $derived(titles[route] ?? '');
	const backend = $derived(
		bench.device === 'webgpu' ? 'WebGPU' : bench.device === 'wasm' ? 'WebAssembly' : bench.device
	);
</script>

<header class="bar">
	<div class="left">
		<a class="wordmark" href={resolve('/compare')}>polyformer</a>
		{#if crumb}
			<span class="sep" aria-hidden="true"></span>
			<span class="crumb">{crumb}</span>
		{/if}
	</div>

	<nav aria-label="Primary">
		{#each nav as item (item.href)}
			<a
				href={item.href}
				class={{ active: route.startsWith(item.match) }}
				aria-current={route.startsWith(item.match) ? 'page' : undefined}>{item.label}</a
			>
		{/each}
	</nav>

	<div class="right">
		<span class="engine" title="Where training runs: everything stays in this browser">
			<Icon icon={Chip} size={16} />
			{#if bench.device}
				<span class="num">{backend}</span>
				{#if bench.status === 'training'}
					<span class="live num">step {bench.step}</span>
				{/if}
			{:else if bench.status === 'booting'}
				<span>Starting…</span>
			{:else}
				<span class="muted">In-browser</span>
			{/if}
		</span>
	</div>
</header>

<style>
	.bar {
		position: sticky;
		top: 0;
		z-index: 20;
		height: var(--bar-h);
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		padding: 0 14px 0 16px;
		background: var(--color-void);
		border-bottom: 1px solid var(--color-edge);
	}
	.left {
		display: flex;
		align-items: center;
		gap: 14px;
		min-width: 0;
	}
	.wordmark {
		font-size: var(--text-lg);
		font-weight: 450;
		letter-spacing: -0.015em;
		color: var(--color-ink);
		text-decoration: none;
	}
	.sep {
		width: 1px;
		height: 16px;
		background: var(--color-rule);
	}
	.crumb {
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	nav {
		display: flex;
		height: 100%;
		gap: 4px;
	}
	nav a {
		position: relative;
		display: flex;
		align-items: center;
		padding: 0 14px;
		color: var(--color-ink-2);
		text-decoration: none;
		font-size: var(--text-ui);
		transition: color 120ms ease;
	}
	nav a:hover {
		color: var(--color-ink);
	}
	nav a.active {
		color: var(--color-ink);
		font-weight: 500;
	}
	nav a.active::after {
		content: '';
		position: absolute;
		left: 10px;
		right: 10px;
		bottom: -1px;
		height: 2px;
		background: var(--color-ink);
	}
	.right {
		display: flex;
		justify-content: flex-end;
	}
	.engine {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		height: 28px;
		padding: 0 10px;
		border: 1px solid var(--color-edge);
		border-radius: var(--radius-ui);
		color: var(--color-ink-2);
		font-size: var(--text-xs);
	}
	.engine .muted {
		color: var(--color-ink-3);
	}
	.live {
		color: var(--color-ink);
		padding-left: 8px;
		border-left: 1px solid var(--color-edge);
	}
	@media (max-width: 860px) {
		.crumb,
		.sep {
			display: none;
		}
	}
	@media (max-width: 640px) {
		.bar {
			grid-template-columns: auto 1fr;
			padding: 0 8px 0 12px;
		}
		.right {
			display: none;
		}
		nav {
			justify-content: flex-end;
			gap: 0;
		}
		nav a {
			padding: 0 8px;
			font-size: var(--text-sm);
		}
		nav a.active::after {
			left: 6px;
			right: 6px;
		}
	}
</style>
