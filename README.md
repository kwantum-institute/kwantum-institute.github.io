# Kwantum Institute

Django + React site for the Kwantum Institute, with token auth, science search, and a local-first KAG GraphRAG editor.

## Features

### Backend (Django)
- **Authentication** — login, registration, logout, profile, password reset
- **Token auth** — DRF token-based API access
- **Science search** — optional Gemma rewrite via Gemini API
- **GraphRAG / KAG** — editable knowledge graph, batch CSV import, Mermaid export, dual-pass Qwen research, asymmetric retrieval, privacy hook chain
- **Env-driven security** — `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and CORS/CSRF origins are read from the environment (not hard-coded for production)

### Frontend (React + Vite)
- Auth forms, profile management, protected flows
- GraphRAG editor at `/graphrag` (nodes, edges, batch import, Mermaid preview, research)
- Architecture dashboard at `/architecture`
- Mermaid errors render via `textContent` (no `innerHTML` XSS sink)

## Project structure

```
.
├── api/                         # Vercel Python WSGI adapter
├── backend/
│   ├── authentication/          # Auth app
│   ├── science_search/          # Science search app
│   ├── graphrag/                # KAG GraphRAG app + services
│   ├── backend/settings.py      # Env-aware Django settings
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/components/
│   │   ├── GraphRagEditor/      # Editor UI + API client
│   │   └── ArchitectureDashboard/
│   ├── package.json
│   └── .env.example
├── docs/fixes/                  # Incident / fix write-ups (md + html)
├── brain.md                     # Approved facts / glossary for GraphRAG
├── soul.md                      # Tone / policy for generated content
├── vercel.json
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 20+ (matches CI `node-version: 20`)
- npm

## Backend setup

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit values
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

API base: `http://localhost:8000`

### Backend environment variables

| Variable | Purpose | Notes |
|---|---|---|
| `DEBUG` | Debug mode | Default `true` locally; set `false` in production |
| `SECRET_KEY` | Django secret | **Required when `DEBUG=false`** |
| `ALLOWED_HOSTS` | Host allowlist | Comma-separated; default localhost list when unset |
| `CORS_ALLOWED_ORIGINS` | Browser origins | Defaults to local Vite ports when `DEBUG=true`; empty in production unless set |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins | Comma-separated HTTPS origins for production |
| `GEMINI_API_KEY` | Science search rewrite | Optional |
| `QWEN_*` / `BGE_*` | Local LLM + embeddings | Local-first; leave remote search keys blank for offline |

See `backend/.env.example`.

## Frontend setup

```bash
cd frontend
cp .env.example .env   # set VITE_GRAPHRAG_API_URL if needed
npm ci                 # or npm install
npm run dev
```

Dev server: Vite default (`http://localhost:5173`). Build with `npm run build`.

GraphRAG calls send `Authorization: Token <token>` when a login token is present in `localStorage`.

## API endpoints

### Auth (`/api/auth/`)
- `POST /login/`, `POST /logout/`, `POST /register/`
- `GET /check-auth/`, `GET /user-info/`
- `GET|PATCH /profile/`
- `POST /password/change/`, `POST /password/reset/`, `POST /password/reset/confirm/`

### GraphRAG (`/api/graphrag/`)
Uses DRF `APIView` defaults (`IsAuthenticated`). Mutating routes are no longer CSRF-exempt.

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/nodes/` | List / create nodes |
| GET/PATCH/DELETE | `/nodes/<id>/` | Node detail |
| GET/POST | `/edges/` | List / create edges |
| GET/DELETE | `/edges/<id>/` | Edge detail |
| GET | `/search/?q=` | Semantic chunk search (BGE) |
| POST | `/batch/` | CSV/JSON batch import (`dry_run` supported) |
| GET | `/mermaid/` | Mermaid + Markdown export |
| GET/POST | `/provenance/` | Provenance list / create |
| POST | `/research/` | KAG research cycle |
| GET | `/architecture/` | Architecture Mermaid + principles |
| POST | `/tune/` | Manual fine-tuning pass |

## GraphRAG usage

1. Sign in at `/login` so the editor can authenticate API calls.
2. Open `/graphrag` to edit nodes/edges, run batch import, preview Mermaid, or run research.
3. Open `/architecture` for the hook-chain diagram and tuning controls.
4. Edit `brain.md` / `soul.md` at the repo root for approved context and tone (read by the research path).

Local-first stack: `BAAI/bge-small-en-v1.5` embeddings + `Qwen3-4B-Instruct-2507` orchestration. Remote Brave / Perplexity / Consensus clients stay inactive unless API keys are set.

## Security notes

- **Production settings** — set `DEBUG=false`, a strong `SECRET_KEY`, and explicit `ALLOWED_HOSTS`. Django raises if `SECRET_KEY` is missing when debug is off.
- **CORS** — prefer same-origin in production; set `CORS_ALLOWED_ORIGINS` only for known frontend origins. Do not rely on edge `Access-Control-Allow-Origin: *` for mutating APIs.
- **GraphRAG auth** — GraphRAG views use DRF auth/permissions; frontend attaches the stored auth token.
- **Mermaid preview** — parse/render errors use `textContent`, not `innerHTML`, so diagram text echoed in errors cannot inject HTML.

## CI / deploy

- GitHub Actions Deploy workflow (`.github/workflows/deploy.yml`) runs `npm ci` then `npm run build` in `frontend/` on pushes to `master`.
- Keep `frontend/package-lock.json` in sync whenever `package.json` changes (`npm ci` will fail on drift).
- Vercel: `vercel.json` builds the Vite frontend and rewrites `/api/*` to `api/index.py`.

Lockfile incident write-up: [`docs/fixes/lockfile-ci-fix.md`](docs/fixes/lockfile-ci-fix.md) (HTML: [`docs/fixes/lockfile-ci-fix.html`](docs/fixes/lockfile-ci-fix.html)).

## Tests

```bash
cd backend
pytest
```

## Troubleshooting

| Symptom | Check |
|---|---|
| CORS errors | `CORS_ALLOWED_ORIGINS` includes your frontend origin |
| `ImproperlyConfigured: SECRET_KEY` | Set `SECRET_KEY` when `DEBUG=false` |
| GraphRAG 401/403 | Log in; confirm `Authorization: Token …` is sent |
| `npm ci` missing packages | Regenerate and commit `frontend/package-lock.json` |
| Heavy ML imports fail on Vercel | Full torch/transformers stack is for a dedicated host; serverless uses the lighter `api/requirements.txt` path |

## Contributing

1. Fork and branch from `master`
2. Keep lockfiles / migrations updated with dependency or model changes
3. Add tests for new GraphRAG or auth behavior
4. Open a PR

## License

Part of the Kwantum Institute website. Refer to the project license for usage terms.
