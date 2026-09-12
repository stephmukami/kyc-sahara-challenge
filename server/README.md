# KYC Orchestrator — server

FastAPI + PostgreSQL backend. This is Stage 1 of the build order in the design
doc: domain models, migrations, and admin CRUD for Apps and the block catalog.

## Setup

```bash
uv sync
cp .env.example .env
docker compose up -d          # starts Postgres on localhost:5432
uv run alembic upgrade head   # creates all tables + enums
uv run python -m app.db.seed  # seeds the starter block catalog (6 blocks)
uv run uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Tests

```bash
docker compose up -d
uv run pytest
```

Tests reset the schema against `DATABASE_URL` before each test — point it at
a disposable database, not one with data you care about.

## What's implemented

- All 9 domain models (§03): `App`, `KYCBlockDefinition`, `AppKYCBlockConfig`,
  `KYCSession`, `KYCBlockExecution`, `ConsentRecord`, `AdminUser`, `EndUser`,
  `AuditLog`.
- Initial Alembic migration (`alembic/versions/b0cded8f4ad7_initial_schema.py`).
- Starter block catalog seed (`app/db/seed.py`) — 6 blocks covering identity,
  biometric, consent, and compliance categories.
- Admin API:
  - `GET /api/v1/admin/apps` — list apps with live active-session counts
  - `POST /api/v1/admin/apps` — create an app
  - `GET /api/v1/admin/apps/{id}` — fetch one app
  - `GET /api/v1/admin/kyc-blocks` — the read-only block catalog
  - `GET /api/v1/admin/apps/{id}/blocks` — an app's current pipeline
  - `PUT /api/v1/admin/apps/{id}/blocks` — bulk-set an app's pipeline

Everything else in the repo tree (orchestrator, channel adapters, block
registry, voice/telephony providers, workers, object storage, session/user/
audit-log admin endpoints, client + telephony API routes) is scaffolded as
empty packages with a comment noting which build stage fills them in — see
`app/services/`, `app/workers/`, `app/storage/`, `app/api/v1/client/`,
`app/api/v1/telephony/`.

No auth is wired up yet (out of scope for Stage 1) — admin endpoints are open,
and `created_by_id` / `updated_by_id` are passed explicitly in request bodies.
