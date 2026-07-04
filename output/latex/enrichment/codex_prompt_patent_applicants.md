# Codex 프롬프트 — Physical AI Risks 특허 출원인·국가 채우기

목표: Physical AI Risks 특허 **31,658건**의 **출원인(기관)**과 **출원인 국가**를 PATSTAT에서 조회해 채운다.

입력 파일:
`/Users/deep1003/data3/integrated_ai_document_space_20260704/patents/physical_ai_risks/physical_ai_risks_patents_integrated_dedup.csv.gz`
- 키 컬럼: `app_id` ( = PATSTAT `appln_id` ). 예: 10155483, 10505009, 102520. 총 31,658개.

작업:
1. 위 파일에서 `app_id` 목록(31,658개)을 읽는다.
2. PATSTAT에서 각 `appln_id`의 출원인 이름·국가를 조회한다:
   ```sql
   SELECT pa.appln_id,
          p.psn_name        AS applicant_name,
          p.person_ctry_code AS applicant_country
   FROM tls207_pers_appln pa
   JOIN tls206_person p ON p.person_id = pa.person_id
   WHERE pa.applt_seq_nr > 0        -- 출원인만(발명자 제외)
     AND pa.appln_id IN (:app_ids);
   ```
   - 출원인이 여러 명이면 `applt_seq_nr = 1` 대표 1건만, 또는 이름/국가를 `|`로 결합.
   - `appln_id`로 매칭이 안 되면 대체로 `tls201_appln.appln_nr`(출원번호)로 조인 시도.
3. 결과를 CSV로 저장:
   `/Users/deep1003/data3/Physical-AI-Risk-Taxonomy/output/latex/enrichment/patent_applicants_from_patstat.csv`
   컬럼: `app_id, applicant_name, applicant_country`

규칙:
- 원본 데이터셋은 **읽기 전용**(수정·삭제 금지).
- 매칭 실패는 빈 값으로 두고, 마지막에 **커버리지(%)**(applicant_name 채움률, applicant_country 채움률)를 보고.
