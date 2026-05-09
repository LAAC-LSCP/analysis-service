import click
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.acoustics import Acoustics
from src.core.effort_model import AcousticsEffortModel
from src.core.metannots_factory import AcousticsMetannotsFactory


@click.command()
def run_acoustics():
    """
    Run acoustics worker.
    """
    config = Config()

    queue = Queue(QueueName.RUN_ACOUSTICS)
    effort_model = AcousticsEffortModel(config=config)

    acoustics = Acoustics(
        queue=queue,
        config=config,
        effort_model=effort_model,
        metannots_factory=AcousticsMetannotsFactory(),
    )
    acoustics.run()

    return


if __name__ == "__main__":
    run_acoustics()
