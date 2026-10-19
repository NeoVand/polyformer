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

// ── Feynman attention diagram probe ─────────────────────────────────────────────────────

export type DiagramSector = 'leaf' | 'hop' | 'cubic' | 'exchange' | 'carry';

/** Total probability a state puts on each sector; the five sum to 1. */
export type SectorMass = Record<DiagramSector, number>;

/**
 * How one token's state Φ^r_t was built at round r (1-based) of one head:
 * its sector masses and the heaviest options inside each sector. Token and
 * key indices are sequence positions (0 = BOS). An option's children are the
 * states of round r − 1 it reads: hop j reads Φ^{r−1}_j, cubic (j, k) reads
 * Φ^{r−1}_j ⊙ Φ^{r−1}_k, exchange (j, m) reads Φ^{r−1}_j ⊙ Ψ^r_m, carry reads
 * Φ^{r−1}_t, and leaf reads v_t (round 0). Expanding children recursively from
 * the query's last round gives the weighted computation tree.
 */
export interface DiagramState {
	token: number;
	round: number;
	sectors: SectorMass;
	/** Heaviest hops, descending. */
	hops: { j: number; weight: number }[];
	/** Heaviest ordered cubic pairs, descending. */
	cubic: { j: number; k: number; weight: number }[];
	/** Heaviest exchanges with virtual mode m, descending. */
	exchanges: { j: number; m: number; weight: number }[];
}

/** Virtual mode Ψ^r_m of one head: the token pairs (k, l) it binds at round r. */
export interface DiagramMode {
	round: number;
	m: number;
	/** Heaviest ordered pairs, descending; weights sum to 1 over all pairs. */
	pairs: { k: number; l: number; weight: number }[];
}

export interface DiagramHead {
	head: number;
	/** The probed token's state at rounds 1…R (query[r − 1] is round r). */
	query: DiagramState[];
	/** Every token's state at every round: states[(r − 1)·n + t]. */
	states: DiagramState[];
	/** Every virtual mode at every round: modes[(r − 1)·M + m]. */
	modes: DiagramMode[];
}

export interface DiagramResult {
	/** Run id and the optimizer step whose weights were read. */
	id: string;
	step: number;
	task: string;
	/** Sequence position that was probed. */
	token: number;
	/** Sequence length, heads, rounds R and virtual modes M. */
	n: number;
	heads: number;
	rounds: number;
	modes: number;
	/** Options kept per sector in each state. */
	topK: number;
	/** Model's class probabilities at the probed token. */
	probs: number[];
	/** True class at the probed token, or null where the task has no label. */
	target: number | null;
	/** One entry per head, first Feynman attention layer. */
	perHead: DiagramHead[];
}

export type WorkerEvent =
	| { id: number; event: 'step'; metrics: StepMetric[] }
	| { id: number; event: 'eval'; metrics: EvalMetric[] }
	| { id: number; event: 'phase'; phase: string };

export type WorkerReply =
	{ id: number; ok: true; result: unknown } | { id: number; ok: false; error: string };
