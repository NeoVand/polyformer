/**
 * Read-outs of a probed cubic head, all in card coordinates: index 0 of a
 * slice is the first card (sequence position 1); BOS is reported separately.
 */
import type { ProbeResult } from '../engine/protocol.ts';
import { LAYOUT_SIZE } from '../set/cards.ts';

const C = LAYOUT_SIZE;

/** P[h, i, j, k] with i, j, k sequence positions. */
export function weight(p: ProbeResult, h: number, i: number, j: number, k: number): number {
	const n = p.n;
	return p.weights[((h * n + i) * n + j) * n + k];
}

/** The query slice P[i, :, :] over cards, row = role-1 card j, column = role-2 card k. */
export function querySlice(p: ProbeResult, h: number, card: number): Float32Array {
	const out = new Float32Array(C * C);
	for (let j = 0; j < C; j++)
		for (let k = 0; k < C; k++) out[j * C + k] = weight(p, h, card + 1, j + 1, k + 1);
	return out;
}

/** The whole tensor over cards, [i][j][k] flattened. */
export function cardTensor(p: ProbeResult, h: number): Float32Array {
	const out = new Float32Array(C * C * C);
	for (let i = 0; i < C; i++) out.set(querySlice(p, h, i), i * C * C);
	return out;
}

/** Weight the query sends to pairs that involve the BOS sink. */
export function sinkMass(p: ProbeResult, h: number, card: number): number {
	let s = 0;
	for (let t = 0; t < p.n; t++) {
		s += weight(p, h, card + 1, 0, t);
		if (t > 0) s += weight(p, h, card + 1, t, 0);
	}
	return s;
}

export interface Hyperedge {
	/** Role-1 and role-2 cards in the stronger orientation. */
	j: number;
	k: number;
	/** P_ijk + P_ikj. */
	weight: number;
	/** P_ijk in the stronger orientation. */
	ordered: number;
}

/** Unordered key pairs (never the query itself) ranked by total weight, each in its stronger orientation. */
export function topHyperedges(slice: Float32Array, count: number, query: number): Hyperedge[] {
	const out: Hyperedge[] = [];
	for (let a = 0; a < C; a++)
		for (let b = a + 1; b < C; b++) {
			if (a === query || b === query) continue;
			const ab = slice[a * C + b];
			const ba = slice[b * C + a];
			out.push(
				ab >= ba
					? { j: a, k: b, weight: ab + ba, ordered: ab }
					: { j: b, k: a, weight: ab + ba, ordered: ba }
			);
		}
	return out.sort((x, y) => y.weight - x.weight).slice(0, count);
}

/** One value row V[h, t, :] for sequence position t. */
export function valueRow(v: Float32Array, p: ProbeResult, h: number, t: number): Float32Array {
	const off = (h * p.n + t) * p.dh;
	return v.slice(off, off + p.dh);
}

/** Pair moment M_i = Σ_jk P_ijk V¹_j V²_kᵀ (dh × dh). Its diagonal is the head output Y_i. */
export function pairMoment(p: ProbeResult, h: number, card: number): Float32Array {
	const d = p.dh;
	const n = p.n;
	const m = new Float32Array(d * d);
	const i = card + 1;
	for (let j = 0; j < n; j++) {
		const v1 = valueRow(p.v1, p, h, j);
		for (let k = 0; k < n; k++) {
			const w = weight(p, h, i, j, k);
			if (w < 1e-7) continue;
			const v2 = valueRow(p.v2, p, h, k);
			for (let a = 0; a < d; a++) {
				const wa = w * v1[a];
				for (let b = 0; b < d; b++) m[a * d + b] += wa * v2[b];
			}
		}
	}
	return m;
}

/** Share of the query's weight on pairs that complete a true SET with it. */
export function setAlignment(slice: Float32Array, partners: [number, number][]): number {
	let s = 0;
	for (const [a, b] of partners) s += slice[a * C + b] + slice[b * C + a];
	return s;
}

/** For card i, the pairs (a, b) that complete a SET with it. */
export function setPartners(sets: [number, number, number][], card: number): [number, number][] {
	return sets
		.filter((s) => s.includes(card))
		.map((s) => s.filter((x) => x !== card) as [number, number]);
}
