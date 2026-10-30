"""Give a program's decoder graph a window into itself: one extra output, `hidden_states` [25, batch, seq, 1024] fp16.

Index 0 is the input embedding (vision tokens included), 1..23 the residual stream entering layers 1..23 (the `output_3`
sum of each SkipLayerNorm), 24 the final normed state that lm_head reads, the same convention as Hugging Face's
`output_hidden_states`. Nothing else in the graph changes, so logits are bit-identical; the browser reads the extra
output on every call. Also writes `lens.bin` beside the graph: the final norm's weight and the lm_head rows of the
answer alphabet, so the page can read any layer's state as a guess at the answer (the logit lens).

  python patch_onnx_inside.py <program graph in> <program graph out> <hf model dir> <base onnx dir>
"""

import json
import sys

import numpy as np
import onnx
from onnx import TensorProto, helper

src, dst, hf = sys.argv[1:4]
m = onnx.load(src, load_external_data=False)
g = m.graph
have = {o for n in g.node for o in n.output}
names = ["/model/graph_inputs/inputs_embeds/Cast/output_0"]
names += [f"/model/layers.{l}/input_layernorm/output_3" for l in range(1, 24)]
names += ["/model/layers.24/final_norm_layernorm/output_0"]
missing = [n for n in names if n not in have]
assert not missing, missing
axes = "/inside/axes0"
g.initializer.append(helper.make_tensor(axes, TensorProto.INT64, [1], [0]))
parts = []
for i, n in enumerate(names):
    out = f"/inside/unsq_{i}"
    g.node.append(helper.make_node("Unsqueeze", [n, axes], [out], name=f"/inside/Unsqueeze_{i}"))
    parts.append(out)
g.node.append(helper.make_node("Concat", parts, ["hidden_states"], name="/inside/Concat", axis=0))
g.output.append(helper.make_tensor_value_info("hidden_states", TensorProto.FLOAT16, [25, "batch_size", "sequence_length", 1024]))
# a push: graph input `steer` [batch, seq, 1024] fp32, added to the residual stream entering layer STEER_LAYER (zeros
# leave every output bit-identical). It enters through the skip input of that layer's SkipLayerNorm, whose output_3 is
# the residual itself, so hidden_states[STEER_LAYER] shows the pushed state.
STEER_LAYER = 20
skip = f"/model/layers.{STEER_LAYER - 1}/mlp/down_proj/MatMul/output_0"
assert skip in have, skip
g.input.append(helper.make_tensor_value_info("steer", TensorProto.FLOAT, ["batch_size", "sequence_length", 1024]))
g.node.append(helper.make_node("Cast", ["steer"], ["/inside/steer16"], name="/inside/SteerCast", to=TensorProto.FLOAT16))
g.node.append(helper.make_node("Add", [skip, "/inside/steer16"], ["/inside/steered"], name="/inside/SteerAdd"))
users = [n for n in g.node if skip in n.input and n.name != "/inside/SteerAdd"]
assert len(users) >= 1, users
for n in users:
    for k, x in enumerate(n.input):
        if x == skip:
            n.input[k] = "/inside/steered"
print("steer enters layer", STEER_LAYER, "via", [n.name for n in users])
onnx.save(m, dst)  # external data stays where it was: the base's decoder_model_merged_fp16.onnx_data
print("wrote", dst, "with output hidden_states from", len(names), "tensors")

# the logit lens: final RMSNorm weight and the lm_head rows of every answer character, read from the deployed ONNX
# weights themselves (the base's external data), so the page's lens uses exactly the numbers the device runs
from onnx import numpy_helper
from transformers import AutoTokenizer

base_dir = sys.argv[4]  # the folder that holds decoder_model_merged_fp16.onnx_data
init = {t.name: t for t in g.initializer}


def weight(name):
    t = init[name]
    if t.data_location != onnx.TensorProto.EXTERNAL:
        return numpy_helper.to_array(t).astype(np.float32)
    # read the bytes ourselves: the served data files are hard links, which onnx's loader refuses
    info = {e.key: e.value for e in t.external_data}
    dt = {TensorProto.FLOAT16: np.float16, TensorProto.FLOAT: np.float32}[t.data_type]
    n = int(np.prod(t.dims))
    with open(f"{base_dir}/{info['location']}", "rb") as f:
        f.seek(int(info.get("offset", 0)))
        a = np.frombuffer(f.read(n * np.dtype(dt).itemsize), dtype=dt)
    return a.reshape(tuple(t.dims)).astype(np.float32)


norm_w = weight("model.layers.24.final_norm_layernorm.weight")
head = weight("lm_head.MatMul.weight")  # [1024, vocab]
tok = AutoTokenizer.from_pretrained(hf)
chars = "0123456789" + "_-MAZFNH" + "abcdefghij"
ids = []
for c in chars:
    t = tok.encode(c, add_special_tokens=False)
    assert len(t) == 1, (c, t)
    ids.append(t[0])
cfg = json.load(open(f"{hf}/config.json"))
eps = cfg.get("text_config", cfg).get("rms_norm_eps", 1e-6)
rows = head[:, ids].T  # [chars, 1024]
blob = np.concatenate([norm_w.ravel(), rows.ravel()]).astype(np.float32)
out = dst.rsplit("/", 1)[0] + "/lens.bin"
blob.tofile(out)
json.dump({"chars": chars, "ids": ids, "eps": eps, "dim": int(norm_w.shape[0])}, open(out.replace(".bin", ".json"), "w"))
print("wrote", out, blob.nbytes, "bytes; final norm weight mean", float(norm_w.mean()))
