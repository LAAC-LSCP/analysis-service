from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.channels import ChannelName
from analysis_service_core.src.redis.pubsub import PubSub

from src.core.alice import ALICE


@click.command()
def run_alice():
    """
    Run alice worker
    """
    env_vars = {
        EnvVar(key="CONDA_ACTIVATE_FILE", type=Path),
        EnvVar(key="CONDA_ENV_NAME", type=str),
    }
    config = Config(env_vars)
    pubsub = PubSub(subscribe_to=[ChannelName.RUN_ALICE])

    alice = ALICE(
        pubsub=pubsub,
        config=config,
        skip_moving_files=True,
    )

    alice.run()


if __name__ == "__main__":
    run_alice()
