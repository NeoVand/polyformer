import { describe, expect, it } from 'vitest';
import { CHASE_NODES, CHASE_QUERY_POS, type ChaseInstance } from '#lib/chase/chase.ts';
import type { DiagramHead, DiagramState, SectorMass } from '#lib/engine/protocol.ts';
import { backwardCone, flowEdges, flowGroups, heldPayloads, pointerOf } from './chaseFlow.ts';

/** Node i has id i and payload i mod 8; ids 0 → 1 → 2 form a list, every other node ends at itself. */
function instance(): ChaseInstance {
	const nodes = Array.from({ length: CHASE_NODES }, (_, i) => ({
		id: i,
		pointer: i,
		payload: i % 8
	}));
	nodes[0].pointer = 1;
	nodes[1].pointer = 2;
	return { nodes, start: 0 };
}

const N = CHASE_QUERY_POS + 1;
const mass = (m: Partial<SectorMass>): SectorMass => ({
	leaf: 0,
	hop: 0,
	cubic: 0,
	exchange: 0,
	carry: 0,
	...m
});

/** A head that follows pointers exactly: every token reads where it points, list ends keep their state. */
function pointerHead(inst: ChaseInstance, rounds: number): DiagramHead {
	const next = pointerOf(inst);
	const states: DiagramState[] = [];
	for (let r = 1; r <= rounds; r++)
		for (let t = 0; t < N; t++) {
			const j = t === 0 ? null : next(t);
			states.push({
				token: t,
				round: r,
				sectors: j === null ? mass({ carry: 1 }) : mass({ hop: 1 }),
				hops: j === null ? [] : [{ j, weight: 1 }],
				cubic: [],
				exchanges: []
			});
		}
	return { head: 0, query: [], states, modes: [] };
}

describe('chase flow', () => {
	it('orders rows along the query list, then the lone nodes', () => {
		const groups = flowGroups(instance());
		expect(groups[0]).toEqual([CHASE_QUERY_POS, 1, 2, 3]);
		expect(groups.flat().sort((a, b) => a - b)).toEqual(
			Array.from({ length: CHASE_NODES + 1 }, (_, i) => i + 1)
		);
	});

	it('moves payloads one link per round until the query holds the end of its list', () => {
		const inst = instance();
		const head = pointerHead(inst, 3);
		const held = heldPayloads(head, N, 3, inst);
		expect(held[0][1]).toBe(0); // node id 0 starts with its own payload
		expect(held[1][1]).toBe(1); // after one round it holds its successor's
		expect(held[2][1]).toBe(2); // and then the end of its list
		expect(held[3][CHASE_QUERY_POS]).toBe(2); // the query reads the start's state at the last round
	});

	it('lights only the reads the readout depends on', () => {
		const inst = instance();
		const head = pointerHead(inst, 3);
		const cone = backwardCone(head, N, 3, CHASE_QUERY_POS);
		expect([...cone[3]]).toEqual([CHASE_QUERY_POS]);
		const lit = flowEdges(head, N, 3, cone).filter((e) => e.lit);
		expect(lit.map((e) => [e.r, e.from, e.to])).toEqual(
			expect.arrayContaining([
				[3, 1, CHASE_QUERY_POS],
				[2, 2, 1],
				[1, 3, 2]
			])
		);
		expect(lit.every((e) => e.to !== 5)).toBe(true);
	});
});
