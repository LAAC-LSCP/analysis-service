from pathlib import Path
from typing import Tuple

from analysis_service_core.src.redis.channels import Channels, get_channels
from analysis_service_core.src.redis.pubsub import PubSub

from src.config.config import load_config
from src.service.command_handlers import CommandHandlers, get_command_handlers
from src.service.http_client import HTTPClient
from src.service.service import Service


async def run(config: Path) -> None:
    pubsub, channels, command_handlers, http_client = setup(config)

    pubsub = PubSub(subscribe_to=list(get_channels().channel_names))

    service = Service(pubsub, channels, command_handlers, http_client)
    await service.start()

    return


def setup(config_file: Path) -> Tuple[PubSub, Channels, CommandHandlers, HTTPClient]:
    if not config_file.exists():
        raise FileNotFoundError(f"File at '{str(config_file)}' not found")

    config = load_config(config_file)

    http_client = HTTPClient(
        base_url=str(config.http.base_url).rstrip("/"),
        client_id=config.http.client_id,
        client_secret=config.http.client_secret,
    )
    command_handlers = get_command_handlers(http_client)

    channels = get_channels()
    pubsub = PubSub(subscribe_to=list(channels.channel_names))

    return pubsub, channels, command_handlers, http_client
