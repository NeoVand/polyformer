# R7 mapping: AOC certification of terroir (wine)

**1. Objects and techniques.**
Objects: *cahier des charges* (published spec: area, grapes, top yield, methods); *parcellaire* (parcel map); cellar
register (each lot's origin).
Techniques: ISO/IEC 17065 (certifier independent of producer); *mass balance* (volume sold ≤ hectares × top yield, checked
on paper); SNIF-NMR (heavy-hydrogen ratios in the alcohol, matched to an EU databank, reveal origin); *déclassement* (a
failing lot is sold under a lower label).

**2. Map to the problem.**
- P1: a buyer who cannot see the vineyard. Us: someone who cannot see inputs or rerun.
- P2: origin is invisible in the wine; tasting is a weak checker. Us: *how* an output was made.
- P3: the guarantee comes in advance; nobody inspects bottles after sale. Us: no-log, on-device runs.
- P4: the spec lists allowed practices, not flavours. Us: certify rules (permissions, protocol).
- P5: the label limits its claim ("from area X", not "good"). Us: tag each answer span certified or not.
- P6: mass balance caught fraud tasters missed. Us: a fault the certificate finds and a test budget misses.
- P7: public spec, independent certifier, lot number. Us: view table, Lean proof, hardware ID, trace hash.

**3. Map from the problem.** Our view check is AOC tasting of every lot, made exact; complete only because the parcel map
is finite. Terroir is our hardware: the same weights on another GPU carry no claim. AOC sets three tests: the
buyer cannot check, fakes are cheap, the real thing earns a premium. Certified arithmetic fails all three: a calculator
is a perfect fake.

**4. Ideas.**

**A. No-trigger label for delegated weights.** Each output is checked exactly, so no hidden channel carries state between
steps, and any fault must appear inside a single view. Listing every view therefore proves no trigger exists at any length,
on the buyer's hardware; the gate proves the adapter leaves everything else bit-identical. *Who:* model supply-chain
security and sleeper-agent research (a model trained to misbehave only on a secret trigger; Hubinger et al. 2024).
*Breaks:* the product is the certificate; the venue is security. *Kill:* if 10^4 random problems already visit all 2,446
views, the certificate equals coverage testing (every case visited once) plus a receipt. I expect this for arithmetic;
A survives only where adversaries reach views natural inputs rarely do.

**B. Mass balance for translation.** Check the written program against conservation rules from the prompt (each quantity
used once, units balance); on failure, use the base model's answer. *Who:* anyone facing the −5.8 GSM8K loss. *Kill:* on
500 fresh items, it flags under 50% of wrong programs, or flags over 10% of correct ones.

**C. Demotion for perception.** Snap a perceived view to a certified view only at margin ≥ δ; otherwise label the run
uncertified. *Breaks:* exact glyphs. *Kill:* over 20% of photographed receipts are demoted.

**5. Grade.** Best idea: A. **FRAME.** Trigger freedom already follows from all-inputs exactness. The main lesson is the
three-test rule (§3). B is a TOOL.
