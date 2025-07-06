from typing import Optional
from .base_setting import AppBaseSettings


class RabbitMQSetting(AppBaseSettings):
    RBMQ_ENABLE: bool = True
    RBMQ_URLS: Optional[str] = None

    def get_rabbitmq_brokers(self):
        if self.RBMQ_ENABLE:
            # return f'amqp://{auth}{self.CELERY_BROKER_RABBITMQ_HOST}:{self.CELERY_BROKER_RABBITMQ_PORT}{vhost}'
            return self.RBMQ_URLS
