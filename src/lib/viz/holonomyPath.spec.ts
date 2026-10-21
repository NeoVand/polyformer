import { describe, expect, it } from 'vitest';
import { idealRotations, multiply } from './a5.ts';
import {
	carriedFrames,
	IDENTITY,
	makeSequence,
	orderedProduct,
	turnDegrees
} from './holonomyPath.ts';

describe('holonomy path', () => {
	it('finds the identity element and measures turns', () => {
		expect(turnDegrees(idealRotations[IDENTITY])).toBeCloseTo(0, 9);
		const turns = idealRotations.map(turnDegrees).map((d) => Math.round(d));
		// A5 has rotations by 0, 72, 120, 144 and 180 degrees
		expect([...new Set(turns)].sort((a, b) => a - b)).toEqual([0, 72, 120, 144, 180]);
	});

	it('plants a triple whose ordered product is the identity', () => {
		for (const seed of [1, 2, 3, 17, 99]) {
			const s = makeSequence(seed);
			expect(s.tokens).toHaveLength(8);
			expect(s.tokens.every((g) => g !== IDENTITY)).toBe(true);
			expect(turnDegrees(orderedProduct(idealRotations, s.tokens, s.planted))).toBeLessThan(1e-6);
			for (const t of s.planted) expect(s.inLoop[t]).toBe(true);
		}
	});

	it('is deterministic for a seed', () => {
		expect(makeSequence(5)).toEqual(makeSequence(5));
		expect(makeSequence(5).tokens).not.toEqual(makeSequence(6).tokens);
	});

	it('carries the frame and turns it only at chosen tokens', () => {
		const s = makeSequence(11);
		const chosen = [1, 4, 6];
		const frames = carriedFrames(idealRotations, s.tokens, chosen);
		const end = orderedProduct(idealRotations, s.tokens, chosen);
		expect(
			frames[7]
				.flat()
				.map((x, i) => x - end.flat()[i])
				.every((d) => Math.abs(d) < 1e-12)
		).toBe(true);
		expect(frames[2]).toEqual(frames[1]);
		const step = multiply(frames[3], idealRotations[s.tokens[4]]);
		expect(frames[4]).toEqual(step);
	});
});
