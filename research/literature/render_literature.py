"""Compose research/LITERATURE.md from the verified records.

Authors, titles and identifiers are printed exactly as the source records give them (arXiv for preprints,
Crossref for DOIs); venues come from venues.py, where each is tied to the evidence in refs_verified.json;
relations come from relations.py. Whether the draft cites a work is decided by searching the draft's own text
(paper/nmi/main.md on the branch named below) for the arXiv id, the DOI or the normalised title.

Run:  python research/literature/render_literature.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from relations import R  # noqa: E402
from venues import V, HOSTILE, HOSTILE_NOTE, INTRO, REACH_NOTES, THEMES  # noqa: E402
from intro_claims import CLAIMS  # noqa: E402

REPO = HERE.parents[1]
BRANCH = "claude/gracious-panini-dde55f"
DRAFT = subprocess.run(["git", "-C", str(REPO), "show", f"{BRANCH}:paper/nmi/main.md"],
                       capture_output=True, text=True, check=True).stdout
COMMIT = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", BRANCH],
                        capture_output=True, text=True, check=True).stdout.strip()


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


REFS = {}
for m in re.finditer(r"^(\d+)\. (.+)$", DRAFT.split("## References", 1)[1], re.M):
    REFS[int(m[1])] = m[2]


def cited(rec):
    hits = []
    for n, text in REFS.items():
        if rec["arxiv_id"] and rec["arxiv_id"] in text:
            hits.append(n)
        elif rec.get("doi_given") and rec["doi_given"].lower() in text.lower():
            hits.append(n)
        elif norm(rec["expected_title"])[:60] in norm(text) or norm(title_of(rec))[:60] in norm(text):
            hits.append(n)
    return sorted(set(hits))


def title_of(rec):
    """A correction in venues.py wins; then the published (Crossref) record; then arXiv."""
    return V[rec["key"]].get("title") or (rec.get("crossref") or {}).get("title") \
        or (rec.get("arxiv") or {}).get("title") or rec["expected_title"]


def authors_of(rec):
    a = V[rec["key"]].get("authors") or (rec.get("crossref") or {}).get("authors") \
        or (rec.get("arxiv") or {}).get("authors")
    return ", ".join(a)


def main():
    recs = {r["key"]: r for r in json.loads((HERE / "refs_verified.json").read_text())}
    missing = [k for k in recs if k not in R or k not in V]
    if missing:
        raise SystemExit(f"no relation or venue for: {missing}")
    lines = [INTRO.format(n=len(recs), branch=BRANCH, commit=COMMIT), ""]
    num = {}
    for theme, heading in THEMES:
        lines += [f"## {heading}", ""]
        for k, r in recs.items():
            if r["theme"] != theme:
                continue
            num[k] = len(num) + 1
            v = V[k]
            ids = []
            if r["arxiv_id"]:
                ids.append(f"arXiv:{r['arxiv_id']}")
            doi = v.get("doi") or r.get("doi_given")
            if doi:
                ids.append(f"doi:{doi}")
            c = cited(r)
            tag = f"cited in the draft as [{', '.join(map(str, c))}]" if c else "**not cited in the draft**"
            lines.append(f"{num[k]}. {authors_of(r)}. {title_of(r)}. *{v['venue']}*"
                         f"{'; ' + '; '.join(ids) if ids else ''}. ({tag}; verified: {v['evidence']})  ")
            lines.append(f"   {R[k]}")
            lines.append("")
    lines += ["## The ten references a hostile reviewer would most expect", "",
              "| # | Reference | Why a hostile reviewer expects it | Cited in the draft? |", "|---|---|---|---|"]
    for i, (k, why) in enumerate(HOSTILE, 1):
        r = recs[k]
        c = cited(r)
        first = authors_of(r).split(", ")[0]
        etal = " et al." if len(authors_of(r).split(", ")) > 2 else (
            " & " + authors_of(r).split(", ")[1] if len(authors_of(r).split(", ")) == 2 else "")
        lines.append(f"| {i} | {first}{etal}, {V[k]['short']} (entry {num[k]}) | {why} | "
                     f"{'yes, [' + ', '.join(map(str, c)) + ']' if c else '**no**'} |")
    lines += ["", HOSTILE_NOTE.format(**num), ""]
    lines += ["## Introduction claims: what large language models get wrong", "",
              "Each row gives the sentence the paper may make, its sources (entry numbers above) and what the sentence rests on.", "",
              "| # | Claim | Sentence the paper may make | Sources | Rests on |", "|---|---|---|---|---|"]
    for i, (claim, keys, sentence, basis) in enumerate(CLAIMS, 1):
        srcs = "; ".join(f"entry {num[k]} ({V[k]['short']}{', cited' if cited(recs[k]) else ''})" for k in keys)
        lines.append(f"| {i} | {claim} | {sentence} | {srcs} | {basis} |")
    lines.append("")
    stale = []
    for k, r in recs.items():
        for n in cited(r):
            if "Preprint" in REFS[n] and not V[k]["venue"].startswith("arXiv preprint"):
                stale.append(f"- [{n}] {REFS[n][:90]}... is listed as a preprint; verified venue: {V[k]['venue']} "
                             f"({V[k]['evidence']}).")
    lines += ["## Draft references whose venue is out of date", ""]
    lines += stale or ["None found."]
    lines += ["", REACH_NOTES,
              f"Draft checked: `paper/nmi/main.md` at `{BRANCH}` (`{COMMIT}`), {len(REFS)} references; "
              f"{sum(bool(cited(r)) for r in recs.values())} of the {len(recs)} works here are cited in it.", ""]
    (HERE.parent / "LITERATURE.md").write_text("\n".join(lines))
    print(f"wrote LITERATURE.md: {len(num)} entries; cited {sum(bool(cited(r)) for r in recs.values())}")


if __name__ == "__main__":
    main()
