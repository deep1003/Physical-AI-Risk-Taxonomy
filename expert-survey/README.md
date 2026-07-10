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

응답은 작성 중 브라우저 `localStorage`에 임시저장된다. 완료 시 Cloudflare Worker가 응답을 Markdown으로 변환해 공개 GitHub 응답 저장소의 `responses/YYYY/MM/` 디렉터리에 자동 커밋한다. 자동 저장이 실패하면 브라우저 임시자료를 유지하고 재시도한다.

Worker는 동일한 익명 응답자 ID와 제출 ID를 사용해 시작·종료·수신 시각, 소요시간과 접속 telemetry를 비공개 `deep1003/Physical-AI-Risk-Survey-Telemetry` 저장소의 `telemetry/YYYY/MM/` 디렉터리에 별도 저장한다. 공개 응답에는 시간정보, 원본 IP나 정밀 접속정보를 포함하지 않는다.

익명 평가자 ID는 브라우저에서 자동 생성된다. 참가자 수에는 상한을 두지 않으며, 각 참가자는 A01~A19의 30문항 균형 블록 중 하나를 암호학적 난수로 배정받는다. 9명 이상을 모집하되 모든 카드에서 최소 3개 판단을 확보하려면 최소 19개 완주 응답이 필요하다.

제출 완료 화면의 `새 응답 시작 / Start a new response` 버튼을 누르면 동일한 컴퓨터에서도 새로운 익명 평가자 ID와 무작위 블록으로 별도 응답을 시작할 수 있다. 기존 제출과 브라우저 임시자료는 삭제하지 않는다.

## Rebuild

```bash
python3 expert-survey/scripts/build_survey_data.py
python3 expert-survey/scripts/validate_survey.py
```

## Assignment integrity

19개 블록은 각각 정확히 30문항이다. 각 L4 카드는 최소 3개 블록에 포함되고, 균형을 위해 24개 카드는 4개 블록에 포함된다. 각 문항은 기존 L3와 같은 L2의 유사 대안 L3를 함께 제시하되 어느 후보가 기존 배정인지 숨기고 A/B 순서를 무작위화한다. 응답자는 두 후보 중 하나를 반드시 선택한다.
