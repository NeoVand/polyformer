# Learn visual review

The Learn route was reviewed from a production build served statically on port 4173 at 1440 × 900 and 390 × 844, with both browser color schemes. The site's deliberately fixed monochrome dark palette is the same in both schemes.

Files follow `learn-{chapter}-{desktop|mobile}-{dark|light}.png`:

- `intro`: title, narrative, provenance legend and initial SET example.
- `groups`: three-position clock arithmetic and a four-attribute card sum.
- `language`: the approximate 0.4% / 0.75% language-loss gains against the 1% target.
- `features`: supplied character features at chance on Match-4, with the separate Newton reference.
- `order`: a labelled triangle turned then flipped versus flipped then turned.
- `representations`: a computed A5 rotation acting on an icosahedron.
- `holonomy`: every ordered matrix product containing the marked token, separated by subset size.
- `group-results`: the A5 accuracy ladder with its exact order-blind ceiling.
- `limits`: theorem assumptions alongside the order-loss illustration.
- `programs`: the same swaps executed in opposite orders.
- `meaning`: comparison, phase addition and ordered rotation products.

For `groups` and `representations`, `-motion.png` captures immediately after pressing the control, and `-frame2.png` captures the settled result 1 second later. The base image shows the initial state.

The first visual pass found a Tailwind `outline` class collision drawing unwanted boxes around triangles, a 4px mobile clipping of the icosahedron caption, and an overly small mobile accuracy ladder. The class was renamed; the icosahedron was reduced slightly; and a compact ladder now uses a wider plot with tighter row spacing. The clock's singular tick label was corrected. The triangle comparison uses stable worked snapshots so its labels never jitter during a reset. New chapter headings retain dynamic numbering, all figures have captions below, and text remains below the mobile sticky figure.

Final production pass: all 11 views were captured in both sizes and both color schemes after rebuilding. All were opened directly or in review contact sheets; clock and icosahedron motion/settled frames were inspected. The automated geometry audit (`learn-audit.json`) reports no horizontal overflow, clipped figure content, or browser errors across the 44 base captures. Final plots, captions and triangle labels are clean.
