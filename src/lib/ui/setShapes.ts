/**
 * Geometry for SET symbols: three 1:1 shapes centred on the origin in a 24 × 24
 * box, sized to roughly equal area so no shape reads heavier than another.
 */

export const SHAPE_SIZE = 24;

/** A rhombus (a square on its point): half-diagonal 12.5. */
export const DIAMOND = 'M0,-12.5 L12.5,0 L0,12.5 L-12.5,0 Z';
/** A circle of radius 10. */
export const CIRCLE = 'M-10,0 A10,10 0 1 0 10,0 A10,10 0 1 0 -10,0 Z';
/** A square of side 17.6 with barely rounded corners. */
export const SQUARE =
	'M-7.8,-8.8 L7.8,-8.8 Q8.8,-8.8 8.8,-7.8 L8.8,7.8 Q8.8,8.8 7.8,8.8 L-7.8,8.8 Q-8.8,8.8 -8.8,7.8 L-8.8,-7.8 Q-8.8,-8.8 -7.8,-8.8 Z';

export const SHAPES = [DIAMOND, CIRCLE, SQUARE] as const;

export const SET_COLOURS = [
	'var(--color-set-red)',
	'var(--color-set-green)',
	'var(--color-set-purple)'
];
