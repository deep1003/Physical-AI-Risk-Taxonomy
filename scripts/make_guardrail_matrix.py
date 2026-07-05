#!/usr/bin/env python3
"""H1-H2 trade-off matrix for Physical AI actions.
Axes: H1 Safety (Safe/Unsafe) x H2 Task Efficiency (Efficient/Inefficient).
Contiguous 2x2 grid; right column leads with 'Efficient'; Korean subtitles in gray.
Rendered on macOS with a Korean-capable font.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager as fm

for cand in ["AppleSDGothicNeo-Regular", "Apple SD Gothic Neo", "AppleGothic", "NanumGothic"]:
    try:
        fm.findfont(cand, fallback_to_default=False); plt.rcParams["font.family"] = cand; break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

INK, NOTE, LINE = "#111111", "#7a7a7a", "#9a9a9a"
fig, ax = plt.subplots(figsize=(9.6, 6.1))
ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis("off")

cells = {
    # (x0,y0): (facecolor, header_en, header_kr, note)
    (0, 1): ("#ededed", "Safe · Inefficient", "(안전하나 비효율적)", "Low operational value"),
    (1, 1): ("#ffffff", "Efficient · Safe", "(효율적이고 안전한)", "Desired region"),
    (0, 0): ("#c4cad6", "Unsafe · Inefficient", "(위험하고 비효율적)", "Worst on both axes"),
    (1, 0): ("#ededed", "Efficient · Unsafe", "(효율적이나 위험한)", "Highest physical-harm risk"),
}
for (x0, y0), (fc, hen, hkr, note) in cells.items():
    ax.add_patch(Rectangle((x0, y0), 1, 1, facecolor=fc, edgecolor=LINE, linewidth=1.0))
    cx, cy = x0 + .5, y0 + .5
    ax.text(cx, cy + .27, hen, ha="center", va="center", fontsize=13, fontweight="bold", color=INK)
    ax.text(cx, cy + .10, hkr, ha="center", va="center", fontsize=11, color=NOTE)
    ax.text(cx, cy - .22, note, ha="center", va="center", fontsize=9.5, color=NOTE)

# axis pole labels (bold black)
ax.text(-0.05, 1.5, "Safe", ha="right", va="center", fontsize=12, fontweight="bold", color=INK)
ax.text(-0.05, 0.5, "Unsafe", ha="right", va="center", fontsize=12, fontweight="bold", color=INK)
ax.text(0.5, -0.09, "Inefficient", ha="center", va="top", fontsize=12, fontweight="bold", color=INK)
ax.text(1.5, -0.09, "Efficient", ha="center", va="top", fontsize=12, fontweight="bold", color=INK)

# axis titles
ax.text(-0.30, 1.0, "H1: Safety", ha="center", va="center", rotation=90, fontsize=13, fontweight="bold", color=INK)
ax.text(1.0, -0.34, "H2: Task Efficiency  ($\\downarrow$ time, $\\downarrow$ energy)", ha="center", va="center", fontsize=13, fontweight="bold", color=INK)

ax.set_title("H1 and H2 Tradeoff - Physical AI Actions",
             fontsize=15.5, fontweight="bold", color=INK, pad=16)

fig.tight_layout()
out = "/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures/fig_guardrail_matrix"
for ext in ("pdf", "png"):
    fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
print("saved", out)
