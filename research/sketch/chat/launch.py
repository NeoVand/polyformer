"""Spawn CHAT jobs on the deployed Modal app polyformer-chat, record the call ids in calls.json, and exit.

  uvx --with modal python launch.py gate [shards=8] [k] # T5 identity test (gate_identity.py), CPU
  uvx --with modal python launch.py stock <data>        # stock replies for <data> (a dir under /vol/data)
  uvx --with modal python launch.py eval <data> <adapter|none> <tag> [chat_eval.py flags]
  uvx --with modal python launch.py train <data> <init adapter> <out> [chat_train.py flags] [--then-eval[=parts]]
  uvx --with modal python launch.py status              # poll recorded calls
<data> is a directory on the polyformer-chat volume holding train_full.jsonl, kl.jsonl and heldout_full.jsonl.
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
    elif argv[0] == "stock":
        spawn("run_h100", f"stock_{time.strftime('%H%M')}", [["python", "chat/stock_replies.py", f"/vol/data/{argv[1]}"]])
    elif argv[0] == "eval":
        data, adapter, tag = argv[1:4]
        spawn("run_h100", f"eval_{tag}", [["python", "chat/chat_eval.py", data, adapter, tag] + argv[4:]])
    elif argv[0] == "train":
        data, init, out = argv[1:4]
        rest = [a for a in argv[4:] if not a.startswith("--then-eval")]
        cmds = [["python", "chat/chat_train.py", data, init, out] + rest]
        then = [a for a in argv if a.startswith("--then-eval")]  # --then-eval or --then-eval=core,heldout,...
        if then:
            parts = then[0].split("=", 1)[1:] or []
            tables = ["--tables", rest[rest.index("--tables") + 1]] if "--tables" in rest else []
            cmds.append(["python", "chat/chat_eval.py", data, out, out] + (["--parts", parts[0]] if parts else []) + tables)
        spawn("run_h100", f"train_{out}", cmds)
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
