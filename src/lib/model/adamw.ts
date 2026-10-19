/**
 * AdamW with global-norm clipping, fused into one jitted training step.
 *
 * Matches optax.chain(clip_by_global_norm(c), adamw(lr, wd)) with a
 * warmup + cosine schedule. The learning rate and bias corrections enter as
 * device scalars so the step traces once and never retraces.
 * (@jax-js/optax 0.1.2's Adam cannot run inside jit: it reads its count back.)
 */
import { jit, numpy as np, tree, valueAndGrad, type Array as Tensor } from '@jax-js/jax';

export interface AdamWOptions {
	lr: number;
	b1: number;
	b2: number;
	eps: number;
	weightDecay: number;
	clipNorm: number;
	warmup: number;
	totalSteps: number;
}

export const DEFAULT_ADAMW: AdamWOptions = {
	lr: 2e-3,
	b1: 0.9,
	b2: 0.999,
	eps: 1e-8,
	weightDecay: 0.01,
	clipNorm: 1.0,
	warmup: 200,
	totalSteps: 4000
};

/** Linear warmup from 0, then cosine decay to 0 at totalSteps (optax warmup_cosine_decay_schedule). */
export function learningRate(step: number, o: AdamWOptions): number {
	if (step < o.warmup) return (o.lr * step) / o.warmup;
	const t = Math.min(1, (step - o.warmup) / Math.max(1, o.totalSteps - o.warmup));
	return o.lr * 0.5 * (1 + Math.cos(Math.PI * t));
}

export interface OptState<P> {
	m: P;
	v: P;
	/** Completed updates. */
	t: number;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
type AnyTree = any;

export interface FusedStep<P> {
	init(params: P): OptState<P>;
	/**
	 * One update. Consumes params, state and the batch arrays; returns
	 * metrics [loss, accuracy, gradNorm] and the new params and state.
	 */
	step(params: P, state: OptState<P>, ...batch: Tensor[]): [Tensor, P, OptState<P>];
	dispose(): void;
}

/** `lossFn(params, ...batch)` must return [loss, aux] (aux is a scalar, not differentiated). */
export function fusedAdamW<P extends AnyTree>(
	lossFn: (params: P, ...batch: Tensor[]) => [Tensor, Tensor],
	o: AdamWOptions = DEFAULT_ADAMW
): FusedStep<P> {
	const jitted = jit(
		(
			p: AnyTree,
			m: AnyTree,
			v: AnyTree,
			lr: Tensor,
			c1: Tensor,
			c2: Tensor,
			...batch: Tensor[]
		) => {
			const [[loss, aux], g] = valueAndGrad((pp: AnyTree) => lossFn(pp, ...batch), {
				hasAux: true
			})(tree.ref(p)) as [[Tensor, Tensor], AnyTree];

			// clip by global norm
			const sq = (tree.leaves(g) as Tensor[]).map((leaf) => np.sum(np.square(leaf.ref)));
			const gnorm = np.sqrt(sq.reduce((a, b) => a.add(b)));
			const clip = np.array(o.clipNorm).div(np.maximum(gnorm.ref, o.clipNorm));
			const gc = tree.map((gg: Tensor) => gg.mul(clip.ref), g);
			clip.dispose();

			const m2 = tree.map(
				(mm: Tensor, gg: Tensor) => mm.mul(o.b1).add(gg.mul(1 - o.b1)),
				m,
				tree.ref(gc)
			);
			const v2 = tree.map(
				(vv: Tensor, gg: Tensor) => vv.mul(o.b2).add(np.square(gg).mul(1 - o.b2)),
				v,
				gc
			);
			const p2 = tree.map(
				(pp: Tensor, mm: Tensor, vv: Tensor) => {
					const adam = mm.div(c1.ref).div(np.sqrt(vv.div(c2.ref)).add(o.eps));
					return pp.ref.sub(adam.add(pp.mul(o.weightDecay)).mul(lr.ref));
				},
				p,
				tree.ref(m2),
				tree.ref(v2)
			);
			lr.dispose();
			c1.dispose();
			c2.dispose();
			const metrics = np.stack([loss, aux, gnorm]);
			return [metrics, p2, m2, v2];
		}
	);

	return {
		init(params: P): OptState<P> {
			return {
				m: tree.map((x: Tensor) => np.zerosLike(x), tree.ref(params as AnyTree)) as P,
				v: tree.map((x: Tensor) => np.zerosLike(x), tree.ref(params as AnyTree)) as P,
				t: 0
			};
		},
		step(params: P, state: OptState<P>, ...batch: Tensor[]): [Tensor, P, OptState<P>] {
			const t = state.t + 1;
			const [metrics, p2, m2, v2] = jitted(
				params,
				state.m,
				state.v,
				np.array(learningRate(state.t, o)),
				np.array(1 - Math.pow(o.b1, t)),
				np.array(1 - Math.pow(o.b2, t)),
				...batch
			) as [Tensor, P, P, P];
			return [metrics, p2, { m: m2, v: v2, t }];
		},
		dispose() {
			jitted.dispose();
		}
	};
}
