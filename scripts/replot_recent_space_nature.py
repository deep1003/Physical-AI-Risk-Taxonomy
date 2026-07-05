#!/usr/bin/env python3
"""Re-render fig_recent_physical_ai_space from saved UMAP coordinates (no
re-embedding; identical point positions).

Two changes over the equal-count version:
1. Population-proportional foreground sampling. The two emphasized layers are
   drawn in proportion to their 2022-2026 record counts (Physical AI 72,502 vs
   Physical AI Risks 34,773, a 2.09:1 ratio), so the risk layer reads as sparser
   than the Physical AI layer and regions of risk concentration versus gaps are
   legible. The AI / AI-infrastructure backdrop (1,551,113 records) is kept at a
   fixed reduced density as neutral gray context.
2. Stronger colour contrast: gray backdrop, teal Physical AI, saturated red
   Physical AI Risks drawn on top with a thin white edge so points stay distinct
   in dense regions.
"""
import csv, os, random
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = "/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures"
SEED = 20260704

# 2022-2026 window record counts (denominators for proportional sampling)
N_PAI, N_RISK = 72_502, 34_773        # Physical AI, Physical AI Risks
N_BG = 1_551_113                      # AI + AI-infrastructure backdrop

rows = list(csv.DictReader(open(os.path.join(FIG, "fig_recent_physical_ai_space_coords.csv"))))

def sel(cats):
    return [r for r in rows if r["category"] in cats]

def xy(rs):
    return [float(r["x"]) for r in rs], [float(r["y"]) for r in rs]

def strat_subsample(rs, k):
    """Deterministic subsample to k points, stratified by doc_type."""
    if k >= len(rs):
        return rs
    by = {}
    for r in rs:
        by.setdefault(r["doc_type"], []).append(r)
    out, frac = [], k / len(rs)
    rng = random.Random(SEED)
    for dt, group in sorted(by.items()):
        g = group[:]
        rng.shuffle(g)
        out += g[:max(1, round(len(group) * frac))]
    rng.shuffle(out)
    return out[:k]

bg = sel({"ai", "ai_infra"})                 # 946 backdrop points (fixed density)
pai = sel({"physical_ai"})                    # 480 points, kept in full
risk_all = sel({"physical_ai_risks"})         # 480 available
k_risk = round(len(pai) * N_RISK / N_PAI)     # proportional -> ~230
risk = strat_subsample(risk_all, k_risk)

bx, by = xy(bg); px, py = xy(pai); rx, ry = xy(risk)

plt.rcParams.update({"font.family": "Arial", "font.size": 8})
fig, ax = plt.subplots(figsize=(5.6, 4.7))
ax.scatter(bx, by, s=4, c="#c9cdd3", alpha=0.50, edgecolors="none", zorder=1,
           label=f"AI / AI-infrastructure ({N_BG/1e6:.2f}M records)")
ax.scatter(px, py, s=15, c="#2a9d8f", alpha=0.85, edgecolors="none", zorder=2,
           label=f"Physical AI ({N_PAI/1e3:.1f}k records)")
ax.scatter(rx, ry, s=28, c="#e63946", alpha=0.95, edgecolors="white", linewidths=0.3,
           zorder=3, label=f"Physical AI risks ({N_RISK/1e3:.1f}k records)")
ax.set_xticks([]); ax.set_yticks([])
for s in ("top", "right", "bottom", "left"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False, fontsize=7.5, loc="upper left", markerscale=1.4, handletextpad=0.4,
          labelspacing=0.7)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(FIG, f"fig_recent_physical_ai_space.{ext}"), dpi=600,
                bbox_inches="tight", facecolor="white")
print(f"saved fig_recent_physical_ai_space | bg={len(bg)} pai={len(pai)} risk={len(risk)} "
      f"(proportional {len(pai)}:{len(risk)} ~= {N_PAI/N_RISK:.2f}:1)")
