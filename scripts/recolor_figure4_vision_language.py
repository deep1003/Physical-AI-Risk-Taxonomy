#!/usr/bin/env python3
"""Recolour Figure 4 (document space) without re-embedding.

Palette request:
  - AI infrastructure  -> pure grey
  - AI (Vision group)  -> light blue tint
  - AI (Language group)-> light green tint
  - AI (other)         -> very light grey (recedes)
  - Physical AI        -> medium coral (same family as risks)
  - Physical AI Risks  -> very dark crimson, drawn on top so it pops

The AI records are split into Vision / Language / other by keyword matching on
their titles, fetched by record_id from the integrated index parquets. Point
coordinates are reused from the existing 1% sample coords file.
"""
import csv, json, re
from pathlib import Path
import pyarrow.parquet as pq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/deep1003/data3/integrated_ai_document_space_20260704")
IDXMAN = ROOT / "full_document_embedding_space_bge_m3_20260704" / "index_manifest.json"
IDXDIR = ROOT / "full_document_embedding_space_bge_m3_20260704" / "index_parts"
FIG = Path("/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures")
COORDS = FIG / "fig_recent_physical_ai_space_coords_full1pct.csv"

VISION = re.compile(r"\b(image|images|imaging|vision|visual|object detection|"
    r"segmentation|recognition|video|camera|ocr|scene|depth|pose|optical flow|"
    r"face|facial|remote sensing|super-resolution|point cloud|lidar|cnn|"
    r"convolutional|semantic segmentation|image classification|medical imag|"
    r"visual question)\b", re.I)
LANGUAGE = re.compile(r"\b(language|linguistic|nlp|natural language|text|textual|"
    r"llm|large language model|translation|sentiment|bert|gpt|dialogue|dialog|"
    r"question answering|summariz|summaris|speech|named entity|word embedding|"
    r"machine translation|chatbot|semantic parsing|text classification|"
    r"language model)\b", re.I)


def classify(title):
    t = title or ""
    v = len(VISION.findall(t)); l = len(LANGUAGE.findall(t))
    if v == 0 and l == 0:
        return "ai_other"
    return "ai_vision" if v >= l else "ai_language"


def main():
    rows = list(csv.DictReader(open(COORDS)))
    ai_ids = {r["record_id"] for r in rows if r["category"] == "ai"}
    print(f"AI points to classify: {len(ai_ids):,}")

    # fetch titles for AI record_ids from the AI index parts only
    parts = json.loads(IDXMAN.read_text())["parts"]
    ai_parts = [p["part"] for p in parts if p["category"] == "ai"]
    title = {}
    for i, pt in enumerate(ai_parts):
        tb = pq.read_table(IDXDIR / pt, columns=["record_id", "title"])
        recs = tb.column("record_id").to_pylist()
        tis = tb.column("title").to_pylist()
        for rid, ti in zip(recs, tis):
            if rid in ai_ids:
                title[rid] = ti
        if (i + 1) % 10 == 0:
            print(f"  scanned {i+1}/{len(ai_parts)} AI parts, matched {len(title):,}")
    print(f"titles matched: {len(title):,}/{len(ai_ids):,}")

    sub = {}
    for r in rows:
        c = r["category"]
        if c == "ai":
            sub[r["record_id"]] = classify(title.get(r["record_id"], ""))
        else:
            sub[r["record_id"]] = c
    # augmented coords
    out = FIG / "fig_recent_physical_ai_space_coords_full1pct_subgroups.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["record_id", "subgroup", "x", "y"])
        for r in rows:
            w.writerow([r["record_id"], sub[r["record_id"]], r["x"], r["y"]])

    import collections
    cnt = collections.Counter(sub.values())
    print("subgroup counts:", dict(cnt))

    # ---- plot ----
    STYLE = [  # order = draw order (bottom first)
        ("ai_other",          "#dadde1", 3,   0.30, "AI other"),
        ("ai_infra",          "#9aa0a6", 3.5, 0.40, "AI infrastructure"),
        ("ai_vision",         "#a9c9e8", 3.5, 0.55, "AI (vision)"),
        ("ai_language",       "#b7d9ad", 3.5, 0.55, "AI (language)"),
        ("physical_ai",       "#e07a5f", 11,  0.82, "Physical AI"),
        ("physical_ai_risks", "#5c0a16", 21,  0.98, "Physical AI risks"),
    ]
    pts = {k: ([], []) for k, *_ in STYLE}
    for r in rows:
        g = sub[r["record_id"]]
        pts[g][0].append(float(r["x"])); pts[g][1].append(float(r["y"]))
    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    fig, ax = plt.subplots(figsize=(6.4, 5.1))
    for g, color, s, alpha, label in STYLE:
        xs, ys = pts[g]
        ec = "white" if g == "physical_ai_risks" else "none"
        lw = 0.25 if g == "physical_ai_risks" else 0
        ax.scatter(xs, ys, s=s, c=color, alpha=alpha, edgecolors=ec, linewidths=lw,
                   rasterized=True, label=f"{label} ({len(xs):,})")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ("top", "right", "bottom", "left"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=6.8, loc="upper left", markerscale=1.5,
              labelspacing=0.6, title="1% stratified sample (all years)",
              title_fontsize=7.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig_recent_physical_ai_space.{ext}", dpi=600,
                    bbox_inches="tight", facecolor="white")
    (FIG / "fig_recent_physical_ai_space_full1pct_manifest.json").write_text(
        json.dumps({"fraction": 0.01, "seed": 20260704, "subgroup_counts": dict(cnt),
                    "note": "AI split into vision/language/other by title keywords; "
                    "AI infra pure grey; Physical AI coral and Physical AI Risks dark "
                    "crimson (same family)."}, indent=2))
    print("saved recoloured fig_recent_physical_ai_space.pdf/png")


if __name__ == "__main__":
    main()
