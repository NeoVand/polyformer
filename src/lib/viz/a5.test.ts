import { describe, expect, it } from 'vitest';
import recording from '../../../static/recorded/a5-irrep.json';
import {
	apply,
	facesFromEdges,
	icosahedron,
	idealRotations,
	multiplication,
	multiply
} from './a5.ts';

describe('computed A5 visualization', () => {
	it('preserves all 3,600 group products', () => {
		let error = 0;
		for (let a = 0; a < 60; a++) {
			for (let b = 0; b < 60; b++) {
				const product = multiply(idealRotations[a], idealRotations[b]);
				const target = idealRotations[multiplication[a][b]];
				for (let i = 0; i < 3; i++) {
					for (let j = 0; j < 3; j++)
						error = Math.max(error, Math.abs(product[i][j] - target[i][j]));
				}
			}
		}
		expect(error).toBeLessThan(1e-12);
	});

	it('constructs an icosahedron preserved by every ideal rotation', () => {
		expect(icosahedron.vertices).toHaveLength(12);
		expect(icosahedron.edges).toHaveLength(30);
		expect(facesFromEdges(icosahedron.edges)).toHaveLength(20);
		let error = 0;
		for (const matrix of idealRotations) {
			for (const vertex of icosahedron.vertices) {
				const moved = apply(matrix, vertex);
				const nearest = Math.min(
					...icosahedron.vertices.map((v) => Math.hypot(...v.map((x, i) => x - moved[i])))
				);
				error = Math.max(error, nearest);
			}
		}
		expect(error).toBeLessThan(1e-12);
	});

	it('ends at different marked vertices in the two displayed action orders', () => {
		const start = icosahedron.vertices[0];
		const ab = apply(multiply(idealRotations[12], idealRotations[1]), start);
		const ba = apply(multiply(idealRotations[1], idealRotations[12]), start);
		expect(Math.hypot(...ab.map((x, i) => x - ba[i]))).toBeGreaterThan(1);
		const recordedStart = recording.vertices[0] as [number, number, number];
		const a = recording.elements[1].ideal;
		const b = recording.elements[12].ideal;
		const recordedAB = apply(multiply(b, a), recordedStart);
		const recordedBA = apply(multiply(a, b), recordedStart);
		expect(Math.hypot(...recordedAB.map((x, i) => x - recordedBA[i]))).toBeGreaterThan(1);
	});
});
