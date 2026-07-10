#!/usr/bin/env python3
"""Build the blinded bilingual survey snapshot and balanced rater assignments."""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_CARDS = ROOT / "data" / "l4_cards.json"
SOURCE_SUMMARY = ROOT / "data" / "taxonomy_summary.json"
OUTPUT = ROOT / "expert-survey" / "data"
RATERS = [f"A{i:02d}" for i in range(1, 10)]
SEED = 20260710


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_bilingual(value: str) -> tuple[str, str]:
    value = value.strip()
    boundary = value.rfind("(")
    if value.endswith(")") and boundary > 0:
        korean, english = value[:boundary], value[boundary + 1 :]
        return korean.strip(), english[:-1].strip()
    return value, value


def allocate(cards: list[dict]) -> dict[str, list[str]]:
    """Greedy L3-stratified assignment: 3 ratings/card, loads differ by <= 1."""
    rng = random.Random(SEED)
    by_family: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        by_family[card["l3_id"]].append(card)
    for family_cards in by_family.values():
        rng.shuffle(family_cards)

    assignments = {rater: [] for rater in RATERS}
    family_loads = {rater: Counter() for rater in RATERS}
    pair_loads: Counter[tuple[str, str]] = Counter()

    families = sorted(by_family, key=lambda key: (-len(by_family[key]), key))
    for family in families:
        for card in by_family[family]:
            candidates = []
            for i, a in enumerate(RATERS):
                for b in RATERS[i + 1 :]:
                    for c in RATERS[RATERS.index(b) + 1 :]:
                        trio = (a, b, c)
                        score = (
                            sum(family_loads[r][family] for r in trio),
                            sum(len(assignments[r]) for r in trio),
                            pair_loads[(a, b)] + pair_loads[(a, c)] + pair_loads[(b, c)],
                            rng.random(),
                        )
                        candidates.append((score, trio))
            _, trio = min(candidates)
            for rater in trio:
                assignments[rater].append(card["card_id"])
                family_loads[rater][family] += 1
            for pair in ((trio[0], trio[1]), (trio[0], trio[2]), (trio[1], trio[2])):
                pair_loads[pair] += 1

    for rater, card_ids in assignments.items():
        random.Random(f"{SEED}-{rater}").shuffle(card_ids)
    return assignments


def main() -> None:
    cards = json.loads(SOURCE_CARDS.read_text(encoding="utf-8"))
    summary = json.loads(SOURCE_SUMMARY.read_text(encoding="utf-8"))
    families = []
    for l2 in summary["hierarchy"]:
        for l3 in l2["l3"]:
            ko_name, en_name = split_bilingual(l3["l3_name"])
            ko_desc, en_desc = split_bilingual(l3["l3_description"])
            families.append(
                {
                    "id": l3["l3_id"],
                    "l2_id": l2["l2_id"],
                    "l2_name_en": l2["l2_name"],
                    "l2_name_ko": l2["l2_korean_label"],
                    "name_ko": ko_name,
                    "name_en": en_name,
                    "definition_ko": ko_desc,
                    "definition_en": en_desc,
                }
            )

    blinded_cards = []
    for index, card in enumerate(cards, start=1):
        ko_label, en_label = split_bilingual(card["label"])
        ko_definition, en_definition = split_bilingual(card["definition"])
        blinded_cards.append(
            {
                "card_id": card["card_id"],
                "display_id": f"V{index:03d}",
                "label_ko": ko_label,
                "label_en": en_label,
                "definition_ko": ko_definition,
                "definition_en": en_definition,
            }
        )

    assignments = allocate(cards)
    counts = Counter(card_id for ids in assignments.values() for card_id in ids)
    assert len(cards) == 182
    assert len(families) == 24
    assert set(counts.values()) == {3}
    loads = [len(ids) for ids in assignments.values()]
    assert max(loads) - min(loads) <= 1

    OUTPUT.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "survey_version": "1.0.0",
        "generated_on": "2026-07-10",
        "source_sha256": sha256(SOURCE_CARDS),
        "families": families,
        "cards": blinded_cards,
    }
    (OUTPUT / "survey-data.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    assignment_payload = {
        "assignment_version": "BIBD-20260710-v1",
        "seed": SEED,
        "raters": assignments,
    }
    (OUTPUT / "assignments.json").write_text(
        json.dumps(assignment_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"families={len(families)} cards={len(cards)} ratings={sum(loads)} loads={loads}")


if __name__ == "__main__":
    main()
