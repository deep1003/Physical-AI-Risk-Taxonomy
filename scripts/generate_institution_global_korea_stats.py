#!/usr/bin/env python3
"""Institution/company source statistics split into Global vs Korea.

Reuses the org-name normalization from generate_institution_source_stats.py.
Global = all records (worldwide, Korea included).
Korea  = Korea-affiliated records only:
  - science: is_korea_affiliated truthy or country mentions Korea
  - patent : applicant_country_guess is a Korea code
  - policy : domestic_foreign == domestic

Writes four LaTeX fragments under output/latex/:
  institution_global_by_family_table.tex   (Table 2a)
  institution_korea_by_family_table.tex    (Table 2b)
  institution_global_by_family_chart.tex
  institution_korea_by_family_chart.tex
"""
from __future__ import annotations
import ast, json, re
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT = Path("/Users/deep1003/data3")
REPO = ROOT / "Physical-AI-Risk-Taxonomy"
DATA = ROOT / "ai_knowledge_ecosystem_codex/50_physical_ai_dataset/02_outputs"
OUT = REPO / "output/latex"
SCIENCE = DATA / "physical_ai_science_dataset.csv"
POLICY = DATA / "physical_ai_policy_dataset.csv"
PATENT = DATA / "physical_ai_patent_dataset.csv"

DROP_PATTERNS = re.compile(
    r"\b(department|school|faculty|college|division|center for|centre for|"
    r"laboratory of|lab\.|program in|graduate school|institute of research)\b", re.I)
SUFFIX_PATTERNS = [
    (re.compile(r"\b(co\.,?\s*ltd\.?|ltd\.?|inc\.?|corp\.?|corporation|"
                r"company|limited|gmbh|s\.a\.|ag|plc)\b", re.I), ""),
    (re.compile(r"\s+", re.I), " "),
]
CANONICAL_ALIASES = {
    "google deepmind": "Google DeepMind", "deepmind": "Google DeepMind", "google": "Google",
    "microsoft research": "Microsoft", "microsoft": "Microsoft",
    "samsung electronics": "Samsung Electronics", "samsung": "Samsung",
    "samsung display": "Samsung Display", "samsung electronics co": "Samsung Electronics",
    "samsung electronics co ltd": "Samsung Electronics",
    "lg electronics": "LG Electronics", "lg electronics inc": "LG Electronics",
    "lg electronic": "LG Electronics", "hynix semiconductor": "SK hynix", "sk hynix": "SK hynix",
    "hyundai motor": "Hyundai Motor", "hyundai motor company": "Hyundai Motor",
    "hyundai mobis co": "Hyundai Mobis", "hyundai mobis company": "Hyundai Mobis",
    "kia motors corporation": "Kia", "kia corporation": "Kia", "kia": "Kia",
    "toyota motor": "Toyota", "toyota": "Toyota",
    "korea advanced institute of science and technology": "KAIST", "kaist": "KAIST",
    "seoul national university": "Seoul National University",
    "massachusetts institute of technology": "Massachusetts Institute of Technology",
    "mit": "Massachusetts Institute of Technology",
    "carnegie mellon university": "Carnegie Mellon University",
    "stanford university": "Stanford University", "university of washington": "University of Washington",
    "university of california berkeley": "University of California, Berkeley",
    "uc berkeley": "University of California, Berkeley",
    "national institute of standards and technology": "NIST", "nist": "NIST",
    "oecd": "OECD", "organization for economic cooperation and development": "OECD",
    "organisation for economic co operation and development": "OECD",
    "rand corporation": "RAND Corporation", "european commission": "European Commission",
    "iso": "ISO", "mitre": "MITRE",
    "electronics and telecommunications research institute": "ETRI", "etri": "ETRI",
    "과학기술정보통신부": "Ministry of Science and ICT", "과학기술정보통신부]": "Ministry of Science and ICT",
    "[과학기술정보통신부]": "Ministry of Science and ICT",
    "중소기업청": "Small and Medium Business Administration",
}
INDIVIDUAL_NAME_TOKENS = {
    "kim", "lee", "park", "choi", "jung", "jeong", "kang", "cho", "yoon", "jang",
    "lim", "shin", "han", "oh", "seo", "kwon", "hwang", "song", "hong", "yang",
    "kim sang", "lee sang", "park hyun",
}


def parse_listlike(value):
    if pd.isna(value):
        return []
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
    parts = re.split(r"\s*\|\s*|\s*;\s*", text)
    return [p.strip() for p in parts if p.strip()]


def clean_org_name(raw):
    name = raw.strip().strip("\"'[]")
    if not name or name.lower() in {"nan", "none", "null", "unknown"}:
        return None
    if "@" in name:
        name = name.split("@", 1)[0]
    if ":" in name and re.search(r"[가-힣]", name):
        name = name.split(":")[-1]
    name = name.strip("[] ")
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"\s+", " ", name).strip(" ,.;")
    if not name:
        return None
    if "," in name:
        candidates = [p.strip() for p in name.split(",") if p.strip()]
        clean_candidates = [p for p in candidates if not DROP_PATTERNS.search(p) and not re.search(r"\d", p)]
        name = clean_candidates[0] if clean_candidates else candidates[0]
    name = re.sub(r"^(the )", "", name, flags=re.I).strip(" ,.;")
    if len(name) < 3:
        return None
    lower = re.sub(r"\s+", " ", name.lower())
    if lower in INDIVIDUAL_NAME_TOKENS:
        return None
    lower_no_suffix = lower
    for pattern, repl in SUFFIX_PATTERNS:
        lower_no_suffix = pattern.sub(repl, lower_no_suffix).strip(" ,.;")
    if lower in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[lower]
    if lower_no_suffix in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[lower_no_suffix]
    if name.isupper() and len(name) <= 8:
        return name
    return name.title().replace(" And ", " and ").replace(" Of ", " of ")


def korea_mask_science(row):
    v = str(row.get("is_korea_affiliated", "")).strip().lower()
    if v in {"true", "1", "yes", "y", "t"}:
        return True
    return "korea" in str(row.get("country", "")).lower()


def korea_mask_patent(row):
    c = str(row.get("applicant_country_guess", "")).strip().upper()
    return c in {"KR", "KOR", "KOREA", "SOUTH KOREA", "REPUBLIC OF KOREA"} or "KOREA" in c


def korea_mask_policy(row):
    return str(row.get("domestic_foreign", "")).strip().lower() in {"domestic", "국내", "kr", "korea"}


def top_two(path, source_family, org_col, extra_cols, korea_fn, top_n=15):
    g, k = Counter(), Counter()
    g_linked = k_linked = 0
    usecols = [org_col] + [c for c in extra_cols]
    for chunk in pd.read_csv(path, chunksize=20000, low_memory=False, usecols=lambda c: c in usecols):
        for _, row in chunk.iterrows():
            orgs = {clean_org_name(x) for x in parse_listlike(row.get(org_col))}
            orgs = {x for x in orgs if x}
            if not orgs:
                continue
            g_linked += 1
            for o in orgs:
                g[o] += 1
            if korea_fn(row):
                k_linked += 1
                for o in orgs:
                    k[o] += 1

    def frame(counter, linked):
        return pd.DataFrame([
            {"source_family": source_family, "organization": o, "records": c,
             "share_of_linked_records_pct": round(c / linked * 100, 2) if linked else 0}
            for o, c in counter.most_common(top_n)
        ])
    return frame(g, g_linked), frame(k, k_linked)


def latex_escape(value):
    text = str(value)
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
           "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(rep.get(ch, ch) for ch in text)


def write_by_family_table(df, path, top_n=5):
    lines = [r"\begin{tabular}{p{0.24\linewidth}p{0.43\linewidth}rr}", r"\toprule",
             "Source family & Institution / company & Records & Share (\\%) \\\\", r"\midrule"]
    for fam in df["source_family"].drop_duplicates():
        sub = df[df.source_family == fam].head(top_n)
        for _, row in sub.iterrows():
            lines.append(" & ".join([
                latex_escape(row["source_family"]), latex_escape(row["organization"]),
                str(int(row["records"])), f"{float(row['share_of_linked_records_pct']):.1f}"]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_by_family_chart(df, path, title, color, top_n=5):
    lines = [r"\begin{tikzpicture}[x=0.014cm,y=0.48cm]", r"\sffamily",
             rf"\node[anchor=west,font=\bfseries] at (0,0.8) {{{latex_escape(title)}}};"]
    y = 0
    for fam in df["source_family"].drop_duplicates():
        sub = df[df.source_family == fam].head(top_n)
        if sub.empty:
            continue
        y -= 0.9
        lines.append(rf"\node[anchor=west,font=\bfseries\footnotesize] at (0,{y:.2f}) {{{latex_escape(fam)}}};")
        for _, row in sub.iterrows():
            y -= 0.58
            width = min(float(row["records"]), 1000.0)
            label = latex_escape(str(row["organization"])[:42])
            lines.append(rf"\draw[fill={color}!82,draw={color}!82] (0,{y:.2f}) rectangle ({width:.2f},{y+0.23:.2f});")
            lines.append(rf"\node[anchor=west,font=\scriptsize] at ({width+10:.2f},{y+0.11:.2f}) {{{label} ({int(row['records'])})}};")
        y -= 0.25
    lines.append(r"\end{tikzpicture}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    sci_g, sci_k = top_two(SCIENCE, "Scholarly publications", "affiliations",
                           ["is_korea_affiliated", "country"], korea_mask_science)
    pol_g, pol_k = top_two(POLICY, "Policy/report documents", "issuing_institution",
                           ["domestic_foreign"], korea_mask_policy)
    pat_g, pat_k = top_two(PATENT, "Patent records", "applicant_name_en",
                           ["applicant_country_guess"], korea_mask_patent)
    # patent english names can be sparse; fall back to applicant_name if global count too low
    if pat_g["records"].sum() < 50:
        pat_g, pat_k = top_two(PATENT, "Patent records", "applicant_name",
                               ["applicant_country_guess"], korea_mask_patent)

    glob = pd.concat([sci_g, pol_g, pat_g], ignore_index=True)
    kor = pd.concat([sci_k, pol_k, pat_k], ignore_index=True)
    glob.to_csv(OUT / "institution_global_top15.csv", index=False)
    kor.to_csv(OUT / "institution_korea_top15.csv", index=False)

    write_by_family_table(glob, OUT / "institution_global_by_family_table.tex")
    write_by_family_table(kor, OUT / "institution_korea_by_family_table.tex")
    write_by_family_chart(glob, OUT / "institution_global_by_family_chart.tex",
                          "Top institutions/companies by source family (Global)", "flowblue")
    write_by_family_chart(kor, OUT / "institution_korea_by_family_chart.tex",
                          "Top institutions/companies by source family (Korea)", "reportblue")

    summary = {"global_rows": {f: int(glob[glob.source_family == f].records.sum())
                               for f in glob.source_family.unique()},
               "korea_rows": {f: int(kor[kor.source_family == f].records.sum())
                              for f in kor.source_family.unique()}}
    (OUT / "institution_global_korea_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("GLOBAL top per family:\n", glob.groupby("source_family").head(3).to_string())
    print("KOREA top per family:\n", kor.groupby("source_family").head(3).to_string())
    print("DONE")


if __name__ == "__main__":
    main()
