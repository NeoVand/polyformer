/**
 * Data for the Learn page's live figures. Everything is computed, nothing is
 * drawn by hand: the barrier figure double-centres real score slices.
 */
import type { ExactProbe } from '#lib/explore/exact.ts';
import { gaussian, mulberry32 } from '#lib/set/rng.ts';

/** Remove row and column means: what is left is how j and k couple. */
export function doubleCentre(m: Float32Array, n: number): Float32Array {
	const row = new Float64Array(n);
	const col = new Float64Array(n);
	let all = 0;
	for (let j = 0; j < n; j++)
		for (let k = 0; k < n; k++) {
			const v = m[j * n + k];
			row[j] += v / n;
			col[k] += v / n;
			all += v / (n * n);
		}
	return m.map((v, idx) => v - row[Math.floor(idx / n)] - col[idx % n] + all);
}

/**
 * Double-centred (j, k) score slices for a few queries, for a degree-2 head with
 * random edge scores f(i,j) + g(j,k) + h(i,k) and for the exact cubic SET head.
 * The degree-2 slices come out identical; the cubic ones do not.
 */
export function barrierSlices(probe: ExactProbe, queries: number[], cards = 12) {
	const rng = mulberry32(17);
	const rand = () => Float32Array.from({ length: cards * cards }, () => gaussian(rng));
	const [f, g, h] = [rand(), rand(), rand()];
	const d = probe.dh;
	const degree2 = queries.map((i) =>
		doubleCentre(
			Float32Array.from({ length: cards * cards }, (_, idx) => {
				const j = Math.floor(idx / cards);
				const k = idx % cards;
				return f[i * cards + j] + g[j * cards + k] + h[i * cards + k];
			}),
			cards
		)
	);
	const cubic = queries.map((i) =>
		doubleCentre(
			Float32Array.from({ length: cards * cards }, (_, idx) => {
				const j = Math.floor(idx / cards) + 1;
				const k = (idx % cards) + 1;
				let s = 0;
				for (let c = 0; c < d; c++)
					s += probe.q[(i + 1) * d + c] * probe.k1[j * d + c] * probe.k2[k * d + c];
				return s;
			}),
			cards
		)
	);
	const spread = (ms: Float32Array[]) => {
		let max = 0;
		for (const m of ms) for (const v of m) max = Math.max(max, Math.abs(v));
		return max;
	};
	return { degree2, cubic, max2: spread(degree2), maxCubic: spread(cubic) };
}

/** Softmax of a few fixed scores: the pairwise figure's attention weights. */
export function softmax(scores: number[]): number[] {
	const m = Math.max(...scores);
	const e = scores.map((s) => Math.exp(s - m));
	const z = e.reduce((a, b) => a + b, 0);
	return e.map((x) => x / z);
}

/** Single-seed results from the research harness (1 layer, d = 64, 4 heads, 4k steps). */
export const ARITY_RESULTS = {
	tasks: [
		{ id: 'match3', label: 'SET: three cards sum to 0' },
		{ id: 'match4', label: 'Four cards sum to 0' }
	],
	models: [
		{ id: 'std', label: 'Standard, 3 layers' },
		{ id: 'strassen', label: 'Strassen' },
		{ id: 'cubic', label: 'Cubic' },
		{ id: 'quartic', label: 'Quartic' }
	],
	/** Token accuracy, or null where the pairing was not run. */
	accuracy: {
		match3: { std: 0.59, strassen: 0.92, cubic: 1, quartic: null },
		match4: { std: 0.63, strassen: 0.63, cubic: 0.63, quartic: 1 }
	} as Record<string, Record<string, number | null>>,
	/** Majority-class rate for four-card SET; three-card SET's is computed from the bench's eval set. */
	majority4: 0.63
};

/**
 * The hand-built head's score on every unordered triple of distinct cards in the
 * deck: A = Σ_t cos(2π(a_t + b_t + c_t)/3) = 4 − 1.5·m, where m is the number of
 * attributes that break the rule. Returns how many triples have each m.
 */
export function scoreDistribution(deck: readonly (readonly number[])[]) {
	const counts = [0, 0, 0, 0, 0];
	for (let i = 0; i < deck.length; i++)
		for (let j = i + 1; j < deck.length; j++)
			for (let k = j + 1; k < deck.length; k++) {
				let m = 0;
				for (let t = 0; t < 4; t++) if ((deck[i][t] + deck[j][t] + deck[k][t]) % 3 !== 0) m++;
				counts[m]++;
			}
	const total = counts.reduce((a, b) => a + b, 0);
	return counts.map((count, m) => ({ m, score: 4 - 1.5 * m, count, share: count / total }));
}

/** Approximate FLOPs for one attention head and layer: pairwise, cubic, and cubic over a window of w keys per role. */
export function costCurves(ns: number[], d = 64, w = 128) {
	return ns.map((n) => ({
		n,
		pairwise: 4 * n * n * d,
		cubic: 4 * n * n * n * d,
		windowed: 4 * n * Math.min(n, w) ** 2 * d
	}));
}

/**
 * How many options each Feynman attention sector offers token p, for a sequence of n tokens
 * and M virtual modes: one leaf, a hop to every other token, a cubic pair of two
 * distinct other tokens (plus the BOS sink pair), an exchange of every other token
 * with every mode, one carry. With equal logits a softmax gives each sector mass in
 * proportion to its size; the bias μ_s = −log(size) evens them out.
 */
export function sectorSizes(n: number, M: number) {
	return [
		{ id: 'leaf', label: 'Leaf', size: 1 },
		{ id: 'hop', label: 'Hop', size: n - 1 },
		{ id: 'cubic', label: 'Cubic', size: (n - 1) * (n - 2) + 1 },
		{ id: 'exchange', label: 'Exchange', size: (n - 1) * M },
		{ id: 'carry', label: 'Carry', size: 1 }
	];
}
