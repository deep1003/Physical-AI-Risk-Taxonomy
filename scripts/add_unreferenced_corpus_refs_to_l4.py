#!/usr/bin/env python3
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import math
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup


ROOT = Path("/Users/deep1003/data3")
HTML_PATH = ROOT / "AI_Topic_Space.github.io/pages/pai_risk_taxonomy_bilingual_v1.0.html"
STANDALONE_HTML = ROOT / "pai_risk_taxonomy/html/pai_risk_taxonomy_bilingual_v1.0.html"
OUT_DIR = ROOT / "AI_Topic_Space.github.io/data/unreferenced_corpus_l4_reference_addition_20260627"

SOURCES = [
    ROOT / "ai_knowledge_ecosystem_codex/50_physical_ai_dataset/02_outputs/physical_ai_science_dataset.csv",
    ROOT / "ai_knowledge_ecosystem_codex/50_physical_ai_dataset/02_outputs/physical_ai_policy_dataset.csv",
    ROOT / "webofscience_ai_global_export/bibtex/physical_ai_risk_cards_20260623/physical_ai_academic_references_20260623.csv",
    ROOT / "webofscience_ai_global_export/bibtex/physical_ai_risk_cards_20260623/physical_ai_policy_references_20260623.csv",
]

PREVIOUS_ADDITIONS = [
    ROOT / "AI_Topic_Space.github.io/data/top200_l4_reference_addition_20260627/applied_top200_l4_reference_additions.csv",
]

PRESTIGE_VENUES = {
    "neurips",
    "neural information processing systems",
    "icml",
    "international conference on machine learning",
    "acl",
    "association for computational linguistics",
    "nature",
    "science",
}

RISK_TERMS = [
    "safety", "safe", "risk", "hazard", "harm", "collision", "accident", "failure",
    "fault", "attack", "adversarial", "security", "privacy", "ethic", "trust",
    "robust", "uncertainty", "bias", "misuse", "jailbreak", "prompt injection",
    "human factors", "explain", "accountab", "liability", "verification",
]

PHYSICAL_TERMS = [
    "robot", "robotic", "humanoid", "embodied", "physical ai", "autonomous vehicle",
    "drone", "uav", "manipulation", "grasp", "navigation", "cps", "cyber physical",
    "industrial", "manufacturing", "medical robot", "surgical robot", "warehouse",
    "human-robot", "hri", "motion", "control", "sensor", "actuator", "tactile",
]

GENERIC_CARD_TERMS = {
    "risk", "failure", "safety", "safe", "violation", "gap", "constraint", "control",
    "physical", "ai", "robot", "robotic", "humanoid", "embodied", "agent", "agents",
    "system", "systems", "test", "testing", "coverage", "mechanism", "query",
    "execution", "misuse", "problem", "hazard", "harm", "model", "based",
}

TAG_RULES = {
    "collision": ["collision", "contact", "impact", "human-robot", "hri", "safe control", "barrier function"],
    "manipulation": ["manipulation", "grasp", "tactile", "force", "gripper", "contact-rich"],
    "navigation": ["navigation", "path planning", "obstacle", "localization", "slam", "mapping"],
    "humanoid": ["humanoid", "biped", "whole-body", "locomotion", "retarget"],
    "drone": ["drone", "uav", "aerial"],
    "vehicle": ["autonomous vehicle", "connected vehicle", "driving", "traffic", "vehicle"],
    "medical": ["medical", "surgical", "healthcare", "care", "patient", "rehabilitation", "assistive"],
    "security": ["attack", "adversarial", "security", "cyber", "intrusion", "spoof", "poison", "jailbreak", "prompt injection"],
    "privacy": ["privacy", "surveillance", "camera", "microphone", "sensing", "data protection"],
    "ethics": ["ethic", "trust", "accountability", "liability", "governance", "responsible"],
    "learning": ["reinforcement learning", "safe learning", "learning-enabled", "foundation model", "llm", "language model"],
    "explainability": ["explain", "interpretable", "transparent", "xai"],
    "uncertainty": ["uncertainty", "robust", "out-of-distribution", "distribution shift", "verification", "validation"],
    "cps": ["cyber physical", "cps", "digital twin", "iot", "industrial control"],
}

KOREAN_TAG_PHRASES = {
    "collision": "사람 가까이 움직이는 로봇에서 충돌과 접촉 안전이 핵심 문제임을 보여준다",
    "manipulation": "물체를 잡고 미는 작업에서 힘·접촉 제어 실패가 실제 위험으로 이어질 수 있음을 다룬다",
    "navigation": "이동 로봇이 장애물과 위치 오차를 잘못 처리하면 안전한 이동이 깨질 수 있음을 보여준다",
    "humanoid": "휴머노이드의 전신 움직임과 균형 제어가 실패하면 사람 주변에서 위험해질 수 있음을 다룬다",
    "drone": "드론의 자율 비행과 제어 실패가 물리적 피해로 이어질 수 있음을 다룬다",
    "vehicle": "자율주행·연결차 환경에서 인식·보안 실패가 실제 주행 위험으로 이어질 수 있음을 보여준다",
    "medical": "의료·돌봄 로봇에서 안전성과 책임 문제가 환자 피해로 연결될 수 있음을 다룬다",
    "security": "공격자가 피지컬 AI의 인식·제어 흐름을 흔들어 위험 행동을 만들 수 있음을 보여준다",
    "privacy": "로봇과 센서가 사람의 공간과 데이터를 계속 관찰하면서 프라이버시 위험을 키울 수 있음을 다룬다",
    "ethics": "피지컬 AI가 사람과 직접 상호작용할 때 책임·신뢰·윤리 문제가 함께 생긴다는 점을 다룬다",
    "learning": "학습 기반 제어가 예외 상황에서 안전 제약을 놓칠 수 있음을 다룬다",
    "explainability": "설명 가능성이 부족하면 피지컬 AI의 위험 판단을 사람이 검토하기 어렵다는 점을 다룬다",
    "uncertainty": "불확실성과 분포 변화가 로봇 판단의 안전성을 흔들 수 있음을 다룬다",
    "cps": "센서·소프트웨어·물리 장치가 연결된 CPS에서 작은 오류가 실제 장비 위험으로 번질 수 있음을 다룬다",
}


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


def short_title(title: str, limit: int = 74) -> str:
    title = norm_text(title)
    return title if len(title) <= limit else title[: limit - 1].rstrip() + "…"


def citation_label(row: pd.Series) -> str:
    year = str(row.get("year", "")).split(".")[0]
    authors = norm_text(row.get("authors", ""))
    first_author = norm_text(row.get("first_author", ""))
    if not first_author and authors:
        first_author = re.split(r",| and |;", authors.strip("[]'\""))[0].strip("'\" ")
    if first_author:
        surname = first_author.split()[-1]
        return f"{surname} et al., {year}" if year else f"{surname} et al."
    title = short_title(norm_text(row.get("title", "")), 34)
    return f"{title}, {year}" if year else title


def contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def tags_for_text(text: str) -> set[str]:
    text = text.lower()
    return {tag for tag, terms in TAG_RULES.items() if contains_any(text, terms)}


def english_label(label: str) -> str:
    match = re.search(r"\(([^()]*)\)\s*$", label)
    return match.group(1) if match else label


def korean_label(label: str) -> str:
    return re.sub(r"\s*\([^()]*\)\s*$", "", label).strip()


def label_terms(label: str) -> set[str]:
    text = english_label(label).lower().replace("-", " ")
    words = {w for w in re.findall(r"[a-z0-9]+", text) if len(w) >= 4}
    return {w for w in words if w not in GENERIC_CARD_TERMS}


def direct_term_overlap(card: "Card", doc_text: str) -> set[str]:
    doc_key = norm_key(doc_text)
    hits = set()
    for term in card.direct_terms:
        if term in doc_key:
            hits.add(term)
    return hits


def url_for(row: pd.Series) -> str:
    for col in ["landing_page_url", "url", "pdf_url"]:
        val = norm_text(row.get(col, ""))
        if val and val.lower() != "nan":
            return val
    doi = doi_key(row.get("doi", ""))
    return f"https://doi.org/{doi}" if doi else ""


def standardize_source(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    out = pd.DataFrame()
    out["source_file"] = str(path)
    if "publication_year" in df.columns:
        out["year"] = pd.to_numeric(df.get("publication_year"), errors="coerce")
    else:
        out["year"] = pd.to_numeric(df.get("year"), errors="coerce")
    out["title"] = df.get("title", "")
    out["abstract"] = df.get("abstract", df.get("doc_text_v2", ""))
    out["venue"] = df.get("venue", df.get("journal", df.get("publication_source", df.get("publishing_institution", ""))))
    out["institution"] = df.get("publisher", df.get("publishing_institution", df.get("issuing_institution", "")))
    out["document_type"] = df.get("publication_type", df.get("type", df.get("document_type", df.get("doc_type_source_label", ""))))
    out["doi"] = df.get("doi", "")
    out["url"] = df.get("url", "")
    out["landing_page_url"] = df.get("landing_page_url", "")
    out["pdf_url"] = df.get("pdf_url", "")
    out["authors"] = df.get("authors", df.get("author", ""))
    out["first_author"] = df.get("first_author", "")
    citation_source = df.get("citation_count", df.get("times-cited", pd.Series([0] * len(df))))
    out["citations"] = pd.to_numeric(citation_source, errors="coerce").fillna(0)
    out["record_id"] = df.get("paper_id", df.get("record_id", df.get("_key", df.get("document_id", ""))))
    out["matched_terms"] = df.get("physical_ai_matched_terms", "")
    out["matched_l3"] = df.get("physical_ai_matched_l3", "")
    out["record_type"] = "report" if "policy" in path.name.lower() else "paper"
    return out


def referenced_keys(soup: BeautifulSoup) -> tuple[set[str], set[str], set[str]]:
    titles: set[str] = set()
    dois: set[str] = set()
    urls: set[str] = set()
    for a in soup.select("a.src-link, a.hf-ref, a.top200-ref-link, a.new-ref"):
        text = norm_key(a.get_text(" ", strip=True).replace("+ ", ""))
        href = norm_text(a.get("href", ""))
        if text:
            titles.add(text)
        if href:
            urls.add(href.lower().rstrip("/"))
            d = doi_key(href)
            if d:
                dois.add(d)
    for p in PREVIOUS_ADDITIONS:
        if p.exists() and p.stat().st_size:
            df = pd.read_csv(p)
            for _, row in df.iterrows():
                titles.add(norm_key(row.get("title", "")))
                d = doi_key(row.get("doi", "")) or doi_key(row.get("url", ""))
                if d:
                    dois.add(d)
                u = norm_text(row.get("url", ""))
                if u:
                    urls.add(u.lower().rstrip("/"))
    return titles, dois, urls


def candidate_score(row: pd.Series) -> tuple[float, str]:
    title = norm_text(row.get("title", ""))
    abstract = norm_text(row.get("abstract", ""))
    venue = norm_text(row.get("venue", ""))
    text = f"{title} {abstract} {venue} {row.get('matched_terms','')} {row.get('matched_l3','')}".lower()
    risk_count = sum(1 for t in RISK_TERMS if t in text)
    physical_count = sum(1 for t in PHYSICAL_TERMS if t in text)
    if risk_count == 0 or physical_count == 0:
        return -999.0, "excluded:no_risk_or_physical_pair"
    year = int(row.get("year")) if pd.notna(row.get("year")) else 0
    citations = float(row.get("citations", 0) or 0)
    venue_key = norm_key(venue)
    prestige = any(v in venue_key for v in PRESTIGE_VENUES)
    recent_bonus = 35 if year >= 2024 else 24 if year == 2023 else 12 if year == 2022 else 0
    venue_bonus = 55 if prestige else 18 if any(x in venue_key for x in ["ieee", "acm", "robotics", "automation", "nature", "science", "lancet", "cell"]) else 0
    source_bonus = 15 if doi_key(row.get("doi", "")) else 8 if url_for(row) else 0
    score = math.log1p(citations) * 14 + recent_bonus + venue_bonus + source_bonus + min(risk_count, 6) * 5 + min(physical_count, 6) * 5
    reason = f"citations={int(citations)}; year={year}; risk_terms={risk_count}; physical_terms={physical_count}"
    if prestige:
        reason += "; prestige_venue=mandatory_candidate"
    return score, reason


def access_check(row: dict[str, Any]) -> dict[str, Any]:
    checked = row.get("checked_url") or row.get("url") or ""
    status = None
    final_url = ""
    content_type = ""
    ok = False
    error = ""
    if not checked:
        return {**row, "access_ok": False, "status_code": None, "final_url": "", "content_type": "", "access_error": "missing_url"}
    try:
        resp = requests.get(
            checked,
            timeout=12,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 reference-access-check"},
            stream=True,
        )
        status = resp.status_code
        final_url = resp.url
        content_type = resp.headers.get("content-type", "")
        ok = 200 <= status < 400
        resp.close()
    except Exception as exc:
        error = type(exc).__name__
    return {**row, "access_ok": ok, "status_code": status, "final_url": final_url, "content_type": content_type, "access_error": error}


@dataclass
class Card:
    idx: int
    badge: str
    label: str
    definition: str
    current_refs: int
    tags: set[str]
    direct_terms: set[str]


def load_cards(soup: BeautifulSoup) -> list[Card]:
    cards = []
    for idx, card in enumerate(soup.select("div.card")):
        badge = card.select_one(".badge").get_text(" ", strip=True)
        label = card.select_one(".card-label").get_text(" ", strip=True)
        definition = card.select_one(".card-def").get_text(" ", strip=True)
        current_refs = len(card.select(".card-justification .just-item"))
        text = f"{label} {definition}"
        tags = tags_for_text(text)
        cards.append(Card(idx, badge, label, definition, current_refs, tags, label_terms(label)))
    return cards


def match_score(card: Card, row: pd.Series) -> tuple[float, set[str]]:
    doc_text = f"{row.get('title','')} {row.get('abstract','')} {row.get('venue','')} {row.get('matched_terms','')} {row.get('matched_l3','')}"
    doc_tags = tags_for_text(doc_text)
    overlap = card.tags & doc_tags
    if not overlap:
        return 0.0, doc_tags
    direct_hits = direct_term_overlap(card, doc_text)
    # Avoid loose matches where only broad words such as "robot", "safety", or "control" align.
    if card.direct_terms and not direct_hits:
        return 0.0, doc_tags
    if card.direct_terms and len(direct_hits) == 1:
        weak_singletons = {"sensor", "privacy", "medical", "vehicle", "drone", "learning", "motion", "contact"}
        if next(iter(direct_hits)) in weak_singletons:
            return 0.0, doc_tags
    card_words = set(norm_key(card.label + " " + card.definition).split())
    doc_words = set(norm_key(doc_text).split())
    lexical = len(card_words & doc_words) / max(1, min(len(card_words), 40))
    score = len(overlap) * 0.28 + lexical + min(len(direct_hits), 4) * 0.16
    if "security" in overlap or "medical" in overlap or "collision" in overlap:
        score += 0.08
    return score, doc_tags


def focus_phrase(title: str) -> str:
    t = title.lower()
    if "barrier function" in t:
        return "제어 장벽 함수 기반 모션 계획"
    if "path planning" in t or "navigation" in t:
        return "불확실한 환경의 경로 계획"
    if "human-robot" in t or "physical human" in t:
        return "사람-로봇 상호작용 안전"
    if "tactile" in t or "force sensor" in t:
        return "촉각·힘 센서 기반 로봇 제어"
    if "uav" in t or "drone" in t or "airspace" in t:
        return "드론·저고도 비행 안전"
    if "spoof" in t or "attack" in t or "intrusion" in t or "adversarial" in t:
        return "공격·스푸핑 탐지"
    if "health" in t or "medical" in t or "care" in t or "patient" in t:
        return "의료·돌봄 로봇"
    if "autonomous vehicle" in t or "driving" in t:
        return "자율주행 시스템"
    if "explain" in t:
        return "설명 가능한 안전 제어"
    if "reinforcement learning" in t or "safe learning" in t:
        return "안전 강화학습"
    return "피지컬 AI 시스템"


def justification(card: Card, row: pd.Series, overlap: set[str]) -> str:
    cite = citation_label(row)
    title_hint = short_title(norm_text(row.get("title", "")), 30)
    focus = focus_phrase(norm_text(row.get("title", "")))
    risk = korean_label(card.label)
    return f"{focus}에서 {risk}이 실제 안전 문제로 이어질 수 있음을 다룬다; {title_hint} ({cite})"


def insert_reference(soup: BeautifulSoup, card: Any, row: pd.Series, just: str) -> None:
    just_box = card.select_one(".card-justification")
    span = soup.new_tag("span", attrs={"class": "just-item"})
    span.string = just
    just_box.append(span)

    anchor = soup.new_tag(
        "a",
        attrs={
            "class": "src-link corpus-ref-link",
            "href": row.get("checked_url") or row.get("url") or "",
            "target": "_blank",
            "style": "border-left:3px solid #8E44AD;padding-left:4px;",
        },
    )
    year = str(row.get("year", "")).split(".")[0]
    anchor.string = f"+ {short_title(norm_text(row.get('title', '')))} ({year})" if year else f"+ {short_title(norm_text(row.get('title', '')))}"
    meta = soup.new_tag("span", attrs={"class": "meta-item corpus-ref"})
    meta.append(anchor)
    marker = card.find("div", style=lambda s: s and "3H1R" in s)
    if marker:
        marker.insert_before(meta)
    else:
        card.append(meta)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    soup = BeautifulSoup(HTML_PATH.read_text(encoding="utf-8"), "html.parser")
    ref_titles, ref_dois, ref_urls = referenced_keys(soup)

    frames = []
    for source in SOURCES:
        frames.append(standardize_source(source))
    pool = pd.concat(frames, ignore_index=True)
    pool["title_key"] = pool["title"].map(norm_key)
    pool["doi_key"] = pool["doi"].map(doi_key)
    pool["candidate_url"] = pool.apply(url_for, axis=1)
    pool["url_key"] = pool["candidate_url"].map(lambda x: norm_text(x).lower().rstrip("/"))
    pool = pool[pool["title_key"].str.len() > 20].copy()
    pool = pool[~pool["doi_key"].isin(ref_dois) | (pool["doi_key"] == "")].copy()
    pool = pool[~pool["url_key"].isin(ref_urls) | (pool["url_key"] == "")].copy()
    pool = pool[~pool["title_key"].isin(ref_titles)].copy()
    pool = pool.drop_duplicates(subset=["doi_key", "title_key"], keep="first")

    scored = []
    for _, row in pool.iterrows():
        score, reason = candidate_score(row)
        if score > 0 and url_for(row):
            item = row.to_dict()
            item["score"] = round(score, 3)
            item["selection_reason"] = reason
            item["checked_url"] = url_for(row)
            scored.append(item)
    scored_df = pd.DataFrame(scored).sort_values(["score", "year", "citations"], ascending=False)

    # Check a buffer so inaccessible links can be replaced while still producing 200 records.
    buffer = scored_df.head(420).to_dict("records")
    checked = []
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for result in ex.map(access_check, buffer):
            checked.append(result)
    checked_df = pd.DataFrame(checked)
    accessible = checked_df[checked_df["access_ok"]].copy().sort_values(["score", "year", "citations"], ascending=False)
    selected = accessible.head(200).copy()
    selected.insert(0, "rank", range(1, len(selected) + 1))

    selected.to_csv(OUT_DIR / "unreferenced_corpus_top200_access_checked.csv", index=False)
    checked_df.to_csv(OUT_DIR / "unreferenced_corpus_access_check_buffer.csv", index=False)

    cards = load_cards(soup)
    card_nodes = soup.select("div.card")
    additions = []
    skipped = []
    used_docs_per_card: set[tuple[str, str]] = set()
    card_counts = {c.idx: c.current_refs for c in cards}

    matches = []
    for _, row in selected.iterrows():
        for card in cards:
            if card_counts[card.idx] >= 5:
                continue
            score, doc_tags = match_score(card, row)
            if score >= 0.86:
                matches.append({
                    "match_score": round(score, 3),
                    "card_idx": card.idx,
                    "card_badge": card.badge,
                    "card_label": card.label,
                    "card_refs_before": card.current_refs,
                    "overlap_tags": ";".join(sorted(card.tags & doc_tags)),
                    **row.to_dict(),
                })
    matches_df = pd.DataFrame(matches).sort_values(["match_score", "score", "year", "citations"], ascending=False)
    matches_df.to_csv(OUT_DIR / "unreferenced_corpus_l4_candidate_matches.csv", index=False)

    seen_doc_card = set()
    seen_just = set()
    doc_use_count: dict[str, int] = {}
    for _, row in matches_df.iterrows():
        card_idx = int(row["card_idx"])
        doc_id = row.get("doi_key") or row.get("title_key")
        key = (card_idx, doc_id)
        if key in used_docs_per_card or key in seen_doc_card:
            continue
        seen_doc_card.add(key)
        if doc_use_count.get(str(doc_id), 0) >= 3:
            skipped.append({**row.to_dict(), "skip_reason": "document_reuse_limit_3"})
            continue
        if card_counts[card_idx] >= 5:
            skipped.append({**row.to_dict(), "skip_reason": "card_reference_limit_5"})
            continue
        # Keep the second pass conservative: at most one new corpus ref per card.
        if any(a["card_idx"] == card_idx for a in additions):
            skipped.append({**row.to_dict(), "skip_reason": "one_new_ref_per_card_this_pass"})
            continue
        card = cards[card_idx]
        overlap = set(str(row.get("overlap_tags", "")).split(";")) - {""}
        just = justification(card, row, overlap or card.tags)
        if just in seen_just:
            suffix = hashlib.sha1(str(doc_id).encode()).hexdigest()[:4]
            just = just.replace(")", f"; 사례 {suffix})")
        seen_just.add(just)
        insert_reference(soup, card_nodes[card_idx], row, just)
        doc_use_count[str(doc_id)] = doc_use_count.get(str(doc_id), 0) + 1
        card_counts[card_idx] += 1
        add = row.to_dict()
        add["justification"] = just
        add["refs_after"] = card_counts[card_idx]
        additions.append(add)

    backup = HTML_PATH.with_suffix(f".bak_before_unreferenced_corpus_refs_{time.strftime('%Y%m%d_%H%M%S')}.html")
    shutil.copy2(HTML_PATH, backup)
    HTML_PATH.write_text(str(soup), encoding="utf-8")
    if STANDALONE_HTML.exists():
        STANDALONE_HTML.write_text(str(soup), encoding="utf-8")

    add_df = pd.DataFrame(additions)
    skip_df = pd.DataFrame(skipped)
    add_df.to_csv(OUT_DIR / "applied_unreferenced_corpus_l4_reference_additions.csv", index=False)
    skip_df.to_csv(OUT_DIR / "skipped_unreferenced_corpus_l4_reference_additions.csv", index=False)

    report = {
        "html_path": str(HTML_PATH),
        "standalone_html": str(STANDALONE_HTML),
        "backup_path": str(backup),
        "candidate_pool_after_excluding_existing_refs": int(len(pool)),
        "scored_candidates": int(len(scored_df)),
        "access_checked_buffer": int(len(checked_df)),
        "accessible_candidates_in_buffer": int(len(accessible)),
        "selected_top200_count": int(len(selected)),
        "candidate_matches": int(len(matches_df)),
        "applied_additions": int(len(add_df)),
        "cards_touched": int(add_df["card_badge"].nunique()) if not add_df.empty else 0,
        "max_refs_after": int(max(card_counts.values())),
        "over_5_cards": int(sum(v > 5 for v in card_counts.values())),
    }
    (OUT_DIR / "unreferenced_corpus_l4_reference_addition_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Unreferenced Corpus L4 Reference Addition Report",
        "",
        f"- Selected access-checked Top 200: {len(selected)}",
        f"- Applied additions: {len(add_df)}",
        f"- Cards touched: {report['cards_touched']}",
        f"- Max references after: {report['max_refs_after']}",
        f"- Cards over 5 references: {report['over_5_cards']}",
        f"- Backup: `{backup}`",
        "",
        "## Applied Additions",
        "",
    ]
    if add_df.empty:
        lines.append("(none)")
    else:
        for _, r in add_df.sort_values(["card_badge", "match_score"], ascending=[True, False]).iterrows():
            lines.append(f"- **{r['card_badge']}** {r['card_label']} -> {short_title(r['title'], 96)} ({int(r['year']) if pd.notna(r['year']) else ''})")
            lines.append(f"  - 근거: {r['justification']}")
            lines.append(f"  - URL: {r['checked_url']}")
    (OUT_DIR / "unreferenced_corpus_l4_reference_addition_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
