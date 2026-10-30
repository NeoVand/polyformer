"""Spawn sketchpad jobs on the deployed Modal app polyformer-sketch, record the call ids, and exit (no live client, so
the runs survive the laptop sleeping; see memory note modal-detach-gotcha).

  uvx --with modal python launch.py e4 <seed> [steps=800] [kl=1.0] [gpu=h100|l4]   # train then eval
  uvx --with modal python launch.py smoke                                           # image/paths/weights check
  uvx --with modal python launch.py status                                          # poll recorded calls
"""
import json
import pathlib
import sys
import time

import modal

APP = "polyformer-sketch"
CALLS = pathlib.Path(__file__).parent / "calls.json"


def record(job, call, cmds):
    calls = json.loads(CALLS.read_text()) if CALLS.exists() else {}
    calls[job] = {"call_id": call.object_id, "cmds": cmds, "spawned": time.strftime("%Y-%m-%d %H:%M:%S %Z")}
    CALLS.write_text(json.dumps(calls, indent=1) + "\n")
    print(job, call.object_id, flush=True)


def main(argv):
    if argv[0] == "smoke":
        fn = "smoke_fast" if len(argv) > 1 and argv[1] == "fast" else "smoke"
        call = modal.Function.from_name(APP, fn).spawn()
        record(fn, call, [fn])
    elif argv[0] == "e4":
        seed = argv[1]
        steps = argv[2] if len(argv) > 2 else "800"
        kl = argv[3] if len(argv) > 3 else "1.0"
        gpu = argv[4] if len(argv) > 4 else "h100"  # h100 | l4 | h100_fast
        job = f"e4_s{seed}_{steps}_kl{kl}" + ("_fast" if gpu.endswith("fast") else "")
        cmds = [["python", "e4_train.py", "train", steps, seed, kl],
                ["python", "e4_train.py", "eval", f"e4_adapter_s{seed}"]]
        call = modal.Function.from_name(APP, f"run_{gpu}").spawn(job, cmds)
        record(job, call, cmds)
    elif argv[0] == "e4h":  # e4h <seed> <hinge> [steps] [kl] [gpu]: train() called directly so hinge can be set
        seed, hinge = argv[1], argv[2]
        steps = argv[3] if len(argv) > 3 else "1500"
        kl = argv[4] if len(argv) > 4 else "1.0"
        gpu = argv[5] if len(argv) > 5 else "h100"
        job = f"e4_s{seed}_{steps}_kl{kl}_h{hinge}" + ("_fast" if gpu.endswith("fast") else "")
        cmds = [["python", "-c", f"import e4_train; e4_train.train(steps={int(steps)}, seed={int(seed)}, kl={float(kl)}, hinge={float(hinge)})"],
                ["python", "e4_train.py", "eval", f"e4_adapter_s{seed}"]]
        call = modal.Function.from_name(APP, f"run_{gpu}").spawn(job, cmds)
        record(job, call, cmds)
    elif argv[0] == "e5":  # e5 <seed> [steps=2000] [hinge=4.0] [gpu=h100_fast]: e5_union.py trains then evaluates itself
        seed = argv[1]
        steps = argv[2] if len(argv) > 2 else "2000"
        hinge = argv[3] if len(argv) > 3 else "4.0"
        gpu = argv[4] if len(argv) > 4 else "h100_fast"
        job = f"e5_s{seed}_{steps}_h{hinge}" + ("_fast" if gpu.endswith("fast") else "")
        cmds = [["python", "e5_union.py", "train", steps, seed, hinge]]
        call = modal.Function.from_name(APP, f"run_{gpu}").spawn(job, cmds)
        record(job, call, cmds)
    elif argv[0] == "e5v2":  # e5v2 <seed> [steps=4000] [hinge=4.0] [stop=3.0] [init adapter dir on the volume, e.g. /vol/runs/<job>/files/<adapter>]
        seed = argv[1]
        steps = argv[2] if len(argv) > 2 else "4000"
        hinge = argv[3] if len(argv) > 3 else "4.0"
        stop = argv[4] if len(argv) > 4 else "3.0"
        init = argv[5] if len(argv) > 5 else None
        job = f"e5v2_s{seed}_{steps}_h{hinge}_stop{stop}" + ("_cont" if init else "") + "_fast"
        cmds = [["python", "e5_union.py", "train2", steps, seed, hinge, stop] + ([init] if init else [])]
        call = modal.Function.from_name(APP, "run_h100_fast").spawn(job, cmds)
        record(job, call, cmds)
    elif argv[0] == "e6":  # e6 <seed> <init adapter dir on the volume> [steps=3000] [hinge=4.0] [stop=3.0]: one forward per tick
        seed, init = argv[1], argv[2]
        steps = argv[3] if len(argv) > 3 else "3000"
        hinge = argv[4] if len(argv) > 4 else "4.0"
        stop = argv[5] if len(argv) > 5 else "3.0"
        job = f"e6_s{seed}_{steps}_h{hinge}_stop{stop}_fast"
        cmds = [["python", "e6_slots.py", "train", steps, seed, hinge, stop, init]]
        call = modal.Function.from_name(APP, "run_h100_fast").spawn(job, cmds)
        record(job, call, cmds)
    elif argv[0] == "status":
        calls = json.loads(CALLS.read_text())
        for job, c in calls.items():
            fc = modal.FunctionCall.from_id(c["call_id"])
            try:
                res = fc.get(timeout=0)
                print(job, "DONE", json.dumps(res)[:400])
            except TimeoutError:
                print(job, "running since", c["spawned"])
            except Exception as e:  # noqa: BLE001
                print(job, "ERROR", repr(e)[:300])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
