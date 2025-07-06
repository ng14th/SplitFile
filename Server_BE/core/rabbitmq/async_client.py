
import asyncio
import json
from typing import Any, Dict, List
from faststream import rabbit
from aio_pika import RobustConnection, RobustQueue, RobustExchange
from aio_pika.exceptions import AMQPConnectionError
from core import constants
from core.async_redis.client import RedisClient
from core.context_var import event_id
from core.rabbitmq.base import BaseClient
from core.async_redis.redis_lock_manager import redis_lock
from core.database import db_init

RABBITMQ_MESSAGE_RETRY_COUNT = 10
RABBITMQ_MESSAGE_DELAY_SECONDS = 30

PREFETCH_COUNT = 10


class AsyncRabbitMqClient(BaseClient):
    """RabbitMQ Client for publish message to RabbitMQ Using AIO-PIKA
    """

    def _singleton_init(self, **kwargs) -> Any:
        self.is_connected: bool = False
        self.broker: rabbit.RabbitBroker = None
        self.exchanges: Dict[str, RobustExchange] = {}
        self.connections: Dict[str, RobustConnection] = {}
        return super()._singleton_init(**kwargs)

    def get_default_connection(self, connection_name) -> RobustConnection:
        connection = self.connections.get(connection_name, None)
        if connection and isinstance(connection, RobustConnection):
            return connection

        for connection_url, connection_instance in self.connections.items():
            return connection_instance

    async def ensure_connection(self, amqp_urls):
        connection = self.get_default_connection(None)
        if connection.connected:
            self.is_connected = True
            return
        await self.connect(amqp_urls)

    async def get_exchange(
        self,
        exchange_name: str,
        connection_name: str = None
    ) -> RobustExchange:

        connection = self.get_default_connection(connection_name)
        if not connection:
            self.logger.error(f'Connection default not found')
            return

        if exchange_name in self.exchanges:
            return self.exchanges[exchange_name]

    async def connect(self, amqp_urls: str) -> None:
        try:
            for amqp_url in amqp_urls.split(","):
                try:
                    if self.is_connected:
                        return
                    self.broker = rabbit.RabbitBroker(
                        amqp_url,
                        max_consumers=PREFETCH_COUNT
                    )
                    connection = await self.broker.connect(amqp_url)
                    self.connections[amqp_url] = connection
                    self.is_connected = True
                    self.logger.info(
                        f'Connected to RabbitMQ with url {amqp_url}')
                    return self.broker
                except AMQPConnectionError as e:
                    self.logger.warning(
                        f'Connect to RabbitMQ with url {amqp_url} get exception {e} try reconnect with other url')
                    continue
        finally:
            if not self.is_connected:
                raise AMQPConnectionError(
                    f'Can not connect to RabbitMQ with list url {amqp_urls}')

    async def _publish(
        self,
        data: Any,
        _exchange: str,
        routing_key: str,
        **kwargs,
    ):

        # if isinstance(data, bytes):
        #     data = data
        # elif isinstance(data, str):
        #     data = data.encode('utf-8')
        # else:
        #     data = json.dumps(data).encode('utf-8')
        publish_headers = {'eid': event_id.get_event_id()}
        return await self.broker.publish(
            data,
            exchange=_exchange,
            routing_key=routing_key,
            headers=publish_headers
        )

    async def declare_exchange(
        self,
        exchange_name: str,
        type: rabbit.ExchangeType.DIRECT,
        durable: bool = True,
        auto_delete: bool = False
    ) -> "RobustExchange":

        exchange = None
        if isinstance(exchange_name, str):
            exchange = await self.get_exchange(exchange_name)

        if not isinstance(exchange, RobustExchange):
            _exchange = rabbit.RabbitExchange(
                name=exchange_name,
                type=type,
                durable=durable,
                auto_delete=auto_delete,
            )
            exchange = await self.broker.declare_exchange(_exchange)

            self.exchanges[exchange_name] = exchange
            self.logger.info(f'Exchange {exchange_name} declared')

        return self.exchanges[exchange_name]

    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        arguments: dict = {}
    ) -> "RobustQueue":

        _queue = rabbit.RabbitQueue(
            name=queue_name,
            queue_type=rabbit.QueueType.QUORUM,
            durable=durable,
            arguments=arguments
        )
        queue = await self.broker.declare_queue(_queue)
        self.logger.info(f'Queue {queue_name} declared')
        return queue

    async def setup(self, settings):
        # setup connection
        await self.connect(settings.get_rabbitmq_brokers())
        # setup redis
        client: RedisClient = RedisClient()
        redis_client = await client.connect(settings.get_redis_server_url())
        redis_lock.set_redis_client(redis_client)
        # setup db
        await db_init()
