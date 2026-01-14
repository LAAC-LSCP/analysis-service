from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.w2v2 import W2V2


@click.command()
def run_w2v2() -> None:
    env_vars = {
        EnvVar("W2V2_FOLDER", Path),
        EnvVar("W2V2_DEVICE", str),
        EnvVar("MAKE_CHUNKS_THREADS", int),
        EnvVar("BATCH_SIZE", int),
        EnvVar("NUM_WORKERS", int),
    }

    config = Config(env_vars)
    queue = Queue(QueueName.RUN_W2V2)

    w2v2 = W2V2(
        queue=queue,
        config=config,
        skip_moving_files=True,
    )

    w2v2.run()

    return


if __name__ == "__main__":
    run_w2v2()
