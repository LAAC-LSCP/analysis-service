import redis

from src.config import get_redis_host_and_port
from src.service.handlers.event_handlers import get_event_handlers
from src.service.queue.channels import get_channels
from src.service.service import Service


def run_app() -> None:
    channels = get_channels()
    r = redis.Redis(**get_redis_host_and_port())
    event_handlers = get_event_handlers()

    service = Service(r, channels, event_handlers)
    service.start()

    return


if __name__ == "__main__":
    run_app()
