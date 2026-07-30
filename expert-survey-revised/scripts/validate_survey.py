#!/usr/bin/env python3
"""Non-visual smoke checks for the revised survey bundle."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    survey = json.loads(
        (ROOT / "data" / "survey-data.json").read_text(encoding="utf-8")
    )
    assignment = json.loads(
        (ROOT / "data" / "assignments.json").read_text(encoding="utf-8")
    )
    assert survey["survey_version"] == "2.2.0-wording-em-l3-20260731"
    assert len(survey["families"]) == 24
    assert len(survey["cards"]) == 182
    family_ids = {family["id"] for family in survey["families"]}
    assert all(len(card["pair_family_ids"]) == 2 for card in survey["cards"])
    assert all(len(set(card["pair_family_ids"])) == 2 for card in survey["cards"])
    assert all(
        set(card["pair_family_ids"]) <= family_ids
        for card in survey["cards"]
    )
    card_ids = {card["card_id"] for card in survey["cards"]}
    ratings = Counter(
        card_id
        for ids in assignment["raters"].values()
        for card_id in ids
    )
    assert set(ratings) == card_ids
    assert set(ratings.values()) == {3, 4}
    assert sum(value == 4 for value in ratings.values()) == 24
    loads = [len(ids) for ids in assignment["raters"].values()]
    assert set(loads) == {30}
    app_js = (ROOT / "app.js").read_text(encoding="utf-8")
    assert "pai-expert-survey-v5-revised-wording-em-l3" in app_js
    assert "localStorage" in app_js and "submitResponse" in app_js
    assert "randomRespondentId" in app_js and "randomBlock" in app_js
    for asset in (
        "index.html",
        "styles.css",
        "app.js",
        "protocol.md",
        "protocol.tex",
    ):
        assert (ROOT / asset).stat().st_size > 100
    print(
        f"OK revised families=24 cards=182 "
        f"ratings={sum(loads)} rater_loads={loads}"
    )


if __name__ == "__main__":
    main()
