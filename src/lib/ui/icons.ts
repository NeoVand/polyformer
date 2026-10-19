/**
 * The curated Hugeicons set (1.5px rounded outline, 24px grid). Import icons
 * from here so the app keeps one consistent, purposeful vocabulary.
 */
export type IconData = import('@hugeicons/core-free-icons/types').IconSvgObject;
export { default as Book } from '@hugeicons/core-free-icons/Book02Icon';
export { default as Cube } from '@hugeicons/core-free-icons/CubeIcon';
export { default as Compare } from '@hugeicons/core-free-icons/ChartLineData01Icon';
export { default as Note } from '@hugeicons/core-free-icons/Note01Icon';
export { default as Play } from '@hugeicons/core-free-icons/PlayIcon';
export { default as Pause } from '@hugeicons/core-free-icons/PauseIcon';
export { default as Reset } from '@hugeicons/core-free-icons/ArrowReloadHorizontalIcon';
export { default as Next } from '@hugeicons/core-free-icons/NextIcon';
export { default as Previous } from '@hugeicons/core-free-icons/PreviousIcon';
export { default as Dice } from '@hugeicons/core-free-icons/DiceIcon';
export { default as Chip } from '@hugeicons/core-free-icons/ChipIcon';
export { default as Settings } from '@hugeicons/core-free-icons/Settings01Icon';
export { default as Grid } from '@hugeicons/core-free-icons/GridIcon';
export { default as Layers } from '@hugeicons/core-free-icons/Layers01Icon';
export { default as Network } from '@hugeicons/core-free-icons/NetworkIcon';
export { default as Triangle } from '@hugeicons/core-free-icons/Triangle01Icon';
export { default as Matrix } from '@hugeicons/core-free-icons/MatrixIcon';
export { default as FunctionIcon } from '@hugeicons/core-free-icons/FunctionIcon';
export { default as Link } from '@hugeicons/core-free-icons/Link01Icon';
export { default as Database } from '@hugeicons/core-free-icons/DatabaseIcon';
export { default as Cards } from '@hugeicons/core-free-icons/Cards01Icon';
export { default as Info } from '@hugeicons/core-free-icons/InformationCircleIcon';
export { default as ArrowLeft } from '@hugeicons/core-free-icons/ArrowLeft01Icon';
export { default as ArrowRight } from '@hugeicons/core-free-icons/ArrowRight01Icon';
export { default as Shapes } from '@hugeicons/core-free-icons/GeometricShapes01Icon';
export { default as Timer } from '@hugeicons/core-free-icons/Timer01Icon';
export { default as Flask } from '@hugeicons/core-free-icons/FlaskConicalIcon';
export { default as Exchange } from '@hugeicons/core-free-icons/Exchange01Icon';
export { default as Maximize } from '@hugeicons/core-free-icons/Maximize01Icon';
export { default as Download } from '@hugeicons/core-free-icons/Download01Icon';
export { default as Thermometer } from '@hugeicons/core-free-icons/ThermometerIcon';
export { default as Hierarchy } from '@hugeicons/core-free-icons/HierarchyIcon';
export { default as Atom } from '@hugeicons/core-free-icons/Atom02Icon';
export { default as Expand } from '@hugeicons/core-free-icons/ArrowExpandIcon';
export { default as Sliders } from '@hugeicons/core-free-icons/SlidersHorizontalIcon';
export { default as Target } from '@hugeicons/core-free-icons/Target01Icon';
export { default as GitGraph } from '@hugeicons/core-free-icons/GitGraphIcon';
export { default as Wave } from '@hugeicons/core-free-icons/Cosine01Icon';
export { default as Scissors } from '@hugeicons/core-free-icons/ScissorIcon';
export { default as Workflow } from '@hugeicons/core-free-icons/WorkflowSquare01Icon';
export { default as Github } from '@hugeicons/core-free-icons/GithubIcon';

/*
 * Two marks drawn for this project on the same 24px grid and 1.5px stroke, so they
 * sit beside the Hugeicons set: a 2-simplex for cubic attention (one query, a pair
 * of keys) and a textbook Feynman diagram for Feynman attention (two lines meet, exchange a
 * photon, and part).
 */
const stroke = {
	stroke: 'currentColor',
	strokeLinecap: 'round',
	strokeLinejoin: 'round',
	strokeWidth: '1.5'
};
export const Simplex = [
	['path', { d: 'M10.7 6.5 L5.8 16.2 M13.3 6.5 L18.2 16.2 M7 18.5 H17', ...stroke, key: '0' }],
	['circle', { cx: '12', cy: '4.5', r: '2', ...stroke, key: '1' }],
	['circle', { cx: '4.75', cy: '18.5', r: '2', ...stroke, key: '2' }],
	['circle', { cx: '19.25', cy: '18.5', r: '2', ...stroke, key: '3' }]
] as unknown as IconData;
export const Feynman = [
	['path', { d: 'M2.5 4 L7.5 12 L2.5 20 M21.5 4 L16.5 12 L21.5 20', ...stroke, key: '0' }],
	['path', { d: 'M7.5 12 q1.125 -2.2 2.25 0 t2.25 0 t2.25 0 t2.25 0', ...stroke, key: '1' }]
] as unknown as IconData;
/** Newton attention: a phase wheel with the three values of a character of Z_3. */
export const Newton = [
	['circle', { cx: '12', cy: '12', r: '8', ...stroke, key: '0' }],
	['circle', { cx: '12', cy: '4', r: '1.6', fill: 'currentColor', ...stroke, key: '1' }],
	['circle', { cx: '5.07', cy: '16', r: '1.6', fill: 'currentColor', ...stroke, key: '2' }],
	['circle', { cx: '18.93', cy: '16', r: '1.6', fill: 'currentColor', ...stroke, key: '3' }]
] as unknown as IconData;
