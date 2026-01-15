from typing import Tuple

from analysis_service_core.src.config import Config, EnvVar
from analysis_service_core.src.redis.queue import Queue, QueueName

from src.service.command_handlers import CommandHandlers, get_command_handlers
from src.service.http_client import HTTPClient
from src.service.service import Service


async def run() -> None:
    completion_queue, command_handlers, http_client = setup()

    service = Service(completion_queue, command_handlers, http_client)
    await service.start()

    return


def setup() -> Tuple[Queue, CommandHandlers, HTTPClient]:
    env_vars = {
        EnvVar("BASE_URL", str),
        EnvVar("CLIENT_ID", str),
        EnvVar("CLIENT_SECRET", str),
    }
    config = Config(env_vars, check_required=False)

    http_client = HTTPClient(
        base_url=config.get("BASE_URL").rstrip("/"),
        client_id=config.get("CLIENT_ID"),
        client_secret=config.get("CLIENT_SECRET"),
    )

    queues = {name: Queue(name) for name in list(QueueName)}
    command_handlers = get_command_handlers(http_client, queues)

    return Queue(QueueName.COMPLETE_TASK), command_handlers, http_client
