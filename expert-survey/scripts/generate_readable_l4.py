#!/usr/bin/env python3
"""Generate survey-only plain-Korean L4 labels and definitions with local Ollama."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "l4_cards.json"
OUTPUT = ROOT / "expert-survey" / "data" / "readable-l4-ko.json"
MODEL = "qwen3:4b"
BATCH_SIZE = 4


SYSTEM = """당신은 로봇 안전 분야의 한국어 학술 편집자다. Physical AI 전문가 설문에 쓰일 L4 위험 설명을, 대학 교양 수준의 비전문가도 편안하게 읽을 수 있는 정확한 한국어로 다듬는다.
규칙:
1. 영어 원문의 의미, 조건, 주체, 실패 방식과 결과를 정확히 보존한다.
2. 원문에 없는 원인, 피해, 확률, 심각도를 추가하지 않는다.
3. definition_ko는 원칙적으로 한 문장으로 쓰고, 무엇이 잘못되며 어떤 위험으로 이어지는지가 바로 이해되게 한다.
4. '비안전', '미모델링', '리타겟팅', '강건성', '피지컬 세계' 같은 번역투를 쉬운 표현으로 바꾼다.
5. 엄밀성에 필요한 기술용어는 보존하되, 문맥 안에서 쉽게 이해되도록 풀어 쓴다. 전문 개념을 일상적이지만 부정확한 개념으로 바꾸지 않는다.
6. L3 분류명이나 정답을 암시하는 문구는 추가하지 않는다.
7. label_ko는 짧고 자연스러운 명사구로 쓴다.
8. 임의의 예시, 원문에 없는 피해, '예를 들어', '(원문: ...)' 같은 설명을 절대 추가하지 않는다.
9. 원문이 열거한 대상과 범위는 임의로 줄이지 않는다. '모든', '완전히'처럼 원문보다 강한 표현도 추가하지 않는다.
10. '위험합니다', '경우입니다'만 반복하는 유아적 문체를 피하고, 자연스러운 설명문으로 쓴다.
11. 카드 ID는 절대 바꾸지 않는다. JSON 이외의 텍스트는 출력하지 않는다.

좋은 문체 예시: '기술 발전과 확산이 너무 빨라 사회 제도와 규칙이 따라가지 못하고 사회 질서가 크게 바뀌는 위험.'
이 예시는 문체만 참고하고 그 내용을 다른 카드에 넣지 않는다."""


def split_bilingual(value: str) -> tuple[str, str]:
    boundary = value.rfind("(")
    if value.endswith(")") and boundary > 0:
        return value[:boundary].strip(), value[boundary + 1 : -1].strip()
    return value.strip(), value.strip()


def request_batch(items: list[dict]) -> list[dict]:
    prompt = "다음 카드들을 편집하라:\n" + json.dumps(
        items, ensure_ascii=False, indent=2
    )
    schema = {
        "type": "object",
        "properties": {
            "cards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "card_id": {"type": "string"},
                        "label_ko": {"type": "string"},
                        "definition_ko": {"type": "string"},
                    },
                    "required": ["card_id", "label_ko", "definition_ko"],
                },
            }
        },
        "required": ["cards"],
    }
    body = json.dumps(
        {
            "model": MODEL,
            "stream": False,
            "think": False,
            "format": schema,
            "options": {"temperature": 0.1, "num_ctx": 8192, "num_predict": 1800},
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode()
    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=body,
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        payload = json.load(response)
    return json.loads(payload["message"]["content"])["cards"]


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    inputs = []
    for card in source:
        label_ko, label_en = split_bilingual(card["label"])
        definition_ko, definition_en = split_bilingual(card["definition"])
        inputs.append(
            {
                "card_id": card["card_id"],
                "label_ko_original": label_ko,
                "definition_ko_original": definition_ko,
                "label_en_reference": label_en,
                "definition_en_reference": definition_en,
            }
        )

    saved = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    results = [saved[item["card_id"]] for item in inputs if item["card_id"] in saved]
    for start in range(len(results), len(inputs), BATCH_SIZE):
        batch = inputs[start : start + BATCH_SIZE]
        edited = request_batch(batch)
        expected = [item["card_id"] for item in batch]
        if len(edited) != len(expected):
            raise ValueError(f"Batch length mismatch: expected={len(expected)}, actual={len(edited)}")
        for expected_id, item in zip(expected, edited):
            item["card_id"] = expected_id
        results.extend(edited)
        OUTPUT.write_text(
            json.dumps({item["card_id"]: item for item in results}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        print(f"edited={len(results)}/{len(inputs)}", flush=True)

    if len(results) != len(inputs):
        raise ValueError("Incomplete readable L4 output")
    OUTPUT.write_text(
        json.dumps({item["card_id"]: item for item in results}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
