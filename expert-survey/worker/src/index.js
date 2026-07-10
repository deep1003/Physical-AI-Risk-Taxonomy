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
    && /^A0[1-9]$/.test(payload.assignment_block || "")
    && /^[a-f0-9-]{36}$/.test(payload.submission_id || "")
    && typeof payload.markdown === "string"
    && payload.markdown.length >= 500
    && payload.markdown.length <= 200_000;
}

async function saveToGitHub(payload, env) {
  const date = new Date(payload.submitted_at || Date.now());
  if (Number.isNaN(date.getTime())) throw new Error("Invalid submitted_at");
  const year = String(date.getUTCFullYear());
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const filename = `${payload.respondent_id}_${payload.submission_id}.md`;
  const path = `responses/${year}/${month}/${filename}`;
  const endpoint = `https://api.github.com/repos/${env.GH_OWNER}/${env.GH_REPO}/contents/${path}`;
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
      message: `Add anonymous survey response ${payload.respondent_id}`,
      content: btoa(unescape(encodeURIComponent(payload.markdown))),
    }),
  });
  if (githubResponse.status === 422) {
    return { path, url: `https://github.com/${env.GH_OWNER}/${env.GH_REPO}/blob/main/${path}`, duplicate: true };
  }
  if (!githubResponse.ok) {
    const detail = await githubResponse.text();
    throw new Error(`GitHub ${githubResponse.status}: ${detail.slice(0, 300)}`);
  }
  const result = await githubResponse.json();
  return { path, url: result.content.html_url, duplicate: false };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("origin") || "";
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin, env.ALLOWED_ORIGIN) });
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return response({ status: "ok", repository: `${env.GH_OWNER}/${env.GH_REPO}` }, 200, origin, env);
    }
    if (request.method !== "POST" || url.pathname !== "/submit") return response({ error: "Not found" }, 404, origin, env);
    if (origin !== env.ALLOWED_ORIGIN && origin !== "http://127.0.0.1:8765") return response({ error: "Origin not allowed" }, 403, origin, env);
    let payload;
    try { payload = await request.json(); } catch { return response({ error: "Invalid JSON" }, 400, origin, env); }
    if (!validPayload(payload)) return response({ error: "Invalid submission" }, 400, origin, env);
    try {
      const stored = await saveToGitHub(payload, env);
      return response({ stored: true, ...stored }, 201, origin, env);
    } catch (error) {
      console.error(error);
      return response({ error: "Storage failed" }, 502, origin, env);
    }
  },
};
