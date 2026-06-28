# Unreferenced Corpus L4 Reference Addition Round 3

- 병렬 에이전트 호출: 시도했으나 사용량 제한으로 3개 모두 실패
- Access-checked unreferenced Top 400: 400
- Top 400 access OK: True
- 2024+ in Top 400: 232
- 2023+ in Top 400: 292
- Initial auto additions: 14
- Removed after quality review: 9
- Kept additions: 5
- Cards touched: 5
- Max references after: 5
- Cards over 5 references: 0

## Kept Additions

- **PHYSBENCH-REF-0032** 안전 강화학습 제약 위반 (Safe reinforcement learning constraint violation) -> 3D RVO-enhanced multi-agent deep reinforcement learning for collision avoidance in urban structured airspace (2025)
  - 근거: 다중 에이전트 강화학습으로 도시 공역 충돌 회피를 다뤄, 안전 제약이 빠진 학습 정책은 충돌 위험을 남길 수 있다 (Zhong et al., 2025)
  - URL: https://doi.org/10.1016/j.ast.2025.110378
- **PHYSBENCH-REF-0055** 제어 장벽 함수 실패 (Control barrier function safety-filter failure) -> Meta-Learning-Based Safety-Critical Control in Multi-Obstacles Environments (2025)
  - 근거: 여러 장애물 환경의 safety-critical control을 다뤄, 안전 필터가 실패하면 제어 장벽이 의도한 충돌 회피를 보장하지 못할 수 있다 (Zhang et al., 2025)
  - URL: https://doi.org/10.1109/tase.2025.3565524
- **PHYSBENCH-REF-0068** 정밀 휴머노이드 접촉력 위험 (Dexterous humanoid contact-force risk) -> A biomimetic elastomeric robot skin using electrical impedance and acoustic tomography for tactile sensing (2022)
  - 근거: 로봇 피부가 접촉 위치와 힘을 감지하는 방식을 다뤄, 정밀 휴머노이드 접촉력 위험을 줄이려면 촉각 센싱이 핵심임을 보여준다 (Park et al., 2022)
  - URL: https://doi.org/10.1126/scirobotics.abm7187
- **PHYSRISK-REF-0004** 적대적 물체·표지 조작 (Adversarial object or sign manipulation) -> Deep learning adversarial attacks and defenses in autonomous vehicles: a systematic literature review from a safet… (2024)
  - 근거: 자율주행 딥러닝 모델의 적대적 공격·방어를 안전 관점에서 정리해, 표지·객체 조작이 주행 판단을 흔들 수 있음을 보여준다 (Ibrahum et al., 2024)
  - URL: https://doi.org/10.1007/s10462-024-11014-8
- **PHYSRISK-REF-0009** 동적 장애물 반응 실패 (Dynamic obstacle response failure) -> Efficient multi-UAV path planning in dynamic and complex environments using hybrid polar lights optimization (2025)
  - 근거: 동적·복잡 환경의 다중 UAV 경로계획을 다뤄, 움직이는 장애물 대응 실패가 비행 충돌 위험으로 이어질 수 있음을 보여준다 (Xu et al., 2025)
  - URL: https://doi.org/10.1007/s44443-025-00139-7

## Removed After Quality Review

- **PHYSBENCH-REF-0063** 시각-촉각 모달리티 불일치 (Visual-tactile modality mismatch) -> Factors that influence robot acceptance (2020)
- **PHYSBENCH-REF-0069** 전신 도달 한계 위반 (Whole-body reach-limit violation) -> A biomimetic elastomeric robot skin using electrical impedance and acoustic tomography for tactile sensing (2022)
- **PHYSBENCH-REF-0085** 가정 장기 계획 조작 위험 (Household long-horizon manipulation risk) -> Human-robot collaborative visual inspection with Large Language Models☆ (2026)
- **PHYSBENCH-REF-0088** 이동-조작 통합 실패 (Locomotion-integrated manipulation failure) -> Human-robot collaborative visual inspection with Large Language Models☆ (2026)
- **PHYSBENCH-REF-0104** 휴머노이드 충돌력 초과 (Humanoid collision-force exceedance) -> Memory-driven deep-reinforcement learning for autonomous robot navigation in partially observable environments (2025)
- **PHYSRISK-REF-0001** 가림에 의한 충돌 (Occlusion-induced collision) -> Collision avoidance for autonomous ship using deep reinforcement learning and prior-knowledge-based approximate re… (2023)
- **PHYSRISK-REF-0003** 다중 센서 융합 충돌 (Multimodal sensor fusion conflict) -> All-printed soft human-machine interface for robotic physicochemical sensing (2022)
- **PHYSRISK-REF-0020** 실시간 지연 및 동기화 실패 (Real-time latency and synchronization failure) -> Enhanced Small Drone Detection Using Optimized YOLOv8 With Attention Mechanisms (2024)
- **PHYSRISK-REF-0027** 센서 스푸핑 및 신호 주입 (Sensor spoofing and signal injection) -> All-printed soft human-machine interface for robotic physicochemical sensing (2022)

## Preexisting Link/Justification Count Mismatches

- **PHYSRISK-REF-0045** 물리적 침입 및 절도 (Autonomous physical intrusion and theft) — 근거 2 / 링크 1
- **PHYSRISK-REF-0046** 표적 추적 및 물리적 괴롭힘 (Targeted following and physical harassment) — 근거 1 / 링크 0
- **PHYSRISK-REF-0044** 현장 무기 부착 휴머노이드 (Field weapon attachment to humanoid) — 근거 1 / 링크 0
- **PHYSRISK-REF-0054** 동료 로봇의 감시 노드 전용화 (Co-worker robot as surveillance node) — 근거 1 / 링크 0
- **PHYSRISK-REF-0047** 의인화 유발 과의존 (Anthropomorphism-induced overreliance) — 근거 1 / 링크 0
- **PHYSRISK-REF-0049** 준사회적 애착과 조종 위험 (Parasocial attachment and manipulability) — 근거 1 / 링크 0
- **PHYSRISK-REF-0050** 아동 상호작용 안전 위험 (Child-interaction developmental and safety risk) — 근거 2 / 링크 1