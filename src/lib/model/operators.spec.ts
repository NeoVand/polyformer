import { beforeAll, describe, expect, it } from 'vitest';
import { defaultDevice, init, numpy as np, type Array as Tensor } from '@jax-js/jax';
import { OPERATORS } from './operators/index.ts';
import { tripleAllowed } from './operators/triple.ts';
import { referenceLogits, referencePair, referenceTriple, type Mat } from './reference.ts';
import { gaussian, mulberry32 } from '../set/rng.ts';

const B = 2;
const H = 2;
const n = 6;
const dh = 4;

function randomHeads(seed: number): Float32Array<ArrayBuffer> {
	const rng = mulberry32(seed);
	return Float32Array.from({ length: B * H * n * dh }, () => gaussian(rng));
}

const toTensor = (buf: Float32Array<ArrayBuffer>) => np.array(buf).reshape([B, H, n, dh]);

/** Slice one (batch, head) of a flat [B, H, n, dh] buffer as a matrix. */
function head(buf: Float32Array, b: number, h: number): Mat {
	const off = (b * H + h) * n * dh;
	return Array.from({ length: n }, (_, i) =>
		Array.from(buf.subarray(off + i * dh, off + (i + 1) * dh))
	);
}

function maxAbsDiff(got: Float32Array, b: number, h: number, want: Mat): number {
	let d = 0;
	const off = (b * H + h) * n * dh;
	for (let i = 0; i < n; i++)
		for (let c = 0; c < dh; c++) d = Math.max(d, Math.abs(got[off + i * dh + c] - want[i][c]));
	return d;
}

beforeAll(async () => {
	await init();
	defaultDevice('cpu');
});

describe('triple attention operators match a brute-force triple loop', () => {
	for (const id of ['cubic', 'tree', 'strassen'] as const) {
		it(`${id}: outputs and normalised weights`, () => {
			const names = ['q', 'k1', 'k2', 'v1', 'v2'];
			const bufs = Object.fromEntries(names.map((name, i) => [name, randomHeads(100 + i)]));
			const inputs: Record<string, Tensor> = Object.fromEntries(
				names.map((name) => [name, toTensor(bufs[name])])
			);
			const r = OPERATORS[id].attend(inputs, { B, H, n, dh }, true);
			const y = r.y.dataSync() as Float32Array;
			const w = r.weights!.dataSync() as Float32Array;
			r.values!.forEach((v) => v.dispose());

			for (let b = 0; b < B; b++) {
				for (let h = 0; h < H; h++) {
					const ref = referenceTriple(
						referenceLogits[id],
						head(bufs.q, b, h),
						head(bufs.k1, b, h),
						head(bufs.k2, b, h),
						head(bufs.v1, b, h),
						head(bufs.v2, b, h)
					);
					expect(maxAbsDiff(y, b, h, ref.y)).toBeLessThan(1e-4);
					const off = (b * H + h) * n * n * n;
					for (let i = 0; i < n; i++)
						for (let j = 0; j < n; j++)
							for (let k = 0; k < n; k++) {
								const got = w[off + i * n * n + j * n + k];
								expect(Math.abs(got - ref.p[i][j][k])).toBeLessThan(1e-5);
								if (!tripleAllowed(i, j, k)) expect(got).toBe(0);
							}
				}
			}
		});
	}

	it('cubic weights are not separable into pairwise terms', () => {
		// The double-centred (j, k) logit matrix of a degree-2 operator does not
		// depend on the query; cubic's does. Check both claims numerically.
		const rng = mulberry32(7);
		const vec = () => Array.from({ length: dh }, () => gaussian(rng));
		const k1 = Array.from({ length: n }, vec);
		const k2 = Array.from({ length: n }, vec);
		const centred = (logit: (q: number[], a: number[], b: number[]) => number, q: number[]) => {
			const m = k1.map((a) => k2.map((b) => logit(q, a, b)));
			const row = m.map((r) => r.reduce((s, x) => s + x, 0) / n);
			const col = m[0].map((_, k) => m.reduce((s, r) => s + r[k], 0) / n);
			const all = row.reduce((s, x) => s + x, 0) / n;
			return m.map((r, j) => r.map((x, k) => x - row[j] - col[k] + all));
		};
		const spread = (logit: (q: number[], a: number[], b: number[]) => number) => {
			const a = centred(logit, vec());
			const b = centred(logit, vec());
			return Math.max(...a.flatMap((r, j) => r.map((x, k) => Math.abs(x - b[j][k]))));
		};
		expect(spread(referenceLogits.tree)).toBeLessThan(1e-9);
		expect(spread(referenceLogits.strassen)).toBeLessThan(1e-9);
		expect(spread(referenceLogits.cubic)).toBeGreaterThan(1e-2);
	});
});

describe('standard attention', () => {
	it('matches the textbook softmax(QKᵀ/√d)V', () => {
		const bufs = { q: randomHeads(1), k: randomHeads(2), v: randomHeads(3) };
		const r = OPERATORS.standard.attend(
			{ q: toTensor(bufs.q), k: toTensor(bufs.k), v: toTensor(bufs.v) },
			{ B, H, n, dh }
		);
		const y = r.y.dataSync() as Float32Array;
		for (let b = 0; b < B; b++)
			for (let h = 0; h < H; h++) {
				const ref = referencePair(head(bufs.q, b, h), head(bufs.k, b, h), head(bufs.v, b, h));
				expect(maxAbsDiff(y, b, h, ref)).toBeLessThan(1e-4);
			}
	});
});
