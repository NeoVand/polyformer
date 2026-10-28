/**
 * The two models, which of them the picker offers, the remembered choice, and cache prefixes that do not overlap.
 */
import { describe, expect, it } from 'vitest';
import {
	DEFAULT_MODEL_ID,
	MODELS,
	MODEL_CHOICE_KEY,
	REASON_MODEL_NAME,
	UNPUBLISHED,
	cachePrefixesOverlap,
	hfUrl,
	modelById,
	modelUrl,
	modelsOffered,
	readModelChoice,
	resolveModelId,
	splitCache,
	weightsReady,
	writeModelChoice,
	type ChoiceStore
} from './config.ts';
import { REASON_PROMPTS } from './prompts.ts';

const r3 = modelById('r3');
const reason = modelById('reason');
const HELD_OUT = [
	'parking_fee',
	'four_total',
	'coin_add_or_sub',
	'drone_compass',
	'rumor_chain',
	'marble_trades'
];

function memory(): ChoiceStore & { map: Map<string, string> } {
	const map = new Map<string, string>();
	return {
		map,
		getItem: (k) => map.get(k) ?? null,
		setItem: (k, v) => map.set(k, v)
	};
}

describe('the two models', () => {
	it('pins r3 and leaves the reasoning model unpublished', () => {
		expect(MODELS.map((m) => m.id)).toEqual(['r3', 'reason']);
		expect(r3).toMatchObject({
			name: 'Savant-4B preview r3',
			revision: 'e2a8de056586e6095b5be74c23f16d5750950776',
			repo: 'mohsenvand/savant-4b-preview',
			bytes: 3.33e9,
			adapter: 'arith-s1r2/adapter_step500',
			multiCall: false,
			arithmetic: true
		});
		expect(weightsReady(r3)).toBe(true);
		expect(reason.name).toBe(REASON_MODEL_NAME);
		expect(reason.multiCall).toBe(true);
		expect(reason.repo).toBe(UNPUBLISHED);
		expect(reason.revision).toBe(UNPUBLISHED);
		expect(reason.adapter).toBe(UNPUBLISHED);
		expect(weightsReady(reason)).toBe(false);
		for (const m of MODELS) {
			expect(m.description.includes('\n')).toBe(false);
			expect(m.description.length).toBeGreaterThan(20);
			expect(m.bytes).toBeGreaterThan(1e9);
			expect(m.devUrl.endsWith('/')).toBe(true);
		}
	});

	it('hides an unpublished model unless the stand-in asks for it', () => {
		expect(modelsOffered(false).map((m) => m.id)).toEqual(['r3']);
		expect(modelsOffered(true).map((m) => m.id)).toEqual(['r3', 'reason']);
		const filled = { ...reason, repo: 'mohsenvand/savant-4b-reason', revision: 'abc1234' };
		expect(weightsReady(filled)).toBe(true);
		expect(modelsOffered(false, [r3, filled]).map((m) => m.id)).toEqual(['r3', 'reason']);
	});

	it('gives each model its own cache prefix, including two revisions of one repo', () => {
		const prod = { dev: false };
		const dev = { dev: true };
		expect(modelUrl(r3, prod)).toBe(hfUrl(r3.repo, r3.revision));
		expect(modelUrl(reason, prod)).toBe(reason.devUrl);
		expect(cachePrefixesOverlap(modelUrl(r3, prod), modelUrl(reason, prod))).toBe(false);
		expect(cachePrefixesOverlap(modelUrl(r3, dev), modelUrl(reason, dev))).toBe(false);
		const forced = 'https://example.test/one-export';
		expect(modelUrl(r3, { dev: false, forced })).toBe(`${forced}/`);
		expect(modelUrl(reason, { dev: false, forced })).toBe(reason.devUrl);
		expect(
			cachePrefixesOverlap(
				modelUrl(r3, { dev: false, forced }),
				modelUrl(reason, { dev: false, forced })
			)
		).toBe(false);
		const other = hfUrl(r3.repo, '0123456789abcdef0123456789abcdef01234567');
		expect(cachePrefixesOverlap(hfUrl(r3.repo, r3.revision), other)).toBe(false);
	});
});

describe('the remembered choice', () => {
	it('round-trips, and a missing or unknown id falls back to r3', () => {
		const store = memory();
		expect(readModelChoice(store)).toBe(null);
		writeModelChoice(store, 'reason');
		expect(store.map.get(MODEL_CHOICE_KEY)).toBe('reason');
		expect(readModelChoice(store)).toBe('reason');
		const both = [{ id: 'r3' }, { id: 'reason' }];
		expect(resolveModelId('reason', both)).toBe('reason');
		expect(resolveModelId(null, both)).toBe(DEFAULT_MODEL_ID);
		expect(resolveModelId('reason', [{ id: 'r3' }])).toBe('r3');
		expect(resolveModelId('nope', both)).toBe('r3');
	});

	it('swallows a store that throws', () => {
		const broken: ChoiceStore = {
			getItem: () => {
				throw new Error('denied');
			},
			setItem: () => {
				throw new Error('denied');
			}
		};
		expect(readModelChoice(broken)).toBe(null);
		expect(readModelChoice(null)).toBe(null);
		writeModelChoice(broken, 'r3');
		writeModelChoice(null, 'r3');
	});
});

describe('forgetting one model', () => {
	it('drops that revision’s files and keeps the other model’s', () => {
		const a = hfUrl(r3.repo, r3.revision);
		const b = 'http://127.0.0.1:4173/models/savant-4b-reason/';
		const keys = [
			`${a}onnx/model`,
			`${a}tokenizer.json`,
			`${b}onnx/model`,
			'https://elsewhere/onnx/x'
		];
		const { drop, keep } = splitCache(keys, a);
		expect(drop).toEqual([`${a}onnx/model`, `${a}tokenizer.json`]);
		expect(keep).toEqual([`${b}onnx/model`, 'https://elsewhere/onnx/x']);
		expect(splitCache(keys, b).drop).toEqual([`${b}onnx/model`]);
	});
});

describe('the reasoning model’s suggested questions', () => {
	it('uses three or four training templates, at a trained phrasing', () => {
		expect(REASON_PROMPTS.length).toBeGreaterThanOrEqual(3);
		expect(REASON_PROMPTS.length).toBeLessThanOrEqual(4);
		const templates = REASON_PROMPTS.map((p) => p.template);
		expect(new Set(templates).size).toBe(templates.length);
		for (const p of REASON_PROMPTS) {
			expect(HELD_OUT).not.toContain(p.template);
			expect(p.phrasing).toBeLessThan(4);
			expect(p.question.length).toBeGreaterThan(40);
			expect(p.title.includes('\n')).toBe(false);
		}
		expect(templates).toEqual(['sales_compare', 'deposit_chain', 'parity_pick_sum', 'shelf_bill']);
	});
});
