import type { OperatorId, OperatorOptions } from '../model/operators/index.ts';
import type { TaskId } from '../tasks/index.ts';

/** One model in a bench: an operator at a depth, trained on a task. */
export interface RunSpec {
	id: string;
	operator: OperatorId;
	layers: number;
	label: string;
	/** Task this run trains on; defaults to SET. */
	task?: TaskId;
	/** Operator options (Feynman attention rounds and modes). */
	options?: OperatorOptions;
	/** Trains when Start is pressed unless switched off; defaults to true. */
	defaultEnabled?: boolean;
	/** Grayscale step for charts and legends, 0 (dim) … 1 (bright). The run under study is brightest. */
	tone: number;
	/** Dash pattern for charts, so runs stay distinct without colour. */
	dash: string;
}

/** The SET bench. Feynman attention is available but off by default, so Start trains the original five. */
export const BENCH_RUNS: RunSpec[] = [
	{ id: 'cubic', operator: 'cubic', layers: 1, label: 'Cubic', tone: 1, dash: '' },
	{ id: 'strassen', operator: 'strassen', layers: 1, label: 'Strassen', tone: 0.72, dash: '6 3' },
	{ id: 'tree', operator: 'tree', layers: 1, label: 'Tree (Columbia)', tone: 0.6, dash: '2 3' },
	{
		id: 'std2',
		operator: 'standard',
		layers: 2,
		label: 'Standard · 2 layers',
		tone: 0.48,
		dash: '8 3 2 3'
	},
	{
		id: 'std1',
		operator: 'standard',
		layers: 1,
		label: 'Standard · 1 layer',
		tone: 0.38,
		dash: '1 2'
	},
	{
		id: 'dspa',
		operator: 'dspa',
		layers: 1,
		label: 'Feynman · 2 rounds',
		options: { rounds: 2, modes: 16 },
		defaultEnabled: false,
		tone: 0.86,
		dash: '10 3'
	}
];

/** The pointer-chase bench: Feynman attention against cubic and standard attention at 1–3 layers. */
export const CHASE_RUNS: RunSpec[] = [
	{
		id: 'dspa',
		operator: 'dspa',
		layers: 1,
		label: 'Feynman · 4 rounds',
		task: 'chase',
		options: { rounds: 4, modes: 16 },
		tone: 1,
		dash: ''
	},
	{
		id: 'cubic',
		operator: 'cubic',
		layers: 1,
		label: 'Cubic',
		task: 'chase',
		tone: 0.72,
		dash: '6 3'
	},
	{
		id: 'std3',
		operator: 'standard',
		layers: 3,
		label: 'Standard · 3 layers',
		task: 'chase',
		tone: 0.6,
		dash: '2 3'
	},
	{
		id: 'std2',
		operator: 'standard',
		layers: 2,
		label: 'Standard · 2 layers',
		task: 'chase',
		tone: 0.48,
		dash: '8 3 2 3'
	},
	{
		id: 'std1',
		operator: 'standard',
		layers: 1,
		label: 'Standard · 1 layer',
		task: 'chase',
		tone: 0.38,
		dash: '1 2'
	}
];

export type SuiteId = 'set' | 'chase';

export interface Suite {
	id: SuiteId;
	task: TaskId;
	label: string;
	runs: RunSpec[];
}

export const SUITES: Record<SuiteId, Suite> = {
	set: { id: 'set', task: 'set', label: 'SET bench', runs: BENCH_RUNS },
	chase: { id: 'chase', task: 'chase', label: 'Pointer-chase bench', runs: CHASE_RUNS }
};

export const runById = (id: string, suite: SuiteId = 'set') =>
	SUITES[suite].runs.find((r) => r.id === id);
