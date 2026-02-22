from redis import Redis
import os

redis_client = Redis(
    host="localhost",
    port=6379,
    db=0,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)

