"""
Copies REASON's reference fixtures (branch `reason`, research/reason/fixtures/reason_fixtures.json, written by
reason_core.selftest) into the page's test fixtures, adding what the browser tests need to run without Qwen3's
tokenizer on disk: each id's token string (for decoding), the ids of the texts the clock and the tests encode (the
chat prompts, the pieces of a `<final>` line, the error lines, the digits), and ids with character offsets for the
texts the clock walks or reads spans from (every question and every call's notes). Nothing in the reference's own
fields is changed.

    UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --no-project --with tokenizers --with huggingface_hub \\
        python -I scripts/reason_fixtures.py [../reason/research/reason/fixtures/reason_fixtures.json]
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "reason" / "research" / "reason" / "fixtures"
                   / "reason_fixtures.json")
OUT = ROOT / "src" / "lib" / "interpreter" / "webgpu" / "fixtures" / "reason.json"
CHAT = "<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
# error lines the page's tests write besides the fixtures' own (REASON_FORMAT §5, §6)
MESSAGES = ["too many calls", "first number: no result 1", "first number: no result 5",
            "second number: no result 3", "first number: anchors not found in the prompt",
            "second number: anchors not found in the prompt", "anchors not found in the prompt"]


def main():
    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer
    path = hf_hub_download("Qwen/Qwen3-4B", "tokenizer.json")
    tok = Tokenizer.from_file(path)
    sha = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    ref = json.loads(SRC.read_text())
    enc = lambda s: list(tok.encode(s, add_special_tokens=False).ids)  # noqa: E731

    texts = ["\n", "\n<final>", " </final>\n", " c=", " s=", " b=", " d=", " t=", "<|im_end|>", "<|endoftext|>",
             "<program>", "<exec/>"] + [str(d) for d in range(10)]
    texts += [f"\n<final> error: {m} </final>\n" for m in MESSAGES]
    for c in ref["cases"]:
        prompt = CHAT.format(q=c["question"])
        # the fixtures were written with this tokenizer: the chat prompt re-encodes to the same ids
        assert enc(prompt) == c["prompt_ids"], f"{c['name']}: the prompt ids differ from this tokenizer's"
        texts.append(prompt)
        for call in c["calls"]:
            texts.append(call["final_text"])
    encoded = {t: enc(t) for t in texts}
    # ids and offsets of every source the clock reads: the questions and each call's notes
    walked = {}
    for c in ref["cases"]:
        for s in [c["question"]] + [call["notes"] for call in c["calls"]]:
            e = tok.encode(s, add_special_tokens=False)
            walked[s] = {"ids": list(e.ids), "offsets": [list(o) for o in e.offsets]}

    ids = set()
    for c in ref["cases"]:
        ids |= set(c["prompt_ids"]) | set(c["response_ids"])
        for call in c["calls"]:
            ids |= set(call["final_ids"])
    for v in encoded.values():
        ids |= set(v)
    for v in walked.values():
        ids |= set(v["ids"])
    try:
        commit = subprocess.run(["git", "-C", str(SRC.parent), "log", "-1", "--format=%H", "--", str(SRC)],
                                capture_output=True, text=True).stdout.strip() or None
    except OSError:
        commit = None
    out = dict(ref)
    out["copied_from"] = {"path": "research/reason/fixtures/reason_fixtures.json", "branch": "reason",
                          "commit": commit, "sha256": hashlib.sha256(SRC.read_bytes()).hexdigest()}
    out["tokenizer_sha256"] = sha
    out["ids"] = {"nl": enc("\n")[0], "im_end": tok.token_to_id("<|im_end|>"),
                  "endoftext": tok.token_to_id("<|endoftext|>"), "digits": [enc(str(d))[0] for d in range(10)]}
    out["tokens"] = {str(i): tok.id_to_token(i) for i in sorted(ids)}
    out["special"] = sorted(i for i, t in tok.get_added_tokens_decoder().items() if t.special)
    out["encoded"] = encoded
    out["walked"] = walked
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"wrote": str(OUT), "cases": len(ref["cases"]), "locate": len(ref["locate"]),
                      "tokens": len(out["tokens"]), "commit": commit}))


if __name__ == "__main__":
    main()
