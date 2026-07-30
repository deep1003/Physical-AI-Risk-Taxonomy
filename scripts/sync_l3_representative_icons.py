#!/usr/bin/env python3
"""Recompute L3 representative 3H1R icons from L4 Primary-tag shares."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from apply_l4_wording_and_em_moves_20260731 import ROOT, group_span


DEFAULT_HTML = [
    ROOT / "index.html",
    ROOT / "docs" / "pai_risk_taxonomy_bilingual_v2.0.html",
]
AXES = {
    "H1 Harmless": ("H1", "rep-h1", "Harmless"),
    "H2 Helpful": ("H2", "rep-h2", "Helpful"),
    "H3 Honest": ("H3", "rep-h3", "Honest"),
    "RC Role": ("RC", "rep-rc", "Role Consistency"),
}


def balanced_span(source: str, start: int) -> tuple[int, int]:
    depth = 0
    for match in re.finditer(r"<span\b[^>]*>|</span\s*>", source[start:], re.I):
        if match.group(0).lower().startswith("<span"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, start + match.end()
    raise ValueError(f"Unbalanced span at {start}")


def representative(primary_counts: Counter[str]) -> list[str]:
    total = sum(primary_counts.values())
    if total == 0:
        raise ValueError("L3 has no Primary tags")
    shares = {axis: primary_counts[axis] / total for axis in AXES}
    ranked = sorted(AXES, key=lambda axis: (-shares[axis], axis))
    if sum(shares[axis] >= 0.20 for axis in AXES) >= 3:
        return ["Mixed"]
    if shares[ranked[0]] >= 0.60:
        return [ranked[0]]
    if shares[ranked[1]] >= 0.25:
        return ranked[:2]
    return [ranked[0]]


def stack_html(axes: list[str], summary: bool) -> str:
    extra = " summary-rep" if summary else ""
    if axes == ["Mixed"]:
        return (
            f'<span class="rep-stack{extra}" aria-label="대표 3H1R">'
            '<span class="rep-pill rep-mixed" title="대표 3H1R: Mixed 3H1R profile" '
            'aria-label="대표 3H1R Mixed 3H1R profile">Mixed</span></span>'
        )
    pills = []
    for axis in axes:
        short, css, title = AXES[axis]
        pills.append(
            f'<span class="rep-pill {css}" title="대표 3H1R: {title}" '
            f'aria-label="대표 3H1R {title}">{short}</span>'
        )
    return f'<span class="rep-stack{extra}" aria-label="대표 3H1R">{"".join(pills)}</span>'


def replace_stack(source: str, marker_pos: int, new_html: str) -> str:
    start = source.find('<span class="rep-stack', marker_pos)
    if start < 0:
        raise ValueError("Representative stack not found")
    start, end = balanced_span(source, start)
    return source[:start] + new_html + source[end:]


def update(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    l3_ids = re.findall(r'<div class="l3-group" data-tax-id="([^"]+)">', source)
    for l3_id in l3_ids:
        start, end = group_span(source, l3_id)
        group = source[start:end]
        counts: Counter[str] = Counter()
        for axis, rank in re.findall(
            r">(H[123] [^<]+|RC Role)<sup[^>]*>([PS])</sup>", group
        ):
            if rank == "P":
                counts[axis] += 1
        axes = representative(counts)
        source = replace_stack(source, start, stack_html(axes, summary=False))

        summary_marker = source.find(
            f'<span class="tax-id summary-id">{l3_id}</span>'
        )
        if summary_marker < 0:
            raise ValueError(f"Summary row not found: {l3_id}")
        source = replace_stack(source, summary_marker, stack_html(axes, summary=True))
    path.write_text(source, encoding="utf-8")
    print(f"representatives updated {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path, default=DEFAULT_HTML)
    args = parser.parse_args()
    for path in args.paths:
        update(path.resolve())


if __name__ == "__main__":
    main()
