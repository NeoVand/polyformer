"""EVENTS.md phase 4: a Python code corpus in the FineWeb-Edu format (GPT-2 tokens, <|endoftext|>
between documents, uint16) at /data/code_python/{train,val}.bin on the polyformer-data volume.

Source: the public CodeParrot-clean Python files on the Hugging Face hub (deduplicated GitHub Python).
Shards are streamed in order until the training file holds `target` tokens; every hundredth file is
held out for validation (at most 10M tokens). CPU only; never touches the GPU ledger.

    uvx modal run research/events_data.py::build --target 800000000
"""

import modal

app = modal.App("polyformer-events-data")
data_vol = modal.Volume.from_name("polyformer-data", create_if_missing=False)
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "tiktoken", "numpy", "huggingface_hub[hf_transfer]"
).env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})

REPO = "codeparrot/codeparrot-clean"


@app.function(image=image, volumes={"/data": data_vol}, cpu=16, memory=32768, timeout=3 * 3600)
def tokenize_code(target: int = 800_000_000, val_cap: int = 10_000_000) -> dict:
    import gzip
    import json
    import os
    import time

    import numpy as np
    import tiktoken
    from huggingface_hub import hf_hub_download, list_repo_files

    started = time.time()
    enc = tiktoken.get_encoding("gpt2")
    eot = enc.eot_token
    out = "/data/code_python"
    os.makedirs(out, exist_ok=True)
    shards = sorted(f for f in list_repo_files(REPO, repo_type="dataset") if f.endswith(".json.gz"))
    n_train = n_val = files = 0
    used = []
    with open(f"{out}/train.bin", "wb") as ft, open(f"{out}/val.bin", "wb") as fv:
        for shard in shards:
            if n_train >= target:
                break
            path = hf_hub_download(REPO, shard, repo_type="dataset", cache_dir="/tmp/hf")
            docs = []
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        docs.append(json.loads(line)["content"])
            os.remove(path)
            train_docs, val_docs = [], []
            for d in docs:
                (val_docs if files % 100 == 0 else train_docs).append(d)
                files += 1
            for group, fh, is_val in ((train_docs, ft, False), (val_docs, fv, True)):
                if is_val and n_val >= val_cap:
                    continue
                for i in range(0, len(group), 5000):
                    ids = enc.encode_ordinary_batch(group[i:i + 5000], num_threads=16)
                    arr = np.fromiter((t for d in ids for t in (*d, eot)), dtype=np.uint16)
                    fh.write(arr.tobytes())
                    if is_val:
                        n_val += len(arr)
                    else:
                        n_train += len(arr)
            used.append(shard)
            print(json.dumps({"shard": shard, "train": n_train, "val": n_val, "secs": round(time.time() - started)}),
                  flush=True)
    data_vol.commit()
    return {"repo": REPO, "shards": used, "files": files, "train_tokens": n_train, "val_tokens": n_val,
            "secs": round(time.time() - started)}


@app.local_entrypoint()
def build(target: int = 800_000_000):
    import json
    print(json.dumps(tokenize_code.remote(target)))
