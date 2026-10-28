/**
 * A stand-in for the worker, for end-to-end tests of the page (no GPU, no download): it plays a recorded run back as
 * the engine's own events, with a pause between them, and answers pokes by running the run's table. The page uses
 * it only when a test has set `globalThis.__SAVANT_STUB__` before the page loaded.
 */
import { digitPairs, exactSum, readNumbers } from './arith.ts';
import type { EngineEvent } from './engine.ts';
import type { FromWorker, ToWorker } from './protocol.ts';
import { modelById } from './config.ts';
import type { LlmRegister, LlmTrace, ProgramRow } from '../trace.ts';

export interface SavantStub {
	/** the GPU to report; absent means the browser has no WebGPU */
	gpu?: string;
	/** recorded runs to play back, matched by prompt (else the first, with the question swapped in) */
	traces: LlmTrace[];
	/** milliseconds between events */
	delay?: number;
	/** milliseconds the download takes */
	loadMs?: number;
	/** load fails with this message */
	failLoad?: string;
	/** recorded on the page for the test to read */
	asked?: string[];
	lookups?: (number | null)[];
	additions?: ({ a: string; b: string } | null)[];
	/** each question's `multiCall` option (the selected model's flag), null when the page sent none */
	multiCalls?: (boolean | null)[];
	poked?: { register: string; step: number; forced: number }[];
}

export const stubOf = (): SavantStub | null =>
	(globalThis as { __SAVANT_STUB__?: SavantStub }).__SAVANT_STUB__ ?? null;

/** One register's certificate and run as the engine's events. */
function registerEvents(ev: EngineEvent[], r: LlmRegister, index: number) {
	ev.push({ type: 'stage', stage: 'certify', register: r.name, total: r.program.rows.length });
	ev.push({
		type: 'register',
		index,
		name: r.name,
		start: r.program.start,
		states: r.program.states,
		events: r.program.events,
		rows: r.program.rows.map((x) =>
			x.a !== undefined ? { s: x.s, a: x.a, b: x.b, t: x.t, o: x.o } : { s: x.s, b: x.b, t: x.t }
		),
		...(r.program.mealy ? { mealy: r.program.mealy } : {})
	});
	r.program.rows.forEach((row, k) => ev.push({ type: 'row', index, k, row }));
	ev.push({
		type: 'certificate',
		index,
		pass: r.certificate.all_ok,
		rows: r.program.rows.length,
		rows_wrong: r.certificate.rows_wrong ?? 0,
		min_margin: r.certificate.min_margin,
		seconds: 0.1,
		codebook: r.codebook
	});
	ev.push({ type: 'stage', stage: 'run', register: r.name, total: r.steps.length });
	// a number-mode run goes a column at a time, so the written sum fills in
	const batch = r.program.mealy ? 1 : 64;
	for (let i = 0; i < r.steps.length; i += batch)
		ev.push({
			type: 'ticks',
			index,
			steps: r.steps.slice(i, i + batch),
			done: Math.min(r.steps.length, i + batch),
			total: r.steps.length
		});
}

/** Words (and a call) being written, as a few `compile` events and the segment's `program` event. */
function writing(ev: EngineEvent[], text: string, exec: boolean) {
	ev.push({ type: 'stage', stage: 'compile' });
	const tokens = Math.max(1, Math.round(text.length / 3));
	for (let k = 1; k <= 6; k++)
		ev.push({
			type: 'compile',
			text: text.slice(0, Math.round((text.length * k) / 6)),
			tokens: Math.round((tokens * k) / 6),
			seconds: (0.5 * k) / 6
		});
	ev.push({ type: 'program', text, tokens, seconds: 0.5, exec, finish: 'stop' });
}

/** A run with calls in the middle (REASON_FORMAT) as the engine's events: words, a call, its final, and so on. */
function eventsFromReason(t: LlmTrace): EngineEvent[] {
	const r = t.reason!;
	const ev: EngineEvent[] = [];
	ev.push({ type: 'stage', stage: 'prefill', total: 100 });
	ev.push({ type: 'prefill', done: 100, total: 100 });
	let before = '';
	for (const s of r.segments) {
		if (s.kind === 'text') {
			before += s.text;
			continue;
		}
		const c = r.calls.find((x) => x.k === s.k)!;
		writing(ev, before + c.program, true);
		ev.push({ type: 'call', k: c.k, before, program: c.program, start: c.start, end: c.end });
		const run = c.run;
		if (run.registers.length && run.input.events) {
			ev.push({ type: 'stage', stage: 'tape' });
			ev.push({
				type: 'tape',
				events: run.input.events,
				span: [0, 0],
				char_spans: run.input.char_spans ?? null,
				...(run.arith ? { numbers: run.arith.numbers, spans: run.arith.spans } : {})
			});
			run.registers.forEach((x, index) => registerEvents(ev, x, index));
		}
		ev.push({ type: 'final', call: c });
		before = '';
	}
	if (r.end !== 'hard stop') writing(ev, before, false);
	ev.push({ type: 'trace', trace: t });
	return ev;
}

/** A finished run as the events the engine emits while making it. */
export function eventsFromTrace(t: LlmTrace): EngineEvent[] {
	if (t.reason) return eventsFromReason(t);
	const ev: EngineEvent[] = [];
	ev.push({ type: 'stage', stage: 'prefill', total: 100 });
	ev.push({ type: 'prefill', done: 100, total: 100 });
	ev.push({ type: 'stage', stage: 'compile' });
	const text = t.compile.text;
	for (let k = 1; k <= 6; k++)
		ev.push({
			type: 'compile',
			text: text.slice(0, Math.round((text.length * k) / 6)),
			tokens: Math.round((t.compile.tokens * k) / 6),
			seconds: (t.compile.seconds * k) / 6
		});
	ev.push({
		type: 'program',
		text,
		tokens: t.compile.tokens,
		seconds: t.compile.seconds,
		exec: text.includes('<exec/>'),
		finish: t.compile.finish
	});
	if (t.registers.length && t.input.events) {
		ev.push({
			type: 'tape',
			events: t.input.events,
			span: [0, 0],
			char_spans: t.input.char_spans ?? null,
			...(t.arith ? { numbers: t.arith.numbers, spans: t.arith.spans } : {})
		});
		t.registers.forEach((r, index) => registerEvents(ev, r, index));
		ev.push({ type: 'stage', stage: 'answer' });
		ev.push({ type: 'answer', text: t.answer, tokens: 8 });
	}
	ev.push({ type: 'trace', trace: t });
	return ev;
}

/** The register's own table run from `forced` at `step` to the end (what a certified executor does). */
function tableRun(r: LlmRegister, step: number, forced: string) {
	const delta = new Map(r.program.rows.map((x) => [`${x.s}\u0000${x.b}`, x.t]));
	let s: string | null = forced;
	for (const st of r.steps.slice(step)) {
		s = delta.get(`${s}\u0000${st.event}`) ?? null;
		if (s === null) break;
	}
	return s;
}

/** A Mealy register's table run on digit pairs from carry `from`: the carries and the sum digits it writes. */
function mealyRun(r: LlmRegister, pairs: [string, string][], from: string) {
	const rowOf = new Map(r.program.rows.map((x, k) => [`${x.s},${x.a},${x.b}`, k]));
	let s: string | null = from;
	const rows: number[] = [];
	for (const [a, b] of pairs) {
		const k: number | undefined = rowOf.get(`${s},${a},${b}`);
		if (k === undefined) return null;
		rows.push(k);
		s = r.program.rows[k].t;
	}
	return { rows, final: s };
}

const sumOf = (outs: string[]) =>
	[...outs]
		.reverse()
		.join('')
		.replace(/^0+(?=.)/, '');

/**
 * A recorded number-mode run, rerun on the numbers of another question: the clock's reading with the program's own
 * quotes, then the recorded table (a certified executor does what its rows say), as the engine would make it.
 */
function rerunAddition(
	t: LlmTrace,
	question: string,
	addition: { a: string; b: string } | null,
	title: string | undefined
) {
	const arith = t.arith!;
	const q = arith.quotes;
	const reading = readNumbers(question, [q.first[0], q.first[1], q.second[0], q.second[1]]);
	if (reading.numbers === null)
		return {
			...t,
			registers: [],
			arith: undefined,
			answer: '',
			final_text: null,
			ctx: null,
			note: `the loop stopped before the run: ${reading.why}`
		};
	const [n1, n2] = reading.numbers;
	const pairs = digitPairs(n1, n2);
	const r = t.registers[0];
	const run = mealyRun(r, pairs, r.program.start);
	if (!run)
		return {
			...t,
			registers: [],
			note: 'the loop stopped before the run: a digit is not an event of the table'
		};
	const xyz = new Map(r.codebook.names.map((n, k) => [n, r.codebook.xyz[k]]));
	let s = r.program.start;
	const steps = run.rows.map((k, i) => {
		const row = r.program.rows[k];
		const st = {
			i,
			event: `${pairs[i][0]}+${pairs[i][1]}`,
			s,
			row: k,
			t: row.t,
			margin: row.m ?? 0,
			pair: pairs[i],
			o: row.o,
			m2: row.m2,
			eq: true,
			xyz: xyz.get(row.t)
		};
		s = row.t;
		return st;
	});
	const outs = steps.map((x) => x.o ?? '0');
	const sum = sumOf(outs);
	const check = exactSum(n1, n2);
	const want = addition ? exactSum(addition.a, addition.b) : null;
	const answer = `The sum is ${sum}.`;
	const register: LlmRegister = {
		...r,
		steps,
		final: run.final ?? r.program.start,
		ticks: { ...r.ticks, real: steps.length, bitwise_equal_to_certified_row: steps.length },
		certificate: { ...r.certificate, ticks_real: steps.length, ticks_equal: steps.length },
		exact: want === null ? null : sum === want,
		first_wrong_step: null,
		steps_wrong: 0
	};
	return {
		...t,
		title: title ?? `Your addition, ${pairs.length.toLocaleString('en-US')} columns`,
		input: { ...t.input, events: steps.map((x) => x.event) },
		registers: [register],
		arith: {
			...arith,
			numbers: reading.numbers,
			spans: reading.spans,
			columns: pairs.length,
			sum,
			check
		},
		answer,
		final_text: `<final> ${r.name}=${run.final} ${r.program.mealy?.output ?? 's'}=${sum} </final>`,
		truth: want,
		score:
			want === null
				? undefined
				: {
						parsed: true,
						table_exact: arith.adder,
						tape_exact: true,
						certified: r.certificate.all_ok,
						run_final_right: sum === want,
						sum_right: sum === want,
						answer_correct: sum === want
					},
		ctx: t.ctx ? { ...t.ctx, pairs: [] } : null
	};
}

const fallbackModel = modelById('r3');

export class StubBackend {
	onmessage: ((m: FromWorker) => void) | null = null;
	private timers = new Set<ReturnType<typeof setTimeout>>();
	private cancelled = new Set<number>();
	private shown = {
		name: fallbackModel.name,
		adapter: fallbackModel.adapter,
		about: fallbackModel.about,
		dtype: fallbackModel.dtype
	};
	constructor(private stub: SavantStub) {}

	private modelInfo() {
		return {
			name: this.shown.name,
			compile_adapter: this.shown.adapter,
			executor_adapter: this.shown.adapter,
			adapter_sha256: { compile: '', executor: '' },
			tokenizer_sha256: '',
			promptbox_commit: '71268f94861079c34572b04eb87ac5aaa7888f96',
			about: this.shown.about
		};
	}

	private hostInfo() {
		return {
			gpu: this.stub.gpu ?? 'a stand-in GPU',
			cpu: null,
			avx512f: null,
			runtime: 'a test stand-in',
			dtype: this.shown.dtype
		};
	}

	private emit(m: FromWorker, after: number) {
		const t = setTimeout(() => {
			this.timers.delete(t);
			this.onmessage?.(m);
		}, after);
		this.timers.add(t);
	}

	/** The recorded run for a question: its own, else a number-mode run for an addition, else the first. */
	private baseFor(question: string): LlmTrace {
		const t = this.stub.traces;
		return (
			t.find((x) => x.prompt === question) ??
			(/\d\s*(plus|\+|and)\s*\d/.test(question) ? t.find((x) => x.arith) : undefined) ??
			t[0]
		);
	}

	postMessage(m: ToWorker) {
		const s = this.stub;
		const d = s.delay ?? 15;
		if (m.type === 'load') {
			this.shown = {
				name: m.model.name,
				adapter: m.model.adapter,
				about: m.model.about,
				dtype: m.dtype
			};
			const ms = s.loadMs ?? 400;
			const total = 2.9e9;
			for (let k = 1; k <= 8; k++)
				this.emit(
					{
						type: 'progress',
						progress: {
							files: { 'onnx/model_q4f16.onnx_data': { loaded: (total * k) / 8, total } },
							loaded: (total * k) / 8,
							total,
							stage: k === 8 ? 'ready' : 'download',
							file: 'onnx/model_q4f16.onnx_data'
						}
					},
					(ms * k) / 9
				);
			if (s.failLoad) this.emit({ type: 'load-error', error: s.failLoad }, ms);
			else
				this.emit(
					{
						type: 'loaded',
						loaded: {
							model: this.modelInfo(),
							host: this.hostInfo(),
							device: 'webgpu',
							dtype: this.shown.dtype,
							lastOnly: true,
							seconds: ms / 1000
						}
					},
					ms
				);
		} else if (m.type === 'cancel') {
			this.cancelled.add(m.rid);
		} else if (m.type === 'ask') {
			(s.asked ??= []).push(m.question);
			(s.lookups ??= []).push(m.opts.lookupAfter ?? null);
			const base = this.baseFor(m.question);
			let trace: LlmTrace = {
				...base,
				id: m.opts.id,
				prompt: m.question,
				title: m.opts.title ?? base.title,
				live: true,
				where: 'browser',
				model: this.modelInfo(),
				host: this.hostInfo(),
				source: 'savant-browser',
				truth: m.opts.truth?.answer ?? null,
				score: m.opts.truth ? base.score : undefined,
				base_answer: null,
				base_answer_meta: null,
				provenance: undefined,
				cost: undefined,
				// as a run here: no attention pass, no recorded pokes or adapter-off run
				registers: base.registers.map((r) => ({
					...r,
					attention: null,
					program: {
						...r.program,
						rows: r.program.rows.map((x): ProgramRow => ({
							s: x.s,
							...(x.a !== undefined ? { a: x.a } : {}),
							b: x.b,
							t: x.t,
							...(x.o !== undefined ? { o: x.o, m2: x.m2 } : {}),
							m: x.m,
							ok: x.ok,
							argmax: x.argmax,
							...(x.argmax2 !== undefined ? { argmax2: x.argmax2 } : {})
						}))
					},
					pokes: [],
					ablation: null
				}))
			};
			// a recorded run with calls in the middle: its calls are this run's, on this stand-in
			if (base.reason)
				trace.reason = {
					...base.reason,
					calls: base.reason.calls.map((c) => ({
						...c,
						run: {
							...c.run,
							id: `${m.opts.id}/call-${c.k}`,
							prompt: m.question,
							live: true,
							where: 'browser' as const,
							model: this.modelInfo(),
							host: this.hostInfo(),
							source: 'savant-browser'
						}
					}))
				};
			(s.additions ??= []).push(m.opts.addition ?? null);
			(s.multiCalls ??= []).push(m.opts.multiCall ?? null);
			if (base.arith && base.registers[0]?.program.mealy)
				trace = rerunAddition(trace, m.question, m.opts.addition ?? null, m.opts.title);
			const events = eventsFromTrace(trace);
			events.forEach((event, k) => {
				const t = setTimeout(
					() => {
						this.timers.delete(t);
						if (this.cancelled.has(m.rid)) return;
						this.onmessage?.({ type: 'event', rid: m.rid, event });
						if (k === events.length - 1) this.onmessage?.({ type: 'answered', rid: m.rid, trace });
					},
					d * (k + 1)
				);
				this.timers.add(t);
			});
			const stop = setInterval(() => {
				if (!this.cancelled.has(m.rid)) return;
				clearInterval(stop);
				this.onmessage?.({ type: 'failed', rid: m.rid, error: 'stopped', cancelled: true });
			}, d);
			setTimeout(() => clearInterval(stop), d * (events.length + 2));
		} else if (m.type === 'poke') {
			(s.poked ??= []).push({ register: m.register, step: m.step, forced: m.forced });
			const base = this.baseFor(m.question);
			const r = base.registers.find((x) => x.name === m.register) ?? base.registers[0];
			const forced = r.program.states[m.forced];
			if (r.program.mealy && base.arith) {
				const q = base.arith.quotes;
				const got = readNumbers(m.question, [q.first[0], q.first[1], q.second[0], q.second[1]]);
				const pairs = got.numbers ? digitPairs(...got.numbers) : [];
				const before = mealyRun(r, pairs.slice(0, m.step), r.program.start);
				const after = mealyRun(r, pairs.slice(m.step), forced);
				const outs = [...(before?.rows ?? []), ...(after?.rows ?? [])].map(
					(k) => r.program.rows[k].o ?? '0'
				);
				const sum = sumOf(outs);
				const n = pairs.length - m.step;
				this.emit(
					{
						type: 'poked',
						rid: m.rid,
						poke: {
							step: m.step,
							from: m.from ?? '',
							forced,
							final: after?.final ?? forced,
							predicted_state: after?.final ?? null,
							answer_after: `The sum is ${sum}.`,
							predicted: `the sum ${sum}`,
							sum_after: sum,
							predicted_sum: sum,
							match: true,
							answer_states_prediction: true,
							ticks: n,
							ticks_equal: n,
							min_margin: 8,
							live: true,
							seconds: { ticks: 0.1, answer: 0.1, total: 0.2 }
						}
					},
					d * 10
				);
				return;
			}
			const final = tableRun(r, m.step, forced);
			const n = r.steps.length - m.step;
			this.emit(
				{
					type: 'poked',
					rid: m.rid,
					poke: {
						step: m.step,
						from: m.from ?? '',
						forced,
						final: final ?? forced,
						predicted_state: final,
						answer_after: `The stand-in answers ${final ?? forced}.`,
						predicted: null,
						match: true,
						answer_states_prediction: null,
						ticks: n,
						ticks_equal: n,
						min_margin: 8,
						live: true,
						seconds: { ticks: 0.1, answer: 0.1, total: 0.2 }
					}
				},
				d * 10
			);
		}
	}

	terminate() {
		for (const t of this.timers) clearTimeout(t);
		this.timers.clear();
	}
}
