/**
 * The panels' view of a number-mode run, on the engine's own run of "What is 4096 plus 77?" (the run the page's
 * browser tests replay, e2e/fixtures/arith-run.json, written and checked by webgpu/engine-arith.spec.ts).
 */
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import {
	certLayout,
	columnsAround,
	mealyEdges,
	mealyRowText,
	mealyWords,
	opOfRows,
	pairAt,
	sumSoFar
} from './mealy.ts';
import { asTrace, llmNote, type LlmTrace, type Trace } from './trace.ts';
import { additionTicks, makeAddition, randomNumber } from './webgpu/prompts.ts';

const run: LlmTrace = JSON.parse(
	readFileSync(new URL('../../../e2e/fixtures/arith-run.json', import.meta.url), 'utf8')
);
const t = asTrace(run) as Trace;

describe('the written sum', () => {
	it('reads the digit pairs from the steps, or from the tape before a column has run', () => {
		expect(pairAt(t, 0)).toEqual(['6', '7']);
		const before = { ...t, steps: [] } as Trace;
		expect(pairAt(before, 3)).toEqual(['4', '0']);
		expect(pairAt(before, 9)).toBeNull();
	});

	it('lays the columns out highest first, with the carry in above and the digit written below', () => {
		const cols = columnsAround(t, 1, 13);
		expect(cols.map((c) => c.i)).toEqual([4, 3, 2, 1, 0]);
		expect(cols.map((c) => c.a + c.b)).toEqual(['00', '40', '00', '97', '67']);
		// 6 + 7 = 13 carries 1 into column 2; 9 + 7 + 1 = 17 carries 1 into column 3
		expect(cols.map((c) => c.cin)).toEqual([null, null, '1', '1', '0']);
		expect(cols.map((c) => c.o)).toEqual([null, null, null, '7', '3']);
		expect(cols.map((c) => [c.done, c.now])).toEqual([
			[false, false],
			[false, false],
			[false, false],
			[true, true],
			[true, false]
		]);
		// 77 is two digits: its columns 3 and 4 are padding; the last column pads both
		expect(cols.map((c) => [c.padA, c.padB])).toEqual([
			[true, true],
			[false, true],
			[false, true],
			[false, false],
			[false, false]
		]);
	});

	it('shows only the start carry while certifying', () => {
		const cols = columnsAround({ ...t, steps: [] } as Trace, -1, 13);
		expect(cols.map((c) => c.cin)).toEqual([null, null, null, null, '0']);
		expect(cols.every((c) => !c.done && !c.now && c.o === null)).toBe(true);
	});

	it('keeps a window inside the run on long sums', () => {
		const long = {
			...t,
			steps: Array.from({ length: 40 }, (_, i) => ({ ...t.steps[0], i })),
			llm: { ...t.llm!, file: { ...run, input: { ...run.input, events: Array(40).fill('1+1') } } }
		} as Trace;
		expect(columnsAround(long, 0, 13).map((c) => c.i)).toEqual(
			Array.from({ length: 13 }, (_, k) => 12 - k)
		);
		expect(columnsAround(long, 20, 13).map((c) => c.i)[6]).toBe(20);
		expect(columnsAround(long, 39, 13).map((c) => c.i)[0]).toBe(39);
	});

	it('builds the sum up newest digit first, and ends at the clock’s sum with its leading 0', () => {
		expect(sumSoFar(t.steps, 0)).toEqual({ newest: '3', rest: '', digits: 1 });
		expect(sumSoFar(t.steps, 4)).toEqual({ newest: '0', rest: '4173', digits: 5 });
		expect(run.arith?.sum).toBe('4173');
	});

	it('writes a row as the table does', () => {
		expect(mealyRowText(t.program.rows[t.steps[0].row])).toBe('0 6 7 → 1 3');
	});
});

describe('the machine and the certificate', () => {
	it('merges the adder into four edges, each with its rule and rows', () => {
		const edges = mealyEdges(t.program.rows, t.program.states);
		expect(Object.fromEntries(edges.map((e) => [`${e.from}>${e.to}`, [e.rule, e.rows]]))).toEqual({
			'0>0': ['a+b ≤ 9 / a+b', 55],
			'0>1': ['a+b ≥ 10 / a+b−10', 45],
			'1>0': ['a+b ≤ 8 / a+b+1', 45],
			'1>1': ['a+b ≥ 9 / a+b−9', 55]
		});
	});

	it('gives an edge no rule when one of its rows does not add', () => {
		const rows = t.program.rows.map((r) =>
			r.s === '0' && r.a === '6' && r.b === '7' ? { ...r, o: '4' } : r
		);
		const edges = mealyEdges(rows, t.program.states);
		expect(edges.find((e) => e.key === '0>1')?.rule).toBeNull();
		expect(edges.find((e) => e.key === '0>0')?.rule).toBe('a+b ≤ 9 / a+b');
	});

	it('lays the certificate out as a 10 × 10 block per carry', () => {
		const l = certLayout(t.program.rows, t.program.states);
		expect([l.cols, l.height]).toEqual([21, 10]);
		expect(l.blocks).toEqual([
			{ x: 0, label: '0' },
			{ x: 11, label: '1' }
		]);
		const at = (s: string, a: string, b: string) =>
			l.cells[t.program.rows.findIndex((r) => r.s === s && r.a === a && r.b === b)];
		expect(at('0', '6', '7')).toMatchObject({ x: 7, y: 6 });
		expect(at('1', '0', '9')).toMatchObject({ x: 20, y: 0 });
		expect(new Set(l.cells.map((c) => `${c.x},${c.y}`)).size).toBe(200);
	});

	it('falls back to reading order for a table of another shape', () => {
		const l = certLayout(t.program.rows.slice(0, 150), t.program.states);
		expect(l.blocks).toEqual([]);
		expect(l.cells[0]).toEqual({ k: 0, x: 0, y: 0 });
	});

	it('says what the run did in one line', () => {
		expect(llmNote(run)).toBe(
			'wrote the adder’s 200-row table, added 5 columns, two forwards each · certified, both cells of every row · 5 of 5 columns bitwise equal to their certified row'
		);
	});
});

describe('the subtracter (REASON_FORMAT §2): another table, the same clock', () => {
	// the engine's own run of reason_core's chain, call 3: first − second, both cited results
	const runs: LlmTrace[] = JSON.parse(
		readFileSync(new URL('../../../e2e/fixtures/reason-runs.json', import.meta.url), 'utf8')
	);
	const call = runs[0].reason!.calls[2];
	const sub = asTrace(call.run) as Trace;

	it('names the table from its rows, and the adder stays the adder', () => {
		expect(opOfRows(sub.program.rows)).toBe('sub');
		expect(opOfRows(t.program.rows)).toBe('add');
		expect(opOfRows(t.program.rows.map((r, k) => (k === 5 ? { ...r, o: '9' } : r)))).toBeNull();
		expect(opOfRows([])).toBeNull();
		expect(mealyWords(sub)).toEqual({
			state: 'borrow',
			states: 'borrows',
			out: 'difference',
			sign: '−'
		});
		expect(mealyWords(t)).toEqual({ state: 'carry', states: 'carries', out: 'sum', sign: '+' });
	});

	it('reads its pairs from a tape written with a minus', () => {
		expect(sub.steps[0].event).toMatch(/^\d−\d$/);
		expect(pairAt({ ...sub, steps: [] } as Trace, 0)).toEqual(sub.steps[0].pair);
	});

	it('merges into four edges, each with the subtracter’s rule', () => {
		const rules = mealyEdges(sub.program.rows, sub.program.states).map((e) => [
			e.key,
			e.rows,
			e.rule
		]);
		expect(rules.sort()).toEqual([
			['0>0', 55, 'a−b ≥ 0 / a−b'],
			['0>1', 45, 'a−b ≤ −1 / a−b+10'],
			['1>0', 45, 'a−b ≥ 1 / a−b−1'],
			['1>1', 55, 'a−b ≤ 0 / a−b+9']
		]);
	});

	it('writes the difference, and says so in one line', () => {
		const outs = sumSoFar(sub.steps, sub.steps.length - 1);
		expect((outs.newest + outs.rest).replace(/^0+/, '')).toBe(call.value);
		expect(llmNote(call.run)).toMatch(
			/^wrote the subtracter’s 200-row table, subtracted 32 columns/
		);
	});
});

describe('the Addition suggestion', () => {
	it('writes two numbers of the chosen length, with no leading zero', () => {
		expect(randomNumber(5, () => 0)).toBe('10000');
		expect(randomNumber(3, () => 0.999)).toBe('999');
		for (const d of [10, 100, 1000]) {
			const add = makeAddition(d);
			expect(add.a).toMatch(new RegExp(`^[1-9][0-9]{${d - 1}}$`));
			expect(add.b).toMatch(new RegExp(`^[1-9][0-9]{${d - 1}}$`));
			expect(add.question).toBe(`What is ${add.a} plus ${add.b}?`);
			expect(add.title).toMatch(new RegExp(`, ${(d + 1).toLocaleString('en-US')} columns$`));
		}
		expect(additionTicks(makeAddition(1000))).toBe(1201);
		expect(additionTicks(makeAddition(1000), 64)).toBe(264);
	});
});
