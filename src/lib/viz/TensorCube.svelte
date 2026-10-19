<script lang="ts">
	/**
	 * The attention tensor as a luminous glass cube: one instanced voxel per (i, j, k).
	 * A shader draws each cell's glass edges and fill in proportion to its value, the
	 * query plane and the selected cell's row and column are lit, and the selected
	 * voxel is rendered above white so the bloom pass catches only it.
	 *
	 * Axes: j (role 1) → right, k (role 2) → up, i (query) → toward the viewer.
	 */
	import type * as THREE_NS from 'three';
	import { createStage, loadKit, project, type Stage } from './stage.ts';

	let {
		values,
		n,
		query,
		selected,
		planes = { i: true, j: false, k: false },
		onpick,
		onanchor,
		background = 0x080808,
		label = 'Attention tensor as a voxel cube'
	}: {
		/** Intensities in [0, 1], flattened [i][j][k]. */
		values: Float32Array | null;
		n: number;
		query: number;
		selected: { j: number; k: number } | null;
		/** Which slice planes through the selected cell to show (tomography). */
		planes?: { i?: boolean; j?: boolean; k?: boolean };
		onpick?: (cell: { i: number; j: number; k: number }) => void;
		/** Viewport position of the selected voxel after each frame, for linking views. */
		onanchor?: (p: { x: number; y: number } | null) => void;
		background?: number;
		label?: string;
	} = $props();

	interface CubeApi {
		update(v: Float32Array | null, q: number, sel: { j: number; k: number } | null): void;
		setPlanes(p: { i?: boolean; j?: boolean; k?: boolean }): void;
	}
	let api = $state.raw<CubeApi | null>(null);
	let labels = $state<{ id: string; tex: string; sub: string; x: number; y: number }[]>([]);

	$effect(() => {
		const v = values;
		const q = query;
		const sel = selected;
		api?.update(v, q, sel);
	});
	$effect(() => {
		const p = planes;
		api?.setPlanes(p);
	});

	function cube(canvas: HTMLCanvasElement) {
		let stage: Stage | null = null;
		let disposed = false;
		loadKit().then((kit) => {
			if (disposed) return;
			stage = createStage(canvas, kit, {
				background,
				fov: 24,
				position: [3.05, 1.75, 3.45],
				fit: [0.98, 0.98],
				distance: [2.6, 7],
				bloom: { strength: 0.75, radius: 0.32, threshold: 0.88 },
				sway: true
			});
			api = build(stage);
		});
		return () => {
			disposed = true;
			api = null;
			stage?.dispose();
		};
	}

	function build(stage: Stage): CubeApi {
		const { THREE, scene } = stage;
		const S = 1;
		const cell = S / n;
		const o = -S / 2;
		const centre = (t: number) => o + (t + 0.5) * cell;
		// world position of voxel (i, j, k): j → x, k → y, i → z (toward viewer)
		const at = (i: number, j: number, k: number) => [centre(j), centre(k), centre(i)] as const;

		// ── frame: outer edges, faint back-plane grids, faint glass faces ──────────
		const line = (pts: number[], color: number, opacity: number) => {
			const g = new THREE.BufferGeometry();
			g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
			return new THREE.LineSegments(
				g,
				new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false })
			);
		};
		scene.add(
			new THREE.LineSegments(
				new THREE.EdgesGeometry(new THREE.BoxGeometry(S, S, S)),
				new THREE.LineBasicMaterial({ color: 0x9a9a9a, transparent: true, opacity: 0.85 })
			)
		);
		const grid: number[] = [];
		for (let t = 1; t < n; t++) {
			const c = o + t * cell;
			grid.push(c, o, o, c, -o, o, o, c, o, -o, c, o); // back wall z = o
			grid.push(c, o, o, c, o, -o, o, o, c, -o, o, c); // floor y = o
			grid.push(o, c, o, o, c, -o, o, o, c, o, -o, c); // left wall x = o
		}
		scene.add(line(grid, 0x343434, 0.55));
		const wallMat = new THREE.MeshBasicMaterial({
			color: 0xffffff,
			transparent: true,
			opacity: 0.025,
			depthWrite: false,
			side: THREE.DoubleSide
		});
		const wall = (w: THREE_NS.Mesh, f: (m: THREE_NS.Mesh) => void) => (f(w), scene.add(w));
		wall(new THREE.Mesh(new THREE.PlaneGeometry(S, S), wallMat), (m) => (m.position.z = o));
		wall(new THREE.Mesh(new THREE.PlaneGeometry(S, S), wallMat), (m) => {
			m.rotation.x = -Math.PI / 2;
			m.position.y = o;
		});
		wall(new THREE.Mesh(new THREE.PlaneGeometry(S, S), wallMat), (m) => {
			m.rotation.y = Math.PI / 2;
			m.position.x = o;
		});

		// ── voxels: glass blocks, depth-sorted back to front ────────────────────
		const shrink = 0.9;
		const box = new THREE.BoxGeometry(cell * shrink, cell * shrink, cell * shrink);
		const count = n * n * n;
		const aI = new THREE.InstancedBufferAttribute(new Float32Array(count), 1);
		const aF = new THREE.InstancedBufferAttribute(new Float32Array(count), 1);
		box.setAttribute('aI', aI);
		box.setAttribute('aF', aF);
		const mat = new THREE.ShaderMaterial({
			uniforms: { uEdge: { value: 0.06 } },
			vertexShader: /* glsl */ `
				attribute float aI;
				attribute float aF;
				varying vec3 vP;
				varying vec3 vN;
				varying float vI;
				varying float vF;
				void main() {
					vP = position / ${(cell * shrink).toFixed(6)};
					vN = normal;
					vI = aI;
					vF = aF;
					gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);
				}`,
			fragmentShader: /* glsl */ `
				uniform float uEdge;
				varying vec3 vP;
				varying vec3 vN;
				varying float vI;
				varying float vF;
				void main() {
					vec3 a = 0.5 - abs(vP);
					float lo = min(a.x, min(a.y, a.z));
					float hi = max(a.x, max(a.y, a.z));
					float mid = a.x + a.y + a.z - lo - hi;
					float edge = 1.0 - smoothstep(0.0, uEdge, mid);
					float plane = step(0.5, vF);
					float beam = step(1.5, vF);
					float sel = step(2.5, vF);
					// faces lit from above and in front, like frosted glass blocks
					float shade = vN.y > 0.5 ? 1.0 : vN.z > 0.5 ? 0.74 : vN.x > 0.5 ? 0.52 : 0.38;
					float body = (0.08 + 0.92 * vI) * shade;
					float rim = edge * (0.16 + 0.5 * vI + 0.2 * plane + 0.25 * beam);
					vec3 col = vec3(body + rim) * (1.0 + sel * 2.4);
					float alpha = 0.02 + 0.45 * vI + 0.05 * plane + 0.12 * beam + rim * 0.45 + sel;
					gl_FragColor = vec4(col, clamp(alpha, 0.0, 1.0));
				}`,
			transparent: true,
			depthWrite: false
		});
		const voxels = new THREE.InstancedMesh(box, mat, count);
		voxels.frustumCulled = false;
		scene.add(voxels);

		// logical state per cell; written to instance slots in back-to-front order
		const centres = new Float32Array(count * 3);
		for (let i = 0; i < n; i++)
			for (let j = 0; j < n; j++)
				for (let k = 0; k < n; k++) centres.set(at(i, j, k), ((i * n + j) * n + k) * 3);
		const cellI = new Float32Array(count);
		const cellF = new Float32Array(count);
		const order = Uint32Array.from({ length: count }, (_, t) => t);
		const depth = new Float32Array(count);
		const m4 = new THREE.Matrix4();
		const eye = new THREE.Vector3(Infinity, 0, 0);
		let unsorted = true;
		stage.beforeRender(() => {
			const cam = stage.camera.position;
			if (eye.distanceToSquared(cam) > 1e-6) {
				eye.copy(cam);
				for (let t = 0; t < count; t++) {
					const dx = centres[t * 3] - cam.x;
					const dy = centres[t * 3 + 1] - cam.y;
					const dz = centres[t * 3 + 2] - cam.z;
					depth[t] = dx * dx + dy * dy + dz * dz;
				}
				order.sort((x, y) => depth[y] - depth[x]);
				for (let slot = 0; slot < count; slot++) {
					const t = order[slot];
					m4.makeTranslation(centres[t * 3], centres[t * 3 + 1], centres[t * 3 + 2]);
					voxels.setMatrixAt(slot, m4);
				}
				voxels.instanceMatrix.needsUpdate = true;
				unsorted = true;
			}
			if (unsorted) {
				const I = aI.array as Float32Array;
				const F = aF.array as Float32Array;
				for (let slot = 0; slot < count; slot++) {
					I[slot] = cellI[order[slot]];
					F[slot] = cellF[order[slot]];
				}
				aI.needsUpdate = true;
				aF.needsUpdate = true;
				unsorted = false;
			}
		});

		// ── query slab and slice planes ──────────────────────────────────────────
		const slab = (sx: number, sy: number, sz: number) => {
			const g = new THREE.Group();
			g.add(
				new THREE.Mesh(
					new THREE.BoxGeometry(sx, sy, sz),
					new THREE.MeshBasicMaterial({
						color: 0xffffff,
						transparent: true,
						opacity: 0.06,
						depthWrite: false,
						blending: THREE.AdditiveBlending
					})
				),
				new THREE.LineSegments(
					new THREE.EdgesGeometry(new THREE.BoxGeometry(sx, sy, sz)),
					new THREE.LineBasicMaterial({ color: 0xd8d8d8, transparent: true, opacity: 0.75 })
				)
			);
			g.renderOrder = 1;
			scene.add(g);
			return g;
		};
		const slabI = slab(S * 1.02, S * 1.02, cell);
		const slabJ = slab(cell, S * 1.02, S * 1.02);
		const slabK = slab(S * 1.02, cell, S * 1.02);

		// ── axis arrows ──────────────────────────────────────────────────────────
		const arrowMat = new THREE.MeshBasicMaterial({ color: 0xe8e8e8 });
		const arrow = (from: [number, number, number], to: [number, number, number]) => {
			const a = new THREE.Vector3(...from);
			const b = new THREE.Vector3(...to);
			const dir = b.clone().sub(a);
			const len = dir.length();
			scene.add(line([...from, ...to], 0xe8e8e8, 0.9));
			const cone = new THREE.Mesh(new THREE.ConeGeometry(0.018, 0.06, 18), arrowMat);
			cone.position.copy(b);
			cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
			scene.add(cone);
			return len;
		};
		const pad = 0.06;
		arrow([o - pad, o - pad, -o + pad], [-o + 0.18, o - pad, -o + pad]); // j
		arrow([o - pad, o - pad, -o + pad], [o - pad, -o + 0.18, -o + pad]); // k
		arrow([o - pad, o - pad, o - pad], [o - pad, o - pad, -o + 0.24]); // i
		const labelAt = [
			{ id: 'j', tex: 'j', sub: 'role 1', p: new THREE.Vector3(-o + 0.27, o - pad, -o + pad) },
			{ id: 'k', tex: 'k', sub: 'role 2', p: new THREE.Vector3(o - pad, -o + 0.27, -o + pad) },
			{ id: 'i', tex: 'i', sub: 'query', p: new THREE.Vector3(o - pad, o - pad, -o + 0.34) }
		];
		const anchor = new THREE.Vector3();
		stage.onRender(() => {
			labels = labelAt.map(({ id, tex, sub, p }) => ({ id, tex, sub, ...project(stage, p) }));
			if (!onanchor) return;
			if (!sel) return onanchor(null);
			anchor.set(...at(q, sel.j, sel.k));
			const s = project(stage, anchor);
			const r = stage.host.getBoundingClientRect();
			onanchor(s.behind ? null : { x: r.left + s.x, y: r.top + s.y });
		});

		// ── state ────────────────────────────────────────────────────────────────
		let current: Float32Array | null = null;
		let q = 0;
		let sel: { j: number; k: number } | null = null;
		let shown = { i: true, j: false, k: false } as { i?: boolean; j?: boolean; k?: boolean };

		function refresh() {
			const I = cellI;
			const F = cellF;
			for (let i = 0; i < n; i++)
				for (let j = 0; j < n; j++)
					for (let k = 0; k < n; k++) {
						const idx = (i * n + j) * n + k;
						const v = current ? Math.max(0, Math.min(1, current[idx])) : 0;
						const inPlane = i === q;
						I[idx] = Math.pow(v, 0.8) * (inPlane ? 1 : 0.32);
						let f = inPlane ? 1 : 0;
						if (sel && inPlane && (j === sel.j || k === sel.k)) f = 2;
						if (sel && inPlane && j === sel.j && k === sel.k) f = 3;
						F[idx] = f;
					}
			unsorted = true;
			slabI.position.set(0, 0, centre(q));
			slabI.visible = !!shown.i;
			slabJ.visible = !!shown.j && !!sel;
			slabK.visible = !!shown.k && !!sel;
			if (sel) {
				slabJ.position.set(centre(sel.j), 0, 0);
				slabK.position.set(0, centre(sel.k), 0);
			}
			stage.invalidate();
		}

		// ── picking: the brightest voxel along the ray ───────────────────────────
		const ray = new THREE.Raycaster();
		const ndc = new THREE.Vector2();
		let downAt: { x: number; y: number } | null = null;
		const el = stage.renderer.domElement;
		el.addEventListener('pointerdown', (e) => (downAt = { x: e.clientX, y: e.clientY }));
		el.addEventListener('pointerup', (e) => {
			if (!downAt || !current || !onpick) return;
			const moved = Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y);
			downAt = null;
			if (moved > 4) return;
			const r = el.getBoundingClientRect();
			ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
			ray.setFromCamera(ndc, stage.camera);
			let best = -1;
			let bestV = 0.02;
			for (const h of ray.intersectObject(voxels)) {
				const id = h.instanceId === undefined ? -1 : order[h.instanceId];
				if (id >= 0 && current[id] > bestV) {
					bestV = current[id];
					best = id;
				}
			}
			if (best >= 0)
				onpick({ i: Math.floor(best / (n * n)), j: Math.floor(best / n) % n, k: best % n });
		});

		return {
			update(v, query, s) {
				current = v;
				q = query;
				sel = s;
				refresh();
			},
			setPlanes(p) {
				shown = p;
				refresh();
			}
		};
	}
</script>

<div class="cube" role="img" aria-label={label}>
	<canvas {@attach cube}></canvas>
	{#each labels as l (l.id)}
		<span class="axis" style:left="{l.x}px" style:top="{l.y}px"
			><i>{l.tex}</i><small>{l.sub}</small></span
		>
	{/each}
</div>

<style>
	.cube {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 260px;
		cursor: grab;
	}
	.cube:active {
		cursor: grabbing;
	}
	canvas {
		position: absolute;
		inset: 0;
		display: block;
		width: 100%;
		height: 100%;
		/* feather the edges so bloom haze dissolves into the page instead of showing a box */
		mask-image:
			linear-gradient(to right, transparent, #000 28px, #000 calc(100% - 28px), transparent),
			linear-gradient(to bottom, transparent, #000 28px, #000 calc(100% - 28px), transparent);
		mask-composite: intersect;
	}
	.axis {
		position: absolute;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1px;
		pointer-events: none;
		white-space: nowrap;
	}
	.axis i {
		font-family: var(--font-math);
		font-size: 20px;
		line-height: 1;
		color: var(--color-ink);
	}
	.axis small {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
</style>
