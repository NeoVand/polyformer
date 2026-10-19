/**
 * Feynman-style diagrams of Feynman attention: expand one token's computation tree from a
 * diagram probe, weight every path by the product of its option weights (its
 * "flow"), and lay it out with rounds as columns and tokens as rows.
 *
 * Rules, as drawn:
 *   leaf      a propagator from the token's own value v_t (round 0)
 *   hop       a propagator from Φ^{r−1}_j
 *   cubic     a trivalent vertex joining Φ^{r−1}_j and Φ^{r−1}_k
 *   exchange  Φ^{r−1}_j meets a wavy line from a virtual mode Ψ^r_m, whose far
 *             vertex binds the pair Φ^{r−1}_k ⊙ Φ^{r−1}_l
 *   carry     a dashed line from Φ^{r−1}_t: the state is kept as it was
 *
 * Pure functions, so the layout is testable and the ideal constructions can
 * stand in before a model has trained.
 */
import type {
	DiagramHead,
	DiagramMode,
	DiagramSector,
	DiagramState,
	SectorMass
} from '#lib/engine/protocol.ts';
import { solveChase, type ChaseInstance } from '#lib/chase/chase.ts';
import { findSets, type Card } from '#lib/set/cards.ts';

export interface StateNode {
	key: string;
	token: number;
	round: number;
	flow: number;
	x: number;
	y: number;
}

export interface Vertex {
	id: string;
	term: number;
	kind: 'cubic' | 'exchange' | 'mode';
	round: number;
	flow: number;
	x: number;
	y: number;
	/** The mode index, for exchange and mode vertices. */
	m?: number;
}

export interface Edge {
	id: string;
	sector: DiagramSector | 'mode' | 'out';
	style: 'line' | 'wavy' | 'dashed';
	/** Round of the state this edge feeds (R + 1 for the output leg). */
	round: number;
	flow: number;
	d: string;
	/** Index into `terms`, or −1 for the output leg. */
	term: number;
	/** Endpoints, for the mid-line arrow. */
	from: [number, number];
	to: [number, number];
}

/** One term of the root's expansion: what a state at round r read, and how much. */
export interface Term {
	sector: DiagramSector;
	round: number;
	token: number;
	flow: number;
	j?: number;
	k?: number;
	m?: number;
	pair?: [number, number];
}

export interface FeynmanLayout {
	width: number;
	height: number;
	rounds: number;
	columns: { round: number; x: number }[];
	rows: { token: number; y: number }[];
	nodes: StateNode[];
	vertices: Vertex[];
	edges: Edge[];
	terms: Term[];
	root: StateNode;
}

export interface ExpandOptions {
	/** Drop paths whose flow falls below this. */
	threshold?: number;
	/** Keep at most this many states per round (heaviest first). */
	perRound?: number;
	/** Pairs per virtual mode to draw. */
	pairsPerMode?: number;
}

/** Expand the root's tree: per round, the states it needs and the terms that feed them. */
export function expand(
	head: DiagramHead,
	n: number,
	rounds: number,
	modes: number,
	root: number,
	opts: ExpandOptions = {}
): { levels: Map<number, number>[]; terms: Term[] } {
	const { threshold = 0.02, perRound = 9, pairsPerMode = 2 } = opts;
	const levels: Map<number, number>[] = Array.from({ length: rounds + 1 }, () => new Map());
	const add = (r: number, t: number, f: number) => levels[r].set(t, (levels[r].get(t) ?? 0) + f);
	levels[rounds].set(root, 1);
	const terms: Term[] = [];
	for (let r = rounds; r >= 1; r--) {
		const here = [...levels[r]].sort((a, b) => b[1] - a[1]).slice(0, perRound);
		levels[r] = new Map(here);
		for (const [t, f] of here) {
			const st: DiagramState | undefined = head.states[(r - 1) * n + t];
			if (!st) continue;
			const leaf = f * st.sectors.leaf;
			if (leaf >= threshold) {
				terms.push({ sector: 'leaf', round: r, token: t, flow: leaf });
				add(0, t, leaf);
			}
			for (const h of st.hops) {
				const fw = f * h.weight;
				if (fw < threshold) continue;
				terms.push({ sector: 'hop', round: r, token: t, flow: fw, j: h.j });
				add(r - 1, h.j, fw);
			}
			for (const c of st.cubic) {
				const fw = f * c.weight;
				if (fw < threshold) continue;
				terms.push({ sector: 'cubic', round: r, token: t, flow: fw, j: c.j, k: c.k });
				add(r - 1, c.j, fw);
				add(r - 1, c.k, fw);
			}
			for (const e of st.exchanges) {
				const fw = f * e.weight;
				if (fw < threshold) continue;
				const mode: DiagramMode | undefined = head.modes[(r - 1) * modes + e.m];
				const pair = mode?.pairs[0];
				terms.push({
					sector: 'exchange',
					round: r,
					token: t,
					flow: fw,
					j: e.j,
					m: e.m,
					pair: pair ? [pair.k, pair.l] : undefined
				});
				add(r - 1, e.j, fw);
				for (const p of mode?.pairs.slice(0, pairsPerMode) ?? []) {
					const pw = fw * p.weight;
					if (pw < threshold) continue;
					add(r - 1, p.k, pw);
					add(r - 1, p.l, pw);
				}
			}
			const carry = f * st.sectors.carry;
			if (carry >= threshold) {
				terms.push({ sector: 'carry', round: r, token: t, flow: carry });
				add(r - 1, t, carry);
			}
		}
	}
	levels[0] = new Map([...levels[0]].sort((a, b) => b[1] - a[1]).slice(0, perRound + 3));
	return { levels, terms };
}

/**
 * Rows by depth: tokens whose states are read in later rounds sit higher, so flow
 * climbs from the values (bottom left) to the probed state (top right) without
 * folding back. Ties go to the heavier token.
 */
function rowOrder(levels: Map<number, number>[], root: number): number[] {
	const weight = new Map<number, number>();
	const depth = new Map<number, number>();
	levels.forEach((level, r) => {
		for (const [t, f] of level) {
			weight.set(t, (weight.get(t) ?? 0) + f);
			depth.set(t, (depth.get(t) ?? 0) + f * r);
		}
	});
	const mean = (t: number) => (depth.get(t) ?? 0) / (weight.get(t) || 1);
	return [...weight.keys()].sort((a, b) =>
		a === root ? -1 : b === root ? 1 : mean(b) - mean(a) || weight.get(b)! - weight.get(a)!
	);
}

const f1 = (v: number) => v.toFixed(1);

/** A propagator: a straight segment, as in a textbook diagram. */
export const line = (x1: number, y1: number, x2: number, y2: number) =>
	`M${f1(x1)},${f1(y1)} L${f1(x2)},${f1(y2)}`;

/**
 * A photon: a smooth sine along the segment, built from cubic Bézier half-waves
 * (the control points of a sine arch sit at 0.3642 of its width and 4/3 its height).
 */
export function photon(
	x1: number,
	y1: number,
	x2: number,
	y2: number,
	amp = 3.2,
	wave = 10
): string {
	const len = Math.hypot(x2 - x1, y2 - y1) || 1;
	const ux = (x2 - x1) / len;
	const uy = (y2 - y1) / len;
	const halves = Math.max(2, Math.round((2 * len) / wave));
	const h = len / halves;
	const at = (u: number, a: number) => [x1 + ux * u - uy * a, y1 + uy * u + ux * a];
	let d = `M${f1(x1)},${f1(y1)}`;
	for (let i = 0; i < halves; i++) {
		const s = i % 2 === 0 ? 1 : -1;
		const u0 = i * h;
		const [c1x, c1y] = at(u0 + h * 0.3642, s * amp * 1.3333);
		const [c2x, c2y] = at(u0 + h * 0.6358, s * amp * 1.3333);
		const [ex, ey] = at(u0 + h, 0);
		d += ` C${f1(c1x)},${f1(c1y)} ${f1(c2x)},${f1(c2y)} ${f1(ex)},${f1(ey)}`;
	}
	return d;
}

export interface LayoutBox {
	width: number;
	height: number;
	/** Room on the left for token labels and on the right for the output leg. */
	padLeft?: number;
	padRight?: number;
	padTop?: number;
	padBottom?: number;
	/** Largest row pitch, so diagrams side by side can share one. */
	maxRow?: number;
	/** Rows hang from the top, or sit centred in the room left over. */
	valign?: 'top' | 'center';
}

/** Lay the expansion out: columns are rounds 0…R, rows are tokens; every edge is straight. */
export function layoutDiagram(
	head: DiagramHead,
	n: number,
	rounds: number,
	modes: number,
	root: number,
	box: LayoutBox,
	opts: ExpandOptions = {}
): FeynmanLayout {
	const {
		width,
		height,
		padLeft = 120,
		padRight = 90,
		padTop = 44,
		padBottom = 20,
		maxRow = 58,
		valign = 'center'
	} = box;
	const { levels, terms } = expand(head, n, rounds, modes, root, opts);
	const order = rowOrder(levels, root);
	const room = height - padTop - padBottom;
	const rowH = Math.min(maxRow, room / Math.max(order.length, 1));
	const top = padTop + (valign === 'top' ? 0 : (room - rowH * order.length) / 2);
	const yOf = new Map(order.map((t, i) => [t, top + (i + 0.5) * rowH]));
	const cw = (width - padLeft - padRight) / Math.max(rounds, 1);
	const xOf = (r: number) => padLeft + r * cw;

	const nodes = new Map<string, StateNode>();
	levels.forEach((level, r) => {
		for (const [t, f] of level) {
			const key = `${t}@${r}`;
			nodes.set(key, { key, token: t, round: r, flow: f, x: xOf(r), y: yOf.get(t)! });
		}
	});
	const node = (t: number, r: number) => nodes.get(`${t}@${r}`);

	const vertices: Vertex[] = [];
	const edges: Edge[] = [];
	type P = { x: number; y: number };
	const push = (
		term: number,
		id: string,
		sector: Edge['sector'],
		style: Edge['style'],
		t: Term,
		a: P,
		b: P
	) =>
		edges.push({
			id,
			term,
			sector,
			style,
			round: t.round,
			flow: t.flow,
			d: style === 'wavy' ? photon(a.x, a.y, b.x, b.y) : line(a.x, a.y, b.x, b.y),
			from: [a.x, a.y],
			to: [b.x, b.y]
		});
	terms.forEach((term, idx) => {
		const to = node(term.token, term.round);
		if (!to) return;
		const id = `${term.sector}-${idx}`;
		if (term.sector === 'leaf') {
			const from = node(term.token, 0);
			if (from) push(idx, id, 'leaf', 'line', term, from, to);
		} else if (term.sector === 'carry') {
			const from = node(term.token, term.round - 1);
			if (from) push(idx, id, 'carry', 'dashed', term, from, to);
		} else if (term.sector === 'hop') {
			const from = node(term.j!, term.round - 1);
			if (from) push(idx, id, 'hop', 'line', term, from, to);
		} else if (term.sector === 'cubic') {
			const a = node(term.j!, term.round - 1);
			const b = node(term.k!, term.round - 1);
			if (!a || !b) return;
			const v = { x: to.x - cw * 0.45, y: 0.55 * ((a.y + b.y) / 2) + 0.45 * to.y };
			vertices.push({ id, term: idx, kind: 'cubic', round: term.round, flow: term.flow, ...v });
			push(idx, `${id}-j`, 'cubic', 'line', term, a, v);
			push(idx, `${id}-k`, 'cubic', 'line', term, b, v);
			push(idx, `${id}-o`, 'cubic', 'line', term, v, to);
		} else if (term.sector === 'exchange') {
			const a = node(term.j!, term.round - 1);
			if (!a) return;
			const v1 = { x: to.x - cw * 0.32, y: (a.y + to.y) / 2 };
			vertices.push({
				id,
				term: idx,
				kind: 'exchange',
				round: term.round,
				flow: term.flow,
				...v1,
				m: term.m
			});
			push(idx, `${id}-j`, 'exchange', 'line', term, a, v1);
			push(idx, `${id}-o`, 'exchange', 'line', term, v1, to);
			const k = term.pair && node(term.pair[0], term.round - 1);
			const l = term.pair && node(term.pair[1], term.round - 1);
			if (k && l) {
				const v2 = { x: to.x - cw * 0.62, y: (k.y + l.y) / 2 };
				if (Math.abs(v2.y - v1.y) < rowH * 0.6) v2.y += v2.y >= v1.y ? rowH * 0.7 : -rowH * 0.7;
				vertices.push({
					term: idx,
					id: `${id}-mode`,
					kind: 'mode',
					round: term.round,
					flow: term.flow,
					...v2,
					m: term.m
				});
				push(idx, `${id}-w`, 'exchange', 'wavy', term, v2, v1);
				push(idx, `${id}-k`, 'mode', 'line', term, k, v2);
				push(idx, `${id}-l`, 'mode', 'line', term, l, v2);
			}
		}
	});
	const rootNode = node(root, rounds)!;
	const outEnd = { x: rootNode.x + Math.min(64, padRight * 0.45), y: rootNode.y };
	edges.push({
		id: 'out',
		term: -1,
		sector: 'out',
		style: 'line',
		round: rounds + 1,
		flow: 1,
		d: line(rootNode.x, rootNode.y, outEnd.x, outEnd.y),
		from: [rootNode.x, rootNode.y],
		to: [outEnd.x, outEnd.y]
	});
	edges.sort((a, b) => a.flow - b.flow);

	return {
		width,
		height,
		rounds,
		columns: Array.from({ length: rounds + 1 }, (_, r) => ({ round: r, x: xOf(r) })),
		rows: order.map((t) => ({ token: t, y: yOf.get(t)! })),
		nodes: [...nodes.values()],
		vertices,
		edges,
		terms,
		root: rootNode
	};
}

// ── ideal constructions ──────────────────────────────────────────────────────

const mass = (m: Partial<SectorMass>): SectorMass => ({
	leaf: 0,
	hop: 0,
	cubic: 0,
	exchange: 0,
	carry: 0,
	...m
});

const blank = (token: number, round: number): DiagramState => ({
	token,
	round,
	sectors: mass({ carry: 1 }),
	hops: [],
	cubic: [],
	exchanges: []
});

/**
 * The computation a perfect Feynman attention performs on pointer chasing: every node's state
 * at round r is the payload r steps down its list (a hop to its successor, or a
 * carry once it is the terminal); the query hops to its start node each round.
 * Positions: 0 is BOS, 1…12 the nodes, 13 the query.
 */
export function idealChase(inst: ChaseInstance, rounds = 4): DiagramHead {
	const n = inst.nodes.length + 2;
	const q = n - 1;
	const byId = new Map(inst.nodes.map((node, i) => [node.id, i + 1]));
	const states: DiagramState[] = [];
	for (let r = 1; r <= rounds; r++)
		for (let t = 0; t < n; t++) {
			if (t === 0) {
				states.push(blank(t, r));
				continue;
			}
			if (t === q) {
				const s = byId.get(inst.start)!;
				states.push({ ...blank(t, r), sectors: mass({ hop: 1 }), hops: [{ j: s, weight: 1 }] });
				continue;
			}
			const next = byId.get(inst.nodes[t - 1].pointer)!;
			if (next !== t)
				states.push({ ...blank(t, r), sectors: mass({ hop: 1 }), hops: [{ j: next, weight: 1 }] });
			else states.push({ ...blank(t, r), sectors: mass(r === 1 ? { leaf: 1 } : { carry: 1 }) });
		}
	return { head: 0, query: states.slice(-1), states, modes: [] };
}

/**
 * The computation a perfect Feynman attention performs on SET membership: at round 1 each
 * card reads the product of its two SET partners through a cubic vertex (split
 * evenly over the SETs it is in), or its own value if it is in none; later
 * rounds carry. Positions: 0 is BOS, 1…12 the cards.
 */
export function idealSet(layout: readonly Card[], rounds = 2): DiagramHead {
	const n = layout.length + 1;
	const sets = findSets(layout);
	const states: DiagramState[] = [];
	for (let r = 1; r <= rounds; r++)
		for (let t = 0; t < n; t++) {
			if (t === 0 || r > 1) {
				states.push(blank(t, r));
				continue;
			}
			const mine = sets.filter((s) => s.includes(t - 1));
			if (!mine.length) {
				states.push({ ...blank(t, r), sectors: mass({ leaf: 1 }) });
				continue;
			}
			const cubic = mine.map((s) => {
				const [j, k] = s.filter((c) => c !== t - 1);
				return { j: j + 1, k: k + 1, weight: 1 / mine.length };
			});
			states.push({ ...blank(t, r), sectors: mass({ cubic: 1 }), cubic });
		}
	return { head: 0, query: [], states, modes: [] };
}

/** The pointer-chase path as sequence positions, for highlighting. */
export function chasePath(inst: ChaseInstance): number[] {
	return solveChase(inst).path.map((i) => i + 1);
}

const LADDER = [0.1, 0.06, 0.04, 0.03, 0.02, 0.014, 0.01, 0.007, 0.005, 0.0035, 0.0025];

/**
 * The largest prune threshold whose tree still has at least `terms` terms, so a
 * trained head whose mass is spread over many small options still draws a full
 * diagram, and a sharp one stays uncluttered.
 */
export function autoThreshold(
	head: DiagramHead,
	n: number,
	rounds: number,
	modes: number,
	root: number,
	terms = 14
): number {
	for (const t of LADDER)
		if (expand(head, n, rounds, modes, root, { threshold: t }).terms.length >= terms) return t;
	return LADDER[LADDER.length - 1];
}

/** Total flow a head's tree puts on the given tokens (e.g. the true path), at a fine threshold. */
export function flowOn(
	head: DiagramHead,
	n: number,
	rounds: number,
	modes: number,
	root: number,
	tokens: number[]
): number {
	const want = new Set(tokens);
	const { levels } = expand(head, n, rounds, modes, root, { threshold: 0.005, perRound: 14 });
	let s = 0;
	levels.forEach((level, r) => {
		if (r === rounds) return;
		for (const [t, f] of level) if (want.has(t)) s += f;
	});
	return s;
}
