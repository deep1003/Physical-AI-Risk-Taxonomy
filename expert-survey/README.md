# Physical AI Independent Expert Survey

GitHub Pages에서 실행되는 한·영 병기 독립 전문가 분류 설문이다.

## Files

- `protocol.md`, `protocol.tex`, `protocol.pdf`: 사전 설문 계획서
- `index.html`, `styles.css`, `app.js`: 정적 설문 앱
- `data/survey-data.json`: 24개 L3 codebook과 맹검 처리한 182개 L4 카드
- `data/assignments.json`: A01~A09 평가자별 고정 카드 배정
- `scripts/build_survey_data.py`: 정식 로컬 데이터로 설문 스냅샷 재생성
- `scripts/validate_survey.py`: 데이터·배정·웹 파일 검증

## Storage model

응답은 브라우저 `localStorage`에 자동 저장되고 완료 시 Markdown으로 다운로드된다. 선택적으로 Markdown을 복사해 GitHub Issue에 제출할 수 있으나, 공개 저장소의 Issue가 공개될 수 있음을 참가자에게 고지한다. 운영 연구에서는 다운로드 파일을 연구팀의 접근 제한 저장소로 전달하는 경로를 기본으로 사용한다.

## Rebuild

```bash
python3 expert-survey/scripts/build_survey_data.py
python3 expert-survey/scripts/validate_survey.py
```

## Assignment integrity

각 L4 카드는 정확히 3명의 서로 다른 평가자에게 배정된다. 평가자별 부담은 60~61개이며, 배정 과정에서는 기존 L3를 층화 변수로만 사용한다. 웹 설문에는 기존 카드별 L3가 포함되지 않는다.
