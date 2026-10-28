<script lang="ts">
	/**
	 * The chat. Suggested questions drop into the box for editing. With Savant-4B loaded, every question runs in this
	 * browser and the chat follows it stage by stage; without it, the recorded runs replay, and a question with no
	 * recording asks for the model. The local server's live model (dev only) still works when it answers.
	 */
	import type { Attachment } from 'svelte/attachments';
	import { SvelteSet } from 'svelte/reactivity';
	import Icon from '#lib/ui/Icon.svelte';
	import { Send } from '#lib/ui/icons.ts';
	import ModelPanel from './ModelPanel.svelte';
	import { opOfRows } from './mealy.ts';
	import ReasonReply from './ReasonReply.svelte';
	import Reply from './Reply.svelte';
	import { PLAIN_NOTE } from './webgpu/engine.ts';
	import type { Health } from './live.ts';
	import {
		adapterName,
		int,
		runNote,
		taskOf,
		unitOf,
		type LiveTurn,
		type LlmTrace,
		type Trace,
		type TraceEntry,
		type Turn
	} from './trace.ts';
	import type { LiveRun } from './webgpu/live-view.ts';
	import {
		ADDITION_DIGITS,
		additionTicks,
		exactReason,
		FAMILIES,
		LOOKUP_AFTER,
		makeAddition,
		REASON_PROMPTS,
		ticksOf,
		type Addition,
		type PromptSet,
		type ReasonPrompt,
		type SuggestedPrompt
	} from './webgpu/prompts.ts';
	import { savant } from './webgpu/savant.svelte.ts';

	let {
		entries,
		prompts,
		turns,
		active,
		done,
		step,
		server,
		working,
		msPerTick,
		draft = $bindable(),
		fast = $bindable(),
		picked = $bindable(),
		pickedPrompt = $bindable(),
		pickedAddition = $bindable(null),
		traceFor,
		fileFor,
		runFor,
		onsend,
		onreplay,
		onbase,
		onstop,
		onretry,
		oncall,
		shownCall = null
	}: {
		entries: TraceEntry[];
		prompts: PromptSet | null;
		turns: Turn[];
		active: number | null;
		done: Set<number>;
		step: number;
		server: Health | null;
		working: string | null;
		/** measured on this GPU by the last run, for estimates */
		msPerTick: number | null;
		draft: string;
		/** lookup mode: real ticks for the first LOOKUP_AFTER events, then the certified rows */
		fast: boolean;
		picked: TraceEntry | null;
		pickedPrompt: SuggestedPrompt | null;
		/** a suggested addition: its numbers go with the question so the run can be scored */
		pickedAddition?: Addition | null;
		traceFor: (id: string) => Trace | undefined;
		fileFor: (id: string) => LlmTrace | undefined;
		runFor: (key: number) => LiveRun | undefined;
		onsend: () => void;
		onreplay: (key: number) => void;
		onbase: (id: string) => void;
		onstop: (key: number) => void;
		onretry: (key: number) => void;
		/** a reply with calls in the middle: show call k of this turn in the panels */
		oncall?: (key: number, k: number) => void;
		/** the turn and call the panels show */
		shownCall?: { key: number; k: number } | null;
	} = $props();

	const older = $derived(entries.filter((e) => e.group !== 'llm'));
	const ready = $derived(savant.status === 'ready');
	const edited = $derived(
		(!!picked && draft.trim() !== picked.prompt.trim()) ||
			(!!pickedPrompt && draft.trim() !== pickedPrompt.question.trim()) ||
			(!!pickedAddition && draft.trim() !== pickedAddition.question.trim())
	);
	const model = $derived(savant.model);
	/** the Addition suggestion: on for a model trained to write the adder */
	const arithmetic = $derived(model.arithmetic);
	/** composites instead of the six families: this model calls programs in the middle of the words */
	const reasoning = $derived(model.multiCall);
	const ADDITION = 'addition';
	/** second sentence of the reasoning scope hint; kept as one string so the text node has no line break */
	const reasonAddition = 'Additions of any length are among them too.';

	let family = $state<string | null>(null);
	const ofFamily = $derived(
		prompts?.prompts.filter((p) => p.family === family && !p.recorded) ?? []
	);
	const recordedOf = $derived(
		prompts?.prompts.filter((p) => p.family === family && p.recorded) ?? []
	);
	let showOlder = $state(false);

	const STAGES: Record<LiveTurn['stage'], string> = {
		connecting: 'Sending to the live model',
		compile: 'Writing the program',
		tape: 'Reading the tape from the question',
		certify: 'Certifying every row',
		run: 'Running one tick per event',
		answer: 'Writing the answer',
		done: 'Done',
		error: 'Stopped'
	};
	function liveLine(s: LiveTurn) {
		const what = STAGES[s.stage] ?? s.stage;
		const reg = s.register ? ` (register ${s.register})` : '';
		const n = s.stage === 'run' && s.total ? ` · ${int(s.done)} of ${int(s.total)}` : '';
		return `${what}${reg}${n}`;
	}

	/** One line for a run in this browser, and how far along its bar is. */
	function browserLine(r: LiveRun): { text: string; frac: number | null } {
		const line = stageLine(r);
		// calls in the middle (REASON_FORMAT): which call the clock has, and the words between calls
		const call = r.reason?.current;
		if (call && line.text) return { ...line, text: `Call ${call.k} · ${line.text}` };
		if (r.reason && r.stage === 'compile')
			return { text: `Writing · ${int(r.compile.tokens)} tokens`, frac: null };
		return line;
	}

	function stageLine(r: LiveRun): { text: string; frac: number | null } {
		const reg = r.at ? r.registers[r.at.register] : null;
		const regName = reg && r.registers.length > 1 ? ` ${reg.name}` : '';
		switch (r.stage) {
			case 'queued':
				return { text: `Waiting for ${model.short} to finish loading`, frac: null };
			case 'prefill':
				return {
					text: `Reading your question · ${int(r.prefill.done)} of ${int(r.prefill.total)} tokens`,
					frac: r.prefill.total ? r.prefill.done / r.prefill.total : null
				};
			case 'compile':
				return { text: `Writing the program · ${int(r.compile.tokens)} tokens`, frac: null };
			case 'tape':
				return {
					text: r.reason?.current ? 'Reading its input' : 'Reading the tape from the question',
					frac: null
				};
			case 'certify':
				return {
					text: `Certifying register${regName} · row ${int(r.at?.rows ?? 0)} of ${int(reg?.program.rows.length ?? 0)}`,
					frac: reg ? (r.at?.rows ?? 0) / reg.program.rows.length : null
				};
			case 'run':
				return {
					text: reg?.program.mealy
						? `${opOfRows(reg.program.rows) === 'sub' ? 'Subtracting' : 'Adding'} · column ${int(r.at?.ticks ?? 0)} of ${int(r.tape?.events.length ?? 0)}`
						: `Running register${regName} · tick ${int(r.at?.ticks ?? 0)} of ${int(r.tape?.events.length ?? 0)}`,
					frac: r.tape ? (r.at?.ticks ?? 0) / r.tape.events.length : null
				};
			case 'answer':
				return { text: 'Writing the answer', frac: null };
			default:
				return { text: '', frac: null };
		}
	}

	const open = new SvelteSet<number>();
	const base = new SvelteSet<number>();
	const toggle = (set: SvelteSet<number>, k: number) => {
		if (set.has(k)) set.delete(k);
		else set.add(k);
	};
	const CLIP = 220;
	let box: HTMLTextAreaElement | undefined;
	const holdBox: Attachment<HTMLTextAreaElement> = (el) => {
		box = el;
		return () => (box = undefined);
	};

	/** Keeps the newest exchange in view when one is added and when its answer arrives. */
	const follow: Attachment<HTMLElement> = (el) => {
		void turns.length;
		void done.size;
		el.scrollTo({ top: el.scrollHeight });
	};

	function focusBox() {
		box?.focus();
		box?.setSelectionRange(0, 0);
		if (box) box.scrollTop = 0;
	}
	function pickReason(p: ReasonPrompt) {
		pickedPrompt = null;
		pickedAddition = null;
		picked = null;
		family = null;
		draft = p.question;
		focusBox();
	}
	function pick(e: TraceEntry) {
		picked = e;
		pickedPrompt = null;
		pickedAddition = null;
		draft = e.prompt;
		focusBox();
	}
	function pickPrompt(p: SuggestedPrompt) {
		pickedPrompt = p;
		pickedAddition = null;
		family = p.family;
		picked = p.recorded ? (entries.find((e) => e.id === p.recorded) ?? null) : null;
		draft = p.question;
		focusBox();
	}
	/** Two new random numbers of this length each time. */
	function pickAddition(digits: number) {
		const add = makeAddition(digits);
		pickedAddition = add;
		pickedPrompt = null;
		picked = null;
		family = ADDITION;
		draft = add.question;
		focusBox();
	}
	function pickFamily(id: string) {
		family = id;
		if (id === ADDITION) return pickAddition(ADDITION_DIGITS[0]);
		const p =
			prompts?.prompts.find((x) => x.family === id && x.default) ??
			prompts?.prompts.find((x) => x.family === id);
		if (p) pickPrompt(p);
	}
	function key(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
			e.preventDefault();
			if (draft.trim()) onsend();
		}
	}
	const lengthLabel = (p: SuggestedPrompt) => int(p.truth.events);
	const estimate = (p: SuggestedPrompt | Addition) => {
		const n =
			'digits' in p
				? additionTicks(p, fast ? LOOKUP_AFTER : null)
				: ticksOf(p, fast ? LOOKUP_AFTER : null);
		return msPerTick
			? `about ${Math.max(1, Math.round((n * msPerTick) / 1000 + 4))} s`
			: `${int(n)} ticks`;
	};
</script>

<div class="chat">
	{#if turns.length}<ModelPanel compact />{/if}
	<div class="log" {@attach follow} aria-live="polite">
		{#if turns.length === 0}
			<div class="empty">
				<p class="eyebrow">Interpreter</p>
				<h1>A model that writes a program and runs it inside</h1>
				<p class="intro">
					{#if reasoning}
						Ask a question that takes more than one step. The model reasons in words and calls a
						program in the middle, the clock runs it, and the model reads the result and goes on.
						The panels follow the call it is in.
					{:else}
						Ask a question about a long list of events. The model writes a small table for it,
						proves every row of the table correct, then runs it one tick per event, and the five
						panels show the inside of that run as it happens.
					{/if}
				</p>
				{#if server}
					<p class="replay-note">
						<span class="live-word">live</span> The local server is connected: {server.model} with the
						compile adapter {adapterName(server.adapters.compile_adapter)} and the executor
						{adapterName(server.adapters.executor_adapter)}, on a GPU through this machine’s local
						server. {server.warm
							? 'It is warm.'
							: 'It is cold: the first question waits a few minutes for the GPU.'}
					</p>
				{/if}
				<ModelPanel />
			</div>
		{/if}
		{#each turns as turn (turn.key)}
			{@const run = turn.browser ? runFor(turn.key) : undefined}
			{@const id = turn.live?.id ?? turn.browser ?? turn.entry?.id}
			{@const t = id && (!run || run.stage === 'done') ? traceFor(id) : undefined}
			{@const isOpen = open.has(turn.key)}
			<div class="user">
				<p class="msg">
					{isOpen || turn.text.length <= CLIP
						? turn.text
						: turn.text.slice(0, CLIP).trimEnd() + ' …'}
				</p>
				{#if turn.text.length > CLIP}
					<button class="link" onclick={() => toggle(open, turn.key)}
						>{isOpen ? 'Show less' : `Show all ${int(turn.text.length)} characters`}</button
					>
				{/if}
			</div>
			<div class={['bot', turn.key === active && 'active']}>
				{#if run && run.stage !== 'done'}
					{#if run.stage === 'error' || run.stage === 'stopped'}
						<p class="msg">
							{run.stage === 'stopped' ? 'Stopped.' : `The run stopped: ${run.error}`}
						</p>
						<div class="actions">
							<button
								class="link"
								disabled={!ready || savant.busy}
								onclick={() => onretry(turn.key)}>Run it again</button
							>
						</div>
					{:else}
						{@const line = browserLine(run)}
						{#if run.reason}
							<ReasonReply segments={run.reason.segments} calls={run.reason.calls} live={run} />
						{/if}
						<p class="quiet num" role="status">
							<span class="live-word">{model.short}</span>
							{line.text}
						</p>
						{#if line.frac !== null}
							<div class="bar-mini" aria-hidden="true">
								<span style:width="{line.frac * 100}%"></span>
							</div>
						{/if}
						{#if run.stage === 'answer' && run.answer}
							<p class="msg answer streaming">{run.answer}</p>
						{/if}
						<div class="actions">
							<button class="link" onclick={() => onstop(turn.key)}>Stop</button>
						</div>
					{/if}
				{:else if turn.needsModel}
					{#if savant.status === 'unsupported'}
						<p class="msg">
							There is no recorded run of this question, and this browser cannot run {model.short}:
							{savant.gpu?.reason}
						</p>
						<p class="quiet">The suggested questions marked “recorded” replay here.</p>
					{:else if ready}
						<p class="msg">{model.short} is loaded now.</p>
						<div class="actions">
							<button class="link" onclick={() => onretry(turn.key)}>Run this question</button>
						</div>
					{:else}
						<p class="msg">
							There is no recorded run of this question. Load {model.short} and it runs here, in your
							browser.
						</p>
						<div class="actions">
							<button
								class="btn primary small"
								disabled={savant.status === 'loading' || savant.status === 'checking'}
								onclick={() => savant.load()}
								>{savant.status === 'loading' ? 'Loading…' : `Load ${model.short}`}</button
							>
							<span class="quiet">It runs as soon as the model is ready.</span>
						</div>
					{/if}
				{:else if turn.live && turn.live.stage !== 'done'}
					{@const s = turn.live}
					{#if s.stage === 'error'}
						<p class="msg">The live run stopped: {s.error}</p>
					{:else}
						<p class="quiet num" role="status">
							<span class="live-word">live</span>
							{liveLine(s)}{#if s.detail}<br />{s.detail}{/if}
						</p>
						{#if s.stage === 'run' && s.total}
							<div class="bar-mini" aria-hidden="true">
								<span style:width="{(s.done / s.total) * 100}%"></span>
							</div>
						{/if}
					{/if}
				{:else if !turn.entry && !turn.live && !turn.browser}
					<p class="msg">
						This page replays recorded runs, and there is none for this question. Answering it needs
						the live model.
					</p>
				{:else}
					{#if turn.edited}
						<p class="notice">
							Your edit was not run: that needs the model. Replaying the recorded run of the
							original question.
						</p>
					{/if}
					{@const multi = id ? fileFor(id) : undefined}
					{#if multi?.reason}
						<ReasonReply
							segments={multi.reason.segments}
							calls={multi.reason.calls}
							end={multi.reason.end}
							shown={shownCall?.key === turn.key ? shownCall.k : null}
							onshow={oncall ? (k) => oncall(turn.key, k) : undefined}
						/>
						<p class="prov num">
							{#if multi.where === 'browser'}
								<span class="live-word">here</span>
								Written by {multi.model.name} in this browser on {multi.host.gpu}; every call run by
								the clock on a table certified first{multi.timing?.total
									? `, ${multi.timing.total.toFixed(1)} s in all`
									: ''}.
							{:else}
								Written by {multi.model.name}; every call run by the clock on a table certified
								first.
							{/if}
						</p>
						{#if turn.key !== active}
							<div class="actions">
								<button class="link" onclick={() => onreplay(turn.key)}>Show this run</button>
							</div>
						{/if}
					{:else if !t}
						{@const file = id ? fileFor(id) : undefined}
						{#if file}
							{#if file.note === PLAIN_NOTE}
								{#if file.answer}<div class="msg answer"><Reply text={file.answer} /></div>{/if}
								<p class="note">Answered directly, in words: this question needed no program.</p>
							{:else}
								{#if file.answer}<p class="msg answer">{file.answer}</p>{/if}
								<p class="note">
									{file.note ?? 'The model wrote no table that could run'}, so there is no run; what
									it wrote is on the right.{#if file.truth}
										No answer (truth: {file.truth}).{/if}
								</p>
							{/if}
						{:else}
							<p class="quiet">Loading the recorded run…</p>
						{/if}
					{:else if !done.has(turn.key) && turn.key !== active}
						<p class="quiet">
							Replay stopped before the end.
							<button class="link" onclick={() => onreplay(turn.key)}>Show this run</button>
						</p>
					{:else if !done.has(turn.key)}
						<p class="quiet num">
							{turn.live ? 'Replaying the live run' : 'Running the program'} · {unitOf(t.title)}
							{int(Math.min(step + 1, t.steps.length))} of {int(t.steps.length)}
						</p>
					{:else}
						{@const f = t.llm?.file}
						<p class="msg answer">{t.answer}</p>
						<p class="note num">
							{runNote(t)}{#if t.exact === false}<span class="warn"
									>· the run made a wrong step</span
								>{/if}
						</p>
						{#if f}
							<p class="prov num">
								{#if f.where === 'browser'}
									<span class="live-word">here</span>
									Written and run by {f.model.name} in this browser on {f.host.gpu}{f.timing?.total
										? `, ${f.timing.total.toFixed(1)} s in all`
										: ''}{f.registers[0]?.ticks.ms_per_tick
										? `, ${Math.round(f.registers[0].ticks.ms_per_tick)} ms per tick`
										: ''}.
								{:else}
									{#if f.live}<span class="live-word">live</span>{/if}
									Program written by {f.model.name} with the compile adapter {adapterName(
										f.model.compile_adapter
									)}; every tick ran on the executor {adapterName(f.model.executor_adapter)}.
								{/if}
								{#if f.arith}
									{@const right = f.arith.sum !== null && f.arith.sum === f.arith.check}
									{right ? 'Right' : 'Wrong'}: the clock’s sum {right ? 'is' : 'is not'} the sum of the
									two numbers it read, checked on this page with exact integers{#if f.score && !f.score.tape_exact},
										but it read other numbers than the question’s{/if}{#if f.score}; the words {f
											.score.answer_correct
											? 'state it'
											: 'do not state it'}{/if}.
								{:else if f.truth !== null}
									{f.score?.answer_correct ? 'Right' : 'Wrong'} (truth: {f.truth}).
								{:else if exactReason(f.prompt)}
									A composite from this model’s training templates. This page does not score it.
								{:else}
									No reference answer: the question is not one of the suggested ones.
								{/if}
								{#if f.cost}{f.cost.container_seconds.toFixed(0)} s of GPU time.{/if}
							</p>
						{:else if t.panels.program.mock}
							<p class="prov">
								<span class="mock">mock</span> program, written by the question's generator; the run on
								the frozen core is real.
							</p>
						{:else}
							<p class="prov">Hand-written program; the run on the frozen core is real.</p>
						{/if}
						<div class="actions">
							{#if turn.key !== active}
								<button class="link" onclick={() => onreplay(turn.key)}>Show this run</button>
							{/if}
							{#if t.base_answer !== null && t.base_answer_meta}
								<button
									class="link"
									aria-expanded={base.has(turn.key)}
									onclick={() => toggle(base, turn.key)}
									>{base.has(turn.key) ? 'Hide' : 'Show'} the base model's answer{t.base_answer_meta
										.live
										? ''
										: ' (recorded)'}</button
								>
							{:else if f && server && f.where !== 'browser'}
								<button
									class="link"
									disabled={!!working}
									onclick={() => {
										if (id) onbase(id);
										base.add(turn.key);
									}}
									>{working === 'base'
										? 'Asking the base model…'
										: 'Ask the base model (no adapter)'}</button
								>
							{:else if f?.where === 'browser'}
								<span class="quiet"
									>The base model’s answer needs the base Qwen3-4B weights, which this page does not
									download; it is recorded for the questions marked “recorded”.</span
								>
							{:else}
								<span class="quiet">No base model answer recorded for this prompt.</span>
							{/if}
						</div>
						{#if base.has(turn.key) && t.base_answer_meta}
							{@const m = t.base_answer_meta}
							<div class="base">
								<p class="who">
									<span class="measured">{m.live ? 'live' : 'recorded'}</span>
									{m.model}, same question, {m.mode}{m.hit_max_tokens
										? ', hit its token budget'
										: ''}
								</p>
								<p class="msg">{t.base_answer || '(no answer)'}</p>
								<p class="quiet num">
									{#if m.correct !== null && t.truth}
										{m.correct ? 'Right' : 'Wrong'} (truth: {t.truth}).
									{:else}
										No reference answer to score it against.
									{/if}
									{#if m.cell_correct}
										On this kind of question it got
										{m.cell_correct[0]} of {m.cell_correct[1]} right{#if m.cell_wilson95}, 95%
											interval
											{(m.cell_wilson95[0] * 100).toFixed(0)}–{(m.cell_wilson95[1] * 100).toFixed(
												0
											)}%{/if}.
									{:else}
										{int(m.response_tokens)} tokens{#if m.seconds}, {m.seconds.toFixed(0)} s{/if}.
									{/if}
									{#if m.excerpt}Shown: {m.excerpt}.{/if}
								</p>
							</div>
						{/if}
					{/if}
				{/if}
			</div>
		{/each}
	</div>

	<div class="compose">
		<div class="suggest" role="group" aria-label="Suggested questions">
			<div class="items families">
				{#if reasoning}
					{#each REASON_PROMPTS as p (p.id)}
						<button
							class="sugg"
							aria-pressed={draft.trim() === p.question.trim()}
							title={p.question}
							onclick={() => pickReason(p)}>{p.title}</button
						>
					{/each}
				{:else}
					{#each FAMILIES as f (f.id)}
						<button
							class="sugg"
							aria-pressed={family === f.id}
							title={f.label}
							onclick={() => pickFamily(f.id)}>{f.label}</button
						>
					{/each}
				{/if}
				{#if arithmetic}
					<button
						class="sugg"
						aria-pressed={family === ADDITION}
						title="Addition"
						onclick={() => pickFamily(ADDITION)}>Addition</button
					>
				{/if}
			</div>
			{#if family === ADDITION}
				<div class="items lengths" role="group" aria-label="Length">
					<span class="k">digits</span>
					{#each ADDITION_DIGITS as d (d)}
						<button
							class="len num"
							aria-pressed={pickedAddition?.digits === d}
							title="Two new random {int(d)}-digit numbers"
							onclick={() => pickAddition(d)}>{int(d)}</button
						>
					{/each}
				</div>
			{:else if family && !reasoning}
				<div class="items lengths" role="group" aria-label="Length">
					<span class="k">{FAMILIES.find((f) => f.id === family)?.unit}</span>
					{#each ofFamily as p (p.id)}
						<button
							class="len num"
							aria-pressed={pickedPrompt?.id === p.id}
							title={p.title}
							onclick={() => pickPrompt(p)}>{lengthLabel(p)}</button
						>
					{/each}
					{#if recordedOf.length}
						<span class="k rec">recorded</span>
						{#each recordedOf as p (p.id)}
							<button
								class="len num"
								aria-pressed={pickedPrompt?.id === p.id}
								title="{p.title}, recorded"
								onclick={() => pickPrompt(p)}
								>{lengthLabel(p)}{p.heldout_phrasing ? ' new wording' : ''}</button
							>
						{/each}
					{/if}
				</div>
			{/if}
			<p class="hint scope">
				{#if reasoning}
					This preview reasons in words and calls programs along the way. The questions above are
					composites from its training templates.{#if arithmetic}&nbsp;{reasonAddition}{/if}
				{:else if arithmetic}
					This preview runs questions like these seven, additions of any length among them. Other
					new kinds of question are not in it yet.
				{:else}
					This preview runs questions like these six. Arithmetic and other new kinds of question are
					not in it yet.
				{/if}
			</p>
			{#if older.length}
				<button class="more" aria-expanded={showOlder} onclick={() => (showOlder = !showOlder)}
					>{showOlder ? 'Hide' : 'More'} recorded runs: the frozen INTERP core</button
				>
				{#if showOlder}
					<div class="items" role="group" aria-label="Recorded runs on the frozen core">
						{#each older as e (e.id)}
							<button
								class="sugg small"
								aria-pressed={picked?.id === e.id}
								title={e.title}
								onclick={() => pick(e)}
								>{taskOf(e.title)}<span class="meta num"
									>{e.title.slice(taskOf(e.title).length + 2)}</span
								></button
							>
						{/each}
					</div>
				{/if}
			{/if}
		</div>
		<div class="input">
			<textarea
				{@attach holdBox}
				bind:value={draft}
				onkeydown={key}
				rows="3"
				placeholder="Pick a suggested question, or type your own"
				aria-label="Your question"></textarea>
			<button
				class="btn primary icon-only send"
				aria-label="Send"
				disabled={!draft.trim() || (ready && savant.busy)}
				onclick={onsend}><Icon icon={Send} size={16} /></button
			>
		</div>
		{#if ready}
			<div class="mode" role="group" aria-label="Ticks">
				<span class="k">ticks</span>
				<button aria-pressed={!fast} onclick={() => (fast = false)}>every event, on the GPU</button>
				<button
					aria-pressed={fast}
					title="PROMPTBOX's lookup mode: by Theorem P a certified row's tick is the same every time, so after the first {LOOKUP_AFTER} events each step is read from its certified row instead of run"
					onclick={() => (fast = true)}>first {LOOKUP_AFTER}, then the certified rows</button
				>
			</div>
		{/if}
		<p class="hint num">
			{#if ready && !(picked && !pickedPrompt && !edited)}
				<span class="live-word">{model.short}</span>
				{edited ? 'Edited: ' : ''}Enter runs it in this browser{(pickedPrompt ?? pickedAddition) &&
				!edited
					? ` · ${estimate((pickedPrompt ?? pickedAddition)!)}`
					: ''}{savant.busy ? ' · after the current run' : ''}
			{:else if server && (!picked || picked.group === 'llm')}
				<span class="live-word">live</span>
				{edited ? 'Edited: ' : ''}Enter runs it on the live model ({server.warm ? 'warm' : 'cold'})
				· spent so far about ${server.spent_estimate_usd.toFixed(2)} of ${server.cap_usd.toFixed(0)}
			{:else if picked && !edited}
				Enter replays the recorded run{savant.status !== 'unsupported'
					? ` · load ${model.short} to run it yourself`
					: ''}
			{:else if draft.trim()}
				{savant.status === 'unsupported'
					? 'This browser cannot run the model: only recorded questions replay.'
					: savant.status === 'loading'
						? `Enter queues it: it runs when ${model.short} has loaded`
						: `Load ${model.short} to run this question in your browser`}
			{:else}
				Enter sends · Shift+Enter for a new line
			{/if}
		</p>
	</div>
</div>

<style>
	.chat {
		display: flex;
		flex-direction: column;
		height: 100%;
		min-height: 0;
	}
	.log {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
		padding: 22px 22px 12px;
		display: flex;
		flex-direction: column;
		gap: 14px;
	}
	.empty {
		margin: auto 0 8px;
	}
	.eyebrow {
		font-size: 10px;
		text-transform: uppercase;
		letter-spacing: 0.14em;
		color: var(--color-ink-3);
		margin-bottom: 6px;
	}
	h1 {
		font-size: 26px;
		font-family: 'KaTeX_Main', 'Times New Roman', serif;
		font-weight: 400;
		line-height: 1.18;
		max-width: 22ch;
	}
	.intro {
		margin-top: 10px;
		font-size: var(--text-sm);
		line-height: 1.6;
		color: var(--color-ink-2);
	}
	.replay-note {
		margin-top: 10px;
		font-size: var(--text-2xs);
		line-height: 1.55;
		color: var(--color-ink-3);
	}
	.user {
		align-self: flex-end;
		max-width: 92%;
		padding: 9px 12px;
		border-radius: 8px;
		background: var(--color-lift);
	}
	.msg {
		font-size: var(--text-sm);
		line-height: 1.55;
		color: var(--color-ink);
		white-space: pre-wrap;
		overflow-wrap: anywhere;
	}
	.user .msg {
		color: var(--color-ink-2);
		font-size: var(--text-xs);
	}
	.bot {
		display: grid;
		gap: 5px;
		padding-left: 12px;
		border-left: 1px solid var(--color-edge);
		transition: border-color 200ms ease-in-out;
	}
	.bot.active {
		border-left-color: var(--color-ink-2);
	}
	.answer {
		font-size: var(--text-ui);
	}
	.msg :global(.reply) {
		white-space: normal;
	}
	.streaming {
		color: var(--color-ink-2);
	}
	.note {
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.warn {
		margin-left: 0.35em;
		color: var(--color-ink);
		text-decoration: underline wavy;
	}
	.prov,
	.quiet {
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-3);
	}
	.notice {
		font-size: var(--text-2xs);
		line-height: 1.5;
		color: var(--color-ink-2);
	}
	.mock {
		color: var(--color-ink);
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-size: 10px;
		text-decoration: underline dashed;
		text-underline-offset: 3px;
	}
	.measured {
		color: var(--color-ink-3);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		font-size: 10px;
		margin-right: 4px;
	}
	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 16px;
		align-items: baseline;
	}
	.link {
		border: 0;
		padding: 2px 0;
		background: transparent;
		color: var(--color-ink-2);
		font: inherit;
		font-size: var(--text-2xs);
		text-decoration: underline;
		text-decoration-color: var(--color-rule);
		text-underline-offset: 3px;
		cursor: pointer;
	}
	.link:hover {
		color: var(--color-ink);
	}
	.btn.small {
		height: 26px;
		padding: 0 10px;
		font-size: var(--text-2xs);
	}
	.base {
		display: grid;
		gap: 4px;
		margin-top: 4px;
		padding-top: 8px;
		border-top: 1px solid #222;
	}
	.who {
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.base .msg {
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		max-height: 160px;
		overflow-y: auto;
	}
	.compose {
		flex: none;
		padding: 10px 22px 14px;
		border-top: 1px solid #222;
		display: grid;
		gap: 8px;
	}
	.suggest {
		display: grid;
		gap: 4px;
		max-height: 200px;
		overflow-y: auto;
	}
	.items {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 2px 16px;
	}
	.lengths {
		gap: 2px 12px;
	}
	.k {
		font-size: 10px;
		letter-spacing: 0.04em;
		color: var(--color-ink-3);
		min-width: 5.5ch;
	}
	.k.rec {
		min-width: 0;
		margin-left: 6px;
	}
	.live-word {
		margin-right: 4px;
		color: var(--color-ink);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-size: 10px;
		font-weight: 500;
	}
	.bar-mini {
		height: 2px;
		background: var(--color-edge);
		border-radius: 1px;
		overflow: hidden;
	}
	.bar-mini span {
		display: block;
		height: 100%;
		background: var(--color-ink-2);
		transition: width 200ms linear;
	}
	.link:disabled {
		opacity: 0.5;
		cursor: default;
	}
	.sugg,
	.len,
	.more {
		border: 0;
		padding: 3px 0;
		background: transparent;
		font: inherit;
		font-size: var(--text-xs);
		color: var(--color-ink-2);
		cursor: pointer;
		white-space: nowrap;
	}
	.len {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.more {
		justify-self: start;
		font-size: 10px;
		color: var(--color-ink-3);
		letter-spacing: 0.04em;
	}
	.sugg.small {
		font-size: var(--text-2xs);
	}
	.sugg:hover,
	.len:hover,
	.more:hover,
	.sugg[aria-pressed='true'],
	.len[aria-pressed='true'] {
		color: var(--color-ink);
	}
	.sugg[aria-pressed='true'],
	.len[aria-pressed='true'] {
		text-decoration: underline;
		text-underline-offset: 5px;
		text-decoration-thickness: 1px;
	}
	.sugg .meta {
		margin-left: 6px;
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.input {
		position: relative;
	}
	textarea {
		display: block;
		width: 100%;
		min-height: 64px;
		max-height: 168px;
		padding: 9px 46px 9px 11px;
		border: 1px solid var(--color-edge);
		border-radius: 6px;
		background: var(--color-well);
		color: var(--color-ink);
		font: inherit;
		font-size: var(--text-xs);
		line-height: 1.5;
		resize: vertical;
		field-sizing: content;
		/* long unbroken inputs (a bit string, a big number) wrap instead of widening the box and the column */
		max-width: 100%;
		min-width: 0;
		overflow-wrap: anywhere;
		word-break: break-all;
	}
	textarea:focus {
		outline: none;
		border-color: var(--color-rule);
	}
	.send {
		position: absolute;
		right: 7px;
		bottom: 7px;
	}
	.hint {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.mode {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 2px 12px;
		font-size: var(--text-2xs);
	}
	.mode .k {
		min-width: 0;
	}
	.mode button {
		border: 0;
		padding: 2px 0;
		background: transparent;
		font: inherit;
		color: var(--color-ink-3);
		cursor: pointer;
	}
	.mode button:hover,
	.mode button[aria-pressed='true'] {
		color: var(--color-ink);
	}
	.mode button[aria-pressed='true'] {
		text-decoration: underline;
		text-underline-offset: 4px;
	}
</style>
