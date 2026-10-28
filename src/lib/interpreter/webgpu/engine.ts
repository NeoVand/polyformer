/**
 * The pinned loop on any causal LM (dl_core.Engine.ask and .poke, ported). Backend-agnostic: the LM is an interface,
 * so the same code runs on transformers.js with WebGPU in the page's worker, on onnxruntime-node in the parity
 * script, and on a scripted stand-in in the unit tests.
 *
 *   compile   greedy generation from the chat prompt until `<exec/>` (or an end token, or 3,000 tokens)
 *   parse     pb_loop.parse_generated on the generated ids; the clock reads the tape from the question
 *   certify   per register: Π (its row tokens as written) is prefilled once and cached; every row runs as one tick,
 *             the block [s][e] at positions |Π| and |Π|+1, and passes when the argmax over the whole vocabulary is
 *             the row's destination with a positive margin
 *   run       one real tick per event on the same path; each tick's logits are compared bit for bit with its
 *             certified row's
 *   answer    `\n<final> X=v </final>\n` after the program, then greedy words (300 tokens at most)
 *   poke      force a state entering tick k, real ticks to the end, the words again
 *   calls     with `multiCall` (REASON_FORMAT, config MULTI_CALL), the words may hold several calls: each `<exec/>`
 *             is run as above with Π built fresh, its `<final>` line (or an error line) is fed like a prompt, and the
 *             model resumes, until its end token
 *
 * Every step emits an event, so the page can show the program streaming in, the certificate filling and the ticks
 * advancing; the last event carries the whole run in the page's `polyformer.trace/0` form.
 */
import { answerCorrect, type AnswerKey } from './answer.ts';
import { clockPairs, digitIds, exactSum, finalIdsMealy } from './arith.ts';
import {
	errorFinalIds,
	exactDifference,
	isSubtracter,
	lastCallStart,
	limitAt,
	readCall,
	resultValueOf,
	TOO_MANY,
	type CallReading
} from './reason.ts';
import { makeCodebook, type Codebook } from './codebook.ts';
import {
	charSpans,
	chatPrompt,
	clockTape,
	findSpan,
	finIds,
	nameOf,
	parseGenerated,
	pyStrip,
	round4,
	top2,
	type MealyRegister,
	type Program,
	type Tok
} from './pb.ts';
import type {
	ArithRecord,
	LlmCtx,
	LlmRegister,
	LlmTrace,
	Poke,
	ProgramRow,
	ReasonCall,
	ReasonFrom,
	ReasonRecord,
	ReasonSegment,
	Xyz
} from '../trace.ts';

// ------------------------------------------------------------------ the model, abstractly

/** A key/value cache: the tokens it has seen, at positions 0 … length-1. */
export interface KV {
	readonly length: number;
	dispose(): void;
}

export interface Forward {
	/** the last position's logits, as float32 */
	logits: Float32Array;
	/** a fingerprint of those logits' raw bits as the model produced them (bitwise equality) */
	bits: string;
	/** the cache extended by the fed ids, when asked to keep it */
	past: KV | null;
}

export interface LM {
	/** Feeds `ids` at positions past.length …; `keep` false frees the extended cache at once. */
	forward(ids: number[], past: KV | null, keep: boolean): Promise<Forward>;
	/** the most tokens to feed in one call when prefilling */
	readonly chunk: number;
}

// ------------------------------------------------------------------ constants (dl_core, pb_loop)

export const COMPILE_MAX_TOKENS = 3000;
/** A reply with no program at all: the model answered in words (since the language repair, ordinary questions). */
export const PLAIN_NOTE = 'the model answered without writing a program';
/** What the page says when the model falls back to its older rule-style programs (arithmetic, for one). */
export const RULE_STYLE_NOTE =
	"the model wrote a rule-style program, the older format it learned for arithmetic, and this preview's clock runs only literal tables, so there is no run. Arithmetic in the runnable format comes with the next model";
export const ANSWER_MAX_TOKENS = 300;
export const MAX_MODEL_LEN = 40960;
export const SCHEMA = 'polyformer.trace/0';
export const PROMPTBOX_COMMIT = '71268f94861079c34572b04eb87ac5aaa7888f96';

export interface Ids {
	nl: number;
	/** generation stops on these (Qwen3: <|im_end|>, <|endoftext|>) */
	stop: number[];
}

/** What the questions the page suggests know about themselves (static/interpreter/prompts.json). */
export interface Truth {
	answer: string;
	key: AnswerKey;
	final: Record<string, string>;
	registers: {
		name: string;
		start: string;
		rows: number;
		values: string[];
		start_id: number;
		table_ids: [number, number, number][];
		final_id: number;
		trace: string | null;
	}[];
	events: number;
	tape_fnv: string;
	anchors: [string, string];
	predicted: Record<string, Record<string, { answer: string | null; key: AnswerKey | null }>>;
}

export interface AskOptions {
	id: string;
	/** lookup mode: real ticks on the first this-many events, then each certified row's argmax (null: every tick) */
	lookupAfter?: number | null;
	title?: string;
	family?: string | null;
	truth?: Truth | null;
	/** a suggested addition: the two numbers the page wrote into the question, to score the run against */
	addition?: { a: string; b: string } | null;
	/** REASON_FORMAT: calls in the middle of the words, resumed after each `<final>` (config MULTI_CALL) */
	multiCall?: boolean;
	signal?: AbortSignal;
}

export interface ModelInfo {
	name: string;
	compile_adapter: string;
	executor_adapter: string;
	adapter_sha256: { compile: string; executor: string };
	tokenizer_sha256: string;
	promptbox_commit: string;
	about: string;
}

export type HostInfo = LlmTrace['host'];

/** Rows of the certificate as they are checked. */
export interface CertRow {
	s: number;
	e: number;
	t: number;
	argmax: number;
	margin: number;
	ok: boolean;
}

export type EngineEvent =
	| { type: 'stage'; stage: Stage; register?: string; total?: number }
	| { type: 'prefill'; done: number; total: number }
	| { type: 'compile'; text: string; tokens: number; seconds: number }
	| {
			type: 'program';
			text: string;
			tokens: number;
			seconds: number;
			exec: boolean;
			finish: string;
	  }
	| {
			type: 'tape';
			events: string[];
			span: [number, number];
			char_spans: [number, number][] | null;
			/** number mode: the two numbers read and their spans */
			numbers?: [string, string];
			spans?: [[number, number], [number, number]];
	  }
	| {
			type: 'register';
			index: number;
			name: string;
			start: string;
			states: string[];
			events: string[];
			rows: { s: string; a?: string; b: string; t: string; o?: string }[];
			/** a Mealy register: its output's name */
			mealy?: { output: string };
	  }
	| { type: 'row'; index: number; k: number; row: ProgramRow }
	| {
			type: 'certificate';
			index: number;
			pass: boolean;
			rows: number;
			rows_wrong: number;
			min_margin: number;
			seconds: number;
			codebook: Codebook;
	  }
	| { type: 'ticks'; index: number; steps: LlmRegister['steps']; done: number; total: number }
	| { type: 'answer'; text: string; tokens: number }
	/** REASON: the clock takes call k (the text before it, and the call from <program> to <exec/>) */
	| { type: 'call'; k: number; before: string; program: string; start: number; end: number }
	/** REASON: call k is done; its final line (or error line) follows in the transcript */
	| { type: 'final'; call: ReasonCall }
	| { type: 'trace'; trace: LlmTrace }
	| { type: 'error'; error: string };

export type Stage = 'prefill' | 'compile' | 'tape' | 'certify' | 'run' | 'answer' | 'poke';

export class Cancelled extends Error {
	constructor() {
		super('stopped');
	}
}

const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());
const secs = (t0: number) => Math.round(now() - t0) / 1000;
const check = (signal?: AbortSignal) => {
	if (signal?.aborted) throw new Cancelled();
};

/** The text that greedy generation keeps: up to and including the first stop string. */
function cut(text: string, stops: string[]): { text: string; hit: boolean } {
	let at = -1;
	let len = 0;
	for (const s of stops) {
		const i = text.indexOf(s);
		if (i >= 0 && (at < 0 || i < at)) {
			at = i;
			len = s.length;
		}
	}
	return at < 0 ? { text, hit: false } : { text: text.slice(0, at + len), hit: true };
}

const fnv1a = (ids: number[]) => {
	let h = 0x811c9dc5;
	for (const c of new TextEncoder().encode(ids.join(','))) {
		h ^= c;
		h = Math.imul(h, 0x01000193) >>> 0;
	}
	return h.toString(16).padStart(8, '0');
};

/** The certified state of one Π: its cache, every row's logits fingerprint and its logits on the states. */
interface PiEntry {
	key: string;
	past: KV;
	P: number;
	rows: CertRow[];
	bits: Map<string, string>;
	z: Map<string, Float32Array>;
	stateIds: number[];
	seconds: number;
}

const pair = (s: number, e: number) => `${s},${e}`;
const cell = (s: number, a: number, b: number) => `${s},${a},${b}`;

/** One row of a Mealy certificate (ARITH_FORMAT §5): both forwards' argmaxes and margins. */
export interface MealyCertRow {
	s: number;
	a: number;
	b: number;
	t: number;
	o: number;
	tArg: number;
	oArg: number;
	m1: number;
	m2: number;
	ok: boolean;
}

/** The certified state of one Mealy Π: its cache, and per row both forwards' fingerprints and state logits. */
interface MealyEntry {
	key: string;
	past: KV;
	P: number;
	rows: MealyCertRow[];
	bits: Map<string, [string, string]>;
	z: Map<string, Float32Array>;
	stateIds: number[];
	seconds: number;
}

const ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';

export class Engine {
	private pis = new Map<string, PiEntry>();
	/** Mealy certificates by Π (ARITH_FORMAT §5): the adder's Π is the same every time, so it is certified once */
	private mealyPis = new Map<string, MealyEntry>();
	/** the cache of the chat prompt and the program, but the program's last token: the words reuse it */
	private session: { key: string; past: KV; last: number } | null = null;
	private busy = false;

	constructor(
		readonly lm: LM,
		readonly tok: Tok,
		readonly ids: Ids,
		readonly model: ModelInfo,
		readonly host: HostInfo,
		readonly maxPis = 4
	) {}

	private enc = (s: string) => this.tok.encode(s);
	private name = (i: number) => nameOf(this.tok, i);

	/** Frees every cache the engine holds. */
	dispose() {
		for (const p of this.pis.values()) p.past.dispose();
		this.pis.clear();
		for (const p of this.mealyPis.values()) p.past.dispose();
		this.mealyPis.clear();
		this.session?.past.dispose();
		this.session = null;
	}

	// -------------------------------------------------------------- generation

	/** Feeds `ids` after `past` in chunks; returns the last logits and the extended cache (kept). */
	private async feed(
		ids: number[],
		past: KV | null,
		signal?: AbortSignal,
		progress?: (done: number) => void
	): Promise<{ logits: Float32Array; past: KV }> {
		let cur = past;
		let out: Forward | null = null;
		try {
			for (let i = 0; i < ids.length; i += this.lm.chunk) {
				check(signal);
				out = await this.lm.forward(ids.slice(i, i + this.lm.chunk), cur, true);
				if (cur && cur !== past) cur.dispose();
				cur = out.past!;
				progress?.(Math.min(ids.length, i + this.lm.chunk));
			}
		} catch (err) {
			if (cur && cur !== past) cur.dispose();
			throw err;
		}
		if (!out || !cur) throw new Error('nothing to feed');
		return { logits: out.logits, past: cur };
	}

	/**
	 * Greedy decoding as vLLM does it at temperature 0: argmax (first on a tie) until an end token, a stop string
	 * (kept in the text) or the budget. `start` is the logits after the prompt and `past` its cache, which is left
	 * intact. Returns the generated ids (end tokens left out), the text (special tokens skipped), and the cache of
	 * everything fed: the prompt and every generated id but the last, which was never fed back (`past` itself when
	 * nothing was fed); the caller frees it.
	 */
	private async greedy(
		start: Float32Array,
		past: KV,
		maxTokens: number,
		stops: string[],
		signal?: AbortSignal,
		onToken?: (text: string, n: number) => void
	): Promise<{ ids: number[]; text: string; finish: 'stop' | 'length'; past: KV }> {
		const out: number[] = [];
		let logits = start;
		let cur = past;
		let text = '';
		const room = Math.max(1, Math.min(maxTokens, MAX_MODEL_LEN - past.length - 8));
		try {
			for (;;) {
				check(signal);
				const next = top2(logits).arg;
				if (this.ids.stop.includes(next)) return { ids: out, text, finish: 'stop', past: cur };
				out.push(next);
				const c = cut(this.tok.decode(out), stops);
				text = c.text;
				onToken?.(text, out.length);
				if (c.hit) return { ids: out, text, finish: 'stop', past: cur };
				if (out.length >= room) return { ids: out, text, finish: 'length', past: cur };
				const f = await this.lm.forward([next], cur, true);
				if (cur !== past) cur.dispose();
				cur = f.past!;
				logits = f.logits;
			}
		} catch (err) {
			if (cur !== past) cur.dispose();
			throw err;
		}
	}

	// -------------------------------------------------------------- certificate and ticks

	/** pb_pin.certify on the cached Π, kept per Π so pokes reuse the run's own certificate. */
	private async certified(
		pi: number[],
		rows: [number, number, number][],
		stateIds: number[],
		signal?: AbortSignal,
		onRow?: (k: number, r: CertRow) => void
	): Promise<{ entry: PiEntry; cached: boolean }> {
		const key = pi.join(',');
		const have = this.pis.get(key);
		if (have) {
			this.pis.delete(key);
			this.pis.set(key, have);
			have.rows.forEach((r, k) => onRow?.(k, r));
			return { entry: have, cached: true };
		}
		const t0 = now();
		check(signal);
		const pre = await this.lm.forward(pi, null, true);
		const past = pre.past!;
		const entry: PiEntry = {
			key,
			past,
			P: pi.length,
			rows: [],
			bits: new Map(),
			z: new Map(),
			stateIds,
			seconds: 0
		};
		try {
			for (const [s, e, t] of rows) {
				check(signal);
				const f = await this.lm.forward([s, e], past, false);
				const { arg, margin } = top2(f.logits);
				const r: CertRow = {
					s,
					e,
					t,
					argmax: arg,
					margin: round4(margin),
					ok: arg === t && margin > 0
				};
				entry.rows.push(r);
				entry.bits.set(pair(s, e), f.bits);
				entry.z.set(pair(s, e), pick(f.logits, stateIds));
				onRow?.(entry.rows.length - 1, r);
			}
		} catch (err) {
			past.dispose();
			throw err;
		}
		entry.seconds = secs(t0);
		this.pis.set(key, entry);
		while (this.pis.size > this.maxPis) {
			const [k, old] = this.pis.entries().next().value!;
			old.past.dispose();
			this.pis.delete(k);
		}
		return { entry, cached: false };
	}

	/**
	 * Ticks from `s0` over `tape` (pb_pin.run), with margins, state logits and bitwise equality per tick. With
	 * `lookupAfter` (PROMPTBOX's lookup mode, pb_pin.run_lookup), a certified table's steps after the first
	 * `lookupAfter` events are read from the certified rows instead of run: Theorem P says a certified row's tick is
	 * the same every time. A pair with no row is always run.
	 */
	private async ticks(
		entry: PiEntry,
		s0: number,
		tape: number[],
		signal?: AbortSignal,
		onTick?: (
			i: number,
			s: number,
			t: number,
			margin: number,
			eq: boolean | null,
			z: Float32Array
		) => void,
		lookupAfter: number | null = null
	) {
		const t0 = now();
		let s = s0;
		const states: number[] = [];
		const margins: number[] = [];
		const same: boolean[] = [];
		let looked = 0;
		const certified = entry.rows.every((r) => r.ok);
		const row = new Map(entry.rows.map((r) => [pair(r.s, r.e), r]));
		for (let i = 0; i < tape.length; i++) {
			const e = tape[i];
			const r = row.get(pair(s, e));
			if (lookupAfter !== null && certified && i >= lookupAfter && r) {
				states.push(r.argmax);
				margins.push(r.margin);
				looked++;
				onTick?.(i, s, r.argmax, r.margin, null, entry.z.get(pair(s, e))!);
				s = r.argmax;
				// let the page draw now and then
				if (looked % 256 === 0) await new Promise((res) => setTimeout(res, 0));
				continue;
			}
			check(signal);
			const f = await this.lm.forward([s, e], entry.past, false);
			const { arg, margin } = top2(f.logits);
			const want = entry.bits.get(pair(s, e));
			const eq = want !== undefined && want === f.bits;
			states.push(arg);
			margins.push(round4(margin));
			same.push(eq);
			onTick?.(i, s, arg, round4(margin), eq, pick(f.logits, entry.stateIds));
			s = arg;
		}
		return { states, margins, same, looked, seconds: secs(t0) };
	}

	// -------------------------------------------------------------- the loop

	/** The whole pinned loop for one question. Emits events as it goes; resolves with the run. */
	async ask(
		question: string,
		opts: AskOptions,
		emit: (ev: EngineEvent) => void
	): Promise<LlmTrace> {
		if (this.busy) throw new Error('the model is busy with another question');
		this.busy = true;
		try {
			const q = question.normalize('NFC');
			return await (opts.multiCall ? this.askMulti(q, opts, emit) : this.askInner(q, opts, emit));
		} finally {
			this.busy = false;
		}
	}

	private async askInner(
		question: string,
		opts: AskOptions,
		emit: (ev: EngineEvent) => void
	): Promise<LlmTrace> {
		const { signal } = opts;
		const tAll = now();
		const timing: Record<string, number> = {};
		const promptIds = this.enc(chatPrompt(question));
		this.session?.past.dispose();
		this.session = null;

		emit({ type: 'stage', stage: 'prefill', total: promptIds.length });
		let t0 = now();
		// the prompt without its last token is the cache the words reuse; the last token gives the first logits
		const head = await this.feed(promptIds, null, signal, (done) =>
			emit({ type: 'prefill', done, total: promptIds.length })
		);
		timing.prefill = secs(t0);

		emit({ type: 'stage', stage: 'compile' });
		t0 = now();
		let lastEmit = 0;
		const gen = await this.greedy(
			head.logits,
			head.past,
			COMPILE_MAX_TOKENS,
			// `<check>` opens the older rule-style format (PROMPTBOX stage (b+c)); the clock cannot run it, so stop there
			['<exec/>', '<check>'],
			signal,
			(text, n) => {
				const t = now();
				if (t - lastEmit > 40) {
					lastEmit = t;
					emit({ type: 'compile', text, tokens: n, seconds: secs(t0) });
				}
			}
		).catch((err) => {
			head.past.dispose();
			throw err;
		});
		timing.compile = secs(t0);
		const ids = gen.ids;
		const text = gen.text;
		const exec = text.includes('<exec/>');
		emit({
			type: 'program',
			text,
			tokens: ids.length,
			seconds: timing.compile,
			exec,
			finish: gen.finish
		});

		const trace = this.blank(question, opts, text, ids.length, gen.finish, timing.compile);
		if (gen.past !== head.past) head.past.dispose();
		// the cache of the prompt and the program but its last token: the words and the pokes reuse it
		this.session =
			exec && ids.length
				? { key: sessionKey(question, ids), past: gen.past, last: ids[ids.length - 1] }
				: null;
		const finish = (note: string | null, answer = '') => {
			if (!this.session) gen.past.dispose();
			timing.total = secs(tAll);
			Object.assign(trace, { answer, note, timing });
			emit({ type: 'trace', trace });
			return trace;
		};
		if (!exec && text.includes('<check>')) return finish(RULE_STYLE_NOTE);
		if (!exec) return finish(PLAIN_NOTE, pyStrip(text));

		const prog = parseGenerated(this.tok, ids, this.ids.nl);
		if (prog.mode === 'numbers')
			return this.numbers(question, opts, prog, ids, trace, timing, tAll, finish, emit);
		const ct = prog.error ? { tape: null, why: prog.error } : clockTape(this.tok, question, prog);
		trace.input = { events: null, char_spans: null, anchors: prog.anchors, error: ct.why };
		if (prog.error || ct.tape === null) {
			trace.score = opts.truth ? scoreLoop(prog, null, null, opts.truth, '') : undefined;
			return finish(`the loop stopped before the run: ${ct.why}`);
		}
		const tape = ct.tape;
		const span = findSpan(question, ...prog.anchors!)!;
		const events = tape.map(this.name);
		trace.input = {
			events,
			char_spans: charSpans(this.tok, question, span, tape),
			anchors: prog.anchors,
			error: null
		};
		if (!opts.title) trace.title = `Your question, ${tape.length.toLocaleString('en-US')} events`;
		emit({ type: 'tape', events, span, char_spans: trace.input.char_spans ?? null });

		const finals: Record<string, number> = {};
		const ctxRegs: LlmCtx['registers'] = [];
		for (let index = 0; index < prog.registers.length; index++) {
			const r = prog.registers[index];
			const view = await this.register(
				r,
				index,
				prog,
				tape,
				trace,
				timing,
				signal,
				emit,
				opts.lookupAfter ?? null
			);
			trace.registers.push(view.view);
			finals[r.name] = view.final;
			ctxRegs.push({ name: r.name, start: r.start, rows: r.rows, run: view.run });
		}

		emit({ type: 'stage', stage: 'answer' });
		t0 = now();
		const words = await this.words(
			finIds(this.tok, prog.registers, finals),
			ANSWER_MAX_TOKENS,
			signal,
			(text, n) => emit({ type: 'answer', text, tokens: n })
		);
		timing.answer = secs(t0);
		timing.total = secs(tAll);
		trace.answer = pyStrip(words.text);
		trace.final_text = pyStrip(this.tok.decode(words.fin));
		trace.timing = timing;
		trace.ctx = { program_ids: ids, nl: this.ids.nl, registers: ctxRegs, tape, finals };
		if (opts.truth) attachTruth(trace, prog, tape, finals, opts.truth);
		emit({ type: 'trace', trace });
		return trace;
	}

	/** Certifies one register and runs it over the tape, emitting the rows and the ticks as they happen. */
	private async register(
		r: Program['registers'][number],
		index: number,
		prog: Program,
		tape: number[],
		trace: LlmTrace,
		timing: Record<string, number>,
		signal: AbortSignal | undefined,
		emit: (ev: EngineEvent) => void,
		lookupAfter: number | null
	) {
		const rows = r.rows;
		const stateIds = [...new Set(rows.map(([s]) => s))];
		const eventIds = [...new Set(rows.map(([, e]) => e))];
		const states = stateIds.map(this.name);
		emit({ type: 'stage', stage: 'certify', register: r.name, total: rows.length });
		emit({
			type: 'register',
			index,
			name: r.name,
			start: this.name(r.start),
			states,
			events: eventIds.map(this.name),
			rows: rows.map(([s, e, t]) => ({ s: this.name(s), b: this.name(e), t: this.name(t) }))
		});
		const outRows: ProgramRow[] = [];
		const rowView = (c: CertRow): ProgramRow => ({
			s: this.name(c.s),
			b: this.name(c.e),
			t: this.name(c.t),
			m: c.margin,
			ok: c.ok,
			...(c.ok ? {} : { argmax: this.name(c.argmax) })
		});
		const { entry } = await this.certified(r.pi, rows, stateIds, signal, (k, c) => {
			outRows[k] = rowView(c);
			emit({ type: 'row', index, k, row: outRows[k] });
		});
		const cert = entry.rows;
		const pass = cert.every((c) => c.ok);
		const rowsWrong = cert.filter((c) => !c.ok).length;
		const minMargin = Math.min(...cert.map((c) => c.margin));
		timing[`certify:${r.name}`] = entry.seconds;
		const { codebook, project } = makeCodebook(
			states,
			rows.map(([s, e]) => entry.z.get(pair(s, e))!),
			cert.map((c) => stateIds.indexOf(c.argmax))
		);
		emit({
			type: 'certificate',
			index,
			pass,
			rows: rows.length,
			rows_wrong: rowsWrong,
			min_margin: minMargin,
			seconds: entry.seconds,
			codebook
		});

		emit({ type: 'stage', stage: 'run', register: r.name, total: tape.length });
		const rowOf = new Map(rows.map(([s, e], k) => [pair(s, e), k]));
		const steps: LlmRegister['steps'] = [];
		let batch: LlmRegister['steps'] = [];
		let lastEmit = now();
		const rec = await this.ticks(
			entry,
			r.start,
			tape,
			signal,
			(i, s, t, margin, eq, z) => {
				const st = {
					i,
					event: this.name(tape[i]),
					s: this.name(s),
					row: rowOf.get(pair(s, tape[i])) ?? -1,
					t: this.name(t),
					margin,
					...(eq === null ? { lookup: true as const } : { eq }),
					xyz: project(z) as Xyz
				};
				steps.push(st);
				batch.push(st);
				const tn = now();
				if (tn - lastEmit > 60 || i === tape.length - 1) {
					lastEmit = tn;
					emit({ type: 'ticks', index, steps: batch, done: i + 1, total: tape.length });
					batch = [];
				}
			},
			lookupAfter
		);
		timing[`run:${r.name}`] = rec.seconds;
		const final = rec.states.length ? rec.states[rec.states.length - 1] : r.start;
		const real = rec.same.length;
		const equal = rec.same.filter(Boolean).length;
		const view: LlmRegister = {
			name: r.name,
			program: {
				text: trace.compile.text,
				states,
				events: eventIds.map(this.name),
				start: this.name(r.start),
				rows: outRows,
				row_lines: rowLines(trace.compile.text, r.name, rows.length),
				registers: prog.registers.map((x) => x.name),
				...(states.length <= 40
					? { diagram: { kind: 'ring', pos: ring(states.length), dims: null } }
					: {})
			},
			certificate: {
				kind: 'logit',
				pairs_checked: rows.length,
				all_ok: pass,
				certified: pass,
				rows_wrong: rowsWrong,
				min_margin: minMargin,
				N_star: null,
				A: eventIds.length,
				covers:
					'execution of this table at every input length (Theorem P), on this GPU and code path; not whether ' +
					'the table fits the question, nor whether the tape fits the prompt',
				path: "one tick per row: the block [s][e] at positions |Π| and |Π|+1 over Π's cached keys and values, batch 1, in this browser",
				ticks_real: real,
				ticks_equal: equal
			},
			attention: null,
			codebook,
			steps,
			final: this.name(final),
			ticks: {
				real,
				bitwise_equal_to_certified_row: equal,
				seconds: rec.seconds,
				ms_per_tick: real ? Math.round((100000 * rec.seconds) / real) / 100 : null,
				...(rec.looked ? { lookup: rec.looked, lookup_after: lookupAfter } : {})
			},
			exact: null,
			first_wrong_step: null,
			pokes: [],
			ablation: null
		};
		return { view, final, run: rec.states };
	}

	/**
	 * The words after `<final>`: greedy from the cached prompt + program, then the program's last token and the line.
	 * `budget` is ANSWER_MAX_TOKENS, plus the sum's digits for a Mealy run (ARITH_FORMAT §7: the words repeat it).
	 */
	private async words(
		fin: number[],
		budget: number,
		signal?: AbortSignal,
		onToken?: (text: string, n: number) => void
	) {
		const sess = this.session;
		if (!sess) throw new Error('no program cached for the words');
		const f = await this.feed([sess.last, ...fin], sess.past, signal);
		try {
			const out = await this.greedy(f.logits, f.past, budget, [], signal, onToken);
			if (out.past !== f.past) out.past.dispose();
			return { ids: out.ids, text: out.text, finish: out.finish, fin };
		} finally {
			f.past.dispose();
		}
	}

	// -------------------------------------------------------------- number mode (ARITH_FORMAT)

	/**
	 * One Mealy tick (§4, as amended 28 Oct): the block [s][a][b] at |Π| … |Π|+2 over Π's cache gives t; then the whole
	 * block [s][a][b][t] at |Π| … |Π|+3, again over Π's cache, gives o at |Π|+3. The fed t is always forward 1's
	 * argmax. Neither forward keeps its extended cache, so Π's is never written, and both are multi-token forwards
	 * (the 1-token [t] of the first version was not bitwise reproducible on an H100).
	 */
	private async mealyTick(entry: MealyEntry, s: number, a: number, b: number) {
		const f1 = await this.lm.forward([s, a, b], entry.past, false);
		const one = top2(f1.logits);
		const f2 = await this.lm.forward([s, a, b, one.arg], entry.past, false);
		const two = top2(f2.logits);
		return {
			t: one.arg,
			m1: round4(one.margin),
			o: two.arg,
			m2: round4(two.margin),
			ok: one.margin > 0 && two.margin > 0,
			bits: [f1.bits, f2.bits] as [string, string],
			z: pick(f1.logits, entry.stateIds)
		};
	}

	/** §5: every row (s, a, b, t, o) as one tick over the same cached Π; kept per Π like the Moore certificates. */
	private async certifiedMealy(
		pi: number[],
		rows: MealyRegister['rows'],
		stateIds: number[],
		signal?: AbortSignal,
		onRow?: (k: number, r: MealyCertRow) => void
	): Promise<{ entry: MealyEntry; cached: boolean }> {
		const key = pi.join(',');
		const have = this.mealyPis.get(key);
		if (have) {
			this.mealyPis.delete(key);
			this.mealyPis.set(key, have);
			have.rows.forEach((r, k) => onRow?.(k, r));
			return { entry: have, cached: true };
		}
		const t0 = now();
		check(signal);
		const pre = await this.lm.forward(pi, null, true);
		const entry: MealyEntry = {
			key,
			past: pre.past!,
			P: pi.length,
			rows: [],
			bits: new Map(),
			z: new Map(),
			stateIds,
			seconds: 0
		};
		try {
			for (const [s, a, b, t, o] of rows) {
				check(signal);
				const k = await this.mealyTick(entry, s, a, b);
				const r: MealyCertRow = {
					s,
					a,
					b,
					t,
					o,
					tArg: k.t,
					oArg: k.o,
					m1: k.m1,
					m2: k.m2,
					ok: k.t === t && k.o === o && k.ok
				};
				entry.rows.push(r);
				entry.bits.set(cell(s, a, b), k.bits);
				entry.z.set(cell(s, a, b), k.z);
				onRow?.(entry.rows.length - 1, r);
			}
		} catch (err) {
			entry.past.dispose();
			throw err;
		}
		entry.seconds = secs(t0);
		this.mealyPis.set(key, entry);
		while (this.mealyPis.size > this.maxPis) {
			const [k, old] = this.mealyPis.entries().next().value!;
			old.past.dispose();
			this.mealyPis.delete(k);
		}
		return { entry, cached: false };
	}

	/**
	 * §6: (s_i, o_i) from the tick on (s_{i-1}, a_i, b_i); a real tick is bitwise equal when both logit vectors equal
	 * its certified row's. Lookup mode reads a certified table's later steps from the rows' two argmaxes.
	 */
	private async mealyRun(
		entry: MealyEntry,
		s0: number,
		pairs: [number, number][],
		signal: AbortSignal | undefined,
		onTick: (
			i: number,
			s: number,
			t: number,
			o: number,
			m1: number,
			m2: number,
			eq: boolean | null,
			z: Float32Array
		) => void,
		lookupAfter: number | null = null
	) {
		const t0 = now();
		const row = new Map(entry.rows.map((r) => [cell(r.s, r.a, r.b), r]));
		const certified = entry.rows.every((r) => r.ok);
		let s = s0;
		const states: number[] = [];
		const outputs: number[] = [];
		const margins: number[] = [];
		const same: boolean[] = [];
		let looked = 0;
		for (let i = 0; i < pairs.length; i++) {
			const [a, b] = pairs[i];
			const r = row.get(cell(s, a, b));
			if (lookupAfter !== null && certified && i >= lookupAfter && r) {
				states.push(r.tArg);
				outputs.push(r.oArg);
				margins.push(Math.min(r.m1, r.m2));
				looked++;
				onTick(i, s, r.tArg, r.oArg, r.m1, r.m2, null, entry.z.get(cell(s, a, b))!);
				s = r.tArg;
				if (looked % 256 === 0) await new Promise((res) => setTimeout(res, 0));
				continue;
			}
			check(signal);
			const k = await this.mealyTick(entry, s, a, b);
			const want = entry.bits.get(cell(s, a, b));
			const eq = !!want && want[0] === k.bits[0] && want[1] === k.bits[1];
			states.push(k.t);
			outputs.push(k.o);
			margins.push(Math.min(k.m1, k.m2));
			same.push(eq);
			onTick(i, s, k.t, k.o, k.m1, k.m2, eq, k.z);
			s = k.t;
		}
		return { states, outputs, margins, same, looked, seconds: secs(t0) };
	}

	/** Number mode, from the parsed program to the words (ARITH_FORMAT §3 to §7). */
	private async numbers(
		question: string,
		opts: AskOptions,
		prog: Program,
		ids: number[],
		trace: LlmTrace,
		timing: Record<string, number>,
		tAll: number,
		finish: (note: string | null, answer?: string) => LlmTrace,
		emit: (ev: EngineEvent) => void
	): Promise<LlmTrace> {
		const { signal } = opts;
		const cp = clockPairs(this.tok, question, prog);
		trace.input = { events: null, char_spans: null, anchors: null, error: cp.why };
		const reg = prog.mealy[0];
		const digit = digitIds(this.tok);
		const adder = !!reg && isAdder(reg, digit);
		if (prog.error || !cp.pairs || cp.reading?.numbers === null || !cp.reading) {
			if (opts.addition)
				trace.score = {
					parsed: !prog.error,
					table_exact: adder,
					tape_exact: false,
					certified: false,
					run_final_right: false,
					answer_correct: false,
					sum_right: false
				};
			return finish(`the loop stopped before the run: ${cp.why}`);
		}
		const pairs = cp.pairs;
		const [n1, n2] = cp.reading.numbers;
		const spans = cp.reading.spans;
		const events = pairs.map(([a, b]) => `${this.name(a)}+${this.name(b)}`);
		trace.input = { events, char_spans: null, anchors: null, error: null };
		const arith: ArithRecord = {
			numbers: [n1, n2],
			spans,
			quotes: { first: prog.numbers.first!, second: prog.numbers.second! },
			columns: pairs.length,
			sum: null,
			check: exactSum(n1, n2),
			adder
		};
		trace.arith = arith;
		if (!opts.title) trace.title = `Your addition, ${pairs.length.toLocaleString('en-US')} columns`;
		emit({ type: 'tape', events, span: spans[0], char_spans: null, numbers: [n1, n2], spans });

		const { view, final, rec, pass, fin } = await this.mealyCall(
			reg,
			pairs,
			events,
			trace.compile.text,
			timing,
			signal,
			emit,
			opts.lookupAfter ?? null
		);
		trace.registers.push(view);

		// the final line and the words (§7)
		arith.sum = sumOf(this.tok, fin, reg);
		emit({ type: 'stage', stage: 'answer' });
		const t0 = now();
		const words = await this.words(fin, ANSWER_MAX_TOKENS + rec.outputs.length, signal, (text, n) =>
			emit({ type: 'answer', text, tokens: n })
		);
		timing.answer = secs(t0);
		timing.total = secs(tAll);
		trace.answer = pyStrip(words.text);
		trace.final_text = pyStrip(this.tok.decode(fin));
		trace.timing = timing;
		trace.ctx = {
			program_ids: ids,
			nl: this.ids.nl,
			registers: [],
			tape: [],
			finals: { [reg.name]: final },
			mealy: {
				name: reg.name,
				output: reg.output,
				start: reg.start,
				rows: reg.rows,
				run: rec.states,
				outputs: rec.outputs
			},
			pairs
		};
		if (opts.addition) {
			const want = exactSum(opts.addition.a, opts.addition.b);
			trace.truth = want;
			const truePairs = digitPairsIds(opts.addition.a, opts.addition.b, digit);
			trace.score = {
				parsed: true,
				table_exact: adder,
				tape_exact: sameIds(truePairs, pairs),
				certified: pass,
				run_final_right: arith.sum === want,
				sum_right: arith.sum === want,
				answer_correct: lastNumber(trace.answer) === want
			};
			const trueOut = trueOutputIds(opts.addition.a, opts.addition.b, digit);
			const got = rec.outputs;
			const wrong: number[] = [];
			for (let k = 0; k < Math.min(got.length, trueOut.length); k++)
				if (got[k] !== trueOut[k]) wrong.push(k);
			if (got.length !== trueOut.length && !wrong.length)
				wrong.push(Math.min(got.length, trueOut.length));
			view.exact = !wrong.length;
			view.first_wrong_step = wrong.length ? wrong[0] : null;
			view.steps_wrong = wrong.length;
		}
		emit({ type: 'trace', trace });
		return trace;
	}

	/**
	 * Certifies one Mealy register (§5; none of it when its Π was certified before) and runs it over the digit pairs
	 * (§6), emitting the register, its rows, the certificate and the ticks; then the `<final>` ids (§7). Number mode
	 * and REASON's calls share it: the clock runs whatever rows are certified, the adder's or any other.
	 */
	private async mealyCall(
		reg: MealyRegister,
		pairs: [number, number][],
		events: string[],
		text: string,
		timing: Record<string, number>,
		signal: AbortSignal | undefined,
		emit: (ev: EngineEvent) => void,
		lookupAfter: number | null,
		/** between a pair's two digits in the event names: `+` (the adder's, and today's for any table), `−` */
		sep = '+'
	) {
		// certify (§5): 400 forwards for the adder, or none when this Π was certified before
		const rows = reg.rows;
		const stateIds = [...new Set(rows.map((r) => r[0]))];
		const states = stateIds.map(this.name);
		emit({ type: 'stage', stage: 'certify', register: reg.name, total: rows.length });
		emit({
			type: 'register',
			index: 0,
			name: reg.name,
			start: this.name(reg.start),
			states,
			events: [...new Set(rows.map((r) => `${this.name(r[1])}${sep}${this.name(r[2])}`))],
			rows: rows.map(([s, a, b, t, o]) => ({
				s: this.name(s),
				a: this.name(a),
				b: this.name(b),
				t: this.name(t),
				o: this.name(o)
			})),
			mealy: { output: reg.output }
		});
		const outRows: ProgramRow[] = [];
		const rowView = (c: MealyCertRow): ProgramRow => ({
			s: this.name(c.s),
			a: this.name(c.a),
			b: this.name(c.b),
			t: this.name(c.t),
			o: this.name(c.o),
			m: c.m1,
			m2: c.m2,
			ok: c.ok,
			...(c.tArg !== c.t ? { argmax: this.name(c.tArg) } : {}),
			...(c.oArg !== c.o ? { argmax2: this.name(c.oArg) } : {})
		});
		const { entry } = await this.certifiedMealy(reg.pi, rows, stateIds, signal, (k, c) => {
			outRows[k] = rowView(c);
			emit({ type: 'row', index: 0, k, row: outRows[k] });
		});
		const cert = entry.rows;
		const pass = cert.every((c) => c.ok);
		const rowsWrong = cert.filter((c) => !c.ok).length;
		const minMargin = Math.min(...cert.map((c) => Math.min(c.m1, c.m2)));
		timing[`certify:${reg.name}`] = entry.seconds;
		const { codebook, project } = makeCodebook(
			states,
			rows.map(([s, a, b]) => entry.z.get(cell(s, a, b))!),
			cert.map((c) => stateIds.indexOf(c.tArg))
		);
		emit({
			type: 'certificate',
			index: 0,
			pass,
			rows: rows.length,
			rows_wrong: rowsWrong,
			min_margin: minMargin,
			seconds: entry.seconds,
			codebook
		});

		// run (§6)
		emit({ type: 'stage', stage: 'run', register: reg.name, total: pairs.length });
		const rowOf = new Map(rows.map(([s, a, b], k) => [cell(s, a, b), k]));
		const steps: LlmRegister['steps'] = [];
		let batch: LlmRegister['steps'] = [];
		let lastEmit = now();
		const rec = await this.mealyRun(
			entry,
			reg.start,
			pairs,
			signal,
			(i, s, t, o, m1, m2, eq, z) => {
				const [a, b] = pairs[i];
				const st = {
					i,
					event: events[i],
					s: this.name(s),
					row: rowOf.get(cell(s, a, b)) ?? -1,
					t: this.name(t),
					margin: m1,
					pair: [this.name(a), this.name(b)] as [string, string],
					o: this.name(o),
					m2,
					...(eq === null ? { lookup: true as const } : { eq }),
					xyz: project(z) as Xyz
				};
				steps.push(st);
				batch.push(st);
				const tn = now();
				if (tn - lastEmit > 60 || i === pairs.length - 1) {
					lastEmit = tn;
					emit({ type: 'ticks', index: 0, steps: batch, done: i + 1, total: pairs.length });
					batch = [];
				}
			},
			lookupAfter
		);
		timing[`run:${reg.name}`] = rec.seconds;
		const final = rec.states.length ? rec.states[rec.states.length - 1] : reg.start;
		const real = rec.same.length;
		const equal = rec.same.filter(Boolean).length;
		const view: LlmRegister = {
			name: reg.name,
			program: {
				text,
				states,
				events: [...new Set(rows.map((r) => `${this.name(r[1])}${sep}${this.name(r[2])}`))],
				start: this.name(reg.start),
				rows: outRows,
				row_lines: rowLines(text, reg.name, rows.length),
				registers: [reg.name],
				mealy: { output: reg.output },
				...(states.length <= 40
					? { diagram: { kind: 'ring' as const, pos: ring(states.length), dims: null } }
					: {})
			},
			certificate: {
				kind: 'logit',
				pairs_checked: rows.length,
				all_ok: pass,
				certified: pass,
				rows_wrong: rowsWrong,
				min_margin: minMargin,
				N_star: null,
				A: rows.length / Math.max(1, states.length),
				covers:
					'execution of this table on every pair of numbers of any length (Theorem P for the Mealy block), on ' +
					'this GPU and code path; not whether the table is the adder, nor whether the spans are the numbers',
				path:
					"two forwards per row and per tick, each over Π's cached keys and values: [c][a][b] at |Π|…|Π|+2, " +
					'then [c][a][b][c′] at |Π|…|Π|+3; batch 1, in this browser',
				ticks_real: real,
				ticks_equal: equal
			},
			attention: null,
			codebook,
			steps,
			final: this.name(final),
			ticks: {
				real,
				bitwise_equal_to_certified_row: equal,
				seconds: rec.seconds,
				ms_per_tick: real ? Math.round((100000 * rec.seconds) / real) / 100 : null,
				...(rec.looked ? { lookup: rec.looked, lookup_after: lookupAfter } : {})
			},
			exact: null,
			first_wrong_step: null,
			pokes: [],
			ablation: null
		};
		const fin = finalIdsMealy(this.tok, reg, final, rec.outputs);
		return { view, final, rec, pass, fin };
	}

	/**
	 * A poke on a Mealy run (§6): force the carry entering column `step`, real ticks to the end, the final line and
	 * the words. The prediction is the table's own run from the forced carry, after the run's own first outputs.
	 */
	private async pokeMealy(
		question: string,
		ctx: LlmCtx,
		step: number,
		forced: number,
		opts: { signal?: AbortSignal; from?: string; lookupAfter?: number | null },
		emit: (ev: EngineEvent) => void
	): Promise<Poke & { min_margin: number | null; seconds: Record<string, number> }> {
		if (this.busy) throw new Error('the model is busy with another question');
		this.busy = true;
		try {
			question = question.normalize('NFC');
			const t0 = now();
			const m = ctx.mealy!;
			const pairs = ctx.pairs ?? [];
			const stateIds = [...new Set(m.rows.map((r) => r[0]))];
			const forcedId = stateIds[forced];
			if (forcedId === undefined)
				throw new Error('the forced state is not one of the table’s states');
			if (step < 0 || step >= pairs.length) throw new Error('the step is off the tape');
			const pi = m.rows.flatMap((row) => [...row, ctx.nl]);
			emit({ type: 'stage', stage: 'poke', register: m.name, total: pairs.length - step });
			const { entry, cached } = await this.certifiedMealy(pi, m.rows, stateIds, opts.signal);
			const rest = pairs.slice(step);
			let last = now();
			const rec = await this.mealyRun(
				entry,
				forcedId,
				rest,
				opts.signal,
				(i) => {
					if (now() - last > 120) {
						last = now();
						emit({ type: 'prefill', done: i + 1, total: rest.length });
					}
				},
				opts.lookupAfter ?? null
			);
			const delta = new Map(m.rows.map(([s, a, b, t, o]) => [cell(s, a, b), [t, o] as const]));
			let pred: number | null = forcedId;
			const predOut: number[] = [];
			for (const [a, b] of rest) {
				const d = delta.get(cell(pred, a, b));
				if (!d) {
					pred = null;
					break;
				}
				pred = d[0];
				predOut.push(d[1]);
			}
			const final = rec.states.length ? rec.states[rec.states.length - 1] : forcedId;
			const outputs = [...m.outputs.slice(0, step), ...rec.outputs];
			const predicted = pred === null ? null : [...m.outputs.slice(0, step), ...predOut];
			const fin = finalIdsMealy(this.tok, m, final, outputs);
			const sumAfter = sumOf(this.tok, fin, m);
			const predictedSum =
				predicted && pred !== null
					? sumOf(this.tok, finalIdsMealy(this.tok, m, pred, predicted), m)
					: null;
			await this.ensureSession(question, ctx.program_ids, opts.signal);
			const tw = now();
			const words = await this.words(fin, ANSWER_MAX_TOKENS + outputs.length, opts.signal);
			const answer = pyStrip(words.text);
			return {
				step,
				from: opts.from ?? this.name(step > 0 ? (m.run[step - 1] ?? m.start) : m.start),
				forced: this.name(forcedId),
				final: this.name(final),
				predicted_state: pred === null ? null : this.name(pred),
				answer_after: answer,
				predicted: predictedSum === null ? null : `the sum ${predictedSum}`,
				match: pred !== null && final === pred && sameList(outputs, predicted!),
				answer_states_prediction:
					predictedSum === null ? null : lastNumber(answer) === predictedSum,
				ticks: rec.states.length,
				ticks_equal: rec.same.filter(Boolean).length,
				min_margin: rec.margins.length ? Math.min(...rec.margins) : null,
				live: true,
				sum_after: sumAfter ?? undefined,
				predicted_sum: predictedSum,
				seconds: { ticks: rec.seconds, answer: secs(tw), total: secs(t0), cached: cached ? 1 : 0 }
			};
		} finally {
			this.busy = false;
		}
	}

	/**
	 * dl_core.Engine.poke: force the state entering tick `step` of `register` (the `forced`-th of its table's states),
	 * real ticks to the end, then the words. The program's prediction is its own table run from the forced state.
	 */
	async poke(
		question: string,
		ctx: LlmCtx,
		register: string,
		step: number,
		forced: number,
		opts: {
			truth?: Truth | null;
			signal?: AbortSignal;
			from?: string;
			lookupAfter?: number | null;
		} = {},
		emit: (ev: EngineEvent) => void = () => {}
	): Promise<Poke & { min_margin: number | null; seconds: Record<string, number> }> {
		if (ctx.mealy && register === ctx.mealy.name)
			return this.pokeMealy(question, ctx, step, forced, opts, emit);
		if (this.busy) throw new Error('the model is busy with another question');
		this.busy = true;
		try {
			question = question.normalize('NFC');
			const t0 = now();
			const reg = ctx.registers.find((r) => r.name === register);
			if (!reg) throw new Error(`no register ${register}`);
			const stateIds = [...new Set(reg.rows.map(([s]) => s))];
			const forcedId = stateIds[forced];
			if (forcedId === undefined)
				throw new Error('the forced state is not one of the table’s states');
			if (step < 0 || step >= ctx.tape.length) throw new Error('the step is off the tape');
			const pi = reg.rows.flatMap((row) => [...row, ctx.nl]);
			emit({ type: 'stage', stage: 'poke', register, total: ctx.tape.length - step });
			const { entry, cached } = await this.certified(pi, reg.rows, stateIds, opts.signal);
			const rest = ctx.tape.slice(step);
			let last = now();
			const rec = await this.ticks(
				entry,
				forcedId,
				rest,
				opts.signal,
				(i) => {
					if (now() - last > 120) {
						last = now();
						emit({ type: 'prefill', done: i + 1, total: rest.length });
					}
				},
				opts.lookupAfter ?? null
			);
			const delta = new Map(reg.rows.map(([s, e, t]) => [pair(s, e), t]));
			let pred = forcedId;
			for (const e of rest) {
				pred = delta.get(pair(pred, e)) ?? -1;
				if (pred < 0) break;
			}
			const final = rec.states.length ? rec.states[rec.states.length - 1] : forcedId;
			const finals = { ...ctx.finals, [register]: final };
			await this.ensureSession(question, ctx.program_ids, opts.signal);
			const tw = now();
			const words = await this.words(
				finIds(this.tok, ctx.registers, finals),
				ANSWER_MAX_TOKENS,
				opts.signal
			);
			const answer = pyStrip(words.text);
			const finalName = this.name(final);
			const k = ctx.registers.indexOf(reg);
			const p = opts.truth ? predictedFor(opts.truth, register, k, finalName) : null;
			return {
				step,
				from:
					opts.from ??
					(step > 0
						? this.name(ctx.registers[k].run?.[step - 1] ?? reg.start)
						: this.name(reg.start)),
				forced: this.name(forcedId),
				final: finalName,
				predicted_state: pred >= 0 ? this.name(pred) : null,
				answer_after: answer,
				predicted: p?.answer ?? null,
				match: final === pred,
				answer_states_prediction: p?.key ? answerCorrect(p.key, answer) : null,
				ticks: rec.states.length,
				ticks_equal: rec.same.filter(Boolean).length,
				min_margin: rec.margins.length ? Math.min(...rec.margins) : null,
				live: true,
				seconds: { ticks: rec.seconds, answer: secs(tw), total: secs(t0), cached: cached ? 1 : 0 }
			};
		} finally {
			this.busy = false;
		}
	}

	// -------------------------------------------------------------- calls in the middle (REASON_FORMAT)

	/**
	 * REASON_FORMAT §7: generate until `<exec/>` or the end token; at an `<exec/>`, parse the call from its own ids,
	 * read its input from the sources (§3) or the results (§5), build Π fresh at positions 0 …, certify and run it as a
	 * single call is run, append its final line (or an error line, §6), feed the final's ids into the cache like a
	 * prompt, and resume. At most 8 calls run; an `<exec/>` beyond the 8th gets an error line and the 12th ends the
	 * response. A response with no call is today's reply, in today's shape.
	 */
	private async askMulti(
		question: string,
		opts: AskOptions,
		emit: (ev: EngineEvent) => void
	): Promise<LlmTrace> {
		const { signal } = opts;
		const tAll = now();
		const timing: Record<string, number> = {};
		const promptIds = this.enc(chatPrompt(question));
		this.session?.past.dispose();
		this.session = null;

		emit({ type: 'stage', stage: 'prefill', total: promptIds.length });
		let t0 = now();
		const head = await this.feed(promptIds, null, signal, (done) =>
			emit({ type: 'prefill', done, total: promptIds.length })
		);
		timing.prefill = secs(t0);
		timing.compile = 0;

		/** the cache of everything fed so far, and the logits for the next token */
		let cache = head.past;
		let logits = head.logits;
		/** the response: the model's ids and the clock's finals, in order */
		const response: number[] = [];
		const calls: ReasonCall[] = [];
		const segments: ReasonSegment[] = [];
		const results: (string | null)[] = [];
		/** where the text after the last final starts */
		let textFrom = 0;
		let written = 0;
		let end: ReasonRecord['end'];
		try {
			for (;;) {
				emit({ type: 'stage', stage: 'compile' });
				t0 = now();
				let lastEmit = 0;
				const first = !calls.length;
				const prev = results.at(-1);
				const gen = await this.greedy(
					logits,
					cache,
					// room to copy the last result into the words, as a single call's words have (ARITH_FORMAT §7)
					COMPILE_MAX_TOKENS + (prev ? prev.length : 0),
					// `<check>` opens the older rule-style format: as today, only before any call
					first ? ['<exec/>', '<check>'] : ['<exec/>'],
					signal,
					(text, n) => {
						const t = now();
						if (t - lastEmit > 40) {
							lastEmit = t;
							emit({ type: 'compile', text, tokens: n, seconds: secs(t0) });
						}
					}
				);
				if (gen.past !== cache) {
					cache.dispose();
					cache = gen.past;
				}
				const seconds = secs(t0);
				timing.compile += seconds;
				written += gen.ids.length;
				response.push(...gen.ids);
				const exec = gen.text.includes('<exec/>');
				emit({
					type: 'program',
					text: gen.text,
					tokens: gen.ids.length,
					seconds,
					exec,
					finish: gen.finish
				});
				if (first && !exec) {
					// no call at all: today's reply (or today's rule-style stop), in today's shape
					const trace = this.blank(question, opts, gen.text, gen.ids.length, gen.finish, seconds);
					const plain = !gen.text.includes('<check>');
					timing.total = secs(tAll);
					Object.assign(trace, {
						answer: plain ? pyStrip(gen.text) : '',
						note: plain ? PLAIN_NOTE : RULE_STYLE_NOTE,
						timing
					});
					emit({ type: 'trace', trace });
					return trace;
				}
				if (!exec) {
					end = gen.finish === 'length' ? 'length' : 'stop';
					break;
				}

				// the clock: the call's own ids, from its last <program> to <exec/>
				const k = calls.length + 1;
				const at = lastCallStart(this.tok, response) ?? 0;
				const program = this.tok.decode(response.slice(at));
				const before = this.tok.decode(response.slice(textFrom, Math.max(textFrom, at)));
				segments.push({ kind: 'text', text: before }, { kind: 'call', k });
				emit({ type: 'call', k, before, program, start: at, end: response.length });
				const sub = this.callTrace(question, opts, k, program, response.length - at, seconds);
				const limit = limitAt(calls.length);
				if (limit === 'end') {
					const call = this.refused(k, at, response.length, program, sub, null);
					calls.push(call);
					emit({ type: 'final', call });
					end = 'hard stop';
					break;
				}
				const call =
					limit === 'too many'
						? this.refused(k, at, response.length, program, sub, errorFinalIds(this.tok, TOO_MANY))
						: await this.runCall(question, opts, k, at, response, results, sub, emit);
				calls.push(call);
				results.push(call.value);
				emit({ type: 'final', call });
				// the final's ids go into the cache like a prompt, after the call's last token (never fed yet)
				const fin = call.final_ids!;
				response.push(...fin);
				textFrom = response.length;
				const f = await this.feed([gen.ids[gen.ids.length - 1], ...fin], cache, signal);
				cache.dispose();
				cache = f.past;
				logits = f.logits;
			}

			if (end !== 'hard stop')
				segments.push({ kind: 'text', text: this.tok.decode(response.slice(textFrom)) });
			const trace = this.blank(
				question,
				opts,
				this.tok.decode(response),
				written,
				end === 'length' ? 'length' : 'stop',
				timing.compile
			);
			if (!opts.title)
				trace.title = `Your question, ${calls.length} call${calls.length === 1 ? '' : 's'}`;
			// §7: the answer is the text after the last final
			trace.answer = pyStrip(this.tok.decode(response.slice(textFrom)));
			const last = calls.findLast((c) => c.final_text !== null);
			trace.final_text = last ? pyStrip(last.final_text!) : null;
			trace.reason = { format: 'REASON_FORMAT', segments, calls, response_ids: response, end };
			timing.total = secs(tAll);
			trace.timing = timing;
			emit({ type: 'trace', trace });
			return trace;
		} finally {
			cache.dispose();
		}
	}

	/** A call's run in the panels' shape, before it has a tape or registers. */
	private callTrace(
		question: string,
		opts: AskOptions,
		k: number,
		program: string,
		tokens: number,
		seconds: number
	): LlmTrace {
		const t = this.blank(
			question,
			{ ...opts, title: `Call ${k}`, truth: null },
			program,
			tokens,
			'stop',
			seconds
		);
		t.id = `${opts.id}/call-${k}`;
		t.timing = {};
		return t;
	}

	/** A call the clock does not run: beyond the 8th (an error line), or the 12th (no line; the response ends). */
	private refused(
		k: number,
		start: number,
		end: number,
		program: string,
		sub: LlmTrace,
		fin: number[] | null
	): ReasonCall {
		sub.note = fin
			? `the clock runs at most 8 calls, so call ${k} got an error line`
			: `call ${k} ends the response: the clock runs at most 8 calls, and the 12th stops the words`;
		const text = fin ? this.tok.decode(fin) : null;
		sub.final_text = text === null ? null : pyStrip(text);
		return {
			k,
			start,
			end,
			program,
			mode: null,
			error: fin ? TOO_MANY : 'hard stop',
			spans: [],
			how: [],
			read: [],
			final_text: text,
			final_ids: fin,
			value: null,
			certified: null,
			run: sub
		};
	}

	/**
	 * One call (§2 to §6): parse it from its own ids with result citations, read its input, then certify and run each
	 * register on a Π built fresh, as a single call's; the final line or the error line.
	 */
	private async runCall(
		question: string,
		opts: AskOptions,
		k: number,
		at: number,
		response: number[],
		results: (string | null)[],
		sub: LlmTrace,
		emit: (ev: EngineEvent) => void
	): Promise<ReasonCall> {
		const { signal } = opts;
		const lookupAfter = opts.lookupAfter ?? null;
		const timing = sub.timing!;
		const t0 = now();
		emit({ type: 'stage', stage: 'tape' });
		const prog = parseGenerated(this.tok, response.slice(at), this.ids.nl, { results: true });
		const reading = readCall(this.tok, question, this.tok.decode(response), prog, results);
		const base = {
			k,
			start: at,
			end: response.length,
			program: sub.compile.text,
			mode: prog.mode,
			spans: reading.spans,
			how: reading.how,
			read: readOf(reading, results)
		};
		sub.input = { events: null, char_spans: null, anchors: prog.anchors, error: reading.error };
		if (reading.error) {
			const fin = errorFinalIds(this.tok, reading.error);
			const text = this.tok.decode(fin);
			sub.note = `the clock could not run call ${k}: ${reading.error}`;
			sub.final_text = pyStrip(text);
			timing.total = secs(t0);
			return {
				...base,
				error: reading.error,
				final_text: text,
				final_ids: fin,
				value: null,
				certified: null,
				run: sub
			};
		}
		let fin: number[];
		if (prog.mode === 'tape') {
			const tape = reading.tape!;
			const [src, b, e] = reading.spans[0] as [number, number, number];
			const events = tape.map(this.name);
			sub.input = {
				events,
				char_spans: charSpans(this.tok, reading.sources[src], [b, e], tape),
				anchors: prog.anchors,
				error: null
			};
			sub.title = `Call ${k}, ${tape.length.toLocaleString('en-US')} events`;
			emit({ type: 'tape', events, span: [b, e], char_spans: sub.input.char_spans ?? null });
			const finals: Record<string, number> = {};
			for (let index = 0; index < prog.registers.length; index++) {
				const r = prog.registers[index];
				const v = await this.register(r, index, prog, tape, sub, timing, signal, emit, lookupAfter);
				v.view.exact = followsTable(v.view);
				sub.registers.push(v.view);
				finals[r.name] = v.final;
			}
			fin = finIds(this.tok, prog.registers, finals);
		} else {
			const reg = prog.mealy[0];
			const digit = digitIds(this.tok);
			const op = isAdder(reg, digit) ? 'add' : isSubtracter(reg, digit) ? 'sub' : null;
			const sep = op === 'sub' ? '−' : '+';
			const pairs = reading.pairs!;
			const [n1, n2] = reading.numbers!;
			const events = pairs.map(([a, b]) => `${this.name(a)}${sep}${this.name(b)}`);
			const spans = reading.spans.map((sp): [number, number] =>
				sp[0] === 'result' ? [0, 0] : [sp[1], sp[2]]
			) as [[number, number], [number, number]];
			const from = reading.spans.map((sp): ReasonFrom =>
				sp[0] === 'result' ? { result: sp[1] } : { source: sp[0] as 0 | 1 }
			) as [ReasonFrom, ReasonFrom];
			const arith: ArithRecord = {
				numbers: [n1, n2],
				spans,
				quotes: {
					first: prog.numbers.first ?? ['', ''],
					second: prog.numbers.second ?? ['', '']
				},
				columns: pairs.length,
				sum: null,
				check: op === 'add' ? exactSum(n1, n2) : op === 'sub' ? exactDifference(n1, n2) : '',
				adder: op === 'add',
				op,
				from
			};
			sub.input = { events, char_spans: null, anchors: null, error: null };
			sub.arith = arith;
			sub.title = `Call ${k}, ${pairs.length.toLocaleString('en-US')} columns`;
			emit({ type: 'tape', events, span: spans[0], char_spans: null, numbers: [n1, n2], spans });
			const m = await this.mealyCall(
				reg,
				pairs,
				events,
				sub.compile.text,
				timing,
				signal,
				emit,
				lookupAfter,
				sep
			);
			m.view.exact = followsTable(m.view);
			sub.registers.push(m.view);
			fin = m.fin;
			arith.sum = sumOf(this.tok, fin, reg);
		}
		const text = this.tok.decode(fin);
		sub.final_text = pyStrip(text);
		timing.total = secs(t0);
		return {
			...base,
			error: null,
			final_text: text,
			final_ids: fin,
			value: resultValueOf(text),
			certified: sub.registers.every((r) => r.certificate.all_ok),
			run: sub
		};
	}

	/** Makes sure the cache of prompt + program (but its last token) is the one for this run. */
	private async ensureSession(question: string, programIds: number[], signal?: AbortSignal) {
		const key = sessionKey(question, programIds);
		if (this.session?.key === key) return;
		this.session?.past.dispose();
		this.session = null;
		const ids = [...this.enc(chatPrompt(question)), ...programIds.slice(0, -1)];
		const f = await this.feed(ids, null, signal);
		this.session = { key, past: f.past, last: programIds[programIds.length - 1] };
	}

	/** The run before it has registers: the page's shape, filled as the loop goes. */
	private blank(
		question: string,
		opts: AskOptions,
		text: string,
		tokens: number,
		finish: string,
		seconds: number
	): LlmTrace {
		return {
			schema: SCHEMA,
			source: 'savant-browser',
			id: opts.id,
			kind: 'llm',
			title: opts.title ?? 'Your question',
			family: opts.family ?? null,
			live: true,
			where: 'browser',
			model: this.model,
			host: this.host,
			at: new Date().toISOString(),
			prompt: question,
			answer: '',
			final_text: null,
			note: null,
			truth: opts.truth?.answer ?? null,
			base_answer: null,
			base_answer_meta: null,
			compile: { text, tokens, finish, seconds },
			panels: browserPanels(),
			input: { events: null, char_spans: null, anchors: null, error: null },
			registers: [],
			timing: null,
			ctx: null
		};
	}
}

/** What each of a call's spans holds: the text read from its source, or the result cited. */
function readOf(reading: CallReading, results: (string | null)[]): ReasonCall['read'] {
	return reading.spans.map((sp) =>
		sp[0] === 'result'
			? { from: { result: sp[1] }, text: results[sp[1] - 1] ?? '' }
			: { from: { source: sp[0] as 0 | 1 }, text: reading.sources[sp[0]].slice(sp[1], sp[2]) }
	);
}

/**
 * The run is its own table's run: every step lands where its row says, and writes the row's output (Theorem P says
 * a certified table's always does). True for a run of no steps.
 */
export function followsTable(r: LlmRegister): boolean {
	return r.steps.every((st) => {
		const row = r.program.rows[st.row];
		return !!row && row.t === st.t && (row.o === undefined || row.o === st.o);
	});
}

const sessionKey = (question: string, ids: number[]) => `${question}\u0000${ids.join(',')}`;

function pick(logits: Float32Array, ids: number[]): Float32Array {
	const out = new Float32Array(ids.length);
	ids.forEach((id, i) => (out[i] = logits[id]));
	return out;
}

/** dl_page._ring */
export function ring(n: number): [number, number][] {
	return Array.from({ length: n }, (_, k) => [
		Math.round((0.5 + 0.5 * Math.cos((2 * Math.PI * k) / n - Math.PI / 2)) * 1e4) / 1e4,
		Math.round((0.5 + 0.5 * Math.sin((2 * Math.PI * k) / n - Math.PI / 2)) * 1e4) / 1e4
	]);
}

/** dl_page.row_lines: the line (in the page's program lines) of each row of a register. */
export function rowLines(text: string, register: string, nRows: number): number[] {
	const lines = text.split('\n').filter((l) => !/^<\/?program>$/.test(l.trim()));
	const at = lines.findIndex(
		(l) => l.startsWith(`register ${register}:`) || l.startsWith(`register ${register} (output `)
	);
	if (at < 0) return new Array(nRows).fill(-1);
	return Array.from({ length: nRows }, (_, k) => (at + 1 + k < lines.length ? at + 1 + k : -1));
}

export function browserPanels(): LlmTrace['panels'] {
	const m = { source: 'savant-browser', mock: false };
	const none = { source: null, mock: false };
	return {
		prompt: { ...m, note: 'the question as sent' },
		program: { ...m, note: 'written by Savant-4B in this browser; parsed from its tokens' },
		run: { ...m, note: 'one real tick per event on the certified batch-1 path, in this browser' },
		answer: { ...m, note: "the model's words after the clock's <final> line" },
		base_answer: { ...none, note: 'needs the base weights, which this page does not download' },
		poke: { ...none, note: 'none yet' },
		ablation: { ...none, note: 'needs the base weights, which this page does not download' }
	};
}

/** What the question's own program answers when `register` ends at `finalName` (dl_prompts.predicted). */
export function predictedFor(truth: Truth, register: string, index: number, finalName: string) {
	const per =
		truth.predicted[register] ??
		(index < truth.registers.length ? truth.predicted[truth.registers[index].name] : undefined);
	return per?.[finalName.trim()] ?? null;
}

/** dl_prompts.score_loop for a run in this browser (registers compared in order, as pb_loop does). */
export function scoreLoop(
	prog: Program,
	tape: number[] | null,
	finals: Record<string, number> | null,
	truth: Truth,
	answer: string
): NonNullable<LlmTrace['score']> {
	const got = prog.registers.map((r) => ({
		start: r.start,
		rows: new Map(r.rows.map(([s, e, t]) => [pair(s, e), t]))
	}));
	const want = truth.registers.map((r) => ({
		start: r.start_id,
		rows: new Map(r.table_ids.map(([s, e, t]) => [pair(s, e), t]))
	}));
	const sameTable =
		got.length === want.length &&
		got.every(
			(g, i) =>
				g.start === want[i].start &&
				g.rows.size === want[i].rows.size &&
				[...g.rows].every(([k, v]) => want[i].rows.get(k) === v)
		);
	let rowsWrong = 0;
	want.forEach((w, i) => {
		for (const [k, v] of w.rows) if (got[i]?.rows.get(k) !== v) rowsWrong++;
	});
	const reached = tape !== null && finals !== null;
	return {
		parsed: !prog.error,
		table_exact: sameTable,
		rows_wrong: rowsWrong,
		tape_exact: reached && tape.length === truth.events && fnv1a(tape) === truth.tape_fnv,
		certified: false,
		run_final_right:
			reached &&
			truth.registers.length === prog.registers.length &&
			prog.registers.every((r, i) => finals[r.name] === truth.registers[i].final_id),
		answer_correct: answerCorrect(truth.key, answer)
	};
}

/** dl_prompts.attach_truth: the true answer, the scores, and each register's run against the question's program. */
function attachTruth(
	trace: LlmTrace,
	prog: Program,
	tape: number[],
	finals: Record<string, number>,
	truth: Truth
) {
	trace.truth = truth.answer;
	trace.score = {
		...scoreLoop(prog, tape, finals, truth, trace.answer),
		certified: trace.registers.every((r) => r.certificate.all_ok)
	};
	trace.registers.forEach((rv, i) => {
		const tr = truth.registers[i];
		if (!tr?.trace) return;
		const want = [...tr.trace].map((c) => tr.values[ALPHABET.indexOf(c)]);
		const got = rv.steps.map((s) => s.t);
		const wrong: number[] = [];
		for (let k = 0; k < Math.min(got.length, want.length); k++)
			if (got[k] !== want[k]) wrong.push(k);
		if (got.length !== want.length && !wrong.length) wrong.push(Math.min(got.length, want.length));
		rv.exact = !wrong.length;
		rv.first_wrong_step = wrong.length ? wrong[0] : null;
		rv.steps_wrong = wrong.length;
	});
}

// ------------------------------------------------------------------ number mode helpers

/** The table is the adder's: 200 rows, carry and digits as bare digit tokens, c'·10 + s = c + a + b, start 0. */
export function isAdder(reg: MealyRegister, digit: number[]): boolean {
	if (reg.start !== digit[0] || reg.rows.length !== 200) return false;
	const want = new Map<string, string>();
	for (let c = 0; c < 2; c++)
		for (let a = 0; a < 10; a++)
			for (let b = 0; b < 10; b++) {
				const v = c + a + b;
				want.set(
					cell(digit[c], digit[a], digit[b]),
					`${digit[Math.floor(v / 10)]},${digit[v % 10]}`
				);
			}
	return (
		reg.rows.every(([s, a, b, t, o]) => want.get(cell(s, a, b)) === `${t},${o}`) &&
		new Set(reg.rows.map(([s, a, b]) => cell(s, a, b))).size === 200
	);
}

/** The clock's sum: the `s=` part of the final line, as text. */
function sumOf(tok: Tok, fin: number[], reg: { output: string }): string | null {
	const text = tok.decode(fin);
	const m = new RegExp(` ${reg.output}=(\\S*) </final>`).exec(text);
	return m ? m[1] : null;
}

/** pb_families.last_number: the last number in a text, digit groups joined across commas and spaces. */
export function lastNumber(text: string): string | null {
	const runs = text.match(/\d(?:[\d,\u2009\u202f ]*\d)?/g);
	return runs ? runs[runs.length - 1].replace(/\D/g, '') : null;
}

function digitPairsIds(a: string, b: string, digit: number[]): [number, number][] {
	const n = Math.max(a.length, b.length);
	const ra = [...a].reverse().join('').padEnd(n, '0');
	const rb = [...b].reverse().join('').padEnd(n, '0');
	const out: [number, number][] = [];
	for (let i = 0; i < n; i++) out.push([digit[Number(ra[i])], digit[Number(rb[i])]]);
	out.push([digit[0], digit[0]]);
	return out;
}

function trueOutputIds(a: string, b: string, digit: number[]): number[] {
	let c = 0;
	return digitPairsIds(a, b, digit).map(([x, y]) => {
		const v = c + digit.indexOf(x) + digit.indexOf(y);
		c = Math.floor(v / 10);
		return digit[v % 10];
	});
}

const sameList = (a: number[], b: number[]) =>
	a.length === b.length && a.every((x, i) => x === b[i]);
const sameIds = (a: [number, number][], b: [number, number][]) =>
	a.length === b.length && a.every(([x, y], i) => x === b[i][0] && y === b[i][1]);
