# fastapi-ai-cicd-demo

A small URL shortener whose **entire CI/CD is driven by AI**. The project
itself (FastAPI backend + Vite/React frontend) is just a vehicle for learning
how to let Claude agents handle code review, test maintenance, build
diagnosis, and release work — including from a phone.

> Inspired by Boris Cherny (Claude Code) and the "Agent-driven CI/CD"
> playbooks. See `CLAUDE.md` for the agent-facing project guide.

## What it does

- Paste a long URL → get a short code
- See your shortened links and click counts
- Drill into a 7-day click chart per link

## Stack

| Layer | Tech |
| --- | --- |
| Backend | FastAPI · Pydantic v2 · SQLAlchemy 2.0 · SQLite |
| Frontend | Vite · React 19 · TypeScript · Tailwind 3 · Recharts |
| Tests | pytest (backend) · vitest + Testing Library (frontend) |
| Container | Multi-stage Dockerfile (frontend build → served by FastAPI) |
| CI | GitHub Actions (lint + test + build + Docker) |
| AI | `anthropics/claude-code-action` for PR review |

## Quick start

```bash
# Backend
cd backend
uv venv --python 3.11 .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload   # http://localhost:8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

Or all-in-one:

```bash
docker compose up --build
# http://localhost:8000
```

## How AI is wired in

| Phase | What happens | Where |
| --- | --- | --- |
| 0 | Baseline CI: lint + test + build, gates every PR | `.github/workflows/ci.yml` |
| 1 | Claude reviews every PR diff and comments | `.github/workflows/claude-review.yml` |
| 2 | _(coming)_ Auto-generate tests for changed code | new workflow |
| 3 | _(coming)_ Auto-fix CI failures | new workflow |
| 4 | _(coming)_ Auto-deploy + release notes | new workflow |
| 5 | _(coming)_ Mobile-driven loops via Claude Dispatch | no repo code — set up in Claude app |

## Repo conventions

See `CLAUDE.md`. TL;DR: keep deps lean, prefer ORM over raw SQL, no comments
unless they explain a non-obvious why, tests live next to the code that needs them.
