# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
import asyncio

from .rabbitmq_setting import RabbitMQSetting
from .redis_setting import RedisSetting
from .minio_setting import MinioSetting

try:
    import core  # noqa
except ModuleNotFoundError:
    current_path = Path(os.getcwd())
    sys.path.append(str(current_path))

import core  # noqa
from core.constants import AUTH_CONSOLE
from core.format_log.init_logger import create_console_logger


class AppEnvConfig(
    RabbitMQSetting,
    RedisSetting,
    MinioSetting
):

    APP_SECRET_KEY: str = ''
    APP_PROJECT_NAME: str = "HLS-DEMO"
    APP_DEBUG: bool = True
    APP_DOCS_URL: Optional[str] = '/docs'
    SERVICE_PATH: Optional[str] = 'HLS-DEMO'
    SERVICE_ENVIRONMENT_INFO: Optional[str] = ''

    GUNICORN_HOST: str = '0.0.0.0'
    GUNICORN_PORT: str = '5000'

    POSTGRESQL_DB_MASTER_ENABLE: bool = True
    POSTGRESQL_DB_MASTER_ENGINE: str = ''
    POSTGRESQL_DB_MASTER_NAME: str = ''
    POSTGRESQL_DB_MASTER_USERNAME: str = ''
    POSTGRESQL_DB_MASTER_PASSWORD: str = ''
    POSTGRESQL_DB_MASTER_HOST: str = ''
    POSTGRESQL_DB_MASTER_PORT: int = 6432

    POSTGRESQL_REPLICA_01_ENABLE: bool = True
    POSTGRESQL_REPLICA_01_ENGINE: str = ''
    POSTGRESQL_REPLICA_01_NAME: str = ''
    POSTGRESQL_REPLICA_01_USERNAME: str = ''
    POSTGRESQL_REPLICA_01_PASSWORD: str = ''
    POSTGRESQL_REPLICA_01_HOST: str = ''
    POSTGRESQL_REPLICA_01_PORT: int = 5432

    class Config:
        case_sensitive = True
        validate_assignment = True
        env_file = Path(__file__).resolve().parent.parent.parent/"envs/.env"

    def set_os_settings(self):
        for attr, value in self.__dict__.items():
            if not attr.startswith("__") and not callable(value):
                os.environ[attr] = str(value) if value is not None else ''


settings = AppEnvConfig()
settings.setup_client_minio()
logger = create_console_logger(AUTH_CONSOLE, format_type='json')
