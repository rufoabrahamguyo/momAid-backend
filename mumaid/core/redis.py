import os
import redis


def redis_client():
    return redis.from_url(os.getenv("REDIS_URL"))