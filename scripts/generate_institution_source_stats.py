#!/usr/bin/env python3
"""Generate institution/company source statistics for the Technical Report.

The script uses the local Physical AI datasets and writes reproducible table
fragments plus PNG figures under output/latex/. It does not display figures.
"""

from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
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
    r"laboratory of|lab\.|program in|graduate school|institute of research)\b",
    re.I,
)

SUFFIX_PATTERNS = [
    (re.compile(r"\b(co\.,?\s*ltd\.?|ltd\.?|inc\.?|corp\.?|corporation|"
                r"company|limited|gmbh|s\.a\.|ag|plc)\b", re.I), ""),
    (re.compile(r"\s+", re.I), " "),
]

CANONICAL_ALIASES = {
    "google deepmind": "Google DeepMind",
    "deepmind": "Google DeepMind",
    "google": "Google",
    "microsoft research": "Microsoft",
    "microsoft": "Microsoft",
    "samsung electronics": "Samsung Electronics",
    "samsung": "Samsung",
    "samsung display": "Samsung Display",
    "samsung electronics co": "Samsung Electronics",
    "samsung electronics co ltd": "Samsung Electronics",
    "lg electronics": "LG Electronics",
    "lg electronics inc": "LG Electronics",
    "lg electronic": "LG Electronics",
    "hynix semiconductor": "SK hynix",
    "sk hynix": "SK hynix",
    "hyundai motor": "Hyundai Motor",
    "hyundai motor company": "Hyundai Motor",
    "hyundai mobis co": "Hyundai Mobis",
    "hyundai mobis company": "Hyundai Mobis",
    "kia motors corporation": "Kia",
    "kia corporation": "Kia",
    "kia": "Kia",
    "toyota motor": "Toyota",
    "toyota": "Toyota",
    "korea advanced institute of science and technology": "KAIST",
    "kaist": "KAIST",
    "seoul national university": "Seoul National University",
    "massachusetts institute of technology": "Massachusetts Institute of Technology",
    "mit": "Massachusetts Institute of Technology",
    "carnegie mellon university": "Carnegie Mellon University",
    "stanford university": "Stanford University",
    "university of washington": "University of Washington",
    "university of california berkeley": "University of California, Berkeley",
    "uc berkeley": "University of California, Berkeley",
    "national institute of standards and technology": "NIST",
    "nist": "NIST",
    "oecd": "OECD",
    "organization for economic cooperation and development": "OECD",
    "organisation for economic co operation and development": "OECD",
    "rand corporation": "RAND Corporation",
    "european commission": "European Commission",
    "iso": "ISO",
    "mitre": "MITRE",
    "electronics and telecommunications research institute": "ETRI",
    "etri": "ETRI",
    "과학기술정보통신부": "Ministry of Science and ICT",
    "과학기술정보통신부]": "Ministry of Science and ICT",
    "[과학기술정보통신부]": "Ministry of Science and ICT",
    "중소기업청": "Small and Medium Business Administration",
}

INDIVIDUAL_NAME_TOKENS = {
    "kim", "lee", "park", "choi", "jung", "jeong", "kang", "cho", "yoon", "jang",
    "lim", "shin", "han", "oh", "seo", "kwon", "hwang", "song", "hong", "yang",
    "kim sang", "lee sang", "park hyun",
}


def parse_listlike(value: object) -> list[str]:
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


def clean_org_name(raw: str) -> str | None:
    name = raw.strip().strip("\"'[]")
    if not name or name.lower() in {"nan", "none", "null", "unknown"}:
        return None
    if "@" in name:
        name = name.split("@", 1)[0]
    if ":" in name and re.search(r"[\uac00-\ud7a3]", name):
        name = name.split(":")[-1]
    name = name.strip("[] ")
    name = re.sub(r"\([^)]*\)", "", name)
    name = re.sub(r"\s+", " ", name).strip(" ,.;")
    if not name:
        return None

    # Prefer institutional forms over departmental/address strings.
    if "," in name:
        candidates = [p.strip() for p in name.split(",") if p.strip()]
        clean_candidates = [
            p for p in candidates
            if not DROP_PATTERNS.search(p) and not re.search(r"\d", p)
        ]
        if clean_candidates:
            name = clean_candidates[0]
        else:
            name = candidates[0]

    name = re.sub(r"^(the )", "", name, flags=re.I)
    name = name.strip(" ,.;")
    if len(name) < 3:
        return None

    lower = name.lower()
    lower = re.sub(r"\s+", " ", lower)
    if lower in INDIVIDUAL_NAME_TOKENS:
        return None
    if re.fullmatch(r"[A-Z][A-Z ]{2,18}", name) and lower in INDIVIDUAL_NAME_TOKENS:
        return None
    lower_no_suffix = lower
    for pattern, repl in SUFFIX_PATTERNS:
        lower_no_suffix = pattern.sub(repl, lower_no_suffix).strip(" ,.;")

    if lower in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[lower]
    if lower_no_suffix in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[lower_no_suffix]

    # Preserve well-known acronyms.
    if name.isupper() and len(name) <= 8:
        return name
    return name.title().replace(" And ", " and ").replace(" Of ", " of ")


def top_by_records(path: Path, source_family: str, column: str, top_n: int = 15) -> pd.DataFrame:
    counts: Counter[str] = Counter()
    record_count = 0
    linked_records = 0
    for chunk in pd.read_csv(path, chunksize=10000, low_memory=False):
        for value in chunk[column]:
            record_count += 1
            orgs = {clean_org_name(x) for x in parse_listlike(value)}
            orgs = {x for x in orgs if x}
            if orgs:
                linked_records += 1
            for org in orgs:
                counts[org] += 1
    rows = [
        {
            "source_family": source_family,
            "organization": org,
            "records": count,
            "share_of_linked_records_pct": round(count / linked_records * 100, 2)
            if linked_records else 0,
            "linked_records": linked_records,
            "total_records": record_count,
        }
        for org, count in counts.most_common(top_n)
    ]
    return pd.DataFrame(rows)


def latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def write_latex_table(df: pd.DataFrame, path: Path, columns: list[str], headers: list[str]) -> None:
    lines = []
    colspec = "p{0.24\\linewidth}p{0.43\\linewidth}rr"
    lines.append("\\begin{tabular}{" + colspec + "}")
    lines.append("\\toprule")
    lines.append(" & ".join(headers) + r" \\")
    lines.append("\\midrule")
    for _, row in df.iterrows():
        vals = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                value = f"{value:.1f}"
            vals.append(latex_escape(value))
        lines.append(" & ".join(vals) + r" \\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tikz_bar_chart(
    df: pd.DataFrame,
    path: Path,
    title: str,
    color: str,
    group_field: str | None = None,
    top_n: int = 8,
) -> None:
    lines = [
        r"\begin{tikzpicture}[x=0.014cm,y=0.48cm]",
        r"\sffamily",
        rf"\node[anchor=west,font=\bfseries] at (0,0.8) {{{latex_escape(title)}}};",
    ]
    y = 0
    if group_field:
        groups = list(df[group_field].drop_duplicates())
        for group in groups:
            sub = df[df[group_field] == group].head(top_n)
            if sub.empty:
                continue
            y -= 0.9
            lines.append(rf"\node[anchor=west,font=\bfseries\footnotesize] at (0,{y:.2f}) {{{latex_escape(group)}}};")
            for _, row in sub.iterrows():
                y -= 0.58
                width = min(float(row["records"]), 1000.0)
                label = latex_escape(row["organization"][:42])
                lines.append(rf"\draw[fill={color}!82,draw={color}!82] (0,{y:.2f}) rectangle ({width:.2f},{y+0.23:.2f});")
                lines.append(rf"\node[anchor=west,font=\scriptsize] at ({width+10:.2f},{y+0.11:.2f}) {{{label} ({int(row['records'])})}};")
            y -= 0.25
    else:
        sub = df.head(top_n)
        for _, row in sub.iterrows():
            y -= 0.58
            width = min(float(row["records"]), 1200.0)
            label = latex_escape(row["organization"][:48])
            lines.append(rf"\draw[fill={color}!86,draw={color}!86] (0,{y:.2f}) rectangle ({width:.2f},{y+0.25:.2f});")
            lines.append(rf"\node[anchor=west,font=\scriptsize] at ({width+10:.2f},{y+0.12:.2f}) {{{label} ({int(row['records'])})}};")
    lines.append(r"\end{tikzpicture}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    stats_dir = OUT / "tables"
    stats_dir.mkdir(parents=True, exist_ok=True)

    science = top_by_records(SCIENCE, "Scholarly publications", "affiliations", top_n=15)
    policy = top_by_records(POLICY, "Policy/report documents", "issuing_institution", top_n=15)
    patent = top_by_records(PATENT, "Patent records", "applicant_name_en", top_n=15)
    patent_fallback = top_by_records(PATENT, "Patent records", "applicant_name", top_n=15)
    if patent["records"].sum() < patent_fallback["records"].sum():
        patent = patent_fallback

    combined = pd.concat([science, policy, patent], ignore_index=True)
    combined.to_csv(OUT / "institution_source_statistics_top15.csv", index=False)

    top5_each = combined.groupby("source_family", group_keys=False).head(5).reset_index(drop=True)
    write_latex_table(
        top5_each,
        OUT / "institution_source_statistics_top5_table.tex",
        ["source_family", "organization", "records", "share_of_linked_records_pct"],
        ["Source family", "Institution / company", "Records", "Share (\\%)"],
    )

    integrated = (
        combined.groupby("organization", as_index=False)
        .agg(records=("records", "sum"))
        .sort_values("records", ascending=False)
        .head(10)
    )
    integrated["source_family"] = "Integrated"
    integrated["share_of_linked_records_pct"] = ""
    write_latex_table(
        integrated,
        OUT / "institution_source_statistics_integrated_table.tex",
        ["source_family", "organization", "records", "share_of_linked_records_pct"],
        ["Scope", "Institution / company", "Records", "Share"],
    )

    write_tikz_bar_chart(
        combined,
        OUT / "institution_source_top_by_family_chart.tex",
        "Top institutions/companies by source family",
        "flowblue",
        group_field="source_family",
        top_n=5,
    )
    write_tikz_bar_chart(
        integrated,
        OUT / "institution_source_integrated_top_chart.tex",
        "Integrated top institutions/companies",
        "reportblue",
        group_field=None,
        top_n=10,
    )

    summary = {
        "science_rows": int(pd.read_csv(SCIENCE, usecols=["paper_id"]).shape[0]),
        "policy_rows": int(pd.read_csv(POLICY, usecols=["document_id"]).shape[0]),
        "patent_rows": int(pd.read_csv(PATENT, usecols=["patent_id"]).shape[0]),
        "output_csv": str(OUT / "institution_source_statistics_top15.csv"),
    }
    pd.Series(summary).to_json(OUT / "institution_source_statistics_summary.json", force_ascii=False, indent=2)
    print(summary)


if __name__ == "__main__":
    main()
