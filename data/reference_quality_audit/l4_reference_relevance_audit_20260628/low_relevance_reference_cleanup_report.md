# Low-Relevance Reference Cleanup Report

- Removed references: 10
- Fixed justification mismatches: 4
- Links after cleanup: 306
- Justifications after cleanup: 315
- Max refs after cleanup: 5
- Cards over 5 refs: 0
- Backup: `/Users/deep1003/data3/AI_Topic_Space.github.io/pages/pai_risk_taxonomy_bilingual_v1.0.bak_before_low_relevance_ref_cleanup_20260628_000419.html`

## Removed References

- **PHYSBENCH-REF-0018** 언어-행동 안전 정렬 실패 (Linguistic-action safety misalignment)
  - Removed: Safety Moderation Benchmark (mvrcii)
  - Reason: 일반 텍스트 안전 분류 벤치마크라서 embodied 행동 정렬 실패의 피지컬 실행 맥락을 직접 보강하지 못함
- **PHYSBENCH-REF-0019** 물리적 행동 기만 (Conceptual deception in physical action)
  - Removed: DynamoAI Safety Benchmark (DynamoAI)
  - Reason: 콘텐츠 조정 벤치마크로 보이며 물리적 행동 기만이나 로봇 실행 사례와 직접 연결이 약함
- **PHYSBENCH-REF-0020** 악의적 행동 요청 (Malicious physical action query execution)
  - Removed: Harmful Behaviors (mlabonne)
  - Reason: 일반 유해 프롬프트 데이터셋이라 악의적 피지컬 행동 실행과 embodied 맥락이 부족함
- **PHYSBENCH-REF-0024** 피지컬 AI의 혐오·학대 행동 (Hateful or abusive embodied action)
  - Removed: Harmful Behaviors (mlabonne)
  - Reason: 일반 유해 행동 프롬프트 데이터셋이라 혐오·학대 행동의 로봇 실행 근거로는 약함
- **PHYSBENCH-REF-0030** 감각 교란 기반 비안전 행동 (Adversarial sensory perturbation induced unsafe action)
  - Removed: ANNIE: Be Careful of Your Robots
  - Reason: 광범위한 Robots 문헌으로, 감각 교란·적대적 센서 공격을 직접 다루는 문헌은 아님
- **PHYSBENCH-REF-0031** 영상-행동 공격 안전 위반 (Safety violation under video-action attack)
  - Removed: ANNIE: Be Careful of Your Robots
  - Reason: 제목이 광범위한 Robots 문헌으로, 영상-행동 공격이나 비디오 입력 조작 안전 위반을 직접 다루는 근거로는 약함
- **PHYSCONN-REF-003** 네트워크 분리와 군집 비동기화 (Network partition and fleet desynchronization)
  - Removed: + An efficient neural network approach to dy… (2000)
  - Reason: 동적 로봇 모션 계획 논문이지 네트워크 분리나 군집 비동기화를 다루는 문헌이 아님
- **PHYSCONN-REF-004** 제어 루프 데드라인 미달 (Control-loop deadline miss)
  - Removed: + A bioinspired neural network for real-time… (2008)
  - Reason: 실시간 지도작성·커버리지 내비게이션 논문으로, 제어 루프 deadline miss의 근거로는 직접성이 낮음
- **PHYSCONN-REF-005** 인지·추론 지연 급증 (Perception and inference latency spike)
  - Removed: + Adaptive network fuzzy inference system ba… (2019)
  - Reason: 여기서 network는 퍼지/신경망 의미에 가깝고, 인지·추론 지연 급증을 직접 다루지 않음
- **PHYSCONN-REF-009** 안전 폴백 실패 (Degraded-mode and safe-fallback failure)
  - Removed: + An efficient neural network approach to dy… (2000)
  - Reason: 동적 로봇 모션 계획 논문이지 degraded mode나 safe fallback 실패를 다루는 근거가 아님

## Fixed Justifications

- **PHYSKR-REF-009** ref #1
  - New: 돌봄 로봇은 노인의 독립성과 돌봄 관계를 바꿀 수 있어, 방치와 존엄성 침해 문제를 함께 봐야 한다 (Granny and the robots, 2010)
- **PHYSKR-REF-009** ref #2
  - New: 정신건강 로봇 사용에서 동의, 책임, 취약 사용자 보호 문제가 직접 제기된다 (Your Robot Therapist Will See You Now, 2019)
- **PHYSKR-REF-009** ref #3
  - New: 의료 AI 신뢰성과 설명 가능성 논의는 환자 보호와 책임 문제를 점검하게 한다 (Trustworthy and explainable AI in healthcare, 2023)
- **PHYSRISK-REF-0055** ref #1
  - New: 로봇 표준과 공공 규제가 어긋나면 감독이 약한 기준을 골라 배포할 여지가 생긴다 (Robots, standards and the law, 2019)