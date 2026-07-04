#!/usr/bin/env python3
"""BGE-M3 + HDBSCAN hyperparameter robustness on the Physical AI risk subset.

Draws a reproducible sample of Physical AI risk documents (papers/policy/patents),
embeds them with BGE-M3, reduces with UMAP, and clusters with HDBSCAN. Reports how
the cluster structure responds to changes in the main hyperparameters
(min_cluster_size, min_samples, and UMAP n_neighbors) via cluster count, noise
fraction, and Adjusted Rand Index (ARI) vs the baseline configuration.
Outputs a LaTeX table fragment + JSON.
"""
from __future__ import annotations
import csv, gzip, json, os, random
from pathlib import Path
import numpy as np
os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
from sentence_transformers import SentenceTransformer
import umap, hdbscan
from sklearn.metrics import adjusted_rand_score

ROOT = Path("/Users/deep1003/data3")
INTEG = ROOT / "integrated_ai_document_space_20260704"
OUT = ROOT / "Physical-AI-Risk-Taxonomy/output/latex/enrichment"
SEED = 20260704
random.seed(SEED); np.random.seed(SEED)
RISK = {
    "papers": (INTEG / "papers/physical_ai_risks/physical_ai_risks_papers_integrated_dedup.csv.gz", 2600),
    "patents": (INTEG / "patents/physical_ai_risks/physical_ai_risks_patents_integrated_dedup.csv.gz", 1300),
    "policy_reports": (INTEG / "policy_reports/physical_ai_risks/physical_ai_risks_policy_reports_integrated_dedup.csv.gz", 100),
}

def sample_texts(path, cap):
    rows = []
    with gzip.open(path, "rt", encoding="utf-8", errors="ignore") as fh:
        for r in csv.DictReader(fh):
            t = (r.get("text_for_embedding") or "").strip()
            if len(t) < 20:
                t = ((r.get("title") or "") + ". " + (r.get("abstract") or "")).strip()
            if len(t) >= 20:
                rows.append(t[:1200])
    rng = random.Random(f"{SEED}-{path.name}")
    return rng.sample(rows, min(cap, len(rows)))

texts = []
for fam, (p, cap) in RISK.items():
    s = sample_texts(p, cap); texts += s; print(f"{fam}: {len(s)}", flush=True)
print("total texts", len(texts), flush=True)

model = SentenceTransformer("BAAI/bge-m3"); model.max_seq_length = 256
E = model.encode(texts, batch_size=32, normalize_embeddings=True, convert_to_numpy=True).astype("float32")
print("embedded", E.shape, flush=True)

def reduce(nn):
    return umap.UMAP(n_neighbors=nn, min_dist=0.0, n_components=10, metric="cosine",
                     random_state=SEED).fit_transform(E)

def cluster(X, mcs, ms):
    cl = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples=ms, metric="euclidean",
                         cluster_selection_method="eom")
    lab = cl.fit_predict(X)
    nclu = len(set(lab)) - (1 if -1 in lab else 0)
    noise = float((lab == -1).mean())
    return lab, nclu, noise

# baseline
BASE = dict(nn=30, mcs=15, ms=5)
Xb = reduce(BASE["nn"])
lab_base, nclu_b, noise_b = cluster(Xb, BASE["mcs"], BASE["ms"])
print(f"baseline: clusters={nclu_b} noise={noise_b:.2f}", flush=True)

grid = []
# vary min_cluster_size and min_samples on the baseline UMAP
for mcs in (8, 10, 15, 20, 30):
    for ms in (1, 5, 10):
        lab, nclu, noise = cluster(Xb, mcs, ms)
        ari = adjusted_rand_score(lab_base, lab)
        grid.append({"knob": "HDBSCAN", "param": f"mcs={mcs}, ms={ms}", "nclusters": nclu,
                     "noise": round(noise, 3), "ari": round(float(ari), 3)})
# vary UMAP n_neighbors at baseline HDBSCAN
for nn in (15, 30, 50, 80):
    X = reduce(nn)
    lab, nclu, noise = cluster(X, BASE["mcs"], BASE["ms"])
    ari = adjusted_rand_score(lab_base, lab) if nn != BASE["nn"] else 1.0
    grid.append({"knob": "UMAP", "param": f"n_neighbors={nn}", "nclusters": nclu,
                 "noise": round(noise, 3), "ari": round(float(ari), 3)})

stats = {"n_docs": len(texts), "baseline": BASE, "baseline_clusters": nclu_b,
         "baseline_noise": round(noise_b, 3), "grid": grid,
         "ari_min": round(min(g["ari"] for g in grid if g["ari"] < 1.0 or True), 3),
         "ari_median": round(float(np.median([g["ari"] for g in grid])), 3)}
(OUT / "hdbscan_robustness_stats.json").write_text(json.dumps(stats, indent=2))

# LaTeX table
def esc(s): return str(s).replace("_", r"\_")
lines = [r"\begin{tabular}{llrrr}", r"\toprule",
         r"Knob & Setting & Clusters & Noise & ARI vs base \\", r"\midrule"]
for g in grid:
    lines.append(f"{g['knob']} & {esc(g['param'])} & {g['nclusters']} & {g['noise']:.2f} & {g['ari']:.2f} " + r"\\")
lines += [r"\bottomrule", r"\end{tabular}"]
(OUT / "tab_hdbscan_robustness.tex").write_text("\n".join(lines) + "\n")
print(json.dumps(stats, indent=2), flush=True)
print("DONE hdbscan robustness", flush=True)
