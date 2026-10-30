"""E1b: the untouched Qwen3.5-0.8B tower on a fovea CROP (not a red box in a full grid).

A crop of 1 or 3 cells (row or column) at 32 px per cell, shown (i) at native size with the processor's minimum pixel
count lowered so it costs 1-3 vision tokens, and (ii) at the default minimum (upscaled to ~64 tokens).
Teacher-forced exact read and logit margin; 100 crops per setting.
"""
import json, random, sys, time
import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoModelForImageTextToText, AutoProcessor

PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"
dev, N = "mps", int(sys.argv[1]) if len(sys.argv) > 1 else 100
proc = AutoProcessor.from_pretrained(PATH)
tok = proc.tokenizer
model = AutoModelForImageTextToText.from_pretrained(PATH, dtype=torch.float32).to(dev).eval()
font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 27)
DEFAULT_MIN = proc.image_processor.size["shortest_edge"]


def crop(cells, vertical, cell=32):
    w, h = (cell, cell * len(cells)) if vertical else (cell * len(cells), cell)
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    for k, g in enumerate(cells):
        x0, y0, x1, y1 = font.getbbox(g)
        cx, cy = (0, k * cell) if vertical else (k * cell, 0)
        d.text((cx + (cell - (x1 - x0)) / 2 - x0, cy + (cell - (y1 - y0)) / 2 - y0), g, fill="black", font=font)
    return img


@torch.no_grad()
def read(img, answer, question):
    msgs = [{"role": "user", "content": [{"type": "image", "image": img}, {"type": "text", "text": question}]}]
    inp = proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, return_dict=True,
                                   return_tensors="pt", enable_thinking=False)
    ans = tok.encode(answer, add_special_tokens=False)
    p = inp["input_ids"].shape[1]
    for k, v in list(inp.items()):
        if torch.is_tensor(v) and v.dim() == 2 and v.shape == (1, p):
            ext = torch.tensor([ans]) if k == "input_ids" else torch.full((1, len(ans)), int(k == "attention_mask"))
            inp[k] = torch.cat([v, ext.to(v.dtype)], 1)
    vt = int(inp["image_grid_thw"].prod(-1).sum() // 4)
    logits = model(**{k: v.to(dev) for k, v in inp.items()}).logits[0, p - 1 : p - 1 + len(ans)].float().cpu()
    t = torch.tensor(ans)
    m = logits.gather(1, t[:, None])[:, 0] - logits.scatter(1, t[:, None], float("-inf")).max(1).values
    return bool((m > 0).all()), float(m.min()), vt


if __name__ == "__main__":
    res, t0 = [], time.time()
    for native in (True, False):
        proc.image_processor.size["shortest_edge"] = 32 * 32 if native else DEFAULT_MIN
        for n, vertical in ((1, False), (3, False), (3, True)):
            rng = random.Random(n * 10 + vertical)
            ok, margins, vts = 0, [], []
            for _ in range(N):
                cells = [rng.choice("0123456789") for _ in range(n)]
                q = "Read the digit." if n == 1 else ("Read the digits from top to bottom." if vertical else "Read the digits from left to right.")
                e, m, vt = read(crop(cells, vertical), "".join(cells), q + " Reply with the digits only.")
                ok += e; margins.append(m); vts.append(vt)
            margins.sort()
            row = {"native": native, "cells": n, "vertical": vertical, "vision_tokens": sum(vts) / N, "exact": ok / N,
                   "min_margin": margins[0], "p05_margin": margins[N // 20], "median_margin": margins[N // 2]}
            res.append(row)
            print(json.dumps(row), f"({time.time() - t0:.0f}s)", flush=True)
    json.dump(res, open("e1b_fovea.json", "w"), indent=1)
