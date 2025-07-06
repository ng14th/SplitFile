# -*- coding: utf-8 -*-
from typing import Any, List
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool = True
    status_code: int = 200
    message: str = ""
    data: Any = []
    count: int = 0
    error_code: int = 0
    error: str = ""
