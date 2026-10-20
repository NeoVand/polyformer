"""Fetch arXiv abstract pages with curl and retain an auditable metadata manifest.

Run from the repository root:
    python3 research/verify_prior_art.py

The manifest records HTTP status, fetched URL, exact citation metadata and the
SHA-256 of each response. It deliberately does not infer publication venues from
arXiv submission years. Full papers must be read separately for technical claims.
"""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone


PAPERS = {
    "2204.00740": "Path Development Network",
    "2012.04597": "Generalized iterated-sums signatures",
    "2009.08443": "Tropical time series",
    "1905.08494": "Deep Signature Transforms",
    "1511.06464": "Unitary Evolution Recurrent Neural Networks",
    "1611.00035": "Full-Capacity Unitary Recurrent Neural Networks",
    "2210.10749": "Transformers Learn Shortcuts to Automata",
    "2404.08819": "The Illusion of State in State-Space Models",
    "2411.12537": "Unlocking State-Tracking",
    "2406.06484": "Parallelizing Linear Transformers",
    "2412.06464": "Gated Delta Networks",
    "2502.10297": "DeltaProduct",
    "2302.03025": "A Toy Model of Universality",
    "2301.05217": "Progress measures for grokking",
    "1909.00668": "Simplicial Transformer",
    "2306.02896": "Representational Strengths and Limitations",
    "2507.02754": "Fast and Simplex",
    "2510.27258": "Higher-order Linear Attention",
    "2603.11133": "Beyond Pairwise Attention",
    "2602.02422": "Poly-attention",
    "1811.01900": "Janossy Pooling",
    "1703.06114": "Deep Sets",
    "1602.07576": "Group Equivariant Convolutional Networks",
    "1802.03690": "On the Generalization of Equivariance",
    "2510.01450": "Local Linear Attention",
    "2605.29157": "Parallax",
    "2506.05233": "MesaNet",
    "2506.06041": "Tensor-to-Tensor Models",
    "2207.00729": "Parallelism Tradeoff",
    "2210.02671": "A Logic for Expressing",
    "1906.05823": "Time-warping invariants",
    "2006.07027": "Seq2Tens",
    "2405.20799": "Rough Transformers",
    "2102.11174": "Linear Transformers Are Secretly Fast Weight Programmers",
    "1901.08428": "Cheap Orthogonal Constraints",
    "2402.19047": "Theoretical Foundations",
}


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta: dict[str, list[str]] = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and "name" in attrs and "content" in attrs:
            self.meta.setdefault(attrs["name"], []).append(attrs["content"])


def plain(value: str) -> str:
    return " ".join(html.unescape(re.sub("<[^>]*>", " ", value)).split())


def fetch(paper_id: str, title_fragment: str) -> dict:
    attempts = []
    result = {"arxiv_id": paper_id, "expected_title_fragment": title_fragment}
    for host in ("export.arxiv.org", "arxiv.org"):
        url = f"https://{host}/abs/{paper_id}"
        proc = subprocess.run(
            ["curl", "--location", "--silent", "--show-error", "--max-time", "45",
             "--write-out", "\n%{http_code}\n%{url_effective}", url],
            capture_output=True,
            text=True,
            check=False,
        )
        parts = proc.stdout.rsplit("\n", 2)
        body, status, final_url = parts if len(parts) == 3 else (proc.stdout, "", url)
        parser = MetaParser()
        parser.feed(body)
        title = parser.meta.get("citation_title", [""])[0]
        match = (
            title_fragment.casefold() in title.casefold()
            and parser.meta.get("citation_arxiv_id") == [paper_id]
        )
        attempts.append({
            "requested_url": url, "effective_url": final_url,
            "http_status": status, "curl_returncode": proc.returncode,
            "stderr": proc.stderr.strip(),
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
        })
        if status == "200" and match:
            result.update({
                "status": "VERIFIED",
                "title": title,
                "authors": parser.meta.get("citation_author", []),
                "citation_date": parser.meta.get("citation_date", []),
                "citation_metadata": {
                    k: v for k, v in parser.meta.items()
                    if k.startswith("citation_") and k != "citation_abstract"
                },
            })
            for field, pattern in {
                "comments": r'<td class="tablecell comments[^"]*">(.*?)</td>',
                "journal_reference": r'<td class="tablecell jref">(.*?)</td>',
                "submission_history": r'<div class="submission-history">(.*?)</div>',
            }.items():
                m = re.search(pattern, body, re.S)
                result[field] = plain(m.group(1)) if m else None
            break
    else:
        result["status"] = "UNVERIFIED"
    result["attempts"] = attempts
    result["verified_at_utc"] = datetime.now(timezone.utc).isoformat()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).parent / "results" / "prior_art_verified.json")
    args = parser.parse_args()
    rows = []
    for paper_id, title in PAPERS.items():
        row = fetch(paper_id, title)
        rows.append(row)
        print(f"{paper_id}: {row['status']} {row.get('title', title)}", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    if any(row["status"] != "VERIFIED" for row in rows):
        raise SystemExit("Some records remain UNVERIFIED; inspect the manifest.")


if __name__ == "__main__":
    main()
