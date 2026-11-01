# R7: provenance by isotope sourcing (archaeology)

## 1. Objects and techniques

**Objects:**
- obsidian traced to single volcanic flows by X-ray fluorescence;
- Bronze Age oxhide copper ingots traced to Cyprus by lead isotopes;
- the Amesbury Archer's enamel strontium (childhood far from his grave).

**Techniques:**
- **Provenance postulate** (Weigand et al. 1977): differences between sources must exceed the scatter within a source.
- **Exclusion principle:** a mismatch rules a source out; a match means only "consistent with", because sources overlap and the reference set may be incomplete.
- **Sample-standard bracketing:** each session is calibrated against certified reference materials (NIST SRM 987).

## 2. Map to the problem

- **P1:** Courts, customs and conflict-mineral schemes (BGR's coltan fingerprint) trust an intrinsic signature; they cannot watch the process.
- **P2:** Smelting erases the mine. Our analog is inputs gone or private at check time.
- **P3:** In-place analysis when objects cannot leave; our on-device case.
- **P4:** Lead isotopes survive smelting. Our analog is a value carried unchanged through the steps.
- **P5:** Recycling mixes sources and breaks attribution. This is our no-go theorem: a step that reads earlier outputs is remelted scrap.
- **P6:** Blind round-robins on shared reference materials.
- **P7:** Calibration per instrument and session (ISO 17025). Our device-bound certificate already has this form.

## 3. Map from the problem

Sourcing is never proof: sources are open, scatter natural. Sketchpad is the special case where the runtime closes both: it renders every view (zero scatter) and enumerates all 2,446 (a closed world). That is a **dilemma**. The conditions that make the certificate a proof also make a 2,446-row lookup table an equivalent, cheaper artifact. The network adds value only where scatter is real but bounded, or where the language model's own weights must do the work.

## 4. Ideas

**A. Certified reading over a family of renderings** (breaks "exact glyphs").
- **Mechanism.** Each view class becomes a source with scatter: fonts, rasterisers, subpixel shifts, JPEG. Certify a grid of renderings and cover the gaps with interval bound propagation, a sound way to push a box of inputs through a network. Uncovered views abstain.
- **Who would care.** Pixel-only agents reading amounts off remote screens with no DOM.
- **Kill.** Covering JPEG quality ≥75 and ±0.5 px shifts needs over 10^8 views, or certifies under 99% of classes.

**B. An auditor that can only reject.**
- **Mechanism.** The gated certified path re-reads each local step of the chat model's own reasoning. Rejection is sound; acceptance is local.
- **Kill.** Under 10% of wrong answers on fresh GSM8K contain a step that is wrong on its own terms.

**C. A calibration certificate.**
- **Mechanism.** The view table as a reference material, run at load, margin drift logged per device.

## 5. Grade

Best idea: A. Grade: **TOOL**. Certified robustness is known (DeepG 2019) but unused by us, and it is the only exit from the dilemma.

Glossary candidates: provenance postulate, exclusion principle, sample-standard bracketing, interval bound propagation, lookup-table dilemma.
