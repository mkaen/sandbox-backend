# sandbox-backend — agent instructions

FastAPI + PostgreSQL backend. Prefer a maintainable, production-grade change over a short hack that “just works”. It has to be proffessional and safe.

## Quality bar

- Keep function signatures compact: do not put each parameter on its own line unless the line would exceed ~120 characters. Prefer a single line (or at most two) for signatures and call sites.
- Finish the real design: validation, authz, error paths, and side effects — not only the happy path.
- Do not leave `TODO`, `FIXME`, `pass`, empty `except`, or commented-out logic as the solution.
- Match existing layers. Do not add shortcuts (SQL in a router, HTTP in a repository, business rules in `main.py`).
- If behaviour changes, update or add tests under `tests/`. If tests are missing for that area, say so and add the ones that lock the change.
- Do not “simplify” auth, cookies, or migrations to save a few lines.

## Architecture

```
router → service → repository → db
         schemas (request/response)
         dependencies (authn/authz)
```

| Layer | Lives in | Responsibility |
|---|---|---|
| HTTP | `src/features/<name>/router.py` | Routes, status codes, `Depends`, map request → service |
| Validation | `src/features/<name>/schemas.py` | Pydantic models, aliases (`firstName`), field/model validators |
| Business rules | `src/features/<name>/service.py` | Authz checks, `HTTPException`, orchestration, logging |
| Persistence | `src/features/<name>/repository.py` | SQLAlchemy queries and commits only |
| Authn/authz | `src/features/<name>/dependencies.py` | `get_current_user`, `require_self_or_admin`, and similar |
| Shared infra | `src/core/`, `src/db/`, `src/config.py` | Security, logging, sessions, settings |

Register new routers in `src/api/router.py`. Keep models in `src/db/models.py`.

## New feature checklist

1. Schemas with camelCase aliases where the API already uses them.
2. Repository functions that return ORM objects or `None` — not HTTP errors (except existing local patterns; prefer raising from the service).
3. Service functions that raise `HTTPException` with a clear `detail`.
4. Thin router: inject `Session` via `get_db` and the current user via dependencies.
5. Schema change → Alembic revision (`alembic revision --autogenerate -m "..."`), never edit old migrations.
6. Wire the router into `src/api/router.py`.

## API and errors

- Versioned prefixes: `/v1/<resource>`.
- Auth is HttpOnly cookies (`access_token` / `refresh_token`), not `Authorization` headers unless the code already does that.
- Domain failures: `HTTPException`. Invalid bodies: Pydantic / `RequestValidationError`. Unhandled errors stay 500 via `src/core/exception_handlers.py` — do not leak internals.
- Log through `src.core.logger.logger`. Do not print.

## Database and config

- Schema changes go through Alembic. Apply with `alembic upgrade head` or `python scripts/migrate.py`.
- Settings live in `src/config.py`. New env vars need a field there and an update to `.env.example` (and `.env.prod.example` if production-relevant).
- Never commit `.env`, `.env.prod`, secrets, or credentials.

## What not to do

- Do not invent a parallel folder layout or a new app factory.
- Do not skip authorization on user-scoped routes (`require_self_or_admin` or equivalent).
- Do not hard-code URLs, secrets, or environment-specific hosts; use `settings`.
- Do not rewrite working code “while here” unless it is required for the task.
