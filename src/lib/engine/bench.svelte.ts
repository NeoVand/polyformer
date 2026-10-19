/**
 * Shared, page-independent state of a bench: one training worker, a suite of
 * runs on one task, their histories. Lives for the whole session so Explore
 * can inspect the models Compare trained. `getBench()` is the SET bench;
 * `getBench('chase')` is the pointer-chase bench, with its own worker.
 */
import { getTask, type TaskSpec } from '../tasks/index.ts';
import { dealExample, majorityBaseline } from './data.ts';
import { Engine } from './engine.ts';
import { SUITES, type RunSpec, type Suite, type SuiteId } from './runs.ts';
import type {
	Backend,
	DiagramResult,
	EvalMetric,
	InitResult,
	RunInfo,
	StepMetric
} from './protocol.ts';

export type BenchStatus = 'idle' | 'booting' | 'ready' | 'training' | 'pausing' | 'error';

export const TOTAL_STEPS = 4000;
export const BATCH = 128;
export const EVAL_LAYOUTS = 1024;
export const EVAL_EVERY = 50;

/** Columnar history for one run. Plain arrays, mutated in place; `bench.version` signals changes. */
export class RunHistory {
	steps: number[] = [];
	loss: number[] = [];
	accuracy: number[] = [];
	evalSteps: number[] = [];
	evalAccuracy: number[] = [];
	evalLayout: number[] = [];
	evalLoss: number[] = [];
	/** Exponential moving average of the step time, ms. */
	msEma = 0;
	msSamples: number[] = [];

	clear() {
		this.steps.length = 0;
		this.loss.length = 0;
		this.accuracy.length = 0;
		this.evalSteps.length = 0;
		this.evalAccuracy.length = 0;
		this.evalLayout.length = 0;
		this.evalLoss.length = 0;
		this.msEma = 0;
		this.msSamples.length = 0;
	}

	get step() {
		return this.steps.at(-1) ?? 0;
	}

	/** Median step time over the last 200 steps (steady state, excludes compile). */
	get msMedian() {
		const s = this.msSamples.slice(-200).sort((a, b) => a - b);
		return s.length ? s[Math.floor(s.length / 2)] : 0;
	}
}

function backendOverride(): Backend | undefined {
	if (typeof location === 'undefined') return undefined;
	const b = new URLSearchParams(location.search).get('backend');
	return b === 'webgpu' || b === 'wasm' || b === 'cpu' ? b : undefined;
}

export class Bench {
	status = $state<BenchStatus>('idle');
	error = $state<string | null>(null);
	device = $state<Backend | null>(null);
	available = $state<string[]>([]);
	seed = $state(0);
	info = $state.raw<RunInfo[]>([]);
	/** Bumped (at most once per frame) whenever histories change. */
	version = $state(0);
	/** Which runs train when Start is pressed. */
	enabled = $state<Record<string, boolean>>({});
	/** Latest step reached by any run. */
	step = $state(0);
	/** Wall-clock ms spent training in this session. */
	elapsedMs = $state(0);

	readonly suite: Suite;
	readonly task: TaskSpec;
	readonly runs: RunSpec[];
	readonly history: Record<string, RunHistory>;

	constructor(suite: Suite = SUITES.set) {
		this.suite = suite;
		this.task = getTask(suite.task);
		this.runs = suite.runs;
		this.history = Object.fromEntries(suite.runs.map((r) => [r.id, new RunHistory()]));
		for (const r of suite.runs) this.enabled[r.id] = r.defaultEnabled !== false;
	}

	private majorityCache: number | null = null;
	/** Held-out accuracy of always predicting the most frequent class. */
	get majority(): number {
		this.majorityCache ??= majorityBaseline(this.task.id, EVAL_LAYOUTS);
		return this.majorityCache;
	}

	/** A fresh example of this bench's task (Card[] for SET, ChaseInstance for chase). */
	dealExample(seed: number): unknown {
		return dealExample(this.task.id, seed);
	}

	/** DS-PA computation tree for `example` at sequence position `token` (see DiagramResult). */
	async diagram(run: string, example: unknown, token: number, topK = 4): Promise<DiagramResult> {
		await this.ensure();
		if (!this.engine) throw new Error('engine unavailable');
		return this.engine.diagram(run, example, token, topK);
	}

	private engine: Engine | null = null;
	private booting: Promise<void> | null = null;
	private frame = 0;
	private trainingSince = 0;
	/** Increments on reset so late events from an old run are ignored. */
	private generation = 0;

	private bump() {
		if (this.frame) return;
		const raf = typeof requestAnimationFrame === 'function' ? requestAnimationFrame : setTimeout;
		this.frame = raf(() => {
			this.frame = 0;
			this.version++;
			if (this.trainingSince)
				this.elapsedMs = this.elapsedBase + performance.now() - this.trainingSince;
		}) as unknown as number;
	}
	private elapsedBase = 0;

	/** Boot the worker and build every run. Idempotent. */
	ensure(): Promise<void> {
		if (this.booting) return this.booting;
		this.status = 'booting';
		this.error = null;
		this.booting = (async () => {
			try {
				this.engine = new Engine();
				const r: InitResult = await this.engine.init({
					seed: this.seed,
					runs: this.runs,
					totalSteps: TOTAL_STEPS,
					batch: BATCH,
					evalLayouts: EVAL_LAYOUTS,
					evalEvery: EVAL_EVERY,
					backend: backendOverride()
				});
				this.device = r.device;
				this.available = r.available;
				this.info = r.runs;
				this.status = 'ready';
			} catch (e) {
				this.fail(e);
				this.booting = null;
				throw e;
			}
		})();
		return this.booting;
	}

	private fail(e: unknown) {
		this.status = 'error';
		this.error = e instanceof Error ? e.message : String(e);
	}

	runInfo(id: string): RunInfo | undefined {
		return this.info.find((r) => r.id === id);
	}

	/** Train the enabled runs (or `only`) until `until` steps or pause. */
	async start(opts: { only?: string[]; until?: number } = {}) {
		await this.ensure();
		if (!this.engine || this.status === 'training') return;
		const gen = this.generation;
		const ids = opts.only ?? this.runs.filter((r) => this.enabled[r.id]).map((r) => r.id);
		this.status = 'training';
		this.trainingSince = performance.now();
		try {
			await this.engine.train(
				{ runs: ids, until: opts.until ?? TOTAL_STEPS },
				(metrics) => gen === this.generation && this.onStep(metrics),
				(metrics) => gen === this.generation && this.onEval(metrics)
			);
			if (gen === this.generation) this.status = 'ready';
		} catch (e) {
			if (gen === this.generation) this.fail(e);
		} finally {
			if (this.trainingSince) this.elapsedBase += performance.now() - this.trainingSince;
			this.trainingSince = 0;
			this.bump();
		}
	}

	async pause() {
		if (this.status !== 'training' || !this.engine) return;
		this.status = 'pausing';
		await this.engine.stop();
	}

	async reset(seed = this.seed) {
		this.generation++;
		if (this.engine && (this.status === 'training' || this.status === 'pausing'))
			await this.engine.stop();
		this.seed = seed;
		for (const h of Object.values(this.history)) h.clear();
		this.step = 0;
		this.elapsedMs = 0;
		this.elapsedBase = 0;
		this.bump();
		if (!this.engine) return;
		this.status = 'booting';
		try {
			await this.engine.reset(seed);
			this.status = 'ready';
		} catch (e) {
			this.fail(e);
		}
	}

	private onStep(metrics: StepMetric[]) {
		for (const m of metrics) {
			const h = this.history[m.id];
			h.steps.push(m.step);
			h.loss.push(m.loss);
			h.accuracy.push(m.accuracy);
			// first steps include jit compilation; keep them out of the steady-state numbers
			if (m.step > 3) {
				h.msSamples.push(m.ms);
				h.msEma = h.msEma ? h.msEma * 0.95 + m.ms * 0.05 : m.ms;
			}
			if (m.step > this.step) this.step = m.step;
		}
		this.bump();
	}

	private onEval(metrics: EvalMetric[]) {
		for (const m of metrics) {
			const h = this.history[m.id];
			h.evalSteps.push(m.step);
			h.evalAccuracy.push(m.tokenAccuracy);
			h.evalLayout.push(m.layoutAccuracy);
			h.evalLoss.push(m.loss);
		}
		this.bump();
	}

	get engineHandle(): Engine | null {
		return this.engine;
	}
}

/** Session-wide benches, one per suite. Created lazily; only ever touched in the browser. */
const instances: Partial<Record<SuiteId, Bench>> = {};
export function getBench(suite: SuiteId = 'set'): Bench {
	return (instances[suite] ??= new Bench(SUITES[suite]));
}
