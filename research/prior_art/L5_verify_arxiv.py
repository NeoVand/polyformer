"""Verify arXiv ids live via the arXiv API. Usage: python3 -I verify.py ids.txt out.json
ids.txt lines: <id> | <expected title fragment>
"""
import sys, json, time, urllib.request, xml.etree.ElementTree as ET, datetime

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}

def fetch(ids):
    url = "https://export.arxiv.org/api/query?id_list=" + ",".join(ids) + "&max_results=%d" % len(ids)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fetch failed " + url)

def main():
    src, out = sys.argv[1], sys.argv[2]
    rows = []
    for line in open(src):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        aid, _, exp = line.partition("|")
        rows.append((aid.strip(), exp.strip()))
    res = {}
    for i in range(0, len(rows), 20):
        chunk = rows[i:i + 20]
        xml = fetch([a for a, _ in chunk])
        root = ET.fromstring(xml)
        for e in root.findall("a:entry", NS):
            eid = e.find("a:id", NS).text.rsplit("/abs/", 1)[-1]
            base = eid.rsplit("v", 1)[0] if "v" in eid.split("/")[-1] else eid
            title = " ".join((e.find("a:title", NS).text or "").split())
            res[base] = {
                "id": base,
                "version": eid,
                "title": title,
                "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
                "published": (e.find("a:published", NS).text or "")[:10],
                "updated": (e.find("a:updated", NS).text or "")[:10],
                "comment": " ".join((e.find("x:comment", NS).text or "").split()) if e.find("x:comment", NS) is not None else "",
                "journal_ref": " ".join((e.find("x:journal_ref", NS).text or "").split()) if e.find("x:journal_ref", NS) is not None else "",
                "summary": " ".join((e.find("a:summary", NS).text or "").split()),
            }
        time.sleep(3)
    acc = datetime.date.today().isoformat()
    report = []
    for aid, exp in rows:
        r = res.get(aid)
        if r is None:
            report.append({"id": aid, "expected": exp, "status": "MISSING"})
            continue
        ok = all(w.lower() in r["title"].lower() for w in exp.split()) if exp else True
        r2 = dict(r, expected=exp, status="OK" if ok else "TITLE_MISMATCH", accessed=acc,
                  url="https://arxiv.org/abs/" + aid)
        report.append(r2)
    json.dump(report, open(out, "w"), indent=1)
    for r in report:
        if r["status"] == "OK":
            print("OK   ", r["id"], r["published"], "|", r["title"][:90], "|", (r["authors"][0] if r["authors"] else ""), "+%d" % (len(r["authors"]) - 1), "|", r["comment"][:60], "|", r["journal_ref"][:50])
        else:
            print(r["status"], r["id"], "| expected:", r["expected"], "| got:", r.get("title", "")[:90])

main()
