"""Read and fingerprint existing token files through the Modal control plane.

No Modal App, Function, container, or GPU is created. The files are streamed to
the local process and are never rewritten or retokenized. Example from worktree:

    python research/analysis/beyond_dataset_fingerprint.py \
        --out research/results/beyond_language_planning/dataset.json

Repeat after the study with --compare DATASET.json and a new --out path.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


VOLUME_NAME = "polyformer-data"
DATA_DIRECTORY = "fineweb_edu"
FILES = ("train.bin", "val.bin")


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(data).hexdigest()


def seal(value):
    value = {k: v for k, v in value.items() if k != "sha256"}
    return {**value, "sha256": digest(value)}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def snapshot(volume):
    return {
        entry.path.lstrip("/"): {
            "bytes": int(entry.size),
            "modified_unix": int(entry.mtime),
            "modified_utc": datetime.fromtimestamp(entry.mtime, timezone.utc).isoformat(),
        }
        for entry in volume.iterdir(DATA_DIRECTORY, recursive=False)
        if entry.path.lstrip("/") in {f"{DATA_DIRECTORY}/{name}" for name in FILES}
    }


def stream_hash(chunks):
    hasher, size = hashlib.sha256(), 0
    for chunk in chunks:
        hasher.update(chunk)
        size += len(chunk)
    return {"sha256": hasher.hexdigest(), "bytes": size}


def fingerprint_files(volume):
    before = snapshot(volume)
    expected = {f"{DATA_DIRECTORY}/{name}" for name in FILES}
    if set(before) != expected:
        raise ValueError("volume is missing a required train/validation token file")
    files = {}
    for name in FILES:
        path = f"{DATA_DIRECTORY}/{name}"
        print(f"Hashing {VOLUME_NAME}/{path}: {before[path]['bytes']} bytes", file=sys.stderr, flush=True)
        value = stream_hash(volume.read_file(path))
        if value["bytes"] != before[path]["bytes"] or value["bytes"] % 2:
            raise ValueError(f"download length differs from uint16 file metadata: {path}")
        files[name] = {**before[path], **value, "tokens": value["bytes"] // 2,
                       "volume_path": path, "worker_path": f"/data/{path}"}
        print(f"Finished {path}: {value['sha256']}", file=sys.stderr, flush=True)
    if snapshot(volume) != before:
        raise ValueError("file size/mtime changed during fingerprinting; no evidence written")
    return files


def make_evidence(root, volume, *, modal_version):
    started, clock_start = utc_now(), time.monotonic()
    preparation = root / "modal_run.py"
    preparation_sha = digest(preparation.read_bytes())
    files = fingerprint_files(volume)
    if digest(preparation.read_bytes()) != preparation_sha:
        raise ValueError("preparation code changed during fingerprinting")
    return seal({
        "schema": "beyond_dataset_fingerprint", "schema_version": 1,
        "method": "local control-plane modal.Volume.read_file streaming SHA-256; no Modal Functions",
        "observed_started_utc": started, "observed_completed_utc": utc_now(),
        "elapsed_seconds": round(time.monotonic() - clock_start, 3),
        "volume_name": VOLUME_NAME, "volume_object_id": volume.object_id,
        "worker_data_directory": f"/data/{DATA_DIRECTORY}",
        "storage": {"dtype": "uint16", "bytes_per_token": 2,
                    "byte_order_evidence": "Preparation and reader use native numpy.uint16 on the Linux Modal runtime; no file header."},
        "files": files,
        "metadata_stable_during_read": True,
        "recipe_evidence": {
            "scope": "Current preparation source describes the intended recipe; this does not prove the historical preparation invocation.",
            "preparation_code_path": "research/modal_run.py",
            "preparation_code_sha256": preparation_sha,
            "observed_repository_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
            "huggingface_dataset": "HuggingFaceFW/fineweb-edu",
            "parquet_path": "sample/10BT/000_00000.parquet",
            "split": "Preserve Parquet row order; zero-based document indices divisible by 100 are validation; all others training.",
            "tokenizer": "tiktoken.get_encoding('gpt2'), encode_ordinary_batch; append EOT 50256 to every document.",
            "original_huggingface_revision": None,
            "original_parquet_sha256": None,
            "original_tokenizer_build": None,
            "unknown_reason": "Preparation used an unpinned dataset revision and unpinned packages; the volume contains no preparation metadata sidecar.",
        },
        "sampling_recipe": {
            "training": "numpy.default_rng(run seed); contiguous 513-token windows with replacement produce 512 next-token targets.",
            "tuning_validation_seed": 1234, "final_validation_seed": 5678,
            "validation_scope": "Both samples draw from val.bin; different window draws, not separate document partitions.",
        },
        "fingerprint_runtime": {"python": sys.version, "modal": modal_version,
                                "helper_sha256": digest(Path(__file__).read_bytes())},
        "limitations": [
            "Pins the observed token bytes, not the unrecorded original download revision or tokenizer build.",
            "Pre/post size and mtime agreement is checked; this is not an atomic immutable-volume snapshot.",
            "No per-job remote rehash; repeat this fingerprint after the study and compare both file digests.",
        ],
    })


def compare_files(reference, observed):
    for value in (reference, observed):
        if value.get("sha256") != digest({k: v for k, v in value.items() if k != "sha256"}):
            raise ValueError("dataset evidence checksum mismatch")
    if reference.get("volume_name") != observed.get("volume_name"):
        raise ValueError("comparison names a different data volume")
    for name in FILES:
        for field in ("sha256", "bytes", "tokens", "volume_path"):
            if reference["files"][name][field] != observed["files"][name][field]:
                raise ValueError(f"dataset bytes or identity changed: {name}.{field}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--compare", type=Path, help="optional prior evidence; fail on a changed file fingerprint")
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError(f"refusing to replace existing evidence: {args.out}")
    import modal
    volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=False)
    evidence = make_evidence(args.research_root.resolve(), volume, modal_version=modal.__version__)
    if args.compare:
        reference = json.loads(args.compare.read_text())
        compare_files(reference, evidence)
        evidence = seal({**evidence, "comparison": {"reference_sha256": reference["sha256"], "status": "same_bytes"}})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        stream.write(json.dumps(evidence, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"out": str(args.out), "sha256": evidence["sha256"],
                      "files": evidence["files"]}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
