# 응답 데이터 사전 / Response Data Dictionary

완료 응답은 YAML front matter와 Markdown 표로 저장된다.

| Field | Type | Description |
|---|---|---|
| `survey_version` | string | 설문 도구 버전 / Survey instrument version |
| `assignment_version` | string | 카드 배정 버전 / Assignment version |
| `respondent_id` | string | 자동 생성된 익명 응답자 ID / Automatically generated anonymous respondent ID |
| `assignment_block` | string | 무작위 배정된 A01~A19의 30문항 카드 블록 / Randomly assigned 30-item block A01–A19 |
| `source_sha256` | string | L4 원본 데이터 SHA-256 |
| `Age band` | categorical | 연령대 / Age band; prefer-not-to-say available |
| `Gender` | categorical | 성별 / Gender; prefer-not-to-say available |
| `Expertise` | categorical, multiple | 전문영역 / Fields of expertise |
| `Career` | ordinal category | 관련 경력 구간 / Experience band |
| `Risk-assessment experience` | ordinal category | 위험평가 경험 / Risk-assessment experience |
| `Standards experience` | binary | 표준·규제 경험 / Standards experience |
| `Display ID` | string | 설문 표시용 카드 ID / Blinded display ID |
| `Card ID` | string | 정식 L4 카드 ID / Canonical card ID |
| `Candidate A` | L3 ID | 먼저 표시된 후보 / First displayed candidate |
| `Candidate B` | L3 ID | 두 번째로 표시된 후보 / Second displayed candidate |
| `Original selected L3` | L3 ID | 최초 쌍대 비교에서 선택된 L3 / Candidate selected in the original pairwise item |
| `Confidence` | integer 1–5 | 순위 선택 확신도 / Ranking confidence |
| `Comment` | text, optional | 카드별 의견 / Card-level comment |
| `Algorithm-selected L3` | L3 ID | 기존 알고리즘 배정 L3 / Existing algorithm-selected assignment |
| `Original confidence` | integer 1–5 | 재검토 대상 문항의 최초 확신도 / Original confidence for reconsidered item |
| `Revised selected L3` | L3 ID | 제출 전 재검토 후 최종 선택 L3 / Final selection after pre-submission reconsideration |
| `Changed` | yes/no | 재검토에서 원래 선택을 수정했는지 여부 / Whether the original choice was changed |

최초 선택과 재검토 후 선택은 별도 표에 분리해 저장한다. 재검토 문항은 알고리즘 배정과 다르게 답한 문항 중 확신도가 가장 높은 항목을 최대 3개까지 제시한다.

Original choices and revised choices are retained in separate Markdown tables. Reconsideration items are limited to at most three highest-confidence cases where the respondent's original choice differs from the algorithm-selected assignment.

설문 문항은 이름, 이메일, 정확한 연령, 소속기관을 요구하지 않는다. 연령대와 성별은 범주형으로 수집하고 `응답하지 않음` 선택지를 제공한다. 접속 telemetry는 별도의 비공개 저장소에 보관하며 공개 응답에는 포함하지 않는다.

The questionnaire does not request names, email addresses, exact age, or institutional affiliation. Age band and gender are categorical and include a prefer-not-to-say option. Connection telemetry is retained in a separate private repository and is not included in the public response.

## Private telemetry fields

The private study-administration record contains only the survey start timestamp, completion timestamp, total duration, and country-level access location. Source IP and finer-grained connection or device metadata are not retained. There is no time limit.
