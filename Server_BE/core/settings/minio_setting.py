# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from .base_setting import AppBaseSettings
from core.minio_manage import MinIOClient, minio_manager
from core import constants


class MinioSetting(
    AppBaseSettings
):

    MINIO_PUBLIC_DOMAIN: str = ''
    MINIO_ACCESS_KEY: str = ''
    MINIO_SECRET_KEY: str = ''
    MINIO_BUCKET_NAME: str = ''
    MINIO_SECURE: bool = False

    def setup_client_minio(self):
        minio_client: MinIOClient = MinIOClient(
            minio_server=self.MINIO_PUBLIC_DOMAIN.replace('https://', ''),
            access_key=self.MINIO_ACCESS_KEY,
            secret_key=self.MINIO_SECRET_KEY,
            bucket_name=self.MINIO_BUCKET_NAME,
            secure_ssl=self.MINIO_SECURE
        )
        minio_manager.add_client(constants.HLS_MINIO, minio_client)
