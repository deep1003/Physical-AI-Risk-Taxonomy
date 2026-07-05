#!/usr/bin/env python3
"""Safety-filter (guardrail) decision matrix for Physical AI actions.
Axes: Safety (Safe/Unsafe) x Task Effectiveness (Effective/Ineffective).
Corrects the over-/under-refusal placement (FP on the Safe row, FN on the Unsafe row).
Bilingual (EN/KR); rendered on macOS with a Korean-capable font.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager as fm

# Korean-capable font (macOS)
for cand in ["AppleSDGothicNeo-Regular", "Apple SD Gothic Neo", "AppleGothic", "NanumGothic"]:
    try:
        fm.findfont(cand, fallback_to_default=False); plt.rcParams["font.family"] = cand; break
    except Exception:
        continue
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(9.2, 6.4))
ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis("off")

cells = {
    # (x0,y0): (facecolor, header_en, header_kr, note)  — 3-tone grayscale, black text/edges
    (0, 1): ("#efefef", "Safe · Inefficient", "안전하나 비효율적",
             "Low operational value"),
    (1, 1): ("#ffffff", "Safe · Efficient", "효율적이고 안전한",
             "Desired region"),
    (0, 0): ("#d0d0d0", "Unsafe · Inefficient", "위험하고 비효율적",
             "Worst on both axes"),
    (1, 0): ("#efefef", "Unsafe · Efficient", "효율적이나 위험한",
             "Highest physical-harm risk\n(danger from capability, not incompetence)"),
}
for (x0, y0), (fc, hen, hkr, note) in cells.items():
    ax.add_patch(FancyBboxPatch((x0 + .04, y0 + .04), .92, .92,
                 boxstyle="round,pad=0,rounding_size=0.03",
                 linewidth=1.6, edgecolor="#000000", facecolor=fc, mutation_aspect=1))
    cx, cy = x0 + .5, y0 + .5
    ax.text(cx, cy + .31, hen, ha="center", va="center", fontsize=12.5, fontweight="bold", color="#000000")
    ax.text(cx, cy + .13, hkr, ha="center", va="center", fontsize=10.5, color="#000000")
    ax.text(cx, cy - .19, note, ha="center", va="center", fontsize=8.6, color="#000000", linespacing=1.4)

# axis pole labels
ax.text(-0.06, 1.5, "Safe", ha="right", va="center", fontsize=11.5, fontweight="bold", color="#000000")
ax.text(-0.06, 0.5, "Unsafe", ha="right", va="center", fontsize=11.5, fontweight="bold", color="#000000")
ax.text(0.5, -0.08, "Inefficient", ha="center", va="top", fontsize=11.5, fontweight="bold", color="#000000")
ax.text(1.5, -0.08, "Efficient", ha="center", va="top", fontsize=11.5, fontweight="bold", color="#000000")

# axis titles
ax.text(-0.34, 1.0, "Safety (Harmlessness)", ha="center", va="center", rotation=90, fontsize=12.5, fontweight="bold", color="#000000")
ax.text(1.0, -0.30, "Task Efficiency  ($\\downarrow$ time, $\\downarrow$ energy)", ha="center", va="center", fontsize=12.5, fontweight="bold", color="#000000")

ax.set_title("Harmless and Helpful Tradeoff - Physical AI Actions",
             fontsize=14.5, fontweight="bold", color="#000000", pad=14)
ax.text(1.0, -0.46, "Efficiency is defined given task completion (else minimizing time/energy degenerates to inaction).",
        ha="center", va="center", fontsize=8.2, style="italic", color="#000000")

fig.tight_layout()
out = "/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures/fig_guardrail_matrix"
for ext in ("pdf", "png"):
    fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
print("saved", out)
