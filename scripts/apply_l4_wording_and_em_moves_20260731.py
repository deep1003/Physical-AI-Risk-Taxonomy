#!/usr/bin/env python3
"""Apply reviewed L4 wording and robust EM-supported L3 moves to taxonomy HTML."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "expert-survey" / "analysis" / "l4_wording_boundary_review_20260731.md"
DEFAULT_HTML = [
    ROOT / "index.html",
    ROOT / "docs" / "pai_risk_taxonomy_bilingual_v2.0.html",
]

# Retained only when the same assignment was selected in at least 80% of the
# 24 model-language-seed sensitivity conditions.
ROBUST_MOVES = {
    "PHYSBENCH-REF-0065": ("I3.7", "P3.2"),
    "PHYSBENCH-REF-0107": ("I3.6", "S3.6"),
}


def parse_revisions() -> dict[str, tuple[str, str]]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from run_l3_reassignment_em_20260731 import parse_review_proposals

    proposals = parse_review_proposals(REVIEW)
    revisions = {
        card_id: (values["label_master"], values["definition_master"])
        for card_id, values in proposals.items()
    }
    if len(revisions) != 84:
        raise RuntimeError(f"Expected 84 reviewed revisions, found {len(revisions)}")
    return revisions


def balanced_div(source: str, start: int) -> tuple[int, int]:
    if not source.startswith("<div", start):
        raise ValueError(f"No div at offset {start}")
    depth = 0
    for match in re.finditer(r"<div\b[^>]*>|</div\s*>", source[start:], re.I):
        token = match.group(0).lower()
        if token.startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, start + match.end()
    raise ValueError(f"Unbalanced div at offset {start}")


def card_span(source: str, card_id: str) -> tuple[int, int]:
    marker = source.find(f">{card_id}</span>")
    if marker < 0:
        raise KeyError(f"Card not found: {card_id}")
    start = source.rfind('<div class="card">', 0, marker)
    if start < 0:
        raise ValueError(f"Card start not found: {card_id}")
    return balanced_div(source, start)


def group_span(source: str, l3_id: str) -> tuple[int, int]:
    marker = f'<div class="l3-group" data-tax-id="{l3_id}">'
    start = source.find(marker)
    if start < 0:
        raise KeyError(f"L3 group not found: {l3_id}")
    return balanced_div(source, start)


def group_for_card(source: str, card_id: str) -> str:
    card_start, _ = card_span(source, card_id)
    matches = list(
        re.finditer(r'<div class="l3-group" data-tax-id="([^"]+)">', source[:card_start])
    )
    if not matches:
        raise ValueError(f"No L3 group before card {card_id}")
    return matches[-1].group(1)


def replace_wording(source: str, card_id: str, label: str, definition: str) -> str:
    start, end = card_span(source, card_id)
    block = source[start:end]
    label_html = html.escape(label, quote=False)
    definition_html = html.escape(definition, quote=False)
    block, label_count = re.subn(
        r'(<span class="card-label">).*?(</span>)',
        rf"\g<1>{label_html}\g<2>",
        block,
        count=1,
        flags=re.S,
    )
    block, definition_count = re.subn(
        r'(<div class="card-def">).*?(</div>)',
        rf"\g<1>{definition_html}\g<2>",
        block,
        count=1,
        flags=re.S,
    )
    if label_count != 1 or definition_count != 1:
        raise RuntimeError(f"Could not update label/definition for {card_id}")
    return source[:start] + block + source[end:]


def move_card(source: str, card_id: str, expected_source: str, target: str) -> str:
    current = group_for_card(source, card_id)
    if current != expected_source:
        raise RuntimeError(f"{card_id}: expected {expected_source}, found {current}")
    start, end = card_span(source, card_id)
    block = source[start:end]
    source = source[:start] + source[end:]

    group_start, group_end = group_span(source, target)
    group = source[group_start:group_end]
    grid_start_rel = group.find('<div class="cards-grid">')
    if grid_start_rel < 0:
        raise RuntimeError(f"cards-grid not found in {target}")
    grid_start = group_start + grid_start_rel
    _, grid_end = balanced_div(source, grid_start)
    closing_start = source.rfind("</div>", grid_start, grid_end)
    insertion = "\n" + block
    return source[:closing_start] + insertion + source[closing_start:]


def card_counts(source: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in re.finditer(r'<div class="l3-group" data-tax-id="([^"]+)">', source):
        l3_id = match.group(1)
        start, end = balanced_div(source, match.start())
        counts[l3_id] = len(re.findall(r'<div class="card(?:"|\s)', source[start:end]))
    return counts


def update_counts(source: str) -> str:
    counts = card_counts(source)
    if len(counts) != 24 or sum(counts.values()) != 182 or min(counts.values()) < 1:
        raise RuntimeError(f"Invalid hierarchy counts: {counts}")

    for l3_id, count in counts.items():
        start, end = group_span(source, l3_id)
        group = source[start:end]
        group, changed = re.subn(
            r'(<span class="l3-count">)\d+(</span>)',
            rf"\g<1>{count}\g<2>",
            group,
            count=1,
        )
        if changed != 1:
            raise RuntimeError(f"Could not update L3 header count for {l3_id}")
        source = source[:start] + group + source[end:]

    l2_members = {
        "P2": [key for key in counts if key.startswith("P3.")],
        "I2": [key for key in counts if key.startswith("I3.")],
        "S2": [key for key in counts if key.startswith("S3.")],
    }
    l2_counts = {key: sum(counts[x] for x in members) for key, members in l2_members.items()}

    for l3_id, count in counts.items():
        l2_id = f"{l3_id[0]}2"
        pct = count / l2_counts[l2_id] * 100
        pattern = re.compile(
            rf'(<span class="tax-id summary-id">{re.escape(l3_id)}</span>.*?'
            rf'</td><td style="color:#555">)\d+(</td><td><div class="bar-wrap">'
            rf'<div class="bar" style="width:)[0-9.]+(%;background:#ccc"></div></div>'
            rf'</td><td style="color:#aaa">)[0-9.]+(%)',
            re.S,
        )
        source, changed = pattern.subn(
            rf"\g<1>{count}\g<2>{pct:.1f}\g<3>{pct:.1f}\g<4>",
            source,
            count=1,
        )
        if changed != 1:
            raise RuntimeError(f"Could not update summary row for {l3_id}")

    total = sum(l2_counts.values())
    for l2_id, count in l2_counts.items():
        pct = count / total * 100
        pattern = re.compile(
            rf'(<span class="tax-id summary-id">{l2_id}</span>.*?'
            rf'</td><td style="font-weight:600">)\d+(</td><td><div class="bar-wrap">'
            rf'<div class="bar" style="width:)[0-9.]+(%;background:[^"]+"></div></div>'
            rf'</td><td style="color:#888">)[0-9.]+(%)',
            re.S,
        )
        source, changed = pattern.subn(
            rf"\g<1>{count}\g<2>{pct:.1f}\g<3>{pct:.1f}\g<4>",
            source,
            count=1,
        )
        if changed != 1:
            raise RuntimeError(f"Could not update summary row for {l2_id}")
    return source


def apply(path: Path, revisions: dict[str, tuple[str, str]]) -> None:
    source = path.read_text(encoding="utf-8")
    for card_id, (label, definition) in revisions.items():
        source = replace_wording(source, card_id, label, definition)
    for card_id, (current, target) in ROBUST_MOVES.items():
        source = move_card(source, card_id, current, target)
    source = update_counts(source)
    path.write_text(source, encoding="utf-8")
    print(f"updated {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path, default=DEFAULT_HTML)
    args = parser.parse_args()
    revisions = parse_revisions()
    for path in args.paths:
        apply(path.resolve(), revisions)


if __name__ == "__main__":
    main()
