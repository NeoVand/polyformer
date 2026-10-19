import { beforeAll, describe, expect, it } from 'vitest';
import { defaultDevice, init, numpy as np, type Array as Tensor } from '@jax-js/jax';
import { dspa, optionAllowed, optionLayout, sectorPrior } from './operators/dspa.ts';
import { referenceDspa, type DspaHeadParams, type Mat } from './reference.ts';
import { gaussian, mulberry32 } from '../set/rng.ts';

const B = 2;
const H = 2;
const n = 5;
const dh = 4;
const R = 2;
const M = 3;

const rng = mulberry32(2026);
const rand = (size: number, std = 1) =>
	Float32Array.from({ length: size }, () => gaussian(rng) * std);
const mat = (buf: Float32Array, off: number, rows: number, cols: number): Mat =>
	Array.from({ length: rows }, (_, r) =>
		Array.from(buf.subarray(off + r * cols, off + (r + 1) * cols))
	);

beforeAll(async () => {
	await init();
	defaultDevice('cpu');
});

describe('Feynman attention matches a brute-force loop over every diagram', () => {
	it('outputs and per-round option weights', () => {
		const heads = {
			q: rand(B * H * n * dh),
			u: rand(B * H * n * dh),
			w: rand(B * H * n * dh),
			v: rand(B * H * n * dh)
		};
		const ex = {
			u0: rand(H * dh),
			w0: rand(H * dh),
			uc: rand(H * dh),
			wc: rand(H * dh),
			wm: rand(H * M * dh),
			qm: rand(H * M * dh),
			// a non-trivial clock so rounds differ
			omega: Float32Array.from({ length: H * R * dh }, () => 1 + 0.5 * gaussian(rng)),
			// perturb the prior so a sign error in any sector would show
			mu: Float32Array.from(
				{ length: H * 5 },
				(_, i) => sectorPrior(n, M)[i % 5] + 0.3 * gaussian(rng)
			)
		};
		const shapes: Record<keyof typeof ex, number[]> = {
			u0: [H, dh],
			w0: [H, dh],
			uc: [H, dh],
			wc: [H, dh],
			wm: [H, M, dh],
			qm: [H, M, dh],
			omega: [H, R, dh],
			mu: [H, 5]
		};
		const extra = Object.fromEntries(
			Object.entries(ex).map(([k, buf]) => [k, np.array(buf).reshape(shapes[k as keyof typeof ex])])
		) as Record<string, Tensor>;
		const proj = Object.fromEntries(
			Object.entries(heads).map(([k, buf]) => [k, np.array(buf).reshape([B, H, n, dh])])
		) as Record<string, Tensor>;

		const r = dspa.attend(proj, { B, H, n, dh }, true, { extra, options: { rounds: R, modes: M } });
		const y = r.y.dataSync() as Float32Array;
		const rounds = r.rounds!.map((t) => t.dataSync() as Float32Array);
		r.modes!.forEach((t) => t.dispose());
		const K = optionLayout(n, M).size;
		expect(rounds).toHaveLength(R);

		let maxY = 0;
		let maxW = 0;
		for (let b = 0; b < B; b++)
			for (let h = 0; h < H; h++) {
				const off = (b * H + h) * n * dh;
				const e: DspaHeadParams = {
					u0: Array.from(ex.u0.subarray(h * dh, (h + 1) * dh)),
					w0: Array.from(ex.w0.subarray(h * dh, (h + 1) * dh)),
					uc: Array.from(ex.uc.subarray(h * dh, (h + 1) * dh)),
					wc: Array.from(ex.wc.subarray(h * dh, (h + 1) * dh)),
					wm: mat(ex.wm, h * M * dh, M, dh),
					qm: mat(ex.qm, h * M * dh, M, dh),
					omega: mat(ex.omega, h * R * dh, R, dh),
					mu: Array.from(ex.mu.subarray(h * 5, (h + 1) * 5))
				};
				const ref = referenceDspa(
					mat(heads.q, off, n, dh),
					mat(heads.u, off, n, dh),
					mat(heads.w, off, n, dh),
					mat(heads.v, off, n, dh),
					e,
					R,
					M
				);
				for (let p = 0; p < n; p++)
					for (let c = 0; c < dh; c++)
						maxY = Math.max(maxY, Math.abs(y[off + p * dh + c] - ref.y[p][c]));
				for (let rr = 0; rr < R; rr++)
					for (let p = 0; p < n; p++) {
						const row = rounds[rr].subarray(
							((b * H + h) * n + p) * K,
							((b * H + h) * n + p + 1) * K
						);
						expect(row.reduce((s, x) => s + x, 0)).toBeCloseTo(1, 5);
						for (let o = 0; o < K; o++) {
							maxW = Math.max(maxW, Math.abs(row[o] - ref.rounds[rr][p][o]));
							if (!optionAllowed(p, o, n, M)) expect(row[o]).toBe(0);
						}
					}
			}
		expect(maxY).toBeLessThan(1e-4);
		expect(maxW).toBeLessThan(1e-5);
	});

	it('starts with equal prior mass on every sector', () => {
		// with all inner products zero, each sector's total weight is set by μ alone
		const prior = sectorPrior(n, M).map((m) => Math.exp(m));
		const L = optionLayout(n, M);
		// sizes of each sector for a middle token (masking removes some options)
		const p = 2;
		const sizes = [L.leaf, L.hop, L.cubic, L.exchange, L.carry].map((start, i, all) => {
			const end = i < 4 ? all[i + 1] : L.size;
			let c = 0;
			for (let o = start; o < end; o++) if (optionAllowed(p, o, n, M)) c++;
			return c;
		});
		const mass = sizes.map((s, i) => s * prior[i]);
		// leaf and carry are exact; the masked sectors are within their mask fraction
		expect(mass[0]).toBeCloseTo(1, 10);
		expect(mass[4]).toBeCloseTo(1, 10);
		for (const m of mass.slice(1, 4)) {
			expect(m).toBeGreaterThan(0.5);
			expect(m).toBeLessThanOrEqual(1);
		}
	});
});
