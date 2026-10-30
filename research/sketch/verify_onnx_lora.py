"""Check the LoRA graph patch: the change the adapter makes to the logits must be the same in ONNX (q4 base, CPU) and in
PyTorch (fp32 base). Text-only, cache-free single forward on the same embeddings.
Reports the correlation of the two logit deltas and their argmax agreement with and without the adapter.

usage: verify_onnx_lora.py <adapter_dir> <onnx_dir>   (expects onnx/decoder_model_merged_q4{,_lora}.onnx)
"""

import sys

import numpy as np
import onnxruntime as ort
import torch
from peft import PeftModel
from transformers import AutoModelForImageTextToText, AutoTokenizer

adapter, onnx_dir = sys.argv[1:3]
HF = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"
tok = AutoTokenizer.from_pretrained(HF)
ids = tok.encode(open("/Users/neo/repos/polyformer/research/PRIMER.md").read())[:96]
model = PeftModel.from_pretrained(AutoModelForImageTextToText.from_pretrained(HF, dtype=torch.float32), adapter).eval()
with torch.no_grad():
    t = torch.tensor([ids])
    emb = model.get_input_embeddings()(t).numpy()
    hf_lora = model(input_ids=t).logits[0].numpy()
    with model.disable_adapter():
        hf_base = model(input_ids=t).logits[0].numpy()


def onnx_logits(path):
    s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    feed, S = {}, len(ids)
    for i in s.get_inputs():
        if i.name == "inputs_embeds":
            feed[i.name] = emb.astype(np.float32)
        elif i.name == "attention_mask":
            feed[i.name] = np.ones((1, S), np.int64)
        elif i.name == "position_ids":
            feed[i.name] = np.tile(np.arange(S, dtype=np.int64), (3, 1, 1))
        elif i.name == "num_logits_to_keep":
            feed[i.name] = np.array(S, np.int64)
        elif i.name.startswith("past_conv"):
            feed[i.name] = np.zeros((1, 6144, 3), np.float32)
        elif i.name.startswith("past_recurrent"):
            feed[i.name] = np.zeros((1, 16, 128, 128), np.float32)
        else:
            feed[i.name] = np.zeros((1, 2, 0, 256), np.float32)
    return s.run(["logits"], feed)[0][0]


ox_base = onnx_logits(f"{onnx_dir}/onnx/decoder_model_merged_q4.onnx")
ox_lora = onnx_logits(f"{onnx_dir}/onnx/decoder_model_merged_q4_lora.onnx")
d_hf, d_ox = (hf_lora - hf_base).ravel(), (ox_lora - ox_base).ravel()
print("delta correlation", float(np.corrcoef(d_hf, d_ox)[0, 1]))
print("delta norm ratio onnx/hf", float(np.linalg.norm(d_ox) / np.linalg.norm(d_hf)))
print("argmax agree base", float((hf_base.argmax(-1) == ox_base.argmax(-1)).mean()),
      "lora", float((hf_lora.argmax(-1) == ox_lora.argmax(-1)).mean()))
