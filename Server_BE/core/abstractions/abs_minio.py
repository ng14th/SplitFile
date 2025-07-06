# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class AbsMinioClient(ABC):
    @property
    @abstractmethod
    def client(self):
        """Master client if use sentinel

        Raises:
            NotImplementedError: _description_

        Returns:
            Redis: _description_
        """
        raise NotImplementedError

    @abstractmethod
    async def connect(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self, *args, **kwargs):
        raise NotImplementedError
