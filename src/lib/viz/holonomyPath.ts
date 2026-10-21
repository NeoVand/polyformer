/**
 * The arithmetic behind the Holonomy lab's "carry a frame" figure. A token sequence is a list of
 * A5 elements, each with a 3 × 3 rotation. Holonomy attention's term for a group of tokens is the
 * product of their rotations in sequence order, which is the frame you get by walking along the
 * sequence and turning only at those tokens (choosing I skips a token, choosing M includes it).
 * The A5 task marks every token that belongs to an in-order triple whose product is the identity.
 */
import { mulberry32 } from '#lib/set/rng.ts';
import { identity, idealRotations, multiply, transpose, type Matrix3 } from './a5.ts';

const frobenius = (a: Matrix3, b: Matrix3) =>
	Math.hypot(...a.flatMap((row, i) => row.map((x, j) => x - b[i][j])));

/** The A5 element whose ideal rotation is the identity. */
export const IDENTITY = idealRotations.findIndex((m) => frobenius(m, identity) < 1e-9);

/** The index of the ideal rotation equal to m. */
function elementOf(m: Matrix3): number {
	let best = 0;
	let bestDistance = Infinity;
	idealRotations.forEach((r, i) => {
		const d = frobenius(r, m);
		if (d < bestDistance) {
			bestDistance = d;
			best = i;
		}
	});
	return best;
}

/** How far a rotation turns, in degrees: 0 for the identity, up to 180. */
export function turnDegrees(m: Matrix3): number {
	// atan2 of the antisymmetric and symmetric parts stays accurate near 0, where acos does not
	const c = (m[0][0] + m[1][1] + m[2][2] - 1) / 2;
	const s = Math.hypot(m[2][1] - m[1][2], m[0][2] - m[2][0], m[1][0] - m[0][1]) / 2;
	return (Math.atan2(s, c) * 180) / Math.PI;
}

/** The product of the chosen tokens' rotations, in sequence order. */
export function orderedProduct(rotations: Matrix3[], tokens: number[], chosen: number[]): Matrix3 {
	return [...chosen]
		.sort((a, b) => a - b)
		.reduce((frame, t) => multiply(frame, rotations[tokens[t]]), identity);
}

/** The frame after each position when it turns only at the chosen tokens. */
export function carriedFrames(rotations: Matrix3[], tokens: number[], chosen: number[]): Matrix3[] {
	const on = new Set(chosen);
	let frame = identity;
	return tokens.map((g, t) => (frame = on.has(t) ? multiply(frame, rotations[g]) : frame));
}

export interface Sequence {
	/** One A5 element per token. */
	tokens: number[];
	/** A planted in-order triple whose product is the identity. */
	planted: [number, number, number];
	/** Whether each token belongs to some in-order triple whose product is the identity. */
	inLoop: boolean[];
}

/** A sequence of non-identity elements with one planted identity triple. */
export function makeSequence(seed: number, n = 8): Sequence {
	const rng = mulberry32(seed);
	const pick = () => 1 + Math.floor(rng() * (idealRotations.length - 1));
	const positions = new Set<number>();
	while (positions.size < 3) positions.add(Math.floor(rng() * n));
	const planted = [...positions].sort((a, b) => a - b) as [number, number, number];
	let a = 0;
	let b = 0;
	let c = IDENTITY;
	while (c === IDENTITY) {
		a = pick();
		b = pick();
		c = elementOf(transpose(multiply(idealRotations[a], idealRotations[b])));
	}
	const tokens = Array.from({ length: n }, pick);
	[tokens[planted[0]], tokens[planted[1]], tokens[planted[2]]] = [a, b, c];
	const inLoop = tokens.map(() => false);
	for (let i = 0; i < n; i++)
		for (let j = i + 1; j < n; j++)
			for (let k = j + 1; k < n; k++)
				if (turnDegrees(orderedProduct(idealRotations, tokens, [i, j, k])) < 1e-4)
					inLoop[i] = inLoop[j] = inLoop[k] = true;
	return { tokens, planted, inLoop };
}

/** A fixed three-quarter view: screen x, screen y (down) and depth (towards the viewer). */
export function project([x, y, z]: number[]): { x: number; y: number; z: number } {
	const yaw = (-35 * Math.PI) / 180;
	const pitch = (22 * Math.PI) / 180;
	const x1 = Math.cos(yaw) * x + Math.sin(yaw) * z;
	const z1 = -Math.sin(yaw) * x + Math.cos(yaw) * z;
	const y2 = Math.cos(pitch) * y - Math.sin(pitch) * z1;
	const z2 = Math.sin(pitch) * y + Math.cos(pitch) * z1;
	return { x: x1, y: -y2, z: z2 };
}
