# sandbox-backend

Main backend application for practicing different systems and libraries. FastAPI application with PostgreSQL, JWT cookie auth (access + refresh), and Alembic migrations.

## Prerequisites

- Python 3.12+
- PostgreSQL database

## Set up environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Create a `.env` file in the project root:

```env
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/sandbox
SECRET_KEY=change-me-to-a-long-random-string

# Optional (defaults shown)
CORS_ORIGINS=http://localhost:8080
ACCESS_TOKEN_EXPIRE_MINUTES=10
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_SIGNING_ALGORITHM=HS256
ACCESS_TOKEN_COOKIE_NAME=access_token
REFRESH_TOKEN_COOKIE_NAME=refresh_token
COOKIE_SECURE=false
DB_ECHO=true
```

`CORS_ORIGINS` accepts a comma-separated list (e.g. `http://localhost:8080,http://localhost:3000`).

Apply database migrations:

```bash
alembic upgrade head
```

Verify the database connection (optional):

```bash
python scripts/check_db.py
```

## Run

```bash
fastapi dev    # development (auto-reload) — http://127.0.0.1:8000
fastapi run    # production
```

Interactive API docs: http://127.0.0.1:8000/docs

Example HTTP requests live in `developer_assets/user_authorization.http`.

## API

| Method | Path                | Description                                      |
|--------|---------------------|--------------------------------------------------|
| POST   | `/v1/auth/register` | Register a user (sets access + refresh cookies)  |
| POST   | `/v1/auth/login`    | Log in (sets access + refresh cookies)           |
| POST   | `/v1/auth/refresh`  | Rotate tokens using the refresh cookie           |
| POST   | `/v1/auth/logout`   | Revoke refresh token and clear auth cookies      |
| GET    | `/v1/users/me`      | Current user (requires access token)             |

## Structure

```
sandbox-backend/
├── alembic/                 # Database migrations
├── developer_assets/        # HTTP request examples
├── scripts/                 # Utility scripts
├── src/
│   ├── main.py              # FastAPI app factory and lifespan
│   ├── config.py            # Settings from environment variables
│   ├── api/
│   │   └── router.py        # Aggregates feature routers
│   ├── core/
│   │   ├── middleware.py    # CORS and other middleware
│   │   └── security.py      # JWT, cookies, and password hashing
│   ├── db/
│   │   ├── database.py      # SQLAlchemy engine and session
│   │   └── models.py        # SQLAlchemy models
│   └── features/
│       ├── auth/            # Login, register, refresh, logout
│       │   └── dependencies.py  # get_current_user
│       └── users/           # User routes
├── tests/
├── .env                     # Local environment (not committed)
├── alembic.ini
└── pyproject.toml           # Dependencies + FastAPI entrypoint (src.main:app)
```
