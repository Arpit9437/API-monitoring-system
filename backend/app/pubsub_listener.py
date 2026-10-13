import asyncio
import logging

import redis.asyncio as redis_asyncio

from app.config import get_settings
from app.events import MONITOR_EVENTS_CHANNEL
from app.websocket_manager import connection_manager

logger = logging.getLogger(__name__)

RECONNECT_DELAY_SECONDS = 3


async def listen_for_check_events() -> None:
    settings = get_settings()
    while True:
        try:
            await _consume_events(settings.celery_broker_url)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("pubsub listener caiu, reconectando em %ss", RECONNECT_DELAY_SECONDS)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)


async def _consume_events(broker_url: str) -> None:
    client = redis_asyncio.from_url(broker_url)
    pubsub = client.pubsub()
    try:
        await pubsub.subscribe(MONITOR_EVENTS_CHANNEL)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            raw_data = message["data"]
            text = raw_data.decode() if isinstance(raw_data, bytes) else raw_data
            await connection_manager.broadcast(text)
    finally:
        try:
            await pubsub.unsubscribe(MONITOR_EVENTS_CHANNEL)
        except Exception:
            logger.exception("falha ao cancelar inscricao do pubsub")
        try:
            await client.aclose()
        except Exception:
            logger.exception("falha ao fechar conexao com o redis")
