# Physical AI 위험 분류체계 독립 전문가 설문 계획서
# Protocol for Independent Expert Annotation of the Physical AI Risk Taxonomy

버전 1.0 / Version 1.0
작성일 / Date: 2026-07-10

## 1. 연구 목적 / Study objective

본 조사의 주목적은 사전에 정의된 24개 L3 위험군을 이용할 때 독립 전문가가 182개 L4 위험 카드를 일관되게 분류할 수 있는지 평가하는 것이다. 이 조사는 제안된 카드-위험군 배정의 재현성과 적용 가능성을 평가하며, 24개 위험군이 유일하거나 최적인 분류체계라는 점을 검증하지 않는다.

The primary objective is to assess whether independent experts can consistently classify 182 L4 risk cards using 24 predefined L3 risk families. The study evaluates the reproducibility and applicability of the proposed card-to-family assignments; it does not establish that the 24-family structure is unique or optimal.

## 2. 연구 설계 / Study design

- 평가 대상: L4 위험 카드 182개, L3 위험군 24개
- 평가자: 독립 전문가 9명
- 배정: 카드당 서로 다른 전문가 3명, 총 546건의 판단
- 부담: 전문가당 60~61개 카드, 두 세션으로 분할
- 설계: L3 기준으로 층화한 균형 불완전 블록 설계
- 맹검: 기존 L3 배정, 임베딩 예측, 유사도, 군집 ID 및 다른 평가자 응답 비공개
- 1차 평가변수: 명목척도 Krippendorff's alpha와 카드 단위 bootstrap 95% 신뢰구간

The study uses a stratified balanced incomplete block design. Nine independent experts each annotate 60 or 61 cards in two sessions; every card receives three independent ratings. Existing labels and computational outputs remain blinded. The primary endpoint is nominal Krippendorff's alpha with a card-level bootstrap 95% confidence interval.

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

이 설문은 다음 정보를 절대 수집하거나 요구하지 않는다: 이름, 이메일, 성별, 연령, 소속기관 등 개인정보. 연구 목적상 필요한 다음의 범주형 정보만 수집한다.

- 익명 평가자 코드
- 주요 전문영역(복수선택)
- 관련 경력 구간
- 소속 부문: 학계·연구, 산업, 공공·규제, 표준화, 기타
- 활동 지역권: 대한민국, 아시아(대한민국 제외), 유럽, 북미, 기타/응답하지 않음
- 최종 학위 구간
- Physical AI 또는 로봇 위험평가 경험 수준
- 안전 표준·규제 업무 경험 여부
- 분류체계 개발 참여 또는 기존 label 노출 여부

This survey never collects or requests personal information such as names, email addresses, gender, age, or institutional affiliation. Only categorical variables necessary to characterize expertise, sector, broad region, education, risk-assessment experience, standards experience, and independence are retained.

## 5. 설문 절차 / Survey procedure

1. 연구 설명, 개인정보 처리 안내 및 참여 동의
2. 포함·제외 기준과 배경 정보 확인
3. 이중언어 L3 codebook 및 분류 규칙 검토
4. 개인별로 배정된 L4 카드의 독립 분류
5. 각 카드에 대해 primary L3, 선택적 secondary L3, 확신도 및 모호성 원인 기록
6. taxonomy로 분류할 수 없는 경우 `Unmappable`, 정보가 부족한 경우 `Insufficient information` 선택
7. 전체 codebook의 명확성, 누락 위험 및 혼동되는 위험군에 대한 종료 의견
8. 응답을 Markdown 파일로 다운로드하고 선택적으로 GitHub 제출

Each expert reviews the bilingual codebook and independently assigns a primary family to each allocated card. A secondary family is optional. Experts also report confidence and, when applicable, the source of ambiguity. `Unmappable` and `Insufficient information` are valid responses rather than forced assignments.

## 6. 카드 표시 및 맹검 / Card presentation and blinding

카드에는 무작위 표시 ID, L4 label 및 definition만 표시한다. 기존 L3 ID·명칭, L2 상위범주, 심각도·확률, 참고문헌 수, 임베딩 결과는 공개하지 않는다. L3는 codebook의 선택지로만 제공한다. 카드 순서는 평가자 코드별로 고정된 seed를 사용해 무작위화한다.

Cards display only a randomized presentation ID, the bilingual L4 label, and the bilingual definition. Existing L2/L3 assignments, severity, probability, reference counts, and computational results are hidden.

## 7. 카드별 설문 문항 / Card-level items

1. **Primary classification**: 가장 적절한 L3 위험군 하나, `Unmappable`, 또는 `Insufficient information`
2. **Secondary classification**: 실질적으로 관련된 두 번째 L3 위험군(선택)
3. **Confidence**: 1(매우 낮음)~5(매우 높음)
4. **Ambiguity reason**: 낮은 확신도 또는 secondary 선택 시 카드 정보 부족, 복수 메커니즘, 정의 중첩, 경계 불명확, 누락된 위험군, 전문지식 한계, 기타
5. **Comment**: 선택적 자유서술

## 8. 자료 보존 / Data retention

응답은 브라우저의 localStorage에 자동 임시저장된다. 완료된 응답은 구조화된 Markdown으로 변환되어 공개 GitHub 응답 저장소에 자동 보존된다. 제출된 익명 응답이 연구 재현성을 위해 공개 저장소에 보존된다는 사실을 동의문에 고지한다. 원자료에는 직접 식별정보를 포함하지 않는다.

Responses are autosaved in browser localStorage and converted to structured Markdown for automatic retention in a public GitHub response repository. The consent statement discloses that anonymous responses are publicly retained for research reproducibility.

## 9. 품질관리 / Quality control

- 평가 중 기존 label을 공개하지 않는다.
- 불일치 자체를 근거로 평가자를 제외하지 않는다.
- 미완료, 독립성 위반, 기술적 손실 또는 사전 정의된 비성실 패턴만 제외 사유로 검토한다.
- 카드별 시작·종료 시각 대신 응답 소요시간을 초 단위로 저장하되 절대 시각은 최소화한다.
- 설문 버전, 데이터 스냅샷 해시, 배정 버전과 평가자 코드를 응답 파일에 기록한다.

## 10. 분석 계획 / Statistical analysis

### 1차 분석 / Primary analysis

- 단위: L4 카드
- 척도: nominal primary L3 assignment
- 지표: Krippendorff's alpha
- 신뢰구간: 카드 단위 bootstrap 5,000회
- `Unmappable`과 `Insufficient information`은 별도 범주로 유지

### 보조 분석 / Secondary analyses

- Gwet's AC1
- 3인 완전 일치율과 2인 이상 다수결 형성률
- 기존 release label과 전문가 다수결의 일치율
- family별 precision, recall, F1, macro-F1 및 worst-family F1
- primary 또는 secondary를 허용한 top-2 agreement
- family별 confusion matrix
- `Unmappable` 및 `Insufficient information` 비율
- 확신도별 일치도
- singleton 대 non-singleton L3 비교
- 기존 expert-corrected 카드 대 비보정 카드 비교
- cosine margin과 인간 불일치의 연관성(탐색적 분석)

546개 개별 응답을 독립 표본으로 간주하지 않으며, 불확실성은 카드 수준에서 평가한다.

## 11. 사전 의사결정 규칙 / Prespecified interpretation

| 결과 / Result | 해석 및 조치 / Interpretation and action |
|---|---|
| alpha >= 0.80 | 높은 적용 재현성; 24-family schema 유지 가능 / High reproducibility |
| 0.67 <= alpha < 0.80 | 잠정적 재현성; 경계 규칙 개선 / Tentative reproducibility; revise boundaries |
| alpha < 0.67 | 확정적 taxonomy 주장 완화 / Do not claim a validated definitive taxonomy |
| family 다수결 일치율 < 60% | 해당 family 재정의 또는 병합 검토 / Redefine or consider merging |
| Unmappable >= 10% | taxonomy coverage 재검토 / Reassess coverage |
| Insufficient information >= 10% | L4 description 충실도 재검토 / Revise card descriptions |

기준은 데이터 확인 전에 고정하며 결과에 맞춰 사후 변경하지 않는다.

## 12. 결과에 따른 개정 / Revision policy

설문 결과로 L3 정의를 수정한 경우 같은 응답으로 수정된 taxonomy의 성능을 확증하지 않는다. 수정된 분류체계는 별도의 holdout 카드 또는 신규 전문가를 이용해 재검증하거나, 원고에서 미검증 개정안임을 명시한다.

If survey results are used to revise family definitions, the same observations will not be reused as confirmatory evidence for the revised taxonomy.

## 13. 산출물 / Deliverables

- 이중언어 연구계획서: Markdown, LaTeX, PDF
- GitHub Pages 이중언어 설문
- 24개 L3 codebook과 182개 L4 카드의 고정 JSON 스냅샷
- A01~A09 균형 배정표
- Markdown 응답 파일
- 데이터 사전 및 분석용 변환 명세
