"""Multi-step word problems for the chat fine-tune: GSM8K training solutions turned into replies that call the sheet
once per step (the ToRA / PAL pattern: reasoning in words, every calculation by the tool).

GSM8K's solutions carry the calculator annotations of the original paper (Cobbe et al. 2021): `48/2 = <<48/2=24>>24`.
Each annotated line becomes a ```sheet block with that expression (ASCII → × ÷ −), the runtime's `= …` line (masked
from the loss), then the line itself without the markup ("Natalia sold 48/2 = 24 clips in May."). A problem
is kept only if every annotation parses on sheet_ref.py and the sheet's printed value equals the annotation's result
exactly, so no reply ever quotes a number the sheet would not print. The test split is never read.

  python gsm8k_dialogues.py <out.jsonl> [--n 1200] [--seed 0]
"""

import argparse
import json
import pathlib
import random
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sheet_ref  # noqa: E402

ANN = re.compile(r"<<([^<>=]+)=([^<>]+)>>")
SUFFIXES = ["", "", "\n\nSolve the problem. End with the final answer on its own line as 'Answer: <number>'.",
            "\n\nShow your steps.", "\n\nWhat is the answer?"]


def sheet_expr(e):
    return " ".join(e.replace("*", " × ").replace("/", " ÷ ").replace("-", " − ").replace("+", " + ").split()) \
        .replace("( ", "(").replace(" )", ")")


def strip_annotations(line):
    """Drop the `<<E=R>>` markup; the sentence keeps its own `48/2 = 24` wording, the value being the sheet's."""
    return ANN.sub("", line)


def convert(q, sol, suffix):
    lines = sol.strip().split("\n")
    final = lines[-1].replace("####", "").strip().replace(",", "")
    segs, text = [], ""
    for line in lines[:-1]:
        anns = ANN.findall(line)
        if not anns:
            text += line + "\n"
            continue
        exprs, shown = [], []
        for e, r in anns:
            ex = sheet_expr(e)
            res = sheet_ref.run(ex)[-1]
            if not res.startswith("= ") or res.startswith("= error"):
                return None
            v = res[2:]
            try:
                if sheet_ref.value(ex) != sheet_ref.Fraction(r.replace(",", "")) or v.endswith("…"):
                    return None
            except (ValueError, ZeroDivisionError):
                return None
            if v != r.replace(",", "").rstrip("0").rstrip(".") and v != r.replace(",", ""):
                return None
            exprs.append(ex)
            shown.append(v)
        sentence = strip_annotations(line)
        for r, v in zip([r for _, r in anns], shown):
            sentence = sentence.replace(r, v) if r != v else sentence
        segs.append([text + "```sheet\n" + "\n".join(exprs) + "\n```", True])
        segs.append(["\n" + "\n".join("= " + v for v in shown) + "\n", False])
        text = sentence + "\n"
    end = f"Answer: {final}" if "Answer:" in suffix else f"The answer is {final}."
    if not segs:
        return None
    segs.append([text + end, True])
    return {"family": "gsm8k", "sub": "gsm8k", "split": "train", "needs_sheet": True, "user": q + suffix,
            "segments": segs, "result": final}


def main():
    from datasets import load_dataset

    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=1200)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ds = list(load_dataset("openai/gsm8k", "main", split="train"))
    rng.shuffle(ds)
    kept = []
    for d in ds:
        x = convert(d["question"], d["answer"], rng.choice(SUFFIXES))
        if x:
            kept.append(x)
        if len(kept) == a.n:
            break
    with open(a.out, "w") as f:
        for i, x in enumerate(kept):
            x["id"] = f"g{i}"
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(json.dumps({"kept": len(kept), "read": ds.index(d) + 1}))


if __name__ == "__main__":
    main()
