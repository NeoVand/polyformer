# SVG check

Each SVG rendered by rsvg-convert at 600 dpi and compared with the matplotlib PNG, both scaled to 150 dpi; 'off' is the share of pixels that differ by more than 64 of 255 in any channel. Antialiasing and glyph rasterisation leave a thin fringe along edges; a missing or moved element would show as a solid block. 'Moved' allows each pixel a one-pixel shift, so it leaves only real displacement. Glyph outlines count `<use>` elements that are not plot markers; they must be 0.

## Figure 1: `fig1_merged.svg` (4.8 MB)

- panels and sublayers (drawn elements): a: axes 19, marks 12, labels 9; b: render 2, labels 16; c: render 1, axes 19, marks 6, labels 7; d: marks 99, labels 71
- live text elements: 49; glyph outlines: 0
- fonts: Helvetica Neue (installed): 663 characters
- renders embedded at native size: b-render-merged-theorem-ours 2800×1292, b-render-merged-theorem-drift 2800×1292, c-render-merged-kick 1400×743, d-rasterised-marks 483×539, d-rasterised-marks-2 574×612, d-rasterised-marks-3 528×555
- differs from the PNG on 0.32% of pixels; on 0.031% by more than a pixel's shift

## Figure 2: `fig2.svg` (6.0 MB)

- panels and sublayers (drawn elements): a: axes 21, marks 5, labels 9; b: axes 23, marks 9, labels 6; c: render 1, marks 9, labels 24; d: render 1, marks 9, labels 10; e: axes 22, marks 8, labels 5; f: axes 22, marks 18, labels 8
- live text elements: 96; glyph outlines: 0
- fonts: Helvetica Neue (installed): 1080 characters
- renders embedded at native size: c-render-balls-main 2200×1364, d-render-balls-contrast 2200×1364
- differs from the PNG on 0.58% of pixels; on 0.032% by more than a pixel's shift

## Figure 3: `fig3.svg` (0.3 MB)

- panels and sublayers (drawn elements): a: marks 293, labels 61; b: axes 98, marks 302, labels 15
- live text elements: 97; glyph outlines: 0
- fonts: Helvetica Neue (installed): 905 characters
- renders embedded at native size: none
- differs from the PNG on 0.20% of pixels; on 0.010% by more than a pixel's shift

## Figure 4: `fig4.svg` (1.8 MB)

- panels and sublayers (drawn elements): a: axes 26, marks 20, labels 12; b: axes 19, marks 42, labels 7; c: marks 32, labels 16; d: axes 36, marks 39, labels 11
- live text elements: 84; glyph outlines: 0
- fonts: Helvetica Neue (installed): 1488 characters
- renders embedded at native size: none
- differs from the PNG on 0.61% of pixels; on 0.022% by more than a pixel's shift

## Extended Data 1: `ed1_domains.svg` (0.5 MB)

- panels and sublayers (drawn elements): figure: labels 8; a: marks 134, labels 30; b: marks 94, labels 42; c: marks 147, labels 37; d: marks 100, labels 35; e: marks 122, labels 40; f: marks 112, labels 37
- live text elements: 229; glyph outlines: 0
- fonts: Helvetica Neue (installed): 2482 characters
- renders embedded at native size: none
- differs from the PNG on 0.33% of pixels; on 0.011% by more than a pixel's shift

## Extended Data 2: `ed2_landscape.svg` (4.3 MB)

- panels and sublayers (drawn elements): a: render 1, marks 2, labels 13; b: render 1, labels 12
- live text elements: 19; glyph outlines: 0
- fonts: Helvetica Neue (installed): 523 characters
- renders embedded at native size: a-render-terrain-ce 2200×1540, b-render-terrain-total 2200×1540
- differs from the PNG on 0.33% of pixels; on 0.000% by more than a pixel's shift

## Extended Data 3: `ed3_losses.svg` (0.0 MB)

- panels and sublayers (drawn elements): a: axes 37, marks 53, labels 6; b: axes 17, marks 28, labels 7
- live text elements: 36; glyph outlines: 0
- fonts: Helvetica Neue (installed): 449 characters
- renders embedded at native size: none
- differs from the PNG on 0.40% of pixels; on 0.030% by more than a pixel's shift

## Extended Data 4: `ed4_globes.svg` (6.1 MB)

- panels and sublayers (drawn elements): a: render 1, marks 1, labels 10; b: axes 27, marks 25, labels 7; c: marks 41342, labels 57
- live text elements: 84; glyph outlines: 0
- fonts: Helvetica Neue (installed): 832 characters
- renders embedded at native size: a-render-tesseract-glass 1374×1373
- differs from the PNG on 0.22% of pixels; on 0.010% by more than a pixel's shift

## Extended Data 5: `ed5_clauses.svg` (2.7 MB)

- panels and sublayers (drawn elements): figure: render 1, marks 1, labels 54
- live text elements: 46; glyph outlines: 0
- fonts: Helvetica Neue (installed): 967 characters; STIXGeneral (installed): '→∼⊆'
- renders embedded at native size: figure-render-clauses 2400×2400
- differs from the PNG on 0.65% of pixels; on 0.043% by more than a pixel's shift

## Extended Data 6: `ed6_ablation.svg` (0.4 MB)

- panels and sublayers (drawn elements): a: marks 418, labels 102; b: axes 14, marks 215, labels 13
- live text elements: 121; glyph outlines: 0
- fonts: Helvetica Neue (installed): 1596 characters
- renders embedded at native size: none
- differs from the PNG on 0.71% of pixels; on 0.005% by more than a pixel's shift

## Extended Data 7: `ed7_frontier.svg` (0.1 MB)

- panels and sublayers (drawn elements): a: axes 41, marks 147, labels 21; b: axes 50, marks 134, labels 28; c: marks 43, labels 41
- live text elements: 107; glyph outlines: 0
- fonts: Helvetica Neue (installed): 1263 characters
- renders embedded at native size: none
- differs from the PNG on 0.29% of pixels; on 0.072% by more than a pixel's shift

## Extended Data 8: `ed8_cube.svg` (7.9 MB)

- panels and sublayers (drawn elements): a: render 6, labels 31; b: axes 25, marks 63, labels 10; c: axes 28, marks 46, labels 5
- live text elements: 58; glyph outlines: 0
- fonts: Helvetica Neue (installed): 838 characters
- renders embedded at native size: a-render-cube-s0 1150×1260, a-render-cube-s32 1150×1260, a-render-cube-s256 1150×1260, a-render-cube-s1024 1150×1260, a-render-cube-s4096 1150×1260, a-render-cube-s4096t 1150×1260
- differs from the PNG on 0.46% of pixels; on 0.026% by more than a pixel's shift

## fig_inside (not in the paper): `fig_inside.svg` (8.5 MB)

- panels and sublayers (drawn elements): a: render 1, axes 19, marks 244, labels 16; b: axes 70, marks 71, labels 10; c: render 6, marks 1, labels 15; d: axes 64, marks 110, labels 12; e: axes 13, marks 10, labels 14
- live text elements: 129; glyph outlines: 0
- fonts: Helvetica Neue (installed): 1775 characters
- renders embedded at native size: a-render-inside-hero 2200×1760, c-render-inside-step0 800×800, c-render-inside-step25 800×800, c-render-inside-step100 800×800, c-render-inside-step200 800×800, c-render-inside-step400 800×800, c-render-inside-step1000 800×800
- differs from the PNG on 0.38% of pixels; on 0.011% by more than a pixel's shift
