/**
 * Calls in the middle of a transcript (REASON_FORMAT §7) end to end on a scripted model: for each of reason_core's
 * four fixture transcripts the model writes the reference's words and calls, and the engine must append, call by
 * call, the reference's final lines (ids and text), read the same spans, give the same values, rebuild the same
 * response, build every Π fresh at positions 0 …, certify each Π once, stream events that rebuild the run, and free
 * every cache it made. Then the limits, a response with no call, and one call at the start (today's block).
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { beforeAll, describe, expect, it } from 'vitest';
import type { LlmTrace } from '../trace.ts';
import { arith } from './arith-fixtures.ts';
import { Engine, PLAIN_NOTE, type EngineEvent } from './engine.ts';
import { applyEvent, liveTrace, startRun } from './live-view.ts';
import { eventsFromTrace } from './stub.ts';
import { parseGenerated, pyStrip, type Tok } from './pb.ts';
import { piecesOf, reason, reasonTok, type ReasonFixtureCase } from './reason-fixtures.ts';
import { errorFinalText } from './reason.ts';
import { findTokenizer, realTok } from './realtok.ts';
import { FakeLM, FixtureTok, TranscriptLM } from './testkit.ts';

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
const { nl, im_end, endoftext } = reason.ids;
const tokPath = findTokenizer();
let tok: Tok;
beforeAll(async () => {
	tok = tokPath ? await realTok(tokPath) : reasonTok();
});

const lmFor = (c: ReasonFixtureCase, pieces = piecesOf(c)) =>
	new TranscriptLM({ prompt: c.prompt_ids, pieces, end: im_end, decode: (x) => tok.decode(x), nl });
const engineFor = (lm: TranscriptLM | FakeLM, t: Tok = tok) =>
	new Engine(lm, t, { nl, stop: [im_end, endoftext] }, model, host);
const caseNamed = (name: string) => reason.cases.find((c) => c.name === name)!;

/** Every Π a fixture's calls write, by its ids, with the forwards its certificate takes (two per Mealy row). */
function pisOf(c: ReasonFixtureCase) {
	const out = new Map<string, number>();
	for (const call of c.calls) {
		const p = parseGenerated(tok, c.response_ids.slice(call.start, call.end), nl, {
			results: true
		});
		for (const r of p.registers) out.set(r.pi.join(','), r.rows.length);
		for (const r of p.mealy) out.set(r.pi.join(','), 2 * r.rows.length);
	}
	return out;
}

describe('the reference’s transcripts on a scripted model', { timeout: 120_000 }, () => {
	for (const c of reason.cases)
		it(`${c.name}: every call’s spans, final ids and text, and value`, async () => {
			const lm = lmFor(c);
			const engine = engineFor(lm);
			const events: EngineEvent[] = [];
			const out = await engine.ask(c.question, { id: 'x', multiCall: true }, (e) => events.push(e));
			const r = out.reason!;
			expect(r.format).toBe('REASON_FORMAT');
			expect(r.end).toBe('stop');
			expect(r.response_ids).toEqual(c.response_ids);
			expect(r.calls).toHaveLength(c.calls.length);
			r.calls.forEach((got, i) => {
				const want = c.calls[i];
				expect(got.k).toBe(want.call);
				expect([got.start, got.end]).toEqual([want.start, want.end]);
				expect(got.final_ids).toEqual(want.final_ids);
				expect(got.final_text).toBe(want.final_text);
				expect(got.value).toBe(want.value);
				expect(got.error).toBe(want.error);
				expect(got.mode).toBe(want.mode);
				expect(got.spans).toEqual(want.spans);
				expect(got.how).toEqual(want.how);
				expect(got.program).toBe(tok.decode(c.response_ids.slice(want.start, want.end)));
				expect(got.run.id).toBe(`x/call-${want.call}`);
				if (want.error) {
					expect(got.certified).toBeNull();
					expect(got.run.registers).toEqual([]);
					expect(got.run.note).toBe(`the clock could not run call ${want.call}: ${want.error}`);
				} else {
					expect(got.certified).toBe(true);
					expect(got.run.registers.every((x) => x.certificate.all_ok && x.exact)).toBe(true);
					expect(got.run.final_text).toBe(pyStrip(want.final_text));
				}
				// what the spans hold
				got.read.forEach((rd, j) => {
					const sp = want.spans[j];
					if (sp[0] === 'result')
						expect(rd).toEqual({ from: { result: sp[1] }, text: c.calls[sp[1] - 1].value });
					else
						expect(rd).toEqual({
							from: { source: sp[0] },
							text: (sp[0] === 0 ? c.question : want.notes).slice(sp[1], sp[2])
						});
				});
			});
			// the segments: text, call, …, text, and the answer after the last final
			const last = c.calls.at(-1)!;
			const after = tok.decode(c.response_ids.slice(last.end + last.final_ids.length));
			expect(r.segments.map((s) => s.kind)).toEqual([
				...c.calls.flatMap(() => ['text', 'call']),
				'text'
			]);
			expect(r.segments.at(-1)).toEqual({ kind: 'text', text: after });
			expect(out.answer).toBe(pyStrip(after));
			expect(out.final_text).toBe(pyStrip(last.final_text));

			// every tick ran right after a Π built fresh at positions 0 …, never where the call sits in the transcript
			const pis = pisOf(c);
			expect(lm.blocks.length).toBeGreaterThan(0);
			for (const b of lm.blocks) {
				expect(pis.has(b.pi.join(','))).toBe(true);
				expect(b.at).toBe(b.pi.length);
			}
			// each Π certified once (the adder's again in a chain would be 400 forwards more), then the ticks
			const cert = [...pis.values()].reduce((a, n) => a + n, 0);
			const run = r.calls.reduce(
				(a, k) =>
					a + k.run.registers.reduce((b, x) => b + (x.program.mealy ? 2 : 1) * x.ticks.real, 0),
				0
			);
			expect(lm.ticks).toBe(cert + run);

			// the events rebuild the run, call by call
			let live = startRun('x', c.question, { model, host });
			let finals = 0;
			for (const ev of events) {
				live = applyEvent(live, ev);
				if (ev.type === 'final') {
					finals++;
					expect(live.reason?.calls).toHaveLength(finals);
					expect(live.reason?.current).toBeNull();
				}
				if (ev.type === 'call') expect(live.reason?.current?.k).toBe(ev.k);
			}
			expect(liveTrace(live)).toBe(out);
			expect(live.reason?.calls).toEqual(r.calls);
			expect(live.reason?.segments).toEqual(r.segments);

			// no session is kept for pokes: only the certified Πs stay, until the engine goes
			expect(lm.live.size).toBe(pis.size);
			engine.dispose();
			expect(lm.live.size).toBe(0);
		});

	it('the error is the reference’s line, and the retry reads the result the error did not make', async () => {
		const c = caseNamed('error_then_retry');
		const out = await engineFor(lmFor(c)).ask(c.question, { id: 'x', multiCall: true }, () => {});
		const [one, bad, retry] = out.reason!.calls;
		expect(bad.final_text).toBe(errorFinalText('first number: no result 5'));
		expect(bad.value).toBeNull();
		expect(retry.value).toBe((2n * BigInt(one.value!)).toString());
		expect(retry.run.arith?.from).toEqual([{ result: 1 }, { result: 1 }]);
		expect(retry.run.arith?.op).toBe('add');
	});

	it('a chain is exact end to end: add, add, then subtract the results', async () => {
		const c = caseNamed('chain_add_add_sub');
		const out = await engineFor(lmFor(c)).ask(c.question, { id: 'x', multiCall: true }, () => {});
		const [a, b, d] = out.reason!.calls;
		const nums = c.question.match(/\d{20,}/g)!.map(BigInt);
		expect(BigInt(a.value!)).toBe(nums[0] + nums[1]);
		expect(BigInt(b.value!)).toBe(nums[2] + nums[3]);
		const want = BigInt(a.value!) - BigInt(b.value!);
		expect(BigInt(d.value!)).toBe(want < 0n ? -want : want);
		const sub = d.run.arith!;
		expect([sub.op, sub.adder, sub.check, sub.sum]).toEqual(['sub', false, d.value, d.value]);
		expect(d.run.registers[0].program.events[0]).toMatch(/^\d−\d$/);
		expect(d.run.registers[0].final).toBe('0');
		expect(d.run.title).toBe(`Call 3, ${sub.columns} columns`);
	});

	it('reads the tape from the notes, and the second number from the question after a first from the notes', async () => {
		const lies = caseNamed('notes_tape_web_of_lies');
		const t = await engineFor(lmFor(lies)).ask(
			lies.question,
			{ id: 'x', multiCall: true },
			() => {}
		);
		const call = t.reason!.calls[0];
		expect(call.spans[0][0]).toBe(1);
		expect(call.run.input.events).toHaveLength(40);
		expect(call.run.input.char_spans).toHaveLength(40);
		const mixed = caseNamed('notes_first_question_second');
		const m = await engineFor(lmFor(mixed)).ask(
			mixed.question,
			{ id: 'x', multiCall: true },
			() => {}
		);
		expect(m.reason!.calls[0].run.arith?.from).toEqual([{ source: 1 }, { source: 0 }]);
		expect(m.reason!.calls[0].read[0].text).toBe('4321');
	});

	it('runs 8 calls, refuses the 9th to the 11th with an error line, and the 12th ends the response', async () => {
		const c = caseNamed('chain_add_add_sub');
		const one = c.calls[0];
		const call = c.response_ids.slice(one.start, one.end);
		const pieces = [c.response_ids.slice(0, one.end), ...Array(11).fill(call), piecesOf(c).at(-1)!];
		const lm = lmFor(c, pieces);
		const engine = engineFor(lm);
		const out = await engine.ask(c.question, { id: 'x', multiCall: true }, () => {});
		const calls = out.reason!.calls;
		expect(calls).toHaveLength(12);
		expect(out.reason!.end).toBe('hard stop');
		expect(calls.slice(0, 8).every((k) => k.value === one.value && k.certified)).toBe(true);
		for (const k of calls.slice(8, 11)) {
			expect(k.error).toBe('too many calls');
			expect(k.final_text).toBe(errorFinalText('too many calls'));
			expect(k.value).toBeNull();
		}
		expect([calls[11].error, calls[11].final_ids, calls[11].final_text]).toEqual([
			'hard stop',
			null,
			null
		]);
		// the response ends at the 12th call's <exec/>: nothing appended, and the last piece never written
		expect(out.reason!.response_ids).toHaveLength(calls[11].end);
		expect(out.reason!.segments.at(-1)).toEqual({ kind: 'call', k: 12 });
		// the adder's Π is certified once for all 8 runs
		expect(lm.ticks).toBe(400 + 8 * 2 * calls[0].run.arith!.columns);
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});

	it('a stop mid-transcript frees every cache', async () => {
		const c = caseNamed('chain_add_add_sub');
		const lm = lmFor(c);
		const engine = engineFor(lm);
		const ctl = new AbortController();
		let finals = 0;
		await expect(
			engine.ask(c.question, { id: 'x', multiCall: true, signal: ctl.signal }, (e) => {
				if (e.type === 'final' && ++finals === 2) ctl.abort();
			})
		).rejects.toThrow('stopped');
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});
});

describe(
	'with calls switched on, a response with one call or none reads as today',
	{ timeout: 60_000 },
	() => {
		const e = arith.examples[1]; // What is 4096 plus 77?
		const atok = () =>
			tokPath
				? tok
				: FixtureTok.from([], arith.special, { tokens: arith.tokens, encoded: arith.encoded });

		it('one call at the start, quoting the question: today’s block, final line and words', async () => {
			const t = atok();
			const words = e.answer_ids.filter((x) => x !== arith.ids.im_end);
			const script = {
				prompt: e.chat_prompt_ids,
				end: arith.ids.im_end,
				finalOpen: t.encode('\n<final>'),
				finalClose: t.encode(' </final>\n'),
				words: () => words,
				mealy: { nl }
			};
			const today = await engineFor(new FakeLM({ ...script, program: e.program_ids }), t).ask(
				e.question,
				{ id: 'x' },
				() => {}
			);
			const lm = new TranscriptLM({
				prompt: e.chat_prompt_ids,
				pieces: [e.program_ids, words],
				end: arith.ids.im_end,
				decode: (x) => t.decode(x),
				nl
			});
			const out = await engineFor(lm, t).ask(e.question, { id: 'x', multiCall: true }, () => {});
			const call = out.reason!.calls[0];
			expect(call.final_ids).toEqual(e.final_ids);
			expect(pyStrip(call.final_text!)).toBe(today.final_text);
			expect(out.answer).toBe(today.answer);
			expect(call.run.ctx).toBeNull();
			const r = call.run.registers[0];
			const r0 = today.registers[0];
			expect(r.steps.map((s) => [s.s, s.t, s.o, s.event])).toEqual(
				r0.steps.map((s) => [s.s, s.t, s.o, s.event])
			);
			// the scripted models' margins differ; the rows and their verdicts do not
			const rows = (x: typeof r) => x.program.rows.map((w) => [w.s, w.a, w.b, w.t, w.o, w.ok]);
			expect(rows(r)).toEqual(rows(r0));
			expect(call.run.arith?.numbers).toEqual(today.arith?.numbers);
			expect(call.run.arith?.spans).toEqual(today.arith?.spans);
		});

		it('no call: today’s direct answer, in today’s shape', async () => {
			const t = atok();
			const words = e.answer_ids.filter((x) => x !== arith.ids.im_end);
			const script = {
				prompt: e.chat_prompt_ids,
				end: arith.ids.im_end,
				finalOpen: t.encode('\n<final>'),
				finalClose: t.encode(' </final>\n'),
				words: () => [],
				program: words
			};
			const strip = (x: LlmTrace) => ({
				...x,
				at: '',
				timing: null,
				compile: { ...x.compile, seconds: 0 }
			});
			const today = await engineFor(new FakeLM(script), t).ask(e.question, { id: 'x' }, () => {});
			const out = await engineFor(new FakeLM(script), t).ask(
				e.question,
				{ id: 'x', multiCall: true },
				() => {}
			);
			expect(out.note).toBe(PLAIN_NOTE);
			expect(out.reason).toBeUndefined();
			expect(strip(out)).toEqual(strip(today));
			expect(Object.keys(out.timing!)).toEqual(Object.keys(today.timing!));
		});
	}
);

describe(
	'the runs the page’s stand-in plays (e2e/fixtures/reason-runs.json)',
	{ timeout: 120_000 },
	() => {
		it('play back as events that rebuild them, call by call', () => {
			const runs: LlmTrace[] = JSON.parse(
				readFileSync(new URL('../../../../e2e/fixtures/reason-runs.json', import.meta.url), 'utf8')
			);
			for (const t of runs) {
				let live = startRun(t.id, t.prompt, { model, host });
				const seen: number[] = [];
				for (const ev of eventsFromTrace(t)) {
					live = applyEvent(live, ev);
					if (ev.type === 'ticks') {
						// mid-call the panels read the current call's run
						const cur = liveTrace(live);
						expect(cur.id).toBe(`${t.id}/call-${live.reason!.current!.k}`);
						expect(cur.registers[ev.index].steps.length).toBe(ev.done);
					}
					if (ev.type === 'final') seen.push(ev.call.k);
				}
				expect(seen).toEqual(t.reason!.calls.map((c) => c.k));
				expect(live.trace).toBe(t);
				expect(live.reason?.segments).toEqual(t.reason!.segments);
			}
		});

		it('are the engine’s own', async () => {
			const file = new URL('../../../../e2e/fixtures/reason-runs.json', import.meta.url);
			const got: LlmTrace[] = [];
			for (const name of ['chain_add_add_sub', 'error_then_retry', 'notes_tape_web_of_lies']) {
				const c = caseNamed(name);
				const engine = engineFor(lmFor(c));
				const out = await engine.ask(
					c.question,
					{ id: `reason-${name}`, multiCall: true },
					() => {}
				);
				engine.dispose();
				got.push(normalise(out));
			}
			if (process.env.WRITE_FIXTURES) writeFileSync(file, JSON.stringify(got) + '\n');
			expect(JSON.parse(readFileSync(file, 'utf8'))).toEqual(got);
		});
	}
);

/** Times vary run to run. */
function normalise(t: LlmTrace): LlmTrace {
	const out: LlmTrace = JSON.parse(JSON.stringify(t));
	const fix = (x: LlmTrace) => {
		x.at = '2026-10-28T00:00:00.000Z';
		x.compile.seconds = 0.5;
		x.timing = Object.fromEntries(Object.keys(x.timing ?? {}).map((k) => [k, 0.5]));
		for (const r of x.registers) {
			r.ticks.seconds = 0.05;
			r.ticks.ms_per_tick = 10;
		}
	};
	fix(out);
	for (const c of out.reason?.calls ?? []) fix(c.run);
	return out;
}
