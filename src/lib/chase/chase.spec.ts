import { describe, expect, it } from 'vitest';
import {
	CHASE_FEATURE_DIM,
	CHASE_IDS,
	CHASE_NODES,
	CHASE_PAYLOADS,
	CHASE_QUERY_POS,
	CHASE_SEQ_LEN,
	ID_BOS,
	ID_NONE,
	ID_VOCAB,
	PAY_BOS,
	PAY_NONE,
	PTR_BOS,
	PTR_VOCAB,
	dealChase,
	encodeChase,
	isChaseInstance,
	solveChase
} from './chase.ts';
import { mulberry32 } from '../set/rng.ts';

describe('pointer chase generator', () => {
	it('deals distinct ids and lists of length 1–4 that end in a self-pointer', () => {
		const rng = mulberry32(21);
		const lengths = new Set<number>();
		for (let trial = 0; trial < 500; trial++) {
			const inst = dealChase(rng);
			expect(inst.nodes).toHaveLength(CHASE_NODES);
			expect(new Set(inst.nodes.map((n) => n.id)).size).toBe(CHASE_NODES);
			const ids = new Set(inst.nodes.map((n) => n.id));
			for (const n of inst.nodes) {
				expect(n.id).toBeGreaterThanOrEqual(0);
				expect(n.id).toBeLessThan(CHASE_IDS);
				expect(ids.has(n.pointer)).toBe(true);
				expect(n.payload).toBeGreaterThanOrEqual(0);
				expect(n.payload).toBeLessThan(CHASE_PAYLOADS);
			}
			// in-degree ≤ 1 apart from self-loops: the nodes form disjoint chains
			const incoming = new Map<number, number>();
			for (const n of inst.nodes)
				if (n.pointer !== n.id) incoming.set(n.pointer, (incoming.get(n.pointer) ?? 0) + 1);
			for (const c of incoming.values()) expect(c).toBe(1);
			// every head of a chain reaches a terminal within 3 hops
			for (const head of inst.nodes.filter((n) => !incoming.has(n.id))) {
				const ans = solveChase({ ...inst, start: head.id });
				expect(ans.hops).toBeLessThanOrEqual(3);
				lengths.add(ans.hops + 1);
				const terminal = inst.nodes[ans.path[ans.path.length - 1]];
				expect(terminal.pointer).toBe(terminal.id);
				expect(ans.payload).toBe(terminal.payload);
			}
			expect(ids.has(inst.start)).toBe(true);
			expect(isChaseInstance(inst)).toBe(true);
		}
		expect([...lengths].sort()).toEqual([1, 2, 3, 4]);
	});

	it('follows pointers exactly like a brute-force walk', () => {
		const rng = mulberry32(5);
		for (let trial = 0; trial < 300; trial++) {
			const inst = dealChase(rng);
			let cur = inst.nodes.find((n) => n.id === inst.start)!;
			for (let s = 0; s < 4 && cur.pointer !== cur.id; s++)
				cur = inst.nodes.find((n) => n.id === cur.pointer)!;
			expect(cur.pointer).toBe(cur.id);
			expect(solveChase(inst).payload).toBe(cur.payload);
		}
	});

	it('encodes BOS, nodes and a query that carries only a pointer', () => {
		const inst = dealChase(mulberry32(9));
		const enc = encodeChase([inst]);
		expect(enc.features.length).toBe(CHASE_SEQ_LEN * CHASE_FEATURE_DIM);
		const row = (r: number) =>
			Array.from(enc.features.subarray(r * CHASE_FEATURE_DIM, (r + 1) * CHASE_FEATURE_DIM));
		const hot = (r: number) => row(r).flatMap((v, i) => (v ? [i] : []));
		expect(hot(0)).toEqual([ID_BOS, ID_VOCAB + PTR_BOS, ID_VOCAB + PTR_VOCAB + PAY_BOS]);
		inst.nodes.forEach((n, i) =>
			expect(hot(i + 1)).toEqual([n.id, ID_VOCAB + n.pointer, ID_VOCAB + PTR_VOCAB + n.payload])
		);
		expect(hot(CHASE_QUERY_POS)).toEqual([
			ID_NONE,
			ID_VOCAB + inst.start,
			ID_VOCAB + PTR_VOCAB + PAY_NONE
		]);
		// loss only at the query, on the terminal's payload
		expect(Array.from(enc.weights)).toEqual(
			Array.from({ length: CHASE_SEQ_LEN }, (_, i) => (i === CHASE_QUERY_POS ? 1 : 0))
		);
		const label = enc.labels.subarray(
			CHASE_QUERY_POS * CHASE_PAYLOADS,
			(CHASE_QUERY_POS + 1) * CHASE_PAYLOADS
		);
		expect(Array.from(label).indexOf(1)).toBe(solveChase(inst).payload);
		expect(enc.labels.reduce((s, v) => s + v, 0)).toBe(1);
	});

	it('rejects malformed instances at the worker boundary', () => {
		const inst = dealChase(mulberry32(1));
		expect(isChaseInstance({ ...inst, start: 99 })).toBe(false);
		expect(isChaseInstance({ ...inst, nodes: inst.nodes.slice(1) })).toBe(false);
		const cyc = structuredClone(inst);
		// make a two-cycle with no terminal
		cyc.nodes[0].pointer = cyc.nodes[1].id;
		cyc.nodes[1].pointer = cyc.nodes[0].id;
		cyc.start = cyc.nodes[0].id;
		expect(isChaseInstance(cyc)).toBe(false);
	});
});
