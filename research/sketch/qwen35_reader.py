"""Can Qwen3.5-0.8B (untouched) read a rendered canvas exactly, and what does a digit cost in vision tokens?

Renders a written sum (two right-aligned numbers over a rule) at several digit counts and font sizes, then
(R) asks for a transcription of both numbers and (A) asks for the sum directly, no thinking. Scored by teacher
forcing: exact = every answer token is the argmax; also per-digit accuracy of the transcription. The same questions
in plain text are the baseline. Vision tokens are counted from image_grid_thw (each token is a 32x32 pixel patch).
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


def render(a: str, b: str, px: int) -> Image.Image:
    font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", px)
    cw = font.getbbox("0")[2]
    width = max(len(a), len(b)) + 2
    W, H = cw * width + 2 * px, int(px * 3.6) + 2 * px
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    for r, s in enumerate((a, "+" + " " * (width - 1 - len(b)) + b)):
        d.text((px + cw * (width - len(s)), px + r * int(px * 1.3)), s, fill="black", font=font)
    y = px + 2 * int(px * 1.3) + px // 4
    d.line((px, y, px + cw * width, y), fill="black", width=max(1, px // 12))
    return img


def build(question: str, answer: str, img=None):
    content = ([{"type": "image", "image": img}] if img is not None else []) + [{"type": "text", "text": question}]
    msgs = [{"role": "user", "content": content}]
    inp = proc.apply_chat_template(
        msgs, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt", enable_thinking=False
    )
    ans = tok.encode(answer, add_special_tokens=False)
    p = inp["input_ids"].shape[1]
    for k, v in list(inp.items()):  # extend every per-token tensor over the answer (text tokens: type 0)
        if torch.is_tensor(v) and v.dim() == 2 and v.shape == (1, p):
            ext = torch.tensor([ans]) if k == "input_ids" else torch.full((1, len(ans)), int(k == "attention_mask"))
            inp[k] = torch.cat([v, ext.to(v.dtype)], 1)
    vt = int(inp["image_grid_thw"].prod(-1).sum() // 4) if "image_grid_thw" in inp else 0
    return {k: v.to(dev) for k, v in inp.items()}, p, ans, vt


@torch.no_grad()
def score(inp, p, ans):
    logits = model(**inp).logits[0, p - 1 : p - 1 + len(ans)].float()
    hit = logits.argmax(-1).cpu() == torch.tensor(ans)
    return bool(hit.all()), float(hit.float().mean())


def number(n, rng):
    return str(rng.randint(10 ** (n - 1), 10**n - 1))


READ_Q = "Read the two numbers in the image. Reply with the first number, a space, then the second number."
SUM_Q = "What is the sum shown in the image? Reply with the number only."
res, t0 = [], time.time()
for n in (8, 16, 32, 64):
    for px in (16, 24, 32):
        rng = random.Random(n * 100 + px)
        acc = {"read_exact": 0, "read_digit": 0.0, "sum_exact": 0, "text_read_exact": 0, "text_sum_exact": 0}
        vts = []
        for _ in range(N):
            a, b = number(n, rng), number(n, rng)
            img = render(a, b, px)
            inp, p, ans, vt = build(READ_Q, f"{a} {b}", img)
            e, dacc = score(inp, p, ans)
            acc["read_exact"] += e
            acc["read_digit"] += dacc
            vts.append(vt)
            acc["sum_exact"] += score(*build(SUM_Q, str(int(a) + int(b)), img)[:3])[0]
            if px == 16:
                txt = f"{a}\n+{b}\n"
                acc["text_read_exact"] += score(*build(READ_Q.replace("in the image", "below") + "\n" + txt, f"{a} {b}")[:3])[0]
                acc["text_sum_exact"] += score(*build(SUM_Q.replace("shown in the image", "below") + "\n" + txt, str(int(a) + int(b)))[:3])[0]
        row = {"digits": n, "font_px": px, "vision_tokens": sum(vts) / N, "tokens_per_digit": sum(vts) / N / (2 * n)}
        row.update({k: v / N for k, v in acc.items()})
        if px != 16:
            row.pop("text_read_exact"), row.pop("text_sum_exact")
        res.append(row)
        print(json.dumps(row), f"({time.time() - t0:.0f}s)", flush=True)
json.dump(res, open("qwen35_reader.json", "w"), indent=1)
render("31415926535897932384", "27182818284590452353", 24).save("canvas_example.png")
print("done")
