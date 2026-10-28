/**
 * The loop on a scripted LM: given each recorded trace's real program ids, the engine must rebuild the recorded run's
 * table, tape, certificate, ticks, `<final>` line, row lines and machine layout exactly (the stand-in runs any table
 * it is shown exactly, as the certified executor did), score it against the question's truth, poke it the way the
 * recorded pokes went, stop where the Python stops, free every cache it made, and stream events that rebuild the run.
 */
import { readFileSync } from 'node:fs';
import { beforeAll, describe, expect, it } from 'vitest';
import { symEig } from './codebook.ts';
import { Cancelled, Engine, type EngineEvent, type Truth } from './engine.ts';
import { applyEvent, liveTrace, startRun } from './live-view.ts';
import { chatPrompt, type Tok } from './pb.ts';
import { findTokenizer, realTok } from './realtok.ts';
import { FakeLM, FixtureTok, type FakeScript, type FixtureCase } from './testkit.ts';
import type { LlmTrace } from '../trace.ts';

const ref = JSON.parse(readFileSync(new URL('./fixtures/reference.json', import.meta.url), 'utf8'));
const prompts: {
	prompts: { id: string; question: string; truth: Truth; recorded: string | null }[];
} = JSON.parse(readFileSync('static/interpreter/prompts.json', 'utf8'));
const recorded = (id: string): LlmTrace =>
	JSON.parse(readFileSync(`static/traces/${id}.json`, 'utf8'));
const traces = (ref.cases as (FixtureCase & { name: string })[])
	.filter((c) => c.name.startsWith('trace:'))
	.map((c) => recorded(c.name.slice(6)))
	.filter((t) => t.ctx);

const model = {
	name: 'Savant-4B preview',
	compile_adapter: 's2g-s1/adapter_step750',
	executor_adapter: 's2g-s1/adapter_step750',
	adapter_sha256: { compile: '', executor: '' },
	tokenizer_sha256: '',
	promptbox_commit: '71268f94861079c34572b04eb87ac5aaa7888f96',
	about: 'test'
};
const host = { gpu: 'a test double', cpu: null, avx512f: null };

const tokPath = findTokenizer();
let tok: Tok;
beforeAll(async () => {
	tok = tokPath
		? await realTok(tokPath)
		: FixtureTok.from(ref.cases, ref.special, { tokens: ref.tokens, encoded: ref.encoded });
});

function script(t: LlmTrace, extra: Partial<FakeScript> = {}): FakeScript {
	return {
		prompt: tok.encode(chatPrompt(t.prompt)),
		program: t.ctx!.program_ids,
		end: ref.im_end,
		finalOpen: tok.encode('\n<final>'),
		finalClose: tok.encode(' </final>\n'),
		// the recorded words when the tokenizer can write them, else the state ids themselves
		words: () => (tokPath ? tok.encode(t.answer) : [t.ctx!.finals[t.registers[0].name]]),
		...extra
	};
}

const engineFor = (lm: FakeLM) =>
	new Engine(lm, tok, { nl: ref.nl, stop: [ref.im_end, ref.endoftext] }, model, host);

describe('the loop on a scripted model, against every recorded run', { timeout: 60_000 }, () => {
	for (const t of traces)
		it(`${t.id}: same table, tape, certificate, ticks and <final> line`, async () => {
			const lm = new FakeLM(script(t));
			const engine = engineFor(lm);
			const events: EngineEvent[] = [];
			const truth = prompts.prompts.find((p) => p.recorded === t.id)?.truth ?? null;
			const out = await engine.ask(t.prompt, { id: 'x', title: t.title, truth }, (e) =>
				events.push(e)
			);

			expect(out.compile.text).toBe(t.compile.text);
			expect(out.compile.tokens).toBe(t.compile.tokens);
			expect(out.input.events).toEqual(t.input.events);
			expect(out.input.char_spans).toEqual(t.input.char_spans);
			expect(out.input.anchors).toEqual(t.input.anchors);
			expect(out.ctx!.tape).toEqual(t.ctx!.tape);
			expect(out.ctx!.finals).toEqual(t.ctx!.finals);
			expect(out.ctx!.registers.map((r) => [r.name, r.start, r.rows])).toEqual(
				t.ctx!.registers.map((r) => [r.name, r.start, r.rows])
			);
			expect(out.final_text).toBe(t.final_text);
			if (tokPath) expect(out.answer).toBe(t.answer);
			expect(out.registers.length).toBe(t.registers.length);
			out.registers.forEach((r, k) => {
				const want = t.registers[k];
				expect(r.name).toBe(want.name);
				expect(r.program.rows.map((x) => [x.s, x.b, x.t, x.ok])).toEqual(
					want.program.rows.map((x) => [x.s, x.b, x.t, x.ok])
				);
				for (const k of ['states', 'events', 'start', 'row_lines', 'registers', 'diagram'] as const)
					expect(r.program[k]).toEqual(want.program[k]);
				expect(r.certificate.all_ok).toBe(true);
				expect(r.steps.map((s) => [s.i, s.event, s.s, s.row, s.t])).toEqual(
					want.steps.map((s) => [s.i, s.event, s.s, s.row, s.t])
				);
				expect(r.steps.every((s) => s.eq)).toBe(true);
				expect(r.final).toBe(want.final);
				expect(r.ticks.real).toBe(t.ctx!.tape.length);
				expect(r.codebook.names).toEqual(want.codebook.names);
				expect(r.steps[0].xyz).toHaveLength(3);
			});
			if (truth) {
				expect(out.truth).toBe(truth.answer);
				expect(out.score).toMatchObject({
					parsed: true,
					table_exact: true,
					rows_wrong: 0,
					tape_exact: true,
					certified: true,
					run_final_right: true
				});
				if (tokPath) expect(out.score!.answer_correct).toBe(t.score!.answer_correct);
				out.registers.forEach((r) => expect(r.exact).toBe(true));
			}

			// the events rebuild the run, step by step
			let run = startRun('x', t.prompt, { title: t.title, model, host });
			let sawPartial = false;
			for (const e of events) {
				run = applyEvent(run, e);
				if (run.stage === 'run' && run.registers[0]?.steps.length) sawPartial = true;
			}
			expect(sawPartial).toBe(true);
			expect(run.stage).toBe('done');
			expect(liveTrace(run)).toBe(out);
			const kinds = events.map((e) => e.type);
			expect(kinds.indexOf('program')).toBeLessThan(kinds.indexOf('tape'));
			expect(kinds.filter((k) => k === 'row')).toHaveLength(
				t.registers.reduce((a, r) => a + r.program.rows.length, 0)
			);
			expect(kinds.at(-1)).toBe('trace');

			// one cache for the prompt and program, one per register's Π; none after dispose
			expect(lm.live.size).toBe(1 + new Set(out.ctx!.registers.map((r) => r.rows.join())).size);
			engine.dispose();
			expect(lm.live.size).toBe(0);
		});
});

describe('pokes', { timeout: 60_000 }, () => {
	const t = traces.find((x) => x.id === 'live-prose-train-256')!;
	it('reruns the recorded pokes from the forced state and lands where the table says', async () => {
		const lm = new FakeLM(script(t));
		const engine = engineFor(lm);
		const truth = prompts.prompts.find((p) => p.recorded === t.id)!.truth;
		const out = await engine.ask(t.prompt, { id: 'x', truth }, () => {});
		const reg = t.registers[0];
		for (const p of reg.pokes) {
			const forced = reg.program.states.indexOf(p.forced);
			const ticksBefore = lm.ticks;
			const got = await engine.poke(t.prompt, out.ctx!, reg.name, p.step, forced, { truth });
			expect(got.final).toBe(p.final);
			expect(got.predicted_state).toBe(p.predicted_state);
			expect(got.match).toBe(true);
			expect(got.from).toBe(p.from);
			expect(got.predicted).toBe(p.predicted);
			expect(got.ticks).toBe(t.ctx!.tape.length - p.step);
			expect(got.ticks_equal).toBe(got.ticks);
			// the certificate is reused: only the poke's own ticks ran
			expect(lm.ticks - ticksBefore).toBe(got.ticks);
		}
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});

	it('pokes a recorded run it never ran (rebuilding its caches) and rejects bad requests', async () => {
		const lm = new FakeLM(script(t));
		const engine = engineFor(lm);
		const reg = t.registers[0];
		const got = await engine.poke(t.prompt, t.ctx!, reg.name, 10, 0);
		expect(got.match).toBe(true);
		expect(got.ticks).toBe(t.ctx!.tape.length - 10);
		await expect(engine.poke(t.prompt, t.ctx!, 'nope', 1, 0)).rejects.toThrow('no register');
		await expect(engine.poke(t.prompt, t.ctx!, reg.name, 10_000, 0)).rejects.toThrow(
			'off the tape'
		);
		await expect(engine.poke(t.prompt, t.ctx!, reg.name, 1, 99)).rejects.toThrow('forced state');
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});
});

describe('where the loop stops, and what goes wrong', { timeout: 60_000 }, () => {
	const t = traces.find((x) => x.id === 'live-prose-train-256')!;

	it('a reply with no program is the answer, with no run', async () => {
		const lm = new FakeLM(script(t, { program: t.ctx!.program_ids.slice(0, 5) }));
		const engine = engineFor(lm);
		const out = await engine.ask(t.prompt, { id: 'x' }, () => {});
		expect(out.note).toBe('the model answered without writing a program');
		expect(out.registers).toEqual([]);
		expect(out.compile.finish).toBe('stop');
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});

	it('a tape the clock cannot read stops before the run, with the Python reason', async () => {
		const c = ref.cases.find((x: { name: string }) => x.name === 'crafted:not_event');
		if (!tokPath) (tok as FixtureTok).learn(chatPrompt(c.question), c.chat_prompt_ids);
		const lm = new FakeLM({ ...script(t), prompt: c.chat_prompt_ids, program: c.program_ids });
		const engine = engineFor(lm);
		const out = await engine.ask(c.question, { id: 'x' }, () => {});
		expect(out.note).toBe(`the loop stopped before the run: ${c.why}`);
		expect(out.input.anchors).toEqual(c.parsed.anchors);
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});

	it('a row the model gets wrong fails the certificate and the run follows the model', async () => {
		const [s, e, ,] = t.ctx!.registers[0].rows[4];
		const lm = new FakeLM(script(t, { wrong: new Map([[`${s},${e}`, s]]) }));
		const engine = engineFor(lm);
		const out = await engine.ask(t.prompt, { id: 'x' }, () => {});
		const r = out.registers[0];
		expect(r.certificate.all_ok).toBe(false);
		expect(r.certificate.rows_wrong).toBe(1);
		expect(r.program.rows[4].ok).toBe(false);
		expect(r.program.rows[4].argmax).toBe(r.program.rows[4].s);
		const used = r.steps.filter((x) => x.row === 4);
		expect(used.length).toBeGreaterThan(0);
		expect(used.every((x) => x.t === x.s)).toBe(true);
		engine.dispose();
	});

	it('lookup mode runs the first events and reads the rest from the certified rows', async () => {
		const full = await engineFor(new FakeLM(script(t))).ask(t.prompt, { id: 'a' }, () => {});
		const lm = new FakeLM(script(t));
		const engine = engineFor(lm);
		const events: EngineEvent[] = [];
		const out = await engine.ask(t.prompt, { id: 'b', lookupAfter: 16 }, (e) => events.push(e));
		const r = out.registers[0];
		expect(r.steps.map((x) => x.t)).toEqual(full.registers[0].steps.map((x) => x.t));
		expect(r.ticks.real).toBe(16);
		expect(r.ticks.lookup).toBe(t.ctx!.tape.length - 16);
		expect(r.steps.filter((x) => x.lookup)).toHaveLength(t.ctx!.tape.length - 16);
		expect(r.steps.slice(0, 16).every((x) => x.eq && !x.lookup)).toBe(true);
		// one Π prefill counts as a tick in the stand-in: rows + 16 real ticks
		expect(lm.ticks).toBe(1 + r.program.rows.length + 16);
		let run = startRun('b', t.prompt, { model, host });
		for (const e of events) run = applyEvent(run, e);
		expect(run.trace).toBe(out);
		engine.dispose();
	});

	it('ticks whose bits differ from their row are counted, not hidden', async () => {
		const lm = new FakeLM(script(t, { jitter: (n) => n > 20 && n % 3 === 0 }));
		const engine = engineFor(lm);
		const out = await engine.ask(t.prompt, { id: 'x' }, () => {});
		const r = out.registers[0];
		expect(r.ticks.bitwise_equal_to_certified_row).toBeLessThan(r.ticks.real);
		expect(r.steps.filter((x) => !x.eq).length).toBe(
			r.ticks.real - r.ticks.bitwise_equal_to_certified_row
		);
		engine.dispose();
	});

	it('stops when asked, frees what it made, and refuses a second question while busy', async () => {
		const lm = new FakeLM(script(t));
		const engine = engineFor(lm);
		const ctl = new AbortController();
		const p = engine.ask(t.prompt, { id: 'x', signal: ctl.signal }, (e) => {
			if (e.type === 'ticks' && e.done > 3) ctl.abort();
		});
		await expect(engine.ask(t.prompt, { id: 'y' }, () => {})).rejects.toThrow('busy');
		await expect(p).rejects.toBeInstanceOf(Cancelled);
		engine.dispose();
		expect(lm.live.size).toBe(0);
	});
});

describe('the state view', () => {
	it('diagonalises a symmetric matrix', () => {
		const n = 5;
		const a = new Float64Array(n * n);
		for (let i = 0; i < n; i++)
			for (let j = i; j < n; j++)
				a[i * n + j] = a[j * n + i] = Math.sin(i * 7 + j * 3) + (i === j ? 3 : 0);
		const { vals, vecs } = symEig(a, n);
		for (let k = 0; k < n; k++)
			for (let i = 0; i < n; i++) {
				let av = 0;
				for (let j = 0; j < n; j++) av += a[i * n + j] * vecs[j * n + k];
				expect(av).toBeCloseTo(vals[k] * vecs[i * n + k], 9);
			}
		expect([...vals]).toEqual([...vals].sort((x, y) => y - x));
	});
});
