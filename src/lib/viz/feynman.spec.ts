import { describe, expect, it } from 'vitest';
import { dealChase, solveChase } from '#lib/chase/chase.ts';
import { dealLayout, findSets } from '#lib/set/cards.ts';
import { mulberry32 } from '#lib/set/rng.ts';
import { expand, idealChase, idealSet, layoutDiagram } from './feynman.ts';

describe('ideal pointer-chase diagram', () => {
	it('walks the true path from the query to the terminal payload', () => {
		const rng = mulberry32(11);
		for (let trial = 0; trial < 40; trial++) {
			const inst = dealChase(rng);
			const head = idealChase(inst, 4);
			const n = inst.nodes.length + 2;
			const { levels, terms } = expand(head, n, 4, 0, n - 1);
			const path = solveChase(inst).path.map((i) => i + 1);
			const terminal = path[path.length - 1];
			// all the flow ends on the terminal's own value
			expect([...levels[0].keys()]).toEqual([terminal]);
			expect(levels[0].get(terminal)).toBeCloseTo(1);
			// hops follow the list in order: query → start → … → terminal
			const hops = terms.filter((t) => t.sector === 'hop').sort((a, b) => b.round - a.round);
			expect(hops.map((t) => t.j)).toEqual(path.slice(0, hops.length));
			expect(hops.length).toBe(Math.min(path.length, 4));
		}
	});
});

describe('ideal SET diagram', () => {
	it('opens one cubic vertex per SET the card is in', () => {
		const rng = mulberry32(5);
		let layout = dealLayout(rng);
		while (findSets(layout).length < 2) layout = dealLayout(rng);
		const sets = findSets(layout);
		const card = sets[0][0];
		const head = idealSet(layout, 2);
		const { terms } = expand(head, layout.length + 1, 2, 0, card + 1, { threshold: 0 });
		const cubic = terms.filter((t) => t.sector === 'cubic');
		const mine = sets.filter((s) => s.includes(card));
		expect(cubic.length).toBe(mine.length);
		for (const t of cubic) {
			const trio = [card, t.j! - 1, t.k! - 1].sort((a, b) => a - b);
			expect(mine.some((s) => [...s].sort((a, b) => a - b).join() === trio.join())).toBe(true);
		}
		expect(terms.find((t) => t.sector === 'carry')?.round).toBe(2);
	});

	it('lays out a vertex between the round columns', () => {
		const rng = mulberry32(9);
		let layout = dealLayout(rng);
		while (!findSets(layout).length) layout = dealLayout(rng);
		const card = findSets(layout)[0][0];
		const L = layoutDiagram(idealSet(layout, 2), 13, 2, 0, card + 1, { width: 800, height: 400 });
		const v = L.vertices.find((x) => x.kind === 'cubic')!;
		expect(v.x).toBeGreaterThan(L.columns[0].x);
		expect(v.x).toBeLessThan(L.columns[1].x);
		expect(L.edges.some((e) => e.sector === 'out')).toBe(true);
	});
});
