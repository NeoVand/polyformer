<script lang="ts">
	/** REGS memory after an instruction: digit arrays read as numbers, registers, and the cells just written. */
	import { memoryReader, type Trace } from './trace.ts';

	let { trace, step }: { trace: Trace; step: number } = $props();

	const regs = $derived(trace.regs!);
	const read = $derived(memoryReader(trace));
	const mem = $derived(read(step + 1));
	const written = $derived(new Set((trace.steps[step].st ?? []).map(([c]) => c)));
	const CONST = new Set(['ZERO', 'ONE', 'HASH']);
	const digit = (v: number) => (v === regs.hash ? '#' : String(v));
	const name = (v: number) => regs.names[String(v)] ?? String(v);
	const pointers = $derived(new Set(regs.pointers));

	const arrays = $derived(
		Object.entries(regs.arrays).map(([a, [base, n]]) => {
			const cells = Array.from({ length: n }, (_, k) => base + n - 1 - k);
			const marks: Record<number, string[]> = {};
			for (const p of regs.pointers) {
				const v = mem[regs.cells[p]];
				if (v >= base && v < base + n && !/^P[A-Z]$/.test(p)) (marks[v] ??= []).push(p);
			}
			return { a, cells, marks };
		})
	);
	const scalars = $derived(
		regs.registers
			.filter((r) => !CONST.has(r))
			.map((r) => {
				const c = regs.cells[r];
				const v = mem[c];
				return { r, c, text: pointers.has(r) ? name(v) : digit(v) };
			})
	);
</script>

<div class="memory" aria-label="Memory after this instruction">
	{#each arrays as arr (arr.a)}
		<div class="arr">
			<span class="an">{arr.a}</span>
			<span class="digits num">
				{#each arr.cells as c (c)}<span
						class={['d', written.has(c) && 'w', arr.marks[c] && 'p']}
						title={arr.marks[c]?.join(', ')}>{digit(mem[c])}</span
					>{/each}
			</span>
		</div>
	{/each}
	<div class="regs num">
		{#each scalars as s (s.r)}
			<span class={['reg', written.has(s.c) && 'w']}><span class="rn">{s.r}</span>{s.text}</span>
		{/each}
	</div>
</div>

<style>
	.memory {
		display: grid;
		gap: 4px;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		min-height: 0;
		overflow: auto;
	}
	.arr {
		display: grid;
		grid-template-columns: 2ch minmax(0, 1fr);
		gap: 8px;
		align-items: baseline;
	}
	.an {
		color: var(--color-ink-3);
	}
	.digits {
		color: var(--color-ink-2);
		word-break: break-all;
		letter-spacing: 0.06em;
	}
	.d {
		border-bottom: 1px solid transparent;
	}
	.d.p {
		border-bottom-color: var(--color-ink-3);
	}
	.d.w {
		color: var(--color-void);
		background: var(--color-ink);
	}
	.regs {
		display: flex;
		flex-wrap: wrap;
		gap: 2px 14px;
		margin-top: 4px;
		color: var(--color-ink-2);
	}
	.reg {
		white-space: nowrap;
	}
	.rn {
		color: var(--color-ink-3);
		margin-right: 5px;
	}
	.reg.w {
		color: var(--color-ink);
	}
	.reg.w .rn {
		color: var(--color-ink);
	}
</style>
