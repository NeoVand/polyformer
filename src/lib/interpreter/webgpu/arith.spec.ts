/**
 * Number mode (ARITH_FORMAT) against arith_core.py's fixtures (fixtures/arith.json, copied from branch `arith` by
 * scripts/arith_fixtures.py): the parser, the two spans, the numbers, the digit pairs, the adder's run and the
 * `<final>` ids, for four questions end to end and five failures, on the fixtures' own tokens and on Qwen3's real
 * tokenizer when one is on disk. Then the spec's other rules, on programs written here.
 */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import {
	clockPairs,
	digitPairs,
	exactSum,
	finalIdsMealy,
	findSpanFrom,
	readNumber,
	readNumbers,
	trueOutputs
} from './arith.ts';
import { chatPrompt, parseGenerated, type Tok } from './pb.ts';
import { findTokenizer, realTok } from './realtok.ts';
import { arith } from './arith-fixtures.ts';
import { FixtureTok } from './testkit.ts';

const fixtureTok = FixtureTok.from([], arith.special, {
	tokens: arith.tokens,
	encoded: arith.encoded
});
const tokPath = findTokenizer();
const nl = arith.ids.nl;

function checks(label: string, getTok: () => Tok, full: boolean) {
	describe(`number mode on ${label}`, () => {
		for (const e of arith.examples)
			it(e.question, () => {
				const tok = getTok();
				const prog = parseGenerated(tok, e.program_ids, nl);
				expect(prog.error).toBe(e.parsed.error);
				expect(prog.mode).toBe(e.parsed.mode);
				expect(prog.numbers).toEqual(e.parsed.numbers);
				expect(prog.registers).toEqual([]);
				expect(prog.mealy).toHaveLength(1);
				const r = prog.mealy[0];
				expect([r.name, r.output, r.start]).toEqual([
					e.parsed.register.name,
					e.parsed.register.output,
					e.parsed.register.start
				]);
				expect(r.rows.map((x) => [...x])).toEqual(e.parsed.register.rows);
				expect(r.pi).toHaveLength(e.parsed.register.pi_len);
				expect(createHash('sha256').update(r.pi.join(',')).digest('hex')).toBe(
					e.parsed.register.pi_sha256
				);

				const got = clockPairs(tok, e.question, prog);
				expect(got.why).toBe(e.reading.error);
				expect(got.pairs).toEqual(e.reading.pairs);
				expect(got.reading?.spans).toEqual(e.reading.spans);
				expect(got.reading?.numbers).toEqual(e.reading.numbers);

				// the first tick's two forwards, as the fixture lays them out
				const P = r.pi.length;
				expect([r.start, ...got.pairs![0]]).toEqual(e.first_tick.forward1.ids);
				expect([P, P + 1, P + 2]).toEqual(e.first_tick.forward1.positions);
				// forward 2 re-feeds the whole block on Π's cache (§4 as amended 28 Oct)
				expect([P, P + 1, P + 2, P + 3]).toEqual(e.first_tick.forward2.positions);

				// the table's own run: states and outputs, then the <final> line
				const delta = new Map(r.rows.map((x) => [`${x[0]},${x[1]},${x[2]}`, [x[3], x[4]]]));
				let s = r.start;
				const states: number[] = [];
				const outputs: number[] = [];
				for (const [a, b] of got.pairs!) {
					const [t, o] = delta.get(`${s},${a},${b}`)!;
					states.push(t);
					outputs.push(o);
					s = t;
				}
				expect(states).toEqual(e.run.states);
				expect(outputs).toEqual(e.run.outputs);
				expect(e.first_tick.forward2.ids).toEqual([r.start, ...got.pairs![0], states[0]]);
				const fin = finalIdsMealy(tok, r, s, outputs);
				expect(fin).toEqual(e.final_ids);
				expect(tok.decode(fin)).toBe(e.final_text);
				expect(exactSum(...e.reading.numbers)).toBe(e.sum);
				if (full) {
					expect(tok.encode(chatPrompt(e.question))).toEqual(e.chat_prompt_ids);
					expect(tok.decode(e.program_ids)).toBe(e.program_text);
					expect(tok.encode(e.program_text)).toEqual(e.program_ids);
				}
			});
		for (const f of arith.failures)
			it(`fails as the reference does: ${f.case}`, () => {
				const tok = getTok();
				const prog = parseGenerated(tok, f.program_ids, nl);
				expect(prog.error).toBe(f.parse_error);
				const got = clockPairs(tok, f.question, prog);
				expect(got.why).toBe(f.parse_error ?? f.reading_error);
			});
	});
}

checks('the fixtures’ tokens', () => fixtureTok, false);

describe.skipIf(!tokPath)('Qwen3’s real tokenizer', () => {
	let tok: Tok;
	it('is the fixtures’ tokenizer', async () => {
		expect(createHash('sha256').update(readFileSync(tokPath!)).digest('hex')).toBe(
			arith.tokenizer_sha256
		);
		tok = await realTok(tokPath!);
		expect([...'0123456789'].map((d) => tok.encode(d)[0])).toEqual(arith.ids.digits);
	});
	checks('the real tokenizer', () => tok, true);

	// ARITH_FORMAT §2's other rules, on programs written here from the reference program's text
	describe('the parser’s rules', () => {
		const base = arith.examples[1];
		const text = base.program_text;
		const parse = (t: string) => parseGenerated(tok, tok.encode(t), nl);
		it('a malformed first: line', () => {
			const p = parse(text.replace(/^first: .*$/m, 'first: after What is until plus'));
			expect(p.mode).toBe('numbers');
			expect(p.numbers.first).toBeNull();
			expect(p.error).toBe('number mode needs a well-formed first: and second: line');
		});
		it('a missing second: line', () => {
			const p = parse(text.replace(/^second: .*\n/m, ''));
			expect(p.error).toBe('number mode needs a well-formed first: and second: line');
		});
		it('a later first: line replaces an earlier one', () => {
			const p = parse(text.replace(/^(first: .*)$/m, 'first: after "x" until "y"\n$1'));
			expect(p.numbers.first).toEqual(base.parsed.numbers.first);
			expect(p.error).toBeNull();
		});
		it('a Mealy register needs first: and second: lines', () => {
			const p = parse(
				text.replace(/^first: .*\n/m, '').replace(/^second: .*\n/m, 'tape: after "a" until "b"\n')
			);
			expect(p.mode).toBe('tape');
			expect(p.error).toBe('a register with an output needs first: and second: lines');
		});
		it('number mode runs exactly one register with an output', () => {
			// two Mealy registers, each a valid table
			const block = text.slice(text.indexOf('register c'), text.indexOf('answer:'));
			const p = parse(
				text.replace('answer:', block.replace('register c', 'register d') + 'answer:')
			);
			expect(p.mealy).toHaveLength(2);
			expect(p.error).toBe('number mode runs exactly one register with an output');
		});
		it('a digit that is not an event of the table', () => {
			// a table over first digits 0 … 4 only is total over its own sets, but cannot read a 7
			const rows = text
				.split('\n')
				.filter((l) => !/^[0-9]{5}$/.test(l) || Number(l[1]) <= 4)
				.join('\n');
			const p = parse(rows);
			expect(p.error).toBeNull();
			expect(clockPairs(tok, 'What is 4096 plus 77?', p).why).toBe(
				'a digit is not an event of the table'
			);
			expect(clockPairs(tok, 'What is 4044 plus 1?', p).why).toBeNull();
		});
		it('the start token is the header’s last token, the rows’ own 0', () => {
			const p = parse(text);
			expect(p.mealy[0].start).toBe(arith.ids.digits[0]);
			expect(p.mealy[0].pi.slice(0, 6)).toEqual([...Array(5).fill(arith.ids.digits[0]), nl]);
		});
	});
});

describe('the clock’s reading (ARITH_FORMAT §3)', () => {
	it('finds spans from a start, as arith_core.find_span', () => {
		expect(findSpanFrom('a+b+c', '+', '+', 0)).toEqual([2, 3]);
		expect(findSpanFrom('a+b+c', '+', '', 2)).toEqual([4, 5]);
		expect(findSpanFrom('a+b', '', '+', 0)).toEqual([0, 1]);
		expect(findSpanFrom('a+b', 'x', '', 0)).toBeNull();
		expect(findSpanFrom('a+b', '', 'x', 0)).toBeNull();
	});
	it('reads digits and comma groups, keeps leading zeros, refuses anything else', () => {
		expect(readNumber(' 007 ')).toBe('007');
		expect(readNumber('1,234,567')).toBe('1234567');
		expect(readNumber('1234,567')).toBeNull();
		expect(readNumber('12,34')).toBeNull();
		expect(readNumber('3.5')).toBeNull();
		expect(readNumber('-3')).toBeNull();
		expect(readNumber('')).toBeNull();
	});
	it('says which number failed and quotes it as Python does', () => {
		expect(readNumbers('What is 4096 plus 77?', ['What ', ' plus ', ' plus ', '?']).why).toBe(
			"first number: not a number: 'is 4096'"
		);
		expect(readNumbers('Add 12 and x.', ['Add ', ' and ', ' and ', '.']).why).toBe(
			"second number: not a number: 'x'"
		);
	});
	it('pairs from the right with zeros, then one more 0 0 pair', () => {
		expect(digitPairs('4096', '77')).toEqual([
			['6', '7'],
			['9', '7'],
			['0', '0'],
			['4', '0'],
			['0', '0']
		]);
		expect(digitPairs('0', '0')).toEqual([
			['0', '0'],
			['0', '0']
		]);
	});
	it('the adder’s true run ends with carry 0 and spells the sum', () => {
		for (const [a, b] of [
			['99999999999999999999', '1'],
			['4096', '77'],
			['0', '0'],
			['123', '0000']
		]) {
			const { outputs, carry } = trueOutputs(a, b);
			expect(carry).toBe(0);
			expect(BigInt([...outputs].reverse().join(''))).toBe(BigInt(a) + BigInt(b));
		}
	});
});
