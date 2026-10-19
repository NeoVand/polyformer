/**
 * Pointer chasing seen through a DS-PA diagram probe: the row order that follows
 * the linked lists, and the payload each state holds after each round.
 */
import { CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
import type { DiagramHead } from '#lib/engine/protocol.ts';
import { dominant, stateAt } from './diagramFlow.ts';

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
				const d = dominant(st);
				if (d === 'hop') return st.hops[0] ? prev[st.hops[0].j] : null;
				if (d === 'carry') return prev[t];
				if (d === 'leaf') return own[t];
				return null;
			})
		);
	}
	return out;
}
