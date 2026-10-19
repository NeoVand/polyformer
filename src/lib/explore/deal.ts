/**
 * One table of twelve SET cards scored by the hand-built cubic head, shared by the
 * landing page and the report: the score tensor for the 3D cube, the strongest
 * hyperedges per query for the graph, and a tour of every card in a SET.
 */
import { querySlice, topHyperedges } from './analysis.ts';
import { exactProbe, scoreSlice, type ExactProbe } from './exact.ts';
import { dealLayout, findSets, LAYOUT_SIZE, type Card } from '#lib/set/cards.ts';
import { mulberry32 } from '#lib/set/rng.ts';

export interface Deal {
	layout: Card[];
	sets: ReturnType<typeof findSets>;
	exact: ExactProbe;
	/** The score tensor, normalised to [0, 1] and sharpened so SET cells stand out. */
	volume: Float32Array;
}

/** A seeded deal with at least three SETs, so every view has something to show. */
export function dealTable(seed: number): Deal {
	const rng = mulberry32(seed * 7717 + 3);
	let layout: Card[];
	do layout = dealLayout(rng);
	while (findSets(layout).length < 3);
	const exact = exactProbe(layout, 3);
	const C = LAYOUT_SIZE;
	const flat = new Float32Array(C * C * C);
	for (let i = 0; i < C; i++) flat.set(scoreSlice(exact, i), i * C * C);
	let lo = Infinity;
	let hi = -Infinity;
	for (const v of flat)
		if (!Number.isNaN(v)) {
			lo = Math.min(lo, v);
			hi = Math.max(hi, v);
		}
	const span = hi - lo || 1;
	const volume = flat.map((v) => (Number.isNaN(v) ? 0 : ((v - lo) / span) ** 3.25));
	return { layout, sets: findSets(layout), exact, volume };
}

/** The query's five strongest pairs, weights relative to the best. */
export function strongestEdges(deal: Deal, q: number) {
	const top = topHyperedges(querySlice(deal.exact, 0, q), 5, q);
	const w = top[0]?.weight || 1;
	return top.map((e) => ({ j: e.j, k: e.k, weight: e.weight / w }));
}

export interface TourStop {
	i: number;
	pair: { j: number; k: number } | null;
}

/** Every card in a SET, once per SET it is in, with one card in no SET halfway through. */
export function tourStops({ layout, sets }: Deal): TourStop[] {
	const out: TourStop[] = [];
	const members = [...new Set(sets.flat())].sort((a, b) => a - b);
	for (const i of members)
		for (const s of sets.filter((x) => x.includes(i))) {
			const [j, k] = s.filter((c) => c !== i);
			out.push({ i, pair: { j, k } });
		}
	const loner = layout.findIndex((_, c) => !sets.some((s) => s.includes(c)));
	if (loner >= 0) out.splice(Math.ceil(out.length / 2), 0, { i: loner, pair: null });
	return out;
}
