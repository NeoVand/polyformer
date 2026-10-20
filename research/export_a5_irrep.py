"""Re-run the registered A5 d=3, seed-0 model and export its best learned head.

Local: uv run --no-project --with 'jax[cpu]' --with optax --with numpy \
  python research/export_a5_irrep.py
GPU: uvx modal run research/export_a5_modal.py

The training loop is the unmodified polybench.main. A diagnostic hook saves the
actual learned matrices before the process exits. No representation fitting loss,
ideal matrices, or group products are supplied to the model during training.
"""

import contextlib
import hashlib
import io
import itertools
import json
import math
import pathlib
import sys

import numpy as np

import groups
import polybench as pb

ARGV = [
    "--task", "g3_a5", "--model", "holo", "--seed", "0", "--steps", "20000",
    "--gdim", "3", "--heads", "85", "--order", "3", "--fnorm", "1", "--pos", "0",
]


def ideal_rotations(dual=1):
    """A5's standard 4D action, restricted to one half of its exterior square.

    This is the construction verified in test_theory.py; dual=-1 gives the other
    real 3D irrep. Element order exactly matches groups._alternating(5).
    """
    perms, _, _, _ = groups._alternating(5)
    basis = np.zeros((5, 4))
    for j in range(4):
        basis[:j + 1, j] = 1 / math.sqrt((j + 1) * (j + 2))
        basis[j + 1, j] = -(j + 1) / math.sqrt((j + 1) * (j + 2))
    P = np.zeros((60, 5, 5))
    for g, p in enumerate(perms):
        P[g, list(p), np.arange(5)] = 1
    R = np.einsum("ia,gij,jb->gab", basis, P, basis)
    pairs = list(itertools.combinations(range(4), 2))
    wedge = np.empty((60, 6, 6))
    for a, (i, j) in enumerate(pairs):
        for b, (k, l) in enumerate(pairs):
            wedge[:, a, b] = R[:, i, k] * R[:, j, l] - R[:, i, l] * R[:, j, k]
    B = np.zeros((6, 3))
    B[[0, 5], 0] = [1, dual]
    B[[1, 4], 1] = [1, -dual]
    B[[2, 3], 2] = [1, dual]
    B /= math.sqrt(2)
    return np.einsum("ia,gij,jb->gab", B, wedge, B)


def icosahedron(R):
    """An orbit of a five-fold rotation axis gives the 12 vertices."""
    G = groups.get("A5")
    g = int(G.classes[3][0])
    vals, vecs = np.linalg.eig(R[g])
    axis = vecs[:, np.argmin(abs(vals - 1))].real
    axis /= np.linalg.norm(axis)
    vertices = []
    for v in np.einsum("gij,j->gi", R, axis):
        if not any(np.linalg.norm(v - w) < 1e-8 for w in vertices):
            vertices.append(v)
    V = np.asarray(vertices)
    assert V.shape == (12, 3)
    distances = np.linalg.norm(V[:, None] - V[None], axis=-1)
    edge = np.min(distances[distances > 1e-8])
    edges = [[i, j] for i in range(12) for j in range(i + 1, 12)
             if abs(distances[i, j] - edge) < 1e-8]
    assert len(edges) == 30
    return V, edges


def align(U, R):
    """One orthogonal change of basis, fitted jointly across all 60 elements."""
    A = np.concatenate([np.kron(u, np.eye(3)) - np.kron(np.eye(3), r.T)
                        for u, r in zip(U, R)])
    _, _, vh = np.linalg.svd(A, full_matrices=False)
    q, _, vt = np.linalg.svd(vh[-1].reshape(3, 3))
    Q = q @ vt
    aligned = Q.T @ U @ Q
    error = np.mean(np.linalg.norm(aligned - R, axis=(1, 2))) / math.sqrt(3)
    return error, Q, aligned


def export_head(cfg, params):
    G = groups.get("A5")
    layer = params["layers"][0]
    x = pb.ln(layer["ln1"], params["emb"][0][:G.n])
    U = np.asarray(pb.holo_mats(cfg, layer["attn"], x).transpose(1, 0, 2, 3), dtype=float)
    error = np.linalg.norm(U[:, :, None] @ U[:, None] - U[:, G.mul], axis=(-2, -1)) / math.sqrt(3)
    errors = error.mean((1, 2))
    head = int(errors.argmin())
    learned = U[head]
    candidates = [(align(learned, ideal_rotations(dual)), dual) for dual in (1, -1)]
    (alignment_error, Q, aligned), dual = min(candidates, key=lambda item: item[0][0])
    ideal = ideal_rotations(dual)
    V, edges = icosahedron(ideal)
    perms, _, _, _ = groups._alternating(5)
    ideal_error = float(np.max(np.abs(ideal[:, None] @ ideal[None] - ideal[G.mul])))
    assert ideal_error < 1e-12
    assert np.max(np.abs(np.linalg.det(learned) - 1)) < 1e-4
    assert float(errors[head]) < 0.5, "Training did not produce a good head; do not publish it."
    return {
        "schema": 1,
        "description": "Actual matrices from the lowest-homomorphism-error head of a labels-only trained model.",
        "group": "A5", "dimension": 3, "seed": 0, "heads": 85, "selectedHead": head,
        "headSelection": "Minimum mean homomorphism error among all 85 heads; descriptive selection after training.",
        "homomorphismError": float(errors[head]),
        "homomorphismErrorDefinition": "mean over all 3600 pairs ||U(a)U(b)-U(ab)||_F / sqrt(3)",
        "headHomomorphismErrors": errors.tolist(),
        "irrepMultiplicities": (np.trace(learned, axis1=-2, axis2=-1) @ G.char_el.conj().T).real.tolist(),
        "alignmentError": float(alignment_error),
        "alignment": Q.tolist(),
        "alignmentDescription": "One common orthogonal change of basis from the least-squares intertwiner, then polar projection; no per-element corrections.",
        "idealConstruction": "Standard 4D permutation representation of A5; self-/anti-self-dual exterior square.",
        "idealDual": dual, "idealHomomorphismMaxError": ideal_error,
        "vertices": V.tolist(), "edges": edges, "multiplication": G.mul.tolist(),
        "elements": [{"id": i, "permutation": list(p), "class": int(G.cls[i]),
                      "learned": learned[i].tolist(), "aligned": aligned[i].tolist(),
                      "ideal": ideal[i].tolist()} for i, p in enumerate(perms)],
    }


def run():
    result = {}
    original = pb.holo_rep_content

    def capture(cfg, params):
        result.update(export_head(cfg, params))
        return original(cfg, params)

    pb.holo_rep_content = capture
    old_argv = sys.argv
    output = io.StringIO()
    try:
        sys.argv = ["polybench.py", *ARGV]
        with contextlib.redirect_stdout(output):
            pb.main()
    finally:
        sys.argv = old_argv
        pb.holo_rep_content = original
    benchmark = json.loads(output.getvalue().splitlines()[-1])
    assert benchmark["bal_acc"] >= 0.95
    result["irrepMultiplicities"] = [m / 60 for m in result["irrepMultiplicities"]]
    result["training"] = {"argv": ARGV, "result": benchmark,
                          "reference": "research/results/grp_e2_long.jsonl (same configuration; independent export rerun)",
                          "polybenchSha256": hashlib.sha256(pathlib.Path(pb.__file__).read_bytes()).hexdigest(),
                          "groupsSha256": hashlib.sha256(pathlib.Path(groups.__file__).read_bytes()).hexdigest()}
    return result


def verify(path):
    """Verify the exported geometry and numerical claims without retraining."""
    data = json.loads(path.read_text())
    G = groups.get("A5")
    U = np.asarray([el["learned"] for el in data["elements"]])
    A = np.asarray([el["aligned"] for el in data["elements"]])
    R = np.asarray([el["ideal"] for el in data["elements"]])
    Q = np.asarray(data["alignment"])
    V = np.asarray(data["vertices"])
    assert U.shape == R.shape == (60, 3, 3)
    assert np.array_equal(data["multiplication"], G.mul)
    assert np.max(np.abs(U @ U.transpose(0, 2, 1) - np.eye(3))) < 1e-5
    assert np.max(np.abs(np.linalg.det(U) - 1)) < 1e-5
    assert np.max(np.abs(A - Q.T @ U @ Q)) < 1e-12
    assert np.max(np.abs(R - ideal_rotations(data["idealDual"]))) < 1e-12
    hom_error = np.mean(np.linalg.norm(U[:, None] @ U[None] - U[G.mul], axis=(-2, -1))) / math.sqrt(3)
    assert abs(hom_error - data["homomorphismError"]) < 1e-12
    assert data["selectedHead"] == int(np.argmin(data["headHomomorphismErrors"]))
    assert V.shape == (12, 3) and len(data["edges"]) == 30
    # Every ideal rotation permutes the icosahedron's vertices.
    transformed = np.einsum("gij,vj->gvi", R, V)
    vertex_error = float(np.linalg.norm(transformed[:, :, None] - V[None, None], axis=-1).min(-1).max())
    assert vertex_error < 1e-12
    assert data["training"]["result"]["seed"] == 0
    assert data["training"]["result"]["bal_acc"] >= 0.95
    return {"elements": 60, "all_pair_homomorphism_error": hom_error,
            "ideal_vertex_permutation_error": vertex_error,
            "balanced_accuracy": data["training"]["result"]["bal_acc"]}


if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parents[1] / "static/recorded/a5-irrep.json"
    if "--verify" in sys.argv:
        print(json.dumps(verify(out)))
    else:
        out.write_text(json.dumps(run(), indent=2) + "\n")
        print(out)
