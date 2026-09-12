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
uv run python -m app.db.seed_admin <email> <password>  # bootstraps the first super_admin
uv run uvicorn app.main:app --reload
```

Set `JWT_SECRET_KEY` in `.env` before running anywhere but local dev — it signs
every access/refresh token. `AFRICASTALKING_USERNAME` / `AFRICASTALKING_API_KEY`
/ `AFRICASTALKING_SENDER_ID` are optional; without them, OTPs are logged
instead of sent (fine for local dev, not for anything real).

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
- Auth API:
  - `POST /api/v1/admin/auth/signup` — create an admin (requires a `super_admin` bearer token; the very first super_admin comes from `app/db/seed_admin.py`, not this endpoint)
  - `POST /api/v1/admin/auth/login` — email + password → access/refresh JWT
  - `POST /api/v1/admin/auth/forgot-password`, `POST /api/v1/admin/auth/reset-password`
  - `POST /api/v1/client/auth/signup`, `POST /api/v1/client/auth/signup/verify` — phone + first/last name → OTP → JWT
  - `POST /api/v1/client/auth/login`, `POST /api/v1/client/auth/login/verify` — phone → OTP → JWT
  - `POST /api/v1/telephony/voice/inbound`, `POST /api/v1/telephony/voice/recording` — Africa's Talking inbound-call webhooks for voice signup (caller ID is treated as proof of phone ownership, so no OTP; the spoken name is stored as an audio recording — transcription into `full_name` is a later step, not yet implemented)

Everything else in the repo tree (orchestrator, channel adapters, block
registry, workers, object storage, session/user/audit-log admin endpoints,
client KYC routes, telephony USSD/resume) is scaffolded as empty packages
with a comment noting which build stage fills them in — see `app/services/`,
`app/workers/`, `app/storage/`, `app/api/v1/client/`, `app/api/v1/telephony/`.

Auth (admin JWT, phone OTP) is now wired up — see Auth API above — but it
isn't yet *enforced* anywhere else: the `admin/apps` and `admin/kyc-blocks`
endpoints are still open, and `created_by_id` / `updated_by_id` are still
passed explicitly in request bodies rather than derived from a logged-in
admin. Gating those endpoints behind `Depends(get_current_admin_user)` is a
follow-up, not done here.
