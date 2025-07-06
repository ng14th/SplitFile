# -*- coding: utf-8 -*-
import io
import logging
from typing import Union

from core import constants
from miniopy_async import Minio
from miniopy_async.error import S3Error
from core.abstractions import AbsMinioClient


class MinIOClient(AbsMinioClient):
    def __init__(
        self,
        minio_server: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure_ssl: bool = False,
        **kwargs
    ):
        self._client: Union[Minio, None] = None
        self._is_connected: bool = False
        self._url_endpoint = minio_server
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket_name = bucket_name
        self._secure_ssl = secure_ssl
        self._is_connected = False
        self.logger = kwargs.get('logger') or logging.getLogger(
            constants.AUTH_CONSOLE)

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def client(self) -> Minio:
        return self._client

    async def reload(self, **kwargs):
        self._is_connected = False
        return await self.connect(**kwargs)

    async def connect(self, **kwargs):
        if self._is_connected:
            return
        self.logger.info(f'server {self._url_endpoint}')
        try:
            self._client = Minio(
                self._url_endpoint,
                access_key=self._access_key,
                secret_key=self._secret_key,
                secure=self._secure_ssl
            )
            found = await self._client.bucket_exists(self._bucket_name)
            if not found:
                await self._client.make_bucket(self._bucket_name)
                self.logger.info(f"Bucket {self._bucket_name} created new")
            else:
                self.logger.warning(
                    f"Bucket {self._bucket_name} already exists")

            self._is_connected = True
        except S3Error as e:
            self.logger.error(
                f'try to connect MinIO get exception {e.message}')

        return self._is_connected

    async def disconnect(self):
        return

    async def upload_file_by_chunk(self, name: str, data: str):
        return await self._client.put_object(
            self._bucket_name,
            name,
            io.BytesIO(data),
            length=len(data),
            part_size=5 * 1024 * 1024,
            num_parallel_uploads=10
        )

    async def put_object(self, name: str, data: bytes):
        return await self._client.put_object(
            self._bucket_name,
            name,
            io.BytesIO(data),
            length=len(data)
        )

    async def fput_object(self, name: str, file_path: str):
        return await self._client.fput_object(
            self._bucket_name,
            name,
            file_path=file_path
        )

    async def get_object(self, name: str):
        res = await self._client.get_object(
            self._bucket_name,
            name
        )
        if res:
            return await res.content.read()

    async def delete_object(self, name: str):
        await self._client.remove_object(
            self._bucket_name,
            name
        )
        self.logger.info(f'MiniIOClient | delete_object {name=}')
        return

    async def presign_get_url(self, name: str, response_headers: dict = {}):
        res = await self._client.presigned_get_object(
            bucket_name=self._bucket_name,
            object_name=name,
            response_headers=response_headers,
        )
        if res:
            return res

        return None
