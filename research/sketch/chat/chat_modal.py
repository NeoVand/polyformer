"""CHAT stream of SKETCHPAD3 (T5 the gate, T4 the chat fine-tune) on Modal: app polyformer-chat.

Volumes: `polyformer-chat` (ours, read/write: /onnx holds the decoder graphs and weights for the gate test, /runs the
jobs' outputs) and `polyformer-sketch` read-only at /sk (the Qwen3.5-0.8B snapshot at /sk/model, the CALC adapters
under /sk/runs). The pattern is research/sketch/modal/sketch_modal.py: research/sketch is mounted unchanged and copied
to a scratch dir per job, where `dev = "mps"` becomes cuda (or cpu) and the hard-coded model, font and PRIMER.md paths
resolve; one job = a list of commands run in order; every file a job writes is copied to /vol/runs/<job id>/ after
each command.

  uvx --with modal modal deploy research/sketch/chat/chat_modal.py
  uvx --with modal python research/sketch/chat/launch.py gate          # T5 identity test, CPU shards
  uvx --with modal modal volume get polyformer-chat runs/<job> research/sketch/chat/out/
"""
import os
import pathlib
import shutil
import subprocess
import tempfile
import threading
import time

import modal

HERE = pathlib.Path(__file__).parent
SKETCH = HERE.parent
MODEL_PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"  # as hard-coded in e2_column.py
vol = modal.Volume.from_name("polyformer-chat", create_if_missing=True)
sk = modal.Volume.from_name("polyformer-sketch").read_only()
app = modal.App("polyformer-chat")

# the sketch app's pip layer first (shared image cache), then ours
base = (modal.Image.debian_slim(python_version="3.12")
        .pip_install("torch==2.14.0", "torchvision", "transformers==5.17.0", "peft", "pillow", "accelerate", "safetensors")
        .pip_install("flash-linear-attention")
        .pip_install("onnxruntime==1.31.1", "datasets")
        .pip_install("lm-eval[ifeval]", "transformers==5.17.0"))  # IFEval's checker
image = (base.add_local_dir(SKETCH, "/src/sketch",
                            ignore=["**/*.png", "**/*.pt", "**/*.safetensors", "**/*.onnx*", "e3_browser/**", "e0/**",
                                    "modal/**", "chat/out/**", "page_shots/**"])
         .add_local_file("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Menlo.ttc")
         .add_local_file(SKETCH.parent / "PRIMER.md", "/Users/neo/repos/polyformer/research/PRIMER.md"))
# CALC's E7 table modules (their files, read from their worktree, never copied into this branch)
for _f in ("e7_calc.py", "calc_tables.py"):
    _p = pathlib.Path("/Users/neo/repos/polyformer-wt/sketchpad/research/sketch") / _f
    if _p.exists():
        image = image.add_local_file(_p, f"/src/calc/{_f}")
VOLS = {"/vol": vol, "/sk": sk}


def _run(job_id: str, cmds: list, dev: str):
    vol.reload()  # a warm container keeps the volume as it was when it started: see files uploaded since
    work = pathlib.Path(tempfile.mkdtemp(prefix="work-")) / "sketch"
    shutil.copytree("/src/sketch", work)
    for f in pathlib.Path("/src/calc").glob("*.py") if pathlib.Path("/src/calc").exists() else []:
        shutil.copy2(f, work / f.name)
    f = work / "e2_column.py"
    f.write_text(f.read_text().replace('dev = "mps"', f'dev = "{dev}"'))
    link = pathlib.Path(MODEL_PATH)
    link.parent.mkdir(parents=True, exist_ok=True)
    if not link.exists():
        link.symlink_to("/sk/model")
    before = {p: p.stat().st_mtime for p in work.rglob("*") if p.is_file()}
    out = pathlib.Path("/vol/runs") / job_id
    out.mkdir(parents=True, exist_ok=True)
    t0, rcs = time.time(), []

    def sync():
        written = []
        for p in work.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts and (p not in before or p.stat().st_mtime != before[p]):
                dst = out / "files" / p.relative_to(work)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                written.append(str(p.relative_to(work)))
        (out / "written.txt").write_text("\n".join(written) + "\n")
        vol.commit()
        return written

    stop = threading.Event()

    def heartbeat():
        while not stop.wait(120):
            try:
                vol.commit()
            except Exception:  # noqa: BLE001
                pass

    threading.Thread(target=heartbeat, daemon=True).start()
    with open(out / "run.log", "w") as log:
        log.write(f"job {job_id}; dev {dev}; start {time.strftime('%Y-%m-%d %H:%M:%S')}; cmds {cmds}\n")
        log.flush()
        for cmd in cmds:
            log.write(f"\n$ {' '.join(cmd)}\n")
            log.flush()
            rc = subprocess.run(cmd, cwd=work, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, "PYTHONUNBUFFERED": "1"}).returncode
            rcs.append(rc)
            log.write(f"\nreturncode {rc}; wall so far {time.time() - t0:.1f}s\n")
            log.flush()
            sync()
            if rc:
                break
    stop.set()
    written = sync()
    return {"job": job_id, "returncodes": rcs, "wall": round(time.time() - t0, 1), "written": written}


@app.function(image=image, cpu=8.0, memory=(24 * 1024, 48 * 1024), timeout=7200, volumes=VOLS, retries=0)
def run_cpu(job_id: str, cmds: list):
    return _run(job_id, cmds, "cpu")


@app.function(image=image, gpu="H100", cpu=(2.0, 8.0), memory=(16 * 1024, 64 * 1024), timeout=10800, volumes=VOLS,
              retries=0)
def run_h100(job_id: str, cmds: list):
    return _run(job_id, cmds, "cuda")
