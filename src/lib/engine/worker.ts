/// <reference lib="webworker" />
/**
 * Training worker. Owns jax-js, every model's parameters and optimizer state,
 * and the data. The page drives it over the RPC in engine.ts.
 *
 * All runs see identical batches: the batch for optimizer step s is a pure
 * function of (seed, s), so a run trained later still sees the same data.
 */
import {
	blockUntilReady,
	defaultDevice,
	init,
	jit,
	numpy as np,
	tree,
	type Array as Tensor,
	type Device
} from '@jax-js/jax';
import { DEFAULT_ADAMW, fusedAdamW, type FusedStep, type OptState } from '../model/adamw.ts';
import {
	defaultConfig,
	evalSums,
	forward,
	forwardFlops,
	initParams,
	lossAndAccuracy,
	paramCount,
	type ModelConfig,
	type Params
} from '../model/transformer.ts';
import { getOperator } from '../model/operators/index.ts';
import {
	FEATURE_DIM,
	LAYOUT_SIZE,
	SEQ_LEN,
	encodeLayouts,
	type Card,
	type SetBatch
} from '../set/cards.ts';
import { deriveSeed } from '../set/rng.ts';
import { evalBatch, trainBatch } from './data.ts';
import type {
	Backend,
	EvalMetric,
	InitRequest,
	InitResult,
	ProbeResult,
	StepMetric,
	WorkerEvent,
	WorkerReply
} from './protocol.ts';
import type { RunSpec } from './runs.ts';

interface Request {
	id: number;
	op: string;
	[key: string]: unknown;
}

interface Run {
	spec: RunSpec;
	cfg: ModelConfig;
	params: Params;
	state: OptState<Params>;
	solver: FusedStep<Params>;
	evalFn: (p: Params, f: Tensor, l: Tensor, w: Tensor) => Tensor;
	probeFn: (p: Params, f: Tensor) => Tensor[];
	step: number;
}

const ctx = self as unknown as DedicatedWorkerGlobalScope;
const post = (msg: WorkerEvent | WorkerReply, transfer: Transferable[] = []) =>
	ctx.postMessage(msg, transfer);

let device: Backend = 'cpu';
let available: string[] = [];
let opts: InitRequest | null = null;
let runs: Run[] = [];
let evalSet: SetBatch | null = null;
let stopRequested = false;
let booted = false;

const EVAL_CHUNK = 256;

async function boot(force?: Backend) {
	if (booted) return;
	available = await init();
	device =
		force && available.includes(force)
			? force
			: available.includes('webgpu')
				? 'webgpu'
				: available.includes('wasm')
					? 'wasm'
					: 'cpu';
	defaultDevice(device as Device);
	booted = true;
}

function disposeRuns() {
	for (const r of runs) {
		tree.dispose(r.params);
		tree.dispose(r.state.m);
		tree.dispose(r.state.v);
		r.solver.dispose();
		(r.evalFn as unknown as { dispose(): void }).dispose();
		(r.probeFn as unknown as { dispose(): void }).dispose();
	}
	runs = [];
}

function buildRun(spec: RunSpec, index: number, seed: number): Run {
	const cfg = defaultConfig(spec.operator, spec.layers);
	const params = initParams(cfg, deriveSeed(seed, index + 1));
	const solver = fusedAdamW<Params>((p, f, l, w) => lossAndAccuracy(p, cfg, f, l, w), {
		...DEFAULT_ADAMW,
		totalSteps: opts!.totalSteps
	});
	const state = solver.init(params);
	const evalFn = jit((p: Params, f: Tensor, l: Tensor, w: Tensor) => evalSums(p, cfg, f, l, w));
	const probeFn = jit((p: Params, f: Tensor) => {
		const { logits, captures } = forward(p, cfg, f, true);
		const out = [logits];
		const cap = captures[0];
		if (cap) out.push(cap.weights, ...cap.values);
		for (const c of captures.slice(1)) {
			c.weights.dispose();
			c.values.forEach((v) => v.dispose());
		}
		return out;
	});
	return { spec, cfg, params, state, solver, evalFn, probeFn, step: 0 };
}

function batchTensors(b: SetBatch): [Tensor, Tensor, Tensor] {
	const rows = b.batch * SEQ_LEN;
	return [
		np.array(b.features).reshape([rows, FEATURE_DIM]),
		np.array(b.labels).reshape([rows, 2]),
		np.array(b.weights)
	];
}

const batchForStep = (s: number): SetBatch => trainBatch(opts!.seed, s, opts!.batch);

async function handleInit(req: Request): Promise<InitResult> {
	const r = req.init as InitRequest;
	await boot(r.backend);
	disposeRuns();
	opts = r;
	runs = r.runs.map((spec, i) => buildRun(spec, i, r.seed));
	await blockUntilReady(runs.map((x) => x.params));
	evalSet = evalBatch(r.evalLayouts);
	return {
		device,
		available,
		runs: runs.map((x) => ({
			id: x.spec.id,
			params: paramCount(x.params),
			trainFlopsPerStep: 3 * forwardFlops(x.cfg) * r.batch
		}))
	};
}

function trainOne(run: Run, b: [Tensor, Tensor, Tensor]): StepMetric {
	const t0 = performance.now();
	const [metrics, p2, s2] = run.solver.step(run.params, run.state, b[0].ref, b[1].ref, b[2].ref);
	run.params = p2;
	run.state = s2;
	const [loss, accuracy, gradNorm] = metrics.dataSync() as Float32Array;
	run.step += 1;
	return { id: run.spec.id, step: run.step, loss, accuracy, gradNorm, ms: performance.now() - t0 };
}

function evaluate(run: Run): EvalMetric {
	const ev = evalSet!;
	const sums = [0, 0, 0];
	for (let start = 0; start < ev.batch; start += EVAL_CHUNK) {
		const chunk = encodeLayouts(ev.layouts.slice(start, start + EVAL_CHUNK));
		const [f, l, w] = batchTensors(chunk);
		const out = run.evalFn(tree.ref(run.params), f, l, w).dataSync() as Float32Array;
		for (let i = 0; i < 3; i++) sums[i] += out[i];
	}
	const tokens = ev.batch * LAYOUT_SIZE;
	return {
		id: run.spec.id,
		step: run.step,
		loss: sums[0] / tokens,
		tokenAccuracy: sums[1] / tokens,
		layoutAccuracy: sums[2] / ev.batch
	};
}

const yieldToEvents = () => new Promise<void>((resolve) => setTimeout(resolve, 0));

async function handleTrain(req: Request) {
	const ids = (req.runs as string[] | undefined) ?? runs.map((r) => r.spec.id);
	const until = Math.min(Number(req.until ?? opts!.totalSteps), opts!.totalSteps);
	const active = runs.filter((r) => ids.includes(r.spec.id));
	const evalEvery = opts!.evalEvery;
	stopRequested = false;

	// Baseline evaluation before the first step, so curves start at chance.
	const fresh = active.filter((r) => r.step === 0);
	if (fresh.length) post({ id: req.id, event: 'eval', metrics: fresh.map(evaluate) });

	while (!stopRequested) {
		const pending = active.filter((r) => r.step < until);
		if (!pending.length) break;
		const minStep = Math.min(...pending.map((r) => r.step));
		const cohort = pending.filter((r) => r.step === minStep);
		const tensors = batchTensors(batchForStep(minStep));
		const metrics = cohort.map((r) => trainOne(r, tensors));
		tensors.forEach((t) => t.dispose());
		post({ id: req.id, event: 'step', metrics });
		const due = cohort.filter((r) => r.step % evalEvery === 0 || r.step === until);
		if (due.length) post({ id: req.id, event: 'eval', metrics: due.map(evaluate) });
		await yieldToEvents();
	}
	return { steps: Object.fromEntries(runs.map((r) => [r.spec.id, r.step])) };
}

function handleProbe(req: Request): ProbeResult & { __transfer: Transferable[] } {
	const run = runs.find((r) => r.spec.id === req.run);
	if (!run) throw new Error(`no run ${String(req.run)}`);
	if (getOperator(run.cfg.operator).arity !== 3) throw new Error('probe needs a triple operator');
	const layout = req.layout as Card[];
	if (!Array.isArray(layout) || layout.length !== LAYOUT_SIZE) throw new Error('bad layout');
	const [f, , w] = batchTensors(encodeLayouts([layout]));
	w.dispose();
	const [logits, weights, v1, v2] = run.probeFn(tree.ref(run.params), f);
	const lg = logits.dataSync() as Float32Array;
	const probs = new Float32Array(LAYOUT_SIZE);
	for (let p = 0; p < LAYOUT_SIZE; p++) {
		const r = p + 1;
		probs[p] = 1 / (1 + Math.exp(lg[r * 2] - lg[r * 2 + 1]));
	}
	const result: ProbeResult = {
		id: run.spec.id,
		step: run.step,
		heads: run.cfg.heads,
		n: run.cfg.seqLen,
		dh: run.cfg.dModel / run.cfg.heads,
		weights: weights.dataSync() as Float32Array,
		v1: v1.dataSync() as Float32Array,
		v2: v2.dataSync() as Float32Array,
		probs
	};
	return {
		...result,
		__transfer: [result.weights.buffer, result.v1.buffer, result.v2.buffer, probs.buffer]
	};
}

function handleExport(req: Request) {
	const run = runs.find((r) => r.spec.id === req.run);
	if (!run) throw new Error(`no run ${String(req.run)}`);
	const leaves = tree.leaves(tree.ref(run.params as never)) as Tensor[];
	const parts = leaves.map((l) => l.dataSync() as Float32Array);
	const flat = new Float32Array(parts.reduce((s, p) => s + p.length, 0));
	let off = 0;
	for (const p of parts) {
		flat.set(p, off);
		off += p.length;
	}
	return { weights: flat, step: run.step, __transfer: [flat.buffer] };
}

async function handleLoad(req: Request) {
	const run = runs.find((r) => r.spec.id === req.run);
	if (!run) throw new Error(`no run ${String(req.run)}`);
	const flat = new Float32Array(req.weights as ArrayBuffer);
	const [leaves, def] = tree.flatten(run.params as never) as [Tensor[], unknown];
	let off = 0;
	const next = leaves.map((l) => {
		const size = l.size;
		const arr = np.array(flat.slice(off, off + size)).reshape(l.shape);
		off += size;
		return arr;
	});
	if (off !== flat.length) throw new Error('checkpoint size mismatch');
	tree.dispose(run.params);
	tree.dispose(run.state.m);
	tree.dispose(run.state.v);
	run.params = tree.unflatten(def as never, next) as unknown as Params;
	run.state = run.solver.init(run.params);
	run.step = Number(req.step ?? 0);
	await blockUntilReady(run.params);
	return { step: run.step };
}

async function handleReset(req: Request) {
	if (!opts) throw new Error('reset before init');
	opts = { ...opts, seed: Number(req.seed ?? opts.seed) };
	const keep = runs.map((r) => r.spec);
	disposeRuns();
	runs = keep.map((spec, i) => buildRun(spec, i, opts!.seed));
	await blockUntilReady(runs.map((x) => x.params));
	return { seed: opts.seed };
}

const handlers: Record<string, (req: Request) => unknown> = {
	init: handleInit,
	train: handleTrain,
	probe: handleProbe,
	export: handleExport,
	load: handleLoad,
	reset: handleReset,
	dispose: () => {
		disposeRuns();
		return {};
	}
};

async function dispatch(req: Request) {
	try {
		const handler = handlers[req.op];
		if (!handler) throw new Error(`unknown op: ${req.op}`);
		const result = (await handler(req)) as Record<string, unknown> & {
			__transfer?: Transferable[];
		};
		const transfer = result?.__transfer ?? [];
		if (result) delete result.__transfer;
		post({ id: req.id, ok: true, result }, transfer);
	} catch (err) {
		post({
			id: req.id,
			ok: false,
			error: err instanceof Error ? `${err.name}: ${err.message}` : String(err)
		});
	}
}

// Model operations run one at a time; stop bypasses the queue.
let queue = Promise.resolve();
ctx.onmessage = (e: MessageEvent<Request>) => {
	const req = e.data;
	if (req.op === 'stop') {
		stopRequested = true;
		post({ id: req.id, ok: true, result: {} });
		return;
	}
	// Probes only read weights and run synchronously, so they may interleave
	// with a training loop between steps instead of waiting for it to finish.
	if (req.op === 'probe' || req.op === 'export') {
		void dispatch(req);
		return;
	}
	if (req.op === 'dispose' || req.op === 'reset' || req.op === 'init') stopRequested = true;
	queue = queue.then(() => dispatch(req));
};
