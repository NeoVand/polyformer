"""Spawn CHAT jobs on the deployed Modal app polyformer-chat, record the call ids in calls.json, and exit.

  uvx --with modal python launch.py gate [shards=8] [k] # T5 identity test (gate_identity.py), CPU
  uvx --with modal python launch.py status              # poll recorded calls
"""
import json
import pathlib
import sys
import time

import modal

APP = "polyformer-chat"
CALLS = pathlib.Path(__file__).parent / "calls.json"


def record(job, call, cmds):
    calls = json.loads(CALLS.read_text()) if CALLS.exists() else {}
    calls[job] = {"call_id": call.object_id, "cmds": cmds, "spawned": time.strftime("%Y-%m-%d %H:%M:%S %Z")}
    CALLS.write_text(json.dumps(calls, indent=1) + "\n")
    print(job, call.object_id, flush=True)


def spawn(fn, job, cmds):
    record(job, modal.Function.from_name(APP, fn).spawn(job, cmds), cmds)


def main(argv):
    if argv[0] == "gate":  # gate [shards=8] [only shard k]: `gate 100 0` is a smoke run (1 prompt, 18 rows)
        n = int(argv[1]) if len(argv) > 1 else 8
        stamp = time.strftime("%H%M")
        for k in ([int(argv[2])] if len(argv) > 2 else range(n)):
            spawn("run_cpu", f"gate_{stamp}_{k}", [["python", "chat/gate_identity.py", "/vol/onnx", str(k), str(n)]])
    elif argv[0] == "status":
        calls = json.loads(CALLS.read_text())
        for job, c in calls.items():
            if len(argv) > 1 and not job.startswith(argv[1]):
                continue
            try:
                res = modal.FunctionCall.from_id(c["call_id"]).get(timeout=0)
                print(job, "DONE", json.dumps(res)[:300])
            except TimeoutError:
                print(job, "running since", c["spawned"])
            except Exception as e:  # noqa: BLE001
                print(job, "ERROR", repr(e)[:300])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
