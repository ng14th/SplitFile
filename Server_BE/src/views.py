from src.app.views import (
    storage_router
)

routers = [
    {"router": storage_router, "prefix": "/storage"},
]
