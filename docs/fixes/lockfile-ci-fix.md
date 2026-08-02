# Frontend Lockfile Fix for CI (`npm ci`)

| Field | Value |
|---|---|
| Date | 2026-08-03 |
| Author | Adrian (Software Engineer) |
| Related PR | [#11 — Fix frontend lockfile for CI (npm ci)](https://github.com/kwantum-institute/kwantum-institute.github.io/pull/11) |
| Related Issue | (created by this documentation pass) |
| Branch | `fix/lockfile-ci` (merged into `master` at `ce5179f`) |
| Severity | **Blocker** — CI failed before build step |
| Status | Resolved |

---

## 1. Summary

The GitHub Actions **Deploy** workflow failed at the `Install dependencies` step
immediately after merging [PR #10](https://github.com/kwantum-institute/kwantum-institute.github.io/pull/10)
(the KAG GraphRAG editor feature). The failure was caused by `npm ci` detecting that
`frontend/package-lock.json` was out of sync with `frontend/package.json`, because
the `mermaid` dependency added in PR #10 was never accompanied by a regenerated
lockfile.

This document records the root cause, the minimal repair, the verification steps,
and the follow-up recommendations. It is published via GitHub's native tracking
features (an Issue + a Pull Request) and committed to the repository as both
Markdown and a self-contained HTML rendering.

## 2. Symptoms

The failing job: [Deploy run #30752010653, job 91507589957](https://github.com/kwantum-institute/kwantum-institute.github.io/actions/runs/30752010653/job/91507589957).

The `Install dependencies` step emitted repeated lines of the form:

```
npm error Missing: d3-transition@3.0.1 from lock file
npm error Missing: d3-zoom@3.0.1 from lock file
npm error Missing: internmap@2.0.3 from lock file
...
npm error Usage: npm ci
```

followed by `Process completed with exit code 1`. The build step never started,
which confirms the failure was dependency-metadata state, not application source.

A secondary warning was also emitted by the runner:

> Node.js 20 is deprecated. The following actions target Node.js 20 but are being
> forced to run on Node.js 24: `actions/checkout@v4`, `actions/setup-node@v4`.

## 3. Root Cause

`npm ci` performs a **clean, strict** install directly from `package-lock.json`.
Unlike `npm install`, it will **not** rewrite the lockfile when `package.json`
and the lockfile disagree — it errors out instead. This is by design: `npm ci` is
meant for reproducible CI builds.

PR #10 added `mermaid` to `frontend/package.json` (required by the new
`MermaidPreview.jsx` component for rendering graph diagrams), but the
corresponding `frontend/package-lock.json` was committed unchanged. As a result,
`npm ci` could not resolve `mermaid`'s transitive dependency tree
(`d3-transition`, `d3-zoom`, `internmap`, `d3-array`, `d3-delaunay`, …) and aborted
before the Vite build could run.

## 4. Workflow Context

Relevant excerpt from `.github/workflows/deploy.yml`:

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm
    cache-dependency-path: frontend/package-lock.json

- name: Install dependencies
  run: npm ci
  working-directory: frontend

- name: Build project
  run: npm run build
  working-directory: frontend
```

Key points:
- `npm ci` is used (strict mode) — correct for CI.
- `node-version: 20` is pinned — the lockfile must be generated with a compatible
  Node major to avoid format drift.
- `cache-dependency-path: frontend/package-lock.json` — the cache key depends on
  the lockfile, so a stale lockfile also degrades cache hits.

## 5. Fix

The minimal repair is to regenerate `frontend/package-lock.json` and commit it.
No source code was changed.

Steps performed locally:

```powershell
# Use Node 20.x to match the workflow's pinned node-version.
$env:PATH = "$env:USERPROFILE\node-port\node-v20.18.1-win-x64;$env:PATH"
Set-Location frontend
npm install --no-audit --no-fund   # rewrites package-lock.json
npm run build                       # verify the build still succeeds
```

Resulting commit (merged via PR #11):

```
7d8b3bf Fix frontend lockfile for CI
 frontend/package-lock.json | +2583 / -1276
```

## 6. Verification

1. **Lockfile integrity** — `frontend/package-lock.json` now contains the
   previously missing packages:
   - `node_modules/mermaid`
   - `node_modules/d3-transition`
   - `node_modules/d3-zoom`
   - `node_modules/internmap`
   - `lockfileVersion: 3`

2. **Local build** — `npm run build` completed successfully in 15.92s, producing
   `dist/` with all assets. Only non-fatal warnings were emitted (chunk-size > 500 kB
   advisories for `flowchart-elk-definition`, `mindmap-definition`, and `index`).

3. **CI** — after PR #11 merged, the Deploy workflow advanced past the
   `Install dependencies` step.

## 7. Files Changed

| File | Change | Purpose |
|---|---|---|
| `frontend/package-lock.json` | +2583 / −1276 | Regenerated to include `mermaid` and its transitive deps |

No other files were modified. This is purely dependency metadata.

## 8. Follow-up Recommendations

These are **not** part of the minimal fix but are recommended to prevent recurrence:

1. **Regenerate the lockfile whenever `package.json` changes.** Add a CI guard:
   ```yaml
   - name: Verify lockfile is up to date
     run: |
       npm install --package-lock-only --no-audit --no-fund
       git diff --exit-code -- frontend/package-lock.json
     working-directory: frontend
   ```
   This fails the job if the committed lockfile drifts from `package.json`.

2. **Bump the Node version.** `node-version: 20` is deprecated on GitHub Actions
   runners. Move to `22` (or `24`) and update `actions/checkout@v4` and
   `actions/setup-node@v4` to their latest majors to clear the deprecation warning.
   Regenerate the lockfile with the same Node version you pin.

3. **Code-split the mermaid bundle.** The build emits chunk-size warnings because
   `mermaid` pulls in large diagram-specific chunks. Consider dynamic
   `import()` for diagram types you don't use, or
   `build.rollupOptions.output.manualChunks` to split them. This is a perf
   improvement only; it does not affect correctness.

4. **Adopt Renovate / Dependabot** to keep `frontend/package-lock.json` and
   `backend/requirements.txt` in sync automatically, so manual edits to
   `package.json` are less likely to land without a lockfile update.

## 9. Reproduction

To reproduce the original failure locally:

```powershell
git checkout 63fb970   # master before PR #11 merged
Set-Location frontend
npm ci                 # fails: Missing: d3-transition ... from lock file
```

To confirm the fix:

```powershell
git checkout ce5179f   # master after PR #11 merged
Set-Location frontend
npm ci                 # succeeds
npm run build           # succeeds
```

## 10. Glossary

- **`npm ci`** — Clean-install command. Installs exactly what `package-lock.json`
  records; errors instead of mutating the lockfile if it disagrees with
  `package.json`.
- **`package-lock.json`** — Deterministic record of every installed package and
  its transitive dependencies, including integrity hashes.
- **`lockfileVersion`** — Schema version of the lockfile. Version 3 is current for
  npm 7+.
- **Transitive dependency** — A dependency required by one of your direct
  dependencies, not listed explicitly in `package.json`.
- **Top-P / Nucleus Sampling** — (Context from the broader feature work, not this
  fix.) LLM sampling parameter controlling the cumulative-probability token pool.
