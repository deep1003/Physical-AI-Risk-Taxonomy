# Physical AI Risk Taxonomy

This repository publishes an interactive L4 risk-card taxonomy for Physical AI systems: embodied AI, humanoids, robots, drones, autonomous vehicles, cyber-physical systems, and other AI systems that perceive, decide, and act in the physical world.

Live page:

- https://deep1003.github.io/Physical-AI-Risk-Taxonomy/

## Contents

- `index.html` — public GitHub Pages entry point for the interactive taxonomy.
- `docs/pai_risk_taxonomy_bilingual_v1.0.html` — versioned copy of the taxonomy HTML.
- `data/l4_cards.csv` and `data/l4_cards.json` — extracted L4 card metadata.
- `data/l4_references.csv` and `data/l4_references.json` — card-level reference and justification table.
- `data/reference_addition_rounds/` — candidate selection, access checks, applied additions, and removed candidates from the reference-enrichment rounds.
- `data/reference_quality_audit/` — low-relevance reference audit and cleanup logs.
- `scripts/` — scripts used to add corpus references and audit reference relevance.
- `methodology/methodology.md` — concise methodology and curation notes.

## Current Snapshot

- L4 cards: 182
- Evidence/justification entries: 321
- Linked references: 314
- Maximum references per L4 card: 5

## Scope

The taxonomy focuses on Physical AI risks where model behavior can propagate into physical action, sensor-mediated decisions, human-robot interaction, embodied surveillance, safety control, certification, and lifecycle governance.

The repository is separate from `AI_Topic_Space.github.io`; future Physical AI risk taxonomy work should happen here.
