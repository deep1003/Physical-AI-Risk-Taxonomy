#!/usr/bin/env python3
"""Bridge Codex PATSTAT Stage-3 person fields -> enriched_patents.csv.

Run AFTER Codex produces the Stage-3 output. Keys on app_id.
Applicant name (std) -> institution; first applicant country -> country.
Note (for report): applicant identity/address is a PATSTAT person/address proxy,
not a full research affiliation.

Outputs OUT/enriched_patents.csv, then you re-run make_country_institution_tables.py.
"""
from __future__ import annotations
import ast, csv, gzip, re, sys
from pathlib import Path

ROOT = Path("/Users/deep1003/data3")
INTEG = ROOT / "integrated_ai_document_space_20260704"
PAT = ROOT / "webofscience_ai_global_export/bibtex/ai_policy_organized_20260619/patstat"
OUT = ROOT / "Physical-AI-Risk-Taxonomy/output/latex/enrichment"
RISK_PAT = INTEG / "patents/physical_ai_risks/physical_ai_risks_patents_integrated_dedup.csv.gz"

# Stage-3 candidate outputs (first that exists wins)
STAGE3 = [
    PAT / "extracted/patstat_keyword_precise_ai_20260704_stage3_person_fields_ai_full_appids_only.csv.gz",
    PAT / "final_three_datasets_20260622/patstat_keyword_precise_ai_20260704_stage3_person_fields_joined_to_ai_full.csv.gz",
]
csv.field_size_limit(10_000_000)


def opn(p):
    p = Path(p)
    return gzip.open(p, "rt", encoding="utf-8-sig", errors="ignore") if p.suffix == ".gz" else open(p, encoding="utf-8-sig", errors="ignore")


def first_item(v):
    if v is None:
        return ""
    t = str(v).strip()
    if not t or t.lower() in ("nan", "none", "[]"):
        return ""
    if t.startswith("[") and t.endswith("]"):
        try:
            xs = [str(x).strip() for x in ast.literal_eval(t) if str(x).strip()]
            return xs[0] if xs else ""
        except Exception:
            pass
    return re.split(r"\s*[|;]\s*", t)[0].strip()


def main():
    src = next((p for p in STAGE3 if p.exists()), None)
    if not src:
        print("Stage-3 output not found yet. Candidates:")
        for p in STAGE3:
            print("  -", p)
        sys.exit(1)
    print("using stage3:", src)

    # app_id -> (applicant_name, applicant_country)
    m = {}
    with opn(src) as fh:
        r = csv.DictReader(fh)
        name_col = next((c for c in r.fieldnames if c in ("stage3_applicant_names_std", "stage3_applicant_name_country", "stage3_applicant_names_raw")), None)
        ctry_col = next((c for c in r.fieldnames if c in ("stage3_applicant_countries",)), None)
        for row in r:
            k = str(row.get("app_id", "")).strip()
            if not k:
                continue
            m[k] = (first_item(row.get(name_col)) if name_col else "",
                    first_item(row.get(ctry_col)).upper()[:2] if ctry_col else "")
    print(f"stage3 app_id map: {len(m):,}")

    rows, ni, nc = [], 0, 0
    with opn(RISK_PAT) as fh:
        for r in csv.DictReader(fh):
            aid = str(r.get("app_id", "")).strip()
            inst, ctry = m.get(aid, ("", ""))
            if inst:
                ni += 1
            if ctry:
                nc += 1
            rows.append({"record_id": r.get("record_id"), "doc_type": "patents", "category": "physical_ai_risks",
                         "year": r.get("year"), "doi": "", "app_id": aid, "source_record_id": r.get("source_record_id"),
                         "institution": inst, "country": ctry, "fill_source": "patstat:stage3" if (inst or ctry) else ""})
    with open(OUT / "enriched_patents.csv", "w", newline="", encoding="utf-8") as w:
        wr = csv.DictWriter(w, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    n = len(rows)
    print(f"patents enriched: n={n} applicant={ni} ({100*ni//n if n else 0}%) country={nc} ({100*nc//n if n else 0}%)")
    print("next: python make_country_institution_tables.py  then recompile the report")


if __name__ == "__main__":
    main()
