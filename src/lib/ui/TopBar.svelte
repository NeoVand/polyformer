<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { getBench } from '#lib/engine/bench.svelte.ts';
	import { connection } from '#lib/interpreter/connection.svelte.ts';
	import { savant } from '#lib/interpreter/webgpu/savant.svelte.ts';
	import Icon from './Icon.svelte';
	import Logo from './Logo.svelte';
	import { Book, Compare, Cube, Github } from './icons.ts';

	const sets = getBench('set');
	const chase = getBench('chase');

	const nav = [
		{ label: 'Paper', href: resolve('/paper'), match: '/paper', icon: Book },
		{ label: 'Explore', href: resolve('/explore'), match: '/explore', icon: Cube },
		{ label: 'Compare', href: resolve('/compare'), match: '/compare', icon: Compare }
	];

	const titles: Record<string, string> = {
		'/paper': 'Learning to compose',
		'/explore': 'Cubic attention',
		'/explore/diagrams': 'Feynman attention, a sum over diagrams',
		'/explore/newton': 'Newton attention',
		'/explore/groups': 'Learned rotations',
		'/compare': 'Bench',
		'/interpreter': 'Interpreter, replayed'
	};

	const route = $derived(page.route.id ?? '/');
	const crumb = $derived(
		route === '/interpreter' && savant.status === 'ready'
			? 'Interpreter, in your browser'
			: route === '/interpreter' && connection.live
				? 'Interpreter, live'
				: (titles[route] ?? '')
	);
	/** Shown only while a model trains, so the bar stays quiet otherwise. */
	const live = $derived(
		[sets, chase].find((b) => b.status === 'training' || b.status === 'pausing') ?? null
	);
</script>

<header class="bar">
	<div class="left">
		<a class="wordmark" href={resolve('/')}><Logo size={20} />polyformer</a>
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
				aria-current={route.startsWith(item.match) ? 'page' : undefined}
				><Icon icon={item.icon} size={16} />{item.label}</a
			>
		{/each}
	</nav>

	<div class="right">
		{#if live}
			<span class="live num"
				><i aria-hidden="true"></i>Training, step {live.step.toLocaleString('en-US')}</span
			>
		{/if}
		<a
			class="gh"
			href="https://github.com/NeoVand/polyformer"
			title="Source on GitHub"
			aria-label="Source on GitHub"><Icon icon={Github} size={18} /></a
		>
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
		padding: 0 16px 0 22px;
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
		display: inline-flex;
		align-items: center;
		gap: 9px;
		font-size: 17px;
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
		font-size: var(--text-sm);
		color: var(--color-ink-3);
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
		gap: 7px;
		padding: 0 14px;
		color: var(--color-ink-3);
		text-decoration: none;
		font-size: var(--text-ui);
		transition: color 120ms ease;
	}
	nav a:hover {
		color: var(--color-ink);
	}
	nav a :global(svg) {
		opacity: 0.85;
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
		align-items: center;
		justify-content: flex-end;
		gap: 16px;
	}
	.gh {
		display: grid;
		place-items: center;
		width: 30px;
		height: 30px;
		border-radius: var(--radius-ui);
		color: var(--color-ink-3);
		transition:
			color 120ms ease,
			background 120ms ease;
	}
	.gh:hover {
		color: var(--color-ink);
		background: var(--color-panel);
	}
	.live {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
	}
	.live i {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink);
		animation: pulse 1.6s ease-in-out infinite;
	}
	@keyframes pulse {
		50% {
			opacity: 0.25;
		}
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
	/* phones: labels alone, so the four links fit beside the wordmark */
	@media (max-width: 480px) {
		nav a {
			padding: 0 6px;
		}
		nav a :global(svg.icon) {
			display: none;
		}
	}
</style>
