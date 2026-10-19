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

export interface DspaHeadParams {
	u0: number[];
	w0: number[];
	uc: number[];
	wc: number[];
	/** [M][dh] */
	wm: Mat;
	/** [M][dh] */
	qm: Mat;
	/** [R][dh] */
	omega: Mat;
	/** Sector biases [leaf, hop, cubic, exchange, carry]. */
	mu: number[];
}

/**
 * Feynman attention for one head by definition, with explicit loops over every diagram.
 * Returns the RMS-normalised output [n][dh] and, per round, each token's
 * option weights in the operator's layout [leaf | hop j | cubic (j,k) | exchange (j,m) | carry].
 */
export function referenceDspa(
	q: Mat,
	u: Mat,
	w: Mat,
	vRaw: Mat,
	e: DspaHeadParams,
	R: number,
	M: number
): { y: Mat; rounds: number[][][] } {
	const n = q.length;
	const dh = q[0].length;
	const sc = 1 / Math.sqrt(dh);
	const tri = (a: number[], b: number[], c: number[]) =>
		a.reduce((s, x, i) => s + x * b[i] * c[i], 0);
	const softmax = (xs: number[]) => {
		const m = Math.max(...xs);
		const ex = xs.map((x) => (x === -Infinity ? 0 : Math.exp(x - m)));
		const z = ex.reduce((a, b) => a + b, 0);
		return ex.map((x) => x / z);
	};
	const leaf = vRaw.map((row) => row.map(Math.tanh));
	let phi = leaf;
	const rounds: number[][][] = [];
	for (let r = 0; r < R; r++) {
		const om = e.omega[r];
		// virtual modes
		const psi: Mat = [];
		for (let m = 0; m < M; m++) {
			const qmr = e.qm[m].map((x, c) => x * om[c]);
			const logits: number[] = [];
			for (let k = 0; k < n; k++)
				for (let l = 0; l < n; l++) logits.push(k === l ? -Infinity : tri(qmr, u[k], w[l]) * sc);
			const p = softmax(logits);
			const out = new Array<number>(dh).fill(0);
			for (let k = 0; k < n; k++)
				for (let l = 0; l < n; l++)
					for (let c = 0; c < dh; c++) out[c] += p[k * n + l] * phi[k][c] * phi[l][c];
			psi.push(out);
		}
		const next: Mat = [];
		const roundW: number[][] = [];
		for (let p = 0; p < n; p++) {
			const qr = q[p].map((x, c) => x * om[c]);
			const logits: number[] = [];
			const values: number[][] = [];
			logits.push(tri(qr, e.u0, e.w0) * sc + e.mu[0]);
			values.push(leaf[p]);
			for (let j = 0; j < n; j++) {
				logits.push(j === p ? -Infinity : tri(qr, u[j], e.w0) * sc + e.mu[1]);
				values.push(phi[j]);
			}
			for (let j = 0; j < n; j++)
				for (let k = 0; k < n; k++) {
					logits.push(tripleAllowed(p, j, k) ? tri(qr, u[j], w[k]) * sc + e.mu[2] : -Infinity);
					values.push(phi[j].map((x, c) => x * phi[k][c]));
				}
			for (let j = 0; j < n; j++)
				for (let m = 0; m < M; m++) {
					logits.push(j === p ? -Infinity : tri(qr, u[j], e.wm[m]) * sc + e.mu[3]);
					values.push(phi[j].map((x, c) => x * psi[m][c]));
				}
			logits.push(tri(qr, e.uc, e.wc) * sc + e.mu[4]);
			values.push(phi[p]);
			const wts = softmax(logits);
			roundW.push(wts);
			const out = new Array<number>(dh).fill(0);
			wts.forEach((wt, o) => {
				for (let c = 0; c < dh; c++) out[c] += wt * values[o][c];
			});
			next.push(out);
		}
		rounds.push(roundW);
		phi = next;
	}
	const y = phi.map((row) => {
		const rms = Math.sqrt(row.reduce((s, x) => s + x * x, 0) / dh + 1e-6);
		return row.map((x) => x / rms);
	});
	return { y, rounds };
}
