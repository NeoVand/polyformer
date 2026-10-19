/**
 * Turns raw Feynman attention weights into the compact diagram the UI draws. Pure
 * functions on Float32Arrays so they run in the worker and in tests.
 */
import { DSPA_SECTORS, optionLayout } from '../model/operators/dspa.ts';
import type { DiagramHead, DiagramMode, DiagramState, SectorMass } from './protocol.ts';

/** The `count` largest entries of `values[start, end)` as [offset, value], descending. */
function top(values: Float32Array, start: number, end: number, count: number): [number, number][] {
	const out: [number, number][] = [];
	for (let i = start; i < end; i++) {
		const v = values[i];
		if (out.length < count || v > out[out.length - 1][1]) {
			out.push([i - start, v]);
			out.sort((a, b) => b[1] - a[1]);
			if (out.length > count) out.pop();
		}
	}
	return out;
}

const sum = (values: Float32Array, start: number, end: number) => {
	let s = 0;
	for (let i = start; i < end; i++) s += values[i];
	return s;
};

/**
 * @param rounds per round, option weights [H, n, K] for one sequence
 * @param modes per round, mode pair weights [H, M, n·n] for one sequence
 */
export function summarizeDiagram(
	rounds: Float32Array[],
	modes: Float32Array[],
	H: number,
	n: number,
	M: number,
	token: number,
	topK = 4
): DiagramHead[] {
	const L = optionLayout(n, M);
	const K = L.size;
	const heads: DiagramHead[] = [];
	for (let h = 0; h < H; h++) {
		const states: DiagramState[] = [];
		const modeList: DiagramMode[] = [];
		rounds.forEach((W, r) => {
			for (let t = 0; t < n; t++) {
				const o = (h * n + t) * K;
				const bounds = [L.leaf, L.hop, L.cubic, L.exchange, L.carry, K];
				const sectors = Object.fromEntries(
					DSPA_SECTORS.map((name, i) => [name, sum(W, o + bounds[i], o + bounds[i + 1])])
				) as SectorMass;
				states.push({
					token: t,
					round: r + 1,
					sectors,
					hops: top(W, o + L.hop, o + L.cubic, topK).map(([j, weight]) => ({ j, weight })),
					cubic: top(W, o + L.cubic, o + L.exchange, topK).map(([jk, weight]) => ({
						j: Math.floor(jk / n),
						k: jk % n,
						weight
					})),
					exchanges: top(W, o + L.exchange, o + L.carry, topK).map(([jm, weight]) => ({
						j: Math.floor(jm / M),
						m: jm % M,
						weight
					}))
				});
			}
			const P = modes[r];
			for (let m = 0; m < M; m++) {
				const o = (h * M + m) * n * n;
				modeList.push({
					round: r + 1,
					m,
					pairs: top(P, o, o + n * n, topK).map(([kl, weight]) => ({
						k: Math.floor(kl / n),
						l: kl % n,
						weight
					}))
				});
			}
		});
		heads.push({
			head: h,
			query: rounds.map((_, r) => states[r * n + token]),
			states,
			modes: modeList
		});
	}
	return heads;
}
