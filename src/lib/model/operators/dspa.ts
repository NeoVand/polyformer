/**
 * Dyson–Schwinger polyattention (Feynman attention).
 *
 * Each token's state is rebuilt for R rounds from a sum over "diagrams" of
 * the previous round's states Φ^{r−1} (Φ⁰ = v = tanh(W_v x)). One softmax per
 * token p chooses among five sectors:
 *
 *   leaf      ⟨q_p ⊙ ω_r, u₀ ⊙ w₀⟩ + μ₀              → v_p
 *   hop       ⟨q_p ⊙ ω_r, u_j ⊙ w₀⟩ + μ₁   (j ≠ p)   → Φ_j
 *   cubic     ⟨q_p ⊙ ω_r, u_j ⊙ w_k⟩ + μ₂  (j ≠ k, both ≠ p; BOS pair allowed) → Φ_j ⊙ Φ_k
 *   exchange  ⟨q_p ⊙ ω_r, u_j ⊙ w^m_m⟩ + μ₃ (j ≠ p)  → Φ_j ⊙ Ψ_m
 *   carry     ⟨q_p ⊙ ω_r, u_c ⊙ w_c⟩ + μ₄            → Φ_p
 *
 * where Ψ_m = Σ_kl softmax_kl(⟨q^m_m ⊙ ω_r, u_k ⊙ w_l⟩/√dh, k ≠ l) Φ_k ⊙ Φ_l are
 * M virtual modes: learned queries that bind a pair of tokens. Inner products
 * are scaled by 1/√dh; the sector biases μ start at −log(sector size) so every
 * sector has equal prior mass. The output is Φᴿ RMS-normalised over the head
 * dimension. Sector biases, the RMS readout and the carry state are all needed
 * for it to train.
 *
 * All contractions are GEMMs over bound keys, as in the cubic operator.
 */
import { nn, numpy as np, type Array as Tensor } from '@jax-js/jax';
import { tripleAllowed, tripleValueFlops } from './triple.ts';
import type { AttentionOperator, OperatorOptions } from './types.ts';

const NEG = -1e9;

export const DSPA_SECTORS = ['leaf', 'hop', 'cubic', 'exchange', 'carry'] as const;
export type Sector = (typeof DSPA_SECTORS)[number];

/** Layout of one token's option vector: [leaf | hop j | cubic (j,k) | exchange (j,m) | carry]. */
export function optionLayout(n: number, M: number) {
	const hop = 1;
	const cubic = hop + n;
	const exchange = cubic + n * n;
	const carry = exchange + n * M;
	return { leaf: 0, hop, cubic, exchange, carry, size: carry + 1 };
}

/** Is option `o` visible to token p? */
export function optionAllowed(p: number, o: number, n: number, M: number): boolean {
	const L = optionLayout(n, M);
	if (o === L.leaf || o === L.carry) return true;
	if (o < L.cubic) return o - L.hop !== p;
	if (o < L.exchange) {
		const jk = o - L.cubic;
		return tripleAllowed(p, Math.floor(jk / n), jk % n);
	}
	return Math.floor((o - L.exchange) / M) !== p;
}

const optionMasks = new Map<string, Float32Array<ArrayBuffer>>();
/** Additive mask [n, K]. */
function optionMask(n: number, M: number): Float32Array<ArrayBuffer> {
	const key = `${n}:${M}`;
	let m = optionMasks.get(key);
	if (!m) {
		const K = optionLayout(n, M).size;
		m = new Float32Array(n * K);
		for (let p = 0; p < n; p++)
			for (let o = 0; o < K; o++) m[p * K + o] = optionAllowed(p, o, n, M) ? 0 : NEG;
		optionMasks.set(key, m);
	}
	return m;
}

const pairMasks = new Map<number, Float32Array<ArrayBuffer>>();
/** Additive mask [n·n] for virtual-mode pairs: k ≠ l. */
function pairMask(n: number): Float32Array<ArrayBuffer> {
	let m = pairMasks.get(n);
	if (!m) {
		m = new Float32Array(n * n);
		for (let k = 0; k < n; k++) for (let l = 0; l < n; l++) m[k * n + l] = k === l ? NEG : 0;
		pairMasks.set(n, m);
	}
	return m;
}

/** Initial sector biases: −log of each sector's size. */
export function sectorPrior(n: number, M: number): number[] {
	return [1, n, n * n, n * M, 1].map((s) => -Math.log(s));
}

function resolve(options: OperatorOptions) {
	return { R: options.rounds ?? 2, M: options.modes ?? 16 };
}

export const dspa: AttentionOperator = {
	id: 'dspa',
	name: 'Feynman attention',
	short: 'Feynman',
	arity: 3,
	projections: ['q', 'u', 'w', 'v'],
	logitTex:
		'\\Phi^{r}_p = \\textstyle\\sum_{\\mathcal{D}} P_p(\\mathcal{D})\\, \\mathcal{D}[\\Phi^{r-1}],\\ \\mathcal{D} \\in \\{\\text{leaf},\\, \\text{hop},\\, \\text{cubic},\\, \\text{exchange},\\, \\text{carry}\\}',
	source: 'Polyformer research harness (2026)',
	defaults: { rounds: 2, modes: 16 },

	initExtra({ H, n, dh }, options, init) {
		const { R, M } = resolve(options);
		const prior = sectorPrior(n, M);
		const mu = new Float32Array(H * 5);
		for (let h = 0; h < H; h++) mu.set(prior, h * 5);
		return {
			u0: init.normal([H, dh], 1),
			w0: init.normal([H, dh], 1),
			uc: init.normal([H, dh], 1),
			wc: init.normal([H, dh], 1),
			wm: init.normal([H, M, dh], 1),
			qm: init.normal([H, M, dh], 1),
			omega: init.full([H, R, dh], 1),
			mu: init.fromArray(mu, [H, 5])
		};
	},

	attend({ q, u, w, v }, s, capture = false, ctx) {
		if (!ctx) throw new Error('dspa needs its layer parameters');
		const { B, H, n, dh } = s;
		const { R, M } = resolve(ctx.options);
		const { u0, w0, uc, wc, wm, qm, omega, mu } = ctx.extra;
		const L = optionLayout(n, M);
		const K = L.size;
		const sc = 1 / Math.sqrt(dh);

		const leafVal = np.tanh(v); // Φ⁰ and the leaf value, [B,H,n,dh]
		let phi = leafVal.ref;

		// round-independent keys
		const hopKeyT = u.ref.mul(w0.ref.reshape([1, H, 1, dh])).transpose([0, 1, 3, 2]); // [B,H,dh,n]
		const leafKey = u0.mul(w0).reshape([1, H, dh, 1]);
		const carryKey = uc.mul(wc).reshape([1, H, dh, 1]);
		const wT = w.transpose([0, 1, 3, 2]); // [B,H,dh,n]
		const wmT = wm.transpose([0, 2, 1]).reshape([1, H, dh, M]);
		const segment = (c: number, len: number) => mu.ref.slice([], [c, c + 1]).mul(np.ones([1, len]));
		const bias = np
			.concatenate(
				[segment(0, 1), segment(1, n), segment(2, n * n), segment(3, n * M), segment(4, 1)],
				1
			)
			.reshape([1, H, 1, K])
			.add(np.array(optionMask(n, M)).reshape([1, 1, n, K]));
		mu.dispose();
		const modeMask = np.array(pairMask(n)).reshape([1, 1, 1, n * n]);

		const rounds: Tensor[] = [];
		const modes: Tensor[] = [];

		for (let r = 0; r < R; r++) {
			const om = omega.ref.slice([], r, []); // [H, dh]
			const qr = q.ref.mul(om.ref.reshape([1, H, 1, dh])); // [B,H,n,dh]

			// virtual modes Ψ_m: learned queries over ordered pairs (k ≠ l)
			const qmu = qm.ref
				.mul(om.reshape([H, 1, dh]))
				.reshape([1, H, M, 1, dh])
				.mul(u.ref.reshape([B, H, 1, n, dh]))
				.reshape([B, H, M * n, dh]);
			const pm = nn.softmax(
				np
					.matmul(qmu, wT.ref)
					.mul(sc)
					.reshape([B, H, M, n * n])
					.add(modeMask.ref),
				-1
			); // [B,H,M,(k,l)]
			if (capture) modes.push(pm.ref);
			const tm = np.matmul(pm.reshape([B, H, M * n, n]), phi.ref).reshape([B, H, M, n, dh]);
			const psi = np.sum(tm.mul(phi.ref.reshape([B, H, 1, n, dh])), 3); // [B,H,M,dh]

			// one softmax per token over every diagram
			const qu = qr.ref
				.reshape([B, H, n, 1, dh])
				.mul(u.ref.reshape([B, H, 1, n, dh]))
				.reshape([B, H, n * n, dh]); // (q_p ⊙ u_j)
			const logits = np
				.concatenate(
					[
						np.matmul(qr.ref, leafKey.ref), // [B,H,n,1]
						np.matmul(qr.ref, hopKeyT.ref), // [B,H,n,n]
						np.matmul(qu.ref, wT.ref).reshape([B, H, n, n * n]),
						np.matmul(qu, wmT.ref).reshape([B, H, n, n * M]),
						np.matmul(qr, carryKey.ref) // [B,H,n,1]
					],
					-1
				)
				.mul(sc)
				.add(bias.ref);
			const W = nn.softmax(logits, -1); // [B,H,n,K]
			if (capture) rounds.push(W.ref);

			const part = (a: number, b: number) => W.ref.slice([], [], [], [a, b]);
			const yLeaf = part(L.leaf, L.leaf + 1).mul(leafVal.ref);
			const yHop = np.matmul(part(L.hop, L.cubic), phi.ref);
			const tc = np
				.matmul(part(L.cubic, L.exchange).reshape([B, H, n * n, n]), phi.ref)
				.reshape([B, H, n, n, dh]);
			const yCubic = np.sum(tc.mul(phi.ref.reshape([B, H, 1, n, dh])), 3);
			const te = np
				.matmul(part(L.exchange, L.carry).reshape([B, H, n * n, M]), psi)
				.reshape([B, H, n, n, dh]);
			const yExchange = np.sum(te.mul(phi.ref.reshape([B, H, 1, n, dh])), 3);
			const yCarry = W.slice([], [], [], [L.carry, K]).mul(phi);
			phi = yLeaf.add(yHop).add(yCubic).add(yExchange).add(yCarry);
		}

		for (const t of [q, u, qm, omega, leafVal, hopKeyT, leafKey, carryKey, wT, wmT, bias, modeMask])
			t.dispose();

		// RMS readout over the head dimension
		const y = phi.ref.div(np.sqrt(np.mean(np.square(phi), -1, { keepdims: true }).add(1e-6)));
		return capture ? { y, rounds, modes } : { y };
	},

	flops(n, H, dh, options = {}) {
		const { R, M } = resolve(options);
		const K = optionLayout(n, M).size;
		const modes = M * dh + M * n * dh + 4 * M * n * n * dh + 5 * M * n * n + 2 * M * n * dh;
		const logits =
			2 * n * dh +
			2 * n * n * dh +
			n * n * dh +
			2 * n * n * n * dh +
			2 * n * n * M * dh +
			2 * n * dh;
		const values =
			2 * n * n * dh +
			tripleValueFlops(n, 1, dh) +
			2 * n * n * M * dh +
			2 * n * n * dh +
			6 * n * dh;
		return H * (R * (n * dh + modes + logits + 5 * n * K + values) + 4 * n * dh);
	}
};
