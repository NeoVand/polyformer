/** Display precision is copied verbatim from research/GROUPS.md §5.1, §5.2, §7.3.
 * Numeric means drive figures only; strings preserve the research tables' rounding.
 * Raw sources: research/results/grp_e1.jsonl, grp_e2.jsonl, grp_swap.jsonl.
 */
export const CEILINGS = { a4: 83.0546984493, a5: 77.2287515874, swap: (100 * 67) / 108 };
export type ResultCell = { mean: number; display: string; seeds?: string };
const cell = (display: string, seeds?: string): ResultCell => ({
	mean: Number(display),
	display,
	seeds
});
export const CHARACTER_ROWS = [
	{
		id: 'char1',
		label: 'Softmax 1L, frozen characters',
		values: [
			cell('54.8', '54.9, 54.9, 54.6'),
			cell('50.0', '50.0, 50.0, 50.0'),
			cell('50.0', '50.0, 50.0, 50.0')
		]
	},
	{
		id: 'char2',
		label: 'Softmax 2L, frozen characters',
		values: [
			cell('54.7', '55.2, 54.9, 54.0'),
			cell('50.0', '50.0, 50.0, 50.0'),
			cell('50.0', '50.0, 50.0, 50.0')
		]
	},
	{
		id: 'rot1',
		label: 'Softmax 1L, rotated characters',
		values: [
			cell('54.8', '54.5, 54.9, 54.8'),
			cell('50.0', '50.0, 50.0, 50.0'),
			cell('50.0', '50.0, 50.0, 50.0')
		]
	},
	{
		id: 'rot2',
		label: 'Softmax 2L, rotated characters',
		values: [
			cell('53.9', '54.5, 54.4, 52.9'),
			cell('50.0', '50.0, 50.0, 50.0'),
			cell('50.0', '50.0, 50.0, 50.0')
		]
	},
	{
		id: 'table1',
		label: 'Softmax 1L, learned tables',
		values: [
			cell('58.1', '57.2, 59.4, 57.6'),
			cell('50.9', '50.7, 51.0, 50.9'),
			cell('50.0', '50.0, 50.0, 50.0')
		]
	},
	{
		id: 'table2',
		label: 'Softmax 2L, learned tables',
		values: [
			cell('58.6', '60.9, 58.2, 56.9'),
			cell('50.5', '50.9, 50.0, 50.6'),
			cell('50.0', '50.0, 50.0, 50.0')
		]
	},
	{
		id: 'newton',
		label: 'Newton attention (reference)',
		values: [cell('100'), cell('100'), cell('85')]
	}
];
export const GROUP_ROWS = [
	{
		id: 'h2',
		label: 'Holonomy d = 2 (commuting)',
		short: 'Holonomy d = 2',
		values: [
			cell('100.0'),
			cell('81.1', '81.7, 81.0, 80.7'),
			cell('100.0'),
			cell('73.1', '73.6, 73.1, 72.5')
		]
	},
	{
		id: 'h3',
		label: 'Holonomy d = 3',
		short: 'd = 3',
		values: [cell('100.0'), cell('100.0'), cell('100.0'), cell('94.1', '93.4, 94.0, 94.8')]
	},
	{
		id: 'h4',
		label: 'Holonomy d = 4',
		short: 'd = 4',
		values: [cell('100.0'), cell('100.0'), cell('100.0'), cell('99.5', '99.2, 99.5, 99.7')]
	},
	{
		id: 'h5',
		label: 'Holonomy d = 5',
		short: 'd = 5',
		values: [cell('100.0'), cell('100.0'), cell('100.0'), cell('100.0', '99.97, 99.96, 99.98')]
	},
	{
		id: 'h8',
		label: 'Holonomy d = 8',
		short: 'd = 8',
		values: [cell('100.0'), cell('100.0'), cell('100.0'), cell('100.0')]
	},
	{
		id: 'newton',
		label: 'Newton attention',
		short: 'Newton',
		values: [
			cell('100.0'),
			cell('80.7', '81.1, 80.8, 80.3'),
			cell('100.0'),
			cell('76.1', '76.1, 76.4, 75.9')
		]
	},
	{
		id: 'soft1',
		label: 'Softmax 1L (positions)',
		short: 'Softmax 1L',
		values: [
			cell('98.2', '96.4, 100.0, 98.2'),
			cell('81.0', '80.6, 81.1, 81.2'),
			cell('50.1'),
			cell('50.0')
		]
	},
	{
		id: 'soft3',
		label: 'Softmax 3L (positions)',
		short: 'Softmax 3L',
		values: [
			cell('100.0'),
			cell('99.7', '99.6, 99.9, 99.8'),
			cell('50.8', '50.6, 50.2, 51.4'),
			cell('50.0')
		]
	}
];
export const SWAP_ROWS = [
	{ id: 'h2', label: 'Holonomy d = 2 (commuting)', result: cell('62.02', '61.94, 62.06, 62.07') },
	{ id: 'h3', label: 'Holonomy d = 3', result: cell('100.00', '100.00, 100.00, 100.00') },
	{ id: 'h4', label: 'Holonomy d = 4', result: cell('100.00', '100.00, 100.00, 100.00') },
	{ id: 'newton', label: 'Newton attention', result: cell('62.05', '61.75, 62.63, 61.77') },
	{ id: 'soft1', label: 'Softmax 1L, positions', result: cell('98.95', '99.80, 98.54, 98.50') },
	{ id: 'soft2', label: 'Softmax 2L, positions', result: cell('100.00', '100.00, 100.00, 100.00') },
	{ id: 'soft3', label: 'Softmax 3L, positions', result: cell('100.00', '100.00, 100.00, 100.00') },
	{
		id: 'rnn',
		label: 'Orthogonal matrix-state RNN d = 6',
		result: cell('100.00', '100.00, 100.00, 100.00')
	}
];
