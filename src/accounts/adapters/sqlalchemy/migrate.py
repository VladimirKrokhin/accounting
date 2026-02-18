import os
from pathlib import Path
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv
import accounts
from accounts.adapters.sqlalchemy.db import get_postgres_uri
from accounts.config import load_config


def run_migrations():
    load_dotenv(".envs/.env.prod")
    app_config = load_config()

    current_dir = Path(__file__).parent.resolve()

    package_root = Path(os.path.dirname(accounts.__file__)).resolve()
    ini_path = package_root / "alembic.ini"

    migrations_path = current_dir / "migrations"

    cfg = Config(str(ini_path))

    cfg.set_main_option("script_location", str(migrations_path / ""))

    db_url = get_postgres_uri(app_config.get_postgres_config())
    cfg.set_main_option("sqlalchemy.url", db_url)

    print(f"Starting migrations from: {migrations_path}")
    command.upgrade(cfg, "head")
