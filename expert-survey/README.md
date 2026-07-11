# Physical AI Domain Expert Survey

GitHub Pages에서 실행되는 한·영 병기 독립 전문가 쌍대 순위 설문이다.

## Files

- `protocol.md`, `protocol.tex`, `protocol.pdf`: 사전 설문 계획서
- `index.html`, `styles.css`, `app.js`: 정적 설문 앱
- `data/survey-data.json`: 24개 L3 codebook과 맹검 처리한 182개 L4 카드
- `data/assignments.json`: A01~A19의 30문항 균형 카드 배정
- `scripts/build_survey_data.py`: 정식 로컬 데이터로 설문 스냅샷 재생성
- `scripts/validate_survey.py`: 데이터·배정·웹 파일 검증

## Storage model

응답은 작성 중 브라우저 `localStorage`에 임시저장된다. 완료 시 Cloudflare Worker가 응답을 Markdown, JSON, CSV로 변환해 공개 GitHub 응답 저장소의 `responses/YYYY/MM/` 디렉터리에 자동 커밋한다. 자동 저장이 실패하면 브라우저 임시자료를 유지하고 재시도한다.

Worker는 동일한 익명 응답자 ID와 제출 ID를 사용해 시작·종료 시각, 소요시간과 국가 수준의 접속지역만 비공개 `deep1003/Physical-AI-Risk-Survey-Telemetry` 저장소의 `telemetry/YYYY/MM/` 디렉터리에 별도 저장한다. 원본 IP와 세부 접속정보는 저장하지 않으며 공개 응답에도 시간·국가 정보를 포함하지 않는다.

익명 평가자 ID는 브라우저에서 자동 생성된다. 참가자 수에는 상한을 두지 않으며, 각 참가자는 A01~A19의 30문항 균형 블록 중 하나를 암호학적 난수로 배정받는다. 설문자는 최소 20명 이상 실시하며, 19개 완주 응답 이후부터 모든 카드에서 최소 3개 판단이 확보된다.

제출 완료 화면의 `새로운 랜덤 문제 시작 / Start new random items` 버튼을 누르면 동일한 컴퓨터에서도 새로운 익명 평가자 ID와 무작위 블록으로 별도 응답을 시작할 수 있다. 기존 제출과 브라우저 임시자료는 삭제하지 않는다.

## Rebuild

```bash
python3 expert-survey/scripts/build_survey_data.py
python3 expert-survey/scripts/validate_survey.py
```

## Assignment integrity

19개 블록은 각각 정확히 30문항이다. 각 L4 카드는 최소 3개 블록에 포함되고, 균형을 위해 24개 카드는 4개 블록에 포함된다. 각 문항은 사전 지정 기준 배정 L3와 같은 L2의 유사 대안 L3를 함께 제시하되 어느 후보가 기준 배정인지 숨기고 A/B 순서를 무작위화한다. 응답자는 두 후보 중 하나를 반드시 선택한다.

최초 30문항 완료 후에는 사전 지정 기준 배정과 다르게 답한 항목 중 확신도가 가장 높은 문항을 최대 3개까지 다시 제시한다. 이 단계에서는 기준 배정과 본인의 원래 답변을 함께 보여주고, 원래 답변을 유지하거나 기준 배정으로 수정할 기회를 제공한다. 주 분석은 원래 응답만 사용하며, 재검토 결과는 고확신 불일치 판단의 안정성과 원래 전문가 답변에서 기준 배정으로 전환한 switch rate를 보는 보조 분석으로만 사용한다. Markdown, JSON, CSV 응답에는 원래 선택과 재검토 후 선택을 별도 필드로 분리해 저장한다.

분석 요약은 card-level, family-level, respondent-level로 분리한다. 카드별 agreement 비율은 Wilson 또는 bootstrap 신뢰구간과 함께 제시한다. 강제선택 pairwise 설계는 unknown 또는 unmappable 판단을 배제한다는 제한을 명시한다.
