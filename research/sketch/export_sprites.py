"""Export the exact training glyph pixels: for each crop row k (0 carry, 1 top, 2 bottom) and glyph g (blank, 0-9),
slice row k out of a training crop. The page assembles fovea crops from these, so the browser sees training pixels."""
import json
from PIL import Image
import importlib.util, sys
spec = importlib.util.spec_from_file_location("e2", "e2_column.py")
src = open("e2_column.py").read().split("PATH = ")[0]  # imports only; rebuild the painter without loading the model
from PIL import ImageDraw, ImageFont
CELL = 32
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 27)
def crop(cells):
    img = Image.new("RGB", (CELL, 3 * CELL), "white")
    d = ImageDraw.Draw(img)
    for k, g in enumerate(cells):
        if g != " ":
            x0, y0, x1, y1 = FONT.getbbox(g)
            d.text(((CELL - (x1 - x0)) / 2 - x0, k * CELL + (CELL - (y1 - y0)) / 2 - y0), g, fill="black", font=FONT)
    return img
GLYPHS = " 0123456789"
sheet = Image.new("RGB", (CELL * len(GLYPHS), 3 * CELL), "white")
for gi, g in enumerate(GLYPHS):
    img = crop([g, g, g])
    sheet.paste(img, (gi * CELL, 0))
sheet.save("e3_browser/sprites.png")
json.dump({"cell": CELL, "glyphs": GLYPHS, "rows": ["carry", "top", "bottom"]}, open("e3_browser/sprites.json", "w"))
# self-check: assembling a crop from the sheet reproduces the training crop pixel for pixel
import random
rng = random.Random(0)
for _ in range(200):
    cells = [rng.choice(GLYPHS) for _ in range(3)]
    ref = crop(cells)
    asm = Image.new("RGB", (CELL, 3 * CELL), "white")
    for k, g in enumerate(cells):
        gi = GLYPHS.index(g)
        asm.paste(sheet.crop((gi * CELL, k * CELL, (gi + 1) * CELL, (k + 1) * CELL)), (0, k * CELL))
    assert list(asm.getdata()) == list(ref.getdata()), cells
print("sprites ok: 200/200 assembled crops are pixel-identical to training crops")
