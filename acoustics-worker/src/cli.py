import click
from analysis_service_core.src.config import Config
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.core.acoustics import Acoustics
from src.core.effort_model import AcousticsEffortModel


@click.command()
def run_acoustics():
    """
    Run acoustics worker.
    """
    config = Config()

    queue = Queue(QueueName.RUN_ACOUSTICS)
    effort_model = AcousticsEffortModel()

    acoustics = Acoustics(
        queue=queue,
        config=config,
        effort_model=effort_model,
        skip_moving_files=True,
    )

    acoustics.run()

    return


if __name__ == "__main__":
    run_acoustics()
