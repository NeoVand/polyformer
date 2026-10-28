/**
 * REASON_FORMAT's clock beyond today's, ported line for line from research/reason/reason_core.py (branch `reason`,
 * ba619ecc): calls in the middle of a transcript. A call reads from two sources, the question (S0) and the notes (S1:
 * the response before the call with every `<program>…<exec/>` deleted); `locate` finds a quote pair over them, exact
 * first and then with whitespace relaxed, falling through S0 to S1; a number line may cite an earlier call's result
 * (`first: result 2`, the 2nd call that ran: an error line takes no number); a call that cannot run gets
 * `\n<final> error: <msg> </final>\n`, and so does an `<exec/>` with no new `<program>` since the last final; at most 8
 * calls run, and the 12th `<exec/>` ends the response (REASON_FORMAT §12 as of 28 Oct, 15:20 UTC). Π, the tick, the certificate and a run's final line are today's (pb.ts, arith.ts,
 * engine.ts). reason.spec.ts checks this file against the reference's fixtures (fixtures/reason.json).
 */
import { digitIds, digitPairs, readNumber } from './arith.ts';
import { pyFind, pyRepr, pyStrip, walk, type Program, type Tok } from './pb.ts';

/** §6: calls that run; an `<exec/>` beyond the 8th gets an error line, and the 12th ends the response */
export const MAX_CALLS = 8;
export const HARD_STOP_CALLS = 11;
export const TOO_MANY = 'too many calls';
/** §12.1: an `<exec/>` with no new `<program>` since the last final */
export const NO_PROGRAM = 'no program';

const PROGRAM_BLOCK = /<program>[\s\S]*?<exec\/>/g;
/** §12: the relaxed match's whitespace is ASCII, so Python and JS agree */
const WS = ' \t\n\r\f\v';
const isWs = (c: string) => c.length === 1 && WS.includes(c);

// ------------------------------------------------------------------ the sources (§3)

/** S1, the notes: the response so far with every <program>…<exec/> block deleted (the current call's too). */
export const notesOf = (responseText: string) => responseText.replace(PROGRAM_BLOCK, '');

/** [S0, S1]: the question, then the notes. */
export const sourcesOf = (question: string, responseText: string): [string, string] => [
	question,
	notesOf(responseText)
];

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\/-]/g, '\\$&');

/** The quote with every maximal run of ASCII whitespace matching any non-empty run of it; the rest literal. */
export function relaxedPattern(quote: string): RegExp {
	const parts = quote.match(/[ \t\n\r\f\v]+|[^ \t\n\r\f\v]+/g) ?? [];
	return new RegExp(
		parts.map((p) => (isWs(p[0]) ? '[ \\t\\n\\r\\f\\v]+' : escapeRe(p))).join(''),
		'g'
	);
}

export type How = 'exact' | 'relaxed';

/**
 * reason_core.match: [start, end, how] of the first exact occurrence of `quote` in `s` at or after `i`; only if there
 * is none, of the first whitespace-relaxed one.
 */
export function match(s: string, quote: string, i: number): [number, number, How] | null {
	const j = pyFind(s, quote, i);
	if (j >= 0) return [j, j + quote.length, 'exact'];
	if (![...quote].some(isWs)) return null;
	if (i > s.length) return null;
	const re = relaxedPattern(quote);
	re.lastIndex = i;
	const m = re.exec(s);
	return m ? [m.index, m.index + m[0].length, 'relaxed'] : null;
}

/** [source, start, end, how] */
export type Located = [number, number, number, How];

/**
 * reason_core.locate (§3): from source k0 at i0, the span after `before` and up to `after`. A `before` not found in
 * a source falls through to the next one (from its start); an `after` not found fails. The empty `before` means
 * "from here" (only in source k0), the empty `after` the end of that source. On S0 from (0, 0) with quotes that
 * occur exactly this is today's find_span.
 */
export function locate(
	sources: string[],
	before: string,
	after: string,
	frm: [number, number] = [0, 0]
): Located | null {
	const [k0, i0] = frm;
	for (let k = k0; k < sources.length; k++) {
		const s = sources[k];
		const i = k === k0 ? i0 : 0;
		let how: How = 'exact';
		let begin: number;
		if (before === '') {
			if (k !== k0) return null;
			begin = i;
		} else {
			const m = match(s, before, i);
			if (m === null) continue;
			begin = m[1];
			how = m[2];
		}
		let end: number;
		if (after === '') end = s.length;
		else {
			const m = match(s, after, begin);
			if (m === null) return null;
			end = m[0];
			if (m[2] === 'relaxed') how = 'relaxed';
		}
		return [k, begin, end, how];
	}
	return null;
}

// ------------------------------------------------------------------ calls, results, finals (§2, §5, §6)

/** Index of the token holding the '<' of the last '<program>' in `ids` (null if there is none). */
export function lastCallStart(tok: Tok, ids: number[]): number | null {
	for (let i = ids.length - 1; i >= 0; i--)
		if (tok.decode([ids[i]]).includes('<') && tok.decode(ids.slice(i, i + 6)).includes('<program>'))
			return i;
	return null;
}

/** §5: the value of a final line, the last `name=value` field stripped; null for an error line. */
export function resultValueOf(text: string): string | null {
	const open = text.indexOf('<final>');
	let inner = open >= 0 ? text.slice(open + '<final>'.length) : text;
	const close = inner.indexOf('</final>');
	if (close >= 0) inner = inner.slice(0, close);
	if (pyStrip(inner).startsWith('error:') || !inner.includes('=')) return null;
	return pyStrip(inner.slice(inner.lastIndexOf('=') + 1));
}

export const resultValue = (tok: Tok, finalIds: number[]) => resultValueOf(tok.decode(finalIds));

/** §6: the line the clock appends for a call it cannot run. */
export const errorFinalText = (msg: string) => `\n<final> error: ${msg} </final>\n`;
export const errorFinalIds = (tok: Tok, msg: string) => tok.encode(errorFinalText(msg));

/**
 * §12.1 (reason_core.clock_step): the text after the last `</final>` holds a `<program>` of its own. Without one the
 * `<exec/>` gets an error line and never re-runs an earlier program.
 */
export function hasNewProgram(responseText: string): boolean {
	const at = responseText.lastIndexOf('</final>');
	return (at < 0 ? responseText : responseText.slice(at + '</final>'.length)).includes('<program>');
}

/** Index of the token holding the '<' of the last '<exec/>' at or after `from` (`from` if there is none). */
export function lastExecStart(tok: Tok, ids: number[], from = 0): number {
	for (let i = ids.length - 1; i >= from; i--)
		if (tok.decode([ids[i]]).includes('<') && tok.decode(ids.slice(i, i + 6)).includes('<exec/>'))
			return i;
	return from;
}

/** The result numbers of calls in order: the k-th call that ran is result k; an error line takes none (§5, §12). */
export function resultNumbers(values: (string | null)[]): (number | null)[] {
	let n = 0;
	return values.map((v) => (v === null ? null : ++n));
}

/** What the clock does at an `<exec/>` after `calls` calls: run it, refuse it with an error line, or end. */
export function limitAt(calls: number): 'run' | 'too many' | 'end' {
	if (calls >= HARD_STOP_CALLS) return 'end';
	if (calls >= MAX_CALLS) return 'too many';
	return 'run';
}

// ------------------------------------------------------------------ the clock's reading of one call

/** Where a span was read: [source, start, end] (0 the question, 1 the notes), or a cited result. */
export type Span = [number, number, number] | ['result', number];

export interface CallReading {
	mode: 'tape' | 'numbers';
	error: string | null;
	spans: Span[];
	how: How[];
	/** [S0, S1] as the call saw them */
	sources: [string, string];
	/** tape mode: the event ids walked */
	tape?: number[];
	/** number mode: the two numbers read and the digit pairs fed */
	numbers?: [string, string];
	pairs?: [number, number][];
}

/**
 * reason_core.read_call: the clock's reading for one parsed call (parsed with `results: true`). `results` holds the
 * values of the earlier calls in order (null for one that ended in an error line); `result k` is the k-th that ran. Tape mode walks the span's tokens in the tokenisation of its own
 * source; number mode reads the first number from (0, 0) and the second from the end of the first, retrying once from
 * (0, 0); a cited result needs no locating.
 */
export function readCall(
	tok: Tok,
	question: string,
	responseText: string,
	prog: Program,
	results: (string | null)[]
): CallReading {
	const sources = sourcesOf(question, responseText);
	const out: CallReading = { mode: prog.mode, error: prog.error, spans: [], how: [], sources };
	if (prog.error) return out;
	if (prog.mode === 'tape') {
		const events = new Map<string, number>();
		for (const r of prog.registers)
			for (const [, e] of r.rows) events.set(pyStrip(tok.decode([e])), e);
		const loc = locate(sources, ...prog.anchors!);
		if (loc === null) {
			out.error = 'anchors not found in the prompt';
			return out;
		}
		const [k, b, e, how] = loc;
		out.spans.push([k, b, e]);
		out.how.push(how);
		const w = walk(tok, sources[k], [b, e], events.keys());
		if (w.names === null) {
			out.error = w.why;
			return out;
		}
		out.tape = w.names.map((n) => events.get(n)!);
		return out;
	}
	const nums: string[] = [];
	let frm: [number, number] = [0, 0];
	for (const which of ['first', 'second'] as const) {
		const cite = prog.cites?.[which];
		if (cite !== undefined) {
			// results are numbered by the calls that ran only (§12)
			const ok = results.filter((v): v is string => v !== null);
			const val = cite >= 1 && cite <= ok.length ? ok[cite - 1] : null;
			if (val === null) {
				out.error = `${which} number: no result ${cite}`;
				return out;
			}
			const n = readNumber(val);
			if (n === null) {
				out.error = `${which} number: not a number: ${pyRepr(val.slice(0, 40))}`;
				return out;
			}
			out.spans.push(['result', cite]);
			nums.push(n);
			continue;
		}
		const [before, after] = prog.numbers[which]!;
		let loc = locate(sources, before, after, frm);
		if (loc === null && which === 'second' && (frm[0] !== 0 || frm[1] !== 0))
			loc = locate(sources, before, after, [0, 0]);
		if (loc === null) {
			out.error = `${which} number: anchors not found in the prompt`;
			return out;
		}
		const [k, b, e, how] = loc;
		out.spans.push([k, b, e]);
		out.how.push(how);
		const text = sources[k].slice(b, e);
		const n = readNumber(text);
		if (n === null) {
			out.error = `${which} number: not a number: ${pyRepr(text.slice(0, 40))}`;
			return out;
		}
		nums.push(n);
		frm = [k, e];
	}
	const reg = prog.mealy[0];
	const firstEv = new Set(reg.rows.map((r) => r[1]));
	const secondEv = new Set(reg.rows.map((r) => r[2]));
	const digit = digitIds(tok);
	const pairs = digitPairs(nums[0], nums[1]).map(
		([a, b]) => [digit[Number(a)], digit[Number(b)]] as [number, number]
	);
	if (pairs.some(([a, b]) => !firstEv.has(a) || !secondEv.has(b))) {
		out.error = 'a digit is not an event of the table';
		return out;
	}
	out.numbers = [nums[0], nums[1]];
	out.pairs = pairs;
	return out;
}

// ------------------------------------------------------------------ the subtracter (§2), for the page's own check

/**
 * The table is the subtracter's: 200 rows, borrow and digits as bare digit tokens, d − 10·b′ = a − c − b, start 0.
 * The clock does not care which table it runs; this only names the table and lets the page check the value.
 */
export function isSubtracter(
	reg: { start: number; rows: [number, number, number, number, number][] },
	digit: number[]
): boolean {
	if (reg.start !== digit[0] || reg.rows.length !== 200) return false;
	const want = new Map<string, string>();
	for (let b = 0; b < 2; b++)
		for (let a = 0; a < 10; a++)
			for (let c = 0; c < 10; c++) {
				const v = a - c - b;
				want.set(
					`${digit[b]},${digit[a]},${digit[c]}`,
					`${digit[v < 0 ? 1 : 0]},${digit[((v % 10) + 10) % 10]}`
				);
			}
	return (
		reg.rows.every(([s, a, b, t, o]) => want.get(`${s},${a},${b}`) === `${t},${o}`) &&
		new Set(reg.rows.map(([s, a, b]) => `${s},${a},${b}`)).size === 200
	);
}

/**
 * The subtracter's value on two digit strings, exactly (the page's check, never the clock's): first − second when
 * first ≥ second; otherwise 10^columns − (second − first), which is what the table's outputs read backwards spell.
 */
export function exactDifference(n1: string, n2: string): string {
	const columns = BigInt(Math.max(n1.length, n2.length) + 1);
	const d = BigInt(n1) - BigInt(n2);
	return (d >= 0n ? d : 10n ** columns + d).toString();
}
