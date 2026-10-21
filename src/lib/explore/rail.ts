import { resolve } from '$app/paths';
import { Feynman, Holonomy, Newton, Simplex } from '#lib/ui/icons.ts';

/** The Explore labs, one per approach, in the order the paper introduces them. */
export const exploreRail = () => [
	{ id: 'tensor', label: 'Cubic', icon: Simplex, href: resolve('/explore') },
	{ id: 'diagrams', label: 'Feynman', icon: Feynman, href: resolve('/explore/diagrams') },
	{ id: 'newton', label: 'Newton', icon: Newton, href: resolve('/explore/newton') },
	{ id: 'groups', label: 'Holonomy', icon: Holonomy, href: resolve('/explore/groups') }
];
