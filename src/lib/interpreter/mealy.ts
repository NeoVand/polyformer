/**
 * The panels' view of a number-mode run (ARITH_FORMAT): a Mealy register whose rows are [carry][a][b] → [carry′][sum
 * digit], one column of the two numbers per tick, the sum written least significant digit first. Pure functions over
 * a trace, so the panels stay thin and the layout is tested here.
 */
import type { ProgramRow, Trace, TraceStep } from './trace.ts';

export const isMealy = (t: Trace) => !!t.program.mealy;

const DIGIT = /^[0-9]$/;

/**
 * Which digit table a Mealy register's rows spell (REASON_FORMAT §2): the adder's (c′·10 + s = c + a + b) or the
 * subtracter's (d − 10·b′ = a − c − b), or neither. The clock runs any table; this only names its parts.
 */
export function opOfRows(rows: ProgramRow[]): 'add' | 'sub' | null {
	if (!rows.length) return null;
	const n = (x: string | undefined) => (x !== undefined && DIGIT.test(x) ? Number(x) : NaN);
	const all = (f: (s: number, a: number, b: number, t: number, o: number) => boolean) =>
		rows.every((r) => f(n(r.s), n(r.a), n(r.b), n(r.t), n(r.o)));
	if (all((s, a, b, t, o) => s <= 1 && t * 10 + o === s + a + b)) return 'add';
	if (all((s, a, b, t, o) => s <= 1 && t <= 1 && o - 10 * t === a - b - s)) return 'sub';
	return null;
}

/** The register's table: the run's own record of it, else read from its rows. */
export const opOf = (t: Trace) => t.llm?.file.arith?.op ?? opOfRows(t.program.rows);

/**
 * What a number-mode run's parts are called: a carry and a sum for the adder (and, as before, for any other table),
 * a borrow and a difference for the subtracter.
 */
export function mealyWords(t: Trace) {
	return opOf(t) === 'sub'
		? { state: 'borrow', states: 'borrows', out: 'difference', sign: '−' }
		: { state: 'carry', states: 'carries', out: 'sum', sign: '+' };
}

/** The digit pair of column `i`: the step's own pair, else (before the tick) the tape the clock read ("6+7", "6−7"). */
export function pairAt(t: Trace, i: number): [string, string] | null {
	const st = t.steps[i];
	if (st?.pair) return st.pair;
	const ev = t.llm?.file.input.events?.[i];
	if (!ev) return null;
	const k = ev.search(/[+−]/);
	return k > 0 ? [ev.slice(0, k), ev.slice(k + 1)] : null;
}

export interface Column {
	/** the column, 0 for the units */
	i: number;
	a: string;
	b: string;
	/** the digit is the clock's padding: the number is shorter than this column (or it is the last 0 0 pair) */
	padA: boolean;
	padB: boolean;
	/** the carry into this column, once known: the run's state before its tick (the start for column 0) */
	cin: string | null;
	/** the sum digit written at this column, once its tick has run */
	o: string | null;
	done: boolean;
	now: boolean;
}

/**
 * The columns in view, highest on the left as the sum is written by hand: `width` columns around the playhead's,
 * kept inside the run. `at` is the playhead's column (-1 before the first tick, while certifying).
 */
export function columnsAround(t: Trace, at: number, width: number): Column[] {
	const total = t.llm?.file.input.events?.length ?? t.steps.length;
	const [n1, n2] = t.llm?.file.arith?.numbers ?? ['', ''];
	const lo = Math.max(0, Math.min(at - Math.floor(width / 2), total - width));
	const out: Column[] = [];
	for (let i = Math.min(total, lo + width) - 1; i >= lo; i--) {
		const p = pairAt(t, i);
		if (!p) continue;
		const st = t.steps[i];
		const done = !!st && i <= at;
		out.push({
			i,
			a: p[0],
			b: p[1],
			padA: !!n1 && i >= n1.length,
			padB: !!n2 && i >= n2.length,
			cin:
				i <= at
					? (st?.s ?? null)
					: i === at + 1
						? at < 0
							? t.program.start
							: (t.steps[at]?.t ?? null)
						: null,
			o: done ? (st.o ?? null) : null,
			done,
			now: i === at
		});
	}
	return out;
}

/** The output tape up to the playhead's column, as the number reads: the newest digit first (leftmost). */
export function sumSoFar(
	steps: TraceStep[],
	at: number
): { newest: string; rest: string; digits: number } {
	const outs: string[] = [];
	for (let i = Math.min(at, steps.length - 1); i >= 0; i--) outs.push(steps[i].o ?? '?');
	return { newest: outs[0] ?? '', rest: outs.slice(1).join(''), digits: outs.length };
}

/** The row read at a step, as the table writes it: "c a b → c′ o". */
export const mealyRowText = (r: ProgramRow | undefined) =>
	r ? `${r.s} ${r.a} ${r.b} → ${r.t} ${r.o}` : '';

export interface MealyEdge {
	key: string;
	from: number;
	to: number;
	rows: number;
	/**
	 * the edge's rule when every row on it follows the adder's (o = c + a + b − 10 c′) or the subtracter's
	 * (d = a − c − b + 10 b′), else null
	 */
	rule: string | null;
}

/**
 * The table's transitions merged per (carry, carry′), each with its rows and, when they all add (or all subtract),
 * their rule.
 */
export function mealyEdges(rows: ProgramRow[], states: string[]): MealyEdge[] {
	const index = new Map(states.map((s, i) => [s, i]));
	const m = new Map<string, { from: number; to: number; rows: ProgramRow[] }>();
	for (const r of rows) {
		const from = index.get(r.s);
		const to = index.get(r.t);
		if (from === undefined || to === undefined) continue;
		const key = `${from}>${to}`;
		const e = m.get(key) ?? { from, to, rows: [] };
		e.rows.push(r);
		m.set(key, e);
	}
	return [...m.entries()].map(([key, e]) => ({
		key,
		from: e.from,
		to: e.to,
		rows: e.rows.length,
		rule: ruleOf(e.rows)
	}));
}

function ruleOf(rows: ProgramRow[]): string | null {
	return addRule(rows) ?? subRule(rows);
}

const signed = (n: number) => (n < 0 ? `−${-n}` : `${n}`);

/** The subtracter's rule for an edge: borrow b to b′ when a − c − b is negative or not, writing a − c − b + 10 b′. */
function subRule(rows: ProgramRow[]): string | null {
	const r0 = rows[0];
	if (!r0) return null;
	const b = Number(r0.s);
	const b2 = Number(r0.t);
	let lo = Infinity;
	let hi = -Infinity;
	for (const r of rows) {
		if (![r.s, r.a, r.b, r.t, r.o].every((x) => x !== undefined && DIGIT.test(x))) return null;
		const diff = Number(r.a) - Number(r.b);
		if (Number(r.s) !== b || Number(r.t) !== b2 || b > 1 || b2 > 1) return null;
		if (diff - b + 10 * b2 !== Number(r.o) || diff - b < 0 !== (b2 === 1)) return null;
		lo = Math.min(lo, diff);
		hi = Math.max(hi, diff);
	}
	const off = 10 * b2 - b;
	const out = off === 0 ? 'a−b' : off > 0 ? `a−b+${off}` : `a−b−${-off}`;
	return `${b2 ? `a−b ≤ ${signed(hi)}` : `a−b ≥ ${signed(lo)}`} / ${out}`;
}

function addRule(rows: ProgramRow[]): string | null {
	const r0 = rows[0];
	if (!r0) return null;
	const c = Number(r0.s);
	const c2 = Number(r0.t);
	let lo = Infinity;
	let hi = -Infinity;
	for (const r of rows) {
		if (![r.s, r.a, r.b, r.t, r.o].every((x) => x !== undefined && DIGIT.test(x))) return null;
		const sum = Number(r.a) + Number(r.b);
		if (Number(r.s) !== c || Number(r.t) !== c2) return null;
		if (c > 1 || c2 > 1 || c + sum - 10 * c2 !== Number(r.o)) return null;
		if (c + sum >= 10 !== (c2 === 1)) return null;
		lo = Math.min(lo, sum);
		hi = Math.max(hi, sum);
	}
	const off = c - 10 * c2;
	const out = off === 0 ? 'a+b' : off > 0 ? `a+b+${off}` : `a+b−${-off}`;
	return `${c2 ? `a+b ≥ ${lo}` : `a+b ≤ ${hi}`} / ${out}`;
}

export interface CertCell {
	k: number;
	x: number;
	y: number;
}

/**
 * Where each row of a Mealy certificate sits: one block per carry, the first digit down and the second across (two
 * 10 × 10 blocks for the adder), in units of one cell. Rows outside that shape fall back to reading order.
 */
export function certLayout(
	rows: ProgramRow[],
	states: string[]
): { cells: CertCell[]; cols: number; height: number; blocks: { x: number; label: string }[] } {
	const as = [...new Set(rows.map((r) => r.a ?? ''))].sort();
	const bs = [...new Set(rows.map((r) => r.b))].sort();
	const si = new Map(states.map((s, i) => [s, i]));
	const ai = new Map(as.map((a, i) => [a, i]));
	const bi = new Map(bs.map((b, i) => [b, i]));
	const gap = 1;
	const grid = states.length * as.length * bs.length;
	const seen = new Set<string>();
	const fits =
		grid === rows.length &&
		rows.every((r) => {
			const key = `${r.s}\u0000${r.a}\u0000${r.b}`;
			if (seen.has(key) || !si.has(r.s)) return false;
			seen.add(key);
			return true;
		});
	if (!fits) {
		const cols = Math.max(10, Math.ceil(Math.sqrt(rows.length * 2)));
		return {
			cells: rows.map((_, k) => ({ k, x: k % cols, y: Math.floor(k / cols) })),
			cols,
			height: Math.ceil(rows.length / cols),
			blocks: []
		};
	}
	const w = bs.length;
	return {
		cells: rows.map((r, k) => ({
			k,
			x: si.get(r.s)! * (w + gap) + bi.get(r.b)!,
			y: ai.get(r.a ?? '')!
		})),
		cols: states.length * (w + gap) - gap,
		height: as.length,
		blocks: states.map((s, i) => ({ x: i * (w + gap), label: s }))
	};
}
