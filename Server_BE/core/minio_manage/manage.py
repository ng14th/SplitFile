# -*- coding: utf-8 -*-
import asyncio
from typing import Dict

from core import constants
from core.abstractions import AbsMinioClient, Singleton


class MinIOManager(Singleton):
    def _singleton_init(self, **kwargs):
        self._clients: Dict[str, AbsMinioClient] = {}

    def add_client(self, name: str, client: AbsMinioClient):
        if not isinstance(client, AbsMinioClient):
            raise ValueError(
                f'expected client is an instance of AbsMinioClient get {type(client)=}')
        self._clients.update({name: client})

    def get_client(self, name: str | int = constants.HLS_MINIO) -> AbsMinioClient:
        return self._clients.get(name)

    def remove_client(self, name: str):
        if name in self._clients:
            try:
                client = self._clients.get(name)
                asyncio.run(client.disconnect())
            except Exception:
                pass
            del self._clients


minio_manager: MinIOManager = MinIOManager()


def get_minio_client(name: str = constants.HLS_MINIO):
    return minio_manager.get_client(name)
