"""Incremental verification: candidates in candidates.py that refs_verified.json does not hold yet.

Same live sources and record format as verify_refs.py (arXiv API, Semantic Scholar batch, Crossref for DOIs), plus the
venue evidence verify_venues.py would add: the arXiv author comment, OpenReview accepted-paper venues matched on the
exact normalised title (api2, v2 notes search), and for JMLR papers the jmlr.org page (JMLR issues no DOIs).
Existing records are left untouched; new ones are appended in candidates.py order.

Run:  python research/literature/verify_new.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from candidates import C  # noqa: E402
from verify_refs import NS, arxiv_batch, crossref, get, norm, s2_batch, sim  # noqa: E402

JMLR_PAGES = {"damour2022underspec": "https://jmlr.org/papers/v23/20-1335.html"}


def arxiv_comments(ids):
    raw = get("http://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": ",".join(ids), "max_results": len(ids)}))
    out = {}
    for e in ET.fromstring(raw).findall("a:entry", NS):
        aid = e.find("a:id", NS).text.rsplit("/", 1)[-1].split("v")[0]
        c = e.find("x:comment", NS)
        out[aid] = " ".join(c.text.split()) if c is not None else None
    return out


def openreview(title):
    raw = get("https://api2.openreview.net/notes/search?" + urllib.parse.urlencode(
        {"term": title, "type": "terms", "content": "title", "limit": 10}))
    hits = []
    for n in (json.loads(raw).get("notes", []) if raw else []):
        c = n.get("content", {})
        val = lambda k: (c.get(k) or {}).get("value") if isinstance(c.get(k), dict) else c.get(k)
        if norm(val("title")) == norm(title):
            hits.append({"venue": val("venue"), "venueid": val("venueid"), "id": n.get("id")})
    return hits


def jmlr(url):
    raw = get(url)
    if not raw:
        return None
    t = raw.decode("utf-8", "replace")
    meta = dict(re.findall(r'name="citation_(\w+)" content="([^"]+)"', t))
    return {"url": url, **{k: meta.get(k) for k in ("title", "journal_title", "volume", "issue", "firstpage", "lastpage", "publication_date")}}


def main():
    path = HERE / "refs_verified.json"
    recs = json.loads(path.read_text())
    have = {r["key"] for r in recs}
    new = [c for c in C if c[0] not in have]
    if not new:
        print("nothing new")
        return
    ax = arxiv_batch([a for _, _, _, a, _ in new if a])
    cm = arxiv_comments([a for _, _, _, a, _ in new if a])
    s2 = s2_batch([f"arXiv:{a}" if a else f"DOI:{d}" for _, _, _, a, d in new if a or d])
    for key, theme, title, aid, doi in new:
        r = {"key": key, "theme": theme, "expected_title": title, "arxiv_id": aid, "doi_given": doi}
        if aid:
            r["arxiv"] = ax.get(aid)
            r["arxiv_comment"] = cm.get(aid)
        if doi:
            r["crossref"] = crossref(doi)
            time.sleep(0.5)
        r["s2"] = s2.get(f"arXiv:{aid}" if aid else f"DOI:{doi}")
        found = [x for x in ((r.get("arxiv") or {}).get("title"), (r.get("crossref") or {}).get("title"),
                             (r.get("s2") or {}).get("title")) if x]
        r["title_match"] = max((sim(f, title) for f in found), default=0.0)
        r["openreview"] = openreview(title)
        time.sleep(2)
        if key in JMLR_PAGES:
            r["jmlr"] = jmlr(JMLR_PAGES[key])
        recs.append(r)
        s = r.get("s2") or {}
        print(f"{key:28s} match {r['title_match']:.2f} | S2 {s.get('venue')} {(s.get('externalIds') or {}).get('DBLP')} | "
              f"OR {[h['venue'] for h in r['openreview']]} | CR {(r.get('crossref') or {}).get('container')} | "
              f"comment {(r.get('arxiv_comment') or '')[:50]}")
    path.write_text(json.dumps(recs, indent=1, ensure_ascii=False) + "\n")
    print(f"appended {len(new)}; total {len(recs)}")


if __name__ == "__main__":
    main()
