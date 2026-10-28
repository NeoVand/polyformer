<script lang="ts">
	/**
	 * Panel 5: poke the brain. Force a different state at a step and let the run resume, or switch off what executes
	 * it: the head on the frozen INTERP core, the executor adapter on the LLM. Recorded interventions replay; with the
	 * live model, both controls run on it.
	 */
	import Pane from './Pane.svelte';
	import { int, type Trace } from './trace.ts';

	let {
		trace,
		step,
		ablated = $bindable(),
		onseek,
		live = false,
		working = null,
		error = null,
		onpoke,
		onablate,
		where = 'server',
		ablateLive,
		pending = false
	}: {
		trace: Trace;
		step: number;
		ablated: boolean;
		onseek: (i: number) => void;
		live?: boolean;
		working?: string | null;
		error?: string | null;
		onpoke?: (step: number, forced: number) => void;
		onablate?: () => void;
		/** where live interventions run: Savant-4B in this browser, or the local server */
		where?: 'browser' | 'server';
		/** the adapter switch can run live (the browser has no base weights) */
		ablateLive?: boolean;
		/** the run is still going */
		pending?: boolean;
	} = $props();
	const here = $derived(where === 'browser');
	const canAblate = $derived(ablateLive ?? live);

	const isLlm = $derived(trace.kind === 'llm');
	const pokes = $derived(trace.pokes);
	const at = $derived([...new Set(pokes.map((p) => p.step))]);
	const matched = $derived(pokes.filter((p) => p.match).length);
	const newest = $derived(pokes.findLast((p) => p.live));
	const abl = $derived(trace.ablation);
	const count = $derived(trace.steps.length);
	let chosenStep = $state<number | null>(null);
	let chosen = $state<number | null>(null);
	const pokeStep = $derived(chosenStep ?? newest?.step ?? at[0] ?? null);
	const options = $derived(pokes.filter((p) => p.step === pokeStep));
	const poke = $derived(
		options[chosen ?? Math.max(0, newest ? options.lastIndexOf(newest) : 0)] ?? null
	);
	const has = $derived(pokes.length > 0);
	const short = $derived(
		pending
			? 'after the run'
			: live
				? here
					? 'in this browser'
					: 'on the live model'
				: has
					? isLlm
						? 'recorded from the live model'
						: 'recorded on this machine'
					: 'needs the live model'
	);
	const source = $derived(
		has
			? trace.panels.poke
			: {
					source: null,
					mock: false,
					note: live
						? here
							? 'run one in this browser'
							: 'run one on the live model'
						: 'needs the live model'
				}
	);
	/** The live poke: the playhead's tick, the state entering it, and the state to force instead. */
	const states = $derived(trace.program.states);
	const entering = $derived(step > 0 ? trace.steps[step - 1]?.t : trace.program.start);
	let forced = $state<number | null>(null);
	const forcedName = $derived(forced !== null ? states[forced] : null);
	const what = $derived(isLlm ? 'Switch off the executor adapter' : 'Switch off the head');
	/** a number-mode run: the state is the carry, and a poke changes the sum */
	const mealy = $derived(!!trace.program.mealy);

	function pickStep(s: number) {
		chosenStep = s;
		chosen = 0;
		ablated = false;
		onseek(s);
	}
	function runPoke() {
		if (forced === null || !onpoke) return;
		chosenStep = null;
		chosen = null;
		ablated = false;
		onpoke(step, forced);
	}
</script>

<Pane
	n={5}
	title="Poke the brain"
	{source}
	{short}
	none={live && isLlm ? 'not run yet' : 'not recorded'}
>
	<div class="poke">
		{#if pending}
			<p class="quiet">
				Pokes open when the run has finished: then force any state at any tick and the model runs on
				from there{here ? ', here on your GPU' : ''}.
			</p>
		{:else}
			<div class="block">
				<div class="row-head">
					<span class="label">{mealy ? 'Force a carry' : 'Force a state'}</span>
					{#if has}<span class="quiet num">{matched} of {pokes.length} match the program</span>{/if}
				</div>
				{#if live && isLlm}
					<div class="choices" role="group" aria-label="State to force at the playhead">
						<span class="k">{mealy ? 'column' : 'at'} {int(step + 1)}</span>
						{#each states as s, k (s)}
							<button
								aria-pressed={k === forced}
								disabled={s === entering || !!working}
								title={s === entering ? 'the state the run has here' : undefined}
								onclick={() => (forced = k)}>{s}</button
							>
						{/each}
					</div>
					<div class="choices">
						<button
							class="go"
							disabled={forced === null || forcedName === entering || !!working}
							onclick={runPoke}
							>{working === 'poke'
								? 'Running on the live model…'
								: forcedName && forcedName !== entering
									? `Force ${forcedName} instead of ${entering}, run on`
									: 'Pick a state to force, then run on'}</button
						>
					</div>
				{/if}
				{#if has && pokeStep !== null}
					<div class="choices" role="group" aria-label="Step to poke">
						<span class="k">at step</span>
						{#each at as s (s)}
							<button aria-pressed={s === pokeStep} onclick={() => pickStep(s)}>{int(s + 1)}</button
							>
						{/each}
					</div>
					<div class="choices" role="group" aria-label="State forced">
						<span class="k">force</span>
						{#each options as p, k (`${p.forced}-${k}`)}
							<button aria-pressed={p === poke} onclick={() => (chosen = k)}
								>{p.forced}{p.live ? ' ·' : ''}</button
							>
						{/each}
					</div>
					{#if poke}
						<dl class="result">
							<div>
								<dt>was</dt>
								<dd>
									{mealy ? `carry ${poke.from} into column ${int(poke.step + 1)}` : poke.from},
									forced to
									{poke.forced}; the run resumed from there
								</dd>
							</div>
							{#if poke.sum_after !== undefined}
								<div>
									<dt>clock's sum</dt>
									<dd class="num">{poke.sum_after}</dd>
								</div>
							{/if}
							<div>
								<dt>model answered</dt>
								<dd>{poke.answer_after}</dd>
							</div>
							<div>
								<dt>program predicts</dt>
								<dd>
									{poke.predicted ??
										(poke.predicted_state !== null
											? `the state ${poke.predicted_state}`
											: 'nothing: its table has no row on the way')}
								</dd>
							</div>
						</dl>
						{#if isLlm && poke.sum_after !== undefined}
							<p class={['verdict', poke.match ? 'ok' : 'bad']}>
								{poke.match
									? 'The sum came out where the table says from the forced carry.'
									: `The sum came out as ${poke.sum_after}; the table says ${poke.predicted_sum ?? 'nothing'}.`}
								{#if poke.answer_states_prediction === true}The words state that sum.{:else if poke.answer_states_prediction === false}The
									words do not state it.{/if}
							</p>
							{#if poke.ticks}
								<p class="quiet num">
									{int(poke.ticks_equal ?? 0)} of {int(poke.ticks)} columns after the poke bitwise equal
									to their certified row{poke.live
										? here
											? ' · run in this browser'
											: ' · run live'
										: ''}
								</p>
							{/if}
						{:else if isLlm}
							<p class={['verdict', poke.match ? 'ok' : 'bad']}>
								{poke.match
									? `The run ended at ${poke.final}, where the table says.`
									: `The run ended at ${poke.final}; the table says ${poke.predicted_state ?? 'nothing'}.`}
								{#if poke.answer_states_prediction === true}The words state that answer.{:else if poke.answer_states_prediction === false}The
									words do not state it.{/if}
							</p>
							{#if poke.ticks}
								<p class="quiet num">
									{int(poke.ticks_equal ?? 0)} of {int(poke.ticks)} ticks after the poke bitwise equal
									to their certified row{poke.live
										? here
											? ' · run in this browser'
											: ' · run live'
										: ''}
								</p>
							{/if}
						{:else}
							<p class={['verdict', poke.match ? 'ok' : 'bad']}>
								{poke.match
									? 'Same answer: the forced state carried through.'
									: 'Different answer.'}
							</p>
						{/if}
					{/if}
				{:else if !live}
					<div class="choices">
						<button disabled>Pick a step</button>
					</div>
					<p class="quiet">
						Needs the live model: no pokes were recorded {isLlm
							? 'on this register'
							: 'for this run'}.
					</p>
				{/if}
			</div>

			<div class="block">
				<div class="row-head">
					<span class="label">{what}</span>
				</div>
				{#if abl}
					<div
						class="choices"
						role="group"
						aria-label={isLlm ? 'The executor adapter' : 'The executing head'}
					>
						<button aria-pressed={!ablated} onclick={() => (ablated = false)}>on</button>
						<button aria-pressed={ablated} onclick={() => (ablated = true)}>off</button>
					</div>
					{#if ablated && isLlm}
						<p class="out num">
							{#if abl.base_certificate}
								Without the adapter the base weights get {int(abl.base_certificate.rows_right)} of
								{int(abl.base_certificate.rows)} rows right.
							{/if}
							{#if abl.first_wrong_step === null}
								The run never leaves the adapter's.
							{:else}
								The run first leaves the adapter's at step {int(abl.first_wrong_step + 1)};
								{int(abl.steps_wrong)} of {int(count)} steps differ{#if abl.off_table_steps}, {int(
										abl.off_table_steps
									)} land off the table{/if}.
							{/if}
							Answer becomes <q>{abl.answer}</q>{#if abl.correct === true}, which happens to be
								right{:else if abl.correct === false}, which is wrong{/if}.
						</p>
					{:else if ablated}
						<p class="out num">
							Answer becomes <q>{abl.answer}</q>. The state sticks at <b>{abl.state}</b>;
							{int(abl.steps_wrong)} of {int(count)} steps wrong, the first at step {int(
								(abl.first_wrong_step ?? 0) + 1
							)}.
							{#if abl.correct}The final answer happens to be right; the steps are not.{/if}
						</p>
					{:else}
						<p class="quiet">
							{isLlm
								? `${abl.live ? 'Run live' : 'Recorded'}: the same table and ticks on the base Qwen3-4B weights.`
								: "Recorded: the same run with the head's output set to zero at every step."}
						</p>
					{/if}
				{:else if canAblate && isLlm}
					<div class="choices">
						<button class="go" disabled={!!working} onclick={() => onablate?.()}
							>{working === 'ablate'
								? 'Running on the live model…'
								: 'Run with the adapter off'}</button
						>
					</div>
					<p class="quiet">The same table and every tick on the base weights, then the words.</p>
				{:else if here && isLlm}
					<div class="choices">
						<button disabled>off</button>
					</div>
					<p class="quiet">
						Switching the adapter off needs the base Qwen3-4B weights, another few GB this page does
						not download. It was recorded on the server for the suggested questions marked
						“recorded”: send one of those to see it.
					</p>
				{:else}
					<div class="choices">
						<button disabled>off</button>
					</div>
					<p class="quiet">
						Needs the live model: no ablation was recorded {isLlm
							? 'on this register'
							: 'for this run'}.
					</p>
				{/if}
			</div>
		{/if}
		{#if error}
			<p class="error">{here ? 'The run stopped' : 'The live model said'}: {error}</p>
		{/if}
	</div>
</Pane>

<style>
	.poke {
		display: grid;
		gap: 14px;
		align-content: start;
		overflow-y: auto;
	}
	.block {
		display: grid;
		gap: 6px;
	}
	.row-head {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 8px;
	}
	.label {
		font-size: var(--text-xs);
		color: var(--color-ink);
	}
	.quiet {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		line-height: 1.5;
	}
	.choices {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 2px 12px;
	}
	.k {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		min-width: 6ch;
	}
	button {
		border: 0;
		border-radius: 0;
		background: transparent;
		padding: 3px 0;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		cursor: pointer;
	}
	button:hover:not(:disabled),
	button[aria-pressed='true'] {
		color: var(--color-ink);
	}
	button[aria-pressed='true'] {
		text-decoration: underline;
		text-underline-offset: 5px;
		text-decoration-thickness: 1px;
	}
	button:disabled {
		opacity: 0.4;
		cursor: default;
	}
	button.go {
		padding: 4px 9px;
		border: 1px solid var(--color-edge);
		border-radius: 4px;
		color: var(--color-ink-2);
		font-family: inherit;
	}
	button.go:hover:not(:disabled) {
		border-color: var(--color-rule);
	}
	.result {
		display: grid;
		gap: 2px;
		margin: 2px 0 0;
		font-size: var(--text-2xs);
	}
	.result div {
		display: grid;
		grid-template-columns: 14ch minmax(0, 1fr);
		gap: 8px;
	}
	dt {
		color: var(--color-ink-3);
	}
	dd {
		color: var(--color-ink);
		overflow-wrap: anywhere;
	}
	.verdict {
		font-size: var(--text-2xs);
		color: var(--color-ink);
		line-height: 1.5;
	}
	.verdict.bad {
		text-decoration: underline wavy;
	}
	.out {
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-2);
	}
	.out b,
	.out q {
		color: var(--color-ink);
		font-weight: 500;
	}
	.error {
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
		text-decoration: underline wavy;
		overflow-wrap: anywhere;
	}
</style>
