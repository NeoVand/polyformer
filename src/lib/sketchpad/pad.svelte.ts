/**
 * The sketchpad from the page's side: the GPU check, which model is loaded, the download, the certificate (fresh or
 * cached for the same files), the live run on the sheet, and the chat. The page owns the sheet, which is the model's
 * only memory; the worker only reads the strips it is sent and answers.
 */
import { ADD_DOMAIN, AddSheet, addCode, addDecode, addRule } from './adder.ts';
import { hashText } from './hash.ts';
import { CERT_FORMAT, MODELS, certFiles, modelFiles, type Kind } from './models.ts';
import { MUL_DOMAIN, MulSheet, outChars, type MulOut, type Op } from './multiplier.ts';
import type { FromWorker, LoadedInfo, TickOp, ToWorker } from './protocol.ts';
import { B, GLYPHS } from './sprites.ts';

export type Sheet = AddSheet | MulSheet;

/** A table row, as the margin and the failure list show it. */
export function rowLabel(kind: Kind, i: number): string {
	const show = (g: string) => (g === B ? '_' : g);
	if (kind === 'add') {
		const v = ADD_DOMAIN[i];
		const r = addRule(v);
		const said = r === 'H' ? 'halt' : `${r[0]}${r[1] === '1' ? ', carry 1' : ''}`;
		return `ADD ${v.map(show).join(' ')} → ${addCode(r)} (${said})`;
	}
	const [op, v] = MUL_DOMAIN[i];
	return `${op} ${v.map(show).join(' ')} → ${outChars(op, v).join(' ')}`;
}

const MUL_INDEX = new Map(MUL_DOMAIN.map(([op, v], i) => [op + v.join(''), i]));

/** The table row a view is, or -1 if the view is not in the table. */
export function rowIndex(op: TickOp, cells: readonly string[]): number {
	if (op === 'ADD-FAST') {
		const c = [B, '1'].indexOf(cells[0]);
		const t = GLYPHS.indexOf(cells[1]);
		const b = GLYPHS.indexOf(cells[2]);
		return c < 0 || t < 0 || b < 0 ? -1 : c * 121 + t * 11 + b;
	}
	return MUL_INDEX.get(op + cells.join('')) ?? -1;
}

/** A margin as text, with a true minus sign. */
export const fmtMargin = (m: number) =>
	Number.isFinite(m) ? (m < 0 ? `−${(-m).toFixed(2)}` : m.toFixed(2)) : m < 0 ? '−∞' : '–';

export interface Failure {
	index: number;
	label: string;
	got: string | null;
	margin: number;
}

export class Cert {
	readonly kind: Kind;
	readonly rows: number;
	status = $state<'none' | 'running' | 'done' | 'cached'>('none');
	checked = $state(0);
	pass = $state(0);
	minMargin = $state(Infinity);
	seconds = $state(0);
	failures = $state<Failure[]>([]);
	/** when a cached certificate was made */
	when = $state<string | null>(null);
	/** bumps whenever `margins` changes (the grid redraws from it) */
	version = $state(0);
	/** NaN until a row is checked */
	margins: Float32Array;
	private t0 = 0;

	constructor(kind: Kind) {
		this.kind = kind;
		this.rows = MODELS[kind].rows;
		this.margins = new Float32Array(this.rows).fill(NaN);
	}

	reset() {
		this.margins.fill(NaN);
		this.checked = 0;
		this.pass = 0;
		this.minMargin = Infinity;
		this.seconds = 0;
		this.failures = [];
		this.when = null;
		this.status = 'none';
		this.version++;
	}

	start() {
		this.reset();
		this.status = 'running';
		this.t0 = performance.now();
	}

	add(start: number, margins: number[], got: (string | null)[]) {
		let pass = 0;
		let min = this.minMargin;
		const fails: Failure[] = [];
		margins.forEach((raw, k) => {
			const i = start + k;
			// a NaN margin is a failed row, never an unchecked one (NaN marks unchecked in `margins`)
			const m = Number.isNaN(raw) ? -Infinity : raw;
			this.margins[i] = m;
			if (m > 0) pass++;
			else fails.push({ index: i, label: rowLabel(this.kind, i), got: got[k], margin: m });
			min = Math.min(min, m);
		});
		this.checked = start + margins.length;
		this.pass += pass;
		this.minMargin = min;
		if (fails.length) this.failures = [...this.failures, ...fails];
		this.seconds = (performance.now() - this.t0) / 1000;
		this.version++;
	}

	/** every row checked and every row passed */
	get certified() {
		return (this.status === 'done' || this.status === 'cached') && this.pass === this.rows;
	}
}

interface Stored {
	key: string;
	pass: number;
	rows: number;
	minMargin: number;
	seconds: number;
	when: string;
	margins: number[];
	failures: Failure[];
}

const storeKey = (k: Kind) => `sketchpad.cert.${k}`;
function readStore(k: Kind): Stored | null {
	try {
		const s = localStorage.getItem(storeKey(k));
		return s ? (JSON.parse(s) as Stored) : null;
	} catch {
		return null;
	}
}
function writeStore(k: Kind, s: Stored) {
	try {
		localStorage.setItem(storeKey(k), JSON.stringify(s));
	} catch {
		/* private mode or full: the certificate simply is not remembered */
	}
}

export interface TickView {
	op: TickOp;
	cells: string[];
	out: string[];
	margin: number | null;
	strip: Uint8ClampedArray;
	ms: number;
}

export interface RunResult {
	ok: boolean;
	got: string;
	want: string;
	operands: [string, string];
	edits: number;
	certified: boolean;
	ticks: number;
	msPerTick: number;
	seconds: number;
	digits: number;
	/** distinct table rows this run read */
	views: number;
	/** of those, rows that did not pass on this device (or were never checked) */
	unchecked: number;
	/** the table rows behind `unchecked`, as the certificate lists them */
	uncheckedLabels: string[];
}

export interface ChatTurn {
	q: string;
	a: string;
	busy: boolean;
	ms: number | null;
	error: string | null;
}

interface Pending {
	resolve: (v: unknown) => void;
	reject: (e: Error) => void;
	onMessage?: (m: FromWorker) => void;
}

export class Cancelled extends Error {
	constructor() {
		super('stopped');
	}
}

const MUL_NEXT = 'MAZFNH';

class Pad {
	/** null while probing */
	gpuOk = $state<boolean | null>(null);
	gpuReason = $state<string | null>(null);
	/** bytes to download per model, from the server; null if unknown, 0 if the weights are not served */
	sizes = $state<Record<Kind, number | null>>({ add: null, mul: null });

	op = $state<Kind>('add');
	loaded = $state<Kind | null>(null);
	loading = $state<Kind | null>(null);
	loadStage = $state<'download' | 'compile'>('download');
	received = $state(0);
	loadError = $state<string | null>(null);
	info = $state.raw<LoadedInfo | null>(null);
	/** a cached certificate cannot be used because a file's fingerprint is missing */
	cacheNote = $state<string | null>(null);
	/** the loaded model's certificate identity (see cacheKey) */
	private certKey: string | null = null;

	certs: Record<Kind, Cert> = { add: new Cert('add'), mul: new Cert('mul') };

	sheet = $state.raw<Sheet | null>(null);
	/** bumps whenever the sheet changes */
	version = $state(0);
	running = $state(false);
	last = $state.raw<TickView | null>(null);
	ticks = $state(0);
	computeMs = $state(0);
	wallMs = $state(0);
	result = $state.raw<RunResult | null>(null);
	runError = $state<string | null>(null);

	chat = $state<ChatTurn[]>([]);

	private worker: Worker | null = null;
	private rid = 0;
	private pending = new Map<number, Pending>();
	private certRid: number | null = null;
	private stopRun = false;
	private probed = false;

	get model() {
		return MODELS[this.op];
	}

	get cert() {
		return this.certs[this.op];
	}

	get ready() {
		return this.loaded === this.op;
	}

	get chatBusy() {
		return this.chat.some((t) => t.busy);
	}

	/** GPU support and download sizes; safe to call more than once */
	async probe(base: string) {
		if (this.probed) return;
		this.probed = true;
		const gpu = typeof navigator !== 'undefined' ? navigator.gpu : undefined;
		if (!gpu) {
			this.gpuOk = false;
			this.gpuReason =
				'This browser has no WebGPU. Chrome or Edge on a desktop has it, and so does Safari 26.';
		} else {
			const a = await gpu.requestAdapter({ powerPreference: 'high-performance' }).catch(() => null);
			if (!a) {
				this.gpuOk = false;
				this.gpuReason =
					'WebGPU is here but offers no GPU (it may be switched off or blocklisted).';
			} else if (!a.features.has('shader-f16')) {
				this.gpuOk = false;
				this.gpuReason = 'This GPU has no 16-bit floats in shaders, which the vision tower needs.';
			} else this.gpuOk = true;
		}
		for (const k of ['add', 'mul'] as Kind[]) void this.size(base, k);
	}

	private async size(base: string, k: Kind) {
		const m = MODELS[k];
		try {
			const lens = await Promise.all(
				modelFiles(m).map(async (f) => {
					const r = await fetch(`${base}${m.id}/${f}`, { method: 'HEAD', cache: 'no-store' });
					if (!r.ok) throw new Error(f);
					return Number(r.headers.get('Content-Length') ?? 0);
				})
			);
			this.sizes[k] = lens.reduce((a, b) => a + b, 0);
		} catch {
			this.sizes[k] = 0;
		}
	}

	private ensureWorker() {
		if (this.worker) return this.worker;
		const w = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
		w.onmessage = (e: MessageEvent<FromWorker>) => this.receive(e.data);
		w.onerror = (e) => {
			this.loadError = e.message || 'the worker failed';
			this.loading = null;
		};
		this.worker = w;
		return w;
	}

	private send(m: ToWorker) {
		this.ensureWorker().postMessage(m);
	}

	private receive(m: FromWorker) {
		if (m.type === 'progress') {
			const vals = Object.values(m.files);
			this.received = vals.reduce((a, f) => a + f.loaded, 0);
			this.loadStage = m.stage;
			return;
		}
		if (m.type === 'loaded') return this.onLoaded(m.info);
		if (m.type === 'load-error') {
			this.loadError = m.error;
			this.loading = null;
			return;
		}
		const p = this.pending.get(m.rid);
		if (!p) return;
		if (m.type === 'failed') {
			this.pending.delete(m.rid);
			p.reject(m.cancelled ? new Cancelled() : new Error(m.error));
		} else if (m.type === 'tick' || m.type === 'cert-done' || m.type === 'done') {
			p.onMessage?.(m);
			this.pending.delete(m.rid);
			p.resolve(m);
		} else p.onMessage?.(m);
	}

	private request<T>(
		m: ToWorker & { rid: number },
		onMessage?: (m: FromWorker) => void
	): Promise<T> {
		return new Promise<T>((resolve, reject) => {
			this.pending.set(m.rid, { resolve: resolve as (v: unknown) => void, reject, onMessage });
			this.send(m);
		});
	}

	/** switch the operation; the other model is loaded only when asked for */
	setOp(k: Kind) {
		if (this.running || k === this.op) return;
		this.op = k;
		this.result = null;
		this.runError = null;
		this.last = null;
	}

	load(base: string, sprites: string) {
		const k = this.op;
		if (this.loading || this.loaded === k || this.running) return;
		if (this.certRid !== null) this.send({ type: 'cancel', rid: this.certRid });
		this.loading = k;
		this.loaded = null;
		this.received = 0;
		this.loadStage = 'download';
		this.loadError = null;
		this.send({ type: 'load', kind: k, base, sprites });
	}

	/** the certificate's identity: format, model files, sprites, GPU and runtime; null if a file went unseen */
	private cacheKey(info: LoadedInfo): string | null {
		const m = MODELS[info.kind];
		const need = certFiles(m);
		const missing = need.filter((f) => !info.prints[f]);
		if (missing.length) {
			this.cacheNote = `no fingerprint for ${missing.join(', ')}`;
			return null;
		}
		this.cacheNote = null;
		const files = need.map((f) => [f, info.prints[f]]);
		return hashText(
			JSON.stringify({
				format: CERT_FORMAT,
				model: m.id,
				dtype: m.dtype,
				files,
				sprites: info.sprites,
				gpu: info.gpu,
				transformers: info.transformers
			})
		);
	}

	private onLoaded(info: LoadedInfo) {
		this.info = info;
		this.loaded = info.kind;
		this.loading = null;
		const cert = this.certs[info.kind];
		const key = (this.certKey = this.cacheKey(info));
		const stored = key ? readStore(info.kind) : null;
		if (stored && stored.key === key && stored.rows === cert.rows) {
			cert.reset();
			stored.margins.forEach((m, i) => (cert.margins[i] = m));
			cert.checked = cert.rows;
			cert.pass = stored.pass;
			cert.minMargin = stored.minMargin;
			cert.seconds = stored.seconds;
			cert.failures = stored.failures;
			cert.when = stored.when;
			cert.status = 'cached';
			cert.version++;
		} else void this.certify();
	}

	/** check every row of the loaded model's table on this device */
	async certify() {
		const k = this.loaded;
		if (!k || this.certRid !== null) return;
		const cert = this.certs[k];
		const rid = ++this.rid;
		this.certRid = rid;
		cert.start();
		try {
			const done = await this.request<{ seconds: number }>(
				{ type: 'certify', rid, kind: k },
				(m) => {
					if (m.type === 'cert-rows') cert.add(m.start, m.margins, m.got);
				}
			);
			cert.seconds = done.seconds;
			cert.status = 'done';
			const key = this.certKey;
			if (key && this.loaded === k)
				writeStore(k, {
					key,
					pass: cert.pass,
					rows: cert.rows,
					minMargin: cert.minMargin,
					seconds: cert.seconds,
					when: new Date().toISOString(),
					margins: Array.from(cert.margins, (m) => Math.round(m * 1000) / 1000),
					failures: cert.failures
				});
		} catch (e) {
			cert.status = 'none';
			if (!(e instanceof Cancelled)) this.loadError = (e as Error).message;
		} finally {
			this.certRid = null;
		}
	}

	/** Stamp a problem on the sheet without running it (what the visitor typed). */
	stage(a: string, b: string) {
		if (this.running) return;
		const clean = (s: string) => s.replace(/\D/g, '');
		if (!clean(a) || !clean(b)) {
			this.sheet = null;
			return;
		}
		this.sheet = this.op === 'add' ? new AddSheet(a, b) : new MulSheet(a, b);
		this.result = null;
		this.runError = null;
		this.last = null;
		this.ticks = 0;
		this.computeMs = 0;
		this.wallMs = 0;
		this.version++;
	}

	private tick(op: TickOp, cells: string[]) {
		const rid = ++this.rid;
		return this.request<Extract<FromWorker, { type: 'tick' }>>({ type: 'tick', rid, op, cells });
	}

	/** Change an unread digit; the next ticks read the new one. */
	bump(row: string, x: number, by = 1) {
		const s = this.sheet;
		if (!s || s.done) return false;
		const ok =
			s instanceof AddSheet
				? (row === 'top' || row === 'bottom') && s.bump(row, x, by)
				: s.bump(row as 'b', x, by);
		if (ok) this.version++;
		return ok;
	}

	stop() {
		this.stopRun = true;
	}

	async run(a: string, b: string) {
		if (this.running || !this.ready) return;
		this.stage(a, b);
		const sheet = this.sheet;
		if (!sheet) return;
		const kind = this.op;
		const cert = this.certs[kind];
		this.running = true;
		this.stopRun = false;
		const t0 = performance.now();
		const limit = sheet instanceof AddSheet ? sheet.n + 1 : 4 * sheet.W * (sheet.m + 1) + 64;
		// every table row this run reads, and whether each passed on this device
		const read: Record<number, boolean> = {};
		try {
			for (;;) {
				if (this.stopRun) throw new Cancelled();
				if (sheet.ticks > limit) throw new Error('the run did not halt');
				const op: TickOp = sheet instanceof AddSheet ? 'ADD-FAST' : sheet.op;
				const cells = sheet.view();
				const row = rowIndex(op, cells);
				read[row] = row >= 0 && cert.margins[row] > 0;
				const r = await this.tick(op, cells);
				this.last = { op, cells, out: r.out, margin: r.margin, strip: r.strip, ms: r.ms };
				this.ticks++;
				this.computeMs += r.ms;
				this.wallMs = performance.now() - t0;
				let more: boolean;
				if (sheet instanceof AddSheet) {
					const rule = addDecode(r.out[0]);
					if (!rule)
						throw new Error(`the model wrote ${JSON.stringify(r.out[0])}, which is not an answer`);
					more = sheet.apply(rule);
				} else {
					const out = r.out as MulOut;
					const digit = (g: string) => /^\d$/.test(g);
					const stamps =
						op === 'MUL' || op === 'ADD' || op === 'ADZ'
							? [out[0], out[1]]
							: op === 'FLS'
								? [out[0]]
								: [];
					const bad = stamps.find((g) => !digit(g) && !(op === 'FLS' && g === B));
					if (bad !== undefined)
						throw new Error(`the model wrote ${JSON.stringify(bad)}, which is not a glyph`);
					if (!MUL_NEXT.includes(out[2]) || out[2].length !== 1)
						throw new Error(`the model named ${JSON.stringify(out[2])} as its next step`);
					more = sheet.apply(out);
				}
				this.version++;
				if (!more) break;
			}
			const got = sheet.result();
			const want = sheet.expected();
			this.result = {
				ok: got === want,
				got,
				want,
				operands: sheet.operands(),
				edits: sheet.edits,
				certified: cert.certified,
				ticks: sheet.ticks,
				msPerTick: this.computeMs / Math.max(1, this.ticks),
				seconds: (performance.now() - t0) / 1000,
				digits: sheet instanceof AddSheet ? sheet.n - 1 : sheet.n,
				views: Object.keys(read).length,
				unchecked: Object.values(read).filter((ok) => !ok).length,
				uncheckedLabels: Object.entries(read)
					.filter(([, ok]) => !ok)
					.map(([row]) =>
						Number(row) >= 0 ? rowLabel(kind, Number(row)) : 'a view outside the table'
					)
			};
		} catch (e) {
			this.runError = e instanceof Cancelled ? 'stopped' : (e as Error).message;
		} finally {
			this.running = false;
			this.wallMs = performance.now() - t0;
			this.version++;
		}
	}

	async ask(question: string) {
		const q = question.trim();
		if (!q || !this.loaded || this.chatBusy) return;
		const turn: ChatTurn = { q, a: '', busy: true, ms: null, error: null };
		this.chat = [...this.chat.slice(-2), turn];
		const live = this.chat[this.chat.length - 1];
		const rid = ++this.rid;
		try {
			const done = await this.request<{ ms: number }>(
				{ type: 'chat', rid, question: q, maxNew: 120 },
				(m) => {
					if (m.type === 'chat-delta') live.a += m.text;
				}
			);
			live.ms = done.ms;
		} catch (e) {
			live.error = (e as Error).message;
		} finally {
			live.busy = false;
		}
	}
}

export const pad = new Pad();

/** What one answer means, in words, for the inset. */
export function explain(op: TickOp, out: string[]): string {
	if (op === 'ADD-FAST') {
		const r = addDecode(out[0]);
		if (!r) return 'not an answer';
		if (r === 'H') return 'halt: the column and the carry are blank';
		return `sum digit ${r[0]}, ${r[1] === '1' ? 'carry 1' : 'no carry'}`;
	}
	const [g1, g2, n] = out;
	const show = (g: string) => (g === B ? 'blank' : g);
	const next: Record<string, string> = {
		M: 'MUL',
		A: 'ADD',
		Z: 'ADZ',
		F: 'FLS',
		N: 'NXT',
		H: 'halt'
	};
	const op2 = op as Op;
	if (op2 === 'MUL') return `product ${show(g1)}, carry ${g2}, then ${next[n] ?? n}`;
	if (op2 === 'ADD' || op2 === 'ADZ')
		return `result ${show(g1)}, carry ${g2}, then ${next[n] ?? n}`;
	if (op2 === 'FLS') return `last carry ${show(g1)}, then ${next[n] ?? n}`;
	return n === 'H' ? 'no digits left: halt' : 'next multiplier digit';
}
