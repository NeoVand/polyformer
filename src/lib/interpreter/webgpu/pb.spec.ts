/**
 * The clock's TypeScript port against what PROMPTBOX's Python computes (fixtures/reference.json, written by
 * research/demolive/dl_web.py): the eight recorded traces' real program ids and questions, generated literal programs
 * of every trained family, and crafted failures. Each check runs on a tokenizer built from the fixtures' own token
 * strings, and again on Qwen3's real tokenizer when one is on disk.
 */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { answerCorrect, type AnswerKey } from './answer.ts';
import {
	anchors,
	charSpans,
	chatPrompt,
	clockTape,
	findSpan,
	finIds,
	isPrintable,
	itemSpan,
	linesOf,
	nameOf,
	parseGenerated,
	pyJsonDumps,
	pyRepr,
	pyStrip,
	top2,
	walk,
	type Tok
} from './pb.ts';
import { findTokenizer, realTok } from './realtok.ts';
import { FixtureTok, type FixtureCase } from './testkit.ts';

interface Case extends FixtureCase {
	name: string;
	program_ids: number[];
	decode: Record<string, string>;
	names: Record<string, string>;
	program_text: string;
	lines: number[][];
	parsed: {
		registers: { name: string; start: number; rows: number[][]; pi: number[] }[];
		anchors: [string, string] | null;
		error: string | null;
	};
	span: [number, number] | null;
	tape: number[] | null;
	why: string | null;
	chat_prompt_ids: number[];
	char_spans?: [number, number][] | null;
	tape_names?: string[];
	fin_start?: { finals: Record<string, number>; ids: number[] };
	fin_first_dest?: { finals: Record<string, number>; ids: number[] };
}

const ref = JSON.parse(
	readFileSync(new URL('./fixtures/reference.json', import.meta.url), 'utf8')
) as {
	tokenizer_sha256: string;
	nl: number;
	special: number[];
	cases: Case[];
	anchors: {
		family: string;
		question: string;
		items: string[];
		item_span: [number, number, number[]] | null;
		anchors: [string, string] | null;
	}[];
	answers: { key: AnswerKey; text: string; correct: boolean }[];
};

const fixtureTok = FixtureTok.from(ref.cases, ref.special);
const tokPath = findTokenizer();

function clockChecks(label: string, getTok: () => Tok, full: boolean) {
	describe(`the clock on ${label}`, () => {
		for (const c of ref.cases) {
			it(c.name, () => {
				const tok = getTok();
				expect(linesOf(tok, c.program_ids, ref.nl)).toEqual(c.lines);
				const prog = parseGenerated(tok, c.program_ids, ref.nl);
				expect({
					registers: prog.registers.map((r) => ({ ...r, rows: r.rows.map((x) => [...x]) })),
					anchors: prog.anchors,
					error: prog.error
				}).toEqual(c.parsed);
				const ct = prog.error ? { tape: null, why: prog.error } : clockTape(tok, c.question, prog);
				expect(ct.tape).toEqual(c.tape);
				expect(ct.why).toEqual(c.why);
				expect(prog.anchors ? findSpan(c.question, ...prog.anchors) : null).toEqual(c.span);
				if (c.tape && c.span) {
					expect(charSpans(tok, c.question, c.span, c.tape)).toEqual(c.char_spans);
					expect(c.tape.map((e) => nameOf(tok, e))).toEqual(c.tape_names);
				}
				for (const [id, name] of Object.entries(c.names))
					expect(nameOf(tok, Number(id))).toBe(name);
				if (full) {
					expect(tok.decode(c.program_ids)).toBe(c.program_text);
					expect(tok.encode(chatPrompt(c.question))).toEqual(c.chat_prompt_ids);
					const q = tok.encodeWithOffsets(c.question);
					expect(q.ids).toEqual(c.question_ids);
					expect(q.offsets).toEqual(c.question_offsets);
					for (const [id, text] of Object.entries(c.decode))
						expect(tok.decode([Number(id)])).toBe(text);
					for (const fin of [c.fin_start, c.fin_first_dest])
						if (fin) expect(finIds(tok, prog.registers, fin.finals)).toEqual(fin.ids);
				}
			});
		}
	});
}

clockChecks('the fixtures’ tokens', () => fixtureTok, false);

describe.skipIf(!tokPath)('Qwen3’s real tokenizer', () => {
	let tok: Tok;
	it('is the one the fixtures were written with', async () => {
		const bytes = readFileSync(tokPath!);
		expect(createHash('sha256').update(bytes).digest('hex')).toBe(ref.tokenizer_sha256);
		tok = await realTok(tokPath!);
		expect(tok.encode('\n')).toEqual([ref.nl]);
	});
	clockChecks('the real tokenizer', () => tok, true);
});

describe('pb_lit.item_span and anchors', () => {
	for (const [k, a] of ref.anchors.entries())
		it(`${a.family} #${k}`, () => {
			expect(itemSpan(a.question, a.items)).toEqual(a.item_span);
			expect(anchors(a.question, a.items)).toEqual(a.anchors);
		});
});

describe('pb_families.answer_correct', () => {
	it(`agrees with the Python on ${ref.answers.length} answers`, () => {
		const wrong = ref.answers.filter((a) => answerCorrect(a.key, a.text) !== a.correct);
		expect(wrong).toEqual([]);
		expect(ref.answers.some((a) => a.correct)).toBe(true);
		expect(ref.answers.some((a) => !a.correct)).toBe(true);
	});
});

describe('Python string semantics', () => {
	it('strips what str.strip strips', () => {
		expect(pyStrip('\x1c\u3000 a b \x85\n')).toBe('a b');
		expect(pyStrip('\ufeffa')).toBe('\ufeffa');
	});
	it('isprintable and json.dumps escape like Python', () => {
		expect(isPrintable('abc é')).toBe(true);
		expect(isPrintable('a\u00a0b')).toBe(false);
		expect(isPrintable('\n')).toBe(false);
		expect(pyJsonDumps('\n é"\\\x7f')).toBe('"\\n \\u00e9\\"\\\\\\u007f"');
	});
	it("repr picks Python's quotes", () => {
		expect(pyRepr("it's")).toBe('"it\'s"');
		expect(pyRepr('noop')).toBe("'noop'");
		expect(pyRepr('a\tb\u00a0')).toBe("'a\\tb\\xa0'");
	});
	it('top2 takes the first maximum and a zero margin on a tie', () => {
		expect(top2([1, 3, 2])).toEqual({ arg: 1, margin: 1 });
		expect(top2([5, 1, 5])).toEqual({ arg: 0, margin: 0 });
	});
	it('walks a span the way pb_lit.walk does', () => {
		const tok: Tok = {
			encode: () => [],
			decode: () => '',
			encodeWithOffsets: () => ({
				ids: [1, 2, 3, 4],
				offsets: [
					[0, 3],
					[3, 4],
					[4, 7],
					[7, 8]
				]
			})
		};
		expect(walk(tok, 'ab ,cd .', [0, 8], ['ab', 'cd'])).toEqual({
			names: ['ab', 'cd'],
			why: null
		});
		expect(walk(tok, 'ab ,cd .', [1, 8], ['ab', 'cd']).why).toBe(
			'token crosses the span edge at 0'
		);
	});
});
