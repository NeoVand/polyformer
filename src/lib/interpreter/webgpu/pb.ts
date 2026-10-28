/**
 * PROMPTBOX's clock, ported line for line from the Python that decides every answer on the recorded and server runs
 * (research/demolive/vendor at 71268f94: pb_loop.lines_of, parse_generated, clock_tape; pb_lit.item_span, anchors,
 * find_span, walk; pb_pin.top2; dl_core's names, character spans and `<final>` line; pb_data.chat_prompt). The
 * fixtures in ./fixtures/reference.json hold what the Python computes for real program ids and questions, and
 * pb.spec.ts checks this file against them.
 *
 * Strings are indexed in UTF-16 code units where the Python indexes code points; the two agree on any text without
 * characters outside the Basic Multilingual Plane, and the rules below are the same either way.
 */

/** The tokenizer as the clock uses it: Qwen3's, with the Python `tokenizers` defaults. */
export interface Tok {
	/** ids of `text`, no special tokens added (`tok.encode(text, add_special_tokens=False).ids`) */
	encode(text: string): number[];
	/** ids and [start, end) offsets of each token in `text` (offsets untrimmed, as Qwen3's byte-level tokenizer) */
	encodeWithOffsets(text: string): { ids: number[]; offsets: [number, number][] };
	/** `tok.decode(ids)`: special tokens skipped, no clean-up */
	decode(ids: number[]): string;
}

export interface Register {
	name: string;
	start: number;
	rows: [number, number, number][];
	pi: number[];
}

/** ARITH_FORMAT's Mealy register: rows [s][a][b][t][o], from state s on the digit pair (a, b) to t, writing o. */
export interface MealyRegister {
	name: string;
	/** the output's name, from `register <name> (output <output>): start <s>` */
	output: string;
	start: number;
	rows: [number, number, number, number, number][];
	pi: number[];
}

export interface Program {
	/** PROMPTBOX's Moore registers (tape mode) */
	registers: Register[];
	anchors: [string, string] | null;
	error: string | null;
	/** ARITH_FORMAT: `numbers` when any `first:` or `second:` line was written */
	mode: 'tape' | 'numbers';
	/** the Mealy registers, in number mode exactly one */
	mealy: MealyRegister[];
	/** the `first:` and `second:` quotes (null where the line did not parse) */
	numbers: { first?: [string, string] | null; second?: [string, string] | null };
	/**
	 * REASON_FORMAT §2: `first: result k` / `second: result k`, a number cited from call k's result. Parsed only when
	 * asked for (`results: true`, the multi-call loop); a later line of the same name replaces an earlier one.
	 */
	cites?: { first?: number; second?: number };
}

export const SYSTEMLESS_TEMPLATE =
	'<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n';

/** pb_data.chat_prompt */
export const chatPrompt = (question: string) => SYSTEMLESS_TEMPLATE.replace('{q}', () => question);

// ------------------------------------------------------------------ Python string semantics

/** Python's str.isspace set (str.strip() with no argument strips these). */
const PY_SPACE = new Set(
	'\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000'
);
export const isPySpace = (c: string) => PY_SPACE.has(c);

export function pyLstrip(s: string): string {
	let i = 0;
	while (i < s.length && PY_SPACE.has(s[i])) i++;
	return s.slice(i);
}
export function pyRstrip(s: string): string {
	let j = s.length;
	while (j > 0 && PY_SPACE.has(s[j - 1])) j--;
	return s.slice(0, j);
}
export const pyStrip = (s: string) => pyRstrip(pyLstrip(s));

/** str.strip(chars) */
export function stripChars(s: string, chars: string): string {
	let i = 0;
	let j = s.length;
	while (i < j && chars.includes(s[i])) i++;
	while (j > i && chars.includes(s[j - 1])) j--;
	return s.slice(i, j);
}

/** Python's str.isprintable: no character in Cc, Cf, Cs, Co, Cn, Zl, Zp or Zs other than the ASCII space. */
export function isPrintable(s: string): boolean {
	for (const c of s) {
		if (c === ' ') continue;
		if (/[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{Zl}\p{Zp}\p{Zs}]/u.test(c)) return false;
	}
	return true;
}

/** json.dumps(s) with Python's defaults (ensure_ascii): everything outside space..tilde escaped. */
export function pyJsonDumps(s: string): string {
	let out = '"';
	for (let i = 0; i < s.length; i++) {
		const c = s[i];
		const code = s.charCodeAt(i);
		if (c === '"') out += '\\"';
		else if (c === '\\') out += '\\\\';
		else if (c === '\n') out += '\\n';
		else if (c === '\r') out += '\\r';
		else if (c === '\t') out += '\\t';
		else if (c === '\b') out += '\\b';
		else if (c === '\f') out += '\\f';
		else if (code < 0x20 || code > 0x7e) out += '\\u' + code.toString(16).padStart(4, '0');
		else out += c;
	}
	return out + '"';
}

/** str.count: non-overlapping occurrences. */
export function pyCount(s: string, sub: string): number {
	if (!sub) return s.length + 1;
	let n = 0;
	let at = s.indexOf(sub);
	while (at >= 0) {
		n++;
		at = s.indexOf(sub, at + sub.length);
	}
	return n;
}

/** str.find(sub, start) with Python's clamping. */
export function pyFind(s: string, sub: string, start = 0): number {
	if (start > s.length) return -1;
	return s.indexOf(sub, Math.max(0, start));
}

// ------------------------------------------------------------------ the program (pb_loop)

/** Token lines: a line ends at any token whose text contains a newline; a bare newline token is dropped. */
export function linesOf(tok: Tok, ids: number[], nl: number): number[][] {
	const out: number[][] = [];
	let cur: number[] = [];
	for (const t of ids) {
		if (t === nl) {
			out.push(cur);
			cur = [];
		} else if (tok.decode([t]).includes('\n')) {
			out.push([...cur, t]);
			cur = [];
		} else cur.push(t);
	}
	out.push(cur);
	return out;
}

const QUOTE = '("(?:[^"\\\\]|\\\\.)*")';
const TAPE_RE = /^tape: after ("(?:[^"\\]|\\.)*") until ("(?:[^"\\]|\\.)*")\s*$/u;
const NUMBER_LINE_RE = new RegExp(`^(first|second): after ${QUOTE} until ${QUOTE}\\s*$`, 'u');
/** REASON_FORMAT §2 (reason_core.RESULT_LINE_RE) */
const RESULT_LINE_RE = /^(first|second): result ([0-9]+)\s*$/u;
const REGISTER_RE = /^register ([\p{L}\p{N}_]+): start/u;
const MEALY_RE = /^register ([\p{L}\p{N}_]+) \(output ([\p{L}\p{N}_]+)\): start/u;
/** ARITH_FORMAT: a Mealy row is [s][a][b][t][o]; a Moore row (PROMPTBOX) is [s][e][t] */
export const MEALY_ROW = 5;

/** Python's json.loads on a quoted string, or undefined where it raises. */
function jsonString(q: string): string | undefined {
	try {
		const v = JSON.parse(q);
		return typeof v === 'string' ? v : undefined;
	} catch {
		return undefined;
	}
}

/**
 * The model's program, read from its token ids (pb_loop.parse_generated, extended by ARITH_FORMAT §2 as
 * arith_core.parse_generated). Tape mode is PROMPTBOX's, unchanged: Moore registers with 3-token rows and a `tape:`
 * line. Number mode (any `first:` or `second:` line) runs exactly one Mealy register with 5-token rows. With
 * `results` (REASON_FORMAT's calls, reason_core.parse_call) a number line may also be `first: result <k>`.
 */
export function parseGenerated(
	tok: Tok,
	ids: number[],
	nl: number,
	opts: { results?: boolean } = {}
): Program {
	type Any = (Register & { kind: 'moore' }) | (MealyRegister & { kind: 'mealy' });
	const regs: Any[] = [];
	let anchors: [string, string] | null = null;
	const numbers: Program['numbers'] = {};
	const cites: NonNullable<Program['cites']> = {};
	let err: string | null = null;
	let openRows = 0;
	for (const line of linesOf(tok, ids, nl)) {
		const text = stripChars(tok.decode(line), '\n');
		if (text.startsWith('tape:')) {
			const m = TAPE_RE.exec(text);
			anchors = null;
			if (m) {
				const a = jsonString(m[1]);
				const b = jsonString(m[2]);
				anchors = a !== undefined && b !== undefined ? [a, b] : null;
			}
		} else if (text.startsWith('first:') || text.startsWith('second:')) {
			const which = text.slice(0, text.indexOf(':')) as 'first' | 'second';
			const cite = opts.results ? RESULT_LINE_RE.exec(text) : null;
			if (cite) {
				delete numbers[which];
				cites[which] = Number(cite[2]);
			} else {
				const m = NUMBER_LINE_RE.exec(text);
				const a = m ? jsonString(m[2]) : undefined;
				const b = m ? jsonString(m[3]) : undefined;
				numbers[which] = a !== undefined && b !== undefined ? [a, b] : null;
				delete cites[which];
			}
		} else if (text.startsWith('register ')) {
			const head = tok.decode(line.slice(0, -1));
			const mealy = MEALY_RE.exec(head);
			if (mealy) {
				regs.push({
					kind: 'mealy',
					name: mealy[1],
					output: mealy[2],
					start: line[line.length - 1],
					rows: [],
					pi: []
				});
				openRows = MEALY_ROW;
				continue;
			}
			const m = REGISTER_RE.exec(head);
			if (!m) {
				// as pb_loop: the rows stay open for the register before (the error stops the run anyway)
				err ??= `bad register line ${pyRepr(text)}`;
				continue;
			}
			regs.push({ kind: 'moore', name: m[1], start: line[line.length - 1], rows: [], pi: [] });
			openRows = 3;
			continue;
		}
		if (
			openRows &&
			line.length === openRows &&
			line.every((x) => !tok.decode([x]).includes('\n'))
		) {
			const r = regs[regs.length - 1];
			if (r.kind === 'mealy') r.rows.push(line as MealyRegister['rows'][number]);
			else r.rows.push(line as Register['rows'][number]);
			r.pi.push(...line, nl);
			continue;
		}
		openRows = 0;
	}
	for (const r of regs) {
		if (r.kind === 'moore') {
			// pb_loop's checks, unchanged
			const states = new Set(r.rows.map(([s]) => s));
			const events = new Set(r.rows.map(([, e]) => e));
			const keys = new Set(r.rows.map(([s, e]) => `${s},${e}`));
			if (keys.size !== r.rows.length || r.rows.length !== states.size * events.size)
				err ??= `register ${r.name}: table is not total and single-valued`;
			if (r.rows.some(([, , t]) => !states.has(t)) || !states.has(r.start))
				err ??= `register ${r.name}: a destination or the start is not a state`;
		} else {
			// ARITH_FORMAT §2 (arith_core.parse_generated)
			const states = new Set(r.rows.map((x) => x[0]));
			const as = new Set(r.rows.map((x) => x[1]));
			const bs = new Set(r.rows.map((x) => x[2]));
			const keys = new Set(r.rows.map((x) => `${x[0]},${x[1]},${x[2]}`));
			if (
				!r.rows.length ||
				keys.size !== r.rows.length ||
				r.rows.length !== states.size * as.size * bs.size
			)
				err ??= `register ${r.name}: table is not total and single-valued`;
			if (r.rows.some((x) => !states.has(x[3])) || !states.has(r.start))
				err ??= `register ${r.name}: a destination or the start is not a state`;
		}
	}
	if (!regs.length) err ??= 'no register';
	const mode =
		'first' in numbers || 'second' in numbers || 'first' in cites || 'second' in cites
			? 'numbers'
			: 'tape';
	if (mode === 'numbers') {
		const has = (w: 'first' | 'second') => cites[w] !== undefined || !!numbers[w];
		if (!has('first') || !has('second'))
			err ??= 'number mode needs a well-formed first: and second: line';
		if (regs.length !== 1 || regs[0].kind !== 'mealy')
			err ??= 'number mode runs exactly one register with an output';
	} else {
		if (regs.some((r) => r.kind === 'mealy'))
			err ??= 'a register with an output needs first: and second: lines';
		if (anchors === null) err ??= 'no tape line';
	}
	const registers: Register[] = [];
	const mealy: MealyRegister[] = [];
	for (const r of regs)
		if (r.kind === 'moore')
			registers.push({ name: r.name, start: r.start, rows: r.rows, pi: r.pi });
		else mealy.push({ name: r.name, output: r.output, start: r.start, rows: r.rows, pi: r.pi });
	return {
		registers,
		anchors,
		error: err,
		mode,
		mealy,
		numbers,
		...(opts.results ? { cites } : {})
	};
}

/** Python's repr of a str (the form error messages quote), for the characters programs contain. */
export function pyRepr(s: string): string {
	const q = s.includes("'") && !s.includes('"') ? '"' : "'";
	let out = q;
	for (const c of s) {
		const code = c.codePointAt(0)!;
		if (c === q || c === '\\') out += '\\' + c;
		else if (c === '\n') out += '\\n';
		else if (c === '\r') out += '\\r';
		else if (c === '\t') out += '\\t';
		else if (code < 0x20 || code === 0x7f) out += '\\x' + code.toString(16).padStart(2, '0');
		else if (!isPrintable(c)) {
			out +=
				code <= 0xff
					? '\\x' + code.toString(16).padStart(2, '0')
					: code <= 0xffff
						? '\\u' + code.toString(16).padStart(4, '0')
						: '\\U' + code.toString(16).padStart(8, '0');
		} else out += c;
	}
	return out + q;
}

// ------------------------------------------------------------------ the tape (pb_lit, pb_loop)

export const SEPARATORS = new Set(['', ',', ';', '.']);

/** pb_lit.find_span: after the first `before` (or the start), up to the first `after` after that (or the end). */
export function findSpan(question: string, before: string, after: string): [number, number] | null {
	let start = 0;
	if (before) {
		const i = question.indexOf(before);
		if (i < 0) return null;
		start = i + before.length;
	}
	let end = question.length;
	if (after) {
		const j = pyFind(question, after, start);
		if (j < 0) return null;
		end = j;
	}
	return [start, end];
}

export type Walk = { names: string[]; why: null } | { names: null; why: string };

/** pb_lit.walk: events in the span, in order, by the text of each prompt token (stripped). */
export function walk(
	tok: Tok,
	question: string,
	span: [number, number],
	eventNames: Iterable<string>
): Walk {
	const { offsets } = tok.encodeWithOffsets(question);
	const [a, b] = span;
	const names = new Set(eventNames);
	const out: string[] = [];
	for (const [s0, e0] of offsets) {
		const raw = question.slice(s0, e0);
		const s = s0 + raw.length - pyLstrip(raw).length;
		const e = e0 - (raw.length - pyRstrip(raw).length);
		if (e <= a || s >= b) continue;
		if (s < a || e > b) return { names: null, why: `token crosses the span edge at ${s}` };
		const text = question.slice(s, e);
		if (names.has(text)) out.push(text);
		else if (!SEPARATORS.has(text))
			return { names: null, why: `not an event or separator: ${pyRepr(text)}` };
	}
	return { names: out, why: null };
}

/** pb_loop.clock_tape: the tokens of the quoted span, matched by text to the table's event names. */
export function clockTape(
	tok: Tok,
	question: string,
	prog: Program
): { tape: number[]; why: null } | { tape: null; why: string } {
	const events = new Map<string, number>();
	for (const r of prog.registers)
		for (const [, e] of r.rows) events.set(pyStrip(tok.decode([e])), e);
	if (prog.anchors === null) return { tape: null, why: 'no tape line' };
	const span = findSpan(question, ...prog.anchors);
	if (span === null) return { tape: null, why: 'anchors not found in the prompt' };
	const w = walk(tok, question, span, events.keys());
	if (w.names === null) return { tape: null, why: w.why };
	return { tape: w.names.map((n) => events.get(n)!), why: null };
}

/** dl_core.Engine._char_spans: where each walked event sits in the question, or null when they do not line up. */
export function charSpans(
	tok: Tok,
	question: string,
	span: [number, number],
	tape: number[]
): [number, number][] | null {
	const { offsets } = tok.encodeWithOffsets(question);
	const [a, b] = span;
	const names = new Set(tape.map((e) => pyStrip(tok.decode([e]))));
	const out: [number, number][] = [];
	for (const [s, e] of offsets) {
		const raw = question.slice(s, e);
		const s2 = s + raw.length - pyLstrip(raw).length;
		const e2 = e - (raw.length - pyRstrip(raw).length);
		if (e2 <= a || s2 >= b) continue;
		if (names.has(question.slice(s2, e2))) out.push([s2, e2]);
	}
	return out.length === tape.length ? out : null;
}

/** pb_lit.item_span: where the items occur in order with only separators between them. */
export function itemSpan(question: string, items: string[]): [number, number, number[]] | null {
	const first = String(items[0]);
	let from = 0;
	for (;;) {
		const at = question.indexOf(first, from);
		if (at < 0 || !first) return null;
		let pos = at + first.length;
		let ok = true;
		const starts = [at];
		for (const raw of items.slice(1)) {
			const it = String(raw);
			let k = pos;
			while (k < question.length && ' ,;\n\t'.includes(question[k])) k++;
			if (!question.startsWith(it, k)) {
				ok = false;
				break;
			}
			starts.push(k);
			pos = k + it.length;
		}
		if (ok) return [at, pos, starts];
		from = at + first.length;
	}
}

/** pb_lit.anchors: the prose just before the first item and just after the last, quoted exactly. */
export function anchors(
	question: string,
	items: string[],
	minWords = 3,
	maxChars = 80
): [string, string] | null {
	const span = itemSpan(question, items);
	if (span === null) return null;
	const [a, b] = span;
	const pre = question.slice(0, a);
	const post = question.slice(b);
	let before: string | null = !pyStrip(pre) ? '' : null;
	let words = [...pre.matchAll(/\S+\s*/gu)];
	for (let w = Math.min(minWords, words.length); w <= words.length; w++) {
		if (before !== null) break;
		const cand = pre.slice(words[words.length - w].index);
		if (cand.length > maxChars) return null;
		if (pyCount(question, cand) === 1) before = cand;
	}
	let after: string | null = !pyStrip(post) ? '' : null;
	words = [...post.matchAll(/\s*\S+/gu)];
	for (let w = Math.min(minWords, words.length); w <= words.length; w++) {
		if (after !== null) break;
		const m = words[w - 1];
		const cand = post.slice(0, m.index + m[0].length);
		if (cand.length > maxChars) return null;
		if (pyFind(question, cand, a) === b) after = cand;
	}
	if (before === null || after === null) return null;
	return [before, after];
}

// ------------------------------------------------------------------ names, the <final> line, top-2

/** dl_core.Engine.name: a token as the page shows it, its text without the leading space; control text escaped. */
export function nameOf(tok: Tok, id: number): string {
	const s = tok.decode([id]);
	const st = pyStrip(s);
	if (st && isPrintable(st)) return st;
	return pyJsonDumps(s).slice(1, -1) || `<${id}>`;
}

/** dl_core.ask: `\n<final> X=v </final>\n`, the state's own id after each register's ` X=`. */
export function finIds(
	tok: Tok,
	registers: { name: string }[],
	finals: Record<string, number>
): number[] {
	const fin = tok.encode('\n<final>');
	for (const r of registers) fin.push(...tok.encode(` ${r.name}=`), finals[r.name]);
	fin.push(...tok.encode(' </final>\n'));
	return fin;
}

/** pb_pin.top2 over the whole vocabulary: the argmax (first on a tie) and its margin over the runner-up. */
export function top2(logits: ArrayLike<number>): { arg: number; margin: number } {
	let i0 = -1;
	let v0 = -Infinity;
	let v1 = -Infinity;
	for (let i = 0; i < logits.length; i++) {
		const v = logits[i];
		if (v > v0) {
			v1 = v0;
			v0 = v;
			i0 = i;
		} else if (v > v1) v1 = v;
	}
	return { arg: i0, margin: v0 - v1 };
}

/** Python's round(x, 4) closely enough for display: half to even is not reproduced bit for bit. */
export const round4 = (x: number) => Math.round(x * 1e4) / 1e4;
