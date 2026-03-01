import os

from dotenv import load_dotenv
from redis import Redis

from config import REDIS_DB, REDIS_HOST, REDIS_PORT

load_dotenv()

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)
