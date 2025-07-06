from core import constants
from core.rabbitmq.async_client import AsyncRabbitMqClient


class OrderRabbitMqClient(AsyncRabbitMqClient):
    async def publish_order_to_payment(self, data):
        result = await self._publish(data, constants.PAYMENT_EXCHANGE, constants.PAYMENT_ROUTING_KEY)
        return result
