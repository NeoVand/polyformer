"""
Copies ARITH's reference fixtures (branch `arith`, research/arith/fixtures/reference.json, written by its
arith_fixtures.py from arith_core.py) into the page's test fixtures, adding what the browser tests need to run
without Qwen3's tokenizer on disk: each id's token string (for decoding) and the ids of the few texts the clock
encodes (with the chat prompts of every question and the words of the trained model's runs, `model_runs`). Nothing
in the reference's own fields is changed.

    uv run --no-project --with tokenizers --with huggingface_hub python -I scripts/arith_fixtures.py \\
        [../arith/research/arith/fixtures/reference.json]
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / "arith" / "research" / "arith" / "fixtures"
                   / "reference.json")
OUT = ROOT / "src" / "lib" / "interpreter" / "webgpu" / "fixtures" / "arith.json"
CHAT = "<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"


def main():
    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer
    path = hf_hub_download("Qwen/Qwen3-4B", "tokenizer.json")
    tok = Tokenizer.from_file(path)
    sha = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    ref = json.loads(SRC.read_text())
    assert ref["tokenizer_sha256"] == sha, "the fixtures were written with another tokenizer"
    enc = lambda s: list(tok.encode(s, add_special_tokens=False).ids)  # noqa: E731
    texts = ["\n", "\n<final>", " </final>\n", " c=", " s=", "<|im_end|>", "<|endoftext|>"] + [str(d) for d in range(10)]
    encoded = {t: enc(t) for t in texts}
    runs = ref.get("model_runs", {}).get("runs", [])
    for e in ref["examples"] + ref["failures"] + runs:
        encoded[CHAT.format(q=e["question"])] = enc(CHAT.format(q=e["question"]))
    for r in runs:
        encoded[r["answer_text"]] = enc(r["answer_text"])
    ids = set()
    for e in ref["examples"]:
        ids |= set(e["program_ids"]) | set(e["chat_prompt_ids"]) | set(e["final_ids"]) | set(e["answer_ids"])
    for f in ref["failures"]:
        ids |= set(f["program_ids"])
    for r in runs:
        ids |= set(r["program_ids"]) | set(r["final_ids"]) | set(r["states"]) | set(r["outputs"])
        ids |= {x for p in r["pairs"] for x in p}
    for v in encoded.values():
        ids |= set(v)
    try:
        commit = subprocess.run(["git", "-C", str(SRC.parent), "log", "-1", "--format=%H", "--", str(SRC)],
                                capture_output=True, text=True).stdout.strip() or None
    except OSError:
        commit = None
    out = dict(ref)
    out["copied_from"] = {"path": "research/arith/fixtures/reference.json", "branch": "arith", "commit": commit,
                          "sha256": hashlib.sha256(SRC.read_bytes()).hexdigest()}
    out["tokens"] = {str(i): tok.id_to_token(i) for i in sorted(ids)}
    out["special"] = sorted(i for i, t in tok.get_added_tokens_decoder().items() if t.special)
    out["encoded"] = encoded
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"wrote": str(OUT), "examples": len(ref["examples"]), "failures": len(ref["failures"]),
                      "tokens": len(out["tokens"]), "commit": commit}))


if __name__ == "__main__":
    main()
