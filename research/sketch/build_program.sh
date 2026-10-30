#!/bin/zsh
# Build a sketchpad program folder from a PEFT adapter, $0 on the M4:
#   1. inject the adapter into the base fp16 decoder graph (patch_onnx_lora.py)
#   2. give the graph its window into itself: hidden_states out, steer in, lens data (patch_onnx_inside.py)
#   3. the states of all 1,795 table rows (inside_atlas.py), then the page's map and lens data (inside_assets.py)
#   4. the SUM push at layer 20 on the server, to check the map's push still lands (inside_steer.py)
# usage: build_program.sh <adapter dir> <program id>
set -e
A=${1:a}
ID=$2
cd ${0:a:h}
M=/Users/neo/repos/polyformer-wt/sketchpad/static/sketchpad/models
BASE_ONNX=/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b-onnx/onnx/decoder_model_merged_fp16.onnx
HF=/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b
P=$M/$ID
TMP=$(mktemp -d)
STATES=$TMP/atlas_states.npy
ONNX=(uv run --no-project --python 3.12 --with onnx --with numpy --with safetensors)
TORCH=(uv run --no-project --python 3.12 --with "transformers>=5.12" --with torch --with torchvision --with pillow --with peft --with matplotlib)
mkdir -p $P/onnx
echo "== lora -> $TMP/lora.onnx"
nice -n 19 $ONNX python patch_onnx_lora.py $A $BASE_ONNX $TMP/decoder_model_merged_fp16.onnx 2>&1 | tail -2
echo "== inside -> $P/onnx"
nice -n 19 $ONNX --with "transformers>=5.12" python patch_onnx_inside.py $TMP/decoder_model_merged_fp16.onnx \
	$P/onnx/decoder_model_merged_fp16.onnx $HF $M/base/onnx 2>&1 | grep -v Warning | tail -3
echo "== atlas (atlas.json in this folder is rewritten; the previous one is kept as atlas_prev.json)"
[ -f atlas.json ] && cp atlas.json atlas_prev.json
nice -n 19 $TORCH python inside_atlas.py $A $STATES 2>&1 | tail -2
echo "== assets"
nice -n 19 uv run --no-project --python 3.12 --with numpy python inside_assets.py $STATES $P/onnx/lens.bin $P | tail -3
echo "== push at layer 20 (SUM)"
nice -n 19 $TORCH python inside_steer.py $A $STATES digit 20 2>&1 | grep steered
cp atlas.json atlas_$ID.json
/bin/ls -la $P $P/onnx
