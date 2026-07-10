const JSON_HEADERS = { "content-type": "application/json; charset=utf-8" };

function cors(origin, allowedOrigin) {
  const accepted = origin === allowedOrigin || origin === "http://127.0.0.1:8765";
  return {
    "access-control-allow-origin": accepted ? origin : allowedOrigin,
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
}

function response(body, status, origin, env) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...JSON_HEADERS, ...cors(origin, env.ALLOWED_ORIGIN) },
  });
}

function validPayload(payload) {
  return payload
    && /^R-[a-f0-9]{12}$/.test(payload.respondent_id || "")
    && /^A(?:0[1-9]|1[0-9])$/.test(payload.assignment_block || "")
    && /^[a-f0-9-]{36}$/.test(payload.submission_id || "")
    && typeof payload.markdown === "string"
    && payload.markdown.length >= 500
    && payload.markdown.length <= 200_000
    && JSON.stringify(payload.client_metadata || {}).length <= 20_000;
}

function partition(dateValue) {
  const date = new Date(dateValue || Date.now());
  if (Number.isNaN(date.getTime())) throw new Error("Invalid timestamp");
  return {
    year: String(date.getUTCFullYear()),
    month: String(date.getUTCMonth() + 1).padStart(2, "0"),
  };
}

async function putGitHubFile(repo, path, content, message, env) {
  const endpoint = `https://api.github.com/repos/${env.GH_OWNER}/${repo}/contents/${path}`;
  const githubResponse = await fetch(endpoint, {
    method: "PUT",
    headers: {
      authorization: `Bearer ${env.GH_TOKEN}`,
      accept: "application/vnd.github+json",
      "content-type": "application/json",
      "user-agent": "pai-risk-survey-worker",
      "x-github-api-version": "2022-11-28",
    },
    body: JSON.stringify({
      message,
      content: btoa(unescape(encodeURIComponent(content))),
    }),
  });
  if (githubResponse.status === 422) return { duplicate: true };
  if (!githubResponse.ok) {
    const detail = await githubResponse.text();
    throw new Error(`GitHub ${githubResponse.status}: ${detail.slice(0, 300)}`);
  }
  return { duplicate: false, result: await githubResponse.json() };
}

function yamlValue(value) {
  return JSON.stringify(value ?? null);
}

function buildTelemetry(payload, request, receivedAt) {
  const cf = request.cf || {};
  const startedAt = new Date(payload.started_at || receivedAt);
  const completedAt = new Date(payload.submitted_at || receivedAt);
  const durationSeconds = Number.isFinite(payload.duration_seconds)
    ? Math.max(0, Math.round(payload.duration_seconds))
    : Math.max(0, Math.round((completedAt - startedAt) / 1000));
  const telemetry = {
    respondent_id: payload.respondent_id,
    submission_id: payload.submission_id,
    assignment_block: payload.assignment_block,
    started_at_client: payload.started_at || null,
    completed_at_client: payload.submitted_at || null,
    received_at_server: receivedAt,
    duration_seconds: durationSeconds,
    ip_address: request.headers.get("cf-connecting-ip"),
    country: cf.country || null,
    continent: cf.continent || null,
    region: cf.region || null,
    region_code: cf.regionCode || null,
    city: cf.city || null,
    postal_code: cf.postalCode || null,
    latitude: cf.latitude || null,
    longitude: cf.longitude || null,
    timezone: cf.timezone || null,
    asn: cf.asn || null,
    as_organization: cf.asOrganization || null,
    cloudflare_colo: cf.colo || null,
    http_protocol: cf.httpProtocol || null,
    tls_version: cf.tlsVersion || null,
    tls_cipher: cf.tlsCipher || null,
    client_tcp_rtt: cf.clientTcpRtt || null,
    user_agent: request.headers.get("user-agent"),
    accept_language: request.headers.get("accept-language"),
    accept_encoding: request.headers.get("accept-encoding"),
    referer: request.headers.get("referer"),
    origin: request.headers.get("origin"),
    cf_ray: request.headers.get("cf-ray"),
    client_metadata: payload.client_metadata || {},
  };
  const lines = ["---"];
  for (const [key, value] of Object.entries(telemetry)) {
    lines.push(`${key}: ${yamlValue(value)}`);
  }
  lines.push("---", "", "# Private Survey Connection Telemetry", "");
  lines.push("This file contains access-restricted connection metadata separated from the public survey response.", "");
  return lines.join("\n");
}

async function saveTelemetry(payload, request, receivedAt, env) {
  const { year, month } = partition(receivedAt);
  const filename = `${payload.respondent_id}_${payload.submission_id}.md`;
  const path = `telemetry/${year}/${month}/${filename}`;
  const content = buildTelemetry(payload, request, receivedAt);
  const stored = await putGitHubFile(
    env.GH_TELEMETRY_REPO,
    path,
    content,
    `Add private survey telemetry ${payload.respondent_id}`,
    env,
  );
  return { path, duplicate: stored.duplicate };
}

async function savePublicResponse(payload, env) {
  const { year, month } = partition(payload.submitted_at);
  const filename = `${payload.respondent_id}_${payload.submission_id}.md`;
  const path = `responses/${year}/${month}/${filename}`;
  const stored = await putGitHubFile(
    env.GH_REPO,
    path,
    payload.markdown,
    `Add anonymous survey response ${payload.respondent_id}`,
    env,
  );
  return {
    path,
    url: `https://github.com/${env.GH_OWNER}/${env.GH_REPO}/blob/main/${path}`,
    duplicate: stored.duplicate,
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("origin") || "";
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(origin, env.ALLOWED_ORIGIN) });
    }
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return response({
        status: "ok",
        public_repository: `${env.GH_OWNER}/${env.GH_REPO}`,
        private_telemetry_repository: `${env.GH_OWNER}/${env.GH_TELEMETRY_REPO}`,
      }, 200, origin, env);
    }
    if (request.method !== "POST" || url.pathname !== "/submit") {
      return response({ error: "Not found" }, 404, origin, env);
    }
    if (origin !== env.ALLOWED_ORIGIN && origin !== "http://127.0.0.1:8765") {
      return response({ error: "Origin not allowed" }, 403, origin, env);
    }
    let payload;
    try {
      payload = await request.json();
    } catch {
      return response({ error: "Invalid JSON" }, 400, origin, env);
    }
    if (!validPayload(payload)) return response({ error: "Invalid submission" }, 400, origin, env);
    try {
      const receivedAt = new Date().toISOString();
      const telemetry = await saveTelemetry(payload, request, receivedAt, env);
      const publicResponse = await savePublicResponse(payload, env);
      return response({
        stored: true,
        ...publicResponse,
        telemetry_stored: true,
        telemetry_duplicate: telemetry.duplicate,
      }, 201, origin, env);
    } catch (error) {
      console.error(error);
      return response({ error: "Storage failed" }, 502, origin, env);
    }
  },
};
