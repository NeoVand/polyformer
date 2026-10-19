/**
 * Pointer chasing seen through a DS-PA diagram probe, every token at once: the
 * row order that follows the linked lists, the payload each state holds after
 * each round, the states the readout depends on, and the reads between rounds.
 * Pure functions, so the view stays a thin drawing layer and the logic is testable.
 */
import { CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
import type { DiagramHead, DiagramSector, DiagramState } from '#lib/engine/protocol.ts';
import { expand } from './feynman.ts';

const SECTORS: DiagramSector[] = ['leaf', 'hop', 'cubic', 'exchange', 'carry'];

const stateAt = (head: DiagramHead, n: number, r: number, t: number): DiagramState | undefined =>
	head.states[(r - 1) * n + t];

/** Sequence position each token points to (the query points to its start), or null at a list's end. */
export function pointerOf(inst: ChaseInstance): (p: number) => number | null {
	const posOf = new Map(inst.nodes.map((nd, i) => [nd.id, i + 1]));
	return (p) => {
		if (p === CHASE_QUERY_POS) return posOf.get(inst.start) ?? null;
		if (p < 1 || p > inst.nodes.length) return null;
		const nd = inst.nodes[p - 1];
		return nd.pointer === nd.id ? null : (posOf.get(nd.pointer) ?? null);
	};
}

/**
 * Tokens grouped into rows: the query's list first (query, start, …, end), then
 * every other list from head to end, then lone nodes. BOS holds nothing for this
 * task and is left out. Reading a list top to bottom follows its pointers.
 */
export function flowGroups(inst: ChaseInstance): number[][] {
	const next = pointerOf(inst);
	const N = inst.nodes.length;
	const pointed = new Set<number>();
	for (let p = 1; p <= N; p++) {
		const q = next(p);
		if (q !== null) pointed.add(q);
	}
	const placed = new Set<number>();
	const chain = (p: number) => {
		const g: number[] = [];
		for (let c: number | null = p; c !== null && !placed.has(c); c = next(c)) {
			g.push(c);
			placed.add(c);
		}
		return g;
	};
	const groups: number[][] = [chain(CHASE_QUERY_POS)];
	const lone: number[] = [];
	for (let p = 1; p <= N; p++) {
		if (placed.has(p) || pointed.has(p)) continue;
		if (next(p) === null) {
			lone.push(p);
			placed.add(p);
		} else groups.push(chain(p));
	}
	// whatever is left hangs off a list placed earlier
	for (let p = 1; p <= N; p++) if (!placed.has(p)) groups.push(chain(p));
	if (lone.length) groups.push(lone);
	return groups.filter((g) => g.length > 0);
}

/**
 * The payload each state holds: round 0 is each node's own payload; later rounds
 * follow the state's dominant read (a hop takes the source's payload, a carry keeps
 * its own state, a leaf rereads its value). Null where nothing definite is held.
 */
export function heldPayloads(
	head: DiagramHead,
	n: number,
	rounds: number,
	inst: ChaseInstance
): (number | null)[][] {
	const own = Array.from({ length: n }, (_, t) =>
		t >= 1 && t <= inst.nodes.length ? inst.nodes[t - 1].payload : null
	);
	const out: (number | null)[][] = [own];
	for (let r = 1; r <= rounds; r++) {
		const prev = out[r - 1];
		out.push(
			Array.from({ length: n }, (_, t) => {
				const st = stateAt(head, n, r, t);
				if (!st) return null;
				const d = SECTORS.reduce((a, b) => (st.sectors[b] > st.sectors[a] ? b : a));
				if (d === 'hop') return st.hops[0] ? prev[st.hops[0].j] : null;
				if (d === 'carry') return prev[t];
				if (d === 'leaf') return own[t];
				return null;
			})
		);
	}
	return out;
}

/** For each round, the tokens whose states feed the root's readout (its backward cone). */
export function backwardCone(
	head: DiagramHead,
	n: number,
	rounds: number,
	root: number,
	threshold = 0.05
): Set<number>[] {
	const { levels } = expand(head, n, rounds, 0, root, { threshold, perRound: n });
	return levels.map((m) => new Set(m.keys()));
}

export interface FlowEdge {
	/** Round of the state that reads. */
	r: number;
	from: number;
	to: number;
	w: number;
	kind: DiagramSector;
	/** Inside the readout's backward cone. */
	lit: boolean;
}

/** Every read between rounds above `min` weight, faint ones first so lit ones draw on top. */
export function flowEdges(
	head: DiagramHead,
	n: number,
	rounds: number,
	cone: Set<number>[],
	min = 0.04
): FlowEdge[] {
	const out: FlowEdge[] = [];
	for (let r = 1; r <= rounds; r++)
		for (let t = 0; t < n; t++) {
			const st = stateAt(head, n, r, t);
			if (!st) continue;
			const lit = (s: number, from = r - 1) => cone[r].has(t) && cone[from].has(s);
			for (const h of st.hops)
				if (h.weight >= min)
					out.push({ r, from: h.j, to: t, w: h.weight, kind: 'hop', lit: lit(h.j) });
			for (const c of st.cubic)
				if (c.weight >= min)
					for (const s of [c.j, c.k])
						out.push({ r, from: s, to: t, w: c.weight, kind: 'cubic', lit: lit(s) });
			for (const e of st.exchanges)
				if (e.weight >= min)
					out.push({ r, from: e.j, to: t, w: e.weight, kind: 'exchange', lit: lit(e.j) });
			if (st.sectors.carry >= 2 * min)
				out.push({ r, from: t, to: t, w: st.sectors.carry, kind: 'carry', lit: lit(t) });
			if (st.sectors.leaf >= 2 * min)
				out.push({ r, from: t, to: t, w: st.sectors.leaf, kind: 'leaf', lit: lit(t, 0) });
		}
	return out.sort((a, b) => Number(a.lit) - Number(b.lit) || a.w - b.w);
}
