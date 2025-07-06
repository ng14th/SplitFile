from core.abstractions.singeton import Singleton
from core import constants
import logging
import redis.asyncio as async_redis
logger = logging.getLogger(constants.AUTH_CONSOLE)


class RedisLockManager(Singleton):
    def __init__(self):
        self._redis_client = None

    def set_redis_client(self, redis_client: async_redis.Redis):
        if not isinstance(redis_client, async_redis.Redis):
            raise TypeError("redis_client must be redis.Redis")
        self._redis_client = redis_client
        logger.info(
            f"RedisLockManager initialized {self._redis_client}"
        )

    def build_key(self, namespace: str, **kwargs) -> str:
        parts = [namespace] + [f"{k}:{v}" for k, v in sorted(kwargs.items())]
        return "lock:" + "-".join(parts)

    async def create_lock(self, namespace: str, timeout: int = 10, **kwargs):
        name = self.build_key(namespace, **kwargs)
        _lock = self._redis_client.lock(name=name, timeout=timeout)
        if await _lock.locked():
            logger.info(
                f"Lock {name} already locked by another process, waiting..."
            )
        return _lock


redis_lock: RedisLockManager = RedisLockManager()
