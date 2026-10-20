"""Bounded, resumable Modal orchestration for BEYOND.md; importing this never launches work.

Prepare a JSON list of jobs, each with ``script``, ``argv``, ``gpu`` (CPU, L4 or H100),
and ``max_seconds``. ``script`` is a research/*.py basename. Then:

    python research/beyond_modal.py plan --name timing --stage development --jobs /tmp/jobs.json
    uvx modal run research/beyond_modal.py::run --manifest research/manifests/timing.json
    python research/beyond_modal.py status

Predictions in BEYOND.md must be committed before planning. A manifest records that
commit, all Python source digests, the exact arguments and conservative reservations.
Results and call IDs are durable; re-running a manifest retrieves existing calls.
No retries are automatic. A new, explicitly numbered attempt is a new experiment.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import pathlib
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
MANIFESTS = ROOT / "manifests"
LEDGER = ROOT / "results" / "beyond_budget.json"
LOCK = ROOT / "results" / "beyond_budget.lock"
CAPS = {"development": 25.0, "screen": 25.0, "language": 100.0}
TOTAL_CAP = 150.0
# Published serverless rates, checked 2026-10-20: https://modal.com/pricing.
# CPU and RAM tuples below impose hard limits; use their maxima in reservations.
GPU_RATES = {"CPU": 0.0, "L4": 0.000222, "H100": 0.001097}
CPU_RATE = 0.0000131
RAM_RATE = 0.00000222
CPU_MAX = 4
RAM_GIB_MAX = 32
STARTUP_SECONDS = 120
WRAPPER_SECONDS = 30
IDLE_SECONDS = 2
MAX_CONCURRENCY = 8
VERSIONS = {"jax": "0.12.0", "optax": "0.2.8", "numpy": "2.5.4"}


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def sources():
    return {p.name: digest(p.read_bytes()) for p in sorted(ROOT.glob("*.py"))}


def rate(gpu):
    return GPU_RATES[gpu] + CPU_MAX * CPU_RATE + RAM_GIB_MAX * RAM_RATE


def reservation(job):
    return round(rate(job["gpu"]) * (job["max_seconds"] + WRAPPER_SECONDS + STARTUP_SECONDS + IDLE_SECONDS), 6)


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


@contextlib.contextmanager
def locked_ledger():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {
            "schema": 1, "caps": CAPS, "total_cap": TOTAL_CAP, "jobs": {},
            "cost_basis": "upper-resource-rate estimate; not an invoice; unresolved calls retain full reservation",
            "pricing_url": "https://modal.com/pricing",
        }
        yield ledger
        atomic_json(LEDGER, ledger)
        fcntl.flock(lock, fcntl.LOCK_UN)


def totals(ledger):
    out = {stage: 0.0 for stage in CAPS}
    for entry in ledger["jobs"].values():
        out[entry["stage"]] += entry.get("settled_usd", entry["reserved_usd"])
    return {**{k: round(v, 6) for k, v in out.items()}, "total": round(sum(out.values()), 6)}


def normalize_job(raw, source_hashes):
    job = dict(raw)
    job.setdefault("script", "beyond_diag.py")
    job.setdefault("gpu", "L4")
    job.setdefault("max_seconds", 900)
    job.setdefault("attempt", 0)
    if job["script"] not in source_hashes or pathlib.Path(job["script"]).name != job["script"]:
        raise ValueError(f"script must name a current research Python source: {job['script']!r}")
    if not isinstance(job.get("argv"), list) or not all(isinstance(a, str) for a in job["argv"]):
        raise ValueError("argv must be a list of strings")
    if job["gpu"] not in GPU_RATES:
        raise ValueError("gpu must be CPU, L4 or H100")
    if not isinstance(job["max_seconds"], int) or not 1 <= job["max_seconds"] <= 7200:
        raise ValueError("max_seconds must be an integer in [1, 7200]")
    if not isinstance(job["attempt"], int) or job["attempt"] < 0:
        raise ValueError("attempt must be a nonnegative integer")
    # Time limits do not change experiment identity. A timeout is never retried by
    # silently increasing its timeout; an explicit attempt increment is required.
    identity = {k: job[k] for k in ("script", "argv", "gpu", "attempt")}
    identity["source_hashes"] = source_hashes
    job["id"] = digest(identity)[:24]
    job["reserved_usd"] = reservation(job)
    return job


def plan(name, stage, jobs_path):
    if not name or pathlib.Path(name).name != name or not all(c.isalnum() or c in "_-" for c in name):
        raise ValueError("name must contain only letters, digits, underscores or hyphens")
    prediction_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    committed = subprocess.check_output(["git", "show", f"{prediction_commit}:research/BEYOND.md"], cwd=ROOT)
    if committed != (ROOT / "BEYOND.md").read_bytes():
        raise ValueError("Commit BEYOND.md predictions before creating the manifest")
    source_hashes = sources()
    raw = json.loads(pathlib.Path(jobs_path).read_text())
    if not isinstance(raw, list) or not raw:
        raise ValueError("jobs file must contain a nonempty JSON list")
    jobs = [normalize_job(j, source_hashes) for j in raw]
    if len({j["id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate experiments in manifest")
    path = MANIFESTS / f"{name}.json"
    if path.exists():
        raise ValueError(f"immutable manifest already exists: {path}")
    manifest = {
        "schema": 1, "name": name, "stage": stage, "created": stamp(),
        "prediction_commit": prediction_commit, "prediction_sha256": digest(committed),
        "source_hashes": source_hashes, "runtime_versions": VERSIONS, "jobs": jobs,
        "resources": {"cpu_request": 2, "cpu_limit": CPU_MAX, "ram_request_mib": 8192,
                      "ram_limit_mib": RAM_GIB_MAX * 1024, "max_concurrency": MAX_CONCURRENCY,
                      "startup_timeout_seconds": STARTUP_SECONDS, "scaledown_seconds": IDLE_SECONDS},
        "max_reserved_usd": round(sum(j["reserved_usd"] for j in jobs), 6),
        "pricing_url": "https://modal.com/pricing",
    }
    manifest["sha256"] = digest(manifest)
    atomic_json(path, manifest)
    print(json.dumps({"manifest": str(path), "jobs": len(jobs), "max_reserved_usd": manifest["max_reserved_usd"],
                      "stage": stage, "note": "Planning does not launch jobs or reserve budget."}, indent=2))
    return path


def read_manifest(path):
    manifest = json.loads(pathlib.Path(path).read_text())
    expected = manifest.pop("sha256")
    if digest(manifest) != expected:
        raise ValueError("manifest was modified after planning")
    manifest["sha256"] = expected
    if manifest["stage"] not in CAPS:
        raise ValueError("unknown budget stage")
    if manifest["runtime_versions"] != VERSIONS:
        raise ValueError("manifest runtime differs from runner")
    for job in manifest["jobs"]:
        if normalize_job(job, manifest["source_hashes"]) != job:
            raise ValueError("manifest job identity or reservation mismatch")
    return manifest


def reserve(manifest, job):
    with locked_ledger() as ledger:
        if job["id"] in ledger["jobs"]:
            return ledger["jobs"][job["id"]], False
        active = sum(e["status"] in ("reserved", "running") for e in ledger["jobs"].values())
        if active >= MAX_CONCURRENCY:
            raise RuntimeError("global eight-job concurrency cap reached; resume this manifest after active calls settle")
        used = totals(ledger)
        amount, stage = job["reserved_usd"], manifest["stage"]
        if used[stage] + amount > CAPS[stage] or used["total"] + amount > TOTAL_CAP:
            raise RuntimeError(f"budget reservation refused: used={used}, next={amount:.4f}, stage={stage}")
        entry = {"id": job["id"], "stage": stage, "manifest": manifest["name"],
                 "manifest_sha256": manifest["sha256"], "reserved_usd": amount,
                 "status": "reserved", "reserved_at": stamp(), "gpu": job["gpu"]}
        ledger["jobs"][job["id"]] = entry
        return entry, True


def record_call(job_id, call_id):
    with locked_ledger() as ledger:
        ledger["jobs"][job_id].update({"call_id": call_id, "status": "running", "launched_at": stamp()})


def settle(job, result, manifest):
    # Result files precede ledger settlement, making interruption after write safe.
    path = ROOT / "results" / "beyond_runs" / f"{job['id']}.json"
    result.update({"job_id": job["id"], "manifest": manifest["name"],
                   "manifest_sha256": manifest["sha256"], "stage": manifest["stage"],
                   "argv": job["argv"], "script": job["script"], "gpu_requested": job["gpu"],
                   "prediction_commit": manifest["prediction_commit"], "source_hashes": manifest["source_hashes"]})
    # Diverged models can emit NaN, which is not JSON. Preserve an explicit
    # numerical-failure annotation while keeping artifacts machine readable.
    def clean(value, path=""):
        if isinstance(value, float) and not math.isfinite(value):
            nonfinite.append(path)
            return None
        if isinstance(value, dict):
            return {k: clean(v, f"{path}.{k}") for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v, f"{path}[{i}]") for i, v in enumerate(value)]
        return value

    nonfinite = []
    result = clean(result)
    if nonfinite:
        result["nonfinite_fields"] = nonfinite
    atomic_json(path, result)
    # Successful measured wall time includes interpreter/compilation/evaluation.
    # Keep full reservation for infrastructure failures with no trustworthy wall.
    amount = job["reserved_usd"]
    if "wall" in result:
        amount = min(amount, round(rate(job["gpu"]) *
                                  (result["wall"] + WRAPPER_SECONDS + STARTUP_SECONDS + IDLE_SECONDS), 6))
    with locked_ledger() as ledger:
        entry = ledger["jobs"][job["id"]]
        entry.update({"status": "error" if result.get("error") else "complete", "settled_usd": amount,
                      "settled_at": stamp(), "result_file": str(path.relative_to(ROOT))})
    return result


def worker(job, expected_sources):
    """Only called inside Modal. The subprocess has its own strict wall timeout."""
    started = time.monotonic()
    remote_root = pathlib.Path("/root/research")
    actual = {p.name: digest(p.read_bytes()) for p in sorted(remote_root.glob("*.py"))}
    if actual != expected_sources:
        return {"error": "remote source hash mismatch", "wall": round(time.monotonic() - started, 3)}
    log_dir = pathlib.Path("/runs") / job["id"]
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path, stderr_path = log_dir / "stdout.log", log_dir / "stderr.log"
    command = [sys.executable, "-u", str(remote_root / job["script"]), *job["argv"]]
    timed_out = False
    with stdout_path.open("w") as fout, stderr_path.open("w") as ferr:
        process = subprocess.Popen(command, cwd=remote_root, stdout=fout, stderr=ferr,
                                   text=True, start_new_session=True)
        deadline, last_commit, offsets = time.monotonic() + job["max_seconds"], 0.0, [0, 0]
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                break
            try:
                process.wait(timeout=min(10, remaining))
            except subprocess.TimeoutExpired:
                pass
            for i, path in enumerate((stdout_path, stderr_path)):
                with path.open() as f:
                    f.seek(offsets[i])
                    new = f.read()
                    offsets[i] = f.tell()
                if new:
                    print(f"[{job['id']} {'stdout' if i == 0 else 'stderr'}] {new}", flush=True)
            if time.monotonic() - last_commit >= 30:
                runs_volume.commit()
                last_commit = time.monotonic()
    stdout, stderr = stdout_path.read_text(), stderr_path.read_text()
    rows = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
        except (ValueError, TypeError):
            pass
    result = rows[-1] if rows and process.returncode == 0 else {}
    if timed_out:
        result["error"] = f"subprocess exceeded {job['max_seconds']} seconds"
    elif process.returncode != 0:
        result["error"] = f"subprocess exit {process.returncode}: {(stderr or stdout)[-6000:]}"
    elif not rows:
        result["error"] = f"no JSON result: {(stderr or stdout)[-6000:]}"
    result["wall"] = round(time.monotonic() - started, 3)
    result["stdout_tail"] = stdout[-12000:]
    result["stderr_tail"] = stderr[-6000:]
    result["python_version"] = sys.version.split()[0]
    result["installed_versions"] = {name: importlib.metadata.version(name) for name in VERSIONS}
    result["remote_completed_at"] = stamp()
    result["log_volume"] = "polyformer-beyond-runs"
    result["log_directory"] = job["id"]
    if job["gpu"] != "CPU":
        try:
            result["gpu_actual"] = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True, timeout=5).strip()
        except Exception:
            result["gpu_actual"] = "unknown"
    # Keep the raw JSON remotely as well, even if the local client is interrupted.
    (log_dir / "result.json").write_text(json.dumps(result) + "\n")
    runs_volume.commit()
    return result


try:
    import modal
except ImportError:
    modal = None

if modal is not None:
    app = modal.App("polyformer-beyond")
    image = (modal.Image.debian_slim(python_version="3.12")
             .pip_install("jax[cuda12]==0.12.0", "optax==0.2.8", "numpy==2.5.4"))
    for source in sorted(ROOT.glob("*.py")):
        image = image.add_local_file(source, f"/root/research/{source.name}")
    data_volume = modal.Volume.from_name("polyformer-data", create_if_missing=False)
    runs_volume = modal.Volume.from_name("polyformer-beyond-runs", create_if_missing=True)

    @app.function(image=image, volumes={"/data": data_volume, "/runs": runs_volume}, cpu=(2, CPU_MAX),
                  memory=(8192, RAM_GIB_MAX * 1024), max_containers=MAX_CONCURRENCY,
                  min_containers=0, buffer_containers=0, scaledown_window=IDLE_SECONDS,
                  timeout=930, startup_timeout=STARTUP_SECONDS, retries=0)
    def execute(job, expected_sources):
        return worker(job, expected_sources)

    @app.local_entrypoint()
    def run(manifest: str, concurrency: int = 8):
        """Launch or resume an immutable manifest; budget is reserved before every spawn."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        spec = read_manifest(manifest)
        if not 1 <= concurrency <= MAX_CONCURRENCY:
            raise ValueError(f"concurrency must be in [1, {MAX_CONCURRENCY}]")
        pending = []
        with locked_ledger() as ledger:
            known = dict(ledger["jobs"])
        # Existing calls can be retrieved after sources change. New calls cannot.
        if any(j["id"] not in known for j in spec["jobs"]) and sources() != spec["source_hashes"]:
            raise ValueError("sources changed since planning; create a new committed manifest")
        for job in spec["jobs"]:
            entry = known.get(job["id"])
            if entry and entry["status"] in ("complete", "error"):
                print(json.dumps({"job_id": job["id"], "status": "already_" + entry["status"]}))
            elif entry and not entry.get("call_id"):
                raise RuntimeError(f"unresolved reservation {job['id']} has no call ID; reconcile before proceeding")
            else:
                pending.append(job)

        def perform(job):
            entry, created = reserve(spec, job)
            if not created and not entry.get("call_id"):
                raise RuntimeError(f"another launcher owns unresolved reservation {job['id']}")
            try:
                if entry.get("call_id"):
                    call = modal.FunctionCall.from_id(entry["call_id"])
                else:
                    fn = execute.with_options(gpu=None if job["gpu"] == "CPU" else job["gpu"],
                                              timeout=job["max_seconds"] + WRAPPER_SECONDS,
                                              max_containers=concurrency)
                    call = fn.spawn(job, spec["source_hashes"])
                    record_call(job["id"], call.object_id)
                result = call.get()
            except Exception as exc:
                # Unknown dispatch/connection outcomes remain resumable and keep
                # their reservation. They must never trigger duplicate dispatch.
                if not isinstance(exc, (modal.exception.FunctionTimeoutError, modal.exception.UserCodeException)):
                    print(json.dumps({"job_id": job["id"], "status": "unresolved",
                                      "error": f"{type(exc).__name__}: {str(exc)[-3000:]}"}), flush=True)
                    return None
                result = {"error": f"Modal {type(exc).__name__}: {str(exc)[-3000:]}"}
            result = settle(job, result, spec)
            brief = {k: result.get(k) for k in
                     ("job_id", "task", "model", "arch", "seed", "val_big", "tok_acc", "wall", "error")}
            print(json.dumps(brief), flush=True)
            return result

        # The scheduler launches at most concurrency jobs at a time. Reservation
        # checks are serialized across threads and independent runner processes.
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(perform, job) for job in pending]
            for future in as_completed(futures):
                try:
                    future.result()
                except RuntimeError as exc:
                    print(json.dumps({"not_launched": str(exc)}), flush=True)
        status()


def status():
    with locked_ledger() as ledger:
        used = totals(ledger)
        counts = {}
        for entry in ledger["jobs"].values():
            counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    print(json.dumps({"conservative_usd": used, "caps_usd": {**CAPS, "total": TOTAL_CAP},
                      "jobs": counts, "note": "Conservative resource estimates, not a billing invoice."}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("plan", help="write an immutable preregistered job manifest; no spend")
    make.add_argument("--name", required=True)
    make.add_argument("--stage", choices=CAPS, required=True)
    make.add_argument("--jobs", required=True)
    commands.add_parser("status", help="show charged estimates and outstanding reservations")
    args = parser.parse_args()
    if args.command == "plan":
        plan(args.name, args.stage, args.jobs)
    else:
        status()


if __name__ == "__main__":
    main()
