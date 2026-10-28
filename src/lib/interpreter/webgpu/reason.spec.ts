/**
 * REASON_FORMAT's clock against reason_core.py's fixtures (fixtures/reason.json, copied from branch `reason` by
 * scripts/reason_fixtures.py): `locate` on the reference's six cases and on today's find_span, the whitespace-relaxed
 * match, each call's notes, the parse of `result k`, the reading of every fixture call, result values and error
 * lines, the limits, and the subtracter. On the fixtures' own tokens, and on Qwen3's real tokenizer when one is on
 * disk.
 */
import { describe, expect, it } from 'vitest';
import { digitPairs } from './arith.ts';
import { isAdder } from './engine.ts';
import { findSpan, parseGenerated, type Tok } from './pb.ts';
import {
	errorFinalIds,
	errorFinalText,
	exactDifference,
	HARD_STOP_CALLS,
	isSubtracter,
	lastCallStart,
	lastExecStart,
	limitAt,
	locate,
	match,
	MAX_CALLS,
	notesOf,
	readCall,
	relaxedPattern,
	resultNumbers,
	resultValueOf,
	roundCallStart,
	sourcesOf
} from './reason.ts';
import { reason, reasonTok } from './reason-fixtures.ts';
import { findTokenizer, realTok } from './realtok.ts';

const tokPath = findTokenizer();
const { nl, digits } = reason.ids;

describe('locate (REASON_FORMAT §3)', () => {
	for (const c of reason.locate)
		it(`${JSON.stringify(c.before)} … ${JSON.stringify(c.after)} from ${c.from}`, () => {
			expect(locate(c.sources, c.before, c.after, c.from)).toEqual(c.want);
		});

	it('is today’s find_span on the question when the quotes occur exactly', () => {
		// reason_core.selftest 1
		for (const q of ['What is 4096 plus 77?', 'Swaps: AB, BC.', 'x'])
			for (const [b, a] of [
				['What is ', ' plus '],
				['', '?'],
				['Swaps: ', '.'],
				['zzz', '']
			]) {
				const got = locate([q, ''], b, a);
				expect(got ? got.slice(1, 3) : null).toEqual(findSpan(q, b, a));
			}
	});

	it('relaxes whitespace only when there is no exact match, and never content', () => {
		// reason_core.selftest 2
		expect(
			locate(['The log:\nin, out ,in.\nDone', ''], 'The log: ', '. Done')?.slice(1, 3)
		).toEqual([9, 20]);
		expect(match('a  b a b', 'a b', 0)).toEqual([5, 8, 'exact']);
		expect(match('a\n\nb', 'a b', 0)).toEqual([0, 4, 'relaxed']);
		// ASCII whitespace only (§12): a no-break space is content
		expect(match('a b', 'a b', 0)).toBeNull();
		expect(match('a\t\f\vb', 'a b', 0)).toEqual([0, 5, 'relaxed']);
		// punctuation and fragments are not relaxed
		expect(match('in,out', 'in, out', 0)).toBeNull();
		expect(match('a b', 'ab', 0)).toBeNull();
		// a quote with no whitespace has no relaxed form
		expect(match('xyz', 'q', 0)).toBeNull();
		// regex characters in a quote are literal
		expect(match('cost: $5.00 (net)\n[a]', '$5.00 (net) [a]', 0)).toEqual([6, 21, 'relaxed']);
		expect(relaxedPattern('a  b.').source).toBe('a[ \\t\\n\\r\\f\\v]+b\\.');
	});

	it('falls through the question to the notes, and an empty before stays in its source', () => {
		const src = ['The list: a, b.', 'My list: c, d.'];
		expect(locate(src, 'My list: ', '.')).toEqual([1, 9, 13, 'exact']);
		// `before` found in S0 but `after` not: it fails there, it does not look in S1
		expect(locate(['My list: c', 'My list: d.'], 'My list: ', '.')).toBeNull();
		expect(locate(src, '', '.', [1, 0])).toEqual([1, 0, 13, 'exact']);
		expect(locate(src, '', '', [1, 3])).toEqual([1, 3, 14, 'exact']);
		expect(locate(src, 'nowhere', '')).toBeNull();
		expect(locate(src, 'a', '.', [2, 0])).toBeNull();
	});
});

describe('limits and lines (§5, §6)', () => {
	it('runs 8 calls, refuses the 9th to the 11th, and ends at the 12th', () => {
		expect([MAX_CALLS, HARD_STOP_CALLS]).toEqual([8, 11]);
		expect(Array.from({ length: 13 }, (_, n) => limitAt(n))).toEqual([
			...Array(8).fill('run'),
			'too many',
			'too many',
			'too many',
			'end',
			'end'
		]);
	});

	it('numbers results by the calls that ran: an error line takes none (§12)', () => {
		expect(resultNumbers(['12', null, '7', null, null, '3'])).toEqual([1, null, 2, null, null, 3]);
		expect(resultNumbers([])).toEqual([]);
	});

	it('reads a final line’s value: the last name=value field; none for an error line', () => {
		expect(resultValueOf('\n<final> t= honest </final>\n')).toBe('honest');
		expect(resultValueOf('\n<final> c=0 s=4173 </final>\n')).toBe('4173');
		expect(resultValueOf('\n<final> n=6 m=x </final>\n')).toBe('x');
		expect(resultValueOf('\n<final> error: first number: no result 5 </final>\n')).toBeNull();
		expect(resultValueOf('\n<final> nothing </final>\n')).toBeNull();
		expect(errorFinalText('too many calls')).toBe('\n<final> error: too many calls </final>\n');
	});

	it('names the subtracter, and checks its value exactly', () => {
		const rows: [number, number, number, number, number][] = [];
		for (let b = 0; b < 2; b++)
			for (let a = 0; a < 10; a++)
				for (let c = 0; c < 10; c++) {
					const v = a - c - b;
					rows.push([
						digits[b],
						digits[a],
						digits[c],
						digits[v < 0 ? 1 : 0],
						digits[(v + 20) % 10]
					]);
				}
		const sub = { start: digits[0], rows, name: 'b', output: 'd', pi: [] };
		expect(isSubtracter(sub, digits)).toBe(true);
		expect(isAdder(sub, digits)).toBe(false);
		const bad = {
			...sub,
			rows: rows.map((r, k) => (k === 7 ? ([...r.slice(0, 4), digits[0]] as typeof r) : r))
		};
		expect(isSubtracter(bad, digits)).toBe(false);
		// the table's own run, against the page's check
		const run = (n1: string, n2: string) => {
			let b = 0;
			const outs: number[] = [];
			for (const [x, y] of digitPairs(n1, n2)) {
				const v = Number(x) - Number(y) - b;
				b = v < 0 ? 1 : 0;
				outs.push((v + 20) % 10);
			}
			return {
				value: outs
					.reverse()
					.join('')
					.replace(/^0+(?=.)/, ''),
				borrow: b
			};
		};
		for (const [n1, n2] of [
			['1000', '1'],
			['1', '1000'],
			['5', '5'],
			['123456789012345678901234567890', '98765432109876543210'],
			['98765432109876543210', '123456789012345678901234567890']
		]) {
			const r = run(n1, n2);
			expect(exactDifference(n1, n2)).toBe(r.value);
			expect(r.borrow).toBe(BigInt(n1) < BigInt(n2) ? 1 : 0);
		}
		expect(exactDifference('1', '1000')).toBe('99001');
	});
});

function checks(label: string, getTok: () => Tok) {
	describe(`the reference's calls on ${label}`, () => {
		for (const c of reason.cases)
			describe(c.name, () => {
				it('every call’s notes, reading, final line and value', () => {
					const tok = getTok();
					expect(tok.decode(c.response_ids)).toBe(c.response_text);
					const results: (string | null)[] = [];
					/** where the clock last stopped appending: the end of the last final, or 0 */
					let round = 0;
					expect(resultNumbers(c.calls.map((x) => x.value))).toEqual(
						c.calls.map((x) => x.result_number)
					);
					for (const call of c.calls) {
						const upTo = c.response_ids.slice(0, call.end);
						const text = tok.decode(upTo);
						expect(notesOf(text)).toBe(call.notes);
						expect(sourcesOf(c.question, text)).toEqual([c.question, call.notes]);
						expect(lastCallStart(tok, upTo)).toBe(call.start);
						expect(roundCallStart(tok, upTo, round)).toBe(call.start);
						expect(lastExecStart(tok, upTo, call.start)).toBe(call.end - 3);
						const prog = parseGenerated(tok, upTo.slice(call.start), nl, { results: true });
						const got = readCall(tok, c.question, text, prog, results);
						expect(got.mode).toBe(call.mode);
						expect(got.error).toBe(call.error);
						expect(got.spans).toEqual(call.spans);
						expect(got.how).toEqual(call.how);
						expect(tok.decode(call.final_ids)).toBe(call.final_text);
						expect(resultValueOf(call.final_text)).toBe(call.value);
						if (call.error) {
							expect(call.final_text).toBe(errorFinalText(call.error));
							expect(errorFinalIds(tok, call.error)).toEqual(call.final_ids);
						}
						results.push(call.value);
						round = call.end + call.final_ids.length;
					}
				});
			});

		it('finds a call only in the model’s own ids since the clock last appended (§12)', () => {
			const tok = getTok();
			const chain = reason.cases.find((x) => x.name === 'chain_add_add_sub')!;
			const [one, two] = chain.calls;
			const afterOne = one.end + one.final_ids.length;
			const exec = chain.response_ids.slice(one.end - 3, one.end);
			// call 2's round holds its program
			expect(roundCallStart(tok, chain.response_ids.slice(0, two.end), afterOne)).toBe(two.start);
			// a round of words and <exec/> has none, though call 1's program is in the response
			const bare = [...chain.response_ids.slice(0, two.start), ...exec];
			expect(roundCallStart(tok, bare, afterOne)).toBeNull();
			expect(roundCallStart(tok, bare, 0)).toBe(one.start);
			expect(lastExecStart(tok, bare, afterOne)).toBe(two.start);
			// before any call the round starts at 0
			expect(roundCallStart(tok, exec, 0)).toBeNull();
		});

		it('a cited result counts only the calls that ran', () => {
			const tok = getTok();
			const chain = reason.cases.find((x) => x.name === 'chain_add_add_sub')!;
			const call = chain.calls[2];
			const upTo = chain.response_ids.slice(0, call.end);
			const prog = parseGenerated(tok, upTo.slice(call.start), nl, { results: true });
			const text = tok.decode(upTo);
			const [a, b] = chain.calls.map((x) => x.value!);
			// results 1 and 2 are the 1st and 3rd calls when the 2nd ended in an error line
			expect(readCall(tok, chain.question, text, prog, [a, null, b]).numbers).toEqual([a, b]);
			expect(readCall(tok, chain.question, text, prog, [a, null]).error).toBe(
				'second number: no result 2'
			);
			expect(readCall(tok, chain.question, text, prog, [null, null, a]).error).toBe(
				'second number: no result 2'
			);
		});

		it('parses `first: result k` only when asked, and today’s parse is unchanged', () => {
			const tok = getTok();
			const chain = reason.cases.find((x) => x.name === 'chain_add_add_sub')!;
			const call = chain.calls[2];
			const ids = chain.response_ids.slice(call.start, call.end);
			const p = parseGenerated(tok, ids, nl, { results: true });
			expect(p.error).toBeNull();
			expect(p.mode).toBe('numbers');
			expect(p.cites).toEqual({ first: 1, second: 2 });
			expect(p.numbers).toEqual({});
			expect([p.mealy[0].name, p.mealy[0].output, p.mealy[0].rows.length]).toEqual(['b', 'd', 200]);
			expect(isSubtracter(p.mealy[0], digits)).toBe(true);
			// today's parser (a single call) reads the line as a malformed quote, as arith_core does
			const today = parseGenerated(tok, ids, nl);
			expect(today.error).toBe('number mode needs a well-formed first: and second: line');
			expect(today.numbers).toEqual({ first: null, second: null });
			expect('cites' in today).toBe(false);
			// a call that quotes both numbers parses the same either way, but for the (empty) citations
			const q = chain.calls[0];
			const quoted = chain.response_ids.slice(q.start, q.end);
			const { cites, ...rest } = parseGenerated(tok, quoted, nl, { results: true });
			expect(cites).toEqual({});
			expect(rest).toEqual(parseGenerated(tok, quoted, nl));
		});
	});
}

checks('the fixtures’ own tokens', reasonTok);
if (tokPath) {
	let real: Tok | null = null;
	const getReal = () => real!;
	describe('Qwen3’s real tokenizer', () => {
		it('loads', async () => {
			real = await realTok(tokPath);
			expect(real.encode('<exec/>')).toEqual(reason.encoded['<exec/>']);
		});
		checks('Qwen3’s real tokenizer', getReal);

		it('a </final> the model writes itself does not end its round', () => {
			const tok = getReal();
			const ids = tok.encode('Words.\n\n<program>\ntask: t\n</final>\n</program>\n<exec/>');
			expect(roundCallStart(tok, ids, 0)).toBe(tok.encode('Words.\n\n').length);
			const bare = tok.encode(
				'<program>\ntask: t\n</program>\n<exec/>\n<final> n=1 </final>\nNo program </final> here <exec/>'
			);
			const round = tok.encode(
				'<program>\ntask: t\n</program>\n<exec/>\n<final> n=1 </final>\n'
			).length;
			expect(roundCallStart(tok, bare, round)).toBeNull();
		});

		it('a later number line replaces an earlier one, citation or quote', () => {
			const tok = getReal();
			const head =
				'<program>\ntask: t\ninput: i\nfirst: after "a" until "b"\nsecond: result 1\nfirst: result 2\n';
			const tail = 'register c (output s): start 0\n';
			const prog = parseGenerated(
				tok,
				tok.encode(head + 'second: after "x" until "y"\n' + tail),
				nl,
				{
					results: true
				}
			);
			expect(prog.cites).toEqual({ first: 2 });
			expect(prog.numbers).toEqual({ second: ['x', 'y'] });
			expect(prog.mode).toBe('numbers');
		});
	});
}
