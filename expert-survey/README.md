# Physical AI Domain Expert Survey

GitHub Pages에서 실행되는 한·영 병기 독립 전문가 쌍대 순위 설문이다.

## Files

- `protocol.md`, `protocol.tex`, `protocol.pdf`: 사전 설문 계획서
- `index.html`, `styles.css`, `app.js`: 정적 설문 앱
- `data/survey-data.json`: 24개 L3 codebook과 맹검 처리한 182개 L4 카드
- `data/assignments.json`: A01~A09 평가자별 고정 카드 배정
- `scripts/build_survey_data.py`: 정식 로컬 데이터로 설문 스냅샷 재생성
- `scripts/validate_survey.py`: 데이터·배정·웹 파일 검증

## Storage model

응답은 작성 중 브라우저 `localStorage`에 임시저장된다. 완료 시 Cloudflare Worker가 응답을 Markdown으로 변환해 공개 GitHub 응답 저장소의 `responses/YYYY/MM/` 디렉터리에 자동 커밋한다. 자동 저장이 실패하면 브라우저 임시자료를 유지하고 재시도한다.

Worker는 동일한 익명 응답자 ID와 제출 ID를 사용해 시작·종료·수신 시각, 소요시간과 접속 telemetry를 비공개 `deep1003/Physical-AI-Risk-Survey-Telemetry` 저장소의 `telemetry/YYYY/MM/` 디렉터리에 별도 저장한다. 공개 응답에는 시간정보, 원본 IP나 정밀 접속정보를 포함하지 않는다.

익명 평가자 ID는 브라우저에서 자동 생성된다. 참가자 수에는 상한을 두지 않으며, 각 참가자는 A01~A09의 균형 블록 중 하나를 암호학적 난수로 배정받는다.

## Rebuild

```bash
python3 expert-survey/scripts/build_survey_data.py
python3 expert-survey/scripts/validate_survey.py
```

## Assignment integrity

각 L4 카드는 정확히 3명의 서로 다른 평가자에게 배정된다. 평가자별 부담은 60~61개이다. 각 문항은 기존 L3와 같은 L2의 유사 대안 L3를 함께 제시하되 어느 후보가 기존 배정인지 숨기고 A/B 순서를 무작위화한다. 응답자는 두 후보 중 하나를 반드시 선택한다.
