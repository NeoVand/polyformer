/**
 * The engine's LM on transformers.js 4.3.1: Savant-4B (Qwen3-4B with PROMPTBOX's adapter merged), exported to ONNX.
 * `forward` calls the model's own forward with explicit positions and a cache it never rewrites (ONNX Runtime returns
 * new present tensors), so Π's cache can be reused by every tick and freed by the engine when it is done with it.
 * Present tensors stay on the GPU (transformers.js asks WebGPU for them as GPU buffers); only the logits come back.
 */
import type { Forward, KV, LM } from './engine.ts';
import { qwenTok, type RawTokenizer } from './tokenizer.ts';
import type { Tok } from './pb.ts';

type TjsModule = typeof import('@huggingface/transformers');
type TjsTensor = InstanceType<TjsModule['Tensor']>;

interface TjsModel {
	forward(inputs: Record<string, unknown>): Promise<Record<string, TjsTensor>>;
	sessions: Record<string, { inputNames: string[]; outputNames: string[] }>;
	dispose(): Promise<unknown>;
}

class TjsKV implements KV {
	disposed = false;
	constructor(
		readonly entries: Record<string, TjsTensor>,
		readonly length: number
	) {}
	dispose() {
		if (this.disposed) return;
		this.disposed = true;
		for (const t of Object.values(this.entries)) if (t.location === 'gpu-buffer') t.dispose();
	}
}

/** float16 bits to float32 */
const F16 = (() => {
	const table = new Float32Array(65536);
	for (let h = 0; h < 65536; h++) {
		const s = h & 0x8000 ? -1 : 1;
		const e = (h >> 10) & 0x1f;
		const f = h & 0x3ff;
		table[h] =
			e === 0
				? s * 2 ** -14 * (f / 1024)
				: e === 31
					? f
						? NaN
						: s * Infinity
					: s * 2 ** (e - 15) * (1 + f / 1024);
	}
	return table;
})();

/** A 64-bit fingerprint of raw bytes (two independent 32-bit lanes over 32-bit words). */
export function fingerprint(bytes: Uint8Array): string {
	const words =
		bytes.byteOffset % 4 === 0 && bytes.byteLength % 4 === 0
			? new Uint32Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 4)
			: new Uint32Array(Uint8Array.from(bytes).buffer, 0, Math.floor(bytes.byteLength / 4));
	let a = 0x811c9dc5;
	let b = 0x9e3779b9;
	for (let i = 0; i < words.length; i++) {
		const w = words[i];
		a = Math.imul(a ^ w, 0x01000193);
		b = Math.imul(b ^ ((w << 13) | (w >>> 19)), 0x85ebca6b) ^ (b >>> 15);
	}
	for (let i = words.length * 4; i < bytes.byteLength; i++) a = Math.imul(a ^ bytes[i], 0x01000193);
	return (a >>> 0).toString(16).padStart(8, '0') + (b >>> 0).toString(16).padStart(8, '0');
}

/** The last position's logits as float32, and the fingerprint of their raw bits. */
export function lastLogits(t: {
	dims: number[];
	type: string;
	data: ArrayLike<number> & ArrayBufferView;
}) {
	const [, T, V] = t.dims;
	const start = (T - 1) * V;
	const data = t.data;
	const raw = new Uint8Array(
		data.buffer,
		data.byteOffset + start * (t.type === 'float16' ? 2 : 4),
		V * (t.type === 'float16' ? 2 : 4)
	);
	let logits: Float32Array;
	if (t.type === 'float32')
		logits = Float32Array.from((data as Float32Array).subarray(start, start + V));
	else if (t.type === 'float16') {
		const bits = new Uint16Array(data.buffer, data.byteOffset + start * 2, V);
		logits = new Float32Array(V);
		for (let i = 0; i < V; i++) logits[i] = F16[bits[i]];
	} else throw new Error(`logits of type ${t.type}`);
	return { logits, bits: fingerprint(raw) };
}

export class TjsLM implements LM {
	private keepOne: boolean;
	constructor(
		private tjs: TjsModule,
		private model: TjsModel,
		private prefer: number
	) {
		const s = model.sessions.model ?? Object.values(model.sessions)[0];
		this.keepOne = s.inputNames.includes('num_logits_to_keep');
	}

	/**
	 * Tokens per prefill call. Without `num_logits_to_keep` every fed position's logits come back to the CPU
	 * (151,936 numbers each), so the chunks are kept small.
	 */
	get chunk() {
		return this.keepOne ? this.prefer : Math.min(this.prefer, 32);
	}

	/** Whether the export lets a forward compute only the last position's logits. */
	get lastOnly() {
		return this.keepOne;
	}

	async forward(ids: number[], past: KV | null, keep: boolean): Promise<Forward> {
		const { Tensor } = this.tjs;
		const n = ids.length;
		const P = past?.length ?? 0;
		const big = (xs: number[]) => BigInt64Array.from(xs, (x) => BigInt(x));
		const inputs: Record<string, unknown> = {
			input_ids: new Tensor('int64', big(ids), [1, n]),
			attention_mask: new Tensor('int64', new BigInt64Array(P + n).fill(1n), [1, P + n]),
			position_ids: new Tensor('int64', big(Array.from({ length: n }, (_, i) => P + i)), [1, n]),
			past_key_values: past ? (past as TjsKV).entries : null
		};
		if (this.keepOne) inputs.num_logits_to_keep = new Tensor('int64', [1n], []);
		const out = await this.model.forward(inputs);
		const entries: Record<string, TjsTensor> = {};
		for (const [k, v] of Object.entries(out))
			if (k.startsWith('present')) entries[k.replace('present', 'past_key_values')] = v;
		const kv = new TjsKV(entries, P + n);
		const lg = out.logits as unknown as Parameters<typeof lastLogits>[0];
		const { logits, bits } = lastLogits(lg);
		if (!keep) kv.dispose();
		return { logits, bits, past: keep ? kv : null };
	}
}

export interface LoadProgress {
	/** bytes received per file so far, and each file's size once known */
	files: Record<string, { loaded: number; total: number }>;
	loaded: number;
	total: number;
	stage: 'download' | 'compile' | 'ready';
	file?: string;
}

export interface Loaded {
	tok: Tok;
	lm: TjsLM;
	nl: number;
	stop: number[];
	device: string;
	dtype: string;
	dispose(): Promise<void>;
}

/**
 * Where transformers.js fetches the files: a folder URL (http, https) or, in Node, a folder on disk. The folder holds
 * the transformers.js layout (config.json, tokenizer files, onnx/model_<dtype>.onnx and its data chunks).
 */
function configure(tjs: TjsModule, base: string): string {
	const { env } = tjs;
	const isUrl = /^https?:\/\//.test(base) || base.startsWith('/');
	if (isUrl && typeof location !== 'undefined') base = new URL(base, location.href).href;
	const trimmed = base.replace(/\/+$/, '');
	const cut = trimmed.lastIndexOf('/');
	const parent = trimmed.slice(0, cut + 1);
	const id = trimmed.slice(cut + 1);
	if (/^https?:\/\//.test(trimmed)) {
		env.allowLocalModels = false;
		env.allowRemoteModels = true;
		env.remoteHost = parent;
		env.remotePathTemplate = '{model}/';
	} else {
		env.allowLocalModels = true;
		env.allowRemoteModels = false;
		env.localModelPath = parent;
	}
	return id;
}

export async function loadTransformers(opts: {
	base: string;
	device: 'webgpu' | 'cpu';
	dtype: string;
	chunk?: number;
	onProgress?: (p: LoadProgress) => void;
}): Promise<Loaded> {
	const tjs = await import('@huggingface/transformers');
	// a built page serves ONNX Runtime's WASM itself (the bundler copies it beside the worker), instead of the
	// CDN transformers.js points at by default; the dev server keeps the CDN, which its pre-bundling needs
	if (import.meta.env?.PROD && tjs.env.backends.onnx.wasm)
		tjs.env.backends.onnx.wasm.wasmPaths = undefined;
	const id = configure(tjs, opts.base);
	const progress: LoadProgress = { files: {}, loaded: 0, total: 0, stage: 'download' };
	const report = () => {
		const vals = Object.values(progress.files);
		progress.loaded = vals.reduce((a, f) => a + f.loaded, 0);
		progress.total = vals.reduce((a, f) => a + f.total, 0);
		opts.onProgress?.({ ...progress, files: { ...progress.files } });
	};
	const progress_callback = (info: {
		status: string;
		file?: string;
		loaded?: number;
		total?: number;
	}) => {
		if (info.status === 'progress' && info.file) {
			progress.files[info.file] = { loaded: info.loaded ?? 0, total: info.total ?? 0 };
			progress.file = info.file;
			report();
		} else if (info.status === 'done' && info.file) {
			const f = progress.files[info.file];
			if (f) f.loaded = f.total;
			report();
		}
	};
	// both at once, so the weights start downloading at the first moment
	const [tokenizer, loadedModel] = await Promise.all([
		tjs.AutoTokenizer.from_pretrained(id, { progress_callback }),
		tjs.AutoModelForCausalLM.from_pretrained(id, {
			device: opts.device,
			dtype: opts.dtype as 'q4f16',
			progress_callback
		})
	]);
	const model = loadedModel as unknown as TjsModel;
	progress.stage = 'ready';
	report();
	const raw = (tokenizer as unknown as { _tokenizer: RawTokenizer })._tokenizer;
	const tok = qwenTok(raw);
	const nl = tok.encode('\n');
	if (nl.length !== 1) throw new Error('newline is not one token');
	const stop = ['<|im_end|>', '<|endoftext|>']
		.map((s) => tok.encode(s))
		.filter((x) => x.length === 1)
		.map((x) => x[0]);
	const lm = new TjsLM(tjs, model, opts.chunk ?? (opts.device === 'webgpu' ? 256 : 512));
	return {
		tok,
		lm,
		nl: nl[0],
		stop,
		device: opts.device,
		dtype: opts.dtype,
		dispose: async () => {
			await model.dispose();
		}
	};
}
