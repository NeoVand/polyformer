/**
 * Savant-4B preview: the model the page runs in the browser. Qwen3-4B with PROMPTBOX's Stage 2g adapter
 * (`s2g-s1/adapter_step750`) merged, exported to ONNX for transformers.js (q4f16: 4-bit weights, fp16 activations).
 */

/** Production weights: the public Hugging Face repo, transformers.js layout (config, tokenizer, onnx/…). */
export const SAVANT_URL = 'https://huggingface.co/mohsenvand/savant-4b-preview/resolve/main/';

/** The model card (licence, provenance); ModelPanel links it as a literal URL. */
export const SAVANT_CARD = 'https://huggingface.co/mohsenvand/savant-4b-preview';

/** `pnpm dev` serves the local export here (vite.config.ts, from ../models/savant-4b-preview). */
export const SAVANT_DEV_URL = '/models/savant-4b-preview/';

/**
 * The Addition suggestion (ARITH_FORMAT number mode). Off until SAVANT_URL points at a model version trained to write
 * the adder: the preview's weights do not. Development builds and the page's test stand-in show it regardless.
 */
export const ARITHMETIC: boolean = false;

export const SAVANT = {
	name: 'Savant-4B preview',
	short: 'Savant-4B',
	dtype: 'q4f16',
	/** what the browser downloads (the q4f16 graph, its two weight files, the tokenizer and configs: 2,844 MB) */
	bytes: 2.844e9,
	adapter: 's2g-s1/adapter_step750',
	base: 'Qwen/Qwen3-4B',
	about:
		"Savant-4B preview: Qwen3-4B with PROMPTBOX's Stage 2g adapter (s2g-s1, step 750) merged, exported to ONNX " +
		'(4-bit weights, fp16 activations) and run by transformers.js on WebGPU in this browser'
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
