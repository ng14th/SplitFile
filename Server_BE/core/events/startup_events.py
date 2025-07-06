from core.settings.service_setting import settings
from core.database.db_postgresql import db_init
from core.minio_manage import MinIOClient, minio_manager
from core import constants


async def startup_event_init_db():
    await db_init()


async def startup_event_init_minio():
    for client in minio_manager._clients.values():
        if not client.is_connected:
            await client.connect()

events = [v for k, v in locals().items() if k.startswith('startup_event_')]
