/** Data streams shared by the worker and the page, so the page can show exactly what the models see. */
import { dealLayout, makeBatch, setMembership, type Card, type SetBatch } from '../set/cards.ts';
import { deriveSeed, mulberry32 } from '../set/rng.ts';
import { getTask, makeTaskBatch, type TaskBatch, type TaskId } from '../tasks/index.ts';

/** Held-out layouts use a fixed seed, independent of the training seed. */
export const EVAL_SEED = 0x5e7e7a1;

/** Per-task stream offsets; SET keeps its original streams so its bench is unchanged. */
const TRAIN_OFFSET: Record<TaskId, number> = { set: 7919, chase: 104729, match4: 1299709 };
const EVAL_SEEDS: Record<TaskId, number> = { set: EVAL_SEED, chase: 0xc4a5e, match4: 0x4a7c4 };

const trainSeed = (seed: number, step: number, task: TaskId = 'set') =>
	deriveSeed(seed + TRAIN_OFFSET[task], step);

/** The SET training batch for optimizer step `step`: a pure function of (seed, step). */
export function trainBatch(seed: number, step: number, batch: number): SetBatch {
	return makeBatch(mulberry32(trainSeed(seed, step)), batch);
}

/** The first layout of that batch, without building the whole batch. */
export function firstLayoutOfBatch(seed: number, step: number): Card[] {
	return dealLayout(mulberry32(trainSeed(seed, step)));
}

export function evalBatch(layouts: number): SetBatch {
	return makeBatch(mulberry32(EVAL_SEED), layouts);
}

/** Share of held-out cards that belong to some SET; the majority-class baseline is max(p, 1 − p). */
export function evalPositiveRate(layouts: number): number {
	const rng = mulberry32(EVAL_SEED);
	let pos = 0;
	for (let b = 0; b < layouts; b++) pos += setMembership(dealLayout(rng)).filter(Boolean).length;
	return pos / (layouts * 12);
}

// ── any task ────────────────────────────────────────────────────────────────

/** Training batch for `task` at optimizer step `step`. For SET this equals `trainBatch`. */
export function taskTrainBatch(task: TaskId, seed: number, step: number, batch: number): TaskBatch {
	return makeTaskBatch(getTask(task), mulberry32(trainSeed(seed, step, task)), batch);
}

/** The held-out examples of a task (plain data), in order. */
export function taskEvalExamples(task: TaskId, count: number): unknown[] {
	const t = getTask(task);
	const rng = mulberry32(EVAL_SEEDS[task]);
	return Array.from({ length: count }, () => t.deal(rng));
}

/** The first example of the training batch at `step`, as the models see it. */
export function firstExampleOfBatch(task: TaskId, seed: number, step: number): unknown {
	return getTask(task).deal(mulberry32(trainSeed(seed, step, task)));
}

/** Deal a fresh example for inspection, from its own seed. */
export function dealExample(task: TaskId, seed: number): unknown {
	return getTask(task).deal(mulberry32(deriveSeed(seed, 0x1ab)));
}

/** Accuracy of always predicting the most frequent held-out class. */
export function majorityBaseline(task: TaskId, count: number): number {
	const t = getTask(task);
	const counts = new Array<number>(t.classes).fill(0);
	let total = 0;
	for (const ex of taskEvalExamples(task, count))
		for (const pos of t.lossPositions) {
			const c = t.targetAt(ex, pos);
			if (c !== null) {
				counts[c]++;
				total++;
			}
		}
	return Math.max(...counts) / Math.max(1, total);
}
