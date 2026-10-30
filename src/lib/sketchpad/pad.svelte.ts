/**
 * The sketchpad from the page's side: the GPU check, which model is loaded, the download, the certificate (fresh or
 * cached for the same files), the live run on the sheet, and the chat. The page owns the sheet, which is the model's
 * only memory; the worker only reads the strips it is sent and answers.
 */
import { ADD_DOMAIN, AddSheet, addCode, addDecode, addRule } from './adder.ts';
import { hashText } from './hash.ts';
import {
	CERT_FORMAT,
	DTYPE,
	FILE_CACHE,
	MODELS,
	certFiles,
	modelFiles,
	servedPath,
	type Kind
} from './models.ts';
import { MUL_DOMAIN, MulSheet, MulWave, outChars, type MulOut, type Op } from './multiplier.ts';
import type { InsideTick } from './inside.ts';
import type { FromWorker, InsideMeta, LoadedInfo, TickOp, ToWorker } from './protocol.ts';
import { B, GLYPHS } from './sprites.ts';

export type Sheet = AddSheet | MulSheet | MulWave;

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
	/**
	 * none, running a full check, done (every row checked on this device now), cached (every row checked on this device
	 * earlier), shipped (the table measured on the reference device and shipped with the model; see `spot`)
	 */
	status = $state<'none' | 'running' | 'done' | 'cached' | 'shipped'>('none');
	/** where a shipped certificate was measured */
	shippedFrom = $state<{ device: string; when: string } | null>(null);
	/** the shipped table's weakest rows, checked again on this device */
	spot = $state<{
		rows: number;
		checked: number;
		pass: number;
		min: number;
		running: boolean;
		when: string | null;
	} | null>(null);
	checked = $state(0);
	pass = $state(0);
	minMargin = $state(Infinity);
	seconds = $state(0);
	failures = $state<Failure[]>([]);
	/** when a cached certificate was made */
	when = $state<string | null>(null);
	/** the files, runtime and device this certificate is about (see Pad.keyFor) */
	key = $state<string | null>(null);
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
		this.key = null;
		this.status = 'none';
		this.shippedFrom = null;
		this.spot = null;
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

	/** device margins for some rows of a shipped table (the spot check) */
	addSpot(indices: number[], margins: number[]) {
		const sp = this.spot;
		if (!sp) return;
		let pass = 0;
		let min = sp.min;
		margins.forEach((raw, k) => {
			const m = Number.isNaN(raw) ? -Infinity : raw;
			this.margins[indices[k]] = m;
			if (m > 0) pass++;
			else
				this.failures = [
					...this.failures,
					{ index: indices[k], label: rowLabel(this.kind, indices[k]), got: null, margin: m }
				];
			min = Math.min(min, m);
		});
		this.spot = { ...sp, checked: sp.checked + margins.length, pass: sp.pass + pass, min };
		this.pass = this.margins.reduce((n, m) => n + (m > 0 ? 1 : 0), 0);
		this.minMargin = Math.min(...this.margins);
		this.version++;
	}

	/** every row checked on this device and passed; or the shipped table, with no failure in its spot check here */
	get certified() {
		if (this.status === 'shipped')
			return this.pass === this.rows && !!this.spot && this.spot.pass === this.spot.checked;
		return (this.status === 'done' || this.status === 'cached') && this.pass === this.rows;
	}
}

/**
 * A certificate shipped with a program: every table row measured on a reference device (research/sketch, made with
 * `sketchpad.exportCertificate()` on the dev page), valid wherever the files, prompts, runtime and strips are the same.
 * Margins move a little between GPUs, so a new device checks the shipped table's weakest rows again (`SPOT`).
 */
export interface ShippedCert {
	format: string;
	program: string;
	dtype: Record<string, string>;
	transformers: string;
	sprites: string;
	files: Record<string, string>;
	device: string;
	when: string;
	kinds: Partial<
		Record<Kind, { prompts: Record<string, string>; rows: number; pass: number; margins: number[] }>
	>;
}
/** the share of a shipped table's rows, weakest first, that a new device checks again */
const SPOT = 0.1;

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
const spotKey = (k: Kind) => `sketchpad.spot.${k}`;
interface StoredSpot {
	key: string;
	when: string;
	indices: number[];
	margins: number[];
}
function readSpot(k: Kind): StoredSpot | null {
	try {
		const s = localStorage.getItem(spotKey(k));
		return s ? (JSON.parse(s) as StoredSpot) : null;
	} catch {
		return null;
	}
}
function writeSpot(k: Kind, s: StoredSpot) {
	try {
		localStorage.setItem(spotKey(k), JSON.stringify(s));
	} catch {
		/* not remembered: the next visit checks again */
	}
}
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
	/** the model's states on this tick: the lens and the path (null when the program has no inside data) */
	inside: InsideTick | null;
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
	/** ticks on which the visitor pushed the model's state */
	pushes: number;
	/** batched steps, when the multiplier's passes ran overlapped (null: one tick at a time) */
	steps: number | null;
	/** the certificate behind `certified`: every row checked here, or the shipped table spot-checked here */
	certSource: 'device' | 'shipped';
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
	/** bytes a load of each operation would take from the network now (what this browser has cached is free) */
	costs = $state<Record<Kind, number | null>>({ add: null, mul: null });
	/** whether the server has each operation's files (null until known) */
	available = $state<Record<Kind, boolean | null>>({ add: null, mul: null });

	op = $state<Kind>('add');
	/** the program the worker holds, as far as the page knows (null while a load replaces it) */
	loadedId = $state<string | null>(null);
	/** the operation whose load is in flight (the newest one asked for) */
	loading = $state<Kind | null>(null);
	loadStage = $state<'fetch' | 'compile'>('fetch');
	/** bytes of the load in flight: from the network, and read from this browser's cache */
	received = $state(0);
	readFromCache = $state(0);
	/** what the load in flight is expected to download, and which operation it is for */
	expect = $state<number | null>(null);
	progressKind = $state<Kind | null>(null);
	loadError = $state<string | null>(null);
	/** the newest load that read or downloaded something (not one that found the program already loaded) */
	lastLoad = $state.raw<LoadedInfo | null>(null);
	/** a certificate cannot be cached because a file's fingerprint is missing */
	cacheNote = $state<string | null>(null);

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

	/** the loaded program's inside data, for the maps (null without one) */
	insideMeta = $state.raw<InsideMeta | null>(null);
	/** an adder answer code to push the next tick toward; one tick only */
	push = $state<string | null>(null);
	/** pause between ticks in ms, so the inside can be watched (0: as fast as the GPU goes) */
	pace = $state(0);
	pushes = $state(0);
	/** run the multiplier's passes overlapped, as a wave of batched steps */
	parallel = $state(true);
	/** the table rows this run has read, and the one it read last (-1 before the first tick) */
	walk = $state.raw<{ current: number; visited: Set<number> }>({ current: -1, visited: new Set() });

	private worker: Worker | null = null;
	private rid = 0;
	private lid = 0;
	/** the newest load asked for */
	private latest: { lid: number; kind: Kind; id: string } | null = null;
	/** what each loaded program reported (fingerprints), by program id */
	private infos: Record<string, LoadedInfo> = {};
	private pending = new Map<number, Pending>();
	private certRun: Promise<void> | null = null;
	private certRid: number | null = null;
	/** certificates shipped with programs, by program id */
	private shipped = new Map<string, Promise<ShippedCert | null>>();
	private certKind: Kind | null = null;
	private stopRun = false;
	private runDone: Promise<void> = Promise.resolve();
	private switchToken = 0;
	private root = '';
	private sizeOf = new Map<string, Promise<number | null>>();

	get model() {
		return MODELS[this.op];
	}

	get cert() {
		return this.certs[this.op];
	}

	/** the operation's program is loaded and nothing is replacing it */
	get ready() {
		return this.loadedId === MODELS[this.op].id && !this.loading;
	}

	/** the operation's table passed in full, on this device, for the files loaded now */
	get certified() {
		const c = this.cert;
		return this.ready && c.certified && c.key !== null && c.key === this.keyFor(this.op);
	}

	get canRun() {
		return this.certified && !this.running && !!this.sheet;
	}

	get chatBusy() {
		return this.chat.some((t) => t.busy);
	}

	get chatReady() {
		return !!this.loadedId && !this.loading;
	}

	/** GPU support and download costs; safe to call more than once */
	async probe(root: string) {
		if (this.root) return;
		this.root = root;
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
		await this.refreshCosts();
	}

	/** a served file's size, asked once */
	private size(url: string) {
		let p = this.sizeOf.get(url);
		if (!p) {
			p = fetch(url, { method: 'HEAD', cache: 'no-store' })
				.then((r) => (r.ok ? Number(r.headers.get('Content-Length') ?? 0) : null))
				.catch(() => null);
			this.sizeOf.set(url, p);
		}
		return p;
	}

	/** what loading each operation would download now: its files' sizes, less what this browser has cached */
	async refreshCosts() {
		if (!this.root) return;
		const cache =
			typeof caches !== 'undefined' ? await caches.open(FILE_CACHE).catch(() => null) : null;
		for (const k of ['add', 'mul'] as Kind[]) {
			const m = MODELS[k];
			let cost = 0;
			let ok = true;
			await Promise.all(
				modelFiles().map(async (f) => {
					const url = this.root + servedPath(m, f);
					const n = await this.size(url);
					if (n === null) ok = false;
					else if (!(cache && (await cache.match(url)))) cost += n;
				})
			);
			this.available[k] = ok;
			this.costs[k] = ok ? cost : null;
		}
	}

	private ensureWorker() {
		if (this.worker) return this.worker;
		const w = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
		w.onmessage = (e: MessageEvent<FromWorker>) => this.receive(e.data);
		w.onerror = (e) => {
			this.loadError = e.message || 'the worker failed';
			this.loading = null;
			this.loadedId = null;
		};
		this.worker = w;
		return w;
	}

	private send(m: ToWorker) {
		this.ensureWorker().postMessage(m);
	}

	private receive(m: FromWorker) {
		if (m.type === 'progress') {
			// an older load may still be running ahead of the newest; its bytes are real, so show them as its own
			if (!this.loading) return;
			this.progressKind = m.kind;
			this.received = m.network;
			this.expect = m.expect;
			this.readFromCache = m.cached;
			this.loadStage = m.stage;
			return;
		}
		if (m.type === 'loaded') return this.onLoaded(m.lid, m.info);
		if (m.type === 'load-skipped') return;
		if (m.type === 'load-error') {
			if (m.lid !== this.latest?.lid) return;
			this.loadError = m.error;
			this.loading = null;
			this.loadedId = null;
			return;
		}
		const p = this.pending.get(m.rid);
		if (!p) return;
		if (m.type === 'failed') {
			this.pending.delete(m.rid);
			p.reject(m.cancelled ? new Cancelled() : new Error(m.error));
		} else if (
			m.type === 'tick' ||
			m.type === 'tick-batch' ||
			m.type === 'cert-done' ||
			m.type === 'done'
		) {
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

	/**
	 * Switch the operation. A run in progress is stopped first; the newest switch wins. The other program loads only
	 * when asked for (unless one program serves both operations).
	 */
	async setOp(k: Kind) {
		const token = ++this.switchToken;
		if (this.running) {
			this.stop();
			await this.runDone;
		}
		if (token !== this.switchToken || k === this.op) return;
		this.op = k;
		this.result = null;
		this.runError = null;
		this.last = null;
		if (this.ready) void this.ensureCert(k);
	}

	load(root: string, sprites: string) {
		const k = this.op;
		const id = MODELS[k].id;
		if (this.running) return;
		if (this.loadedId === id && !this.loading) return void this.ensureCert(k);
		if (this.loading && this.latest?.id === id) return;
		// a certificate of the program being replaced would be cancelled by the worker anyway; say so now
		if (this.certRid !== null && this.certKind && MODELS[this.certKind].id !== id)
			this.send({ type: 'cancel', rid: this.certRid });
		const lid = ++this.lid;
		this.latest = { lid, kind: k, id };
		if (this.loadedId !== id) this.loadedId = null;
		this.loading = k;
		this.received = 0;
		this.readFromCache = 0;
		this.loadStage = 'fetch';
		this.loadError = null;
		this.expect = this.costs[k];
		this.progressKind = k;
		this.send({ type: 'load', lid, kind: k, root, sprites });
	}

	private onLoaded(lid: number, info: LoadedInfo) {
		this.infos[info.id] = info;
		// an older load finished; the newest one is still queued behind it and will replace or reuse it
		if (lid !== this.latest?.lid) return;
		this.loadedId = info.id;
		this.loading = null;
		this.insideMeta = info.inside;
		if (!info.reused) this.lastLoad = info;
		void this.refreshCosts();
		void this.ensureCert(this.latest.kind);
		if (this.op !== this.latest.kind) void this.ensureCert(this.op);
	}

	/**
	 * The certificate's identity: format, operation, prompts, the program's files, sprites, GPU and runtime. Without a
	 * fingerprint for every file it is bound to this load only (and never cached).
	 */
	private keyFor(k: Kind): string | null {
		const m = MODELS[k];
		const info = this.infos[m.id];
		if (!info || this.loadedId !== m.id) return null;
		const need = certFiles();
		const missing = need.filter((f) => !info.prints[f]);
		this.cacheNote = missing.length ? `no fingerprint for ${missing.join(', ')}` : null;
		if (missing.length) return `session:${m.id}:${this.latest?.lid}`;
		return hashText(
			JSON.stringify({
				format: CERT_FORMAT,
				kind: k,
				program: m.id,
				prompts: m.prompts,
				dtype: DTYPE,
				files: need.map((f) => [servedPath(m, f), info.prints[f]]),
				sprites: info.sprites,
				gpu: info.gpu,
				transformers: info.transformers
			})
		);
	}

	/** the certificate shipped with a program, fetched once (null when it has none) */
	private shippedFor(id: string) {
		let p = this.shipped.get(id);
		if (!p) {
			p = fetch(`${this.root}${id}/certificate.json`, { cache: 'no-cache' })
				.then((r) => (r.ok ? (r.json() as Promise<ShippedCert>) : null))
				.catch(() => null);
			this.shipped.set(id, p);
		}
		return p;
	}

	/** the shipped table for this operation, if it was measured on exactly the files, prompts and runtime loaded now */
	private shippedTable(k: Kind, sc: ShippedCert) {
		const m = MODELS[k];
		const info = this.infos[m.id];
		const t = sc.kinds[k];
		if (!info || !t || t.rows !== this.certs[k].rows || t.margins.length !== t.rows) return null;
		const same =
			sc.format === CERT_FORMAT &&
			sc.program === m.id &&
			sc.transformers === info.transformers &&
			sc.sprites === info.sprites &&
			JSON.stringify(sc.dtype) === JSON.stringify(DTYPE) &&
			JSON.stringify(t.prompts) === JSON.stringify(m.prompts) &&
			certFiles().every((f) => !!info.prints[f] && sc.files[f] === info.prints[f]);
		return same ? t : null;
	}

	/** take the shipped table, then check its weakest rows on this device (or recall that check) */
	private useShipped(
		k: Kind,
		sc: ShippedCert,
		t: NonNullable<ShippedCert['kinds'][Kind]>,
		key: string | null
	) {
		const cert = this.certs[k];
		cert.reset();
		t.margins.forEach((x, i) => (cert.margins[i] = x));
		cert.checked = cert.rows;
		cert.pass = t.margins.filter((x) => x > 0).length;
		cert.minMargin = Math.min(...t.margins);
		cert.failures = t.margins.flatMap((x, i) =>
			x > 0 ? [] : [{ index: i, label: rowLabel(k, i), got: null, margin: x }]
		);
		cert.shippedFrom = { device: sc.device, when: sc.when };
		cert.key = key;
		cert.status = 'shipped';
		const order = t.margins.map((x, i) => [x, i]).sort((a, b) => a[0] - b[0]);
		const indices = order.slice(0, Math.ceil(cert.rows * SPOT)).map(([, i]) => i);
		cert.spot = {
			rows: indices.length,
			checked: 0,
			pass: 0,
			min: Infinity,
			running: false,
			when: null
		};
		const kept = key && !key.startsWith('session:') ? readSpot(k) : null;
		if (kept && kept.key === key && kept.indices.length === indices.length) {
			cert.addSpot(kept.indices, kept.margins);
			cert.spot = { ...cert.spot, when: kept.when };
			return;
		}
		cert.version++;
		void this.spotCheck(k, indices, key);
	}

	private async spotCheck(k: Kind, indices: number[], key: string | null) {
		const cert = this.certs[k];
		if (this.certRid !== null) {
			if (this.certKind === k) return;
			this.send({ type: 'cancel', rid: this.certRid });
		}
		const rid = ++this.rid;
		this.certRid = rid;
		this.certKind = k;
		if (cert.spot) cert.spot = { ...cert.spot, running: true };
		try {
			await this.request<{ seconds: number }>(
				{ type: 'certify', rid, kind: k, rows: indices },
				(msg) => {
					if (msg.type === 'cert-rows' && msg.indices) cert.addSpot(msg.indices, msg.margins);
				}
			);
			const when = new Date().toISOString();
			if (cert.spot) cert.spot = { ...cert.spot, running: false, when };
			if (key && !key.startsWith('session:'))
				writeSpot(k, {
					key,
					when,
					indices,
					margins: indices.map((i) => Math.round(cert.margins[i] * 1000) / 1000)
				});
		} catch (e) {
			// a spot check that stopped part way proves nothing: the next look at this operation starts it again
			cert.reset();
			if (!(e instanceof Cancelled)) this.loadError = (e as Error).message;
		} finally {
			if (this.certRid === rid) {
				this.certRid = null;
				this.certKind = null;
			}
		}
	}

	/**
	 * The certificate to ship with the loaded program: every operation whose table passed in full on this device for
	 * the files loaded now (dev page: `sketchpad.exportCertificate()`, saved as `<program>/certificate.json`).
	 */
	exportCertificate(): ShippedCert | null {
		const id = this.loadedId;
		const info = id ? this.infos[id] : null;
		if (!id || !info) return null;
		const kinds: ShippedCert['kinds'] = {};
		const whens: string[] = [];
		for (const k of ['add', 'mul'] as Kind[]) {
			const c = this.certs[k];
			if (MODELS[k].id !== id || c.key !== this.keyFor(k)) continue;
			if (!(c.status === 'done' || c.status === 'cached') || c.pass !== c.rows) continue;
			whens.push(c.when ?? new Date().toISOString());
			kinds[k] = {
				prompts: { ...MODELS[k].prompts } as Record<string, string>,
				rows: c.rows,
				pass: c.pass,
				margins: Array.from(c.margins, (x) => Math.round(x * 1000) / 1000)
			};
		}
		return {
			format: CERT_FORMAT,
			program: id,
			dtype: { ...DTYPE },
			transformers: info.transformers,
			sprites: info.sprites,
			files: Object.fromEntries(certFiles().map((f) => [f, info.prints[f]])),
			device: info.gpu,
			// the oldest of the checks it ships
			when: whens.sort()[0] ?? new Date().toISOString(),
			kinds
		};
	}

	/**
	 * make sure the operation's certificate is there: kept from this session, checked on this device earlier, shipped
	 * with the model (spot-checked here), or checked in full now
	 */
	private async ensureCert(k: Kind) {
		const m = MODELS[k];
		if (this.loadedId !== m.id) return;
		const key = this.keyFor(k);
		const cert = this.certs[k];
		const settled = ['done', 'cached', 'shipped'].includes(cert.status);
		if (key && cert.key === key && settled) return;
		if (this.certRid !== null && this.certKind === k) return;
		const stored = key && !key.startsWith('session:') ? readStore(k) : null;
		if (stored && stored.key === key && stored.rows === cert.rows) {
			cert.reset();
			stored.margins.forEach((x, i) => (cert.margins[i] = x));
			cert.checked = cert.rows;
			cert.pass = stored.pass;
			cert.minMargin = stored.minMargin;
			cert.seconds = stored.seconds;
			cert.failures = stored.failures;
			cert.when = stored.when;
			cert.key = key;
			cert.status = 'cached';
			cert.version++;
			return;
		}
		const sc = await this.shippedFor(m.id);
		// the program changed, or another call settled this certificate, while the shipped one was fetched
		if (this.loadedId !== m.id || (cert.key === key && cert.status !== 'none')) return;
		if (this.certRid !== null && this.certKind === k) return;
		const t = sc && this.shippedTable(k, sc);
		if (sc && t) return this.useShipped(k, sc, t, key);
		void this.certify(k);
	}

	/** check every row of an operation's table on this device (again, if asked) */
	async certify(k: Kind = this.op) {
		const m = MODELS[k];
		if (this.loadedId !== m.id || this.loading) return;
		if (this.certRid !== null) {
			if (this.certKind === k) return;
			// one table at a time: the other operation's check stops and runs again when it is shown
			this.send({ type: 'cancel', rid: this.certRid });
		}
		const key = this.keyFor(k);
		const cert = this.certs[k];
		const rid = ++this.rid;
		this.certRid = rid;
		this.certKind = k;
		let settle = () => {};
		this.certRun = new Promise((r) => (settle = r));
		cert.start();
		cert.key = key;
		try {
			const done = await this.request<{ seconds: number }>(
				{ type: 'certify', rid, kind: k },
				(msg) => {
					if (msg.type === 'cert-rows') cert.add(msg.start, msg.margins, msg.got);
				}
			);
			cert.seconds = done.seconds;
			cert.status = 'done';
			if (key && !key.startsWith('session:'))
				writeStore(k, {
					key,
					pass: cert.pass,
					rows: cert.rows,
					minMargin: cert.minMargin,
					seconds: cert.seconds,
					when: new Date().toISOString(),
					margins: Array.from(cert.margins, (x) => Math.round(x * 1000) / 1000),
					failures: cert.failures
				});
		} catch (e) {
			// a check that stopped part way certifies nothing
			cert.reset();
			if (!(e instanceof Cancelled)) this.loadError = (e as Error).message;
		} finally {
			if (this.certRid === rid) {
				this.certRid = null;
				this.certKind = null;
			}
			settle();
		}
	}

	/** resolves when the table check under way (if any) ends, passed or not */
	certSettled(): Promise<void> {
		return this.certRun ?? Promise.resolve();
	}

	/** Stamp a problem on the sheet without running it (what the visitor typed). */
	stage(a: string, b: string) {
		if (this.running) return;
		const clean = (s: string) => s.replace(/\D/g, '');
		if (!clean(a) || !clean(b)) {
			this.sheet = null;
			return;
		}
		this.sheet =
			this.op === 'add'
				? new AddSheet(a, b)
				: this.parallel
					? new MulWave(a, b)
					: new MulSheet(a, b);
		this.result = null;
		this.runError = null;
		this.last = null;
		this.ticks = 0;
		this.pushes = 0;
		this.walk = { current: -1, visited: new Set() };
		this.computeMs = 0;
		this.wallMs = 0;
		this.version++;
	}

	private tick(op: TickOp, cells: string[], push: string | null) {
		const rid = ++this.rid;
		return this.request<Extract<FromWorker, { type: 'tick' }>>({
			type: 'tick',
			rid,
			op,
			cells,
			push
		});
	}

	/** wait between ticks; a stop cuts it short */
	private async rest(ms: number) {
		const end = performance.now() + ms;
		while (!this.stopRun && performance.now() < end)
			await new Promise((r) => setTimeout(r, Math.min(50, end - performance.now())));
	}

	/** several multiplier views in one batched generation (the wave schedule; also the dev page's benchmark) */
	tickBatch(items: { op: TickOp; cells: string[] }[]) {
		const rid = ++this.rid;
		return this.request<Extract<FromWorker, { type: 'tick-batch' }>>({
			type: 'tick-batch',
			rid,
			items
		});
	}

	/** Change an unread digit; the next ticks read the new one. */
	bump(row: string, x: number, by = 1) {
		const s = this.sheet;
		if (!s || s.done || !this.running) return false;
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

	/** a multiplier answer must be glyphs and a step name; anything else stops the run */
	private checkMul(op: TickOp, out: MulOut) {
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
	}

	/** one table row read: on the walk, and in the run's record of rows and whether each passed here */
	private noteRead(op: TickOp, cells: string[], read: Record<number, boolean>, cert: Cert) {
		const row = rowIndex(op, cells);
		read[row] = row >= 0 && cert.margins[row] > 0;
		return row;
	}

	/**
	 * The multiplier as a wave: every pass under way takes its step together, in one batch (a slotted program; otherwise
	 * one per step word length, ADD being one token and the other words two, since a generated batch must not pad),
	 * every view is read before any answer is applied, and the inside panels follow the leading pass.
	 */
	private async runWave(w: MulWave, cert: Cert, read: Record<number, boolean>, t0: number) {
		const limit = 6 * w.m + 2 * w.n + 64;
		while (!w.done) {
			if (this.stopRun) throw new Cancelled();
			if (w.steps > limit) throw new Error('the run did not halt');
			const act = w.active();
			const views = act.map((q) => ({ op: q.op as TickOp, cells: w.view(q) }));
			const rows = views.map((v) => this.noteRead(v.op, v.cells, read, cert));
			// eslint-disable-next-line svelte/prefer-svelte-reactivity
			const visited = new Set(this.walk.visited);
			rows.forEach((r) => r >= 0 && visited.add(r));
			this.walk = { current: rows[0] ?? -1, visited };
			const outs: MulOut[] = new Array(act.length);
			const strips: Uint8ClampedArray[] = new Array(act.length);
			const seen: (InsideTick | null)[] = new Array(act.length);
			let ms = 0;
			// a slotted program pads every step's prompt to one length: one batch; otherwise one per step word length
			const groups = MODELS.mul.slots ? [null] : [true, false];
			for (const short of groups) {
				const idx = act
					.map((q, i) => i)
					.filter((i) => short === null || (act[i].op === 'ADD') === short);
				if (!idx.length) continue;
				const r = await this.tickBatch(idx.map((i) => views[i]));
				idx.forEach((i, k) => {
					outs[i] = r.outs[k] as MulOut;
					strips[i] = r.strips[k];
					seen[i] = r.inside[k];
				});
				ms += r.ms;
			}
			act.forEach((q, i) => this.checkMul(views[i].op, outs[i]));
			act.forEach((q, i) => w.apply(q, outs[i]));
			w.endStep();
			this.last = {
				op: views[0].op,
				cells: views[0].cells,
				out: outs[0],
				margin: null,
				strip: strips[0],
				ms,
				inside: seen[0]
			};
			this.ticks += act.length;
			this.computeMs += ms;
			this.wallMs = performance.now() - t0;
			this.version++;
			if (!w.done && this.pace > 0) await this.rest(this.pace);
		}
	}

	async run(a: string, b: string) {
		if (this.running || !this.certified) return;
		this.stage(a, b);
		const sheet = this.sheet;
		if (!sheet) return;
		const kind = this.op;
		const cert = this.certs[kind];
		let finish = () => {};
		this.runDone = new Promise((r) => (finish = r));
		this.running = true;
		this.stopRun = false;
		const t0 = performance.now();
		// every table row this run reads, and whether each passed on this device
		const read: Record<number, boolean> = {};
		try {
			if (sheet instanceof MulWave) await this.runWave(sheet, cert, read, t0);
			else
				for (;;) {
					const limit = sheet instanceof AddSheet ? sheet.n + 1 : 4 * sheet.W * (sheet.m + 1) + 64;
					if (this.stopRun) throw new Cancelled();
					if (sheet.ticks > limit) throw new Error('the run did not halt');
					const op: TickOp = sheet instanceof AddSheet ? 'ADD-FAST' : sheet.op;
					const cells = sheet.view();
					const row = this.noteRead(op, cells, read, cert);
					// the walk is replaced whole on every tick ($state.raw), never changed in place
					// eslint-disable-next-line svelte/prefer-svelte-reactivity
					if (row >= 0) this.walk = { current: row, visited: new Set(this.walk.visited).add(row) };
					const push = op === 'ADD-FAST' ? this.push : null;
					this.push = null;
					const r = await this.tick(op, cells, push);
					if (r.inside?.pushed) this.pushes++;
					this.last = {
						op,
						cells,
						out: r.out,
						margin: r.margin,
						strip: r.strip,
						ms: r.ms,
						inside: r.inside
					};
					this.ticks++;
					this.computeMs += r.ms;
					this.wallMs = performance.now() - t0;
					let more: boolean;
					if (sheet instanceof AddSheet) {
						const rule = addDecode(r.out[0]);
						if (!rule)
							throw new Error(
								`the model wrote ${JSON.stringify(r.out[0])}, which is not an answer`
							);
						more = sheet.apply(rule);
					} else {
						const out = r.out as MulOut;
						this.checkMul(op, out);
						more = sheet.apply(out);
					}
					this.version++;
					if (!more) break;
					if (this.pace > 0) await this.rest(this.pace);
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
					),
				pushes: this.pushes,
				certSource: cert.status === 'shipped' ? 'shipped' : 'device',
				steps: sheet instanceof MulWave ? sheet.steps : null
			};
		} catch (e) {
			this.runError = e instanceof Cancelled ? 'stopped' : (e as Error).message;
		} finally {
			this.running = false;
			this.wallMs = performance.now() - t0;
			this.version++;
			finish();
		}
	}

	async ask(question: string) {
		const q = question.trim();
		if (!q || !this.chatReady || this.chatBusy) return;
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
