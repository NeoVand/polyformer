/**
 * The page's theme. The site is dark-only today (layout.css sets `color-scheme: dark` and has no light tokens), so this
 * page follows `<html data-theme="light|dark">` when the site sets it and the site's dark otherwise. Flip FOLLOW_SYSTEM
 * to also follow the system preference when no data-theme is set.
 *
 * Only what the page draws changes. The strips fed to the model are always the training pixels, black on white.
 */
export type Theme = 'dark' | 'light';

const FOLLOW_SYSTEM = false;

class ThemeState {
	current = $state<Theme>('dark');

	/** start following the document; returns the cleanup */
	watch(): () => void {
		const root = document.documentElement;
		const mq = matchMedia('(prefers-color-scheme: light)');
		const read = () => {
			const t = root.dataset.theme;
			this.current =
				t === 'light' || t === 'dark' ? t : FOLLOW_SYSTEM && mq.matches ? 'light' : 'dark';
		};
		read();
		const mo = new MutationObserver(read);
		mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
		mq.addEventListener('change', read);
		return () => {
			mo.disconnect();
			mq.removeEventListener('change', read);
		};
	}
}

export const theme = new ThemeState();

/** How the display sheet is drawn. Light is the training pixels exactly: black ink on white paper. */
export interface SheetPalette {
	paper: string;
	/** glyph colour; each glyph pixel is this ink at alpha (255 - its grey level) */
	ink: string;
	rule: string;
	/** behind a digit the pointer can change */
	tint: string;
	fovea: string;
	/** under a digit a visitor changed */
	mark: string;
}

export const SHEET: Record<Theme, SheetPalette> = {
	light: {
		paper: '#ffffff',
		ink: '#000000',
		rule: '#c9c9c9',
		tint: '#ececec',
		fovea: '#111111',
		mark: '#9a9a9a'
	},
	// the site's greys: a sheet one step above the panel, ink a step below the page's text
	dark: {
		paper: '#151515',
		ink: '#e6e6e6',
		rule: '#2e2e2e',
		tint: '#242424',
		fovea: '#b4b4b4',
		mark: '#6a6a6a'
	}
};

/** The certificate grid's tones: unchecked, passed, failed (a hollow ring), and pointed at. */
export const GRID: Record<Theme, { idle: string; pass: string; fail: string; hot: string }> = {
	light: { idle: '#dedede', pass: '#5a5a5a', fail: '#0d0d0d', hot: '#000000' },
	dark: { idle: '#1c1c1c', pass: '#c8c8c8', fail: '#f5f5f5', hot: '#ffffff' }
};
