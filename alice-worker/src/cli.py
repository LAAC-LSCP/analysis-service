from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.alice import ALICE
from src.core.effort_model import ALICEEffortModel


@click.command()
def run_alice():
    """
    Run alice worker
    """
    env_vars = {
        EnvVar(key="CONDA_ACTIVATE_FILE", type=Path),
        EnvVar(key="CONDA_ENV_NAME", type=str),
        EnvVar(key="ALICE_FOLDER", type=Path),
        EnvVar(key="ALICE_DEVICE", type=str),
    }
    config = Config(env_vars)
    queue = Queue(QueueName.RUN_ALICE)
    effort_model = ALICEEffortModel(config)

    alice = ALICE(
        queue=queue,
        config=config,
        effort_model=effort_model,
    )

    alice.run()


if __name__ == "__main__":
    run_alice()
