"""Status of the spawned audit reruns: done (with return code and wall) or still running; never blocks."""
import json, pathlib, modal
calls = json.loads((pathlib.Path(__file__).parent / "calls.json").read_text())
for job, c in calls.items():
    try:
        r = modal.FunctionCall.from_id(c["call_id"]).get(timeout=0)
        print(job, "DONE rc", r["returncode"], "wall", r["wall"], "files", len(r["written"]))
    except TimeoutError:
        print(job, "running")
    except Exception as e:
        print(job, "ERROR", type(e).__name__, str(e)[:200])
