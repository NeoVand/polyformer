"""Second pass: venue evidence that Semantic Scholar's year field cannot give. Augments refs_verified.json.

  OpenReview (api2.openreview.net v2 first, then api.openreview.net v1): accepted-paper venue strings such as
      "ICLR 2023 notable top 25%", matched on the exact normalised title; dblp mirror records are ignored.
      Queried only for entries whose venue is not already fixed by a DBLP conference key, a journal record or a
      Crossref DOI. v1 is rate-limited, so requests are paced and results cached in venue_cache.json (resumable).
  arXiv comments: author statements such as "Appears in ... UAI2004".
  Crossref bibliographic search: for works with neither an arXiv id nor a DOI, and for journal versions whose
      title differs from the preprint; Crossref article numbers for DOIs.

Run after verify_refs.py:  python -u research/literature/verify_venues.py
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from verify_refs import NS, crossref_search, get, norm

HERE = Path(__file__).resolve().parent
CACHE = HERE / "venue_cache.json"
EXTRA_SEARCH = {  # key -> titles whose journal or book versions must be found by search
    "littman2002psr": ["Predictive representations of state"],
    "vonneumann1956": ["Probabilistic logics and the synthesis of reliable organisms from unreliable components"],
    "hafner2023dreamerv3": ["Mastering diverse control tasks through world models"],
    "perez2021attention": ["Attention is Turing-complete"],
}


def needs_openreview(r):
    s2 = r.get("s2") or {}
    dblp = (s2.get("externalIds") or {}).get("DBLP") or ""
    if not r["arxiv_id"]:
        return False
    if dblp.startswith(("conf/", "journals/")) and not dblp.startswith("journals/corr"):
        return False   # a DBLP conference or journal record fixes the venue and year
    return True


def openreview(title, cache):
    if title in cache:
        return cache[title]
    hits, ok = [], True
    for base, v2, pause in (("https://api2.openreview.net", True, 1.5), ("https://api.openreview.net", False, 7.0)):
        if hits:
            break   # v2 already found the accepted venue; v1 (rate-limited) only for older venues
        raw = get(f"{base}/notes/search?" + urllib.parse.urlencode({"term": title, "limit": 10}), tries=3)
        if raw is None:
            ok = False
        for n in (json.loads(raw).get("notes", []) if raw else []):
            c = n.get("content", {})
            t = (c.get("title") or {}).get("value") if v2 else c.get("title")
            v = (c.get("venue") or {}).get("value") if v2 else c.get("venue")
            if t and v and norm(t) == norm(title) and not str(v).startswith(("CoRR", "Submitted to")):
                hits.append(v)
        time.sleep(pause)
    res = {"venues": sorted(set(hits)), "complete": ok}
    if ok:
        cache[title] = res
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False) + "\n")
    return res


def arxiv_comments(ids):
    out = {}
    for i in range(0, len(ids), 50):
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(ids[i:i + 50]), "max_results": 50})
        for e in ET.fromstring(get(url)).findall("a:entry", NS):
            aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.split("/abs/")[-1])
            c = e.find("x:comment", NS)
            out[aid] = " ".join(c.text.split()) if c is not None and c.text else None
        time.sleep(3.2)
    return out


def main():
    p = HERE / "refs_verified.json"
    recs = json.loads(p.read_text())
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    com = arxiv_comments([r["arxiv_id"] for r in recs if r["arxiv_id"]])
    for r in recs:
        if r["arxiv_id"]:
            r["arxiv_comment"] = com.get(r["arxiv_id"])
        if needs_openreview(r):
            r["openreview"] = openreview(r["expected_title"], cache)
        for t in EXTRA_SEARCH.get(r["key"], []):
            r["crossref_extra"] = crossref_search(t)[:3]
            time.sleep(1)
        if r.get("doi_given"):
            raw = get("https://api.crossref.org/works/" + urllib.parse.quote(r["doi_given"]))
            if raw:
                r.setdefault("crossref", {})["article_number"] = json.loads(raw)["message"].get("article-number")
        print(f"{r['key']:28s} OR {r.get('openreview')}  comment {str(r.get('arxiv_comment'))[:60]}", flush=True)
    p.write_text(json.dumps(recs, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
