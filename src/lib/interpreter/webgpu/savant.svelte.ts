/**
 * Savant in this browser, from the page's side: which model the visitor picked, whether the browser can run it
 * (WebGPU, 16-bit shaders, buffer sizes), whether that model's weights are already cached, the download, and one
 * question or poke at a time in the worker. Reactive, so the chat and the panels follow it.
 */
import {
	browserStorage,
	gb,
	gpuLabel,
	modelById,
	modelUrl,
	modelsOffered,
	readModelChoice,
	resolveModelId,
	splitCache,
	writeModelChoice,
	type SavantModel
} from './config.ts';
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

/** What the GPU probe found, before the sentences that name the selected model. */
interface GpuFacts {
	kind: 'ok' | 'no-webgpu' | 'no-adapter' | 'no-f16';
	adapter: string | null;
	mobile: boolean;
	buffer: number | null;
	stub: boolean;
}

export class Stopped extends Error {
	constructor() {
		super('stopped');
	}
}

const CACHE = 'transformers-cache';
/** the largest single weight (the tied embedding, fp16): a GPU must hold it in one buffer */
const BIGGEST_TENSOR = 151936 * 2560 * 2;

function describeGpu(f: GpuFacts, model: SavantModel): GpuCheck {
	const mobile = f.mobile;
	if (f.stub && f.kind === 'no-webgpu')
		return { ok: false, reason: 'This browser has no WebGPU.', warn: null, adapter: null, mobile };
	if (f.stub) return { ok: true, reason: null, warn: null, adapter: f.adapter, mobile };
	if (f.kind === 'no-webgpu')
		return {
			ok: false,
			reason:
				'This browser has no WebGPU. Chrome or Edge 113+ on a desktop has it; so do Safari 26 and Firefox 141 on some systems.',
			warn: null,
			adapter: null,
			mobile
		};
	if (f.kind === 'no-adapter')
		return {
			ok: false,
			reason:
				'WebGPU is here but offers no GPU (it may be switched off, or this GPU is blocklisted).',
			warn: null,
			adapter: null,
			mobile
		};
	if (f.kind === 'no-f16')
		return {
			ok: false,
			reason: `This GPU (${f.adapter}) offers no 16-bit floats in shaders (shader-f16), which ${model.short}’s weights need.`,
			warn: null,
			adapter: f.adapter,
			mobile
		};
	const big = f.buffer ?? 0;
	const warn =
		big && big < BIGGEST_TENSOR
			? `This GPU’s largest buffer is ${Math.round(big / 1e6)} MB; the model’s largest weight is ${Math.round(BIGGEST_TENSOR / 1e6)} MB, so loading may fail.`
			: mobile
				? `${model.short} is a ${gb(model.bytes)} download and needs a few GB of GPU memory: it is made for desktop GPUs.`
				: null;
	return { ok: true, reason: null, warn, adapter: f.adapter, mobile };
}

async function probeGpu(): Promise<GpuFacts> {
	const mobile =
		typeof navigator !== 'undefined' && /Android|iPhone|iPad|Mobile/i.test(navigator.userAgent);
	const stub = stubOf();
	if (stub)
		return stub.gpu
			? { kind: 'ok', adapter: stub.gpu, mobile, buffer: null, stub: true }
			: { kind: 'no-webgpu', adapter: null, mobile, buffer: null, stub: true };
	const gpu = typeof navigator !== 'undefined' ? navigator.gpu : undefined;
	if (!gpu) return { kind: 'no-webgpu', adapter: null, mobile, buffer: null, stub: false };
	const a = await gpu.requestAdapter({ powerPreference: 'high-performance' }).catch(() => null);
	if (!a) return { kind: 'no-adapter', adapter: null, mobile, buffer: null, stub: false };
	const i: Partial<GPUAdapterInfo> = a.info ?? {};
	const adapter = gpuLabel(i) ?? 'an unnamed GPU';
	if (!a.features.has('shader-f16'))
		return { kind: 'no-f16', adapter, mobile, buffer: null, stub: false };
	const big = Math.min(a.limits.maxBufferSize, a.limits.maxStorageBufferBindingSize);
	return { kind: 'ok', adapter, mobile, buffer: big || null, stub: false };
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
	/** the selected model's weights are in this browser's cache already */
	cached = $state<boolean | null>(null);
	/** a question or a poke is running */
	busy = $state(false);
	/** download speed, bytes per second over the last few seconds */
	rate = $state(0);
	/** which model the visitor picked; r3 until the saved choice is read on the client */
	modelId = $state(modelById('r3').id);

	private backend: Backend | null = null;
	private samples: { t: number; b: number }[] = [];
	private readyListeners = new Set<() => void>();
	private facts: GpuFacts | null = null;
	/** cache presence per model id, filled by check */
	private knownCache: Record<string, boolean> = {};

	/** Calls `fn` each time the model becomes ready; returns the unsubscribe. */
	onReady(fn: () => void) {
		this.readyListeners.add(fn);
		return () => this.readyListeners.delete(fn);
	}
	private pending = new Map<number, Pending>();
	private rid = 0;

	get model(): SavantModel {
		return modelById(this.modelId);
	}

	private publishGpu() {
		this.gpu = this.facts ? describeGpu(this.facts, this.model) : null;
	}

	/** The models the picker can show right now. The stand-in also shows one whose weights are not uploaded. */
	offered(): SavantModel[] {
		return modelsOffered(stubOf() !== null);
	}

	/** Applies the choice saved in this browser. The page calls it once the document exists, so SSR stays on r3. */
	restoreChoice() {
		const id = resolveModelId(readModelChoice(browserStorage()), this.offered());
		if (id === this.modelId || this.status === 'loading') return;
		this.modelId = id;
		if (id in this.knownCache) this.cached = this.knownCache[id];
		this.publishGpu();
	}

	/** Picks a model. A model that is loading, or busy with a question, stays put. The choice is remembered. */
	select(id: string) {
		if (!this.offered().some((m) => m.id === id)) return;
		if (this.status === 'loading' || this.busy) return;
		writeModelChoice(browserStorage(), id);
		if (id === this.modelId) return;
		const live = this.backend !== null;
		if (live) this.release();
		this.modelId = id;
		this.cached = id in this.knownCache ? this.knownCache[id] : null;
		this.error = null;
		this.publishGpu();
		if (live || this.status === 'error' || this.status === 'ready')
			this.status = this.gpu?.ok ? 'can-load' : 'unsupported';
	}

	private release() {
		for (const p of this.pending.values()) p.reject(new Stopped());
		this.pending.clear();
		this.busy = false;
		this.backend?.terminate();
		this.backend = null;
		this.loaded = null;
		this.progress = null;
		this.samples = [];
		this.rate = 0;
	}

	/** WebGPU and each offered model's cache, once; safe to call again. */
	async check() {
		if (this.status !== 'idle') return;
		this.status = 'checking';
		this.facts = await probeGpu();
		this.publishGpu();
		const stub = stubOf() !== null;
		for (const m of this.offered())
			this.knownCache[m.id] = stub
				? false
				: (await cachedKeys(modelUrl(m))).some((r) => r.url.includes('onnx/'));
		this.cached = this.knownCache[this.modelId] ?? false;
		this.status = this.gpu?.ok ? 'can-load' : 'unsupported';
	}

	load() {
		if (this.status === 'loading' || this.status === 'ready') return;
		const model = this.model;
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
		backend.postMessage({
			type: 'load',
			base: modelUrl(model),
			dtype: model.dtype,
			device: 'webgpu',
			model: { name: model.name, adapter: model.adapter, about: model.about }
		});
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
			this.knownCache[this.modelId] = true;
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

	/** Deletes the selected model's weights from this browser's cache. The other model's files stay. */
	async forget() {
		const prefix = absolute(modelUrl(this.model));
		if (typeof caches === 'undefined') {
			this.knownCache[this.modelId] = false;
			this.cached = false;
			return;
		}
		try {
			const c = await caches.open(CACHE);
			const keys = (await c.keys()).map((r) => r.url);
			for (const url of splitCache(keys, prefix).drop) await c.delete(url);
		} catch {
			/* a cache the browser will not open; the button has still done what it can */
		}
		this.knownCache[this.modelId] = false;
		this.cached = false;
	}
}

export const savant = new Savant();
