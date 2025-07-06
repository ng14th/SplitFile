from typing import Any, Dict, List, Callable
from functools import wraps

from aio_pika import RobustQueue
from .async_client import AsyncRabbitMqClient
from faststream import rabbit
from faststream.rabbit.annotations import RabbitMessage
from core.context_var import event_id


RABBITMQ_MESSAGE_RETRY_COUNT = 10
RABBITMQ_MESSAGE_DELAY_SECONDS = 30
lname = 'rabbitmq-consumer'


class AsyncRabbitMqConsumer(AsyncRabbitMqClient):

    async def with_ack(self, function):
        try:
            if hasattr(function, '__qualname__'):
                func_name = function.__qualname__.split('.')[0]
            else:
                func_name = function.__repr__()
        except:
            func_name = function.__name__

        @wraps(function)
        async def wrapper(message: RabbitMessage):
            exchange_name, routing_key = message.exchange, message.routing_key
            try:

                if message.headers.get('eid'):
                    event_id.set_event_id(message.headers.get('eid'))

                self.logger.info(
                    f'{func_name} get message',
                    rbmq_exchange=exchange_name,
                    rbmq_routing_key=routing_key,
                    rbmq_consume_data=message.body,
                )

                await function(message)
                await message.ack()

            # except aio_pika.exceptions.MessageProcessError as e:
            #     pass

            except Exception as e:
                self.logger.warning(
                    f'{lname} handle message get exception {e} at {exchange_name=} {routing_key=}'
                )
                await self.retry_or_sent_to_deadletter_queue(message, exchange_name, routing_key)

        return wrapper

    def get_xdead_expired_count(self, message: RabbitMessage) -> int:
        xdead_header = message.headers.get('x-death', [])
        if xdead_header:
            for xdead in xdead_header:
                if xdead.get('reason', '') == 'rejected' and xdead.get('count', 0) > 0:
                    return xdead.get('count', 0)

            self.logger.warning(
                f'{lname} not found expired and count in x-death header')

        self.logger.warning(f'{lname} not found x-death in message.headers')
        return 0

    async def retry_or_sent_to_deadletter_queue(
        self,
        message: RabbitMessage,
        exchange_name: str,
        routing_key: str,
    ):

        expired_count = self.get_xdead_expired_count(message)
        if expired_count > RABBITMQ_MESSAGE_RETRY_COUNT:
            # send to dead-letter queue after 10 retries
            if exchange_name and routing_key:
                await self._publish(
                    message.body,
                    _exchange=exchange_name,
                    routing_key=f'{routing_key}.deadlettered',
                    retry=True,
                    headers={'eid': event_id.get_event_id()}
                )
                self.logger.info(
                    f'{lname} message sent to dead-letter queue after expired {expired_count} times',
                    rbmq_exchange=exchange_name,
                    rbmq_routing_key=routing_key
                )
            else:

                self.logger.error(
                    f'{lname} Cannot send message to dead-letter queue. reason not found {exchange_name=} {routing_key=}',
                )

            # remove message from queue
            await message.ack()
        else:
            # reject to sent message to delay queue
            self.logger.warning(
                f'{lname} sent message to delay queue',
                rbmq_exchange=exchange_name,
                rbmq_routing_key=routing_key,
            )

            await message.reject()

    async def create_queue_with_dead_letter_2_tier_strategy(
        self,
        exchange_name: str,
        exchange_type: str,
        queue_name: str,
        routing_key: str,
        rabbitmq_urls: List[str],
        **kwargs
    ) -> rabbit.RabbitQueue:

        if exchange_type not in ('direct', 'topic', 'fanout'):
            raise ValueError('exchange_type must be direct, topic or fanout')

        await self.ensure_connection(rabbitmq_urls)

        exchange = await self.declare_exchange(
            exchange_name=exchange_name,
            type=exchange_type,
            durable=True,
            auto_delete=False,
        )
        if not exchange:
            raise 'Can not create exchange'

        delay_queue_name = f'{queue_name}.delayed'
        delay_routing_key = f'{routing_key}.delayed'

        dead_queue_name = f'{queue_name}.deadlettered'
        dead_routing_key = f'{routing_key}.deadlettered'

        queue_arguments = {
            'x-dead-letter-exchange': exchange_name,
            'x-dead-letter-routing-key': delay_routing_key,
        }

        if kwargs.get('queue_arguments'):
            input_queue_arguments = kwargs.get('queue_arguments')
            for forbidden_arg in ('x-dead-letter-exchange', 'x-dead-letter-routing-key'):
                if forbidden_arg in input_queue_arguments:
                    del input_queue_arguments[forbidden_arg]
            queue_arguments.update(input_queue_arguments)

        # main queue
        queue: RobustQueue = await self.declare_queue(
            queue_name=queue_name,
            durable=True,
            arguments=queue_arguments
        )
        await queue.bind(exchange=exchange, routing_key=routing_key)

        # delay queue
        delay_queue: RobustQueue = await self.declare_queue(
            queue_name=delay_queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': exchange.name,
                'x-dead-letter-routing-key': routing_key,
                'x-message-ttl': RABBITMQ_MESSAGE_DELAY_SECONDS * 1000,
            }
        )
        await delay_queue.bind(exchange=exchange, routing_key=delay_routing_key)

        # dead letter queue
        dead_queue: RobustQueue = await self.declare_queue(
            queue_name=dead_queue_name,
            durable=True
        )
        await dead_queue.bind(exchange=exchange, routing_key=dead_routing_key)

        return queue

    async def create_queue(
        self,
        exchange_name: str,
        exchange_type: str,
        queue_name: str,
        routing_key: str,
        rabbitmq_urls: List[str]
    ):
        queue = await self.create_queue_with_dead_letter_2_tier_strategy(
            exchange_name,
            exchange_type,
            queue_name,
            routing_key,
            rabbitmq_urls
        )
        return queue

    async def consume(self, queue: RobustQueue, handler: Callable) -> None:
        return await queue.consume(await self.with_ack(handler))
