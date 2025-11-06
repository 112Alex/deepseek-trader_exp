import redis.asyncio as redis
from typing import Set
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

# Используем одну Redis-инстанцию для всего приложения
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

async def add_subscriber(symbol: str, timeframe: str, chat_id: int):
    """
    Добавляет пользователя в список подписчиков на сигнал.
    Ключ в Redis будет иметь вид: sub:BTCUSDT:1h
    """
    key = f"sub:{symbol.replace('/', '')}:{timeframe}"
    await redis_client.sadd(key, str(chat_id))

async def remove_subscriber(symbol: str, timeframe: str, chat_id: int):
    """
    Удаляет пользователя из списка подписчиков.
    """
    key = f"sub:{symbol.replace('/', '')}:{timeframe}"
    await redis_client.srem(key, str(chat_id))

async def get_subscribers(symbol: str, timeframe: str) -> Set[str]:
    """
    Возвращает множество chat_id всех подписчиков на данный сигнал.
    """
    key = f"sub:{symbol.replace('/', '')}:{timeframe}"
    return await redis_client.smembers(key)

async def get_all_subscriptions() -> Set[str]:
    """
    Возвращает все уникальные ключи подписок (например, 'sub:BTCUSDT:1h').
    """
    return await redis_client.keys("sub:*")
