import { numpy as np, nn } from '@jax-js/jax';
import type { AttentionOperator } from './types.ts';

/** Dense softmax attention: P_ij ∝ exp⟨Q_i, K_j⟩/√dh, Y_i = Σ_j P_ij V_j. */
export const standard: AttentionOperator = {
	id: 'standard',
	name: 'Standard attention',
	short: 'Standard',
	arity: 2,
	projections: ['q', 'k', 'v'],
	logitTex: 'A_{ij} = \\langle Q_i, K_j \\rangle',
	source: 'Vaswani et al. 2017',
	attend({ q, k, v }, { dh }, capture = false) {
		const scores = np.matmul(q, k.transpose([0, 1, 3, 2])).mul(1 / Math.sqrt(dh));
		const P = nn.softmax(scores, -1); // [B,H,i,j]
		const weights = capture ? P.ref : undefined;
		const values = capture ? [v.ref] : undefined;
		return { y: np.matmul(P, v), weights, values };
	},
	flops: (n, H, dh) => H * (4 * n * n * dh + 5 * n * n)
};
