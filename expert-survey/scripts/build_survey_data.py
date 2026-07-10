#!/usr/bin/env python3
"""Build the blinded bilingual survey snapshot and balanced rater assignments."""

from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_CARDS = ROOT / "data" / "l4_cards.json"
SOURCE_SUMMARY = ROOT / "data" / "taxonomy_summary.json"
OUTPUT = ROOT / "expert-survey" / "data"
RATERS = [f"A{i:02d}" for i in range(1, 10)]
SEED = 20260710

EASY_L3 = {
    "P3.1": ("의도하지 않은 피해", "시스템의 목표 설정, 상황 이해 또는 현실 적용 오류로 예상하지 못한 물리적 피해가 생기는 위험."),
    "P3.2": ("로봇 움직임·제어 오류", "로봇의 움직임, 힘, 속도 또는 이동 경로를 잘못 제어해 충돌이나 피해가 생기는 위험."),
    "P3.3": ("하드웨어·기계 고장", "부품의 마모, 파손, 과열 또는 전력 문제로 로봇이 안전하게 작동하지 못하는 위험."),
    "P3.4": ("소프트웨어·설계 결함", "프로그램 오류, 빠진 예외 처리 또는 불충분한 시험 때문에 잘못된 판단이나 동작이 생기는 위험."),
    "P3.5": ("낯선 환경에서의 작동 실패", "학습하지 않은 장소나 조건에서 로봇이 상황에 적응하지 못해 이동·조작 오류를 일으키는 위험."),
    "I3.1": ("고의적·악의적 이용", "사람이 안전장치를 우회하거나 시스템을 속여 고의로 위험한 행동을 유도하는 위험."),
    "I3.2": ("로봇에 대한 물리적 공격", "기기 변조, 부품 조작 또는 무기 부착처럼 로봇에 직접 가해지는 공격으로 안전 기능이 무력화되는 위험."),
    "I3.3": ("해킹·네트워크 공격", "네트워크, 클라우드 또는 연결 장치가 공격받아 로봇이 탈취되거나 위험하게 움직이는 위험."),
    "I3.4": ("센서·입력 확인 실패", "센서 고장, 위조된 신호 또는 잘못된 입력을 걸러내지 못해 위험한 행동으로 이어지는 위험."),
    "I3.5": ("잘못된 정보 생성·이해", "시스템이 사실과 다른 정보를 만들거나 상황을 잘못 이해해 위험한 행동 계획을 세우는 위험."),
    "I3.6": ("변화하는 환경에 대한 대응 실패", "날씨, 가림, 조명 또는 주변 움직임의 변화 때문에 상황을 잘못 파악하고 행동하는 위험."),
    "I3.7": ("사람과 함께 일할 때의 안전 실패", "사람과 같은 공간에서 일하는 로봇이 안전거리, 정지 또는 개입 절차를 지키지 못하는 위험."),
    "I3.8": ("사람의 지시를 잘못 이해함", "자연어 지시나 안전 원칙을 잘못 해석해 사용자의 의도와 다른 위험한 행동을 하는 위험."),
    "I3.9": ("여러 로봇의 협력 실패", "여러 로봇이 통신하거나 역할을 나누는 과정에서 충돌·혼선·집단 위험이 생기는 문제."),
    "I3.10": ("상호작용형 에이전트의 윤리·안전 문제", "사람과 대화하고 행동하는 에이전트가 부적절하게 개입해 자율성, 존엄성 또는 안전을 해치는 위험."),
    "S3.1": ("개인정보·사생활 침해", "이동형 센서와 카메라가 동의 없이 행동, 생체정보 또는 사적 공간을 수집·감시하는 위험."),
    "S3.2": ("일자리 감소·노동 대체", "피지컬 AI가 사람의 일을 대체하면서 일자리와 노동시장에 부정적인 영향을 주는 위험."),
    "S3.3": ("사회·경제적 격차 확대", "피지컬 AI에 접근하거나 혜택을 얻는 정도의 차이가 소득과 기회의 격차를 키우는 위험."),
    "S3.4": ("권한과 영향력의 집중", "피지컬 AI를 소유·감시·운영하는 권한이 일부 기업이나 국가에 지나치게 집중되는 위험."),
    "S3.5": ("편향된 판단과 차별", "데이터나 모델의 편향이 현실의 서비스 배제 또는 차별적 행동으로 나타나는 위험."),
    "S3.6": ("사고 책임과 보상 주체의 불명확성", "자율 시스템 사고가 발생했을 때 제조사, 운영자 또는 모델 제공자 중 누가 책임지고 보상할지 불분명한 위험."),
    "S3.7": ("설명 부족과 신뢰 저하", "로봇이 왜 그런 행동을 했는지 설명하기 어렵거나 정체가 불분명해 신뢰가 낮아지는 위험."),
    "S3.8": ("사람과 AI 사이의 해로운 관계", "사람과 닮은 외형이나 행동 때문에 지나친 의존, 애착, 조종 또는 심리적 피해가 생기는 위험."),
    "S3.9": ("사회 구조를 크게 바꾸는 영향", "기술 발전과 확산이 너무 빨라 사회 제도와 규칙이 따라가지 못하고 사회 질서가 크게 바뀌는 위험."),
}

PAIRWISE_NEIGHBORS = {
    "P3.1": ["P3.2", "P3.4", "P3.5"], "P3.2": ["P3.1", "P3.3", "P3.5"],
    "P3.3": ["P3.2", "P3.4"], "P3.4": ["P3.1", "P3.3", "P3.5"], "P3.5": ["P3.1", "P3.2", "P3.4"],
    "I3.1": ["I3.2", "I3.3", "I3.4"], "I3.2": ["I3.1", "I3.3"], "I3.3": ["I3.1", "I3.2", "I3.4"],
    "I3.4": ["I3.3", "I3.5", "I3.6"], "I3.5": ["I3.4", "I3.8", "I3.10"], "I3.6": ["I3.4", "I3.7", "I3.9"],
    "I3.7": ["I3.6", "I3.8", "I3.10"], "I3.8": ["I3.5", "I3.7", "I3.10"], "I3.9": ["I3.6", "I3.7"],
    "I3.10": ["I3.5", "I3.7", "I3.8"],
    "S3.1": ["S3.4", "S3.7", "S3.8"], "S3.2": ["S3.3", "S3.9"], "S3.3": ["S3.2", "S3.4", "S3.9"],
    "S3.4": ["S3.1", "S3.3", "S3.6"], "S3.5": ["S3.3", "S3.7"], "S3.6": ["S3.4", "S3.7", "S3.9"],
    "S3.7": ["S3.1", "S3.5", "S3.6"], "S3.8": ["S3.1", "S3.5", "S3.9"], "S3.9": ["S3.2", "S3.3", "S3.6"],
}

PLAIN_KOREAN_REPLACEMENTS = {
    "강건성": "안정적인 작동 능력", "미학습": "처음 접하는", "우발적": "의도하지 않은",
    "액추에이터": "구동장치", "가드레일": "안전장치", "스푸핑": "신호 위조",
    "환각": "사실과 다른 정보 생성", "내비게이션": "이동 경로 탐색", "탈옥": "안전 제한 우회",
    "적대적": "공격성", "정렬 실패": "목표와 안전 원칙의 불일치", "책임·배상": "책임과 보상",
    "투명성·설명 가능성": "행동 과정과 이유의 설명", "프로토콜": "절차", "멀티 에이전트": "여러 에이전트",
}


def plain_korean(value: str) -> str:
    for difficult, plain in PLAIN_KOREAN_REPLACEMENTS.items():
        value = value.replace(difficult, plain)
    return value


def distractor_for(card: dict) -> str:
    candidates = PAIRWISE_NEIGHBORS[card["l3_id"]]
    digest = hashlib.sha256(card["card_id"].encode()).digest()
    return candidates[digest[0] % len(candidates)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_bilingual(value: str) -> tuple[str, str]:
    value = value.strip()
    boundary = value.rfind("(")
    if value.endswith(")") and boundary > 0:
        korean, english = value[:boundary], value[boundary + 1 :]
        return korean.strip(), english[:-1].strip()
    return value, value


def allocate(cards: list[dict]) -> dict[str, list[str]]:
    """Greedy L3-stratified assignment: 3 ratings/card, loads differ by <= 1."""
    rng = random.Random(SEED)
    by_family: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        by_family[card["l3_id"]].append(card)
    for family_cards in by_family.values():
        rng.shuffle(family_cards)

    assignments = {rater: [] for rater in RATERS}
    family_loads = {rater: Counter() for rater in RATERS}
    pair_loads: Counter[tuple[str, str]] = Counter()

    families = sorted(by_family, key=lambda key: (-len(by_family[key]), key))
    for family in families:
        for card in by_family[family]:
            candidates = []
            for i, a in enumerate(RATERS):
                for b in RATERS[i + 1 :]:
                    for c in RATERS[RATERS.index(b) + 1 :]:
                        trio = (a, b, c)
                        score = (
                            sum(family_loads[r][family] for r in trio),
                            sum(len(assignments[r]) for r in trio),
                            pair_loads[(a, b)] + pair_loads[(a, c)] + pair_loads[(b, c)],
                            rng.random(),
                        )
                        candidates.append((score, trio))
            _, trio = min(candidates)
            for rater in trio:
                assignments[rater].append(card["card_id"])
                family_loads[rater][family] += 1
            for pair in ((trio[0], trio[1]), (trio[0], trio[2]), (trio[1], trio[2])):
                pair_loads[pair] += 1

    for rater, card_ids in assignments.items():
        random.Random(f"{SEED}-{rater}").shuffle(card_ids)
    return assignments


def main() -> None:
    cards = json.loads(SOURCE_CARDS.read_text(encoding="utf-8"))
    summary = json.loads(SOURCE_SUMMARY.read_text(encoding="utf-8"))
    families = []
    for l2 in summary["hierarchy"]:
        for l3 in l2["l3"]:
            ko_name, en_name = split_bilingual(l3["l3_name"])
            ko_desc, en_desc = split_bilingual(l3["l3_description"])
            families.append(
                {
                    "id": l3["l3_id"],
                    "l2_id": l2["l2_id"],
                    "l2_name_en": l2["l2_name"],
                    "l2_name_ko": l2["l2_korean_label"],
                    "name_ko": EASY_L3[l3["l3_id"]][0],
                    "name_en": en_name,
                    "definition_ko": EASY_L3[l3["l3_id"]][1],
                    "definition_en": en_desc,
                }
            )

    blinded_cards = []
    for index, card in enumerate(cards, start=1):
        ko_label, en_label = split_bilingual(card["label"])
        ko_definition, en_definition = split_bilingual(card["definition"])
        blinded_cards.append(
            {
                "card_id": card["card_id"],
                "display_id": f"V{index:03d}",
                "label_ko": plain_korean(ko_label),
                "label_en": en_label,
                "definition_ko": plain_korean(ko_definition),
                "definition_en": en_definition,
                "pair_family_ids": [card["l3_id"], distractor_for(card)],
            }
        )

    assignments = allocate(cards)
    counts = Counter(card_id for ids in assignments.values() for card_id in ids)
    assert len(cards) == 182
    assert len(families) == 24
    assert set(counts.values()) == {3}
    loads = [len(ids) for ids in assignments.values()]
    assert max(loads) - min(loads) <= 1

    OUTPUT.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "survey_version": "2.0.0-pairwise",
        "generated_on": "2026-07-10",
        "source_sha256": sha256(SOURCE_CARDS),
        "families": families,
        "cards": blinded_cards,
    }
    (OUTPUT / "survey-data.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    assignment_payload = {
        "assignment_version": "BIBD-20260710-v1",
        "seed": SEED,
        "raters": assignments,
    }
    (OUTPUT / "assignments.json").write_text(
        json.dumps(assignment_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"families={len(families)} cards={len(cards)} ratings={sum(loads)} loads={loads}")


if __name__ == "__main__":
    main()
