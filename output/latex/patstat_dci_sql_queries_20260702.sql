-- ============================================================================
-- PATSTAT Online SQL — DCI (Data Center Interconnect) Stage 1.3 검색식
-- 작성: 2026-07-02
-- 기반: patstat_ai_infra_methodology_appendix_20260620 A.9 컨벤션
--   - 연도 치환: a.earliest_filing_year BETWEEN YYYY AND YYYY
--   - 다운로드 제한: 연도별 결과 9,999행 이하 range 분할
--   - IPC/CPC 심볼: subclass(4자) + main group 우측정렬 4자 공백 패딩
-- release label 제안: patstat_2026_summer_dci_stage1_3
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Q0. 연도별 건수 사전 확인 (range 분할 계획용)
-- ----------------------------------------------------------------------------
SELECT a.earliest_filing_year priority_year, COUNT(DISTINCT a.appln_id) n
FROM tls201_appln a
LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
LEFT JOIN tls203_appln_abstr b0 ON a.appln_id = b0.appln_id
WHERE a.earliest_filing_year BETWEEN YYYY AND YYYY
  AND a.granted = 'Y'
  AND (
    LOWER(t.appln_title) LIKE '%data center interconnect%'
    OR LOWER(t.appln_title) LIKE '%datacenter interconnect%'
    OR LOWER(t.appln_title) LIKE '%data centre interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%data center interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%datacenter interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%data centre interconnect%'
  )
GROUP BY a.earliest_filing_year
ORDER BY a.earliest_filing_year;

-- ----------------------------------------------------------------------------
-- Q1. DCI Stage 1.3 메인 검색식
--   Layer A: DCI 직접 문구 (제목/초록)
--   Layer B: DCI 요소기술 IPC/CPC × 데이터센터 문맥 키워드
--   플래그: has_dci_phrase / has_coherent_code / has_component_code / has_dc_context
-- ----------------------------------------------------------------------------
SELECT DISTINCT
 a.appln_id app_id,
 a.appln_auth patent_office,
 a.appln_nr app_num,
 a.earliest_filing_year priority_year,
 t.appln_title title,
 b0.appln_abstract abstract,
 a.docdb_family_size family_size,
 a.granted granted,
 CASE WHEN (
   LOWER(t.appln_title) LIKE '%data center interconnect%'
   OR LOWER(t.appln_title) LIKE '%datacenter interconnect%'
   OR LOWER(t.appln_title) LIKE '%data centre interconnect%'
   OR LOWER(t.appln_title) LIKE '%inter-data center%'
   OR LOWER(t.appln_title) LIKE '%inter-datacenter%'
   OR LOWER(b0.appln_abstract) LIKE '%data center interconnect%'
   OR LOWER(b0.appln_abstract) LIKE '%datacenter interconnect%'
   OR LOWER(b0.appln_abstract) LIKE '%data centre interconnect%'
   OR LOWER(b0.appln_abstract) LIKE '%inter-data center%'
   OR LOWER(b0.appln_abstract) LIKE '%inter-datacenter%'
 ) THEN 1 ELSE 0 END has_dci_phrase,
 CASE WHEN (
   EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
     i.ipc_class_symbol LIKE 'H04B  10/61%'
     OR i.ipc_class_symbol LIKE 'H04B  10/54%'
     OR i.ipc_class_symbol LIKE 'H04J  14/02%'
     OR i.ipc_class_symbol LIKE 'H04J  14/06%'))
   OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
     c.cpc_class_symbol LIKE 'H04B  10/61%'
     OR c.cpc_class_symbol LIKE 'H04B  10/54%'
     OR c.cpc_class_symbol LIKE 'H04J  14/02%'
     OR c.cpc_class_symbol LIKE 'H04J  14/06%'))
 ) THEN 1 ELSE 0 END has_coherent_code,
 CASE WHEN (
   EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
     i.ipc_class_symbol LIKE 'H04B  10/40%'
     OR i.ipc_class_symbol LIKE 'G02B   6/12%'
     OR i.ipc_class_symbol LIKE 'G02B   6/42%'
     OR i.ipc_class_symbol LIKE 'H01S   5/%'
     OR i.ipc_class_symbol LIKE 'G02F   1/01%'
     OR i.ipc_class_symbol LIKE 'G02F   1/21%'))
   OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
     c.cpc_class_symbol LIKE 'H04B  10/40%'
     OR c.cpc_class_symbol LIKE 'G02B   6/12%'
     OR c.cpc_class_symbol LIKE 'G02B   6/42%'
     OR c.cpc_class_symbol LIKE 'H01S   5/%'
     OR c.cpc_class_symbol LIKE 'G02F   1/01%'
     OR c.cpc_class_symbol LIKE 'G02F   1/21%'))
 ) THEN 1 ELSE 0 END has_component_code,
 CASE WHEN (
   LOWER(t.appln_title) LIKE '%data center%'
   OR LOWER(t.appln_title) LIKE '%datacenter%'
   OR LOWER(t.appln_title) LIKE '%data centre%'
   OR LOWER(b0.appln_abstract) LIKE '%data center%'
   OR LOWER(b0.appln_abstract) LIKE '%datacenter%'
   OR LOWER(b0.appln_abstract) LIKE '%data centre%'
   OR LOWER(b0.appln_abstract) LIKE '%hyperscale%'
 ) THEN 1 ELSE 0 END has_dc_context
FROM tls201_appln a
LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
LEFT JOIN tls203_appln_abstr b0 ON a.appln_id = b0.appln_id
WHERE a.earliest_filing_year BETWEEN YYYY AND YYYY
  AND a.granted = 'Y'
  AND (
    -- Layer A: DCI 직접 문구
    LOWER(t.appln_title) LIKE '%data center interconnect%'
    OR LOWER(t.appln_title) LIKE '%datacenter interconnect%'
    OR LOWER(t.appln_title) LIKE '%data centre interconnect%'
    OR LOWER(t.appln_title) LIKE '%inter-data center%'
    OR LOWER(t.appln_title) LIKE '%inter-datacenter%'
    OR LOWER(t.appln_title) LIKE '%optical interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%data center interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%datacenter interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%data centre interconnect%'
    OR LOWER(b0.appln_abstract) LIKE '%inter-data center%'
    OR LOWER(b0.appln_abstract) LIKE '%inter-datacenter%'
    -- Layer B: DCI 요소기술 코드 × 데이터센터 문맥
    OR (
      (
        EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
          i.ipc_class_symbol LIKE 'H04B  10/%'
          OR i.ipc_class_symbol LIKE 'H04J  14/%'
          OR i.ipc_class_symbol LIKE 'H04Q  11/%'
          OR i.ipc_class_symbol LIKE 'G02B   6/12%'
          OR i.ipc_class_symbol LIKE 'G02B   6/42%'
          OR i.ipc_class_symbol LIKE 'H01S   5/%'
          OR i.ipc_class_symbol LIKE 'G02F   1/01%'
          OR i.ipc_class_symbol LIKE 'G02F   1/21%'
          OR i.ipc_class_symbol LIKE 'H04L  45/%'
          OR i.ipc_class_symbol LIKE 'H04L  49/%'))
        OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
          c.cpc_class_symbol LIKE 'H04B  10/%'
          OR c.cpc_class_symbol LIKE 'H04J  14/%'
          OR c.cpc_class_symbol LIKE 'H04Q  11/%'
          OR c.cpc_class_symbol LIKE 'G02B   6/12%'
          OR c.cpc_class_symbol LIKE 'G02B   6/42%'
          OR c.cpc_class_symbol LIKE 'H01S   5/%'
          OR c.cpc_class_symbol LIKE 'G02F   1/01%'
          OR c.cpc_class_symbol LIKE 'G02F   1/21%'
          OR c.cpc_class_symbol LIKE 'H04L  45/%'
          OR c.cpc_class_symbol LIKE 'H04L  49/%'))
      )
      AND (
        LOWER(t.appln_title) LIKE '%data center%'
        OR LOWER(t.appln_title) LIKE '%datacenter%'
        OR LOWER(t.appln_title) LIKE '%data centre%'
        OR LOWER(b0.appln_abstract) LIKE '%data center%'
        OR LOWER(b0.appln_abstract) LIKE '%datacenter%'
        OR LOWER(b0.appln_abstract) LIKE '%data centre%'
        OR LOWER(b0.appln_abstract) LIKE '%hyperscale%'
      )
    )
  );

-- ----------------------------------------------------------------------------
-- Q2. Coherent 광전송·DSP 특화 (조원선 스택 ①: coherent DSP)
--   coherent 수신/변조 코드 또는 coherent 문구, DC 문맥 불요 (기술군 자체 수집)
-- ----------------------------------------------------------------------------
SELECT DISTINCT
 a.appln_id app_id, a.appln_auth patent_office, a.appln_nr app_num,
 a.earliest_filing_year priority_year, t.appln_title title,
 b0.appln_abstract abstract, a.docdb_family_size family_size, a.granted granted
FROM tls201_appln a
LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
LEFT JOIN tls203_appln_abstr b0 ON a.appln_id = b0.appln_id
WHERE a.earliest_filing_year BETWEEN YYYY AND YYYY
  AND a.granted = 'Y'
  AND (
    EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
      i.ipc_class_symbol LIKE 'H04B  10/61%'
      OR i.ipc_class_symbol LIKE 'H04B  10/54%'))
    OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
      c.cpc_class_symbol LIKE 'H04B  10/61%'
      OR c.cpc_class_symbol LIKE 'H04B  10/54%'))
    OR LOWER(t.appln_title) LIKE '%coherent optical%'
    OR LOWER(t.appln_title) LIKE '%coherent receiver%'
    OR LOWER(t.appln_title) LIKE '%coherent transceiver%'
    OR LOWER(t.appln_title) LIKE '%coherent transmission%'
    OR LOWER(b0.appln_abstract) LIKE '%coherent optical communication%'
    OR LOWER(b0.appln_abstract) LIKE '%coherent optical transmission%'
    OR LOWER(b0.appln_abstract) LIKE '%coherent receiver%'
    OR LOWER(b0.appln_abstract) LIKE '%coherent transceiver%'
    OR LOWER(b0.appln_abstract) LIKE '%digital coherent%'
  );

-- ----------------------------------------------------------------------------
-- Q3. 광부품 특화 (조원선 스택 ②③: 트랜시버·EML 레이저·CPO·실리콘 포토닉스)
--   부품 코드 × 광통신/DC 문맥, 또는 부품 직접 문구
-- ----------------------------------------------------------------------------
SELECT DISTINCT
 a.appln_id app_id, a.appln_auth patent_office, a.appln_nr app_num,
 a.earliest_filing_year priority_year, t.appln_title title,
 b0.appln_abstract abstract, a.docdb_family_size family_size, a.granted granted
FROM tls201_appln a
LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
LEFT JOIN tls203_appln_abstr b0 ON a.appln_id = b0.appln_id
WHERE a.earliest_filing_year BETWEEN YYYY AND YYYY
  AND a.granted = 'Y'
  AND (
    LOWER(t.appln_title) LIKE '%optical transceiver%'
    OR LOWER(t.appln_title) LIKE '%silicon photonic%'
    OR LOWER(t.appln_title) LIKE '%co-packaged optic%'
    OR LOWER(t.appln_title) LIKE '%electro-absorption modulat%'
    OR LOWER(t.appln_title) LIKE '%externally modulated laser%'
    OR LOWER(b0.appln_abstract) LIKE '%optical transceiver%'
    OR LOWER(b0.appln_abstract) LIKE '%silicon photonic%'
    OR LOWER(b0.appln_abstract) LIKE '%co-packaged optic%'
    OR LOWER(b0.appln_abstract) LIKE '%electro-absorption modulat%'
    OR LOWER(b0.appln_abstract) LIKE '%externally modulated laser%'
    OR LOWER(b0.appln_abstract) LIKE '%photonic integrated circuit%'
    OR (
      (
        EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
          i.ipc_class_symbol LIKE 'H04B  10/40%'
          OR i.ipc_class_symbol LIKE 'G02B   6/12%'
          OR i.ipc_class_symbol LIKE 'G02B   6/42%'
          OR i.ipc_class_symbol LIKE 'H01S   5/%'
          OR i.ipc_class_symbol LIKE 'G02F   1/01%'))
        OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
          c.cpc_class_symbol LIKE 'H04B  10/40%'
          OR c.cpc_class_symbol LIKE 'G02B   6/12%'
          OR c.cpc_class_symbol LIKE 'G02B   6/42%'
          OR c.cpc_class_symbol LIKE 'H01S   5/%'
          OR c.cpc_class_symbol LIKE 'G02F   1/01%'))
      )
      AND (
        LOWER(b0.appln_abstract) LIKE '%optical communication%'
        OR LOWER(b0.appln_abstract) LIKE '%optical network%'
        OR LOWER(b0.appln_abstract) LIKE '%data center%'
        OR LOWER(b0.appln_abstract) LIKE '%datacenter%'
        OR LOWER(b0.appln_abstract) LIKE '%wavelength division%'
      )
    )
  );

-- ----------------------------------------------------------------------------
-- Q4. 해저·장거리 (조원선 구분상 DCI 밖 >2,000km — 비교군)
--   기존 DC Network Stage 1.2 해저 코드 + 해저 문구
-- ----------------------------------------------------------------------------
SELECT DISTINCT
 a.appln_id app_id, a.appln_auth patent_office, a.appln_nr app_num,
 a.earliest_filing_year priority_year, t.appln_title title,
 b0.appln_abstract abstract, a.docdb_family_size family_size, a.granted granted
FROM tls201_appln a
LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
LEFT JOIN tls203_appln_abstr b0 ON a.appln_id = b0.appln_id
WHERE a.earliest_filing_year BETWEEN YYYY AND YYYY
  AND a.granted = 'Y'
  AND (
    EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
      i.ipc_class_symbol LIKE 'H02G   9/%'
      OR i.ipc_class_symbol LIKE 'H04B   3/52%'
      OR i.ipc_class_symbol LIKE 'H04B   3/54%'))
    OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
      c.cpc_class_symbol LIKE 'H02G   9/%'
      OR c.cpc_class_symbol LIKE 'H04B   3/52%'
      OR c.cpc_class_symbol LIKE 'H04B   3/54%'))
    OR LOWER(t.appln_title) LIKE '%submarine cable%'
    OR LOWER(t.appln_title) LIKE '%undersea cable%'
    OR LOWER(t.appln_title) LIKE '%submarine optical%'
    OR LOWER(b0.appln_abstract) LIKE '%submarine optical cable%'
    OR LOWER(b0.appln_abstract) LIKE '%undersea optical%'
    OR LOWER(b0.appln_abstract) LIKE '%submarine repeater%'
  );

-- ============================================================================
-- 사용 메모
-- 1) Q0로 연도별 건수 확인 후 9,999행 초과 연도는 range 분할 다운로드.
-- 2) Q1이 메인. 플래그 4종(has_dci_phrase, has_coherent_code,
--    has_component_code, has_dc_context)은 후속 keyword/embedding 분류에서
--    precision 판정에 사용 (has_dci_phrase=1은 무조건 유지 권장).
-- 3) Q2~Q4는 기술군별 보완 수집. 기존 Stage 1.2(광역 optical)와 app_id 기준
--    중복 제거 후 병합. Stage 2 enrichment는 기존 스크립트에
--    PATSTAT_STAGE1_RELEASE_LABEL override로 재사용.
-- 4) H01S 5/%, G02F 1/% 계열은 recall용 광범위 코드이므로 단독 매칭은
--    최종 판정 근거로 쓰지 말 것 (Stage 1.2의 has_optical_core_code 원칙과 동일).
-- 5) 비영어권(CN·JP·KR) 원문 특허는 영어 기계번역 title/abstract에 의존하므로
--    A.11 다국어 키워드 보정 원칙에 따라 후속 재분류에서 보강.
-- ============================================================================
