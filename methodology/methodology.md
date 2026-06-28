# Methodology

## 1. Taxonomy Structure

The published taxonomy is a bilingual L4 risk-card view for Physical AI. Each card contains:

- a stable L4 card identifier,
- Korean and English risk label,
- Korean and English risk definition,
- short Korean evidence justifications,
- source references or benchmark links,
- severity and probability proxy values,
- 3H1R alignment tags.

Physical AI is treated as AI deployed in systems that sense, reason, and act in the physical world, including robots, humanoids, drones, autonomous vehicles, CPS, and embodied agents.

L1 is the root Physical AI category. L2 uses `P2`, `I2`, and `S2` to show that Physical Safety, Interaction Safety, and Societal Safety are second-level categories under Physical AI. L3 uses the same domain prefix with level number `3`, such as `P3.1`, `I3.4`, or `P3.9`. L4 risks remain identified by their card IDs.

Human decision on 2026-06-28 moved `S3.10` Lack of Robustness in Unseen Environments from Societal Safety to Physical Safety as `P3.9`. The move does not absorb the category into `P3.2`; absorption or redistribution is deferred to a future human decision.

## 2. 3H1R Alignment Rule

3H1R Primary marks identify the main failure mechanism, not every downstream consequence. A card should normally have one Primary axis and may have at most two Primary axes when there is a clear tradeoff or explicit causal branch.

Three Primary axes are allowed only as documented exceptions. Each exception must state why three axes are simultaneously causal rather than merely downstream. The current exception list is published in `data/three_h_one_r_primary_exceptions_20260628.csv` and `.json`.

## 3. Reference Curation

Reference additions were performed in multiple rounds:

1. candidate papers and reports were collected from local Physical AI risk corpora,
2. references already attached to L4 cards were excluded using title, DOI, and URL keys,
3. candidates were ranked using source clarity, citation count, publication venue, recency, and Physical AI/risk keyword evidence,
4. candidate links were opened with HTTP access checks,
5. matched candidates were attached only when they complemented the L4 risk definition,
6. each L4 card was capped at five references,
7. low-relevance additions were removed after manual quality review.

NeurIPS, ICML, ACL, Nature, Science, and strong robotics/automation venues were prioritized, but final attachment required direct relevance to an L4 definition.

## 4. Justification Style

Evidence justifications are written in short Korean sentences. They explain why a reference matters for the specific L4 card. The same paper may appear on multiple cards only when the justification differs by L4 definition.

Reference lists keep only the reference title and link. Korean explanatory text is kept in the evidence line, not duplicated in the reference list.

## 5. Quality Controls

The curation workflow includes:

- duplicate DOI/title/URL exclusion,
- link access checks,
- card-level max-reference validation,
- low-relevance reference audit,
- manual cleanup of weak matches,
- grammar and citation-name cleanup.

Known residual issue: a small number of cards contain evidence text without a matching link because they originated as curated internal evidence notes. These are tracked in the audit reports.

## 6. Reproducibility Files

The key curation artifacts are:

- `data/reference_addition_rounds/`
- `data/reference_quality_audit/`
- `data/taxonomy_migrations.json`
- `data/three_h_one_r_primary_exceptions_20260628.csv`
- `scripts/add_unreferenced_corpus_refs_to_l4*.py`
- `scripts/audit_low_relevance_l4_references.py`

These scripts assume the original local corpus paths used during construction. The published CSV/JSON files provide the reproducible public snapshot of the final taxonomy state.
