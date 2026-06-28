#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup


ROOT = Path("/Users/deep1003/data3")
HTML_PATH = ROOT / "AI_Topic_Space.github.io/pages/pai_risk_taxonomy_bilingual_v1.0.html"
OUT_DIR = ROOT / "AI_Topic_Space.github.io/data/l4_reference_relevance_audit_20260628"

METADATA_SOURCES = [
    ROOT / "AI_Topic_Space.github.io/data/top200_l4_reference_addition_20260627/applied_top200_l4_reference_additions.csv",
    ROOT / "AI_Topic_Space.github.io/data/unreferenced_corpus_l4_reference_addition_20260627/applied_unreferenced_corpus_l4_reference_additions.csv",
    ROOT / "webofscience_ai_global_export/bibtex/physical_ai_risk_cards_20260623/curated_top200_access_checked_20260627/physical_ai_safety_risk_ethics_security_top200_access_checked_compact.csv",
    ROOT / "webofscience_ai_global_export/bibtex/physical_ai_risk_cards_20260623/physical_ai_academic_references_20260623.csv",
    ROOT / "webofscience_ai_global_export/bibtex/physical_ai_risk_cards_20260623/physical_ai_policy_references_20260623.csv",
]

GENERIC_TERMS = {
    "risk", "risks", "failure", "safety", "safe", "violation", "gap", "constraint",
    "control", "physical", "ai", "robot", "robotic", "robots", "humanoid", "embodied",
    "agent", "agents", "system", "systems", "test", "testing", "coverage", "mechanism",
    "query", "execution", "misuse", "problem", "hazard", "harm", "model", "based",
    "task", "action", "policy", "data", "dataset", "benchmark", "evaluation",
}

TAG_RULES = {
    "llm_jailbreak": ["jailbreak", "prompt injection", "llm", "language model", "agentic"],
    "collision": ["collision", "contact", "impact", "human-robot", "hri", "separation distance"],
    "force": ["force", "grip", "tactile", "compliant", "admittance"],
    "navigation": ["navigation", "path planning", "obstacle", "localization", "slam", "mapping"],
    "humanoid": ["humanoid", "biped", "whole-body", "locomotion", "gait"],
    "drone": ["drone", "uav", "aerial", "airspace", "low-altitude"],
    "vehicle": ["autonomous vehicle", "connected vehicle", "driving", "traffic", "vehicle"],
    "medical_care": ["medical", "surgical", "healthcare", "care", "patient", "rehabilitation", "assistive"],
    "security": ["attack", "adversarial", "security", "cyber", "intrusion", "spoof", "poison", "hijack"],
    "privacy": ["privacy", "surveillance", "camera", "microphone", "sensing", "intimate"],
    "ethics": ["ethic", "trust", "accountability", "liability", "governance", "responsible", "dignity"],
    "learning": ["reinforcement learning", "safe learning", "imitation learning", "sim2real", "foundation model"],
    "explainability": ["explain", "interpretable", "transparent", "xai"],
    "uncertainty": ["uncertainty", "robust", "out-of-distribution", "distribution shift", "verification", "validation"],
    "cps": ["cyber physical", "cps", "digital twin", "iot", "industrial control"],
    "labor": ["labor", "labour", "worker", "automation", "job"],
}

SUSPICIOUS_DOMAIN_TERMS = [
    "food supply chain", "plant science", "sentiment", "anaesthesia", "anesthesia",
    "smart grids", "nature-based solutions", "fresh food", "protein structure",
    "carbon stock", "spine research",
]


def norm_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def norm_key(value: Any) -> str:
    text = norm_text(value).lower()
    text = re.sub(r"https?://(dx\.)?doi\.org/", "", text)
    text = re.sub(r"[^a-z0-9가-힣]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def doi_key(value: Any) -> str:
    text = norm_text(value).lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    match = re.search(r"10\.\d{4,9}/[^\s<>\"]+", text)
    return match.group(0).rstrip(").,;") if match else ""


def english_label(label: str) -> str:
    match = re.search(r"\(([^()]*)\)\s*$", label)
    return match.group(1) if match else label


def label_terms(label: str) -> set[str]:
    text = english_label(label).lower().replace("-", " ")
    words = {w for w in re.findall(r"[a-z0-9]+", text) if len(w) >= 4}
    return {w for w in words if w not in GENERIC_TERMS}


def tags_for_text(text: str) -> set[str]:
    low = text.lower()
    return {tag for tag, terms in TAG_RULES.items() if any(term in low for term in terms)}


def load_metadata() -> dict[str, dict[str, str]]:
    meta: dict[str, dict[str, str]] = {}
    for path in METADATA_SOURCES:
        if not path.exists() or path.stat().st_size == 0:
            continue
        df = pd.read_csv(path, low_memory=False)
        for _, row in df.iterrows():
            title = norm_text(row.get("title", row.get("reference_title", "")))
            abstract = norm_text(row.get("abstract", ""))
            venue = norm_text(row.get("venue", row.get("journal", row.get("venue_or_institution", row.get("publishing_institution", "")))))
            year = norm_text(row.get("year", row.get("publication_year", "")))
            url = norm_text(row.get("checked_url", row.get("url", row.get("landing_page_url", ""))))
            doi = doi_key(row.get("doi", "")) or doi_key(url)
            record = {"full_title": title, "abstract": abstract, "venue": venue, "year": year, "metadata_source": str(path)}
            if doi:
                meta[f"doi:{doi}"] = record
            if url:
                meta[f"url:{url.lower().rstrip('/')}"] = record
            if title:
                meta[f"title:{norm_key(title)}"] = record
    return meta


def find_metadata(meta: dict[str, dict[str, str]], href: str, title: str) -> dict[str, str]:
    href_key = href.lower().rstrip("/")
    d = doi_key(href)
    if d and f"doi:{d}" in meta:
        return meta[f"doi:{d}"]
    if href_key and f"url:{href_key}" in meta:
        return meta[f"url:{href_key}"]
    title_clean = norm_key(title.replace("+", ""))
    if f"title:{title_clean}" in meta:
        return meta[f"title:{title_clean}"]
    # fallback for truncated HTML titles
    for key, val in meta.items():
        if not key.startswith("title:"):
            continue
        full = key[6:]
        if title_clean and (title_clean in full or full in title_clean):
            return val
    return {"full_title": title, "abstract": "", "venue": "", "year": "", "metadata_source": ""}


def severity(row: dict[str, Any]) -> str:
    if row["suspicious_domain_hit"]:
        return "high"
    if row["direct_term_hits"] == 0 and row["tag_overlap_count"] == 0:
        return "high"
    if row["direct_term_hits"] == 0 and row["tag_overlap_count"] <= 1 and row["ref_title_word_overlap"] <= 1:
        return "medium"
    if row["direct_term_hits"] == 0 and row["tag_overlap_count"] <= 1:
        return "low"
    return "ok"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(HTML_PATH.read_text(encoding="utf-8"), "html.parser")
    meta = load_metadata()
    rows = []
    for card_idx, card in enumerate(soup.select("div.card")):
        badge = card.select_one(".badge").get_text(" ", strip=True)
        label = card.select_one(".card-label").get_text(" ", strip=True)
        definition = card.select_one(".card-def").get_text(" ", strip=True)
        just_items = [j.get_text(" ", strip=True) for j in card.select(".card-justification .just-item")]
        card_tags = tags_for_text(label + " " + definition)
        terms = label_terms(label)
        links = card.select("a.src-link")
        for ref_idx, a in enumerate(links):
            ref_title = a.get_text(" ", strip=True).lstrip("+ ").strip()
            href = norm_text(a.get("href", ""))
            just = just_items[ref_idx] if ref_idx < len(just_items) else ""
            m = find_metadata(meta, href, ref_title)
            full_title = m.get("full_title") or ref_title
            ref_text = " ".join([full_title, m.get("abstract", ""), m.get("venue", ""), just])
            ref_key = norm_key(ref_text)
            direct_hits = {t for t in terms if t in ref_key}
            ref_tags = tags_for_text(ref_text)
            tag_overlap = card_tags & ref_tags
            title_words = set(norm_key(full_title).split())
            card_words = set(norm_key(english_label(label)).split()) - GENERIC_TERMS
            title_overlap = card_words & title_words
            suspicious = [t for t in SUSPICIOUS_DOMAIN_TERMS if t in ref_text.lower()]
            row = {
                "card_badge": badge,
                "card_label": label,
                "card_definition": definition,
                "reference_index": ref_idx + 1,
                "reference_title_html": ref_title,
                "reference_title_full": full_title,
                "reference_url": href,
                "reference_year": m.get("year", ""),
                "reference_venue": m.get("venue", ""),
                "justification": just,
                "card_direct_terms": ";".join(sorted(terms)),
                "direct_term_hits": len(direct_hits),
                "direct_terms_hit": ";".join(sorted(direct_hits)),
                "card_tags": ";".join(sorted(card_tags)),
                "reference_tags": ";".join(sorted(ref_tags)),
                "tag_overlap_count": len(tag_overlap),
                "tag_overlap": ";".join(sorted(tag_overlap)),
                "ref_title_word_overlap": len(title_overlap),
                "title_words_hit": ";".join(sorted(title_overlap)),
                "suspicious_domain_hit": ";".join(suspicious),
                "metadata_source": m.get("metadata_source", ""),
            }
            row["severity"] = severity(row)
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "l4_reference_relevance_audit_all.csv", index=False)
    flagged = df[df["severity"].isin(["high", "medium", "low"])].copy()
    severity_order = {"high": 0, "medium": 1, "low": 2}
    flagged["_sev_order"] = flagged["severity"].map(severity_order)
    flagged = flagged.sort_values(["_sev_order", "card_badge", "reference_index"]).drop(columns=["_sev_order"])
    flagged.to_csv(OUT_DIR / "l4_reference_low_relevance_candidates.csv", index=False)

    summary = {
        "cards": len(soup.select("div.card")),
        "references": len(df),
        "flagged_total": len(flagged),
        "by_severity": flagged["severity"].value_counts().to_dict(),
        "output_all": str(OUT_DIR / "l4_reference_relevance_audit_all.csv"),
        "output_candidates": str(OUT_DIR / "l4_reference_low_relevance_candidates.csv"),
    }
    (OUT_DIR / "l4_reference_relevance_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# L4 Reference Relevance Audit",
        "",
        f"- Cards audited: {summary['cards']}",
        f"- References audited: {summary['references']}",
        f"- Flagged candidates: {summary['flagged_total']}",
        f"- By severity: {summary['by_severity']}",
        "",
        "## High And Medium Candidates",
        "",
    ]
    subset = flagged[flagged["severity"].isin(["high", "medium"])]
    if subset.empty:
        lines.append("(none)")
    else:
        for _, r in subset.iterrows():
            lines.append(f"- **{r.card_badge}** {r.card_label}")
            lines.append(f"  - Ref: {r.reference_title_full}")
            lines.append(f"  - Severity: {r.severity}")
            lines.append(f"  - Why flagged: direct hits={r.direct_term_hits}, tag overlap={r.tag_overlap or '(none)'}, suspicious={r.suspicious_domain_hit or '(none)'}")
            lines.append(f"  - 근거: {r.justification}")
            lines.append(f"  - URL: {r.reference_url}")
    (OUT_DIR / "l4_reference_relevance_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
