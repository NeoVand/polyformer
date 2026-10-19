/**
 * The game of SET as Match3 over Z_3^4.
 *
 * A card is a vector in Z_3^4: (number, shape, shading, colour). Three distinct
 * cards form a SET iff they sum to 0 mod 3 in every attribute, i.e. each
 * attribute is either all-equal or all-different.
 */
import type { Rng } from './rng.ts';

export const ATTRS = 4;
export const VALUES = 3;
/** Attribute value reserved for the BOS / sink token. */
export const BOS_VALUE = 3;
/** Embedding table width per attribute: values 0–2 plus BOS. */
export const ATTR_VOCAB = 4;
export const DECK_SIZE = 81;
export const LAYOUT_SIZE = 12;
/** Sequence length: BOS sink at position 0, then the layout. */
export const SEQ_LEN = LAYOUT_SIZE + 1;

export type Card = readonly [number, number, number, number];

export const ATTR_NAMES = ['number', 'shape', 'shading', 'colour'] as const;
export const VALUE_NAMES = [
	['one', 'two', 'three'],
	['diamond', 'oval', 'squiggle'],
	['solid', 'striped', 'open'],
	['red', 'green', 'purple']
] as const;

export function cardFromId(id: number): Card {
	return [id % 3, Math.floor(id / 3) % 3, Math.floor(id / 9) % 3, Math.floor(id / 27) % 3];
}

export function cardId(c: Card): number {
	return c[0] + 3 * c[1] + 9 * c[2] + 27 * c[3];
}

export const DECK: readonly Card[] = Array.from({ length: DECK_SIZE }, (_, i) => cardFromId(i));

export function isSet(a: Card, b: Card, c: Card): boolean {
	for (let t = 0; t < ATTRS; t++) if ((a[t] + b[t] + c[t]) % 3 !== 0) return false;
	return true;
}

/** The unique card that completes a SET with a and b. */
export function thirdCard(a: Card, b: Card): Card {
	return [
		(6 - a[0] - b[0]) % 3,
		(6 - a[1] - b[1]) % 3,
		(6 - a[2] - b[2]) % 3,
		(6 - a[3] - b[3]) % 3
	];
}

/** All SETs in a layout as sorted index triples (positions within the layout). */
export function findSets(layout: readonly Card[]): [number, number, number][] {
	const pos = new Map<number, number>();
	layout.forEach((c, i) => pos.set(cardId(c), i));
	const out: [number, number, number][] = [];
	for (let a = 0; a < layout.length; a++) {
		for (let b = a + 1; b < layout.length; b++) {
			const c = pos.get(cardId(thirdCard(layout[a], layout[b])));
			if (c !== undefined && c > b) out.push([a, b, c]);
		}
	}
	return out;
}

/** Per-card label: does this card belong to at least one SET in the layout? */
export function setMembership(layout: readonly Card[]): boolean[] {
	const member = new Array<boolean>(layout.length).fill(false);
	for (const [a, b, c] of findSets(layout)) member[a] = member[b] = member[c] = true;
	return member;
}

/** Deal `size` distinct cards uniformly (partial Fisher–Yates over card ids). */
export function dealLayout(rng: Rng, size = LAYOUT_SIZE): Card[] {
	const ids = Array.from({ length: DECK_SIZE }, (_, i) => i);
	for (let i = 0; i < size; i++) {
		const j = i + Math.floor(rng() * (DECK_SIZE - i));
		[ids[i], ids[j]] = [ids[j], ids[i]];
	}
	return ids.slice(0, size).map(cardFromId);
}

export interface SetBatch {
	/** Number of layouts. */
	batch: number;
	/** One-hot attribute features [batch·SEQ_LEN, ATTRS·ATTR_VOCAB]; summing four tables = one matmul. */
	features: Float32Array<ArrayBuffer>;
	/** One-hot labels [batch·SEQ_LEN, 2] (column 1 = in some SET). BOS rows are zero. */
	labels: Float32Array<ArrayBuffer>;
	/** Loss weight per token [batch·SEQ_LEN]: 0 for BOS, 1 for cards. */
	weights: Float32Array<ArrayBuffer>;
	/** The dealt layouts, for inspection. */
	layouts: Card[][];
}

export const FEATURE_DIM = ATTRS * ATTR_VOCAB;

export function encodeLayouts(layouts: Card[][]): SetBatch {
	const batch = layouts.length;
	const rows = batch * SEQ_LEN;
	const features = new Float32Array(rows * FEATURE_DIM);
	const labels = new Float32Array(rows * 2);
	const weights = new Float32Array(rows);
	for (let b = 0; b < batch; b++) {
		const base = b * SEQ_LEN;
		for (let t = 0; t < ATTRS; t++) features[base * FEATURE_DIM + t * ATTR_VOCAB + BOS_VALUE] = 1;
		const member = setMembership(layouts[b]);
		for (let p = 0; p < LAYOUT_SIZE; p++) {
			const row = base + 1 + p;
			const card = layouts[b][p];
			for (let t = 0; t < ATTRS; t++) features[row * FEATURE_DIM + t * ATTR_VOCAB + card[t]] = 1;
			labels[row * 2 + (member[p] ? 1 : 0)] = 1;
			weights[row] = 1;
		}
	}
	return { batch, features, labels, weights, layouts };
}

export function makeBatch(rng: Rng, batch: number): SetBatch {
	return encodeLayouts(Array.from({ length: batch }, () => dealLayout(rng)));
}
