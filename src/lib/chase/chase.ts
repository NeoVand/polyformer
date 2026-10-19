/**
 * Pointer chasing: follow a linked list to its end and read the payload there.
 *
 * Twelve node tokens each carry a distinct id (from 16), a pointer to another
 * node's id and a payload (from 8). The nodes form linked lists of random
 * lengths 1–4 whose terminal points to itself. A query token at the end holds
 * only a pointer to a random start node; the target is the payload of the
 * terminal reached from that start. Up to three hops, so depth matters.
 *
 * Sequence: BOS at position 0, the 12 nodes in random order, the query last.
 */
import type { Rng } from '../set/rng.ts';

export const CHASE_NODES = 12;
export const CHASE_IDS = 16;
export const CHASE_PAYLOADS = 8;
export const CHASE_MAX_LIST = 4;
/** BOS + nodes + query. */
export const CHASE_SEQ_LEN = CHASE_NODES + 2;
/** Sequence position of the query token. */
export const CHASE_QUERY_POS = CHASE_SEQ_LEN - 1;

/** Special values: BOS, and "none" for fields a token does not have. */
export const ID_BOS = CHASE_IDS;
export const ID_NONE = CHASE_IDS + 1;
export const ID_VOCAB = CHASE_IDS + 2;
export const PTR_BOS = CHASE_IDS;
export const PTR_VOCAB = CHASE_IDS + 2;
export const PAY_BOS = CHASE_PAYLOADS;
export const PAY_NONE = CHASE_PAYLOADS + 1;
export const PAY_VOCAB = CHASE_PAYLOADS + 2;
/** One-hot width: separate id, pointer and payload tables, concatenated. */
export const CHASE_FEATURE_DIM = ID_VOCAB + PTR_VOCAB + PAY_VOCAB;

export interface ChaseNode {
	id: number;
	pointer: number;
	payload: number;
}

export interface ChaseInstance {
	/** Node tokens in sequence order (positions 1…12). */
	nodes: ChaseNode[];
	/** Id the query points at. */
	start: number;
}

export interface ChaseAnswer {
	/** Node indices (0…11) visited from the start to the terminal, inclusive. */
	path: number[];
	/** Pointer hops taken: path.length − 1. */
	hops: number;
	/** Payload of the terminal: the target class. */
	payload: number;
}

/** Deal one instance: distinct ids, random lists of length 1–4, a random start. */
export function dealChase(rng: Rng): ChaseInstance {
	const pick = (n: number) => Math.floor(rng() * n);
	// 12 distinct ids from 16 (partial Fisher–Yates)
	const ids = Array.from({ length: CHASE_IDS }, (_, i) => i);
	for (let i = 0; i < CHASE_NODES; i++) {
		const j = i + pick(CHASE_IDS - i);
		[ids[i], ids[j]] = [ids[j], ids[i]];
	}
	// random sequence order of the node slots, cut into lists of length 1–4
	const order = Array.from({ length: CHASE_NODES }, (_, i) => i);
	for (let i = CHASE_NODES - 1; i > 0; i--) {
		const j = pick(i + 1);
		[order[i], order[j]] = [order[j], order[i]];
	}
	const nodes: ChaseNode[] = Array.from({ length: CHASE_NODES }, (_, i) => ({
		id: ids[i],
		pointer: ids[i],
		payload: pick(CHASE_PAYLOADS)
	}));
	let at = 0;
	while (at < CHASE_NODES) {
		const len = Math.min(1 + pick(CHASE_MAX_LIST), CHASE_NODES - at);
		const list = order.slice(at, at + len);
		for (let t = 0; t < len - 1; t++) nodes[list[t]].pointer = nodes[list[t + 1]].id;
		nodes[list[len - 1]].pointer = nodes[list[len - 1]].id; // terminal points to itself
		at += len;
	}
	return { nodes, start: nodes[pick(CHASE_NODES)].id };
}

/** Follow pointers from the start until a node points to itself. */
export function solveChase(inst: ChaseInstance): ChaseAnswer {
	const byId = new Map(inst.nodes.map((n, i) => [n.id, i]));
	let cur = byId.get(inst.start);
	if (cur === undefined) throw new Error('start id is not a node');
	const path = [cur];
	for (let guard = 0; guard <= CHASE_NODES; guard++) {
		const next = byId.get(inst.nodes[cur].pointer);
		if (next === undefined) throw new Error('dangling pointer');
		if (next === cur) return { path, hops: path.length - 1, payload: inst.nodes[cur].payload };
		cur = next;
		path.push(cur);
	}
	throw new Error('pointer cycle without a terminal');
}

/** Check an untrusted value is a well-formed instance (used at the worker boundary). */
export function isChaseInstance(x: unknown): x is ChaseInstance {
	if (!x || typeof x !== 'object') return false;
	const c = x as ChaseInstance;
	const int = (v: unknown, hi: number) =>
		Number.isInteger(v) && (v as number) >= 0 && (v as number) < hi;
	if (!Array.isArray(c.nodes) || c.nodes.length !== CHASE_NODES || !int(c.start, CHASE_IDS))
		return false;
	if (
		!c.nodes.every(
			(n) => int(n?.id, CHASE_IDS) && int(n?.pointer, CHASE_IDS) && int(n?.payload, CHASE_PAYLOADS)
		)
	)
		return false;
	if (new Set(c.nodes.map((n) => n.id)).size !== CHASE_NODES) return false;
	try {
		solveChase(c);
		return true;
	} catch {
		return false;
	}
}

export interface ChaseBatch {
	batch: number;
	/** One-hot [batch·14, 46]: id | pointer | payload tables. */
	features: Float32Array<ArrayBuffer>;
	/** One-hot payload [batch·14, 8], only on the query row. */
	labels: Float32Array<ArrayBuffer>;
	/** 1 on the query row, 0 elsewhere. */
	weights: Float32Array<ArrayBuffer>;
	instances: ChaseInstance[];
}

export function encodeChase(instances: ChaseInstance[]): ChaseBatch {
	const batch = instances.length;
	const rows = batch * CHASE_SEQ_LEN;
	const features = new Float32Array(rows * CHASE_FEATURE_DIM);
	const labels = new Float32Array(rows * CHASE_PAYLOADS);
	const weights = new Float32Array(rows);
	const put = (row: number, id: number, pointer: number, payload: number) => {
		const o = row * CHASE_FEATURE_DIM;
		features[o + id] = 1;
		features[o + ID_VOCAB + pointer] = 1;
		features[o + ID_VOCAB + PTR_VOCAB + payload] = 1;
	};
	for (let b = 0; b < batch; b++) {
		const base = b * CHASE_SEQ_LEN;
		const inst = instances[b];
		put(base, ID_BOS, PTR_BOS, PAY_BOS);
		inst.nodes.forEach((n, i) => put(base + 1 + i, n.id, n.pointer, n.payload));
		const q = base + CHASE_QUERY_POS;
		put(q, ID_NONE, inst.start, PAY_NONE);
		labels[q * CHASE_PAYLOADS + solveChase(inst).payload] = 1;
		weights[q] = 1;
	}
	return { batch, features, labels, weights, instances };
}

export function makeChaseBatch(rng: Rng, batch: number): ChaseBatch {
	return encodeChase(Array.from({ length: batch }, () => dealChase(rng)));
}
