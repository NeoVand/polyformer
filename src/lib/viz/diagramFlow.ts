/**
 * A Feynman attention diagram probe read as a whole, every token at once: each state's
 * dominant sector, the states a root's readout depends on (its backward cone),
 * and every read between rounds. Pure functions behind the spacetime view.
 */
import type { DiagramHead, DiagramSector, DiagramState } from '#lib/engine/protocol.ts';
import { expand } from './feynman.ts';

export const SECTORS: DiagramSector[] = ['leaf', 'hop', 'cubic', 'exchange', 'carry'];

export const stateAt = (
	head: DiagramHead,
	n: number,
	r: number,
	t: number
): DiagramState | undefined => head.states[(r - 1) * n + t];

/** The sector holding most of a state's mass. */
export const dominant = (st: DiagramState): DiagramSector =>
	SECTORS.reduce((a, b) => (st.sectors[b] > st.sectors[a] ? b : a));

/**
 * For each round, the tokens whose states feed the root's readout (its backward
 * cone), with the share of the readout that flows through each.
 */
export function backwardCone(
	head: DiagramHead,
	n: number,
	rounds: number,
	root: number,
	threshold = 0.05
): Map<number, number>[] {
	return expand(head, n, rounds, 0, root, { threshold, perRound: n }).levels;
}

export interface FlowEdge {
	/** Round of the state that reads. */
	r: number;
	from: number;
	to: number;
	w: number;
	kind: DiagramSector;
	/** Carries at least `threshold` of the readout. */
	lit: boolean;
	/** Share of the readout through this read (0 outside the cone). */
	flow: number;
}

/**
 * Every read between rounds above `min` weight, faint ones first so lit ones draw
 * on top. A read is lit when at least `threshold` of the root's readout passes
 * through it, so weak options out of a lit state stay faint.
 */
export function flowEdges(
	head: DiagramHead,
	n: number,
	rounds: number,
	cone: Map<number, number>[],
	min = 0.04,
	threshold = 0.05
): FlowEdge[] {
	const out: FlowEdge[] = [];
	for (let r = 1; r <= rounds; r++)
		for (let t = 0; t < n; t++) {
			const st = stateAt(head, n, r, t);
			if (!st) continue;
			const into = cone[r].get(t) ?? 0;
			const push = (from: number, w: number, kind: DiagramSector, src = r - 1) => {
				const flow = cone[src].has(from) ? into * w : 0;
				out.push({ r, from, to: t, w, kind, flow, lit: flow >= threshold });
			};
			for (const h of st.hops) if (h.weight >= min) push(h.j, h.weight, 'hop');
			for (const c of st.cubic)
				if (c.weight >= min) for (const s of [c.j, c.k]) push(s, c.weight, 'cubic');
			for (const e of st.exchanges) if (e.weight >= min) push(e.j, e.weight, 'exchange');
			if (st.sectors.carry >= 2 * min) push(t, st.sectors.carry, 'carry');
			if (st.sectors.leaf >= 2 * min) push(t, st.sectors.leaf, 'leaf', 0);
		}
	return out.sort((a, b) => Number(a.lit) - Number(b.lit) || a.w - b.w);
}
