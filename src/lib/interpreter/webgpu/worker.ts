/// <reference lib="webworker" />
/**
 * The worker that holds Savant-4B: it loads the weights with transformers.js on WebGPU, runs the pinned loop
 * (engine.ts) one question at a time, and posts every event to the page, which stays free to draw.
 */
import { SAVANT, gpuLabel } from './config.ts';
import { Cancelled, Engine, PROMPTBOX_COMMIT, type HostInfo, type ModelInfo } from './engine.ts';
import type { FromWorker, ToWorker } from './protocol.ts';
import { loadTransformers } from './transformers-lm.ts';

declare const self: DedicatedWorkerGlobalScope;

let engine: Engine | null = null;
let loading = false;
const controllers = new Map<number, AbortController>();
const post = (m: FromWorker) => self.postMessage(m);
const message = (e: unknown) => (e instanceof Error ? e.message : String(e));

/** The GPU as the browser names it (vendor and architecture; some browsers hide more). */
export async function gpuName(): Promise<string | null> {
	const a = await navigator.gpu?.requestAdapter({ powerPreference: 'high-performance' });
	const i = a?.info;
	if (!i) return null;
	return gpuLabel(i);
}

/**
 * One short pass through every shape the loop uses (a prefill, a one-token step, a two-token block over a small
 * cache), so the runtime compiles its GPU kernels while the page still says "preparing" and the first question
 * does not pay for it.
 */
async function warm(lm: Awaited<ReturnType<typeof loadTransformers>>) {
	const ids = warmIds(lm).slice(0, 24);
	const a = await lm.lm.forward(ids, null, true);
	const b = await lm.lm.forward([ids[0]], a.past, true);
	await lm.lm.forward([ids[1], ids[2]], b.past, false);
	a.past?.dispose();
	b.past?.dispose();
}
const warmIds = (m: Awaited<ReturnType<typeof loadTransformers>>) =>
	m.tok.encode('<|im_start|>user\nWhich spot hides the ball after the swaps AB BC AC?<|im_end|>\n');

async function load(m: Extract<ToWorker, { type: 'load' }>) {
	if (engine || loading) return;
	loading = true;
	const t0 = performance.now();
	try {
		const loaded = await loadTransformers({
			base: m.base,
			device: m.device,
			dtype: m.dtype,
			onProgress: (progress) => post({ type: 'progress', progress })
		});
		await warm(loaded).catch(() => {});
		const gpu = m.device === 'webgpu' ? await gpuName().catch(() => null) : null;
		const model: ModelInfo = {
			name: SAVANT.name,
			compile_adapter: SAVANT.adapter,
			executor_adapter: SAVANT.adapter,
			adapter_sha256: { compile: '', executor: '' },
			tokenizer_sha256: '',
			promptbox_commit: PROMPTBOX_COMMIT,
			about: SAVANT.about
		};
		const host: HostInfo = {
			gpu: gpu ?? (m.device === 'webgpu' ? 'this browser’s GPU' : 'CPU'),
			cpu: null,
			avx512f: null,
			platform: navigator.platform || null,
			runtime: `transformers.js 4.3.1, ONNX Runtime Web, ${m.device === 'webgpu' ? 'WebGPU' : 'CPU'}`,
			dtype: m.dtype
		};
		engine = new Engine(loaded.lm, loaded.tok, { nl: loaded.nl, stop: loaded.stop }, model, host);
		post({
			type: 'loaded',
			loaded: {
				model,
				host,
				device: loaded.device,
				dtype: loaded.dtype,
				lastOnly: loaded.lm.lastOnly,
				seconds: Math.round(performance.now() - t0) / 1000
			}
		});
	} catch (e) {
		post({ type: 'load-error', error: message(e) });
	} finally {
		loading = false;
	}
}

self.onmessage = async (ev: MessageEvent<ToWorker>) => {
	const m = ev.data;
	if (m.type === 'load') return load(m);
	if (m.type === 'cancel') return controllers.get(m.rid)?.abort();
	if (!engine) {
		post({ type: 'failed', rid: m.rid, error: 'the model is not loaded', cancelled: false });
		return;
	}
	const ctl = new AbortController();
	controllers.set(m.rid, ctl);
	try {
		if (m.type === 'ask') {
			const trace = await engine.ask(m.question, { ...m.opts, signal: ctl.signal }, (event) =>
				post({ type: 'event', rid: m.rid, event })
			);
			post({ type: 'answered', rid: m.rid, trace });
		} else if (m.type === 'poke') {
			const poke = await engine.poke(
				m.question,
				m.ctx,
				m.register,
				m.step,
				m.forced,
				{ truth: m.truth, signal: ctl.signal, from: m.from, lookupAfter: m.lookupAfter },
				(event) => post({ type: 'event', rid: m.rid, event })
			);
			post({ type: 'poked', rid: m.rid, poke });
		}
	} catch (e) {
		post({ type: 'failed', rid: m.rid, error: message(e), cancelled: e instanceof Cancelled });
	} finally {
		controllers.delete(m.rid);
	}
};
