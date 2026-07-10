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

응답은 작성 중 브라우저 `localStorage`에 임시저장된다. 완료 시 Cloudflare Worker가 응답을 Markdown으로 변환해 공개 GitHub 응답 저장소의 `responses/YYYY/MM/` 디렉터리에 자동 커밋한다. 자동 저장이 실패하면 브라우저 임시자료를 유지하고 재시도한다.

익명 평가자 ID는 브라우저에서 자동 생성된다. 참가자 수에는 상한을 두지 않으며, 각 참가자는 A01~A09의 균형 블록 중 하나를 암호학적 난수로 배정받는다.

## Rebuild

```bash
python3 expert-survey/scripts/build_survey_data.py
python3 expert-survey/scripts/validate_survey.py
```

## Assignment integrity

각 L4 카드는 정확히 3명의 서로 다른 평가자에게 배정된다. 평가자별 부담은 60~61개이며, 배정 과정에서는 기존 L3를 층화 변수로만 사용한다. 웹 설문에는 기존 카드별 L3가 포함되지 않는다.
