<script lang="ts">
	import { asset } from '$app/paths';
	import { onMount } from 'svelte';
	import { SvelteMap, SvelteSet } from 'svelte/reactivity';
	import CertificatePanel from '#lib/interpreter/CertificatePanel.svelte';
	import Chat from '#lib/interpreter/Chat.svelte';
	import LiveProgram from '#lib/interpreter/LiveProgram.svelte';
	import NoRunPanel from '#lib/interpreter/NoRunPanel.svelte';
	import PokePanel from '#lib/interpreter/PokePanel.svelte';
	import ProgramPanel from '#lib/interpreter/ProgramPanel.svelte';
	import RunPanel from '#lib/interpreter/RunPanel.svelte';
	import Scrubber from '#lib/interpreter/Scrubber.svelte';
	import StageLine from '#lib/interpreter/StageLine.svelte';
	import StatePanel from '#lib/interpreter/StatePanel.svelte';
	import { connection } from '#lib/interpreter/connection.svelte.ts';
	import * as live from '#lib/interpreter/live.ts';
	import {
		adapterName,
		asTrace,
		cpuName,
		int,
		isLlm,
		unitOf,
		type LiveTurn,
		type LlmRegister,
		type LlmTrace,
		type TraceEntry,
		type TraceFile,
		type TraceStep,
		type Turn
	} from '#lib/interpreter/trace.ts';
	import { MULTI_CALL, SAVANT } from '#lib/interpreter/webgpu/config.ts';
	import {
		applyEvent,
		liveTrace,
		startRun,
		type LiveRun
	} from '#lib/interpreter/webgpu/live-view.ts';
	import {
		exactPrompt,
		LOOKUP_AFTER,
		type Addition,
		type PromptSet,
		type SuggestedPrompt
	} from '#lib/interpreter/webgpu/prompts.ts';
	import { savant, Stopped } from '#lib/interpreter/webgpu/savant.svelte.ts';

	let entries = $state.raw<TraceEntry[]>([]);
	let prompts = $state.raw<PromptSet | null>(null);
	let loadError = $state(false);
	const files = new SvelteMap<string, TraceFile>();
	const pending: Record<string, Promise<TraceFile | null>> = {};
	/** The live model behind the local server, when there is one (never on the published site). */
	let server = $state.raw<live.Health | null>(null);

	let turns = $state<Turn[]>([]);
	let draft = $state('');
	/** lookup mode for runs here: real ticks on the first LOOKUP_AFTER events, then the certified rows */
	let fast = $state(false);
	let picked = $state.raw<TraceEntry | null>(null);
	let pickedPrompt = $state.raw<SuggestedPrompt | null>(null);
	let pickedAddition = $state.raw<Addition | null>(null);
	/** suggested additions sent, by turn: their numbers go with the question to score the run */
	const additions = new SvelteMap<number, Addition>();
	let active = $state<number | null>(null);
	const done = new SvelteSet<number>();
	/** Runs in this browser, by turn: rebuilt from the engine's events as they arrive. */
	const runs = new SvelteMap<number, LiveRun>();
	const rids = new SvelteMap<number, number>();
	/** The trace on the right: the active turn's, else a still preview of the first prompt. */
	let shownId = $state<string | null>(null);
	/** Which register of an LLM run the panels show. */
	let reg = $state(0);
	let step = $state(0);
	let playing = $state(false);
	let ablated = $state(false);
	/** While a run in this browser is going, the panels follow its newest tick unless the visitor scrubs away. */
	let follow = $state(true);
	/** A live intervention in flight, and the last one's error. */
	let working = $state<'poke' | 'ablate' | 'base' | null>(null);
	let liveError = $state<string | null>(null);
	/** Milliseconds per tick on this GPU, from the last run here (for estimates). */
	let msPerTick = $state<number | null>(null);

	/** The active turn's run in this browser while it is still going. */
	const activeRun = $derived(active !== null ? runs.get(active) : undefined);
	const going = $derived(
		activeRun &&
			activeRun.stage !== 'done' &&
			activeRun.stage !== 'error' &&
			activeRun.stage !== 'stopped'
			? activeRun
			: undefined
	);
	/** Before the program is parsed there is nothing for the panels: the model writing is shown instead. */
	const writing = $derived(!!going && !going.registers.length);
	const liveFile = $derived(going && going.registers.length ? liveTrace(going) : null);
	const file = $derived(liveFile ?? (shownId ? (files.get(shownId) ?? null) : null));
	const llm = $derived(file && isLlm(file) ? file : null);
	/** the register shown: the one being worked on while following a run, else the visitor's pick */
	const shownReg = $derived(
		liveFile && follow ? Math.min(going?.at?.register ?? 0, liveFile.registers.length - 1) : reg
	);
	const trace = $derived(file ? asTrace(file, shownReg) : null);
	const count = $derived(trace?.steps.length ?? 0);
	/** this register is being certified right now: no ticks yet */
	const certifying = $derived(!!liveFile && !!trace && count === 0);
	const shownStep = $derived(
		liveFile && follow ? Math.max(0, count - 1) : Math.min(step, Math.max(0, count - 1))
	);
	const cur = $derived.by((): TraceStep | null => {
		if (!trace) return null;
		if (count) return trace.steps[shownStep];
		// certifying: the row being checked, as a step
		const rows = trace.program.rows;
		if (!rows.length) return null;
		const checked = rows.filter((r) => r.ok !== undefined).length;
		const k = Math.min(rows.length - 1, checked);
		const r = rows[k];
		return {
			i: 0,
			event: r.a !== undefined ? `${r.a}+${r.b}` : r.b,
			s: r.s,
			row: k,
			attn: [],
			t: r.t,
			margin: r.m ?? NaN,
			...(r.a !== undefined ? { pair: [r.a, r.b] as [string, string], o: r.o, m2: r.m2 } : {})
		};
	});
	const preview = $derived(active === null);
	/** With the head (INTERP) or the executor adapter (LLM) off: the state at this step, else null. */
	const stuck = $derived.by(() => {
		const a = trace?.ablation;
		if (!ablated || !a) return null;
		if (a.states) return a.states[Math.min(shownStep, a.states.length - 1)] ?? null;
		return a.constant ? a.state : null;
	});
	/** Pokes run in this browser when Savant-4B is loaded, else on the local server when it is up. */
	const pokeWhere = $derived<'browser' | 'server' | null>(
		!llm?.ctx || liveFile
			? null
			: savant.status === 'ready'
				? 'browser'
				: server && llm.where !== 'browser'
					? 'server'
					: null
	);

	function load(entry: TraceEntry): Promise<TraceFile | null> {
		const have = files.get(entry.id);
		if (have) return Promise.resolve(have);
		pending[entry.id] ??= fetch(asset(entry.file as Parameters<typeof asset>[0]))
			.then((r) => (r.ok ? (r.json() as Promise<TraceFile>) : null))
			.then((t) => {
				if (t) files.set(entry.id, t);
				return t;
			})
			.catch(() => null);
		return pending[entry.id];
	}

	const message = (e: unknown) => (e instanceof Error ? e.message : String(e));

	/** A run with one register (or the whole run) changed; panels keep their place because the id stays. */
	function patch(
		f: LlmTrace,
		k: number | null,
		change: Partial<LlmRegister>,
		rest: Partial<LlmTrace> = {}
	) {
		const registers =
			k === null ? f.registers : f.registers.map((r, i) => (i === k ? { ...r, ...change } : r));
		files.set(f.id, { ...f, ...rest, registers });
	}

	async function livePoke(at: number, forced: number) {
		const f = llm;
		if (!f?.ctx || working || !pokeWhere) return;
		const k = reg;
		const r = f.registers[k];
		working = 'poke';
		liveError = null;
		try {
			const p =
				pokeWhere === 'browser'
					? await savant.poke(f.prompt, f.ctx, r.name, at, forced, {
							truth: exactPrompt(prompts, f.prompt)?.truth ?? null,
							from: at > 0 ? r.steps[at - 1]?.t : r.program.start,
							lookupAfter: r.ticks.lookup ? LOOKUP_AFTER : null
						}).done
					: await live.poke(f, r.name, at, forced);
			const now = (files.get(f.id) as LlmTrace | undefined) ?? f;
			const note = pokeWhere === 'browser' ? 'pokes run in this browser' : 'live pokes';
			patch(
				now,
				k,
				{ pokes: [...now.registers[k].pokes, p] },
				{
					panels: { ...now.panels, poke: { source: now.source, mock: false, note } }
				}
			);
		} catch (e) {
			liveError = message(e);
		} finally {
			working = null;
		}
	}

	async function liveAblate() {
		const f = llm;
		if (!f || working) return;
		const k = reg;
		working = 'ablate';
		liveError = null;
		try {
			const a = await live.ablate(f, f.registers[k].name);
			const now = (files.get(f.id) as LlmTrace | undefined) ?? f;
			patch(
				now,
				k,
				{ ablation: a },
				{
					panels: { ...now.panels, ablation: { source: 'promptbox', mock: false, note: 'live' } }
				}
			);
			ablated = true;
		} catch (e) {
			liveError = message(e);
		} finally {
			working = null;
		}
	}

	async function liveBase(id: string) {
		const f = files.get(id);
		if (!f || !isLlm(f) || working) return;
		working = 'base';
		liveError = null;
		try {
			const b = await live.base(f.prompt);
			const now = (files.get(id) as LlmTrace | undefined) ?? f;
			patch(
				now,
				null,
				{},
				{
					...b,
					panels: { ...now.panels, base_answer: { source: 'promptbox', mock: false, note: 'live' } }
				}
			);
		} catch (e) {
			liveError = message(e);
		} finally {
			working = null;
		}
	}

	/** The answer shows once the run has been seen to its end, by replay or by scrubbing. */
	function reached() {
		if (active !== null && count && step >= count - 1) done.add(active);
	}

	let raf = 0;
	function pause() {
		playing = false;
		cancelAnimationFrame(raf);
	}
	/** Replays from the playhead to the end in four to nine seconds, whatever the run's length. */
	function play() {
		if (!count || liveFile) return;
		cancelAnimationFrame(raf);
		if (step >= count - 1) step = 0;
		playing = true;
		const n = count;
		const ms = Math.min(9000, Math.max(4000, n * 8));
		let at = step;
		let last = performance.now();
		const tick = (now: number) => {
			at += ((now - last) / ms) * n;
			last = now;
			if (at >= n - 1) {
				step = n - 1;
				playing = false;
				reached();
				return;
			}
			step = Math.floor(at);
			raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
	}

	function show(id: string, replay: boolean) {
		pause();
		if (shownId !== id) reg = 0;
		shownId = id;
		step = 0;
		ablated = false;
		liveError = null;
		if (replay) play();
	}

	let nextKey = 0;
	function send() {
		const text = draft.trim();
		if (!text) return;
		const exact = entries.find((e) => e.prompt.trim() === text) ?? null;
		const suggested = exactPrompt(prompts, text);
		const addition = pickedAddition?.question.trim() === text ? pickedAddition : null;
		const frozenCore = !!exact && exact.group !== 'llm';
		// Savant-4B in this browser runs everything but the frozen-core recordings, which it cannot run
		if (!frozenCore && savant.status === 'ready') return browserSend(text, suggested, addition);
		if (server && !frozenCore) return liveSend(text);
		if (!frozenCore && savant.status === 'loading' && !exact)
			return browserSend(text, suggested, addition);
		const entry = exact ?? picked;
		if (addition) additions.set(nextKey, addition);
		pickedAddition = null;
		const turn: Turn = {
			key: nextKey++,
			text,
			entry,
			edited: !exact && !!picked,
			prompt: suggested?.id ?? null,
			needsModel: !entry
		};
		turns = [...turns, turn];
		draft = '';
		picked = null;
		pickedPrompt = null;
		if (!entry) return;
		active = turn.key;
		pause();
		load(entry).then((t) => {
			if (t && active === turn.key) show(entry.id, true);
		});
	}

	/** A question for Savant-4B: a new turn, run now or as soon as the model has loaded. */
	function browserSend(
		text: string,
		suggested: SuggestedPrompt | null,
		addition: Addition | null = null
	) {
		const key = nextKey++;
		if (addition) additions.set(key, addition);
		pickedAddition = null;
		turns = [
			...turns,
			{
				key,
				text,
				entry: null,
				edited: false,
				browser: `savant-${key}`,
				prompt: suggested?.id ?? null
			}
		];
		draft = '';
		picked = null;
		pickedPrompt = null;
		startBrowser(key);
	}

	let attempt = 0;
	function startBrowser(key: number) {
		const turn = turns.find((t) => t.key === key);
		if (!turn) return;
		const suggested = prompts?.prompts.find((p) => p.id === turn.prompt) ?? null;
		const addition = additions.get(key) ?? null;
		const id = `savant-${key}-${++attempt}`;
		turn.browser = id;
		turn.needsModel = false;
		const opts = {
			title: suggested?.title ?? addition?.title,
			family: suggested?.family ?? (addition ? 'addition' : null),
			model: savant.loaded?.model ?? {
				name: SAVANT.name,
				compile_adapter: SAVANT.adapter,
				executor_adapter: SAVANT.adapter,
				adapter_sha256: { compile: '', executor: '' },
				tokenizer_sha256: '',
				promptbox_commit: '',
				about: SAVANT.about
			},
			host: savant.loaded?.host ?? { gpu: null, cpu: null, avx512f: null }
		};
		let run = startRun(id, turn.text, opts);
		runs.set(key, run);
		active = key;
		follow = true;
		reg = 0;
		pause();
		if (savant.status !== 'ready') {
			turn.waiting = true;
			return;
		}
		turn.waiting = false;
		let asked: ReturnType<typeof savant.ask>;
		try {
			asked = savant.ask(
				turn.text,
				{
					id,
					title: suggested?.title ?? addition?.title,
					family: suggested?.family ?? (addition ? 'addition' : null),
					truth: suggested?.truth ?? null,
					lookupAfter: fast ? LOOKUP_AFTER : null,
					...(addition ? { addition: { a: addition.a, b: addition.b } } : {}),
					...(MULTI_CALL ? { multiCall: true } : {})
				},
				(ev) => {
					run = applyEvent(run, ev);
					runs.set(key, run);
				}
			);
		} catch (e) {
			runs.set(key, { ...run, stage: 'error', error: message(e) });
			return;
		}
		rids.set(key, asked.rid);
		asked.done
			.then(async (trace) => {
				const out = await withRecorded(trace, suggested);
				files.set(id, out);
				runs.set(key, { ...run, stage: 'done', trace: out });
				const ticks = out.registers.reduce((a, r) => a + r.ticks.real, 0);
				const secs = out.registers.reduce((a, r) => a + r.ticks.seconds, 0);
				if (ticks > 20) msPerTick = (1000 * secs) / ticks;
				done.add(key);
				if (active === key) {
					const keep = reg;
					shownId = id;
					reg = Math.min(keep, Math.max(0, out.registers.length - 1));
					step = Math.max(0, (out.registers[reg]?.steps.length ?? 1) - 1);
					ablated = false;
					liveError = null;
				}
			})
			.catch((e) => {
				runs.set(key, {
					...run,
					stage: e instanceof Stopped ? 'stopped' : 'error',
					error: message(e)
				});
			})
			.finally(() => rids.delete(key));
	}

	/**
	 * A suggested question DEMOLIVE recorded on the server keeps its recorded base-model answer and adapter-off run
	 * (the browser has no base weights), labelled as recorded.
	 */
	async function withRecorded(t: LlmTrace, suggested: SuggestedPrompt | null): Promise<LlmTrace> {
		const entry = suggested?.recorded ? entries.find((e) => e.id === suggested.recorded) : null;
		if (!entry) return t;
		const rec = await load(entry);
		if (!rec || !isLlm(rec)) return t;
		const registers = t.registers.map((r, k) => {
			const want = rec.registers[k];
			return want && want.name === r.name && want.ablation
				? { ...r, ablation: { ...want.ablation, live: false } }
				: r;
		});
		const recorded = { source: 'promptbox', mock: false };
		return {
			...t,
			registers,
			base_answer: rec.base_answer,
			base_answer_meta: rec.base_answer_meta ? { ...rec.base_answer_meta, live: false } : null,
			panels: {
				...t.panels,
				base_answer: rec.base_answer_meta
					? { ...recorded, note: 'recorded on the server: Qwen3-4B, no adapter' }
					: t.panels.base_answer,
				ablation: registers.some((r) => r.ablation)
					? { ...recorded, note: 'recorded on the server: the executor adapter off' }
					: t.panels.ablation
			}
		};
	}

	/** Questions sent while the model was loading (or that asked for it) run once it is ready and free. */
	function runWaiting() {
		if (savant.status !== 'ready' || savant.busy) return;
		const last = turns.at(-1);
		const waiting = turns.findLast((t) => t.waiting || (t.needsModel && t.key === last?.key));
		if (waiting) startBrowser(waiting.key);
	}

	function stop(key: number) {
		const rid = rids.get(key);
		if (rid !== undefined) savant.cancel(rid);
		const run = runs.get(key);
		if (run && run.stage === 'queued') runs.set(key, { ...run, stage: 'stopped' });
		const turn = turns.find((t) => t.key === key);
		if (turn) turn.waiting = false;
	}

	function retry(key: number) {
		if (savant.status === 'ready' && !savant.busy) startBrowser(key);
	}

	/** Runs a question on the live model, following the server's stream in the chat. */
	async function liveSend(text: string) {
		const key = nextKey++;
		const progress: LiveTurn = {
			stage: 'connecting',
			register: null,
			done: 0,
			total: 0,
			detail: '',
			error: null,
			id: null,
			started: Date.now()
		};
		turns = [...turns, { key, text, entry: null, edited: false, live: progress }];
		draft = '';
		picked = null;
		pickedPrompt = null;
		active = key;
		pause();
		const s = turns[turns.length - 1].live!;
		try {
			for await (const ev of live.ask(text)) {
				if (ev.type === 'stage') {
					s.stage = ev.stage as LiveTurn['stage'];
					s.register = ev.register ?? null;
					s.done = 0;
					s.total = ev.total ?? ev.rows ?? 0;
				} else if (ev.type === 'program') {
					s.detail = ev.exec
						? `wrote a ${int(ev.tokens)}-token program in ${ev.seconds.toFixed(1)} s`
						: 'answered without writing a program';
				} else if (ev.type === 'tape') {
					s.detail = `read ${int(ev.events)} events from the question`;
				} else if (ev.type === 'certificate') {
					s.detail = `register ${ev.register}: ${ev.rows - ev.rows_wrong} of ${ev.rows} rows certified`;
				} else if (ev.type === 'progress') {
					s.done = ev.done;
					s.total = ev.total;
				} else if (ev.type === 'error') {
					s.stage = 'error';
					s.error = ev.error;
				} else if (ev.type === 'trace') {
					const id = `live-${key}`;
					files.set(id, { ...ev.trace, id, where: 'server' });
					s.id = id;
					s.stage = 'done';
					if (active === key) show(id, true);
				}
			}
			if (s.stage !== 'done' && s.stage !== 'error') {
				s.stage = 'error';
				s.error = 'the server closed the stream before the run finished';
			}
		} catch (e) {
			s.stage = 'error';
			s.error = message(e);
		}
	}

	function replay(key: number) {
		const turn = turns.find((t) => t.key === key);
		const id =
			turn?.live?.id ??
			(turn?.browser && runs.get(key)?.trace ? turn.browser : null) ??
			turn?.entry?.id;
		active = key;
		if (!id) return;
		show(id, true);
	}

	function seek(i: number) {
		pause();
		if (liveFile) follow = false;
		step = Math.max(0, Math.min(count - 1, i));
		reached();
	}

	onMount(() => {
		const controller = new AbortController();
		fetch(asset('traces/index.json'), { signal: controller.signal })
			.then((r) => {
				if (!r.ok) throw new Error('Trace index unavailable');
				return r.json();
			})
			.then((index: { traces: TraceEntry[] }) => {
				entries = index.traces;
				const first = entries[0];
				if (first)
					load(first).then((t) => {
						if (t && shownId === null && active === null) show(first.id, false);
					});
			})
			.catch((error) => {
				if (error.name !== 'AbortError') loadError = true;
			});
		fetch(asset('interpreter/prompts.json'), { signal: controller.signal })
			.then((r) => (r.ok ? (r.json() as Promise<PromptSet>) : null))
			.then((p) => (prompts = p))
			.catch(() => {});
		// the local server's live model (dev only) comes and goes; recheck now and then
		let stopped = false;
		const check = async () => {
			const h = await live.health();
			if (stopped) return;
			server = h;
			connection.live = !!h;
		};
		check();
		const timer = setInterval(check, 20_000);
		const unready = savant.onReady(runWaiting);
		// for checking runs from the console and the browser tests in development
		if (import.meta.env.DEV)
			(globalThis as { __interp?: unknown }).__interp = { files, runs, savant };
		return () => {
			stopped = true;
			unready();
			connection.live = false;
			clearInterval(timer);
			controller.abort();
			cancelAnimationFrame(raf);
		};
	});

	const inBrowser = $derived(llm?.where === 'browser');
	const sub = $derived(
		going
			? going.stage === 'certify'
				? `Certifying in this browser: row ${int((going.at?.rows ?? 0) + 1)} of ${int(trace?.program.rows.length ?? 0)}`
				: going.stage === 'answer'
					? 'Writing the answer in this browser'
					: `Running in this browser: ${trace?.program.mealy ? 'column' : 'tick'} ${int(count)} of ${int(going.tape?.events.length ?? 0)}`
			: preview
				? llm
					? 'Preview of a run recorded from the live model: send a question to replay it'
					: 'Preview: send a question to replay its run'
				: inBrowser
					? playing
						? 'Replaying the run from this browser'
						: 'Run in this browser'
					: llm?.live
						? playing
							? 'Replaying the live run'
							: 'Live run, paused'
						: playing
							? 'Replaying the recorded run'
							: 'Recorded run, paused'
	);
</script>

<svelte:head>
	<title>Interpreter · Polyformer</title>
	<meta
		name="description"
		content="A language model writes a program for a question and runs it inside itself, one certified tick per event, in your browser: the program, the run, the digital state, the certificate, and interventions."
	/>
</svelte:head>

<div class="page">
	<aside class="left" aria-label="Chat">
		<Chat
			{entries}
			{prompts}
			{turns}
			{active}
			{done}
			step={shownStep}
			{server}
			{working}
			{msPerTick}
			bind:draft
			bind:fast
			bind:picked
			bind:pickedPrompt
			bind:pickedAddition
			traceFor={(id) => {
				const f = files.get(id);
				return f ? (asTrace(f) ?? undefined) : undefined;
			}}
			fileFor={(id) => {
				const f = files.get(id);
				return f && isLlm(f) ? f : undefined;
			}}
			runFor={(key) => runs.get(key)}
			onsend={send}
			onreplay={replay}
			onbase={liveBase}
			onstop={stop}
			onretry={retry}
		/>
		{#if loadError}
			<p class="error">The recorded runs could not be loaded.</p>
		{/if}
	</aside>

	<main class="right" aria-label="Inside the model">
		{#if writing && going}
			<LiveProgram run={going} />
		{:else if trace && cur}
			<div class="bar">
				<div class="what">
					<span class="title">{trace.title}</span>
					<span class="sub">{sub}</span>
					{#if llm && llm.registers.length > 1}
						<span class="regs-pick" role="group" aria-label="Register">
							<span class="k">register</span>
							{#each llm.registers as r, k (r.name)}
								<button
									aria-pressed={k === shownReg}
									onclick={() => {
										reg = k;
										follow = false;
										ablated = false;
									}}>{r.name}</button
								>
							{/each}
						</span>
					{/if}
				</div>
				{#if going && certifying}
					<StageLine run={going} />
				{:else}
					<div class="scrub-wrap">
						<Scrubber
							step={shownStep}
							{playing}
							{count}
							unit={unitOf(trace.title)}
							event={stuck !== null ? (llm ? 'adapter off' : 'head off') : cur.event}
							onseek={seek}
							ontoggle={() => (playing ? pause() : play())}
						/>
						{#if going && !follow}
							<button class="follow" onclick={() => (follow = true)}>Follow the run</button>
						{/if}
					</div>
				{/if}
			</div>
			{#key trace.id}
				<div class={['grid', trace.kind === 'regs' && 'regs']}>
					<div class="a-program"><ProgramPanel {trace} {cur} {stuck} /></div>
					<div class="a-run">
						<RunPanel {trace} {cur} {stuck} onseek={seek} pending={certifying} />
					</div>
					<div class="a-state">
						<StatePanel {trace} {cur} {stuck} fast={playing || !!going} onseek={seek} />
					</div>
					<div class="a-cert">
						<CertificatePanel {trace} {cur} {stuck} pending={certifying} />
					</div>
					<div class="a-poke">
						<PokePanel
							{trace}
							step={shownStep}
							bind:ablated
							onseek={seek}
							live={!!pokeWhere}
							where={pokeWhere ?? (inBrowser ? 'browser' : 'server')}
							ablateLive={pokeWhere === 'server'}
							pending={!!going}
							{working}
							error={liveError}
							onpoke={livePoke}
							onablate={liveAblate}
						/>
					</div>
				</div>
			{/key}
			{#if llm && llm.where === 'browser'}
				<footer class="prov num">
					{llm.model.name}: {SAVANT.base} with {adapterName(SAVANT.adapter)} merged · {llm.host
						.dtype ?? SAVANT.dtype} · run in this browser on {llm.host.gpu ?? 'this GPU'} · {llm
						.host.runtime ?? 'transformers.js'} · PROMPTBOX {llm.model.promptbox_commit.slice(
						0,
						8
					)}{#if llm.timing?.total}
						· {llm.timing.total.toFixed(1)} s{/if}
				</footer>
			{:else if llm}
				<footer class="prov num">
					{llm.model.name} · compile {adapterName(llm.model.compile_adapter)} · executor
					{adapterName(llm.model.executor_adapter)} · {llm.live ? 'run live' : 'recorded'} on
					{llm.host.gpu ?? 'an unknown GPU'}, {cpuName(llm.host)}{llm.host.avx512f
						? ' (avx512f)'
						: ''} · torch {llm.host.torch} · PROMPTBOX {llm.model.promptbox_commit.slice(
						0,
						8
					)}{#if llm.provenance}
						· recorded {llm.provenance.recorded_at.slice(0, 10)} at {llm.provenance.demolive_commit.slice(
							0,
							8
						)}{/if}{#if llm.cost}
						· {llm.cost.container_seconds.toFixed(0)} s of GPU time, about ${llm.cost.usd.toFixed(
							3
						)}{/if}
				</footer>
			{:else}
				<footer class="prov num">
					{trace.model.name} · {trace.model.heads} head · params {trace.model.params_sha256_16} · run
					on
					{trace.host.cpu}, {trace.host.gpu} · jax {trace.host.jax}
				</footer>
			{/if}
		{:else if llm}
			<NoRunPanel file={llm} />
		{:else if going}
			<LiveProgram run={going} />
		{:else}
			<p class="waiting">{loadError ? 'No recorded runs found.' : 'Loading the recorded runs…'}</p>
		{/if}
	</main>
</div>

<style>
	.page {
		display: grid;
		grid-template-columns: minmax(340px, 400px) minmax(0, 1fr);
		height: calc(100dvh - var(--bar-h));
		min-height: 560px;
		border-top: 1px solid #1c1c1c;
	}
	.left {
		min-height: 0;
		border-right: 1px solid #222;
		display: flex;
		flex-direction: column;
	}
	.left > :global(:first-child) {
		flex: 1;
		min-height: 0;
	}
	.error {
		padding: 0 22px 12px;
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
	}
	.right {
		min-width: 0;
		min-height: 0;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
	}
	.bar {
		position: sticky;
		top: 0;
		z-index: 5;
		display: grid;
		grid-template-columns: minmax(0, auto) minmax(260px, 1fr);
		align-items: center;
		gap: 24px;
		padding: 9px 16px;
		background: var(--color-void);
		border-bottom: 1px solid #222;
	}
	.what {
		display: grid;
		min-width: 0;
	}
	.title {
		font-size: var(--text-sm);
		font-weight: 500;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.sub {
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
	}
	.scrub-wrap {
		display: flex;
		align-items: center;
		gap: 12px;
		min-width: 0;
	}
	.scrub-wrap > :global(:first-child) {
		flex: 1;
	}
	.follow {
		flex: none;
		border: 1px solid var(--color-edge);
		border-radius: 4px;
		padding: 3px 8px;
		background: transparent;
		color: var(--color-ink-2);
		font: inherit;
		font-size: var(--text-2xs);
		cursor: pointer;
	}
	.follow:hover {
		color: var(--color-ink);
		border-color: var(--color-rule);
	}
	.regs-pick {
		display: flex;
		align-items: baseline;
		gap: 10px;
		font-size: var(--text-2xs);
	}
	.regs-pick .k {
		color: var(--color-ink-3);
	}
	.regs-pick button {
		border: 0;
		background: transparent;
		padding: 2px 0;
		font-family: var(--font-mono);
		font-size: var(--text-2xs);
		color: var(--color-ink-3);
		cursor: pointer;
	}
	.regs-pick button:hover,
	.regs-pick button[aria-pressed='true'] {
		color: var(--color-ink);
	}
	.regs-pick button[aria-pressed='true'] {
		text-decoration: underline;
		text-underline-offset: 4px;
	}
	.grid {
		flex: 1;
		display: grid;
		grid-template-columns: repeat(12, minmax(0, 1fr));
		grid-template-rows: minmax(0, 1fr) minmax(0, 1fr);
		min-height: 690px;
	}
	.grid > div {
		min-width: 0;
		min-height: 0;
		overflow: hidden;
		display: flex;
		flex-direction: column;
		border-bottom: 1px solid #222;
	}
	.grid > div > :global(*) {
		flex: 1;
	}
	.a-program {
		grid-column: 1 / 8;
	}
	.a-run {
		grid-column: 8 / 13;
		border-left: 1px solid #222;
	}
	.regs .a-program {
		grid-column: 1 / 5;
	}
	.regs .a-run {
		grid-column: 5 / 13;
	}
	.a-state {
		grid-column: 1 / 5;
	}
	.a-cert {
		grid-column: 5 / 9;
		border-left: 1px solid #222;
	}
	.a-poke {
		grid-column: 9 / 13;
		border-left: 1px solid #222;
	}
	.prov {
		padding: 8px 16px 10px;
		font-size: 10px;
		color: var(--color-ink-3);
	}
	.waiting {
		margin: auto;
		font-size: var(--text-xs);
		color: var(--color-ink-3);
	}
	@media (max-width: 1180px) {
		.grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
			grid-template-rows: auto;
			min-height: 0;
		}
		.grid > div {
			overflow: visible;
		}
		.grid .a-program {
			grid-column: 1 / 3;
		}
		.grid .a-run,
		.grid .a-state,
		.grid .a-cert,
		.grid .a-poke {
			grid-column: auto;
		}
		.a-run {
			border-left: 0;
		}
		.a-state {
			border-left: 1px solid #222;
		}
		.a-cert {
			border-left: 0;
		}
	}
	@media (max-width: 860px) {
		.page {
			display: block;
			height: auto;
			min-height: 0;
		}
		.left {
			border-right: 0;
			border-bottom: 1px solid #222;
			max-height: none;
		}
		.right {
			overflow: visible;
		}
		.bar {
			top: var(--bar-h);
			grid-template-columns: 1fr;
			gap: 6px;
			padding: 8px 14px;
		}
		.grid {
			display: block;
		}
		.grid > div {
			border-left: 0;
		}
	}
</style>
