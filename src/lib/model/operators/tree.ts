import { numpy as np } from '@jax-js/jax';
import { tripleAggregate, tripleValueFlops } from './triple.ts';
import type { AttentionOperator } from './types.ts';

/**
 * Columbia tree poly-attention (arXiv 2602.02422): logits on the path
 * i — j — k, A_ijk = ⟨Q_i, K¹_j⟩ + ⟨K¹_j, K²_k⟩, with the same Hadamard pair
 * values as cubic attention. Degree 2 in the token features.
 */
export const tree: AttentionOperator = {
	id: 'tree',
	name: 'Tree poly-attention',
	short: 'Tree',
	arity: 3,
	projections: ['q', 'k1', 'k2', 'v1', 'v2'],
	logitTex: 'A_{ijk} = \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle',
	source: 'Columbia poly-attention, arXiv 2602.02422',
	attend({ q, k1, k2, v1, v2 }, s, capture = false) {
		const { B, H, n } = s;
		const sij = np.matmul(q, k1.ref.transpose([0, 1, 3, 2])); // [B,H,i,j]
		const sjk = np.matmul(k1, k2.transpose([0, 1, 3, 2])); // [B,H,j,k]
		const logits = sij
			.reshape([B, H, n, n, 1])
			.add(sjk.reshape([B, H, 1, n, n]))
			.mul(1 / Math.sqrt(s.dh));
		return tripleAggregate(logits, v1, v2, s, capture);
	},
	flops: (n, H, dh) => H * (4 * n * n * dh + 2 * n * n * n) + tripleValueFlops(n, H, dh)
};
