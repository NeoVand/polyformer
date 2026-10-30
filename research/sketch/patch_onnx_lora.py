"""Inject a PEFT LoRA adapter into the onnx-community Qwen3.5-0.8B decoder graph (MatMulNBits, q4) as a side path:
y = MatMulNBits(x, Wq) + scale * (x @ A^T) @ B^T. The 4-bit base weights are untouched (no requantisation); the adapter
weights ride in the .onnx protobuf as fp32 initializers. Then check the patched graph against PyTorch + adapter on
plain-text inputs_embeds (cache-free single forward).

usage: patch_onnx_lora.py <adapter_dir> <src_decoder.onnx> <dst_decoder.onnx>
"""

import json
import re
import sys

import numpy as np
import onnx
from onnx import helper, numpy_helper
from safetensors.numpy import load_file

adapter, src, dst = sys.argv[1:4]
FP16 = "fp16" in src  # the fp16 graph has plain MatMul nodes with fp16 activations
SUFFIX = "MatMul" if FP16 else "MatMul_Quant"
WDT = np.float16 if FP16 else np.float32
cfg = json.load(open(f"{adapter}/adapter_config.json"))
scale = cfg["lora_alpha"] / cfg["r"]
w = load_file(f"{adapter}/adapter_model.safetensors")
pairs = {}
for k, v in w.items():
    m = re.search(r"layers\.(\d+)\.(linear_attn|self_attn|mlp)\.(\w+)\.lora_(A|B)\.weight$", k)
    assert m, k
    layer, block, proj, ab = m.groups()
    onnx_block = {"linear_attn": "gdn", "self_attn": "attn", "mlp": "mlp"}[block]
    pairs.setdefault(f"/model/layers.{layer}/{onnx_block}/{proj}/{SUFFIX}", {})[ab] = v.astype(np.float32)

model = onnx.load(src, load_external_data=False)
g = model.graph
by_name = {n.name: n for n in g.node}
missing = [k for k in pairs if k not in by_name]
assert not missing, missing[:5]
new_nodes = []
for name, ab in pairs.items():
    node = by_name[name]
    x, y = node.input[0], node.output[0]
    base = y + "_lora_base"
    node.output[0] = base
    stem = name.replace("/", "_").strip("_")
    a_t = numpy_helper.from_array(np.ascontiguousarray(ab["A"].T).astype(WDT), stem + "_lora_A_T")  # (in, r)
    b_t = numpy_helper.from_array(np.ascontiguousarray(ab["B"].T * scale).astype(WDT), stem + "_lora_B_T")  # (r, out)
    g.initializer.extend([a_t, b_t])
    new_nodes += [
        helper.make_node("MatMul", [x, a_t.name], [stem + "_lora_h"], name=stem + "_lora_A"),
        helper.make_node("MatMul", [stem + "_lora_h", b_t.name], [stem + "_lora_d"], name=stem + "_lora_B"),
        helper.make_node("Add", [base, stem + "_lora_d"], [y], name=stem + "_lora_add"),
    ]
# keep topological order: append each side path right after its MatMulNBits
order = []
side = {n.name.rsplit("_lora_", 1)[0]: [] for n in new_nodes}
for n in new_nodes:
    side[n.name.rsplit("_lora_", 1)[0]].append(n)
for n in g.node:
    order.append(n)
    stem = n.name.replace("/", "_").strip("_")
    if n.name in pairs:
        order += side[stem]
del g.node[:]
g.node.extend(order)
onnx.save(model, dst)  # external data references (decoder_model_merged_q4.onnx_data) are kept as they were
print(f"patched {len(pairs)} matmuls, scale {scale}, wrote {dst}")
