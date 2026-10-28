/**
 * A stand-in for the worker, for end-to-end tests of the page (no GPU, no download): it plays a recorded run back as
 * the engine's own events, with a pause between them, and answers pokes by running the run's table. The page uses
 * it only when a test has set `globalThis.__SAVANT_STUB__` before the page loaded.
 */
import type { EngineEvent } from './engine.ts';
import type { FromWorker, ToWorker } from './protocol.ts';
import { SAVANT } from './config.ts';
import type { LlmRegister, LlmTrace } from '../trace.ts';

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
	poked?: { register: string; step: number; forced: number }[];
}

export const stubOf = (): SavantStub | null =>
	(globalThis as { __SAVANT_STUB__?: SavantStub }).__SAVANT_STUB__ ?? null;

/** A finished run as the events the engine emits while making it. */
export function eventsFromTrace(t: LlmTrace): EngineEvent[] {
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
			char_spans: t.input.char_spans ?? null
		});
		t.registers.forEach((r, index) => {
			ev.push({ type: 'stage', stage: 'certify', register: r.name, total: r.program.rows.length });
			ev.push({
				type: 'register',
				index,
				name: r.name,
				start: r.program.start,
				states: r.program.states,
				events: r.program.events,
				rows: r.program.rows.map((x) => ({ s: x.s, b: x.b, t: x.t }))
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
			for (let i = 0; i < r.steps.length; i += 64)
				ev.push({
					type: 'ticks',
					index,
					steps: r.steps.slice(i, i + 64),
					done: Math.min(r.steps.length, i + 64),
					total: r.steps.length
				});
		});
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

const stubModel = () => ({
	name: SAVANT.name,
	compile_adapter: SAVANT.adapter,
	executor_adapter: SAVANT.adapter,
	adapter_sha256: { compile: '', executor: '' },
	tokenizer_sha256: '',
	promptbox_commit: '71268f94861079c34572b04eb87ac5aaa7888f96',
	about: SAVANT.about
});
const stubHost = (s: SavantStub) => ({
	gpu: s.gpu ?? 'a stand-in GPU',
	cpu: null,
	avx512f: null,
	runtime: 'a test stand-in',
	dtype: SAVANT.dtype
});

export class StubBackend {
	onmessage: ((m: FromWorker) => void) | null = null;
	private timers = new Set<ReturnType<typeof setTimeout>>();
	private cancelled = new Set<number>();
	constructor(private stub: SavantStub) {}

	private emit(m: FromWorker, after: number) {
		const t = setTimeout(() => {
			this.timers.delete(t);
			this.onmessage?.(m);
		}, after);
		this.timers.add(t);
	}

	postMessage(m: ToWorker) {
		const s = this.stub;
		const d = s.delay ?? 15;
		if (m.type === 'load') {
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
							model: stubModel(),
							host: stubHost(s),
							device: 'webgpu',
							dtype: SAVANT.dtype,
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
			const base = s.traces.find((t) => t.prompt === m.question) ?? s.traces[0];
			const trace: LlmTrace = {
				...base,
				id: m.opts.id,
				prompt: m.question,
				title: m.opts.title ?? base.title,
				live: true,
				where: 'browser',
				model: stubModel(),
				host: stubHost(s),
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
						rows: r.program.rows.map((x) => ({
							s: x.s,
							b: x.b,
							t: x.t,
							m: x.m,
							ok: x.ok,
							argmax: x.argmax
						}))
					},
					pokes: [],
					ablation: null
				}))
			};
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
			const base = s.traces.find((t) => t.prompt === m.question) ?? s.traces[0];
			const r = base.registers.find((x) => x.name === m.register) ?? base.registers[0];
			const forced = r.program.states[m.forced];
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
