from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.channels import ChannelName
from analysis_service_core.src.redis.pubsub import PubSub

from src.core.vtc import VTC


@click.command()
def run_vtc():
    """
    Run VTC worker.
    """
    env_vars = {
        EnvVar(key="CONDA_ACTIVATE_FILE", type=Path),
        EnvVar(key="CONDA_ENV_NAME", type=str),
    }
    config = Config(env_vars)
    pubsub = PubSub(subscribe_to=[ChannelName.RUN_VTC])

    vtc = VTC(
        pubsub=pubsub,
        config=config,
        skip_moving_files=True,
    )

    vtc.run()

    return


if __name__ == "__main__":
    run_vtc()
