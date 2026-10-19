import { describe, expect, it } from 'vitest';
import { DECK } from '../set/cards.ts';
import { gaussian, mulberry32 } from '../set/rng.ts';
import {
	CLASSES,
	cardPhases,
	charValue,
	classStrength,
	countFound,
	deckIndexAt,
	fitChannels,
	type PhaseProbe
} from './characters.ts';

const heads = 2;
const n = 10;
const dh = 3;
const size = n - 1;

/** A probe whose channels are given as a function of (head, channel, card, position). */
function probe(phase: (h: number, c: number, x: number, p: number) => number): PhaseProbe {
	const len = DECK.length * heads * n * dh;
	const angle = new Float32Array(len);
	const gate = new Float32Array(len).fill(0.7);
	for (let b = 0; b < DECK.length; b++)
		for (let h = 0; h < heads; h++)
			for (let p = 0; p < size; p++)
				for (let c = 0; c < dh; c++)
					angle[((b * heads + h) * n + p + 1) * dh + c] = phase(h, c, deckIndexAt(b, p, size), p);
	return { heads, n, dh, angle, gate };
}

describe('character classes', () => {
	it('40 representatives, and with their conjugates every non-trivial character', () => {
		expect(CLASSES).toHaveLength(40);
		const keys = new Set<string>();
		for (const c of CLASSES) {
			keys.add(c.join(''));
			keys.add(c.map((v) => (3 - v) % 3).join(''));
		}
		expect(keys.size).toBe(80);
	});

	it('the deck layout puts every card once at every position', () => {
		for (let p = 0; p < size; p++) {
			const seen = new Set(DECK.map((_, b) => deckIndexAt(b, p, size)));
			expect(seen.size).toBe(DECK.length);
		}
	});
});

describe('fitChannels', () => {
	const rng = mulberry32(5);
	const target = 17;
	const c = CLASSES[target];
	// head 0 channel 0: the character with an offset; channel 1: its conjugate;
	// channel 2 and head 1: noise
	const pr = probe((h, ch, x, p) => {
		const v = (2 * Math.PI * charValue(c, DECK[x])) / 3;
		if (h === 0 && ch === 0) return v + 1.1;
		if (h === 0 && ch === 1) return -v - 0.4;
		return 3 * gaussian(rng) + 0.3 * p;
	});
	const fits = fitChannels(pr);

	it('recovers a character and its conjugate exactly', () => {
		expect(fits[0]).toMatchObject({ cls: target, sign: 1 });
		expect(fits[0].R).toBeCloseTo(1, 5);
		expect(fits[1]).toMatchObject({ cls: target, sign: -1 });
		expect(fits[1].R).toBeCloseTo(1, 5);
	});

	it('scores noise far below the threshold', () => {
		for (const f of fits.slice(2)) expect(f.R).toBeLessThan(0.5);
		expect(countFound(classStrength(fits))).toBe(1);
	});

	it('rotates a character channel onto 0, 1/3 and 2/3 of a turn', () => {
		for (const fit of fits.slice(0, 2)) {
			const phases = cardPhases(pr, fit);
			phases.forEach(({ angle, length }, x) => {
				const want = (2 * Math.PI * charValue(c, DECK[x])) / 3;
				const d = Math.atan2(Math.sin(angle - want), Math.cos(angle - want));
				expect(Math.abs(d)).toBeLessThan(1e-4);
				expect(length).toBeCloseTo(1, 5);
			});
		}
	});
});
