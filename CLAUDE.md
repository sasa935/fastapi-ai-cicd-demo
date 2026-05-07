# CLAUDE.md — Project guide for AI agents

This file is the canonical project guide for any Claude agent working on this
repo (local Claude Code, mobile Dispatch, GitHub Action, etc.). Read it first.

## What this project is

A small URL shortener used as a learning demo for **AI-driven CI/CD**. The
point of the repo is not the shortener itself — it is the development workflow
around it: AI agents review code, generate tests, diagnose failing builds, and
help with deployment.

## Layout

```
fastapi-ai-cicd-demo/
├── backend/        FastAPI + SQLAlchemy URL shortener
│   ├── app/        application code
│   ├── tests/      pytest suite
│   └── pyproject.toml
├── frontend/       Vite + React 19 + TypeScript + Tailwind 3
│   ├── src/
│   │   ├── pages/      Home, Links, Stats
│   │   ├── components/ Layout
│   │   └── lib/api.ts  tiny fetch client
│   └── package.json
├── Dockerfile      multi-stage: build frontend → serve from FastAPI
├── docker-compose.yml
└── .github/workflows/
    ├── ci.yml              backend + frontend + docker
    └── claude-review.yml   Claude reviews every PR
```

## Local dev

**Backend** (terminal 1):

```bash
cd backend
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev    # http://localhost:5173, proxies /api to :8000
```

**Production-style** (single container):

```bash
docker compose up --build
# open http://localhost:8000
```

## Commands you must know

| What | Where | Command |
| --- | --- | --- |
| Run backend tests | `backend/` | `pytest -q` |
| Lint backend | `backend/` | `ruff check app tests` |
| Format backend | `backend/` | `ruff format app tests` |
| Run frontend tests | `frontend/` | `npm test` |
| Lint frontend | `frontend/` | `npm run lint` |
| Build frontend | `frontend/` | `npm run build` |
| Build full image | repo root | `docker build -t shortlink .` |

## Conventions for AI agents

- **Don't add dependencies casually.** This is a learning demo; keep both
  `pyproject.toml` and `package.json` lean.
- **Tests live next to code that needs them.** Backend tests in
  `backend/tests/`. Frontend tests as `*.test.tsx` next to the component.
- **No comments unless they explain a non-obvious why.** Leave the code clean.
- **Pydantic v2 + SQLAlchemy 2.0 syntax only.** No legacy patterns.
- **Frontend uses Tailwind utility classes**, not custom CSS. Keep components
  small and stateless where possible.
- **Don't introduce a frontend state library** (no Redux/Zustand/etc.). Local
  `useState` is enough for this demo.
- **Backend URL validation goes through Pydantic's `HttpUrl`** — do not hand-roll.
- **Database access only via SQLAlchemy ORM** — no raw SQL string concatenation.

## CI gates (must stay green)

A PR cannot merge unless:

1. `backend` job: ruff lint + format + pytest all pass
2. `frontend` job: eslint + vitest + build all pass
3. `docker` job: image builds end-to-end

When you change code, run the corresponding local commands before opening a PR.

## Secrets used by CI

These must be set in the GitHub repo settings as Actions secrets:

- `ANTHROPIC_AUTH_TOKEN` — API key for the Claude review job
- `ANTHROPIC_BASE_URL` — proxy/base URL for the Claude API

Local development does not need these — they are CI-only.
