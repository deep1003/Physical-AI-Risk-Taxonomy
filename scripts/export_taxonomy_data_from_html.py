#!/usr/bin/env python3
"""Export L4 card and reference maps from the canonical taxonomy HTML."""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
DATA_DIR = ROOT / "data"


def strip_tags(value: str) -> str:
    value = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value, flags=re.S)
    return " ".join(html.unescape(value).split())


def attrs(tag: str) -> dict[str, str]:
    return {
        key: html.unescape(value)
        for key, value in re.findall(r'([\w-]+)="([^"]*)"', tag)
    }


def first(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.S)
    return strip_tags(match.group(1)) if match else default


def export() -> dict[str, object]:
    source = HTML_PATH.read_text(encoding="utf-8")
    refs_start = source.find('<section class="refs-section"')
    if refs_start == -1:
        refs_start = len(source)

    section_positions = [
        (match.start(), match.group(1))
        for match in re.finditer(
            r'<section class="l2-section"[^>]*data-tax-id="([^"]+)"[^>]*>',
            source,
        )
    ]

    cards: list[dict[str, object]] = []
    references: list[dict[str, object]] = []
    hierarchy: list[dict[str, object]] = []

    for section_index, (section_start, l2_id) in enumerate(section_positions):
        section_end = (
            section_positions[section_index + 1][0]
            if section_index + 1 < len(section_positions)
            else refs_start
        )
        section = source[section_start:section_end]
        l2_name = first(
            r"<span>(System Safety|Interaction Safety|Societal Safety)</span>",
            section,
        )
        l2_ko = first(r'<span class="l2-ko">(.*?)</span>', section)
        l2_desc = first(r'<p class="l2-desc">(.*?)</p>', section)

        l3_positions = [
            (match.start(), match.group(1))
            for match in re.finditer(r'<div class="l3-group" data-tax-id="([^"]+)">', section)
        ]

        l3_entries: list[dict[str, object]] = []
        for l3_index, (l3_start, l3_id) in enumerate(l3_positions):
            l3_end = (
                l3_positions[l3_index + 1][0]
                if l3_index + 1 < len(l3_positions)
                else len(section)
            )
            l3 = section[l3_start:l3_end]
            l3_name = first(r'<span class="l3-name">(.*?)</span>', l3)
            l3_count = int(first(r'<span class="l3-count">(.*?)</span>', l3, "0"))
            l3_desc = first(r'<div class="l3-desc">(.*?)</div>', l3)

            card_positions = [
                match.start()
                for match in re.finditer(r'<div class="card(?:"|\s)', l3)
            ]
            l3_entries.append(
                {
                    "l3_id": l3_id,
                    "l3_name": l3_name,
                    "declared_l4_count": l3_count,
                    "exported_l4_count": len(card_positions),
                    "l3_description": l3_desc,
                }
            )

            for card_index, card_start in enumerate(card_positions):
                card_end = (
                    card_positions[card_index + 1]
                    if card_index + 1 < len(card_positions)
                    else len(l3)
                )
                card = l3[card_start:card_end]
                card_id = first(r'<span class="badge"[^>]*>(.*?)</span>', card)
                label = first(r'<span class="card-label">(.*?)</span>', card)
                definition = first(
                    r'<div class="card-def">(.*?)(?:</div><div class="card-justification">|</div>\s*<div class="card-meta">)',
                    card,
                )
                justifications = [
                    strip_tags(match.group(1))
                    for match in re.finditer(r'<span class="just-item">(.*?)</span>', card, re.S)
                ]

                links: list[dict[str, str]] = []
                for link_match in re.finditer(
                    r'<a\b([^>]*class="[^"]*src-link[^"]*"[^>]*)>(.*?)</a>',
                    card,
                    re.S,
                ):
                    link_attrs = attrs(link_match.group(1))
                    links.append(
                        {
                            "reference_title": strip_tags(link_match.group(2)),
                            "reference_url": link_attrs.get("href", ""),
                            "reference_class": link_attrs.get("class", ""),
                        }
                    )

                severity = first(r"심각도.*?margin-left:4px\">([0-9.]+)</span>", card)
                probability = first(r"확률 <span[^>]*>([0-9.]+)</span>", card)
                three_h_one_r = " | ".join(
                    f"{strip_tags(axis)}[{strip_tags(rank)}]"
                    for axis, rank in re.findall(
                        r">(H[123] [^<]+|RC Role)<sup[^>]*>([PS])</sup>",
                        card,
                    )
                )

                cards.append(
                    {
                        "card_id": card_id,
                        "l2_id": l2_id,
                        "l2_name": l2_name,
                        "l3_id": l3_id,
                        "l3_name": l3_name,
                        "label": label,
                        "definition": definition,
                        "severity": severity,
                        "probability": probability,
                        "three_h_one_r": three_h_one_r,
                        "justification_count": len(justifications),
                        "reference_link_count": len(links),
                    }
                )

                row_count = max(len(justifications), len(links))
                for row_index in range(row_count):
                    link = links[row_index] if row_index < len(links) else {}
                    references.append(
                        {
                            "card_id": card_id,
                            "l2_id": l2_id,
                            "l2_name": l2_name,
                            "l3_id": l3_id,
                            "l3_name": l3_name,
                            "card_label": label,
                            "reference_index": row_index + 1,
                            "justification": justifications[row_index]
                            if row_index < len(justifications)
                            else "",
                            "reference_title": link.get("reference_title", ""),
                            "reference_url": link.get("reference_url", ""),
                            "reference_class": link.get("reference_class", ""),
                            "is_linked": bool(link.get("reference_url", "")),
                        }
                    )

        hierarchy.append(
            {
                "l2_id": l2_id,
                "l2_name": l2_name,
                "l2_korean_label": l2_ko,
                "l2_description": l2_desc,
                "l3_count": len(l3_entries),
                "l4_count": sum(int(entry["exported_l4_count"]) for entry in l3_entries),
                "l3": l3_entries,
            }
        )

    summary = {
        "title": "Responsible AI Risk Taxonomy v2.0",
        "canonical_html": str(HTML_PATH),
        "cards": len(cards),
        "l2_categories": len(hierarchy),
        "l3_subcategories": sum(len(entry["l3"]) for entry in hierarchy),
        "evidence_rows": len(references),
        "linked_references": sum(1 for row in references if row["is_linked"]),
        "unlinked_evidence_rows": sum(1 for row in references if not row["is_linked"]),
        "max_references_per_card": max((card["reference_link_count"] for card in cards), default=0),
        "cards_over_5_references": [
            card["card_id"] for card in cards if int(card["reference_link_count"]) > 5
        ],
        "cards_with_reference_mismatch": [
            {
                "card_id": card["card_id"],
                "justification_count": card["justification_count"],
                "reference_link_count": card["reference_link_count"],
            }
            for card in cards
            if card["justification_count"] != card["reference_link_count"]
        ],
        "hierarchy": hierarchy,
        "id_scheme": {
            "L1": "Physical AI Risks",
            "L2": "P2 System Safety / I2 Interaction Safety / S2 Societal Safety",
            "L3": "P3.x / I3.x / S3.x",
            "L4": "PHYS*-REF-####",
        },
    }

    DATA_DIR.mkdir(exist_ok=True)
    write_csv(DATA_DIR / "l4_cards.csv", cards)
    write_csv(DATA_DIR / "l4_references.csv", references)
    (DATA_DIR / "l4_cards.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DATA_DIR / "l4_references.json").write_text(
        json.dumps(references, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DATA_DIR / "taxonomy_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    summary = export()
    print(json.dumps({
        "cards": summary["cards"],
        "l3_subcategories": summary["l3_subcategories"],
        "evidence_rows": summary["evidence_rows"],
        "linked_references": summary["linked_references"],
        "unlinked_evidence_rows": summary["unlinked_evidence_rows"],
        "cards_over_5_references": summary["cards_over_5_references"],
        "mismatch_count": len(summary["cards_with_reference_mismatch"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
