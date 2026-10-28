/**
 * A run in progress, rebuilt from the engine's events, in the shapes the page's panels read. Each event returns a
 * new object (the page keeps it as raw state), so panels update as the program streams in, the certificate fills,
 * and the ticks advance. When the run finishes, its `trace` is the engine's own record of it.
 */
import type { EngineEvent, ModelInfo, HostInfo, Stage } from './engine.ts';
import { browserPanels, ring, rowLines } from './engine.ts';
import type { LlmRegister, LlmTrace, ProgramRow } from '../trace.ts';

export interface LiveRun {
	id: string;
	question: string;
	title: string;
	family: string | null;
	stage: Stage | 'queued' | 'done' | 'error' | 'stopped';
	prefill: { done: number; total: number };
	compile: {
		text: string;
		tokens: number;
		seconds: number;
		finish: string | null;
		exec: boolean | null;
	};
	tape: { events: string[]; span: [number, number]; char_spans: [number, number][] | null } | null;
	registers: LlmRegister[];
	/** the register being certified or run, and how far it is */
	at: { register: number; rows: number; ticks: number } | null;
	answer: string;
	error: string | null;
	trace: LlmTrace | null;
	started: number;
	/** seconds per stage as they finish */
	model: ModelInfo;
	host: HostInfo;
}

export function startRun(
	id: string,
	question: string,
	opts: { title?: string; family?: string | null; model: ModelInfo; host: HostInfo }
): LiveRun {
	return {
		id,
		question,
		title: opts.title ?? 'Your question',
		family: opts.family ?? null,
		stage: 'queued',
		prefill: { done: 0, total: 0 },
		compile: { text: '', tokens: 0, seconds: 0, finish: null, exec: null },
		tape: null,
		registers: [],
		at: null,
		answer: '',
		error: null,
		trace: null,
		started: Date.now(),
		model: opts.model,
		host: opts.host
	};
}

const PENDING = Number.NaN;

function pendingRegister(
	run: LiveRun,
	ev: Extract<EngineEvent, { type: 'register' }>,
	names: string[]
): LlmRegister {
	const rows: ProgramRow[] = ev.rows.map((r) => ({ s: r.s, b: r.b, t: r.t }));
	return {
		name: ev.name,
		program: {
			text: run.compile.text,
			states: ev.states,
			events: ev.events,
			start: ev.start,
			rows,
			row_lines: rowLines(run.compile.text, ev.name, rows.length),
			registers: names,
			...(ev.states.length <= 40
				? { diagram: { kind: 'ring' as const, pos: ring(ev.states.length), dims: null } }
				: {})
		},
		certificate: {
			kind: 'logit',
			pairs_checked: 0,
			all_ok: false,
			certified: false,
			rows_wrong: 0,
			min_margin: PENDING,
			N_star: null,
			A: ev.events.length,
			covers:
				'execution of this table at every input length (Theorem P), on this GPU and code path',
			ticks_real: 0,
			ticks_equal: 0
		},
		attention: null,
		codebook: { names: [], xyz: [], variance_kept: 0, projection: '' },
		steps: [],
		final: ev.start,
		ticks: { real: 0, bitwise_equal_to_certified_row: 0, seconds: 0, ms_per_tick: null },
		exact: null,
		first_wrong_step: null,
		pokes: [],
		ablation: null
	};
}

/** Register names in the program text, in order (for the panels' register list before every register exists). */
const namesIn = (text: string) => [...text.matchAll(/^register (\w+): start/gm)].map((m) => m[1]);

export function applyEvent(run: LiveRun, ev: EngineEvent): LiveRun {
	switch (ev.type) {
		case 'stage':
			return { ...run, stage: ev.stage };
		case 'prefill':
			return { ...run, prefill: { done: ev.done, total: ev.total } };
		case 'compile':
			return {
				...run,
				compile: { ...run.compile, text: ev.text, tokens: ev.tokens, seconds: ev.seconds }
			};
		case 'program':
			return {
				...run,
				compile: {
					text: ev.text,
					tokens: ev.tokens,
					seconds: ev.seconds,
					finish: ev.finish,
					exec: ev.exec
				}
			};
		case 'tape':
			return {
				...run,
				title:
					run.title === 'Your question'
						? `Your question, ${ev.events.length.toLocaleString('en-US')} events`
						: run.title,
				tape: { events: ev.events, span: ev.span, char_spans: ev.char_spans }
			};
		case 'register': {
			const regs = [...run.registers];
			regs[ev.index] = pendingRegister(run, ev, namesIn(run.compile.text));
			return { ...run, registers: regs, at: { register: ev.index, rows: 0, ticks: 0 } };
		}
		case 'row': {
			const regs = [...run.registers];
			const r = regs[ev.index];
			if (!r) return run;
			const rows = [...r.program.rows];
			rows[ev.k] = ev.row;
			const done = rows.filter((x) => x.ok !== undefined);
			regs[ev.index] = {
				...r,
				program: { ...r.program, rows },
				certificate: {
					...r.certificate,
					pairs_checked: done.length,
					rows_wrong: done.filter((x) => !x.ok).length,
					min_margin: Math.min(...done.map((x) => x.m ?? Infinity))
				}
			};
			return { ...run, registers: regs, at: { register: ev.index, rows: done.length, ticks: 0 } };
		}
		case 'certificate': {
			const regs = [...run.registers];
			const r = regs[ev.index];
			if (!r) return run;
			regs[ev.index] = {
				...r,
				certificate: {
					...r.certificate,
					pairs_checked: ev.rows,
					all_ok: ev.pass,
					certified: ev.pass,
					rows_wrong: ev.rows_wrong,
					min_margin: ev.min_margin
				},
				codebook: ev.codebook
			};
			return { ...run, registers: regs };
		}
		case 'ticks': {
			const regs = [...run.registers];
			const r = regs[ev.index];
			if (!r) return run;
			const steps = [...r.steps, ...ev.steps];
			const equal = steps.filter((s) => s.eq).length;
			const real = steps.filter((s) => !s.lookup).length;
			regs[ev.index] = {
				...r,
				steps,
				final: steps.length ? steps[steps.length - 1].t : r.final,
				certificate: { ...r.certificate, ticks_real: real, ticks_equal: equal },
				ticks: {
					...r.ticks,
					real,
					bitwise_equal_to_certified_row: equal,
					...(real < steps.length ? { lookup: steps.length - real } : {})
				}
			};
			return {
				...run,
				registers: regs,
				at: { register: ev.index, rows: r.program.rows.length, ticks: ev.done }
			};
		}
		case 'answer':
			return { ...run, answer: ev.text };
		case 'trace':
			return {
				...run,
				stage: 'done',
				trace: ev.trace,
				title: ev.trace.title,
				registers: ev.trace.registers,
				answer: ev.trace.answer
			};
		case 'error':
			return { ...run, stage: 'error', error: ev.error };
	}
}

/** The run so far as a trace the panels can read (the finished trace once there is one). */
export function liveTrace(run: LiveRun): LlmTrace {
	if (run.trace) return run.trace;
	return {
		schema: 'polyformer.trace/0',
		source: 'savant-browser',
		id: run.id,
		kind: 'llm',
		title: run.title,
		family: run.family,
		live: true,
		where: 'browser',
		model: run.model,
		host: run.host,
		at: new Date(run.started).toISOString(),
		prompt: run.question,
		answer: run.answer,
		final_text: null,
		note: null,
		truth: null,
		base_answer: null,
		base_answer_meta: null,
		compile: {
			text: run.compile.text,
			tokens: run.compile.tokens,
			finish: run.compile.finish ?? '',
			seconds: run.compile.seconds
		},
		panels: browserPanels(),
		input: {
			events: run.tape?.events ?? null,
			char_spans: run.tape?.char_spans ?? null,
			anchors: null,
			error: null
		},
		registers: run.registers.filter(Boolean),
		timing: null,
		ctx: null
	};
}

/** Whether a register's rows are all certified (its codebook exists) so the state view can show it. */
export const certifiedYet = (r: LlmRegister) => r.codebook.names.length > 0;
