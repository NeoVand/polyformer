import { numpy as np } from '@jax-js/jax';
import { tripleAggregate, tripleValueFlops } from './triple.ts';
import type { AttentionOperator } from './types.ts';

/**
 * Strassen attention: all three pairwise edges of the triangle,
 * A_ijk = ⟨Q_i, K¹_j⟩ + ⟨K¹_j, K²_k⟩ + ⟨Q_i, K²_k⟩. Still degree 2, so the
 * j–k coupling it can express does not depend on the query.
 */
export const strassen: AttentionOperator = {
	id: 'strassen',
	name: 'Strassen attention',
	short: 'Strassen',
	arity: 3,
	projections: ['q', 'k1', 'k2', 'v1', 'v2'],
	logitTex:
		'A_{ijk} = \\langle Q_i, K^1_j \\rangle + \\langle K^1_j, K^2_k \\rangle + \\langle Q_i, K^2_k \\rangle',
	source: 'Kozachinskiy et al. 2025',
	attend({ q, k1, k2, v1, v2 }, s, capture = false) {
		const { B, H, n } = s;
		const sij = np.matmul(q.ref, k1.ref.transpose([0, 1, 3, 2])); // [B,H,i,j]
		const sjk = np.matmul(k1, k2.ref.transpose([0, 1, 3, 2])); // [B,H,j,k]
		const sik = np.matmul(q, k2.transpose([0, 1, 3, 2])); // [B,H,i,k]
		const logits = sij
			.reshape([B, H, n, n, 1])
			.add(sjk.reshape([B, H, 1, n, n]))
			.add(sik.reshape([B, H, n, 1, n]))
			.mul(1 / Math.sqrt(s.dh));
		return tripleAggregate(logits, v1, v2, s, capture);
	},
	flops: (n, H, dh) => H * (6 * n * n * dh + 3 * n * n * n) + tripleValueFlops(n, H, dh)
};
