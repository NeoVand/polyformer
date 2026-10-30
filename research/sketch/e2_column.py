"""E2 (SKETCHPAD.md section 6): column addition on the model's own canvas, Qwen3.5-0.8B + LoRA, $0 on the M4.

The canvas is the only state. Each tick the model sees a fixed instruction and a fovea crop of one column
(carry, top digit, bottom digit; 3 cells, 32 px, ~3 vision tokens) and writes two tokens: the sum digit and the carry,
or "H" (halt) when the column and carry are blank. A fixed painter stamps the written digit in the sum row and the
carry above the next column; a fixed cropper moves one column left. Nothing else carries the past.

Certificate: every possible fovea is (carry in {blank, 1}) x (top in blank+0-9) x (bottom in blank+0-9) = 242 crops.
If all 242 are read and answered correctly with positive margin, every addition of every length is exact (induction
over columns). Training uses the whole domain every step (certificate as loss, O3) with a margin hinge; the vision
tower is frozen; LoRA on the language model only. Retention: perplexity ratio on plain text with the adapter on/off.

usage: e2_column.py train [steps] | e2_column.py eval <adapter_dir>
"""

import itertools
import json
import math
import random
import sys
import time

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoModelForImageTextToText, AutoProcessor

PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"
dev = "mps"
CELL = 32
proc = AutoProcessor.from_pretrained(PATH)
proc.image_processor.size["shortest_edge"] = CELL * CELL  # native size: a 3-cell crop costs 3 vision tokens
tok = proc.tokenizer
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 27)
INSTR = "Column addition. The image shows one column: the carry (blank or 1), the top digit, the bottom digit. " \
        "Write the sum digit and the carry, or H if the column and the carry are blank."
BLANK = " "


def crop(carry: str, top: str, bottom: str) -> Image.Image:
    img = Image.new("RGB", (CELL, 3 * CELL), "white")
    d = ImageDraw.Draw(img)
    for k, g in enumerate((carry, top, bottom)):
        if g != BLANK:
            x0, y0, x1, y1 = FONT.getbbox(g)
            d.text(((CELL - (x1 - x0)) / 2 - x0, k * CELL + (CELL - (y1 - y0)) / 2 - y0), g, fill="black", font=FONT)
    return img


def rule(carry, top, bottom):
    if carry == top == bottom == BLANK:
        return "H"
    s = sum(int(g) for g in (carry, top, bottom) if g != BLANK)
    return f"{s % 10}{s // 10}"


DOMAIN = [(c, t, b) for c in (BLANK, "1") for t in BLANK + "0123456789" for b in BLANK + "0123456789"]
assert len(DOMAIN) == 242


def build(img, answer):
    msgs = [{"role": "user", "content": [{"type": "image", "image": img}, {"type": "text", "text": INSTR}]}]
    inp = proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, return_dict=True,
                                   return_tensors="pt", enable_thinking=False)
    ans = tok.encode(answer, add_special_tokens=False)
    p = inp["input_ids"].shape[1]
    for k, v in list(inp.items()):
        if torch.is_tensor(v) and v.dim() == 2 and v.shape == (1, p):
            ext = torch.tensor([ans]) if k == "input_ids" else torch.full((1, len(ans)), int(k == "attention_mask"))
            inp[k] = torch.cat([v, ext.to(v.dtype)], 1)
    return {k: v.to(dev) for k, v in inp.items()}, p, torch.tensor(ans, device=dev)


CACHE = {}


def example(x):
    if x not in CACHE:
        CACHE[x] = build(crop(*x), rule(*x))
    return CACHE[x]


def answer_logits(model, x):
    inp, p, ans = example(x)
    return model(**inp).logits[0, p - 1 : p - 1 + len(ans)].float(), ans


def margins(logits, ans):
    true = logits.gather(1, ans[:, None])[:, 0]
    other = logits.scatter(1, ans[:, None], float("-inf")).max(1).values
    return true - other


@torch.no_grad()
def certify(model):
    rows = []
    for x in DOMAIN:
        logits, ans = answer_logits(model, x)
        m = margins(logits, ans)
        rows.append({"col": "".join(x).replace(BLANK, "_"), "want": rule(*x),
                     "got": tok.decode(logits.argmax(-1).tolist()), "margin": float(m.min())})
    ok = sum(r["margin"] > 0 for r in rows)
    return ok, min(r["margin"] for r in rows), rows


TEXT = tok.encode(open("/Users/neo/repos/polyformer/research/PRIMER.md").read())[:512]


@torch.no_grad()
def text_ppl(model):
    ids = torch.tensor([TEXT], device=dev)
    logits = model(input_ids=ids).logits[0, :-1].float()
    return math.exp(float(torch.nn.functional.cross_entropy(logits, ids[0, 1:])))


def load_base():
    m = AutoModelForImageTextToText.from_pretrained(PATH, dtype=torch.float32).to(dev)
    for p in m.parameters():
        p.requires_grad_(False)
    return m


TEXT_CHUNKS = [TEXT[i : i + 128] for i in range(0, 512, 128)]


def text_kl(model):
    """KL(base || adapted) on a plain-text chunk: the retention term (O4)."""
    ids = torch.tensor([TEXT_CHUNKS[random.randrange(len(TEXT_CHUNKS))]], device=dev)
    with torch.no_grad(), model.disable_adapter():
        ref = model(input_ids=ids).logits.float().log_softmax(-1)
    cur = model(input_ids=ids).logits.float().log_softmax(-1)
    return torch.nn.functional.kl_div(cur, ref, log_target=True, reduction="batchmean") / ids.shape[1]


def train(steps=300, batch=16, lr=2e-4, hinge=2.0, seed=0, kl=0.0):
    torch.manual_seed(seed)
    rng = random.Random(seed)
    base = load_base()
    ppl0 = text_ppl(base.eval())
    ok0, min0, _ = certify(base)
    print(f"untouched: certificate {ok0}/242 (min margin {min0:.2f}), text ppl {ppl0:.2f}", flush=True)
    targets = r"model\.language_model\.layers\.\d+\.(self_attn\.(q|k|v|o)_proj|linear_attn\.(in_proj_qkv|in_proj_z|out_proj)|mlp\.(gate|up|down)_proj)"
    model = get_peft_model(base, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, target_modules=targets))
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr)
    log, t0 = [], time.time()
    for step in range(1, steps + 1):
        model.train()
        loss_sum = 0.0
        for x in rng.sample(DOMAIN, batch):
            logits, ans = answer_logits(model, x)
            loss = torch.nn.functional.cross_entropy(logits, ans) + torch.relu(hinge - margins(logits, ans)).mean()
            (loss / batch).backward()
            loss_sum += float(loss)
        if kl:
            (kl * text_kl(model)).backward()
        opt.step()
        opt.zero_grad()
        if step % 25 == 0 or step == steps:
            model.eval()
            ok, mn, _ = certify(model)
            ppl = text_ppl(model)
            log.append({"step": step, "loss": loss_sum / batch, "cert": ok, "min_margin": mn, "ppl_ratio": ppl / ppl0})
            print(json.dumps(log[-1]), f"({time.time() - t0:.0f}s)", flush=True)
            if ok == 242 and mn >= hinge / 2:
                break
    out = f"e2_adapter_s{seed}" + (f"_kl{kl:g}" if kl else "")
    model.save_pretrained(out)
    json.dump({"untouched": {"cert": ok0, "min_margin": min0, "ppl": ppl0}, "log": log}, open(f"{out}/train_log.json", "w"), indent=1)
    return model, out


def run_sum(model, a: str, b: str, edit=None):
    """Pinned-canvas run: the canvas (carry row, a, b, sum row) is the only state. edit=(tick, row, col_from_right, glyph)
    paints a change before that tick, as a user would."""
    n = max(len(a), len(b)) + 1
    carry, top, bot, out = [BLANK] * n, list(a.rjust(n, BLANK)), list(b.rjust(n, BLANK)), [BLANK] * n
    rows = {"carry": carry, "top": top, "bottom": bot}
    for t in range(n + 1):
        i = n - 1 - t  # column index from the left
        if edit and edit[0] == t:
            rows[edit[1]][n - 1 - edit[2]] = edit[3]
        if i < 0:
            break
        x = (carry[i], top[i], bot[i])
        with torch.no_grad():
            inp, p, _ = build(crop(*x), "00")
            nxt = model(**inp).logits[0, p - 1].argmax()
            w = tok.decode([int(nxt)])
            if w == "H":
                break
            inp["input_ids"][0, p] = nxt
            c = tok.decode([int(model(**inp).logits[0, p].argmax())])
        out[i] = w
        if i > 0:
            carry[i - 1] = "1" if c == "1" else BLANK
    return "".join(out).strip()


def evaluate(adapter):
    model = PeftModel.from_pretrained(load_base(), adapter).eval()
    ok, mn, rows = certify(model)
    res = {"cert": ok, "min_margin": mn, "fails": [r for r in rows if r["margin"] <= 0][:20]}
    rng = random.Random(1)
    for n, k in ((10, 20), (100, 5), (1000, 2)):
        good = 0
        for _ in range(k):
            a, b = (str(rng.randint(10 ** (n - 1), 10**n - 1)) for _ in range(2))
            good += run_sum(model, a, b) == str(int(a) + int(b))
        res[f"sum_{n}_digits"] = f"{good}/{k}"
        print(n, res[f"sum_{n}_digits"], flush=True)
    a, b = "4815162342", "1123581321"
    edited = run_sum(model, a, b, edit=(4, "top", 6, "9"))  # change a digit of the top number mid-run
    a2 = list(a.rjust(11, BLANK)); a2[11 - 1 - 6] = "9"
    res["edit"] = {"got": edited, "want": str(int("".join(a2)) + int(b))}
    res["ppl"] = text_ppl(model)
    json.dump(res, open(f"{adapter}/eval.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "train":
        a = sys.argv[2:] + [None] * 3
        train(steps=int(a[0] or 300), seed=int(a[1] or 0), kl=float(a[2] or 0))
    else:
        evaluate(sys.argv[2])
