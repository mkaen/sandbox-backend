# sandbox-backend

Main backend application for practicing different systems and libraries. FastAPI application with PostgreSQL, JWT cookie auth, and Alembic migrations.

## Prerequisites

- Python 3.12+
- PostgreSQL database

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sandbox
SECRET_KEY=change-me-to-a-long-random-string

# Optional
CORS_ORIGINS=http://localhost:8080
ACCESS_TOKEN_EXPIRE_MINUTES=10
JWT_SIGNING_ALGORITHM=HS256
ACCESS_TOKEN_COOKIE_NAME=access_token
COOKIE_SECURE=false
DB_ECHO=true
```

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

| Method | Path                | Description               |
|--------|---------------------|---------------------------|
| POST   | `/v1/auth/register` | Register a user           |
| POST   | `/v1/auth/login`    | Log in (sets auth cookie) |

## Structure

```
sandbox-backend/
├── alembic/                 # Database migrations
├── developer_assets/        # HTTP request examples
├── scripts/                 # Utility scripts
├── src/
│   ├── main.py              # FastAPI app factory and lifespan
│   ├── config.py            # Settings from environment variables
│   ├── dependencies.py      # Shared dependencies (e.g. current user)
│   ├── api/
│   │   └── router.py        # Aggregates feature routers
│   ├── core/
│   │   ├── middleware.py    # CORS and other middleware
│   │   └── security.py      # JWT and password hashing
│   ├── db/
│   │   ├── database.py      # SQLAlchemy engine and session
│   │   └── models.py        # SQLAlchemy models
│   └── features/
│       ├── auth/            # Login and registration
│       └── users/           # User routes
├── tests/
├── .env                     # Local environment (not committed)
├── alembic.ini
└── pyproject.toml           # Dependencies + FastAPI entrypoint (src.main:app)
```
