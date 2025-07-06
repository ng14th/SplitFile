# -*- coding: utf-8 -*-
import logging
import ujson
from typing import Any

from core import constants
from core.abstractions import Singleton


class BaseClient(Singleton):
    def _singleton_init(self, **kwargs) -> Any:
        self.logger: logging.Logger = kwargs.get(
            "logger",
            logging.getLogger(constants.AUTH_CONSOLE)
        )

    def log_publish_result(
        self,
        result,
        data: Any,
        exchange_name: str,
        routing_key: str,
        **kwargs
    ):
        self.logger.info(
            f'Published rabbitmq message, ready {result.ready}',
            exchange=exchange_name,
            routing_key=routing_key,
            rabbit_publish_data=data,
            rabbit_publish_result={
                "ready": result.ready,
                "failed": result.failed,
                "cancelled": result.cancelled,
            },
            **kwargs,
        )

    def log_publish_result_async(
        self,
        result,
        data: Any,
        exchange_name: str,
        routing_key: str,
        **kwargs
    ):

        if isinstance(data, dict):
            data = ujson.dumps(data)

        self.logger.info(
            f'Published rabbitmq message, ready',
            rbmq_exchange=exchange_name,
            rbmq_routing_key=routing_key,
            rbmq_publish_data=data,
            **kwargs,
        )
