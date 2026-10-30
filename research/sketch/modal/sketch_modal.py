"""Sketchpad training on Modal (Neo, 29 Oct 2026: "go ahead and use a modal").

The sketch scripts (research/sketch/*.py) are mounted unchanged and patched in a scratch copy inside the container:
the device "mps" becomes "cuda", and the model snapshot, the Menlo font and PRIMER.md are placed at the paths the
scripts hard-code, so a run here is the same code and the same weights as a run on the M4. One job = a list of
commands run in order in the scratch copy; every file a job writes or changes, plus the full log, is copied to the
volume `polyformer-sketch` under /runs/<job id>/.

  uvx --with modal modal volume put polyformer-sketch <local qwen3.5-0.8b dir> /model     # once
  uvx --with modal modal deploy research/sketch/modal/sketch_modal.py
  uvx --with modal python research/sketch/modal/launch.py e4 <seed> [steps] [kl]        # spawn and exit
  uvx --with modal modal volume get polyformer-sketch runs/<job> research/sketch/modal/out/<job>
"""
import os
import pathlib
import shutil
import tempfile
import subprocess
import time

import modal

HERE = pathlib.Path(__file__).parent
SKETCH = HERE.parent
APP = "polyformer-sketch"
MODEL_PATH = "/Users/neo/repos/polyformer-wt/models/qwen3.5-0.8b"  # as hard-coded in e2_column.py
vol = modal.Volume.from_name("polyformer-sketch", create_if_missing=True)
app = modal.App(APP)

base = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch==2.14.0", "torchvision", "transformers==5.17.0", "peft", "pillow", "accelerate", "safetensors")
# Faster variant: Triton kernels for the gated delta rule (transformers otherwise falls back to slow reference
# PyTorch; the reference path cost 54 min per 1,000 E4 steps). Numerics differ from the reference at float32 rounding
# level, so any certificate is re-run on the deployment numerics anyway. Smoke-test first: python launch.py smoke fast
base_fast = base.pip_install("flash-linear-attention")


def _mount(img):
    """Local files last, so a file change never rebuilds the pip layers."""
    return (img.add_local_dir(SKETCH, "/src/sketch",
                              ignore=["**/*.png", "**/*.pt", "**/*.safetensors", "e3_browser/**", "e0/**", "modal/**"])
            .add_local_file("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Menlo.ttc")
            .add_local_file(SKETCH.parent / "PRIMER.md", "/Users/neo/repos/polyformer/research/PRIMER.md"))


image = _mount(base)
image_fast = _mount(base_fast)


# Patches applied to the scratch copy only (file, old, new). The scripts in research/sketch are never edited.
PATCHES = [
    ("e2_column.py", 'dev = "mps"', 'dev = "cuda"'),
    # orchestrator, 29 Oct: evaluate 20 products at 4x4, 10 at 6x6, 5 at 10x10 instead of the M4 defaults
    ("e4_train.py", "for n, k in ((4, 10), (6, 5), (10, 2)):", "for n, k in ((4, 20), (6, 10), (10, 5)):"),
]


def _run(job_id: str, cmds: list):
    # a fresh scratch copy per job, under its own name: Modal reuses warm containers, and a second job in the same
    # container found the first one's /tmp/work (FileExistsError, 30 Oct)
    work = pathlib.Path(tempfile.mkdtemp(prefix="work-")) / "sketch"
    shutil.copytree("/src/sketch", work)
    patched = []
    for fname, old, new in PATCHES:
        f = work / fname
        if f.exists() and old in f.read_text():
            f.write_text(f.read_text().replace(old, new))
            patched.append(f"{fname}: {old!r} -> {new!r}")
        else:
            patched.append(f"{fname}: PATCH NOT APPLIED ({old!r} not found)")
    link = pathlib.Path(MODEL_PATH)
    link.parent.mkdir(parents=True, exist_ok=True)
    if not link.exists():
        link.symlink_to("/vol/model")
    before = {p: p.stat().st_mtime for p in work.rglob("*") if p.is_file()}
    out = pathlib.Path("/vol/runs") / job_id
    out.mkdir(parents=True, exist_ok=True)
    t0, rcs = time.time(), []

    def sync():
        """Copy every file the job has written or changed so far to the volume (after each command, not only at
        the end: a later command hitting the timeout must not lose an adapter the earlier one saved)."""
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

    # A volume shows a file to other readers only after a commit, so commit the log every two minutes while a command
    # runs; otherwise nothing of a long job is visible until it ends.
    import threading
    stop = threading.Event()

    def heartbeat():
        while not stop.wait(120):
            try:
                vol.commit()
            except Exception:  # noqa: BLE001
                pass

    threading.Thread(target=heartbeat, daemon=True).start()

    with open(out / "run.log", "w") as log:
        log.write(f"job {job_id}; start {time.strftime('%Y-%m-%d %H:%M:%S')}; cmds {cmds}\n")
        log.write("patches:\n  " + "\n  ".join(patched) + "\n")
        log.flush()
        for cmd in cmds:
            log.write(f"\n$ {' '.join(cmd)}\n")
            log.flush()
            rc = subprocess.run(cmd, cwd=work, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, "PYTHONUNBUFFERED": "1"}).returncode
            rcs.append(rc)
            log.write(f"\nreturncode {rc}; wall so far {time.time() - t0:.1f}s\n")
            log.flush()
            written = sync()
            if rc:
                break
    stop.set()
    written = sync()
    return {"job": job_id, "returncodes": rcs, "wall": round(time.time() - t0, 1), "written": written}


@app.function(image=image, gpu="H100", cpu=(2.0, 8.0), memory=(16 * 1024, 64 * 1024), timeout=10800,
              volumes={"/vol": vol}, retries=0)
def run_h100(job_id: str, cmds: list):
    return _run(job_id, cmds)


@app.function(image=image, gpu="L4", cpu=(2.0, 8.0), memory=(16 * 1024, 32 * 1024), timeout=5400,
              volumes={"/vol": vol}, retries=0)
def run_l4(job_id: str, cmds: list):
    return _run(job_id, cmds)




@app.function(image=image_fast, gpu="H100", cpu=(2.0, 8.0), memory=(16 * 1024, 64 * 1024), timeout=10800,
              volumes={"/vol": vol}, retries=0)
def run_h100_fast(job_id: str, cmds: list):
    return _run(job_id, cmds)


@app.function(image=image_fast, gpu="H100", timeout=600, volumes={"/vol": vol})
def smoke_fast():
    return _run("smoke_fast", [["python", "-c",
                                "import time, e2_column as e2, json; m=e2.load_base().eval(); t=time.time(); "
                                "ok,mn,_=e2.certify(m); print(json.dumps({'untouched_e2_rows_ok': ok, 'min_margin': mn, "
                                "'ppl': e2.text_ppl(m), 'certify_242_seconds': round(time.time()-t,1)}))"]])


@app.function(image=image, gpu="H100", timeout=600, volumes={"/vol": vol})
def smoke():
    """Load the model on the GPU and certify the untouched E2 domain: proves the image, paths and weights."""
    import json
    return _run("smoke", [["python", "-c",
                           "import e2_column as e2, json; m=e2.load_base().eval(); ok,mn,_=e2.certify(m); "
                           "print(json.dumps({'untouched_e2_rows_ok': ok, 'min_margin': mn, 'ppl': e2.text_ppl(m)}))"]])
