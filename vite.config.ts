import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { createReadStream, existsSync, statSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import type { Connect, Plugin } from 'vite';

// The interpreter page's live model (research/demolive/dl_server.py, 127.0.0.1 only). Only the local dev and preview
// servers proxy /api; the built site has no such route, so there the page replays recordings.
const liveApi = { '/api': { target: 'http://127.0.0.1:8787', changeOrigin: true } };

/**
 * Savant-4B's weights for local work: the dev and preview servers serve the export folder at /models/ (default
 * ../models, beside this worktree; $SAVANT_MODELS_DIR to change it). Nothing under it is ever bundled or committed.
 */
const modelsDir = resolve(
	process.env.SAVANT_MODELS_DIR ?? resolve(import.meta.dirname, '../models')
);
const serveModels: Connect.NextHandleFunction = (req, res, next) => {
	const path = decodeURIComponent((req.url ?? '/').split('?')[0]);
	const file = resolve(modelsDir, '.' + path);
	if (!file.startsWith(modelsDir + sep) || !existsSync(file) || !statSync(file).isFile())
		return next();
	const size = statSync(file).size;
	const type = file.endsWith('.json') ? 'application/json' : 'application/octet-stream';
	const range = /^bytes=(\d+)-(\d*)$/.exec(req.headers.range ?? '');
	res.setHeader('Accept-Ranges', 'bytes');
	res.setHeader('Content-Type', type);
	res.setHeader('Cache-Control', 'no-cache');
	if (range) {
		const start = Number(range[1]);
		const end = range[2] ? Number(range[2]) : size - 1;
		res.statusCode = 206;
		res.setHeader('Content-Range', `bytes ${start}-${end}/${size}`);
		res.setHeader('Content-Length', String(end - start + 1));
		if (req.method === 'HEAD') return res.end();
		createReadStream(file, { start, end }).pipe(res);
		return;
	}
	res.setHeader('Content-Length', String(size));
	if (req.method === 'HEAD') return res.end();
	createReadStream(file).pipe(res);
};
const savantModels: Plugin = {
	name: 'savant-models',
	configureServer: (server) => void server.middlewares.use('/models', serveModels),
	configurePreviewServer: (server) => void server.middlewares.use('/models', serveModels)
};

export default defineConfig({
	server: { proxy: liveApi },
	preview: { proxy: liveApi },
	// jax-js lazily imports its backends, which needs ES-module workers
	worker: { format: 'es' },
	optimizeDeps: { include: ['@jax-js/jax'] },
	plugins: [
		savantModels,
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter({ fallback: '404.html' }),
			// GitHub Pages serves the site from /<repo>; the deploy workflow sets BASE_PATH
			paths: { base: (process.env.BASE_PATH ?? '') as '' | `/${string}` }
		})
	],
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'client',
					browser: {
						enabled: true,
						provider: playwright(),
						instances: [{ browser: 'chromium', headless: true }]
					},
					include: ['src/**/*.svelte.{test,spec}.{js,ts}'],
					exclude: ['src/lib/server/**']
				}
			},

			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});
