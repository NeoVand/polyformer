/**
 * dl_core.Engine._codebook, ported: the digital-state view. Each certified row's logits on the table's state names,
 * centred per vector (softmax ignores a common shift), on the rows' top three principal directions; a state's code is
 * the mean of the rows that write it; each tick's point is its own logits in the same view. The principal directions
 * come from a Jacobi eigendecomposition of the states × states scatter matrix (the right singular vectors numpy's SVD
 * gives, up to sign).
 */
import type { Xyz } from '../trace.ts';

export interface Codebook {
	names: string[];
	xyz: Xyz[];
	variance_kept: number;
	projection: string;
}

export const PROJECTION =
	"logits on the table's state names at the block's event position, centred per vector, on the certified rows' " +
	"top three principal directions; a state's code is the mean of the rows that write it, and each tick's point " +
	'is its own logits in the same view';

/** Eigenvalues (descending) and eigenvectors (columns of `vecs`, row-major n×n) of a symmetric matrix. */
export function symEig(a: Float64Array, n: number): { vals: number[]; vecs: Float64Array } {
	const A = Float64Array.from(a);
	const V = new Float64Array(n * n);
	for (let i = 0; i < n; i++) V[i * n + i] = 1;
	for (let sweep = 0; sweep < 100; sweep++) {
		let off = 0;
		for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += A[p * n + q] ** 2;
		if (off < 1e-22) break;
		for (let p = 0; p < n; p++)
			for (let q = p + 1; q < n; q++) {
				const apq = A[p * n + q];
				if (Math.abs(apq) < 1e-300) continue;
				const theta = (A[q * n + q] - A[p * n + p]) / (2 * apq);
				const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
				const c = 1 / Math.sqrt(t * t + 1);
				const s = t * c;
				for (let k = 0; k < n; k++) {
					const akp = A[k * n + p];
					const akq = A[k * n + q];
					A[k * n + p] = c * akp - s * akq;
					A[k * n + q] = s * akp + c * akq;
				}
				for (let k = 0; k < n; k++) {
					const apk = A[p * n + k];
					const aqk = A[q * n + k];
					A[p * n + k] = c * apk - s * aqk;
					A[q * n + k] = s * apk + c * aqk;
				}
				for (let k = 0; k < n; k++) {
					const vkp = V[k * n + p];
					const vkq = V[k * n + q];
					V[k * n + p] = c * vkp - s * vkq;
					V[k * n + q] = s * vkp + c * vkq;
				}
			}
	}
	const order = [...Array(n).keys()].sort((i, j) => A[j * n + j] - A[i * n + i]);
	const vecs = new Float64Array(n * n);
	order.forEach((src, dst) => {
		for (let k = 0; k < n; k++) vecs[k * n + dst] = V[k * n + src];
	});
	return { vals: order.map((i) => Math.max(0, A[i * n + i])), vecs };
}

const centred = (z: ArrayLike<number>) => {
	let m = 0;
	for (let i = 0; i < z.length; i++) m += z[i];
	m /= z.length || 1;
	return Array.from(z, (v) => v - m);
};

const r4 = (x: number) => Math.round(x * 1e4) / 1e4;

/**
 * The codebook from the certified rows' state logits (`rowsZ`, one vector of length S per row) and the index of
 * each row's argmax among the states (-1 when it is not a state). Returns the view and a projector for ticks.
 */
export function makeCodebook(
	names: string[],
	rowsZ: ArrayLike<number>[],
	rowsTIdx: number[]
): { codebook: Codebook; project: (z: ArrayLike<number>) => Xyz } {
	const S = names.length;
	const Z = rowsZ.map(centred);
	const R = Z.length;
	const mu = new Array(S).fill(0);
	for (const z of Z) for (let j = 0; j < S; j++) mu[j] += z[j] / R;
	const M = new Float64Array(S * S);
	for (const z of Z)
		for (let i = 0; i < S; i++) {
			const di = z[i] - mu[i];
			for (let j = 0; j < S; j++) M[i * S + j] += di * (z[j] - mu[j]);
		}
	const { vals, vecs } = symEig(M, S);
	const k = Math.min(3, Math.min(R, S));
	const P3: number[][] = [];
	for (let d = 0; d < 3; d++) {
		const col = new Array(S).fill(0);
		if (d < k) {
			for (let j = 0; j < S; j++) col[j] = vecs[j * S + d];
			// a fixed sign (numpy's is arbitrary too): the largest entry positive
			let big = 0;
			for (let j = 0; j < S; j++) if (Math.abs(col[j]) > Math.abs(big)) big = col[j];
			if (big < 0) for (let j = 0; j < S; j++) col[j] = -col[j];
		}
		P3.push(col);
	}
	const total = vals.reduce((a, b) => a + b, 0);
	const kept = vals.slice(0, k).reduce((a, b) => a + b, 0);
	const variance = kept / Math.max(total, 1e-12);
	const maxes = Z.map((z) => Math.max(...z)).sort((a, b) => a - b);
	const median = maxes.length
		? maxes.length % 2
			? maxes[(maxes.length - 1) / 2]
			: (maxes[maxes.length / 2 - 1] + maxes[maxes.length / 2]) / 2
		: 0;
	const codes = names.map((_, j) => {
		const mine = Z.filter((_, r) => rowsTIdx[r] === j);
		if (mine.length) {
			const c = new Array(S).fill(0);
			for (const z of mine) for (let i = 0; i < S; i++) c[i] += z[i] / mine.length;
			return c;
		}
		const v = new Array(S).fill(-1 / S);
		v[j] += 1;
		return v.map((x) => x * median);
	});
	const proj = (c: number[]): Xyz => {
		const out: Xyz = [0, 0, 0];
		for (let d = 0; d < 3; d++) {
			let s = 0;
			for (let j = 0; j < S; j++) s += (c[j] - mu[j]) * P3[d][j];
			out[d] = s;
		}
		return out;
	};
	const C = codes.map(proj);
	const scale = Math.max(...C.map((c) => Math.hypot(...c))) || 1;
	return {
		codebook: {
			names,
			xyz: C.map((c) => c.map((x) => r4(x / scale)) as Xyz),
			variance_kept: r4(variance),
			projection: PROJECTION
		},
		project: (z) => proj(centred(z)).map((x) => r4(x / scale)) as Xyz
	};
}
