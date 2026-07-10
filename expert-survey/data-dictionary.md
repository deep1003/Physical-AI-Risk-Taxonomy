# 응답 데이터 사전 / Response Data Dictionary

완료 응답은 YAML front matter와 Markdown 표로 저장된다.

| Field | Type | Description |
|---|---|---|
| `survey_version` | string | 설문 도구 버전 / Survey instrument version |
| `assignment_version` | string | 카드 배정 버전 / Assignment version |
| `rater_code` | string | A01~A09 익명 코드 / Anonymous rater code |
| `completed_at` | ISO 8601 | 완료 시각 / Completion timestamp |
| `source_sha256` | string | L4 원본 데이터 SHA-256 |
| `Expertise` | categorical, multiple | 전문영역 / Fields of expertise |
| `Career` | ordinal category | 관련 경력 구간 / Experience band |
| `Sector` | categorical | 소속 부문 / Employment sector |
| `Region` | categorical | 광역 활동 지역 / Broad region |
| `Education` | categorical | 최종 학위 / Highest qualification |
| `Risk-assessment experience` | ordinal category | 위험평가 경험 / Risk-assessment experience |
| `Standards experience` | binary | 표준·규제 경험 / Standards experience |
| `Display ID` | string | 설문 표시용 카드 ID / Blinded display ID |
| `Card ID` | string | 정식 L4 카드 ID / Canonical card ID |
| `Primary L3` | nominal | 주 분류; L3, `UNMAPPABLE`, `INSUFFICIENT` |
| `Secondary L3` | nominal, optional | 선택적 두 번째 L3 |
| `Confidence` | integer 1–5 | 분류 확신도 / Assignment confidence |
| `Ambiguity` | categorical, optional | 모호성 원인 / Source of ambiguity |
| `Comment` | text, optional | 카드별 의견 / Card-level comment |
| `Clarity` | ordinal 1–5 | L3 정의의 전반적 명확성 |
| `Confusing pairs` | text, optional | 혼동된 L3 쌍 |
| `Missing risks` | text, optional | 누락 위험영역 |
| `Suggestions` | text, optional | 병합·분리·정의 개선 제안 |

정확한 이름, 이메일, 성별, 연령 및 소속기관은 수집하지 않는다. 자유서술에는 개인식별정보를 입력하지 않도록 참가자에게 안내해야 한다.

Exact names, email addresses, gender, age, and institutional affiliation are not collected. Participants should not enter personal identifiers in free-text fields.
