# Reproducibility — Physical AI Risk Taxonomy Technical Report

This document describes how to reproduce every result, figure, and table in the
Technical Report (`technical_report.pdf`, source in
`output/latex/physical_ai_risk_taxonomy_methodology.tex`).

The repository is **results-centered**: it ships the report source, the analysis
scripts, the released taxonomy, and every derived figure/table/statistic needed to
regenerate the report. The multi-million-record raw corpora and record-level
intermediate dumps are **not** included (see *Data availability* below); the scripts
and manifests document exactly how they were produced so the results can be
regenerated from the original sources.

## Environment

- Python 3 (Anaconda). Install: `pip install sentence-transformers umap-learn hdbscan scikit-learn numpy pandas matplotlib pyarrow`
- Embedding model: `BAAI/bge-m3` (BGE-M3, dense mode, 1024-d, L2-normalized).
- LaTeX: TeX Live with **xelatex**; fonts Times New Roman + Apple SD Gothic Neo
  (Korean). The report compiles on macOS (`cd output/latex && xelatex ... ×2`).
- Global random seed: **20260704** (used by every stochastic step).

## Pipeline overview

The construction method is a hybrid corpus-to-taxonomy pipeline:
authoritative L0–L3 upper structure → BGE-M3 embedding → HDBSCAN candidate
discovery (Algorithm 1) → reference-grounding + deduplication + human audit →
EM-style L3 assignment (Algorithm 2) → validation. See report §Workflow.

## Scripts → outputs map

| Script | Produces | Report artifact |
|---|---|---|
| `scripts/l4_convergence_sim.py` | `output/latex/figures/fig_l4_convergence.{pdf,png}`, `figures/l4_convergence_stats.json` | Figure 10 (L4→L3 convergence & stability) |
| `scripts/hdbscan_robustness.py` | `output/latex/enrichment/tab_hdbscan_robustness.tex`, `enrichment/hdbscan_robustness_stats.json` | Table 13 (BGE-M3/HDBSCAN robustness) |
| `scripts/make_country_institution_tables.py` | `enrichment/tab_country_top.tex`, `tab_institution_top.tex`, `country_institution_summary.json` | Country/institution result tables |
| `scripts/generate_institution_source_stats.py` | `output/latex/institution_source_*.{tex,csv,json}` | Institution-by-source statistics |
| `scripts/generate_institution_global_korea_stats.py` | `output/latex/institution_{global,korea}_*.{tex,csv,json}` | Global vs. Korea institution stats |
| `scripts/enrich_institution_country.py`, `scripts/enrich_v2.py` | record-level enrichment (raw, not shipped) → the aggregated result tables above | — |
| `scripts/integrate_patents_from_stage3.py` | PATSTAT Stage-3 person-field patent enrichment (raw, not shipped) | Patent country/institution backup |

The `output/latex/enrichment/tab_prior_taxonomies.tex` (Table 1, prior-taxonomy
comparison) is authored from verified sources listed in the report bibliography.
`figures/fig_recent_physical_ai_space.{pdf,png}` (Figure 8) is accompanied by its
`_coords.csv` and `_manifest.json` (sample indices, per-group sample/total, seed) so
the projection is fully reproducible.

## Data availability

Retrieval is reproducible from the preserved queries:
- Patents: PATSTAT SQL in `output/latex/*.sql` (AI retrieval + Physical-AI/risk filters).
- Papers: Web of Science query in `output/latex/wos_query_20260530.txt`.
- Policy/reports: sources documented in the report §Data Sources.

Raw corpora (≈82,971 Physical-AI-risk records across papers/policy/patents, and the
integrated AI document space of ~1.66M 2022–2026 records) and record-level
intermediates (`enriched_*.csv`, API caches, curation rounds) are kept outside the
repository for size/licensing reasons. Every count reported in the paper is
traceable to these sources via the manifests and the scripts above.

## Released taxonomy (`data/`)

- `l4_cards.{csv,json}` — 182 released L4 risk cards (label, bilingual definition,
  L2/L3, severity/probability proxies, 3H1R tags).
- `l4_references.{csv,json}` — per-card evidence references (≤5 per card).
- `taxonomy_summary.json`, `taxonomy_migrations.json` — hierarchy summary and
  migration log.
- `three_h_one_r_primary_exceptions_20260628.{csv,json}` — 3H1R Primary-axis
  exception list used in curation.

## Rebuild the report

```bash
cd output/latex
xelatex -interaction=nonstopmode physical_ai_risk_taxonomy_methodology.tex
xelatex -interaction=nonstopmode physical_ai_risk_taxonomy_methodology.tex   # refs/longtable
```

The live taxonomy interface is `index.html` (GitHub Pages), with the
**Technical Report** button linking to `technical_report.html` → `technical_report.pdf`.
