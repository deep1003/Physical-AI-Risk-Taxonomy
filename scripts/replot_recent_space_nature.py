#!/usr/bin/env python3
"""Re-render fig_recent_physical_ai_space in a Nature-style layout from the saved
UMAP coordinates (no re-embedding; identical points). Arial, muted palette,
no in-figure title, no axis frame."""
import csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = "/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures"
rows = list(csv.DictReader(open(os.path.join(FIG, "fig_recent_physical_ai_space_coords.csv"))))
def pts(cats):
    xs = [float(r["x"]) for r in rows if r["category"] in cats]
    ys = [float(r["y"]) for r in rows if r["category"] in cats]
    return xs, ys

plt.rcParams.update({"font.family": "Arial", "font.size": 8})
fig, ax = plt.subplots(figsize=(5.6, 4.7))
bx, by = pts({"ai", "ai_infra"})
px, py = pts({"physical_ai"})
rx, ry = pts({"physical_ai_risks"})
ax.scatter(bx, by, s=5, c="#d4d8df", alpha=0.55, edgecolors="none", label=f"AI / AI infra ({len(bx)})")
ax.scatter(px, py, s=11, c="#5f8f86", alpha=0.85, edgecolors="none", label=f"Physical AI ({len(px)})")
ax.scatter(rx, ry, s=13, c="#b5726a", alpha=0.9, edgecolors="none", label=f"Physical AI risks ({len(rx)})")
ax.set_xticks([]); ax.set_yticks([])
for s in ("top", "right", "bottom", "left"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=7.5, loc="upper left", markerscale=1.6, handletextpad=0.4)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(FIG, f"fig_recent_physical_ai_space.{ext}"), dpi=600,
                bbox_inches="tight", facecolor="white")
print("saved fig_recent_physical_ai_space (Nature style, from saved coords)")
