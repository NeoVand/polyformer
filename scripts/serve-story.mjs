// Serve adapter-static output, including extensionless GitHub Pages routes.
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
const root = resolve('build');
const port = Number(process.env.PORT || 4173);
const basePath = (process.env.BASE_PATH || '').replace(/\/$/, '');
const mime = {
	'.html': 'text/html',
	'.js': 'text/javascript',
	'.css': 'text/css',
	'.json': 'application/json',
	'.svg': 'image/svg+xml',
	'.png': 'image/png',
	'.woff2': 'font/woff2',
	'.wasm': 'application/wasm'
};
createServer(async (req, res) => {
	const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
	if (basePath && pathname !== basePath && !pathname.startsWith(basePath + '/')) {
		res.writeHead(404).end('Not found');
		return;
	}
	const base = resolve(root, '.' + (pathname.slice(basePath.length) || '/'));
	if (base !== root && !base.startsWith(root + sep)) {
		res.writeHead(403).end();
		return;
	}
	for (const name of [base, base + '.html', resolve(base, 'index.html')]) {
		try {
			if (!(await stat(name)).isFile()) continue;
			res.writeHead(200, {
				'Content-Type': mime[extname(name)] || 'application/octet-stream',
				'Cache-Control': 'no-store'
			});
			res.end(await readFile(name));
			return;
		} catch {}
	}
	res.writeHead(404).end('Not found');
}).listen(port, '127.0.0.1', () =>
	console.log(`Static production build: http://127.0.0.1:${port}${basePath}/`)
);
