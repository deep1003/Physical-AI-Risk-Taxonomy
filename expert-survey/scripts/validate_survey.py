#!/usr/bin/env python3
"""Non-visual smoke checks for survey data, assignment, and static assets."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    survey = json.loads((ROOT / "data" / "survey-data.json").read_text(encoding="utf-8"))
    assignment = json.loads((ROOT / "data" / "assignments.json").read_text(encoding="utf-8"))
    assert len(survey["families"]) == 24
    assert len(survey["cards"]) == 182
    card_ids = {card["card_id"] for card in survey["cards"]}
    ratings = Counter(card_id for ids in assignment["raters"].values() for card_id in ids)
    assert set(ratings) == card_ids
    assert set(ratings.values()) == {3}
    loads = [len(ids) for ids in assignment["raters"].values()]
    assert max(loads) - min(loads) <= 1
    for asset in ("index.html", "styles.css", "app.js", "protocol.md", "protocol.tex"):
        assert (ROOT / asset).stat().st_size > 100
    app_js = (ROOT / "app.js").read_text(encoding="utf-8")
    assert "l3_id" not in json.dumps(survey["cards"], ensure_ascii=False)
    assert "localStorage" in app_js and "submitResponse" in app_js
    assert "randomRespondentId" in app_js and "randomBlock" in app_js
    print(f"OK families=24 cards=182 ratings={sum(loads)} rater_loads={loads}")


if __name__ == "__main__":
    main()
