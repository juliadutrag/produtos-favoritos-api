import redis.asyncio as redis

from app.core.config import settings

redis_pool = redis.ConnectionPool.from_url(
    f"redis://{settings.HOST_REDIS}:{settings.PORTA_REDIS}/0",
    decode_responses=True
)

def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)
