# Responsible AI Risk Taxonomy v2.0

This repository publishes an interactive Responsible AI risk taxonomy for Physical AI Risks: embodied AI, humanoids, robots, drones, autonomous vehicles, cyber-physical systems, and other AI systems that perceive, decide, and act in the physical world.

Live page:

- https://deep1003.github.io/Physical-AI-Risk-Taxonomy/

## Contents

- `index.html` — master public GitHub Pages entry point for the interactive taxonomy.
- `docs/pai_risk_taxonomy_bilingual_v2.0.html` — versioned copy synced from `index.html` with docs-relative asset paths.
- `data/l4_cards.csv` and `data/l4_cards.json` — extracted L4 card metadata.
- `data/l4_references.csv` and `data/l4_references.json` — card-level reference and justification table.
- `data/taxonomy_migrations.json` — human-approved hierarchy migration notes.
- `data/three_h_one_r_primary_exceptions_20260628.*` — cards that retain three 3H1R Primary axes with explicit reasons.
- `data/reference_addition_rounds/` — candidate selection, access checks, applied additions, and removed candidates from the reference-enrichment rounds.
- `data/reference_quality_audit/` — low-relevance reference audit and cleanup logs.
- `scripts/` — scripts used to add corpus references and audit reference relevance.
- `methodology/methodology.md` — concise methodology and curation notes.
- `expert-survey/` — frozen baseline expert survey, taxonomy version 2.1.
- `expert-survey-revised/` — parallel survey using revised L4 wording and robust EM-supported L3 assignments, taxonomy version 2.2.

## Current Snapshot

- L4 cards: 182
- Evidence/justification entries: 360
- Linked references: 353
- Maximum references per L4 card: 5
- L2 card counts: `P2 System Safety=92`, `I2 Interaction Safety=60`, `S2 Societal Safety=30`

The 2026-07-31 wording audit revised 84 L4 labels or definitions. A constrained EM sensitivity analysis using three embedding models, bilingual and English-only inputs, four L3 seed weights, and 1,000 bootstrap replicates supported two L3 moves: `PHYSBENCH-REF-0065` from `I3.7` to `P3.2`, and `PHYSBENCH-REF-0107` from `I3.6` to `S3.6`. All 24 L3 categories remain populated.

## Taxonomy IDs

The current public slice is organized as `L1 Physical AI Risks` > `L2 Categories` > `L3 Sub-categories` > `L4 Risk Cards`. The three L2 children use short stable IDs: `P2` for System Safety, `I2` for Interaction Safety, and `S2` for Societal Safety.

L3 categories use the same domain prefix and the L3 level number, followed by a local sequence number. For example, `P3.1` means the first L3 category under System Safety. L4 risks keep their original card IDs, such as `PHYSBENCH-REF-0017`.

Human decision on 2026-06-28 moved `S3.10` Lack of Robustness in Unseen Environments to `P3.9`. The category was moved only; absorption into `P3.2` or redistribution remains a future human decision.

Human decision on 2026-07-04 realigned the L2/L3 hierarchy to the master structure: `P2 System Safety` has 5 L3 categories, `I2 Interaction Safety` has 10 L3 categories, and `S2 Societal Safety` has 9 L3 categories. The affected L3 groups were moved as groups, and their L4 cards followed their L3 parent.

## Scope

The taxonomy focuses on Physical AI risks where model behavior can propagate into physical action, sensor-mediated decisions, human-robot interaction, embodied surveillance, safety control, certification, and lifecycle governance.

The repository is separate from `AI_Topic_Space.github.io`; future Physical AI risk taxonomy work should happen here.
