#!/usr/bin/env python3
"""Regenerate the released L2/L3 count figure from the canonical JSON export."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "taxonomy_summary.json"
OUTPUT = ROOT / "output" / "latex" / "figures"
COLORS = {"P2": "#6488ad", "I2": "#77a680", "S2": "#927fb3"}


def english_name(value: str) -> str:
    if value.endswith(")") and "(" in value:
        return value[value.rfind("(") + 1 : -1]
    return value


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    l2_counts = {item["l2_id"]: item["l4_count"] for item in summary["hierarchy"]}
    families = []
    for l2 in summary["hierarchy"]:
        for l3 in l2["l3"]:
            families.append(
                {
                    "l2_id": l2["l2_id"],
                    "l3_id": l3["l3_id"],
                    "name": english_name(l3["l3_name"]),
                    "count": l3["exported_l4_count"],
                }
            )
    top = sorted(families, key=lambda row: (-row["count"], row["l3_id"]))[:12]
    top.reverse()

    fig = plt.figure(figsize=(13.5, 6.7), dpi=160)
    ax = fig.add_axes([0.30, 0.12, 0.66, 0.80])
    labels = [f"{row['l3_id']} {row['name']}" for row in top]
    values = [row["count"] for row in top]
    colors = [COLORS[row["l2_id"]] for row in top]
    bars = ax.barh(labels, values, color=colors)
    ax.bar_label(bars, padding=5, fontsize=10)
    ax.set_xlabel("L4 risks per L3 sub-category", fontsize=11)
    ax.set_xlim(0, max(values) * 1.12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=10)
    ax.tick_params(axis="x", labelsize=9)

    inset = fig.add_axes([0.66, 0.17, 0.28, 0.34])
    l2_ids = ["P2", "I2", "S2"]
    l2_values = [l2_counts[key] for key in l2_ids]
    l2_bars = inset.bar(
        l2_ids, l2_values, color=[COLORS[key] for key in l2_ids], width=0.68
    )
    inset.bar_label(l2_bars, padding=2, fontsize=9, fontweight="bold")
    inset.set_title("L2 categories", fontsize=10)
    inset.set_ylim(0, max(l2_values) * 1.25)
    inset.spines[["top", "right"]].set_visible(False)
    inset.tick_params(labelsize=8)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "jpg"):
        fig.savefig(
            OUTPUT / f"fig_taxonomy_levels.{suffix}",
            dpi=240,
            bbox_inches="tight",
            facecolor="white",
        )
    plt.close(fig)
    print(f"wrote {OUTPUT / 'fig_taxonomy_levels.png'}")


if __name__ == "__main__":
    main()
