import uuid

import click
import redis

from src.core.redis_utils import get_redis_host_and_port
from src.core.run_vtc import run_vtc as run_vtc_cmd


@click.command()
@click.option(
    "--task-id",
    type=click.UUID,
    required=True,
    help="The task ID to use",
)
def run_vtc(task_id: uuid.UUID):
    """
    Run VTC worker with the specified task ID.
    """
    r = redis.Redis(**get_redis_host_and_port())

    run_vtc_cmd(r, task_id)

    return


if __name__ == "__main__":
    run_vtc()
