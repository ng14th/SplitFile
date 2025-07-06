import logging
from tortoise import Tortoise
from tortoise.backends.base.client import BaseDBAsyncClient
from core.settings.service_setting import settings
from core.constants import AUTH_CONSOLE

logger = logging.getLogger(AUTH_CONSOLE)

URL_POSTGRESQL = 'postgres://{username}:{password}@{host}:{port}/{db_name}'
URL_POSTGRESQL = URL_POSTGRESQL.format(
    username=settings.POSTGRESQL_DB_MASTER_USERNAME,
    password=settings.POSTGRESQL_DB_MASTER_PASSWORD,
    host=settings.POSTGRESQL_DB_MASTER_HOST,
    port=settings.POSTGRESQL_DB_MASTER_PORT,
    db_name=settings.POSTGRESQL_DB_MASTER_NAME
)


URL_POSTGRESQL_REPLICA = 'postgres://{username}:{password}@{host}:{port}/{db_name}'
URL_POSTGRESQL_REPLICA = URL_POSTGRESQL_REPLICA.format(
    username=settings.POSTGRESQL_REPLICA_01_USERNAME,
    password=settings.POSTGRESQL_REPLICA_01_PASSWORD,
    host=settings.POSTGRESQL_REPLICA_01_HOST,
    port=settings.POSTGRESQL_REPLICA_01_PORT,
    db_name=settings.POSTGRESQL_REPLICA_01_NAME
)


TORTOISE_ORM = {
    "connections": {
        "master": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.POSTGRESQL_DB_MASTER_HOST,
                "port": settings.POSTGRESQL_DB_MASTER_PORT,
                "user": settings.POSTGRESQL_DB_MASTER_USERNAME,
                "password": settings.POSTGRESQL_DB_MASTER_PASSWORD,
                "database": settings.POSTGRESQL_DB_MASTER_NAME,
                "statement_cache_size": 0,  # Disable statement caching
            }
        },
        "replica": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.POSTGRESQL_REPLICA_01_HOST,
                "port": settings.POSTGRESQL_REPLICA_01_PORT,
                "user": settings.POSTGRESQL_REPLICA_01_USERNAME,
                "password": settings.POSTGRESQL_REPLICA_01_PASSWORD,
                "database": settings.POSTGRESQL_REPLICA_01_NAME,
                "statement_cache_size": 0,  # Disable statement caching
            }
        }
    },
    "apps": {
        "app": {
            "models": ['src.app.models', 'aerich.models'],
            "default_connection": "master",
        },
    },
    # "routers": ['core.middlewares.db_router.MasterReplicaRouter']
}


async def check_db_excute(db_connection: BaseDBAsyncClient):
    try:
        await db_connection.execute_query('SELECT 1')
        logger.info(f'Check {db_connection.connection_name} success')
    except Exception as e:
        logger.error(f'Check {db_connection.connection_name} failed | {e}')
        raise e


async def db_init():

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    master = Tortoise.get_connection('master')
    await check_db_excute(master)
    replica = Tortoise.get_connection('replica')
    await check_db_excute(replica)

    logger.info(f'Connect to postgresql success | {master=} | {replica=}')
