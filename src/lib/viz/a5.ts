/** Computed A5 rotations, in the same element order as research/groups.py.
 * The standard four-dimensional action is restricted to self-dual two-forms.
 * No table of rotation matrices is hand-entered.
 */
export type Matrix3 = number[][];
export type Point3 = [number, number, number];
export interface A5Recording {
	selectedHead: number;
	homomorphismError: number;
	alignmentError: number;
	idealHomomorphismMaxError: number;
	vertices: Point3[];
	edges: [number, number][];
	multiplication: number[][];
	elements: {
		id: number;
		permutation: number[];
		class: number;
		ideal: Matrix3;
		learned: Matrix3;
		aligned: Matrix3;
	}[];
	training: { result: { bal_acc: number; steps: number; seed: number } };
}

export const identity: Matrix3 = [
	[1, 0, 0],
	[0, 1, 0],
	[0, 0, 1]
];
export function transpose(m: number[][]): number[][] {
	return m[0].map((_, i) => m.map((row) => row[i]));
}
export function multiply(a: number[][], b: number[][]): number[][] {
	return a.map((row) =>
		b[0].map((_, j) => row.reduce((sum, value, k) => sum + value * b[k][j], 0))
	);
}
export function apply(m: Matrix3, v: Point3): Point3 {
	return m.map((row) => row.reduce((sum, value, i) => sum + value * v[i], 0)) as Point3;
}
function permutations(items: number[]): number[][] {
	if (!items.length) return [[]];
	return items.flatMap((x) =>
		permutations(items.filter((y) => y !== x)).map((rest) => [x, ...rest])
	);
}
function even(p: number[]): boolean {
	let inversions = 0;
	for (let i = 0; i < p.length; i++)
		for (let j = i + 1; j < p.length; j++) if (p[i] > p[j]) inversions++;
	return inversions % 2 === 0;
}
export const elements = permutations([0, 1, 2, 3, 4]).filter(even);
const elementIndex = new Map(elements.map((p, i) => [p.join(''), i]));
export const multiplication = elements.map((a) =>
	elements.map((b) => elementIndex.get(b.map((x) => a[x]).join(''))!)
);

function makeRotations(): Matrix3[] {
	const basis = Array.from({ length: 5 }, () => Array<number>(4).fill(0));
	for (let j = 0; j < 4; j++) {
		for (let i = 0; i <= j; i++) basis[i][j] = 1 / Math.sqrt((j + 1) * (j + 2));
		basis[j + 1][j] = -(j + 1) / Math.sqrt((j + 1) * (j + 2));
	}
	const pairs = [
		[0, 1],
		[0, 2],
		[0, 3],
		[1, 2],
		[1, 3],
		[2, 3]
	];
	const b = [
		[1, 0, 0],
		[0, 1, 0],
		[0, 0, 1],
		[0, 0, 1],
		[0, -1, 0],
		[1, 0, 0]
	].map((row) => row.map((x) => x / Math.SQRT2));
	return elements.map((p) => {
		const permutation = Array.from({ length: 5 }, () => Array<number>(5).fill(0));
		p.forEach((to, from) => {
			permutation[to][from] = 1;
		});
		const standard = multiply(multiply(transpose(basis), permutation), basis);
		const wedge = pairs.map(([i, j]) =>
			pairs.map(([k, l]) => standard[i][k] * standard[j][l] - standard[i][l] * standard[j][k])
		);
		return multiply(multiply(transpose(b), wedge), b);
	});
}
export const idealRotations = makeRotations();

function normalize(v: Point3): Point3 {
	const length = Math.hypot(...v);
	return v.map((x) => x / length) as Point3;
}
function geometry() {
	const five = elements.findIndex((p) => {
		let x = 0;
		let count = 0;
		do {
			x = p[x];
			count++;
		} while (x !== 0);
		return count === 5;
	});
	const m = idealRotations[five];
	// The antisymmetric part of a rotation gives its axis.
	const axis = normalize([m[2][1] - m[1][2], m[0][2] - m[2][0], m[1][0] - m[0][1]]);
	const vertices: Point3[] = [];
	for (const rotation of idealRotations) {
		const v = apply(rotation, axis);
		if (!vertices.some((w) => Math.hypot(...v.map((x, i) => x - w[i])) < 1e-8)) vertices.push(v);
	}
	const distances = vertices.flatMap((a, i) =>
		vertices.slice(i + 1).map((b) => Math.hypot(...a.map((x, j) => x - b[j])))
	);
	const length = Math.min(...distances);
	const edges: [number, number][] = [];
	for (let i = 0; i < vertices.length; i++)
		for (let j = i + 1; j < vertices.length; j++) {
			if (Math.abs(Math.hypot(...vertices[i].map((x, k) => x - vertices[j][k])) - length) < 1e-8)
				edges.push([i, j]);
		}
	return { vertices, edges };
}
export const icosahedron = geometry();
export function facesFromEdges(edges: [number, number][]): [number, number, number][] {
	const set = new Set(edges.map(([a, b]) => `${Math.min(a, b)},${Math.max(a, b)}`));
	const count = Math.max(...edges.flat()) + 1;
	const faces: [number, number, number][] = [];
	for (let a = 0; a < count; a++)
		for (let b = a + 1; b < count; b++)
			for (let c = b + 1; c < count; c++) {
				if (set.has(`${a},${b}`) && set.has(`${a},${c}`) && set.has(`${b},${c}`))
					faces.push([a, b, c]);
			}
	return faces;
}
export function cycleLabel(p: number[]): string {
	const visited = new Set<number>();
	const cycles: string[] = [];
	for (let i = 0; i < p.length; i++) {
		if (visited.has(i)) continue;
		const cycle = [];
		let at = i;
		while (!visited.has(at)) {
			visited.add(at);
			cycle.push(at + 1);
			at = p[at];
		}
		if (cycle.length > 1) cycles.push(`(${cycle.join(' ')})`);
	}
	return cycles.join('') || 'identity';
}
