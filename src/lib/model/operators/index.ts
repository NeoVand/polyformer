import { cubic } from './cubic.ts';
import { standard } from './standard.ts';
import { strassen } from './strassen.ts';
import { tree } from './tree.ts';
import type { AttentionOperator, OperatorId } from './types.ts';

export type { AttentionOperator, OperatorId, HeadShape, AttendResult } from './types.ts';

/** Registry of attention operators. New operators plug in here. */
export const OPERATORS: Record<OperatorId, AttentionOperator> = { standard, tree, strassen, cubic };

export function getOperator(id: OperatorId): AttentionOperator {
	const op = OPERATORS[id];
	if (!op) throw new Error(`unknown attention operator: ${id}`);
	return op;
}
