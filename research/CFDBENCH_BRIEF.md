# Long, stable rollouts of a learned fluid simulator on CFDBench (lid-driven cavity)

## What we did

CFDBench (Luo et al.) is a public benchmark for machine-learned fluid simulators. In its lid-driven cavity task, a
network learns to advance a 64×64 velocity field by one time step. It is then judged on one-step accuracy and on
autoregressive rollouts, where the simulator is fed its own output step after step.

- **Reproduction.** We ported the benchmark's code, data splits, metric (normalised mean squared error, NMSE) and
  training schedule line by line. We checked the data against the paper's published numbers to every printed digit.
- **One-step baseline.** We reproduced the benchmark's U-Net. On the subset the paper's figures use, it matches the
  published one-step record: 2.80×10⁻⁴ on the horizontal velocity, against 2.815×10⁻⁴ published.
- **Comparison.** We trained our own method and compared it with the U-Net and with standard rollout stabilisers
  (training-noise injection, the pushforward trick, and a randomly directed variant of our method), under identical
  protocols.
- **Scale and evaluation.** 80 training runs, 5 seeds per arm, on two test subsets, with predictions written down
  before each run. We evaluated rollouts out to 200 steps, 200 times the one-step horizon the models are trained on.

## What we found

- **At long horizons, ours is the only method that stays stable.** At 200 steps it is the only method with no seed
  exploding. In every other arm, several seeds end with an error larger than the flow field itself.
- **Paired comparisons at 200 steps** (per test case and seed):

| Ours against | All cases | Fluid-property subset |
|---|---|---|
| the benchmark's U-Net | better on 78 of 80 | better on 45 of 45 |
| noise injection | better on 80 of 80 | better on 45 of 45 |
| the randomly directed variant | better on 66 of 80 | better on 34 of 45 |

- **What that error means.** Our 200-step error (NMSE 0.08–0.10 on average) stays below the trivial "hold the first
  frame" predictor on 9 of 10 seeds. The other methods reach errors from about 1 to over a million.
- **The cost.** Ours is somewhat less accurate over the first few steps. At 20 steps the plain U-Net is better on most
  paired comparisons. It does not beat the one-step record.
- **The published 20-step rollout record.** Retrained from the benchmark's own published code, the plain U-Net scores
  0.013 at 20 steps on the subset the figure appears to use. That is 3.6 times below the published record (0.0478), and
  76 times below the U-Net curve shown in the paper's own figure. That record is therefore not a reliable bar. We have
  drafted a question to the authors about which subset and model the figure used.

## Round 2: the other three flows (did not hold up)

We applied the same protocol, with predictions registered in advance, to the benchmark's other three flows: flow in a
tube, a dam break, and flow past a cylinder. The cavity result does not carry over as registered:

| At 200 steps | Tube | Dam | Cylinder |
|---|---|---|---|
| Our seeds staying below "hold the first frame" (registered bar: 5 of 5) | 1 of 5 | 4 of 5 | 4 of 5 |
| Paired cases where ours beats noise injection (registered bar: 70%) | 62% | 60% | 66% |
| Paired cases where ours beats the randomly directed variant | 54% | 66% | 94% |

- **What still holds.** On every flow, the arms using our method's core term keep the most seeds stable at 200 steps.
- **What is weak.** No method is reliable on the tube. The cylinder data contain only nine steps of ground truth, and
  we trained on a tenth of it to save cost. A full-data run would cost about $150.
- **A protocol finding.** The benchmark's published training code leaves BatchNorm in evaluation mode. Under that
  setting, a stripped-down version of our method collapsed on 4 of 5 cavity seeds. With BatchNorm trained normally, none
  of the 20 seeds using the core term collapses, and the full method is stable on 4 of 5 and 5 of 5 seeds on the two
  cavity subsets. It beats noise injection on 94–98% of paired cases at 200 steps, and most of its short-horizon cost
  disappears. This analysis is labelled as secondary because it departs from the published
  protocol.

So the defensible claim is a long-horizon win on the cavity, the benchmark's flagship task, not on the whole benchmark.
