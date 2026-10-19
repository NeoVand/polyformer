import type { OperatorId } from '../model/operators/index.ts';

/** One model in the bench: an operator at a depth. */
export interface RunSpec {
	id: string;
	operator: OperatorId;
	layers: number;
	label: string;
	/** Grayscale step for charts and legends, 0 (dim) … 1 (bright). Cubic is brightest. */
	tone: number;
	/** Dash pattern for charts, so runs stay distinct without colour. */
	dash: string;
}

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
	}
];

export const runById = (id: string) => BENCH_RUNS.find((r) => r.id === id);
