#!/usr/bin/env python3
"""Constrained spherical-EM audit for proposed Physical AI L3 moves.

The audit separates wording effects from placement effects:

1. original wording with released assignments
2. revised wording with released assignments
3. revised wording with proposed assignments

Only predeclared candidate cards may change family during EM. All other cards
remain fixed, preserving the expert-defined 24-family hierarchy. Sensitivity is
evaluated across three local embedding models, English and bilingual text,
family-seed weights, and bootstrap-resampled family centroids.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
import urllib.request
from pathlib import Path

import numpy as np


SEED = 20260731
MODELS = ("bge-m3", "mxbai-embed-large", "nomic-embed-text")
SEED_WEIGHTS = (1.0, 3.0, 5.0, 10.0)
PROPOSED_MOVES = {
    "PHYSBENCH-REF-0065": "P3.2",
    "PHYSBENCH-REF-0107": "S3.6",
    "PHYSRISK-REF-0033": "S3.6",
    "PHYSRISK-REF-0037": "S3.9",
    "PHYSRISK-REF-0055": "S3.6",
}


def normalize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-12)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_bilingual(value: str) -> tuple[str, str]:
    """Return English and Korean from `English (Korean)` proposal text."""
    value = value.strip()
    match = re.match(r"^(.*) \(([^()]*)\)$", value)
    if not match:
        raise ValueError(f"Cannot split bilingual proposal: {value}")
    return match.group(1).strip(), match.group(2).strip()


def parse_review_proposals(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    section = text.split("## 2. 우선 수정 카드", 1)[1].split("## 3. 카드 간 경계 규칙", 1)[0]
    proposals: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        if not line.startswith("| PHYS"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            raise ValueError(f"Unexpected review row: {line}")
        card_id, _, label_value, definition_value = cells
        label_en, label_ko = split_bilingual(label_value)
        definition_en, definition_ko = split_bilingual(definition_value)
        proposals[card_id] = {
            "label_en": label_en,
            "label_ko": label_ko,
            "definition_en": definition_en,
            "definition_ko": definition_ko,
            "label_master": f"{label_ko} ({label_en})",
            "definition_master": f"{definition_ko} ({definition_en})",
        }
    return proposals


def english_fragment(value: str) -> str:
    spans = re.findall(r"\(([^()]*)\)", str(value))
    candidates = [s.strip() for s in spans if re.search(r"[A-Za-z]", s)]
    if candidates:
        return max(candidates, key=lambda s: sum(ch.isascii() for ch in s))
    return str(value).strip()


def load_families(summary_path: Path) -> list[dict]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    families = []
    for parent in summary["hierarchy"]:
        for family in parent["l3"]:
            families.append(
                {
                    "l2_id": parent["l2_id"],
                    "l3_id": family["l3_id"],
                    "l3_name": family["l3_name"],
                    "l3_description": family["l3_description"],
                }
            )
    return sorted(families, key=lambda item: item["l3_id"])


def card_text(card: dict, mode: str) -> str:
    if mode == "english":
        return f"{english_fragment(card['label'])}. {english_fragment(card['definition'])}"
    return f"{card['label']}. {card['definition']}"


def family_text(family: dict, mode: str) -> str:
    if mode == "english":
        return f"{english_fragment(family['l3_name'])}. {english_fragment(family['l3_description'])}"
    return f"{family['l3_name']}. {family['l3_description']}"


def ollama_embed(texts: list[str], model: str, endpoint: str, batch_size: int = 32) -> np.ndarray:
    vectors = []
    for start in range(0, len(texts), batch_size):
        request = urllib.request.Request(
            f"{endpoint}/api/embed",
            data=json.dumps(
                {"model": model, "input": texts[start : start + batch_size]}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=900) as response:
            payload = json.loads(response.read().decode("utf-8"))
        vectors.extend(payload["embeddings"])
    return normalize(np.asarray(vectors, dtype=np.float64))


def seeded_centroids(
    y: np.ndarray,
    z: np.ndarray,
    seed_vectors: np.ndarray,
    seed_weight: float,
    exclude_index: int | None = None,
) -> np.ndarray:
    centroids = np.zeros_like(seed_vectors)
    for family in range(len(seed_vectors)):
        members = np.where(z == family)[0]
        if exclude_index is not None:
            members = members[members != exclude_index]
        vector = seed_weight * seed_vectors[family]
        if len(members):
            vector = vector + y[members].sum(axis=0)
        centroids[family] = vector
    return normalize(centroids)


def constrained_em(
    y: np.ndarray,
    z_initial: np.ndarray,
    seed_vectors: np.ndarray,
    seed_weight: float,
    candidate_allowed: dict[int, tuple[int, int]],
    max_iter: int = 50,
) -> tuple[np.ndarray, list[dict]]:
    z = z_initial.copy()
    candidate_indices = sorted(candidate_allowed)
    history = []
    for iteration in range(max_iter):
        centroids = seeded_centroids(y, z, seed_vectors, seed_weight)
        best_score = -np.inf
        z_new = z.copy()
        for choices in itertools.product((0, 1), repeat=len(candidate_indices)):
            trial = z.copy()
            for index, choice in zip(candidate_indices, choices):
                trial[index] = candidate_allowed[index][choice]
            if np.any(np.bincount(trial, minlength=len(seed_vectors)) == 0):
                continue
            score = float(
                sum(y[index] @ centroids[trial[index]] for index in candidate_indices)
            )
            if score > best_score:
                best_score = score
                z_new = trial
        changed = int((z_new != z).sum())
        objective = float(np.mean(np.sum(y * centroids[z_new], axis=1)))
        history.append({"iteration": iteration + 1, "changed": changed, "objective": objective})
        z = z_new
        if changed == 0:
            break
    return z, history


def assignment_metrics(
    y: np.ndarray,
    z: np.ndarray,
    seed_vectors: np.ndarray,
    seed_weight: float,
) -> dict:
    centroids = seeded_centroids(y, z, seed_vectors, seed_weight)
    similarities = y @ centroids.T
    own = similarities[np.arange(len(y)), z]
    other = similarities.copy()
    other[np.arange(len(y)), z] = -np.inf
    margins = own - other.max(axis=1)
    loo_own = np.zeros(len(y))
    loo_margin = np.zeros(len(y))
    for index in range(len(y)):
        loo_centroids = seeded_centroids(y, z, seed_vectors, seed_weight, exclude_index=index)
        scores = y[index] @ loo_centroids.T
        loo_own[index] = scores[z[index]]
        scores[z[index]] = -np.inf
        loo_margin[index] = loo_own[index] - scores.max()
    family_cohesion = []
    family_margin = []
    for family in range(len(seed_vectors)):
        members = np.where(z == family)[0]
        family_cohesion.append(float(own[members].mean()))
        family_margin.append(float(margins[members].mean()))
    return {
        "micro_cohesion": float(own.mean()),
        "macro_cohesion": float(np.mean(family_cohesion)),
        "micro_margin": float(margins.mean()),
        "macro_margin": float(np.mean(family_margin)),
        "negative_margin_fraction": float((margins < 0).mean()),
        "loo_micro_cohesion": float(loo_own.mean()),
        "loo_micro_margin": float(loo_margin.mean()),
        "loo_negative_margin_fraction": float((loo_margin < 0).mean()),
        "min_family_size": int(min(np.bincount(z, minlength=len(seed_vectors)))),
    }


def move_diagnostics(
    y: np.ndarray,
    z_released: np.ndarray,
    seed_vectors: np.ndarray,
    seed_weight: float,
    cards: list[dict],
    family_index: dict[str, int],
    bootstrap_repeats: int,
    rng: np.random.Generator,
) -> list[dict]:
    rows = []
    for card_id, target_id in PROPOSED_MOVES.items():
        index = next(i for i, card in enumerate(cards) if card["card_id"] == card_id)
        current = int(z_released[index])
        target = family_index[target_id]
        centroids = seeded_centroids(y, z_released, seed_vectors, seed_weight, exclude_index=index)
        current_score = float(y[index] @ centroids[current])
        target_score = float(y[index] @ centroids[target])
        preferences = []
        current_members = np.where(z_released == current)[0]
        current_members = current_members[current_members != index]
        target_members = np.where(z_released == target)[0]
        for _ in range(bootstrap_repeats):
            current_sample = (
                rng.choice(current_members, len(current_members), replace=True)
                if len(current_members)
                else np.asarray([], dtype=int)
            )
            target_sample = (
                rng.choice(target_members, len(target_members), replace=True)
                if len(target_members)
                else np.asarray([], dtype=int)
            )
            current_vector = normalize(
                (seed_weight * seed_vectors[current] + y[current_sample].sum(axis=0))[None, :]
            )[0]
            target_vector = normalize(
                (seed_weight * seed_vectors[target] + y[target_sample].sum(axis=0))[None, :]
            )[0]
            preferences.append(float(y[index] @ target_vector > y[index] @ current_vector))
        rows.append(
            {
                "card_id": card_id,
                "current_l3": cards[index]["l3_id"],
                "target_l3": target_id,
                "current_similarity": current_score,
                "target_similarity": target_score,
                "target_minus_current": target_score - current_score,
                "bootstrap_target_preference": float(np.mean(preferences)),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path("/Users/deep1003/data3/Physical-AI-Risk-Taxonomy"),
    )
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--bootstrap-repeats", type=int, default=1000)
    args = parser.parse_args()

    repo = args.repo.resolve()
    source_path = repo / "data/l4_cards.json"
    review_path = repo / "expert-survey/analysis/l4_wording_boundary_review_20260731.md"
    summary_path = repo / "data/taxonomy_summary.json"
    output_dir = repo / "output/l3_reassignment_em_20260731"
    output_dir.mkdir(parents=True, exist_ok=True)

    cards_original = json.loads(source_path.read_text(encoding="utf-8"))
    proposals = parse_review_proposals(review_path)
    cards_revised = [dict(card) for card in cards_original]
    for card in cards_revised:
        proposal = proposals.get(card["card_id"])
        if proposal:
            card["label"] = proposal["label_master"]
            card["definition"] = proposal["definition_master"]
            card["wording_revision"] = "l4_wording_boundary_review_20260731"

    families = load_families(summary_path)
    family_index = {family["l3_id"]: i for i, family in enumerate(families)}
    z_released = np.asarray([family_index[card["l3_id"]] for card in cards_original], dtype=int)
    z_proposed = z_released.copy()
    for card_id, target_id in PROPOSED_MOVES.items():
        index = next(i for i, card in enumerate(cards_revised) if card["card_id"] == card_id)
        z_proposed[index] = family_index[target_id]

    candidate_allowed = {}
    for card_id, target_id in PROPOSED_MOVES.items():
        index = next(i for i, card in enumerate(cards_revised) if card["card_id"] == card_id)
        candidate_allowed[index] = (int(z_released[index]), family_index[target_id])

    results = {}
    metric_rows = []
    move_rows = []
    rng = np.random.default_rng(SEED)
    for model in MODELS:
        results[model] = {}
        for mode in ("bilingual", "english"):
            original_texts = [card_text(card, mode) for card in cards_original]
            revised_texts = [card_text(card, mode) for card in cards_revised]
            family_texts = [family_text(family, mode) for family in families]
            cache_path = output_dir / f"embeddings_{model}_{mode}.npy"
            expected_rows = len(original_texts) + len(revised_texts) + len(family_texts)
            if cache_path.exists():
                embedded = np.load(cache_path)
                if len(embedded) != expected_rows:
                    raise ValueError(f"Stale embedding cache: {cache_path}")
            else:
                embedded = ollama_embed(
                    original_texts + revised_texts + family_texts, model, args.endpoint
                )
                np.save(cache_path, embedded)
            n_cards = len(cards_original)
            y_original = embedded[:n_cards]
            y_revised = embedded[n_cards : 2 * n_cards]
            family_vectors = embedded[2 * n_cards :]
            model_result = {}
            for seed_weight in SEED_WEIGHTS:
                em_assignment, history = constrained_em(
                    y_revised,
                    z_released,
                    family_vectors,
                    seed_weight,
                    candidate_allowed,
                )
                scenario_metrics = {
                    "original_released": assignment_metrics(
                        y_original, z_released, family_vectors, seed_weight
                    ),
                    "revised_released": assignment_metrics(
                        y_revised, z_released, family_vectors, seed_weight
                    ),
                    "revised_proposed": assignment_metrics(
                        y_revised, z_proposed, family_vectors, seed_weight
                    ),
                    "revised_em": assignment_metrics(
                        y_revised, em_assignment, family_vectors, seed_weight
                    ),
                }
                diagnostics = move_diagnostics(
                    y_revised,
                    z_released,
                    family_vectors,
                    seed_weight,
                    cards_original,
                    family_index,
                    args.bootstrap_repeats,
                    rng,
                )
                model_result[str(seed_weight)] = {
                    "em_history": history,
                    "em_assignments": {
                        cards_original[index]["card_id"]: families[int(em_assignment[index])]["l3_id"]
                        for index in candidate_allowed
                    },
                    "metrics": scenario_metrics,
                    "move_diagnostics": diagnostics,
                }
                for scenario, metrics in scenario_metrics.items():
                    metric_rows.append(
                        {
                            "model": model,
                            "text_mode": mode,
                            "seed_weight": seed_weight,
                            "scenario": scenario,
                            **metrics,
                        }
                    )
                for row in diagnostics:
                    move_rows.append(
                        {
                            "model": model,
                            "text_mode": mode,
                            "seed_weight": seed_weight,
                            **row,
                        }
                    )
            results[model][mode] = model_result

    # Aggregate sensitivity support for each proposed movement.
    move_summary = {}
    for card_id in PROPOSED_MOVES:
        subset = [row for row in move_rows if row["card_id"] == card_id]
        move_summary[card_id] = {
            "current_l3": subset[0]["current_l3"],
            "target_l3": subset[0]["target_l3"],
            "runs": len(subset),
            "target_similarity_preferred_runs": int(
                sum(row["target_minus_current"] > 0 for row in subset)
            ),
            "mean_target_minus_current": float(
                np.mean([row["target_minus_current"] for row in subset])
            ),
            "min_target_minus_current": float(
                np.min([row["target_minus_current"] for row in subset])
            ),
            "max_target_minus_current": float(
                np.max([row["target_minus_current"] for row in subset])
            ),
            "mean_bootstrap_target_preference": float(
                np.mean([row["bootstrap_target_preference"] for row in subset])
            ),
        }

    manifest = {
        "run_id": "PAI-L3-EM-20260731",
        "seed": SEED,
        "source_l4_sha256": sha256(source_path),
        "review_sha256": sha256(review_path),
        "n_cards": len(cards_original),
        "n_families": len(families),
        "n_wording_revisions": len(proposals),
        "proposed_moves": PROPOSED_MOVES,
        "models": MODELS,
        "text_modes": ["bilingual", "english"],
        "seed_weights": SEED_WEIGHTS,
        "bootstrap_repeats": args.bootstrap_repeats,
        "scope_note": (
            "Internal semantic-cohesion and placement-sensitivity audit. "
            "It does not estimate external taxonomy validity."
        ),
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "em_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "move_sensitivity_summary.json").write_text(
        json.dumps(move_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "candidate_l4_cards.json").write_text(
        json.dumps(cards_revised, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_csv(output_dir / "scenario_metrics.csv", metric_rows)
    write_csv(output_dir / "move_sensitivity.csv", move_rows)
    print(json.dumps({"manifest": manifest, "move_summary": move_summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
