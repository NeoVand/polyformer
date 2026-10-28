/**
 * ARITH_FORMAT §3 and §7, ported line for line from arith_core.py (branch `arith`): the clock's reading of two
 * numbers in number mode, the digit pairs it feeds, and the `<final>` line of a Mealy run. The clock computes
 * nothing about the numbers: it finds two spans, reads their digits, pairs them from the right and runs the table.
 * arith.spec.ts checks this file against arith_core's fixtures (fixtures/arith.json).
 */
import { pyRepr, pyStrip, type MealyRegister, type Program, type Tok } from './pb.ts';

const NUMBER_RE = /^(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)$/;

/** arith_core.find_span: from the end of the first `before` at or after `start` to the first `after` past it. */
export function findSpanFrom(
	question: string,
	before: string,
	after: string,
	start = 0
): [number, number] | null {
	if (before) {
		const i = start > question.length ? -1 : question.indexOf(before, start);
		if (i < 0) return null;
		start = i + before.length;
	}
	let end = question.length;
	if (after) {
		const j = start > question.length ? -1 : question.indexOf(after, start);
		if (j < 0) return null;
		end = j;
	}
	return [start, end];
}

/** arith_core.read_number: digits, or digits grouped by commas in threes (commas dropped); null otherwise. */
export function readNumber(text: string): string | null {
	const s = pyStrip(text);
	return NUMBER_RE.test(s) ? s.replaceAll(',', '') : null;
}

export type Reading =
	| { numbers: [string, string]; spans: [[number, number], [number, number]]; why: null }
	| {
			numbers: null;
			spans: [[number, number], [number, number] | null] | null;
			why: string;
	  };

/** arith_core.read_numbers: anchors = (before1, after1, before2, after2). */
export function readNumbers(question: string, anchors: [string, string, string, string]): Reading {
	const [b1, a1, b2, a2] = anchors;
	const sp1 = findSpanFrom(question, b1, a1, 0);
	if (!sp1)
		return { numbers: null, spans: null, why: 'first number: anchors not found in the prompt' };
	const sp2 = findSpanFrom(question, b2, a2, sp1[1]);
	if (!sp2)
		return {
			numbers: null,
			spans: [sp1, null],
			why: 'second number: anchors not found in the prompt'
		};
	const t1 = question.slice(...sp1);
	const t2 = question.slice(...sp2);
	const n1 = readNumber(t1);
	const n2 = readNumber(t2);
	if (n1 === null)
		return {
			numbers: null,
			spans: [sp1, sp2],
			why: `first number: not a number: ${pyRepr(t1.slice(0, 40))}`
		};
	if (n2 === null)
		return {
			numbers: null,
			spans: [sp1, sp2],
			why: `second number: not a number: ${pyRepr(t2.slice(0, 40))}`
		};
	return { numbers: [n1, n2], spans: [sp1, sp2], why: null };
}

/** arith_core.digit_pairs: right-aligned, least significant first, a missing digit read as 0, then one 0 0 pair. */
export function digitPairs(n1: string, n2: string): [string, string][] {
	const n = Math.max(n1.length, n2.length);
	const r1 = [...n1].reverse().join('').padEnd(n, '0');
	const r2 = [...n2].reverse().join('').padEnd(n, '0');
	const out: [string, string][] = [];
	for (let i = 0; i < n; i++) out.push([r1[i], r2[i]]);
	out.push(['0', '0']);
	return out;
}

/** The bare digit tokens "0" … "9" (Qwen3: ids 15 … 24). */
export function digitIds(tok: Tok): number[] {
	return [...'0123456789'].map((d) => {
		const ids = tok.encode(d);
		if (ids.length !== 1) throw new Error(`the digit ${d} is not one token`);
		return ids[0];
	});
}

export interface Pairs {
	pairs: [number, number][] | null;
	why: string | null;
	reading: Reading | null;
}

/** arith_core.clock_pairs: the (a, b) token-id pairs the clock feeds, or the reason it cannot. */
export function clockPairs(tok: Tok, question: string, prog: Program): Pairs {
	if (prog.error) return { pairs: null, why: prog.error, reading: null };
	const f = prog.numbers.first!;
	const s = prog.numbers.second!;
	const reading = readNumbers(question, [f[0], f[1], s[0], s[1]]);
	if (reading.numbers === null) return { pairs: null, why: reading.why, reading };
	const reg = prog.mealy[0];
	const firstEv = new Set(reg.rows.map((r) => r[1]));
	const secondEv = new Set(reg.rows.map((r) => r[2]));
	const digit = digitIds(tok);
	const pairs = digitPairs(...reading.numbers).map(
		([a, b]) => [digit[Number(a)], digit[Number(b)]] as [number, number]
	);
	if (pairs.some(([a, b]) => !firstEv.has(a) || !secondEv.has(b)))
		return { pairs: null, why: 'a digit is not an event of the table', reading };
	return { pairs, why: null, reading };
}

/**
 * arith_core.final_ids: `\n<final> c=<state> s=<outputs, last first, leading zeros dropped> </final>\n`. The output
 * ids are copied as emitted; the dropped zero is the digit-0 id, and one id is always kept.
 */
export function finalIdsMealy(
	tok: Tok,
	reg: Pick<MealyRegister, 'name' | 'output'>,
	finalState: number,
	outputs: number[]
): number[] {
	const zero = digitIds(tok)[0];
	const rev = [...outputs].reverse();
	while (rev.length > 1 && rev[0] === zero) rev.shift();
	return [
		...tok.encode('\n<final>'),
		...tok.encode(` ${reg.name}=`),
		finalState,
		...tok.encode(` ${reg.output}=`),
		...rev,
		...tok.encode(' </final>\n')
	];
}

/** The adder's true outputs (the sum's digits, least significant first) and final carry, for tests and checks. */
export function trueOutputs(n1: string, n2: string): { outputs: string[]; carry: number } {
	let c = 0;
	const outputs: string[] = [];
	for (const [a, b] of digitPairs(n1, n2)) {
		const v = c + Number(a) + Number(b);
		c = Math.floor(v / 10);
		outputs.push(String(v % 10));
	}
	return { outputs, carry: c };
}

/** The sum of two digit strings, exactly (the page's own check, never the clock's). */
export const exactSum = (n1: string, n2: string) => (BigInt(n1) + BigInt(n2)).toString();
