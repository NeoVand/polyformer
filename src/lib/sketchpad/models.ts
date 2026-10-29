/**
 * The two sketchpad models: Qwen3.5-0.8B with a small adapter merged, exported to ONNX for transformers.js. The dev
 * server serves them from static/sketchpad/models/<id>/ (never committed). Each operation loads only its own model.
 */
export type Kind = 'add' | 'mul';

export interface SketchModel {
	kind: Kind;
	id: string;
	/** what the visitor reads */
	name: string;
	dtype: Record<'embed_tokens' | 'vision_encoder' | 'decoder_model_merged', 'q4' | 'fp16'>;
	/** table rows the certificate checks */
	rows: number;
}

export const MODELS: Record<Kind, SketchModel> = {
	add: {
		kind: 'add',
		id: 'qwen35-canvas-fast',
		name: 'the adder',
		dtype: { embed_tokens: 'q4', vision_encoder: 'fp16', decoder_model_merged: 'q4' },
		rows: 242
	},
	mul: {
		kind: 'mul',
		// seed 3, hinge 4 (Modal, 29 Oct): 1,553/1,553 on the server (min margin 2.86) and on an M4 with this q4 decoder (0.37)
		id: 'qwen35-mul-s3h4-q4',
		name: 'the multiplier',
		dtype: { embed_tokens: 'q4', vision_encoder: 'fp16', decoder_model_merged: 'q4' },
		rows: 1553
	}
};

/** Every file transformers.js fetches for a model, relative to the model's folder. */
export function modelFiles(m: SketchModel): string[] {
	const onnx = Object.entries(m.dtype).flatMap(([name, d]) => [
		`onnx/${name}_${d}.onnx`,
		`onnx/${name}_${d}.onnx_data`
	]);
	return [
		'config.json',
		'generation_config.json',
		'preprocessor_config.json',
		'processor_config.json',
		'tokenizer.json',
		'tokenizer_config.json',
		'chat_template.jinja',
		...onnx
	];
}

/**
 * The files a certificate depends on: the weights, the configs and the tokenizer. (processor_config.json and
 * chat_template.jinja are never fetched: the processor reads preprocessor_config.json, the tokenizer its own config.)
 */
export const certFiles = (m: SketchModel) =>
	modelFiles(m).filter((f) => f !== 'processor_config.json' && f !== 'chat_template.jinja');

/**
 * The format the certificate certifies. Any change to prompts, tables, scoring or strip assembly must change this
 * string, so a cached certificate never outlives the format it checked.
 */
export const CERT_FORMAT = 'sketchpad-cert-v1;add=fast-242;mul=3tok-1553;strip=sprites-rowk-32x96';
