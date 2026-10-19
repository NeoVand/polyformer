/**
 * An exact cubic head for SET, constructed by hand instead of trained.
 *
 * With θ = 2π/3 and card attributes a, b, c ∈ Z₃, the trilinear score
 *
 *   A_ijk = Σ_t cos θ(a_t + b_t + c_t)
 *
 * is 4 for every SET and at most 2.5 for every other triple. Each cosine expands
 * into four trilinear terms, cos(α+β+γ) = cα cβ cγ − cα sβ sγ − sα cβ sγ − sα sβ cγ,
 * so one cubic head with d_h = 16 computes it exactly: Q, K¹ and K² are those
 * cosine/sine features. The views use it so every panel shows a correct, sharp
 * state before any training has happened.
 */
import type { ProbeResult } from '../engine/protocol.ts';
import { ATTRS, LAYOUT_SIZE, type Card } from '../set/cards.ts';

export const EXACT_DH = 4 * ATTRS;
const TH = (2 * Math.PI) / 3;
/** Logit of the BOS sink pair: halfway between a SET (4) and the best non-SET (2.5). */
export const SINK_LOGIT = 3.25;

export interface ExactProbe extends ProbeResult {
	/** Raw trilinear scores A[i, j, k] over sequence positions; NaN where masked. */
	scores: Float32Array;
	/** Projections [n, d_h] for the single head. */
	q: Float32Array;
	k1: Float32Array;
	k2: Float32Array;
}

/** Cosine/sine features of every attribute, laid out as the four channel groups of the construction. */
function features(card: Card | null) {
	const c = new Float32Array(ATTRS);
	const s = new Float32Array(ATTRS);
	if (card)
		for (let t = 0; t < ATTRS; t++) {
			c[t] = Math.cos(TH * card[t]);
			s[t] = Math.sin(TH * card[t]);
		}
	const cat = (...parts: Float32Array[]) => {
		const out = new Float32Array(EXACT_DH);
		parts.forEach((p, g) => out.set(p, g * ATTRS));
		return out;
	};
	const neg = (x: Float32Array) => x.map((v) => -v);
	return {
		q: cat(c, neg(c), neg(s), neg(s)),
		k1: cat(c, s, c, s),
		k2: cat(c, s, s, c)
	};
}

/**
 * Probe the exact head on a layout. `beta` is the inverse temperature of the
 * joint softmax over ordered pairs (j, k): higher is sharper.
 */
export function exactProbe(layout: readonly Card[], beta = 3): ExactProbe {
	const n = LAYOUT_SIZE + 1;
	const d = EXACT_DH;
	const q = new Float32Array(n * d);
	const k1 = new Float32Array(n * d);
	const k2 = new Float32Array(n * d);
	const v1 = new Float32Array(n * d);
	const v2 = new Float32Array(n * d);
	for (let t = 0; t < n; t++) {
		const f = features(t === 0 ? null : layout[t - 1]);
		q.set(f.q, t * d);
		k1.set(f.k1, t * d);
		k2.set(f.k2, t * d);
		// values reuse the key features: V¹ ⊙ V² then holds second-order Fourier
		// features of the pair, from which a readout can recover their completion
		v1.set(f.k1, t * d);
		v2.set(f.k2, t * d);
	}

	const scores = new Float32Array(n * n * n).fill(NaN);
	const weights = new Float32Array(n * n * n);
	const probs = new Float32Array(LAYOUT_SIZE);
	const logits = new Float64Array(n * n);
	for (let i = 1; i < n; i++) {
		let max = -Infinity;
		logits.fill(-Infinity);
		for (let j = 0; j < n; j++)
			for (let k = 0; k < n; k++) {
				let a: number;
				if (j === 0 && k === 0) a = SINK_LOGIT;
				else if (j === 0 || k === 0 || j === i || k === i || j === k) continue;
				else {
					a = 0;
					for (let c = 0; c < d; c++) a += q[i * d + c] * k1[j * d + c] * k2[k * d + c];
				}
				scores[(i * n + j) * n + k] = a;
				logits[j * n + k] = beta * a;
				if (beta * a > max) max = beta * a;
			}
		let z = 0;
		for (let x = 0; x < n * n; x++) z += logits[x] === -Infinity ? 0 : Math.exp(logits[x] - max);
		for (let x = 0; x < n * n; x++)
			if (logits[x] !== -Infinity) weights[i * n * n + x] = Math.exp(logits[x] - max) / z;
		probs[i - 1] = 1 - weights[i * n * n]; // weight not on the sink pair
	}
	return { id: 'exact', step: 0, heads: 1, n, dh: d, weights, v1, v2, probs, scores, q, k1, k2 };
}

/** The 12 × 12 score slice A[i, :, :] over cards (row j, column k); NaN on masked cells. */
export function scoreSlice(p: ExactProbe, card: number): Float32Array {
	const n = p.n;
	const out = new Float32Array(LAYOUT_SIZE * LAYOUT_SIZE);
	for (let j = 0; j < LAYOUT_SIZE; j++)
		for (let k = 0; k < LAYOUT_SIZE; k++)
			out[j * LAYOUT_SIZE + k] = p.scores[((card + 1) * n + j + 1) * n + k + 1];
	return out;
}
