/**
 * Match-k on SET cards: a card is positive when it and k − 1 other cards on the table sum to
 * zero, attribute by attribute, modulo 3. SET is Match-3; Match-4 is the four-card relation that
 * every operator below order 4 fails to learn. Same encoding as SET: a sink token, then one-hot
 * attributes per card.
 */
import { ATTRS, ATTR_VOCAB, BOS_VALUE, FEATURE_DIM, dealLayout, type Card } from '../set/cards.ts';

/** For every card, whether it lies in some k-subset of distinct cards that sums to zero. */
export function zeroSumMembers(layout: readonly Card[], k: number): boolean[] {
	const n = layout.length;
	const member = new Array<boolean>(n).fill(false);
	const pick: number[] = [];
	const walk = (from: number) => {
		if (pick.length === k) {
			for (let a = 0; a < ATTRS; a++) {
				let s = 0;
				for (const i of pick) s += layout[i][a];
				if (s % 3 !== 0) return;
			}
			for (const i of pick) member[i] = true;
			return;
		}
		for (let i = from; i < n; i++) {
			pick.push(i);
			walk(i + 1);
			pick.pop();
		}
	};
	walk(0);
	return member;
}

export interface MatchBatch {
	batch: number;
	features: Float32Array<ArrayBuffer>;
	labels: Float32Array<ArrayBuffer>;
	weights: Float32Array<ArrayBuffer>;
}

export function encodeMatch(layouts: Card[][], k: number): MatchBatch {
	const size = layouts[0]?.length ?? 0;
	const seq = size + 1;
	const batch = layouts.length;
	const features = new Float32Array(batch * seq * FEATURE_DIM);
	const labels = new Float32Array(batch * seq * 2);
	const weights = new Float32Array(batch * seq);
	for (let b = 0; b < batch; b++) {
		const base = b * seq;
		for (let t = 0; t < ATTRS; t++) features[base * FEATURE_DIM + t * ATTR_VOCAB + BOS_VALUE] = 1;
		const member = zeroSumMembers(layouts[b], k);
		for (let p = 0; p < size; p++) {
			const row = base + 1 + p;
			for (let t = 0; t < ATTRS; t++)
				features[row * FEATURE_DIM + t * ATTR_VOCAB + layouts[b][p][t]] = 1;
			labels[row * 2 + (member[p] ? 1 : 0)] = 1;
			weights[row] = 1;
		}
	}
	return { batch, features, labels, weights };
}

export const dealMatch = dealLayout;
