from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config


def resolve_config_path(override: Optional[Path] = None) -> Path:
    if override:
        return override
    default_path = Path.cwd() / "alembic.ini"
    if default_path.exists():
        return default_path
    raise FileNotFoundError(
        "Unable to locate alembic.ini. "
        "Set ALEMBIC_CONFIG_PATH or pass --config pointing to the file."
    )


def get_alembic_config(config_path: Path) -> Config:
    return Config(str(config_path))


def main() -> None:
    parser = ArgumentParser(description="Run alembic migrations")
    parser.add_argument(
        "--config", "-c", type=Path, help="Path to alembic.ini"
    )
    args = parser.parse_args()
    config_path = resolve_config_path(args.config)
    command.upgrade(get_alembic_config(config_path), "head")
