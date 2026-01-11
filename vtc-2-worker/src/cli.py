from pathlib import Path

import click
from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.channels import ChannelName
from analysis_service_core.src.redis.pubsub import PubSub

from src.core.vtc_2 import VTC_2


@click.command()
def run_vtc_2() -> None:
    env_vars = {
        EnvVar(key="VTC_2_FOLDER", type=Path),
        EnvVar(key="VTC_2_DEVICE", type=str),
    }
    config = Config(env_vars)
    pubsub = PubSub(subscribe_to=[ChannelName.RUN_VTC_2])

    vtc_2 = VTC_2(
        pubsub=pubsub,
        config=config,
        skip_moving_files=True,
    )

    vtc_2.run()

    return
