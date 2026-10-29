/// <reference lib="webworker" />
/**
 * The worker that holds the sketchpad model. The page owns the sheet (the model's only memory); the worker owns the
 * model's eyes and hands: it assembles each strip from the training sprites, runs one forward (or three greedy tokens),
 * and posts the answer back. It also checks the whole table for the certificate and answers chat questions. One GPU
 * job runs at a time; certificate rows, ticks and chat take turns.
 */
import { ADD_DOMAIN, ADD_PROMPT, addCode, addRule } from './adder.ts';
import { StreamHash, hashBytes } from './hash.ts';
import { MODELS, type Kind } from './models.ts';
import { MUL_DOMAIN, mulPrompt, outChars, type Op } from './multiplier.ts';
import type { FromWorker, ToWorker } from './protocol.ts';
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
	(text: string, images?: unknown[]): Promise<Inputs>;
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
let kind: Kind | null = null;
let sprites: SpriteSheet | null = null;
let spritesPrint = '';
let gpu = '';
/** fingerprints of the files fetched, by path below the models folder */
const prints = new Map<string, string>();
const cancelled = new Set<number>();

/** one GPU job at a time */
let chain: Promise<unknown> = Promise.resolve();
function exclusive<T>(fn: () => Promise<T>): Promise<T> {
	const run = chain.then(fn, fn);
	chain = run.catch(() => {});
	return run;
}

/** fetch that fingerprints every whole-file download as it streams past */
function hashingFetch(base: string) {
	return async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
		const res = await fetch(input, init);
		const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
		const ranged = new Headers(init?.headers).has('Range');
		if (res.status !== 200 || ranged || !res.body || !url.startsWith(base)) return res;
		const name = url.slice(base.length).split('?')[0];
		const h = new StreamHash();
		const body = res.body.pipeThrough(
			new TransformStream<Uint8Array, Uint8Array>({
				transform(chunk, ctl) {
					h.update(chunk);
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

// ---- the adder: one forward over "ADD<image>=", the last position's logits give the one answer token -------------
async function addForward(cells: string[]) {
	const { strip, image } = stripImage(cells);
	const out = await model!(await processor!(ADD_PROMPT, [image]));
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

/**
 * Teacher-forced check of one table row: the answer is appended one token id per character, as in training
 * (tokenising "_-N" jointly would merge pieces), and every answer token must be the argmax.
 */
async function mulScore(op: Op, v: string[]) {
	const ans = outChars(op, v);
	const ids = ans.map(tokenOf);
	const { image } = stripImage(v);
	const inp = await processor!(mulPrompt(op), [image]);
	const L = (inp.input_ids as TTensor).dims[1];
	for (const k of Object.keys(inp)) {
		const t = inp[k] as TTensor | undefined;
		if (t?.dims?.length === 2 && t.dims[0] === 1 && t.dims[1] === L)
			inp[k] = extend(t, k === 'input_ids' ? ids : ids.map(() => (k === 'attention_mask' ? 1 : 0)));
	}
	const out = await model!(inp);
	const S = out.logits.dims[1];
	let worst = Infinity;
	let got = '';
	ids.forEach((t, j) => {
		const { m, arg } = margin(logitsAt(out.logits, S - ids.length - 1 + j), t);
		worst = Math.min(worst, m);
		got += m > 0 ? ans[j] : tok!.decode([arg]);
	});
	return { m: worst, got: worst > 0 ? null : got };
}

async function mulTick(op: Op, cells: string[]) {
	const { strip, image } = stripImage(cells);
	const inputs = await processor!(mulPrompt(op), [image]);
	const L = (inputs.input_ids as TTensor).dims[1];
	const out = await model!.generate({ ...inputs, do_sample: false, max_new_tokens: 3 });
	const ids = Array.from(out.data)
		.slice(L)
		.map((x) => Number(x));
	const ch = ids.map((i) => tok!.decode([i]));
	return { out: [ch[0] === '_' ? B : ch[0], ch[1], ch[2]], strip };
}

// ---- jobs -----------------------------------------------------------------------------------------------------
async function load(m: Extract<ToWorker, { type: 'load' }>) {
	if (kind === m.kind && model) return post({ type: 'loaded', info: info(m.kind, 0) });
	await exclusive(async () => {
		const t0 = performance.now();
		try {
			if (model) {
				await model.dispose().catch(() => {});
				model = null;
				processor = null;
				kind = null;
			}
			tjs ??= await import('transformers-420');
			const { env } = tjs;
			// a built page serves ONNX Runtime's WASM itself; the dev server keeps the CDN its pre-bundling needs
			if (import.meta.env?.PROD && env.backends.onnx.wasm)
				env.backends.onnx.wasm.wasmPaths = undefined;
			env.allowLocalModels = false;
			env.allowRemoteModels = true;
			env.useBrowserCache = false;
			env.remoteHost = m.base;
			env.remotePathTemplate = '{model}/';
			env.fetch = hashingFetch(m.base);
			if (!sprites) await loadSprites(m.sprites);
			gpu ||= await gpuName().catch(() => 'this browser’s GPU');

			const spec = MODELS[m.kind];
			const files: Record<string, { loaded: number; total: number }> = {};
			let last = 0;
			const report = (force = false) => {
				const now = performance.now();
				if (!force && now - last < 120) return;
				last = now;
				post({ type: 'progress', kind: m.kind, files: { ...files }, stage: 'download' });
			};
			const progress_callback = (p: {
				status: string;
				file?: string;
				loaded?: number;
				total?: number;
			}) => {
				if (!p.file) return;
				if (p.status === 'progress') files[p.file] = { loaded: p.loaded ?? 0, total: p.total ?? 0 };
				else if (p.status === 'done' && files[p.file]) files[p.file].loaded = files[p.file].total;
				else return;
				report(p.status === 'done');
			};
			const [proc, mdl] = await Promise.all([
				tjs.AutoProcessor.from_pretrained(spec.id, { progress_callback }),
				tjs.Qwen3_5ForConditionalGeneration.from_pretrained(spec.id, {
					dtype: spec.dtype,
					device: 'webgpu',
					progress_callback
				})
			]);
			processor = proc as unknown as Processor;
			model = mdl as unknown as Model;
			tok = processor.tokenizer;
			post({ type: 'progress', kind: m.kind, files: { ...files }, stage: 'compile' });
			// one forward compiles the GPU kernels before the certificate starts its clock
			await addForward([B, B, B]);
			kind = m.kind;
			post({ type: 'loaded', info: info(m.kind, (performance.now() - t0) / 1000) });
		} catch (e) {
			post({ type: 'load-error', kind: m.kind, error: message(e) });
		}
	});
}

function info(k: Kind, seconds: number) {
	const id = MODELS[k].id + '/';
	const mine = Object.fromEntries(
		[...prints].filter(([p]) => p.startsWith(id)).map(([p, h]) => [p.slice(id.length), h])
	);
	return {
		kind: k,
		seconds,
		prints: mine,
		sprites: spritesPrint,
		gpu,
		transformers: tjs?.env.version ?? ''
	};
}

async function certify(rid: number, k: Kind) {
	if (k !== kind) throw new Error(`${MODELS[k].name} is not loaded`);
	let compute = 0;
	let start = 0;
	let margins: number[] = [];
	let got: (string | null)[] = [];
	let sent = performance.now();
	const flush = () => {
		post({ type: 'cert-rows', rid, start, margins, got });
		start += margins.length;
		margins = [];
		got = [];
		sent = performance.now();
	};
	const n = k === 'add' ? ADD_DOMAIN.length : MUL_DOMAIN.length;
	for (let i = 0; i < n; i++) {
		if (cancelled.has(rid)) throw new Cancelled();
		const r = await exclusive(async () => {
			const t = performance.now();
			const res = k === 'add' ? await addScore(ADD_DOMAIN[i]) : await mulScore(...MUL_DOMAIN[i]);
			compute += performance.now() - t;
			return res;
		});
		margins.push(r.m);
		got.push(r.got);
		if (performance.now() - sent > 60 || i === n - 1) flush();
	}
	post({ type: 'cert-done', rid, seconds: compute / 1000 });
}

async function tick(m: Extract<ToWorker, { type: 'tick' }>) {
	const r = await exclusive(async () => {
		const t = performance.now();
		if (m.op === 'ADD-FAST') {
			if (kind !== 'add') throw new Error('the adder is not loaded');
			const { row, strip } = await addForward(m.cells);
			const a = argmax(row);
			const { m: mg } = margin(row, a);
			const text = tok!.decode([a]);
			return { out: [text], margin: mg, strip, ms: performance.now() - t };
		}
		if (kind !== 'mul') throw new Error('the multiplier is not loaded');
		const { out, strip } = await mulTick(m.op, m.cells);
		return { out, margin: null, strip, ms: performance.now() - t };
	});
	post({ type: 'tick', rid: m.rid, out: r.out, margin: r.margin, ms: r.ms, strip: r.strip }, [
		r.strip.buffer
	]);
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
		if (m.type === 'certify') await certify(m.rid, m.kind);
		else if (m.type === 'tick') await tick(m);
		else if (m.type === 'chat') await chat(m);
	} catch (e) {
		post({ type: 'failed', rid: m.rid, error: message(e), cancelled: e instanceof Cancelled });
	} finally {
		cancelled.delete(m.rid);
	}
};
