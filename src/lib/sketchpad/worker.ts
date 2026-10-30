/// <reference lib="webworker" />
/**
 * The worker that holds the sketchpad model. The page owns the sheet (the model's only memory); the worker owns the
 * model's eyes and hands: it assembles each strip from the training sprites, runs one forward (or three greedy tokens),
 * and posts the answer back. It also checks the whole table for the certificate and answers chat questions. One GPU
 * job runs at a time; loads, certificate rows, ticks and chat take turns.
 *
 * Files: every program asks for `<root><program>/<file>`; base files are routed to one shared folder and kept in the
 * browser's Cache API under the URL they came from, so the base downloads once and a switch fetches only the program's
 * own graph. Each cached copy carries the fingerprint of the bytes that were downloaded, for the certificate cache.
 */
import { ADD_DOMAIN, addCode, addRule } from './adder.ts';
import { StreamHash, hashBytes } from './hash.ts';
import {
	DTYPE,
	FILE_CACHE,
	MODELS,
	kindOf,
	modelFiles,
	promptFor,
	route,
	servedPath,
	type Kind,
	type SketchModel
} from './models.ts';
import { analyse, parseAssets, steerVector, type InsideAssets } from './inside.ts';
import { MUL_DOMAIN, outChars, type Op } from './multiplier.ts';
import type { FromWorker, InsideMeta, LoadedInfo, TickOp, ToWorker } from './protocol.ts';
import { B, CELL, assembleStrip, type SpriteSheet } from './sprites.ts';

declare const self: DedicatedWorkerGlobalScope;

/**
 * transformers.js 4.2.0, pinned for this page (package alias `transformers-420`). The rest of the site runs 4.3.1;
 * 4.3.1 bundles ONNX Runtime Web 1.31 instead of 1.26, whose kernels move the logits slightly (the adder's lowest
 * margin 1.46 instead of 1.40), so the page keeps the runtime its tables were verified on.
 */
type Tjs = typeof import('transformers-420');

interface TTensor {
	type: string;
	dims: number[];
	data: ArrayLike<number | bigint> & Iterable<number | bigint>;
}
type Inputs = Record<string, TTensor | unknown>;
interface Tok {
	encode(s: string, o?: { add_special_tokens?: boolean }): number[];
	decode(ids: number[], o?: { skip_special_tokens?: boolean }): string;
}
interface Processor {
	(text: string | string[], images?: unknown[]): Promise<Inputs>;
	tokenizer: Tok;
	apply_chat_template(messages: unknown[], o: Record<string, unknown>): string;
}
interface Model {
	(inputs: Inputs): Promise<{ logits: TTensor }>;
	generate(o: Record<string, unknown>): Promise<TTensor>;
	dispose(): Promise<unknown>;
}

const post = (m: FromWorker, transfer: Transferable[] = []) => self.postMessage(m, transfer);
const message = (e: unknown) => (e instanceof Error ? e.message : String(e));

class Cancelled extends Error {
	constructor() {
		super('cancelled');
	}
}

let tjs: Tjs | null = null;
let processor: Processor | null = null;
let model: Model | null = null;
let tok: Tok | null = null;
/** the loaded program's inside data (null for a program whose graph has no hidden_states output) */
let inside: InsideAssets | null = null;
let insideMeta: InsideMeta | null = null;
/** while on, every decoder call's states at its last position are kept, one entry per call */
let capturing = false;
/** per decoder call, per batch row, the states at its last `captureLast` positions */
let captured: Float32Array[][][] = [];
let captureLast = 1;
/** a push for the next decoder call that reads a whole prompt (the tick's first call) */
let steerNext: Float32Array | null = null;
/** the program loaded now, and a counter that moves whenever the loaded model changes */
let loadedId: string | null = null;
let generation = 0;
/** the newest load the page asked for; an older one still queued is skipped */
let wanted = 0;
let sprites: SpriteSheet | null = null;
let spritesPrint = '';
let gpu = '';
/** fingerprints of model files, by served path below the models folder */
const prints = new Map<string, string>();
const cancelled = new Set<number>();
/** bytes of the current load: from the network (by served path) and from the cache */
let network: Record<string, number> = {};
let cachedBytes = 0;
let onBytes: () => void = () => {};
const PRINT_HEADER = 'x-sketchpad-print';

/** one GPU job at a time */
let chain: Promise<unknown> = Promise.resolve();
function exclusive<T>(fn: () => Promise<T>): Promise<T> {
	const run = chain.then(fn, fn);
	chain = run.catch(() => {});
	return run;
}

const urlOf = (input: RequestInfo | URL) =>
	typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;

/**
 * fetch for transformers.js: routes base files to the shared folder, and fingerprints and counts every whole-file
 * download as it streams past
 */
function routedFetch(root: string) {
	return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
		const url = route(urlOf(input), root);
		if (!url) return fetch(input, init);
		const res = await fetch(url, init);
		const ranged = new Headers(init?.headers).has('Range');
		if (res.status !== 200 || ranged || !res.body) return res;
		const name = url.slice(root.length);
		const h = new StreamHash();
		network[name] = 0;
		const body = res.body.pipeThrough(
			new TransformStream<Uint8Array, Uint8Array>({
				transform(chunk, ctl) {
					h.update(chunk);
					network[name] += chunk.length;
					onBytes();
					ctl.enqueue(chunk);
				},
				flush() {
					prints.set(name, h.digest());
				}
			})
		);
		return new Response(body, {
			status: res.status,
			statusText: res.statusText,
			headers: res.headers
		});
	};
}

/**
 * transformers.js's custom cache: the Cache API under the served URL, so every program shares the base's copy. A hit
 * restores the fingerprint stored with it.
 */
function fileCache(root: string) {
	const open = () => caches.open(FILE_CACHE);
	return {
		async match(key: RequestInfo | URL) {
			const url = route(urlOf(key), root);
			if (!url) return undefined;
			const hit = await (await open()).match(url);
			if (!hit) return undefined;
			const print = hit.headers.get(PRINT_HEADER);
			if (print) prints.set(url.slice(root.length), print);
			cachedBytes += Number(hit.headers.get('content-length') ?? 0);
			onBytes();
			return hit;
		},
		async put(key: RequestInfo | URL, response: Response) {
			const url = route(urlOf(key), root);
			if (!url) return;
			const headers = new Headers(response.headers);
			const print = prints.get(url.slice(root.length));
			if (print) headers.set(PRINT_HEADER, print);
			await (await open()).put(url, new Response(response.body, { status: 200, headers }));
		}
	};
}

/**
 * Drop cached files the server has since replaced (a new export under the same name): compare length, Last-Modified
 * and ETag with a HEAD. Offline, the cached copies stand.
 */
async function dropStale(m: SketchModel, root: string) {
	const cache = await caches.open(FILE_CACHE);
	await Promise.all(
		modelFiles().map(async (f) => {
			const url = root + servedPath(m, f);
			const hit = await cache.match(url);
			if (!hit) return;
			const head = await fetch(url, { method: 'HEAD', cache: 'no-store' }).catch(() => null);
			if (!head?.ok) return;
			const same = (k: string) => {
				const a = head.headers.get(k);
				return !a || a === hit.headers.get(k);
			};
			if (!same('content-length') || !same('last-modified') || !same('etag'))
				await cache.delete(url);
		})
	);
}

async function loadSprites(url: string) {
	const blob = await (await fetch(url)).blob();
	spritesPrint = hashBytes(new Uint8Array(await blob.arrayBuffer()));
	const bmp = await createImageBitmap(blob, {
		colorSpaceConversion: 'none',
		premultiplyAlpha: 'none'
	});
	const c = new OffscreenCanvas(bmp.width, bmp.height);
	const ctx = c.getContext('2d', { willReadFrequently: true })!;
	ctx.fillStyle = '#fff';
	ctx.fillRect(0, 0, c.width, c.height);
	ctx.drawImage(bmp, 0, 0);
	sprites = {
		width: c.width,
		height: c.height,
		data: ctx.getImageData(0, 0, c.width, c.height).data
	};
}

async function gpuName() {
	const a = await navigator.gpu?.requestAdapter({ powerPreference: 'high-performance' });
	const i = a?.info;
	if (!i) return 'this browser’s GPU';
	const vendor = i.vendor ? i.vendor[0].toUpperCase() + i.vendor.slice(1) : '';
	return [vendor, i.architecture, i.description].filter(Boolean).join(' ') || 'this browser’s GPU';
}

function stripImage(cells: string[]) {
	const strip = assembleStrip(sprites!, cells);
	// the model gets its own copy; `strip` goes back to the page for the inset
	return { strip, image: new tjs!.RawImage(strip.slice(), CELL, 3 * CELL, 4) };
}

/** float16 bits to float32 */
const F16 = (() => {
	const t = new Float32Array(65536);
	for (let h = 0; h < 65536; h++) {
		const s = h & 0x8000 ? -1 : 1;
		const e = (h >> 10) & 0x1f;
		const f = h & 0x3ff;
		t[h] =
			e === 0
				? s * 2 ** -14 * (f / 1024)
				: e === 31
					? f
						? NaN
						: s * Infinity
					: s * 2 ** (e - 15) * (1 + f / 1024);
	}
	return t;
})();

/**
 * Logits at position `pos` as float32. An fp16 decoder's logits arrive as a Float16Array where the browser has one
 * (values), and as a Uint16Array of raw half-precision bits where it does not.
 */
function logitsAt(t: TTensor, pos: number): Float32Array {
	const V = t.dims[2];
	const data = t.data as unknown as ArrayLike<number> & { subarray?: unknown };
	if (t.type === 'float32') return (data as Float32Array).subarray(pos * V, (pos + 1) * V);
	if (t.type === 'float16') {
		const out = new Float32Array(V);
		if (data instanceof Uint16Array) for (let i = 0; i < V; i++) out[i] = F16[data[pos * V + i]];
		else for (let i = 0; i < V; i++) out[i] = data[pos * V + i];
		return out;
	}
	throw new Error(`logits of type ${t.type}`);
}

/** margin of token `t` (its logit minus the best other) and the best other token */
function margin(row: Float32Array, t: number) {
	let best = -Infinity;
	let arg = -1;
	for (let v = 0; v < row.length; v++)
		if (v !== t && row[v] > best) {
			best = row[v];
			arg = v;
		}
	return { m: row[t] - best, arg };
}

function argmax(row: Float32Array) {
	let a = 0;
	for (let v = 1; v < row.length; v++) if (row[v] > row[a]) a = v;
	return a;
}

const tokenOf = (c: string) => tok!.encode(c, { add_special_tokens: false })[0];

// ---- the inside: the decoder session's extra output and input ---------------------------------------------------
interface OrtTensor {
	type: string;
	dims: readonly number[];
	data: unknown;
}
interface OrtSession {
	inputNames: readonly string[];
	run(feeds: Record<string, OrtTensor>, opts?: unknown): Promise<Record<string, OrtTensor>>;
}

/** Row `b`'s states at position `pos` of a `hidden_states` output [DEPTH, batch, seq, DIM], as DEPTH x DIM. */
function statesAt(t: OrtTensor, b: number, pos: number): Float32Array {
	const [L, Bn, S, D] = t.dims;
	const data = t.data as ArrayLike<number>;
	const bits = data instanceof Uint16Array;
	const out = new Float32Array(L * D);
	for (let l = 0; l < L; l++) {
		const off = ((l * Bn + b) * S + pos) * D;
		for (let i = 0; i < D; i++) out[l * D + i] = bits ? F16[data[off + i]] : data[off + i];
	}
	return out;
}

/** the states that wrote each answer token of batch row b: one per call, or the last positions of one call (slots) */
const tokenStates = (b: number) =>
	captureLast > 1 && captured.length ? captured[0][b] : captured.map((c) => c[b][0]);

/** the program's placeholder slots after the multiplier's prompt (0: answers generated token by token) */
const slots = () => MODELS.mul.slots ?? 0;

/**
 * Hook the decoder session: hide `steer` from transformers.js (which feeds only the inputs it knows) and feed it here,
 * zeros except for an armed push at the last prompt position; keep `hidden_states` while a tick is capturing.
 */
function wrapDecoder(m: Model) {
	const sessions = (m as unknown as { sessions: Record<string, OrtSession> }).sessions;
	const s = sessions?.decoder_model_merged;
	if (!s || !s.inputNames.includes('steer')) return false;
	const names = s.inputNames.filter((n) => n !== 'steer');
	Object.defineProperty(s, 'inputNames', { value: names, configurable: true });
	const run = s.run.bind(s);
	s.run = async (feeds, opts) => {
		const dims = feeds.inputs_embeds.dims as number[];
		const data = new Float32Array(dims[0] * dims[1] * dims[2]);
		if (steerNext && dims[1] > 1 && dims[0] === 1) {
			data.set(steerNext, (dims[1] - 1) * dims[2]);
			steerNext = null;
		}
		const steer = (new tjs!.Tensor('float32', data, dims) as unknown as { ort_tensor: OrtTensor })
			.ort_tensor;
		const out = await run({ ...feeds, steer }, opts);
		const hs = out.hidden_states;
		if (capturing && hs) {
			const S = hs.dims[2];
			const k = Math.min(captureLast, S);
			captured.push(
				Array.from({ length: hs.dims[1] }, (_, b) =>
					Array.from({ length: k }, (_, i) => statesAt(hs, b, S - k + i))
				)
			);
		}
		return out;
	};
	return true;
}

/** The program's inside data, beside its graph; null when the program has none. */
async function loadInside(spec: SketchModel, root: string) {
	const base = `${root}${spec.id}/`;
	const get = async (f: string) => {
		const r = await fetch(base + f);
		if (!r.ok) throw new Error(`${f}: ${r.status}`);
		return r;
	};
	const [lj, lb, ij, ib] = await Promise.all([
		get('onnx/lens.json').then((r) => r.json()),
		get('onnx/lens.bin').then((r) => r.arrayBuffer()),
		get('inside.json').then((r) => r.json()),
		get('inside.bin').then((r) => r.arrayBuffer())
	]);
	inside = parseAssets(lj, lb, ij, ib);
	insideMeta = {
		steerLayer: ij.steerLayer,
		steerCodes: ij.steerCodes,
		families: Object.fromEntries(
			Object.entries(ij.families as Record<string, InsideMeta['families']['SUM']>).map(([k, f]) => [
				k,
				{
					cloud: f.cloud,
					cloudLabels: f.cloudLabels,
					cloudViews: f.cloudViews,
					labels: f.labels,
					radius: f.radius,
					separation: f.separation
				}
			])
		) as InsideMeta['families']
	};
}

/** run `fn` with every decoder call's states kept, and read them */
async function withInside<T>(
	op: TickOp,
	cells: string[],
	push: string | null,
	fn: () => Promise<T>
) {
	captured = [];
	capturing = !!inside;
	captureLast = op !== 'ADD-FAST' && slots() ? 1 + slots() : 1;
	steerNext = null;
	let pushed: string | null = null;
	if (inside && push && op === 'ADD-FAST') {
		// moves the stream entering the steer layer from the class mean of the true answer to the asked one
		const v = steerVector(inside, addCode(addRule(cells)), push);
		if (v) {
			steerNext = v;
			pushed = push;
		}
	}
	try {
		const r = await fn();
		const read = inside && captured.length ? analyse(inside, op, tokenStates(0), pushed) : null;
		return { r, inside: read };
	} finally {
		capturing = false;
		captured = [];
		steerNext = null;
	}
}

// ---- the adder: one forward over "ADD<image>=", the last position's logits give the one answer token -------------
async function addForward(cells: string[]) {
	const { strip, image } = stripImage(cells);
	const out = await model!(await processor!(promptFor('ADD-FAST'), [image]));
	const S = out.logits.dims[1];
	return { row: logitsAt(out.logits, S - 1), strip };
}

async function addScore(cells: string[]) {
	const want = addCode(addRule(cells));
	const { row } = await addForward(cells);
	const { m, arg } = margin(row, tokenOf(want));
	return { m, got: m > 0 ? null : tok!.decode([arg]) };
}

// ---- the multiplier: "<OP><image>=" then three tokens (glyph, glyph, next-op) ------------------------------------
function extend(t: TTensor, vals: number[]): TTensor {
	const { Tensor } = tjs!;
	const data =
		t.type === 'int64'
			? BigInt64Array.from([...(t.data as Iterable<bigint>), ...vals.map(BigInt)])
			: Float32Array.from([...(t.data as Iterable<number>), ...vals]);
	return new Tensor(t.type as 'int64', data, [1, t.dims[1] + vals.length]) as unknown as TTensor;
}

/** append token ids to a one-row prompt's per-token tensors (attention 1, modality 0 for the new places) */
function appendTokens(inp: Inputs, ids: number[]) {
	const L = (inp.input_ids as TTensor).dims[1];
	for (const k of Object.keys(inp)) {
		const t = inp[k] as TTensor | undefined;
		if (t?.dims?.length === 2 && t.dims[0] === 1 && t.dims[1] === L)
			inp[k] = extend(t, k === 'input_ids' ? ids : ids.map(() => (k === 'attention_mask' ? 1 : 0)));
	}
	return L;
}

/** a multiplier prompt with its placeholder slots, for the one forward pass that reads all three answers */
async function slotted(op: Op, image: unknown) {
	const inp = await processor!(promptFor(op), [image]);
	const L = appendTokens(inp, Array(slots()).fill(tokenOf('?')));
	return { inp, L };
}

/**
 * Check one table row: every answer token must be the argmax at its place. Generated programs are scored teacher-
 * forced (the answer appended one token id per character, as in training: tokenising "_-N" jointly would merge
 * pieces); slotted programs read their three answers
 * at `=` and the slots, exactly as a tick does.
 */
async function mulScore(op: Op, v: string[]) {
	const ans = outChars(op, v);
	const ids = ans.map(tokenOf);
	const { image } = stripImage(v);
	let inp: Inputs;
	let L: number;
	if (slots()) ({ inp, L } = await slotted(op, image));
	else {
		inp = await processor!(promptFor(op), [image]);
		L = appendTokens(inp, ids);
	}
	const out = await model!(inp);
	let worst = Infinity;
	let got = '';
	ids.forEach((t, j) => {
		const { m, arg } = margin(logitsAt(out.logits, L - 1 + j), t);
		worst = Math.min(worst, m);
		got += m > 0 ? ans[j] : tok!.decode([arg]);
	});
	return { m: worst, got: worst > 0 ? null : got };
}

/** three answers from one forward of a slotted prompt, for batch row `row` */
function readSlots(logits: TTensor, row: number, L: number) {
	const S = logits.dims[1];
	return [0, 1, 2].map((j) => tok!.decode([argmax(logitsAt(logits, row * S + L - 1 + j))]));
}

async function mulTick(op: Op, cells: string[]) {
	const { strip, image } = stripImage(cells);
	if (slots()) {
		const { inp, L } = await slotted(op, image);
		const ch = readSlots((await model!(inp)).logits, 0, L);
		return { out: [ch[0] === '_' ? B : ch[0], ch[1], ch[2]], strip };
	}
	const inputs = await processor!(promptFor(op), [image]);
	const L = (inputs.input_ids as TTensor).dims[1];
	const out = await model!.generate({ ...inputs, do_sample: false, max_new_tokens: 3 });
	const ids = Array.from(out.data)
		.slice(L)
		.map((x) => Number(x));
	const ch = ids.map((i) => tok!.decode([i]));
	return { out: [ch[0] === '_' ? B : ch[0], ch[1], ch[2]], strip };
}

/**
 * Several multiplier ticks in one batched generation: one strip and prompt per row (every op word is one token, so
 * the prompts have one length), three greedy tokens each. The rows are independent views; batching only shares the
 * GPU calls.
 */
async function mulBatch(items: { op: Op; cells: string[] }[]) {
	const strips = items.map((it) => stripImage(it.cells));
	// transformers.js's Qwen image processor reads a list of images as the frames of one video, so each row is
	// prepared on its own and the rows are stacked: token rows (equal lengths), patches, and one grid row per image
	const parts = await Promise.all(
		items.map(async (it, b) =>
			slots()
				? (await slotted(it.op, strips[b].image)).inp
				: processor!(promptFor(it.op), [strips[b].image])
		)
	);
	const inputs: Inputs = {};
	for (const k of Object.keys(parts[0])) {
		const ts = parts.map((x) => x[k] as TTensor);
		if (!ts[0]?.dims) continue;
		inputs[k] = tjs!.cat(ts as never, 0) as unknown as TTensor;
	}
	const L = (inputs.input_ids as TTensor).dims[1];
	if (parts.some((x) => (x.input_ids as TTensor).dims[1] !== L))
		throw new Error('batched prompts differ in length');
	if (slots()) {
		// one forward: row b's answers sit at `=` and its slots
		const logits = (await model!(inputs)).logits;
		return items.map((_, b) => {
			const ch = readSlots(logits, b, L - slots());
			return { out: [ch[0] === '_' ? B : ch[0], ch[1], ch[2]], strip: strips[b].strip };
		});
	}
	const out = await model!.generate({ ...inputs, do_sample: false, max_new_tokens: 3 });
	const W = out.dims[1];
	const data = Array.from(out.data, (x) => Number(x));
	return items.map((_, b) => {
		const ch = data.slice(b * W + L, b * W + W).map((i) => tok!.decode([i]));
		return { out: [ch[0] === '_' ? B : ch[0], ch[1], ch[2]], strip: strips[b].strip };
	});
}

async function tickBatch(m: Extract<ToWorker, { type: 'tick-batch' }>) {
	const r = await exclusive(async () => {
		if (!serves('mul')) throw new Error(`${MODELS.mul.name} is not loaded`);
		const t = performance.now();
		captured = [];
		capturing = !!inside;
		captureLast = slots() ? 1 + slots() : 1;
		try {
			const rows = await mulBatch(m.items as { op: Op; cells: string[] }[]);
			const seen = rows.map((_, b) =>
				inside && captured.length ? analyse(inside, m.items[b].op, tokenStates(b), null) : null
			);
			return { rows, seen, ms: performance.now() - t };
		} finally {
			capturing = false;
			captured = [];
		}
	});
	post(
		{
			type: 'tick-batch',
			rid: m.rid,
			outs: r.rows.map((x) => x.out),
			strips: r.rows.map((x) => x.strip),
			inside: r.seen,
			ms: r.ms
		},
		r.rows.map((x) => x.strip.buffer)
	);
}

// ---- jobs -----------------------------------------------------------------------------------------------------
async function setup(m: Extract<ToWorker, { type: 'load' }>) {
	tjs ??= await import('transformers-420');
	const { env } = tjs;
	// a built page serves ONNX Runtime's WASM itself; the dev server keeps the CDN its pre-bundling needs
	if (import.meta.env?.PROD && env.backends.onnx.wasm) env.backends.onnx.wasm.wasmPaths = undefined;
	env.allowLocalModels = false;
	env.allowRemoteModels = true;
	env.useBrowserCache = false;
	env.remoteHost = m.root;
	env.remotePathTemplate = '{model}/';
	env.fetch = routedFetch(m.root);
	// private windows may have no Cache API: then every load downloads, nothing else changes
	const canCache =
		typeof caches !== 'undefined' &&
		(await caches.open(FILE_CACHE).then(
			() => true,
			() => false
		));
	env.useCustomCache = canCache;
	env.customCache = canCache ? fileCache(m.root) : null;
	if (!sprites) await loadSprites(m.sprites);
	gpu ||= await gpuName().catch(() => 'this browser’s GPU');
	return canCache;
}

async function load(m: Extract<ToWorker, { type: 'load' }>) {
	wanted = m.lid;
	await exclusive(async () => {
		if (m.lid !== wanted) return post({ type: 'load-skipped', lid: m.lid });
		const spec = MODELS[m.kind];
		const t0 = performance.now();
		try {
			if (model && loadedId === spec.id)
				return post({ type: 'loaded', lid: m.lid, info: info(spec, m.root, 0, true) });
			if (model) {
				// the old program goes first: its sessions free their GPU memory before the new ones are made
				const old = model;
				model = null;
				processor = null;
				loadedId = null;
				generation++;
				await old.dispose().catch(() => {});
			}
			const canCache = await setup(m);
			if (canCache) await dropStale(spec, m.root);
			const expect = await uncachedBytes(spec, m.root, canCache);
			network = {};
			cachedBytes = 0;
			performance.clearResourceTimings();
			performance.setResourceTimingBufferSize(2000);
			let last = -Infinity;
			onBytes = () => {
				const now = performance.now();
				if (now - last < 120) return;
				last = now;
				post({
					type: 'progress',
					lid: m.lid,
					kind: m.kind,
					network: sum(network),
					expect,
					cached: cachedBytes,
					stage: 'fetch'
				});
			};
			onBytes();
			const [proc, mdl] = await Promise.all([
				tjs!.AutoProcessor.from_pretrained(spec.id),
				tjs!.Qwen3_5ForConditionalGeneration.from_pretrained(spec.id, {
					dtype: DTYPE,
					device: 'webgpu'
				})
			]);
			onBytes = () => {};
			processor = proc as unknown as Processor;
			model = mdl as unknown as Model;
			tok = processor.tokenizer;
			inside = null;
			insideMeta = null;
			if (wrapDecoder(model))
				await loadInside(spec, m.root).catch((e) => {
					inside = null;
					insideMeta = null;
					console.warn('sketchpad: no inside data', e);
				});
			post({
				type: 'progress',
				lid: m.lid,
				kind: m.kind,
				network: sum(network),
				expect,
				cached: cachedBytes,
				stage: 'compile'
			});
			// one forward compiles the GPU kernels before the certificate starts its clock
			await addForward([B, B, B]);
			loadedId = spec.id;
			generation++;
			post({
				type: 'loaded',
				lid: m.lid,
				info: info(spec, m.root, (performance.now() - t0) / 1000, false)
			});
		} catch (e) {
			onBytes = () => {};
			post({ type: 'load-error', lid: m.lid, kind: m.kind, error: message(e) });
		}
	});
}

const sum = (r: Record<string, number>) => Object.values(r).reduce((a, b) => a + b, 0);

/** what this load will take from the network: the sizes of the files not in this browser's cache */
async function uncachedBytes(m: SketchModel, root: string, canCache: boolean) {
	const cache = canCache ? await caches.open(FILE_CACHE) : null;
	const sizes = await Promise.all(
		modelFiles().map(async (f) => {
			const url = root + servedPath(m, f);
			if (cache && (await cache.match(url))) return 0;
			const head = await fetch(url, { method: 'HEAD', cache: 'no-store' }).catch(() => null);
			return Number(head?.headers.get('content-length') ?? 0);
		})
	);
	return sizes.reduce((a, b) => a + b, 0);
}

function info(spec: SketchModel, root: string, seconds: number, reused: boolean): LoadedInfo {
	const files = modelFiles();
	const transferSize = (performance.getEntriesByType('resource') as PerformanceResourceTiming[])
		.filter((e) => e.name.startsWith(root))
		.reduce((a, e) => a + e.transferSize, 0);
	return {
		id: spec.id,
		kind: spec.kind,
		seconds,
		prints: Object.fromEntries(
			files.flatMap((f) => {
				const p = prints.get(servedPath(spec, f));
				return p ? [[f, p]] : [];
			})
		),
		sprites: spritesPrint,
		gpu,
		transformers: tjs?.env.version ?? '',
		network: reused ? 0 : sum(network),
		networkFiles: reused ? {} : { ...network },
		transferSize: reused ? 0 : transferSize,
		cached: reused ? 0 : cachedBytes,
		reused,
		inside: insideMeta
	};
}

/** the loaded program serves this kind */
const serves = (k: Kind) => !!model && loadedId === MODELS[k].id;

async function certify(rid: number, k: Kind, only?: number[]) {
	if (!serves(k)) throw new Error(`${MODELS[k].name} is not loaded`);
	const born = generation;
	let compute = 0;
	let start = 0;
	let margins: number[] = [];
	let got: (string | null)[] = [];
	let indices: number[] = [];
	let sent = performance.now();
	const flush = () => {
		post({ type: 'cert-rows', rid, start, margins, got, ...(only ? { indices } : {}) });
		start += margins.length;
		margins = [];
		got = [];
		indices = [];
		sent = performance.now();
	};
	const n = k === 'add' ? ADD_DOMAIN.length : MUL_DOMAIN.length;
	const order = only ?? Array.from({ length: n }, (_, i) => i);
	for (let j = 0; j < order.length; j++) {
		const i = order[j];
		if (cancelled.has(rid)) throw new Cancelled();
		const r = await exclusive(async () => {
			// a load got in between: these rows would no longer be about this model
			if (generation !== born || !serves(k)) throw new Cancelled();
			const t = performance.now();
			const res = k === 'add' ? await addScore(ADD_DOMAIN[i]) : await mulScore(...MUL_DOMAIN[i]);
			compute += performance.now() - t;
			return res;
		});
		margins.push(r.m);
		got.push(r.got);
		indices.push(i);
		if (performance.now() - sent > 60 || j === order.length - 1) flush();
	}
	post({ type: 'cert-done', rid, seconds: compute / 1000 });
}

async function tick(m: Extract<ToWorker, { type: 'tick' }>) {
	const r = await exclusive(async () => {
		if (!serves(kindOf(m.op))) throw new Error(`${MODELS[kindOf(m.op)].name} is not loaded`);
		const t = performance.now();
		if (m.op === 'ADD-FAST') {
			const { r: f, inside: seen } = await withInside(m.op, m.cells, m.push, () =>
				addForward(m.cells)
			);
			const a = argmax(f.row);
			const { m: mg } = margin(f.row, a);
			const text = tok!.decode([a]);
			return { out: [text], margin: mg, strip: f.strip, ms: performance.now() - t, inside: seen };
		}
		const { r: f, inside: seen } = await withInside(m.op, m.cells, null, () =>
			mulTick(m.op as Op, m.cells)
		);
		return { out: f.out, margin: null, strip: f.strip, ms: performance.now() - t, inside: seen };
	});
	post(
		{
			type: 'tick',
			rid: m.rid,
			out: r.out,
			margin: r.margin,
			ms: r.ms,
			strip: r.strip,
			inside: r.inside
		},
		[r.strip.buffer]
	);
}

async function chat(m: Extract<ToWorker, { type: 'chat' }>) {
	await exclusive(async () => {
		if (!model || !processor || !tjs) throw new Error('no model is loaded');
		const t = performance.now();
		const text = processor.apply_chat_template(
			[{ role: 'user', content: [{ type: 'text', text: m.question }] }],
			{ add_generation_prompt: true, tokenizer_kwargs: { enable_thinking: false } }
		);
		const inputs = await processor(text);
		const streamer = new tjs.TextStreamer(tok as never, {
			skip_prompt: true,
			skip_special_tokens: true,
			callback_function: (s: string) => post({ type: 'chat-delta', rid: m.rid, text: s })
		});
		// greedy, with repeated 5-grams blocked: plain greedy restates its answer word for word, and a repetition
		// penalty (1.1) pushes this small model into inventing facts
		await model.generate({
			...inputs,
			do_sample: false,
			max_new_tokens: m.maxNew,
			no_repeat_ngram_size: 5,
			streamer
		});
		post({ type: 'done', rid: m.rid, ms: performance.now() - t });
	});
}

self.onmessage = async (ev: MessageEvent<ToWorker>) => {
	const m = ev.data;
	if (m.type === 'load') return load(m);
	if (m.type === 'cancel') return void cancelled.add(m.rid);
	try {
		if (m.type === 'certify') await certify(m.rid, m.kind, m.rows);
		else if (m.type === 'tick') await tick(m);
		else if (m.type === 'tick-batch') await tickBatch(m);
		else if (m.type === 'chat') await chat(m);
	} catch (e) {
		post({ type: 'failed', rid: m.rid, error: message(e), cancelled: e instanceof Cancelled });
	} finally {
		cancelled.delete(m.rid);
	}
};
