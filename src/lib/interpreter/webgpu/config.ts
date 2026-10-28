/**
 * The models the interpreter can run, one entry each. The browser cache keys files by revision, so two models never
 * share a file. Savant-4B preview r3 and Savant-4B Loom (preview) are both published and pinned by revision. A model
 * whose repo or revision is UNPUBLISHED is hidden by the picker.
 */

/** The reasoning model's name (Neo, 28 Oct 2026). Every label reads this constant. */
export const REASON_MODEL_NAME = 'Savant-4B Loom (preview)';

/**
 * Placeholder for a repo or revision the orchestrator replaces after upload. A model whose repo or revision is still
 * this value has no weights, and the picker hides it.
 */
export const UNPUBLISHED = 'FILL_AFTER_UPLOAD';

export interface SavantModel {
	id: string;
	name: string;
	short: string;
	/** one line on what this model is good at */
	description: string;
	/** Hugging Face repo (`owner/name`), or {@link UNPUBLISHED} */
	repo: string;
	/** pinned commit, or {@link UNPUBLISHED} */
	revision: string;
	/** `pnpm dev` serves the local export here (vite.config.ts) */
	devUrl: string;
	/** what the browser downloads */
	bytes: number;
	adapter: string;
	dtype: string;
	base: string;
	/** model card; none until the repo exists */
	card: string | null;
	/** calls in the middle of the words (REASON_FORMAT) */
	multiCall: boolean;
	/** the Addition suggestion (ARITH_FORMAT number mode) */
	arithmetic: boolean;
	about: string;
}

export const MODELS: readonly SavantModel[] = [
	{
		id: 'r3',
		name: 'Savant-4B preview r3',
		short: 'Savant-4B',
		description: 'Certified addition and the six task families, one program per question.',
		repo: 'mohsenvand/savant-4b-preview',
		revision: '41b273e33a2251204da47c002f660bb57f173dfc',
		devUrl: '/models/savant-4b-preview-r3/',
		/** the q4f16 graph, its two weight files, the tokenizer and configs: 3,330 MB */
		bytes: 3.33e9,
		adapter: 'arith-s1r2/adapter_step500',
		dtype: 'q4f16',
		base: 'Qwen/Qwen3-4B',
		card: 'https://huggingface.co/mohsenvand/savant-4b-preview',
		multiCall: false,
		arithmetic: true,
		about:
			"Savant-4B preview r3: Qwen3-4B with ARITH's adapter (PROMPTBOX's final adapter continued on certified " +
			'addition, arith-s1r2 step 500) merged, exported ' +
			'to ONNX (4-bit weights, v and down projections 8-bit, fp16 activations) and run by transformers.js on WebGPU ' +
			'in this browser'
	},
	{
		id: 'reason',
		name: REASON_MODEL_NAME,
		short: 'Savant-4B Loom',
		description: 'Reasons in words and calls programs mid-thought.',
		repo: 'mohsenvand/savant-4b-loom-preview',
		revision: 'bf72f6bf462d71a3e0b2e39c3539d964194a96bd',
		devUrl: '/models/savant-4b-loom-preview/',
		/** the q4f16 graph, its two weight files, the tokenizer and configs: 3,344 MB (all 16 files verified by sha256) */
		bytes: 3.34e9,
		adapter: 'reason-s1/adapter_step500',
		dtype: 'q4f16',
		base: 'Qwen/Qwen3-4B',
		card: 'https://huggingface.co/mohsenvand/savant-4b-loom-preview',
		multiCall: true,
		arithmetic: true,
		about:
			`${REASON_MODEL_NAME}: Qwen3-4B with REASON's adapter (ARITH's adapter continued on multi-call reasoning, ` +
			'reason-s1 step 500) merged, exported to ONNX (4-bit weights, v and down projections 8-bit, fp16 activations) ' +
			'and run by transformers.js on WebGPU in this browser. It reasons in words and calls programs mid-thought.'
	}
];

export const DEFAULT_MODEL_ID = 'r3';

/** localStorage key for the visitor's choice. Reads and writes are wrapped in try/catch. */
export const MODEL_CHOICE_KEY = 'polyformer.interpreter.model';

export function modelById(id: string): SavantModel {
	return MODELS.find((m) => m.id === id) ?? MODELS[0];
}

/** Weights exist to download: both the repo and the revision have been filled in. */
export function weightsReady(model: Pick<SavantModel, 'repo' | 'revision'>): boolean {
	return (
		model.repo !== UNPUBLISHED &&
		model.revision !== UNPUBLISHED &&
		model.repo.length > 0 &&
		model.revision.length > 0
	);
}

/**
 * Models the picker shows. An unpublished model stays hidden until its repo and revision are filled. The page's test
 * stand-in passes `allowUnpublished` so the choice can be selected before the upload.
 */
export function modelsOffered(
	allowUnpublished: boolean,
	models: readonly SavantModel[] = MODELS
): SavantModel[] {
	return models.filter((m) => weightsReady(m) || allowUnpublished);
}

export interface UrlEnv {
	dev: boolean;
	/** `$VITE_SAVANT_URL`. Applied to r3 only, so a local override never shares a cache prefix with the other model. */
	forced?: string;
}

const withSlash = (url: string) => (url.endsWith('/') ? url : `${url}/`);

export function hfUrl(repo: string, revision: string): string {
	return `https://huggingface.co/${repo}/resolve/${revision}/`;
}

function runtimeEnv(): UrlEnv {
	return {
		dev: import.meta.env.DEV,
		forced: import.meta.env.VITE_SAVANT_URL || undefined
	};
}

/**
 * Where this build loads one model's weights. In dev, each model has its own path. In production, a published model
 * is its Hugging Face revision. An unpublished model keeps its dev path and is not offered, so nothing fetches it.
 */
export function modelUrl(model: SavantModel, env: UrlEnv = runtimeEnv()): string {
	if (env.forced && model.id === DEFAULT_MODEL_ID) return withSlash(env.forced);
	if (env.dev) return model.devUrl;
	if (weightsReady(model)) return hfUrl(model.repo, model.revision);
	return model.devUrl;
}

export interface ChoiceStore {
	getItem(key: string): string | null;
	setItem(key: string, value: string): void;
}

export function browserStorage(): ChoiceStore | null {
	try {
		if (typeof localStorage === 'undefined') return null;
		return localStorage;
	} catch {
		return null;
	}
}

export function readModelChoice(storage: ChoiceStore | null): string | null {
	if (!storage) return null;
	try {
		return storage.getItem(MODEL_CHOICE_KEY);
	} catch {
		return null;
	}
}

export function writeModelChoice(storage: ChoiceStore | null, id: string): void {
	if (!storage) return;
	try {
		storage.setItem(MODEL_CHOICE_KEY, id);
	} catch {
		/* private mode, a full disk, or a store that throws */
	}
}

/** The stored id when that model is offered, otherwise the default, otherwise the first offered model. */
export function resolveModelId(
	stored: string | null,
	offered: readonly { id: string }[],
	fallback = DEFAULT_MODEL_ID
): string {
	if (stored && offered.some((m) => m.id === stored)) return stored;
	if (offered.some((m) => m.id === fallback)) return fallback;
	return offered[0]?.id ?? fallback;
}

/** Cache URLs that belong to `prefix`, and the ones that belong to other models. */
export function splitCache(
	keys: readonly string[],
	prefix: string
): { drop: string[]; keep: string[] } {
	const root = withSlash(prefix);
	const drop: string[] = [];
	const keep: string[] = [];
	for (const key of keys) (key.startsWith(root) ? drop : keep).push(key);
	return { drop, keep };
}

/** True when deleting one prefix could delete the other's files. */
export function cachePrefixesOverlap(a: string, b: string): boolean {
	const pa = withSlash(a);
	const pb = withSlash(b);
	return pa.startsWith(pb) || pb.startsWith(pa);
}

export const gb = (bytes: number) => `${(bytes / 1e9).toFixed(1)} GB`;

/** The GPU's name as the browser gives it: its description, else "Apple GPU (metal-3)". */
export function gpuLabel(i: { vendor?: string; architecture?: string; description?: string }) {
	if (i.description) return i.description;
	const vendor = i.vendor ? i.vendor[0].toUpperCase() + i.vendor.slice(1) : '';
	if (!vendor) return null;
	return i.architecture ? `${vendor} GPU (${i.architecture})` : `${vendor} GPU`;
}
