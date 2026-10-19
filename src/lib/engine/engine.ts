/**
 * Main-thread client for the training worker: a promise RPC with streaming
 * step/eval events. The page never touches a jax-js array.
 */
import type {
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
import type { Card } from '../set/cards.ts';

interface Pending {
	resolve: (v: unknown) => void;
	reject: (e: Error) => void;
	onStep?: (m: StepMetric[]) => void;
	onEval?: (m: EvalMetric[]) => void;
}

export class Engine {
	private worker: Worker;
	private pending = new Map<number, Pending>();
	private nextId = 1;
	private closed = false;

	constructor() {
		this.worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
		this.worker.onmessage = (e: MessageEvent<WorkerEvent | WorkerReply>) => this.onMessage(e.data);
		this.worker.onerror = (e) => this.shutdown(new Error(e.message || 'worker error'));
		this.worker.onmessageerror = () =>
			this.shutdown(new Error('worker message could not be decoded'));
	}

	private onMessage(msg: WorkerEvent | WorkerReply) {
		const p = this.pending.get(msg.id);
		if (!p) return;
		if ('event' in msg) {
			if (msg.event === 'step') p.onStep?.(msg.metrics);
			else if (msg.event === 'eval') p.onEval?.(msg.metrics);
			return;
		}
		this.pending.delete(msg.id);
		if (msg.ok) p.resolve(msg.result);
		else p.reject(new Error(msg.error));
	}

	private shutdown(error: Error) {
		this.closed = true;
		for (const [, p] of this.pending) p.reject(error);
		this.pending.clear();
		this.worker.terminate();
	}

	private call<T>(
		op: string,
		payload: Record<string, unknown> = {},
		extra: Omit<Pending, 'resolve' | 'reject'> = {},
		transfer: Transferable[] = []
	): Promise<T> {
		if (this.closed) return Promise.reject(new Error('engine closed'));
		const id = this.nextId++;
		return new Promise<T>((resolve, reject) => {
			this.pending.set(id, { resolve: resolve as (v: unknown) => void, reject, ...extra });
			this.worker.postMessage({ id, op, ...payload }, transfer);
		});
	}

	init(req: InitRequest): Promise<InitResult> {
		return this.call('init', { init: req });
	}

	/** Train the given runs up to `until` steps; resolves when done or paused. */
	train(
		opts: { runs?: string[]; until?: number },
		onStep: (m: StepMetric[]) => void,
		onEval: (m: EvalMetric[]) => void
	): Promise<{ steps: Record<string, number> }> {
		return this.call('train', opts, { onStep, onEval });
	}

	/** Ask an in-flight train() to return after its current step. */
	stop(): Promise<void> {
		return this.call('stop');
	}

	reset(seed: number): Promise<{ seed: number }> {
		return this.call('reset', { seed });
	}

	probe(run: string, layout: Card[]): Promise<ProbeResult> {
		return this.call('probe', { run, layout: layout.map((c) => [...c]) });
	}

	/**
	 * Feynman attention computation tree for one example and one token (a sequence position,
	 * e.g. the chase query at CHASE_QUERY_POS or a SET card at 1…12). `example`
	 * is the task's plain data: a Card[] layout for SET, a ChaseInstance for chase.
	 */
	diagram(run: string, example: unknown, token: number, topK = 4): Promise<DiagramResult> {
		return this.call('diagram', { run, example, token, topK });
	}

	/** A Newton attention run's phases for every card of the deck, and its view of `layout`. */
	newton(run: string, layout: Card[]): Promise<NewtonProbe> {
		return this.call('newton', { run, layout: layout.map((c) => [...c]) });
	}

	/** Held-out accuracy of a Newton attention run with each arity switched off in turn. */
	knockout(run: string): Promise<Knockout> {
		return this.call('knockout', { run });
	}

	exportWeights(run: string): Promise<{ weights: Float32Array; step: number }> {
		return this.call('export', { run });
	}

	loadWeights(run: string, weights: ArrayBuffer, step: number): Promise<{ step: number }> {
		return this.call('load', { run, weights, step }, {}, [weights]);
	}

	async dispose(): Promise<void> {
		if (this.closed) return;
		try {
			await Promise.race([this.call('dispose'), new Promise((r) => setTimeout(r, 400))]);
		} catch {
			// best effort; terminate regardless
		}
		this.shutdown(new Error('engine disposed'));
	}
}
