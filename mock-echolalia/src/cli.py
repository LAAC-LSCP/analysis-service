import os
from pathlib import Path

import click
import yaml

from src.create_app import create_app
from src.app_types import Database

EXPECTED_CLIENT_ID = os.environ.get("EXPECTED_CLIENT_ID", None)
EXPECTED_CLIENT_SECRET = os.environ.get("EXPECTED_CLIENT_SECRET", None)
FLASK_PORT = os.environ.get("FLASK_PORT", None)


@click.command()
@click.option(
    "--db-path",
    required=True,
    type=click.Path(exists=True),
    help="Path to database.yml",
)
def start_server(db_path: Path):
    """Start a mock Echolalia server"""
    check_config()

    db_raw: dict
    with open(db_path, "r") as f:
        db_raw = yaml.safe_load(f)

    db = Database(**db_raw)

    start_app(db)


def check_config() -> None:
    if EXPECTED_CLIENT_ID is None:
        raise ValueError("EXPECTED_CLIENT_ID environment variable is not set.")
    if EXPECTED_CLIENT_SECRET is None:
        raise ValueError(
            "EXPECTED_CLIENT_SECRET environment variable is not \
set."
        )
    if FLASK_PORT is None:
        raise ValueError("FLASK_PORT environment variable is not set.")


def start_app(db):
    app = create_app(
        db=db,
        expected_client_id=EXPECTED_CLIENT_ID,
        expected_client_secret=EXPECTED_CLIENT_SECRET,
    )
    app.run(debug=True, host="0.0.0.0", port=FLASK_PORT)


if __name__ == "__main__":
    start_server()
