from redis import Redis

from config import REDIS_DB, REDIS_HOST, REDIS_PORT, settings

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=settings.redis_password,
    decode_responses=True,
)
