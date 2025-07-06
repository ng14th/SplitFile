# -*- coding: utf-8 -*-
from typing import Any, List


class ErrorResponseException(Exception):
    def __init__(
        self,
        success: bool = False,
        data: List[Any] = [],
        status_code: int = 400,
        error_code: int = 0,
        error: str = "",
        message: str = ""
    ):
        self.status_code = status_code
        self.success = success
        self.message = message
        self.data = data
        self.count = len(data) if data else 0
        self.error_code = error_code
        self.error = error


class ErrorHtmlResponseException(Exception):
    def __init__(
        self,
        error: str
    ):
        self.error = error
