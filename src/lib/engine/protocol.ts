/** Messages between the page and the training worker. Plain data only. */
import type { RunSpec } from './runs.ts';

export type Backend = 'webgpu' | 'wasm' | 'cpu';

export interface InitRequest {
	seed: number;
	runs: RunSpec[];
	totalSteps: number;
	batch: number;
	evalLayouts: number;
	evalEvery: number;
	/** Force a backend (testing); otherwise WebGPU, then wasm. */
	backend?: Backend;
}

export interface RunInfo {
	id: string;
	params: number;
	/** Training FLOPs per optimizer step (≈ 3× forward, whole batch). */
	trainFlopsPerStep: number;
}

export interface InitResult {
	device: Backend;
	available: string[];
	runs: RunInfo[];
}

export interface StepMetric {
	id: string;
	step: number;
	loss: number;
	accuracy: number;
	gradNorm: number;
	/** Wall time of the update including the metric readback. */
	ms: number;
}

export interface EvalMetric {
	id: string;
	step: number;
	loss: number;
	tokenAccuracy: number;
	layoutAccuracy: number;
}

export interface ProbeResult {
	id: string;
	step: number;
	heads: number;
	n: number;
	dh: number;
	/** Joint weights [H, n, n, n] for the first triple layer (i, j, k). */
	weights: Float32Array;
	/** Value projections [H, n, dh]. */
	v1: Float32Array;
	v2: Float32Array;
	/** P(card ∈ some SET) for each of the 12 cards. */
	probs: Float32Array;
}

export type WorkerEvent =
	| { id: number; event: 'step'; metrics: StepMetric[] }
	| { id: number; event: 'eval'; metrics: EvalMetric[] }
	| { id: number; event: 'phase'; phase: string };

export type WorkerReply =
	{ id: number; ok: true; result: unknown } | { id: number; ok: false; error: string };
