import redis

from app.config import get_settings

settings = get_settings()
_redis_client = redis.Redis.from_url(settings.celery_broker_url)


def _lock_key(monitor_id: int) -> str:
    return f"monitor-check-lock:{monitor_id}"


def acquire_check_lock(monitor_id: int, ttl_seconds: int) -> bool:
    return bool(_redis_client.set(_lock_key(monitor_id), "1", nx=True, ex=ttl_seconds))


def release_check_lock(monitor_id: int) -> None:
    _redis_client.delete(_lock_key(monitor_id))
