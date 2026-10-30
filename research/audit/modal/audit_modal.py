"""Audit reruns (research/audit/RERUNS.md) on Modal, from clean `git archive` exports of the record commits.

Each domain's export (plus its gitignored data file, sha256 checked against the registration) is baked into the image
at deploy time. A job copies its export to a scratch directory, runs one registered command there, and writes every
file the run created or changed, plus the full log, to the volume `polyformer-audit` under /<job id>/.

  uvx --with modal==<v> modal deploy audit_modal.py      # then: python launch.py (spawns, writes call ids, exits)
"""
import os
import pathlib
import shutil
import subprocess
import time

import modal

HERE = pathlib.Path(__file__).parent
APP = "polyformer-audit"
vol = modal.Volume.from_name("polyformer-audit", create_if_missing=True)
app = modal.App(APP)

jax_cpu = (modal.Image.debian_slim(python_version="3.12")
           .pip_install("jax[cpu]==0.12.0", "optax==0.2.8", "numpy==2.5.4")
           .add_local_dir(HERE / "code", "/src/code").add_local_dir(HERE / "arith", "/src/arith"))
jax_gpu = (modal.Image.debian_slim(python_version="3.12")
           .pip_install("jax[cuda12]==0.12.0", "optax==0.2.8", "numpy==2.5.4")
           .add_local_dir(HERE / "lean", "/src/lean"))
torch_l4 = (modal.Image.debian_slim(python_version="3.12")
            .pip_install("torch==2.5.1", "transformers==4.46.3", "numpy==1.26.4", "huggingface_hub==0.26.2", "accelerate==1.1.1")
            .add_local_dir(HERE / "stories", "/src/stories"))


def _run(job_id, tree, argv):
    work = pathlib.Path("/tmp/work")
    shutil.copytree(f"/src/{tree}", work)
    before = {p: p.stat().st_mtime for p in work.rglob("*") if p.is_file()}
    out = pathlib.Path("/vol") / job_id
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with open(out / "run.log", "w") as log:
        log.write(f"job {job_id}; tree {tree}; argv {argv}; start {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.flush()
        rc = subprocess.run(["python", *argv], cwd=work, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "PYTHONUNBUFFERED": "1"}).returncode
        log.write(f"\nreturncode {rc}; wall {time.time() - t0:.1f}s\n")
    written = []
    for p in work.rglob("*"):
        if p.is_file() and (p not in before or p.stat().st_mtime != before[p]):
            dst = out / "files" / p.relative_to(work)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            written.append(str(p.relative_to(work)))
    (out / "written.txt").write_text("\n".join(written) + "\n")
    vol.commit()
    return {"job": job_id, "returncode": rc, "wall": round(time.time() - t0, 1), "written": written}


@app.function(image=jax_cpu, cpu=(8.0, 16.0), memory=(4096, 32 * 1024), timeout=7300, volumes={"/vol": vol}, retries=0)
def run_cpu_long(job_id: str, tree: str, argv: list):
    return _run(job_id, tree, argv)


@app.function(image=jax_cpu, cpu=(8.0, 16.0), memory=(4096, 32 * 1024), timeout=2400, volumes={"/vol": vol}, retries=0)
def run_cpu_short(job_id: str, tree: str, argv: list):
    return _run(job_id, tree, argv)


@app.function(image=jax_gpu, gpu="H100", cpu=(2.0, 8.0), memory=(4096, 32 * 1024), timeout=1800, volumes={"/vol": vol}, retries=0)
def run_h100(job_id: str, tree: str, argv: list):
    return _run(job_id, tree, argv)


@app.function(image=torch_l4, gpu="L4", cpu=2.0, memory=16 * 1024, timeout=2400, volumes={"/vol": vol}, retries=0)
def run_l4(job_id: str, tree: str, argv: list):
    return _run(job_id, tree, argv)
