import click
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.w2v2 import W2V2


@click.command()
def run_vtc_2() -> None:
    config = Config()
    queue = Queue(QueueName.RUN_W2V2)

    w2v2 = W2V2(
        queue=queue,
        config=config,
        skip_moving_files=True,
    )

    w2v2.run()

    return
