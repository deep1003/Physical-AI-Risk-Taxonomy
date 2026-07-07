# Handover — GitHub Pages deployment failure

**Repo:** `github.com/deep1003/Physical-AI-Risk-Taxonomy` (branch `main`)
**Symptom:** Pages workflow `build` job = green, `report-build-status` = green, **`deploy` job = red**, fails in ~6–10 s.
**Exact error (deploy job, `actions/deploy-pages@v5`):**

```
Fetching artifact metadata for "github-pages" in this workflow run
Found 1 artifact(s)
Creating Pages deployment with payload: { artifact_id: 8087711450, pages_build_version: "363b239...", oidc_token: "***" }
Created deployment for 363b239f701453a8a6c59a81a2e6cbdf79a9eae3
Getting Pages deployment status...
Error: Deployment failed, try again later.
```

The failure is at the **"Getting Pages deployment status"** poll — i.e. the artifact uploaded fine and the deployment was *created*; the GitHub Pages backend then returned a failure/timeout while finalizing. This is a **deploy-side (GitHub Pages API) failure, not a build/content failure.**

---

## What was changed (recent work, this session)

All changes are to the Technical Report and static site; **no workflow or Pages-config files were added or edited.** Recent commits on `main` (newest first):

- `2d9dc27` empty commit to re-trigger Pages deploy (already attempted once)
- `363b239` Background narrative rework (Asimov → RLHF → 3H1R), +5 verified citations
- `6788e8f` Background + Contributions + Limitations sections; move Workflow figure; remove Figure 3; fix Figure 4 (inset)
- `d23b864` Nature-style figures; remove per-page draft footer
- `ea70a2a` mark report DRAFT; page numbers to bottom-center
- `824dadc` major report reorder + Sensitivity Analysis + equation sourcing/numbering
- (earlier) trade-off matrix, reproducibility artifacts, DRAFT badge on `index.html`

Files touched that the site serves: `index.html`, `technical_report.html`, `technical_report.pdf`, `output/latex/figures/*`. **`index.html` and `technical_report.html` are valid and unchanged in structure** (only a DRAFT badge span and a button were edited).

## Objective repo/site facts (rule out common causes)

- **`.github/workflows/` does not exist** in the repo → deployment is the **GitHub-managed "pages-build-deployment" pipeline** (Pages **source = Deploy from a branch**, `main` / root). `.nojekyll` (0 bytes) is present, so Jekyll processing is off (static serving).
- **Total tracked size = 20 MB**, **113 files**, **largest file = 2.6 MB** (`output/latex/figures/risk_space_korea_hires.png`); `technical_report.pdf` = 1.8 MB. **Nothing near the GitHub Pages limits** (site ≤ 1 GB; file ≤ 100 MB; ≤ ~10 min build). → **Size / file-count is NOT the cause.**
- No `CNAME`, no custom domain, no `_config.yml`. No large/binary data files are tracked (raw corpora and caches are `.gitignore`d).
- `git push` itself succeeds every time; the repo state is clean and the branch is not diverged.

## Suspected causes (ranked, objective)

1. **Transient GitHub Pages infrastructure incident** — this exact string (`Deployment failed, try again later`) is GitHub's generic Pages-backend failure and is most often a temporary service issue. **Check <https://www.githubstatus.com> (GitHub Pages component).**
2. **Stuck / superseded concurrent deployment on the `github-pages` environment.** Several commits were pushed in quick succession; GitHub serializes Pages deployments per environment, and an overlapping/stuck previous deployment can make new ones fail. **Check Settings → Environments → `github-pages` for an in-progress/stuck deployment; cancel older running/queued Actions runs, then re-run only the latest.**
3. **Environment protection rules on `github-pages`** (required reviewers / wait timer / branch restriction) blocking the deploy. **Check Settings → Environments → `github-pages` → Deployment protection rules.**
4. **Pages source misconfiguration / needs a toggle.** Even though `build` succeeds, the Pages backend occasionally needs Settings → Pages source toggled (Deploy from a branch ↔ GitHub Actions) to reset. Confirm source = **Deploy from a branch: `main` / `/ (root)`**.
5. **Account/repo temporary rate or abuse flag on Pages** (least likely given small repo and normal push cadence).

Not suspected: build errors, oversized artifact, broken HTML, missing `index.html`, custom-workflow bugs (there is no custom workflow).

## Suggested checks for the next agent (Codex)

1. Open <https://www.githubstatus.com>; if Pages is degraded, just wait and re-run.
2. Repo → **Actions** tab → cancel any queued/older "pages build and deployment" runs → open the latest failed run → **Re-run failed jobs** (single, not repeated).
3. Repo → **Settings → Pages**: confirm source (`Deploy from a branch: main /root`); if in doubt, switch to **GitHub Actions** source (which uses `actions/deploy-pages` explicitly and often clears the stuck state), or toggle branch off/on.
4. Repo → **Settings → Environments → `github-pages`**: remove any protection rule; check for a stuck active deployment and delete/cancel it.
5. If still failing after status is green: push one fresh commit (avoid rapid multiple pushes so deployments don't overlap), and watch a single deploy run to completion.
6. Optional hardening: add an explicit `.github/workflows/pages.yml` using `actions/configure-pages`, `actions/upload-pages-artifact` (path `.`), and `actions/deploy-pages@v4/v5` with `concurrency: group: pages, cancel-in-progress: true` — this makes deployment deterministic and prevents overlap.

## Verification target

The site should serve `index.html` (the taxonomy browser) with a working **"Technical Report [DRAFT]"** button → `technical_report.html` → embedded `technical_report.pdf`. All three files are present and valid at `HEAD` (`2d9dc27`).
