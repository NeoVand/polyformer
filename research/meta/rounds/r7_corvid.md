# R7 · Corvid cache-recovery memory (ethology)

**1. Objects and techniques.**
Objects: nutcracker caches (tens of thousands of seeds, recovered months later); scrub-jay sand trays; the
enlarged hippocampus of food-storing birds.
Techniques: *cue-removal and own-versus-other probes* (Vander Wall 1982: birds dig where seeds were, after removal, and
find their own caches, not a neighbour's); *what-where-when with a decay schedule* (Clayton & Dickinson
1998: jays stop seeking worms once worms would have rotted); *observed-versus-private caching* (Emery & Clayton 2001:
only jays that have stolen re-cache when watched), with *cache-spacing theory* (Stapanian & Smith 1978: spread caches
so a thief who finds one cannot find the rest nearby).

**2. Map to the problem.**
- P1 Who: whoever has a thief problem: anyone installing weights someone else trained.
- P2 What: behaviour on unseen inputs. Output checkers check inputs that occurred; a planted trigger is a cache they
  never dig.
- P3 Where: on device, in the weights. The threat is the model, so no tool stands in.
- P4 Beyond: what-where-when is a state slot with an expiry rule.
- P5 Composition: the gate makes the adapter's footprint enumerable (off: base model bit for bit; on: 2,446 checked
  views), so the uncertified chat is provably untouched.
- P6 Evidence: cue-removal probe becomes planted-trigger probe.
- P7 Trust: ethology trusts a sceptic's controls (Morgan's canon: prefer the simplest mechanism); here a security team
  re-runs the margin table and Lean check on its own hardware.

**3. Map from the problem.** Our theorem (a step that reads earlier steps has no finite certifying test) explains why
the jay episodic-memory debate never closes: a choice that reads unbounded history (time since caching, who watched)
cannot be pinned by a finite probe battery. Only the bounded part (landmarks, then dig) is testable.

**4. Ideas.**
*A. The pilfer-proof adapter.* A backdoor hides like a well-spaced cache in a huge input space; Goldwasser et al. 2022
prove planted backdoors can be undetectable. In Sketchpad the adapter's whole input space is 2,446 views plus the gate,
so the auditor digs every site: each view is margin-checked and the gate-off path is the base model exactly. The product is the certificate "this third-party adapter does its spec and nothing else", which no output
checker gives.
Who: adapter hubs, security teams, AI Act auditors. Breaks: *the product is the computation*; *the venue is an
ML journal* (security). The runtime, not the model, must own the gate.
Kill: in two weeks a red team builds an adapter that passes the certificate yet changes one user-visible
output. Value kill: trigger inversion (Neural Cleanse) already finds ≥95% of
single-trigger LoRA backdoors on ordinary models.

*B. Spent caches.* Inputs deleted after use (private on-device data) allow no later check; only an advance
certificate assures. Weak: verified conventional code does the same. Kill: a verified parser plus
calculator covers ≥99% of inputs.

**5. Grade.** A: FRAME. No new mechanism, but a "who" needing a guarantee on the network itself.
Needs a prior-art gate on exhaustive backdoor verification.
