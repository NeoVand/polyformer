import { describe, expect, it } from 'vitest';
import {
	adapterName,
	asTrace,
	isLlm,
	llmNote,
	marginBuckets,
	memoryReader,
	programLines,
	ruleLine,
	runNote,
	taskOf,
	unitOf,
	type LlmTrace,
	type Trace,
	type TraceStep
} from './trace.ts';

const step = (i: number, margin: number, st?: [number, number][]): TraceStep => ({
	i,
	event: 'LM',
	s: 'left',
	row: 0,
	attn: [[0, 1]],
	t: 'middle',
	margin,
	xyz: [0, 0, 0],
	...(st ? { st } : {})
});

describe('marginBuckets', () => {
	it('keeps every step when there are fewer steps than buckets', () => {
		expect(marginBuckets([step(0, 3), step(1, 2)], 10)).toEqual([
			{ i: 0, m: 3 },
			{ i: 1, m: 2 }
		]);
	});
	it('keeps the smallest margin of each bucket, so a dip survives downsampling', () => {
		const steps = Array.from({ length: 100 }, (_, i) => step(i, i === 37 ? 0.5 : 9));
		const b = marginBuckets(steps, 10);
		expect(b).toHaveLength(10);
		expect(Math.min(...b.map((x) => x.m))).toBe(0.5);
		expect(b.find((x) => x.m === 0.5)?.i).toBe(37);
	});
});

describe('memoryReader', () => {
	const trace = {
		steps: Array.from({ length: 10 }, (_, i) => step(i, 8, [[i % 3, i]])),
		regs: { mem0: [7, 7, 7] }
	} as unknown as Trace;
	it('rebuilds memory before any step from the image and the stores, across checkpoints', () => {
		const read = memoryReader(trace, 4);
		expect(read(0)).toEqual([7, 7, 7]);
		expect(read(1)).toEqual([0, 7, 7]);
		expect(read(5)).toEqual([3, 4, 2]);
		expect(read(10)).toEqual([9, 7, 8]);
	});
	it('returns copies, so a reader cannot corrupt its checkpoints', () => {
		const read = memoryReader(trace, 4);
		read(4)[0] = 99;
		expect(read(4)[0]).toBe(3);
	});
});

describe('labels', () => {
	it('names the unit and the task from a title', () => {
		expect(unitOf('Shell game, 1,024 swaps')).toBe('swap');
		expect(taskOf('Shell game, 1,024 swaps')).toBe('Shell game');
		expect(taskOf('Multiply two 36-digit numbers, 10,803 instructions')).toBe(
			'Multiply two 36-digit numbers'
		);
	});
	it('finds the rule line for an event, or the catch-all rule', () => {
		const lines = programLines('<program>\nevents: LM MR\non LM: a\non MR: b\n</program>');
		expect(lines).toEqual(['events: LM MR', 'on LM: a', 'on MR: b']);
		expect(ruleLine(lines, 'MR')).toBe(2);
		expect(ruleLine(['on each digit d: r = d'], '7')).toBe(0);
	});
	it('says certified only when every row passed and the size is inside the bound', () => {
		const t = {
			kind: 'automaton',
			steps: [step(0, 1), step(1, 1)],
			program: { states: ['a', 'b', 'c'] },
			certificate: { certified: true, all_ok: true }
		} as unknown as Trace;
		expect(runNote(t)).toBe('ran a 3-state program over 2 events · certified');
		expect(runNote({ ...t, certificate: { ...t.certificate, all_ok: false } })).toMatch(
			/not certified$/
		);
	});
});

describe('LLM runs', () => {
	const register = (name: string, ok: boolean) => ({
		name,
		program: {
			states: ['A', 'B'],
			rows: [
				{ s: 'A', e: 'x', t: 'B', attn: [[3, 0.99]] },
				{ s: 'B', e: 'x', t: 'A', attn: [[5, 0.98]] }
			]
		},
		certificate: { certified: ok, all_ok: ok },
		ticks: { real: 3, bitwise_equal_to_certified_row: 3 },
		steps: [0, 1, 0].map((row, i) => ({ ...step(i, 9), row, attn: [] }))
	});
	const run = (regs: ReturnType<typeof register>[]) =>
		({
			schema: 'polyformer.trace/0',
			id: 'live-x',
			title: 'Shell game, 3 swaps',
			model: {
				name: 'Qwen/Qwen3-4B',
				promptbox_commit: 'abc',
				adapter_sha256: { executor: 'f'.repeat(64) }
			},
			host: { cpu: 'Xeon', gpu: 'H100', avx512f: true },
			registers: regs
		}) as unknown as LlmTrace;

	it('reads a register as a trace whose ticks reuse their certified row’s attention', () => {
		const f = run([register('ball', true)]);
		expect(isLlm(f)).toBe(true);
		const t = asTrace(f)!;
		expect(t.kind).toBe('llm');
		expect(t.steps.map((s) => s.attn)).toEqual([[[3, 0.99]], [[5, 0.98]], [[3, 0.99]]]);
		expect(asTrace(f)).toBe(t);
		expect(runNote(t)).toBe(llmNote(f));
	});
	it('certifies a run only when every register certified, and counts bitwise-equal ticks', () => {
		expect(llmNote(run([register('a', true)]))).toBe(
			'wrote a 2-row table, ran 3 ticks · certified · 3 of 3 ticks bitwise equal to their certified row'
		);
		expect(llmNote(run([register('a', true), register('b', false)]))).toMatch(
			/^wrote a 4-row table in 2 registers, ran 6 ticks · not certified/
		);
	});
	it('names an adapter by its run and step', () => {
		expect(adapterName('s2g-s1/adapter_step750')).toBe('s2g-s1 step 750');
	});
});
