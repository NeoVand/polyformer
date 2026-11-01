# R7 mapper: the WHO surgical safety checklist (surgery)

**1. Objects.** The 19-item card with three pause points (Sign In before anaesthesia, Time Out before incision, Sign
Out before leaving); the whiteboard tally of sponges and instruments; the surgeon's site mark.
**Techniques.** The Joint Commission Universal Protocol (2004); READ-DO versus DO-CONFIRM checklists (Boorman,
Boeing); Reason's Swiss cheese model (harm needs holes in independent layers to line up). Evidence: Haynes 2009
(NEJM) saw deaths fall from 1.5% to 0.8%; Urbach 2014 (NEJM) saw no effect under Ontario's mandate.

**2. Map to.**
- P1: hospitals, insurers and accreditors need the guarantee; surgeons do not.
- P2: checks sit just before irreversible acts, where checking afterwards costs an X-ray or a second operation. Our
  analogue is an a priori certificate, for when the checker cannot see the input later.
- P3: the check runs where the facts live, in people's heads.
- P4: each item is a bounded view of a present fact. Only the count needs history, and a whiteboard (a sheet)
  makes it bounded.
- P5: a layer helps only if its failures are independent. A model checking itself is the same slice.
- P6: Haynes versus Urbach: before/after studies overstate gains; measure fidelity.
- P7: the signed card in the record, read in root-cause analysis after a serious harm.

**3. Map from.** Gawande 2003 (NEJM): in retained-sponge cases the count was falsely "correct" 88% of the time. The
tally, the part one could certify, was not where things failed. Reading and recording were. The fix was barcoded
sponges, which make the input exact glyphs. Our GSM8K loss looks the same: word problems fail at reading.

**4. Ideas.**
- **A. DO-CONFIRM routing.**
  - Mechanism: the model answers in its head first. At commit it sends only the "killer" operations (large operands,
    many steps) to the sheet. The sheet's answer wins only when the two disagree.
  - Who: chat-model users. Breaks: none.
  - Kill: 0.8B model on 500 fresh GSM8K items plus 500 variants with 6 to 12 digits. Kill if it falls more than 1
    point below in-head on GSM8K or gains less than 10 points on the variants.
- **B. Pause-point gate.**
  - Mechanism: before an irreversible action, the agent writes a fixed-format ledger to the sheet. A certified
    procedure checks a conservation invariant and blocks the action on failure. The log of views is the "signed card".
  - Who: agent platforms and regulators. Breaks: "the product is the computation".
  - Kill: a 30-line conventional checker on the same ledger blocks at least 95% of the same errors (likely).
- **C. Inputs that are already glyphs.**
  - Mechanism: split the 5.8-point GSM8K loss into translation errors and computation errors.
  - Kill: computation errors are more than 30% of the lost points.

**5. Grade.** Best idea A: **TOOL** (a known design rule we were not using). On the goal itself the subfield gives
only a **FRAME**, a priori certification at pause points, which does not beat the cheap-checker objection.
