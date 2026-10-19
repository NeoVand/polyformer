<script lang="ts" module>
	export type QedKind =
		| 'blob'
		| 'tree-t'
		| 'tree-u'
		| 'vacuum'
		| 'vertex'
		| 'box'
		| 'dressed'
		| 'bare'
		| 'bare-sigma-dressed'
		| 'bare-sigma-bare'
		| 'bare-sigma-bare-sigma-bare';
</script>

<script lang="ts">
	/**
	 * Textbook Feynman diagrams for the field-theory chapters: electron lines with
	 * arrows, photons as smooth waves, loops, and the hatched blobs of a
	 * Dyson–Schwinger equation. Drawn in a 100 × 64 box (propagators in 100 × 24).
	 */
	import { photon } from '#lib/viz/feynman.ts';

	let { kind, width = 100 }: { kind: QedKind; width?: number } = $props();

	const PROP: QedKind[] = ['dressed', 'bare', 'bare-sigma-dressed', 'bare-sigma-bare', 'bare-sigma-bare-sigma-bare'];
	const isProp = $derived(PROP.includes(kind));
	const W = $derived(kind === 'bare-sigma-bare-sigma-bare' ? 150 : 100);
	const H = $derived(isProp ? 24 : 64);

	type P = [number, number];
	/** An electron line with a mid arrow pointing from a to b. */
	function fermion(a: P, b: P) {
		const dx = b[0] - a[0];
		const dy = b[1] - a[1];
		const len = Math.hypot(dx, dy);
		const ux = dx / len;
		const uy = dy / len;
		const s = 4.2;
		const mx = (a[0] + b[0]) / 2 + ux * s * 0.5;
		const my = (a[1] + b[1]) / 2 + uy * s * 0.5;
		const bx = mx - ux * s;
		const by = my - uy * s;
		const w = s * 0.45;
		return {
			line: `M${a[0]},${a[1]} L${b[0]},${b[1]}`,
			tip: `M${mx},${my} L${bx - uy * w},${by + ux * w} L${bx + uy * w},${by - ux * w} Z`
		};
	}
	/** A photon along an arc (for the vertex correction), wiggled about the curve. */
	function photonArc(a: P, b: P, lift: number, amp = 2.2, wave = 6.5) {
		const pts: P[] = [];
		const N = 120;
		for (let i = 0; i <= N; i++) {
			const t = i / N;
			const x = a[0] + (b[0] - a[0]) * t;
			const y = a[1] + (b[1] - a[1]) * t - Math.sin(Math.PI * t) * lift;
			pts.push([x, y]);
		}
		let len = 0;
		const acc = [0];
		for (let i = 1; i < pts.length; i++) {
			len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
			acc.push(len);
		}
		const cycles = Math.max(2, Math.round(len / wave));
		return pts
			.map((p, i) => {
				const prev = pts[Math.max(0, i - 1)];
				const next = pts[Math.min(pts.length - 1, i + 1)];
				const tx = next[0] - prev[0];
				const ty = next[1] - prev[1];
				const tl = Math.hypot(tx, ty) || 1;
				const off = Math.sin((acc[i] / len) * cycles * 2 * Math.PI) * amp;
				return `${i ? 'L' : 'M'}${(p[0] - (ty / tl) * off).toFixed(2)},${(p[1] + (tx / tl) * off).toFixed(2)}`;
			})
			.join(' ');
	}

	/** Lines and photons for each scattering diagram: two electrons in on the left, out on the right. */
	const parts = $derived.by(() => {
		const f: ReturnType<typeof fermion>[] = [];
		const ph: string[] = [];
		const dots: P[] = [];
		const loops: { c: P; r: number }[] = [];
		const top: P = [50, 14];
		const bot: P = [50, 50];
		switch (kind) {
			case 'tree-t':
				f.push(fermion([6, 6], top), fermion(top, [94, 6]), fermion([6, 58], bot), fermion(bot, [94, 58]));
				ph.push(photon(top[0], top[1], bot[0], bot[1], 2.4, 6.5));
				dots.push(top, bot);
				break;
			case 'tree-u':
				f.push(fermion([6, 6], top), fermion(top, [94, 58]), fermion([6, 58], bot), fermion(bot, [94, 6]));
				ph.push(photon(top[0], top[1], bot[0], bot[1], 2.4, 6.5));
				dots.push(top, bot);
				break;
			case 'vacuum':
				f.push(fermion([6, 6], top), fermion(top, [94, 6]), fermion([6, 58], bot), fermion(bot, [94, 58]));
				ph.push(photon(50, 14, 50, 23, 2.2, 6), photon(50, 41, 50, 50, 2.2, 6));
				loops.push({ c: [50, 32], r: 9 });
				dots.push(top, bot, [50, 23], [50, 41]);
				break;
			case 'vertex': {
				const a: P = [24, 10];
				const b: P = [76, 10];
				f.push(
					fermion([4, 6], a),
					fermion(a, top),
					fermion(top, b),
					fermion(b, [96, 6]),
					fermion([6, 58], bot),
					fermion(bot, [94, 58])
				);
				ph.push(photon(top[0], top[1], bot[0], bot[1], 2.4, 6.5), photonArc(a, b, 11));
				dots.push(a, b, top, bot);
				break;
			}
			case 'box': {
				const tl: P = [34, 14];
				const tr: P = [66, 14];
				const bl: P = [34, 50];
				const br: P = [66, 50];
				f.push(
					fermion([6, 6], tl),
					fermion(tl, tr),
					fermion(tr, [94, 6]),
					fermion([6, 58], bl),
					fermion(bl, br),
					fermion(br, [94, 58])
				);
				ph.push(photon(34, 14, 34, 50, 2.4, 6.5), photon(66, 14, 66, 50, 2.4, 6.5));
				dots.push(tl, tr, bl, br);
				break;
			}
		}
		return { f, ph, dots, loops };
	});
</script>

<svg {width} height={(width * H) / W} viewBox="0 0 {W} {H}" class="qed" aria-hidden="true">
	<defs>
		<pattern id="qed-hatch" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
			<line x1="0" y1="0" x2="0" y2="3" stroke="#f2f2f2" stroke-width="0.8" />
		</pattern>
	</defs>
	{#if kind === 'blob'}
		<path d="M6,6 L36,26 M6,58 L36,38 M64,26 L94,6 M64,38 L94,58" class="ln" />
		<circle cx="50" cy="32" r="16" class="blob" />
	{:else if isProp}
		{#if kind === 'dressed'}
			<path d="M4,10 L96,10 M4,14 L96,14" class="ln thin" />
		{:else if kind === 'bare'}
			<path d="M4,12 L96,12" class="ln" />
		{:else if kind === 'bare-sigma-dressed'}
			<path d="M4,12 L38,12" class="ln" />
			<circle cx="50" cy="12" r="10" class="blob" />
			<path d="M62,10 L96,10 M62,14 L96,14" class="ln thin" />
		{:else if kind === 'bare-sigma-bare'}
			<path d="M4,12 L38,12 M62,12 L96,12" class="ln" />
			<circle cx="50" cy="12" r="10" class="blob" />
		{:else}
			<path d="M4,12 L33,12 M57,12 L93,12 M117,12 L146,12" class="ln" />
			<circle cx="45" cy="12" r="10" class="blob" />
			<circle cx="105" cy="12" r="10" class="blob" />
		{/if}
	{:else}
		{#each parts.loops as l, i (i)}
			<circle cx={l.c[0]} cy={l.c[1]} r={l.r} class="ln" />
			<path d="M{l.c[0] - l.r - 2},{l.c[1] - 1} l2,3 l2,-3" class="ln" />
			<path d="M{l.c[0] + l.r - 2},{l.c[1] + 1} l2,-3 l2,3" class="ln" />
		{/each}
		{#each parts.f as fl, i (i)}
			<path d={fl.line} class="ln" />
			<path d={fl.tip} class="tip" />
		{/each}
		{#each parts.ph as d, i (i)}<path {d} class="ln wave" />{/each}
		{#each parts.dots as p, i (i)}<circle cx={p[0]} cy={p[1]} r="1.9" class="tip" />{/each}
	{/if}
</svg>

<style>
	.qed {
		display: block;
		overflow: visible;
	}
	.ln {
		fill: none;
		stroke: #f2f2f2;
		stroke-width: 1.25;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.ln.thin {
		stroke-width: 1.1;
	}
	.ln.wave {
		stroke-width: 1.1;
	}
	.tip {
		fill: #f2f2f2;
	}
	.blob {
		fill: url(#qed-hatch);
		stroke: #f2f2f2;
		stroke-width: 1.2;
	}
</style>
