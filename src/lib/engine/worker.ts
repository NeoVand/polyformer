/// <reference lib="webworker" />
/**
 * Training worker. Owns jax-js, every model's parameters and optimizer state,
 * and the data. The page drives it over the RPC in engine.ts.
 *
 * All runs on a task see identical batches: the batch for optimizer step s is
 * a pure function of (task, seed, s), so a run trained later still sees the
 * same data.
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
	disposeCapture,
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
import { DECK, LAYOUT_SIZE, type Card } from '../set/cards.ts';
import { deriveSeed } from '../set/rng.ts';
import { getTask, type TaskBatch, type TaskId, type TaskSpec } from '../tasks/index.ts';
import { taskEvalExamples, taskTrainBatch } from './data.ts';
import { summarizeDiagram } from './diagram.ts';
import type {
	Backend,
	DiagramResult,
	EvalMetric,
	InitRequest,
	InitResult,
	Knockout,
	NewtonProbe,
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

type Jitted<F> = F & { dispose(): void };

interface Run {
	spec: RunSpec;
	cfg: ModelConfig;
	task: TaskSpec;
	params: Params;
	state: OptState<Params>;
	solver: FusedStep<Params>;
	evalFn: Jitted<(p: Params, f: Tensor, l: Tensor, w: Tensor) => Tensor>;
	/** Forward with the first layer's captures: [logits, …captured tensors]. */
	probeFn: Jitted<(p: Params, f: Tensor) => Tensor[]>;
	step: number;
}

const ctx = self as unknown as DedicatedWorkerGlobalScope;
const post = (msg: WorkerEvent | WorkerReply, transfer: Transferable[] = []) =>
	ctx.postMessage(msg, transfer);

let device: Backend = 'cpu';
let available: string[] = [];
let opts: InitRequest | null = null;
let runs: Run[] = [];
const evalSets = new Map<TaskId, unknown[]>();
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
		r.evalFn.dispose();
		r.probeFn.dispose();
	}
	runs = [];
}

function buildRun(spec: RunSpec, index: number, seed: number): Run {
	const cfg = defaultConfig(spec.operator, spec.layers, spec.task ?? 'set', spec.options);
	if (spec.dModel) cfg.dModel = spec.dModel;
	if (spec.heads) cfg.heads = spec.heads;
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
		const [first, ...rest] = captures;
		if (first?.weights || cfg.operator === 'newton') {
			if (first?.weights) out.push(first.weights);
			out.push(...(first?.values ?? []));
		} else first?.values?.forEach((v) => v.dispose());
		out.push(...(first?.rounds ?? []), ...(first?.modes ?? []));
		rest.forEach(disposeCapture);
		return out;
	});
	return { spec, cfg, task: getTask(cfg.task), params, state, solver, evalFn, probeFn, step: 0 };
}

function batchTensors(b: TaskBatch, cfg: ModelConfig): [Tensor, Tensor, Tensor] {
	const rows = b.batch * cfg.seqLen;
	return [
		np.array(b.features).reshape([rows, cfg.featureDim]),
		np.array(b.labels).reshape([rows, cfg.classes]),
		np.array(b.weights)
	];
}

async function handleInit(req: Request): Promise<InitResult> {
	const r = req.init as InitRequest;
	await boot(r.backend);
	disposeRuns();
	opts = r;
	runs = r.runs.map((spec, i) => buildRun(spec, i, r.seed));
	await blockUntilReady(runs.map((x) => x.params));
	evalSets.clear();
	for (const t of new Set(runs.map((x) => x.cfg.task)))
		evalSets.set(t, taskEvalExamples(t, r.evalLayouts));
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

function evaluate(run: Run, params: Params = run.params): EvalMetric {
	const examples = evalSets.get(run.cfg.task)!;
	const sums = [0, 0, 0];
	for (let start = 0; start < examples.length; start += EVAL_CHUNK) {
		const chunk = run.task.encode(examples.slice(start, start + EVAL_CHUNK));
		const [f, l, w] = batchTensors(chunk, run.cfg);
		const out = run.evalFn(tree.ref(params), f, l, w).dataSync() as Float32Array;
		for (let i = 0; i < 3; i++) sums[i] += out[i];
	}
	const tokens = examples.length * run.task.lossPositions.length;
	return {
		id: run.spec.id,
		step: run.step,
		loss: sums[0] / tokens,
		tokenAccuracy: sums[1] / tokens,
		layoutAccuracy: sums[2] / examples.length
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
	if (fresh.length) post({ id: req.id, event: 'eval', metrics: fresh.map((r) => evaluate(r)) });

	while (!stopRequested) {
		const pending = active.filter((r) => r.step < until);
		if (!pending.length) break;
		const minStep = Math.min(...pending.map((r) => r.step));
		const cohort = pending.filter((r) => r.step === minStep);
		const metrics: StepMetric[] = [];
		// one batch per task at this step, shared by every run on that task
		for (const task of new Set(cohort.map((r) => r.cfg.task))) {
			const members = cohort.filter((r) => r.cfg.task === task);
			const tensors = batchTensors(
				taskTrainBatch(task, opts!.seed, minStep, opts!.batch),
				members[0].cfg
			);
			for (const r of members) metrics.push(trainOne(r, tensors));
			tensors.forEach((t) => t.dispose());
		}
		post({ id: req.id, event: 'step', metrics });
		const due = cohort.filter((r) => r.step % evalEvery === 0 || r.step === until);
		if (due.length) post({ id: req.id, event: 'eval', metrics: due.map((r) => evaluate(r)) });
		await yieldToEvents();
	}
	return { steps: Object.fromEntries(runs.map((r) => [r.spec.id, r.step])) };
}

function findRun(id: unknown): Run {
	const run = runs.find((r) => r.spec.id === id);
	if (!run) throw new Error(`no run ${String(id)}`);
	return run;
}

function handleProbe(req: Request): ProbeResult & { __transfer: Transferable[] } {
	const run = findRun(req.run);
	const op = getOperator(run.cfg.operator);
	if (op.arity !== 3 || op.id === 'dspa' || run.cfg.task !== 'set')
		throw new Error('probe needs a triple-score operator on SET');
	if (!run.task.isExample(req.layout)) throw new Error('bad layout');
	const [f, , w] = batchTensors(run.task.encode([req.layout]), run.cfg);
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

function newtonRun(id: unknown): Run {
	const run = findRun(id);
	if (run.cfg.operator !== 'newton' || run.cfg.task !== 'match4')
		throw new Error('needs a Newton attention run on Match-4');
	return run;
}

function handleNewton(req: Request): NewtonProbe & { __transfer: Transferable[] } {
	const run = newtonRun(req.run);
	if (!run.task.isExample(req.layout)) throw new Error('bad layout');
	const n = run.cfg.seqLen;
	const size = n - 1;
	const deck = DECK.length;
	const tables: Card[][] = Array.from({ length: deck }, (_, b) =>
		Array.from({ length: size }, (_, p) => DECK[(b + p * size) % deck])
	);
	tables.push(req.layout as Card[]);
	const [f, , w] = batchTensors(run.task.encode(tables), run.cfg);
	w.dispose();
	const [logits, angle, gate] = run.probeFn(tree.ref(run.params), f);
	const lg = (logits.dataSync() as Float32Array).subarray(deck * n * 2);
	const probs = new Float32Array(size);
	for (let p = 0; p < size; p++) {
		const r = p + 1;
		probs[p] = 1 / (1 + Math.exp(lg[r * 2] - lg[r * 2 + 1]));
	}
	const result: NewtonProbe = {
		id: run.spec.id,
		step: run.step,
		heads: run.cfg.heads,
		n,
		dh: run.cfg.dModel / run.cfg.heads,
		order: run.cfg.options.order ?? 4,
		angle: angle.dataSync() as Float32Array,
		gate: gate.dataSync() as Float32Array,
		probs
	};
	return {
		...result,
		__transfer: [result.angle.buffer, result.gate.buffer, probs.buffer]
	};
}

function handleKnockout(req: Request): Knockout {
	const run = newtonRun(req.run);
	const K = run.cfg.options.order ?? 4;
	const dh = run.cfg.dModel / run.cfg.heads;
	const without: number[] = [];
	for (let m = 0; m < K; m++) {
		// a copy of the parameters whose per-arity scale is zero for this arity
		const mask = new Float32Array(K * dh).fill(1).fill(0, m * dh, (m + 1) * dh);
		const base = tree.ref(run.params);
		const [first, ...rest] = base.layers;
		const masked: Params = {
			...base,
			layers: [
				{
					...first,
					extra: {
						...first.extra,
						alpha: first.extra!.alpha.mul(np.array(mask).reshape([K, dh]))
					}
				},
				...rest
			]
		};
		without.push(evaluate(run, masked).tokenAccuracy);
		tree.dispose(masked);
	}
	return { id: run.spec.id, step: run.step, full: evaluate(run).tokenAccuracy, without };
}

function handleDiagram(req: Request): DiagramResult {
	const run = findRun(req.run);
	if (run.cfg.operator !== 'dspa') throw new Error('diagram needs a Feynman attention run');
	if (!run.task.isExample(req.example)) throw new Error(`bad ${run.task.id} example`);
	const n = run.cfg.seqLen;
	const token = Number(req.token);
	if (!Number.isInteger(token) || token < 0 || token >= n) throw new Error('bad token');
	const topK = Math.min(16, Math.max(1, Math.floor(Number(req.topK ?? 4))));
	const R = run.cfg.options.rounds ?? 2;
	const M = run.cfg.options.modes ?? 16;
	const H = run.cfg.heads;
	const C = run.cfg.classes;

	const [f, , w] = batchTensors(run.task.encode([req.example]), run.cfg);
	w.dispose();
	const [logits, ...captured] = run.probeFn(tree.ref(run.params), f);
	const read = captured.map((t) => t.dataSync() as Float32Array);
	const lg = (logits.dataSync() as Float32Array).subarray(token * C, (token + 1) * C);
	const max = Math.max(...lg);
	const ex = Array.from(lg, (x) => Math.exp(x - max));
	const z = ex.reduce((a, b) => a + b, 0);
	return {
		id: run.spec.id,
		step: run.step,
		task: run.cfg.task,
		token,
		n,
		heads: H,
		rounds: R,
		modes: M,
		topK,
		probs: ex.map((x) => x / z),
		target: run.task.targetAt(req.example, token),
		perHead: summarizeDiagram(read.slice(0, R), read.slice(R, 2 * R), H, n, M, token, topK)
	};
}

function handleExport(req: Request) {
	const run = findRun(req.run);
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
	const run = findRun(req.run);
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
	diagram: handleDiagram,
	newton: handleNewton,
	knockout: handleKnockout,
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
	if (
		req.op === 'probe' ||
		req.op === 'diagram' ||
		req.op === 'export' ||
		req.op === 'newton' ||
		req.op === 'knockout'
	) {
		void dispatch(req);
		return;
	}
	if (req.op === 'dispose' || req.op === 'reset' || req.op === 'init') stopRequested = true;
	queue = queue.then(() => dispatch(req));
};
