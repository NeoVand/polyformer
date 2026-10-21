# LOOPS review: what the result means, and where the breakthrough is

21 October 2026. A response to [LOOPS_REPORT.md](LOOPS_REPORT.md) and [LOOPS.md](LOOPS.md), after
reading both, the frame implementation (`loops_layers.py`) and the earlier studies. Section 2 answers
the four questions in the report; section 3 is the recommendation.

## 0. Verdict

The study is well run and its negative half is more valuable than its positive half. The positive
half: a two-memory model (Gated DeltaNet alternating with forgetting attention in content-driven
frames) is the best of nine arms on every seed, 0.9% below RoPE softmax at equal modeled FLOPs,
1.8% below softmax with learned positions, and, counting the short convolution from BEYOND, about
3% below a plain transformer. That is a real, reproducible result and it already beats the ordinary
transformer. It is not a breakthrough, and the report says why: the gain decomposes into published
parts, the margin does not grow with size, and the one new mechanism is used by the model without
moving the loss.

The negative half is the finding. Everything that lowered the loss is a **reset or a recency
device** (short convolution, relative positions, a forget gate, a compressed recent-state memory
beside exact recall), and the model, left to itself, built an event-segmented, multi-timescale
memory out of those devices. Everything that tracks **order** (non-commuting frames, value
transport) was learned, is used, and is worth nothing on 512-token web text. That is not a failure
of the mechanism; it is a measurement of the data. The breakthrough, if there is one here, is to
take the model at its word: make events, not tokens, the unit of memory and compute, and move the
order-tracking to the regime and the data where order is dense. Section 3 spells that out, with the
arithmetic that says why it can pay at equal compute and why it cannot at context 512.

## What to do, in order

1. **Stop chasing the last tenth of a percent at context 512, and retire the 1% gate.** The
   current model already beats the plain transformer by about 3% and a strong RoPE baseline by
   0.9%. At 512 tokens attention is about 7% of a layer's compute (table in 3.2), so no change to
   attention can win much there, and 1% at one size and one context is a number nobody else uses.
2. **Spend one cheap day making the current result honest and a little stronger** (section 4):
   a softmax baseline with equal parameters and wall-clock times beside the FLOP counts; gated
   attention output and value residuals, two free published parts that will probably carry the
   model past 1% on their own; value transport in one head only, so state tracking is kept at
   almost no cost on text; an inference ablation that switches the learned frames off to see which
   tokens, if any, get worse; and the correction to Part VIII of the paper (1.4).
3. **Change the regime: make events, not tokens, the unit of memory** (section 3). The trained
   model split text into sentences and clauses and forgot at the boundaries on its own. Build that
   in as computation: the recurrent layer runs within an event and resets at its boundary,
   attention runs over one summary vector per event, and the order-tracking frames are carried over
   the sequence of events. At 8k context this removes most of the attention cost and the saved
   compute buys a bigger or longer-trained model, which is a reason for the margin to grow with
   context and scale. H-Net has shown learned chunking beats a transformer at equal compute.
4. **Measure the new model where order is dense**: train the same arms on code, and evaluate
   entity tracking and long-range recall directly (Q3 in section 2) rather than through average
   loss. On web prose the order-tracking machinery will stay silent; that is a fact about prose.
5. **Register the claim as a slope, not a number**: two sizes, two context lengths, three seeds at
   the headline cell, with the sign and minimum size of the margin's growth written down first
   (3.5). "The gap widens as context and scale grow" is the claim nobody else has.

In one sentence: the token-level model told you text is made of events, so build the event-level
model, test it at long context and on code, and claim a slope.

## 1. What the data say

**1.1 The decomposition is a locality story.** Rank the effects at 443M tokens: hybrid 0.80%,
forget gate 0.25%, RoPE over learned positions 0.94%, frames plus gate inside the hybrid 0.10%,
value transport −0.4%, content clocks alone −0.3%. Each positive term improves how the model weights
the recent segment: RoPE's inner product decays with distance; the forget gate learns where the
segment ends; the Gated DeltaNet layer is a compressed memory of the recent past with its own decay.
Each negative term weakens recency: content clocks that slow down on sub-word pieces make far tokens
look near (which is why grid alone loses to RoPE and grid+forget does not), and value transport
rotates 16 of 64 value dimensions by the holonomy between key and query, which is noise for a copy.
The model wants locality, segmentation and a hierarchy of timescales, and the probes show it built
exactly that.

**1.2 Why the group atom does nothing on text: natural language is mostly aperiodic.** In
Krohn–Rhodes terms a sequential computation is a cascade of reset automata and group automata. The
reset-only cascades are the star-free (aperiodic) languages; masked hard-attention transformers
recognise exactly the star-free languages (Yang, Chiang and Angluin, 2024), and the 2026 "Rational
Transductors" paper draws the same line: attention covers the aperiodic part, a matrix recurrence
adds the group part. What next-token prediction on web text rewards is almost entirely aperiodic
structure: segment boundaries, recency, counting a few things, binding a few entities. The group
part (permutation-like state that must be composed in order over long spans) is rare in prose, and
the dilution study already measured how rare: decision tokens were 0.5–1.7% of tokens. So the
forget gate and the clocks (reset and counter atoms) pay; the holonomy blocks (group atom) do not,
and no amount of tuning on this data will change that. The group atom pays where order-sensitive
state is dense: code (scopes, variable binding, bracket depth), symbolic traces, long structured
documents, and the synthetic word problems where it already wins. Kim and Schuster (2023) found
that only code-pretrained models track entity state, and a 2024 follow-up showed code training
causes it; that is the same fact seen from the data side.

**1.3 Why the margin does not grow.** Resets and recency are learned early and cheaply by any
architecture; a bigger model with more tokens finds them anyway, so an inductive bias toward them
yields a constant offset, not a slope. The project saw this before (Newton attention's transfer
result, the holonomy curriculum effect): building in structure the model can find buys learning
speed, not asymptotic loss. The scale check (0.86% at three times the parameters, 0.97% at base)
is consistent with a fixed offset, and the proposed "event clock built in" step will, on this
reading, buy the same thing: faster early learning, the same loss at the end.

**1.4 The BEYOND correction matters for the paper.** Under one protocol, Gated DeltaNet is 0.07%
better than RoPE softmax and DeltaProduct 0.30%; the "recurrent networks beat softmax by about 1%"
of BEYOND and of the paper's Part VIII was the baseline's learned absolute positions. The paper's
language table needs a RoPE row and the sentence about recurrence winning on language needs to be
rewritten as: recurrence wins by 0.1–0.3% over a RoPE baseline, and a hybrid of the two wins by
0.8–0.9%.

**1.5 The loop arm says what the literature says.** At equal compute a looped block loses to
untied blocks (−0.54%) and beats the same blocks unlooped (+0.89%). Loops are a parameter-efficiency
and reasoning lever, and their practical case is decoding (fewer weights to stream per token), not
training FLOPs. Nothing further is needed here unless the goal changes to inference cost.

## 2. The four questions

**Q1. Equal modeled FLOPs, wall time, or parameters?** Equal modeled FLOPs is the right comparison
for the mechanism claim and should stay. Two more rows are needed before any claim leaves the lab:
equal parameters (widen the softmax baseline's MLP by about 10% so it matches the candidate's
20.9M) and equal wall clock on implementations that have had the same engineering effort. The wall
clock gap (candidate 1,817 s against RoPE 1,180 s) is a kernel problem, not a science problem, but
at equal wall clock the candidate has two thirds of the updates and the 0.9% is gone. Note that the
comparison reverses at long context: the hybrid has half the attention layers, so its wall clock
advantage grows with context length, which is one more reason context 512 is the wrong regime
(section 3).

**Q2. Build the clock in, or measure the exponent?** Neither as proposed. Building the discovered
gates in buys learning speed (1.3), and the exponent of the current candidate has one data point
already saying "flat". The money should go to the regime change in section 3, which has a mechanism
for a slope, with the exponent measured on *that* candidate at two sizes and two context lengths.

**Q3. A probe for whether the frames matter.** Five, cheapest first.
1. *Inference ablation.* Set the quaternion moves to identity (the blocks become RoPE) in the
   trained candidate and measure loss per token. If the change is within noise everywhere, the
   frames are redundant with other paths and their large commutators are decoration; if it
   concentrates on identifiable tokens, those tokens are the probe.
2. *Loss on long-range-dependent tokens.* Bucket held-out tokens by whether the same token last
   occurred more than 128, 256, 384 positions back, and by position in the window. Report every
   arm's loss per bucket. This is the cheapest way to see which arm uses distance and order; it
   costs nothing but a pass over saved per-token losses.
3. *Entity-tracking evaluation on the trained models.* Kim and Schuster's task (initial state plus a
   sequence of operations; report the final state), RULER's variable-tracking subtask, and the
   project's own swap programs and ownership narratives rendered as text. Score answer tokens only,
   as the dilution study did. A 20M model will be weak on all of them, so compare arms, not absolute
   numbers.
4. *Code.* Train the same arms on a Python corpus at the same budget. If 1.2 is right, the frames
   and value transport move from neutral to positive on code and the ordering between arms changes.
   This is the one probe that can turn the frame result into a language result.
5. *One transport head.* Transport values in one of eight heads only. Prediction: A5 tracking
   survives (one head suffices in the synthetic check) and the 0.4% text cost drops below 0.1%,
   because seven heads keep clean values for copying.

**Q4. Keep the 1% gate?** Drop it as the headline. With per-arm seed spreads of 0.001–0.004 nats, a
0.03-nat gap is many standard deviations; significance was never the issue, and a paired test on
per-sequence losses with a registered effect size is still worth doing because it is standard and
cheap. What the field believes is a slope: register the sign and minimum size of the margin's change
across two sizes and across two context lengths, and the equal-parameter and equal-wall-clock rows.
A fixed 1% at one size and one context is a number nobody else uses.

## 3. The insight to pursue: events are the unit

**3.1 What the model said.** Forget gates reset at sentence and line boundaries; half-lives grow
from tens of tokens in early layers to thousands in late ones; the clocks tick on sentence ends,
clause words and verbs and stop on sub-word pieces. This is event segmentation (Baldassano et al.,
2017, for the hippocampus) and the cortical hierarchy of temporal receptive windows (Hasson et al.,
2008), discovered from next-token loss. The study treated it as a finding about gates. It is a
finding about the right *unit of memory*: the model is trying to store and retrieve events, and it
is doing so with token-level machinery.

**3.2 The arithmetic that says where it pays.** Per token, with width d and context n, a layer
costs roughly 8d² for the attention projections, 16d² for the MLP, and about 2nd for the attention
scores and averaging (causal). At d = 512:

| context | attention scores as share of layer FLOPs |
|---|---|
| 512 | about 7% |
| 2,048 | about 25% |
| 8,192 | about 57% |
| 32,768 | about 84% |

At context 512 there is nothing to save, which is why every equal-FLOP comparison in this project
has been a fight over tenths of a percent. If attention ran over events instead of tokens, with
e = n/ℓ events of mean length ℓ (the probes suggest ℓ of 10–40 for the fast gates), the score cost
drops by ℓ², and at 8k context roughly half the FLOPs of a transformer become free to spend on
width, depth or tokens. That is a mechanism for a margin that grows with context length and with
scale, which the current candidate lacks. It is also the mechanism behind the one published
hierarchy result that beats the transformer at equal compute: H-Net (Hwang, Wang and Gu, ICLR 2026)
learns chunk boundaries end to end, runs its main network over chunks, matches a BPE transformer at
equal compute with one stage, and with two stages scales better with data and matches a tokenised
transformer of twice its size. Their boundary module discovers what your forget gates discovered.

**3.3 The design: three memories, one boundary signal.**

1. *Within an event*: the fast-weight state (Gated DeltaNet) runs over tokens, with its decay tied
   to the boundary signal so the state is reset, or sharply decayed, at event ends.
2. *Across events*: attention runs over one vector per event, written at the boundary (the state at
   the boundary token, or a learned pooling of the event), with the forgetting gate and the frames
   carried over events rather than tokens. Cost scales with events.
3. *Across episodes*: a slow memory written at larger boundaries (paragraphs, documents), a
   Titans-style or compressive memory; optional at first.

The boundary signal is one learned detector per layer group, initialised from the forget-gate
probes (sentence and line ends), trained with a target compression ratio as H-Net does. Tokens
still receive the event-level output by broadcast or smoothing, as in H-Net's upsampling.

**3.4 Where the frames belong.** Over events, not tokens. A context holds a few hundred events at
most, and the order of events (who did what, then what) is exactly the order-sensitive state that
entity tracking needs. Holonomy over a short sequence of events is cheap, the values of event
summaries are not needed for verbatim copying (so transport does not fight retrieval), and the
synthetic result (one layer tracks A5 with transported values) transfers directly. This resolves the
value-transport paradox: transport the event stream, copy the token stream.

**3.5 Predictions to register.**
- At context 512, the event model is within ±0.2% of the current candidate (no room to win).
- At context 8,192 and equal FLOPs, the event model is at least 1% below the current candidate and
  at least 2% below RoPE+forget softmax, with the margin larger at 8k than at 2k (the slope is the
  claim).
- On long-range buckets (Q3, probe 2) and on entity tracking (probe 3), the event model leads;
  on code, the frames become positive.
- The learned boundaries land on sentence and clause ends without supervision, at a mean event
  length between 10 and 40 tokens.

**3.6 Cost.** The study needs long-context data (FineWeb-Edu documents concatenated to 8k, plus a
code corpus), the H-Net-style chunking module (its code is public), and runs at two context lengths
and two sizes with three seeds at the headline cell: roughly 2–3× the LOOPS budget. The 512-context
rows are not needed beyond one sanity run.

## 4. Cheap things to do before that

These are known parts; they do not change the story, but they close the 1% gate honestly and
strengthen the baseline the real study will be judged against.

- **Gated attention output** (Qiu et al., Qwen, NeurIPS 2025): an element-wise sigmoid gate on the
  attention output, before the output projection. It is another reset atom and it has no cost. On
  the evidence of that paper it is worth more than the frames.
- **Value residual** (Zhou et al., 2024): a residual from the first layer's values into every
  later layer's values; reported as equivalent to about 13–16% fewer parameters at equal loss.
- **One transport head** (Q3, probe 5) instead of none, so the candidate keeps its state-tracking
  claim at near-zero text cost.
- **Equal-parameter baseline** and the **inference ablation** of the frames (Q3, probes 1 and 2),
  both nearly free.
- **Correct the paper** (1.4) now, independent of everything else.

## 5. What goes into the paper from LOOPS

- The result: a two-memory model beats RoPE softmax by 0.9% and the ordinary transformer by about
  3% at equal compute, reproducibly, with the decomposition into resets, recency and the second
  memory. State the wall-clock and parameter caveats in the same paragraph.
- The finding: the model builds an event-segmented, multi-timescale memory from next-token loss
  alone, with the probe figures (half-lives by layer, what the clocks count). This is the paper's
  best new figure and it stands on its own.
- The explanation: text rewards the reset atoms; the group atom is used but unrewarded because
  prose is mostly aperiodic; the group atom wins where order is dense (one-layer A5 with transported
  values). Cite the star-free characterisation of attention and the Krohn–Rhodes split.
- The correction to Part VIII (1.4).
- The next step as a registered design (section 3), not as a wish.
