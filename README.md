# Physical AI Risk Taxonomy

This repository publishes an interactive L4 risk-card taxonomy for Physical AI systems: embodied AI, humanoids, robots, drones, autonomous vehicles, cyber-physical systems, and other AI systems that perceive, decide, and act in the physical world.

Live page:

- https://deep1003.github.io/Physical-AI-Risk-Taxonomy/

## Contents

- `index.html` — public GitHub Pages entry point for the interactive taxonomy.
- `docs/pai_risk_taxonomy_bilingual_v1.0.html` — versioned copy of the taxonomy HTML.
- `data/l4_cards.csv` and `data/l4_cards.json` — extracted L4 card metadata.
- `data/l4_references.csv` and `data/l4_references.json` — card-level reference and justification table.
- `data/taxonomy_migrations.json` — human-approved hierarchy migration notes.
- `data/three_h_one_r_primary_exceptions_20260628.*` — cards that retain three 3H1R Primary axes with explicit reasons.
- `data/reference_addition_rounds/` — candidate selection, access checks, applied additions, and removed candidates from the reference-enrichment rounds.
- `data/reference_quality_audit/` — low-relevance reference audit and cleanup logs.
- `scripts/` — scripts used to add corpus references and audit reference relevance.
- `methodology/methodology.md` — concise methodology and curation notes.

## Current Snapshot

- L4 cards: 182
- Evidence/justification entries: 321
- Linked references: 314
- Maximum references per L4 card: 5
- L2 card counts: `P2=117`, `I2=39`, `S2=26`

## Taxonomy IDs

The root L1 category is Physical AI. Its three L2 children use short stable IDs: `P2` for Physical Safety, `I2` for Interaction Safety, and `S2` for Societal Safety.

L3 categories inherit the parent L2 ID and add a sequence number, for example `P2.1` for Purposeful / Malicious Harm under Physical Safety. L4 risks keep their original card IDs, such as `PHYSBENCH-REF-0017`.

Human decision on 2026-06-28 moved `S2.10` Lack of Robustness in Unseen Environments to `P2.9`. The category was moved only; absorption into `P2.2` or redistribution remains a future human decision.

## Scope

The taxonomy focuses on Physical AI risks where model behavior can propagate into physical action, sensor-mediated decisions, human-robot interaction, embodied surveillance, safety control, certification, and lifecycle governance.

The repository is separate from `AI_Topic_Space.github.io`; future Physical AI risk taxonomy work should happen here.
