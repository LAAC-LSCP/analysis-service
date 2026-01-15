from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.vtc import VTC


@click.command()
def run_vtc():
    """
    Run VTC worker.
    """
    env_vars = {
        EnvVar(key="CONDA_ACTIVATE_FILE", type=Path),
        EnvVar(key="CONDA_ENV_NAME", type=str),
        EnvVar(key="VTC_FOLDER", type=Path),
        EnvVar(key="VTC_DEVICE", type=str),
    }
    config = Config(env_vars)
    queue = Queue(QueueName.RUN_VTC)

    vtc = VTC(
        queue=queue,
        config=config,
        skip_moving_files=True,
    )

    vtc.run()

    return


if __name__ == "__main__":
    run_vtc()
