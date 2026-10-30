"""Content checks for relation sentences that rest on more than an arXiv abstract. Writes content_checks.json.
  - context distillation's attribution to Askell et al. 2021: Semantic Scholar citation contexts
  - TEM, Siegelmann-Sontag, Givan, Angluin, Balle, Crutchfield-Young, CSCG, AlphaQubit (Nature), Ho-Kalman:
    abstracts or TLDRs from PubMed / Semantic Scholar / Crossref
"""
import json, re, time, urllib.parse, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "polyformer-literature-check/1.0 (mailto:mmv@mit.edu)"}

def get(u, data=None, tries=6):
    for k in range(tries):
        try:
            h = dict(UA, **({"Content-Type": "application/json"} if data else {}))
            return urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=60).read()
        except Exception:
            time.sleep(8 * (k + 1))
    return None

out = {}
raw = get("https://api.semanticscholar.org/graph/v1/paper/arXiv:2112.00861/citations?fields=title,contexts&limit=1000")
ctx = [(c["citingPaper"]["title"], x) for c in (json.loads(raw)["data"] if raw else [])
       for x in (c.get("contexts") or []) if "context distillation" in x.lower()]
out["askell2021_context_distillation_contexts"] = {"n": len(ctx), "examples": ctx[:5]}
es = json.loads(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode(
    {"db": "pubmed", "term": "10.1016/j.cell.2020.10.024[doi]", "retmode": "json"})))
pmid = es["esearchresult"]["idlist"][0]
xml = get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
    {"db": "pubmed", "id": pmid, "retmode": "xml"})).decode()
out["whittington2020tem_pubmed"] = {"pmid": pmid, "abstract": " ".join(re.sub(r"<[^>]+>", " ", " ".join(
    re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", xml, re.S))).split())}
dois = ["10.1016/0890-5401(87)90052-6", "10.1016/S0004-3702(02)00376-4", "10.1007/s10994-013-5416-x",
        "10.1103/PhysRevLett.63.105", "10.1038/s41467-021-22559-5", "10.1006/jcss.1995.1013",
        "10.1038/s41586-024-08148-8", "10.1524/auto.1966.14.112.545"]
raw = get("https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,abstract,tldr",
          data=json.dumps({"ids": ["DOI:" + d for d in dois]}).encode())
for d, p in zip(dois, json.loads(raw) if raw else [None] * len(dois)):
    cr = get("https://api.crossref.org/works/" + urllib.parse.quote(d))
    crm = json.loads(cr)["message"] if cr else {}
    out["doi:" + d] = {"s2_title": (p or {}).get("title"), "s2_abstract": (p or {}).get("abstract"),
                       "s2_tldr": ((p or {}).get("tldr") or {}).get("text"),
                       "crossref_abstract": re.sub(r"<[^>]+>", " ", crm.get("abstract", "")).strip() or None}
    time.sleep(1)
(HERE / "content_checks.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(out["askell2021_context_distillation_contexts"]["n"], out["whittington2020tem_pubmed"]["abstract"][:700])
for k, v in out.items():
    if k.startswith("doi:"):
        print(k, "|", (v["s2_abstract"] or v["crossref_abstract"] or v["s2_tldr"] or "NONE")[:300])
