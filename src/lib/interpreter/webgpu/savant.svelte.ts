/**
 * Savant-4B in this browser, from the page's side: whether the browser can run it (WebGPU, 16-bit shaders, buffer
 * sizes), whether its weights are already in the browser's cache, the download, and one question or poke at a time
 * in the worker. Reactive, so the chat and the panels follow it.
 */
import { gb, gpuLabel, SAVANT, savantUrl } from './config.ts';
import type { EngineEvent, Truth } from './engine.ts';
import type { FromWorker, Loaded, PokeResult, ToWorker } from './protocol.ts';
import { StubBackend, stubOf } from './stub.ts';
import type { LoadProgress } from './transformers-lm.ts';
import type { LlmCtx, LlmTrace } from '../trace.ts';

export interface GpuCheck {
	ok: boolean;
	/** why the model cannot run here, in a sentence */
	reason: string | null;
	/** a caution that does not stop it */
	warn: string | null;
	adapter: string | null;
	mobile: boolean;
}

type Status = 'idle' | 'checking' | 'unsupported' | 'can-load' | 'loading' | 'ready' | 'error';

interface Backend {
	postMessage(m: ToWorker): void;
	terminate(): void;
}

interface Pending {
	resolve: (v: never) => void;
	reject: (e: Error) => void;
	onEvent?: (e: EngineEvent) => void;
}

export class Stopped extends Error {
	constructor() {
		super('stopped');
	}
}

const CACHE = 'transformers-cache';
/** the largest single weight (the tied embedding, fp16): a GPU must hold it in one buffer */
const BIGGEST_TENSOR = 151936 * 2560 * 2;

async function checkGpu(): Promise<GpuCheck> {
	const mobile =
		typeof navigator !== 'undefined' && /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent);
	const stub = stubOf();
	if (stub)
		return stub.gpu
			? { ok: true, reason: null, warn: null, adapter: stub.gpu, mobile }
			: { ok: false, reason: 'This browser has no WebGPU.', warn: null, adapter: null, mobile };
	const gpu = typeof navigator !== 'undefined' ? navigator.gpu : undefined;
	if (!gpu)
		return {
			ok: false,
			reason:
				'This browser has no WebGPU. Chrome or Edge 113+ on a desktop has it; so do Safari 26 and Firefox 141 on some systems.',
			warn: null,
			adapter: null,
			mobile
		};
	const a = await gpu.requestAdapter({ powerPreference: 'high-performance' }).catch(() => null);
	if (!a)
		return {
			ok: false,
			reason:
				'WebGPU is here but offers no GPU (it may be switched off, or this GPU is blocklisted).',
			warn: null,
			adapter: null,
			mobile
		};
	const i: Partial<GPUAdapterInfo> = a.info ?? {};
	const adapter = gpuLabel(i) ?? 'an unnamed GPU';
	if (!a.features.has('shader-f16'))
		return {
			ok: false,
			reason: `This GPU (${adapter}) offers no 16-bit floats in shaders (shader-f16), which ${SAVANT.short}’s weights need.`,
			warn: null,
			adapter,
			mobile
		};
	const big = Math.min(a.limits.maxBufferSize, a.limits.maxStorageBufferBindingSize);
	const warn =
		big && big < BIGGEST_TENSOR
			? `This GPU’s largest buffer is ${Math.round(big / 1e6)} MB; the model’s largest weight is ${Math.round(BIGGEST_TENSOR / 1e6)} MB, so loading may fail.`
			: mobile
				? `${SAVANT.short} is a ${gb(SAVANT.bytes)} download and needs a few GB of GPU memory: it is made for desktop GPUs.`
				: null;
	return { ok: true, reason: null, warn, adapter, mobile };
}

const absolute = (base: string) =>
	typeof location !== 'undefined' ? new URL(base, location.href).href : base;

async function cachedKeys(base: string): Promise<Request[]> {
	if (typeof caches === 'undefined') return [];
	try {
		const c = await caches.open(CACHE);
		const root = absolute(base);
		return (await c.keys()).filter((r) => r.url.startsWith(root));
	} catch {
		return [];
	}
}

class Savant {
	status = $state<Status>('idle');
	gpu = $state.raw<GpuCheck | null>(null);
	progress = $state.raw<LoadProgress | null>(null);
	loaded = $state.raw<Loaded | null>(null);
	error = $state<string | null>(null);
	/** the weights are in this browser's cache already */
	cached = $state<boolean | null>(null);
	/** a question or a poke is running */
	busy = $state(false);
	/** download speed, bytes per second over the last few seconds */
	rate = $state(0);
	readonly base = savantUrl();

	private backend: Backend | null = null;
	private samples: { t: number; b: number }[] = [];
	private readyListeners = new Set<() => void>();

	/** Calls `fn` each time the model becomes ready; returns the unsubscribe. */
	onReady(fn: () => void) {
		this.readyListeners.add(fn);
		return () => this.readyListeners.delete(fn);
	}
	private pending = new Map<number, Pending>();
	private rid = 0;

	/** WebGPU and the cache, once; safe to call again. */
	async check() {
		if (this.status !== 'idle') return;
		this.status = 'checking';
		this.gpu = await checkGpu();
		this.cached = stubOf()
			? false
			: (await cachedKeys(this.base)).some((r) => r.url.includes('onnx/'));
		this.status = this.gpu.ok ? 'can-load' : 'unsupported';
	}

	load() {
		if (this.status === 'loading' || this.status === 'ready') return;
		this.status = 'loading';
		this.error = null;
		this.progress = null;
		const stub = stubOf();
		let backend: Backend;
		if (stub) {
			const b = new StubBackend(stub);
			b.onmessage = (m) => this.receive(m);
			backend = b;
		} else {
			const w = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
			w.onmessage = (e: MessageEvent<FromWorker>) => this.receive(e.data);
			w.onerror = (e) => {
				this.fail(e.message || 'the model’s worker stopped');
			};
			backend = w;
		}
		this.backend = backend;
		backend.postMessage({ type: 'load', base: this.base, dtype: SAVANT.dtype, device: 'webgpu' });
	}

	private fail(error: string) {
		this.status = 'error';
		this.error = error;
		for (const p of this.pending.values()) p.reject(new Error(error));
		this.pending.clear();
		this.busy = false;
		this.backend?.terminate();
		this.backend = null;
	}

	private receive(m: FromWorker) {
		if (m.type === 'progress') {
			this.progress = m.progress;
			const t = performance.now();
			this.samples.push({ t, b: m.progress.loaded });
			while (this.samples.length > 2 && t - this.samples[0].t > 4000) this.samples.shift();
			const first = this.samples[0];
			if (t - first.t > 400) this.rate = ((m.progress.loaded - first.b) * 1000) / (t - first.t);
		} else if (m.type === 'loaded') {
			this.loaded = m.loaded;
			this.status = 'ready';
			this.cached = true;
			this.samples = [];
			for (const fn of this.readyListeners) fn();
		} else if (m.type === 'load-error') this.fail(m.error);
		else {
			const p = this.pending.get(m.rid);
			if (!p) return;
			if (m.type === 'event') return p.onEvent?.(m.event);
			this.pending.delete(m.rid);
			this.busy = this.pending.size > 0;
			if (!this.busy) for (const fn of this.readyListeners) queueMicrotask(fn);
			if (m.type === 'answered') p.resolve(m.trace as never);
			else if (m.type === 'poked') p.resolve(m.poke as never);
			else p.reject(m.cancelled ? new Stopped() : new Error(m.error));
		}
	}

	private run<T>(m: ToWorker & { rid: number }, onEvent?: (e: EngineEvent) => void) {
		if (!this.backend || this.status !== 'ready') throw new Error('the model is not loaded');
		this.busy = true;
		const done = new Promise<T>((resolve, reject) =>
			this.pending.set(m.rid, { resolve: resolve as (v: never) => void, reject, onEvent })
		);
		// structured clone cannot copy reactive proxies
		this.backend.postMessage($state.snapshot(m) as ToWorker);
		return done;
	}

	/** One question: events as they happen, the finished run at the end. */
	ask(
		question: string,
		opts: {
			id: string;
			title?: string;
			family?: string | null;
			truth?: Truth | null;
			lookupAfter?: number | null;
			addition?: { a: string; b: string } | null;
			multiCall?: boolean;
		},
		onEvent: (e: EngineEvent) => void
	): { rid: number; done: Promise<LlmTrace> } {
		const rid = ++this.rid;
		return { rid, done: this.run<LlmTrace>({ type: 'ask', rid, question, opts }, onEvent) };
	}

	poke(
		question: string,
		ctx: LlmCtx,
		register: string,
		step: number,
		forced: number,
		extra: { truth?: Truth | null; from?: string; lookupAfter?: number | null } = {}
	): { rid: number; done: Promise<PokeResult> } {
		const rid = ++this.rid;
		return {
			rid,
			done: this.run<PokeResult>({
				type: 'poke',
				rid,
				question,
				ctx,
				register,
				step,
				forced,
				...extra
			})
		};
	}

	cancel(rid: number) {
		this.backend?.postMessage({ type: 'cancel', rid });
	}

	/** Deletes the weights from this browser's cache (the next load downloads them again). */
	async forget() {
		if (typeof caches === 'undefined') return;
		const c = await caches.open(CACHE);
		for (const r of await cachedKeys(this.base)) await c.delete(r);
		this.cached = false;
	}
}

export const savant = new Savant();
