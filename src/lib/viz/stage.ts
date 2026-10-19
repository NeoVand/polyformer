/**
 * A small three.js stage shared by the 3D views: HDR rendering with ACES tone
 * mapping, an environment map for metallic and glass materials, and a bloom
 * pass with a high threshold so only super-bright elements (the selection)
 * glow. Rendering is on demand; a view calls `invalidate()` when it changes.
 */
import type * as THREE_NS from 'three';

export type Three = typeof THREE_NS;

export interface StageKit {
	THREE: Three;
	OrbitControls: typeof import('three/examples/jsm/controls/OrbitControls.js').OrbitControls;
	EffectComposer: typeof import('three/examples/jsm/postprocessing/EffectComposer.js').EffectComposer;
	RenderPass: typeof import('three/examples/jsm/postprocessing/RenderPass.js').RenderPass;
	UnrealBloomPass: typeof import('three/examples/jsm/postprocessing/UnrealBloomPass.js').UnrealBloomPass;
	OutputPass: typeof import('three/examples/jsm/postprocessing/OutputPass.js').OutputPass;
	RoomEnvironment: typeof import('three/examples/jsm/environments/RoomEnvironment.js').RoomEnvironment;
}

let kitPromise: Promise<StageKit> | null = null;

/** Load three.js and the examples once, lazily, so pages without 3D stay light. */
export function loadKit(): Promise<StageKit> {
	kitPromise ??= (async () => {
		const [THREE, oc, ec, rp, ub, op, re] = await Promise.all([
			import('three'),
			import('three/examples/jsm/controls/OrbitControls.js'),
			import('three/examples/jsm/postprocessing/EffectComposer.js'),
			import('three/examples/jsm/postprocessing/RenderPass.js'),
			import('three/examples/jsm/postprocessing/UnrealBloomPass.js'),
			import('three/examples/jsm/postprocessing/OutputPass.js'),
			import('three/examples/jsm/environments/RoomEnvironment.js')
		]);
		return {
			THREE,
			OrbitControls: oc.OrbitControls,
			EffectComposer: ec.EffectComposer,
			RenderPass: rp.RenderPass,
			UnrealBloomPass: ub.UnrealBloomPass,
			OutputPass: op.OutputPass,
			RoomEnvironment: re.RoomEnvironment
		};
	})();
	return kitPromise;
}

export interface StageOptions {
	/** Opaque background; the colour the page shows around the canvas (tone mapping is inverted). */
	background?: number;
	/** World half-extents [x, y] that must stay in view; the camera distance follows the aspect. */
	fit?: [number, number];
	fov?: number;
	position?: [number, number, number];
	target?: [number, number, number];
	distance?: [number, number];
	bloom?: { strength: number; radius: number; threshold: number };
	/** Gentle idle sway of the camera; disabled for reduced motion and once the user orbits. */
	sway?: boolean;
	environment?: boolean;
}

export interface Stage {
	kit: StageKit;
	THREE: Three;
	scene: THREE_NS.Scene;
	camera: THREE_NS.PerspectiveCamera;
	renderer: THREE_NS.WebGLRenderer;
	controls: InstanceType<StageKit['OrbitControls']>;
	host: HTMLElement;
	invalidate(): void;
	/** Called after each rendered frame (for projecting HTML labels). */
	onRender(cb: () => void): void;
	/** Called just before each rendered frame (for depth-sorting transparent instances). */
	beforeRender(cb: () => void): void;
	size(): { w: number; h: number };
	dispose(): void;
}

export function createStage(canvas: HTMLCanvasElement, kit: StageKit, opts: StageOptions = {}): Stage {
	const { THREE } = kit;
	const host = canvas.parentElement!;
	const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
	renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
	renderer.toneMapping = THREE.ACESFilmicToneMapping;
	renderer.toneMappingExposure = 1.0;
	renderer.outputColorSpace = THREE.SRGBColorSpace;

	const scene = new THREE.Scene();
	scene.background = toneMappedBackground(THREE, opts.background ?? 0x080808);

	let pmrem: THREE_NS.PMREMGenerator | null = null;
	if (opts.environment) {
		pmrem = new THREE.PMREMGenerator(renderer);
		scene.environment = pmrem.fromScene(new kit.RoomEnvironment(), 0.04).texture;
	}

	const camera = new THREE.PerspectiveCamera(opts.fov ?? 30, 1, 0.05, 100);
	camera.position.set(...(opts.position ?? [2.4, 1.6, 2.8]));
	const controls = new kit.OrbitControls(camera, renderer.domElement);
	controls.enableDamping = true;
	controls.dampingFactor = 0.1;
	controls.enablePan = false;
	controls.rotateSpeed = 0.7;
	controls.target.set(...(opts.target ?? [0, 0, 0]));
	if (opts.distance) [controls.minDistance, controls.maxDistance] = opts.distance;

	const composer = new kit.EffectComposer(renderer);
	composer.addPass(new kit.RenderPass(scene, camera));
	const b = opts.bloom ?? { strength: 0.9, radius: 0.55, threshold: 0.92 };
	const bloom = new kit.UnrealBloomPass(new THREE.Vector2(256, 256), b.strength, b.radius, b.threshold);
	composer.addPass(bloom);
	composer.addPass(new kit.OutputPass());

	let dirty = true;
	const listeners: (() => void)[] = [];
	const pre: (() => void)[] = [];
	const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	let swaying = !!opts.sway && !reduced;
	const base = camera.position.clone();
	const t0 = performance.now();
	controls.addEventListener('start', () => (swaying = false));
	controls.addEventListener('change', () => (dirty = true));

	const size = () => ({ w: host.clientWidth, h: host.clientHeight });
	const resize = () => {
		const { w, h } = size();
		// a hidden view reports 0×0; resizing the renderer and bloom targets to zero breaks them
		if (w < 2 || h < 2) return;
		renderer.setSize(w, h, false);
		composer.setSize(w, h);
		camera.aspect = w / Math.max(1, h);
		camera.updateProjectionMatrix();
		if (opts.fit) {
			const half = Math.tan(((camera.fov / 2) * Math.PI) / 180);
			const need = Math.max(opts.fit[1] / half, opts.fit[0] / (half * camera.aspect));
			const scale = need / base.distanceTo(controls.target);
			base.sub(controls.target).multiplyScalar(scale).add(controls.target);
			camera.position.sub(controls.target).multiplyScalar(scale).add(controls.target);
		}
		dirty = true;
	};
	const ro = new ResizeObserver(resize);
	ro.observe(host);
	resize();

	let raf = 0;
	const loop = () => {
		raf = requestAnimationFrame(loop);
		if (swaying) {
			const t = (performance.now() - t0) / 1000;
			const a = Math.sin(t * 0.25) * 0.12;
			const r = Math.hypot(base.x, base.z);
			const ang = Math.atan2(base.z, base.x) + a;
			camera.position.set(r * Math.cos(ang), base.y + Math.sin(t * 0.18) * 0.06, r * Math.sin(ang));
			camera.lookAt(controls.target);
			dirty = true;
		}
		controls.update();
		if (!dirty || host.clientWidth < 2 || host.clientHeight < 2) return;
		dirty = false;
		for (const cb of pre) cb();
		composer.render();
		for (const cb of listeners) cb();
	};
	loop();

	return {
		kit,
		THREE,
		scene,
		camera,
		renderer,
		controls,
		host,
		invalidate: () => (dirty = true),
		onRender: (cb) => listeners.push(cb),
		beforeRender: (cb) => pre.push(cb),
		size,
		dispose() {
			cancelAnimationFrame(raf);
			ro.disconnect();
			controls.dispose();
			scene.traverse((o) => {
				const mesh = o as THREE_NS.Mesh;
				mesh.geometry?.dispose();
				const mat = mesh.material as THREE_NS.Material | THREE_NS.Material[] | undefined;
				if (Array.isArray(mat)) mat.forEach((x) => x.dispose());
				else mat?.dispose();
			});
			scene.environment?.dispose();
			pmrem?.dispose();
			composer.dispose();
			renderer.dispose();
		}
	};
}

/**
 * ACES (as three.js applies it after the bloom pass) crushes dark greys, so an opaque
 * background set to the page colour renders visibly darker. Invert the curve per channel
 * so the canvas lands on exactly the CSS colour and the view has no visible edge.
 */
function toneMappedBackground(THREE: Three, hex: number): THREE_NS.Color {
	const fit = (v: number) =>
		(v * (v + 0.0245786) - 0.000090537) / (v * (0.983729 * v + 0.432951) + 0.238081);
	const invert = (target: number) => {
		let lo = 0;
		let hi = 4;
		for (let it = 0; it < 48; it++) {
			const mid = (lo + hi) / 2;
			if (fit(mid) < target) lo = mid;
			else hi = mid;
		}
		return lo * 0.6; // three.js scales by exposure / 0.6 before the fit
	};
	const c = new THREE.Color(hex); // sRGB hex → linear working space
	return new THREE.Color().setRGB(invert(c.r), invert(c.g), invert(c.b), THREE.LinearSRGBColorSpace);
}

/** Project a world point to pixel coordinates inside the stage's host element. */
export function project(stage: Stage, p: THREE_NS.Vector3): { x: number; y: number; behind: boolean } {
	const v = p.clone().project(stage.camera);
	const { w, h } = stage.size();
	return { x: ((v.x + 1) / 2) * w, y: ((1 - v.y) / 2) * h, behind: v.z > 1 };
}
