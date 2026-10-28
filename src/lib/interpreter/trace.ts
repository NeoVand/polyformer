/**
 * The demo page's data: traces in `polyformer.trace/0` (research/DEMO_SPEC.md §4 on the notes branch). Three kinds:
 * an automaton run on the frozen INTERP core (one lookup per event) and a REGS run (one instruction of 18 lookups per
 * step), both written by research/demopage/make_traces.py; and an LLM run, PROMPTBOX's Qwen3-4B writing a table and
 * running it one pinned tick per event, written by research/demolive (recorded, or live from the local server).
 * Fields a source cannot fill are absent, never faked.
 */

export type Xyz = [number, number, number];

export interface TraceStep {
	i: number;
	event: string;
	/** the state read at this step (REGS: the program line) */
	s: string;
	/** index into `program.rows` (REGS: the line the fetch reads; LLM: -1 when the run left the table) */
	row: number;
	/** [row, attention weight], largest first (REGS: weight summed over the line's six fields) */
	attn: [number, number][];
	/** the state written (REGS: the next line) */
	t: string;
	/** logit margin of the right name over the best other one (REGS: the smallest over the consumed lookups) */
	margin: number;
	/** the head's output before the snap, in the codebook's 3-D view (LLM: the tick's logits on the state names) */
	xyz?: Xyz;
	/** automaton: distance from that output to the snapped code, per coordinate */
	d?: number;
	/** REGS: the slot of the instruction's tightest lookup */
	ms?: string;
	/** REGS: the debugger's annotation (values read and written) */
	note?: string;
	/** REGS: stores [cell, value] */
	st?: [number, number][];
	/** LLM: the tick's logits are bitwise equal to its certified row's */
	eq?: boolean;
	/** LLM, lookup mode: this step was read from its certified row, not run */
	lookup?: boolean;
	/** Mealy (ARITH_FORMAT): the digit pair read at this column, first number's digit first */
	pair?: [string, string];
	/** Mealy: the output digit written at this column, and the second forward's margin */
	o?: string;
	m2?: number;
}

export interface PanelSource {
	source: string | null;
	mock: boolean;
	note: string;
}

export interface ProgramRow {
	s: string;
	b: string;
	t: string;
	/** automaton: the row's own margin when stepped once from exact codes (LLM: its certified tick's margin) */
	m?: number;
	/** LLM: the certified tick's argmax is the written destination */
	ok?: boolean;
	/** LLM: the argmax when it is not */
	argmax?: string;
	/** LLM: [row, weight] of the chosen head at the event position, largest first */
	attn?: [number, number][];
	/** Mealy rows [s][a][b][t][o]: the first digit (`b` is the second), the output, its margin and its argmax */
	a?: string;
	o?: string;
	m2?: number;
	argmax2?: string;
}

export interface Poke {
	step: number;
	from: string;
	forced: string;
	final: string;
	/** the state the program's own table reaches from the forced state (null: the table has no row on the way) */
	predicted_state: string | null;
	answer_after: string;
	/** the answer the question's program gives for that final state, when the question is a registered one */
	predicted: string | null;
	match: boolean;
	/** LLM: the words after the poke state the predicted answer (by the family's answer key) */
	answer_states_prediction?: boolean | null;
	ticks?: number;
	ticks_equal?: number;
	/** run on the live model in this session, not recorded */
	live?: boolean;
	/** Mealy: the clock's sum after the poke, and the table's own sum from the forced carry */
	sum_after?: string;
	predicted_sum?: string | null;
}

export interface Ablation {
	head: string;
	intervention: string;
	answer: string;
	final: string;
	first_wrong_step: number | null;
	steps_wrong: number;
	constant: boolean;
	state: string;
	correct: boolean | null;
	/** LLM: the state after every tick with the adapter off */
	states?: string[];
	off_table_steps?: number;
	base_certificate?: { pass: boolean; rows: number; rows_right: number; min_margin: number };
	live?: boolean;
}

export interface BaseAnswerMeta {
	model: string;
	mode: string;
	prompt_suffix: string;
	response_tokens: number;
	hit_max_tokens: boolean;
	answer_found: boolean | null;
	correct: boolean | null;
	excerpt: string;
	cell: string | null;
	cell_correct: [number, number] | null;
	cell_wilson95: [number, number] | null;
	file: string | null;
	commit: string | null;
	seconds?: number;
	live?: boolean;
}

export interface RegsTable {
	N: number;
	A: number;
	column: string;
	N_star: number;
	inside: boolean;
}

export interface Trace {
	schema: 'polyformer.trace/0';
	source: string;
	id: string;
	kind: 'automaton' | 'regs' | 'llm';
	title: string;
	family: string;
	model: {
		name: string;
		commit: string | null;
		params_sha256_16: string;
		params: string;
		heads: number;
		about: string;
	};
	host: { cpu: string; machine: string; avx512f: boolean; gpu: string; jax: string };
	prompt: string;
	answer: string;
	truth: string;
	base_answer: string | null;
	base_answer_meta: BaseAnswerMeta | null;
	panels: Record<
		'prompt' | 'program' | 'run' | 'answer' | 'base_answer' | 'poke' | 'ablation',
		PanelSource
	>;
	program: {
		text: string;
		states: string[];
		events: string[];
		start: string;
		rows: ProgramRow[];
		registers?: string[];
		/** LLM: the line of each row in the program text (programLines), -1 when not found */
		row_lines?: number[];
		diagram?: {
			kind: 'ring' | 'grid' | 'chain' | 'cloud';
			pos: [number, number][];
			dims: number[] | null;
		};
		labels?: Record<string, string>;
		lines?: number;
		/** a Mealy register (ARITH_FORMAT): rows [s][a][b][t][o], each tick two forwards, output named here */
		mealy?: { output: string };
	};
	certificate: {
		all_ok: boolean;
		min_margin: number;
		N_star: number | null;
		A: number;
		covers: string;
		certified: boolean;
		pairs_checked?: number;
		N?: number;
		A_column?: number;
		kind?: 'composition' | 'logit';
		lookups_checked?: number;
		tables?: Record<string, RegsTable>;
		/** LLM: rows whose argmax is not their written destination */
		rows_wrong?: number;
		/** LLM: the code path the rows and the ticks share */
		path?: string;
		/** LLM: real ticks in the run, and how many were bitwise equal to their certified row */
		ticks_real?: number;
		ticks_equal?: number;
	};
	input: {
		events?: string[] | null;
		char_spans?: [number, number][] | null;
		numbers?: Record<string, string>;
	};
	codebook: { names: string[]; xyz: Xyz[]; variance_kept: number; projection: string };
	steps: TraceStep[];
	/** every step matched the question's own program (LLM: null when there is no reference, e.g. an edited prompt) */
	exact: boolean | null;
	first_wrong_step: number | null;
	pokes: Poke[];
	ablation: Ablation | null;
	/** LLM: the run this view is one register of */
	llm?: { file: LlmTrace; register: number };
	regs?: {
		slots: string[];
		consumed: Record<string, string[]>;
		mem0: number[];
		cells: Record<string, number>;
		arrays: Record<string, [number, number]>;
		registers: string[];
		pointers: string[];
		hash: number;
		names: Record<string, string>;
		lookups: number;
		consumed_lookups: number;
	};
}

export interface TraceEntry {
	id: string;
	kind: Trace['kind'];
	/** 'llm': recorded from PROMPTBOX's live model; otherwise the frozen INTERP core */
	group?: 'llm';
	title: string;
	prompt: string;
	file: string;
	bytes: number;
	states: number;
	steps: number;
	mock_program: boolean;
	base_answer: boolean;
}

/** An LLM run's register, in the shapes the panels read. */
export interface LlmRegister {
	name: string;
	program: Trace['program'];
	certificate: Trace['certificate'];
	attention: {
		head: string;
		mean_on_matching_row: number;
		min_on_matching_row: number;
		rows_where_matching_row_is_top: number;
		rows: number;
		how: string;
		sdpa_path_restored?: boolean;
		error?: string;
	} | null;
	codebook: Trace['codebook'];
	steps: Omit<TraceStep, 'attn'>[];
	final: string;
	ticks: {
		real: number;
		bitwise_equal_to_certified_row: number;
		seconds: number;
		ms_per_tick: number | null;
		/** lookup mode: steps read from their certified rows after the first `lookup_after` events */
		lookup?: number;
		lookup_after?: number | null;
	};
	exact: boolean | null;
	first_wrong_step: number | null;
	steps_wrong?: number;
	pokes: Poke[];
	ablation: Ablation | null;
}

/** What the server needs to poke or switch off a run it made: token ids, never shown. */
export interface LlmCtx {
	program_ids: number[];
	nl: number;
	registers: { name: string; start: number; rows: [number, number, number][]; run?: number[] }[];
	tape: number[];
	finals: Record<string, number>;
	/** number mode (ARITH_FORMAT): the Mealy register, its run and outputs, and the digit pairs read */
	mealy?: {
		name: string;
		output: string;
		start: number;
		rows: [number, number, number, number, number][];
		run: number[];
		outputs: number[];
	};
	pairs?: [number, number][];
}

/** A number-mode run (ARITH_FORMAT): what the clock read, what it wrote, and the page's own check. */
export interface ArithRecord {
	/** the two numbers the clock read (digits only) and where they are in the question */
	numbers: [string, string];
	spans: [[number, number], [number, number]];
	quotes: { first: [string, string]; second: [string, string] };
	/** columns run: the longer number's digits and one more 0 0 pair */
	columns: number;
	/** the clock's sum: the output tape, last first, leading zeros dropped */
	sum: string | null;
	/** BigInt of the two numbers read: the page's check, not the model's or the clock's */
	check: string;
	/** the table is digit for digit the adder's 200 rows */
	adder: boolean;
}

/** An LLM run: PROMPTBOX's model wrote the program and ran it (kind 'llm' of polyformer.trace/0). */
export interface LlmTrace {
	schema: 'polyformer.trace/0';
	source: string;
	id: string;
	kind: 'llm';
	title: string;
	family: string | null;
	/** produced by the live model in this session (false: a recording) */
	live: boolean;
	/** where a live run ran: Savant-4B in this browser, or the local server's GPU */
	where?: 'browser' | 'server';
	model: {
		name: string;
		compile_adapter: string;
		executor_adapter: string;
		adapter_sha256: { compile: string; executor: string };
		tokenizer_sha256: string;
		promptbox_commit: string;
		about: string;
	};
	host: {
		gpu: string | null;
		cpu: string | null;
		cpu_vendor_family_model?: string | null;
		avx512f: boolean | null;
		platform?: string | null;
		torch?: string;
		cuda?: string;
		transformers?: string;
		vllm?: string;
		/** in-browser runs: the runtime and weights' precision */
		runtime?: string;
		dtype?: string;
	};
	at: string;
	prompt: string;
	answer: string;
	final_text: string | null;
	/** why the loop stopped before the run, when it did */
	note: string | null;
	truth: string | null;
	base_answer: string | null;
	base_answer_meta: BaseAnswerMeta | null;
	compile: { text: string; tokens: number; finish: string; seconds: number };
	panels: Trace['panels'];
	input: Trace['input'] & { anchors?: [string, string] | null; error?: string | null };
	registers: LlmRegister[];
	/** number mode (ARITH_FORMAT) */
	arith?: ArithRecord;
	timing: Record<string, number> | null;
	ctx: LlmCtx | null;
	score?: {
		parsed: boolean;
		table_exact: boolean;
		tape_exact: boolean;
		certified: boolean;
		run_final_right: boolean;
		answer_correct: boolean;
		rows_wrong?: number;
		table_from?: string | null;
		/** number mode: the clock's sum is the true sum */
		sum_right?: boolean;
	};
	cost?: { container_seconds: number; wall_seconds: number; usd: number };
	provenance?: { recorded_at: string; demolive_commit: string; promptbox_commit: string };
}

export type TraceFile = Trace | LlmTrace;

export const isLlm = (f: TraceFile): f is LlmTrace =>
	'registers' in f && Array.isArray(f.registers);

const views = new WeakMap<LlmTrace, Map<number, Trace>>();

/**
 * One register of an LLM run, as the panels read a trace. Each tick reuses its certified row's attention. Views are
 * kept per run object, so an updated run (a new poke) gets new views.
 */
export function viewOf(t: LlmTrace, k: number): Trace | null {
	let byReg = views.get(t);
	if (!byReg) views.set(t, (byReg = new Map()));
	const have = byReg.get(k);
	if (have) return have;
	const made = makeView(t, k);
	if (made) byReg.set(k, made);
	return made;
}

/** The trace the chat and the panels read for a file: the file itself, or an LLM run's first register. */
export const asTrace = (f: TraceFile, k = 0): Trace | null => (isLlm(f) ? viewOf(f, k) : f);

function makeView(t: LlmTrace, k: number): Trace | null {
	const r = t.registers[Math.min(k, t.registers.length - 1)];
	if (!r) return null;
	const rows = r.program.rows;
	return {
		schema: t.schema,
		source: t.source,
		id: `${t.id}/${r.name}`,
		kind: 'llm',
		title: t.title,
		family: t.family ?? '',
		model: {
			name: t.model.name,
			commit: t.model.promptbox_commit,
			params_sha256_16: t.model.adapter_sha256.executor.slice(0, 16),
			params: '',
			heads: 0,
			about: t.model.about
		},
		host: {
			cpu: cpuName(t.host),
			machine: t.host.platform ?? '',
			avx512f: !!t.host.avx512f,
			gpu: t.host.gpu ?? 'unknown GPU',
			jax: ''
		},
		prompt: t.prompt,
		answer: t.answer,
		truth: t.truth ?? '',
		base_answer: t.base_answer,
		base_answer_meta: t.base_answer_meta,
		panels: t.panels,
		program: r.program,
		certificate: r.certificate,
		input: t.input,
		codebook: r.codebook,
		steps: r.steps.map((s) => ({ ...s, attn: (s.row >= 0 && rows[s.row]?.attn) || [] })),
		exact: r.exact,
		first_wrong_step: r.first_wrong_step,
		pokes: r.pokes,
		ablation: r.ablation,
		llm: { file: t, register: k }
	};
}

/** Live progress of one question, as the server streams it. */
export interface LiveTurn {
	stage: 'connecting' | 'compile' | 'tape' | 'certify' | 'run' | 'answer' | 'done' | 'error';
	register: string | null;
	done: number;
	total: number;
	detail: string;
	error: string | null;
	id: string | null;
	started: number;
}

/** One exchange in the chat: what was sent, the recorded run it replays (if any), and whether it was edited. */
export interface Turn {
	key: number;
	text: string;
	entry: TraceEntry | null;
	edited: boolean;
	/** set when the question ran on the live model */
	live?: LiveTurn;
	/** set when the question runs on Savant-4B in this browser: the run's id */
	browser?: string;
	/** the suggested question this was, unedited */
	prompt?: string | null;
	/** sent while the model was still loading: it runs when the model is ready */
	waiting?: boolean;
	/** the model was not loaded and the question has no recording */
	needsModel?: boolean;
}

export const int = (n: number) => n.toLocaleString('en-US');

/** A short adapter name: "s2g-s1/adapter_step750" → "s2g-s1 step 750". */
/** The host's CPU model; sandboxed hosts (gVisor) hide the name, leaving vendor, family and model numbers. */
export function cpuName(host: LlmTrace['host']): string {
	if (host.cpu && host.cpu !== 'unknown') return host.cpu;
	const [vendor, family, model] = (host.cpu_vendor_family_model ?? '').split(' ');
	return vendor && family && model ? `${vendor} family ${family} model ${model}` : 'unknown CPU';
}

export const adapterName = (path: string) => path.replace(/\/adapter_step(\d+)$/, ' step $1');

/** What one step of a run is called, from the title ("Shell game, 1,024 swaps" → "swap"). */
export const unitOf = (title: string) => (title.split(' ').at(-1) ?? 'step').replace(/s$/, '');

/** The title's name for the task, before the count ("Shell game, 1,024 swaps" → "Shell game"). */
export const taskOf = (title: string) => title.replace(/,\s*[\d,]+\s+\w+$/, '');

/** A short, quiet summary of the run for the line under the answer. */
export function runNote(t: Trace): string {
	const n = t.steps.length;
	const verdict = t.certificate.certified && t.certificate.all_ok ? 'certified' : 'not certified';
	if (t.llm) return llmNote(t.llm.file);
	if (t.kind === 'regs') {
		const lines = t.program.lines ?? t.program.states.length;
		return `ran a ${lines}-line program for ${int(n)} instructions (${int(t.regs?.lookups ?? n * 18)} lookups) · ${verdict}`;
	}
	return `ran a ${t.program.states.length}-state program over ${int(n)} events · ${verdict}`;
}

/** An LLM run in one line: the table it wrote, the ticks, the certificate, and bitwise equality. */
export function llmNote(f: LlmTrace): string {
	const regs = f.registers;
	if (!regs.length) return f.note ?? 'no run';
	const rows = regs.reduce((a, r) => a + r.program.rows.length, 0);
	const ticks = regs.reduce((a, r) => a + r.ticks.real, 0);
	const same = regs.reduce((a, r) => a + r.ticks.bitwise_equal_to_certified_row, 0);
	const looked = regs.reduce((a, r) => a + (r.ticks.lookup ?? 0), 0);
	const cert = regs.every((r) => r.certificate.all_ok) ? 'certified' : 'not certified';
	const where = regs.length > 1 ? ` in ${regs.length} registers` : '';
	const read = looked ? `, read ${int(looked)} more steps from the certified rows` : '';
	return `wrote a ${rows}-row table${where}, ran ${int(ticks)} ticks${read} · ${cert} · ${int(same)} of ${int(ticks)} ticks bitwise equal to their certified row`;
}

/** Downsampled margin trace: per bucket the smallest margin, so a dip is never averaged away. */
export function marginBuckets(steps: TraceStep[], buckets: number): { i: number; m: number }[] {
	const n = steps.length;
	if (n <= buckets) return steps.map((s) => ({ i: s.i, m: s.margin }));
	const out: { i: number; m: number }[] = [];
	for (let b = 0; b < buckets; b++) {
		const lo = Math.floor((b * n) / buckets);
		const hi = Math.max(lo + 1, Math.floor(((b + 1) * n) / buckets));
		let m = Infinity;
		let at = lo;
		for (let k = lo; k < hi; k++)
			if (steps[k].margin < m) {
				m = steps[k].margin;
				at = k;
			}
		out.push({ i: at, m });
	}
	return out;
}

/**
 * REGS memory before instruction `step`, rebuilt from the initial image and the stores. Checkpoints every
 * `every` instructions keep scrubbing cheap on runs of tens of thousands of instructions.
 */
export function memoryReader(t: Trace, every = 256) {
	const regs = t.regs;
	if (!regs) return () => [] as number[];
	const marks: number[][] = [regs.mem0.slice()];
	const mem = regs.mem0.slice();
	for (let i = 0; i < t.steps.length; i++) {
		for (const [c, v] of t.steps[i].st ?? []) mem[c] = v;
		if ((i + 1) % every === 0) marks.push(mem.slice());
	}
	return (step: number): number[] => {
		const k = Math.min(Math.floor(step / every), marks.length - 1);
		const out = marks[k].slice();
		for (let i = k * every; i < step; i++) for (const [c, v] of t.steps[i].st ?? []) out[c] = v;
		return out;
	};
}

/** The program text as shown: its lines without the wrapping tags. */
export const programLines = (text: string) =>
	text.split('\n').filter((l) => !/^<\/?program>$/.test(l.trim()));

/** The line of the program text that holds the rule for an event, for highlighting. */
export function ruleLine(lines: string[], event: string): number {
	const exact = lines.findIndex((l) => l.startsWith(`on ${event}:`));
	if (exact >= 0) return exact;
	return lines.findIndex((l) => /^on each /.test(l));
}
