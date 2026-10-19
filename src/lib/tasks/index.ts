/**
 * Tasks the bench can train on. Each task deals plain-data examples and
 * encodes them into one-hot features, one-hot labels and per-token loss
 * weights, so the model, optimizer and worker never need to know which task
 * they are running.
 */
import {
	CHASE_FEATURE_DIM,
	CHASE_PAYLOADS,
	CHASE_QUERY_POS,
	CHASE_SEQ_LEN,
	dealChase,
	encodeChase,
	isChaseInstance,
	solveChase,
	type ChaseInstance
} from '../chase/chase.ts';
import {
	ATTRS,
	FEATURE_DIM,
	LAYOUT_SIZE,
	SEQ_LEN,
	dealLayout,
	encodeLayouts,
	setMembership,
	type Card
} from '../set/cards.ts';
import type { Rng } from '../set/rng.ts';

export type TaskId = 'set' | 'chase';

export interface TaskBatch {
	batch: number;
	features: Float32Array<ArrayBuffer>;
	labels: Float32Array<ArrayBuffer>;
	weights: Float32Array<ArrayBuffer>;
}

export interface TaskSpec<E = unknown> {
	id: TaskId;
	name: string;
	seqLen: number;
	featureDim: number;
	classes: number;
	/** Sequence positions that carry a loss. */
	lossPositions: readonly number[];
	deal(rng: Rng): E;
	encode(examples: E[]): TaskBatch;
	/** Validate an example received over postMessage. */
	isExample(x: unknown): x is E;
	/** Target class at a sequence position, or null where there is no loss. */
	targetAt(example: E, position: number): number | null;
}

export const SET_TASK: TaskSpec<Card[]> = {
	id: 'set',
	name: 'SET membership',
	seqLen: SEQ_LEN,
	featureDim: FEATURE_DIM,
	classes: 2,
	lossPositions: Array.from({ length: LAYOUT_SIZE }, (_, i) => i + 1),
	deal: (rng) => dealLayout(rng),
	encode: (layouts) => encodeLayouts(layouts),
	isExample(x): x is Card[] {
		if (!Array.isArray(x) || x.length !== LAYOUT_SIZE) return false;
		const ok = x.every(
			(c) =>
				Array.isArray(c) &&
				c.length === ATTRS &&
				c.every((v) => Number.isInteger(v) && v >= 0 && v < 3)
		);
		return ok && new Set(x.map((c) => c.join())).size === LAYOUT_SIZE;
	},
	targetAt: (layout, position) =>
		position >= 1 && position <= LAYOUT_SIZE ? Number(setMembership(layout)[position - 1]) : null
};

export const CHASE_TASK: TaskSpec<ChaseInstance> = {
	id: 'chase',
	name: 'Pointer chase',
	seqLen: CHASE_SEQ_LEN,
	featureDim: CHASE_FEATURE_DIM,
	classes: CHASE_PAYLOADS,
	lossPositions: [CHASE_QUERY_POS],
	deal: (rng) => dealChase(rng),
	encode: (instances) => encodeChase(instances),
	isExample: isChaseInstance,
	targetAt: (inst, position) => (position === CHASE_QUERY_POS ? solveChase(inst).payload : null)
};

export const TASKS: Record<TaskId, TaskSpec> = {
	set: SET_TASK as TaskSpec,
	chase: CHASE_TASK as TaskSpec
};

export function getTask(id: TaskId): TaskSpec {
	const t = TASKS[id];
	if (!t) throw new Error(`unknown task: ${id}`);
	return t;
}

/** Deal `batch` examples in order, then encode (same RNG use as the SET generator's makeBatch). */
export function makeTaskBatch(task: TaskSpec, rng: Rng, batch: number): TaskBatch {
	return task.encode(Array.from({ length: batch }, () => task.deal(rng)));
}
