<script lang="ts">
	/**
	 * A translucent voxel cube of the attention tensor P[i, j, k] over cards.
	 * Voxels glow additively in proportion to their weight, so the volume reads
	 * like an X-ray: bright cells are where queries put their mass. The query
	 * plane and the selected voxel are outlined; everything else stays gray.
	 *
	 * Axes: j (role 1) → right, k (role 2) → up, i (query) → toward the viewer.
	 */
	import type * as THREE_NS from 'three';

	let {
		values,
		n,
		query,
		selected,
		onpick,
		label = 'Attention tensor P as a voxel cube'
	}: {
		/** Flattened [i][j][k], each query slice summing to ≤ 1. */
		values: Float32Array | null;
		n: number;
		query: number;
		selected: { j: number; k: number } | null;
		onpick?: (cell: { i: number; j: number; k: number }) => void;
		label?: string;
	} = $props();

	let labels = $state<{ id: string; text: string; x: number; y: number }[]>([]);
	interface CubeApi {
		setValues(v: Float32Array | null, query: number): void;
		setSelection(query: number, sel: { j: number; k: number } | null): void;
	}
	let api = $state.raw<CubeApi | null>(null);

	// sync props into the three.js scene (an external system)
	$effect(() => {
		const v = values;
		const q = query;
		api?.setValues(v, q);
	});
	$effect(() => {
		const q = query;
		const sel = selected;
		api?.setSelection(q, sel);
	});

	/** Attachment: builds the scene on the canvas once three.js has loaded; tears it down on unmount. */
	function cube(canvas: HTMLCanvasElement) {
		let disposed = false;
		let cleanup = () => {};
		(async () => {
			const THREE = await import('three');
			const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js');
			if (!disposed) cleanup = build(canvas, THREE, OrbitControls);
		})();
		return () => {
			disposed = true;
			cleanup();
		};
	}

	function build(
		canvas: HTMLCanvasElement,
		THREE: typeof THREE_NS,
		OrbitControls: typeof import('three/examples/jsm/controls/OrbitControls.js').OrbitControls
	) {
		const host = canvas.parentElement!;
		const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
		renderer.setClearColor(0x000000, 0);

		const scene = new THREE.Scene();
		const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
		camera.position.set(-1.75, 1.25, 2.6);

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.dampingFactor = 0.12;
		controls.enablePan = false;
		controls.minDistance = 2.2;
		controls.maxDistance = 6;
		controls.target.set(0, 0, 0);

		const S = 1; // cube side
		const cell = S / n;
		const origin = -S / 2;
		const centre = (t: number) => origin + (t + 0.5) * cell;

		// frame: outer edges plus faint back-plane grids
		const frame = new THREE.Group();
		const edgeMat = new THREE.LineBasicMaterial({
			color: 0x6a6a6a,
			transparent: true,
			opacity: 0.9
		});
		frame.add(
			new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(S, S, S)), edgeMat)
		);
		const gridMat = new THREE.LineBasicMaterial({
			color: 0x2a2a2a,
			transparent: true,
			opacity: 0.8
		});
		const gridPts: number[] = [];
		for (let t = 1; t < n; t++) {
			const c = origin + t * cell;
			// back plane z = origin (j–k grid)
			gridPts.push(c, origin, origin, c, -origin, origin, origin, c, origin, -origin, c, origin);
			// floor y = origin (j–i grid)
			gridPts.push(c, origin, origin, c, origin, -origin, origin, origin, c, -origin, origin, c);
			// side x = origin (k–i grid)
			gridPts.push(origin, c, origin, origin, c, -origin, origin, origin, c, origin, -origin, c);
		}
		const gridGeo = new THREE.BufferGeometry();
		gridGeo.setAttribute('position', new THREE.Float32BufferAttribute(gridPts, 3));
		frame.add(new THREE.LineSegments(gridGeo, gridMat));
		// the three near faces get a fainter grid, so the box reads as glass
		const glassGeo = gridGeo.clone();
		glassGeo.scale(-1, -1, -1);
		const glassMat = new THREE.LineBasicMaterial({
			color: 0x2a2a2a,
			transparent: true,
			opacity: 0.35,
			depthWrite: false
		});
		frame.add(new THREE.LineSegments(glassGeo, glassMat));
		scene.add(frame);

		// voxels: one instanced box per (i, j, k), additive so order never matters
		const box = new THREE.BoxGeometry(cell * 0.86, cell * 0.86, cell * 0.86);
		const voxMat = new THREE.MeshBasicMaterial({
			color: 0xffffff,
			transparent: true,
			blending: THREE.AdditiveBlending,
			depthWrite: false
		});
		const count = n * n * n;
		const voxels = new THREE.InstancedMesh(box, voxMat, count);
		const m4 = new THREE.Matrix4();
		const colour = new THREE.Color();
		for (let i = 0; i < n; i++)
			for (let j = 0; j < n; j++)
				for (let k = 0; k < n; k++) {
					const idx = (i * n + j) * n + k;
					m4.makeTranslation(centre(j), centre(k), -centre(i));
					voxels.setMatrixAt(idx, m4);
					voxels.setColorAt(idx, colour.setScalar(0));
				}
		voxels.instanceMatrix.needsUpdate = true;
		scene.add(voxels);

		// query plane: a faint slab at i
		const slabMat = new THREE.MeshBasicMaterial({
			color: 0xffffff,
			transparent: true,
			opacity: 0.05,
			blending: THREE.AdditiveBlending,
			depthWrite: false,
			side: THREE.DoubleSide
		});
		const slab = new THREE.Mesh(new THREE.BoxGeometry(S, S, cell), slabMat);
		const slabEdges = new THREE.LineSegments(
			new THREE.EdgesGeometry(new THREE.BoxGeometry(S, S, cell)),
			new THREE.LineBasicMaterial({ color: 0x9a9a9a, transparent: true, opacity: 0.7 })
		);
		scene.add(slab, slabEdges);

		// selected voxel: bright edges and a soft glow sprite
		const selEdges = new THREE.LineSegments(
			new THREE.EdgesGeometry(new THREE.BoxGeometry(cell, cell, cell)),
			new THREE.LineBasicMaterial({ color: 0xffffff })
		);
		const glowTex = (() => {
			const c = document.createElement('canvas');
			c.width = c.height = 64;
			const g = c.getContext('2d')!;
			const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
			grad.addColorStop(0, 'rgba(255,255,255,0.9)');
			grad.addColorStop(0.35, 'rgba(255,255,255,0.25)');
			grad.addColorStop(1, 'rgba(255,255,255,0)');
			g.fillStyle = grad;
			g.fillRect(0, 0, 64, 64);
			return new THREE.CanvasTexture(c);
		})();
		const glow = new THREE.Sprite(
			new THREE.SpriteMaterial({
				map: glowTex,
				blending: THREE.AdditiveBlending,
				depthWrite: false,
				transparent: true
			})
		);
		glow.scale.setScalar(cell * 3.2);
		scene.add(selEdges, glow);

		let current: Float32Array | null = null;
		let dirty = true;

		function setValues(v: Float32Array | null, q: number) {
			current = v;
			for (let idx = 0; idx < count; idx++) {
				const w = v ? v[idx] : 0;
				// absolute scale with a floor: a pair holding ≥ 30% of a query's weight is
				// full white and weights under 3% are dark, so a diffuse (untrained) tensor
				// reads as nearly empty instead of an additive white block
				const inPlane = Math.floor(idx / (n * n)) === q;
				const b = Math.min(1, Math.max(0, (w - 0.03) / 0.27)) * (inPlane ? 1 : 0.42);
				voxels.setColorAt(idx, colour.setScalar(b));
			}
			if (voxels.instanceColor) voxels.instanceColor.needsUpdate = true;
			dirty = true;
		}

		function setSelection(q: number, sel: { j: number; k: number } | null) {
			slab.position.set(0, 0, -centre(q));
			slabEdges.position.copy(slab.position);
			selEdges.visible = glow.visible = !!sel;
			if (sel) {
				selEdges.position.set(centre(sel.j), centre(sel.k), -centre(q));
				glow.position.copy(selEdges.position);
			}
			if (current) setValues(current, q);
			dirty = true;
		}

		// picking: along the ray, take the brightest voxel the ray passes through
		const ray = new THREE.Raycaster();
		const ndc = new THREE.Vector2();
		let downAt: { x: number; y: number } | null = null;
		const el = renderer.domElement;
		const onDown = (e: PointerEvent) => (downAt = { x: e.clientX, y: e.clientY });
		const onUp = (e: PointerEvent) => {
			if (!downAt || !current || !onpick) return;
			const moved = Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y);
			downAt = null;
			if (moved > 4) return; // it was a drag
			const r = el.getBoundingClientRect();
			ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
			ray.setFromCamera(ndc, camera);
			const hits = ray.intersectObject(voxels);
			let best = -1;
			let bestW = 0.01;
			for (const h of hits) {
				const id = h.instanceId ?? -1;
				if (id >= 0 && current[id] > bestW) {
					bestW = current[id];
					best = id;
				}
			}
			if (best >= 0)
				onpick({ i: Math.floor(best / (n * n)), j: Math.floor(best / n) % n, k: best % n });
		};
		el.addEventListener('pointerdown', onDown);
		el.addEventListener('pointerup', onUp);

		const resize = () => {
			const w = host.clientWidth;
			const h = host.clientHeight;
			renderer.setSize(w, h, false);
			camera.aspect = w / Math.max(1, h);
			camera.updateProjectionMatrix();
			dirty = true;
		};
		const ro = new ResizeObserver(resize);
		ro.observe(host);
		resize();
		controls.addEventListener('change', () => (dirty = true));

		const axisPoints = [
			{ id: 'j', text: 'j  role 1', p: new THREE.Vector3(S * 0.62, origin - 0.06, -origin + 0.04) },
			{ id: 'k', text: 'k  role 2', p: new THREE.Vector3(origin - 0.08, S * 0.6, -origin + 0.04) },
			{ id: 'i', text: 'i  query', p: new THREE.Vector3(origin - 0.08, origin - 0.06, 0) }
		];
		const projectLabels = () => {
			const w = host.clientWidth;
			const h = host.clientHeight;
			labels = axisPoints.map(({ id, text, p }) => {
				const v = p.clone().project(camera);
				return { id, text, x: ((v.x + 1) / 2) * w, y: ((1 - v.y) / 2) * h };
			});
		};

		let raf = 0;
		const loop = () => {
			raf = requestAnimationFrame(loop);
			controls.update();
			if (!dirty) return;
			dirty = false;
			renderer.render(scene, camera);
			projectLabels();
		};
		loop();

		api = { setValues, setSelection };

		return () => {
			cancelAnimationFrame(raf);
			ro.disconnect();
			el.removeEventListener('pointerdown', onDown);
			el.removeEventListener('pointerup', onUp);
			controls.dispose();
			scene.traverse((o) => {
				const mesh = o as THREE_NS.Mesh;
				mesh.geometry?.dispose();
				const mat = mesh.material as THREE_NS.Material | THREE_NS.Material[] | undefined;
				if (Array.isArray(mat)) mat.forEach((x) => x.dispose());
				else mat?.dispose();
			});
			glowTex.dispose();
			renderer.dispose();
			api = null;
		};
	}
</script>

<div class="cube" role="img" aria-label={label}>
	<canvas {@attach cube}></canvas>
	{#each labels as l (l.id)}
		<span class="axis" style:left="{l.x}px" style:top="{l.y}px">{l.text}</span>
	{/each}
</div>

<style>
	.cube {
		position: relative;
		width: 100%;
		height: 100%;
		min-height: 240px;
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
	}
	.axis {
		position: absolute;
		transform: translate(-50%, -50%);
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
		font-style: italic;
		white-space: nowrap;
		pointer-events: none;
	}
</style>
