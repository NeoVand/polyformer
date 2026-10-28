<script lang="ts">
	/**
	 * A reply the model wrote in words: a small Markdown subset (headings, bold, code, lists, rules, paragraphs) and
	 * TeX ($$…$$, \[…\], $…$, \(…\)) through KaTeX. Everything else is escaped, so model text can never inject markup.
	 */
	import katex from 'katex';

	let { text }: { text: string } = $props();

	const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
	const tex = (t: string, display: boolean) =>
		katex.renderToString(t, { displayMode: display, throwOnError: false, output: 'html' });
	const marks = (h: string) =>
		h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');

	function inline(s: string): string {
		const out: string[] = [];
		const re = /\\\((.+?)\\\)|\$([^$\n]+?)\$/g;
		let last = 0;
		for (let m = re.exec(s); m; m = re.exec(s)) {
			out.push(marks(esc(s.slice(last, m.index))), tex(m[1] ?? m[2], false));
			last = re.lastIndex;
		}
		out.push(marks(esc(s.slice(last))));
		return out.join('');
	}

	function blocks(s: string): string {
		const out: string[] = [];
		let para: string[] = [];
		let list: string[] = [];
		const flush = () => {
			if (para.length) out.push(`<p>${para.map(inline).join(' ')}</p>`);
			if (list.length) out.push(`<ul>${list.map((l) => `<li>${inline(l)}</li>`).join('')}</ul>`);
			para = [];
			list = [];
		};
		for (const raw of s.split('\n')) {
			const line = raw.trim();
			if (!line) {
				flush();
			} else if (/^-{3,}$/.test(line)) {
				flush();
				out.push('<hr />');
			} else if (/^#{1,6}\s/.test(line)) {
				flush();
				out.push(`<p class="h">${inline(line.replace(/^#+\s*/, ''))}</p>`);
			} else if (/^[-*]\s+/.test(line)) {
				if (para.length) flush();
				list.push(line.replace(/^[-*]\s+/, ''));
			} else {
				if (list.length) flush();
				para.push(line);
			}
		}
		flush();
		return out.join('');
	}

	function render(src: string): string {
		const out: string[] = [];
		const re = /\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]/g;
		let last = 0;
		for (let m = re.exec(src); m; m = re.exec(src)) {
			out.push(
				blocks(src.slice(last, m.index)),
				`<div class="disp">${tex((m[1] ?? m[2]).trim(), true)}</div>`
			);
			last = re.lastIndex;
		}
		out.push(blocks(src.slice(last)));
		return out.join('');
	}

	const html = $derived(render(text));
</script>

<!-- eslint-disable-next-line svelte/no-at-html-tags -- escaped model text plus KaTeX output -->
<div class="reply">{@html html}</div>

<style>
	.reply {
		display: flex;
		flex-direction: column;
		gap: 6px;
		min-width: 0;
		overflow-wrap: anywhere;
	}
	.reply :global(p) {
		margin: 0;
	}
	.reply :global(p.h) {
		font-weight: 600;
		margin-top: 4px;
	}
	.reply :global(ul) {
		margin: 0;
		padding-left: 18px;
	}
	.reply :global(hr) {
		display: none;
	}
	.reply :global(code) {
		font-family: var(--font-mono);
		font-size: 0.92em;
	}
	.reply :global(.disp) {
		overflow-x: auto;
		overflow-y: hidden;
	}
	.reply :global(.katex-display) {
		margin: 0.2em 0;
		text-align: left;
	}
</style>
