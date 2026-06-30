# MITRE ATLAS v2026.05 vs Physical AI L4 Gap Review

이 문서는 MITRE ATLAS v2026.05의 Generative AI / Agentic AI technique을 현재 Physical AI Risk Taxonomy L4 카드와 보수적으로 대조한 검토본이다.

## 결론
현재 taxonomy는 프롬프트 주입, 탈옥, 물리 행동 전환, 공급망/클라우드/API 침해, 연산 고갈, 데이터 유출, 은닉 트리거를 이미 폭넓게 포함한다. 다만 ATLAS 2026.05의 Agentic AI 고유 항목 중 일부는 “도구 호출, 에이전트 설정, 지속 메모리, 자격증명, 지연 실행, UI/렌더링 조작” 레이어에서 독립 L4 후보로 검토할 가치가 있다.

## 신규 또는 세분화 후보
| 후보 Physical AI L4 위험 | 관련 ATLAS technique | 판단 | 현재 taxonomy와의 관계 |
|---|---|---|---|
| Agent tool invocation to physical actuation | AML.T0053 AI Agent Tool Invocation; AML.T0086 Exfiltration via AI Agent Tool Invocation; AML.T0101 Data Destruction via AI Agent Tool Invocation | AI agent가 외부 도구를 호출해 물리 장치·로봇·현장 시스템 명령을 실행하는 경로 자체를 다룬다. | 프롬프트→행동 주입, 클라우드/API 침해, 파괴 행위로 일부 커버되지만 “도구 호출 권한/승인 경로”가 독립 실패 메커니즘으로 명명되어 있지 않다. |
| Poisoned / malicious agent tool supply chain | AML.T0011.002 Poisoned AI Agent Tool; AML.T0099 AI Agent Tool Data Poisoning; AML.T0104 Publish Poisoned AI Agent Tool; AML.T0110 AI Agent Tool Poisoning; AML.T0010.005 AI Agent Tool | 오염된 에이전트 도구·도구 데이터·도구 정의가 정상 도구처럼 등록되어 행동 정책을 오염시키는 공격면이다. | 공급망·은닉 트리거·소프트웨어 취약점으로 일부 커버되지만 Agentic tool/MCP 스타일 도구 오염은 더 구체적이다. |
| Agent configuration compromise | AML.T0081 Modify AI Agent Configuration; AML.T0083 Credentials from AI Agent Configuration; AML.T0084 Discover AI Agent Configuration; AML.T0084.000 Embedded Knowledge; AML.T0084.001 Tool Definitions; AML.T0084.002 Activation Triggers; AML.T0084.003 Call Chains | 에이전트 설정, 내장 지식, 도구 정의, 활성화 트리거, 호출 체인이 노출·수정되는 위험이다. | 로봇 헌법 누락/프로토콜 위반/클라우드 침해와 겹치지만 “agent configuration” 레이어가 독립 L4로는 보이지 않는다. |
| Persistent context or memory poisoning | AML.T0080 AI Agent Context Poisoning; AML.T0080.000 Memory; AML.T0080.001 Thread; AML.T0092 Manipulate User LLM Chat History | 메모리·스레드·대화 기록이 오염되어 이후 물리 행동 판단까지 지속적으로 왜곡되는 위험이다. | 프롬프트 주입/탈옥은 있으나 일회성 입력보다 긴 지속 컨텍스트 오염은 별도 정의가 약하다. |
| Delayed / triggered instruction execution | AML.T0051.002 Triggered; AML.T0094 Delay Execution of LLM Instructions | 조건이 충족될 때 뒤늦게 실행되는 지시가 물리 행동 시점에서 안전 검사를 우회하는 위험이다. | 은닉 트리거 카드는 있으나 훈련·배포 파이프라인 중심이고, agent instruction delayed execution은 부분 커버다. |
| Credential-mediated physical control escalation | AML.T0082 RAG Credential Harvesting; AML.T0098 AI Agent Tool Credential Harvesting; AML.T0083 Credentials from AI Agent Configuration; AML.T0024 Exfiltration via AI Inference API; AML.T0085 Data from AI Services; AML.T0085.001 AI Agent Tools | RAG·도구·설정에서 자격증명을 탈취해 로봇/현장 시스템 제어 권한으로 확장하는 위험이다. | 가정 내 정보 유출이나 클라우드/API 침해는 있으나 “credential → actuator/control escalation” 사슬은 명확히 분리되어 있지 않다. |
| Trusted output / UI rendering manipulation for operator action | AML.T0067 LLM Trusted Output Components Manipulation; AML.T0067.000 Citations; AML.T0077 LLM Response Rendering; AML.T0100 AI Agent Clickbait | 인용·렌더링·클릭 유도·UI 표시를 조작해 운영자나 agent가 잘못된 물리 명령을 승인하게 만드는 위험이다. | 기만/프롬프트 주입과 겹치지만 운영자 승인 UI와 trusted output 조작은 Physical AI 운용에서 별도 위험 후보다. |
| Agentic resource-consumption denial of safe operation | AML.T0034.002 Agentic Resource Consumption; AML.T0034 Cost Harvesting; AML.T0029 Denial of AI Service | 반복 도구 호출·장기 에이전트 루프가 연산, 비용, API quota를 고갈시켜 안전 감시·제어를 약화시키는 위험이다. | 온디바이스 연산·메모리 고갈, 클라우드 의존 실패로 대부분 커버되므로 신규 L4보다는 기존 카드 보강 후보다. |
| Hallucinated dependency or entity in physical workflows | AML.T0060 Publish Hallucinated Entities; AML.T0111 AI Supply Chain Reputation Inflation; AML.T0109 AI Supply Chain Rug Pull | 존재하지 않는 패키지·도구·기관·절차를 hallucination으로 만들어 공급망이나 운용 절차에 끼워 넣는 위험이다. | 기반모델 환각/세계모델 환각과 겹치지만 “hallucinated entity → physical workflow/supply-chain”은 약하게만 드러난다. |

## 보수적 우선순위
1. 새 L4로 검토: Agent tool invocation to physical actuation; Agent configuration compromise; Persistent context or memory poisoning; Credential-mediated physical control escalation.
2. 기존 L4 보강 우선: Agentic resource-consumption denial of safe operation; Delayed / triggered instruction execution; Hallucinated dependency or entity in physical workflows.
3. 연구/운영 사례가 더 필요: Trusted output / UI rendering manipulation for operator action; Poisoned / malicious agent tool supply chain.