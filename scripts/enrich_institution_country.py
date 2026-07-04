#!/usr/bin/env python3
"""Backfill institution + country for the Physical AI Risks corpus (82,971).

Two-tier, resumable:
  1) LOCAL re-join from the actually-collected source files (thorough), using the
     keys the integrated export preserved (app_id / doi / source_record_id).
  2) ONLINE fallback: for records still empty but carrying a DOI, query OpenAlex
     one document batch at a time (checkpointed, resumable).

Also harvests the curated, verified L4 risk-card references (reference_url) as a
trusted layer. Source master datasets are never modified; outputs go to
output/latex/enrichment/.

Usage:
  python enrich_institution_country.py --stage local
  python enrich_institution_country.py --stage api      # resumable
  python enrich_institution_country.py --stage all
"""
from __future__ import annotations
import argparse, ast, csv, gzip, json, re, time, urllib.parse, urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/deep1003/data3")
INTEG = ROOT / "integrated_ai_document_space_20260704"
WOS = ROOT / "webofscience_ai_global_export/bibtex/physical_ai_risk_cards_20260623"
COEVO = ROOT / "ai_risk_coevolution_1990_2026/04_processed"
REPO = ROOT / "Physical-AI-Risk-Taxonomy"
OUT = REPO / "output/latex/enrichment"
OUT.mkdir(parents=True, exist_ok=True)
MAILTO = "youngsam.dream@gmail.com"

RISK = {
    "papers": INTEG / "papers/physical_ai_risks/physical_ai_risks_papers_integrated_dedup.csv.gz",
    "patents": INTEG / "patents/physical_ai_risks/physical_ai_risks_patents_integrated_dedup.csv.gz",
    "policy": INTEG / "policy_reports/physical_ai_risks/physical_ai_risks_policy_reports_integrated_dedup.csv.gz",
}
PATENT_REF = WOS / "physical_ai_risk_cards_20260623/physical_ai_patent_references_20260623.csv"
PATENT_REF2 = WOS / "physical_ai_patent_references_20260623.csv"
POLICY_REF = WOS / "physical_ai_policy_references_20260623.csv"
COEVO_BROAD = COEVO / "final_integrated_physical_ai_risk_20260612/final_integrated_ai_risk_papers_all_domains_broad.csv"
PAPERS_CLEAN = COEVO / "physical_ai_risk_papers.clean.csv"
L4_REFS = REPO / "data/l4_references.csv"
API_CACHE = OUT / "openalex_cache.json"

csv.field_size_limit(10_000_000)


def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def open_any(p):
    p = Path(p)
    return gzip.open(p, "rt", encoding="utf-8", errors="ignore") if p.suffix == ".gz" \
        else open(p, "r", encoding="utf-8", errors="ignore")


def listlike(v):
    if v is None:
        return []
    t = str(v).strip()
    if not t or t.lower() in ("nan", "none", "[]"):
        return []
    if t.startswith("[") and t.endswith("]"):
        try:
            return [str(x).strip() for x in ast.literal_eval(t) if str(x).strip()]
        except Exception:
            pass
    return [p.strip() for p in re.split(r"\s*[|;,]\s*", t) if p.strip()]


def first_org(v):
    for item in listlike(v):
        name = re.sub(r"\([^)]*\)", "", str(item)).strip(" \"'[],.;{}")
        # applicant_info may be dict-like "{'name': 'X'}"
        m = re.search(r"name['\"]?\s*[:=]\s*['\"]([^'\"]+)", str(item))
        if m:
            name = m.group(1).strip()
        if name and len(name) >= 2 and name.lower() not in ("nan", "none", "unknown"):
            return name
    return ""


CTRY_FIX = {"KOR": "KR", "USA": "US", "CHN": "CN", "JPN": "JP", "DEU": "DE", "GBR": "GB"}


def first_country(v):
    for item in listlike(v):
        c = str(item).strip().upper().strip("[]'\" ")
        c = CTRY_FIX.get(c, c)
        if re.fullmatch(r"[A-Z]{2}", c):
            return c
        if "KOREA" in c:
            return "KR"
    return ""


def norm_doi(v):
    if not v:
        return ""
    m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", str(v))
    return m.group(0).lower().rstrip(".").rstrip(")") if m else ""


def arxiv_id(url):
    m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", str(url))
    return m.group(1) if m else ""


# ---------------- local maps ----------------
def build_local_maps():
    pat, pap_doi, pap_sid, pol_id, pol_doi = {}, {}, {}, {}, {}
    # patents
    pf = PATENT_REF if PATENT_REF.exists() else PATENT_REF2
    with open_any(pf) as fh:
        for r in csv.DictReader(fh):
            k = str(r.get("app_id", "")).strip()
            if k:
                pat[k] = (first_org(r.get("applicant_info")), first_country(r.get("applicant_ctry_codes")))
    log(f"patent_ref map: {len(pat):,}")
    # coevolution papers (rich)
    for path in (COEVO_BROAD, PAPERS_CLEAN):
        if not path.exists():
            continue
        with open_any(path) as fh:
            for r in csv.DictReader(fh):
                inst = (first_org(r.get("institutions_openalex")) or first_org(r.get("affiliation_institutions"))
                        or first_org(r.get("institutions")))
                ctry = first_country(r.get("affiliation_countries")) or first_country(r.get("country"))
                if not inst and not ctry:
                    continue
                val = (inst, ctry)
                d = norm_doi(r.get("doi") or r.get("doi_norm"))
                if d:
                    pap_doi.setdefault(d, val)
                sid = str(r.get("source_id", "")).strip()
                if sid:
                    pap_sid.setdefault(sid, val)
    log(f"papers doi map: {len(pap_doi):,} | src_id map: {len(pap_sid):,}")
    # policy
    if POLICY_REF.exists():
        with open_any(POLICY_REF) as fh:
            for r in csv.DictReader(fh):
                val = (str(r.get("publishing_institution", "")).strip(), first_country(r.get("country")))
                rid = str(r.get("record_id", "")).strip()
                d = norm_doi(r.get("doi"))
                if rid:
                    pol_id.setdefault(rid, val)
                if d:
                    pol_doi.setdefault(d, val)
    log(f"policy id map: {len(pol_id):,} | doi map: {len(pol_doi):,}")
    return pat, pap_doi, pap_sid, pol_id, pol_doi


def load_rows(fam):
    with open_any(RISK[fam]) as fh:
        return list(csv.DictReader(fh))


def stage_local():
    pat, pap_doi, pap_sid, pol_id, pol_doi = build_local_maps()
    out = {}
    for fam in ("papers", "patents", "policy"):
        rows = load_rows(fam)
        filled = []
        cov = Counter()
        for r in rows:
            inst = country = ""
            src = ""
            doi = norm_doi(r.get("doi"))
            srid = str(r.get("source_record_id", "")).strip()
            appid = str(r.get("app_id", "")).strip()
            if fam == "patents":
                if appid in pat:
                    inst, country = pat[appid]; src = "local:patent_ref"
            elif fam == "papers":
                if doi and doi in pap_doi:
                    inst, country = pap_doi[doi]; src = "local:coevo_doi"
                elif srid and srid in pap_sid:
                    inst, country = pap_sid[srid]; src = "local:coevo_srcid"
            else:  # policy
                if srid and srid in pol_id:
                    inst, country = pol_id[srid]; src = "local:policy_id"
                elif doi and doi in pol_doi:
                    inst, country = pol_doi[doi]; src = "local:policy_doi"
            if inst:
                cov["inst"] += 1
            if country:
                cov["country"] += 1
            if src:
                cov["any"] += 1
            filled.append({"record_id": r.get("record_id"), "doc_type": fam, "category": "physical_ai_risks",
                           "year": r.get("year"), "doi": doi, "app_id": appid, "source_record_id": srid,
                           "institution": inst, "country": country, "fill_source": src})
        out[fam] = filled
        n = len(rows)
        log(f"LOCAL {fam}: n={n} inst={cov['inst']} ({100*cov['inst']//n if n else 0}%) "
            f"country={cov['country']} ({100*cov['country']//n if n else 0}%)")
        with open(OUT / f"enriched_{fam}.csv", "w", newline="", encoding="utf-8") as w:
            wr = csv.DictWriter(w, fieldnames=list(filled[0].keys()))
            wr.writeheader(); wr.writerows(filled)
    _report(out, "local")
    return out


# ---------------- OpenAlex fallback ----------------
def openalex_batch(dois):
    filt = "|".join("https://doi.org/" + d for d in dois)
    url = ("https://api.openalex.org/works?per-page=50&mailto=" + MAILTO
           + "&select=doi,authorships&filter=doi:" + urllib.parse.quote(filt, safe="|:/."))
    req = urllib.request.Request(url, headers={"User-Agent": f"pai-enrich/{MAILTO}"})
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    res = {}
    for w in data.get("results", []):
        d = norm_doi(w.get("doi"))
        inst = country = ""
        for a in w.get("authorships", []):
            for i in a.get("institutions", []):
                if i.get("display_name"):
                    inst = inst or i["display_name"]
                    country = country or (i.get("country_code") or "")
            if inst:
                break
        if d:
            res[d] = (inst, country)
    return res


def stage_api():
    cache = json.loads(API_CACHE.read_text()) if API_CACHE.exists() else {}
    for fam in ("papers", "policy"):
        p = OUT / f"enriched_{fam}.csv"
        if not p.exists():
            log(f"run --stage local first ({fam} missing)"); continue
        rows = list(csv.DictReader(open(p, encoding="utf-8")))
        need = [r for r in rows if not r["institution"] and not r["country"] and r["doi"]]
        dois = sorted({r["doi"] for r in need if r["doi"] not in cache})
        log(f"API {fam}: need={len(need)} uncached_dois={len(dois)}")
        for i in range(0, len(dois), 50):
            batch = dois[i:i + 50]
            try:
                res = openalex_batch(batch)
            except Exception as e:
                log(f"  batch {i} error: {e}; sleep 30"); time.sleep(30); continue
            for d in batch:
                cache[d] = res.get(d, ["", ""])
            if i % 500 == 0:
                API_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
                log(f"  {fam} progress {i+len(batch)}/{len(dois)}")
            time.sleep(0.15)
        API_CACHE.write_text(json.dumps(cache, ensure_ascii=False))
        # apply
        for r in rows:
            if not r["institution"] and not r["country"] and r["doi"] in cache:
                inst, country = cache[r["doi"]]
                if inst or country:
                    r["institution"], r["country"] = inst, country
                    r["fill_source"] = "api:openalex"
        with open(p, "w", newline="", encoding="utf-8") as w:
            wr = csv.DictWriter(w, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
        log(f"API {fam} applied.")
    out = {fam: list(csv.DictReader(open(OUT / f"enriched_{fam}.csv", encoding="utf-8")))
           for fam in ("papers", "patents", "policy")}
    _report(out, "local+api")


def _report(out, stage):
    rep = {"stage": stage, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "families": {}}
    gc, gi = Counter(), Counter()
    for fam, rows in out.items():
        n = len(rows)
        ni = sum(1 for r in rows if r["institution"])
        nc = sum(1 for r in rows if r["country"])
        rep["families"][fam] = {"n": n, "institution_filled": ni, "country_filled": nc,
                                "institution_pct": round(100 * ni / n, 1) if n else 0,
                                "country_pct": round(100 * nc / n, 1) if n else 0}
        for r in rows:
            if r["country"]:
                gc[r["country"]] += 1
            if r["institution"]:
                gi[r["institution"]] += 1
    rep["top_countries"] = gc.most_common(20)
    rep["top_institutions"] = gi.most_common(25)
    rep["korea_share_pct"] = round(100 * gc.get("KR", 0) / max(sum(gc.values()), 1), 1)
    (OUT / f"coverage_report_{stage.replace('+','_')}.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"REPORT[{stage}]: " + json.dumps(rep["families"], ensure_ascii=False))
    log(f"  top countries: {gc.most_common(8)}  KR share={rep['korea_share_pct']}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["local", "api", "all"])
    a = ap.parse_args()
    if a.stage in ("local", "all"):
        stage_local()
    if a.stage in ("api", "all"):
        stage_api()
    log("DONE")


if __name__ == "__main__":
    main()
