# sandbox-backend

Main backend application for practicing different systems and libraries. FastAPI application with PostgreSQL, JWT cookie auth (access + refresh), structured JSON logging, and Alembic migrations.

## Stack

- **Python** 3.12+ (Docker image uses 3.14)
- **FastAPI** + Uvicorn
- **PostgreSQL** (Third service provider or local Docker)
- **SQLAlchemy** 2.x + **Alembic**
- **PyJWT** + **pwdlib** (Argon2 password hashing)

## Prerequisites

- Python 3.12+
- PostgreSQL database (remote or local via Docker)
- [Optional] Docker & Docker Compose

## Getting started

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Configure environment

Copy the example file and edit values:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Long random string for signing JWTs |

See [Environment variables](#environment-variables) for the full list.

> `.env` and `.env.prod` are gitignored. Never commit credentials.

### 3. Apply database migrations

Migrations read `DATABASE_URL` from `.env` (via `src/config.py`):

```bash
alembic upgrade head
# or
python scripts/migrate.py
```

Verify the connection (optional):

```bash
python scripts/check_db.py
```

### 4. Run the app

```bash
fastapi dev    # development (auto-reload) — http://127.0.0.1:8000
fastapi run    # production-style local run
```

Interactive API docs: http://127.0.0.1:8000/docs

Example HTTP requests: `developer_assets/user_authorization.http`

---

## Database setup

The app only needs a single `DATABASE_URL`. You can use a remote provider or a local Postgres container.

### Supabase (recommended for dev & prod)

Use **separate Supabase projects** for development and production. Each project has its own:

- Reference ID (used in the username: `postgres.<project-ref>`)
- Pooler hostname (e.g. `aws-0-eu-west-1` vs `aws-1-eu-west-1` — these differ per project)
- Database password

| Environment | Env file | When to migrate |
|-------------|----------|-----------------|
| Local development | `.env` | `alembic upgrade head` |
| Live production | `.env.prod` | CI: `alembic upgrade head` before deploy |

**Getting the connection string**

1. Open the correct Supabase project (dev or prod).
2. Go to **Connect** → choose **Transaction pooler** (port `6543`) or **Session pooler** / **Direct** (port `5432`).
3. Copy the URI and paste it as `DATABASE_URL` in the matching env file.

Example format (Transaction pooler):

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-<N>-<region>.pooler.supabase.com:6543/postgres
```

**Common mistake:** mixing credentials from one project with the hostname from another (e.g. dev project ref + prod pooler host). Supabase returns `tenant/user postgres.<ref> not found`. Always copy the full URI from the **same** project's Connect page.

**Production migrations**

`scripts/migrate.py` and Alembic load `.env` by default. For production, pass variables from `.env.prod`:

```bash
set -a && source .env.prod && set +a && python scripts/migrate.py
```

Or inline:

```bash
DATABASE_URL="postgresql://..." python scripts/migrate.py
```

### Local PostgreSQL (Docker)

Run a local Postgres instance without an external provider:

```bash
docker compose --profile local-db up -d db
```

Use the host URL in `.env` for both the app and migrations:

```env
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/sandbox
```

When the API runs in Docker Compose, `127.0.0.1:5433` is rewritten to `db:5432` so the container reaches Postgres on the compose network.

Then apply migrations:

```bash
python scripts/migrate.py
```

---

## Docker

### Local development

Hot reload, optional local Postgres. Uses `.env`.

```bash
docker compose up --build
docker compose --profile local-db up --build   # with local Postgres
```

App: http://localhost:8000

### Live production

Uses `.env.prod`. Workers, HTTPS cookies, no source mount:

```bash
cp .env.prod.example .env.prod         # once
docker compose -f docker-compose.prod.yml up --build -d
```

Production overrides:

- `ENVIRONMENT=production` (`/docs` is disabled)
- `COOKIE_SECURE=true`
- `POOL_PRE_PING=true`
- `DB_ECHO=false`
- `LOG_JSON=true`

Run database migrations in CI **before** deploying the new image. The container does not run Alembic.

Health check: `GET /health` → `{"status":"ok"}`.

---

## Migrations (Alembic)

Migration scripts live in `alembic/versions/`.

```bash
# Apply all pending migrations
alembic upgrade head

# Show current revision
alembic current

# Create a new migration (after model changes)
alembic revision --autogenerate -m "describe change"
```

Alembic reads `DATABASE_URL` from environment / `.env` through `alembic/env.py` → `src.config.settings`.

---

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/auth/register` | Register a user (sets access + refresh cookies) |
| POST | `/v1/auth/login` | Log in (sets access + refresh cookies) |
| POST | `/v1/auth/refresh` | Rotate tokens using the refresh cookie |
| POST | `/v1/auth/logout` | Revoke refresh token and clear auth cookies |
| GET | `/v1/users/me` | Current user (requires access token cookie) |
| GET | `/health` | Liveness probe (no auth, not logged) |

Auth uses **HttpOnly cookies** for access and refresh tokens. `COOKIE_SECURE` must be `true` on HTTPS (production). If the frontend is on a different site than the API, set `COOKIE_SAMESITE=none`.

---

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | yes | — | PostgreSQL connection string |
| `SECRET_KEY` | yes | — | JWT signing secret |
| `ENVIRONMENT` | no | `development` | Environment name (`development`, `production`, …) |
| `CORS_ORIGINS` | no | `http://localhost:8080` | Comma-separated allowed origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | `10` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | no | `7` | Refresh token lifetime |
| `JWT_SIGNING_ALGORITHM` | no | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_COOKIE_NAME` | no | `access_token` | Access cookie name |
| `REFRESH_TOKEN_COOKIE_NAME` | no | `refresh_token` | Refresh cookie name |
| `COOKIE_SECURE` | no | `false` | Set `true` when serving over HTTPS |
| `COOKIE_SAMESITE` | no | `lax` | Cookie SameSite (`none` if frontend is on another site) |
| `POOL_PRE_PING` | no | `false` | Recycle stale DB connections (`true` in production) |
| `DB_ECHO` | no | `true` | Log SQL statements |
| `LOG_LEVEL` | no | `INFO` | Logging level |
| `LOG_JSON` | no | `true` | Emit structured JSON logs |

Templates: `.env.example` (local), `.env.prod.example` (production)

---

## Project structure

```
sandbox-backend/
├── alembic/                    # Database migrations
│   └── versions/
├── developer_assets/           # HTTP request examples (.http)
├── scripts/
│   ├── migrate.py              # Apply migrations (upgrade head)
│   └── check_db.py             # Test DATABASE_URL connectivity
├── src/
│   ├── main.py                 # FastAPI app factory and lifespan
│   ├── config.py               # Settings from environment variables
│   ├── api/
│   │   └── router.py           # Aggregates feature routers
│   ├── core/
│   │   ├── middleware.py       # CORS and other middleware
│   │   ├── security.py         # JWT, cookies, password hashing
│   │   └── logger.py           # Structured logging setup
│   ├── db/
│   │   ├── database.py         # SQLAlchemy engine and session
│   │   └── models.py           # SQLAlchemy models
│   └── features/
│       ├── auth/               # Login, register, refresh, logout
│       │   └── dependencies.py # get_current_user
│       └── users/              # User routes
├── tests/
├── .env                        # Local development (not committed)
├── .env.prod                   # Live production (not committed)
├── .env.example                # Local env template
├── .env.prod.example           # Production env template
├── alembic.ini
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Live production
├── Dockerfile
└── pyproject.toml              # Dependencies + FastAPI entrypoint (src.main:app)
```

---

## Before deployment to production

Live’i juurde jõudes jäta meelde: .env.prod täidetud, HTTPS proxy ees, CORS_ORIGINS päris frontend, enne deploy’d alembic upgrade head prod baasi peal. Need ei ole Dockeri augud.
