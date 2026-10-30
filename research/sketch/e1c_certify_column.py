"""E1c: exhaustive certificate of the untouched Qwen3.5-0.8B eye on every 3-digit vertical column crop (1,000 images,
32 px per cell, Menlo), native (3 vision tokens) and upscaled (~70 tokens). Reuses e1b's renderer and reader."""
import itertools, json, sys, time
sys.argv = [sys.argv[0], "0"]
import e1b_fovea as e  # loads the model; N=0 skips its own loop

res, t0 = {}, time.time()
for native in (False, True):
    e.proc.image_processor.size["shortest_edge"] = 32 * 32 if native else e.DEFAULT_MIN
    fails, margins = [], []
    for cells in itertools.product("0123456789", repeat=3):
        ok, m, vt = e.read(e.crop(list(cells), True), "".join(cells), "Read the digits from top to bottom. Reply with the digits only.")
        margins.append(m)
        if not ok:
            fails.append("".join(cells))
    res["native" if native else "upscaled"] = {"rows": 1000, "pass": 1000 - len(fails), "min_margin": min(margins),
                                               "fails": fails[:40], "vision_tokens": vt}
    print(json.dumps(res["native" if native else "upscaled"]), f"({time.time() - t0:.0f}s)", flush=True)
json.dump(res, open("e1c_certify_column.json", "w"), indent=1)
