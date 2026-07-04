#!/usr/bin/env python3
"""Convergence + stability validation for the 182 L4 -> 24 L3 assignment.

Embeds the 182 L4 cards (label + definition) with BGE-M3 and studies the
spherical k-means / EM assignment used in the report:
  (A) EM convergence: the within-family cosine objective increases monotonically
      and the assignment stabilizes in a few iterations.
  (B) Assignment stability under Gaussian embedding perturbation: fraction of
      cards that keep their assignment, with the 90/95/97% levels marked.
Also reports permutation-null significance and top-k containment of the released
L3 among the embedding-nearest families. Outputs fig_l4_convergence.{pdf,png}
and l4_convergence_stats.json.
"""
from __future__ import annotations
import csv, json, os
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
from sentence_transformers import SentenceTransformer

REPO = Path("/Users/deep1003/data3/Physical-AI-Risk-Taxonomy")
FIG = REPO / "output/latex/figures"
SEED = 20260704
rng = np.random.default_rng(SEED)

rows = list(csv.DictReader(open(REPO / "data/l4_cards.csv", encoding="utf-8-sig")))
texts = [f"{r['label']}. {r['definition']}" for r in rows]
labels = sorted(set(r["l3_id"] for r in rows)); K = len(labels)
lab2k = {l: i for i, l in enumerate(labels)}
z0 = np.array([lab2k[r["l3_id"]] for r in rows]); N = len(rows)
print(f"cards={N} L3={K}", flush=True)

model = SentenceTransformer("BAAI/bge-m3"); model.max_seq_length = 256
Y = model.encode(texts, batch_size=32, normalize_embeddings=True, convert_to_numpy=True).astype("float64")
Y /= np.linalg.norm(Y, axis=1, keepdims=True) + 1e-12

def centroids(assign, k=K):
    C = np.zeros((k, Y.shape[1]))
    for j in range(k):
        m = assign == j
        if m.any():
            v = Y[m].mean(0); C[j] = v / (np.linalg.norm(v) + 1e-12)
    return C

# ---- (A) EM convergence: objective + assignment stabilization ----
C = centroids(z0); z = z0.copy()
obj_hist, change_hist = [], []
for _ in range(40):
    S = Y @ C.T
    obj_hist.append(float(S[np.arange(N), z].mean()))     # mean within-assignment cosine
    znew = S.argmax(1)
    change_hist.append(int((znew != z).sum()))
    C = centroids(znew)
    if np.array_equal(znew, z):
        z = znew; break
    z = znew
z_hat = z                                                 # model (embedding) assignment
repro = float((z_hat == z0).mean())                       # agreement with expert release
iters = len(obj_hist)

# ---- permutation test: intra-family cohesion of the released partition vs random
#      partitions of identical family sizes (mean cosine of each card to its own centroid) ----
Ccoh = centroids(z0)
obs_cohesion = float((Y * Ccoh[z0]).sum(1).mean())
P = 5000; null_coh = np.zeros(P)
for p in range(P):
    zp = rng.permutation(z0)
    Cp = centroids(zp)
    null_coh[p] = (Y * Cp[zp]).sum(1).mean()
null_mean = float(null_coh.mean())
pval = float(((null_coh >= obs_cohesion).sum() + 1) / (P + 1))

# ---- top-k containment: is the released L3 among the k nearest family centroids ----
Cc = centroids(z0); sims = Y @ Cc.T
order = np.argsort(-sims, axis=1)
rank_of_true = np.array([np.where(order[i] == z0[i])[0][0] for i in range(N)])  # 0-based
topk = {k: float((rank_of_true < k).mean()) for k in (1, 2, 3, 5)}

# ---- (B) stability under Gaussian embedding perturbation (centroids fixed on clean data) ----
Cfix = centroids(z_hat)                                    # stability of the model's own assignment
base = (Y @ Cfix.T).argmax(1)
sigmas = np.linspace(0.0, 0.60, 25); B = 200
stab_mean = np.zeros_like(sigmas); stab_lo = np.zeros_like(sigmas); stab_hi = np.zeros_like(sigmas)
for si, s in enumerate(sigmas):
    ag = np.zeros(B)
    for b in range(B):
        Yp = Y + rng.normal(0, s, Y.shape)
        Yp /= np.linalg.norm(Yp, axis=1, keepdims=True) + 1e-12
        ag[b] = ((Yp @ Cfix.T).argmax(1) == base).mean()
    stab_mean[si] = ag.mean() * 100; stab_lo[si] = np.percentile(ag, 2.5) * 100; stab_hi[si] = np.percentile(ag, 97.5) * 100

def cross(th):
    below = np.where(stab_mean < th)[0]
    return float(sigmas[below[0]]) if len(below) else float(sigmas[-1])
sig_cross = {t: round(cross(t), 3) for t in (97, 95, 90)}

stats = {"n_cards": N, "n_l3": K, "em_iterations_to_converge": iters,
         "embedding_reproduction_pct": round(100 * repro, 1),
         "observed_cohesion": round(obs_cohesion, 4),
         "permutation_null_cohesion_mean": round(null_mean, 4), "permutation_p_value": pval,
         "topk_containment_pct": {k: round(100 * v, 1) for k, v in topk.items()},
         "assignment_stability_sigma_cross": sig_cross}
(FIG / "l4_convergence_stats.json").write_text(json.dumps(stats, indent=2))
print(json.dumps(stats, indent=2), flush=True)

# ---------- figure ----------
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(14.5, 4.2))
TH = {90: "#c1121f", 95: "#bf6f26", 97: "#0f8c7f"}

# (A) EM convergence
it = np.arange(1, iters + 1)
axA.plot(it, obj_hist, "o-", color="#173458", lw=2, ms=4)
ax2 = axA.twinx()
ax2.bar(it, change_hist, color="#c9ced6", alpha=.7, width=.6)
ax2.set_ylabel("cards reassigned", color="#7a7f88")
axA.set_xlabel("EM iteration"); axA.set_ylabel("Objective (mean within-family cosine)")
axA.set_title("(A) EM convergence", fontsize=11); axA.set_xlim(.5, iters + .5)
axA.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)

# (B) top-k containment
ks = [1, 2, 3, 5]; vals = [topk[k] * 100 for k in ks]
axB.bar([f"top-{k}" for k in ks], vals, color="#173458", width=.6)
for i, v in enumerate(vals):
    axB.text(i, v + 0.4, f"{v:.1f}", ha="center", va="bottom", fontsize=9)
for t, c in TH.items():
    axB.axhline(t, ls="--", lw=1, color=c, alpha=.85)
    axB.text(3.6, t, f"{t}%", va="center", ha="left", fontsize=8, color=c)
axB.set_ylabel("Cards with released L3 among nearest families (%)")
axB.set_title("(B) Top-$k$ containment of the released L3", fontsize=11)
axB.set_ylim(80, 101)
for s in ("top", "right"): axB.spines[s].set_visible(False)

# (C) perturbation stability
axC.plot(sigmas, stab_mean, color="#0f8c7f", lw=2, label="mean over 200 perturbations")
axC.fill_between(sigmas, stab_lo, stab_hi, color="#0f8c7f", alpha=.15, label="95% band")
for t, c in TH.items():
    axC.axhline(t, ls="--", lw=1, color=c, alpha=.85)
    axC.text(sigmas[-1], t, f" {t}%", va="center", ha="left", fontsize=8, color=c)
axC.set_xlabel("Gaussian embedding perturbation $\\sigma$")
axC.set_ylabel("Assignment agreement (%)")
axC.set_title("(C) Assignment stability under perturbation", fontsize=11)
axC.set_ylim(0, 102); axC.set_xlim(0, sigmas[-1])
for s in ("top", "right"): axC.spines[s].set_visible(False)
axC.legend(fontsize=8, loc="lower left", frameon=False)

fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(FIG / f"fig_l4_convergence.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
print("saved fig_l4_convergence", flush=True)
