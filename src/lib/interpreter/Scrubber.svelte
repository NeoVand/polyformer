<script lang="ts">
	/** The playhead every panel follows: step back and forth, play or pause the replay, drag anywhere in the run. */
	import Icon from '#lib/ui/Icon.svelte';
	import { Next, Pause, Play, Previous } from '#lib/ui/icons.ts';
	import { int } from './trace.ts';

	let {
		step,
		count,
		playing,
		unit,
		event,
		onseek,
		ontoggle
	}: {
		step: number;
		count: number;
		playing: boolean;
		unit: string;
		event: string;
		onseek: (i: number) => void;
		ontoggle: () => void;
	} = $props();
</script>

<div class="scrub">
	<div class="buttons">
		<button class="btn icon-only ghost" aria-label="Previous step" onclick={() => onseek(step - 1)}>
			<Icon icon={Previous} size={15} />
		</button>
		<button
			class="btn icon-only"
			aria-label={playing ? 'Pause the replay' : 'Play the replay'}
			onclick={ontoggle}
		>
			<Icon icon={playing ? Pause : Play} size={15} />
		</button>
		<button class="btn icon-only ghost" aria-label="Next step" onclick={() => onseek(step + 1)}>
			<Icon icon={Next} size={15} />
		</button>
	</div>
	<input
		type="range"
		min="0"
		max={count - 1}
		value={step}
		aria-label="Step of the run"
		aria-valuetext="{unit} {step + 1} of {count}"
		oninput={(e) => onseek(+e.currentTarget.value)}
	/>
	<span class="where num"
		><span class="ev">{event}</span>{unit}
		{int(step + 1)}<span class="of">{` of ${int(count)}`}</span></span
	>
</div>

<style>
	.scrub {
		display: flex;
		align-items: center;
		gap: 12px;
		min-width: 0;
	}
	.buttons {
		display: flex;
		gap: 2px;
		flex: none;
	}
	input {
		flex: 1;
		min-width: 60px;
		height: 20px;
		margin: 0;
		cursor: pointer;
	}
	.where {
		flex: none;
		font-size: var(--text-2xs);
		color: var(--color-ink-2);
		min-width: 22ch;
		text-align: right;
		white-space: nowrap;
	}
	.ev {
		display: inline-block;
		vertical-align: bottom;
		font-family: var(--font-mono);
		color: var(--color-ink);
		margin-right: 10px;
		max-width: 12ch;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.of {
		color: var(--color-ink-3);
	}
	@media (max-width: 560px) {
		.of {
			display: none;
		}
		.where {
			min-width: 0;
		}
	}
</style>
