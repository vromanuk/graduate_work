from functools import lru_cache
from typing import Optional

from redis import Redis

redis: Optional[Redis] = None


@lru_cache()
def get_redis() -> Redis:
    return redis
