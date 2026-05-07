import asyncio

import click

from src.run_app import run


@click.command()
def run_daemon() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    run_daemon()
