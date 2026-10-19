import type { Array as Tensor } from '@jax-js/jax';

/** Shape of the per-head projections every operator receives: [B, H, n, dh]. */
export interface HeadShape {
	B: number;
	H: number;
	n: number;
	dh: number;
}

export type OperatorId = 'standard' | 'tree' | 'strassen' | 'cubic' | 'dspa';

/** Per-run knobs for operators that have them (ignored by the rest). */
export interface OperatorOptions {
	/** Message-passing rounds (Feynman attention). */
	rounds?: number;
	/** Virtual exchange modes (Feynman attention). */
	modes?: number;
}

/** Host-side initialisers handed to `initExtra`, drawing from the model's seeded stream. */
export interface ParamInit {
	normal(shape: number[], std: number): Tensor;
	full(shape: number[], value: number): Tensor;
	fromArray(values: Float32Array<ArrayBuffer>, shape: number[]): Tensor;
}

export interface AttendContext {
	/** The operator's own parameters for this layer, from `initExtra`. Consumed like projections. */
	extra: Record<string, Tensor>;
	options: OperatorOptions;
}

export interface AttendResult {
	/** Per-head outputs [B, H, n, dh]. */
	y: Tensor;
	/** Normalised weights, only when captured: [B, H, n, n] (pairwise) or [B, H, n, n·n] (triple). */
	weights?: Tensor;
	/** Value projections used by the aggregation, only when captured. Each [B, H, n, dh]. */
	values?: Tensor[];
	/** Per-round token option weights, only when captured (Feynman attention): each [B, H, n, K]. */
	rounds?: Tensor[];
	/** Per-round virtual-mode pair weights, only when captured (Feynman attention): each [B, H, M, n·n]. */
	modes?: Tensor[];
}

/**
 * An attention mechanism, pluggable into the shared transformer block.
 *
 * `attend` consumes every projection it is given (jax-js move semantics) and
 * returns per-head outputs. Adding an operator means adding one of these and
 * registering it in `operators/index.ts`; the block, optimizer, worker and UI
 * read everything else (projections, arity, FLOPs, formula) from here.
 * Operators with learned parameters of their own declare them in `initExtra`;
 * they live in the layer's `extra` subtree and train with everything else.
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
	/** Default options, merged under a run's own. */
	defaults?: OperatorOptions;
	/** Operator-owned parameters for one layer. */
	initExtra?(
		s: Omit<HeadShape, 'B'>,
		options: OperatorOptions,
		init: ParamInit
	): Record<string, Tensor>;
	attend(
		p: Record<string, Tensor>,
		s: HeadShape,
		capture?: boolean,
		ctx?: AttendContext
	): AttendResult;
	/** Forward FLOPs of the attention core for one sequence (all heads, excluding projections). */
	flops(n: number, H: number, dh: number, options?: OperatorOptions): number;
}
