"""LFM3-1.7B direct-answer probe ($0, local MPS): the same tasks as ouro_probe.py, one forward per example,
teacher-forced (every answer token must be the argmax). Also times a forward."""

import json
import random
import time
import zlib

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import ouro_probe_tasks as tasks

PATH = "/Users/neo/repos/polyformer-wt/models/lfm3-1.7b"
N = 40
dev = "mps"
tok = AutoTokenizer.from_pretrained(PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(PATH, trust_remote_code=True, dtype=torch.bfloat16).to(dev).eval()


@torch.no_grad()
def run(prompt, answer):
    p = tok.encode(prompt, add_special_tokens=False)
    a = tok.encode(prompt + answer, add_special_tokens=False)[len(p):]
    ids = torch.tensor([p + a], device=dev)
    logits = model(input_ids=ids).logits[0, len(p) - 1 : len(p) + len(a) - 1].float()
    return bool((logits.argmax(-1) == torch.tensor(a, device=dev)).all())


res, t0 = {}, time.time()
for name, make in tasks.TASKS.items():
    rng = random.Random(zlib.crc32(name.encode()))
    res[name] = sum(run(*make(rng)) for _ in range(N)) / N
    print(f"{name:6s} {res[name]:.2f} ({time.time() - t0:.0f}s)", flush=True)
ids = torch.tensor([tok.encode(tasks.TEXT, add_special_tokens=False)[:512]], device=dev)
for _ in range(2):
    model(input_ids=ids)
torch.mps.synchronize()
t1 = time.time()
for _ in range(5):
    model(input_ids=ids[:, :64])
torch.mps.synchronize()
res["ms_per_64tok_forward"] = (time.time() - t1) / 5 * 1000
print(f"forward 64 tokens: {res['ms_per_64tok_forward']:.0f} ms")
json.dump(res, open("lfm3_probe.json", "w"), indent=1)
