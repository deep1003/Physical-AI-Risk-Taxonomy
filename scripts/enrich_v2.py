#!/usr/bin/env python3
"""Enrichment v2 — raise institution/country completeness for papers & policy.

Accuracy-first, DOI-based only (no fuzzy title matching):
  Layer A: re-query OpenAlex for DOIs that returned empty, now using authorship
           countries + raw_affiliation_strings (not just institutions.display_name).
  Layer B: Crossref per-DOI author affiliations (parallel, polite pool).
  Layer C: arXiv papers w/o DOI -> construct 10.48550/arXiv.<id> and retry A/B.
  Policy : map free-text country NAMES -> ISO2 locally; OpenAlex for policy DOIs.

Resumable via json caches. Master data read-only. Rewrites enriched_*.csv.
"""
from __future__ import annotations
import csv, gzip, json, re, time, urllib.parse, urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path("/Users/deep1003/data3")
INTEG = ROOT / "integrated_ai_document_space_20260704"
OUT = ROOT / "Physical-AI-Risk-Taxonomy/output/latex/enrichment"
MAILTO = "youngsam.dream@gmail.com"
OA_RAW = OUT / "openalex_raw_cache.json"
CR_CACHE = OUT / "crossref_cache.json"
csv.field_size_limit(10_000_000)

COUNTRY = {
    "united states": "US", "usa": "US", "u.s.a": "US", "u.s.": "US", "united states of america": "US",
    "china": "CN", "p.r. china": "CN", "peoples r china": "CN", "people's republic of china": "CN",
    "united kingdom": "GB", "uk": "GB", "england": "GB", "scotland": "GB", "wales": "GB",
    "south korea": "KR", "korea": "KR", "republic of korea": "KR", "korea (the republic of)": "KR",
    "germany": "DE", "japan": "JP", "india": "IN", "canada": "CA", "italy": "IT", "france": "FR",
    "spain": "ES", "australia": "AU", "netherlands": "NL", "switzerland": "CH", "sweden": "SE",
    "singapore": "SG", "taiwan": "TW", "hong kong": "HK", "brazil": "BR", "turkey": "TR", "turkiye": "TR",
    "türkiye": "TR", "austria": "AT", "belgium": "BE", "denmark": "DK", "finland": "FI", "norway": "NO",
    "poland": "PL", "portugal": "PT", "ireland": "IE", "greece": "GR", "israel": "IL", "iran": "IR",
    "saudi arabia": "SA", "united arab emirates": "AE", "uae": "AE", "russia": "RU", "russian federation": "RU",
    "mexico": "MX", "new zealand": "NZ", "czech republic": "CZ", "czechia": "CZ", "romania": "RO",
    "hungary": "HU", "malaysia": "MY", "thailand": "TH", "indonesia": "ID", "vietnam": "VN",
    "south africa": "ZA", "egypt": "EG", "pakistan": "PK", "bangladesh": "BD", "chile": "CL",
    "colombia": "CO", "argentina": "AR", "ukraine": "UA", "luxembourg": "LU", "slovenia": "SI",
    "croatia": "HR", "estonia": "EE", "serbia": "RS", "qatar": "QA", "jordan": "JO", "lebanon": "LB",
    "european union": "EU", "international": "", "global/unspecified": "", "global": "",
}


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def norm_doi(v):
    if not v: return ""
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", str(v))
    return m.group(0).lower().rstrip(".").rstrip(")") if m else ""


def country_from_text(s):
    if not s: return ""
    t = str(s).strip()
    # explicit trailing ISO2
    m = re.search(r",\s*([A-Z]{2})\.?\s*$", t)
    if m: return m.group(1)
    low = t.lower()
    for name, code in COUNTRY.items():
        if re.search(r"(^|[,;\s])" + re.escape(name) + r"([,;\.\s]|$)", low):
            return code
    return ""


def org_from_text(s):
    if not s: return ""
    for seg in [p.strip() for p in str(s).split(",")]:
        if seg and not re.search(r"\b(department|dept|school|faculty|college|division|lab|laboratory|institute of technology dept)\b", seg, re.I) and not re.search(r"\d", seg):
            if len(seg) >= 3 and seg.lower() not in COUNTRY:
                return seg
    seg0 = str(s).split(",")[0].strip()
    return seg0 if len(seg0) >= 3 else ""


def load_json(p): return json.loads(p.read_text()) if p.exists() else {}
def save_json(p, o): p.write_text(json.dumps(o, ensure_ascii=False))


# ---------- OpenAlex (raw) ----------
def openalex_raw(dois):
    filt = "|".join("https://doi.org/" + d for d in dois)
    url = ("https://api.openalex.org/works?per-page=50&mailto=" + MAILTO
           + "&select=doi,authorships&filter=doi:" + urllib.parse.quote(filt, safe="|:/."))
    req = urllib.request.Request(url, headers={"User-Agent": f"pai-enrich/{MAILTO}"})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.loads(r.read().decode())
    out = {}
    for w in data.get("results", []):
        d = norm_doi(w.get("doi")); inst = country = ""
        for a in w.get("authorships", []):
            for i in a.get("institutions", []):
                inst = inst or (i.get("display_name") or "")
                country = country or (i.get("country_code") or "")
            if not country and a.get("countries"):
                country = a["countries"][0]
            if not inst and a.get("raw_affiliation_strings"):
                raw = a["raw_affiliation_strings"][0]
                inst = org_from_text(raw); country = country or country_from_text(raw)
            if inst or country: break
        if d: out[d] = [inst, country]
    return out


# ---------- Crossref ----------
def crossref_one(doi):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}?mailto={MAILTO}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": f"pai-enrich/{MAILTO}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            m = json.loads(r.read().decode()).get("message", {})
        for au in m.get("author", []):
            affs = au.get("affiliation") or []
            if affs:
                name = affs[0].get("name", "")
                return doi, [org_from_text(name), country_from_text(name)]
        return doi, ["", ""]
    except Exception:
        return doi, ["", ""]


def apply_paper_layers():
    rows = list(csv.DictReader(open(OUT / "enriched_papers.csv", encoding="utf-8")))
    # source url for arxiv-doi construction
    url_map = {}
    with gzip.open(INTEG / "papers/physical_ai_risks/physical_ai_risks_papers_integrated_dedup.csv.gz", "rt", encoding="utf-8", errors="ignore") as fh:
        for r in csv.DictReader(fh):
            url_map[r["record_id"]] = str(r.get("url", ""))

    def arxiv_doi(rid, cur):
        if cur: return cur
        m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", url_map.get(rid, "").lower())
        return ("10.48550/arxiv." + m.group(1)) if m else ""

    # attach effective doi (incl arxiv)
    for r in rows:
        r["_doi"] = r["doi"] or arxiv_doi(r["record_id"], "")

    unfilled = [r for r in rows if not r["institution"] and not r["country"] and r["_doi"]]
    log(f"papers unfilled with usable DOI(incl arXiv)={len(unfilled)}")

    # Layer A: OpenAlex raw
    oa = load_json(OA_RAW)
    todo = sorted({r["_doi"] for r in unfilled if r["_doi"] not in oa})
    log(f"OpenAlex-raw todo={len(todo)}")
    for i in range(0, len(todo), 50):
        b = todo[i:i + 50]
        try:
            res = openalex_raw(b)
        except Exception as e:
            log(f"  oa err {i}: {e}; sleep 20"); time.sleep(20); continue
        for d in b: oa[d] = res.get(d, ["", ""])
        if i % 1000 == 0: save_json(OA_RAW, oa); log(f"  oa {i}/{len(todo)}")
        time.sleep(0.12)
    save_json(OA_RAW, oa)
    for r in unfilled:
        v = oa.get(r["_doi"])
        if v and (v[0] or v[1]):
            r["institution"], r["country"], r["fill_source"] = v[0], v[1], "api:openalex_raw"

    # Layer B: Crossref for still-empty
    still = [r for r in rows if not r["institution"] and not r["country"] and r["_doi"]]
    cr = load_json(CR_CACHE)
    todo2 = sorted({r["_doi"] for r in still if r["_doi"] not in cr})
    log(f"Crossref todo={len(todo2)}")
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(crossref_one, d) for d in todo2]
        for f in as_completed(futs):
            d, v = f.result(); cr[d] = v; done += 1
            if done % 1000 == 0: save_json(CR_CACHE, cr); log(f"  crossref {done}/{len(todo2)}")
    save_json(CR_CACHE, cr)
    for r in still:
        v = cr.get(r["_doi"])
        if v and (v[0] or v[1]):
            r["institution"] = r["institution"] or v[0]
            r["country"] = r["country"] or v[1]
            if v[0] or v[1]: r["fill_source"] = "api:crossref"

    for r in rows: r.pop("_doi", None)
    with open(OUT / "enriched_papers.csv", "w", newline="", encoding="utf-8") as w:
        wr = csv.DictWriter(w, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    ni = sum(1 for r in rows if r["institution"]); nc = sum(1 for r in rows if r["country"])
    log(f"papers now: inst={ni} ({100*ni//len(rows)}%) country={nc} ({100*nc//len(rows)}%)")


def apply_policy():
    p = OUT / "enriched_policy.csv"
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    # raw country name from source
    raw = {}
    with gzip.open(INTEG / "policy_reports/physical_ai_risks/physical_ai_risks_policy_reports_integrated_dedup.csv.gz", "rt", encoding="utf-8", errors="ignore") as fh:
        for r in csv.DictReader(fh):
            raw[r["record_id"]] = str(r.get("country", ""))
    for r in rows:
        if not r["country"]:
            nm = raw.get(r["record_id"], "").strip().lower()
            r["country"] = COUNTRY.get(nm, country_from_text(raw.get(r["record_id"], "")))
            if r["country"]: r["fill_source"] = (r["fill_source"] + ";local:ctry_name").strip(";")
    with open(p, "w", newline="", encoding="utf-8") as w:
        wr = csv.DictWriter(w, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    nc = sum(1 for r in rows if r["country"])
    log(f"policy now: country={nc} ({100*nc//len(rows)}%)")


def report():
    out = {fam: list(csv.DictReader(open(OUT / f"enriched_{fam}.csv", encoding="utf-8")))
           for fam in ("papers", "patents", "policy")}
    gc, gi = Counter(), Counter()
    fam_stats = {}
    for fam, rows in out.items():
        n = len(rows); ni = sum(1 for r in rows if r["institution"]); nc = sum(1 for r in rows if r["country"])
        fam_stats[fam] = {"n": n, "institution_pct": round(100*ni/n, 1) if n else 0, "country_pct": round(100*nc/n, 1) if n else 0}
        for r in rows:
            if r["country"]: gc[r["country"]] += 1
            if r["institution"]: gi[r["institution"]] += 1
    rep = {"stage": "v2", "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "families": fam_stats,
           "top_countries": gc.most_common(25), "top_institutions": gi.most_common(30),
           "korea_share_pct": round(100*gc.get("KR", 0)/max(sum(gc.values()), 1), 1)}
    save_json(OUT / "coverage_report_v2.json", rep)
    log("REPORT v2: " + json.dumps(fam_stats))
    log(f"  top countries: {gc.most_common(10)} KR%={rep['korea_share_pct']}")


if __name__ == "__main__":
    apply_paper_layers()
    apply_policy()
    report()
    log("DONE v2")
