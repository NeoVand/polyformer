import { describe, expect, it } from 'vitest';
import { DECK } from '#lib/set/cards.ts';
import { scoreDistribution, sectorSizes } from './figures.ts';

describe('learn figures', () => {
	it('scores every SET at 4 and finds all 1,080 of them among 85,320 triples', () => {
		const d = scoreDistribution(DECK);
		expect(d.reduce((a, b) => a + b.count, 0)).toBe(85320);
		expect(d[0]).toMatchObject({ score: 4, count: 1080 });
		expect(d[1].score).toBe(2.5);
	});

	it('counts DS-PA options per sector for the pointer-chase sequence', () => {
		const s = sectorSizes(14, 16);
		expect(s.map((x) => x.size)).toEqual([1, 13, 157, 208, 1]);
	});
});
