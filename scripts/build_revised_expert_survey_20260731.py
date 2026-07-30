#!/usr/bin/env python3
"""Build a parallel revised survey while preserving the released survey."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "expert-survey"
TARGET = ROOT / "expert-survey-revised"
CARDS = ROOT / "data" / "l4_cards.json"
SUMMARY = ROOT / "data" / "taxonomy_summary.json"
VERSION = "2.2.0-wording-em-l3-20260731"
ASSIGNMENT_VERSION = "BIBD-20260710-v2-30items-reused-for-v2.2"


def load_builder():
    path = SOURCE / "scripts" / "build_survey_data.py"
    spec = importlib.util.spec_from_file_location("survey_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load original survey builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    builder = load_builder()
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "styles.css", "app.js", "protocol.md", "protocol.tex", "data-dictionary.md"):
        shutil.copy2(SOURCE / name, TARGET / name)
    (TARGET / "data").mkdir(exist_ok=True)

    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    original_survey = json.loads(
        (SOURCE / "data" / "survey-data.json").read_text(encoding="utf-8")
    )
    display_ids = {
        card["card_id"]: card["display_id"] for card in original_survey["cards"]
    }

    families = []
    for l2 in summary["hierarchy"]:
        for l3 in l2["l3"]:
            _, en_name = builder.split_bilingual(l3["l3_name"])
            _, en_desc = builder.split_bilingual(l3["l3_description"])
            families.append(
                {
                    "id": l3["l3_id"],
                    "l2_id": l2["l2_id"],
                    "l2_name_en": l2["l2_name"],
                    "l2_name_ko": l2["l2_korean_label"],
                    "name_ko": builder.EASY_L3[l3["l3_id"]][0],
                    "name_en": en_name,
                    "definition_ko": builder.EASY_L3[l3["l3_id"]][1],
                    "definition_en": en_desc,
                }
            )

    blinded_cards = []
    for card in cards:
        ko_label, en_label = builder.split_bilingual(card["label"])
        ko_definition, en_definition = builder.split_bilingual(card["definition"])
        blinded_cards.append(
            {
                "card_id": card["card_id"],
                "display_id": display_ids[card["card_id"]],
                "label_ko": ko_label,
                "label_en": en_label,
                "definition_ko": ko_definition,
                "definition_en": en_definition,
                "pair_family_ids": [
                    card["l3_id"],
                    builder.distractor_for(card),
                ],
            }
        )
    blinded_cards.sort(key=lambda card: card["display_id"])

    snapshot = {
        "survey_version": VERSION,
        "generated_on": "2026-07-31",
        "source_sha256": sha256(CARDS),
        "comparison_design": {
            "baseline_survey": "2.1.0-pairwise-30items",
            "same_card_blocks": True,
            "same_display_ids": True,
            "changed_components": [
                "reviewed_l4_wording",
                "robust_em_supported_l3_reassignments",
            ],
        },
        "families": families,
        "cards": blinded_cards,
    }
    (TARGET / "data" / "survey-data.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    assignments = json.loads(
        (SOURCE / "data" / "assignments.json").read_text(encoding="utf-8")
    )
    assignments["assignment_version"] = ASSIGNMENT_VERSION
    assignments["baseline_assignment_version"] = "BIBD-20260710-v2-30items"
    (TARGET / "data" / "assignments.json").write_text(
        json.dumps(assignments, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    app_path = TARGET / "app.js"
    app = app_path.read_text(encoding="utf-8")
    app = app.replace(
        'storagePrefix: "pai-expert-survey-v4-reference-review30"',
        'storagePrefix: "pai-expert-survey-v5-revised-wording-em-l3"',
    )
    app_path.write_text(app, encoding="utf-8")

    index_path = TARGET / "index.html"
    index = index_path.read_text(encoding="utf-8")
    index = index.replace(
        "Physical AI 도메인 전문가 설문 | Physical AI Domain Expert Survey",
        "Physical AI 도메인 전문가 설문 개정판 | Revised Physical AI Domain Expert Survey",
    )
    index = index.replace(
        "Independent expert annotation · Version 1.0",
        "Independent expert annotation · Revised taxonomy version 2.2",
    )
    index = index.replace(
        "<h1>Physical AI 도메인 전문가 설문</h1>",
        "<h1>Physical AI 도메인 전문가 설문 개정판</h1>",
    )
    index = index.replace(
        "<p class=\"subtitle\">Physical AI Domain Expert Survey</p>",
        "<p class=\"subtitle\">Revised Physical AI Domain Expert Survey</p>",
    )
    index = index.replace(
        "styles.css?v=20260711-reference-review",
        "styles.css?v=20260731-revised",
    ).replace(
        "app.js?v=20260711-reference-review",
        "app.js?v=20260731-revised",
    )
    index_path.write_text(index, encoding="utf-8")

    readme = f"""# Revised Physical AI Domain Expert Survey

This directory is a parallel survey for taxonomy version `{VERSION}`.

- Baseline survey: `/expert-survey/`
- Revised survey: `/expert-survey-revised/`
- Card blocks and display IDs are held constant.
- The revised condition changes only reviewed L4 wording and robust EM-supported L3 assignments.
- The original survey files and collected responses remain unchanged.
"""
    (TARGET / "README.md").write_text(readme, encoding="utf-8")
    print(f"revised survey built: {TARGET}")


if __name__ == "__main__":
    main()
