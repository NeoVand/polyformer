/**
 * Brute-force triple-loop references for the attention operators, in plain
 * TypeScript. Used by tests to pin the GEMM formulations to the definitions.
 * Inputs are per-head matrices [n][dh].
 */
import { tripleAllowed } from './operators/triple.ts';

export type Mat = number[][];

const dot = (a: number[], b: number[]) => a.reduce((s, x, c) => s + x * b[c], 0);

export type TripleLogit = (q: number[], k1j: number[], k2k: number[]) => number;

export const referenceLogits = {
	cubic: (q: number[], a: number[], b: number[]) => {
		let s = 0;
		for (let c = 0; c < q.length; c++) s += q[c] * a[c] * b[c];
		return s;
	},
	tree: (q: number[], a: number[], b: number[]) => dot(q, a) + dot(a, b),
	strassen: (q: number[], a: number[], b: number[]) => dot(q, a) + dot(a, b) + dot(q, b)
} satisfies Record<string, TripleLogit>;

/** Triple attention by definition: Y_i = Σ_jk softmax_jk(A_ijk/√dh) (V¹_j ⊙ V²_k). Returns Y [n][dh] and P [n][n][n]. */
export function referenceTriple(
	logit: TripleLogit,
	q: Mat,
	k1: Mat,
	k2: Mat,
	v1: Mat,
	v2: Mat
): { y: Mat; p: number[][][] } {
	const n = q.length;
	const dh = q[0].length;
	const y: Mat = [];
	const p: number[][][] = [];
	for (let i = 0; i < n; i++) {
		const a: number[][] = [];
		let max = -Infinity;
		for (let j = 0; j < n; j++) {
			a.push([]);
			for (let k = 0; k < n; k++) {
				const s = tripleAllowed(i, j, k) ? logit(q[i], k1[j], k2[k]) / Math.sqrt(dh) : -Infinity;
				a[j].push(s);
				max = Math.max(max, s);
			}
		}
		let z = 0;
		for (let j = 0; j < n; j++) for (let k = 0; k < n; k++) z += Math.exp(a[j][k] - max);
		const yi = new Array<number>(dh).fill(0);
		const pi: number[][] = [];
		for (let j = 0; j < n; j++) {
			pi.push([]);
			for (let k = 0; k < n; k++) {
				const w = Math.exp(a[j][k] - max) / z;
				pi[j].push(w);
				for (let c = 0; c < dh; c++) yi[c] += w * v1[j][c] * v2[k][c];
			}
		}
		y.push(yi);
		p.push(pi);
	}
	return { y, p };
}

/** Standard attention by definition. */
export function referencePair(q: Mat, k: Mat, v: Mat): Mat {
	const n = q.length;
	const dh = q[0].length;
	return q.map((qi) => {
		const s = k.map((kj) => dot(qi, kj) / Math.sqrt(dh));
		const max = Math.max(...s);
		const e = s.map((x) => Math.exp(x - max));
		const z = e.reduce((a, b) => a + b, 0);
		const out = new Array<number>(dh).fill(0);
		for (let j = 0; j < n; j++) for (let c = 0; c < dh; c++) out[c] += (e[j] / z) * v[j][c];
		return out;
	});
}
