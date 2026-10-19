import type { Array as Tensor } from '@jax-js/jax';

/** Shape of the per-head projections every operator receives: [B, H, n, dh]. */
export interface HeadShape {
	B: number;
	H: number;
	n: number;
	dh: number;
}

export type OperatorId = 'standard' | 'tree' | 'strassen' | 'cubic';

export interface AttendResult {
	/** Per-head outputs [B, H, n, dh]. */
	y: Tensor;
	/** Normalised weights, only when captured: [B, H, n, n] (pairwise) or [B, H, n, n·n] (triple). */
	weights?: Tensor;
	/** Value projections used by the aggregation, only when captured. Each [B, H, n, dh]. */
	values?: Tensor[];
}

/**
 * An attention mechanism, pluggable into the shared transformer block.
 *
 * `attend` consumes every projection it is given (jax-js move semantics) and
 * returns per-head outputs. Adding an operator means adding one of these and
 * registering it in `operators/index.ts`; the block, optimizer, worker and UI
 * read everything else (projections, arity, FLOPs, formula) from here.
 */
export interface AttentionOperator {
	id: OperatorId;
	/** Display name, sentence case. */
	name: string;
	/** Short label for legends. */
	short: string;
	/** 2 = scores over keys j; 3 = scores over ordered key pairs (j, k). */
	arity: 2 | 3;
	/** Per-head projections the block must produce, in order. */
	projections: readonly string[];
	/** Logit formula in TeX, for the UI. */
	logitTex: string;
	/** One-line description of where it comes from. */
	source: string;
	attend(p: Record<string, Tensor>, s: HeadShape, capture?: boolean): AttendResult;
	/** Forward FLOPs of the attention core for one sequence (all heads, excluding projections). */
	flops(n: number, H: number, dh: number): number;
}
