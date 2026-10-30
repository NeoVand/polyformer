"""Multi-step word problems in stock Qwen's own words, every calculation routed through the sheet (Toolformer's recipe on
the model's own text: generate, insert the tool calls, keep what checks out).

Stock writes step-by-step solutions to GSM8K **training** problems (greedy, thinking off) under a system prompt asking
for each calculation on its own line as `expression = result`. A solution is kept only if its final `Answer:` equals
GSM8K's and every calculation line, run on sheet_ref.py (the host stand-in), prints exactly the result stock wrote. Each
calculation line then becomes a ```sheet block (model), the runtime's `= …` line (masked) and stock's next words. The
training dialogue has no system prompt: the user asks the question, the model reasons as stock does and computes on
the sheet. The test split is never read.

  python chat/gsm8k_stock.py <out dir> [n_problems=1600]      # writes gsm8k_stock.jsonl and gsm8k_stock_stats.json
"""

import json
import pathlib
import random
import re
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import e2_column as e2  # noqa: E402
import sheet_ref  # noqa: E402
from gen import chat_prefix, generate  # noqa: E402

SYSTEM = ("Solve the problem step by step in plain sentences. Whenever you calculate, write the calculation alone on its "
          "own line in the form `expression = result`, using only numbers, brackets and + - × ÷ (no units, no LaTeX, "
          "no variables). End with a line `Answer: <number>`.\n\nExample:\nQuestion: A shop has 12 boxes of 8 pens and "
          "5 loose pens. It sells 30 pens. How many pens are left?\nThe boxes hold 12 boxes of 8 pens:\n12 × 8 = 96\n"
          "With the loose pens, the shop has:\n96 + 5 = 101\nAfter selling 30 pens:\n101 - 30 = 71\nAnswer: 71")
INLINE = re.compile(r"(?<![\w.])(\(?[0-9][0-9.,]*(?:\s*[+\-−×*÷/]\s*\(?[0-9][0-9.,]*\)?)+\)?)\s*=\s*\$?(-?[0-9][0-9,]*(?:\.[0-9]+)?)")
CALC = re.compile(r"^\s*`?\s*([0-9][0-9.,\s()+\-−×*÷/]*[0-9)])\s*=\s*\$?(-?[0-9][0-9,]*\.?[0-9]*)\s*`?\s*$")
SUFFIXES = ["", "", "\n\nSolve the problem. End with the final answer on its own line as 'Answer: <number>'.",
            "\n\nShow your steps.", "\n\nWhat is the answer?"]


def number(s):
    return Fraction(s.replace(",", "").rstrip("."))


def sheet_line(raw, result):
    """(expr, printed value) if raw arithmetic runs on the stand-in and prints exactly `result`, else (None, why)."""
    expr = " ".join(raw.replace(",", "").replace("*", " × ").replace("/", " ÷ ").replace("-", " − ")
                    .replace("+", " + ").split()).replace("( ", "(").replace(" )", ")")
    res = sheet_ref.run(expr)[-1]
    if not res.startswith("= ") or res.startswith("= error") or res.endswith("…"):
        return None, "unparsed or inexact step"
    if number(res[2:]) != number(result):
        return None, "stock arithmetic slip"
    if res[2:] != result.replace(",", ""):
        return None, "format differs"
    return expr, res


def convert(reply, want):
    m = re.findall(r"Answer:\s*\$?(-?[0-9][0-9,]*\.?[0-9]*)", reply)
    if not m or number(m[-1]) != want:
        return None, "wrong answer"
    segs, text, blocks = [], "", 0
    for line in reply.split("\n"):
        c = CALC.match(line)
        if c and any(op in c.group(1) for op in "+-−×*÷/"):  # a calculation on its own line
            expr, res = sheet_line(c.group(1), c.group(2))
            if expr is None:
                return None, res
            segs.append([text + "```sheet\n" + expr + "\n```", True])
            segs.append(["\n" + res + "\n", False])
            text = ""
            blocks += 1
            continue
        found = [m for m in INLINE.finditer(line) if any(op in m.group(1) for op in "+-−×*÷/")]
        if not found or "\\" in line:  # leave LaTeX lines as stock wrote them
            text += line + "\n"
            continue
        pos = 0
        for m in found:  # inline: the words before it (the plan), the block, the rest with the sheet's value
            expr, res = sheet_line(m.group(1), m.group(2))
            if expr is None:
                return None, res
            head = (text + line[pos : m.start()]).rstrip()
            segs.append([(head + "\n" if head else "") + "```sheet\n" + expr + "\n```", True])
            segs.append(["\n" + res + "\n", False])
            text = res[2:]
            pos = m.end()
            blocks += 1
        text += line[pos:] + "\n"
    if not blocks:
        return None, "no calculation line"
    segs.append([text.rstrip("\n"), True])
    return segs, "kept"


def main():
    from datasets import load_dataset

    out = pathlib.Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 1600
    rng = random.Random(0)
    ds = list(load_dataset("openai/gsm8k", "main", split="train"))
    rng.shuffle(ds)
    ds = ds[:n]
    tok = e2.tok
    model = e2.load_base().eval()
    prompts = [chat_prefix(tok, [{"role": "system", "content": SYSTEM}, {"role": "user", "content": d["question"]}])
               for d in ds]
    outs = generate(model, tok, prompts, max_new=640, batch=64)
    raw = [tok.decode(o, skip_special_tokens=True).strip() for o in outs]
    with open(out / "gsm8k_stock_raw.jsonl", "w") as f:
        for d, r in zip(ds, raw):
            f.write(json.dumps({"question": d["question"], "answer": d["answer"], "reply": r}, ensure_ascii=False) + "\n")
    stats, kept = {}, []
    for d, reply in zip(ds, raw):
        want = number(d["answer"].split("####")[-1].strip())
        segs, why = convert(reply, want)
        stats[why] = stats.get(why, 0) + 1
        if segs:
            kept.append({"family": "gsm8k", "sub": "gsm8k_stock", "split": "train", "needs_sheet": True,
                         "user": d["question"] + rng.choice(SUFFIXES), "segments": segs, "id": f"s{len(kept)}"})
    with open(out / "gsm8k_stock.jsonl", "w") as f:
        for x in kept:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    json.dump({"read": len(ds), **stats}, open(out / "gsm8k_stock_stats.json", "w"), indent=1)
    print(json.dumps({"read": len(ds), **stats}), flush=True)


if __name__ == "__main__":
    main()
