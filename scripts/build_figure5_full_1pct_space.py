#!/usr/bin/env python3
"""Figure 5 (Physical AI document space) rebuilt from a 1% stratified random
sample of the FULL integrated corpus (Table 3 population), all years.

Why this exists
---------------
The report's Table 3 reports the full-corpus counts (AI 3.9M, AI infra 741k,
Physical AI 383k, Physical AI Risks 83k). The earlier Figure 5 used an
equal-per-group cap, so the four groups looked the same size and the 2022-2026
window confused interpretation. This script instead draws the SAME 1% fraction
from every (category x doc_type) stratum of the 5.1M-row integrated index, so the
plotted point counts are proportional to Table 3 by construction, across all
years.

Pipeline (single run): stratified 1% sample -> BGE-M3 embedding -> UMAP 2D ->
scatter. Colours are light tints (no grey); Physical AI and Physical AI Risks are
the emphasised layers, risks drawn on top. "1%" is stated in the legend and the
figure note.

Run (Mac, anaconda python with torch/sentence-transformers/umap/pyarrow):
    /opt/anaconda3/bin/python3 scripts/build_figure5_full_1pct_space.py
Re-plot only (after coords exist, no re-embedding):
    /opt/anaconda3/bin/python3 scripts/build_figure5_full_1pct_space.py --plot-only

Expected sample size ~50,990 points. Embedding ~51k docs on MPS takes roughly
30-60 min; progress is written to build_figure5_full_1pct.log next to the output.
"""
from __future__ import annotations
import argparse, csv, json, os, sys, time, random
from pathlib import Path

ROOT = Path("/Users/deep1003/data3/integrated_ai_document_space_20260704")
IDX_MANIFEST = ROOT / "full_document_embedding_space_bge_m3_20260704" / "index_manifest.json"
IDX_DIR = ROOT / "full_document_embedding_space_bge_m3_20260704" / "index_parts"
FIGDIR = Path("/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/figures")
COORDS = FIGDIR / "fig_recent_physical_ai_space_coords_full1pct.csv"
MANIFEST = FIGDIR / "fig_recent_physical_ai_space_full1pct_manifest.json"
LOG = FIGDIR / "build_figure5_full_1pct.log"
OUT = FIGDIR / "fig_recent_physical_ai_space.pdf"  # replaces the report figure

SEED = 20260704
FRACTION = 0.01          # 1% of each stratum's population
MAX_CHARS = 1200
MAX_SEQ = 256
MODEL = "BAAI/bge-m3"

# light palette (no grey); risks most saturated, drawn last
STYLE = {
    "ai":                ("#d3e4f5", 3,  0.45, 1, "AI"),
    "ai_infra":          ("#e5ddf3", 3,  0.50, 2, "AI infrastructure"),
    "physical_ai":       ("#2a9d8f", 12, 0.85, 3, "Physical AI"),
    "physical_ai_risks": ("#e63946", 20, 0.95, 4, "Physical AI risks"),
}
CAT_TOTAL = {"ai": 3_906_767, "ai_infra": 741_428,
             "physical_ai": 383_149, "physical_ai_risks": 82_971}


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def sample_rows():
    """Return list of dicts (category, doc_type, year, record_id, text) for a
    deterministic 1% stratified sample across all (category x doc_type) parts."""
    import pyarrow.parquet as pq
    manifest = json.loads(IDX_MANIFEST.read_text())["parts"]
    rng = random.Random(SEED)
    picked = []
    # group parts by stratum so the fraction is applied per stratum
    by_stratum = {}
    for p in manifest:
        by_stratum.setdefault((p["category"], p["doc_type"]), []).append(p)
    for (cat, dt), parts in sorted(by_stratum.items()):
        total = sum(p["rows"] for p in parts)
        k = round(total * FRACTION)
        if k <= 0:
            continue
        # choose k global positions within this stratum, then map to parts
        idxs = sorted(rng.sample(range(total), min(k, total)))
        # walk parts in order, translating stratum-local offset -> part-local row
        offset = 0
        ptr = 0
        for p in parts:
            hi = offset + p["rows"]
            want = []
            while ptr < len(idxs) and idxs[ptr] < hi:
                want.append(idxs[ptr] - offset)
                ptr += 1
            if want:
                tbl = pq.read_table(IDX_DIR / p["part"],
                                    columns=["record_id", "category", "doc_type",
                                             "year", "text_for_embedding"])
                rec = tbl.column("record_id").to_pylist()
                yr = tbl.column("year").to_pylist()
                tx = tbl.column("text_for_embedding").to_pylist()
                for r in want:
                    t = (tx[r] or "")[:MAX_CHARS]
                    if len(t.strip()) < 20:
                        continue
                    picked.append({"record_id": rec[r], "category": cat,
                                   "doc_type": dt, "year": yr[r], "text": t})
            offset = hi
        log(f"stratum {cat}/{dt}: {total:,} rows -> sampled ~{k:,}")
    log(f"total sampled with usable text: {len(picked):,}")
    return picked


def embed_and_reduce(rows):
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import umap
    log(f"loading {MODEL} ...")
    model = SentenceTransformer(MODEL, device="mps")
    model.max_seq_length = MAX_SEQ
    texts = [r["text"] for r in rows]
    log(f"embedding {len(texts):,} texts (batch 32, normalized) ...")
    emb = model.encode(texts, batch_size=32, normalize_embeddings=True,
                       show_progress_bar=True, convert_to_numpy=True)
    log(f"embeddings shape {emb.shape}; running UMAP (cosine) ...")
    reducer = umap.UMAP(n_neighbors=35, min_dist=0.05, metric="cosine",
                        random_state=SEED)
    xy = reducer.fit_transform(emb)
    with open(COORDS, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["record_id", "category", "doc_type", "year", "x", "y"])
        for r, (x, y) in zip(rows, xy):
            w.writerow([r["record_id"], r["category"], r["doc_type"], r["year"],
                        f"{x:.5f}", f"{y:.5f}"])
    log(f"wrote coords -> {COORDS}")


def plot():
    import collections
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(COORDS)))
    cnt = collections.Counter(r["category"] for r in rows)
    plt.rcParams.update({"font.family": "Arial", "font.size": 8})
    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    for cat in ("ai", "ai_infra", "physical_ai", "physical_ai_risks"):
        color, s, alpha, z, label = STYLE[cat]
        xs = [float(r["x"]) for r in rows if r["category"] == cat]
        ys = [float(r["y"]) for r in rows if r["category"] == cat]
        ec = "white" if cat == "physical_ai_risks" else "none"
        lw = 0.25 if cat == "physical_ai_risks" else 0
        ax.scatter(xs, ys, s=s, c=color, alpha=alpha, edgecolors=ec, linewidths=lw,
                   zorder=z, rasterized=True,
                   label=f"{label} ({cnt[cat]:,} pts, 1% of {CAT_TOTAL[cat]/1e3:,.0f}k)")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ("top", "right", "bottom", "left"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=7, loc="upper left", markerscale=1.5,
              labelspacing=0.7, title="1% stratified sample (all years)",
              title_fontsize=7.5)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIGDIR / f"fig_recent_physical_ai_space.{ext}", dpi=600,
                    bbox_inches="tight", facecolor="white")
    MANIFEST.write_text(json.dumps({
        "seed": SEED, "fraction": FRACTION, "model": MODEL,
        "plotted_by_category": dict(cnt), "category_population": CAT_TOTAL,
        "note": "1% stratified random sample per (category x doc_type) of the "
                "5,099,045-row integrated index; all years; points proportional "
                "to Table 3 by construction."}, indent=2))
    log(f"plotted counts {dict(cnt)} -> {OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot-only", action="store_true")
    a = ap.parse_args()
    LOG.write_text("")
    if a.plot_only:
        plot(); return
    rows = sample_rows()
    embed_and_reduce(rows)
    plot()


if __name__ == "__main__":
    main()
