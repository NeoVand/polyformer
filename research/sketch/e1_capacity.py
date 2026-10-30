"""E1 (SKETCHPAD.md section 6): the exact optical capacity of Qwen3.5-0.8B, untouched weights, $0 on the M4.

Digit grids rendered at 32, 16 and 8 px per cell, all as 256x256 images (64 vision tokens), so 1, 4 and 16 cells per
vision token. Two reads, teacher-forced, no thinking:
  grid  - transcribe the whole grid, one line per row: per-cell accuracy, whole-grid exact, minimum logit margin
  fovea - the digit in the red box and the two to its right (3 tokens): exact rate and margin, isolating the eye from
          long copying
Margin = logit of the true token minus the best other token, per answer token.
"""

import json
import random
import sys
import time

import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoModelForImageTextToText, AutoProcessor

PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"
dev = "mps"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
proc = AutoProcessor.from_pretrained(PATH)
tok = proc.tokenizer
model = AutoModelForImageTextToText.from_pretrained(PATH, dtype=torch.float32).to(dev).eval()
FONT = "/System/Library/Fonts/Menlo.ttc"


def render(grid, cell, box=None):
    n = len(grid)
    img = Image.new("RGB", (n * cell, n * cell), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, int(cell * 0.85))
    for r, row in enumerate(grid):
        for c, g in enumerate(row):
            x0, y0, x1, y1 = font.getbbox(g)
            d.text((c * cell + (cell - (x1 - x0)) / 2 - x0, r * cell + (cell - (y1 - y0)) / 2 - y0), g, fill="black", font=font)
    if box is not None:
        r, c = box
        d.rectangle((c * cell, r * cell, (c + 1) * cell - 1, (r + 1) * cell - 1), outline=(220, 0, 0), width=max(1, cell // 10))
    return img


def build(question, answer, img):
    msgs = [{"role": "user", "content": [{"type": "image", "image": img}, {"type": "text", "text": question}]}]
    inp = proc.apply_chat_template(
        msgs, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt", enable_thinking=False
    )
    ans = tok.encode(answer, add_special_tokens=False)
    p = inp["input_ids"].shape[1]
    for k, v in list(inp.items()):
        if torch.is_tensor(v) and v.dim() == 2 and v.shape == (1, p):
            ext = torch.tensor([ans]) if k == "input_ids" else torch.full((1, len(ans)), int(k == "attention_mask"))
            inp[k] = torch.cat([v, ext.to(v.dtype)], 1)
    vt = int(inp["image_grid_thw"].prod(-1).sum() // 4)
    return {k: v.to(dev) for k, v in inp.items()}, p, ans, vt


@torch.no_grad()
def score(inp, p, ans):
    logits = model(**inp).logits[0, p - 1 : p - 1 + len(ans)].float().cpu()
    tgt = torch.tensor(ans)
    true = logits.gather(1, tgt[:, None])[:, 0]
    other = logits.scatter(1, tgt[:, None], float("-inf")).max(1).values
    margin = true - other
    return margin > 0, margin


GRID_Q = "Transcribe the grid of digits row by row: one line per row, the digits of a row written together."
FOVEA_Q = "Read the digit inside the red box and the two digits to its right. Reply with the three digits only."
res, t0 = [], time.time()
for n, cell in ((8, 32), (16, 16), (32, 8)):
    rng = random.Random(n)
    g = {"cells": 0, "cell_ok": 0, "grid_exact": 0, "fovea_exact": 0, "min_margin_cell": [], "min_margin_fovea": []}
    vts = []
    for _ in range(N):
        grid = ["".join(rng.choice("0123456789") for _ in range(n)) for _ in range(n)]
        inp, p, ans, vt = build(GRID_Q, "\n".join(grid), render(grid, cell))
        vts.append(vt)
        ok, m = score(inp, p, ans)
        digit = torch.tensor([tok.decode([a]).isdigit() for a in ans])
        g["cells"] += int(digit.sum())
        g["cell_ok"] += int(ok[digit].sum())
        g["grid_exact"] += bool(ok.all())
        g["min_margin_cell"].append(float(m[digit].min()))
        r, c = rng.randrange(n), rng.randrange(n - 2)
        ok, m = score(*build(FOVEA_Q, grid[r][c : c + 3], render(grid, cell, (r, c)))[:3])
        g["fovea_exact"] += bool(ok.all())
        g["min_margin_fovea"].append(float(m.min()))
    row = {
        "grid": f"{n}x{n}",
        "px_per_cell": cell,
        "vision_tokens": sum(vts) / N,
        "cells_per_token": n * n / (sum(vts) / N),
        "per_cell": g["cell_ok"] / g["cells"],
        "grid_exact": g["grid_exact"] / N,
        "fovea_exact": g["fovea_exact"] / N,
        "median_min_margin_cell": sorted(g["min_margin_cell"])[N // 2],
        "median_min_margin_fovea": sorted(g["min_margin_fovea"])[N // 2],
    }
    res.append(row)
    print(json.dumps(row), f"({time.time() - t0:.0f}s)", flush=True)
json.dump(res, open("e1_capacity.json", "w"), indent=1)
grid = ["".join(random.Random(7).choice("0123456789") for _ in range(16)) for _ in range(16)]
render(grid, 16, (5, 6)).save("e1_example_16px.png")
print("done")
