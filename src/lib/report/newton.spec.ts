import { describe, expect, it } from 'vitest';
import { mulberry32 } from '#lib/set/rng.ts';
import { bruteCounts, newtonCounts, type Element } from './newton.ts';

const deal = (seed: number, n: number, m: number, distinct: boolean): Element[] => {
	const rng = mulberry32(seed);
	const Q = 3 ** m;
	const pick = new Set<number>();
	const out: Element[] = [];
	while (out.length < n) {
		const v = Math.floor(rng() * Q);
		if (distinct && pick.has(v)) continue;
		pick.add(v);
		out.push(Array.from({ length: m }, (_, a) => Math.floor(v / 3 ** a) % 3));
	}
	return out;
};

describe("Newton's identities in the group algebra", () => {
	it('count zero-sum k-subsets exactly on SET tables, k = 2..6', () => {
		for (let seed = 1; seed <= 12; seed++) {
			const xs = deal(seed, 9 + (seed % 4), 4, true);
			expect(newtonCounts(xs, 6)).toEqual(bruteCounts(xs, 6));
		}
	});

	it('handle repeated cards at distinct positions', () => {
		for (let seed = 20; seed <= 26; seed++) {
			const xs = deal(seed, 8, 2, false);
			expect(newtonCounts(xs, 5)).toEqual(bruteCounts(xs, 5));
		}
	});
});
