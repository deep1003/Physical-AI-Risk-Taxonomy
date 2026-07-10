# Physical AI 위험 분류체계 독립 전문가 설문 계획서
# Protocol for Independent Expert Annotation of the Physical AI Risk Taxonomy

버전 1.0 / Version 1.0
작성일 / Date: 2026-07-10

## 1. 연구 목적 / Study objective

본 조사의 주목적은 각 L4 위험 카드에 대해 기존 L3와 유사한 대안 L3를 쌍으로 제시했을 때, 독립 전문가가 어느 후보를 더 적합하다고 평가하는지 검증하는 것이다. 이 조사는 기존 카드-L3 연결의 판별 타당성을 평가하며, 24개 위험군 전체가 유일하거나 최적인 분류체계라는 점을 검증하지 않는다.

The primary objective is to test which of two candidate L3 families independent experts judge to be the better fit for each L4 risk card: the canonical assignment or a closely matched alternative. The study evaluates the discriminant validity of existing card-to-family links; it does not establish that the complete 24-family structure is unique or optimal.

## 2. 연구 설계 / Study design

- 평가 대상: L4 위험 카드 182개, L3 위험군 24개
- 평가자: 독립 전문가 9명 이상 모집; 전체 카드의 최소 3회 평가를 위해 최소 19개 완주 응답을 목표로 함
- 배정: 19개 균형 블록, 블록당 30문항, 총 570건의 계획 판단; 카드당 3회 또는 4회
- 부담: 응답자당 30개 쌍대비교 문항; 제한시간 없음, 중단 후 재개 가능
- 설계: L3 기준으로 층화한 균형 불완전 블록 설계
- 맹검: 기존 L3 배정, 임베딩 예측, 유사도, 군집 ID 및 다른 평가자 응답 비공개
- 후보 구성: 기존 L3와 같은 L2에 속하는 유사 대안 L3를 사전 규칙으로 매칭
- 1차 평가변수: 기존 L3 선택률과 카드 단위 bootstrap 95% 신뢰구간

The study recruits at least nine independent experts and uses 19 balanced 30-item blocks. At least 19 completed responses are required to obtain a minimum of three ratings per card; 24 cards receive a fourth rating, yielding 570 planned judgments. Additional respondents receive repeated balanced blocks. For each card, the canonical L3 is paired with a prespecified, same-L2 hard negative; left/right order is randomized. The primary endpoint is the canonical-choice proportion with a card-level bootstrap 95% confidence interval.

## 3. 전문가 선정 / Expert eligibility

### 포함 기준 / Inclusion criteria

다음 중 하나 이상을 충족해야 한다.

- 로봇공학, 자율시스템, 제어공학, HRI, 안전공학 또는 AI safety 관련 학위
- 관련 학위과정 1년 이상
- 관련 산업·공공·표준화 분야 경력 1년 이상
- Physical AI, 로봇 안전 또는 자율시스템 위험평가 경험

Experts must satisfy at least one of the following: a relevant degree; at least one year in a relevant degree programme; at least one year of relevant professional experience in industry, the public sector, or standardization; or substantive experience in Physical AI, robot safety, or autonomous-system risk assessment.

### 제외 기준 / Exclusion criteria

- 원고 공동저자
- L3 정의 또는 L4 카드 생성·최초 배정에 참여한 사람
- 기존 카드별 label을 사전에 열람한 사람
- 독립적 평가를 저해하는 이해상충이 있는 사람

Co-authors, taxonomy developers, prior label reviewers, and persons with conflicts that compromise independent judgment are excluded.

## 4. 수집할 배경 정보 / Background variables

설문 문항은 이름, 이메일, 정확한 연령, 소속기관을 요구하지 않는다. 다음 응답 정보는 범주형으로 수집하며, 연령대와 성별에는 `응답하지 않음` 선택지를 제공한다.

- 익명 평가자 코드
- 연령대
- 성별
- 주요 전문영역(복수선택)
- 관련 경력 구간
- Physical AI 또는 로봇 위험평가 경험 수준
- 안전 표준·규제 업무 경험 여부
- 분류체계 개발 참여 또는 기존 label 노출 여부

The questionnaire does not request names, email addresses, exact age, or institutional affiliation. Anonymous respondent code, age band, gender, expertise, experience band, risk-assessment experience, standards or regulatory experience, and independence are collected categorically. Age band and gender include a prefer-not-to-say option.

## 5. 설문 절차 / Survey procedure

1. 연구 설명, 개인정보 처리 안내 및 참여 동의
2. 포함·제외 기준과 배경 정보 확인
3. 이중언어 L3 codebook 및 분류 규칙 검토
4. 개인별로 배정된 L4 카드마다 두 L3 후보 중 더 적합한 하나를 선택
5. 선택 확신도와 선택적 의견 기록
6. 전체 codebook의 명확성, 누락 위험 및 혼동되는 위험군에 대한 종료 의견
7. 응답을 Markdown으로 변환해 GitHub 응답 저장소에 제출

Each expert reviews the bilingual codebook and completes a forced-choice comparison between two L3 candidates for every allocated L4 card. Candidate order is randomized, and neither a tie nor an indeterminate option is provided. Experts also report confidence and may add a comment.

## 6. 카드 표시 및 맹검 / Card presentation and blinding

카드에는 무작위 표시 ID, L4 label·definition 및 두 L3 후보만 표시한다. 어느 후보가 기존 배정인지, L2 상위범주, 심각도·확률, 참고문헌 수와 계산 결과는 공개하지 않는다. 카드 순서와 후보 A/B 순서는 평가자별로 재현 가능한 방식으로 무작위화한다.

Cards display only a randomized presentation ID, the bilingual L4 label, and the bilingual definition. Existing L2/L3 assignments, severity, probability, reference counts, and computational results are hidden.

## 7. 카드별 설문 문항 / Card-level items

1. **Pairwise ranking**: 후보 A와 B 중 해당 L4 위험을 더 잘 설명하는 L3 하나를 반드시 선택
2. **Confidence**: 1(매우 낮음)~5(매우 높음)
3. **Comment**: 선택적 자유서술

## 8. 자료 보존 / Data retention

응답은 브라우저의 localStorage에 자동 임시저장된다. 완료된 응답은 구조화된 Markdown으로 변환되어 공개 GitHub 응답 저장소에 자동 보존된다. 설문 시작·종료 시각, 총 소요시간과 국가 수준의 접속지역은 응답 Markdown과 분리된 비공개 GitHub 저장소에 보존한다. 원본 IP와 더 세부적인 위치·접속·기기 정보는 저장하지 않는다. 공개 응답에는 시간 및 국가 정보를 포함하지 않는다. 제한시간은 없다. 비공개 운영 기록의 보유기간은 수집일로부터 1년으로 정한다.

Responses are autosaved in browser localStorage and converted to structured Markdown for automatic retention in a public GitHub response repository. Survey start and completion timestamps, total duration, and country-level access location are retained separately in a private GitHub repository. Source IP and finer-grained location, connection, or device metadata are not retained. The public response does not contain timing or country information. There is no time limit. Private administration records are retained for one year.

## 9. 품질관리 / Quality control

- 평가 중 기존 label을 공개하지 않는다.
- 불일치 자체를 근거로 평가자를 제외하지 않는다.
- 미완료, 독립성 위반, 기술적 손실 또는 사전 정의된 비성실 패턴만 제외 사유로 검토한다.
- 시작·종료 시각, 총 소요시간과 국가 정보는 비공개 운영 기록에만 저장한다.
- 설문 버전, 데이터 스냅샷 해시, 배정 버전과 평가자 코드를 응답 파일에 기록한다.

## 10. 분석 계획 / Statistical analysis

### 1차 분석 / Primary analysis

- 단위: L4 카드
- 척도: 두 후보 간 강제선택
- 지표: 기존 L3 선택률(canonical preference rate)
- 신뢰구간: 카드 단위 bootstrap 5,000회
- 귀무가설: 기존 L3 선택확률 0.5

### 보조 분석 / Secondary analyses

- 카드별 3인 중 기존 L3 다수선택률과 완전일치율
- L3 family별 기존 L3 선택률, macro-average 및 worst-family 결과
- 후보쌍별 선택률과 방향성
- 확신도별 기존 L3 선택률
- singleton 대 non-singleton L3 비교
- 기존 expert-corrected 카드 대 비보정 카드 비교
- cosine margin과 인간 불일치의 연관성(탐색적 분석)

570개 계획 판단을 독립 표본으로 간주하지 않으며, 불확실성은 카드 수준에서 평가한다. 9~18개 완주 응답은 전체 카드 검증을 위한 중간자료로만 취급한다.

## 11. 사전 의사결정 규칙 / Prespecified interpretation

| 결과 / Result | 해석 및 조치 / Interpretation and action |
|---|---|
| 전체 기존 L3 선택률의 95% CI 하한 > 0.50 | 매칭된 대안보다 기존 연결이 우세하다는 증거 / Evidence favouring canonical links over matched alternatives |
| 95% CI가 0.50 포함 | 판별 근거 불충분; 확정적 타당화 주장 금지 / Inconclusive discrimination; avoid definitive validation claims |
| family 선택률 < 0.60 | 해당 family의 정의·경계 또는 카드 연결 재검토 / Review family boundaries or card links |
| 카드에서 3인 중 2인 이상이 대안 선택 | 해당 카드 연결을 우선 재검토 / Prioritize the card-family link for review |

기준은 데이터 확인 전에 고정하며 결과에 맞춰 사후 변경하지 않는다.

## 12. 결과에 따른 개정 / Revision policy

설문 결과로 L3 정의를 수정한 경우 같은 응답으로 수정된 taxonomy의 성능을 확증하지 않는다. 수정된 분류체계는 별도의 holdout 카드 또는 신규 전문가를 이용해 재검증하거나, 원고에서 미검증 개정안임을 명시한다.

If survey results are used to revise family definitions, the same observations will not be reused as confirmatory evidence for the revised taxonomy.

## 13. 산출물 / Deliverables

- 이중언어 연구계획서: Markdown, LaTeX, PDF
- GitHub Pages 이중언어 설문
- 24개 L3 codebook과 182개 L4 카드의 고정 JSON 스냅샷
- A01~A19 균형 배정표
- Markdown 응답 파일
- 데이터 사전 및 분석용 변환 명세
