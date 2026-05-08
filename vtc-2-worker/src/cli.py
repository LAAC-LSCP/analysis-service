from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.effort_model import VTC2EffortModel
from src.core.vtc_2 import VTC2


@click.command()
def run_vtc_2() -> None:
    env_vars = {
        EnvVar(key="VTC_2_FOLDER", type=Path),
        EnvVar(key="VTC_2_DEVICE", type=str),
    }
    config = Config(env_vars)
    queue = Queue(QueueName.RUN_VTC_2)
    effort_model = VTC2EffortModel(config)

    vtc_2 = VTC2(
        queue=queue,
        config=config,
        effort_model=effort_model,
    )

    vtc_2.run()

    return


if __name__ == "__main__":
    run_vtc_2()
