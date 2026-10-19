/** Data streams shared by the worker and the page, so the page can show exactly what the models see. */
import { dealLayout, makeBatch, setMembership, type Card, type SetBatch } from '../set/cards.ts';
import { deriveSeed, mulberry32 } from '../set/rng.ts';

/** Held-out layouts use a fixed seed, independent of the training seed. */
export const EVAL_SEED = 0x5e7e7a1;

const trainSeed = (seed: number, step: number) => deriveSeed(seed + 7919, step);

/** The training batch for optimizer step `step`: a pure function of (seed, step). */
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
