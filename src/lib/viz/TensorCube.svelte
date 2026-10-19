<script lang="ts">
	/**
	 * The attention tensor as a cube of blocks, one per (i, j, k), each sized by its
	 * value like a Hinton diagram. The query plane is drawn solid; strong cells on other
	 * planes appear as faint ghosts and weak ones are left out, so the cube stays
	 * legible. The selected cell is white and outlined.
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
		label = 'Attention tensor as a voxel cube',
		spin = 0
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
		/** Slow turntable rotation; 0 keeps the camera still. */
		spin?: number;
	} = $props();

	interface CubeApi {
		update(v: Float32Array | null, q: number, sel: { j: number; k: number } | null): void;
		setPlanes(p: { i?: boolean; j?: boolean; k?: boolean }): void;
		dispose(): void;
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
				// the box and its axis arrows stay in frame as the cube turns; the margin is for labels
				fitOrbit: {
					points: [
						[Math.SQRT2 * 0.5, 0.5],
						[Math.hypot(0.68, 0.56), 0.56],
						[Math.hypot(0.56, 0.74), 0.56],
						[Math.SQRT2 * 0.56, 0.68]
					],
					margin: 14
				},
				distance: [2.6, 7],
				// only the selected block's lit top face crosses the threshold
				bloom: { strength: 0.22, radius: 0.2, threshold: 0.93 },
				spin
			});
			api = build(stage);
		});
		return () => {
			disposed = true;
			api?.dispose();
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

		// ── frame: the outer box and a floor grid; the walls stay empty ───────────
		const line = (pts: number[], color: number, opacity = 1) => {
			const g = new THREE.BufferGeometry();
			g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
			return new THREE.LineSegments(
				g,
				new THREE.LineBasicMaterial({
					color,
					transparent: opacity < 1,
					opacity,
					depthWrite: opacity >= 1
				})
			);
		};
		scene.add(
			new THREE.LineSegments(
				new THREE.EdgesGeometry(new THREE.BoxGeometry(S, S, S)),
				new THREE.LineBasicMaterial({ color: 0x5c5c5c })
			)
		);
		const floor: number[] = [];
		for (let t = 1; t < n; t++) {
			const c = o + t * cell;
			floor.push(c, o, o, c, o, -o, o, o, c, -o, o, c);
		}
		scene.add(line(floor, 0x272727));

		// ── voxels: a 3D Hinton diagram, size by value ──────────────────────────
		// The query plane is solid and depth-tested, so it needs no sorting and cannot
		// pop as the camera turns. Strong cells elsewhere are faint additive ghosts,
		// which are order independent for the same reason.
		const faces = /* glsl */ `
			float shadeOf(vec3 n) { return n.y > 0.5 ? 1.0 : n.z > 0.5 ? 0.7 : n.x > 0.5 ? 0.48 : 0.34; }`;
		const vertexShader = /* glsl */ `
			attribute float aV;
			attribute float aF;
			attribute float aS;
			varying vec3 vP;
			varying vec3 vN;
			varying float vV;
			varying float vF;
			varying float vS;
			void main() {
				vP = position;
				vN = normal;
				vV = aV;
				vF = aF;
				vS = aS;
				gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);
			}`;
		const solidMat = new THREE.ShaderMaterial({
			vertexShader,
			fragmentShader: /* glsl */ `
				varying vec3 vP;
				varying vec3 vN;
				varying float vV;
				varying float vF;
				varying float vS;
				${faces}
				void main() {
					vec3 a = 0.5 - abs(vP);
					float lo = min(a.x, min(a.y, a.z));
					float hi = max(a.x, max(a.y, a.z));
					float mid = a.x + a.y + a.z - lo - hi;
					float w = fwidth(mid);
					// a soft bevel, antialiased in screen space, separates neighbouring blocks
					float bevel = 1.0 - smoothstep(0.07 - w, 0.07 + w, mid);
					float shade = shadeOf(vN);
					// both ease in and out: aF is how much the cell is in the selection's beam,
					// aS how much it is the selected cell
					float sel = vS;
					float beam = vF;
					float tone = 0.05 + 0.85 * vV * vV + 0.08 * beam;
					vec3 col = vec3(tone * shade * (1.0 - 0.35 * bevel));
					col = mix(col, vec3(1.08 * shade * (1.0 - 0.2 * bevel)), sel);
					gl_FragColor = vec4(col, 1.0);
				}`
		});
		const ghostMat = new THREE.ShaderMaterial({
			vertexShader,
			fragmentShader: /* glsl */ `
				varying vec3 vP;
				varying vec3 vN;
				varying float vV;
				varying float vF;
				${faces}
				void main() {
					// aF fades a ghost out while its cell grows into the query plane
					gl_FragColor = vec4(vec3(0.006 + 0.055 * vV) * shadeOf(vN) * vF, 1.0);
				}`,
			transparent: true,
			depthWrite: false,
			blending: THREE.AdditiveBlending
		});
		const voxelLayer = (mat: THREE_NS.ShaderMaterial, capacity: number) => {
			const g = new THREE.BoxGeometry(1, 1, 1);
			const v = new THREE.InstancedBufferAttribute(new Float32Array(capacity), 1);
			const f = new THREE.InstancedBufferAttribute(new Float32Array(capacity), 1);
			const sa = new THREE.InstancedBufferAttribute(new Float32Array(capacity), 1);
			g.setAttribute('aV', v);
			g.setAttribute('aF', f);
			g.setAttribute('aS', sa);
			const mesh = new THREE.InstancedMesh(g, mat, capacity);
			mesh.frustumCulled = false;
			mesh.count = 0;
			scene.add(mesh);
			/** The tensor cell drawn in each instance slot, for picking. */
			const cellOf = new Int32Array(capacity);
			return { mesh, v, f, s: sa, cellOf };
		};
		const solid = voxelLayer(solidMat, n * n);
		const ghost = voxelLayer(ghostMat, n * n * n);
		/** Off-plane cells weaker than this are not drawn at all. */
		const GHOST_FLOOR = 0.45;

		// ── the selection: a crisp outline instead of a glow ─────────────────────
		const ring = new THREE.LineSegments(
			new THREE.EdgesGeometry(new THREE.BoxGeometry(cell * 1.08, cell * 1.08, cell * 1.08)),
			new THREE.LineBasicMaterial({ color: 0xf2f2f2 })
		);
		scene.add(ring);

		// ── slice planes: an outline and a whisper of fill ──────────────────────
		const sheet = (axis: 'x' | 'y' | 'z') => {
			const h = (S * 1.04) / 2;
			const corners =
				axis === 'z'
					? [-h, -h, 0, h, -h, 0, h, h, 0, -h, h, 0]
					: axis === 'x'
						? [0, -h, -h, 0, -h, h, 0, h, h, 0, h, -h]
						: [-h, 0, -h, h, 0, -h, h, 0, h, -h, 0, h];
			const pts: number[] = [];
			for (let c = 0; c < 4; c++) {
				const d = (c + 1) % 4;
				pts.push(...corners.slice(c * 3, c * 3 + 3), ...corners.slice(d * 3, d * 3 + 3));
			}
			const fill = new THREE.Mesh(
				new THREE.PlaneGeometry(S * 1.04, S * 1.04),
				new THREE.MeshBasicMaterial({
					color: 0xffffff,
					transparent: true,
					opacity: 0.025,
					depthWrite: false,
					side: THREE.DoubleSide,
					blending: THREE.AdditiveBlending
				})
			);
			if (axis === 'x') fill.rotation.y = Math.PI / 2;
			if (axis === 'y') fill.rotation.x = -Math.PI / 2;
			const g = new THREE.Group();
			g.add(fill, line(pts, 0xbdbdbd, 0.7));
			scene.add(g);
			return g;
		};
		const slabI = sheet('z');
		const slabJ = sheet('x');
		const slabK = sheet('y');

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

		// ── eased state: each cell carries how much it is on the query plane, in the
		// selection's beam, and selected. A new query or pick tweens all of it at once,
		// from wherever it is, with one ease-in-out: the old plane sinks back into ghosts
		// while the new one rises out of them, and the slice and outline glide along.
		const N3 = n * n * n;
		const onPlane = new Float32Array(N3);
		const inBeam = new Float32Array(N3);
		const picked = new Float32Array(N3);
		/** The scores themselves, so a new set of values (scores, weights, a trained head) morphs too. */
		const value = new Float32Array(N3);
		const from = [
			new Float32Array(N3),
			new Float32Array(N3),
			new Float32Array(N3),
			new Float32Array(N3)
		];
		const goal = [
			new Float32Array(N3),
			new Float32Array(N3),
			new Float32Array(N3),
			new Float32Array(N3)
		];
		const slabAt = new THREE.Vector3();
		const ringAt = new THREE.Vector3();
		const slabFrom = new THREE.Vector3();
		const ringFrom = new THREE.Vector3();
		const slabGoal = new THREE.Vector3();
		const ringGoal = new THREE.Vector3();
		const DURATION = 850;
		const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		let primed = false;
		let raf = 0;
		let t0 = 0;
		const m4 = new THREE.Matrix4();
		const inOut = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

		/** Fix the targets for the current query and pick, starting from where things are now. */
		function aim() {
			const now = [onPlane, inBeam, picked, value];
			for (let i = 0; i < n; i++)
				for (let j = 0; j < n; j++)
					for (let k = 0; k < n; k++) {
						const idx = (i * n + j) * n + k;
						const mine = i === q;
						const both = mine && !!sel && j === sel.j && k === sel.k;
						const beam = mine && !!sel && !both && (j === sel.j || k === sel.k);
						goal[0][idx] = mine ? 1 : 0;
						goal[1][idx] = beam ? 1 : 0;
						goal[2][idx] = both ? 1 : 0;
						goal[3][idx] = current ? Math.max(0, Math.min(1, current[idx])) : 0;
						for (let g = 0; g < 4; g++) from[g][idx] = now[g][idx];
					}
			slabFrom.copy(slabAt);
			slabGoal.set(0, 0, centre(q));
			if (sel) {
				ringGoal.set(...at(q, sel.j, sel.k));
				ringFrom.copy(ring.visible ? ringAt : ringGoal);
			}
		}
		/** Place everything at progress `p` of the tween (1 = arrived). */
		function blend(p: number) {
			const e = inOut(p);
			const now = [onPlane, inBeam, picked, value];
			for (let g = 0; g < 4; g++)
				for (let idx = 0; idx < N3; idx++)
					now[g][idx] = from[g][idx] + (goal[g][idx] - from[g][idx]) * e;
			slabAt.lerpVectors(slabFrom, slabGoal, e);
			if (sel) ringAt.lerpVectors(ringFrom, ringGoal, e);
		}

		function draw() {
			let ns = 0;
			let ng = 0;
			for (let i = 0; i < n; i++)
				for (let j = 0; j < n; j++)
					for (let k = 0; k < n; k++) {
						const idx = (i * n + j) * n + k;
						const v = value[idx];
						const w = onPlane[idx];
						if (w > 0.002) {
							const side = cell * (0.1 + 0.8 * Math.pow(v, 0.7)) * w;
							m4.makeScale(side, side, side).setPosition(...at(i, j, k));
							solid.mesh.setMatrixAt(ns, m4);
							solid.v.array[ns] = v;
							solid.f.array[ns] = inBeam[idx];
							solid.s.array[ns] = picked[idx];
							solid.cellOf[ns++] = idx;
						}
						if (v > GHOST_FLOOR && w < 0.998) {
							const side = cell * (0.2 + 0.62 * Math.sqrt(v));
							m4.makeScale(side, side, side).setPosition(...at(i, j, k));
							ghost.mesh.setMatrixAt(ng, m4);
							ghost.v.array[ng] = v;
							ghost.f.array[ng] = 1 - w;
							ghost.cellOf[ng++] = idx;
						}
					}
			for (const [layer, count] of [
				[solid, ns],
				[ghost, ng]
			] as const) {
				layer.mesh.count = count;
				layer.mesh.instanceMatrix.needsUpdate = true;
				layer.v.needsUpdate = true;
				layer.f.needsUpdate = true;
				layer.s.needsUpdate = true;
				layer.mesh.computeBoundingSphere();
			}
			ring.visible = !!sel;
			ring.position.copy(ringAt);
			slabI.position.copy(slabAt);
			slabI.visible = !!shown.i;
			slabJ.visible = !!shown.j && !!sel;
			slabK.visible = !!shown.k && !!sel;
			if (sel) {
				slabJ.position.set(centre(sel.j), 0, 0);
				slabK.position.set(0, centre(sel.k), 0);
			}
			stage.invalidate();
		}

		function frame(t: number) {
			if (!t0) t0 = t;
			const p = Math.min(1, (t - t0) / DURATION);
			blend(p);
			draw();
			raf = p < 1 ? requestAnimationFrame(frame) : 0;
		}

		function refresh() {
			aim();
			if (!primed || reduced) {
				blend(1);
				draw();
				primed = true;
				return;
			}
			t0 = 0;
			if (!raf) raf = requestAnimationFrame(frame);
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
			for (const h of ray.intersectObjects([solid.mesh, ghost.mesh], false)) {
				const layer = h.object === solid.mesh ? solid : ghost;
				const id = h.instanceId === undefined ? -1 : layer.cellOf[h.instanceId];
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
			},
			dispose() {
				cancelAnimationFrame(raf);
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
			linear-gradient(
				to bottom,
				transparent,
				#000 var(--feather-top, 28px),
				#000 calc(100% - 28px),
				transparent
			);
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
