<script lang="ts">
	import { Matrix4, Quaternion, Vector3 } from 'three';
	import { cubicInOut } from 'svelte/easing';
	import { prefersReducedMotion, Tween } from 'svelte/motion';
	import {
		apply,
		facesFromEdges,
		icosahedron,
		idealRotations,
		type A5Recording,
		type Matrix3,
		type Point3
	} from './a5.ts';

	let {
		element = 1,
		model = 'ideal',
		recording,
		matrix,
		background = 0x080808,
		label = 'An icosahedron transformed by a three-dimensional rotation'
	}: {
		element?: number;
		model?: 'ideal' | 'recorded';
		recording?: A5Recording | null;
		matrix?: Matrix3;
		background?: number;
		label?: string;
	} = $props();

	const vertices = $derived(recording?.vertices ?? icosahedron.vertices);
	const faces = $derived(facesFromEdges(recording?.edges ?? icosahedron.edges));
	const selected = $derived(
		matrix ??
			(model === 'recorded' && recording
				? recording.elements[element].aligned
				: (recording?.elements[element].ideal ?? idealRotations[element]))
	);
	function quaternion(m: Matrix3) {
		return new Quaternion()
			.setFromRotationMatrix(
				new Matrix4().set(
					m[0][0],
					m[0][1],
					m[0][2],
					0,
					m[1][0],
					m[1][1],
					m[1][2],
					0,
					m[2][0],
					m[2][1],
					m[2][2],
					0,
					0,
					0,
					0,
					1
				)
			)
			.normalize();
	}
	function interpolate(a: Matrix3, b: Matrix3) {
		const from = quaternion(a);
		const to = quaternion(b);
		return (t: number): Matrix3 => {
			const e = new Matrix4().makeRotationFromQuaternion(from.clone().slerp(to, t)).elements;
			return [
				[e[0], e[4], e[8]],
				[e[1], e[5], e[9]],
				[e[2], e[6], e[10]]
			];
		};
	}
	const rotation = Tween.of(() => selected, {
		duration: () => (prefersReducedMotion.current ? 0 : 850),
		easing: cubicInOut,
		interpolate
	});
	// Fixed camera. Only the represented action moves; there is no idle camera sway.
	const camera = new Quaternion()
		.setFromAxisAngle(new Vector3(1, 0, 0), -0.23)
		.multiply(new Quaternion().setFromAxisAngle(new Vector3(0, 1, 0), 0.31));
	function project(point: Point3) {
		const v = new Vector3(...point).applyQuaternion(camera);
		const scale = 111 / (1 - v.z * 0.09);
		return { x: 160 + v.x * scale, y: 145 - v.y * scale, z: v.z };
	}
	const projected = $derived(vertices.map((v) => project(apply(rotation.current, v))));
	const orderedFaces = $derived(
		faces
			.map((ids) => ({
				id: ids.join('-'),
				points: ids.map((i) => `${projected[i].x},${projected[i].y}`).join(' '),
				depth: ids.reduce((sum, i) => sum + projected[i].z, 0) / 3
			}))
			.sort((a, b) => a.depth - b.depth)
	);
	const origin = $derived(project(vertices[0]));
	const tip = $derived(projected[0]);
	const dark = $derived(background < 0x808080);
	function surface(depth: number) {
		const shade = Math.round(dark ? 15 + (depth + 1) * 8 : 246 - (depth + 1) * 8);
		return `rgb(${shade},${shade},${shade})`;
	}
</script>

<svg viewBox="0 0 320 290" role="img" aria-label={label} class:light={!dark}>
	<ellipse cx="160" cy="274" rx="76" ry="2" class="ground" />
	{#each orderedFaces as face (face.id)}
		<polygon points={face.points} fill={surface(face.depth)} class="facet" />
	{/each}
	<line x1="160" y1="145" x2={origin.x} y2={origin.y} class="origin" />
	<circle cx={origin.x} cy={origin.y} r="4.5" class="start" />
	<line x1="160" y1="145" x2={tip.x} y2={tip.y} class="radius" />
	<circle cx="160" cy="145" r="2" class="centre" />
	<circle cx={tip.x} cy={tip.y} r="6" class="tip" />
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: 100%;
		overflow: visible;
		color: #f5f5f5;
	}
	svg.light {
		color: #171717;
	}
	.facet {
		stroke: currentColor;
		stroke-width: 0.75;
		stroke-opacity: 0.38;
		stroke-linejoin: round;
	}
	.ground {
		fill: currentColor;
		opacity: 0.08;
	}
	.origin {
		stroke: currentColor;
		stroke-width: 0.8;
		stroke-dasharray: 2.5 4;
		opacity: 0.35;
	}
	.radius {
		stroke: currentColor;
		stroke-width: 1.5;
	}
	.start {
		fill: none;
		stroke: currentColor;
		stroke-width: 1;
		opacity: 0.6;
	}
	.tip,
	.centre {
		fill: currentColor;
	}
</style>
