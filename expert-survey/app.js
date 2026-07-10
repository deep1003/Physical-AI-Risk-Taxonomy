"use strict";

const CONFIG = {
  repo: "deep1003/Physical-AI-Risk-Taxonomy",
  apiUrl: "https://pai-risk-survey-api.deep1003-pai.workers.dev",
  storagePrefix: "pai-expert-survey-v1",
};

const app = document.querySelector("#app");
let surveyData;
let assignments;
let state = {
  page: "consent",
  raterCode: "",
  assignmentBlock: "",
  consent: false,
  demographics: {},
  responses: {},
  exit: {},
  cardIndex: 0,
  startedAt: Date.now(),
};

const esc = (value = "") =>
  String(value).replace(
    /[&<>'"]/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[
        char
      ],
  );
const selected = (a, b) => (a === b ? "selected" : "");
const checked = (value) => (value ? "checked" : "");
function groupBy(items, keyFn) {
  return items.reduce((groups, item) => {
    const key = keyFn(item);
    (groups[key] ||= []).push(item);
    return groups;
  }, {});
}

function storageKey() {
  return `${CONFIG.storagePrefix}:${state.raterCode || "unassigned"}`;
}
function save() {
  localStorage.setItem(storageKey(), JSON.stringify(state));
  if (state.raterCode)
    localStorage.setItem(`${CONFIG.storagePrefix}:active`, state.raterCode);
}
function restoreActive() {
  const code = localStorage.getItem(`${CONFIG.storagePrefix}:active`);
  const raw = code && localStorage.getItem(`${CONFIG.storagePrefix}:${code}`);
  if (raw) state = { ...state, ...JSON.parse(raw) };
}
function randomRespondentId() {
  const bytes = crypto.getRandomValues(new Uint8Array(6));
  return `R-${[...bytes].map((value) => value.toString(16).padStart(2, "0")).join("")}`;
}
function randomBlock() {
  const byte = new Uint8Array(1);
  do crypto.getRandomValues(byte);
  while (byte[0] >= 252);
  return `A0${(byte[0] % 9) + 1}`;
}
function seededShuffle(values, seedText) {
  let seed = 2166136261;
  for (const char of seedText) seed = Math.imul(seed ^ char.charCodeAt(0), 16777619);
  const random = () => {
    seed += 0x6d2b79f5;
    let value = seed;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
  const shuffled = [...values];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const target = Math.floor(random() * (index + 1));
    [shuffled[index], shuffled[target]] = [shuffled[target], shuffled[index]];
  }
  return shuffled;
}
function assignedCards() {
  const ids = seededShuffle(
    assignments.raters[state.assignmentBlock] || [],
    state.raterCode,
  );
  const lookup = new Map(surveyData.cards.map((card) => [card.card_id, card]));
  return ids.map((id) => lookup.get(id)).filter(Boolean);
}
function familyOptions(value = "", includeSpecial = true) {
  const groups = groupBy(surveyData.families, (family) => family.l2_id);
  let html = '<option value="">선택 / Select</option>';
  for (const families of Object.values(groups)) {
    const first = families[0];
    html += `<optgroup label="${esc(first.l2_name_ko)} / ${esc(first.l2_name_en)}">`;
    html += families
      .map(
        (f) =>
          `<option value="${f.id}" ${selected(value, f.id)}>${f.id} · ${esc(f.name_ko)} / ${esc(f.name_en)}</option>`,
      )
      .join("");
    html += "</optgroup>";
  }
  if (includeSpecial) {
    html += `<option value="UNMAPPABLE" ${selected(value, "UNMAPPABLE")}>현재 분류체계로 분류 불가 / Unmappable</option>`;
    html += `<option value="INSUFFICIENT" ${selected(value, "INSUFFICIENT")}>정보 부족 / Insufficient information</option>`;
  }
  return html;
}

function renderConsent() {
  app.innerHTML = `<section class="panel">
    <h2>연구 안내 및 동의 <span class="english">Study information and consent</span></h2>
    <div class="notice"><p>이 연구는 182개 Physical AI 위험 카드를 24개 위험군으로 분류할 때 독립 전문가 판단의 재현성을 평가합니다.</p><p class="english">This study evaluates the reproducibility of independent expert assignments of 182 Physical AI risk cards to 24 predefined families.</p></div>
    <p>이 설문은 다음 정보를 절대 수집하거나 요구하지 않습니다: 이름, 이메일, 성별, 연령, 소속기관 등 개인정보. 설문은 약 60개 카드로 구성되며 브라우저에 자동 임시저장됩니다.</p>
    <p class="english">This survey never collects or requests personal information such as names, email addresses, gender, age, or institutional affiliation. Approximately 60 cards are assigned and progress is temporarily autosaved in this browser.</p>
    <div class="notice warning"><p><strong>제출된 익명 응답은 연구 재현성을 위해 공개 저장소에 보존됩니다.</strong></p><p class="english"><strong>Anonymous responses will be retained in a public repository for research reproducibility.</strong></p></div>
    <label class="choice"><input id="consent" type="checkbox">위 내용을 이해했으며 자발적으로 참여하는 데 동의합니다. <span class="english">I understand the information above and voluntarily consent to participate.</span></label>
    <p id="consentError" class="error" role="alert"></p>
    <div class="actions"><span></span><button id="begin" class="primary">설문 시작 / Begin survey</button></div>
  </section>`;
  document.querySelector("#begin").onclick = () => {
    if (!document.querySelector("#consent").checked) {
      document.querySelector("#consentError").textContent =
        "참여 동의가 필요합니다. / Consent is required.";
      return;
    }
    state.raterCode = randomRespondentId();
    state.assignmentBlock = randomBlock();
    state.consent = true;
    state.page = "demographics";
    save();
    render();
  };
}

function renderDemographics() {
  const d = state.demographics;
  app.innerHTML = `<section class="panel">
    <h2>전문가 배경 정보 <span class="english">Expert background</span></h2>
    <p class="help">이 설문은 이름, 이메일, 성별, 연령, 소속기관 등 개인정보를 절대 수집하거나 요구하지 않습니다. 별표 문항은 필수입니다. / This survey never collects or requests personal information such as names, email addresses, gender, age, or institutional affiliation. Asterisked items are required.</p>
    <div class="grid">
      ${selectField("career", "관련 경력 구간*", "Relevant experience*", ["1년 미만 / Under 1 year", "1–2년 / 1–2 years", "3–5년 / 3–5 years", "6–10년 / 6–10 years", "11–15년 / 11–15 years", "16년 이상 / 16+ years"], d.career)}
      ${selectField("sector", "현재 소속 부문*", "Current sector*", ["학계·연구 / Academia or research", "산업 / Industry", "공공·규제 / Government or regulatory", "표준화 / Standards organization", "기타 / Other"], d.sector)}
      ${selectField("region", "주요 활동 지역권*", "Primary region*", ["대한민국 / Republic of Korea", "아시아(한국 제외) / Asia excluding Korea", "유럽 / Europe", "북미 / North America", "기타 / Other", "응답하지 않음 / Prefer not to say"], d.region)}
      ${selectField("education", "최종 학위*", "Highest qualification*", ["박사 / Doctorate", "박사과정 / Doctoral candidate", "석사 / Master's", "학사 / Bachelor's", "전문자격·기타 / Professional or other"], d.education)}
      ${selectField("riskExperience", "Physical AI·로봇 위험평가 경험*", "Risk-assessment experience*", ["없음 / None", "제한적 / Limited", "반복적 / Repeated", "주요 업무 / Core responsibility"], d.riskExperience)}
      ${selectField("standardsExperience", "안전 표준·규제 경험*", "Safety standards or regulation experience*", ["없음 / No", "있음 / Yes"], d.standardsExperience)}
    </div>
    <fieldset><legend>주요 전문영역* <span class="english">Primary fields of expertise*</span></legend>${["Robotics", "Autonomous systems", "Control engineering", "Human–robot interaction", "Safety engineering", "AI safety", "Risk governance", "Standards or regulation"].map((x) => `<label class="choice"><input type="checkbox" name="expertise" value="${x}" ${checked((d.expertise || []).includes(x))}>${x}</label>`).join("")}</fieldset>
    <fieldset><legend>적격성·독립성 확인* <span class="english">Eligibility and independence check*</span></legend>
      <label class="choice"><input type="checkbox" id="eligibilityConfirmed" ${checked(d.eligibilityConfirmed)}>관련 학위, 관련 학위과정 1년 이상, 관련 산업·공공·표준화 경력 1년 이상 또는 관련 위험평가 경험 중 하나 이상을 충족합니다. <span class="english">I meet at least one criterion: a relevant degree, at least one year in a relevant degree programme, at least one year of relevant professional experience, or relevant risk-assessment experience.</span></label>
      <label class="choice"><input type="checkbox" id="independent" ${checked(d.independent)}>나는 공동저자가 아니며 L3/L4 개발 또는 기존 label 배정에 참여하지 않았습니다. <span class="english">I am not a co-author and did not develop the taxonomy or assign the existing labels.</span></label>
      <label class="choice"><input type="checkbox" id="notExposed" ${checked(d.notExposed)}>나는 기존 카드별 L3 label을 제공받지 않았습니다. <span class="english">I have not been given the existing card-level L3 labels.</span></label>
    </fieldset><p id="demoError" class="error"></p>
    <div class="actions"><button class="secondary" data-back>이전 / Back</button><button id="demoNext" class="primary">Codebook 보기 / View codebook</button></div>
  </section>`;
  bindBack("consent");
  document.querySelector("#demoNext").onclick = () => {
    const required = [
      "career",
      "sector",
      "region",
      "education",
      "riskExperience",
      "standardsExperience",
    ];
    const next = Object.fromEntries(
      required.map((id) => [id, document.querySelector(`#${id}`).value]),
    );
    next.expertise = [
      ...document.querySelectorAll('[name="expertise"]:checked'),
    ].map((el) => el.value);
    next.eligibilityConfirmed = document.querySelector(
      "#eligibilityConfirmed",
    ).checked;
    next.independent = document.querySelector("#independent").checked;
    next.notExposed = document.querySelector("#notExposed").checked;
    if (
      required.some((id) => !next[id]) ||
      !next.expertise.length ||
      !next.eligibilityConfirmed ||
      !next.independent ||
      !next.notExposed
    ) {
      document.querySelector("#demoError").textContent =
        "모든 필수 항목과 적격성·독립성 확인이 필요합니다. / Complete all required fields and eligibility/independence checks.";
      return;
    }
    state.demographics = next;
    state.page = "codebook";
    save();
    render();
  };
}

function selectField(id, ko, en, options, value) {
  return `<div class="field"><label for="${id}">${ko}<span class="english">${en}</span></label><select id="${id}"><option value="">선택 / Select</option>${options.map((x) => `<option ${selected(value, x)}>${x}</option>`).join("")}</select></div>`;
}

function renderCodebook() {
  const groups = groupBy(surveyData.families, (f) => f.l2_id);
  app.innerHTML = `<section class="panel codebook"><h2>L3 위험군 Codebook <span class="english">L3 risk-family codebook</span></h2>
    <div class="notice"><p>위험의 결과보다 카드에 명시된 주요 발생 메커니즘을 우선하십시오. 카드에 없는 상황을 추론하지 마십시오.</p><p class="english">Prioritize the primary risk-generating mechanism stated in the card rather than consequence severity. Do not infer unstated circumstances.</p></div>
    ${Object.values(groups)
      .map(
        (fs) =>
          `<h3 class="l2-heading">${esc(fs[0].l2_name_ko)} / ${esc(fs[0].l2_name_en)}</h3>${fs.map((f) => `<details><summary>${f.id} · ${esc(f.name_ko)} / ${esc(f.name_en)}</summary><p>${esc(f.definition_ko)}</p><p class="english">${esc(f.definition_en)}</p></details>`).join("")}`,
      )
      .join("")}
    <label class="choice"><input id="readCodebook" type="checkbox">분류 규칙과 24개 위험군을 검토했습니다. <span class="english">I have reviewed the classification rules and all 24 families.</span></label>
    <p id="bookError" class="error"></p><div class="actions"><button class="secondary" data-back>이전 / Back</button><button id="startCards" class="primary">카드 분류 시작 / Start annotation</button></div></section>`;
  bindBack("demographics");
  document.querySelector("#startCards").onclick = () => {
    if (!document.querySelector("#readCodebook").checked) {
      document.querySelector("#bookError").textContent =
        "Codebook 검토 확인이 필요합니다. / Please confirm codebook review.";
      return;
    }
    state.page = "cards";
    save();
    render();
  };
}

function renderCard() {
  const cards = assignedCards();
  const index = Math.min(state.cardIndex, cards.length - 1);
  const card = cards[index];
  const response = state.responses[card.card_id] || {};
  const completed = Object.values(state.responses).filter(
    (r) => r.primary && r.confidence,
  ).length;
  app.innerHTML = `<div class="progress-wrap"><progress value="${completed}" max="${cards.length}"></progress><strong>${completed}/${cards.length}</strong></div>
  <section class="panel risk-card"><p class="card-id">${esc(card.display_id)} · ${index + 1}/${cards.length}</p>
    <p class="risk-title">${esc(card.label_ko)} <span class="english">${esc(card.label_en)}</span></p>
    <div class="risk-definition"><p>${esc(card.definition_ko)}</p><p class="english">${esc(card.definition_en)}</p></div>
    <div class="field"><label for="primary">가장 적절한 Primary L3* <span class="english">Most appropriate primary L3*</span></label><select id="primary">${familyOptions(response.primary)}</select></div>
    <div class="field"><label for="secondary">Secondary L3 (선택) <span class="english">Secondary L3 (optional)</span></label><select id="secondary">${familyOptions(response.secondary, false)}</select></div>
    <fieldset><legend>Primary 판단 확신도* <span class="english">Confidence in primary assignment*</span></legend>${[1, 2, 3, 4, 5].map((n) => `<label class="choice"><input type="radio" name="confidence" value="${n}" ${checked(String(response.confidence) === String(n))}>${n} · ${["매우 낮음 / Very low", "낮음 / Low", "보통 / Moderate", "높음 / High", "매우 높음 / Very high"][n - 1]}</label>`).join("")}</fieldset>
    <div class="field"><label for="ambiguity">모호성의 주된 원인 (해당 시) <span class="english">Primary source of ambiguity (if applicable)</span></label><select id="ambiguity"><option value="">해당 없음 / Not applicable</option>${["카드 정보 부족 / Insufficient card information", "복수 위험 메커니즘 / Multiple mechanisms", "정의 중첩 / Overlapping definitions", "경계 규칙 불명확 / Unclear boundary", "적합한 위험군 없음 / Missing family", "전문지식 한계 / Expertise limitation", "기타 / Other"].map((x) => `<option ${selected(response.ambiguity, x)}>${x}</option>`).join("")}</select></div>
    <div class="field"><label for="comment">선택적 의견 <span class="english">Optional comment</span></label><textarea id="comment">${esc(response.comment || "")}</textarea></div><p id="cardError" class="error"></p>
    <div class="actions"><button id="book" class="secondary">Codebook</button><div class="actions-right"><button id="previous" class="secondary" ${index === 0 ? "disabled" : ""}>이전 카드 / Previous</button><button id="next" class="primary">${index === cards.length - 1 ? "검토 / Review" : "다음 카드 / Next"}</button></div></div>
  </section>`;
  document.querySelector("#book").onclick = () => {
    persistCard(card);
    state.page = "codebook-return";
    save();
    renderCodebookReturn();
  };
  document.querySelector("#previous").onclick = () => {
    persistCard(card);
    state.cardIndex = Math.max(0, index - 1);
    save();
    render();
  };
  document.querySelector("#next").onclick = () => {
    if (!persistCard(card, true)) return;
    if (index === cards.length - 1) state.page = "review";
    else state.cardIndex = index + 1;
    save();
    render();
  };
}

function persistCard(card, validate = false) {
  const primary = document.querySelector("#primary").value;
  const secondary = document.querySelector("#secondary").value;
  const confidence =
    document.querySelector('[name="confidence"]:checked')?.value || "";
  if (
    validate &&
    (!primary || !confidence || (secondary && secondary === primary))
  ) {
    document.querySelector("#cardError").textContent =
      "Primary와 확신도는 필수이며 Secondary는 Primary와 달라야 합니다. / Primary and confidence are required; secondary must differ.";
    return false;
  }
  state.responses[card.card_id] = {
    primary,
    secondary,
    confidence,
    ambiguity: document.querySelector("#ambiguity").value,
    comment: document.querySelector("#comment").value.trim(),
    elapsed_seconds: Math.round((Date.now() - state.startedAt) / 1000),
  };
  return true;
}

function renderCodebookReturn() {
  renderCodebook();
  document.querySelector("#readCodebook").closest("label").remove();
  document.querySelector("#bookError").remove();
  document.querySelector("#startCards").textContent =
    "카드로 돌아가기 / Return to card";
  document.querySelector("#startCards").onclick = () => {
    state.page = "cards";
    save();
    render();
  };
  document.querySelector("[data-back]").remove();
}

function renderReview() {
  const cards = assignedCards();
  const missing = cards.filter(
    (c) =>
      !state.responses[c.card_id]?.primary ||
      !state.responses[c.card_id]?.confidence,
  );
  app.innerHTML = `<section class="panel"><h2>응답 검토 <span class="english">Review responses</span></h2>
    <p><span class="stat">완료 / Complete: ${cards.length - missing.length}</span><span class="stat">미완료 / Missing: ${missing.length}</span></p>
    ${missing.length ? `<p class="error">미완료 카드가 있습니다. / Some cards are incomplete.</p>` : `<p class="notice">모든 카드가 완료되었습니다. 종료 문항으로 이동할 수 있습니다. / All assigned cards are complete.</p>`}
    <div class="actions"><button id="returnCards" class="secondary">카드로 돌아가기 / Return</button><button id="exitNext" class="primary" ${missing.length ? "disabled" : ""}>종료 문항 / Exit questions</button></div></section>`;
  document.querySelector("#returnCards").onclick = () => {
    state.page = "cards";
    if (missing.length)
      state.cardIndex = cards.findIndex(
        (c) => c.card_id === missing[0].card_id,
      );
    save();
    render();
  };
  document.querySelector("#exitNext").onclick = () => {
    state.page = "exit";
    save();
    render();
  };
}

function renderExit() {
  const x = state.exit;
  app.innerHTML = `<section class="panel"><h2>종료 평가 <span class="english">Exit assessment</span></h2>
    ${selectField("clarity", "L3 정의의 전반적 명확성*", "Overall clarity of L3 definitions*", ["1 매우 불명확 / Very unclear", "2 불명확 / Unclear", "3 보통 / Moderate", "4 명확 / Clear", "5 매우 명확 / Very clear"], x.clarity)}
    <div class="field"><label for="confusing">가장 혼동된 위험군 쌍(최대 3쌍) <span class="english">Most confusing family pairs (up to three)</span></label><textarea id="confusing">${esc(x.confusing || "")}</textarea></div>
    <div class="field"><label for="missingRisk">누락된 주요 위험영역 <span class="english">Important missing risk areas</span></label><textarea id="missingRisk">${esc(x.missingRisk || "")}</textarea></div>
    <div class="field"><label for="suggestion">병합·분리·정의 개선 제안 <span class="english">Suggestions for merging, splitting, or redefining families</span></label><textarea id="suggestion">${esc(x.suggestion || "")}</textarea></div><p id="exitError" class="error"></p>
    <div class="actions"><button class="secondary" data-back>이전 / Back</button><button id="finish" class="primary">응답 완료 / Complete</button></div></section>`;
  bindBack("review");
  document.querySelector("#finish").onclick = () => {
    const clarity = document.querySelector("#clarity").value;
    if (!clarity) {
      document.querySelector("#exitError").textContent =
        "명확성 평가는 필수입니다. / Clarity rating is required.";
      return;
    }
    state.exit = {
      clarity,
      confusing: document.querySelector("#confusing").value.trim(),
      missingRisk: document.querySelector("#missingRisk").value.trim(),
      suggestion: document.querySelector("#suggestion").value.trim(),
    };
    state.page = "complete";
    state.completedAt = new Date().toISOString();
    state.submissionId ||= crypto.randomUUID();
    save();
    render();
  };
}

function markdown() {
  const rows = assignedCards()
    .map((card) => {
      const r = state.responses[card.card_id] || {};
      return `| ${card.display_id} | ${card.card_id} | ${r.primary || ""} | ${r.secondary || ""} | ${r.confidence || ""} | ${String(r.ambiguity || "").replaceAll("|", "/")} | ${String(
        r.comment || "",
      )
        .replaceAll("|", "/")
        .replaceAll("\n", " ")} |`;
    })
    .join("\n");
  const d = state.demographics,
    x = state.exit;
  return `---\nsurvey_version: "${surveyData.survey_version}"\nassignment_version: "${assignments.assignment_version}"\nrespondent_id: "${state.raterCode}"\nassignment_block: "${state.assignmentBlock}"\ncompleted_at: "${state.completedAt || new Date().toISOString()}"\nsource_sha256: "${surveyData.source_sha256}"\n---\n\n# Physical AI Expert Annotation Response\n\n## Background / 배경 정보\n\n- Expertise / 전문영역: ${(d.expertise || []).join(", ")}\n- Career / 경력: ${d.career}\n- Sector / 부문: ${d.sector}\n- Region / 지역권: ${d.region}\n- Education / 학위: ${d.education}\n- Risk-assessment experience / 위험평가 경험: ${d.riskExperience}\n- Standards experience / 표준 경험: ${d.stardsExperience || d.standardsExperience}\n- Independence confirmed / 독립성 확인: ${d.independent && d.notExposed}\n\n## Card annotations / 카드 분류\n\n| Display ID | Card ID | Primary L3 | Secondary L3 | Confidence | Ambiguity | Comment |\n|---|---|---|---|---:|---|---|\n${rows}\n\n## Exit assessment / 종료 평가\n\n- Clarity / 명확성: ${x.clarity || ""}\n- Confusing pairs / 혼동 위험군: ${x.confusing || ""}\n- Missing risks / 누락 위험: ${x.missingRisk || ""}\n- Suggestions / 개선 제안: ${x.suggestion || ""}\n`;
}

function renderComplete() {
  const stored = state.submission?.stored;
  app.innerHTML = `<section class="panel complete"><h2>${stored ? "응답 저장 완료" : "응답 저장 중"} <span class="english">${stored ? "Response stored" : "Saving response"}</span></h2>
    ${stored ? `<div class="notice"><p>익명 응답이 공개 GitHub 저장소에 Markdown으로 저장됐습니다.</p><p class="english">The anonymous response has been stored as Markdown in the public GitHub repository.</p><p><code>${esc(state.submission.path)}</code></p></div>` : `<p>창을 닫지 마십시오. / Please do not close this window.</p><p id="submitStatus" class="help">GitHub 저장소에 연결하고 있습니다. / Connecting to the GitHub repository…</p><button id="retry" class="secondary" hidden>다시 시도 / Retry</button>`}
    ${stored ? `<a class="button secondary" target="_blank" rel="noopener" href="${esc(state.submission.url)}">저장된 응답 보기 / View stored response</a>` : ""}</section>`;
  if (!stored) submitResponse();
}

async function submitResponse() {
  const status = document.querySelector("#submitStatus");
  const retry = document.querySelector("#retry");
  try {
    const response = await fetch(`${CONFIG.apiUrl}/submit`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        respondent_id: state.raterCode,
        assignment_block: state.assignmentBlock,
        submission_id: state.submissionId,
        submitted_at: state.completedAt,
        markdown: markdown(),
      }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.submission = await response.json();
    save();
    renderComplete();
  } catch (error) {
    status.textContent = `자동 저장에 실패했습니다. 브라우저에 안전하게 임시보존했습니다. / Automatic storage failed; the response remains in this browser. (${error.message})`;
    retry.hidden = false;
    retry.onclick = submitResponse;
  }
}

function bindBack(page) {
  document.querySelector("[data-back]").onclick = () => {
    state.page = page;
    save();
    render();
  };
}
function render() {
  (
    ({
      consent: renderConsent,
      demographics: renderDemographics,
      codebook: renderCodebook,
      cards: renderCard,
      review: renderReview,
      exit: renderExit,
      complete: renderComplete,
    })[state.page] || renderConsent
  )();
}

Promise.all([
  fetch("data/survey-data.json").then((r) => r.json()),
  fetch("data/assignments.json").then((r) => r.json()),
])
  .then(([data, allocation]) => {
    surveyData = data;
    assignments = allocation;
    restoreActive();
    render();
  })
  .catch((error) => {
    app.innerHTML = `<section class="panel"><p class="error">설문 데이터를 불러오지 못했습니다. / Failed to load survey data.</p><pre>${esc(error.message)}</pre></section>`;
  });
