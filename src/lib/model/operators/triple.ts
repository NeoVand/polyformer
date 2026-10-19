/**
 * Shared machinery for triple (arity-3) attention: the role mask, the joint
 * softmax over ordered key pairs (j, k), and Hadamard pair values
 * D_jk = V¹_j ⊙ V²_k aggregated as Y_i = Σ_jk P_ijk D_jk.
 *
 * Every contraction is a GEMM over bound keys, so no n³·d intermediate exists:
 *   T_i = P_i · V²            ([n_j, n_k] · [n_k, dh] per query)
 *   Y_i = Σ_j V¹_j ⊙ T_ij
 */
import { numpy as np, nn, type Array as Tensor } from '@jax-js/jax';
import type { AttendResult, HeadShape } from './types.ts';

const NEG = -1e9;

/**
 * Is the ordered key pair (j, k) visible to query i? Keys must be distinct
 * from the query and from each other; the BOS pair (0, 0) is always visible so
 * every row can fall back to the sink.
 */
export function tripleAllowed(i: number, j: number, k: number): boolean {
	if (j === 0 && k === 0) return true;
	return j !== i && k !== i && j !== k;
}

const maskCache = new Map<number, Float32Array<ArrayBuffer>>();

/** Additive mask [n, n·n]: 0 where (i, j, k) is visible, −1e9 elsewhere. */
export function tripleMaskBias(n: number): Float32Array<ArrayBuffer> {
	let m = maskCache.get(n);
	if (!m) {
		m = new Float32Array(n * n * n);
		for (let i = 0; i < n; i++)
			for (let j = 0; j < n; j++)
				for (let k = 0; k < n; k++) m[i * n * n + j * n + k] = tripleAllowed(i, j, k) ? 0 : NEG;
		maskCache.set(n, m);
	}
	return m;
}

/**
 * Normalise triple logits [B, H, n, n, n] (axes i, j, k) jointly over (j, k)
 * and aggregate Hadamard pair values. Consumes logits, v1 and v2.
 */
export function tripleAggregate(
	logits: Tensor,
	v1: Tensor,
	v2: Tensor,
	s: HeadShape,
	capture = false
): AttendResult {
	const { B, H, n, dh } = s;
	const mask = np.array(tripleMaskBias(n)).reshape([1, 1, n, n * n]);
	const P = nn.softmax(logits.reshape([B, H, n, n * n]).add(mask), -1); // [B,H,i,(j,k)]
	const weights = capture ? P.ref : undefined;
	const values = capture ? [v1.ref, v2.ref] : undefined;
	// T[i,j,:] = Σ_k P_ijk V²_k  — one GEMM with (i, j) folded into rows
	const T = np.matmul(P.reshape([B, H, n * n, n]), v2).reshape([B, H, n, n, dh]);
	// Y_i = Σ_j V¹_j ⊙ T_ij
	const y = np.sum(T.mul(v1.reshape([B, H, 1, n, dh])), 3);
	return { y, weights, values };
}

/** FLOPs of the shared value path: P·V² GEMM plus the V¹ contraction, per sequence. */
export function tripleValueFlops(n: number, H: number, dh: number): number {
	return H * (2 * n * n * n * dh + 2 * n * n * dh + 5 * n * n * n);
}
