/**
 * The panels' view of a number-mode run (ARITH_FORMAT): a Mealy register whose rows are [carry][a][b] → [carry′][sum
 * digit], one column of the two numbers per tick, the sum written least significant digit first. Pure functions over
 * a trace, so the panels stay thin and the layout is tested here.
 */
import type { ProgramRow, Trace, TraceStep } from './trace.ts';

export const isMealy = (t: Trace) => !!t.program.mealy;

/** The digit pair of column `i`: the step's own pair, else (before the tick) the tape the clock read ("6+7"). */
export function pairAt(t: Trace, i: number): [string, string] | null {
	const st = t.steps[i];
	if (st?.pair) return st.pair;
	const ev = t.llm?.file.input.events?.[i];
	if (!ev) return null;
	const k = ev.indexOf('+');
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
	/** the adder's rule for this edge when every row on it follows it (o = c + a + b − 10 c′), else null */
	rule: string | null;
}

const DIGIT = /^[0-9]$/;

/** The table's transitions merged per (carry, carry′), each with its rows and, when they all add, their rule. */
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
