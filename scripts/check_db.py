import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from src.db.database import engine

# RUN IT WITH COMMAND IN TERMINAL: .venv/bin/python scripts/check_db.py

if __name__ == "__main__":
    with engine.connect() as conn:
        print("Connection OK:", conn.execute(text("SELECT 1")).scalar())
