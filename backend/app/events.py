import json

import redis

from app.config import get_settings
from app.schemas import CheckEvent

MONITOR_EVENTS_CHANNEL = "monitor_events"

settings = get_settings()
_redis_client = redis.Redis.from_url(settings.celery_broker_url)


def publish_check_event(event: CheckEvent) -> None:
    _redis_client.publish(MONITOR_EVENTS_CHANNEL, event.model_dump_json())


def parse_check_event(raw_message: bytes | str) -> CheckEvent:
    payload = json.loads(raw_message)
    return CheckEvent.model_validate(payload)
