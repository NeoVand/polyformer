"""Bounded, single-run Modal entry point for export_a5_irrep.py."""

import json
import pathlib

import modal

root = pathlib.Path(__file__).resolve().parent
app = modal.App("polyformer-a5-export")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("jax[cuda12]", "optax", "numpy")
    .add_local_file(root / "polybench.py", "/root/polybench.py")
    .add_local_file(root / "groups.py", "/root/groups.py")
    .add_local_file(root / "export_a5_irrep.py", "/root/export_a5_irrep.py")
)


@app.function(image=image, gpu="L4", timeout=20 * 60)
def train():
    from export_a5_irrep import run
    return run()


@app.local_entrypoint()
def main():
    result = train.remote()
    out = root.parent / "static/recorded/a5-irrep.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"path": str(out), "head": result["selectedHead"],
                      "homomorphism_error": result["homomorphismError"],
                      "balanced_accuracy": result["training"]["result"]["bal_acc"]}))
