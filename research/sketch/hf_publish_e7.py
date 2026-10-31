"""Publish the gated E7 program as a new revision of mohsenvand/sketchpad-0.8b-preview (CALC, 30 Oct 2026; Neo's OK
of 30 Oct relayed by the orchestrator), then check every file of the new revision by sha256 against the staged copy.

The staged folder holds exactly the files that change: arithmetic/onnx/* (the gated E7 graph, its lens), arithmetic/
inside.*, arithmetic/certificate.json (measured on the M4), arithmetic/adapter/* (the E7 adapter the graph was built
from) and README.md. base/ and arithmetic/sprites.png are not touched; the check confirms they are unchanged.
The token is the one the Hugging Face library finds on this machine; it is never printed.

  python hf_publish_e7.py <staged dir> <parent revision>            # upload, then verify
  python hf_publish_e7.py <staged dir> <parent revision> <revision>  # verify an upload only
"""

import hashlib
import json
import pathlib
import sys
import tempfile

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download

REPO = "mohsenvand/sketchpad-0.8b-preview"
stage, parent = pathlib.Path(sys.argv[1]), sys.argv[2]
api = HfApi()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


local = {str(p.relative_to(stage)): sha(p) for p in sorted(stage.rglob("*")) if p.is_file()}
if len(sys.argv) > 3:
    rev = sys.argv[3]
else:
    ops = [CommitOperationAdd(path_in_repo=k, path_or_fileobj=str(stage / k)) for k in local]
    info = api.create_commit(
        REPO, operations=ops, parent_commit=parent,
        commit_message="Arithmetic program E7 with the gate: the calculator's tables (SUB, EST, DEC) as well; "
                       "certificate 2,446/2,446 on an M4",
        commit_description="E7 (seed 3) is the E6 adapter trained on with 651 more rows: subtraction with borrow, the "
                           "quotient-digit guess and its correction. Gate 1 is the ungated E7 graph and gate 0 stock "
                           "Qwen3.5-0.8B, bit for bit on ONNX Runtime CPU; every certificate margin on the M4 equals the "
                           "ungated graph's.")
    rev = info.oid
print("revision", rev, flush=True)


def tree(r):
    return {f.path: f for f in api.list_repo_tree(REPO, revision=r, recursive=True, expand=True) if hasattr(f, "size")}


new, old = tree(rev), tree(parent)
report = {"revision": rev, "parent": parent, "changed": {}, "unchanged": [], "missing": []}
with tempfile.TemporaryDirectory() as tmp:
    for k, want in local.items():
        f = new.get(k)
        if f is None:
            report["missing"].append(k)
            continue
        if f.lfs:
            got = f.lfs.sha256
        else:
            got = sha(hf_hub_download(REPO, k, revision=rev, cache_dir=tmp))
        report["changed"][k] = {"sha256": want, "ok": got == want, "lfs": bool(f.lfs), "size": f.size}
for k, f in old.items():
    if k in local:
        continue
    g = new.get(k)
    same = g is not None and (f.lfs.sha256 == g.lfs.sha256 if f.lfs else f.blob_id == g.blob_id)
    if same:
        report["unchanged"].append(k)
    else:
        report["missing"].append(k)
report["ok"] = not report["missing"] and all(v["ok"] for v in report["changed"].values())
print(json.dumps(report, indent=1))
