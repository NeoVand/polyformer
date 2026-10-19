import { numpy as np } from '@jax-js/jax';
import { tripleAggregate, tripleValueFlops } from './triple.ts';
import type { AttentionOperator } from './types.ts';

/**
 * Cubic polyattention: a trilinear score over the query and an ordered key
 * pair, A_ijk = ⟨Q_i, K¹_j ⊙ K²_k⟩ / √dh, normalised jointly over (j, k), with
 * Hadamard pair values D_jk = V¹_j ⊙ V²_k.
 *
 * The score is computed as one GEMM per query, (Q_i ⊙ K¹) · K²ᵀ, so the
 * largest intermediate is n²·dh rather than n³·dh.
 */
export const cubic: AttentionOperator = {
	id: 'cubic',
	name: 'Cubic polyattention',
	short: 'Cubic',
	arity: 3,
	projections: ['q', 'k1', 'k2', 'v1', 'v2'],
	logitTex: 'A_{ijk} = \\langle Q_i,\\, K^1_j \\odot K^2_k \\rangle',
	source: 'Polyformer (2023)',
	attend({ q, k1, k2, v1, v2 }, s, capture = false) {
		const { B, H, n, dh } = s;
		// (Q_i ⊙ K¹_j) for every (i, j): [B, H, n·n, dh]
		const qk1 = q
			.reshape([B, H, n, 1, dh])
			.mul(k1.reshape([B, H, 1, n, dh]))
			.reshape([B, H, n * n, dh]);
		// contract with K²: [B, H, n·n, n] = A[i, j, k]
		const logits = np.matmul(qk1, k2.transpose([0, 1, 3, 2])).mul(1 / Math.sqrt(dh));
		return tripleAggregate(logits.reshape([B, H, n, n, n]), v1, v2, s, capture);
	},
	flops: (n, H, dh) => H * (n * n * dh + 2 * n * n * n * dh) + tripleValueFlops(n, H, dh)
};
