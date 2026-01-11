import click
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.channels import ChannelName
from analysis_service_core.src.redis.pubsub import PubSub

from src.core.acoustics import Acoustics


@click.command()
def run_acoustics():
    """
    Run acoustics worker.
    """
    config = Config()
    pubsub = PubSub(subscribe_to=[ChannelName.RUN_ACOUSTICS])

    acoustics = Acoustics(
        pubsub=pubsub,
        config=config,
        skip_moving_files=True,
    )

    acoustics.run()

    return


if __name__ == "__main__":
    run_acoustics()
