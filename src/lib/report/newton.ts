/**
 * Counting zero-sum k-tuples in the group algebra of G = Z_3^m, the way a
 * Hadamard-product attention layer could: in the Fourier (character) domain a
 * group convolution is a pointwise product, so every step below is either a
 * Hadamard product, a Hadamard power or a sum over tokens.
 *
 *   power sums        P_j = sum_t phi(x_t)^j                 (pool Hadamard powers)
 *   Newton's identities  r E_r = sum_{j=1}^r (-1)^{j-1} E_{r-j} P_j   (Hadamard products)
 *   readout           N_{i,k} = (1/Q) sum_c sum_{j<k} (-1)^j E_{k-1-j}(c) phi_c(x_i)^{j+1}
 *
 * where phi_c(x) = w^{<c,x>} is the character c of x and w = e^{2 pi i / 3}.
 * N_{i,k} is the number of (k-1)-subsets of the other tokens that sum with x_i
 * to zero, distinct positions only. Pure functions; complex numbers as (re, im).
 */

/** Cube roots of unity, w^0, w^1, w^2. */
const W_RE = [1, -0.5, -0.5];
const W_IM = [0, Math.sqrt(3) / 2, -Math.sqrt(3) / 2];

export type Element = readonly number[];

/** <c, x> mod 3 for every pair of group elements, indexed by base-3 digits. */
function dotTable(m: number): Uint8Array {
	const Q = 3 ** m;
	const digits = (v: number) => Array.from({ length: m }, (_, a) => Math.floor(v / 3 ** a) % 3);
	const D = Array.from({ length: Q }, (_, v) => digits(v));
	const out = new Uint8Array(Q * Q);
	for (let c = 0; c < Q; c++)
		for (let g = 0; g < Q; g++) {
			let s = 0;
			for (let a = 0; a < m; a++) s += D[c][a] * D[g][a];
			out[c * Q + g] = s % 3;
		}
	return out;
}

const index = (x: Element) => x.reduce((acc, v, a) => acc + (((v % 3) + 3) % 3) * 3 ** a, 0);

interface Vec {
	re: Float64Array;
	im: Float64Array;
}
const zeros = (Q: number): Vec => ({ re: new Float64Array(Q), im: new Float64Array(Q) });

/** Hadamard product of two complex vectors. */
function mul(a: Vec, b: Vec): Vec {
	const Q = a.re.length;
	const out = zeros(Q);
	for (let c = 0; c < Q; c++) {
		out.re[c] = a.re[c] * b.re[c] - a.im[c] * b.im[c];
		out.im[c] = a.re[c] * b.im[c] + a.im[c] * b.re[c];
	}
	return out;
}

/**
 * Witness counts N[i][k] for k = 2..K by Newton's identities in the Fourier domain.
 * Every intermediate is a Q-vector: power sums, elementary symmetric sums, readouts.
 */
export function newtonCounts(xs: readonly Element[], K: number): number[][] {
	const m = xs[0]?.length ?? 1;
	const Q = 3 ** m;
	const dot = dotTable(m);
	const ids = xs.map(index);

	// power sums: sum over tokens of the j-th Hadamard power of each token's character vector
	const P: Vec[] = [zeros(Q)];
	for (let j = 1; j <= K; j++) {
		const p = zeros(Q);
		for (const g of ids)
			for (let c = 0; c < Q; c++) {
				const e = (j * dot[c * Q + g]) % 3;
				p.re[c] += W_RE[e];
				p.im[c] += W_IM[e];
			}
		P.push(p);
	}

	// elementary symmetric sums by Newton's identities, all as Hadamard products
	const one = zeros(Q);
	one.re.fill(1);
	const E: Vec[] = [one];
	for (let r = 1; r < K; r++) {
		const acc = zeros(Q);
		for (let j = 1; j <= r; j++) {
			const t = mul(E[r - j], P[j]);
			const sign = j % 2 === 1 ? 1 : -1;
			for (let c = 0; c < Q; c++) {
				acc.re[c] += sign * t.re[c];
				acc.im[c] += sign * t.im[c];
			}
		}
		for (let c = 0; c < Q; c++) {
			acc.re[c] /= r;
			acc.im[c] /= r;
		}
		E.push(acc);
	}

	// readout: each token pairs the sums with its own character powers
	return ids.map((g) => {
		const row = Array.from({ length: K + 1 }, () => 0);
		for (let k = 2; k <= K; k++) {
			let total = 0;
			for (let j = 0; j < k; j++) {
				const e = E[k - 1 - j];
				let s = 0;
				for (let c = 0; c < Q; c++) {
					const p = ((j + 1) * dot[c * Q + g]) % 3;
					s += e.re[c] * W_RE[p] - e.im[c] * W_IM[p];
				}
				total += (j % 2 === 0 ? 1 : -1) * s;
			}
			row[k] = Math.round(total / Q) || 0; // no signed zeros
		}
		return row;
	});
}

/** The same counts by enumerating every (k-1)-subset: the reference. */
export function bruteCounts(xs: readonly Element[], K: number): number[][] {
	const n = xs.length;
	const m = xs[0]?.length ?? 1;
	return xs.map((x, i) => {
		const others = Array.from({ length: n }, (_, t) => t).filter((t) => t !== i);
		const row = Array.from({ length: K + 1 }, () => 0);
		const walk = (start: number, left: number, sum: number[], k: number) => {
			if (left === 0) {
				if (sum.every((v) => v % 3 === 0)) row[k] += 1;
				return;
			}
			for (let a = start; a < others.length; a++) {
				const t = others[a];
				walk(
					a + 1,
					left - 1,
					sum.map((v, d) => v + xs[t][d]),
					k
				);
			}
		};
		for (let k = 2; k <= K; k++)
			walk(
				0,
				k - 1,
				Array.from({ length: m }, (_, d) => x[d]),
				k
			);
		return row;
	});
}
