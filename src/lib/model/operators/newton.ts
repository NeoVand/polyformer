/**
 * Newton attention: every arity up to K at once, linear in the sequence.
 *
 * Each head has dh complex channels, φ = σ(g) · e^{i c·θ}, from the projections θ and g (a
 * character of a group is one linear map away). For every query q and m < K, the elementary
 * symmetric polynomial e_m of the OTHER tokens follows from leave-one-out power sums
 * P_j = Σ_t φ_t^j − φ_q^j by Newton's identities, m e_m = Σ_j (−1)^{j−1} e_{m−j} P_j, so
 * φ_q ⊙ e_m is the sum over (m+1)-subsets containing q of their channel products: arity m+1,
 * with no tuple ever enumerated. Each arity's [Re, Im] features are scaled by 1/C(n−1, m),
 * RMS-normalised (so no arity dominates by magnitude), mapped to dh by one projection shared
 * across arities and scaled by a learned per-arity vector; the block's output projection
 * takes it from there.
 *
 * jax-js has no complex dtype, so complex values are (re, im) pairs; every helper consumes
 * its arguments, and `share` lends a pair for one more use. Captured, the layer returns each
 * token's phase angles and gates as its `values`.
 */
import { nn, numpy as np, type Array as Tensor } from '@jax-js/jax';
import type { AttentionOperator, OperatorOptions } from './types.ts';

/** Phase scale: θ = c · (projection), so a unit projection spans a few turns. */
const PHASE = 2;

interface Complex {
	re: Tensor;
	im: Tensor;
}
const share = (a: Complex): Complex => ({ re: a.re.ref, im: a.im.ref });
const mul = (a: Complex, b: Complex): Complex => ({
	re: a.re.ref.mul(b.re.ref).sub(a.im.ref.mul(b.im.ref)),
	im: a.re.mul(b.im).add(a.im.mul(b.re))
});
const add = (a: Complex, b: Complex): Complex => ({ re: a.re.add(b.re), im: a.im.add(b.im) });
const scale = (a: Complex, c: number): Complex => ({ re: a.re.mul(c), im: a.im.mul(c) });
const drop = (a: Complex) => {
	a.re.dispose();
	a.im.dispose();
};

export function binomial(n: number, k: number): number {
	if (k < 0 || k > n) return 0;
	let r = 1;
	for (let i = 1; i <= k; i++) r = (r * (n - k + i)) / i;
	return r;
}

function resolve(options: OperatorOptions) {
	return { K: Math.max(2, options.order ?? 4) };
}

export const newton: AttentionOperator = {
	id: 'newton',
	name: 'Newton attention',
	short: 'Newton',
	arity: 'all',
	projections: ['th', 'g'],
	logitTex:
		'\\phi_q \\odot e^{(-q)}_m = \\sum_{|S| = m,\\, q \\notin S}\\; \\bigodot_{t \\in S \\cup \\{q\\}} \\phi_t',
	source: 'Polyformer research harness (2026)',
	defaults: { order: 4 },

	initExtra({ dh }, options, init) {
		const { K } = resolve(options);
		return {
			readout: init.normal([2 * dh, dh], 1 / Math.sqrt(2 * dh)),
			alpha: init.full([K, dh], 1)
		};
	},

	attend({ th, g }, s, capture, ctx) {
		if (!ctx) throw new Error('newton needs its layer parameters');
		const { B, H, n, dh } = s;
		const { K } = resolve(ctx.options);
		const { readout, alpha } = ctx.extra;

		const gate = nn.sigmoid(g);
		const angle = th.mul(PHASE);
		// captured: every token's phase and gate per channel, [B, H, n, dh] each
		const values = capture ? [angle.ref, gate.ref] : undefined;
		const phi: Complex = { re: gate.ref.mul(np.cos(angle.ref)), im: gate.mul(np.sin(angle)) };

		// powers φ^1 … φ^{K−1}, then leave-one-out sums over the sequence
		const powers: Complex[] = [share(phi)];
		for (let j = 2; j < K; j++) powers.push(mul(share(powers[j - 2]), share(phi)));
		const others = (x: Tensor) => np.sum(x.ref, 2, { keepdims: true }).sub(x);
		const P = powers.map((w) => ({ re: others(w.re), im: others(w.im) }));

		// Newton's identities: e_0 = 1, m e_m = Σ_{j=1}^{m} (−1)^{j−1} e_{m−j} P_j
		const e: (Complex | null)[] = [null];
		for (let m = 1; m < K; m++) {
			let acc: Complex | null = null;
			for (let j = 1; j <= m; j++) {
				const prev = e[m - j];
				let term = prev ? mul(share(prev), share(P[j - 1])) : share(P[j - 1]);
				if (j % 2 === 0) term = scale(term, -1);
				acc = acc ? add(acc, term) : term;
			}
			e.push(scale(acc!, 1 / m));
		}

		// every arity's features, on one scale, through one shared read-out
		let y: Tensor | null = null;
		for (let m = 0; m < K; m++) {
			const f = m === 0 ? share(phi) : mul(share(phi), share(e[m]!));
			const c = 1 / Math.max(1, binomial(n - 1, m));
			const feat = np.concatenate([f.re.mul(c), f.im.mul(c)], -1).reshape([B * H * n, 2 * dh]);
			const normed = feat.ref.div(
				np.sqrt(np.mean(np.square(feat), -1, { keepdims: true }).add(1e-6))
			);
			const part = np
				.matmul(normed, readout.ref)
				.reshape([B, H, n, dh])
				.mul(alpha.ref.slice(m, []).reshape([1, 1, 1, dh]));
			y = y ? y.add(part) : part;
		}

		drop(phi);
		for (const p of P) drop(p);
		for (const x of e) if (x) drop(x);
		readout.dispose();
		alpha.dispose();
		return { y: y!, values };
	},

	flops(n, H, dh, options = {}) {
		const { K } = resolve(options);
		// phases, K−1 powers and sums, Newton's recursion, K read-outs of 2dh → dh
		return (
			H * (6 * n * dh + K * (8 * n * dh) + K * K * 8 * n * dh + K * (4 * n * dh * dh + 6 * n * dh))
		);
	}
};
