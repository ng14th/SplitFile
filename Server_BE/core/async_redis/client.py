# -*- coding: utf-8 -*-
import logging
from typing import Optional

import redis.asyncio as redis
from core import constants
from redis import Redis as SyncRedis

from core.abstractions.singeton import Singleton


class RedisClient(Singleton):
    def __init__(self, **kwargs) -> None:
        self._client: redis.Redis = None
        self._name: Optional[str] = None
        self._is_connected: bool = False
        self.logger = kwargs.get('logger') \
            or logging.getLogger(constants.AUTH_CONSOLE)

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def client(self) -> redis.Redis:
        return self._client

    @property
    def slave_client(self) -> redis.Redis:
        return self._client

    async def connect(
        self,
        server_url: str,
        decode_responses: bool = True,     # response is bytes (default)
        **kwargs
    ):
        if isinstance(self._client, redis.Redis):
            return
        try:
            self._client = redis.Redis.from_url(
                server_url,
                decode_responses=decode_responses
            )
            self._name = f'Redis-Client-{server_url}'
            self._is_connected = True
            self.logger.info(
                f'RedisClient {self._name} | connected {self._is_connected}')
        except Exception as e:
            self.logger.exception(
                f'connect redis {server_url=} get exception {e}')

        return self._client

    async def disconnect(self, *args, **kwargs):
        if self._client and isinstance(self._client, redis.Redis):
            await self._client.close()
