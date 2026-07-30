# L3 Reassignment EM Sensitivity Report

## Scope

This audit tests whether five boundary-review candidates should move to a different L3 family after 84 L4 labels or definitions were revised. It evaluates internal semantic consistency. It does not estimate external construct validity.

## Design

- L4 risks: 182
- L3 families: 24
- embedding models: BGE-M3, mxbai-embed-large, nomic-embed-text
- text modes: bilingual Korean-English and English-only
- L3 seed weights: 1, 3, 5, 10
- sensitivity conditions: 24
- bootstrap replicates per candidate and condition: 1,000
- EM form: unit-normalized spherical nearest-centroid E-step and normalized centroid M-step
- structural constraint: every L3 must retain at least one L4
- release rule: the same target must be selected by constrained EM in at least 80% of the 24 conditions

## Candidate results

| L4 risk | Released L3 | Candidate L3 | Target similarity preferred | Mean bootstrap target preference | Constrained EM target selection | Decision |
|---|---|---|---:|---:|---:|---|
| PHYSBENCH-REF-0065 | I3.7 | P3.2 | 24/24 | 0.997 | 20/24 | Move |
| PHYSBENCH-REF-0107 | I3.6 | S3.6 | 24/24 | 0.979 | 23/24 | Move |
| PHYSRISK-REF-0033 | I3.6 | S3.6 | 23/24 | 0.814 | 10/24 | Retain |
| PHYSRISK-REF-0037 | P3.3 | S3.9 | 0/24 | 0.000 | 0/24 | Retain |
| PHYSRISK-REF-0055 | S3.9 | S3.6 | 24/24 | 1.000 | 0/24 under non-empty constraint | Retain |

`PHYSRISK-REF-0055` is semantically closer to S3.6 in isolation, but it is the only L4 assigned to S3.9. Moving it would remove an entire human-defined L3 family. It therefore remains in S3.9 pending a separate human decision on the S3.9 family boundary.

## Performance comparison

The comparison below isolates assignment effects by holding the revised wording constant.

| Metric | Revised wording, released L3 | Revised wording, constrained EM | Change |
|---|---:|---:|---:|
| Micro cohesion | 0.811584 | 0.812148 | +0.000564 |
| Macro cohesion | 0.810807 | 0.811066 | +0.000259 |
| Micro assignment margin | 0.025601 | 0.026731 | +4.41% |
| Macro assignment margin | 0.031159 | 0.031610 | +1.45% |
| Negative-margin fraction | 0.246566 | 0.234203 | -5.01% |
| Leave-one-out micro cohesion | 0.780581 | 0.781258 | +0.000677 |
| Leave-one-out micro margin | -0.005402 | -0.004159 | +0.001243 |
| Leave-one-out negative-margin fraction | 0.513507 | 0.503434 | -1.96% |

The released moves improve all eight internal metrics. The absolute cohesion gain is small because only two of 182 L4 risks moved. The more diagnostic assignment margin improves by 4.41%, while the negative-margin fraction falls by 5.01%.

## Released hierarchy

- P2 System Safety: 92 L4 risks
- I2 Interaction Safety: 60 L4 risks
- S2 Societal Safety: 30 L4 risks
- L3 families: 24, all non-empty

## Reproducibility

Primary files:

- `scripts/run_l3_reassignment_em_20260731.py`
- `output/l3_reassignment_em_20260731/run_manifest.json`
- `output/l3_reassignment_em_20260731/em_results.json`
- `output/l3_reassignment_em_20260731/scenario_metrics.csv`
- `output/l3_reassignment_em_20260731/move_sensitivity.csv`
- `output/l3_reassignment_em_20260731/move_sensitivity_summary.json`
