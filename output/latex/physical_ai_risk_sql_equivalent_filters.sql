-- SQL-equivalent reproducibility specification for AI -> Physical AI -> Physical AI Risks
-- This file documents the filtering logic used after AI-corpus retrieval.
-- The actual local extraction was implemented in:
--   ../50_physical_ai_dataset/04_scripts/build_physical_ai_dataset.py
-- and audited in:
--   ../50_physical_ai_dataset/05_logs/physical_ai_dataset_manifest.json
--   ../50_physical_ai_dataset/03_audit/physical_ai_collection_status_20260627.md

-- -------------------------------------------------------------------------
-- Stage 1. Physical AI selection from AI corpus
-- Select if either:
--   A. a strong Physical AI marker appears in title/abstract/keywords/classification text; or
--   B. a broad perception/control term appears together with a physical/embodied/robotic context marker.
-- -------------------------------------------------------------------------

WITH normalized_ai_corpus AS (
  SELECT
    source_family,
    source_id,
    year,
    LOWER(CONCAT_WS(' ',
      title,
      abstract,
      keywords,
      l1_label,
      l2_label,
      l3_label,
      ipc,
      cpc,
      source_metadata
    )) AS doc_text
  FROM ai_corpus
),
physical_ai_candidates AS (
  SELECT *
  FROM normalized_ai_corpus
  WHERE
    (
      doc_text LIKE '%physical ai%'
      OR doc_text LIKE '%physical artificial intelligence%'
      OR doc_text LIKE '%embodied ai%'
      OR doc_text LIKE '%embodied artificial intelligence%'
      OR doc_text LIKE '%embodied agent%'
      OR doc_text LIKE '%embodied agents%'
      OR doc_text LIKE '%embodied intelligence%'
      OR doc_text LIKE '%robot%'
      OR doc_text LIKE '%robotic%'
      OR doc_text LIKE '%robotics%'
      OR doc_text LIKE '%humanoid%'
      OR doc_text LIKE '%autonomous vehicle%'
      OR doc_text LIKE '%autonomous vehicles%'
      OR doc_text LIKE '%autonomous driving%'
      OR doc_text LIKE '%autonomous car%'
      OR doc_text LIKE '%autonomous mobility%'
      OR doc_text LIKE '%autonomous system%'
      OR doc_text LIKE '%autonomous systems%'
      OR doc_text LIKE '%autonomous weapons%'
      OR doc_text LIKE '%self-driving%'
      OR doc_text LIKE '%drone%'
      OR doc_text LIKE '%uav%'
      OR doc_text LIKE '%unmanned%'
      OR doc_text LIKE '%cyber-physical%'
      OR doc_text LIKE '%cyber physical%'
      OR doc_text LIKE '%cps%'
      OR doc_text LIKE '%digital twin%'
      OR doc_text LIKE '%digital twins%'
      OR doc_text LIKE '%sensor fusion%'
      OR doc_text LIKE '%simultaneous localization and mapping%'
      OR doc_text LIKE '%simultaneous localisation and mapping%'
      OR doc_text LIKE '%slam%'
      OR doc_text LIKE '%sim-to-real%'
      OR doc_text LIKE '%sim to real%'
      OR doc_text LIKE '%robotic manipulation%'
      OR doc_text LIKE '%manipulation%'
      OR doc_text LIKE '%grasping%'
      OR doc_text LIKE '%gripper%'
      OR doc_text LIKE '%navigation%'
      OR doc_text LIKE '%motion planning%'
      OR doc_text LIKE '%path planning%'
      OR doc_text LIKE '%mobile robot%'
      OR doc_text LIKE '%service robot%'
      OR doc_text LIKE '%industrial robot%'
      OR doc_text LIKE '%collaborative robot%'
      OR doc_text LIKE '%cobot%'
      OR doc_text LIKE '%machine vision%'
      OR doc_text LIKE '%smart manufacturing%'
      OR doc_text LIKE '%smart factory%'
      OR doc_text LIKE '%factory automation%'
      OR doc_text LIKE '%industrial automation%'
      OR doc_text LIKE '%actuator%'
      OR doc_text LIKE '%actuation%'
      OR doc_text LIKE '%robot control%'
      OR doc_text LIKE '%vehicle control%'
      OR doc_text LIKE '%physical safety%'
      OR doc_text LIKE '%피지컬 ai%'
      OR doc_text LIKE '%피지컬 인공지능%'
      OR doc_text LIKE '%물리 인공지능%'
      OR doc_text LIKE '%물리적 인공지능%'
      OR doc_text LIKE '%체화 인공지능%'
      OR doc_text LIKE '%체화형 인공지능%'
      OR doc_text LIKE '%임바디드%'
      OR doc_text LIKE '%로봇%'
      OR doc_text LIKE '%로보틱스%'
      OR doc_text LIKE '%휴머노이드%'
      OR doc_text LIKE '%자율주행%'
      OR doc_text LIKE '%자율 주행%'
      OR doc_text LIKE '%자율주행차%'
      OR doc_text LIKE '%자율 차량%'
      OR doc_text LIKE '%자율무기%'
      OR doc_text LIKE '%자율 무기%'
      OR doc_text LIKE '%무인%'
      OR doc_text LIKE '%드론%'
      OR doc_text LIKE '%사이버 물리%'
      OR doc_text LIKE '%사이버-물리%'
      OR doc_text LIKE '%디지털 트윈%'
      OR doc_text LIKE '%센서 융합%'
      OR doc_text LIKE '%동시 위치%'
      OR doc_text LIKE '%지도 작성%'
      OR doc_text LIKE '%로봇 조작%'
      OR doc_text LIKE '%파지%'
      OR doc_text LIKE '%그리퍼%'
      OR doc_text LIKE '%내비게이션%'
      OR doc_text LIKE '%네비게이션%'
      OR doc_text LIKE '%동작 계획%'
      OR doc_text LIKE '%경로 계획%'
      OR doc_text LIKE '%이동 로봇%'
      OR doc_text LIKE '%서비스 로봇%'
      OR doc_text LIKE '%산업용 로봇%'
      OR doc_text LIKE '%협동로봇%'
      OR doc_text LIKE '%협동 로봇%'
      OR doc_text LIKE '%기계 비전%'
      OR doc_text LIKE '%스마트팩토리%'
      OR doc_text LIKE '%스마트 팩토리%'
      OR doc_text LIKE '%공장 자동화%'
      OR doc_text LIKE '%제조 자동화%'
      OR doc_text LIKE '%액추에이터%'
      OR doc_text LIKE '%물리적 안전%'
    )
    OR
    (
      (
        doc_text LIKE '%computer vision%'
        OR doc_text LIKE '%object detection%'
        OR doc_text LIKE '%object recognition%'
        OR doc_text LIKE '%image recognition%'
        OR doc_text LIKE '%image segmentation%'
        OR doc_text LIKE '%semantic segmentation%'
        OR doc_text LIKE '%instance segmentation%'
        OR doc_text LIKE '%scene understanding%'
        OR doc_text LIKE '%action recognition%'
        OR doc_text LIKE '%visual perception%'
        OR doc_text LIKE '%vision-language%'
        OR doc_text LIKE '%vision language%'
        OR doc_text LIKE '%visual navigation%'
        OR doc_text LIKE '%remote sensing%'
        OR doc_text LIKE '%reinforcement learning%'
        OR doc_text LIKE '%safe reinforcement learning%'
        OR doc_text LIKE '%control%'
        OR doc_text LIKE '%optimal control%'
        OR doc_text LIKE '%sensor%'
        OR doc_text LIKE '%sensing%'
        OR doc_text LIKE '%perception%'
        OR doc_text LIKE '%컴퓨터비전%'
        OR doc_text LIKE '%컴퓨터 비전%'
        OR doc_text LIKE '%객체탐지%'
        OR doc_text LIKE '%객체 탐지%'
        OR doc_text LIKE '%객체인식%'
        OR doc_text LIKE '%객체 인식%'
        OR doc_text LIKE '%이미지 인식%'
        OR doc_text LIKE '%영상인식%'
        OR doc_text LIKE '%영상 인식%'
        OR doc_text LIKE '%이미지 분할%'
        OR doc_text LIKE '%영상 분할%'
        OR doc_text LIKE '%장면 이해%'
        OR doc_text LIKE '%행동 인식%'
        OR doc_text LIKE '%강화학습%'
        OR doc_text LIKE '%강화 학습%'
        OR doc_text LIKE '%제어%'
        OR doc_text LIKE '%센서%'
        OR doc_text LIKE '%감지%'
        OR doc_text LIKE '%인지%'
      )
      AND
      (
        doc_text LIKE '%physical%'
        OR doc_text LIKE '%embodied%'
        OR doc_text LIKE '%robot%'
        OR doc_text LIKE '%robotic%'
        OR doc_text LIKE '%robotics%'
        OR doc_text LIKE '%humanoid%'
        OR doc_text LIKE '%autonomous%'
        OR doc_text LIKE '%vehicle%'
        OR doc_text LIKE '%driving%'
        OR doc_text LIKE '%drone%'
        OR doc_text LIKE '%uav%'
        OR doc_text LIKE '%unmanned%'
        OR doc_text LIKE '%mobility%'
        OR doc_text LIKE '%cyber-physical%'
        OR doc_text LIKE '%cyber physical%'
        OR doc_text LIKE '%digital twin%'
        OR doc_text LIKE '%manufacturing%'
        OR doc_text LIKE '%factory%'
        OR doc_text LIKE '%industrial%'
        OR doc_text LIKE '%machine vision%'
        OR doc_text LIKE '%sensor fusion%'
        OR doc_text LIKE '%slam%'
        OR doc_text LIKE '%navigation%'
        OR doc_text LIKE '%manipulation%'
        OR doc_text LIKE '%grasp%'
        OR doc_text LIKE '%actuator%'
        OR doc_text LIKE '%물리%'
        OR doc_text LIKE '%체화%'
        OR doc_text LIKE '%임바디%'
        OR doc_text LIKE '%로봇%'
        OR doc_text LIKE '%휴머노이드%'
        OR doc_text LIKE '%자율%'
        OR doc_text LIKE '%차량%'
        OR doc_text LIKE '%주행%'
        OR doc_text LIKE '%드론%'
        OR doc_text LIKE '%무인%'
        OR doc_text LIKE '%모빌리티%'
        OR doc_text LIKE '%사이버 물리%'
        OR doc_text LIKE '%디지털 트윈%'
        OR doc_text LIKE '%제조%'
        OR doc_text LIKE '%공장%'
        OR doc_text LIKE '%산업%'
        OR doc_text LIKE '%센서 융합%'
        OR doc_text LIKE '%내비게이션%'
        OR doc_text LIKE '%네비게이션%'
        OR doc_text LIKE '%조작%'
        OR doc_text LIKE '%파지%'
        OR doc_text LIKE '%액추에이터%'
      )
    )
)

-- -------------------------------------------------------------------------
-- Stage 2. Physical AI Risk subset from Physical AI candidates
-- Apply risk/safety/security/ethics/failure terms to title/abstract/keyword text.
-- This produces the Physical AI risk subset used for L4 risk-card generation.
-- -------------------------------------------------------------------------

SELECT *
FROM physical_ai_candidates
WHERE
  doc_text LIKE '%risk%'
  OR doc_text LIKE '%risks%'
  OR doc_text LIKE '%safety%'
  OR doc_text LIKE '%safe%'
  OR doc_text LIKE '%unsafe%'
  OR doc_text LIKE '%harm%'
  OR doc_text LIKE '%hazard%'
  OR doc_text LIKE '%accident%'
  OR doc_text LIKE '%failure%'
  OR doc_text LIKE '%fault%'
  OR doc_text LIKE '%error%'
  OR doc_text LIKE '%robustness%'
  OR doc_text LIKE '%vulnerability%'
  OR doc_text LIKE '%threat%'
  OR doc_text LIKE '%attack%'
  OR doc_text LIKE '%security%'
  OR doc_text LIKE '%cybersecurity%'
  OR doc_text LIKE '%privacy%'
  OR doc_text LIKE '%ethics%'
  OR doc_text LIKE '%ethical%'
  OR doc_text LIKE '%bias%'
  OR doc_text LIKE '%discrimination%'
  OR doc_text LIKE '%accountability%'
  OR doc_text LIKE '%liability%'
  OR doc_text LIKE '%transparency%'
  OR doc_text LIKE '%explainability%'
  OR doc_text LIKE '%trust%'
  OR doc_text LIKE '%misinformation%'
  OR doc_text LIKE '%misalignment%'
  OR doc_text LIKE '%jailbreak%'
  OR doc_text LIKE '%prompt injection%'
  OR doc_text LIKE '%안전%'
  OR doc_text LIKE '%위험%'
  OR doc_text LIKE '%리스크%'
  OR doc_text LIKE '%위해%'
  OR doc_text LIKE '%유해%'
  OR doc_text LIKE '%사고%'
  OR doc_text LIKE '%실패%'
  OR doc_text LIKE '%오류%'
  OR doc_text LIKE '%결함%'
  OR doc_text LIKE '%취약%'
  OR doc_text LIKE '%공격%'
  OR doc_text LIKE '%보안%'
  OR doc_text LIKE '%프라이버시%'
  OR doc_text LIKE '%윤리%'
  OR doc_text LIKE '%편향%'
  OR doc_text LIKE '%차별%'
  OR doc_text LIKE '%책임%'
  OR doc_text LIKE '%투명%'
  OR doc_text LIKE '%설명가능%'
  OR doc_text LIKE '%신뢰%'
  OR doc_text LIKE '%허위%'
  OR doc_text LIKE '%탈옥%'
  OR doc_text LIKE '%프롬프트 주입%';
