import asyncio
from pathlib import Path

import click

from src.run_app import run


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Path to config file",
)
def run_daemon(config: str) -> None:
    asyncio.run(run(Path(config)))


if __name__ == "__main__":
    run_daemon()
