import json

import redis
from redis.client import PubSub

from src import config
from src.service.queue.channels import ChannelName

r = redis.Redis(**config.get_redis_host_and_port())


def subscribe_to(channel) -> PubSub:
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    confirmation = pubsub.get_message(timeout=3)

    assert confirmation["type"] == "subscribe"

    return pubsub


def publish_message(channel: ChannelName, message: dict) -> None:
    r.publish(channel, json.dumps(message))
