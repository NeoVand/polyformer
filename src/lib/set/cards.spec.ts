import { describe, expect, it } from 'vitest';
import {
	DECK,
	FEATURE_DIM,
	SEQ_LEN,
	cardFromId,
	cardId,
	dealLayout,
	encodeLayouts,
	findSets,
	isSet,
	setMembership,
	thirdCard,
	type Card
} from './cards.ts';
import { mulberry32 } from './rng.ts';

describe('SET over Z_3^4', () => {
	it('enumerates 81 distinct cards', () => {
		expect(new Set(DECK.map(cardId)).size).toBe(81);
		for (let i = 0; i < 81; i++) expect(cardId(cardFromId(i))).toBe(i);
	});

	it('has exactly 1080 SETs in the deck and each pair has one completion', () => {
		let count = 0;
		for (let a = 0; a < 81; a++)
			for (let b = a + 1; b < 81; b++)
				for (let c = b + 1; c < 81; c++) if (isSet(DECK[a], DECK[b], DECK[c])) count++;
		expect(count).toBe(1080);
		const a = DECK[5];
		const b = DECK[40];
		expect(isSet(a, b, thirdCard(a, b))).toBe(true);
	});

	it('matches the attribute rule: all equal or all different', () => {
		const allSameOrDiff = (a: Card, b: Card, c: Card) =>
			[0, 1, 2, 3].every((t) => new Set([a[t], b[t], c[t]]).size !== 2);
		const rng = mulberry32(3);
		for (let trial = 0; trial < 2000; trial++) {
			const [a, b, c] = dealLayout(rng, 3);
			expect(isSet(a, b, c)).toBe(allSameOrDiff(a, b, c));
		}
	});

	it('labels cards by membership in some SET of the layout', () => {
		const rng = mulberry32(11);
		for (let trial = 0; trial < 200; trial++) {
			const layout = dealLayout(rng);
			expect(new Set(layout.map(cardId)).size).toBe(12);
			const member = setMembership(layout);
			for (let i = 0; i < 12; i++) {
				let brute = false;
				for (let j = 0; j < 12; j++)
					for (let k = 0; k < 12; k++)
						if (i !== j && j !== k && i !== k && isSet(layout[i], layout[j], layout[k]))
							brute = true;
				expect(member[i]).toBe(brute);
			}
			for (const [a, b, c] of findSets(layout))
				expect(isSet(layout[a], layout[b], layout[c])).toBe(true);
		}
	});

	it('encodes BOS at position 0 and one-hot attributes elsewhere', () => {
		const layout = dealLayout(mulberry32(5));
		const enc = encodeLayouts([layout]);
		expect(enc.features.length).toBe(SEQ_LEN * FEATURE_DIM);
		// BOS row: value 3 in every attribute
		expect(Array.from(enc.features.subarray(0, FEATURE_DIM))).toEqual([
			0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1
		]);
		expect(enc.weights[0]).toBe(0);
		expect(enc.labels[0] + enc.labels[1]).toBe(0);
		for (let p = 0; p < 12; p++) {
			const row = enc.features.subarray((p + 1) * FEATURE_DIM, (p + 2) * FEATURE_DIM);
			for (let t = 0; t < 4; t++) expect(row[t * 4 + layout[p][t]]).toBe(1);
			expect(row.reduce((s, x) => s + x, 0)).toBe(4);
			expect(enc.weights[p + 1]).toBe(1);
		}
	});
});
