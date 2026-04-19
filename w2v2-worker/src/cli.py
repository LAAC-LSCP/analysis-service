from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.effort_model import W2V2EffortModel
from src.core.w2v2 import W2V2


@click.command()
def run_w2v2() -> None:
    env_vars = {
        EnvVar("W2V2_FOLDER", Path),
        EnvVar("W2V2_DEVICE", str),
        EnvVar("CHUNKIFY_THREADS", int),
        EnvVar("BATCH_SIZE", int),
        EnvVar("NUM_WORKERS", int),
    }

    config = Config(env_vars)
    queue = Queue(QueueName.RUN_W2V2)
    effort_model = W2V2EffortModel()

    w2v2 = W2V2(
        queue=queue,
        config=config,
        effort_model=effort_model,
        skip_moving_files=True,
    )

    w2v2.run()

    return


if __name__ == "__main__":
    run_w2v2()
