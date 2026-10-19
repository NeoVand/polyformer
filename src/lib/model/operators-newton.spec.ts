import { beforeAll, describe, expect, it } from 'vitest';
import { defaultDevice, init, numpy as np } from '@jax-js/jax';
import { binomial, newton } from './operators/newton.ts';
import { gaussian, mulberry32 } from '../set/rng.ts';

const B = 2;
const H = 2;
const n = 6;
const dh = 3;
const K = 4;
const PHASE = 2;

const rng = mulberry32(1707);
const rand = (size: number, std = 1) =>
	Float32Array.from({ length: size }, () => gaussian(rng) * std);

beforeAll(async () => {
	await init();
	defaultDevice('cpu');
});

/** Every subset of `items` with `m` elements. */
function subsets(items: number[], m: number): number[][] {
	if (m === 0) return [[]];
	if (items.length < m) return [];
	const [first, ...rest] = items;
	return [...subsets(rest, m - 1).map((s) => [first, ...s]), ...subsets(rest, m)];
}

describe('Newton attention matches explicit sums over distinct subsets', () => {
	it('every arity, every query, through the shared read-out', () => {
		const th = rand(B * H * n * dh, 0.8);
		const g = rand(B * H * n * dh);
		const readout = rand(2 * dh * dh, 1 / Math.sqrt(2 * dh));
		const alpha = Float32Array.from({ length: K * dh }, () => 1 + 0.4 * gaussian(rng));

		const { y } = newton.attend(
			{ th: np.array(th).reshape([B, H, n, dh]), g: np.array(g).reshape([B, H, n, dh]) },
			{ B, H, n, dh },
			false,
			{
				extra: {
					readout: np.array(readout).reshape([2 * dh, dh]),
					alpha: np.array(alpha).reshape([K, dh])
				},
				options: { order: K }
			}
		);
		const got = y.dataSync();

		const at = (buf: Float32Array, b: number, h: number, t: number, c: number) =>
			buf[((b * H + h) * n + t) * dh + c];
		for (let b = 0; b < B; b++)
			for (let h = 0; h < H; h++)
				for (let q = 0; q < n; q++) {
					// φ_t per channel, as (re, im)
					const phi = (t: number, c: number) => {
						const gate = 1 / (1 + Math.exp(-at(g, b, h, t, c)));
						const a = PHASE * at(th, b, h, t, c);
						return [gate * Math.cos(a), gate * Math.sin(a)];
					};
					const others = Array.from({ length: n }, (_, t) => t).filter((t) => t !== q);
					const want = new Array(dh).fill(0);
					for (let m = 0; m < K; m++) {
						// Σ over m-subsets of the others of Π φ over the subset and the query
						const feat = new Array(2 * dh).fill(0);
						for (let c = 0; c < dh; c++) {
							let re = 0;
							let im = 0;
							for (const S of subsets(others, m)) {
								let [pr, pi] = phi(q, c);
								for (const t of S) {
									const [r2, i2] = phi(t, c);
									[pr, pi] = [pr * r2 - pi * i2, pr * i2 + pi * r2];
								}
								re += pr;
								im += pi;
							}
							feat[c] = re / binomial(n - 1, m);
							feat[dh + c] = im / binomial(n - 1, m);
						}
						const rms = Math.sqrt(feat.reduce((s, v) => s + v * v, 0) / (2 * dh) + 1e-6);
						for (let o = 0; o < dh; o++) {
							let acc = 0;
							for (let c = 0; c < 2 * dh; c++) acc += (feat[c] / rms) * readout[c * dh + o];
							want[o] += acc * alpha[m * dh + o];
						}
					}
					for (let o = 0; o < dh; o++)
						expect(got[((b * H + h) * n + q) * dh + o]).toBeCloseTo(want[o], 3);
				}
	});
});
