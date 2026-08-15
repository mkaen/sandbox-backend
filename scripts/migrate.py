import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alembic import command
from alembic.config import Config

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if __name__ == "__main__":
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied.")
