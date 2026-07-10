# 응답 데이터 사전 / Response Data Dictionary

완료 응답은 YAML front matter와 Markdown 표로 저장된다.

| Field | Type | Description |
|---|---|---|
| `survey_version` | string | 설문 도구 버전 / Survey instrument version |
| `assignment_version` | string | 카드 배정 버전 / Assignment version |
| `respondent_id` | string | 자동 생성된 익명 응답자 ID / Automatically generated anonymous respondent ID |
| `assignment_block` | string | 무작위 배정된 A01~A09 카드 블록 / Randomly assigned card block |
| `completed_at` | ISO 8601 | 완료 시각 / Completion timestamp |
| `source_sha256` | string | L4 원본 데이터 SHA-256 |
| `Age band` | categorical | 연령대 / Age band; prefer-not-to-say available |
| `Gender` | categorical | 성별 / Gender; prefer-not-to-say available |
| `Expertise` | categorical, multiple | 전문영역 / Fields of expertise |
| `Career` | ordinal category | 관련 경력 구간 / Experience band |
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

설문 문항은 이름, 이메일, 정확한 연령, 소속기관을 요구하지 않는다. 연령대와 성별은 범주형으로 수집하고 `응답하지 않음` 선택지를 제공한다. 접속 telemetry는 별도의 비공개 저장소에 보관하며 공개 응답에는 포함하지 않는다.

The questionnaire does not request names, email addresses, exact age, or institutional affiliation. Age band and gender are categorical and include a prefer-not-to-say option. Connection telemetry is retained in a separate private repository and is not included in the public response.

## Private telemetry fields

The private telemetry record may contain client and server timestamps, duration, source IP, country, continent, region, city, postal code, latitude, longitude, timezone, ASN, network organization, Cloudflare data centre, HTTP and TLS properties, User-Agent, accepted languages and encodings, referrer, browser platform, screen and viewport dimensions, pixel ratio, device memory, processor concurrency, cookie status, and do-not-track preference.
