from core import constants
from typing import List, Optional, Tuple
from pydantic_settings import BaseSettings
import logging


logger = logging.getLogger(constants.AUTH_CONSOLE)


class RedisSetting(BaseSettings):
    REDIS_HOST: Optional[str] = 'localhost'
    REDIS_PORT: Optional[int] = 6379
    REDIS_DB: Optional[int] = 0
    REDIS_AUTH: Optional[str] = None
    REDIS_USER: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SENTINEL_SERVERS: List[Tuple[str, int]] = []
    REDIS_SENTINEL_NAME: Optional[str] = None
    REDIS_SENTINEL_REDIS_DB: Optional[int] = 0
    REDIS_SENTINEL_REDIS_PASSWORD: Optional[str] = None

    def get_redis_server_url(self) -> str:
        if self.REDIS_USER and self.REDIS_PASSWORD:
            logger.info('Connect redis with user and password success')
            return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        logger.info('Connect redis with auth success')
        return f"redis://:{self.REDIS_AUTH}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_redis_sentinel_urls(self) -> str:
        """get sentinel redis url

        Returns:
            str: result like sentinel://...
        """
        pass
