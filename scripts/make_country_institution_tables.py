#!/usr/bin/env python3
"""Build worldwide country + institution LaTeX tables from enriched data.

Uses record-level enriched_{papers,policy,patents}.csv (institution, country).
Patents are included only if enriched_patents.csv has values (from Codex/PATSTAT);
otherwise they are excluded and noted. Honest coverage-based counts.
Outputs LaTeX fragments under output/latex/enrichment/.
"""
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

OUT = Path("/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/enrichment")
csv.field_size_limit(10_000_000)

CNAME = {
    "US": "United States", "CN": "China", "IN": "India", "KR": "South Korea", "GB": "United Kingdom",
    "DE": "Germany", "IT": "Italy", "CA": "Canada", "JP": "Japan", "AU": "Australia", "ES": "Spain",
    "FR": "France", "NL": "Netherlands", "CH": "Switzerland", "SG": "Singapore", "SE": "Sweden",
    "TW": "Taiwan", "HK": "Hong Kong", "BR": "Brazil", "TR": "Türkiye", "IR": "Iran", "SA": "Saudi Arabia",
    "AE": "United Arab Emirates", "PL": "Poland", "BE": "Belgium", "AT": "Austria", "DK": "Denmark",
    "FI": "Finland", "NO": "Norway", "PT": "Portugal", "IE": "Ireland", "GR": "Greece", "IL": "Israel",
    "RU": "Russia", "MY": "Malaysia", "TH": "Thailand", "ID": "Indonesia", "VN": "Vietnam",
    "ZA": "South Africa", "EG": "Egypt", "PK": "Pakistan", "NZ": "New Zealand", "CZ": "Czechia",
    "EU": "European Union",
}


def esc(s):
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def load(fam):
    p = OUT / f"enriched_{fam}.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def main():
    fams = {f: load(f) for f in ("papers", "policy", "patents")}
    patents_have = any(r.get("institution") or r.get("country") for r in fams["patents"])
    # Patents are intentionally EXCLUDED from the country/institution ranking: patent-applicant
    # counts reflect commercial IP activity and would read as a technology-competitiveness
    # ranking rather than research/governance attention. Patents remain enriched (backup) and
    # their coverage is reported in the Note.
    used = ["papers", "policy"]
    rows = [r for f in used for r in fams[f]]

    cc = Counter(r["country"] for r in rows if r.get("country"))
    ic = Counter(r["institution"] for r in rows if r.get("institution"))
    n_ctry = sum(cc.values())
    n_inst = sum(ic.values())

    # country table (top 15)
    lines = [r"\begin{tabular}{rlrr}", r"\toprule",
             r"Rank & Country & Records & Share (\%) \\", r"\midrule"]
    for i, (c, v) in enumerate(cc.most_common(15), 1):
        nm = CNAME.get(c, c)
        bold = r"\bfseries " if c == "KR" else ""
        lines.append(f"{bold}{i} & {bold}{esc(nm)} & {bold}{v:,} & {bold}{100*v/n_ctry:.1f} " + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_country_top.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # institution table (top 15)
    lines = [r"\begin{tabular}{rlr}", r"\toprule",
             r"Rank & Institution / organization & Records \\", r"\midrule"]
    for i, (o, v) in enumerate(ic.most_common(15), 1):
        lines.append(f"{i} & {esc(o[:52])} & {v:,} " + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_institution_top.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "families_used": used, "patents_included": patents_have,
        "records_with_country": n_ctry, "records_with_institution": n_inst,
        "distinct_countries": len(cc), "distinct_institutions": len(ic),
        "korea_records": cc.get("KR", 0), "korea_share_pct": round(100 * cc.get("KR", 0) / max(n_ctry, 1), 1),
        "top_country": cc.most_common(1)[0] if cc else None,
    }
    (OUT / "country_institution_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
