# Current expert-survey response analysis

Snapshot source: GitHub repo `deep1003/Physical-AI-Risk-Survey-Responses`, path `responses/`.
Analyzed structured JSON responses: 5; legacy Markdown-only responses included with recovered reference assignments: 1.

## Headline
- Completed respondents analyzed: 6
- Original pairwise judgments analyzed: 180
- Unique L4 cards covered so far: 128 / 182 (70.3%)
- Overall agreement with pre-specified L3 assignment: 141/180 (78.3%)
- Mean confidence: 3.37 / 5
- Reconsideration rows available: 12; changed: 5; switched to reference assignment: 5

## Respondent summary
| respondent | block | format | n | agreement | rate | mean confidence | expertise |
|---|---|---|---:|---:|---:|---:|---|
| R-4e32b07fe24b | A01 | json | 30 | 30 | 100.0% | 3.80 | AI safety |
| R-538c0ce57dff | A03 | md_legacy | 30 | 25 | 83.3% | 3.53 | AI safety; Risk governance |
| R-6727de20305f | A05 | json | 30 | 18 | 60.0% | 2.70 | AI safety; Risk governance; Standards or regulation |
| R-951c8affb6d8 | A04 | json | 30 | 23 | 76.7% | 3.07 | AI safety; Risk governance |
| R-a027ac600680 | A08 | json | 30 | 24 | 80.0% | 3.27 | Autonomous systems; Human–robot interaction; AI safety; Risk governance; Standards or regulation |
| R-ea6ca044ebf8 | A12 | json | 30 | 21 | 70.0% | 3.87 | Safety engineering; AI safety; Risk governance; Standards or regulation |

## Reference-L3 summary
| ref L3 | name | n | unique cards | agreement | rate | mean confidence |
|---|---|---:|---:|---:|---:|---:|
| I3.1 | 의도적·악의적 피해(Purposeful / Malicious Harm) | 17 | 12 | 13 | 76.5% | 3.35 |
| I3.10 | 상호작용 에이전트의 윤리·안전 함의(Ethical & Safety Implications of Interactive Agents) | 2 | 2 | 2 | 100.0% | 3.50 |
| I3.2 | 물리적 공격(Physical Attacks) | 2 | 1 | 2 | 100.0% | 3.00 |
| I3.3 | 사이버보안 위협(Cybersecurity Threats) | 4 | 2 | 0 | 0.0% | 2.50 |
| I3.4 | 센서·입력 검증 실패(Sensor & Input Validation Failures) | 4 | 3 | 3 | 75.0% | 4.00 |
| I3.5 | 허위 정보(Misinformation) | 6 | 4 | 3 | 50.0% | 3.33 |
| I3.6 | 동적 환경 요인(Dynamic Environmental Factors) | 8 | 6 | 7 | 87.5% | 2.50 |
| I3.7 | 인간 상호작용·안전 프로토콜 실패(Human Interaction & Safety Protocol Failures) | 13 | 8 | 11 | 84.6% | 3.62 |
| I3.8 | 지시 오해석(Instruction Misinterpretation) | 2 | 1 | 2 | 100.0% | 4.00 |
| I3.9 | 멀티 에이전트 협력(Multi-Agent Collaboration) | 5 | 4 | 4 | 80.0% | 3.80 |
| P3.1 | 우발적 피해(Accidental Harm) | 21 | 16 | 11 | 52.4% | 3.48 |
| P3.2 | 로봇 제어(Robot Control) | 43 | 32 | 38 | 88.4% | 3.26 |
| P3.3 | 하드웨어·기계적 결함(Hardware & Mechanical Failures) | 2 | 2 | 1 | 50.0% | 2.00 |
| P3.4 | 소프트웨어 취약점·설계 결함(Software Vulnerabilities & Design Flaws) | 7 | 5 | 7 | 100.0% | 3.86 |
| P3.5 | 미학습 환경에서의 강건성 부재(Lack of Robustness in Unseen Environments) | 12 | 9 | 12 | 100.0% | 3.67 |
| S3.1 | 프라이버시 침해(Privacy Violations) | 6 | 5 | 6 | 100.0% | 4.17 |
| S3.2 | 노동 대체(Labor Displacement) | 2 | 1 | 1 | 50.0% | 3.50 |
| S3.3 | 사회경제적 불평등(Socioeconomic Inequality) | 1 | 1 | 1 | 100.0% | 4.00 |
| S3.4 | 권력 집중(Power Concentration) | 2 | 1 | 0 | 0.0% | 4.00 |
| S3.5 | 편향·차별(Bias & Discrimination) | 3 | 2 | 3 | 100.0% | 4.00 |
| S3.6 | 책임·배상 부재(Lack of Accountability & Liability) | 12 | 7 | 8 | 66.7% | 3.00 |
| S3.7 | 투명성·설명 가능성·신뢰 부재(Lack of Transparency, Explainability & Trust) | 2 | 1 | 2 | 100.0% | 1.50 |
| S3.8 | 인간-EAI의 해로운 관계(Unhealthy / Dangerous Human-EAI Relationships) | 4 | 3 | 4 | 100.0% | 3.50 |

## Lowest-agreement observed cards
| card | reference L3 | n | agreement rate | mean confidence | selected counts | label |
|---|---|---:|---:|---:|---|---|
| PHYSBENCH-REF-0022 | I3.1 | 2 | 0.0% | 3.00 | I3.4:2 | 피지컬 AI 파괴 행위 (Embodied sabotage) |
| PHYSBENCH-REF-0043 | I3.3 | 2 | 0.0% | 3.00 | I3.4:2 | 로봇 백도어 공격 취약성 (Robotic backdoor attack vulnerability) |
| PHYSBENCH-REF-0065 | I3.7 | 2 | 0.0% | 3.00 | I3.6:2 | 휴머노이드 균형 상실 및 낙상 위험 (Humanoid balance-loss and fall risk) |
| PHYSRISK-REF-0031 | I3.3 | 2 | 0.0% | 2.00 | I3.2:2 | 핵심 인프라 로봇 파괴 (Critical infrastructure robotic sabotage) |
| PHYSRISK-REF-0054 | S3.4 | 2 | 0.0% | 4.00 | S3.3:2 | 동료 로봇의 감시 노드 전용화 (Co-worker robot as surveillance node) |
| PHYSBENCH-REF-0012 | P3.1 | 1 | 0.0% | 3.00 | P3.5:1 | 복합 물리적 제약 위반 (Compositional physical constraint violation) |
| PHYSBENCH-REF-0016 | P3.3 | 1 | 0.0% | 3.00 | P3.2:1 | 하드웨어 한계 리스크 (Embodiment-specific hardware limitation failure) |
| PHYSBENCH-REF-0026 | P3.2 | 1 | 0.0% | 4.00 | P3.1:1 | 위험 도구 작업 공간 침입 (Hazardous-tool workspace intrusion) |
| PHYSBENCH-REF-0039 | P3.1 | 1 | 0.0% | 4.00 | P3.4:1 | 물리적 상호작용 안전 공백 (Physical interaction safety control gap) |
| PHYSBENCH-REF-0058 | P3.1 | 1 | 0.0% | 2.00 | P3.4:1 | 로봇 형태 전이 리스크 (Robot morphology transfer risk) |
| PHYSBENCH-REF-0063 | I3.6 | 1 | 0.0% | 2.00 | I3.9:1 | 시각-촉각 모달리티 불일치 (Visual-tactile modality mismatch) |
| PHYSBENCH-REF-0064 | P3.1 | 1 | 0.0% | 3.00 | P3.4:1 | 인간 시연 전이 모호성 (Human demonstration transfer ambiguity) |
| PHYSBENCH-REF-0077 | P3.1 | 1 | 0.0% | 3.00 | P3.2:1 | 모션 리타겟팅 안전 실패 (Motion-retargeting safety failure) |
| PHYSBENCH-REF-0081 | P3.1 | 1 | 0.0% | 4.00 | P3.2:1 | 휴머노이드 제로샷 전이 불안정성 (Zero-shot humanoid sim-to-real instability) |
| PHYSBENCH-REF-0090 | P3.1 | 1 | 0.0% | 3.00 | P3.2:1 | 장기 예측 누적 오차 (Long-horizon rollout drift) |
| PHYSBENCH-REF-0092 | I3.5 | 1 | 0.0% | 2.00 | I3.4:1 | 미래 접촉 예측 실패 (Future contact prediction failure) |
| PHYSBENCH-REF-0094 | S3.6 | 1 | 0.0% | 1.00 | S3.7:1 | 로봇 헌법 커버리지 공백 (Robot constitution coverage gap) |
| PHYSKR-REF-017 | S3.6 | 1 | 0.0% | 2.00 | S3.9:1 | 피지컬 AI 사고 보고 체계 부재 (Absence of standardized embodied-incident reporting) |
| PHYSRISK-REF-0009 | P3.2 | 1 | 0.0% | 4.00 | P3.5:1 | 동적 장애물 반응 실패 (Dynamic obstacle response failure) |
| PHYSRISK-REF-0030 | I3.1 | 1 | 0.0% | 4.00 | I3.2:1 | 로봇의 무기화 오남용 (Robot-as-weapon misuse) |

## Confidence summary
| confidence | n | agreement rate |
|---:|---:|---:|
| 1 | 15 | 73.3% |
| 2 | 17 | 58.8% |
| 3 | 52 | 73.1% |
| 4 | 78 | 82.1% |
| 5 | 18 | 100.0% |

## Demographics
- Age bands: {'25–34세 / 25–34': 2, '35–44세 / 35–44': 1, '45–54세 / 45–54': 3}
- Gender: {'남성 / Man': 4, '여성 / Woman': 2}
- Career: {'3–5년 / 3–5 years': 2, '1–2년 / 1–2 years': 1, '6–10년 / 6–10 years': 1, '16년 이상 / 16+ years': 2}
- Expertise: {'AI safety': 6, 'Risk governance': 5, 'Standards or regulation': 3, 'Autonomous systems': 1, 'Human–robot interaction': 1, 'Safety engineering': 1}

## Data-quality notes
- Planned minimum completed responses is 20, so current results are exploratory and should not be cited as final validation.
- One legacy Markdown-only response has no JSON/CSV companion and no reconsideration fields. Its reference assignment was recovered from the current L4 taxonomy by card ID.
- Public static survey files matched the local files in the previous deployment check.