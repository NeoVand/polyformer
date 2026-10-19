<script lang="ts">
	/**
	 * The Polyformer mark: a small hypergraph. Two hyperedges share an edge, one a
	 * filled 2-simplex (a cubic interaction), the other a fainter neighbour, over four
	 * token nodes.
	 */
	let { size = 20 }: { size?: number } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" class="logo">
	<path d="M13 5 L28 10 L22 23 Z" class="face faint" />
	<path d="M13 5 L4.5 24.5 L22 23 Z" class="face" />
	<path d="M13 5 L4.5 24.5 L22 23 Z M13 5 L28 10 L22 23" class="edge" />
	<circle cx="13" cy="5" r="2.6" class="node" />
	<circle cx="4.5" cy="24.5" r="2.6" class="node" />
	<circle cx="22" cy="23" r="2.6" class="node" />
	<circle cx="28" cy="10" r="2.1" class="node dim" />
</svg>

<style>
	.logo {
		display: block;
		overflow: visible;
	}
	.face {
		fill: #f2f2f2;
		fill-opacity: 0.28;
	}
	.face.faint {
		fill-opacity: 0.08;
	}
	.edge {
		fill: none;
		stroke: #f2f2f2;
		stroke-width: 1.5;
		stroke-linejoin: round;
		stroke-opacity: 0.85;
	}
	.node {
		fill: #f2f2f2;
		stroke: var(--color-void);
		stroke-width: 1.4;
	}
	.node.dim {
		fill: #a6a6a6;
	}
</style>
