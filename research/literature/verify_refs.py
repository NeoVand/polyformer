"""Verify every candidate reference against primary bibliographic services; write refs_verified.json.

Sources, queried live (no citation is taken from memory):
  arXiv API (export.arxiv.org)        exact author list, title, first-version date, journal_ref, DOI
  Semantic Scholar Graph API (batch)  venue, publication venue, year, DBLP key, DOI
  Crossref (api.crossref.org)         for DOIs: authors, title, container, year, volume, pages
Works with neither an arXiv id nor a DOI are found by Crossref and Semantic Scholar title search.
Each record keeps the raw fields and a title-match flag, so a wrong id cannot pass silently.

Run:  python research/literature/verify_refs.py
"""
from __future__ import annotations

import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from candidates import C  # noqa: E402

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
UA = {"User-Agent": "polyformer-literature-check/1.0 (mailto:mmv@mit.edu)"}


def get(url, data=None, tries=6):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={**UA, **({"Content-Type": "application/json"} if data else {})})
            return urllib.request.urlopen(req, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and k < tries - 1:
                time.sleep(5 * (k + 1))
                continue
            if e.code in (404, 429):
                return None   # recorded as missing; the record keeps the other sources
            raise
        except urllib.error.URLError:
            time.sleep(5 * (k + 1))
    return None


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def arxiv_batch(ids):
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(chunk), "max_results": len(chunk)})
        root = ET.fromstring(get(url))
        for e in root.findall("a:entry", NS):
            aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.split("/abs/")[-1])
            jr = e.find("x:journal_ref", NS)
            doi = e.find("x:doi", NS)
            out[aid] = {"title": " ".join(e.find("a:title", NS).text.split()),
                        "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
                        "first_version": e.find("a:published", NS).text[:10],
                        "journal_ref": jr.text if jr is not None else None,
                        "doi": doi.text if doi is not None else None}
        time.sleep(3.2)
    return out


def s2_batch(keys):
    fields = "title,venue,year,publicationVenue,externalIds,journal,publicationDate,authors"
    out = {}
    for i in range(0, len(keys), 100):
        chunk = keys[i:i + 100]
        raw = get("https://api.semanticscholar.org/graph/v1/paper/batch?fields=" + fields,
                  data=json.dumps({"ids": chunk}).encode())
        for k, rec in zip(chunk, json.loads(raw) if raw else [None] * len(chunk)):
            out[k] = rec
        time.sleep(3)
    return out


def crossref(doi):
    raw = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if not raw:
        return None
    m = json.loads(raw)["message"]
    return {"title": " ".join((m.get("title") or [""])[0].split()),
            "authors": [" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name", "")
                        for a in m.get("author", [])],
            "container": (m.get("container-title") or [None])[0],
            "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "volume": m.get("volume"), "issue": m.get("issue"), "page": m.get("page"),
            "publisher": m.get("publisher"), "type": m.get("type")}


def crossref_search(title):
    raw = get("https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": title, "rows": 5}))
    hits = []
    for m in json.loads(raw)["message"]["items"] if raw else []:
        t = " ".join((m.get("title") or [""])[0].split())
        hits.append({"doi": m.get("DOI"), "title": t, "match": round(sim(t, title), 3),
                     "container": (m.get("container-title") or [None])[0],
                     "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                     "authors": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in m.get("author", [])]})
    return sorted(hits, key=lambda h: -h["match"])


def s2_search(title):
    raw = get("https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(
        {"query": title, "limit": 5, "fields": "title,venue,year,authors,externalIds,publicationVenue"}))
    hits = []
    for p in (json.loads(raw).get("data", []) if raw else []):
        hits.append({"title": p["title"], "match": round(sim(p["title"], title), 3), "venue": p.get("venue"),
                     "year": p.get("year"), "authors": [a["name"] for a in p.get("authors", [])],
                     "externalIds": p.get("externalIds")})
    return sorted(hits, key=lambda h: -h["match"])


def main():
    ax = arxiv_batch([a for _, _, _, a, _ in C if a])
    s2keys = [f"arXiv:{a}" if a else f"DOI:{d}" for _, _, _, a, d in C if a or d]
    s2 = s2_batch(s2keys)
    recs = []
    for key, theme, title, aid, doi in C:
        r = {"key": key, "theme": theme, "expected_title": title, "arxiv_id": aid, "doi_given": doi}
        if aid:
            r["arxiv"] = ax.get(aid)
        if doi:
            r["crossref"] = crossref(doi)
            time.sleep(0.5)
        r["s2"] = s2.get(f"arXiv:{aid}" if aid else f"DOI:{doi}") if (aid or doi) else None
        if not aid and not doi:
            r["crossref_search"] = crossref_search(title)
            r["s2_search"] = s2_search(title)
            time.sleep(3)
        found = [x for x in ((r.get("arxiv") or {}).get("title"), (r.get("crossref") or {}).get("title"),
                             (r.get("s2") or {}).get("title")) if x]
        r["title_match"] = max((sim(f, title) for f in found), default=0.0)
        recs.append(r)
        print(f"{key:28s} match {r['title_match']:.2f}  "
              f"{'arXiv ok' if r.get('arxiv') else ('no arXiv' if aid else '')} "
              f"{'S2 ' + str((r.get('s2') or {}).get('venue'))[:40] if r.get('s2') else ''}")
    (HERE / "refs_verified.json").write_text(json.dumps(recs, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
