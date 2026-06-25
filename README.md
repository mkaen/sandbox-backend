# sandbox-backend
This is main backend repo for vibecoding

## Run

```bash
pip install -r requirements.txt
fastapi dev    # development (auto-reload)
fastapi run    # production
```

## Structure

```
sandbox-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI rakenduse loomine + middleware registreerimine
│   ├── config.py            # Seadistused (env muutujad)
│   ├── dependencies.py      # Ühised sõltuvused (auth, db sessioon jne)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py        # Kõigi routerite koondamine
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── items.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── middleware.py    # Kohandatud middleware klassid
│   │   └── security.py     # JWT, hashing jne
│   │
│   ├── models/              # SQLAlchemy / Pydantic mudelid
│   └── services/            # Äriloogika
│
├── tests/
├── .env
├── pyproject.toml       # fastapi dev / fastapi run entrypoint
└── requirements.txt
```
