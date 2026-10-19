<script lang="ts">
	/**
	 * The layout as a luminous hypergraph: each card is a flat disc holding its glyph, every SET on the
	 * table is a faint glass membrane, the query's top hyperedges are brighter membranes
	 * weighted by attention, and the selected 2-simplex (i, j, k) glows. The query's disc
	 * is ringed in white, the two keys' in grey.
	 */
	import type * as THREE_NS from 'three';
	import type { Card } from '#lib/set/cards.ts';
	import SetCard from '#lib/ui/SetCard.svelte';
	import { createStage, loadKit, project, type Stage } from './stage.ts';

	export interface WeightedEdge {
		j: number;
		k: number;
		weight: number;
	}

	let {
		layout,
		query,
		edges,
		selected,
		sets = [],
		onquery,
		onedge,
		onanchor,
		background = 0x080808,
		showCards = true
	}: {
		layout: readonly Card[];
		query: number;
		/** The query's top hyperedges, weights in [0, 1]. */
		edges: WeightedEdge[];
		selected: { j: number; k: number } | null;
		/** Every SET on the table, drawn as faint membranes. */
		sets?: [number, number, number][];
		onquery?: (card: number) => void;
		onedge?: (edge: { j: number; k: number }) => void;
		/** Viewport position of the query node after each frame, for linking views. */
		onanchor?: (p: { x: number; y: number } | null) => void;
		background?: number;
		showCards?: boolean;
	} = $props();

	const N = $derived(layout.length);

	interface GraphApi {
		update(q: number, e: WeightedEdge[], sel: { j: number; k: number } | null, s: [number, number, number][]): void;
	}
	let api = $state.raw<GraphApi | null>(null);
	let nodes = $state<{ x: number; y: number; z: number; s: number }[]>([]);

	$effect(() => {
		const q = query;
		const e = edges;
		const sel = selected;
		const s = sets;
		api?.update(q, e, sel, s);
	});

	/** A fixed constellation: Fibonacci points on a flattened ellipsoid. */
	function positions(count: number): [number, number, number][] {
		const out: [number, number, number][] = [];
		const golden = Math.PI * (3 - Math.sqrt(5));
		for (let t = 0; t < count; t++) {
			const y = 1 - (2 * (t + 0.5)) / count;
			const r = Math.sqrt(1 - y * y);
			const a = t * golden + 0.6;
			out.push([Math.cos(a) * r * 1.25, y * 0.82, Math.sin(a) * r * 0.62]);
		}
		return out;
	}

	function graph(canvas: HTMLCanvasElement) {
		let stage: Stage | null = null;
		let disposed = false;
		loadKit().then((kit) => {
			if (disposed) return;
			stage = createStage(canvas, kit, {
				background,
				fov: 30,
				position: [0.35, 0.45, 4.1],
				fit: [1.42, 1.12],
				distance: [2.8, 7],
				bloom: { strength: 0.35, radius: 0.3, threshold: 0.97 },
				sway: true,
				environment: true
			});
			api = build(stage);
		});
		return () => {
			disposed = true;
			api = null;
			stage?.dispose();
		};
	}

	function build(stage: Stage): GraphApi {
		const { THREE, scene } = stage;
		const P = positions(N).map((p) => new THREE.Vector3(...p));
		// a faint crystal: every triangle of mutually-near cards becomes a glass facet
		const near: Record<string, true> = {};
		const pairKey = (a: number, b: number) => (a < b ? `${a}-${b}` : `${b}-${a}`);
		P.forEach((p, a) => {
			P.map((q, b) => ({ b, d: p.distanceTo(q) }))
				.filter((x) => x.b !== a)
				.sort((x, y) => x.d - y.d)
				.slice(0, 4)
				.forEach(({ b }) => (near[pairKey(a, b)] = true));
		});
		const facetPos: number[] = [];
		const facetBary: number[] = [];
		const linePos: number[] = [];
		for (const key of Object.keys(near)) {
			const [a, b] = key.split('-').map(Number);
			linePos.push(P[a].x, P[a].y, P[a].z, P[b].x, P[b].y, P[b].z);
		}
		for (let a = 0; a < N; a++)
			for (let b = a + 1; b < N; b++)
				for (let c = b + 1; c < N; c++)
					if (near[pairKey(a, b)] && near[pairKey(b, c)] && near[pairKey(a, c)]) {
						for (const t of [a, b, c]) facetPos.push(P[t].x, P[t].y, P[t].z);
						facetBary.push(1, 0, 0, 0, 1, 0, 0, 0, 1);
					}
		const facetGeo = new THREE.BufferGeometry();
		facetGeo.setAttribute('position', new THREE.Float32BufferAttribute(facetPos, 3));
		facetGeo.setAttribute('bary', new THREE.Float32BufferAttribute(facetBary, 3));
		scene.add(
			new THREE.Mesh(
				facetGeo,
				new THREE.ShaderMaterial({
					vertexShader: /* glsl */ `
						attribute vec3 bary;
						varying vec3 vB;
						varying vec3 vV;
						void main() {
							vB = bary;
							vec4 mv = modelViewMatrix * vec4(position, 1.0);
							vV = mv.xyz;
							gl_Position = projectionMatrix * mv;
						}`,
					fragmentShader: /* glsl */ `
						varying vec3 vB;
						varying vec3 vV;
						void main() {
							vec3 nrm = normalize(cross(dFdx(vV), dFdy(vV)));
							float fres = pow(1.0 - abs(dot(nrm, normalize(-vV))), 2.0);
							float e = 1.0 - smoothstep(0.0, 0.025, min(vB.x, min(vB.y, vB.z)));
							gl_FragColor = vec4(vec3(0.012 + 0.03 * fres + e * 0.05), 1.0);
						}`,
					transparent: true,
					depthWrite: false,
					blending: THREE.AdditiveBlending,
					side: THREE.DoubleSide
				})
			)
		);
		const lineGeo = new THREE.BufferGeometry();
		lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePos, 3));
		scene.add(
			new THREE.LineSegments(
				lineGeo,
				new THREE.LineBasicMaterial({ color: 0x5a5a5a, transparent: true, opacity: 0.35, depthWrite: false })
			)
		);

		// membranes: one triangle mesh per hyperedge, brighter toward the query vertex and along edges
		const memVert = /* glsl */ `
			attribute vec3 bary;
			varying vec3 vB;
			void main() {
				vB = bary;
				gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
			}`;
		const memFrag = /* glsl */ `
			uniform float uW;
			uniform float uSel;
			varying vec3 vB;
			void main() {
				float e = 1.0 - smoothstep(0.0, 0.03, min(vB.x, min(vB.y, vB.z)));
				float grad = 0.3 + 0.7 * vB.x;
				vec3 col = vec3(uW * 0.07 * grad + e * uW * 0.32) * (1.0 + uSel * 2.2);
				gl_FragColor = vec4(col, 1.0);
			}`;
		const bary = new Float32Array([1, 0, 0, 0, 1, 0, 0, 0, 1]);
		const membrane = () => {
			const g = new THREE.BufferGeometry();
			g.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(9), 3));
			g.setAttribute('bary', new THREE.Float32BufferAttribute(bary, 3));
			const mat = new THREE.ShaderMaterial({
				uniforms: { uW: { value: 0 }, uSel: { value: 0 } },
				vertexShader: memVert,
				fragmentShader: memFrag,
				transparent: true,
				depthWrite: false,
				blending: THREE.AdditiveBlending,
				side: THREE.DoubleSide
			});
			const m = new THREE.Mesh(g, mat);
			m.visible = false;
			scene.add(m);
			return m;
		};
		const pool = Array.from({ length: 24 }, membrane);
		const place = (m: THREE_NS.Mesh, a: number, b: number, c: number, w: number, sel: boolean) => {
			const pos = m.geometry.getAttribute('position') as THREE_NS.BufferAttribute;
			[a, b, c].forEach((t, v) => pos.setXYZ(v, P[t].x, P[t].y, P[t].z));
			pos.needsUpdate = true;
			m.geometry.computeBoundingSphere();
			const mat = m.material as THREE_NS.ShaderMaterial;
			mat.uniforms.uW.value = w;
			mat.uniforms.uSel.value = sel ? 1 : 0;
			m.userData = { j: b, k: c };
			m.visible = true;
		};

		const ray = new THREE.Raycaster();
		const ndc = new THREE.Vector2();
		let downAt: { x: number; y: number } | null = null;
		const el = stage.renderer.domElement;
		el.addEventListener('pointerdown', (e) => (downAt = { x: e.clientX, y: e.clientY }));
		el.addEventListener('pointerup', (e) => {
			if (!downAt) return;
			const moved = Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y);
			downAt = null;
			if (moved > 4) return;
			const r = el.getBoundingClientRect();
			ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
			ray.setFromCamera(ndc, stage.camera);
			const hitMem = ray.intersectObjects(pool.filter((m) => m.visible && m.userData.attn))[0];
			if (hitMem) onedge?.({ j: hitMem.object.userData.j, k: hitMem.object.userData.k });
		});

		stage.onRender(() => {
			const raw = P.map((p) => {
				const s = project(stage, p);
				return { x: s.x, y: s.y, z: p.clone().applyMatrix4(stage.camera.matrixWorldInverse).z, s: 1 };
			});
			// nearer cards draw a little larger, so the disc layer keeps the scene's depth
			const zs = raw.map((n) => n.z);
			const lo = Math.min(...zs);
			const span = Math.max(...zs) - lo || 1;
			for (const n of raw) n.s = 0.8 + 0.32 * ((n.z - lo) / span);
			nodes = raw;
			const qn = nodes[query];
			if (!onanchor || !qn) return;
			const r = stage.host.getBoundingClientRect();
			onanchor({ x: r.left + qn.x, y: r.top + qn.y });
		});

		return {
			update(q, e, sel, s) {
				pool.forEach((m) => {
					m.visible = false;
					m.userData = {};
				});
				let used = 0;
				for (const [a, b, c] of s) {
					if (used >= pool.length) break;
					place(pool[used++], a, b, c, 0.22, false);
				}
				for (const edge of e) {
					if (used >= pool.length) break;
					const isSel = !!sel && sel.j === edge.j && sel.k === edge.k;
					const m = pool[used++];
					place(m, q, edge.j, edge.k, 0.25 + 0.75 * edge.weight, isSel);
					m.userData.attn = true;
				}
				stage.invalidate();
			}
		};
	}

	const roleOf = (t: number) =>
		t === query ? 'query' : selected && t === selected.j ? 'role1' : selected && t === selected.k ? 'role2' : null;
</script>

<div class="graph">
	<canvas {@attach graph} aria-label="Hypergraph of the layout: cards as nodes, SETs and attention as membranes"></canvas>
	{#each nodes as p, t (t)}
		{@const role = roleOf(t)}
		<button
			class="node {role ?? ''}"
			style:left="{p.x}px"
			style:top="{p.y}px"
			style:--s={p.s}
			style:z-index={role ? 1000 : Math.round(100 + p.z * 10)}
			aria-label="Card {t + 1}{role ? `, ${role === 'query' ? 'query' : role === 'role1' ? 'role 1' : 'role 2'}` : ''}"
			onclick={() => onquery?.(t)}
		>
			{#if showCards && layout[t]}<SetCard card={layout[t]} width={24} />{/if}
			{#if role}
				<span class="role"
					><i>{role === 'query' ? 'i' : role === 'role1' ? 'j' : 'k'}</i><small
						>{role === 'query' ? 'query' : role === 'role1' ? 'role 1' : 'role 2'}</small
					></span
				>
			{/if}
		</button>
	{/each}
</div>

<style>
	.graph {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 260px;
		overflow: hidden;
		cursor: grab;
	}
	canvas {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		display: block;
		/* feather the edges so bloom haze dissolves into the page instead of showing a box */
		mask-image:
			linear-gradient(to right, transparent, #000 28px, #000 calc(100% - 28px), transparent),
			linear-gradient(to bottom, transparent, #000 28px, #000 calc(100% - 28px), transparent);
		mask-composite: intersect;
	}
	/* each card is a flat disc over the 3D edges, its glyph inside */
	.node {
		position: absolute;
		display: grid;
		place-items: center;
		width: 40px;
		height: 40px;
		padding: 0;
		border: 1px solid #2e2e2e;
		border-radius: 50%;
		background: #0e0e0e;
		transform: translate(-50%, -50%) scale(var(--s, 1));
		cursor: pointer;
		transition:
			border-color 160ms ease,
			box-shadow 160ms ease;
	}
	.node:hover {
		border-color: #5a5a5a;
	}
	.node:focus {
		outline: none;
	}
	.node:focus-visible {
		border-color: var(--color-ink);
	}
	.node.query {
		width: 48px;
		height: 48px;
		border: 1.5px solid var(--color-ink);
		box-shadow: 0 0 18px rgb(255 255 255 / 0.18);
	}
	.node.role1,
	.node.role2 {
		border: 1.25px solid var(--color-ink-2);
	}
	.role {
		position: absolute;
		left: calc(100% + 6px);
		top: 50%;
		transform: translateY(-50%);
		display: flex;
		align-items: baseline;
		gap: 4px;
		line-height: 1;
		white-space: nowrap;
		pointer-events: none;
		text-shadow:
			0 0 6px var(--color-void),
			0 0 2px var(--color-void);
	}
	.role i {
		font-family: var(--font-math);
		font-size: 17px;
		color: var(--color-ink);
	}
	.role small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
</style>
