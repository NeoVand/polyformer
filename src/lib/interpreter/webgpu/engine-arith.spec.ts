/**
 * Number mode end to end on the scripted LM (ARITH_FORMAT §4 to §7): for each of arith_core's fixture questions the
 * engine must read the same pairs, certify the 200 rows with two forwards each (once per Π), run two forwards per
 * column, give the fixture's states, outputs and `<final>` ids, budget the words for the sum, score the run, poke a
 * carry to where the table says, stop where the reference stops, and free every cache it made.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { beforeAll, describe, expect, it } from 'vitest';
import type { LlmTrace } from '../trace.ts';
import { arith } from './arith-fixtures.ts';
import { ANSWER_MAX_TOKENS, Engine, type EngineEvent } from './engine.ts';
import { applyEvent, liveTrace, startRun } from './live-view.ts';
import { chatPrompt, type Tok } from './pb.ts';
import { findTokenizer, realTok } from './realtok.ts';
import { FakeLM, FixtureTok, type FakeScript } from './testkit.ts';

const model = {
	name: 'Savant-4B preview',
	compile_adapter: 'test',
	executor_adapter: 'test',
	adapter_sha256: { compile: '', executor: '' },
	tokenizer_sha256: '',
	promptbox_commit: '',
	about: 'test'
};
const host = { gpu: 'a test double', cpu: null, avx512f: null };
const tokPath = findTokenizer();
let tok: Tok;
beforeAll(async () => {
	tok = tokPath
		? await realTok(tokPath)
		: FixtureTok.from([], arith.special, { tokens: arith.tokens, encoded: arith.encoded });
});

const { nl, im_end } = arith.ids;
const words = (ids: number[]) => ids.filter((x) => x !== im_end);

function script(e: (typeof arith.examples)[number], extra: Partial<FakeScript> = {}): FakeScript {
	return {
		prompt: e.chat_prompt_ids,
		program: e.program_ids,
		end: im_end,
		finalOpen: tok.encode('\n<final>'),
		finalClose: tok.encode(' </final>\n'),
		words: () => words(e.answer_ids),
		mealy: { nl },
		...extra
	};
}
const engineFor = (lm: FakeLM) => new Engine(lm, tok, { nl, stop: [im_end, 151643] }, model, host);

describe('number mode on a scripted model', { timeout: 60_000 }, () => {
	for (const e of arith.examples)
		it(e.question, async () => {
			const lm = new FakeLM(script(e));
			const engine = engineFor(lm);
			const events: EngineEvent[] = [];
			const [a, b] = e.reading.numbers;
			const out = await engine.ask(e.question, { id: 'x', addition: { a, b } }, (ev) =>
				events.push(ev)
			);
			expect(out.note).toBeNull();
			expect(out.arith?.numbers).toEqual(e.reading.numbers);
			expect(out.arith?.spans).toEqual(e.reading.spans);
			expect(out.arith?.columns).toBe(e.reading.pairs.length);
			expect(out.arith?.adder).toBe(true);
			expect(out.ctx?.pairs).toEqual(e.reading.pairs);
			expect(out.ctx?.mealy?.run).toEqual(e.run.states);
			expect(out.ctx?.mealy?.outputs).toEqual(e.run.outputs);
			expect(out.final_text).toBe(e.final_text.trim());
			expect(out.arith?.sum).toBe(e.sum);
			expect(out.arith?.check).toBe(e.sum);
			expect(out.answer).toBe(e.answer_text);
			expect(out.truth).toBe(e.sum);
			expect(out.score).toEqual({
				parsed: true,
				table_exact: true,
				tape_exact: true,
				certified: true,
				run_final_right: true,
				sum_right: true,
				answer_correct: true
			});
			const r = out.registers[0];
			expect(r.program.mealy).toEqual({ output: 's' });
			expect(r.program.rows).toHaveLength(200);
			expect(r.program.rows.every((x) => x.ok && x.a !== undefined && x.o !== undefined)).toBe(
				true
			);
			expect(r.program.row_lines?.every((k) => k >= 0)).toBe(true);
			expect(r.certificate.all_ok).toBe(true);
			expect(r.steps.map((x) => x.o)).toEqual(e.run.outputs.map((x) => tok.decode([x])));
			expect(r.steps.every((x) => x.eq && x.pair && x.m2 !== undefined)).toBe(true);
			expect(r.exact).toBe(true);
			// one prefill of Π, two forwards per row, two per column
			expect(lm.ticks).toBe(1 + 2 * 200 + 2 * e.reading.pairs.length);
			// every block right after Π, and the first tick's two as the fixture lays them out (§4)
			const span = (b: { ids: number[]; at: number }) => b.ids.map((_, i) => b.at + i);
			expect(lm.blocks.every((b) => b.at === e.parsed.register.pi_len)).toBe(true);
			const [f1, f2] = lm.blocks.slice(400, 402);
			expect([f1.ids, span(f1)]).toEqual([
				e.first_tick.forward1.ids,
				e.first_tick.forward1.positions
			]);
			expect([f2.ids, span(f2)]).toEqual([
				e.first_tick.forward2.ids,
				e.first_tick.forward2.positions
			]);
			// certification takes the same path: [s][a][b], then [s][a][b][t] with t forward 1's argmax
			expect(lm.blocks.slice(0, 400)).toEqual(
				out.ctx!.mealy!.rows.flatMap(([s, a, b, t]) => [
					{ ids: [s, a, b], at: 1200 },
					{ ids: [s, a, b, t], at: 1200 }
				])
			);

			// the events rebuild the run
			let run = startRun('x', e.question, { model, host });
			for (const ev of events) run = applyEvent(run, ev);
			expect(liveTrace(run)).toBe(out);

			// the same table again: the certificate is reused, only the columns run
			const before = lm.ticks;
			await engine.ask(e.question, { id: 'y' }, () => {});
			expect(lm.ticks - before).toBe(2 * e.reading.pairs.length);

			expect(lm.live.size).toBe(2); // the prompt + program cache and the one certified Π
			engine.dispose();
			expect(lm.live.size).toBe(0);
		});

	const e = arith.examples[1]; // What is 4096 plus 77?

	it('pokes a carry and lands where the table says', async () => {
		const lm = new FakeLM(script(e));
		const engine = engineFor(lm);
		const out = await engine.ask(e.question, { id: 'x' }, () => {});
		// entering column 2 the carry is 1; force 0: 4096 + 77 without that carry is 4073
		expect(out.registers[0].steps[1].t).toBe('1');
		const p = await engine.poke(e.question, out.ctx!, 'c', 2, 0);
		expect(p.from).toBe('1');
		expect(p.forced).toBe('0');
		expect(p.match).toBe(true);
		expect(p.sum_after).toBe('4073');
		expect(p.predicted_sum).toBe('4073');
		expect(p.ticks).toBe(3);
		expect(p.ticks_equal).toBe(3);
		await expect(engine.poke(e.question, out.ctx!, 'c', 99, 0)).rejects.toThrow('off the tape');
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});

	it('lookup mode runs the first columns and reads the rest from the certified rows', async () => {
		const e3 = arith.examples[0];
		const lm = new FakeLM(script(e3));
		const engine = engineFor(lm);
		const out = await engine.ask(e3.question, { id: 'x', lookupAfter: 4 }, () => {});
		const r = out.registers[0];
		expect(out.ctx?.mealy?.outputs).toEqual(e3.run.outputs);
		expect(r.ticks.real).toBe(4);
		expect(r.ticks.lookup).toBe(e3.reading.pairs.length - 4);
		expect(lm.ticks).toBe(1 + 400 + 2 * 4);
		engine.dispose();
	});

	it('a wrong carry row fails the certificate and the run follows the model', async () => {
		const d0 = arith.ids.digits[0];
		// carry 0, 6 + 7: the model says carry 0 instead of 1
		const key = `${d0},${arith.ids.digits[6]},${arith.ids.digits[7]}`;
		const lm = new FakeLM(script(e, { mealy: { nl, wrongT: new Map([[key, d0]]) } }));
		const engine = engineFor(lm);
		const out = await engine.ask(
			e.question,
			{ id: 'x', addition: { a: '4096', b: '77' } },
			() => {}
		);
		const r = out.registers[0];
		expect(r.certificate.all_ok).toBe(false);
		expect(r.certificate.rows_wrong).toBe(1);
		const bad = r.program.rows.find((x) => x.ok === false)!;
		expect([bad.s, bad.a, bad.b, bad.t, bad.argmax]).toEqual(['0', '6', '7', '1', '0']);
		expect(out.arith?.sum).toBe('4163');
		expect(out.score?.sum_right).toBe(false);
		expect(r.exact).toBe(false);
		expect(r.first_wrong_step).toBe(1);
		engine.dispose();
	});

	it('a wrong output digit fails the certificate on the second forward', async () => {
		const key = `${arith.ids.digits[0]},${arith.ids.digits[6]},${arith.ids.digits[7]}`;
		const lm = new FakeLM(
			script(e, { mealy: { nl, wrongO: new Map([[key, arith.ids.digits[9]]]) } })
		);
		const engine = engineFor(lm);
		const out = await engine.ask(e.question, { id: 'x' }, () => {});
		const bad = out.registers[0].program.rows.find((x) => x.ok === false)!;
		expect([bad.o, bad.argmax2, bad.argmax]).toEqual(['3', '9', undefined]);
		expect(out.arith?.sum).toBe('4179');
		engine.dispose();
	});

	it('ticks whose bits differ from their row are counted per tick, both forwards', async () => {
		const lm = new FakeLM(script(e, { jitter: (n) => n > 401 && n % 2 === 1 }));
		const engine = engineFor(lm);
		const out = await engine.ask(e.question, { id: 'x' }, () => {});
		const r = out.registers[0];
		expect(r.ticks.bitwise_equal_to_certified_row).toBe(0);
		expect(r.certificate.ticks_real).toBe(5);
		engine.dispose();
	});

	for (const f of arith.failures)
		it(`stops before the run as the reference does: ${f.case}`, async () => {
			const lm = new FakeLM({ ...script(e), program: f.program_ids });
			const engine = engineFor(lm);
			const out = await engine.ask(
				f.question,
				{ id: 'x', addition: { a: '4096', b: '77' } },
				() => {}
			);
			expect(out.note).toBe(`the loop stopped before the run: ${f.parse_error ?? f.reading_error}`);
			expect(out.registers).toEqual([]);
			expect(out.score?.sum_right).toBe(false);
			engine.dispose();
			expect(lm.live.size).toBe(0);
		});

	it('is the run the page’s stand-in plays (e2e/fixtures/arith-run.json)', async () => {
		// the browser tests replay this run as the engine's events; the stand-in reruns its table on other numbers
		const file = new URL('../../../../e2e/fixtures/arith-run.json', import.meta.url);
		const lm = new FakeLM(script(e));
		const engine = engineFor(lm);
		const out = await engine.ask(
			e.question,
			{ id: 'arith-run', addition: { a: '4096', b: '77' } },
			() => {}
		);
		engine.dispose();
		// times vary run to run
		const got: LlmTrace = JSON.parse(JSON.stringify(out));
		got.at = '2026-10-27T00:00:00.000Z';
		got.compile.seconds = 0.5;
		got.timing = Object.fromEntries(Object.keys(got.timing ?? {}).map((k) => [k, 0.5]));
		for (const r of got.registers) {
			r.ticks.seconds = 0.05;
			r.ticks.ms_per_tick = 10;
		}
		if (process.env.WRITE_FIXTURES) writeFileSync(file, JSON.stringify(got) + '\n');
		expect(JSON.parse(readFileSync(file, 'utf8'))).toEqual(got);
	});

	it('feeds forward 2 the argmax of forward 1, not the row’s written carry', async () => {
		const d = arith.ids.digits;
		const key = `${d[0]},${d[6]},${d[7]}`;
		const lm = new FakeLM(script(e, { mealy: { nl, wrongT: new Map([[key, d[0]]]) } }));
		const engine = engineFor(lm);
		await engine.ask(e.question, { id: 'x' }, () => {});
		// the certificate's row, then the run's first column (6 + 7), both fed the model's 0
		expect(lm.blocks.filter((b) => b.ids.length === 4 && `${b.ids.slice(0, 3)}` === key)).toEqual([
			{ ids: [d[0], d[6], d[7], d[0]], at: 1200 },
			{ ids: [d[0], d[6], d[7], d[0]], at: 1200 }
		]);
		engine.dispose();
	});

	it.skipIf(!tokPath)('gives the words room for a 1,000-digit sum (ARITH_FORMAT §7)', async () => {
		const a = '7'.repeat(1000);
		const b = '3'.repeat(999);
		const q = `What is ${a} plus ${b}?`;
		const program = tok.encode(arith.examples[1].program_text);
		const sum = (BigInt(a) + BigInt(b)).toString();
		const lm = new FakeLM({
			...script(e),
			prompt: tok.encode(chatPrompt(q)),
			program,
			words: () => tok.encode(`The sum is ${sum}.`)
		});
		const engine = engineFor(lm);
		const out = await engine.ask(q, { id: 'x', addition: { a, b } }, () => {});
		expect(tok.encode(`The sum is ${sum}.`).length).toBeGreaterThan(ANSWER_MAX_TOKENS);
		expect(out.arith?.columns).toBe(1001);
		expect(out.arith?.sum).toBe(sum);
		expect(out.answer).toBe(`The sum is ${sum}.`);
		expect(out.score?.answer_correct).toBe(true);
		engine.dispose();
	});
});

/**
 * The trained model's own runs from ARITH's counted gate (reference.json `model_runs`): its program ids, played back
 * by the scripted LM with each row's two certified margins as the model measured them. The engine must read the
 * same pairs, certify every row with those margins, and give the model's states, outputs, `<final>` line and words.
 */
describe('the trained model’s counted runs, replayed', { timeout: 60_000 }, () => {
	for (const run of arith.model_runs.runs)
		it(`${run.cell}: ${run.question.slice(0, 48)}…`, async () => {
			const d = arith.ids.digits;
			const margins = new Map(
				run.certificate.margins.map(([cell, m1, m2]): [string, [number, number]] => [
					[...cell].map((c) => d[Number(c)]).join(','),
					[m1, m2]
				])
			);
			const lm = new FakeLM({
				prompt: tok.encode(chatPrompt(run.question)),
				program: run.program_ids,
				end: im_end,
				finalOpen: tok.encode('\n<final>'),
				finalClose: tok.encode(' </final>\n'),
				words: () => tok.encode(run.answer_text),
				mealy: { nl, margins }
			});
			const engine = engineFor(lm);
			// the two numbers as the reference's pairs spell them, to score the run against
			const num = (k: 0 | 1) =>
				run.pairs
					.slice(0, -1)
					.map((p) => String(d.indexOf(p[k])))
					.reverse()
					.join('');
			const out = await engine.ask(
				run.question,
				{ id: 'x', addition: { a: num(0), b: num(1) } },
				() => {}
			);
			expect(out.note).toBeNull();
			expect(out.arith?.quotes).toEqual(run.anchors);
			expect(out.ctx?.pairs).toEqual(run.pairs);
			expect(out.ctx?.mealy?.run).toEqual(run.states);
			expect(out.ctx?.mealy?.outputs).toEqual(run.outputs);
			expect(out.final_text).toBe(run.final_text.trim());
			expect(out.answer).toBe(run.answer_text);
			const sum = run.final_text.match(/ s=(\d+) /)![1];
			expect([out.arith?.sum, out.arith?.check]).toEqual([sum, sum]);
			expect(out.score).toEqual({
				parsed: true,
				table_exact: true,
				tape_exact: true,
				certified: true,
				run_final_right: true,
				sum_right: true,
				answer_correct: true
			});
			const r = out.registers[0];
			expect(r.certificate.all_ok).toBe(run.certificate.pass);
			expect(r.certificate.min_margin).toBe(run.certificate.min_margin);
			expect(r.program.rows.map((x) => [`${x.s}${x.a}${x.b}`, x.m, x.m2])).toEqual(
				run.certificate.margins
			);
			expect(r.ticks.bitwise_equal_to_certified_row).toBe(run.pairs.length);
			expect(lm.ticks).toBe(1 + 400 + 2 * run.pairs.length);
			engine.dispose();
			expect(lm.live.size).toBe(0);
		});
});
