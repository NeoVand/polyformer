<script lang="ts">
	/**
	 * The Polyformer mark: a small hypergraph. Two hyperedges (2-simplices) share an
	 * edge over four token nodes, and attention moves between them: the lit face and
	 * its far node trade places with the other's, slowly, the way a cubic head's
	 * weight moves from one triple to another. Still under reduced motion.
	 */
	let { size = 20, live = true }: { size?: number; live?: boolean } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" class="logo" class:live>
	<path d="M13 5 L4.5 24.5 L22 23 Z" class="face a" />
	<path d="M13 5 L28 10 L22 23 Z" class="face b" />
	<path d="M13 5 L22 23" class="edge" />
	<path d="M13 5 L4.5 24.5 L22 23" class="edge a" />
	<path d="M13 5 L28 10 L22 23" class="edge b" />
	<circle cx="13" cy="5" r="2.6" class="node" />
	<circle cx="22" cy="23" r="2.6" class="node" />
	<circle cx="4.5" cy="24.5" r="2.6" class="node a" />
	<circle cx="28" cy="10" r="2.6" class="node b" />
</svg>

<style>
	.logo {
		display: block;
		overflow: visible;
		--period: 7s;
	}
	.face {
		fill: #f2f2f2;
	}
	.face.a {
		fill-opacity: 0.3;
	}
	.face.b {
		fill-opacity: 0.07;
	}
	.edge {
		fill: none;
		stroke: #f2f2f2;
		stroke-width: 1.5;
		stroke-linejoin: round;
		stroke-linecap: round;
		stroke-opacity: 0.9;
	}
	.edge.b {
		stroke-opacity: 0.4;
	}
	.node {
		fill: #f2f2f2;
		stroke: var(--color-void);
		stroke-width: 1.4;
	}
	.node.b {
		fill: #8c8c8c;
		r: 2.1px;
	}

	/* the lit hyperedge hands over to its neighbour and back */
	.live .face.a {
		animation: face-a var(--period) ease-in-out infinite;
	}
	.live .face.b {
		animation: face-b var(--period) ease-in-out infinite;
	}
	.live .edge.a {
		animation: edge-a var(--period) ease-in-out infinite;
	}
	.live .edge.b {
		animation: edge-b var(--period) ease-in-out infinite;
	}
	.live .node.a {
		animation: node-a var(--period) ease-in-out infinite;
	}
	.live .node.b {
		animation: node-b var(--period) ease-in-out infinite;
	}
	/* hovering the wordmark hurries the exchange along */
	:global(a:hover) > .live {
		--period: 2.4s;
	}
	@keyframes face-a {
		0%,
		38%,
		100% {
			fill-opacity: 0.3;
		}
		50%,
		88% {
			fill-opacity: 0.07;
		}
	}
	@keyframes face-b {
		0%,
		38%,
		100% {
			fill-opacity: 0.07;
		}
		50%,
		88% {
			fill-opacity: 0.3;
		}
	}
	@keyframes edge-a {
		0%,
		38%,
		100% {
			stroke-opacity: 0.9;
		}
		50%,
		88% {
			stroke-opacity: 0.4;
		}
	}
	@keyframes edge-b {
		0%,
		38%,
		100% {
			stroke-opacity: 0.4;
		}
		50%,
		88% {
			stroke-opacity: 0.9;
		}
	}
	@keyframes node-a {
		0%,
		38%,
		100% {
			fill: #f2f2f2;
			r: 2.6px;
		}
		50%,
		88% {
			fill: #8c8c8c;
			r: 2.1px;
		}
	}
	@keyframes node-b {
		0%,
		38%,
		100% {
			fill: #8c8c8c;
			r: 2.1px;
		}
		50%,
		88% {
			fill: #f2f2f2;
			r: 2.6px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.live * {
			animation: none !important;
		}
	}
</style>
