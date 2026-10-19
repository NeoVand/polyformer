/**
 * A small pre-LN transformer for per-token SET classification, with a
 * pluggable attention operator.
 *
 * Input: sum of four attribute embedding tables (one matmul against the
 * concatenated one-hot features) plus learned positional embeddings.
 * Block: x += Wo·attn(LN x); x += MLP(LN x) with a 4× GELU MLP. Biases on all
 * projections. Head: LN, then 2 logits per token.
 *
 * All arrays follow jax-js move semantics: every function consumes its array
 * arguments unless noted.
 */
import { numpy as np, nn, tree, type Array as Tensor } from '@jax-js/jax';
import { FEATURE_DIM, SEQ_LEN } from '../set/cards.ts';
import { gaussian, mulberry32 } from '../set/rng.ts';
import { getOperator, type AttentionOperator, type OperatorId } from './operators/index.ts';

export interface ModelConfig {
	operator: OperatorId;
	layers: number;
	dModel: number;
	heads: number;
	/** MLP hidden width multiplier. */
	mlpRatio: number;
	seqLen: number;
	featureDim: number;
	classes: number;
}

export function defaultConfig(operator: OperatorId, layers = 1): ModelConfig {
	return {
		operator,
		layers,
		dModel: 64,
		heads: 4,
		mlpRatio: 4,
		seqLen: SEQ_LEN,
		featureDim: FEATURE_DIM,
		classes: 2
	};
}

export interface Dense {
	w: Tensor;
	b: Tensor;
}
export interface Norm {
	g: Tensor;
	b: Tensor;
}
export interface Layer {
	ln1: Norm;
	proj: Record<string, Dense>;
	out: Dense;
	ln2: Norm;
	fc1: Dense;
	fc2: Dense;
}
export interface Params {
	emb: Tensor;
	pos: Tensor;
	layers: Layer[];
	lnf: Norm;
	head: Dense;
}

// ── initialisation ──────────────────────────────────────────────────────────

/** Deterministic host-side init: the same seed gives the same weights on every backend. */
export function initParams(cfg: ModelConfig, seed: number): Params {
	const rng = mulberry32(seed);
	const normal = (shape: number[], std: number) => {
		const size = shape.reduce((a, b) => a * b, 1);
		const buf = new Float32Array(size);
		for (let i = 0; i < size; i++) buf[i] = gaussian(rng) * std;
		return np.array(buf).reshape(shape);
	};
	const dense = (fanIn: number, fanOut: number): Dense => ({
		w: normal([fanIn, fanOut], 1 / Math.sqrt(fanIn)),
		b: np.zeros([fanOut])
	});
	const norm = (d: number): Norm => ({ g: np.ones([d]), b: np.zeros([d]) });
	const D = cfg.dModel;
	const op = getOperator(cfg.operator);
	const layers: Layer[] = [];
	for (let l = 0; l < cfg.layers; l++) {
		const proj: Record<string, Dense> = {};
		for (const name of op.projections) proj[name] = dense(D, D);
		layers.push({
			ln1: norm(D),
			proj,
			out: dense(D, D),
			ln2: norm(D),
			fc1: dense(D, cfg.mlpRatio * D),
			fc2: dense(cfg.mlpRatio * D, D)
		});
	}
	return {
		emb: normal([cfg.featureDim, D], 1 / Math.sqrt(D)),
		pos: normal([cfg.seqLen, D], 0.02),
		layers,
		lnf: norm(D),
		head: dense(D, cfg.classes)
	};
}

export function paramCount(params: Params): number {
	return (tree.leaves(params as never) as Tensor[]).reduce((s, l) => s + l.size, 0);
}

// ── forward ─────────────────────────────────────────────────────────────────

function linear(x: Tensor, p: Dense): Tensor {
	return np.dot(x, p.w).add(p.b);
}

function layerNorm(x: Tensor, p: Norm): Tensor {
	const mean = np.mean(x.ref, -1, { keepdims: true });
	const centred = x.sub(mean);
	const variance = np.mean(np.square(centred.ref), -1, { keepdims: true });
	return centred
		.div(np.sqrt(variance.add(1e-5)))
		.mul(p.g)
		.add(p.b);
}

export interface LayerCapture {
	/** [B, H, n, n] or [B, H, n, n·n]. */
	weights: Tensor;
	/** Value projections, each [B, H, n, dh]. */
	values: Tensor[];
}

/** Rows are [B·n, D]; returns per-token logits [B·n, classes]. Consumes params and features. */
export function forward(
	params: Params,
	cfg: ModelConfig,
	features: Tensor,
	capture = false
): { logits: Tensor; captures: LayerCapture[] } {
	const op: AttentionOperator = getOperator(cfg.operator);
	const n = cfg.seqLen;
	const D = cfg.dModel;
	const H = cfg.heads;
	const dh = D / H;
	const B = features.shape[0] / n;
	const captures: LayerCapture[] = [];

	let x = np
		.dot(features, params.emb)
		.reshape([B, n, D])
		.add(params.pos)
		.reshape([B * n, D]);

	for (const layer of params.layers) {
		const h = layerNorm(x.ref, layer.ln1);
		const proj: Record<string, Tensor> = {};
		op.projections.forEach((name, idx) => {
			const last = idx === op.projections.length - 1;
			proj[name] = linear(last ? h : h.ref, layer.proj[name])
				.reshape([B, n, H, dh])
				.transpose([0, 2, 1, 3]);
		});
		const r = op.attend(proj, { B, H, n, dh }, capture);
		if (capture && r.weights && r.values) captures.push({ weights: r.weights, values: r.values });
		const y = r.y.transpose([0, 2, 1, 3]).reshape([B * n, D]);
		x = x.add(linear(y, layer.out));
		const h2 = layerNorm(x.ref, layer.ln2);
		x = x.add(linear(nn.gelu(linear(h2, layer.fc1)), layer.fc2));
	}
	const logits = linear(layerNorm(x, params.lnf), params.head);
	return { logits, captures };
}

/**
 * Weighted token cross-entropy and accuracy. Returns [loss, accuracy]; the
 * accuracy is auxiliary (not differentiated). Consumes everything.
 */
export function lossAndAccuracy(
	params: Params,
	cfg: ModelConfig,
	features: Tensor,
	labels: Tensor,
	weights: Tensor
): [Tensor, Tensor] {
	const { logits } = forward(params, cfg, features);
	const total = np.sum(weights.ref);
	const nll = np.sum(nn.logSoftmax(logits.ref, -1).mul(labels.ref), -1).neg();
	const loss = np.sum(nll.mul(weights.ref)).div(total.ref);
	// two classes: predict 1 iff logit₁ > logit₀
	const margin = logits.ref.slice([], 1).sub(logits.slice([], 0));
	const predOne = np.greater(margin, 0);
	const correct = np.where(predOne, labels.ref.slice([], 1), labels.slice([], 0));
	const accuracy = np.sum(correct.mul(weights)).div(total);
	return [loss, accuracy];
}

/**
 * Held-out metrics as sums so chunks can be pooled:
 * [Σ token NLL, Σ correct tokens, Σ fully-correct layouts]. Consumes everything.
 */
export function evalSums(
	params: Params,
	cfg: ModelConfig,
	features: Tensor,
	labels: Tensor,
	weights: Tensor
): Tensor {
	const n = cfg.seqLen;
	const { logits } = forward(params, cfg, features);
	const nll = np.sum(nn.logSoftmax(logits.ref, -1).mul(labels.ref), -1).neg();
	const lossSum = np.sum(nll.mul(weights.ref));
	const margin = logits.ref.slice([], 1).sub(logits.slice([], 0));
	const correct = np.where(np.greater(margin, 0), labels.ref.slice([], 1), labels.slice([], 0));
	const counted = correct.mul(weights.ref);
	const correctSum = np.sum(counted.ref);
	// BOS rows count as correct so a layout is right iff all 12 cards are
	const perLayout = np.min(counted.add(np.ones(weights.shape).sub(weights)).reshape([-1, n]), 1);
	return np.stack([lossSum, correctSum, np.sum(perLayout)]);
}

/** Forward FLOPs for one sequence. Training ≈ 3× this. */
export function forwardFlops(cfg: ModelConfig): number {
	const op = getOperator(cfg.operator);
	const n = cfg.seqLen;
	const D = cfg.dModel;
	const H = cfg.heads;
	const dh = D / H;
	const F = cfg.mlpRatio * D;
	const perLayer =
		2 * n * D * D * (op.projections.length + 1) + // projections + output
		2 * n * D * F * 2 + // MLP
		op.flops(n, H, dh);
	return 2 * n * cfg.featureDim * D + cfg.layers * perLayer + 2 * n * D * cfg.classes;
}
