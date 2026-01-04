from pathlib import Path
from typing import Tuple

import redis

from src.config.config import ANALYSIS_SERVICE_DIR, load_config
from src.redis_utils import get_redis_host_and_port
from src.service.handlers.event_handlers import EventHandlers, get_event_handlers
from src.service.http_client import HTTPClient
from src.service.queue.channels import Channels, get_channels
from src.service.service import Service


async def run(config: Path) -> None:
    r, channels, event_handlers, http_client = setup(config)

    service = Service(r, channels, event_handlers, http_client)
    await service.start()

    return


def setup(config_file: Path) -> Tuple[redis.Redis, Channels, EventHandlers, HTTPClient]:
    ANALYSIS_SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    if not config_file.exists():
        raise FileNotFoundError(f"File at '{str(config_file)}' not found")

    config = load_config(config_file)

    http_client = HTTPClient(
        base_url=str(config.http.base_url).rstrip("/"),
        client_id=config.http.client_id,
        client_secret=config.http.client_secret,
    )
    event_handlers = get_event_handlers(http_client)

    channels = get_channels()
    r = redis.Redis(**get_redis_host_and_port())

    return r, channels, event_handlers, http_client
