/**
 * Savant-4B preview r2: the model the page runs in the browser. Qwen3-4B with PROMPTBOX's final adapter
 * (`rlg-ours/adapter_iter60`: stage 2g, the stage 2r language repair, then RL) merged, exported to ONNX for
 * transformers.js (q4f16: 4-bit weights with the v and down projections at 8 bits, fp16 activations).
 */

/**
 * Production weights: the public Hugging Face repo, transformers.js layout (config, tokenizer, onnx/…), pinned to the
 * r2 commit so a browser never mixes files from two versions in its cache.
 */
export const SAVANT_REVISION = '1d29721c6b2a1ee4f16f2828c21f59b5abee1df0';
export const SAVANT_URL = `https://huggingface.co/mohsenvand/savant-4b-preview/resolve/${SAVANT_REVISION}/`;

/** The model card (licence, provenance); ModelPanel links it as a literal URL. */
export const SAVANT_CARD = 'https://huggingface.co/mohsenvand/savant-4b-preview';

/** `pnpm dev` serves the local export here (vite.config.ts, from ../models/savant-4b-preview). */
export const SAVANT_DEV_URL = '/models/savant-4b-preview-r2/';

/**
 * The Addition suggestion (ARITH_FORMAT number mode). Off until SAVANT_URL points at a model version trained to write
 * the adder: the preview's weights do not. Development builds and the page's test stand-in show it regardless.
 */
export const ARITHMETIC: boolean = false;

export const SAVANT = {
	name: 'Savant-4B preview r2',
	short: 'Savant-4B',
	dtype: 'q4f16',
	/** what the browser downloads (the q4f16 graph, its two weight files, the tokenizer and configs: 3,340 MB) */
	bytes: 3.34e9,
	adapter: 'rlg-ours/adapter_iter60',
	base: 'Qwen/Qwen3-4B',
	about:
		"Savant-4B preview r2: Qwen3-4B with PROMPTBOX's final adapter (rlg-ours, RL iteration 60) merged, exported " +
		'to ONNX (4-bit weights, v and down projections 8-bit, fp16 activations) and run by transformers.js on WebGPU ' +
		'in this browser'
} as const;

/** Where this build loads the weights from: $VITE_SAVANT_URL, else the local export in dev, else Hugging Face. */
export function savantUrl(): string {
	const forced = import.meta.env.VITE_SAVANT_URL as string | undefined;
	if (forced) return forced;
	return import.meta.env.DEV ? SAVANT_DEV_URL : SAVANT_URL;
}

export const gb = (bytes: number) => `${(bytes / 1e9).toFixed(1)} GB`;

/** The GPU's name as the browser gives it: its description, else "Apple GPU (metal-3)". */
export function gpuLabel(i: { vendor?: string; architecture?: string; description?: string }) {
	if (i.description) return i.description;
	const vendor = i.vendor ? i.vendor[0].toUpperCase() + i.vendor.slice(1) : '';
	if (!vendor) return null;
	return i.architecture ? `${vendor} GPU (${i.architecture})` : `${vendor} GPU`;
}
